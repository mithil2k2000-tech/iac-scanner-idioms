"""Score both scanners on the mutation corpus and compare them on the real corpus."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW, RES, FIG, TAB = ROOT / "raw", ROOT / "results", ROOT / "paper" / "figures", ROOT / "paper" / "tables"
for p in (RES, FIG, TAB):
    p.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False})
IDIOM_LABEL = {"literal": "Literal value", "variable_default": "Variable default", "tfvars": "terraform.tfvars",
               "local": "Local value", "conditional": "Conditional", "module": "Local module", "omitted": "Omitted (default)"}


def checkov_findings(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    d = json.loads(path.read_text())
    d = d if isinstance(d, list) else [d]
    out = []
    for block in d:
        if not isinstance(block, dict) or "results" not in block:
            continue
        for r in block["results"].get("failed_checks", []):
            out.append({"rule": r["check_id"], "file": r.get("file_abs_path") or r["file_path"],
                        "resource": r.get("resource", ""), "lines": r.get("file_line_range", [0, 0])})
    return out


def semgrep_findings(path: Path) -> list[dict]:
    d = json.loads(path.read_text())
    return [{"rule": r["check_id"].split(".")[-1], "file": str(Path(r["path"]).resolve()), "line": r["start"]["line"]}
            for r in d["results"]]


# ------------------------------------------------------------------ mutation corpus

def case_of(file: str) -> tuple[str, str, str] | None:
    m = re.search(r"mutants/([^/]+)/([^/]+)/(secure|insecure)/", file)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def mutation():
    meta = pd.DataFrame(json.loads((RES / "mutants.json").read_text()))
    fired: dict[tuple, dict[str, set]] = defaultdict(lambda: {"Checkov": set(), "Semgrep": set()})
    for f in (RAW / "checkov_mutants").glob("*.json"):
        # One Checkov run per case; the case is encoded in the output file name.
        m = re.match(r"mutants_(.+?)_(literal|variable_default|tfvars|local|conditional|module|omitted)_(secure|insecure)$",
                     f.stem)
        c = (m.group(1), m.group(2), m.group(3))
        for x in checkov_findings(f):
            fired[c]["Checkov"].add(x["rule"])
    for x in semgrep_findings(RAW / "semgrep_mutants.json"):
        c = case_of(x["file"])
        if c:
            fired[c]["Semgrep"].add(x["rule"])

    rows, rules = [], {}
    for cat in sorted(meta.category.unique()):
        for sc in ("Checkov", "Semgrep"):
            relevant = fired[(cat, "literal", "insecure")][sc] - fired[(cat, "literal", "secure")][sc]
            rules[(cat, sc)] = sorted(relevant)
            for _, r in meta[meta.category == cat].iterrows():
                hit = bool(relevant & fired[(cat, r.idiom, r.truth)][sc])
                rows.append({"category": cat, "family": r.family, "idiom": r.idiom, "truth": r.truth, "scanner": sc,
                             "covered": bool(relevant), "flagged": hit})
    df = pd.DataFrame(rows)
    df.to_csv(RES / "mutation_scores.csv", index=False)
    (RES / "rule_map.json").write_text(json.dumps({f"{c}|{s}": v for (c, s), v in rules.items()}, indent=1))

    cov = df[df.idiom == "literal"].groupby(["scanner", "category"]).covered.first().unstack(0)
    facts = {"categories": len(cov), "coverage": cov.sum().astype(int).to_dict(),
             "both": int((cov.Checkov & cov.Semgrep).sum()), "neither": int((~cov.Checkov & ~cov.Semgrep).sum()),
             "only_checkov": sorted(cov.index[cov.Checkov & ~cov.Semgrep]),
             "only_semgrep": sorted(cov.index[~cov.Checkov & cov.Semgrep]), "neither_list": sorted(cov.index[~cov.Checkov & ~cov.Semgrep])}

    # Recall and false-positive rate per idiom, over the categories the scanner covers.
    tab = []
    for sc in ("Checkov", "Semgrep"):
        d = df[(df.scanner == sc) & df.covered]
        for idiom in IDIOM_LABEL:
            di = d[d.idiom == idiom]
            ins, sec = di[di.truth == "insecure"], di[di.truth == "secure"]
            tab.append({"scanner": sc, "idiom": idiom, "n_insecure": len(ins), "recall": ins.flagged.mean() if len(ins) else np.nan,
                        "n_secure": len(sec), "fpr": sec.flagged.mean() if len(sec) else np.nan})
    t = pd.DataFrame(tab)
    t.to_csv(RES / "idiom_table.csv", index=False)
    facts["idiom"] = t.round(3).to_dict("records")

    out = []
    for idiom, lab in IDIOM_LABEL.items():
        r = {"Setting written as": lab}
        for sc in ("Checkov", "Semgrep"):
            x = t[(t.scanner == sc) & (t.idiom == idiom)].iloc[0]
            r[f"{sc} recall"] = "--" if np.isnan(x.recall) else f"{x.recall:.2f} ({int(round(x.recall * x.n_insecure))}/{x.n_insecure})"
            r[f"{sc} FPR"] = "--" if np.isnan(x.fpr) else f"{x.fpr:.2f} ({int(round(x.fpr * x.n_secure))}/{x.n_secure})"
        out.append(r)
    (TAB / "idioms.tex").write_text(
        "\\begin{table*}[t]\n\\centering\n\\caption{Recall on insecure cases and false-positive rate on secure cases, by how the "
        "security setting is written, over the categories each scanner covers (" + f"{facts['coverage']['Checkov']} for Checkov, "
        f"{facts['coverage']['Semgrep']} for Semgrep" + "). Omitted settings are counted as insecure or secure according to the "
        "provider default.}\n\\label{tab:idioms}\n\\small\n" + pd.DataFrame(out).to_latex(index=False, escape=False,
                                                                                    column_format="lrrrr") + "\\end{table*}\n")

    # Per-category heat map.
    piv = df[df.truth == "insecure"].assign(v=lambda x: np.where(~x.covered, np.nan, x.flagged.astype(float)))
    fig, axes = plt.subplots(1, 2, figsize=(7, 4.6), sharey=True)
    cats = sorted(df.category.unique())
    for ax, sc in zip(axes, ("Checkov", "Semgrep")):
        m = piv[piv.scanner == sc].pivot_table(index="category", columns="idiom", values="v", aggfunc="mean", dropna=False)
        m = m.reindex(index=cats, columns=[i for i in IDIOM_LABEL if i in m.columns])
        ax.imshow(np.ma.masked_invalid(m.values), cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.values[i, j]
                ax.text(j, i, "" if np.isnan(v) else ("+" if v == 1 else "x"), ha="center", va="center", fontsize=6, color="white")
        ax.set_xticks(range(m.shape[1]))
        ax.set_xticklabels([IDIOM_LABEL[c] for c in m.columns], rotation=45, ha="right", fontsize=6)
        ax.set_yticks(range(len(cats)))
        ax.set_yticklabels([c.replace("_", " ") for c in cats], fontsize=6)
        ax.set_title(sc)
    fig.tight_layout()
    fig.savefig(FIG / "heatmap.pdf")
    plt.close(fig)
    return facts, rules


# ------------------------------------------------------------------ real corpus

RES_RE = re.compile(r'^\s*resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.M)


def resource_spans(file: Path) -> list[tuple[int, int, str]]:
    text = file.read_text(errors="ignore")
    lines = text.splitlines()
    spans = []
    for m in RES_RE.finditer(text):
        start = text[:m.start()].count("\n") + 1
        depth, end = 0, start
        for i in range(start - 1, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth == 0:
                end = i + 1
                break
        spans.append((start, end, f"{m.group(1)}.{m.group(2)}"))
    return spans


def corpus(rules):
    cat_of = {(sc, r): c for (c, sc), rs in rules.items() for r in rs}
    projects = sorted(p.name for p in (ROOT / "corpus").iterdir() if p.is_dir())
    flags = defaultdict(set)  # (file, resource, category) -> scanners
    totals = []
    span_cache = {}
    for proj in projects:
        ck = checkov_findings(RAW / "checkov" / f"{proj}.json")
        n_ck = len(ck)
        for x in ck:
            c = cat_of.get(("Checkov", x["rule"]))
            fp = x["file"]
            f = str(Path(fp).resolve()) if Path(fp).is_absolute() and Path(fp).exists() else \
                str((ROOT / "corpus" / proj / fp.lstrip("/")).resolve())
            if c:
                # Resource address without module prefix or count/for_each index: type.name
                parts = re.sub(r"\[[^\]]*\]", "", x["resource"]).split(".")
                flags[(f, ".".join(parts[-2:]), c)].add("Checkov")
        totals.append({"project": proj, "checkov_failed": n_ck})
    sg = semgrep_findings(RAW / "semgrep_corpus.json")
    n_sg = defaultdict(int)
    for x in sg:
        proj = re.search(r"corpus/([^/]+)/", x["file"]).group(1)
        n_sg[proj] += 1
        c = cat_of.get(("Semgrep", x["rule"]))
        if not c:
            continue
        f = Path(x["file"])
        if f not in span_cache:
            span_cache[f] = resource_spans(f)
        res = next((r for s, e, r in span_cache[f] if s <= x["line"] <= e), None)
        if res:
            flags[(str(f), res, c)].add("Semgrep")
    tot = pd.DataFrame(totals)
    tot["semgrep_failed"] = tot.project.map(n_sg).fillna(0).astype(int)
    tot.to_csv(RES / "corpus_totals.csv", index=False)
    # Agreement over (resource, category) pairs where both scanners cover the category.
    both_cov = {c for (c, sc), rs in rules.items() if rs and rules.get((c, "Semgrep" if sc == "Checkov" else "Checkov"))}
    rows = [{"file": k[0], "resource": k[1], "category": k[2], "checkov": "Checkov" in v, "semgrep": "Semgrep" in v}
            for k, v in flags.items() if k[2] in both_cov]
    a = pd.DataFrame(rows)
    a.to_csv(RES / "corpus_agreement.csv", index=False)
    summary = a.groupby("category").agg(both=("checkov", lambda s: int((s & a.loc[s.index, "semgrep"]).sum())),
                                        checkov_only=("checkov", lambda s: int((s & ~a.loc[s.index, "semgrep"]).sum())),
                                        semgrep_only=("semgrep", lambda s: int((s & ~a.loc[s.index, "checkov"]).sum())))
    summary.to_csv(RES / "corpus_agreement_by_category.csv")
    return {"projects": len(projects), "tf_files": sum(1 for _ in (ROOT / "corpus").rglob("*.tf")),
            "checkov_total": int(tot.checkov_failed.sum()), "semgrep_total": int(tot.semgrep_failed.sum()),
            "pairs": len(a), "both": int((a.checkov & a.semgrep).sum()), "checkov_only": int((a.checkov & ~a.semgrep).sum()),
            "semgrep_only": int((~a.checkov & a.semgrep).sum()), "both_covered_categories": sorted(both_cov)}


if __name__ == "__main__":
    facts, rules = mutation()
    facts["corpus"] = corpus(rules)
    (RES / "facts.json").write_text(json.dumps(facts, indent=1, default=str))
    print(json.dumps({k: v for k, v in facts.items() if k != "idiom"}, indent=1, default=str))
    print(pd.read_csv(RES / "idiom_table.csv").round(2).to_string())

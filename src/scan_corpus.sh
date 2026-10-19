#!/usr/bin/env bash
# Scan the corpus and the mutation cases with both scanners (JSON output in raw/).
set -u
cd "$(dirname "$0")/.."
SG=".venv/bin/semgrep --config semgrep-rules/terraform --json --metrics=off --disable-version-check --quiet"
# Semgrep: one run per tree (rule loading dominates its run time); findings carry their file paths.
[ -s raw/semgrep_corpus.json ] || $SG -o raw/semgrep_corpus.json corpus/ 2>/dev/null < /dev/null
[ -s raw/semgrep_mutants.json ] || $SG -o raw/semgrep_mutants.json mutants/ 2>/dev/null < /dev/null
echo "$(date +%T) semgrep done"
# Checkov: one run per project or case, because it builds one graph per directory tree.
ck() {
  src=$1; out=$2
  # Default invocation, as in a typical CI job (no --var-file).
  [ -s "$out" ] || .venv/bin/checkov -d "$src" --framework terraform -o json --quiet --compact --skip-download > "$out" 2>/dev/null < /dev/null < /dev/null
}
export -f ck
mkdir -p raw/checkov raw/checkov_mutants
ls corpus | xargs -P 2 -I{} bash -c 'ck corpus/{} raw/checkov/{}.json'
echo "$(date +%T) checkov corpus done"
find mutants -mindepth 3 -maxdepth 3 -type d | xargs -P 2 -I{} bash -c 'n=$(echo {} | tr / _); ck {} raw/checkov_mutants/$n.json'
echo "$(date +%T) ALLDONE"

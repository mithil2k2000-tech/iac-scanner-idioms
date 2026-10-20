# Same setting, different verdict

📄 **Paper (PDF): [iac-scanner-idioms.pdf](iac-scanner-idioms.pdf)**

Does the way a Terraform value is written change what IaC security scanners report? A mutation corpus of 24 AWS
security settings, each secure and insecure in seven idioms (literal, variable default, tfvars, local, conditional,
local module, omitted): 312 cases with ground truth by construction.

| Written as | Checkov recall / FPR | Semgrep recall / FPR |
|---|---|---|
| Literal | 1.00 / 0.00 | 1.00 / 0.00 |
| Variable default | 0.95 / 0.00 | 0.93 / 0.00 |
| terraform.tfvars | 0.95 / 0.00 | 0.79 / 0.79 |
| Local | 0.95 / 0.00 | 0.93 / 0.00 |
| Conditional | 0.95 / 0.00 | 0.79 / 0.79 |
| Local module | 0.95 / 0.00 | 0.79 / 0.79 |
| Omitted | 1.00 / 0.75 | 1.00 / 0.25 |

* Checkov missed `null` passed through a variable (SNS encryption) and flags secure defaults, including SQS queues
  that AWS has encrypted by default since 2022.
* For values Semgrep cannot resolve, the verdict follows the rule's polarity, not the configuration.
* On 53 real projects the scanners agreed on 7 of 63 shared-category findings.

## Use the corpus

`mutants/<category>/<idiom>/<secure|insecure>/` — point any scanner at it; `results/mutants.json` holds the ground truth.

## Reproduce

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
./fetch_corpus.sh
python src/mutants.py
bash src/scan_corpus.sh
python src/analyse.py
cd paper && latexmk -pdf main.tex
```

## AI assistance

An AI assistant (Claude, Anthropic) helped write experiment code and draft text. The author designed the
study questions, reviewed the code and results, and is responsible for the content.

## Licence

MIT

# Model card: DOM-XSS LightGBM Security v2

## Summary

Security v2 ranks function-level JavaScript for DOM-XSS investigation. It is a
LightGBM derivative trained in this repository, not the TensorFlow DNN or model
weights published with the CMU study.

| Property | Value |
|---|---|
| Model family | LightGBM binary classifier |
| Output | Uncalibrated risk-ranking score |
| Default serving threshold | `0.5` |
| Feature contract | `cmu-ast-bow-security-interactions-v2` |
| Vocabulary | 4,096 training-only terms |
| Training seed | `42` |
| Primary use | Security triage before manual or dynamic verification |

Artifacts:

- `models/lightgbm_security_v2.txt` — native production artifact
- `models/lightgbm_security_v2.pkl` — reproducibility artifact
- `models/lightgbm_security_v2_metadata.json` — provenance and training audit
- `preprocessing/vocab_security_v2.json` — ordered feature mapping

## Ownership and relationship to the paper

The data comes from Carnegie Mellon University's
[DOM XSS Web Vulnerability Dataset](https://kilthub.cmu.edu/articles/dataset/DOM_XSS_Web_Vulnerability_Dataset/13870256).
The associated
[WWW 2021 paper](https://www.contrib.andrew.cmu.edu/~liminjia/research/papers/www2021-dom-xss-dnn.pdf)
motivates function-level AST features, script-level separation, and a hybrid
workflow.

This project independently implements a LightGBM model, source/sink
co-occurrence features, duplicate controls, model selection, threshold
selection, and native serving artifacts. No published CMU checkpoint is
included or used for initialization.

## Data audit

The legacy sampled derivative supplied 90,500 rows. The trainer accepted
87,210 and rejected 3,290 rows whose XLSX feature cell reached Excel's
32,767-character limit.

| Item | Count |
|---|---:|
| Parsed positive rows | 37,258 |
| Parsed negative rows | 49,952 |
| Unique scripts | 22,886 |
| Training rows after duplicate cap | 39,600 |
| Validation bags, unique and unseen | 3,088 |
| Test bags, unique and unseen | 3,215 |
| Positive test bags | 56 |

The metadata artifact records the exact source paths, byte sizes, and SHA-256
digests used by the run.

## Feature contract

Each function is represented by normalized AST token counts. Security v2 adds
deterministic binary features when one function contains:

- a URL, cookie, referrer, storage, message, or `window.name` source;
- an `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `eval`, or
  `document.write` sink; and
- a source and sink combination.

These additions encode co-occurrence, not verified control or data flow. They
are intentionally exposed separately in the serving response.

## Leakage controls

1. The `dbg` script identifier deterministically assigns the complete script to
   train, validation, or test.
2. Vocabulary fitting uses training scripts only.
3. Invalid, truncated, zero-coverage, and conflicting-label rows are excluded.
4. Training retains at most 20 rows per identical feature bag.
5. Validation bags must be unique and absent from training.
6. Test bags must be unique and absent from training and validation.
7. Hyperparameters and thresholds use validation only.

The duplicate cap replaces the earlier “one row per feature bag” policy, which
discarded most positive training rows. It preserves common positive patterns
without allowing them into held-out evaluation.

## Held-out results

### LightGBM only

| Operating point | Precision | Recall | F1 | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Exported artifact at `0.5` | 0.8545 | 0.8393 | 0.8468 | 0.9161 | 0.9967 |
| Validation 95%-recall target (`0.02206`) | 0.6000 | 0.9107 | 0.7234 | 0.9130 | 0.9961 |

### Hybrid downstream decision

The consuming pipeline can raise priority when either the model crosses its
threshold or a source/sink co-occurrence signal is present.

| Operating point | Precision | Recall | F1 |
|---|---:|---:|---:|
| Exported artifact at `0.5` | 0.7206 | 0.8750 | 0.7903 |
| Validation 95%-recall target (`0.02206`) | 0.5604 | 0.9107 | 0.6939 |

Hybrid metrics are reported separately because the rule contribution is not an
ML prediction.

The recall-target rows describe the train-only selection model. The default
rows describe the exported artifact after refitting on train and validation;
these are the numbers relevant to the production bundle.

The exact report is
[`docs/results/lightgbm_security_v2_evaluation.json`](docs/results/lightgbm_security_v2_evaluation.json).

## Score semantics

The LightGBM value is an **ML risk score**, not a probability that exploitation
will succeed. `high_priority` means “investigate or dynamically verify this
page”; it does not mean “confirmed vulnerable.” Only reproducible evidence or
an authorized dynamic rule can confirm a finding.

## Known limitations

- The Tree-sitter serving extractor is a compatible subset, not the modified
  V8 extractor that produced the source data.
- A function-level bag cannot prove source-to-sink flow or sanitizer efficacy.
- The strict test includes only 56 independent positive examples.
- The dataset is derived from a 2019 crawl and can underrepresent current
  frameworks and build tooling.
- A page-level maximum score changes the false-positive behavior on large
  applications.
- The model does not replace taint tracking, browser interaction, or human
  review.

## Reproduction

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-training.txt
.venv/bin/python -m pytest -q

.venv/bin/python training/train_lightgbm_grouped.py \
  /path/to/positive_rows.xlsx \
  /path/to/negative_rows.xlsx \
  --output-root runs/security-v2 \
  --vocab-size 4096 \
  --min-token-count 5 \
  --target-recall 0.95 \
  --max-train-duplicates 20
```

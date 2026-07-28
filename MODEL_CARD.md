# LightGBM DOM-XSS risk-ranking model

## Intended use

This model ranks JavaScript functions for DOM-XSS review. It is intended to
prioritize dynamic analysis, not to prove that a page is exploitable. A low
score must not be treated as proof that a page is safe.

The production artifact is:

- `models/lightgbm_grouped_model.txt`
- `preprocessing/vocab_top500_grouped.json`
- `models/lightgbm_grouped_metadata.json`

The native LightGBM artifact is used in production so the serving image does
not need to deserialize Python pickle files.

## Dataset and provenance

The source data is Carnegie Mellon University's
[DOM XSS Web Vulnerability Dataset](https://kilthub.cmu.edu/articles/dataset/DOM_XSS_Web_Vulnerability_Dataset/13870256),
published for the WWW 2021 paper
[Towards a Lightweight, Hybrid Approach for Detecting DOM XSS Vulnerabilities with Machine Learning](https://www.contrib.andrew.cmu.edu/~liminjia/research/papers/www2021-dom-xss-dnn.pdf).
The researchers' parsing and TensorFlow tools are available in
[pwwl/www-dom-xss-tools](https://github.com/pwwl/www-dom-xss-tools).

This LightGBM model is a derivative experiment. It is not the paper's DNN and
does not claim to reproduce the paper's full 32-million-function experiment.

## Leakage controls

The current training pipeline:

1. Assigns complete JavaScript scripts to deterministic 80/10/10
   train/validation/test splits using the `dbg` script identifier.
2. Builds the 500-token vocabulary from the training split only.
3. Rejects invalid feature dictionaries and XLSX cells at Excel's 32,767
   character limit.
4. Excludes rows with no vocabulary coverage.
5. Excludes feature bags with conflicting labels.
6. Collapses exact duplicate feature bags.
7. Evaluates only validation and test feature bags that were not present in
   earlier splits.
8. Selects hyperparameters by validation PR-AUC and reads the test split once.

Raw `.xz` JSONL input from the CMU release is preferred. XLSX support exists
only to audit and migrate the earlier sampled dataset.

## Evaluation

The cleaned sampled dataset contains 87,210 readable rows after rejecting
3,290 Excel-truncated rows. The strict held-out test contains 3,169 unique
feature bags, including 55 positive rows.

| Threshold | Precision | Recall | F1 | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Validation-selected `0.96085` | 0.9545 | 0.7636 | 0.8485 | 0.9066 | 0.9948 |
| `0.50` pre-filter threshold | 0.8431 | 0.7818 | 0.8113 | 0.9066 | 0.9948 |

These measurements are function-level results on a sampled derivative
dataset. They do not estimate page-level accuracy or production precision at
the much lower prevalence found on the public web. The exact machine-readable
report is in `docs/results/lightgbm_grouped_evaluation.json`.

### External negative benchmark

The frozen model was additionally evaluated on 146,772 unique negative feature
bags sampled from four separate CMU confirmed-data shards (`101`, `150`, `200`,
and `250`). Scripts and exact feature bags already present in the baseline were
excluded before evaluation. All 874 positive rows encountered in those shards
belonged to baseline scripts, so they were not new independent positives and
were not included in this negative-only benchmark.

| Threshold | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|
| Validation-selected `0.96085` | 493 | 0.3359% | 99.6641% |
| `0.50` | 1,441 | 0.9818% | 99.0182% |

Vocabulary coverage was 95.6573%; 6,374 rows had no vocabulary coverage. This
benchmark measures specificity on additional in-distribution CMU negatives. It
does not measure recall, modern-web generalization, or page-level performance.
The machine-readable report is in
`docs/results/external_negative_benchmark.json`.

## Score semantics

LightGBM output is exposed as an **ML risk score**, not as a calibrated
probability of exploitability. The validation-selected `0.96085` threshold is
the function-level operating point for this model evaluation. The downstream
browser pipeline deliberately retains `0.50` as a recall-oriented triage
threshold before optional dynamic verification: on its small page-level
regression corpus, raising the threshold to `0.96085` removed the only true
positive. Threshold choice therefore belongs to the consuming feature
contract and must not be transferred from this CMU evaluation blindly.

## Known limitations

- The available sampled XLSX files irreversibly truncated 3,290 feature
  dictionaries. They are rejected rather than converted to zero vectors.
- Only 55 independent positives remain in the strict test after removing
  overlaps, so confidence intervals are wider than headline metrics imply.
- The production extractor uses Tree-sitter, while the CMU data was generated
  from modified Chromium/V8 instrumentation. Runtime feature-contract
  validation remains necessary.
- Interaction-dependent, authenticated, and unexecuted paths may be missed.
- The data was collected from an Alexa 10K crawl in 2019 and may not represent
  modern JavaScript frameworks.

## Reproduction

Install the pinned dependencies:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-training.txt
```

Train directly from CMU `.xz` files:

```bash
.venv/bin/python training/train_lightgbm_grouped.py \
  /path/to/shuf.comp.wb.training.*.data.xz \
  --output-root .
```

The command also accepts the two legacy XLSX samples for audit reproduction:

```bash
.venv/bin/python training/train_lightgbm_grouped.py \
  /path/to/positive_rows.xlsx \
  /path/to/negative_rows.xlsx \
  --output-root .
```

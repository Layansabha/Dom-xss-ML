# DOM-XSS ML

Function-level machine learning for prioritizing JavaScript that may contain
DOM-based Cross-Site Scripting (DOM XSS).

The current release, **LightGBM Security v2**, is trained and maintained in this
repository. It uses the public CMU DOM XSS dataset, but it does **not** copy or
fine-tune the researchers' published model weights. The paper is used as a
methodological reference; the feature engineering, LightGBM training,
evaluation protocol, thresholds, and exported artifacts are this project's
own derivative work.

> This is a triage model, not a vulnerability proof. Its score is not a
> calibrated probability of exploitation.

## Current model

Security v2 combines a 4,096-term, training-only AST vocabulary with
deterministic function-level source/sink co-occurrence features. Examples
include the presence of a URL-controlled source and an HTML or script-execution
sink in the same function. Co-occurrence is useful for prioritization, but it
does not prove data flow.

The default downstream operating point is `0.5`:

| Evaluation mode | Precision | Recall | F1 | PR-AUC |
|---|---:|---:|---:|---:|
| LightGBM only | 0.8545 | 0.8393 | 0.8468 | 0.9161 |
| Hybrid decision: model or source/sink signal | 0.7206 | 0.8750 | 0.7903 | n/a |

These results use 3,215 unique held-out feature bags that were not present in
training or validation. They are function-level results on a cleaned sampled
derivative of the CMU dataset; they are not page-level public-web accuracy.
See [MODEL_CARD.md](MODEL_CARD.md) and the
[machine-readable evaluation](docs/results/lightgbm_security_v2_evaluation.json).

## Repository layout

```text
models/            Native and Python model artifacts; older models are baselines
preprocessing/     Feature contract, CMU sampler, and exported vocabulary
training/          Leakage-resistant LightGBM training entry point
evaluation/        External negative-corpus evaluation
docs/results/      Machine-readable results and historical charts
tests/             Split, feature, sampler, and benchmark regression tests
```

## Dataset

The source is Carnegie Mellon University's
[DOM XSS Web Vulnerability Dataset](https://kilthub.cmu.edu/articles/dataset/DOM_XSS_Web_Vulnerability_Dataset/13870256),
published with the WWW 2021 paper
[Towards a Lightweight, Hybrid Approach for Detecting DOM XSS Vulnerabilities with Machine Learning](https://www.contrib.andrew.cmu.edu/~liminjia/research/papers/www2021-dom-xss-dnn.pdf).

Raw CMU JSONL/LZMA shards are preferred. The trainer also accepts the legacy
XLSX samples for reproducibility. XLSX feature cells at Excel's 32,767-character
limit are rejected because they are truncated, not converted to empty vectors.

The v2 run read 90,500 rows and retained 87,210 after rejecting 3,290 truncated
XLSX rows:

- 37,258 positive rows
- 49,952 negative rows
- 22,886 unique script identifiers

Dataset files are intentionally excluded from Git.

## Reproduce the model

Python 3.12 is recommended:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-training.txt
.venv/bin/python -m pytest -q
```

Train from the two audited XLSX samples:

```bash
.venv/bin/python training/train_lightgbm_grouped.py \
  data/raw/positive_rows.xlsx \
  data/raw/negative_rows.xlsx \
  --output-root runs/security-v2 \
  --vocab-size 4096 \
  --min-token-count 5 \
  --target-recall 0.95 \
  --max-train-duplicates 20
```

The same command accepts raw `.jsonl`, `.jsonl.gz`, or `.data.xz` inputs.
Artifacts are written as:

```text
runs/security-v2/models/lightgbm_security_v2.txt
runs/security-v2/models/lightgbm_security_v2.pkl
runs/security-v2/models/lightgbm_security_v2_metadata.json
runs/security-v2/preprocessing/vocab_security_v2.json
runs/security-v2/docs/results/lightgbm_security_v2_evaluation.json
```

## Evaluation protocol

The trainer:

1. assigns complete scripts to deterministic 80/10/10 splits;
2. builds the vocabulary from training scripts only;
3. rejects invalid, truncated, and zero-coverage rows;
4. removes feature bags with conflicting labels;
5. retains at most 20 identical training bags so common patterns remain
   learnable without dominating training;
6. excludes validation and test bags seen in any earlier split;
7. selects hyperparameters by validation PR-AUC;
8. derives the recall-oriented threshold from validation only; and
9. reports the test split once, with model-only and hybrid metrics separated.

The report retains the train-only selection model's test metrics and separately
reports the exported deployment artifact after it is refit on train and
validation. The table above describes the artifact that is actually served.

Older Decision Tree, AdaBoost, Random Forest, XGBoost, and LightGBM artifacts
remain in `models/` for historical comparison. Their original random row split
allows script and exact-pattern leakage, so they must not be selected from
their old headline accuracy alone.

## Adding CMU shards

Use the streaming sampler rather than concatenating multi-gigabyte shards into
Excel:

```bash
.venv/bin/python -m preprocessing.sample_cmu_shards \
  data/raw/cmu/vulnerability-data/confirmed/*.data.xz \
  --exclude data/raw/full_dataset.xlsx \
  --negative-rows-per-input 50000 \
  --output data/processed/cmu-confirmed-additions.jsonl.gz
```

If a shard adds no independent positive scripts, use it as a negative benchmark
instead of silently changing the training balance:

```bash
.venv/bin/python -m evaluation.evaluate_negative_benchmark \
  data/processed/cmu-confirmed-additions.jsonl.gz \
  --model models/lightgbm_security_v2.pkl \
  --vocabulary preprocessing/vocab_security_v2.json \
  --metadata models/lightgbm_security_v2_metadata.json \
  --output runs/security-v2/docs/results/external_negative_benchmark.json
```

## Limitations

- The training features came from modified Chromium/V8 instrumentation, while
  the serving pipeline reconstructs a compatible subset with Tree-sitter.
- Source/sink co-occurrence is not taint tracking.
- The strict test has only 56 independent positive bags.
- The source crawl is from 2019 and does not fully represent modern frameworks.
- Authenticated, interaction-dependent, or unexecuted paths can be missed.

Use the model only on systems you own or are explicitly authorized to test.

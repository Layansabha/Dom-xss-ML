# Repository Structure

```text
Dom-xss-ML/
├── README.md
├── requirements.txt
├── training/
│   ├── train_lightgbm.py
│   ├── train_xgboost.py
│   ├── train_adaboost.py
│   ├── train_decision_tree.py
│   └── train_random_forest.py
├── preprocessing/
│   ├── create_vocabulary.py
│   └── vectorize_data.py
├── scripts/
│   ├── save_negative_samples.py
│   └── shuffle_data.py
├── models/
│   ├── trained model artifacts
│   └── vocabulary files
├── data/
└── docs/
```

## Folder Purpose

- `training/`: model training scripts.
- `preprocessing/`: vocabulary creation and vectorization scripts.
- `models/`: trained model artifacts and vocabulary files.
- `data/`: dataset files and split outputs.
- `scripts/`: helper scripts for dataset preparation.
- `docs/`: project documentation.

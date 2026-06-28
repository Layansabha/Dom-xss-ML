# Repository Structure

```text
Dom-xss-ML/
├── README.md
├── requirements.txt
├── docs/
│   ├── project-summary.md
│   ├── setup.md
│   └── structure.md
├── src/
│   ├── backend/
│   ├── frontend/
│   │   ├── public/
│   │   └── styles/
│   ├── models/
│   └── pipeline/
├── data/
├── models/
├── reports/
├── notebooks/
├── assets/
├── tests/
├── scripts/
└── config/
```

## Folder Purpose

- `src/backend/`: Flask API and backend services.
- `src/frontend/`: React/frontend files, styles, public assets, and build configuration.
- `src/pipeline/`: DOM extraction, vocabulary creation, feature extraction, and vectorization logic.
- `src/models/`: model training scripts for LightGBM, XGBoost, AdaBoost, Decision Tree, and Random Forest.
- `models/`: trained model artifacts and vocabulary files.
- `data/`: datasets and split files.
- `scripts/`: helper scripts for preprocessing and automation.
- `reports/`: generated reports, evaluation outputs, and screenshots.
- `docs/`: project documentation.
- `assets/`: images, diagrams, and visual project assets.
- `tests/`: unit and integration tests.
- `config/`: configuration files and environment templates.

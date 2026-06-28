# DOM XSS ML

DOM XSS ML is an academic machine learning project for detecting DOM-Based Cross-Site Scripting (DOM XSS) through structural analysis of web page DOM content.

The repository focuses on the data preparation, feature extraction, model training, and trained model artifacts used for DOM XSS classification. It does not include a production frontend or backend application.

## Project Idea

DOM-Based XSS is difficult to detect because the vulnerability happens inside the browser through client-side DOM manipulation. Many traditional scanners depend on payload injection, static signatures, or server-side behavior, which can miss DOM-level vulnerabilities.

This project takes a machine learning approach: DOM samples are collected, cleaned, converted into structural features, and used to train classification models that predict whether a page is vulnerable or non-vulnerable.

## Dataset

The dataset was prepared as part of the project workflow. It contains DOM samples labeled as vulnerable or non-vulnerable.

The vulnerable samples were based on confirmed DOM XSS cases and deliberately vulnerable web applications used for security testing, including Mutillidae. The non-vulnerable samples were collected from clean or non-vulnerable DOM pages to help the models learn the difference between normal and risky DOM structures.

Dataset preparation flow:

1. Collect DOM samples from web pages.
2. Label each sample as vulnerable or non-vulnerable.
3. Clean and normalize DOM content.
4. Build a filtered vocabulary of important DOM tokens.
5. Convert DOM samples into numerical feature vectors.
6. Split the dataset for training, validation, and testing.

The preprocessing code is located in `preprocessing/` and helper scripts are located in `scripts/`.

## Machine Learning Models

The project trains and compares multiple supervised learning models:

- LightGBM
- XGBoost
- AdaBoost
- Decision Tree
- Random Forest
- MLP

Training scripts are stored in `training/`. Saved model artifacts and vocabulary files are stored in `models/`.

## Repository Structure

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
│   ├── lightgbm_best_model_final.pkl
│   ├── xgboost_best_model_final.pkl
│   ├── adaboost_best_model_final.pkl
│   ├── decision_tree_model_final.pkl
│   ├── random_forest_best_model_final.pkl
│   └── vocab_top500_filtered.pkl
├── data/
└── docs/
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Layansabha/Dom-xss-ML.git
cd Dom-xss-ML
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Before running the scripts, make sure the dataset path inside each script points to the correct local dataset file.

## Example Usage

Create vocabulary:

```bash
python preprocessing/create_vocabulary.py
```

Vectorize DOM samples:

```bash
python preprocessing/vectorize_data.py
```

Train a model:

```bash
python training/train_lightgbm.py
```

## Outputs

The training scripts generate model files, evaluation reports, feature-importance outputs, and ROC curve images depending on the selected model.

## Scope

This repository focuses on DOM-Based XSS classification using structural DOM features and machine learning. It does not cover SQL Injection, CSRF, reflected XSS, stored XSS, network security, or mobile security.

## Limitations

- Model quality depends on the size and quality of the labeled dataset.
- Runtime-only DOM XSS cases may require additional browser execution or user interaction to detect.
- The current work is an academic prototype and requires further validation before production use.

## Ethical Use

This project is intended for academic research, cybersecurity learning, and authorized testing only.

## Authors

TRIO Graduation Project

- Layan Hasan Sabha
- Ghazal Hamdi Alzoubi
- Mohammad Mofeed Hattoub

Supervised by Dr. Mamoon Yusef Obiedat and Dr. Majdi Ahmad Maabreh.

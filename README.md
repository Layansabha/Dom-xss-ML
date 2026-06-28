# DOM XSS ML

DOM XSS ML is an academic machine learning project for detecting **DOM-Based Cross-Site Scripting (DOM XSS)** using structural analysis of web page DOM content.

The repository focuses on the machine learning workflow only: dataset cleaning, preprocessing, feature extraction, model training, model comparison, and saved model artifacts. It does not include a production frontend or backend application.

## Overview

DOM-Based XSS is difficult to detect because the vulnerability happens inside the browser through client-side DOM manipulation. Traditional scanners often depend on payload injection, static signatures, or server-side behavior, which can miss DOM-level vulnerabilities.

This project uses a machine learning approach. DOM samples are cleaned, transformed into structural features, and passed into classification models to predict whether a page is vulnerable or non-vulnerable.

## Dataset

The original dataset used in this project is the **DOM XSS Web Vulnerability Dataset** from Carnegie Mellon University's KiltHub:

[DOM XSS Web Vulnerability Dataset](https://kilthub.cmu.edu/articles/dataset/DOM_XSS_Web_Vulnerability_Dataset/13870256)

The dataset was used as the starting point for the ML workflow. It was cleaned, filtered, vectorized, and split into training, validation, and testing sets before model training.

## Data Preparation

The preprocessing stage includes:

1. Loading the original DOM XSS dataset.
2. Cleaning raw DOM samples and removing unusable records.
3. Normalizing DOM content for consistent processing.
4. Building a filtered vocabulary of important DOM tokens.
5. Converting DOM samples into numerical feature vectors.
6. Splitting the processed dataset into training, validation, and testing sets.

The preprocessing scripts are stored in `preprocessing/`, and helper scripts are stored in `scripts/`.

## Models

The project trains and compares multiple supervised machine learning models:

- LightGBM
- XGBoost
- AdaBoost
- Decision Tree
- Random Forest
- MLP

Training scripts are stored in `training/`, while trained model artifacts and vocabulary files are stored in `models/`.

## Results

### Model Comparison

![Model Comparison](docs/results/model-comparison.svg)

### Shared Features Between Random Forest and MLP

![RF and MLP Shared Features](docs/results/rf-mlp-intersection-features.svg)

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
├── data/
└── docs/
    └── results/
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

Before running the scripts, update the dataset path inside each script to match the local dataset location.

## Example Usage

Create the vocabulary:

```bash
python preprocessing/create_vocabulary.py
```

Vectorize the dataset:

```bash
python preprocessing/vectorize_data.py
```

Train a model:

```bash
python training/train_lightgbm.py
```

## Outputs

Depending on the selected model, the training scripts generate:

- Trained model files
- Evaluation reports
- Feature-importance outputs
- ROC curve images

## Scope

This repository focuses on DOM-Based XSS classification using structural DOM features and machine learning. It does not cover SQL Injection, CSRF, reflected XSS, stored XSS, network security, or mobile security.

## Limitations

- Model quality depends on the size and quality of the labeled dataset.
- Runtime-only DOM XSS cases may require additional browser execution or user interaction to detect.
- The current work is an academic prototype and requires further validation before production use.

## Ethical Use

This project is intended for academic research, cybersecurity learning, and authorized testing only.

# DOM XSS ML

DOM XSS ML is an academic cybersecurity project for detecting DOM-Based Cross-Site Scripting (DOM XSS) using structural analysis and machine learning.

Instead of depending only on payload injection or brute-force scanning, the project analyzes the structure of web pages, extracts DOM-based features, and uses trained machine learning models to classify whether a page may be vulnerable to DOM XSS.

## Problem Statement

DOM-Based XSS is difficult to detect because the vulnerability happens inside the browser through client-side DOM manipulation. Traditional scanners often focus on server-side behavior, static rules, or payload-based testing, which can miss vulnerabilities that only appear through JavaScript-driven page behavior.

This project addresses that gap by building a lightweight AI-assisted pipeline that focuses on DOM structure and client-side patterns.

## Dataset

The dataset was prepared as part of the project workflow. It was built from collected and labeled DOM samples representing vulnerable and non-vulnerable web pages.

The vulnerable samples were based on confirmed DOM XSS cases and deliberately vulnerable web applications used for security testing, including Mutillidae. The collected pages were parsed, cleaned, and transformed into a vectorized dataset using DOM feature extraction and vocabulary-based preprocessing.

Dataset preparation flow:

1. Collect accessible web pages and DOM samples.
2. Label samples as vulnerable or non-vulnerable.
3. Parse and clean DOM content.
4. Build a filtered vocabulary of important DOM tokens.
5. Vectorize the dataset for machine learning training.
6. Split the data for training, validation, and testing.

Relevant preprocessing scripts are located in `src/pipeline/` and `scripts/`.

## Pipeline

The detection pipeline follows these stages:

1. User provides a target domain or URL.
2. The system crawls and filters accessible pages.
3. The DOM structure of each page is extracted and cleaned.
4. DOM features are converted into a machine-readable format.
5. A trained model predicts DOM XSS risk.
6. Results are generated with recommendations for mitigation.

## Machine Learning Models

The project compares multiple supervised learning models for DOM XSS classification:

- LightGBM
- XGBoost
- AdaBoost
- Decision Tree
- Random Forest
- MLP

Trained model artifacts are stored in `models/`, while model training scripts are stored in `src/models/`.

## Tech Stack

- Python
- Flask
- React.js
- Selenium
- Beautiful Soup
- Requests
- Pandas
- Scikit-learn
- XGBoost
- LightGBM
- Joblib

## Repository Structure

```text
Dom-xss-ML/
├── README.md
├── requirements.txt
├── docs/
├── src/
│   ├── backend/
│   ├── frontend/
│   ├── models/
│   └── pipeline/
├── data/
├── models/
├── reports/
├── scripts/
├── tests/
├── assets/
└── config/
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

Before running the training scripts, update the dataset paths in the scripts or move the dataset files into the expected project folders.

## Example Usage

Train a model:

```bash
python src/models/train_lightgbm.py
```

Run preprocessing scripts:

```bash
python src/pipeline/create_vocabulary.py
python src/pipeline/vectorize_data.py
```

## Project Scope

This project focuses only on DOM-Based XSS detection. It does not cover other vulnerability classes such as SQL Injection, CSRF, server-side XSS, network security issues, or mobile application security.

## Limitations

- The system depends on the quality and coverage of the collected dataset.
- Runtime-only vulnerabilities may be missed if they require specific user interaction or complex JavaScript execution.
- The current implementation is an academic prototype and may require additional hardening before production use.

## Ethical Use

This repository is intended for academic research, cybersecurity learning, and authorized security testing only. Do not use it to scan or test systems without permission.

## Authors

TRIO Graduation Project

- Layan Hasan Sabha
- Ghazal Hamdi Alzoubi
- Mohammad Mofeed Hattoub

Supervised by Dr. Mamoon Yusef Obiedat and Dr. Majdi Ahmad Maabreh.

## Status

Academic graduation project prototype for DOM-Based XSS detection using structural AI analysis.

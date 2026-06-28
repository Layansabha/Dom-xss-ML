# DOM XSS ML

DOM XSS ML is an academic machine learning project for detecting **DOM-Based Cross-Site Scripting (DOM XSS)** using structural analysis of web page DOM content.

The project focuses on dataset cleaning, preprocessing, feature extraction, model training, model comparison, and saved model artifacts for DOM XSS classification.

## Overview

DOM-Based XSS is difficult to detect because the vulnerability happens inside the browser through user-controlled changes to the Document Object Model. Traditional scanners often depend on payload injection, static signatures, or server-side behavior, which can miss vulnerabilities that appear only through client-side DOM manipulation.

Instead of relying on payloads or brute-force testing, this project uses a machine learning approach. DOM samples are cleaned, transformed into structural features, and passed into classification models to predict whether a page is vulnerable or non-vulnerable.

## Dataset

The original dataset used in this project is the **DOM XSS Web Vulnerability Dataset** from Carnegie Mellon University's KiltHub:

[DOM XSS Web Vulnerability Dataset](https://kilthub.cmu.edu/articles/dataset/DOM_XSS_Web_Vulnerability_Dataset/13870256)

The dataset was used as the starting point for the ML workflow. It was cleaned, filtered, vectorized, and split into training, validation, and testing sets before model training.

## Data Preparation

The preprocessing stage included cleaning raw DOM samples, removing unusable records, normalizing DOM content, building a filtered vocabulary of important DOM tokens, converting the samples into numerical feature vectors, and splitting the processed dataset into training, validation, and testing sets.

## Detection Workflow

The project is designed as a full detection workflow, not only a trained model:

1. DOM samples are prepared from the dataset.
2. DOM content is cleaned and normalized.
3. Structural DOM features are extracted and vectorized.
4. The processed features are passed into trained machine learning models.
5. The models classify the samples as vulnerable or non-vulnerable.
6. Model results are compared to evaluate detection performance.

## Models

The project trains and compares multiple supervised machine learning models:

- LightGBM
- XGBoost
- AdaBoost
- Decision Tree
- Random Forest
- MLP

The trained models were evaluated and compared to identify the strongest approach for DOM XSS classification.

## Results

### Model Comparison

![Model Comparison](docs/results/model-comparison.svg)

### Shared Features Between Random Forest and MLP

![RF and MLP Shared Features](docs/results/rf-mlp-intersection-features.svg)

## Scope

This repository focuses on DOM-Based XSS classification using structural DOM features and machine learning. It does not cover SQL Injection, CSRF, reflected XSS, stored XSS, network security, or mobile security.

## Limitations

- Model quality depends on the size and quality of the labeled dataset.
- Runtime-only DOM XSS cases may require additional browser execution or user interaction to detect.
- The current work is an academic prototype and requires further validation before production use.

## Ethical Use

This project is intended for academic research, cybersecurity learning, and authorized testing only.

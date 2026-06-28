# DOM XSS ML

DOM XSS ML is a graduation project that uses AI to analyze web page DOM structure and classify pages for potential DOM-Based XSS risk.

## Overview

The system receives a domain or URL, collects accessible pages, extracts DOM features, and passes them to trained machine learning models. The output is a report with prediction results and general recommendations.

## Pipeline

1. Enter a domain or URL.
2. Crawl and filter accessible pages.
3. Extract and clean DOM features.
4. Run AI prediction.
5. Generate results and report.

## Models

XGBoost, AdaBoost, LightGBM, Decision Tree, Random Forest, and MLP.

## Tech Stack

Python, Flask, React.js, Selenium, Beautiful Soup, Requests, and machine learning libraries.

## Status

Graduation project prototype for DOM-Based XSS detection using structural AI analysis.

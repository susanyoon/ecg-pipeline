# ECG Signal Pipeline

![CI](https://github.com/susanyoon/ecg-pipeline/actions/workflows/ci.yml/badge.svg)

An end-to-end pipeline over the PTB-XL clinical ECG dataset: ingests 12-lead ECG recordings & metadata, stores them in a normalized PostgreSQL database, extracts signal features, and (in progress) serves them through an API with a baseline diagnostic-class classifier.

> **Note:** This is an engineering demonstration, not a medical device or
> diagnostic tool. Nothing here is validated for clinical use.

## Tech Stack

- Python
- PostgreSQL
- psycopg
- wfdb
- NumPy
- SciPy
- scikit-learn
- FastAPI
- Streamlit
- Docker
- pytest
- ruff

## Status

- [x] Dockerized PostgreSQL database
- [x] Normalized clinical schema (patients, recordings, multi-label diagnoses)
- [x] ETL pipeline: metadata ingestion with label aggregation
- [x] Signal processing and feature extraction
- [ ] Baseline ML classifier with honest evaluation
- [ ] REST API
- [ ] Clinical-facing dashboard

## Data

Uses [PTB-XL](https://physionet.org/content/ptb-xl/), a public dataset of
21,799 clinical 12-lead ECGs from ~18,800 patients, released on PhysioNet
under the Creative Commons Attribution license.

> Wagner et al. (2020). *PTB-XL, a large publicly available electrocardiography
> dataset.* Scientific Data. PhysioNet.

The dataset is not redistributed in this repository; it is downloaded directly
from PhysioNet.
# End-to-End Usage Guide

This guide explains how to rebuild the project exactly from the public repository.

## 1. Clone

```bash
git clone https://github.com/analyticsdurgesh/Retail-Revenue-Intelligence.git
cd Retail-Revenue-Intelligence
```

## 2. Create Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run the Full Pipeline

```bash
bash scripts/run_all.sh
```

This runs:

1. Dataset download.
2. Raw Excel extraction.
3. Data cleaning and feature engineering.
4. Parquet export.
5. SQLite analytics database creation.
6. EDA chart generation.
7. SQL query export.

## 4. Start the Dashboard

```bash
streamlit run dashboard/app.py
```

Open:

```text
http://localhost:8501
```

## 5. What to Look For

- Revenue trend by month.
- Countries driving sales.
- Products driving revenue.
- Customer RFM-style ranking.
- Cancellation risk by country.
- SQL output tables in the dashboard.

## 6. Rebuild From Scratch

Delete generated folders and rerun:

```bash
rm -rf data/raw/* data/processed/* outputs/figures/* outputs/sql_results/*
bash scripts/run_all.sh
```


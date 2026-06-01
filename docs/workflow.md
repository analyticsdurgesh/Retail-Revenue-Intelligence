# Workflow

## 1. Download

`src/download_data.py` downloads the public UCI ZIP file and extracts `Online Retail.xlsx`.

Why this matters: the repository stays lightweight while still making the data source reproducible.

## 2. Clean and Model

`src/prepare_data.py`:

- Standardizes column names.
- Converts invoice timestamps.
- Creates cancellation flags.
- Calculates gross and net revenue.
- Adds month, day, and hour fields.
- Saves a fast Parquet file.
- Builds a SQLite database for SQL analysis.

## 3. EDA

`src/eda.py`:

- Profiles row count, date range, customers, invoices, and countries.
- Builds revenue trend charts.
- Builds top country and top product charts.
- Saves a markdown EDA summary.

## 4. SQL Analysis

`src/sql_analysis.py` and `sql/analysis_queries.sql` answer:

- Revenue trend.
- Country performance.
- Product performance.
- Customer RFM.
- Cancellation risk.

## 5. Dashboard

`dashboard/app.py` uses Streamlit and Plotly to create:

- Interactive country and date filters.
- KPI cards.
- Revenue trend charts.
- Product analysis.
- Customer RFM view.
- SQL result tables.


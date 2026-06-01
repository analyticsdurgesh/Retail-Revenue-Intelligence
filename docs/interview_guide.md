# Interview Guide

Use this project to tell a complete analytics story, not just show charts.

## 30-Second Pitch

I built a retail revenue analytics project using the public UCI Online Retail dataset. It downloads raw data, cleans and models transactions, performs Python EDA, runs SQL analysis in SQLite, and serves an interactive Streamlit dashboard. The project answers revenue, product, country, customer, and cancellation questions in one reproducible workflow.

## Problem Framing

The business wants to understand revenue performance and customer behavior across countries and products. Raw transaction data is not enough; the company needs clean metrics, customer segmentation, and a dashboard leadership can explore.

## Technical Decisions

| Decision | Why it matters |
|---|---|
| Keep raw data out of GitHub | The repo stays lightweight and reproducible. |
| Use Parquet after cleaning | Dashboard reads become fast. |
| Build SQLite analytics DB | SQL skills are visible and reproducible. |
| Export EDA charts | Reviewers can see analysis output quickly. |
| Use Streamlit + Plotly | Dashboard is interactive and easy to run locally. |

## Questions You Can Answer

- How did you clean cancellation transactions?
- Why did you use both Python and SQL?
- What is your definition of revenue?
- How would you convert this to a production dashboard?
- What would you do next if this were a real client project?

## Strong Answer: Python vs SQL

Python was used for ingestion, cleaning, feature engineering, and EDA because it is strong for data profiling and visualization. SQL was used for business questions because it mirrors how analysts query warehouse tables in real companies. The dashboard consumes the processed model so the analytical logic stays reproducible.

## Improvements for Production

- Add dbt models for the SQL transformation layer.
- Schedule refreshes with Airflow.
- Add product/category dimensions.
- Add customer cohort analysis.
- Deploy the dashboard to Streamlit Community Cloud or an internal BI server.


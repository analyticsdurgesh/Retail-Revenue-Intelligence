from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path("data/processed/retail_orders.parquet")

st.set_page_config(page_title="Retail Revenue Intelligence", layout="wide")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    return df


def metric(label: str, value: str) -> None:
    st.metric(label, value)


df = load_data()
sales = df[(~df["is_cancelled"]) & (df["quantity"] > 0) & (df["unit_price"] > 0)].copy()

st.title("Retail Revenue Intelligence")
st.caption("Open-source analytics project using UCI Online Retail data, Python EDA, SQL outputs, and Plotly dashboards.")

with st.sidebar:
    st.header("Filters")
    countries = sorted(sales["country"].dropna().unique())
    selected_countries = st.multiselect("Country", countries, default=countries[:8])
    min_date = sales["invoice_date"].min().date()
    max_date = sales["invoice_date"].max().date()
    date_range = st.date_input("Invoice date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    top_n = st.slider("Top N", 5, 30, 12)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = sales[
    (sales["country"].isin(selected_countries if selected_countries else countries))
    & (sales["invoice_date"].dt.date >= start_date)
    & (sales["invoice_date"].dt.date <= end_date)
].copy()

orders = filtered["invoice_no"].nunique()
customers = filtered["customer_id"].nunique()
revenue = filtered["net_revenue"].sum()
avg_order_value = revenue / orders if orders else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric("Revenue", f"${revenue:,.0f}")
with col2:
    metric("Orders", f"{orders:,}")
with col3:
    metric("Customers", f"{customers:,}")
with col4:
    metric("Avg Order Value", f"${avg_order_value:,.2f}")

tab_overview, tab_products, tab_customers, tab_sql = st.tabs(["Revenue", "Products", "Customers", "SQL Insights"])

with tab_overview:
    monthly = filtered.groupby("month", as_index=False).agg(revenue=("net_revenue", "sum"), orders=("invoice_no", "nunique"))
    country = filtered.groupby("country", as_index=False).agg(revenue=("net_revenue", "sum"), orders=("invoice_no", "nunique")).sort_values("revenue", ascending=False).head(top_n)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue Trend"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(country, x="country", y="revenue", color="orders", title="Top Countries by Revenue"), use_container_width=True)

    day_hour = filtered.groupby(["day_name", "hour"], as_index=False)["net_revenue"].sum()
    st.plotly_chart(px.density_heatmap(day_hour, x="hour", y="day_name", z="net_revenue", title="Revenue Heatmap by Day and Hour"), use_container_width=True)

with tab_products:
    product = filtered.groupby("description", as_index=False).agg(revenue=("net_revenue", "sum"), units=("quantity", "sum")).sort_values("revenue", ascending=False).head(top_n)
    st.plotly_chart(px.bar(product, x="revenue", y="description", orientation="h", color="units", title="Top Products by Revenue"), use_container_width=True)
    st.dataframe(product, use_container_width=True, hide_index=True)

with tab_customers:
    customer = filtered.dropna(subset=["customer_id"]).groupby("customer_id", as_index=False).agg(
        revenue=("net_revenue", "sum"),
        orders=("invoice_no", "nunique"),
        last_purchase=("invoice_date", "max"),
    )
    max_date_ts = filtered["invoice_date"].max()
    customer["recency_days"] = (max_date_ts - customer["last_purchase"]).dt.days
    customer = customer.sort_values("revenue", ascending=False).head(top_n)
    st.plotly_chart(px.scatter(customer, x="orders", y="revenue", size="revenue", color="recency_days", hover_name="customer_id", title="Customer RFM View"), use_container_width=True)
    st.dataframe(customer, use_container_width=True, hide_index=True)

with tab_sql:
    sql_dir = Path("outputs/sql_results")
    files = sorted(sql_dir.glob("*.csv"))
    if not files:
        st.warning("Run `python src/sql_analysis.py` first.")
    for file in files:
        st.subheader(file.stem.replace("_", " ").title())
        st.dataframe(pd.read_csv(file), use_container_width=True, hide_index=True)


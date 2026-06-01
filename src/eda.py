from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATA_PATH = Path("data/processed/retail_orders.parquet")
FIG_DIR = Path("outputs/figures")
REPORT_PATH = Path("outputs/eda_summary.md")


def save_bar(data: pd.DataFrame, x: str, y: str, title: str, file_name: str) -> None:
    plt.figure(figsize=(12, 6))
    sns.barplot(data=data, x=x, y=y, color="#2A9D8F")
    plt.title(title)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / file_name, dpi=160)
    plt.close()


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(DATA_PATH)
    valid_sales = df[(~df["is_cancelled"]) & (df["quantity"] > 0) & (df["unit_price"] > 0)].copy()

    monthly = valid_sales.groupby("month", as_index=False)["net_revenue"].sum()
    top_countries = valid_sales.groupby("country", as_index=False)["net_revenue"].sum().sort_values("net_revenue", ascending=False).head(12)
    top_products = valid_sales.groupby("description", as_index=False)["net_revenue"].sum().sort_values("net_revenue", ascending=False).head(12)

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly, x="month", y="net_revenue", marker="o", color="#264653")
    plt.title("Monthly Revenue Trend")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "monthly_revenue_trend.png", dpi=160)
    plt.close()

    save_bar(top_countries, "country", "net_revenue", "Top Countries by Revenue", "top_countries_revenue.png")
    save_bar(top_products, "description", "net_revenue", "Top Products by Revenue", "top_products_revenue.png")

    report = f"""# EDA Summary

## Dataset Shape

- Rows after base cleaning: {len(df):,}
- Valid sales rows: {len(valid_sales):,}
- Unique invoices: {valid_sales["invoice_no"].nunique():,}
- Unique customers: {valid_sales["customer_id"].nunique():,}
- Countries: {valid_sales["country"].nunique():,}

## Key Metrics

- Total net revenue: ${valid_sales["net_revenue"].sum():,.2f}
- Average order line value: ${valid_sales["net_revenue"].mean():,.2f}
- Cancellation rows: {int(df["is_cancelled"].sum()):,}
- Date range: {valid_sales["invoice_date"].min()} to {valid_sales["invoice_date"].max()}

## Generated Charts

- `outputs/figures/monthly_revenue_trend.png`
- `outputs/figures/top_countries_revenue.png`
- `outputs/figures/top_products_revenue.png`
"""
    REPORT_PATH.write_text(report)
    print(f"EDA report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()


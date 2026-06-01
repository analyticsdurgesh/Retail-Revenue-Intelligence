from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RAW_FILE = Path("data/raw/Online Retail.xlsx")
PROCESSED_DIR = Path("data/processed")
ORDERS_PATH = PROCESSED_DIR / "retail_orders.parquet"
DB_PATH = PROCESSED_DIR / "retail_analytics.sqlite"


def load_raw() -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError("Run `python src/download_data.py` first.")
    return pd.read_excel(RAW_FILE)


def clean_retail(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [c.strip().lower().replace(" ", "_") for c in cleaned.columns]
    cleaned = cleaned.rename(columns={"customerid": "customer_id"})
    cleaned["invoice_date"] = pd.to_datetime(cleaned["invoicedate"], errors="coerce")
    cleaned["invoice_no"] = cleaned["invoiceno"].astype(str)
    cleaned["stock_code"] = cleaned["stockcode"].astype(str)
    cleaned["description"] = cleaned["description"].fillna("Unknown").astype(str).str.strip()
    cleaned["country"] = cleaned["country"].fillna("Unknown").astype(str).str.strip()
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unitprice"], errors="coerce")
    cleaned["customer_id"] = cleaned["customer_id"].astype("Int64").astype("string")
    cleaned["is_cancelled"] = cleaned["invoice_no"].str.startswith("C")
    cleaned["gross_revenue"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned["net_revenue"] = np.where(cleaned["is_cancelled"], 0, cleaned["gross_revenue"])
    cleaned["order_date"] = cleaned["invoice_date"].dt.date.astype("string")
    cleaned["month"] = cleaned["invoice_date"].dt.to_period("M").astype("string")
    cleaned["day_name"] = cleaned["invoice_date"].dt.day_name()
    cleaned["hour"] = cleaned["invoice_date"].dt.hour
    cleaned = cleaned[
        [
            "invoice_no",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
            "is_cancelled",
            "gross_revenue",
            "net_revenue",
            "order_date",
            "month",
            "day_name",
            "hour",
        ]
    ]
    cleaned = cleaned.dropna(subset=["invoice_date", "quantity", "unit_price"])
    return cleaned


def build_sqlite(df: pd.DataFrame) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("retail_orders", conn, index=False, if_exists="replace")
        conn.executescript(
            """
            CREATE INDEX idx_retail_invoice_date ON retail_orders(invoice_date);
            CREATE INDEX idx_retail_country ON retail_orders(country);
            CREATE INDEX idx_retail_customer ON retail_orders(customer_id);
            CREATE INDEX idx_retail_stock ON retail_orders(stock_code);
            """
        )


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    cleaned = clean_retail(raw)
    cleaned.to_parquet(ORDERS_PATH, index=False)
    build_sqlite(cleaned)
    print(f"Rows cleaned: {len(cleaned):,}")
    print(f"Processed file: {ORDERS_PATH}")
    print(f"SQLite database: {DB_PATH}")


if __name__ == "__main__":
    main()


import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

from config import DB_PATH


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS listings_raw (
    run_id TEXT,
    snapshot_ts TEXT,
    portal TEXT,
    segment TEXT,
    transaction_type TEXT,
    listing_id TEXT,
    listing_key TEXT,
    title TEXT,
    location TEXT,
    price REAL,
    price_per_sqm REAL,
    area_sqm REAL,
    advertiser_type TEXT,
    publication_date TEXT,
    listing_age_days REAL,
    reduced_price INTEGER,
    url TEXT,
    source_url TEXT,
    status TEXT,
    extracted_text TEXT
);

CREATE TABLE IF NOT EXISTS listings_unique (
    run_id TEXT,
    snapshot_ts TEXT,
    portal TEXT,
    segment TEXT,
    transaction_type TEXT,
    listing_id TEXT,
    listing_key TEXT,
    title TEXT,
    location TEXT,
    price REAL,
    price_per_sqm REAL,
    area_sqm REAL,
    advertiser_type TEXT,
    publication_date TEXT,
    listing_age_days REAL,
    reduced_price INTEGER,
    url TEXT,
    source_url TEXT,
    status TEXT,
    extracted_text TEXT,
    dedup_group TEXT
);

CREATE TABLE IF NOT EXISTS aggregates (
    run_id TEXT,
    snapshot_ts TEXT,
    segment TEXT,
    transaction_type TEXT,
    metric_name TEXT,
    metric_value REAL
);
"""


def get_connection() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def append_df(df: pd.DataFrame, table_name: str) -> None:
    if df.empty:
        return
    conn = get_connection()
    try:
        df.to_sql(table_name, conn, if_exists="append", index=False)
    finally:
        conn.close()


def read_table(table_name: str, where: Optional[str] = None) -> pd.DataFrame:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()

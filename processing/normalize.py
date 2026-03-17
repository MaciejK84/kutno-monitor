from __future__ import annotations

import hashlib
from datetime import datetime

import pandas as pd


def normalize_listings(df: pd.DataFrame, snapshot_ts: str, run_id: str) -> pd.DataFrame:
    if df.empty:
        return _empty_df()

    out = df.copy()
    out["snapshot_ts"] = snapshot_ts
    out["run_id"] = run_id
    out["location"] = out["location"].fillna("").astype(str).str.strip()
    out = out[out["location"].str.contains("Kutno", case=False, na=False)].copy()

    numeric_cols = ["price", "price_per_sqm", "area_sqm", "reduced_price"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out["advertiser_type"] = out["advertiser_type"].fillna("nieustalone")
    out["publication_date"] = pd.to_datetime(out["publication_date"], errors="coerce")
    snap_dt = pd.to_datetime(snapshot_ts)
    out["listing_age_days"] = (snap_dt - out["publication_date"]).dt.days
    out.loc[out["listing_age_days"] < 0, "listing_age_days"] = None
    out["listing_key"] = out.apply(_build_listing_key, axis=1)

    columns = [
        "run_id",
        "snapshot_ts",
        "portal",
        "segment",
        "transaction",
        "listing_id",
        "listing_key",
        "title",
        "location",
        "price",
        "price_per_sqm",
        "area_sqm",
        "advertiser_type",
        "publication_date",
        "listing_age_days",
        "reduced_price",
        "url",
        "source_url",
        "status",
        "extracted_text",
    ]
    return out[columns].sort_values(["portal", "segment", "transaction", "price"], na_position="last")


def _build_listing_key(row: pd.Series) -> str:
    title = str(row.get("title") or "").lower().strip()
    title = " ".join(title.split())
    area = row.get("area_sqm")
    price = row.get("price")
    loc = str(row.get("location") or "").lower().strip()
    payload = f"{row.get('segment')}|{row.get('transaction')}|{loc}|{round(area or 0,1)}|{round(price or 0,0)}|{title[:80]}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "run_id","snapshot_ts","portal","segment","transaction","listing_id","listing_key","title","location",
            "price","price_per_sqm","area_sqm","advertiser_type","publication_date","listing_age_days",
            "reduced_price","url","source_url","status","extracted_text"
        ]
    )

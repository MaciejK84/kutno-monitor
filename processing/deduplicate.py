from __future__ import annotations

import math
from typing import List

import pandas as pd
from rapidfuzz import fuzz

from config import DEDUP_AREA_TOLERANCE, DEDUP_PRICE_TOLERANCE, DEDUP_TITLE_THRESHOLD


def deduplicate_listings(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        out = df.copy()
        out["dedup_group"] = []
        return out

    df = df.copy().reset_index(drop=True)
    groups = []
    used = set()

    for i, row in df.iterrows():
        if i in used:
            continue
        group = [i]
        used.add(i)
        for j in range(i + 1, len(df)):
            if j in used:
                continue
            if _is_duplicate(row, df.loc[j]):
                group.append(j)
                used.add(j)
        groups.append(group)

    dedup_rows = []
    for gid, idxs in enumerate(groups, start=1):
        subset = df.loc[idxs].copy()
        best = _choose_best(subset)
        best["dedup_group"] = f"G{gid:05d}"
        dedup_rows.append(best)

    return pd.DataFrame(dedup_rows)


def _is_duplicate(a: pd.Series, b: pd.Series) -> bool:
    if a["segment"] != b["segment"] or a["transaction_type"] != b["transaction_type"]:
        return False
    if "kutno" not in str(a.get("location", "")).lower() or "kutno" not in str(b.get("location", "")).lower():
        return False
    title_score = fuzz.token_set_ratio(str(a.get("title", "")), str(b.get("title", "")))
    if title_score < DEDUP_TITLE_THRESHOLD:
        return False
    if not _within_tolerance(a.get("price"), b.get("price"), DEDUP_PRICE_TOLERANCE):
        return False
    if not _within_tolerance(a.get("area_sqm"), b.get("area_sqm"), DEDUP_AREA_TOLERANCE):
        return False
    return True


def _within_tolerance(x, y, tolerance: float) -> bool:
    if pd.isna(x) or pd.isna(y):
        return True
    x = float(x)
    y = float(y)
    if x == 0 and y == 0:
        return True
    base = max(abs(x), abs(y), 1.0)
    return abs(x - y) / base <= tolerance


def _choose_best(df: pd.DataFrame) -> pd.Series:
    score = pd.Series(0, index=df.index, dtype="float")
    score += df["url"].notna().astype(int) * 2
    score += df["price"].notna().astype(int) * 2
    score += df["area_sqm"].notna().astype(int) * 2
    score += df["price_per_sqm"].notna().astype(int) * 1
    score += df["publication_date"].notna().astype(int) * 1
    score += (df["advertiser_type"].fillna("nieustalone") != "nieustalone").astype(int)
    return df.loc[score.sort_values(ascending=False).index[0]].copy()

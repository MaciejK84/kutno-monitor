from __future__ import annotations

import pandas as pd


def compute_aggregates(unique_df: pd.DataFrame, new_df: pd.DataFrame, price_changes_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if unique_df.empty:
        return pd.DataFrame(columns=["segment", "transaction_type_type", "metric_name", "metric_value"])

    for (segment, transaction_type_type), group in unique_df.groupby(["segment", "transaction_type_type"], dropna=False):
        rows.extend(_rows_for_group(segment, transaction_type_type, group, new_df, price_changes_df))

    rows.extend(_rows_for_group("razem", "razem", unique_df, new_df, price_changes_df))
    return pd.DataFrame(rows)


def _rows_for_group(segment, transaction_type_type, group, new_df, price_changes_df):
    subset_new = new_df[(new_df["segment"] == segment) & (new_df["transaction_type_type"] == transaction_type_type)] if segment != "razem" else new_df
    subset_changes = price_changes_df[(price_changes_df["segment"] == segment) & (price_changes_df["transaction_type_type"] == transaction_type_type)] if segment != "razem" else price_changes_df

    biuro_share = ((group["advertiser_type"] == "biuro").mean() * 100) if len(group) else None
    prywatne_share = ((group["advertiser_type"] == "prywatne").mean() * 100) if len(group) else None
    reduced_share = ((group["reduced_price"].fillna(0) > 0).mean() * 100) if len(group) else None

    bins = [0, 100_000, 200_000, 300_000, 500_000, 1_000_000, 9_999_999_999]
    labels = ["0-100k", "100-200k", "200-300k", "300-500k", "500k-1m", ">1m"]
    bucket = pd.cut(group["price"], bins=bins, labels=labels, include_lowest=True)
    distribution = bucket.value_counts(dropna=False).to_dict()

    rows = [
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "count_unique", "metric_value": float(len(group))},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "median_price", "metric_value": _safe_median(group["price"])},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "mean_price_sqm", "metric_value": _safe_mean(group["price_per_sqm"])},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "median_price_sqm", "metric_value": _safe_median(group["price_per_sqm"])},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "median_area_sqm", "metric_value": _safe_median(group["area_sqm"])},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "median_listing_age_days", "metric_value": _safe_median(group["listing_age_days"])},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "share_biuro_pct", "metric_value": biuro_share},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "share_prywatne_pct", "metric_value": prywatne_share},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "share_reduced_pct", "metric_value": reduced_share},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "new_listings_count", "metric_value": float(len(subset_new))},
        {"segment": segment, "transaction_type_type": transaction_type, "metric_name": "price_changes_count", "metric_value": float(len(subset_changes))},
    ]
    for label, value in distribution.items():
        if pd.isna(label):
            continue
        rows.append(
            {
                "segment": segment,
                "transaction_type_type": transaction_type_type,
                "metric_name": f"price_bucket_{label}",
                "metric_value": float(value),
            }
        )
    return rows


def _safe_mean(series: pd.Series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    return float(s.mean()) if len(s) else None


def _safe_median(series: pd.Series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    return float(s.median()) if len(s) else None

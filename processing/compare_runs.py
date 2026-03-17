from __future__ import annotations

import pandas as pd


def compare_with_previous(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if current_df.empty:
        return current_df.iloc[0:0].copy(), current_df.iloc[0:0].copy()

    if previous_df.empty:
        return current_df.copy(), current_df.iloc[0:0].copy()

    prev = previous_df[["listing_key", "price"]].drop_duplicates().rename(columns={"price": "previous_price"})
    merged = current_df.merge(prev, on="listing_key", how="left")

    new_listings = merged[merged["previous_price"].isna()].copy()
    price_changes = merged[
        merged["previous_price"].notna() &
        merged["price"].notna() &
        (merged["price"] != merged["previous_price"])
    ].copy()
    if not price_changes.empty:
        price_changes["price_delta"] = price_changes["price"] - price_changes["previous_price"]
        price_changes["price_delta_pct"] = (price_changes["price_delta"] / price_changes["previous_price"]).round(4)
    return new_listings, price_changes

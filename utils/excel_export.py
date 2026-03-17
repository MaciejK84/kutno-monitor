from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_report(output_path: Path, aggregates: pd.DataFrame, history: pd.DataFrame, unique_df: pd.DataFrame,
                  raw_df: pd.DataFrame, new_df: pd.DataFrame, price_changes_df: pd.DataFrame) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        aggregates.to_excel(writer, sheet_name="aggregates", index=False)
        history.to_excel(writer, sheet_name="history", index=False)
        unique_df.to_excel(writer, sheet_name="unique_listings", index=False)
        raw_df.to_excel(writer, sheet_name="raw_listings", index=False)
        new_df.to_excel(writer, sheet_name="new_listings", index=False)
        price_changes_df.to_excel(writer, sheet_name="price_changes", index=False)

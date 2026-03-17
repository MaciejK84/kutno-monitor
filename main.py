from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import PROCESSED_DIR, RAW_DIR, REPORTS_DIR, SEARCHES
from processing.compare_runs import compare_with_previous
from processing.deduplicate import deduplicate_listings
from processing.metrics import compute_aggregates
from processing.normalize import normalize_listings
from scrapers import PARSERS
from scrapers.common import fetch_page
from utils.db import append_df, init_db, read_table
from utils.excel_export import export_report
from utils.logging_config import setup_logging


def run() -> Path:
    setup_logging()
    init_db()

    snapshot_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_rows = []
    for search in SEARCHES:
        portal = search["portal"]
        parser = PARSERS[portal]
        meta = {
            "portal": portal,
            "segment": search["segment"],
            "transaction": search["transaction"],
            "source_url": search["url"],
        }
        try:
            payload = fetch_page(search["url"])
            rows = parser(payload, meta)
            logging.info("%s | %s | %s -> %s rekordów", portal, search["segment"], search["transaction"], len(rows))
            all_rows.extend(rows)
        except Exception as exc:
            logging.exception("Błąd przy %s | %s | %s: %s", portal, search["segment"], search["transaction"], exc)

    raw_df = pd.DataFrame(all_rows)
    normalized_df = normalize_listings(raw_df, snapshot_ts=snapshot_ts, run_id=run_id)
    unique_df = deduplicate_listings(normalized_df)

    previous_df = read_table("listings_unique", where=f"run_id = (SELECT MAX(run_id) FROM listings_unique WHERE run_id < '{run_id}')")
    new_df, price_changes_df = compare_with_previous(unique_df, previous_df)

    if not price_changes_df.empty:
        unique_df.loc[unique_df["listing_key"].isin(price_changes_df["listing_key"]), "reduced_price"] = 1

    aggregates = compute_aggregates(unique_df, new_df, price_changes_df)
    if not aggregates.empty:
        aggregates["run_id"] = run_id
        aggregates["snapshot_ts"] = snapshot_ts
        aggregates = aggregates[["run_id", "snapshot_ts", "segment", "transaction", "metric_name", "metric_value"]]

    append_df(normalized_df, "listings_raw")
    append_df(unique_df, "listings_unique")
    append_df(aggregates, "aggregates")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_csv = PROCESSED_DIR / f"raw_{run_id}.csv"
    uniq_csv = PROCESSED_DIR / f"unique_{run_id}.csv"
    agg_csv = PROCESSED_DIR / f"aggregates_{run_id}.csv"
    normalized_df.to_csv(raw_csv, index=False, encoding="utf-8-sig")
    unique_df.to_csv(uniq_csv, index=False, encoding="utf-8-sig")
    aggregates.to_csv(agg_csv, index=False, encoding="utf-8-sig")

    history = read_table("aggregates")
    report_path = REPORTS_DIR / f"kutno_monitor_{run_id}.xlsx"
    export_report(report_path, aggregates, history, unique_df, normalized_df, new_df, price_changes_df)

    logging.info("Raport zapisany: %s", report_path)
    return report_path


if __name__ == "__main__":
    run()

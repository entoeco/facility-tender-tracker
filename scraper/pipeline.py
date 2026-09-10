"""Orchestrates a full scrape run: fetch -> normalize -> keyword-filter -> store."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DEFAULT_MIN_SCORE  # noqa: E402
from scraper import db  # noqa: E402
from scraper.filter import score_all  # noqa: E402
from scraper.normalize import (  # noqa: E402
    is_open_tender_release,
    normalize_contracts_finder,
    normalize_find_a_tender,
)
from scraper.sources import fetch_contracts_finder_releases, fetch_find_a_tender_releases  # noqa: E402


def run_pipeline(days_back: int = 21, min_score: int = DEFAULT_MIN_SCORE) -> dict:
    """Runs one full scrape + filter + store cycle. Returns a summary dict for the UI."""
    summary = {"errors": []}

    cf_records: list[dict] = []
    try:
        cf_releases = fetch_contracts_finder_releases(days_back=days_back)
        cf_records = [
            r for rel in cf_releases if is_open_tender_release(rel)
            for r in [normalize_contracts_finder(rel)] if r
        ]
    except Exception as exc:  # noqa: BLE001
        summary["errors"].append(f"Contracts Finder: {exc}")

    fts_records: list[dict] = []
    try:
        fts_releases = fetch_find_a_tender_releases(days_back=days_back)
        fts_records = [
            r for rel in fts_releases if is_open_tender_release(rel)
            for r in [normalize_find_a_tender(rel)] if r
        ]
    except Exception as exc:  # noqa: BLE001
        summary["errors"].append(f"Find a Tender: {exc}")

    all_records = cf_records + fts_records
    matched = score_all(all_records, min_score=min_score)

    conn = db.get_connection()
    new_count, updated_count = db.upsert_opportunities(conn, matched)
    conn.close()

    summary.update(
        {
            "fetched_cf": len(cf_records),
            "fetched_fts": len(fts_records),
            "matched": len(matched),
            "new": new_count,
            "updated": updated_count,
        }
    )
    return summary


if __name__ == "__main__":
    result = run_pipeline()
    print(result)

"""SQLite persistence: opportunities found by the scraper + user review status.

Two tables are kept separate on purpose: `opportunities` is fully overwritten by
each scrape (source data), while `status` is only ever written by the user via
the Streamlit app, so a refresh never clobbers someone's "applied" / "dismissed"
marking.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "opportunities.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    notice_key      TEXT PRIMARY KEY,
    source          TEXT,
    title           TEXT,
    description     TEXT,
    buyer           TEXT,
    value_amount    REAL,
    value_currency  TEXT,
    published_date  TEXT,
    deadline        TEXT,
    cpv_code        TEXT,
    cpv_description TEXT,
    url             TEXT,
    matched_tags    TEXT,
    score           INTEGER,
    first_seen      TEXT,
    last_seen       TEXT
);

CREATE TABLE IF NOT EXISTS status (
    notice_key TEXT PRIMARY KEY,
    status     TEXT DEFAULT 'new',
    notes      TEXT DEFAULT '',
    updated_at TEXT,
    FOREIGN KEY (notice_key) REFERENCES opportunities(notice_key)
);
"""

VALID_STATUSES = ("new", "seen", "dismissed", "applied")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: Streamlit can rerun the script on a different
    # thread than the one that created this cached connection.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_opportunities(conn: sqlite3.Connection, records: list[dict]) -> tuple[int, int]:
    """Insert new opportunities / refresh existing ones. Returns (new_count, updated_count)."""
    now = datetime.now(timezone.utc).isoformat()
    new_count = 0
    updated_count = 0

    for r in records:
        existing = conn.execute(
            "SELECT notice_key FROM opportunities WHERE notice_key = ?", (r["notice_key"],)
        ).fetchone()

        conn.execute(
            """
            INSERT INTO opportunities
                (notice_key, source, title, description, buyer, value_amount, value_currency,
                 published_date, deadline, cpv_code, cpv_description, url, matched_tags, score,
                 first_seen, last_seen)
            VALUES (:notice_key, :source, :title, :description, :buyer, :value_amount, :value_currency,
                    :published_date, :deadline, :cpv_code, :cpv_description, :url, :matched_tags, :score,
                    :first_seen, :last_seen)
            ON CONFLICT(notice_key) DO UPDATE SET
                source=excluded.source, title=excluded.title, description=excluded.description,
                buyer=excluded.buyer, value_amount=excluded.value_amount, value_currency=excluded.value_currency,
                published_date=excluded.published_date, deadline=excluded.deadline, cpv_code=excluded.cpv_code,
                cpv_description=excluded.cpv_description, url=excluded.url, matched_tags=excluded.matched_tags,
                score=excluded.score, last_seen=excluded.last_seen
            """,
            {
                **r,
                "matched_tags": json.dumps(r.get("matched_tags", [])),
                "first_seen": now,
                "last_seen": now,
            },
        )

        if existing is None:
            new_count += 1
            conn.execute(
                "INSERT OR IGNORE INTO status (notice_key, status, updated_at) VALUES (?, 'new', ?)",
                (r["notice_key"], now),
            )
        else:
            updated_count += 1

    conn.commit()
    return new_count, updated_count


def fetch_opportunities(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT o.*, COALESCE(s.status, 'new') AS status, COALESCE(s.notes, '') AS notes
        FROM opportunities o
        LEFT JOIN status s ON s.notice_key = o.notice_key
        ORDER BY o.published_date DESC
        """
    ).fetchall()

    results = []
    for row in rows:
        d = dict(row)
        try:
            d["matched_tags"] = json.loads(d["matched_tags"] or "[]")
        except json.JSONDecodeError:
            d["matched_tags"] = []
        results.append(d)
    return results


def update_status(conn: sqlite3.Connection, notice_key: str, status: str, notes: str | None = None) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    now = datetime.now(timezone.utc).isoformat()
    if notes is None:
        conn.execute(
            """
            INSERT INTO status (notice_key, status, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(notice_key) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at
            """,
            (notice_key, status, now),
        )
    else:
        conn.execute(
            """
            INSERT INTO status (notice_key, status, notes, updated_at) VALUES (?, ?, ?, ?)
            ON CONFLICT(notice_key) DO UPDATE SET status=excluded.status, notes=excluded.notes, updated_at=excluded.updated_at
            """,
            (notice_key, status, notes, now),
        )
    conn.commit()

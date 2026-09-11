"""Streamlit dashboard: Sussex technical facilities - external tender/opportunity tracker.

Sources: UK Contracts Finder + Find a Tender (OCDS APIs), filtered against a
keyword list of Sussex facilities and relevant research/industry sectors.
No LLM involved - matching is plain keyword scoring, and nothing is drafted
or submitted automatically. Refresh is manual (button below).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ALL_KEYWORDS, FACILITY_KEYWORDS, SECTOR_KEYWORDS  # noqa: E402
from scraper import db  # noqa: E402
from scraper.pipeline import run_pipeline  # noqa: E402

st.set_page_config(page_title="Sussex Facilities - Opportunity Tracker", layout="wide")

STATUS_OPTIONS = ["new", "seen", "dismissed", "applied"]


@st.cache_resource
def get_conn():
    return db.get_connection()


def load_df() -> pd.DataFrame:
    conn = get_conn()
    records = db.fetch_opportunities(conn)
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce", utc=True)
    df["deadline"] = pd.to_datetime(df["deadline"], errors="coerce", utc=True)
    return df


st.title("Sussex Technical Facilities — Opportunity Tracker")
st.caption(
    "Scrapes Contracts Finder + Find a Tender for open UK public tenders, scores them against "
    "Sussex's technical facilities and relevant sectors, and lists matches below. Keyword matching "
    "only — no AI drafting, nothing is submitted automatically."
)

with st.sidebar:
    st.header("Refresh")
    days_back = st.slider(
        "Look back (days)", min_value=7, max_value=60, value=7,
        help=(
            "Contracts Finder and Find a Tender have no keyword search of their own, "
            "so every notice in this window has to be pulled and scanned locally. "
            "7 days (matching a weekly refresh) usually finishes in a couple of minutes; "
            "60 days can take 10+ minutes and may not reach every notice in the window."
        ),
    )
    if st.button("Refresh now", type="primary"):
        with st.spinner(
            "Fetching from Contracts Finder and Find a Tender... "
            "these APIs are slow (a longer lookback can take a couple of minutes)."
        ):
            result = run_pipeline(days_back=days_back)
        get_conn.clear()
        if result.get("errors"):
            for err in result["errors"]:
                st.error(err)
        st.success(
            f"Scanned {result.get('raw_cf', 0)} (Contracts Finder) + "
            f"{result.get('raw_fts', 0)} (Find a Tender) notices in the window, "
            f"of which {result.get('fetched_cf', 0)} + {result.get('fetched_fts', 0)} "
            f"were open tenders. {result.get('matched', 0)} matched keywords — "
            f"{result.get('new', 0)} new, {result.get('updated', 0)} updated."
        )

    st.divider()
    st.header("Filters")
    facility_filter = st.multiselect("Facility", options=list(FACILITY_KEYWORDS.keys()))
    sector_filter = st.multiselect("Sector", options=list(SECTOR_KEYWORDS.keys()))
    status_filter = st.multiselect("Status", options=STATUS_OPTIONS, default=["new", "seen"])
    min_score = st.slider("Minimum match score", min_value=1, max_value=5, value=1)
    text_search = st.text_input("Search title/description")

df = load_df()

if df.empty:
    st.info("No opportunities stored yet. Click **Refresh now** in the sidebar to run the first scrape.")
    st.stop()

filtered = df.copy()

if status_filter:
    filtered = filtered[filtered["status"].isin(status_filter)]

filtered = filtered[filtered["score"] >= min_score]

if facility_filter or sector_filter:
    wanted_tags = set(facility_filter) | set(sector_filter)
    filtered = filtered[filtered["matched_tags"].apply(lambda tags: bool(wanted_tags & set(tags)))]

if text_search:
    needle = text_search.lower()
    filtered = filtered[
        filtered["title"].str.lower().str.contains(needle, na=False)
        | filtered["description"].str.lower().str.contains(needle, na=False)
    ]

st.subheader(f"{len(filtered)} opportunities")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total tracked", len(df))
col2.metric("New", int((df["status"] == "new").sum()))
col3.metric("Applied", int((df["status"] == "applied").sum()))
col4.metric(
    "Closing within 14 days",
    int((filtered["deadline"] - pd.Timestamp.now(tz=timezone.utc) < pd.Timedelta(days=14)).sum()),
)

filtered = filtered.sort_values("published_date", ascending=False)

for _, row in filtered.iterrows():
    deadline_str = row["deadline"].strftime("%Y-%m-%d") if pd.notna(row["deadline"]) else "n/a"
    published_str = row["published_date"].strftime("%Y-%m-%d") if pd.notna(row["published_date"]) else "n/a"
    value_str = f"£{row['value_amount']:,.0f}" if pd.notna(row["value_amount"]) else "n/a"
    tags_str = ", ".join(row["matched_tags"]) if row["matched_tags"] else "n/a"

    with st.container(border=True):
        header_col, status_col = st.columns([5, 1])
        with header_col:
            st.markdown(f"**[{row['title']}]({row['url']})**")
            st.caption(f"{row['source']} · {row['buyer']} · Published {published_str} · Deadline {deadline_str} · {value_str}")
            st.caption(f"Matched: {tags_str} (score {row['score']})")
            with st.expander("Description"):
                st.write(row["description"] or "No description provided.")
        with status_col:
            new_status = st.selectbox(
                "Status",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(row["status"]) if row["status"] in STATUS_OPTIONS else 0,
                key=f"status_{row['notice_key']}",
                label_visibility="collapsed",
            )
            if new_status != row["status"]:
                db.update_status(get_conn(), row["notice_key"], new_status)
                st.rerun()

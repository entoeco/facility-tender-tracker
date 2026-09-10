"""Fetches raw OCDS release data from UK public procurement APIs.

Both Contracts Finder and Find a Tender publish notices as OCDS (Open Contracting
Data Standard) release packages. Neither API supports keyword search server-side,
so we pull every notice published/updated in a recent window and filter locally
(see filter.py).
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests

CF_SEARCH_URL = "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
FTS_SEARCH_URL = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"

HEADERS = {"Accept": "application/json", "User-Agent": "sussex-facility-tender-tracker/1.0"}

MAX_PAGES = 20          # safety cap per source per run
REQUEST_DELAY_SECONDS = 0.4
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 2
SOURCE_TIME_BUDGET_SECONDS = 25  # both source APIs are prone to going flaky for
                                  # minutes at a time; cap wall-clock time per
                                  # source so a manual refresh never hangs the UI


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _get_with_retries(url: str, params: dict | None) -> requests.Response:
    """GET with retries on transient server errors (both gov.uk procurement APIs
    are prone to intermittent 502s / momentarily-empty responses under load)."""
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            last_exc = exc
        else:
            if resp.status_code < 500:
                return resp
            last_exc = requests.HTTPError(f"{resp.status_code} from {resp.url}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
    raise last_exc or RuntimeError("request failed with no exception captured")


def _fetch_paginated(url: str, params: dict) -> list[dict]:
    """Paginates through a source, always returning whatever was collected so far
    rather than raising - a page that keeps failing (or a source having a bad
    day) should degrade to a partial/empty result, not blow up the whole run or
    hang the UI indefinitely."""
    releases: list[dict] = []
    next_params: dict | None = params
    deadline = time.monotonic() + SOURCE_TIME_BUDGET_SECONDS

    for page in range(MAX_PAGES):
        if time.monotonic() > deadline:
            break
        try:
            resp = _get_with_retries(url, next_params if page == 0 else None)
        except requests.RequestException:
            break  # gave up on this page after retries; keep what we have so far

        if resp.status_code == 403:
            break  # rate-limited; stop gracefully and use what we have
        if resp.status_code >= 400:
            break
        payload = resp.json()
        releases.extend(payload.get("releases", []))

        next_url = payload.get("links", {}).get("next")
        if not next_url:
            break
        url = next_url
        time.sleep(REQUEST_DELAY_SECONDS)

    return releases


def fetch_contracts_finder_releases(days_back: int = 21) -> list[dict]:
    """Pull notices published in the last `days_back` days; caller filters by tag/stage.

    Note: the API's own `stages` filter causes slow queries that the backend
    times out on (502), so we pull everything in the date window unfiltered and
    apply the tender/active filter locally instead (same approach as Find a Tender).
    """
    published_from = _iso(datetime.now(timezone.utc) - timedelta(days=days_back))
    return _fetch_paginated(CF_SEARCH_URL, {"publishedFrom": published_from, "limit": 100})


def fetch_find_a_tender_releases(days_back: int = 21) -> list[dict]:
    """Pull notices updated in the last `days_back` days; caller filters by tag/stage."""
    updated_from = _iso(datetime.now(timezone.utc) - timedelta(days=days_back))
    return _fetch_paginated(FTS_SEARCH_URL, {"updatedFrom": updated_from, "limit": 100})

"""Keyword scoring: tags each normalized opportunity with matched facilities/sectors."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ALL_KEYWORDS  # noqa: E402

# Word-boundary matching (not plain substring) so short keywords like "ivd" or
# "tem imaging" don't false-positive inside unrelated words, e.g. "system imaging".
_TAG_PATTERNS = {
    tag: re.compile(
        "|".join(rf"\b{re.escape(kw)}\b" for kw in keywords),
        re.IGNORECASE,
    )
    for tag, keywords in ALL_KEYWORDS.items()
}


def score_opportunity(record: dict) -> dict:
    """Adds matched_tags (list[str]) and score (int) to a normalized record."""
    haystack = f"{record.get('title', '')} {record.get('description', '')}"
    matched = [tag for tag, pattern in _TAG_PATTERNS.items() if pattern.search(haystack)]
    record["matched_tags"] = matched
    record["score"] = len(matched)
    return record


def score_all(records: list[dict], min_score: int = 1) -> list[dict]:
    scored = [score_opportunity(dict(r)) for r in records]
    return [r for r in scored if r["score"] >= min_score]

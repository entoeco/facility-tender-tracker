"""Converts raw OCDS releases from either source into one common record shape."""

from __future__ import annotations

from typing import Any, Optional


def _buyer_name(release: dict) -> Optional[str]:
    buyer = release.get("buyer") or {}
    if buyer.get("name"):
        return buyer["name"]
    for party in release.get("parties", []) or []:
        if "buyer" in (party.get("roles") or []):
            return party.get("name")
    return None


def _cf_notice_url(tender: dict, ocid: str) -> str:
    for doc in tender.get("documents", []) or []:
        if doc.get("documentType") == "tenderNotice" and doc.get("url"):
            return doc["url"]
    for doc in tender.get("documents", []) or []:
        if doc.get("url"):
            return doc["url"]
    return f"https://www.contractsfinder.service.gov.uk/Notice/{ocid}"


def normalize_contracts_finder(release: dict) -> Optional[dict[str, Any]]:
    tender = release.get("tender") or {}
    if not tender.get("title"):
        return None
    ocid = release.get("ocid", "")
    classification = tender.get("classification") or {}
    value = tender.get("value") or {}
    return {
        "source": "Contracts Finder",
        "notice_key": f"cf:{ocid}",
        "title": tender.get("title", "").strip(),
        "description": (tender.get("description") or "").strip(),
        "buyer": _buyer_name(release) or "",
        "value_amount": value.get("amount"),
        "value_currency": value.get("currency"),
        "published_date": tender.get("datePublished") or release.get("date"),
        "deadline": (tender.get("tenderPeriod") or {}).get("endDate"),
        "cpv_code": classification.get("id"),
        "cpv_description": classification.get("description"),
        "url": _cf_notice_url(tender, ocid),
    }


def normalize_find_a_tender(release: dict) -> Optional[dict[str, Any]]:
    tender = release.get("tender") or {}
    if not tender.get("title"):
        return None
    notice_id = release.get("id", "")
    classification = tender.get("classification") or {}
    value = tender.get("value") or {}
    return {
        "source": "Find a Tender",
        "notice_key": f"fts:{release.get('ocid', notice_id)}",
        "title": tender.get("title", "").strip(),
        "description": (tender.get("description") or "").strip(),
        "buyer": _buyer_name(release) or "",
        "value_amount": value.get("amount"),
        "value_currency": value.get("currency"),
        "published_date": tender.get("datePublished") or release.get("date"),
        "deadline": (tender.get("tenderPeriod") or {}).get("endDate"),
        "cpv_code": classification.get("id"),
        "cpv_description": classification.get("description"),
        "url": f"https://www.find-tender.service.gov.uk/Notice/{notice_id}",
    }


def is_open_tender_release(release: dict) -> bool:
    """True if this release represents a currently-open tender notice (not an award/planning notice)."""
    tags = release.get("tag") or []
    if "tender" not in tags:
        return False
    tender = release.get("tender") or {}
    return (tender.get("status") or "").lower() == "active"

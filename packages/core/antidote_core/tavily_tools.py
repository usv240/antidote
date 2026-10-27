"""Tavily tool for Antidote: resolve a pesticide brand name to its active ingredient when the registry has no row.

Results are labelled web-sourced and unverified; the pipeline caps match confidence so the antidote row stays
suppressed until a human confirms. Restricted to regulator and manufacturer domains where possible.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from antidote_llm import CallRecord, Ledger

DOMAINS = ["ppqs.gov.in", "cibrc.gov.in", "fssai.gov.in", "who.int", "syngenta.co.in", "bayer.in", "upl-ltd.com", "fmc.com", "corteva.in", "dhanuka.com", "indiamart.com", "bighaat.com", "agribegri.com", "krishisevakendra.in"]


def _client():
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return None
    from tavily import TavilyClient

    return TavilyClient(api_key=key)


def resolve_brand(brand: str, *, ledger: Ledger | None = None, trace_id: str | None = None) -> dict[str, Any]:
    c = _client()
    if not c:
        return {"available": False, "reason": "TAVILY_API_KEY not set", "results": []}
    q = f'"{brand}" pesticide active ingredient composition India'
    t0 = time.perf_counter()
    try:
        r = c.search(q, search_depth="advanced", max_results=5, include_domains=DOMAINS)
        if ledger:
            ledger.record(CallRecord(trace_id or str(uuid.uuid4()), "tool", "Tavily", "tavily/search", "tavily.resolve_brand", 0, 0, 0.0, int((time.perf_counter() - t0) * 1000)))
        return {"available": True, "query": q, "unverified": True, "results": [{"title": x.get("title"), "url": x.get("url"), "snippet": (x.get("content") or "")[:300]} for x in r.get("results", [])]}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": type(e).__name__, "results": []}


def brand_votes(web: dict[str, Any], ais: list[dict[str, Any]]) -> list[tuple[dict[str, Any], int]]:
    """Registry chemicals mentioned in brand search results, most-mentioned first. Pages often list other products,
    so a single mention is weak evidence; callers act only on a clear winner."""
    import re

    blob = " ".join((r.get("title") or "") + " " + (r.get("snippet") or "") for r in web.get("results", [])).lower()
    votes = [(a, len(re.findall(rf"(?<![a-z]){re.escape(a['name'].lower())}(?![a-z])", blob))) for a in ais]
    return sorted([v for v in votes if v[1]], key=lambda v: v[1], reverse=True)


def clear_winner(votes: list[tuple[dict[str, Any], int]]) -> dict[str, Any] | None:
    if not votes:
        return None
    if len(votes) == 1 or votes[0][1] > votes[1][1]:
        return votes[0][0]
    return None

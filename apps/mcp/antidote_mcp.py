"""Antidote as an MCP server: any agent can read a pesticide label, get the cited card or stop, and file the register row.

Run over stdio: uv run python apps/mcp/antidote_mcp.py
"""

from __future__ import annotations

import base64
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parents[2]
for _env in (ROOT / ".env", ROOT.parent / ".env"):
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from antidote_core import ChemRegistry
from antidote_core.pipeline import NPIC, AntidotePipeline
from antidote_llm import Ledger, TokenFactoryClient
from antidote_retrieval import PageStore
from antidote_vision import describe

mcp = MCPServer("antidote", instructions=f"Pesticide-label decision support for trained clinicians. Airway, breathing, circulation first. {NPIC}.")
LEDGER = Ledger(ROOT / "data/ledger.db")
STORE = PageStore(ROOT / "data/index/antidote.db")
REGISTRY = ChemRegistry()
try:
    CLIENT: TokenFactoryClient | None = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = AntidotePipeline(CLIENT, STORE, REGISTRY)


@mcp.tool()
def classify_chemical(active_ingredient: str) -> dict[str, Any]:
    """WHO 2019 hazard class, chemical group, India registration status and whether a specific antidote exists, from the parsed registry."""
    from antidote_core import LabelFields

    m = REGISTRY.match(LabelFields(active_ingredients=[{"name": active_ingredient}]))
    if not m:
        return {"found": False}
    g = REGISTRY.group(m[0].group) or {}
    return {"found": True, "active_ingredient": m[0].active_ingredient, "group": g.get("name"), "who_class": m[0].who_class, "india_status": m[0].india_status, "antidote_exists": g.get("antidote_exists"), "confidence": m[0].confidence}


@mcp.tool()
def read_label_photo(image_base64: str) -> dict[str, Any]:
    """Read the fields printed on a pesticide label photo (product, active ingredient, registration number, triangle colour, antidote statement)."""
    vr = describe(base64.b64decode(image_base64))
    return {"mode": vr.mode, "raw": vr.raw[:2000], "notes": vr.notes}


@mcp.tool()
def analyze_label(label: dict[str, Any], context: dict[str, str] | None = None, audit: bool = True) -> dict[str, Any]:
    """Full card: identity, expected toxidrome, cited management, cautions, stop cards. Every clinical sentence is a verbatim quote from a cited guideline page; a deterministic verifier and an Ultra audit check it."""
    r = PIPE.analyze(raw_label=label, context=context or {}, audit=audit)
    return {"trace_id": r.trace_id, "banner": r.banner, "chosen": r.chosen.__dict__ if r.chosen else None, "group": r.group, "guarded": r.guarded, "stops": r.stops, "card": r.card.model_dump() if r.card else None, "citations": {k: v for k, v in r.citation_report.items() if k != "failures"}, "audit": r.audit.overall if r.audit else None, "notes": r.notes, "trace": LEDGER.trace(r.trace_id)}


@mcp.tool()
def read_guideline_page(doc_id: str, page: int) -> dict[str, Any]:
    """Return the text of a cited guideline page so a clinician can verify a quote."""
    meta = STORE.doc_meta(doc_id) or {}
    return {"doc_id": doc_id, "page": page, "title": meta.get("title"), "source_url": meta.get("source_url"), "text": STORE.page_text(doc_id, page) or "(page not indexed)"}


@mcp.tool()
def file_mlc_record(alleged_history: str, substance_product: str | None = None, substance_active_ingredient: str | None = None, route: str | None = None, doctor: str | None = None, ai_trace_id: str = "") -> dict[str, Any]:
    """File a medico-legal case register row (NHSRC fields). Patient identifiers are entered by staff in the register itself."""
    row = {"id": str(uuid.uuid4()), "created_at": time.time(), "datetime": time.strftime("%Y-%m-%d %H:%M"), "alleged_history": alleged_history, "substance_product": substance_product, "substance_active_ingredient": substance_active_ingredient, "route": route, "doctor": doctor, "ai_trace_id": ai_trace_id, "poison_centre_called": False}
    with (ROOT / "data/mlc_register.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


if __name__ == "__main__":
    mcp.run(transport=os.environ.get("ANTIDOTE_MCP_TRANSPORT", "stdio"))

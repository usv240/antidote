"""Antidote API. OpenAPI at /docs. Runs in replay mode without a model key so the demo never dead-ends."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from antidote_core import ChemRegistry
from antidote_core.pipeline import NPIC, AntidotePipeline
from antidote_core.schemas import MLCRecord
from antidote_llm import Ledger, TokenFactoryClient
from antidote_retrieval import PageStore
from antidote_vision import describe
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[3]
for _env in (ROOT / ".env", ROOT.parent / ".env"):
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

app = FastAPI(title="Antidote API", version="0.1.0", description="Photograph a pesticide label; get the chemical, its WHO hazard class, cited poisoning guidance or an explicit stop, and a medico-legal register row. Decision support for trained clinicians.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LEDGER = Ledger(ROOT / "data/ledger.db")
STORE = PageStore(ROOT / "data/index/antidote.db")
REGISTRY = ChemRegistry()
try:
    CLIENT: TokenFactoryClient | None = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = AntidotePipeline(CLIENT, STORE, REGISTRY)
RECORDS = ROOT / "data/mlc_register.jsonl"

LABEL_PROMPT = (
    "You are reading a photo of a pesticide container label for a doctor. Return ONLY a JSON object with keys: product_name, "
    "active_ingredients (list of {name, percent} exactly as printed), formulation_code, registration_number (e.g. CIR-...), batch, expiry, "
    "manufacturer, triangle_colour (red, yellow, blue or green if a coloured triangle or band is visible), signal_word, antidote_statement_text "
    "(the antidote sentence exactly as printed, or null), visible_text (list of strings as printed), languages_seen (list), confidence (0 to 1). "
    "Do not infer anything not visible; use null."
)


class AnalyzeBody(BaseModel):
    label: dict[str, Any]
    context: dict[str, str] = {}
    chosen_ai: str | None = None
    audit: bool = True


def _result_json(res) -> dict[str, Any]:
    return {
        "trace_id": res.trace_id,
        "banner": res.banner,
        "label": res.label.model_dump(),
        "matches": [m.__dict__ for m in res.matches],
        "chosen": res.chosen.__dict__ if res.chosen else None,
        "group": res.group,
        "triangle": res.triangle,
        "guarded": res.guarded,
        "stops": res.stops,
        "card": res.card.model_dump() if res.card else None,
        "audit": res.audit.model_dump() if res.audit else None,
        "citations": res.citation_report,
        "retrieved": res.retrieved,
        "web": res.web,
        "notes": res.notes,
        "npic": NPIC,
        "trace": LEDGER.trace(res.trace_id),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "mode": "live" if CLIENT else "no-model-key", "token_factory": bool(CLIENT), "tavily": bool(os.environ.get("TAVILY_API_KEY")), "index": STORE.stats(), "rules_version": PIPE.rules.version, "who_rows": len(REGISTRY.who), "active_ingredients": len(REGISTRY.ais)}


@app.get("/v1/chemicals")
def chemicals() -> list[dict[str, Any]]:
    return [{"name": a["name"], "group": a["group"], "who_class": a.get("who_class"), "india_status": a.get("india_status"), "verified": not a.get("verify", True), "antidote_exists": (REGISTRY.group(a["group"]) or {}).get("antidote_exists")} for a in REGISTRY.ais]


@app.post("/v1/read-label")
async def read_label(image: UploadFile = File(...)) -> dict[str, Any]:
    """Vision reads the label fields; nothing clinical is asked of the vision model."""
    import antidote_vision as av

    av.PROMPT = LABEL_PROMPT
    vr = describe(await image.read())
    raw = vr.raw
    start, end = raw.find("{"), raw.rfind("}")
    fields: dict[str, Any] = {}
    if start >= 0 and end > start:
        try:
            fields = json.loads(raw[start : end + 1])
        except Exception:  # noqa: BLE001
            fields = {}
    return {"mode": vr.mode, "fields": fields, "notes": vr.notes}


@app.post("/v1/analyze")
def analyze(body: AnalyzeBody) -> dict[str, Any]:
    t0 = time.perf_counter()
    res = PIPE.analyze(raw_label=body.label, context=body.context, audit=body.audit, chosen_ai=body.chosen_ai)
    out = _result_json(res)
    out["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    return out


@app.get("/v1/page/{doc_id}/{page}")
def page(doc_id: str, page: int) -> dict[str, Any]:
    text = STORE.page_text(doc_id, page)
    if text is None:
        raise HTTPException(404, "page not indexed")
    meta = STORE.doc_meta(doc_id) or {}
    return {"doc_id": doc_id, "page": page, "title": meta.get("title"), "source_url": meta.get("source_url"), "licence": meta.get("licence"), "text": text}


@app.post("/v1/records")
def create_record(rec: MLCRecord) -> dict[str, Any]:
    row = rec.model_dump() | {"id": str(uuid.uuid4()), "created_at": time.time()}
    with RECORDS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


@app.get("/v1/records")
def list_records() -> list[dict[str, Any]]:
    if not RECORDS.exists():
        return []
    return [json.loads(line) for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.strip()]


@app.get("/v1/evals/latest")
def evals_latest() -> dict[str, Any]:
    p = ROOT / "eval/results/latest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"status": "no eval run yet"}


@app.get("/v1/costs")
def costs() -> dict[str, Any]:
    return LEDGER.totals()

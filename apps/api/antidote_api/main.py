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

# --- API keys and rate limiting (simple, file-backed; enough for a hosted demo) ---
import hashlib
import secrets
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

KEYS_FILE = ROOT / "data/api_keys.json"
REQUIRE_KEY = os.environ.get("ANTIDOTE_REQUIRE_KEY", "0") == "1"
RATE_LIMIT_PER_MIN = int(os.environ.get("ANTIDOTE_RATE_LIMIT_PER_MIN", "30"))
_hits: dict[str, deque] = defaultdict(deque)


def _key_hashes() -> set[str]:
    if not KEYS_FILE.exists():
        return set()
    return {k["hash"] for k in json.loads(KEYS_FILE.read_text(encoding="utf-8"))}


@app.middleware("http")
async def keys_and_limits(request: Request, call_next):
    path = request.url.path
    if path.startswith("/v1/"):
        ident = request.headers.get("x-api-key") or (request.client.host if request.client else "anon")
        if REQUIRE_KEY and path != "/v1/keys":
            key = request.headers.get("x-api-key", "")
            if hashlib.sha256(key.encode()).hexdigest() not in _key_hashes():
                return JSONResponse({"error": "API key required: POST /v1/keys to create one, then send X-API-Key"}, status_code=401)
        now = time.time()
        q = _hits[ident]
        while q and q[0] < now - 60:
            q.popleft()
        if len(q) >= RATE_LIMIT_PER_MIN:
            return JSONResponse({"error": f"rate limit: {RATE_LIMIT_PER_MIN} requests per minute"}, status_code=429)
        q.append(now)
    return await call_next(request)


class KeyBody(BaseModel):
    label: str = "demo"


@app.post("/v1/keys")
def create_key(body: KeyBody) -> dict[str, Any]:
    """Issue an API key. Only the SHA-256 hash is stored; the key is shown once."""
    key = "antidote_" + secrets.token_urlsafe(24)
    keys = json.loads(KEYS_FILE.read_text(encoding="utf-8")) if KEYS_FILE.exists() else []
    keys.append({"label": body.label, "hash": hashlib.sha256(key.encode()).hexdigest(), "created_at": time.time()})
    KEYS_FILE.write_text(json.dumps(keys, indent=1), encoding="utf-8")
    return {"key": key, "label": body.label, "note": "Shown once. Send as X-API-Key. Required when ANTIDOTE_REQUIRE_KEY=1 on the server."}


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


@app.post("/v1/upload-protocol")
async def upload_protocol(file: UploadFile = File(...), kind: str = "protocol", workspace: str = "demo") -> dict[str, Any]:
    """Bring your own data: a state or hospital protocol (PDF) is indexed into the workspace and cited beside the national module, labelled local.
    kind=stock accepts a CSV of antidote stock (name,quantity) that the card uses to say what is on the shelf here."""
    import csv as _csv
    import hashlib as _h
    import io as _io
    import re as _re

    raw = await file.read()
    dest = ROOT / "data/corpus/uploads" / workspace
    dest.mkdir(parents=True, exist_ok=True)
    safe = _re.sub(r"[^A-Za-z0-9._-]+", "-", file.filename or "upload")[:120]
    (dest / safe).write_bytes(raw)
    if kind == "stock":
        rows = list(_csv.DictReader(_io.StringIO(raw.decode("utf-8", errors="replace"))))
        (dest / "stock.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
        return {"kind": "stock", "items": len(rows), "workspace": workspace}
    if not safe.lower().endswith(".pdf"):
        raise HTTPException(400, "upload a PDF protocol or a CSV stock list with kind=stock")
    import fitz

    pages: list[tuple[int, str]] = []
    with fitz.open(dest / safe) as doc:
        for i, pg in enumerate(doc, start=1):
            pages.append((i, _re.sub(r"[ 	]+", " ", pg.get_text("text") or "").strip()))
    doc_id = f"local-{workspace}-" + _re.sub(r"[^a-z0-9]+", "-", safe.lower().rsplit(".", 1)[0])[:60]
    STORE.add_doc(doc_id=doc_id, title=f"{safe} (local protocol, workspace {workspace})", path=str(dest / safe), device_class="guideline", device_ids=[], licence="Uploaded by the workspace owner; indexed locally only", source_url="", sha256=_h.sha256(raw).hexdigest(), pages=pages, ingested_at=time.time())
    return {"kind": "protocol", "doc_id": doc_id, "pages": len(pages), "workspace": workspace, "note": "Cited beside the national module as a local source from the next card onward."}

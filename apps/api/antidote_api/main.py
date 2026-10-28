"""Antidote API. OpenAPI at /docs. Runs in replay mode without a model key so the demo never dead-ends."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from antidote_core import ChemRegistry
from antidote_core.paths import data_dir
from antidote_core.pipeline import NPIC, AntidotePipeline
from antidote_core.schemas import MLCRecord
from antidote_llm import Ledger, TokenFactoryClient
from antidote_retrieval import PageStore
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from antidote_api.replay import ReplayBook, antidote_signature

ROOT = Path(__file__).resolve().parents[3]
DATA = data_dir()
for _env in (ROOT / ".env", ROOT.parent / ".env"):
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

app = FastAPI(title="Antidote API", version="0.1.0", description="Photograph a pesticide label; get the chemical, its WHO hazard class, cited poisoning guidance or an explicit stop, and a medico-legal register row. Decision support for trained clinicians.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"])

# --- API keys and rate limiting (simple, file-backed; enough for a hosted demo) ---
import hashlib
import secrets
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

REQUIRE_KEY = os.environ.get("ANTIDOTE_REQUIRE_KEY", "0") == "1"
RATE_LIMIT_PER_MIN = int(os.environ.get("ANTIDOTE_RATE_LIMIT_PER_MIN", "30"))
_hits: dict[str, deque] = defaultdict(deque)


def _deny(body: dict[str, Any], status: int, extra: dict[str, str] | None = None) -> JSONResponse:
    """Errors returned by this middleware run outside the CORS layer, so they carry CORS headers themselves;
    otherwise a browser hides the 401 or 429 and reports a network error."""
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After", **(extra or {})}
    return JSONResponse(body, status_code=status, headers=headers)


@app.middleware("http")
async def keys_and_limits(request: Request, call_next):
    path = request.url.path
    if path.startswith("/v1/") and request.method != "OPTIONS":
        key = request.headers.get("x-api-key", "")
        if key and not _key_valid(key):
            return _deny({"error": "invalid API key: create one with POST /v1/keys"}, 401)
        if REQUIRE_KEY and not key and path != "/v1/keys":
            return _deny({"error": "API key required: POST /v1/keys to create one, then send X-API-Key"}, 401)
        ident = key or (request.client.host if request.client else "anon")
        now = time.time()
        q = _hits[ident]
        while q and q[0] < now - 60:
            q.popleft()
        if len(q) >= RATE_LIMIT_PER_MIN:
            return _deny({"error": f"rate limit: {RATE_LIMIT_PER_MIN} requests per minute"}, 429, {"Retry-After": "60"})
        q.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_PER_MIN)
        response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT_PER_MIN - len(q)))
        return response
    return await call_next(request)


def _key_secret() -> bytes:
    """Signing secret for API keys. KEY_SIGNING_SECRET if set, else derived from the model key so it is stable across
    serverless instances and never stored or shown."""
    s = os.environ.get("KEY_SIGNING_SECRET") or ("keys:" + os.environ.get("NEBIUS_API_KEY", "local-dev"))
    return hashlib.sha256(s.encode()).digest()


def _sign(token: str) -> str:
    import hmac

    return hmac.new(_key_secret(), token.encode(), hashlib.sha256).hexdigest()[:24]


def _key_valid(key: str) -> bool:
    """Keys are signed, not stored: any instance can verify one without a database."""
    import hmac

    if not key.startswith("antidote_") or "." not in key:
        return False
    token, sig = key.rsplit(".", 1)
    return hmac.compare_digest(_sign(token), sig)


class KeyBody(BaseModel):
    label: str = "demo"


@app.post("/v1/keys")
def create_key(body: KeyBody) -> dict[str, Any]:
    """Issue an API key. It is signed by the server, so nothing about it is stored; it is shown once."""
    label = re.sub(r"[^A-Za-z0-9-]", "", body.label)[:24] or "key"
    token = f"antidote_{label}_{secrets.token_urlsafe(12)}"
    return {"key": f"{token}.{_sign(token)}", "label": label, "rate_limit_per_min": RATE_LIMIT_PER_MIN,
            "note": "Shown once. Send it as the X-API-Key header. Any key you send is verified; invalid keys get 401."}


@app.get("/v1/keys/verify")
def verify_key(request: Request) -> dict[str, Any]:
    """Check the X-API-Key header and report its usage in the current minute."""
    key = request.headers.get("x-api-key", "")
    used = len(_hits.get(key, ())) if key else 0
    return {"valid": bool(key) and _key_valid(key), "label": key.split("_")[1] if key.count("_") >= 2 else None,
            "requests_last_minute": used, "rate_limit_per_min": RATE_LIMIT_PER_MIN, "required_by_server": REQUIRE_KEY}


LEDGER = Ledger(DATA / "ledger.db")
STORE = PageStore(DATA / "index/antidote.db")
REGISTRY = ChemRegistry()
try:
    CLIENT: TokenFactoryClient | None = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = AntidotePipeline(CLIENT, STORE, REGISTRY)
REPLAYS = ReplayBook(DATA / "samples/replay", antidote_signature)
RECORDS = DATA / "mlc_register.jsonl"

LABEL_PROMPT = (
    "You are reading a photo of a pesticide container label for a doctor. Return ONLY a JSON object with keys: product_name, "
    "active_ingredients (list of {name, percent} exactly as printed), formulation_code, registration_number (e.g. CIR-...), batch, expiry, "
    "manufacturer, triangle_colour (red, yellow, blue or green if a coloured triangle or band is visible), signal_word, antidote_statement_text "
    "(the antidote sentence exactly as printed, or null), visible_text (at most 15 short strings as printed), languages_seen (list), confidence (0 to 1). "
    "Do not infer anything not visible; use null."
)


class AnalyzeBody(BaseModel):
    label: dict[str, Any]
    context: dict[str, str] = {}
    chosen_ai: str | None = None
    audit: bool = True
    workspace: str | None = None  # uploads from /v1/upload-protocol for this workspace: its protocol pages and its stock list


def _workspace_dir(workspace: str) -> Path:
    import re as _re

    return DATA / "uploads" / _re.sub(r"[^A-Za-z0-9_-]+", "-", workspace)[:40]


def stock_check(group: dict[str, Any] | None, workspace: str | None) -> dict[str, Any] | None:
    """Is the antidote on this hospital's shelf? A lookup in the uploaded stock CSV, no model involved."""
    names = (group or {}).get("stock_names") or []
    if not workspace or not names:
        return None
    path = _workspace_dir(workspace) / "stock.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))

    def qty(r: dict[str, Any]) -> str:
        return str(next((v for k, v in r.items() if k and k.strip().lower() in ("quantity", "qty", "stock", "count")), "")).strip()

    def name(r: dict[str, Any]) -> str:
        return str(next((v for k, v in r.items() if k and k.strip().lower() in ("name", "drug", "item", "antidote")), "")).strip()

    out = []
    for n in names:
        row = next((r for r in rows if n in name(r).lower()), None)
        q = qty(row) if row else ""
        in_stock = bool(row) and q not in ("", "0", "0.0") and not q.lower().startswith(("nil", "none", "out"))
        out.append({"antidote": n, "listed_as": name(row) if row else None, "quantity": q or None, "in_stock": in_stock})
    return {"workspace": workspace, "items": out, "source": "your uploaded stock list"}


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


@app.get("/", include_in_schema=False)
def root():
    from fastapi.responses import RedirectResponse

    return RedirectResponse("/docs", status_code=307)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "mode": "live" if CLIENT else "no-model-key", "token_factory": bool(CLIENT), "tavily": bool(os.environ.get("TAVILY_API_KEY")), "index": STORE.stats(), "rules_version": PIPE.rules.version, "who_rows": len(REGISTRY.who), "active_ingredients": len(REGISTRY.ais)}


@app.get("/v1/chemicals")
def chemicals() -> list[dict[str, Any]]:
    return [{"name": a["name"], "group": a["group"], "who_class": a.get("who_class"), "india_status": a.get("india_status"), "verified": not a.get("verify", True), "antidote_exists": (REGISTRY.group(a["group"]) or {}).get("antidote_exists")} for a in REGISTRY.ais]


@app.post("/v1/read-label")
async def read_label(image: UploadFile = File(...)) -> dict[str, Any]:
    """Vision reads the label fields; nothing clinical is asked of the vision model."""
    return read_label_checked(await image.read())


def _group_of(fields: dict[str, Any]) -> str | None:
    """The registry chemical group a read points to, without web lookups. Used only to compare two reads."""
    from antidote_core import LabelFields

    lab = PIPE.normalise(fields, str(uuid.uuid4()))
    m = REGISTRY.match(LabelFields(product_name=lab.product_name, active_ingredients=lab.active_ingredients, raw_text=lab.visible_text))
    return m[0].group if m and m[0].confidence >= 0.75 else None


def _brand_group(product_name: str | None) -> str | None:
    """The chemical group the web says a brand contains (Tavily over Indian agrochemical sources), or None if unclear."""
    from antidote_core.tavily_tools import brand_votes, clear_winner, resolve_brand

    if not product_name or not os.environ.get("TAVILY_API_KEY"):
        return None
    win = clear_winner(brand_votes(resolve_brand(product_name), REGISTRY.ais))
    return win["group"] if win else None


def read_label_checked(image: bytes) -> dict[str, Any]:
    """Two different vision models read the label in parallel. If their reads point to different chemical groups, the
    chemical is left blank for the doctor to confirm from the bottle: a vision model can invent small print."""
    import antidote_vision as av

    av.PROMPT = LABEL_PROMPT
    from antidote_core.pipeline import clean_label

    vr, second = av.describe_pair(image)
    fields = clean_label(parse_label_fields(vr.raw))
    check: dict[str, Any] = {"second_read": second is not None}
    if fields.get("active_ingredients") or fields.get("visible_text"):
        g1 = _group_of(fields)
        g2 = _group_of(clean_label(parse_label_fields(second.raw))) if second else None
        check.update({"first": g1, "second": g2, "agreed": g1 is not None and g1 == g2})
        web_group = _brand_group(fields.get("product_name")) if check["agreed"] else None
        if web_group and web_group != g1:
            # Two reads agree but the brand's registered composition on the web points elsewhere: trust neither.
            check.update({"agreed": False, "web": web_group})
        if not check["agreed"]:
            check["first_read_ingredients"] = [a.get("name") for a in (fields.get("active_ingredients") or []) if isinstance(a, dict)]
            # Keep the brand and maker; drop every chemical-bearing line, so no invented name can reach the registry.
            fields = {k: v for k, v in fields.items() if k in ("product_name", "manufacturer", "triangle_colour", "signal_word", "registration_number")}
    return {"mode": vr.mode, "fields": fields, "cross_check": check, "notes": vr.notes + (second.notes if second else ["no second read"])}


def parse_label_fields(raw: str) -> dict[str, Any]:
    """Parse the vision reply; when the JSON is cut off or malformed, salvage what was printed rather than return nothing."""
    import re

    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        try:
            fields = json.loads(raw[start : end + 1])
            if isinstance(fields, dict):
                return fields
        except Exception:  # noqa: BLE001, S110 - fall through to salvage
            pass
    out: dict[str, Any] = {}
    for k in ("product_name", "formulation_code", "registration_number", "manufacturer", "triangle_colour", "signal_word", "antidote_statement_text"):
        m = re.search(rf'"{k}"\s*:\s*"([^"]*)"', raw)
        if m and m.group(1).strip():
            out[k] = m.group(1).strip()
    m = re.search(r'"active_ingredients"\s*:\s*\[(.*?)(\]|$)', raw, re.DOTALL)
    if m:
        ais = [{"name": n.strip(), **({"percent": p} if p else {})} for n, p in re.findall(r'"name"\s*:\s*"([^"]+)"(?:\s*,\s*"percent"\s*:\s*"?([^",}]*)"?)?', m.group(1))]
        if ais:
            out["active_ingredients"] = ais
    m = re.search(r'"visible_text"\s*:\s*\[(.*?)(\]|$)', raw, re.DOTALL)
    if m:
        out["visible_text"] = re.findall(r'"([^"]{2,80})"', m.group(1))[:20]
    return out


@app.post("/v1/analyze")
def analyze(body: AnalyzeBody) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        res = PIPE.analyze(raw_label=body.label, context=body.context, audit=body.audit, chosen_ai=body.chosen_ai, workspace=body.workspace)
    except Exception as e:
        served = REPLAYS.serve(body.model_dump(), f"{type(e).__name__}")
        if served:
            return served
        raise HTTPException(503, f"The model service is unavailable right now ({type(e).__name__}). The sample presets still work from recorded results; please try one of them.") from e
    out = _result_json(res)
    # Only when the card actually gives antidote guidance: a withheld or stopped card gets no stock line.
    out["stock"] = None if res.guarded else stock_check(res.group, body.workspace)
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
    dest = _workspace_dir(workspace)
    workspace = dest.name
    dest.mkdir(parents=True, exist_ok=True)
    safe = _re.sub(r"[^A-Za-z0-9._-]+", "-", file.filename or "upload")[:120]
    (dest / safe).write_bytes(raw)
    if kind == "stock":
        try:
            rows = list(_csv.DictReader(_io.StringIO(raw.decode("utf-8-sig", errors="replace"), newline="")))
        except _csv.Error:
            rows = []
        names = {k.strip().lower() for k in (rows[0].keys() if rows else []) if k}
        if not rows or not names & {"name", "drug", "item", "antidote"}:
            raise HTTPException(400, "The stock CSV needs a header row with a name column and a quantity column, e.g. name,quantity")
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


# --- Telegram front door (set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET to enable) ---
@app.post("/v1/telegram/webhook", include_in_schema=False)
async def telegram_webhook(request: Request) -> dict[str, Any]:
    import httpx

    from antidote_api.telegram import handle_update

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not token or not secret:
        raise HTTPException(404, "telegram not configured")
    if request.headers.get("x-telegram-bot-api-secret-token") != secret:
        raise HTTPException(403, "bad secret")
    update = await request.json()
    api = f"https://api.telegram.org/bot{token}"

    def send(chat: int, text: str) -> None:
        httpx.post(f"{api}/sendMessage", json={"chat_id": chat, "text": text[:4000]}, timeout=20)

    def read_photo(file_id: str) -> dict[str, Any]:

        info = httpx.get(f"{api}/getFile", params={"file_id": file_id}, timeout=20).json()
        path = (info.get("result") or {}).get("file_path")
        if not path:
            return {}
        img = httpx.get(f"https://api.telegram.org/file/bot{token}/{path}", timeout=30).content
        return read_label_checked(img)["fields"]

    def analyze_label(fields: dict[str, Any]):
        return PIPE.analyze(raw_label=fields, context={}, audit=False)

    did = handle_update(update, analyze=analyze_label, read_photo=read_photo, send=send, npic=NPIC)
    return {"ok": True, "did": did}


# --- Surveillance: the register as an early-warning signal (deterministic alerts; Nemotron 3.5 Lightning brief) ---
def _register_rows() -> list[dict[str, Any]]:
    from antidote_core.surveillance import load_rows

    return load_rows(RECORDS, DATA / "samples/register_demo.jsonl")


@app.get("/v1/surveillance/alerts")
def surveillance_alerts() -> dict[str, Any]:
    """Clusters and banned chemicals in the register, by fixed rules only. Instant, no model call."""
    from antidote_core.surveillance import detect_alerts, status_map

    rows = _register_rows()
    return {"register_rows": len(rows), "demo_rows": sum(1 for r in rows if r.get("demo")), "alerts": detect_alerts(rows, status_map(REGISTRY))}


@app.post("/v1/surveillance/brief")
def surveillance_brief() -> dict[str, Any]:
    """Nemotron 3.5 Lightning reads the whole register and every published case report for the chemicals in it, in one
    long-context call, and writes the district brief. Item-level safety rules apply before it is returned."""
    from antidote_core.surveillance import build_brief

    if not CLIENT:
        raise HTTPException(503, "model key not configured")
    t0 = time.perf_counter()
    trace_id = str(uuid.uuid4())
    out = build_brief(CLIENT, _register_rows(), REGISTRY, PIPE.rules, trace_id=trace_id)
    out["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    out["trace"] = LEDGER.trace(trace_id)
    return out


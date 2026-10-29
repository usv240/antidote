"""Antidote as a hosted MCP server at /mcp (streamable HTTP, stateless), so any agent adds it by URL with no install.

The tools call the same pipeline, registry and guideline store as the HTTP API; the lethal-error rules, quote verifier
and Nemotron 3 Ultra audit run exactly as they do for the web app. Stateless mode fits a serverless function: every
request gets its own session manager, so nothing depends on the app's lifespan.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from mcp.server.mcpserver import MCPServer
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from antidote_api import main as api

mcp = MCPServer(
    "antidote",
    instructions=(
        "Decision support for trained clinicians treating pesticide poisoning in India. Call bedside_card with what the "
        "label says. Show every stop card first and exactly as given; never add a drug or a dose the card does not quote. "
        "Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117."
    ),
)


@mcp.tool()
def list_chemicals() -> dict[str, Any]:
    """Active ingredients Antidote covers, with chemical group, WHO hazard class, Indian status and whether an antidote exists."""
    return {"chemicals": api.chemicals()}


@mcp.tool()
def bedside_card(
    product_name: str = "",
    active_ingredients: list[str] | None = None,
    triangle_colour: str = "",
    visible_text: list[str] | None = None,
    route: str = "",
    time_since_exposure: str = "",
    signs: str = "",
    audit: bool = True,
) -> dict[str, Any]:
    """From what the label says, the cited bedside card: the chemical, its WHO class and Indian status, stop cards when
    there is no antidote or a common treatment would harm, and guidance made only of guideline sentences quoted with
    their pages. Fixed rules block lethal errors such as atropine for paraquat, and Nemotron 3 Ultra audits the card
    against both national guidelines. active_ingredients like "Paraquat dichloride 24%". Takes up to a minute."""
    ais = []
    for a in active_ingredients or []:
        name, _, pct = a.rstrip("% ").rpartition(" ")
        ais.append({"name": name, "percent": pct} if name and pct.replace(".", "").isdigit() else {"name": a})
    label = {"product_name": product_name or None, "active_ingredients": ais, "triangle_colour": triangle_colour or None,
             "visible_text": visible_text or [x for x in [product_name, *(active_ingredients or [])] if x]}
    context = {k: v for k, v in {"route": route, "time_since_exposure": time_since_exposure, "signs": signs}.items() if v}
    try:
        out = api.analyze(api.AnalyzeBody(label=label, context=context, audit=audit))
    except HTTPException as e:
        return {"error": e.detail}
    keep = ("trace_id", "banner", "chosen", "group", "triangle", "guarded", "stops", "card", "audit", "citations", "notes", "npic", "latency_ms")
    return {k: out.get(k) for k in keep} | {"models": [{"model": t.get("model"), "tier": t.get("tier"), "usd": t.get("usd")} for t in out.get("trace") or []]}


@mcp.tool()
def read_guideline_page(doc_id: str, page: int) -> dict[str, Any]:
    """Full text of one guideline page (NHSRC module, ISCCM 2024 statement), with its title and source, to check a quote."""
    try:
        return api.page(doc_id, page)
    except HTTPException as e:
        return {"error": f"{e.detail}: {doc_id} page {page}. Use a doc_id and page from a card citation."}


@mcp.tool()
def surveillance_alerts() -> dict[str, Any]:
    """District early-warning alerts from the register, decided by fixed rules: spraying clusters, banned chemicals still
    reaching patients, restricted-use chemicals. The demo register rows are synthetic and marked."""
    return api.surveillance_alerts()


class MCPEndpoint:
    """ASGI endpoint the API routes /mcp to. A class instance, so Starlette passes it the raw ASGI call."""

    async def __call__(self, scope, receive, send) -> None:
        manager = StreamableHTTPSessionManager(app=mcp._lowlevel_server, json_response=True, stateless=True)
        async with manager.run():
            await manager.handle_request(scope, receive, send)

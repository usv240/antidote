"""Poisoning surveillance: the medico-legal register as an early-warning signal.

In Yavatmal in 2017 about 800 farm workers were poisoned while spraying cotton and more than 20 died over twelve weeks
before the cluster was recognised. Every one of those patients was entered in a hospital register. This module reads
the register the way a district surveillance officer would want it read:

1. Deterministic alerts (no model): clusters of the same chemical group within a week, clusters from spraying (skin or
   inhaled), and banned or restricted chemicals still reaching patients. These decide what is flagged.
2. A brief written by NVIDIA Nemotron 3.5 Lightning, which reads the whole register, the alerts, the registry status
   of every chemical seen, and the full text of every published case report for those chemicals, in one long-context
   call. The brief explains; it does not decide, and it is checked by the same safety rules as the bedside card.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
WINDOW_DAYS = 7
CLUSTER_MIN = 3


def _when(row: dict[str, Any]) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(row.get("datetime", ""))[:16], fmt)
        except ValueError:
            continue
    return None


def _spraying(row: dict[str, Any]) -> bool:
    return bool(re.search(r"inhal|skin|spray|dermal", f"{row.get('route', '')} {row.get('alleged_history', '')}", re.IGNORECASE))


def detect_alerts(rows: list[dict[str, Any]], status: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Rules only. A cluster is CLUSTER_MIN or more cases of one chemical group inside any WINDOW_DAYS window."""
    alerts: list[dict[str, Any]] = []
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        if r.get("chemical_group") and _when(r):
            by_group[r["chemical_group"]].append(r)
    for group, rs in by_group.items():
        rs.sort(key=_when)
        best: list[dict[str, Any]] = []
        for i, r in enumerate(rs):
            window = [x for x in rs[i:] if _when(x) - _when(r) <= timedelta(days=WINDOW_DAYS)]
            if len(window) > len(best):
                best = window
        if len(best) >= CLUSTER_MIN:
            spray = sum(_spraying(x) for x in best)
            kind = "spraying cluster" if spray >= CLUSTER_MIN else "cluster"
            alerts.append({
                "type": kind, "chemical_group": group, "cases": len(best),
                "from": best[0]["datetime"], "to": best[-1]["datetime"],
                "chemicals": sorted({x.get("substance_active_ingredient") or "unknown" for x in best}),
                "localities": sorted({x.get("locality") for x in best if x.get("locality")}),
                "row_ids": [x.get("id") for x in best],
                "why": f"{len(best)} cases of {group} within {WINDOW_DAYS} days" + (f", {spray} from skin or inhaled exposure while spraying" if kind == "spraying cluster" else ""),
            })
    status = status or {}
    banned = [r for r in rows if status.get((r.get("substance_active_ingredient") or "").lower()) == "banned"]
    for r in banned:
        alerts.append({"type": "banned chemical in circulation", "chemical_group": r.get("chemical_group"), "cases": 1,
                       "from": r.get("datetime"), "to": r.get("datetime"), "chemicals": [r.get("substance_active_ingredient")],
                       "localities": [r.get("locality")] if r.get("locality") else [], "row_ids": [r.get("id")],
                       "why": f"{r.get('substance_active_ingredient')} is banned in India (CIB&RC) and still reached a patient: the product is still being sold or stored"})
    restricted = [r for r in rows if status.get((r.get("substance_active_ingredient") or "").lower()) == "restricted"]
    if len(restricted) >= 2:
        chems = sorted({r.get("substance_active_ingredient") for r in restricted})
        alerts.append({"type": "restricted-use chemicals", "chemical_group": None, "cases": len(restricted),
                       "from": min(r["datetime"] for r in restricted), "to": max(r["datetime"] for r in restricted), "chemicals": chems,
                       "localities": sorted({r.get("locality") for r in restricted if r.get("locality")}), "row_ids": [r.get("id") for r in restricted],
                       "why": f"{len(restricted)} poisonings from chemicals whose sale is restricted in India: {', '.join(chems)}"})
    return alerts


class BriefItem(BaseModel):
    title: str
    detail: str = Field(description="Two plain sentences. Cite register row ids or case report URLs inline.")
    evidence: list[str] = Field(default_factory=list, description="Row ids or case report URLs that support this item")


class SurveillanceBrief(BaseModel):
    """One-page brief for the district surveillance officer and the hospital's poisoning committee."""

    headline: str = Field(description="One sentence: the most important thing in this register this period.")
    clusters: list[BriefItem] = Field(description="One item per deterministic alert of type cluster or spraying cluster, explained. Do not add clusters the alerts do not list.")
    regulatory: list[BriefItem] = Field(description="Banned or restricted chemicals that still reached patients, with what the registry says about them.")
    what_published_cases_teach: list[BriefItem] = Field(description="For chemicals seen in this register, lessons from the published case reports provided: how cases were misidentified, what worked. Cite the case URL.")
    actions: list[BriefItem] = Field(description="Practical actions for the district: field visit, farmer outreach, retailer inspection, report to the poison centre. No drug doses.")
    confidence_note: str = Field(description="One sentence on how complete the data is: number of register rows, date range, which rows are demo data.")


SYSTEM = """You are the analyst for a district surveillance officer in India. You receive a hospital's complete medico-legal poisoning register, alerts already computed by fixed rules, the registry status of each chemical, and the full text of published case reports about those chemicals.
Write a brief the officer can act on in five minutes. The alerts are authoritative: explain them, never add or remove a cluster, and copy every count from the alerts rather than recounting the register. Cite register row ids and case report URLs. Do not give drug names with doses or treatment instructions; this brief is for public-health action, not bedside care. If register rows are marked as demo data, say so in the confidence note. Return the SurveillanceBrief tool call."""


def status_map(registry: Any) -> dict[str, str]:
    """India regulatory status per chemical, from the registry (CIB&RC), lower-cased name to banned, restricted or registered."""
    return {a["name"].lower(): a.get("india_status", "unknown") for a in registry.ais}


def load_rows(records_path: Path, demo_path: Path | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in (demo_path, records_path):
        if p and p.exists():
            rows += [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows


def literature_for(rows: list[dict[str, Any]], max_chars: int = 2_600_000) -> list[dict[str, Any]]:
    """Full text of every published case report whose chemical group appears in the register."""
    groups = {r.get("chemical_group") for r in rows if r.get("chemical_group")}
    out: list[dict[str, Any]] = []
    used = 0
    for fname, manifest in (("case_reports.json", "case_reports_manifest.json"), ("case_reports_v2.json", "case_reports_manifest_v2.json")):
        cases_p, man_p = ROOT / "data/external" / fname, ROOT / "data/external" / manifest
        if not (cases_p.exists() and man_p.exists()):
            continue
        files = {m["url"]: m.get("file") for m in json.loads(man_p.read_text(encoding="utf-8"))["items"]}
        for c in json.loads(cases_p.read_text(encoding="utf-8"))["cases"]:
            if "excluded" in c or c.get("expected_group") not in groups:
                continue
            f = files.get(c["url"])
            path = ROOT / "data/corpus/case_reports" / f if f else None
            text = path.read_text(encoding="utf-8") if path and path.exists() else ""
            item = {"url": c["url"], "substance": c.get("substance"), "group": c.get("expected_group"), "authors_management": c.get("authors_management"), "full_text": text}
            size = len(text) + 400
            if used + size > max_chars:
                item["full_text"] = ""  # keep the structured facts even when the text no longer fits
            else:
                used += size
            out.append(item)
    return out


COUNT_RE = re.compile(r"\b(\d+)\s+(?:of the\s+|more\s+)?(?:cases?|patients?|poisonings?|rows?|deaths?)\b", re.IGNORECASE)


def allowed_counts(alerts: list[dict[str, Any]], n_rows: int) -> set[int]:
    """Every count the rules computed: case totals, the spraying sub-count, the register size."""
    nums = {n_rows}
    for a in alerts:
        nums.add(int(a.get("cases") or 0))
        nums.update(int(x) for x in re.findall(r"\d+", a.get("why", "")))
    return nums


def drop_unbacked_counts(text: str, allowed: set[int]) -> tuple[str, list[str]]:
    """Remove each clause that states a case count the rules did not compute. Counts are facts; the model only explains them."""
    kept, dropped = [], []
    for clause in re.split(r"(?<=[.;])\s+", text.strip()):
        bad = [int(m.group(1)) for m in COUNT_RE.finditer(clause) if int(m.group(1)) not in allowed]
        (dropped if bad else kept).append(clause)
    return " ".join(kept).rstrip(";") + ("" if not kept or kept[-1].endswith(".") else "."), dropped


def build_brief(client: Any, rows: list[dict[str, Any]], registry: Any, rules: Any, trace_id: str | None = None) -> dict[str, Any]:
    from antidote_llm import Tier, call_structured

    alerts = detect_alerts(rows, status_map(registry))
    seen = sorted({r.get("substance_active_ingredient") for r in rows if r.get("substance_active_ingredient")})
    status = [{"chemical": a["name"], "group": a["group"], "who_class": a.get("who_class"), "india_status": a.get("india_status")}
              for a in registry.ais if a["name"].lower() in {s.lower() for s in seen}]
    lit = literature_for(rows)
    payload = {"register": rows, "alerts": alerts, "registry_status": status, "published_case_reports": lit}
    text = json.dumps(payload, ensure_ascii=False)
    approx = len(text) // 3
    brief = call_structured(client, Tier.FAST, SurveillanceBrief,
                            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"DATA (JSON):\n{text}\n\nWrite the SurveillanceBrief."}],
                            purpose="surveillance.brief", trace_id=trace_id, max_tokens=3000, context_tokens=approx)
    # The brief is model text: the same rules that guard the bedside card check every item before anyone sees it.
    # An item the rules would block is removed whole, and the removal is reported, so the rest of the brief survives.
    removed: list[dict[str, Any]] = []
    if rules.blocks(rules.check(brief.headline, "output")):
        brief.headline = "Alerts below were computed by fixed rules; the model's headline was removed by the safety rules."
    for sec in ("clusters", "regulatory", "what_published_cases_teach", "actions"):
        kept = []
        for item in getattr(brief, sec):
            hits = rules.check(f"{item.title}. {item.detail}", "output")
            if rules.blocks(hits):
                removed.append({"section": sec, "title": item.title, "rules": sorted({h.rule_id for h in hits if h.action == "block"})})
            else:
                kept.append(item)
        setattr(brief, sec, kept)
    # Counts must come from the rules. Lightning once wrote "3 skin or inhaled, 2 unknown route" for a cluster the
    # rules had counted as 5 of 5; a clause with a count the rules did not compute is removed and the removal reported.
    allowed = allowed_counts(alerts, len(rows))
    for sec in ("clusters", "regulatory"):
        for item in getattr(brief, sec):
            item.detail, dropped = drop_unbacked_counts(item.detail, allowed)
            if dropped:
                removed.append({"section": sec, "title": f"{item.title}: {' '.join(dropped)}", "rules": ["count-not-computed-by-rules"]})
    return {"alerts": alerts, "brief": brief.model_dump(), "removed_by_rules": removed,
            "input_tokens_approx": approx, "case_reports_read": sum(1 for x in lit if x["full_text"]), "register_rows": len(rows)}

"""Antidote evaluation. `make eval` writes eval/results/latest.json and REPORT.md.

Without a model key: hazard-text gating (rules only), registry routing for no-antidote, not-pesticide and
organophosphate labels, and WHO-class agreement between the registry and the parsed WHO 2019 table.
With NEBIUS_API_KEY: the same label sets through the full pipeline (stop cards, atropine absence, citation integrity).
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path

import typer
import yaml
from antidote_core import ChemRegistry, LabelFields
from antidote_rules import load_rules

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
app = typer.Typer(add_completion=False)


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def _label_fields(d: dict) -> LabelFields:
    return LabelFields(product_name=d.get("product_name"), active_ingredients=d.get("active_ingredients"), formulation_code=d.get("formulation_code"), triangle_colour=d.get("triangle_colour"), antidote_statement_text=d.get("antidote_statement_text"), raw_text=d.get("visible_text"))


def deterministic() -> tuple[dict, list[dict]]:
    sets = yaml.safe_load((HERE / "negative_controls.yaml").read_text(encoding="utf-8"))
    rules = load_rules(ROOT / "packages/rules/antidote_rules/antidote.yaml")
    reg = ChemRegistry()
    sections: list[dict] = []
    # 1. hazardous text blocked by rules
    rows, ok = [], 0
    for t in sets["hazardous_text"]:
        hits = rules.check(t, "output")
        blocked = rules.blocks(hits)
        ok += blocked
        rows.append({"text": t, "result": "blocked" if blocked else "MISSED", "rules": ",".join(sorted({h.rule_id for h in hits}))})
    sections.append({"name": "Hazardous text blocked by rules", "description": "Lethal-error sentences the rules engine must block before any model output reaches a clinician.", "columns": ["text", "result", "rules"], "rows": rows})
    haz = _pct(ok, len(sets["hazardous_text"]))
    # 2. registry routing
    def route(labels: list[dict], expect: str) -> tuple[list[dict], int]:
        rs, n_ok = [], 0
        for d in labels:
            m = reg.match(_label_fields(d))
            top = m[0] if m else None
            g = reg.group(top.group) if top else None
            if expect == "no_antidote":
                good = bool(top) and g is not None and g.get("antidote_exists") is False and top.group != "not_pesticide"
            elif expect == "not_pesticide":
                good = (not top) or top.group == "not_pesticide"
            else:
                good = bool(top) and top.group in ("organophosphate", "carbamate") and (g or {}).get("antidote_exists") is True
            n_ok += good
            rs.append({"product": d.get("product_name"), "matched": top.active_ingredient if top else None, "group": top.group if top else None, "who_class": top.who_class if top else None, "result": "correct" if good else "WRONG"})
        return rs, n_ok
    r1, ok1 = route(sets["no_antidote_labels"], "no_antidote")
    r2, ok2 = route(sets["not_pesticide_labels"], "not_pesticide")
    r3, ok3 = route(sets["benign_op_labels"], "op")
    sections.append({"name": "Registry routing: no-antidote labels", "description": "Each label must route to a chemical group with antidote_exists=false so the stop card fires.", "columns": ["product", "matched", "group", "who_class", "result"], "rows": r1})
    sections.append({"name": "Registry routing: not a pesticide", "description": "Fertilisers, cleaners, medicines and fuels must route to the general approach, never to a pesticide antidote.", "columns": ["product", "matched", "group", "who_class", "result"], "rows": r2})
    sections.append({"name": "Registry routing: organophosphates and carbamates", "description": "These must NOT be stopped; they have a cited antidote path.", "columns": ["product", "matched", "group", "who_class", "result"], "rows": r3})
    # 3. WHO class agreement
    agree = total = 0
    rows = []
    for a in reg.ais:
        w = reg.who.get(a["name"].lower()) or reg.who.get(a["name"].lower().replace(" dichloride", ""))
        if a.get("who_class") in (None, "FM") and not w:
            continue
        total += 1
        ok_ = bool(w) and w["who_class"] == a.get("who_class")
        agree += ok_
        rows.append({"active_ingredient": a["name"], "registry_class": a.get("who_class"), "who_2019_class": w["who_class"] if w else "not in parsed table", "source_line": w["source_line"] if w else "", "result": "agree" if ok_ else "CHECK"})
    sections.append({"name": "WHO 2019 class agreement", "description": "Registry class versus the class parsed from the WHO 2019 classification text (458 active ingredients). CHECK rows are the ones the parser could not find (table 5 and two unusual names).", "columns": ["active_ingredient", "registry_class", "who_2019_class", "source_line", "result"], "rows": rows})
    summary = {
        "hazard_blocked": {"value": haz, "unit": "%", "label": "Lethal-error sentences blocked", "note": f"{ok} of {len(sets['hazardous_text'])} by rules alone"},
        "no_antidote_routing": {"value": _pct(ok1, len(r1)), "unit": "%", "label": "No-antidote labels routed to a stop", "note": f"{ok1} of {len(r1)} chemical groups without a specific antidote"},
        "not_pesticide_routing": {"value": _pct(ok2, len(r2)), "unit": "%", "label": "Non-pesticides kept away from antidotes", "note": f"{ok2} of {len(r2)} fertilisers, cleaners, medicines, fuels"},
        "op_not_stopped": {"value": _pct(ok3, len(r3)), "unit": "%", "label": "Organophosphates kept on the antidote path", "note": f"{ok3} of {len(r3)}; target 100, these must not be falsely stopped"},
        "who_agreement": {"value": _pct(agree, total), "unit": "%", "label": "WHO 2019 class agreement", "note": f"{agree} of {total} registry chemicals match the parsed WHO table"},
    }
    return summary, sections


def with_model() -> tuple[dict, list[dict]]:
    from antidote_core.pipeline import AntidotePipeline
    from antidote_llm import Ledger, TokenFactoryClient
    from antidote_retrieval import PageStore

    sets = yaml.safe_load((HERE / "negative_controls.yaml").read_text(encoding="utf-8"))
    client = TokenFactoryClient(ledger=Ledger(ROOT / "data/ledger_eval.db"))
    pipe = AntidotePipeline(client, PageStore(ROOT / "data/index/antidote.db"))
    atropine = re.compile(r"\b(atropine|pralidoxime|2-?pam|oxime)\b", re.IGNORECASE)
    rows, stop_ok, atro_free, cit_ok, cit_total = [], 0, 0, 0, 0
    for d in sets["no_antidote_labels"]:
        try:
            r = pipe.analyze(raw_label=d, audit=False)
            has_stop = any(s["rule"] == "no-specific-antidote" for s in r.stops)
            text = " ".join(s.text for sec in ("manage", "cautions") for s in getattr(r.card, sec)) if r.card else ""
            no_atro = not atropine.search(text)
            c = r.citation_report or {}
            cit_ok += c.get("verified", 0)
            cit_total += c.get("total", 0)
            stop_ok += has_stop
            atro_free += no_atro
            rows.append({"product": d["product_name"], "stop_card": "yes" if has_stop else "NO", "atropine_in_card": "no" if no_atro else "YES", "citations": f"{c.get('verified', 0)}/{c.get('total', 0)}"})
        except Exception as e:  # noqa: BLE001
            rows.append({"product": d["product_name"], "stop_card": f"error {type(e).__name__}", "atropine_in_card": "", "citations": ""})
    n = len(sets["no_antidote_labels"])
    summary = {
        "stop_cards": {"value": _pct(stop_ok, n), "unit": "%", "label": "Stop card on no-antidote labels (full pipeline)", "note": f"{stop_ok} of {n}, Nemotron 3 Super composition with registry gates"},
        "atropine_free": {"value": _pct(atro_free, n), "unit": "%", "label": "No atropine or oxime in those cards", "note": f"{atro_free} of {n}; the headline refusal"},
        "citation_integrity": {"value": _pct(cit_ok, cit_total), "unit": "%", "label": "Citation integrity", "note": f"{cit_ok} of {cit_total} clinical quotes found on the cited guideline page"},
        "cost_usd": {"value": round(sum(v["usd"] for v in client.ledger.totals().values()), 4), "unit": "", "label": "Ledger total (USD)", "note": "all Token Factory calls for this run"},
    }
    return summary, [{"name": "Full pipeline: no-antidote labels", "description": "Each label through normalise, match, compose, verify and gate. Audit disabled for speed; the deterministic gates are what decide.", "columns": ["product", "stop_card", "atropine_in_card", "citations"], "rows": rows}]


@app.command()
def run(out: Path = typer.Option(ROOT / "eval/results")) -> None:
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    summary, sections = deterministic()
    has_key = bool(os.environ.get("NEBIUS_API_KEY"))
    if has_key:
        s2, sec2 = with_model()
        summary |= s2
        sections += sec2
    report = {"generated_at": datetime.now(UTC).isoformat(), "command": "make eval", "model_key_present": has_key, "summary": summary, "sections": sections, "seconds": round(time.time() - t0, 1)}
    (out / "latest.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    md = [f"# Antidote eval report ({report['generated_at']})", ""] + [f"- **{v['label']}**: {v['value']}{v.get('unit', '')}  ({v.get('note', '')})" for v in summary.values()]
    (out / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    typer.echo(json.dumps({k: v["value"] for k, v in summary.items()}, indent=1))


if __name__ == "__main__":
    app()

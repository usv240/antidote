"""The Antidote agent: read label, normalise, match registry, classify, compose from quotes, gate, audit, record.

Design rule: the model reads the label; tables and rules make the clinical statements. No clinical sentence reaches
the screen unless it is a verbatim quote from a cited guideline page that the verifier found on that page.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from antidote_llm import Tier, TokenFactoryClient, call_structured
from antidote_retrieval import PageStore, Searcher
from antidote_rules import RuleHit, RulesEngine, load_rules

from .citations import verify_quote
from .registry import ChemMatch, ChemRegistry, LabelFields
from .schemas import AuditReport, CardSentence, LabelRead, ManagementCard
from .tavily_tools import resolve_brand

ROOT = Path(__file__).resolve().parents[3]
RULES_PATH = ROOT / "packages/rules/antidote_rules/antidote.yaml"
NPIC = "National Poisons Information Centre, AIIMS New Delhi: 1800-116-117 (24x7)"
CONFIDENCE_THRESHOLD = 0.75


@dataclass
class AnalyzeResult:
    trace_id: str
    label: LabelRead
    matches: list[ChemMatch]
    chosen: ChemMatch | None
    group: dict[str, Any] | None
    triangle: dict[str, str] | None
    card: ManagementCard | None
    audit: AuditReport | None
    rule_hits: list[RuleHit]
    citation_report: dict[str, Any]
    retrieved: list[dict[str, Any]]
    guarded: bool = False
    stops: list[dict[str, Any]] = field(default_factory=list)
    web: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    banner: str = f"Decision support for trained clinicians. Airway, breathing, circulation first. {NPIC}."


NORMALISE_SYSTEM = """You normalise text read from an Indian pesticide label. Map spellings to ISO common names (e.g. 'Chlorpyriphos' -> 'chlorpyrifos', 'Cypermethrine' -> 'cypermethrin'). Parse percentages and formulation codes (EC, SC, WP, SL, GR, DP, WG). Do not add anything not on the label. Return the LabelRead tool call."""

COMPOSE_SYSTEM = """You assemble a bedside card for a trained doctor from the guideline pages provided. HARD RULES:
1. Every clinical statement (signs, timing, treatment, antidote, dose, caution) must be kind=quote with a verbatim span copied from a provided page and a cite with that page's doc_id and page number.
2. kind=explanation sentences may only connect ideas; they must contain NO drug names and NO numbers.
3. If the pages say there is no specific antidote for this chemical group, set no_antidote=true and quote that statement.
4. Never write a dose yourself. If a dose appears in a page, quote it verbatim with its page; otherwise say in an explanation that the dose is on the cited page.
5. Keep each section to at most four sentences. Return the ManagementCard tool call."""

AUDIT_SYSTEM = """You are an independent clinical auditor. You receive the complete national poison-management module, the ISCCM position statement, and a proposed card for a named chemical group. For each quote sentence decide approve (the quote is used for the correct chemical group and nothing in the documents contradicts it) or reject (wrong group, contradicted, or not clinical guidance). Be strict about atropine, pralidoxime, oxygen and decontamination statements. Return the AuditReport tool call."""


class AntidotePipeline:
    def __init__(self, client: TokenFactoryClient | None, store: PageStore, registry: ChemRegistry | None = None, rules: RulesEngine | None = None):
        self.client = client
        self.store = store
        self.search = Searcher(store)
        self.registry = registry or ChemRegistry()
        self.rules = rules or load_rules(RULES_PATH)

    # ---------- 1 + 2: read and normalise ----------
    def normalise(self, raw: dict[str, Any], trace_id: str) -> LabelRead:
        base = LabelRead.model_validate({k: v for k, v in raw.items() if k in LabelRead.model_fields})
        if not self.client:
            return base
        try:
            return call_structured(self.client, Tier.FAST, LabelRead, [{"role": "system", "content": NORMALISE_SYSTEM}, {"role": "user", "content": json.dumps(raw, ensure_ascii=False)}], purpose="normalise.label", trace_id=trace_id, max_tokens=700)
        except Exception as e:  # noqa: BLE001
            base.visible_text.append(f"normalise_error:{type(e).__name__}")
            return base

    # ---------- 3: match ----------
    def match(self, label: LabelRead, trace_id: str) -> tuple[list[ChemMatch], dict[str, Any]]:
        fields = LabelFields(product_name=label.product_name, active_ingredients=label.active_ingredients, formulation_code=label.formulation_code, registration_number=label.registration_number, triangle_colour=label.triangle_colour, signal_word=label.signal_word, antidote_statement_text=label.antidote_statement_text, manufacturer=label.manufacturer, raw_text=label.visible_text)
        matches = self.registry.match(fields)
        web: dict[str, Any] = {}
        if (not matches or matches[0].confidence < CONFIDENCE_THRESHOLD) and label.product_name and os.environ.get("TAVILY_API_KEY"):
            web = resolve_brand(label.product_name, ledger=self.client.ledger if self.client else None, trace_id=trace_id)
            # Scan web snippets for a known active ingredient; cap confidence so the antidote row stays suppressed until confirmed.
            blob = " ".join((r.get("title") or "") + " " + (r.get("snippet") or "") for r in web.get("results", [])).lower()
            for a in self.registry.ais:
                if re.search(rf"(?<![a-z]){re.escape(a['name'].lower())}(?![a-z])", blob):
                    matches = [ChemMatch(a["name"], a["group"], a.get("who_class"), a.get("india_status", "unknown"), bool(a.get("verify", True)), 0.6, "web-sourced via Tavily (unverified)")] + matches
                    break
        return matches, web

    # ---------- full analysis ----------
    def analyze(self, *, raw_label: dict[str, Any], context: dict[str, str] | None = None, trace_id: str | None = None, audit: bool = True, chosen_ai: str | None = None) -> AnalyzeResult:
        trace_id = trace_id or str(uuid.uuid4())
        notes: list[str] = []
        label = self.normalise(raw_label, trace_id)
        matches, web = self.match(label, trace_id)
        chosen = next((m for m in matches if chosen_ai and m.active_ingredient.lower() == chosen_ai.lower()), matches[0] if matches else None)
        group = self.registry.group(chosen.group) if chosen else self.registry.group("not_pesticide")
        triangle = self.registry.triangle(label.triangle_colour)
        guarded = (chosen is None) or (chosen.confidence < CONFIDENCE_THRESHOLD)
        stops: list[dict[str, Any]] = []
        rule_hits: list[RuleHit] = []

        # Group-level stop cards come from the registry table, not the model.
        if group and group.get("antidote_exists") is False and chosen and chosen.group != "not_pesticide":
            stops.append({"rule": "no-specific-antidote", "message": f"No specific antidote for {group['name']}. Do not give atropine for this exposure. Management is supportive per the cited guidance.", "citation": "Registry (chemical_groups.yaml) + cited guideline pages below"})
        if chosen and chosen.group == "paraquat":
            stops.append({"rule": "paraquat-oxygen", "message": "Paraquat: avoid supplemental oxygen unless the patient is hypoxic; oxygen accelerates lung injury. See the cited guidance.", "citation": "ISCCM 2024 position statement"})
        if guarded:
            stops.append({"rule": "identify-before-antidote", "message": "Product not confidently identified. Treat the patient, not the bottle: manage the toxidrome you see and call the poison centre before any specific antidote.", "citation": "NHSRC module, syndromic approach"})
        if chosen and chosen.india_status in ("banned", "restricted"):
            notes.append(f"{chosen.active_ingredient} is {chosen.india_status} in India (CIB&RC); note this in the medico-legal record")

        # Retrieve guideline pages for the group.
        terms = " ".join(group.get("retrieval_terms", [])) if group else "general approach poisoning"
        q = f"{chosen.active_ingredient if chosen else ''} {terms} toxidrome management antidote"
        hits = self.search.search(q, device_class="guideline", k=6)
        retrieved = [{"doc": h.doc_id, "title": h.title, "page": h.page, "source_url": h.source_url} for h in hits]

        card: ManagementCard | None = None
        audit_report: AuditReport | None = None
        cit: dict[str, Any] = {}
        if self.client and hits:
            ctx = self.search.pack_context(hits, max_chars=18000)
            allowed = sorted({h.doc_id for h in hits})
            user = (f"Allowed doc_id values for cite (use only these, with the page numbers shown): {', '.join(allowed)}.\n"
                    f"Chemical: {chosen.active_ingredient if chosen else 'unknown'} | group: {group['name'] if group else 'unknown'} | WHO class: {chosen.who_class if chosen else 'n/a'} | label antidote statement as printed: {label.antidote_statement_text or 'none'}\n"
                    f"Patient context: {json.dumps(context or {})}\n\nGuideline pages:\n{ctx}\n\nReturn the ManagementCard tool call.")
            try:
                card = call_structured(self.client, Tier.MID, ManagementCard, [{"role": "system", "content": COMPOSE_SYSTEM}, {"role": "user", "content": user}], purpose="compose.card", trace_id=trace_id, max_tokens=2200)
            except Exception as e:  # noqa: BLE001
                notes.append(f"compose failed: {type(e).__name__}")
        if card:
            cit = self._verify(card)
            card = self._gate(card, rule_hits)
            if guarded:
                card.manage = [s for s in card.manage if s.kind == "explanation"] or [CardSentence(kind="explanation", text="Antidote guidance is withheld until the product is confidently identified.")]
            if audit:
                audit_report = self._audit(card, chosen.group if chosen else "unknown", trace_id)
                card = self._apply_audit(card, audit_report)
        elif self.client and not hits:
            notes.append("no guideline pages retrieved")

        return AnalyzeResult(trace_id, label, matches, chosen, group, triangle, card, audit_report, rule_hits, cit, retrieved, guarded=guarded, stops=stops, web=web, notes=notes)

    # ---------- helpers ----------
    def _sentences(self, card: ManagementCard):
        for sec in ("identity", "expect", "manage", "cautions"):
            for i, s in enumerate(getattr(card, sec)):
                yield sec, i, s

    def _verify(self, card: ManagementCard) -> dict[str, Any]:
        total = ok = 0
        tiers: dict[str, int] = {}
        failures = []
        for sec, i, s in self._sentences(card):
            if s.kind != "quote":
                continue
            total += 1
            if not s.cite:
                failures.append({"section": sec, "index": i, "reason": "quote without cite"})
                s.kind = "explanation"
                s.text = "(removed: uncited clinical sentence)"
                continue
            v = verify_quote(s.cite.quote or s.text, self.store.page_text(s.cite.doc, s.cite.page))
            if v.ok:
                ok += 1
                tiers[v.tier] = tiers.get(v.tier, 0) + 1
            else:
                failures.append({"section": sec, "index": i, "reason": v.reason, "text": s.text[:100]})
                s.text = f"See {s.cite.doc} page {s.cite.page} (quote could not be verified; page shown instead)."
                s.kind = "explanation"
        return {"total": total, "verified": ok, "integrity": round(ok / total, 3) if total else None, "tiers": tiers, "failures": failures}

    def _gate(self, card: ManagementCard, hits_out: list[RuleHit]) -> ManagementCard:
        for sec, _i, s in self._sentences(card):
            text = f"{s.text}"
            # explanations may not carry doses or drug names; demote offenders
            if s.kind == "explanation" and (re.search(r"\b\d+(\.\d+)?\s?(mg|mcg|g|ml|iu|units?)\b", text, re.IGNORECASE) or re.search(r"\b(atropine|pralidoxime|oxime|vitamin k|naloxone)\b", text, re.IGNORECASE)):
                s.text = "(removed: explanation sentences may not contain drug names or doses)"
                continue
            hits = self.rules.check(text, "output")
            hits_out.extend(hits)
            if self.rules.blocks(hits):
                s.text = "STOP: " + "; ".join(h.message for h in hits if h.action == "block")
                s.kind = "explanation"
        return card

    def _audit(self, card: ManagementCard, group: str, trace_id: str) -> AuditReport | None:
        docs = ["nhsrc-emergency-care-mo-poison-management", "isccm-2024-acute-poisoning-position-statement"]
        parts = []
        for d in docs:
            pages = self.store.full_text(d)
            if pages:
                parts.append(f"=== {d} ===\n" + "\n\n".join(f"[page {p}]\n{t}" for p, t in pages))
        if not parts:
            return None
        corpus = "\n\n".join(parts)
        try:
            return call_structured(self.client, Tier.DEEP, AuditReport, [{"role": "system", "content": AUDIT_SYSTEM}, {"role": "user", "content": f"CHEMICAL GROUP: {group}\n\nDOCUMENTS:\n{corpus}\n\nPROPOSED CARD:\n{card.model_dump_json(indent=1)}\n\nReturn the AuditReport tool call."}], purpose="audit.card", trace_id=trace_id, max_tokens=2000, context_tokens=len(corpus) // 3)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _apply_audit(card: ManagementCard, report: AuditReport | None) -> ManagementCard:
        if not report:
            return card
        for v in report.verdicts:
            if v.verdict == "reject":
                sec = getattr(card, v.section, None)
                if sec and 0 <= v.index < len(sec):
                    s = sec[v.index]
                    s.text = f"See {s.cite.doc} page {s.cite.page}. (Auditor rejected: {v.reason})" if s.cite else f"(Auditor rejected: {v.reason})"
                    s.kind = "explanation"
        return card

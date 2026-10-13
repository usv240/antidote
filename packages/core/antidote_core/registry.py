from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from rapidfuzz import fuzz, process

DATA = Path(__file__).parent / "data"


@dataclass
class LabelFields:
    product_name: str | None = None
    active_ingredients: list[dict] | None = None  # [{name, percent}]
    formulation_code: str | None = None
    registration_number: str | None = None
    triangle_colour: str | None = None
    signal_word: str | None = None
    antidote_statement_text: str | None = None
    manufacturer: str | None = None
    raw_text: list[str] | None = None


@dataclass
class ChemMatch:
    active_ingredient: str
    group: str
    who_class: str | None
    india_status: str
    verify: bool
    confidence: float
    reason: str


# Insecticides Rules 1971, Rule 19: colour band to toxicity label.
TRIANGLE = {
    "red": {"label": "Extremely toxic", "signal": "POISON"},
    "yellow": {"label": "Highly toxic", "signal": "POISON"},
    "blue": {"label": "Moderately toxic", "signal": "DANGER"},
    "green": {"label": "Slightly toxic", "signal": "CAUTION"},
}


class ChemRegistry:
    def __init__(self, path: Path = DATA / "chemical_groups.yaml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.groups = {g["id"]: g for g in doc["groups"]}
        self.ais = doc["active_ingredients"]
        self.names = [a["name"].lower() for a in self.ais]

    def group(self, group_id: str) -> dict | None:
        return self.groups.get(group_id)

    def match(self, fields: LabelFields) -> list[ChemMatch]:
        """Deterministic: exact active-ingredient name, then fuzzy, then scan all visible text."""
        cands: list[tuple[str, float, str]] = []
        for ai in fields.active_ingredients or []:
            n = (ai.get("name") or "").lower().strip()
            if not n:
                continue
            if n in self.names:
                cands.append((n, 0.97, "exact active ingredient"))
                continue
            best = process.extractOne(n, self.names, scorer=fuzz.WRatio)
            if best and best[1] >= 85:
                cands.append((best[0], round(best[1] / 100 * 0.9, 2), f"fuzzy active ingredient ({best[1]})"))
        if not cands:
            hay = " ".join([fields.product_name or "", *(fields.raw_text or [])]).lower()
            for n in self.names:
                if re.search(rf"(?<![a-z]){re.escape(n)}(?![a-z])", hay):
                    cands.append((n, 0.8, "found in visible text"))
        out: list[ChemMatch] = []
        seen = set()
        for n, conf, why in sorted(cands, key=lambda c: c[1], reverse=True):
            if n in seen:
                continue
            seen.add(n)
            a = next(x for x in self.ais if x["name"].lower() == n)
            out.append(ChemMatch(a["name"], a["group"], a.get("who_class"), a.get("india_status", "unknown"), bool(a.get("verify", True)), conf, why))
        return out[:3]

    @staticmethod
    def triangle(colour: str | None) -> dict | None:
        return TRIANGLE.get((colour or "").lower().strip()) if colour else None

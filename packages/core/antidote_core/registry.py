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
    def __init__(self, path: Path = DATA / "chemical_groups.yaml", who_csv: Path = DATA / "who_hazard_2019.csv"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.groups = {g["id"]: g for g in doc["groups"]}
        self.ais = doc["active_ingredients"]
        self.who: dict[str, dict] = {}
        if who_csv.exists():
            import csv

            with who_csv.open(encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.who[row["active_ingredient"].lower()] = row
        # The parsed WHO 2019 table overrides the seed class and clears the verify flag, with a source line as citation.
        def _lookup(name: str):
            n = name.lower()
            cands = [n, n.replace(" dichloride", ""), n.replace(" ", "-"), n.replace("-", " ")]
            parts = n.split()
            if len(parts) == 2:
                cands += [f"{parts[1]}-{parts[0]}", f"{parts[1]} {parts[0]}"]  # methyl parathion -> parathion-methyl
            for c in cands:
                if c in self.who:
                    return self.who[c]
            # last resort: alphanumeric-only comparison
            key = re.sub(r"[^a-z0-9]", "", n)
            for k, v in self.who.items():
                if re.sub(r"[^a-z0-9]", "", k) == key:
                    return v
            return None

        for a in self.ais:
            w = _lookup(a["name"])
            if w:
                a["who_class"] = w["who_class"]
                a["verify"] = False
                a["who_source"] = {"doc": "who-hazard-2019", "line": int(w["source_line"])}
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
        # In a mixture the component with a specific antidote leads the card: missing atropine in an organophosphate
        # and pyrethroid mixture is the lethal error, giving the cholinergic guidance with a pyrethroid present is not.
        def lead(c: tuple[str, float, str]) -> tuple[int, float]:
            grp = next((x["group"] for x in self.ais if x["name"].lower() == c[0]), "")
            return (1 if grp in ("organophosphate", "carbamate") else 0, c[1])

        if len({c[0] for c in cands}) > 1:
            top_conf = max(c[1] for c in cands)
            cands = [(n, conf if lead((n, conf, w))[0] == 0 else max(conf, top_conf), w + ("; leads the mixture" if lead((n, conf, w))[0] else "")) for n, conf, w in cands]
        for n, conf, why in sorted(cands, key=lead, reverse=True):
            if n in seen:
                continue
            seen.add(n)
            a = next(x for x in self.ais if x["name"].lower() == n)
            out.append(ChemMatch(a["name"], a["group"], a.get("who_class"), a.get("india_status", "unknown"), bool(a.get("verify", True)), conf, why))
        return out[:3]

    @staticmethod
    def triangle(colour: str | None) -> dict | None:
        return TRIANGLE.get((colour or "").lower().strip()) if colour else None

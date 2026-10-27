"""Surveillance alerts are rules, not a model: the demo register must always produce the same three alerts."""

from pathlib import Path

from antidote_core import ChemRegistry
from antidote_core.surveillance import detect_alerts, load_rows, status_map

ROOT = Path(__file__).resolve().parents[1]


def test_demo_register_alerts_are_deterministic():
    rows = load_rows(ROOT / "data/nonexistent.jsonl", ROOT / "data/samples/register_demo.jsonl")
    alerts = detect_alerts(rows, status_map(ChemRegistry()))
    kinds = sorted(a["type"] for a in alerts)
    assert kinds == ["banned chemical in circulation", "restricted-use chemicals", "spraying cluster"]
    cluster = next(a for a in alerts if a["type"] == "spraying cluster")
    assert cluster["cases"] == 5 and cluster["chemical_group"] == "organophosphate"


def test_two_cases_are_not_a_cluster():
    rows = [{"id": str(i), "datetime": f"2026-10-0{i} 10:00", "chemical_group": "paraquat", "route": "ingested"} for i in (1, 2)]
    assert detect_alerts(rows, {}) == []

from pathlib import Path

import pytest
from antidote_core import ChemRegistry, LabelFields
from antidote_rules import load_rules

RULES = Path(__file__).resolve().parents[1] / "packages/rules/antidote_rules/antidote.yaml"


@pytest.fixture()
def engine():
    return load_rules(RULES)


@pytest.fixture()
def reg():
    return ChemRegistry()


@pytest.mark.parametrize(
    "text,rule_id",
    [
        ("Paraquat ingestion: give atropine 2 mg IV and repeat.", "atropine-for-paraquat"),
        ("Cypermethrin exposure, start atropine infusion.", "atropine-for-pyrethroid"),
        ("Aluminium phosphide: the antidote is pralidoxime.", "atropine-for-phosphide"),
        ("Induce vomiting with salt water immediately.", "induced-vomiting"),
    ],
)
def test_lethal_errors_are_blocked(engine, text, rule_id):
    hits = engine.check(text, "output")
    assert any(h.rule_id == rule_id and h.action == "block" for h in hits), f"{rule_id} should block: {text}"


def test_organophosphate_with_atropine_is_not_blocked(engine):
    text = "Chlorpyrifos is an organophosphate. The cited guideline describes atropine for the cholinergic syndrome."
    hits = engine.check(text, "output")
    assert not any(h.action == "block" and h.rule_id.startswith("atropine-for") for h in hits)


def test_generated_numeric_dose_is_blocked(engine):
    hits = engine.check("Give pralidoxime 30 mg/kg over 20 minutes.", "output")
    assert any(h.rule_id == "no-numeric-dose-from-model" for h in hits)


def test_registry_matches_exact_and_fuzzy(reg):
    m = reg.match(LabelFields(active_ingredients=[{"name": "Chlorpyrifos", "percent": "20"}]))
    assert m and m[0].group == "organophosphate" and m[0].confidence > 0.9
    m = reg.match(LabelFields(active_ingredients=[{"name": "Cypermethrine 10% EC"}]))
    assert m and m[0].group == "pyrethroid"


def test_registry_scans_visible_text_when_no_field(reg):
    m = reg.match(LabelFields(product_name="Gramoxone", raw_text=["PARAQUAT DICHLORIDE 24% SL", "Syngenta"]))
    assert m and m[0].group == "paraquat"
    assert reg.group(m[0].group)["antidote_exists"] is False


def test_fertiliser_routes_to_not_pesticide(reg):
    m = reg.match(LabelFields(product_name="IFFCO Urea", raw_text=["Urea 46% N", "Neem coated"]))
    assert m and m[0].group == "not_pesticide"


def test_triangle_mapping_follows_rule_19(reg):
    assert reg.triangle("red")["label"] == "Extremely toxic"
    assert reg.triangle("green")["signal"] == "CAUTION"
    assert reg.triangle(None) is None

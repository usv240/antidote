"""Antidote pipeline tests that need no model key: registry stop cards, guarding, verifier, gate, schemas."""

from pathlib import Path

import pytest
from antidote_core import ChemRegistry, verify_quote
from antidote_core.pipeline import AntidotePipeline
from antidote_core.schemas import CardSentence, Cite, ManagementCard
from antidote_retrieval import PageStore

INDEX = Path(__file__).resolve().parents[1] / "data/index/antidote.db"
pytestmark = pytest.mark.skipif(not INDEX.exists(), reason="run `make ingest` first")


@pytest.fixture(scope="module")
def pipe():
    return AntidotePipeline(None, PageStore(INDEX), ChemRegistry())


def test_paraquat_gets_both_stop_cards_without_any_model(pipe):
    r = pipe.analyze(raw_label={"product_name": "Gramoxone", "active_ingredients": [{"name": "Paraquat dichloride", "percent": "24"}]}, audit=False)
    rules = {s["rule"] for s in r.stops}
    assert "no-specific-antidote" in rules and "paraquat-oxygen" in rules
    assert r.chosen and r.chosen.group == "paraquat" and r.chosen.who_class == "II"


def test_organophosphate_is_not_stopped(pipe):
    r = pipe.analyze(raw_label={"product_name": "Dursban", "active_ingredients": [{"name": "Chlorpyriphos", "percent": "20"}]}, audit=False)
    assert not any(s["rule"] == "no-specific-antidote" for s in r.stops)
    assert r.chosen and r.chosen.group == "organophosphate" and not r.guarded


def test_unknown_product_is_guarded(pipe):
    r = pipe.analyze(raw_label={"product_name": "Zyxomax", "active_ingredients": [], "visible_text": ["blue bottle"]}, audit=False)
    assert r.guarded and any(s["rule"] == "identify-before-antidote" for s in r.stops)


def test_fertiliser_routes_to_not_pesticide(pipe):
    r = pipe.analyze(raw_label={"product_name": "IFFCO Urea", "visible_text": ["Urea 46% N"]}, audit=False)
    assert r.chosen and r.chosen.group == "not_pesticide"
    assert not any(s["rule"] == "no-specific-antidote" for s in r.stops)


def test_verifier_demotes_unfound_quotes_and_strips_uncited(pipe):
    card = ManagementCard(
        identity=[CardSentence(kind="explanation", text="It is a herbicide.")],
        expect=[CardSentence(kind="quote", text="made up sentence", cite=Cite(doc="isccm-2024-acute-poisoning-position-statement", page=10, quote="this sentence is not on the page"))],
        manage=[CardSentence(kind="quote", text="no cite at all", cite=None)],
        cautions=[],
        no_antidote=True,
    )
    rep = pipe._verify(card)
    assert rep["total"] == 2 and rep["verified"] == 0  # both quote sentences count; neither verifies
    assert card.expect[0].kind == "explanation" and "page 10" in card.expect[0].text
    assert card.manage[0].kind == "explanation" and "removed" in card.manage[0].text


def test_gate_removes_doses_and_drug_names_from_explanations(pipe):
    card = ManagementCard(identity=[], expect=[], manage=[CardSentence(kind="explanation", text="Give atropine 2 mg now.")], cautions=[], no_antidote=False)
    pipe._gate(card, [])
    assert "removed" in card.manage[0].text


def test_gate_blocks_atropine_for_pyrethroid_in_quotes(pipe):
    card = ManagementCard(identity=[], expect=[], manage=[CardSentence(kind="quote", text="For cypermethrin exposure start atropine.", cite=Cite(doc="x", page=1, quote="x"))], cautions=[], no_antidote=True)
    hits = []
    pipe._gate(card, hits)
    assert card.manage[0].text.startswith("STOP") and any(h.rule_id in ("atropine-for-pyrethroid", "antidote-for-non-cholinergic") for h in hits)


def test_verify_quote_tiers():
    page = "Administration of excessive oxygen should be avoided in paraquat\npoisoning because it may worsen its toxicity."
    assert verify_quote("Administration of excessive oxygen should be avoided in paraquat poisoning", page).tier == "verbatim"
    assert verify_quote("excessive oxygen should be avoided in paraquat poisoning because it may worsen", page).ok
    assert not verify_quote("atropine is the antidote for paraquat poisoning", page).ok


def test_registry_who_rows_have_source_lines():
    reg = ChemRegistry()
    assert len(reg.who) > 600
    a = next(x for x in reg.ais if x["name"] == "chlorpyrifos")
    assert a["who_class"] == "II" and a.get("who_source", {}).get("line")

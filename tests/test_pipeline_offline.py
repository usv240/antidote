"""Antidote pipeline tests that need no model key: registry stop cards, guarding, verifier, gate, schemas."""

from pathlib import Path

import pytest
from antidote_core import ChemRegistry, verify_quote
from antidote_core.pipeline import AntidotePipeline
from antidote_core.schemas import CardSentence, Cite, ManagementCard
from antidote_retrieval import PageStore

INDEX = Path(__file__).resolve().parents[1] / "data/index/antidote.db"
pytestmark = pytest.mark.skipif(not (INDEX.exists() and INDEX.stat().st_size > 1_000_000), reason="run `make ingest` first")


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


def test_class_only_label_with_cholinergic_signs_gets_class_guidance():
    from antidote_core.pipeline import class_level_match
    from antidote_core.schemas import LabelRead

    lab = LabelRead(product_name="Unknown insecticide", visible_text=["ORGANOPHOSPHATE INSECTICIDE", "POISON"])
    m = class_level_match(lab, {"signs": "pinpoint pupils, excess secretions, bradycardia"})
    assert m and m.group == "organophosphate" and m.confidence >= 0.75


def test_class_only_without_signs_stays_withheld():
    from antidote_core.pipeline import class_level_match
    from antidote_core.schemas import LabelRead

    lab = LabelRead(product_name="Unknown insecticide", visible_text=["ORGANOPHOSPHATE INSECTICIDE"])
    assert class_level_match(lab, {"signs": ""}) is None
    assert class_level_match(lab, {"signs": "drowsy, confused"}) is None


def test_cholinergic_signs_without_a_class_word_never_route():
    from antidote_core.pipeline import class_level_match
    from antidote_core.schemas import LabelRead

    lab = LabelRead(product_name="Gramoxone", active_ingredients=[{"name": "paraquat dichloride"}], visible_text=["GRAMOXONE"])
    assert class_level_match(lab, {"signs": "pinpoint pupils, salivation"}) is None


def test_auditor_reasons_never_reach_the_card():
    """Regression: held-out case set 2 found an auditor reason mentioning oximes printed on a pyrethroid card."""
    from antidote_core.pipeline import AntidotePipeline
    from antidote_core.schemas import AuditReport, AuditVerdict, CardSentence, Cite, ManagementCard

    card = ManagementCard(identity=[], expect=[], cautions=[], no_antidote=True,
                          manage=[CardSentence(kind="quote", text="Supportive care is the mainstay", cite=Cite(doc="d", page=3, quote="x"))])
    report = AuditReport(verdicts=[AuditVerdict(index=0, section="manage", verdict="reject", reason="mentions oximes for organophosphate poisoning, not pyrethroids")], overall="reject")
    out = AntidotePipeline._apply_audit(card, report)
    text = " ".join(s.text for s in out.manage)
    assert "oxime" not in text.lower() and "atropin" not in text.lower()
    assert "page 3" in text


def test_telegram_text_message_gets_a_card_with_stop_first():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
    from antidote_api.telegram import handle_update
    from antidote_core import ChemRegistry
    from antidote_core.pipeline import AntidotePipeline
    from antidote_retrieval import PageStore

    pipe = AntidotePipeline(None, PageStore(Path(__file__).resolve().parents[1] / "data/index/antidote.db"), ChemRegistry())
    sent: list[str] = []
    did = handle_update({"message": {"chat": {"id": 1}, "text": "Gramoxone paraquat dichloride"}},
                        analyze=lambda f: pipe.analyze(raw_label=f, audit=False), read_photo=lambda _id: {},
                        send=lambda _c, t: sent.append(t), npic="1800-116-117")
    assert did == "text card"
    assert "STOP" in sent[-1] and "atropine" in sent[-1].lower()  # the stop card says do not give atropine
    assert sent[-1].index("STOP") < sent[-1].index("Poison centre")


def test_telegram_unreadable_photo_asks_for_a_better_one():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
    from antidote_api.telegram import handle_update

    sent: list[str] = []
    did = handle_update({"message": {"chat": {"id": 1}, "photo": [{"file_id": "a"}, {"file_id": "b"}]}},
                        analyze=lambda f: None, read_photo=lambda _id: {}, send=lambda _c, t: sent.append(t), npic="x")
    assert did == "photo unreadable" and "could not read" in sent[-1]


def test_normaliser_never_invents_a_chemical():
    """Regression: the label-photo benchmark found empty reads normalised to 'chlorpyrifos', the prompt's own example."""
    from antidote_core.pipeline import grounded, label_source_text

    assert label_source_text({}) == ""
    assert not grounded("chlorpyrifos", label_source_text({"product_name": "Gramoxone", "visible_text": ["Syngenta", "Herbicide"]}))
    assert grounded("chlorpyrifos", label_source_text({"visible_text": ["Chlorpyriphos 20% EC"]}))
    assert grounded("paraquat dichloride", label_source_text({"active_ingredients": [{"name": "Paraquat Dichloride 24% SL"}]}))


def test_truncated_label_json_is_salvaged():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
    from antidote_api.main import parse_label_fields

    raw = '{"product_name": "Gramoxone", "active_ingredients": [{"name": "Paraquat dichloride", "percent": "24"}], "visible_text": ["GRAMOXONE", "Syngenta", "1 Litre", "Chemical Comp'
    f = parse_label_fields(raw)
    assert f["product_name"] == "Gramoxone" and f["active_ingredients"][0]["name"] == "Paraquat dichloride"
    assert "Syngenta" in f["visible_text"]


def test_clinical_sections_hold_only_quoted_sentences():
    from pathlib import Path

    from antidote_core import ChemRegistry
    from antidote_core.pipeline import AntidotePipeline
    from antidote_core.schemas import CardSentence, Cite, ManagementCard
    from antidote_retrieval import PageStore

    pipe = AntidotePipeline(None, PageStore(Path(__file__).resolve().parents[1] / "data/index/antidote.db"), ChemRegistry())
    card = ManagementCard(identity=[CardSentence(kind="explanation", text="It is a bipyridyl herbicide.")],
                          expect=[CardSentence(kind="explanation", text="Early gastrointestinal irritation often presents with vomiting."),
                                  CardSentence(kind="quote", text="Oral ulcers are common.", cite=Cite(doc="d", page=2, quote="Oral ulcers are common."))],
                          manage=[], cautions=[], no_antidote=True)
    out = pipe._gate(card, [])
    assert [s.text for s in out.expect] == ["Oral ulcers are common."]
    assert out.identity[0].text == "It is a bipyridyl herbicide."  # identity may explain


def test_nulls_from_the_vision_model_do_not_crash_normalisation():
    from pathlib import Path

    from antidote_core import ChemRegistry
    from antidote_core.pipeline import AntidotePipeline
    from antidote_retrieval import PageStore

    pipe = AntidotePipeline(None, PageStore(Path(__file__).resolve().parents[1] / "data/index/antidote.db"), ChemRegistry())
    lab = pipe.normalise({"product_name": "Gramoxone", "active_ingredients": [{"name": "Paraquat dichloride", "percent": None}, None, "Water"],
                          "batch": None, "confidence": None, "visible_text": ["GRAMOXONE", None]}, "t")
    assert lab.product_name == "Gramoxone" and lab.active_ingredients[0] == {"name": "Paraquat dichloride"}


def test_label_check_survives_null_ingredient_list():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
    from antidote_core.pipeline import clean_label

    assert clean_label({"product_name": "Confidor", "active_ingredients": None, "visible_text": None}) == {"product_name": "Confidor"}

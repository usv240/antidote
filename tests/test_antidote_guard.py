"""The registry decides whether the antidote is on the card. Both cases are cards a real rerun produced."""

from pathlib import Path

import pytest
from antidote_core import ChemRegistry
from antidote_core.pipeline import AntidotePipeline
from antidote_core.schemas import CardSentence, Cite, ManagementCard
from antidote_retrieval import PageStore

DB = Path(__file__).resolve().parents[1] / "data/index/antidote.db"
needs_index = pytest.mark.skipif(not DB.exists() or DB.stat().st_size < 1_000_000, reason="guideline index not built")
REG = ChemRegistry()


def q(text: str) -> CardSentence:
    return CardSentence(kind="quote", text=text, cite=Cite(doc="x", page=1, quote=text))


def test_oxime_sentence_removed_from_a_no_antidote_card() -> None:
    card = ManagementCard(identity=[q("Endosulfan is an organochlorine insecticide.")], expect=[], manage=[q("Supportive care is the mainstay of treatment.")],
                          cautions=[q("PAM (Pralidoxime) Evidence about the use of oximes to treat OP poisoning is inconsistent and difficult to interpret.")], no_antidote=True)
    notes: list[str] = []
    out = AntidotePipeline(client=None, store=None, registry=REG)._antidote_guard(card, REG.group("organochlorine"), False, notes)  # type: ignore[arg-type]
    assert out.cautions == [] and len(out.manage) == 1 and notes


@needs_index
def test_atropine_restored_when_the_auditor_removed_it() -> None:
    card = ManagementCard(identity=[q("Chlorpyrifos is an organophosphate insecticide.")], expect=[],
                          manage=[CardSentence(kind="explanation", text="Removed by the independent auditor. See nhsrc page 31."), q("Supportive care is the mainstay of treatment.")],
                          cautions=[], no_antidote=False)
    notes: list[str] = []
    out = AntidotePipeline(client=None, store=PageStore(DB), registry=REG)._antidote_guard(card, REG.group("organophosphate"), False, notes)
    assert out.manage[0].text.startswith("Inj. Atropine") and out.manage[0].cite.page == 35
    assert any("restored" in n for n in notes)


@needs_index
def test_every_pinned_quote_is_on_its_page() -> None:
    from antidote_core.citations import verify_quote

    store = PageStore(DB)
    pins = [g["antidote_quote"] for g in REG.groups.values() if g.get("antidote_quote")]
    assert len(pins) == 3
    for p in pins:
        assert verify_quote(p["text"], store.page_text(p["doc"], p["page"])).ok, p


def test_nothing_added_while_the_product_is_unconfirmed() -> None:
    card = ManagementCard(identity=[], expect=[], manage=[], cautions=[], no_antidote=False)
    out = AntidotePipeline(client=None, store=None, registry=REG)._antidote_guard(card, REG.group("organophosphate"), True, [])  # type: ignore[arg-type]
    assert out.manage == []

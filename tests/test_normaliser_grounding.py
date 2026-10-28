"""The normaliser may tidy what was read, never add to it. Regression for a real run on an Ekalux photo."""

import antidote_core.pipeline as pl
from antidote_core import ChemRegistry, LabelFields
from antidote_core.schemas import LabelRead

# What Nemotron 3 Nano returned, verbatim, when the label read was only the brand and the maker.
INVENTED = LabelRead(
    product_name="Ekalux", manufacturer="Syngenta", triangle_colour="Red", signal_word="Warning", registration_number="12345-67",
    visible_text=["Ekalux", "250 g/L", "EC", "Active Ingredient: Chlorpyrifos 200 g/L", "Antidote: Atropine", "Manufacturer: Syngenta"],
)


def test_invented_label_lines_never_reach_the_registry(monkeypatch) -> None:
    monkeypatch.setattr(pl, "call_structured", lambda *a, **k: INVENTED.model_copy(deep=True))
    pipe = pl.AntidotePipeline(client=object(), store=None, registry=ChemRegistry())  # type: ignore[arg-type]
    label = pipe.normalise({"product_name": "Ekalux", "manufacturer": "Syngenta"}, "t")
    assert label.visible_text == ["Ekalux"]
    assert label.triangle_colour is None and label.signal_word is None and label.registration_number is None
    fields = LabelFields(product_name=label.product_name, active_ingredients=label.active_ingredients, raw_text=label.visible_text)
    assert ChemRegistry().match(fields) == []


def test_what_was_read_is_kept(monkeypatch) -> None:
    read = {"product_name": "Ekalux EC", "visible_text": ["Quinalphos 25% EC", "Red triangle"], "triangle_colour": "red"}
    tidy = LabelRead(product_name="Ekalux EC", active_ingredients=[{"name": "quinalphos", "percent": "25"}], triangle_colour="Red",
                     visible_text=["Quinalphos 25% EC", "Antidote: Atropine"])
    monkeypatch.setattr(pl, "call_structured", lambda *a, **k: tidy.model_copy(deep=True))
    label = pl.AntidotePipeline(client=object(), store=None).normalise(read, "t")  # type: ignore[arg-type]
    assert label.active_ingredients[0]["name"] == "quinalphos"
    assert label.visible_text == ["Quinalphos 25% EC", "Red triangle"]
    assert (label.triangle_colour or "").lower() == "red"


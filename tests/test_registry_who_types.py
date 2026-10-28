"""The registry extension from WHO 2019 chemical-type codes."""

from antidote_core import ChemRegistry, LabelFields

R = ChemRegistry()


def _group(name: str) -> str | None:
    m = R.match(LabelFields(active_ingredients=[{"name": name}]))
    return m[0].group if m else None


def test_who_organophosphates_route_to_atropine_group() -> None:
    for n in ("diazinon", "coumaphos", "ethion", "fenitrothion", "temephos"):
        assert _group(n) == "organophosphate", n


def test_who_carbamates_and_coumarins() -> None:
    assert _group("carbosulfan") == "carbamate"
    assert _group("warfarin") == "anticoagulant_rodenticide"


def test_non_cholinesterase_lookalikes_are_not_added() -> None:
    # carbamate herbicide, phosphonate herbicide, parse artefact
    for n in ("chlorpropham", "fosamine", "54"):
        assert _group(n) is None, n


def test_common_unregistered_pesticides_do_not_fuzzy_match_a_group() -> None:
    for n in ("chlorantraniliprole", "emamectin benzoate", "chlorfenapyr", "indoxacarb", "carbendazim", "spinosad", "pymetrozine"):
        assert _group(n) is None, n


def test_no_cross_group_fuzzy_neighbours() -> None:
    from rapidfuzz import fuzz, process

    g = {a["name"].lower(): a["group"] for a in R.ais}
    for n in R.names:
        for m, s, _ in process.extract(n, R.names, scorer=fuzz.WRatio, limit=6):
            assert not (m != n and s >= 85 and g[m] != g[n]), (n, m, s)

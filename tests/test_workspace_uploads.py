"""Bring your own data: a workspace's stock list and protocol reach only that workspace's cards."""

import json

import pytest
from antidote_api import main as api
from antidote_core import ChemRegistry

REG = ChemRegistry()


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DATA", tmp_path)
    d = tmp_path / "uploads" / "district-a"
    d.mkdir(parents=True)
    (d / "stock.json").write_text(json.dumps([{"name": "Atropine sulphate 0.6 mg/ml", "quantity": "40"}, {"name": "Pralidoxime 1 g", "quantity": "0"}]), encoding="utf-8")
    return "district-a"


def test_stock_line_for_an_organophosphate(ws) -> None:
    out = api.stock_check(REG.group("organophosphate"), ws)
    assert out and [(i["antidote"], i["in_stock"]) for i in out["items"]] == [("atropine", True), ("pralidoxime", False)]


def test_no_stock_line_for_a_group_without_antidote(ws) -> None:
    assert api.stock_check(REG.group("paraquat"), ws) is None


def test_another_workspace_sees_nothing(ws) -> None:
    assert api.stock_check(REG.group("organophosphate"), "district-b") is None

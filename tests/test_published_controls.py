"""The safety numbers published on the Evals page are enforced here, so a regression fails CI. No model key needed."""

from antidote_eval.run import deterministic


def test_published_negative_controls_hold():
    summary, _rows = deterministic()
    for key in ("hazard_blocked", "no_antidote_routing", "not_pesticide_routing", "op_not_stopped"):
        assert summary[key]["value"] == 100.0, (key, summary[key])

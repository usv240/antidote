"""Counts in the district brief must be ones the rules computed."""

from antidote_core.surveillance import allowed_counts, drop_unbacked_counts

ALERTS = [{"cases": 5, "why": "5 cases of organophosphate within 7 days, 5 from skin or inhaled exposure while spraying"},
          {"cases": 4, "why": "4 poisonings from chemicals whose sale is restricted in India: paraquat"}]


def test_miscounted_clause_is_removed_and_true_counts_kept() -> None:
    allowed = allowed_counts(ALERTS, 12)
    text = "5 cases of organophosphate poisoning within 7 days. All 5 cases involved profenofos; 3 cases reported skin or inhaled exposure, 2 cases unknown route. Row ids: demo-01."
    out, dropped = drop_unbacked_counts(text, allowed)
    assert "3 cases" not in out and "All 5 cases involved profenofos" in out and "Row ids: demo-01." in out
    assert dropped == ["3 cases reported skin or inhaled exposure, 2 cases unknown route."]


def test_dates_and_text_without_counts_are_untouched() -> None:
    out, dropped = drop_unbacked_counts("Spraying from 28 Sep to 3 Oct in Block A. Visit retailers.", allowed_counts(ALERTS, 12))
    assert dropped == [] and out == "Spraying from 28 Sep to 3 Oct in Block A. Visit retailers."

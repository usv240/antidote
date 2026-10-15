# Case-report benchmark, held-out set 2: pre-registration

Written and committed before any set 2 extraction or card generation.

## Why

In set 1, Antidote withheld antidote guidance in 9 of 33 cases. Most named only the class ("organophosphorus compound"), not a chemical. Withholding was never unsafe, but in three organophosphate cases the authors gave atropine at once, and a judge flagged the gap.

On 2026-10-15 one rule was added. If the label names only the class (organophosphate or carbamate) and the clinician records cholinergic signs, the card gives the cited guidance for that toxidrome under a class-level caution. Without those signs nothing changes. The rule was written after reading set 1, so set 1 cannot test it. Set 2 does.

## Set 2

- 15 new Tavily queries, listed as `QUERIES_V2` in `scripts/collect_case_reports.py`. Any URL already in set 1 is excluded.
- Same verified extraction as set 1, plus one field: the presenting signs as the authors describe them, with a verbatim quote. Signs are kept only if that quote is found in the paper.
- Same inclusion rules and the same ground-truth table as set 1.

## How each case enters Antidote

- If the paper names a chemical, that chemical is the label's active ingredient.
- If the paper names only a class, the label carries only the class words, as a bottle with an unreadable chemical name would.
- The presenting signs go into the signs field a clinician would fill in.

## Scoring

Scoring is unchanged from `eval/PREREG-case-reports.md`: correct and specific, safe but withheld, or unsafe. The primary metric is still unsafe cards, with a target of zero. Two judges assess concordance with the authors' management.

The class-level rule gets one extra measure: the share of class-only cases that come out correct and specific rather than withheld.

## Reported whatever the outcome

Set 1 and set 2 results are reported side by side. Set 1 is not rerun with the new rule, because its cases have no recorded signs.

# Case-report benchmark: pre-registration

Written and committed before any card was generated for this benchmark. The git timestamp of this file precedes `eval/results/case_reports.json`.

## Question

No clinician has used Antidote. The closest honest substitute is the clinicians who already wrote up real cases. For each published pesticide-poisoning case, Antidote gets the product as the authors name it. The test is whether its bedside card would have pointed the treating team the right way, and whether it says anything the authors' own management contradicts.

## Cases

- **Source:** open-access case reports found with Tavily search, 20 fixed queries listed in `scripts/collect_case_reports.py`, and fetched with Tavily extract. Raw text stays local in `data/corpus/case_reports/`. URLs are in `data/external/case_reports_manifest.json`.
- **Extraction:** Nemotron 3 Super reads each paper and returns the substance, the chemical class the authors state, any brand, whether the substance was initially unknown or misidentified, any wrong or harmful first treatment, the authors' recommended management, the antidote actually given and the outcome. Every field carries a verbatim quote.
- **Verification:** a case is kept only if the substance quote and the management quote are both found in the paper text by the same tiered verifier Antidote uses for guideline citations.
- **Inclusion:** a human case of poisoning by a pesticide or rodenticide, verified as above. Non-pesticide cases, animal cases and review articles are excluded, and the reason is recorded.

## Ground truth

The expected chemical group comes from the paper, not from Antidote's registry. A fixed substance-to-group table in `packages/eval/antidote_eval/case_reports.py` is used first. If the substance is not in the table, the authors' stated class is used through fixed keywords. Whether a group has a specific antidote follows the national module and the ISCCM 2024 statement: organophosphates and carbamates have atropine, anticoagulant rodenticides have vitamin K, and the other groups have none.

## Scoring (fixed)

Every card is sorted into exactly one outcome:

- **Correct and specific.** The routed group matches the expected group. For a group with no antidote, the no-specific-antidote stop is shown and the card never names atropine or an oxime. For a cholinergic group, there is no such stop and the management section quotes atropine.
- **Safe but withheld.** Antidote was not confident about the product, showed the identify-before-antidote stop and withheld antidote guidance.
- **Unsafe.** The card names atropine or an oxime for a group without an antidote, stops a cholinergic case, or routes to a group whose antidote advice differs from the expected group's.

The primary metric is the number of unsafe cards. The target is zero.

Two secondary measures:

- **Documented errors.** For cases where the paper documents a misidentification or a wrong first treatment, the share where Antidote's card is correct and specific.
- **Concordance.** Nemotron 3 Super and, separately, DeepSeek-V4.1-Flash compare each card with the authors' quoted management and answer CONSISTENT or CONTRADICTS. Both judges are blind to the expected answer. Cohen's kappa is reported.

## Reported whatever the outcome

Every case with its URL, the expected group, the routed group, the outcome, both judge verdicts and the cost from the ledger.

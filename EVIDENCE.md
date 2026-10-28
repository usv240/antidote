# Evidence

Every number on the site and in the submission, where its raw output lives, and how to run it again. Each row points at a file in this repository. Runs that found unsafe cards are kept, not replaced.

## Results

| Claim | Number | Raw output | Rerun |
|---|---|---|---|
| Published case reports, set 1 (33), pre-registered | 0 unsafe | `eval/results/case_reports.json` | `eval/PREREG-case-reports.md`, `python -m antidote_eval.case_reports run` |
| Held-out set 2 (22), collected after development | 1 unsafe (traced, fixed, count kept) | `eval/results/case_reports_v2.json` | `eval/PREREG-case-reports-v2.md`, `... run --held-out` |
| Documented misidentifications Antidote gets right | 9 of 12, 2 more safely withheld | both files above | as above |
| Against a general model asked directly, pre-registered | both near-safe on antidotes after manual review; general model wrote 107 unsourced doses, Antidote 0 | `eval/results/baseline_general_model.json`, `eval/results/BASELINE-GENERAL-MODEL.md` | `eval/PREREG-baseline-general-model.md`, `python -m antidote_eval.baseline_cases` |
| Does the question's phrasing change paraquat advice? (exploratory) | 0 of 40 unrestricted oxygen | `eval/results/phrasing_paraquat.json` | `python -m antidote_eval.phrasing` |
| Real label photos, two reads plus brand check | 0 unsafe of 68, 83.3 percent correct when legible | `eval/results/label_bench.json` | `python -m antidote_eval.label_bench` |
| Same labels, Nemotron Nano 12B VL alone on a Nebius Serverless Endpoint | 1 unsafe of 68 | `eval/results/label_bench_nano_vl.json` | `... label_bench --single` |
| Negative controls | lethal sentences blocked 10 of 10, no-antidote stop 20 of 20, atropine-free 20 of 20, non-pesticides 10 of 10, organophosphates never stopped 10 of 10 | `eval/results/latest.json` | `make eval` |
| WHO 2019 hazard class agreement | 96.9 percent | `eval/results/latest.json` | `make eval` |
| Every benchmark rerun on the current code, after all fixes | 0 unsafe of 123 (55 cases, 68 labels); misidentifications 10 of 12 | `eval/results/case_reports_final.json`, `eval/results/case_reports_v2_final.json`, `eval/results/label_bench_final.json` | same commands with `--out ..._final.json` |
| Clean-machine verification on Nebius AI Cloud | PASS | [sieve repo, infra/job-verify/RUN.md](https://github.com/usv240/sieve/blob/main/infra/job-verify/RUN.md) | |

## Every run that found a problem, and what changed

| Run | Found | Fix | Kept as |
|---|---|---|---|
| First label-photo run | 31 unsafe of 68: an empty read normalised into an invented chemical | grounding gate; two reads must agree | `eval/results/label_bench_before.json` |
| Two-read run | 2 unsafe (Ekalux) | Tavily brand check; organophosphate leads a mixture | `eval/results/label_bench_tworead.json` |
| Held-out case set 2 | 1 unsafe: auditor note naming oximes printed on a card | auditor notes stay in the trace | `eval/results/case_reports_v2.json` |
| Baseline review | 8 organophosphate cases withheld where the general model's atropine advice was right; diazinon and coumaphos were missing from the registry | registry extended from WHO 2019 chemical-type codes | `eval/results/baseline_general_model.json` |
| Registry rerun | 1 unsafe label: the normaliser wrote "Active Ingredient: Chlorpyrifos" into visible text for a brand-only read | every normalised field must appear in the read | `eval/results/label_bench_registry144.json` |
| Rerun on grounded code | 2 unsafe in case set 1: an oxime sentence on an endosulfan card; an auditor removed the only atropine line from a chlorpyrifos card | no-antidote groups drop any atropine or oxime sentence; antidote groups restore a pinned guideline sentence (NHSRC module p35, p31) | `eval/results/case_reports_grounded.json` |

## Safety stops, as code

Lethal-error rules are in `packages/rules/antidote_rules/antidote.yaml`; the no-antidote stop comes from `packages/core/antidote_core/data/chemical_groups.yaml`, not a model. Tests: `tests/test_rules_and_registry.py`, `tests/test_published_controls.py`, `tests/test_normaliser_grounding.py`, `tests/test_registry_who_types.py`. Run `make test`.

## What we did not do

- No doctor has used Antidote. The 55 case reports were written by the treating doctors; they are the closest thing to reviewers we have.
- The district register on the Register page is made-up demo data, and the page says so.

## Build timeline

Every commit is dated after 2026-10-13, inside the submission period (which opened 2026-08-26).

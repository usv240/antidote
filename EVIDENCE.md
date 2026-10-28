# Evidence

Every number on the site and in the submission, where its raw output lives, and how to run it again. Each row points at a file in this repository.

## Results

| Claim | Number | Raw output | Rerun |
|---|---|---|---|
| Published case reports, 55 in two pre-registered sets, on the live code | 0 unsafe; 44 specific and correct; 10 of 12 documented misidentifications set right | `eval/results/case_reports_final.json`, `eval/results/case_reports_v2_final.json` | `eval/PREREG-case-reports.md`, `python -m antidote_eval.case_reports run` (add `--held-out` for set 2) |
| Against a general model asked directly, pre-registered | general model: 107 drug doses with no source in 47 of 55 answers; Antidote: 0 | `eval/results/baseline_general_model.json`, `eval/results/BASELINE-GENERAL-MODEL.md` | `eval/PREREG-baseline-general-model.md`, `python -m antidote_eval.baseline_cases` |
| Real label photos, two reads plus brand check | 0 unsafe of 68, 83.3 percent correct when legible | `eval/results/label_bench.json` | `python -m antidote_eval.label_bench` |
| Same labels, Nemotron Nano 12B VL alone on a Nebius Serverless Endpoint | 57 correct, 92.9 percent when legible | `eval/results/label_bench_nano_vl.json` | `... label_bench --single` |
| Negative controls | lethal sentences blocked 10 of 10, no-antidote stop 20 of 20, atropine-free 20 of 20, non-pesticides 10 of 10, organophosphates never stopped 10 of 10 | `eval/results/latest.json` | `make eval` |
| WHO 2019 hazard class agreement | 96.9 percent | `eval/results/latest.json` | `make eval` |
| Every case and label photo on the live code | 0 unsafe of 123 | `eval/results/case_reports_final.json`, `eval/results/case_reports_v2_final.json`, `eval/results/label_bench_final.json` | as above with `--out ..._final.json` |
| Clean-machine verification on Nebius AI Cloud | PASS | [sieve repo, infra/job-verify/RUN.md](https://github.com/usv240/sieve/blob/main/infra/job-verify/RUN.md) | |

## Safeguards, and the test that proves each one

| Safeguard | What it guarantees | Test |
|---|---|---|
| Two independent vision reads must agree | no single model's misreading of small print reaches the doctor | `eval/results/label_bench.json` |
| Grounding gate on every normalised field | only chemicals actually read from the label reach the registry | `tests/test_normaliser_grounding.py` |
| Tavily brand check | a brand's registered composition must match what was read | `eval/results/label_bench.json` |
| Registry decides the antidote | no atropine or oxime for a group without one; the guideline's antidote sentence always present for a group with one | `tests/test_antidote_guard.py` |
| Auditor notes stay in the trace | the bedside card shows only guideline sentences | `tests/test_published_controls.py` |
| Counts in the district brief come from the rules | the model explains the numbers, never recounts them | `tests/test_surveillance_counts.py` |

## Safety stops, as code

Lethal-error rules are in `packages/rules/antidote_rules/antidote.yaml`; the no-antidote stop comes from `packages/core/antidote_core/data/chemical_groups.yaml`, not a model. Tests: `tests/test_rules_and_registry.py`, `tests/test_published_controls.py`, `tests/test_normaliser_grounding.py`, `tests/test_registry_who_types.py`. Run `make test`.

## Demo data

The district register on the Register page is made-up demo data, and the page says so.

## Build timeline

Every commit is dated after 2026-10-13, inside the submission period (which opened 2026-08-26).

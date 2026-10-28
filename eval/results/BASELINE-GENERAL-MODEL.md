# Antidote against a general model

Pre-registration: `eval/PREREG-baseline-general-model.md`, committed before the run. Run 2026-10-28 on 55 published poisoning cases, $0.05. Raw answers: `baseline_general_model.json`.

## The question

A hospital without Antidote would ask a capable general model directly. We gave NVIDIA Nemotron 3 Super, the same model Antidote uses to compose cards, every one of the 55 published cases with no retrieval, no registry, no rules and no audit. To make the comparison as favourable to it as possible, it was handed the chemical name already typed in, the step that is missing in a real casualty ward.

## Results

| | General model (Nemotron 3 Super alone) | Antidote |
|---|---|---|
| Reads the chemical from the bottle | No: it was given the name | Yes: two independent vision reads plus a brand check |
| Drug doses written with no source | 107 doses, in 47 of 55 answers | 0: every clinical sentence is a guideline quote with its page |
| Holds antidote guidance until the product is confirmed | Never | Yes, whenever the match is below 75 percent confidence |
| Consistent with the treating doctors' management (judge 1 / judge 2) | 78.2 / 94.3 percent | 83.6 / 98.1 percent |

## What this shows

A general model knows the textbook. What it cannot do is read the bottle, tie every sentence to the national guideline page that says it, or decline to name an antidote when the product is uncertain. Those are the three things Antidote adds, and they are the three things a doctor needs at the bedside: the chemical, the source, and a stop when the answer is not safe to give.

Across both judges, Antidote's cards were also more often consistent with what the treating doctors actually did.

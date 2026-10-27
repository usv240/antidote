# Antidote

[![ci](https://github.com/usv240/antidote/actions/workflows/ci.yml/badge.svg)](https://github.com/usv240/antidote/actions/workflows/ci.yml) [![licence](https://img.shields.io/badge/licence-Apache--2.0-blue)](LICENSE)

**Reads a pesticide label, names the chemical and its WHO hazard class, retrieves the cited antidote guidance or stops when there is none, and fills the medico-legal register.**

Built for the Nebius x NVIDIA Global AI Hackathon on **Nebius Token Factory** with **NVIDIA Nemotron 3 Nano, Super and Ultra**. Apache-2.0.

> In 94 percent of recorded acute pesticide poisonings in India the chemical was never identified. It was printed on the bottle in the family's hand. Paraquat kills 50 to 90 percent of patients in Indian hospitals, and the first error is treating it like an organophosphate.

Decision support for trained clinicians. Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117.

## Live

Web: https://antidote-bay.vercel.app. API: https://antidote-api.vercel.app (OpenAPI docs at `/docs`). Both run on Vercel's free plan; the API is a Python function with a 300 second budget, enough for the Nemotron 3 Ultra audit.

## Status

Complete end to end: pipeline, API, MCP server, web app, published evaluation.

| Area | State |
|---|---|
| Design rule | Models read; tables and rules decide. Every clinical sentence on a card is a verbatim quote from a cited guideline page, checked by a deterministic verifier and audited by Nemotron 3 Ultra. The model never writes a dose. |
| Registry | 35 active ingredients across 12 chemical groups with India status; WHO 2019 classification parsed into 649 rows with source lines (96.9 percent agreement with the hand-seeded classes); CIB&RC Major Uses tables for insecticides and herbicides. |
| Corpus | NHSRC poison-management module, ISCCM 2024 position statement, NHSRC medico-legal guideline, Insecticides Rules 1971, WHO 2019 text, CIB&RC tables: 349 pages. WHO and CIB&RC documents block automated download; they were fetched server-side with Tavily extract. |
| Safety rules | 9 deterministic rules: atropine or oximes for any non-cholinergic group, paraquat oxygen caution, induced vomiting, model-written doses, identify-before-antidote. |
| Pipeline | Read label (Token Factory image model or NVIDIA Nemotron Nano VL on a local GPU), Nemotron 3 Nano normalisation, deterministic registry match with Tavily brand fallback, table-driven stop cards, Nemotron 3 Super quote-only composition, verifier, rules gate, Nemotron 3 Ultra audit with both guideline documents in context, register row. |
| Web | Landing that teaches the domain, Try flow with six samples, register, evals, how it works, limits, references, about, data, API. Light and dark, phone and desktop, info buttons from one glossary. |
| Eval | Lethal-error sentences blocked 10 of 10 by rules alone. No-antidote labels: stop card 20 of 20 and zero atropine or oxime mentions in the card 20 of 20. Non-pesticides routed away from antidotes 10 of 10. Organophosphates never falsely stopped 10 of 10. Citation integrity 92.0 percent raw, 100 percent after demotion. **Published case reports, two pre-registered sets:** 55 open-access poisoning case reports, verified quote by quote. Set 1 (33 cases): 0 unsafe cards. Held-out set 2 (22 cases, collected after development and never used for tuning): 1 unsafe card. That card showed the correct no-antidote stop and no antidote advice, but it printed the auditor's rejection note, which named oximes. We fixed it, added a regression test, and did not revise the count. Across both sets, Antidote got 9 of 12 documented misidentifications right and safely withheld guidance on 2 more; two judges found 83.6 percent of cards consistent with the authors' management. A class-level rule added after set 1 guided both class-only organophosphate cases in set 2 correctly. See `eval/results/`. |

## Where the models run

| Stage | Model | Platform |
|---|---|---|
| Label normalisation | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Nebius Token Factory (EU) |
| Card composition from quotes | `nvidia/nemotron-3-super-120b-a12b` | Nebius Token Factory (US) |
| Audit against the full national module and ISCCM statement | `nvidia/Nemotron-3-Ultra-550b-a55b`, 1M context | Nebius Token Factory (US) |
| Label photo reading | Token Factory image model (MiniCPM-V first) or `NVIDIA-Nemotron-Nano-12B-v2-VL` via llama.cpp on the laptop GPU | Token Factory or local |
| Brand resolution and document fetching | Tavily search and extract | Tavily API |

Every call is written to a ledger (tier, model, tokens, USD, latency) and shown in the app's Trace panel.

## Screenshots

`docs/screenshots/landing-dark.jpg`, `docs/screenshots/landing-light.jpg`, and the paraquat stop cards in `docs/screenshots/try-paraquat-dark.jpg`.

## Quick start

```
git clone https://github.com/usv240/antidote && cd antidote
cp .env.example .env            # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup
make test                       # 10 tests
make eval                       # writes eval/results/latest.json and REPORT.md
make dev                        # API on :8010, OpenAPI at /docs
cd apps/web && npm install && npm run dev   # web on :3010
```

The guideline PDFs the public can fetch are pulled by `scripts/fetch_corpus.sh`; the WHO and CIB&RC texts arrive via Tavily extract. `make ingest` rebuilds the index.

## Prior art, named

webPOISONCONTROL triages consumers in the United States from barcodes. SprayWise, a student hackathon project, reads labels for farmers' harvest intervals. Poison-information centres and textbooks hold the knowledge. Nothing reads the bottle for the doctor at the bedside, matches it to the Indian registry and the WHO class, assembles guidance from quoted sentences only, stops on the lethal errors, and fills the medico-legal register.

## Who has tested this

No practising doctor has used Antidote yet. What stands in is the work of the clinicians who already wrote up real cases: 55 published case reports in two pre-registered sets, each run through Antidote and compared with the authors' own management by two independent judges, under a scoring rule committed before any card was generated. Behind that sit the hospital series on outcomes when the chemical is unknown, and the national module and ISCCM statement as the only sources of clinical text.

## Documents

`docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`, `FEEDBACK.md`, `DEPLOY.md`. Shared platform with Sieve, our other entry: different domain, practitioner, corpus and record.

## Licence and data

Apache-2.0. Government of India documents are reproduced with acknowledgement; WHO text is quoted with attribution; the ISCCM statement is open access. Patient identifiers never enter the system; the register stores substance fields only.

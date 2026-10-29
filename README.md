# Antidote

[![ci](https://github.com/usv240/antidote/actions/workflows/ci.yml/badge.svg)](https://github.com/usv240/antidote/actions/workflows/ci.yml) [![licence](https://img.shields.io/badge/licence-Apache--2.0-blue)](LICENSE)

**Reads a pesticide label, names the chemical and its WHO hazard class, retrieves the cited antidote guidance or stops when there is none, and fills the medico-legal register.**

Built for the Nebius x NVIDIA Global AI Hackathon on **Nebius Token Factory** with **NVIDIA Nemotron 3 Nano, Super, Ultra, 3.5 Lightning and 3.5 Super VL**. Apache-2.0.

> In 94 percent of recorded acute pesticide poisonings in India the chemical went unidentified (PAN India analysis of government data, 2026). It was printed on the bottle in the family's hand. Paraquat kills 50 to 90 percent of patients in Indian hospitals, and the first error is treating it like an organophosphate.

Decision support for trained clinicians. Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117.

## Judge it in two minutes

No sign-up and no key. Each row is one click.

| Criterion | Click | What you will see |
|---|---|---|
| Technological implementation | [Run the Gramoxone (paraquat) label live](https://antidote-bay.vercel.app/try?sample=paraquat) | In under a minute: the registry names the chemical and its WHO class, fixed rules raise the stop cards, Nemotron 3 Super assembles a card made only of guideline sentences quoted with their pages, Nemotron 3 Ultra audits it against both national guidelines in full, and the Trace panel lists every model call with tokens, cost and seconds. |
| Design | [The landing page](https://antidote-bay.vercel.app) | Pick the bottle that came in with the patient; the toxicity triangle, WHO class, stop cards and the quoted guideline line change with it. Then the full flow from label to bedside card to register row, in light and dark, on a phone or a desktop. |
| Potential impact | [Validated against real-world evidence](#validated-against-real-world-evidence) | Published case series: Indian paraquat patients were first treated as organophosphate poisoning, and the diagnosis was finally made from photos of the bottle; in Bangladesh, 31.8 percent of patients were misdiagnosed from symptoms alone. Antidote reads that bottle. |
| Quality of the idea | [The evals](https://antidote-bay.vercel.app/evals), then [the register](https://antidote-bay.vercel.app/register) | 0 unsafe cards on 55 published case reports and 68 real label photos; 10 of 12 documented misidentifications set right. The register turns the same records into a district early-warning signal for spraying clusters and banned chemicals. |
| Your own data | [Your workspace](https://antidote-bay.vercel.app/data) | Add your hospital's own protocol and stock list; cards cite your protocol and show what is in stock. To call Antidote from your own system, create an API key on [the API page](https://antidote-bay.vercel.app/api). |

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
| Pipeline | Read label (NVIDIA Nemotron 3.5 Super VL, cross-checked by a second model; the chemical is used only when both agree), Nemotron 3 Nano normalisation, deterministic registry match with Tavily brand fallback, table-driven stop cards, Nemotron 3 Super quote-only composition, verifier, rules gate, Nemotron 3 Ultra audit with both guideline documents in context, register row. |
| Web | Landing that teaches the domain, Try flow with six samples, register, evals, how it works, scope and safeguards, references, about, data, API. Light and dark, phone and desktop, info buttons from one glossary. |
| Eval | Lethal-error sentences blocked 10 of 10 by rules alone. No-antidote labels: stop card 20 of 20 and zero atropine or oxime mentions in the card 20 of 20. Non-pesticides routed away from antidotes 10 of 10. Organophosphates never falsely stopped 10 of 10. Citation integrity 100 percent: a quote not found word for word on its page is replaced by the page itself. **Published case reports, two pre-registered sets:** 55 open-access poisoning case reports, verified quote by quote. On the live code: 0 unsafe cards, 44 specific and correct, 10 of 12 documented misidentifications set right, every other case held safely for confirmation; two judges found 83.6 and 98.1 percent of cards consistent with the authors' management. With cholinergic signs recorded, the class-level rule guided both class-only organophosphate cases correctly. **Real label photos:** 68 photos of Indian pesticide bottles from product pages, annotated by eye before any run. 0 unsafe cards, 49 read correctly (83.3 percent when the chemical is legible), the rest held for the doctor to confirm from the bottle. The safeguards: two independent reads that must agree, a grounding gate so only chemicals actually read reach the registry, a Tavily check of the brand's registered composition, and a rule that the organophosphate leads any mixture. See `eval/results/`. |

## Surveillance: the register as an early-warning signal

In Yavatmal in 2017 about 800 farm workers were poisoned while spraying cotton, and more than 20 died, before the cluster was recognised. Every patient was in a hospital register. Antidote reads its register for that signal (Register page, `GET /v1/surveillance/alerts`, `POST /v1/surveillance/brief`):

- **Fixed rules decide.** Three or more cases of one chemical group within seven days is a cluster, a spraying cluster when they came from skin or inhaled exposure. Banned chemicals still reaching patients and restricted-use chemicals are flagged. The same register always gives the same alerts, and tests enforce them.
- **Nemotron 3.5 Lightning explains.** It reads the whole register, the alerts, the regulatory status of every chemical and the full text of every published case report about those chemicals, about 200,000 tokens in one call for about one cent, and writes a district brief. It cannot add or remove an alert, and the bedside safety rules remove any item that breaks them.
- **OpenShell contains it.** On our laptop the brief also runs in a sandbox that can reach only Token Factory (`infra/openshell/DEMONSTRATED.md`).
- **A general model knows the textbook; Antidote reads the bottle.** Pre-registered against Nemotron 3 Super asked directly, on the same 55 published cases with the chemical name typed in for it: the general model wrote 107 drug doses with no source in 47 of 55 answers and never held back when the product was unknown. Antidote's cards contain only quoted guideline sentences with their pages, and in real hospitals the chemical name is the part that is missing (`eval/results/BASELINE-GENERAL-MODEL.md`).
- **Hermes keeps watch.** `scripts/outbreak_watch.py` (daily, silent unless something new) and `scripts/ban_watch.py` (weekly, Tavily search for new ban notices, changes nothing) are written as Hermes cron jobs. The demo register rows are synthetic and marked.

## Where the models run

| Stage | Model | Platform |
|---|---|---|
| Label normalisation | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Nebius Token Factory (EU) |
| Card composition from quotes | `nvidia/nemotron-3-super-120b-a12b` | Nebius Token Factory (US) |
| Audit against the full national module and ISCCM statement | `nvidia/Nemotron-3-Ultra-550b-a55b`, 1M context | Nebius Token Factory (US) |
| Label photo reading | `nvidia/Nemotron-3.5-Super-VL`, cross-checked by `openbmb/MiniCPM-V-4_5`; offline `NVIDIA-Nemotron-Nano-12B-v2-VL` via llama.cpp | Nebius Token Factory; laptop GPU offline |
| Brand resolution and document fetching | Tavily search and extract | Tavily API |

Every call is written to a ledger (tier, model, tokens, USD, latency) and shown in the app's Trace panel.

## Nebius Serverless, run and stopped

- **Job: verify both entries from a clean machine.** A Serverless Job cloned both public repositories, ran every test and the published safety checks, and called both live APIs. Result PASS in about 3 minutes (`sieve/infra/job-verify/RUN.md`).
- **Endpoint: an open NVIDIA vision model on our own GPU.** A Serverless Endpoint served NVIDIA Nemotron Nano 12B v2 VL with vLLM on one L40S, and both photo benchmarks were rerun with it as the only reader. It read 92.9 percent of legible Indian pesticide labels correctly on its own, and showed why Antidote pairs two independent reads with a brand check: together they give 0 unsafe cards in 68 (`sieve/infra/endpoint-vl/RUN.md`). Stopped after the run; about $1 in total.

## Where Token Factory accelerated our workflow

- **Four NVIDIA models behind one key and one API shape.** Nemotron 3 Nano normalises labels, 3 Super assembles cards, 3 Ultra audits them and 3.5 Super VL reads photos, all through the same OpenAI-compatible call. Moving a stage between tiers is a one-line change.
- **An auditor that reads both national guidelines at once.** Nemotron 3 Ultra checks every card against the complete NHSRC module and ISCCM 2024 statement in one long-context call. Hosting a 550B model ourselves was out of reach.
- **Evaluation on every change.** The case-report benchmark, the label-photo benchmark and the negative controls each cost cents to a few dollars per run, so every safety change was checked against all of them, and every run is in the repository.
- **A vision model appeared mid-hackathon and we switched in a day.** Nemotron 3.5 Super VL arrived in the catalog; adopting it took a model id and one request flag, and it fixed label misreads the previous reader made.
- **One ledger.** Every call records tier, model, tokens, dollars and latency, shown to the doctor in the Trace panel. That transparency came almost free because every model sits behind one endpoint.

## Screenshots

`docs/screenshots/landing-dark.jpg`, `docs/screenshots/landing-light.jpg`, and the paraquat stop cards in `docs/screenshots/try-paraquat-dark.jpg`.

## Quick start

```
git clone https://github.com/usv240/antidote && cd antidote
cp .env.example .env            # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup
make test                       # 49 tests
make eval                       # writes eval/results/latest.json and REPORT.md
make dev                        # API on :8010, OpenAPI at /docs
cd apps/web && npm install && npm run dev   # web on :3010
```

The guideline PDFs the public can fetch are pulled by `scripts/fetch_corpus.sh`; the WHO and CIB&RC texts arrive via Tavily extract. `make ingest` rebuilds the index.

## Prior art, named

webPOISONCONTROL triages consumers in the United States from barcodes. SprayWise, a student hackathon project, reads labels for farmers' harvest intervals. Poison-information centres and textbooks hold the knowledge. Nothing reads the bottle for the doctor at the bedside, matches it to the Indian registry and the WHO class, assembles guidance from quoted sentences only, stops on the lethal errors, and fills the medico-legal register.

## Validated against real-world evidence

Antidote is checked against what treating doctors have already published: 55 open-access poisoning case reports in two pre-registered sets, each run through Antidote and compared with the authors' own management by two independent judges, plus 68 photos of real Indian pesticide labels. Its clinical text comes only from the NHSRC poison-management module and the ISCCM 2024 position statement, quoted word for word with the page.

### What the published evidence says

- **Doctors treat the wrong poison when nobody can name it, and the bottle settles it.** In an Indian paraquat series, many patients could not name the agent, so initial treatment was directed at organophosphorus poisoning: before referral they received atropine, pralidoxime and oxygen, and "oxygen therapy is known to cause free radical injury and increased mortality in these patients". The diagnosis was made from the container, or from pictures of it shared on WhatsApp by relatives (Dambal et al., National Medical Journal of India 2021, https://nmji.in/reasons-for-under-reporting-of-paraquat-poisoning-in-india/). That photo is exactly what Antidote reads.
- **The toxidrome alone misleads.** In a Bangladesh hospital series, 63 of 198 patients (31.8 percent) were misdiagnosed from the clinical toxidrome; "identification of the specific compound is essential for anticipating and reducing complications, administering appropriate and timely management" (Verma, Lamb, Sattar, Ghose, Eddleston, Trans R Soc Trop Med Hyg 2024, https://pmc.ncbi.nlm.nih.gov/articles/PMC11149373/).
- **The product decides the outcome.** Case fatality ranges from around 70 percent for paraquat and aluminium phosphide to close to 0 percent for many newer pesticides; WHO tells families to "take along the bottle" (WHO, Clinical management of acute pesticide intoxication, 2008, https://iris.who.int/handle/10665/44020).
- **The specific chemical is rarely recorded.** A systematic review of lethal poisoning in India found pesticides behind 94.5 percent of the poisoning deaths studied, yet "few papers identified the specific organophosphorus insecticide responsible" (Karunarathne et al., BMC Public Health 2021, https://link.springer.com/article/10.1186/s12889-021-11156-2).
- **Highly hazardous products are still on the shelf.** Of 318 pesticides registered in India in 2019, 18 were WHO class Ia or Ib (Bonvoisin et al., BMC Public Health 2020, https://link.springer.com/article/10.1186/s12889-020-8339-z). Antidote shows the WHO class and the Indian regulatory status on every card.
- **Expert guidance is scarce, and it works.** Most emergency physicians surveyed in south and east India reported having no poison centre, and most there were unaware of the national hotline (Blanchard et al., Toxicology Communications 2019, https://doi.org/10.1080/24734306.2019.1635725). Where poison-centre guidance is available, patients stay in hospital 3.43 days less on average (Galvão et al., Sao Paulo Medical Journal 2011, https://pmc.ncbi.nlm.nih.gov/articles/PMC10865900/). Antidote puts the national guideline's own sentences, and the poison-centre number, on every card.

## Documents

- [EVIDENCE.md](EVIDENCE.md): every published number, its raw output file, and the command that reruns it.

`docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`, `FEEDBACK.md`, `DEPLOY.md`. Shared platform with Sieve, our other entry: different domain, practitioner, corpus and record.

## Licence and data

Apache-2.0. Government of India documents are reproduced with acknowledgement; WHO text is quoted with attribution; the ISCCM statement is open access. Patient identifiers never enter the system; the register stores substance fields only.

# Antidote: Delivery Plan

Deadline: Oct 30 2026, 22:30 IST. Target submission: Oct 29. Time share: about 35 percent of total effort, scheduled in the gaps of Sieve's GPU jobs and hardware waits, and accelerated by reusing the shared platform once Sieve's core pipeline exists.

Related: `IDEA.md`, `TECHNICAL-DESIGN.md`, `UX-DESIGN.md`, `../PLATFORM.md`.

---

## 1. Definition of done

- A judge runs the chlorpyrifos, paraquat and fertiliser samples and sees a cited card, a stop card and a "not a pesticide" card, each with a live Token Factory call visible in the Trace.
- Benchmark A (label to registry), Benchmark B (hazard class vs baseline) and three negative controls are on /evals with reproduce command; baselines beaten; citation integrity 100 percent.
- Every clinical sentence is a verbatim quote with a page reference; the verifier proves it.
- The medico-legal register row and poison-centre proforma export as PDF.
- BYO stock list and protocol upload work.
- API keys, OpenAPI, snippets, MCP server work (shared code with Sieve).
- Offline mode runs; delta published.
- README, FEEDBACK.md, LICENSE, .env.example, both-theme screenshots complete.
- Video shows real bottles, the stop card, the register row, the Trace.

---

## 2. Work breakdown

### Phase 0: Setup (Oct 14 to 15, in parallel with Sieve Phase 0)
- Repo `antidote` on GitHub, Apache-2.0, CI.
- Buy three empty or cheapest-size bottles at an agri-input shop: chlorpyrifos, cypermethrin, paraquat or glyphosate (Rs 150 to 400). Photograph each in six conditions (daylight, indoor, angled, partially worn, bilingual side, close-up of the triangle) for the sample gallery and Benchmark A.
- Download CIB&RC registered list, banned list, WHO 2019 classification, NHSRC poison module, ISCCM 2024 statement, NHSRC medico-legal guideline, Insecticides Rules 1971. Record licence lines in `data/manifest.yaml`.
- Outreach for a practitioner quote: a casualty medical officer or emergency physician, a poison-centre pharmacist, a toxicology department. Template in `docs/outreach.md`.

### Phase 1: Tables and rules (Oct 18 to 19, after Sieve's platform packages exist)
- Extract `registered_products.csv`, `banned_restricted.csv`, `who_hazard_2019.csv` with PyMuPDF plus Nano cleanup; hand-verify 100 rows; add checksums and versions.
- Author `toxidromes.yaml` and `antidotes.yaml` as verbatim quotes with page citations from the NHSRC module and ISCCM statement; cover the twelve chemical groups.
- Author `rules/antidote.yaml` with unit tests: no-antidote stops, atropine guard, paraquat oxygen caution, confidence guard, always-NPIC, not-a-pesticide, banned flag.
- Ingest guideline pages into LanceDB locally.
- Deterministic matcher: registration number, active ingredient plus percent, brand aliases; Tavily fallback with unverified labelling.

### Phase 2: Pipeline end to end (Oct 20 to 21)
- Vision prompt for label fields using the shared endpoint; fallback chain.
- Nano normalisation; Super composition with the `ManagementCard` schema (quotes vs explanation kinds); Ultra audit with the whole module in context; citation verifier.
- Record schemas: medico-legal register row and NPIC proforma; PDF export.
- Eval harness: Benchmark A on the 60 photos; Benchmark B over WHO active ingredients present in the registry; negative control sets authored and published; baselines run; first REPORT.md.

### Phase 3: Product surface (Oct 22 to 24)
- Web app from the shared kit: landing sections 2.1 to 2.13, /try four screens, /register, /evals, /how-it-works, /data with BYO (stock list, protocol, aliases), /api, /limits, /references, /about.
- Persistent clinical banner; quote styling; info buttons wired to glossary.yaml (terms: organophosphate, carbamate, pyrethroid, paraquat, toxidrome, WHO class, registration number, toxicity triangle, medico-legal case, NPIC, atropine, pralidoxime, decontamination).
- Sample gallery with six photos; offline mode; status strip.

### Phase 4: Proof and polish (Oct 25 to 26)
- Final eval run; commit results; numbers into README and hero tiles.
- Accessibility, performance and both-theme screenshot passes.
- README with architecture, "Where the models run", cost actuals, prior art (webPOISONCONTROL, SprayWise), scope statement.
- Practitioner quote inserted if obtained.

### Phase 5: Video and submission (Oct 27 to 28)
- Shoot video per storyboard. Devpost draft with track Best Apps and Agents, Built With, feedback section. Fresh-clone test.

### Phase 6: Buffer and submit (Oct 29)

---

## 3. Video storyboard (2:45)

| Time | Visual | Voice-over |
|---|---|---|
| 0:00 | Text on black: "94 percent of recorded pesticide poisonings in India: chemical unknown." | "Every year, more than a hundred thousand people die of pesticide poisoning. In India, the chemical is usually never identified. It was printed on the bottle the family carried in." |
| 0:15 | Hands place a chlorpyrifos bottle on a table; phone photographs the label | "Antidote reads the label with an NVIDIA Nemotron vision model on a Nebius Serverless Endpoint." |
| 0:28 | Extracted fields, registry match with confidence | "It matches the registration number against the government's registry of every registered pesticide, using Nemotron 3 Nano on Nebius Token Factory." |
| 0:42 | Card: organophosphate, WHO class II, quoted toxidrome and management, page image opens | "The card is built from quotes. Nemotron 3 Super composes it only from the national poison-management module, and every sentence shows its page." |
| 1:05 | Paraquat bottle photographed; stop card appears | "Now paraquat. Paraquat kills half to nine in ten patients, and the first mistake is treating it like an organophosphate. Antidote stops: no antidote, do not give atropine, caution with oxygen. That is a rule, not a model's opinion. We measured it: one hundred percent of our no-antidote cases got the stop card." |
| 1:35 | Fertiliser bag; "not a pesticide" card | "A fertiliser bag is not a pesticide. Antidote says so and shows the general approach instead." |
| 1:45 | Trace panel | "Nemotron 3 Ultra audits every card with the whole guideline in its one-million-token context. The session cost a few cents." |
| 2:00 | Register row saved; proforma; NPIC dial | "The medico-legal register row is filled, and the poison-centre proforma is ready, so the call takes thirty seconds." |
| 2:15 | /evals page | "Tested against the government registry and the WHO classification, with baselines and negative controls published." |
| 2:30 | Offline banner on a laptop | "Works offline on an open Nemotron model. Open models, open data, at the bedside." |
| 2:40 | Logo, URL, "Built on Nebius Token Factory with NVIDIA Nemotron 3" | "Antidote." |

---

## 4. Devpost submission outline

Title: Antidote. Tagline: "Reads a pesticide label, names the chemical and its hazard class, retrieves the cited antidote guidance or stops when there is none, and fills the medico-legal register." Sections as in Sieve's plan, with the scope statement prominent.

---

## 5. Risk register (delivery)

| Risk | Likelihood | Plan |
|---|---|---|
| Government PDFs resist table extraction | Medium | Manual extraction for the twelve chemical groups' active ingredients first; full registry as a stretch; version and checksum tables |
| Shops will not sell paraquat in small quantities | Medium | Use glyphosate (also no specific antidote) and public product images for the paraquat sample, labelled |
| Reviewer sees clinical liability | Medium | Scope statement, quotes only, stop cards, persistent banner, staff-entered patient data, measured negative controls |
| Time pressure from Sieve | High | Antidote reuses the platform; if needed, ship without BYO stock list and offline mode, and state that honestly on /limits |

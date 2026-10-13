# Antidote: UX and Landing Page Design

Goal: a judge, a first-year doctor, or someone who has never heard of an organophosphate opens the site and, within two minutes, understands the problem, sees a label photo turn into a cited management card, watches the system refuse to give atropine for paraquat, and understands why that refusal is the whole point.

Shared UI kit, tokens, Info component, Explain mode and theme behaviour are in `../PLATFORM.md` section 10. Design principles are the same seven as Sieve (`../sieve/UX-DESIGN.md` section 1) with one addition:

8. **Clinical copy is quoted, never paraphrased.** Every clinical sentence on screen is visibly a quotation with a page reference. The visual style of a quote (left rule, source line) is the same everywhere, so a reader learns in one glance which words came from a guideline and which are connective text.

---

## 1. Information architecture

```
/                 Landing: teaches and invites a first run
/try              The app: Read label -> Confirm -> Card -> Record (also /try?sample=paraquat)
/register         Medico-legal register view for the demo workspace
/evals            Live evaluation results, baselines, negative controls, reproduce command
/how-it-works     Pipeline diagram, trace example, "tables decide, models read" explanation
/data             Registries, guidelines, licences, BYO upload (stock list, protocol, aliases)
/api              API keys, OpenAPI, snippets, MCP server
/limits           Measured limits, scope statement, what Antidote refuses
/references       Every statistic with its primary source
/about            Prior art, Nebius and NVIDIA tools used, feedback
```

Header: logo, Try it, How it works, Evals, API, Explain mode, theme. A persistent thin banner on all app screens: "Decision support for trained clinicians. Airway, breathing, circulation first. NPIC 1800-116-117."

---

## 2. Landing page, section by section

### 2.1 Hero
- Headline: **"The chemical was never identified in 94 percent of cases. It was printed on the bottle in the family's hand."**
- Subhead: "Antidote reads a pesticide label and gives the doctor the chemical, its hazard class, what the poisoning will look like, and the cited antidote guidance, or a clear stop when there is none."
- Two stat tiles with info buttons to sources: "110,000 to 168,000 pesticide self-poisoning deaths a year worldwide" and "Paraquat kills 50 to 90 percent of patients in Indian hospitals; the first error is treating it like something else."
- Buttons: "Try it on a sample bottle" (opens /try with the chlorpyrifos sample) and "Watch the 3-minute video".
- Status strip: Live, vision endpoint, Token Factory, last eval.

### 2.2 What is this, in one minute
Three cards: **What** (a bedside reader for pesticide labels), **Why** (the label legally carries the answer; the registry and guidelines are public; none of it is at the bedside at 11 pm), **How** (photo, confirm, cited card, stop cards, register row). Info buttons: "What is an organophosphate?", "What is the toxicity triangle?", "What is a medico-legal case?".

### 2.3 See it work (interactive, no hardware)
Sample gallery of six label photos: chlorpyrifos (organophosphate, class II), carbofuran (carbamate, class Ib), cypermethrin (pyrethroid, no antidote), paraquat (stop card), aluminium phosphide (stop card), and a urea fertiliser bag (not a pesticide). Clicking runs the live flow in a framed panel with the Live or Replay label. Info button: "Why samples? So anyone can see the whole flow without a bottle."

### 2.4 Who it is for
Three personas: the medical officer at a primary or community health centre (gets the chemical and the cited guidance in seconds), the casualty nurse (knows which questions to ask the family and what to prepare), the poison-centre pharmacist on the phone (receives a complete proforma instead of "a white bottle with a red triangle"). Info buttons on each role.

### 2.5 The numbers
Table of six statistics with plain sentence, link, year: deaths worldwide; 94 percent unidentified (labelled as an NGO analysis of government data); survival improved when the chemical was known; paraquat fatality rates; poisoning share of suicides in India; the label rule from 1971. Info button: "Why do we label one number as an NGO analysis?" (honesty about evidence grades).

### 2.6 How the AI works
Plain: five boxes. Read (the label), Match (the government registry), Look up (WHO class and the national guideline), Check (a rules engine stops dangerous outputs; a larger model audits every sentence against the full guideline), Record (the register row). The sentence under the diagram: "Models read. Tables and rules decide."
Technical: Nemotron Nano VL on a Nebius Serverless Endpoint for label fields; Nemotron 3 Nano for normalisation; deterministic registry matching with Tavily fallback; WHO and CIB&RC tables; Nemotron 3 Super for composing the card from quotes; a YAML rules engine; Nemotron 3 Ultra with the whole national module in a 1M context as auditor; an exact-span citation verifier. Link to a real Trace.

### 2.7 What Antidote refuses
Three stop cards rendered as in the app: paraquat (no antidote, no atropine, oxygen caution), aluminium phosphide (no antidote), low-confidence match (antidote row suppressed). Text: "These are rules that fire before the model is allowed to speak. We measured them." Link to /evals negative controls.

### 2.8 Evaluation results
Stat tiles from `eval/results/latest.json`: label-to-registry match accuracy, hazard-class accuracy vs the no-tables baseline, negative controls (stop-card correctness, non-pesticide routing, false stops), citation integrity. Button: See full results and reproduce.

### 2.9 Bring your own data
"Upload your antidote stock list and your state protocol. Antidote will show what is in stock here and cite your protocol beside the national one. Your data stays in your workspace." Info button: "What happens to my file?"

### 2.10 Use Antidote as a service
curl, Python, JavaScript tabs for `/v1/identify` and `/v1/analyze`; MCP server note; Get an API key. Info buttons for API key and MCP.

### 2.11 Built with
Nebius Token Factory, Nemotron 3 Nano, Super, Ultra, Nemotron Nano VL, Nebius Serverless, Tavily, CIB&RC, WHO, NHSRC. Link to FEEDBACK.md.

### 2.12 Limits, honestly
Measured: OCR accuracy on worn labels; registry snapshot date and coverage; offline delta; chemical groups covered. The scope statement in full.

### 2.13 References and FAQ
FAQ includes: "Is this medical advice?" (No. It identifies the product and retrieves cited guidance for trained clinicians, and it stops where the guidance says there is no antidote.) "Why not just call the poison centre?" (Do call. Antidote fills the proforma so the call is faster and the chemical is named.) "What about labels in Hindi or Telugu?" (The registration number and percentage are printed in Latin script on every label; the original text is shown beside the canonical name.) "Why open models?" (Hospitals need offline, auditable, sovereign tools.)

---

## 3. The app (/try) screen by screen

**Screen 1: Read the label.** Camera, upload, or sample. The extracted fields appear as editable chips: product, active ingredient and percent, registration number, triangle colour, antidote statement text as printed. The original script is shown under each chip when present. Info buttons: "What is a registration number?", "Why do you show the printed antidote statement?" (because the label itself is evidence).

**Screen 2: Confirm.** The matched registry row with confidence. Below threshold: up to three candidates, or type the active ingredient. A banned or restricted flag appears here if relevant. Optional patient context toggles: route (ingested, inhaled, skin), time since exposure band, adult or child, key signs picked from pictures and words (pinpoint pupils, excess secretions, seizures, vomiting, breathing difficulty). Every toggle has an info button explaining why it matters.

**Screen 3: Card.** Order is fixed: the persistent banner; any stop card first, full width; then Identity (chemical, group, WHO class with info button on what the class means); Expect (toxidrome quotes); Manage (cited guidance quotes, with "Show page" for each); Cautions; Call NPIC with a one-tap dial on mobile and the proforma ready. Right rail or bottom sheet: Trace, Sources, Stock (if BYO stock uploaded).

**Screen 4: Record.** The medico-legal register row with staff-entered fields clearly marked; the poison-information proforma; Save, Export PDF, Print. Confirmation shows the register updating.

---

## 4. Visual system

- Accent: a deep green that reads as agriculture and safety; stop red with octagon icon and the word Stop; caution amber with triangle and the word Caution. Severity never by colour alone.
- Quote style: left rule in the accent colour, source line in small caps "NHSRC module, page 14", page image on demand.
- Type and spacing as in the shared kit; large chips for extracted fields so they can be corrected with a thumb.
- Imagery: our own label photographs, with brand names visible only where the licence and fairness allow; the toxicity triangle as a recurring explanatory graphic with an info button.

---

## 5. Light and dark, phone and desktop

Same behaviour as Sieve: system default, persisted toggle, no flash, both palettes complete; breakpoints 320 to 1280; mobile bottom tabs (Read, Card, Record, Register); desktop left rail and right details rail; installable PWA with offline shell and an offline banner listing what still works (tables, rules, manual entry).

---

## 6. Content rules

Same as Sieve, plus: clinical sentences are always quotations with a page; connective sentences never contain a drug name or a number; the persistent banner is never hidden; the NPIC number is on every card and every exported document.

---

## 7. Judge path, timed

0:00 land, read headline and two numbers. 0:15 click "Try it on a sample bottle". 0:25 see extracted fields and the registry match with confidence. 0:40 see the card: organophosphate, class II, quoted toxidrome and management, page image opens. 1:05 switch to the paraquat sample. 1:15 stop card: no antidote, no atropine, oxygen caution, cited. 1:30 switch to the fertiliser bag: not a pesticide. 1:40 open the Trace: Nano, Super, Ultra, cost. 1:55 save the register row and open /register. 2:15 open /evals: match accuracy, class accuracy vs baseline, negative controls at 100 and 0. Under three minutes, everything verified.

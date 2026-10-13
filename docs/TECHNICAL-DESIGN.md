# Antidote: Technical Design

Shared platform decisions (client, router, vision, retrieval, rules engine, eval harness, API, UI kit) are in `../PLATFORM.md`. This document covers what is specific to Antidote.

---

## 1. What Antidote does, as a system

Input: a phone photo of a pesticide container label, plus optional patient context (route of exposure, time since exposure, weight band, key signs). Output: the identified product and active ingredient with confidence, WHO hazard class, expected toxidrome, the management card grounded in the national poison-management module with page citations, hard stop cards where no antidote exists or where a common error is lethal, the poison-centre number, and a pre-filled medico-legal case register row and poison-information proforma.

Design rule that governs everything: **the model reads the label; tables and rules make the clinical statements.** The language model never invents a dose. Every clinical sentence on a card is either a verbatim quote from a cited guideline page or a row from a curated, cited table.

---

## 2. Architecture

```
 Phone / desktop (PWA)
   |  label photo + context taps                       Trace panel <-- cost ledger
   v
 apps/api (FastAPI)
   |-- 1 Read label -----> vision endpoint (Nemotron Nano VL) -> fallback Token Factory image2text -> manual fields
   |-- 2 Normalise ------> Nemotron 3 Nano: canonical active ingredient names, percentages, formulation, reg no, triangle colour
   |-- 3 Match ----------> deterministic: CIR registration number exact -> active ingredient fuzzy -> Tavily brand lookup
   |-- 4 Classify -------> tables: WHO 2019 hazard class; chemical group; toxidrome; antidote row
   |-- 5 Compose --------> Nemotron 3 Super: management card from retrieved guideline pages (quotes only)
   |-- 6 Gate -----------> rules engine: no-antidote stops, atropine guard, oxygen guard, confidence guard, always-NPIC
   |-- 7 Audit ----------> Nemotron 3 Ultra: full module + ISCCM statement in context; approve/repair/reject per sentence
   |                       citation verifier: exact-span match
   |-- 8 Record ---------> MLC register row + NPIC proforma JSON -> PDF/print/export
   v
 Ingestion (local or Nebius Serverless Job): registries -> tables; guidelines -> pages -> LanceDB
 BYO: hospital antidote stock list, state protocol, local formulary, regional-language brand aliases
```

---

## 3. Data layer

### 3.1 Registries and tables (`packages/core/data/`)

| Table | Source | Fields | Build |
|---|---|---|---|
| `registered_products.csv` | CIB&RC registered pesticides list (31.03.2024) | registration number, product name, active ingredient(s), percentage, formulation code, registrant | PDF table extraction with PyMuPDF plus Nano cleanup; spot-checked by hand on 100 rows |
| `banned_restricted.csv` | CIB&RC banned, refused, restricted list | active ingredient, status, order date | Same |
| `who_hazard_2019.csv` | WHO Recommended Classification of Pesticides by Hazard, 2019 | active ingredient, class (Ia, Ib, II, III, U, FM, O), chemical group, oral and dermal LD50 basis | Same, with page citation per row |
| `label_bands.yaml` | Insecticides Rules 1971, Rule 19 | colour band to toxicity category and signal word mapping | Hand-coded with citation |
| `toxidromes.yaml` | NHSRC poison-management module; ISCCM 2024; WHO | chemical group to expected signs, time course, key investigations | Each entry is a list of verbatim quotes with page citations |
| `antidotes.yaml` | NHSRC module; ISCCM 2024 | chemical group to antidote row: agent, exists (bool), indication, cautions, contraindications, monitoring, source quotes | Verbatim quotes only; numeric doses are shown as quoted text from the source page with the page image available, never computed |
| `brand_aliases.yaml` | Built incrementally from CIB&RC, product photos, and Tavily lookups | brand to registration number or active ingredient | Grows during testing; BYO can extend per workspace |

Chemical groups covered in the first release, chosen by Indian poisoning epidemiology: organophosphates, carbamates, pyrethroids, paraquat, glyphosate, aluminium phosphide, zinc phosphide, anticoagulant rodenticides, neonicotinoids, organochlorines (banned but still encountered), 2,4-D and other phenoxy herbicides, and an explicit "not a pesticide" class for fertilisers and household chemicals.

### 3.2 Guideline pages
LanceDB `pages` table built from the NHSRC module, the ISCCM position statement, WHO 2019 introduction chapters, the NHSRC medico-legal guideline, and the Insecticides Rules. Each page: text, figure descriptions, embeddings, licence tag. Small corpus (a few hundred pages), so ingestion runs locally in minutes; the Serverless Job container is still provided for BYO uploads.

### 3.3 Label photo set (for development and eval)
- Our own photographs of bottles bought at agri-input shops, in varied lighting, angles and wear (target 60 photos across 20 products).
- Manufacturer product images where terms permit, used for development only.
- Ground truth for every photo comes from the registry row for the registration number printed on the label, so no clinical label was authored by us.

---

## 4. The flow in detail

### Step 1: Read label (vision)
Prompt asks for structured fields only: `product_name, active_ingredients[] (name, percent), formulation_code, registration_number, batch, manufacture_date, expiry_date, manufacturer, triangle_colour, signal_word, antidote_statement_text, visible_warnings[], languages_seen[]`. Nothing clinical is asked of the vision model.

### Step 2: Normalise (Nano, thinking off)
Maps OCR spellings to canonical active-ingredient names (ISO common names), parses percentages and formulation codes (EC, SC, WP, SL, GR), and returns a confidence per field. Regional-script text is transliterated where present; the UI shows the original text beside the canonical name.

### Step 3: Match (deterministic, then Tavily)
1. Registration number exact match in `registered_products.csv`.
2. Else active ingredient plus percentage plus formulation match.
3. Else brand alias table.
4. Else Tavily `search` restricted to manufacturer and regulator domains for `"<brand>" pesticide active ingredient`, with `extract` on the top result; the result is shown as "web-sourced, unverified" with the link, and the match confidence is capped so the card stays in guarded mode.
Below the confidence threshold, the app asks the user to confirm from up to three candidates, or to type the active ingredient from the label.

### Step 4: Classify (tables)
Join to WHO class, chemical group, toxidrome entry, antidote row, banned status. All table lookups; no model involved.

### Step 5: Compose (Super)
Super receives the matched rows and the top retrieved guideline pages and produces the card using the `ManagementCard` tool schema. Constraint: every clinical sentence must be a `quote` from a provided page with a `cite`. Super may write connective plain-language sentences marked `kind: explanation` that carry no clinical content (for example "This chemical belongs to the organophosphate group"). The schema separates the two so the UI can style and verify them differently.

### Step 6: Gate (rules engine, `rules/antidote.yaml`)
- `no-antidote-stop`: if the antidote row says `exists: false` (paraquat, aluminium phosphide, glyphosate, pyrethroids), render a full-width stop card first: "No specific antidote. Do not give atropine for this exposure." with the cited quote.
- `paraquat-oxygen`: for paraquat, add the cited caution on oxygen.
- `atropine-guard`: block any output that mentions atropine for a chemical group whose antidote row does not include it.
- `confidence-guard`: if match confidence is below threshold, the card shows class and toxidrome but suppresses the antidote row and shows "Identify the product before antidote decisions. Treat the patient, not the bottle."
- `always-npic`: every card includes the National Poisons Information Centre number and the sentence "Airway, breathing, circulation first."
- `decontamination-caution`: cited cautions on gastric lavage per the national module.
- `not-a-pesticide`: fertiliser, cleaning agents and unmatched items route to a generic poison-approach card and never to pesticide antidotes.
- `banned-flag`: if the active ingredient is banned or restricted, annotate the card and the MLC record (relevant for the medico-legal narrative).

### Step 7: Audit (Ultra) and citation verification
Ultra receives the whole NHSRC module and the ISCCM statement (both fit easily in 1M context), the card, and the instruction to check that every clinical quote is used for the chemical group it belongs to and that no sentence contradicts any page. Verifier confirms each quote exists verbatim on its cited page. Failures replace the sentence with "see page N" plus the page image.

### Step 8: Record
Two documents, both exportable as PDF and print-ready:
- **Medico-legal case register row** per the NHSRC medico-legal guideline fields: date and time, patient identifiers (entered by staff, never inferred), brought by, alleged history, substance identified (product, active ingredient, registration number, photo attached), examination findings (entered by staff), treatment given (entered by staff; the card's cited options are offered as checkboxes), referral, informant, doctor's name.
- **Poison information proforma** matching the fields the national poison centre asks for on the phone, so the call takes thirty seconds.
Records live in the workspace, exportable and deletable.

---

## 5. BYO (bring your own data)

- **Antidote stock list**: a hospital uploads its stock of atropine, pralidoxime, vitamin K and others; the card shows "in stock here" or "nearest stock: district hospital" (the second requires a district workspace).
- **State or hospital protocol**: upload a PDF; it is ingested into the workspace index and cited alongside the national module, labelled as local.
- **Brand aliases in regional languages**: a CSV of local brand names to registration numbers.
All BYO data is workspace-scoped, exportable, deletable, and never merged into the shared index.

---

## 6. Offline mode

Same approach as Sieve: llama.cpp with Nemotron 3 Nano GGUF for normalisation and composition, tables and rules local, vision replaced by manual field entry. The registries and guideline pages are small enough to ship in full in the offline bundle. Delta measured and published.

---

## 7. Evaluation (project-specific)

| Metric | Set | Source | Report |
|---|---|---|---|
| Benchmark A: label to registry | 60 self-shot label photos across 20 products, ground truth = CIB&RC registry row for the printed registration number | Registry is external; photos are ours | Field extraction accuracy (registration number, active ingredient, percent), match accuracy, confidence calibration |
| Benchmark B: classification | All active ingredients in the WHO 2019 table that appear in the CIB&RC registry (several hundred) | External | Hazard class and chemical group accuracy of the full pipeline from text input, vs nano-zero-shot without tables |
| Negative control 1 | 40 no-antidote and common-error cases: paraquat, aluminium phosphide, pyrethroid, glyphosate, rodenticide, mixed products | Authored, published | Percent with correct stop card and zero atropine mentions: target 100 |
| Negative control 2 | 20 non-pesticide items: fertiliser bags, detergents, kerosene, medicines | Authored, published | Percent routed to generic approach with no pesticide antidote: target 100 |
| Negative control 3 | 30 benign organophosphate and carbamate cases | Authored, published | False stop rate: target 0 |
| Citation integrity | All cards | Verifier | Percent of quotes found verbatim: target 100 |
| Offline delta | Benchmark B subset | Same | Accuracy offline vs cloud |
| Cost and latency | All | Ledger | USD per card, seconds per card |

Baselines: `nano-zero-shot` (photo text to card with no tables or rules) and `chunk-rag` (retrieval without the auditor and rules). Same inputs, same prompts where applicable.

---

## 8. Safety and scope statement (shown in the app and README)

Antidote is decision support for trained clinicians. It identifies the product and retrieves the relevant cited guidance. It does not diagnose, does not compute doses, does not replace a poison centre call, and it stops when the guidance says to. All clinical text is quoted from the national module, the ISCCM statement or WHO documents with page references. Patient identifiers are entered by staff and stored only in the hospital's workspace.

---

## 9. Costs and operations

Vision endpoint shared with Sieve (one L40S endpoint serves both projects during demo and judging windows). Token Factory usage per card: Nano about 2K tokens, Super about 6K, Ultra audit about 60K input with the module in context, roughly 8 to 10 cents per card at list prices; cached module context reduces this. Published as actuals.

---

## 10. Risks and mitigations (technical)

| Risk | Mitigation |
|---|---|
| OCR on faded, curved, bilingual labels | Match on registration number and percentage first; show candidates; manual field entry always available |
| Brand not in registry snapshot | Tavily lookup clearly labelled unverified; confidence guard suppresses antidote row |
| Any clinical hallucination | No clinical sentence without a verbatim cited quote; rules engine; Ultra audit; verifier |
| Table extraction errors from government PDFs | Hand-verified 100-row sample; checksum and version on every table; errors reportable from the UI |
| Liability optics | Scope statement everywhere; staff enters patient data; cards are cited retrieval, not advice |

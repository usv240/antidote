# ANTIDOTE: Project 2 (LOCKED 2026-10-13)

Pesticide-container photo to poisoning management card and medico-legal record, for the emergency doctor in a rural health centre.

Alternate name if Antidote is taken on Devpost: Triangle (after the toxicity triangle printed on every Indian pesticide label).

Hackathon: Nebius x NVIDIA Global AI Hackathon. Deadline Oct 30 2026, 22:30 IST. Track: Best Apps and Agents. Bonus: Best Use of Tavily.

Full candidate research and the eight other finalists: `../PROJECT2-RESEARCH.md`.

---

## One line
The family brought the bottle. Photograph it. Antidote reads the label, names the chemical and its WHO hazard class, tells the doctor what the poisoning will look like and what the antidote is, or says plainly "no antidote, do NOT give atropine", and fills the medico-legal case register.

## Tagline
"In 94 percent of recorded pesticide poisonings in India the chemical was never identified. The answer was printed on the bottle in the family's hand."

## Why it feels like Sieve
- Named practitioner in front of a physical thing with urgency: a medical officer at 11 pm, a convulsing farmer, a relative holding a half-empty bottle with a coloured triangle.
- The gap is knowledge, not money: every Indian pesticide label is legally required to print the active ingredient, a colour-coded toxicity triangle and an antidote statement. The government publishes the registry of every registered product. WHO publishes a hazard class for every active ingredient. None of it is in the doctor's hand at the bedside.
- Photo in, action out: label photo to a management card and a filled register row.
- Negative control as the headline: "It refused to give atropine for paraquat." Paraquat kills 50 to 90 percent of patients in Indian hospitals and the first error is treating it as an organophosphate.
- Demo for Rs 150 to 400: three empty bottles from any agri-input shop.
- Zero incumbents in India; nothing clinician-facing anywhere.
- Lands in a real record: every poisoning in India is a mandatory medico-legal case with a register.

## Primary evidence
| Fact | Source |
|---|---|
| 110,000 to 168,000 pesticide self-poisoning deaths per year worldwide, 14 to 20 percent of all suicides | Mew et al., J Affect Disord 2017, https://files.givewell.org/files/DWDA%202009/Centre_for_Pesticide_Suicide_Prevention/Mew_et_al_2017.pdf |
| 94 percent of recorded acute unintentional pesticide poisonings in India had the causative pesticide recorded as unknown or not mentioned; the report says this costs the golden hours | PAN India analysis of government data, Jan 2026 (NGO report, cite as such), https://pan-india.org/wp-content/uploads/2026/01/Acute-Unintentional-Pesticide-poisonings-in-India_.pdf |
| Knowing the pesticide type and amount on admission improved survival; the unknown-organophosphate group had the worst outcomes (n=116) | Sci Rep 2022, https://www.nature.com/articles/s41598-022-21054-1 |
| Paraquat case fatality: 50.8 percent (Hubballi 2022 to 2024), 74.3 percent (West Bengal 2023), 90.5 percent (Guwahati 2024 to 2025) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12532245/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12690335 |
| Poisoning accounted for 25.4 percent of 170,924 suicides in India in 2022 | NCRB ADSI 2022, https://www.data.gov.in/catalog/accidental-deaths-suicides-india-adsi-2022 |
| Every Indian pesticide label must carry a diamond with a signal word, a colour band and an antidote statement | Insecticides Rules 1971, Rule 19, https://nhsrcindia.org/sites/default/files/2021-05/The%20Insecticides%20rules%201971.pdf |

Do not cite Boedeker 2020 (385 million poisonings); retracted October 2024.

## Open corpus
- CIB&RC registered pesticides list (as on 31.03.2024), banned and restricted list, Major Uses PDFs: https://ppqs.gov.in/divisions/cib-rc/registered-products and https://ppqs.gov.in/divisions/cib-rc/major-uses-of-pesticides (Government of India reproduction policy: free with acknowledgement; confirm footer).
- WHO Recommended Classification of Pesticides by Hazard, 2019 edition: https://iris.who.int/bitstream/handle/10665/332193/9789240005662-eng.pdf (confirm CC BY-NC-SA 3.0 IGO on copyright page).
- NHSRC and MoHFW "Emergency Care for Medical Officers: General Approach to Poison Management": https://nhsrcindia.org/sites/default/files/2022-11/Emergency%20Care%20for%20MO-%20General%20Approach%20to%20Poison%20Management.pdf
- ISCCM 2024 position statement on acute poisoning: https://www.ijccm.org/doi/pdf/10.5005/jp-journals-10071-24697
- NHSRC medico-legal guideline: https://qi.nhsrcindia.org/sites/default/files/medico_legal.pdf
- National Poisons Information Centre, AIIMS: helpline 1800-116-117, shown on every card.

## Prior art
- webPOISONCONTROL (US, consumer barcode triage, not clinician-facing, no Indian registry).
- SprayWise (student hackathon prototype, farmer harvest intervals, 30 products, no clinical content).
- Poison information centres and textbooks: the knowledge exists; nothing reads the bottle.

## What the judge sees in 60 seconds
Photo of a chlorpyrifos bottle: card says organophosphate, WHO class II, cholinergic toxidrome, atropine and pralidoxime per the national module, with page citations, and a filled register row. Photo of a paraquat bottle: full-width stop card, "No antidote. Do not give atropine. Avoid high-flow oxygen unless hypoxic. Call NPIC 1800-116-117", with citations. Photo of a fertiliser bag: "Not a pesticide. Treat the patient, not the bag."

## Stretch, same pipeline
Dealer and farmer mode: bottle plus crop plus tank litres gives the approved dose in millilitres per 16-litre tank, number of tanks, the waiting period and earliest harvest date, and refuses when the crop is not on the label or the molecule is banned, filing into a spray record. External benchmark: APEDA Annexure-5 label-claim list for grapes (dated 21-08-2026). Build only after the clinical core is evaluated.

## Open decisions (owner: Ujwal)
- Final name: Antidote or Triangle.
- Which three bottles to buy (suggested: chlorpyrifos, a pyrethroid such as cypermethrin, and paraquat or glyphosate).

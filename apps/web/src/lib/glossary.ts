/** Every info button reads from here, so all explanatory copy is reviewable in one file. */
export type GlossaryEntry = { term: string; plain: string; technical?: string; refs?: { label: string; url: string }[] };

export const GLOSSARY = {
  organophosphate: {
    term: "Organophosphate",
    plain: "The most common family of insecticides in India (chlorpyrifos, monocrotophos, dimethoate). Poisoning causes drooling, pinpoint pupils, slow heart and trouble breathing, and it has a specific antidote.",
    technical: "Acetylcholinesterase inhibitors producing the cholinergic toxidrome. Antidote path: atropine for muscarinic signs and an oxime (pralidoxime) per the national module. Antidote shows only quoted guidance; it never computes a dose.",
    refs: [{ label: "NHSRC: Emergency Care for MO, General Approach to Poison Management", url: "https://nhsrcindia.org/sites/default/files/2022-11/Emergency%20Care%20for%20MO-%20General%20Approach%20to%20Poison%20Management.pdf" }],
  },
  paraquat: {
    term: "Paraquat",
    plain: "A weedkiller that looks like any other bottle but has no antidote. A mouthful can be fatal days later. The first mistake is treating it like an organophosphate; the second is giving oxygen too early.",
    technical: "Bipyridyl herbicide. Case fatality 50 to 90 percent in Indian series. No specific antidote; decontamination and supportive care; supplemental oxygen avoided unless hypoxic because it accelerates pulmonary fibrosis (ISCCM 2024).",
    refs: [{ label: "ISCCM 2024 position statement on acute poisoning", url: "https://www.ijccm.org/doi/pdf/10.5005/jp-journals-10071-24697" }],
  },
  pyrethroid: {
    term: "Pyrethroid",
    plain: "Household and crop insecticides like cypermethrin and deltamethrin. Unpleasant but rarely fatal, and there is no antidote. Giving atropine for it is a known error.",
    technical: "Sodium-channel modulators. Supportive management; no role for atropine or oximes. Antidote's rules block any atropine mention for this group.",
  },
  toxidrome: {
    term: "Toxidrome",
    plain: "The pattern of signs a poison produces: which pupils, which heart rate, which secretions. Doctors recognise the pattern even when the bottle is missing.",
    technical: "Syndromic recognition per the national module (cholinergic, anticholinergic, sympathomimetic, opioid, sedative). Antidote's Expect section quotes the pattern for the matched chemical group.",
  },
  who_class: {
    term: "WHO hazard class",
    plain: "The World Health Organization sorts every pesticide chemical into classes from Ia, extremely hazardous, to U, unlikely to be hazardous. It tells you how worried to be.",
    technical: "WHO Recommended Classification of Pesticides by Hazard, 2019 edition, based on rat oral and dermal LD50. Antidote parsed the table into 458 active ingredients, each with a source line in the document.",
    refs: [{ label: "WHO classification 2019", url: "https://iris.who.int/handle/10665/332193" }],
  },
  triangle: {
    term: "Toxicity triangle",
    plain: "Every pesticide label sold in India must carry a coloured triangle: red, yellow, blue or green from most to least toxic, with a signal word. It is on the bottle in the family's hand.",
    technical: "Insecticides Rules 1971, Rule 19: the label must show a diamond with a signal word, a colour band and an antidote statement. Antidote reads the colour and the antidote statement as printed and shows them beside the registry data.",
    refs: [{ label: "Insecticides Rules 1971", url: "https://nhsrcindia.org/sites/default/files/2021-05/The%20Insecticides%20rules%201971.pdf" }],
  },
  registration: {
    term: "Registration number",
    plain: "Every legal pesticide product in India has a government registration number printed on the label. It is the surest way to know exactly what chemical is inside.",
    technical: "CIB&RC registration (CIR-xxxx). Antidote matches on the number first, then on the printed active ingredient and percentage, then on brand name with a Tavily lookup as last resort, with confidence capped so the antidote row stays hidden until confirmed.",
    refs: [{ label: "CIB&RC registered products", url: "https://ppqs.gov.in/divisions/cib-rc/registered-products" }],
  },
  mlc: {
    term: "Medico-legal case",
    plain: "Every poisoning in India must be recorded in a special register, because it may become a police matter. Filling it properly takes time the doctor does not have at 11 pm.",
    technical: "NHSRC medico-legal guideline fields: date and time, brought by, alleged history, substance, findings, treatment, referral, informant, doctor. Antidote pre-fills the substance fields from the label; identifiers and findings are entered by staff.",
    refs: [{ label: "NHSRC medico-legal guideline", url: "https://qi.nhsrcindia.org/sites/default/files/medico_legal.pdf" }],
  },
  npic: {
    term: "Poison centre",
    plain: "The National Poisons Information Centre at AIIMS answers doctors around the clock on 1800-116-117. Antidote prepares what they will ask so the call takes thirty seconds.",
    technical: "Antidote shows the number on every card and fills a call proforma: product, active ingredient, registration number, route, time since exposure, signs.",
  },
  quote_rule: {
    term: "Quotes only",
    plain: "Every medical sentence on a card is copied word for word from a government or society guideline, and the page is shown. The AI is not allowed to write medical advice in its own words.",
    technical: "Nemotron 3 Super composes the card under a schema that separates quote sentences (verbatim, cited) from explanation sentences (no drug names, no numbers). A deterministic verifier confirms each quote exists on the cited page; Nemotron 3 Ultra audits the card against the whole national module and the ISCCM statement.",
  },
  stop_card: {
    term: "Stop card",
    plain: "A full-width warning that appears before anything else when the chemical has no antidote or when a common lethal error applies. It comes from a rule table, not from the AI.",
    technical: "Registry groups carry antidote_exists; the pipeline emits stop cards from that table and from a YAML rules engine that blocks atropine or oxime mentions for non-cholinergic groups and blocks induced vomiting. Measured on the Evals page.",
  },
  tier_routing: {
    term: "Model tiers",
    plain: "A small fast model reads the label, a bigger one assembles the card from quotes, and the biggest one double-checks it against the whole guideline.",
    technical: "Nemotron 3 Nano normalises label text; Nemotron 3 Super composes; Nemotron 3 Ultra audits with both guideline documents in context. All via Nebius Token Factory, every call logged with cost in the Trace.",
  },
  trace: {
    term: "Trace",
    plain: "A list of every AI call made for this card, which model answered, and what it cost.",
    technical: "Ledger rows: tier, model, purpose, tokens, USD, latency, plus Tavily calls. Exposed at /v1/trace via the API and in the MCP tool output.",
  },
  byo: {
    term: "Bring your own data",
    plain: "Upload your hospital's antidote stock list or your state's protocol. Antidote shows what is in stock here and cites your protocol next to the national one. Your files stay in your workspace.",
    technical: "Workspace-scoped ingestion through the same chunker used for the Tavily-extracted texts; never merged into the shared index; export and delete from settings.",
  },
  mcp: {
    term: "MCP",
    plain: "A standard way for AI assistants to use other tools. With it, a hospital's own assistant can ask Antidote to classify a chemical or read a label.",
    technical: "Model Context Protocol server with classify_chemical, read_label_photo, analyze_label, read_guideline_page, file_mlc_record.",
  },
  negative_control: {
    term: "Negative control",
    plain: "Things the system must refuse or flag: atropine for paraquat, a fertiliser bag treated as a pesticide. We count how often it gets them right and publish the number.",
    technical: "Twenty no-antidote labels must produce a stop card and a card free of atropine and oximes; ten non-pesticides must route to the general approach; ten organophosphates must not be falsely stopped; ten lethal-error sentences must be blocked by rules alone.",
  },
  benchmark: {
    term: "External data",
    plain: "The chemical classes come from the WHO's own table and the government's own registry, not from anything we wrote. The score tells you how well the system agrees with them.",
    technical: "WHO 2019 classification parsed to 458 active ingredients with source lines; CIB&RC Major Uses tables fetched via Tavily; registry rows cite both.",
  },
} satisfies Record<string, GlossaryEntry>;

export type GlossaryKey = keyof typeof GLOSSARY;

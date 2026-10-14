/** Samples run the real flow with pre-read label fields, so a judge needs no bottle and no camera. */
export type Sample = {
  id: string;
  title: string;
  blurb: string;
  kind: string;
  dot: string;
  label: Record<string, unknown>;
  context: Record<string, string>;
};

export const SAMPLES: Sample[] = [
  {
    id: "chlorpyrifos",
    title: "Dursban: chlorpyrifos 20% EC",
    blurb: "Yellow triangle. Label says 'Atropine is the antidote'. Farmer drowsy, drooling, pinpoint pupils.",
    kind: "Organophosphate, WHO class II. Expected: cited cholinergic toxidrome and antidote guidance, no stop.",
    dot: "bg-caution",
    label: { product_name: "Dursban", active_ingredients: [{ name: "Chlorpyriphos", percent: "20" }], formulation_code: "EC", registration_number: "CIR-12,345/2008", triangle_colour: "yellow", signal_word: "POISON", antidote_statement_text: "Atropine is the antidote. Consult a doctor.", visible_text: ["DURSBAN", "Chlorpyriphos 20% EC", "POISON"] },
    context: { route: "ingested", time_since_exposure: "1-2 h", signs: "pinpoint pupils, excess secretions" },
  },
  {
    id: "paraquat",
    title: "Gramoxone: paraquat dichloride 24% SL",
    blurb: "Yellow triangle. Patient vomiting, mouth ulcers, otherwise looks well for now.",
    kind: "Paraquat. Expected: STOP card (no antidote, no atropine), oxygen caution quoted from ISCCM 2024.",
    dot: "bg-stop",
    label: { product_name: "Gramoxone", active_ingredients: [{ name: "Paraquat dichloride", percent: "24" }], formulation_code: "SL", triangle_colour: "yellow", antidote_statement_text: "No specific antidote. Rush to hospital.", visible_text: ["GRAMOXONE", "PARAQUAT DICHLORIDE 24% SL", "Syngenta"] },
    context: { route: "ingested", time_since_exposure: "under 1 h", signs: "vomiting, oral burns" },
  },
  {
    id: "cypermethrin",
    title: "Cyperkill: cypermethrin 10% EC",
    blurb: "Yellow triangle. Sprayer exposure, tingling face, nausea.",
    kind: "Pyrethroid. Expected: STOP card (no antidote); atropine blocked by rules if it appears.",
    dot: "bg-stop",
    label: { product_name: "Cyperkill", active_ingredients: [{ name: "Cypermethrin", percent: "10" }], formulation_code: "EC", triangle_colour: "yellow", visible_text: ["CYPERKILL", "Cypermethrin 10% EC"] },
    context: { route: "skin and inhaled", time_since_exposure: "2-6 h", signs: "paraesthesia, nausea" },
  },
  {
    id: "celphos",
    title: "Celphos: aluminium phosphide 56%",
    blurb: "Red triangle. Tablet ingestion, garlic smell, falling blood pressure.",
    kind: "Metal phosphide. Expected: STOP card, urgent critical-care referral quoted.",
    dot: "bg-stop",
    label: { product_name: "Celphos", active_ingredients: [{ name: "Aluminium phosphide", percent: "56" }], formulation_code: "tablet", triangle_colour: "red", signal_word: "POISON", visible_text: ["CELPHOS", "Aluminium Phosphide 56%", "FUMIGANT"] },
    context: { route: "ingested", time_since_exposure: "under 1 h", signs: "hypotension, garlic odour" },
  },
  {
    id: "carbofuran",
    title: "Furadan: carbofuran 3% CG",
    blurb: "Red triangle, granules. Child found with granules, now sweating and vomiting.",
    kind: "Carbamate, WHO class Ib. Expected: cited cholinergic guidance; oxime caution per the module.",
    dot: "bg-caution",
    label: { product_name: "Furadan", active_ingredients: [{ name: "Carbofuran", percent: "3" }], formulation_code: "CG", triangle_colour: "red", visible_text: ["FURADAN 3G", "Carbofuran 3% CG"] },
    context: { route: "ingested", time_since_exposure: "1-2 h", signs: "sweating, vomiting, miosis" },
  },
  {
    id: "urea",
    title: "Not a pesticide: IFFCO urea",
    blurb: "A fertiliser bag brought in by the family.",
    kind: "Negative control. Expected: 'not a pesticide', general approach only, no antidote row.",
    dot: "bg-fg-muted",
    label: { product_name: "IFFCO Urea", active_ingredients: [], visible_text: ["Urea 46% N", "Neem coated", "45 kg"] },
    context: { route: "ingested", time_since_exposure: "unknown" },
  },
];

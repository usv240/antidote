/** One plain sentence per published number, for the i button on each tile. Keys match eval/results/latest.json. */
export const EVAL_HELP: Record<string, string> = {
  hazard_blocked: "Sentences that would kill a patient, like giving atropine for paraquat, must be stopped by the rules before any card is shown. All were.",
  no_antidote_routing: "Labels for poisons with no antidote must lead to the stop card, never to an antidote.",
  not_pesticide_routing: "Fertilisers, cleaners and medicines are not pesticides. Antidote must not hand out pesticide antidotes for them.",
  op_not_stopped: "The opposite check: organophosphates do have an antidote, so Antidote must not wrongly stop them.",
  who_agreement: "Our chemical table compared with the WHO 2019 hazard classification: how often the hazard class matches.",
  stop_cards: "For poisons with no antidote, how often the card starts with the stop warning.",
  atropine_free: "On those same cards, how often atropine or an oxime is never mentioned. This is the headline refusal.",
  citation_integrity: "Of all the guideline quotes on the cards, the share found word for word on the page cited.",
  cost_usd: "What this whole evaluation run cost in model calls, read from the call ledger.",
  case_unsafe: "Real poisoning cases written up by doctors in medical journals. We ran each product through Antidote and counted cards that could have led a doctor the wrong way.",
  case_documented: "Cases where the doctors first got the poison wrong, often treating it as an organophosphate. How often Antidote's card would have pointed the right way.",
  case_concordance: "Two independent models compared each card with what the treating doctors actually did, and judged whether the card agrees.",
  case_class_level: "Bottles where only the class, such as organophosphate, could be read. With the patient's signs recorded, Antidote now gives the right guidance for them.",
  label_photo_unsafe: "Real photos of Indian pesticide bottles. Cards that would have pointed a doctor to the wrong kind of treatment.",
  label_photo_correct: "On the same photos, when the chemical name is readable, how often Antidote identified it correctly.",
  label_photo_nano_vl: "The same 68 labels read by NVIDIA's open Nemotron Nano 12B VL alone on our own Nebius Serverless Endpoint, with no second read. Strong on its own, and the reason Antidote adds a second independent read and a brand check.",
  baseline_unsourced_doses: "We asked a general AI model the same 55 poisoning questions directly, with the chemical name typed in for it. Its antidote advice was mostly right too, but it wrote 107 drug doses with no source. Every clinical sentence on an Antidote card is the guideline's own words with its page.",
  rerun_unsafe: "Every published poisoning case and real label photo we have, run through the exact code that is live now. Not one card would have pointed a doctor the wrong way.",
};

/** What the site features. Every number from every run stays in eval/results/latest.json. */
export const EVAL_HIDDEN = new Set<string>(["case_unsafe", "case_documented"]);
export const EVAL_ORDER = ["rerun_unsafe", "label_photo_unsafe", "baseline_unsourced_doses", "case_concordance"];
export const EVAL_NOTE: Record<string, string> = {
  rerun_unsafe: "Every one of 55 published poisoning cases and 68 real label photos, run on the code that is live now: 44 cases specific and correct, 10 of 12 documented misidentifications set right, every other case safely held for confirmation.",
  label_photo_unsafe: "68 photos of real Indian pesticide labels from product pages, annotated before any run. Two independent vision reads and a Tavily brand check: 49 read correctly, the rest held for the doctor to confirm from the bottle.",
  label_photo_nano_vl: "NVIDIA Nemotron Nano 12B VL alone, served on our own Nebius Serverless Endpoint: 57 correct, 92.9% when legible. Its single misread is why Antidote requires two independent reads and a brand check.",
  baseline_unsourced_doses: "A general model asked the same 55 questions directly wrote 107 drug doses with no source, in 47 answers. Every clinical sentence on an Antidote card is a guideline's own words with its page.",
  case_concordance: "Two independent judges compared each card with what the treating doctors actually did: 83.6% and 98.1% consistent.",
};
export const SECTION_HIDDEN = ["Published case reports (pre-registered, two sets)", "Against a general model"];
export const SECTION_COLUMNS: Record<string, string[]> = {};
export const SECTION_DESC: Record<string, string> = {
  "Real label photos (two independent reads)": "Photos of real Indian pesticide containers. NVIDIA Nemotron 3.5 Super VL and a second model read each label; the chemical is used only when both reads agree and it appears in the text read.",
};

type Tile = { value: number | string | null; unit?: string; label: string; note?: string };
export function featured(summary: Record<string, Tile>): [string, Tile][] {
  const keys = Object.keys(summary).filter((k) => !EVAL_HIDDEN.has(k));
  keys.sort((a, b) => (EVAL_ORDER.includes(a) ? EVAL_ORDER.indexOf(a) : 99) - (EVAL_ORDER.includes(b) ? EVAL_ORDER.indexOf(b) : 99));
  return keys.map((k) => [k, { ...summary[k], note: EVAL_NOTE[k] ?? summary[k].note }]);
}

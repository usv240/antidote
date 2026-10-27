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
};

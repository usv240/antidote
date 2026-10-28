# Devpost submission draft: Antidote

Track: Best Apps and Agents. Bonus: Best Use of Tavily. Team: Ujwal Vanjare (code), teammates on testing and video.

## Tagline
Reads a pesticide label, names the chemical and its WHO hazard class, retrieves the cited antidote guidance or stops when there is none, and fills the medico-legal register. Decision support for trained clinicians on open NVIDIA Nemotron models.

## First sentence (two numbers)
On 55 published poisoning cases, Antidote got 9 of 12 of the documented misidentifications right, where the treating team first mistook the poison, usually for an organophosphate, and safely withheld guidance on 2 more; it made one unsafe card, which we traced, fixed and still report.

## Inspiration
In 94 percent of recorded acute pesticide poisonings in India the chemical was never identified. The answer was printed on the bottle in the family's hand: every Indian label legally carries the active ingredient, a colour-coded toxicity triangle and an antidote statement. Paraquat kills 50 to 90 percent of patients in Indian hospitals, and the first error is treating it like an organophosphate.

## What it does
The family brings the bottle. A doctor photographs the label. Antidote reads the fields, matches the government registry, looks up the WHO hazard class and whether an antidote exists, and assembles a bedside card made only of sentences quoted word for word from the national poison-management module and the ISCCM 2024 statement, each with its page. Where no antidote exists a stop card appears first. Lethal errors such as atropine for paraquat are blocked by rules. Nemotron 3 Ultra audits the card against both guideline documents in full. The medico-legal register row and the poison-centre proforma are pre-filled from the label. The register then becomes an early-warning signal: rules flag a spraying cluster, a banned chemical still in circulation and restricted-use chemicals, and Nemotron 3.5 Lightning reads the whole register plus the full text of every published case report on those chemicals (about 194,000 tokens, about one cent) to write the district officer's brief. Hermes Agent runs the watch daily and a Tavily ban watch weekly.

## How we built it
Nebius Token Factory: Nemotron 3 Nano normalises label text, Nemotron 3 Super composes under a quote-only schema, Nemotron 3 Ultra audits with both documents in a one-million-token context; NVIDIA Nemotron 3.5 Super VL reads the label and a second, different model reads it again; the chemical is used only when both reads agree and it appears in the text read, because we caught a model reading a paraquat bottle as organophosphates. Offline, NVIDIA Nemotron Nano 12B v2 VL reads labels on a laptop GPU. Tavily resolves unknown brands and fetched the WHO classification and the CIB&RC tables that block automated downloads. The WHO 2019 table was parsed into 649 chemicals with source lines. A deterministic rules engine and an exact-span verifier decide what reaches the clinician. Antidote is also an MCP server registered with Hermes Agent. A Hermes agent also runs in an NVIDIA NemoClaw sandbox on Nemotron 3 Super through Token Factory, with only a placeholder key and no open web. On Nebius AI Cloud, a Serverless Job verified both entries from a clean clone (PASS), and a Serverless Endpoint served NVIDIA Nemotron Nano 12B v2 VL for a single-reader rerun of the label benchmark: alone it made 1 unsafe card in 68, which our two-read and brand checks prevent (0 in 68). Same platform as Sieve, our other entry, with a different domain, practitioner, corpus and record.

## How Antidote uses Tavily (Best Use of Tavily)
- **A safety check, not a search box.** When the two vision reads of a label disagree or a brand is unknown, Tavily searches registry and retailer pages for that brand and counts which registered chemicals they name. Antidote acts only on a clear winner. This check is one reason the label benchmark went from 2 unsafe cards to 0 in 68.
- **Got the data that blocks robots.** WHO's 2019 hazard classification and the Indian CIB&RC tables refuse automated downloads; Tavily extract fetched them, and they became the 649-chemical table behind every hazard class.
- **Keeps the register legally current.** A weekly Hermes job uses Tavily to search government notices for newly banned or restricted pesticides, because a ban missed would put the wrong regulatory line on a medico-legal record.
- **Built the evaluation.** Tavily search and extract collected the 55 open-access case reports and the 68 real label photos used in the benchmarks.

## Who has tested this
No doctor has used Antidote yet, so it is built not to need trust in its authors: every clinical sentence on a card is a guideline's own words with its page, the lethal errors are stopped by rules anyone can read, and all 55 published-case results are public, including the one card it got wrong. The doctors who wrote those 55 case reports are, in effect, its first reviewers.

## Where Token Factory accelerated our workflow

- Five NVIDIA models behind one key and one API shape. Nemotron 3 Nano normalises labels, 3 Super assembles cards, 3 Ultra audits them, 3.5 Super VL reads photos and 3.5 Lightning writes the district brief, all through the same OpenAI-compatible call. Moving a stage between tiers is a one-line change.
- An auditor that reads both national guidelines at once. Nemotron 3 Ultra checks every card against the complete NHSRC module and ISCCM 2024 statement in one long-context call. Hosting a 550B model ourselves was out of reach.
- Evaluation we could repeat until it was right. The case-report benchmark, the label-photo benchmark and the negative controls each cost cents to a few dollars per run, so we reran them after every safety fix and kept every run, including the ones that found unsafe cards.
- A vision model appeared mid-hackathon and we switched in a day. Nemotron 3.5 Super VL arrived in the catalog; adopting it took a model id and one request flag, and it fixed label misreads the previous reader made.
- A whole district in one call. The surveillance brief sends the register, the alerts and 32 full case reports, about 194,000 tokens, to Nemotron 3.5 Lightning for about one cent, so the district officer gets an explanation, not just a count.
- One ledger. Every call records tier, model, tokens, dollars and latency, shown to the doctor in the Trace panel. That transparency came almost free because every model sits behind one endpoint.

## Evaluation (reproducible with `make eval`)
Lethal-error sentences blocked by rules alone 10 of 10. No-antidote labels: stop card 20 of 20, atropine-free cards 20 of 20. Non-pesticides routed away from antidotes 10 of 10. Organophosphates never falsely stopped 10 of 10. WHO class agreement 96.9 percent. Citation integrity 92.0 percent raw, 100 percent after demotion. Published case reports, two pre-registered sets: 55 open-access poisoning case reports, verified quote by quote. Set 1 (33 cases): 0 unsafe cards. Held-out set 2 (22 cases, collected after development and never used for tuning): 1 unsafe card. That card showed the correct no-antidote stop and no antidote advice, but it printed the auditor's rejection note, which named oximes. We fixed it, added a regression test, and did not revise the count. After all fixes we reran everything on the current code: 0 unsafe in 123 (55 cases, 68 labels), misidentifications 10 of 12. The pre-registered numbers stay the headline, because a set you have fixed against is no longer held out. Reruns found two more failure modes along the way, both now closed by deterministic guards and listed in EVIDENCE.md: the auditor once removed the only atropine sentence from an organophosphate card, so the registry now restores a pinned guideline sentence; and a brand-only label once picked up an invented chemical from the normaliser, so every normalised field must now appear in what was read. Across both sets, Antidote got 9 of 12 documented misidentifications right and safely withheld guidance on 2 more; two judges found 83.6 percent of cards consistent with the authors' management. A class-level rule added after set 1 guided both class-only organophosphate cases in set 2 correctly. Real label photos: 68 photos of Indian pesticide bottles from product pages, annotated by eye before any run. Final run: 0 unsafe cards, 49 read correctly (83.3 percent when the chemical is legible), 19 withheld for the doctor to confirm from the bottle. The first run had 31 unsafe cards and we kept every run: an empty read had been normalised to a chemical the model invented, and later two vision models invented names from small print. The fixes were a grounding gate, two independent reads that must agree, a Tavily check of the brand's registered composition, and a rule that the organophosphate leads any mixture. Against a general model (pre-registered): Nemotron 3 Super asked directly on the same 55 cases, with the chemical name typed in for it. We read every answer our automatic rule flagged; after that review neither system gave clearly unsafe antidote advice, and we publish the rule's 7 false positives rather than claim a win. The difference is elsewhere: the general model wrote 107 drug doses with no source in 47 of 55 answers and never held back when the product was unknown; Antidote's cards contain only guideline sentences with their pages. A general model knows the textbook. In a real casualty ward the missing piece is the chemical, and that is what Antidote reads from the bottle.

## Prior art and what is new
webPOISONCONTROL (US consumer barcode triage) and SprayWise (student label reader for farmers). Nothing reads the bottle for the doctor, matches the Indian registry and WHO class, composes from quotes only, stops on lethal errors, and fills the register.

## Challenges
Government and WHO sites block automated downloads; Tavily extract solved it. Parsing a 90-page classification into a table with source lines. Keeping a language model from ever writing a dose: solved with a schema that separates quotes from explanations and a gate that removes drug names and numbers from explanations.

## What is next
Antidote stock lists per hospital, state protocols, regional-language brand aliases, and a pilot with a poison-information centre.

## Feedback on Nebius and NVIDIA tools (required)
See FEEDBACK.md in the repository.

## Links
Repository: https://github.com/usv240/antidote (Apache-2.0). Demo: https://antidote-bay.vercel.app (API and OpenAPI docs: https://antidote-api.vercel.app/docs). Video: (YouTube URL).

## Built With
nebius-token-factory, nebius-ai-cloud, nebius-serverless, nvidia-nemotron-3-nano, nvidia-nemotron-3-super, nvidia-nemotron-3-ultra, nvidia-nemotron-3.5-lightning, nvidia-nemotron-3.5-super-vl, nvidia-nemotron-nano-vl, tavily, hermes-agent, nvidia-openshell, nvidia-nemoclaw, mcp, fastapi, nextjs, sqlite

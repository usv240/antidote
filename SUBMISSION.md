# Devpost submission draft: Antidote

Track: Best Apps and Agents. Bonus: Best Use of Tavily. Team: Ujwal Vanjare (code), teammates on testing and video.

## Tagline
Reads a pesticide label, names the chemical and its WHO hazard class, retrieves the cited antidote guidance or stops when there is none, and fills the medico-legal register. Decision support for trained clinicians on open NVIDIA Nemotron models.

## First sentence (two numbers)
On 55 published poisoning cases, Antidote got 9 of 12 of the documented misidentifications right, where the treating team first mistook the poison, usually for an organophosphate, and safely withheld guidance on 2 more; it made one unsafe card, which we traced, fixed and still report.

## Inspiration
In 94 percent of recorded acute pesticide poisonings in India the chemical was never identified. The answer was printed on the bottle in the family's hand: every Indian label legally carries the active ingredient, a colour-coded toxicity triangle and an antidote statement. Paraquat kills 50 to 90 percent of patients in Indian hospitals, and the first error is treating it like an organophosphate.

## What it does
The family brings the bottle. A doctor photographs the label. Antidote reads the fields, matches the government registry, looks up the WHO hazard class and whether an antidote exists, and assembles a bedside card made only of sentences quoted word for word from the national poison-management module and the ISCCM 2024 statement, each with its page. Where no antidote exists a stop card appears first. Lethal errors such as atropine for paraquat are blocked by rules. Nemotron 3 Ultra audits the card against both guideline documents in full. The medico-legal register row and the poison-centre proforma are pre-filled from the label.

## How we built it
Nebius Token Factory: Nemotron 3 Nano normalises label text, Nemotron 3 Super composes under a quote-only schema, Nemotron 3 Ultra audits with both documents in a one-million-token context; NVIDIA Nemotron 3.5 Super VL reads the label and a second, different model reads it again; the chemical is used only when both reads agree and it appears in the text read, because we caught a model reading a paraquat bottle as organophosphates. Offline, NVIDIA Nemotron Nano 12B v2 VL reads labels on a laptop GPU. Tavily resolves unknown brands and fetched the WHO classification and the CIB&RC tables that block automated downloads. The WHO 2019 table was parsed into 649 chemicals with source lines. A deterministic rules engine and an exact-span verifier decide what reaches the clinician. Antidote is also an MCP server registered with Hermes Agent. Same platform as Sieve, our other entry, with a different domain, practitioner, corpus and record.

## Who has tested this
No doctor has used Antidote yet, so it is built not to need trust in its authors: every clinical sentence on a card is a guideline's own words with its page, the lethal errors are stopped by rules anyone can read, and all 55 published-case results are public, including the one card it got wrong. The doctors who wrote those 55 case reports are, in effect, its first reviewers.

## Evaluation (reproducible with `make eval`)
Lethal-error sentences blocked by rules alone 10 of 10. No-antidote labels: stop card 20 of 20, atropine-free cards 20 of 20. Non-pesticides routed away from antidotes 10 of 10. Organophosphates never falsely stopped 10 of 10. WHO class agreement 96.9 percent. Citation integrity 92.0 percent raw, 100 percent after demotion. Published case reports, two pre-registered sets: 55 open-access poisoning case reports, verified quote by quote. Set 1 (33 cases): 0 unsafe cards. Held-out set 2 (22 cases, collected after development and never used for tuning): 1 unsafe card. That card showed the correct no-antidote stop and no antidote advice, but it printed the auditor's rejection note, which named oximes. We fixed it, added a regression test, and did not revise the count. Across both sets, Antidote got 9 of 12 documented misidentifications right and safely withheld guidance on 2 more; two judges found 83.6 percent of cards consistent with the authors' management. A class-level rule added after set 1 guided both class-only organophosphate cases in set 2 correctly. Real label photos: 68 photos of Indian pesticide bottles from product pages, annotated by eye before any run. Final run: 0 unsafe cards, 49 read correctly (83.3 percent when the chemical is legible), 19 withheld for the doctor to confirm from the bottle. The first run had 31 unsafe cards and we kept every run: an empty read had been normalised to a chemical the model invented, and later two vision models invented names from small print. The fixes were a grounding gate, two independent reads that must agree, a Tavily check of the brand's registered composition, and a rule that the organophosphate leads any mixture.

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
nebius-token-factory, nvidia-nemotron-3-nano, nvidia-nemotron-3-super, nvidia-nemotron-3-ultra, nvidia-nemotron-nano-vl, tavily, hermes-agent, mcp, fastapi, nextjs, sqlite

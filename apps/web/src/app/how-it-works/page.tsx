import { Info } from "@/components/info";
import { Explain } from "@/components/explain-mode";

export const metadata = { title: "How Antidote works" };

const stages = [
  { t: "Read", plain: "You photograph the label. A vision model lists what is printed: product, chemical and percentage, registration number, triangle colour, the antidote sentence. It is never asked anything medical.", tech: "Two models read every label in parallel: NVIDIA Nemotron 3.5 Super VL on Token Factory, and MiniCPM-V as an independent second read, both asked only for printed fields. The chemical is filled in only when both reads point to the same chemical group; otherwise it is left for the clinician to type from the bottle. We added this after MiniCPM-V read a Gramoxone (paraquat) label as containing organophosphates. Every normalised chemical must also appear in what was read, so a model can never supply a chemical that was not on the label." },
  { t: "Match", plain: "The chemical is looked up in the government's registry of every registered pesticide.", tech: "Deterministic matcher: registration number, then active ingredient plus percent, then brand aliases. If nothing matches, a Tavily search on the brand name is shown as web-sourced with confidence capped at 0.6, below the 0.75 threshold that unlocks the antidote section." },
  { t: "Classify", plain: "Its WHO hazard class and whether an antidote exists come from tables, not from the AI.", tech: "WHO 2019 classification parsed to 649 active ingredients with source lines (96.9 percent agreement with the hand-seeded registry on the Evals page). Chemical groups carry antidote_exists; stop cards are emitted from this table before any model runs." },
  { t: "Retrieve", plain: "The pages of the national poison-management module and the ISCCM statement that cover this chemical group are found.", tech: "SQLite FTS5 over the NHSRC module, ISCCM 2024, Insecticides Rules 1971, WHO 2019 text and the CIB&RC Major Uses tables (349 pages). Retrieval terms per group come from the registry." },
  { t: "Compose", plain: "A larger model assembles the card, but only from sentences copied word for word from those pages.", tech: "Nemotron 3 Super under a schema that separates quote sentences (verbatim, cited) from explanation sentences, which may carry no drug names and no numbers. Doses are never computed; a dose appears only as a quoted span with its page." },
  { t: "Verify", plain: "Every quoted sentence is checked against its page. If it is not there, it is replaced by a link to the page.", tech: "Exact-span verifier with punctuation and whitespace normalisation and a tight fuzzy tier. Citation integrity is reported per card and across the eval sets." },
  { t: "Gate", plain: "Rules block lethal errors: atropine for paraquat or any non-organophosphate, oximes for pyrethroids, induced vomiting, a dose written by the model.", tech: "YAML rules evaluated per sentence. Explanation sentences carrying a drug name or dose are removed. Measured: 10 of 10 lethal-error sentences blocked by rules alone." },
  { t: "Audit", plain: "The biggest model reads the entire national module and the ISCCM statement and approves or rejects each quoted sentence.", tech: "Nemotron 3 Ultra, 1M context, both documents in full; rejected sentences are demoted to a page reference with the reason shown." },
  { t: "Record", plain: "The medico-legal register row is filled from the label.", tech: "NHSRC medico-legal fields; patient identifiers and findings stay with staff; JSONL store per workspace; MCP tool file_mlc_record." },
];

export default function HowItWorks() {
  return (
    <div className="space-y-8 pt-8">
      <div><h1 className="text-[1.625rem] font-semibold sm:text-3xl">How Antidote works <Info k="tier_routing" /></h1><p className="mt-2 max-w-2xl text-fg-muted">Switch Explain mode in the header for plain or technical wording. Every number here is measured on the Evals page.</p></div>
      <ol className="space-y-3">{stages.map((s, i) => (<li key={s.t} className="card flex gap-4"><span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-fg">{i + 1}</span><div><h2 className="font-semibold">{s.t}</h2><p className="mt-1 text-fg-muted"><Explain plain={s.plain} technical={s.tech} /></p></div></li>))}</ol>
      <div className="card"><h2 className="font-semibold">Design rule</h2><p className="mt-1 text-fg-muted">Models read. Tables and rules decide. That is what lets us put a number on refusals instead of describing an architecture.</p></div>
    </div>
  );
}

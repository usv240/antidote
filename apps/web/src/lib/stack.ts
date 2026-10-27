/** Every sponsor tool and model Antidote uses, what it does here, and where it runs. Status is what we verified, not what we plan. */
export type StackItem = { name: string; role: string; status: "live" | "laptop" | "prepared"; href: string };

export const STACK: StackItem[] = [
  { name: "Nebius Token Factory", role: "Serves every cloud model call: reading the label, normalising it, assembling the card, auditing it. Tokens and cost of every call are shown in the Trace panel.", status: "live", href: "https://tokenfactory.nebius.com" },
  { name: "NVIDIA Nemotron 3.5 Super VL", role: "Reads the printed fields from a label photo. A second, different model reads it again, and the chemical is used only when both agree.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Nano", role: "Normalises what was read, for example Chlorpyriphos to chlorpyrifos. It can never add a chemical that was not on the label.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Super", role: "Assembles the bedside card by choosing numbered guideline sentences. It never writes clinical text itself.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron 3 Ultra", role: "Audits every card against the complete national module and the ISCCM statement in one long context.", status: "live", href: "/how-it-works" },
  { name: "NVIDIA Nemotron Nano 12B v2 VL", role: "Offline label reading on a laptop GPU through llama.cpp, with no internet.", status: "laptop", href: "/limits" },
  { name: "Tavily", role: "Checks a brand's registered composition on Indian agrochemical sources before a card is trusted, and fetched the WHO and CIB&RC documents that block automated download.", status: "live", href: "/how-it-works" },
  { name: "Hermes Agent", role: "Runs Antidote as tools for an agent alongside Sieve.", status: "laptop", href: "https://github.com/usv240/antidote" },
  { name: "MCP", role: "Five Antidote tools any agent can call: read a label, analyse, look up a chemical, fetch a guideline page, write a register row.", status: "laptop", href: "/api" },
];

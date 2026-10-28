"use client";

import { useState } from "react";
import Link from "next/link";
import { ShieldAlert } from "lucide-react";
import { Info } from "@/components/info";

type Bottle = {
  id: string; brand: string; label: string; triangle: "red" | "yellow" | null; signal: string;
  chemical: string; group: string; who: string; status: string;
  stops: string[]; quote?: { text: string; doc: string; page: number }; antidote: boolean;
  verified: string; audit: string;
};

const TRI = { red: { fill: "var(--stop)", word: "Extremely toxic" }, yellow: { fill: "var(--caution)", word: "Highly toxic" } } as const;

/**
 * The hero's one live thing. Every line is copied from recorded live runs (data/samples/replay): the registry's
 * match, the stop cards the rules raised, and the guideline sentence the card quoted. Nothing is written for the page.
 */
const BOTTLES: Bottle[] = [
  {
    id: "paraquat", brand: "Gramoxone", label: "Paraquat dichloride 24% SL", triangle: "yellow", signal: "POISON",
    chemical: "paraquat dichloride", group: "Paraquat (bipyridyl herbicide)", who: "II", status: "restricted in India",
    stops: ["No specific antidote for Paraquat (bipyridyl herbicide). Do not give atropine for this exposure. Management is supportive per the cited guidance.", "Paraquat: avoid supplemental oxygen unless the patient is hypoxic; oxygen accelerates lung injury. See the cited guidance."],
    quote: { text: "So therefore, oxygen therapy should be avoided in Paraquat poisoning until there is evidence of hypoxia (SpO2 is dropped to < 90%).", doc: "ISCCM 2024 position statement", page: 10 },
    antidote: false, verified: "7 of 7", audit: "approved",
  },
  {
    id: "chlorpyrifos", brand: "Dursban", label: "Chlorpyrifos 20% EC", triangle: "yellow", signal: "POISON",
    chemical: "chlorpyrifos", group: "Organophosphate insecticide", who: "II", status: "restricted in India",
    stops: [], quote: { text: "Atropine, Pralidoxime – Organophosphates", doc: "NHSRC poison-management module", page: 31 },
    antidote: true, verified: "4 of 4", audit: "approved",
  },
  {
    id: "cypermethrin", brand: "Cyperkill", label: "Cypermethrin 10% EC", triangle: "yellow", signal: "POISON",
    chemical: "cypermethrin", group: "Synthetic pyrethroid insecticide", who: "II", status: "registered in India",
    stops: ["No specific antidote for Synthetic pyrethroid insecticide. Do not give atropine for this exposure. Management is supportive per the cited guidance."],
    antidote: false, verified: "4 of 4", audit: "approved",
  },
  {
    id: "celphos", brand: "Celphos", label: "Aluminium phosphide 56%", triangle: "red", signal: "POISON",
    chemical: "aluminium phosphide", group: "Metal phosphides", who: "Fumigant, listed separately", status: "restricted in India",
    stops: ["No specific antidote for Metal phosphides (aluminium phosphide, zinc phosphide). Do not give atropine for this exposure. Management is supportive per the cited guidance."],
    antidote: false, verified: "6 of 6", audit: "approved",
  },
  {
    id: "urea", brand: "IFFCO Urea", label: "Fertiliser, not a pesticide", triangle: null, signal: "",
    chemical: "urea", group: "Not a pesticide", who: "Not classified", status: "fertiliser",
    stops: [], quote: { text: "Supportive care is the mainstay of treatment.", doc: "ISCCM 2024 position statement", page: 11 },
    antidote: false, verified: "2 of 2", audit: "approved",
  },
];

export function BottleDemo() {
  const [id, setId] = useState("paraquat");
  const b = BOTTLES.find((x) => x.id === id) ?? BOTTLES[0];
  return (
    <div data-ui className="rise rounded-[24px] bg-surface p-5 sm:p-7" style={{ "--d": "200ms" } as React.CSSProperties}>
      <p id="bottle-q" className="text-base font-semibold">Which bottle came in with the patient?</p>
      <div role="radiogroup" aria-labelledby="bottle-q" className="mt-3 flex flex-wrap gap-2">
        {BOTTLES.map((x) => (
          <button key={x.id} type="button" role="radio" aria-checked={x.id === id} onClick={() => setId(x.id)}
            className={`min-h-0 rounded-full px-3.5 py-2 text-[0.9375rem] font-medium transition-[background-color,color,transform] duration-150 active:scale-[0.97] ${x.id === id ? "bg-accent text-accent-fg" : "bg-bg-elev text-fg hover:text-accent"}`}>
            {x.brand}
          </button>
        ))}
      </div>

      <div className="mt-5 flex items-center gap-4 rounded-[16px] bg-bg-elev px-5 py-4">
        <Triangle t={b.triangle} signal={b.signal} />
        <div className="min-w-0">
          <p className="text-lg font-semibold leading-snug">{b.brand}</p>
          <p className="text-[0.9375rem] text-fg-muted">{b.label}</p>
          <p className="text-[0.8125rem] text-fg-muted">{b.triangle ? `${TRI[b.triangle].word} triangle on the label` : "No toxicity triangle"}<Info k="triangle" /></p>
        </div>
      </div>

      <div key={b.id} className="swap mt-5" aria-live="polite">
        <dl className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-1 text-[0.9375rem]">
          <dt className="text-fg-muted">Chemical</dt><dd className="font-medium">{b.chemical}</dd>
          <dt className="text-fg-muted">Group</dt><dd>{b.group}</dd>
          <dt className="text-fg-muted">WHO class<Info k="who_class" /></dt><dd>{b.who}</dd>
          <dt className="text-fg-muted">Status</dt><dd>{b.status}</dd>
        </dl>
        {b.stops.map((s) => (
          <div key={s} className="mt-3 rounded-[16px] border-2 border-stop bg-bg-elev p-3.5">
            <p className="flex items-center gap-2 font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stop</p>
            <p className="mt-1 text-[0.9375rem] leading-relaxed">{s}</p>
          </div>
        ))}
        {b.quote && (
          <blockquote className="quote mt-4 text-[0.9375rem] leading-relaxed">
            {b.antidote && <span className="mb-1 block font-semibold text-ok">Antidote guidance, quoted</span>}
            &ldquo;{b.quote.text}&rdquo;
            <footer className="mt-1 text-fg-muted">{b.quote.doc}, page {b.quote.page}</footer>
          </blockquote>
        )}
        <p className="mt-4 text-[0.875rem] leading-relaxed text-fg-muted">
          Recorded live run: {b.verified} quotes verified on their pages, Nemotron 3 Ultra audit {b.audit}.{" "}
          <Link href={`/try?sample=${b.id}`} className="text-accent underline underline-offset-2">Run it live</Link>
        </p>
      </div>
    </div>
  );
}

/** The toxicity triangle printed on every Indian pesticide label (Insecticides Rules 1971, Rule 19): a diamond, signal word above, colour below. */
function Triangle({ t, signal }: { t: Bottle["triangle"]; signal: string }) {
  if (!t) return <span aria-hidden className="flex h-16 w-16 shrink-0 items-center justify-center rounded-[12px] bg-fg/10 text-[0.8125rem] text-fg-muted">none</span>;
  return (
    <svg aria-hidden viewBox="0 0 100 100" className="h-16 w-16 shrink-0">
      <polygon points="50,2 98,50 2,50" fill="#ffffff" stroke="currentColor" strokeOpacity="0.25" strokeWidth="2" />
      <polygon points="2,50 98,50 50,98" fill={TRI[t].fill} />
      <text x="50" y="42" textAnchor="middle" fontSize="13" fontWeight="700" fill="#111">{signal}</text>
    </svg>
  );
}

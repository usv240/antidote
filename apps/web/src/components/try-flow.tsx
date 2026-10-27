"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ShieldAlert, Phone, FileText } from "lucide-react";
import { apiUrl } from "@/lib/api";
import { downscaleImage } from "@/lib/image";
import { SAMPLES } from "@/lib/samples";
import { Info } from "@/components/info";

type Sentence = { kind: "quote" | "explanation"; text: string; cite: { doc: string; page: number; quote: string } | null };
type Result = {
  trace_id: string; banner: string; label: Record<string, unknown>;
  matches: { active_ingredient: string; group: string; who_class: string | null; india_status: string; confidence: number; reason: string }[];
  chosen: { active_ingredient: string; group: string; who_class: string | null; india_status: string; confidence: number } | null;
  group: { id: string; name: string; antidote_exists: boolean } | null;
  triangle: { label: string; signal: string } | null;
  guarded: boolean; stops: { rule: string; message: string; citation: string }[];
  card: { identity: Sentence[]; expect: Sentence[]; manage: Sentence[]; cautions: Sentence[]; no_antidote: boolean } | null;
  audit: { overall: string } | null; citations: { total?: number; verified?: number; tiers?: Record<string, number> };
  retrieved: { doc: string; title: string; page: number }[]; web: { results?: { title: string; url: string }[] }; notes: string[]; npic: string;
  trace: { model: string; purpose: string; tokens_in: number; tokens_out: number; usd: number }[]; latency_ms: number;
};

const CONTEXT_FIELDS: { k: string; q: string; opts: string[] }[] = [
  { k: "route", q: "Route of exposure", opts: ["ingested", "inhaled", "skin", "unknown"] },
  { k: "time_since_exposure", q: "Time since exposure", opts: ["under 1 h", "1-2 h", "2-6 h", "over 6 h", "unknown"] },
  { k: "age", q: "Patient", opts: ["adult", "child"] },
];

export function TryFlow() {
  const params = useSearchParams();
  const sample = useMemo(() => SAMPLES.find((s) => s.id === params.get("sample")), [params]);
  const [label, setLabel] = useState<Record<string, unknown>>({ product_name: "", active_ingredients: [], registration_number: "", triangle_colour: "", antidote_statement_text: "", visible_text: [] });
  const [aiText, setAiText] = useState("");
  const [ctx, setCtx] = useState<Record<string, string>>({});
  const [signs, setSigns] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [readMode, setReadMode] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);

  useEffect(() => {
    if (!sample) return;
    setLabel(sample.label);
    const ais = (sample.label.active_ingredients as { name: string; percent?: string }[] | undefined) ?? [];
    setAiText(ais.map((a) => `${a.name}${a.percent ? ` ${a.percent}%` : ""}`).join(", "));
    setCtx(sample.context); setSigns(sample.context.signs ?? ""); setResult(null);
  }, [sample]);

  async function readPhoto(file: File) {
    setBusy("Reading the label…");
    const fd = new FormData(); fd.append("image", await downscaleImage(file), "label.jpg");
    const r = await fetch(apiUrl("/v1/read-label"), { method: "POST", body: fd });
    if (!r.ok) { setReadMode(r.status === 413 ? "photo too large for the hosted API; type the label fields instead" : `label reader unavailable (${r.status})`); setBusy(null); return; }
    const j = await r.json();
    const cc = j.cross_check as { agreed?: boolean | null; first?: string | null; second?: string | null } | undefined;
    setReadMode(cc && cc.agreed === false
      ? `Two independent reads of this label disagreed (${cc.first ?? "unclear"} and ${cc.second ?? "unclear"}). Type the chemical exactly as printed on the bottle.`
      : cc && cc.agreed ? `${j.mode}; two independent reads agree` : j.mode);
    if (j.fields && Object.keys(j.fields).length) {
      setLabel(j.fields);
      const ais = (j.fields.active_ingredients as { name: string; percent?: string }[] | undefined) ?? [];
      setAiText(ais.map((a) => `${a.name}${a.percent ? ` ${a.percent}%` : ""}`).join(", "));
    }
    setBusy(null);
  }

  async function analyze(chosen?: string) {
    setBusy("Matching the registry and assembling the cited card…");
    const ais = aiText.split(",").map((s) => s.trim()).filter(Boolean).map((s) => { const m = s.match(/^(.*?)\s*(\d+(?:\.\d+)?)\s*%?$/); return m ? { name: m[1].trim(), percent: m[2] } : { name: s }; });
    const body = { label: { ...label, active_ingredients: ais }, context: { ...ctx, signs }, chosen_ai: chosen ?? null, audit: true };
    const r = await fetch(apiUrl("/v1/analyze"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    setResult(await r.json()); setBusy(null); setSaved(null);
  }

  async function save() {
    if (!result) return;
    const rec = { datetime: new Date().toISOString().slice(0, 16).replace("T", " "), alleged_history: `${String(label.product_name ?? "")} exposure, ${ctx.route ?? "route unknown"}, ${ctx.time_since_exposure ?? "time unknown"}. Signs: ${signs || "not recorded"}`, substance_product: String(label.product_name ?? ""), substance_active_ingredient: result.chosen?.active_ingredient ?? null, registration_number: String(label.registration_number ?? "") || null, who_class: result.chosen?.who_class ?? null, chemical_group: result.group?.name ?? null, banned_or_restricted: ["banned", "restricted"].includes(result.chosen?.india_status ?? ""), route: ctx.route ?? null, time_since_exposure: ctx.time_since_exposure ?? null, examination_findings: "", treatment_given: [], referral: null, doctor: null, poison_centre_called: false, ai_trace_id: result.trace_id, label_photo_attached: readMode !== null };
    const r = await fetch(apiUrl("/v1/records"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(rec) });
    const j = await r.json(); setSaved(j.id);
  }

  const S = ({ s }: { s: Sentence }) => s.kind === "quote" && s.cite ? (
    <blockquote className="quote text-sm">“{s.text}”<footer className="mt-1 text-xs text-fg-muted">{s.cite.doc}, page {s.cite.page} · <a className="text-accent" href={apiUrl(`/v1/page/${s.cite.doc}/${s.cite.page}`)} target="_blank" rel="noreferrer">Show page</a></footer></blockquote>
  ) : <p className="text-sm text-fg-muted">{s.text}</p>;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="space-y-6">
        <div className="rounded-xl border border-stop/40 bg-bg-elev px-4 py-2 text-sm"><Phone className="mr-2 inline h-4 w-4 text-stop" />Decision support for trained clinicians. Airway, breathing, circulation first. NPIC 1800-116-117. <Info k="npic" /></div>

        <section className="card space-y-3">
          <h1 className="text-2xl font-semibold">1. Read the label <Info k="registration" /></h1>
          <p className="text-sm text-fg-muted">Photograph the bottle, use a sample, or type what is printed. The vision model only reads; the registry decides.</p>
          <label className="btn-ghost cursor-pointer">Upload a label photo<input type="file" accept="image/*" className="sr-only" onChange={(e) => e.target.files?.[0] && readPhoto(e.target.files[0])} /></label>
          <p className="text-xs text-fg-muted">No bottle nearby? Download a sample label and upload it:{" "}
            <a className="text-accent underline underline-offset-2" href="/samples/sample-label-organophosphate.png" download>organophosphate</a>,{" "}
            <a className="text-accent underline underline-offset-2" href="/samples/sample-label-paraquat.png" download>paraquat</a>,{" "}
            <a className="text-accent underline underline-offset-2" href="/samples/sample-label-phosphide.png" download>phosphide</a>. These labels were made for testing and are not real products.</p>
          {readMode && (readMode.startsWith("Two independent") ? <p role="alert" className="rounded-xl border border-caution p-2 text-sm">{readMode}</p> : <p className="text-xs text-fg-muted">Read with: {readMode}</p>)}
          <div className="grid gap-3 sm:grid-cols-2">
            <L label="Product name"><input className="inp" value={String(label.product_name ?? "")} onChange={(e) => setLabel({ ...label, product_name: e.target.value })} /></L>
            <L label="Active ingredient and percent, as printed"><input className="inp" placeholder="Chlorpyriphos 20%" value={aiText} onChange={(e) => setAiText(e.target.value)} /></L>
            <L label="Registration number (CIR-…)"><input className="inp" value={String(label.registration_number ?? "")} onChange={(e) => setLabel({ ...label, registration_number: e.target.value })} /></L>
            <L label="Triangle colour"><select className="inp" value={String(label.triangle_colour ?? "")} onChange={(e) => setLabel({ ...label, triangle_colour: e.target.value })}><option value="">not visible</option><option>red</option><option>yellow</option><option>blue</option><option>green</option></select></L>
            <L label="Antidote statement as printed"><input className="inp" value={String(label.antidote_statement_text ?? "")} onChange={(e) => setLabel({ ...label, antidote_statement_text: e.target.value })} /></L>
          </div>
        </section>

        <section className="card space-y-3">
          <h2 className="text-xl font-semibold">2. Patient context <Info k="toxidrome" /></h2>
          {CONTEXT_FIELDS.map((f) => (
            <div key={f.k} className="flex flex-wrap items-center gap-2"><span className="text-sm">{f.q}</span>{f.opts.map((o) => <button key={o} onClick={() => setCtx({ ...ctx, [f.k]: o })} className={`btn-ghost min-h-0 px-3 py-1.5 text-sm ${ctx[f.k] === o ? "border-accent" : ""}`}>{o}</button>)}</div>
          ))}
          <L label="Key signs (optional)"><input className="inp" placeholder="pinpoint pupils, excess secretions, seizures…" value={signs} onChange={(e) => setSigns(e.target.value)} /></L>
          <button className="btn-primary" onClick={() => analyze()} disabled={!!busy}>Build the card</button>
          {busy && <p className="text-sm text-fg-muted" role="status">{busy}</p>}
        </section>

        {result && (
          <section className="space-y-4">
            {result.stops.map((s) => (
              <div key={s.rule} role="alert" className="rounded-[16px] border-2 border-stop bg-bg-elev p-4"><p className="flex items-center gap-2 font-semibold text-stop"><ShieldAlert className="h-5 w-5" /> Stop</p><p className="mt-1">{s.message}</p><p className="mt-1 text-xs text-fg-muted">Source: {s.citation}</p></div>
            ))}
            <div className="card space-y-3">
              <h2 className="text-xl font-semibold">3. Card: {result.chosen ? result.chosen.active_ingredient : "product not identified"}</h2>
              {result.matches.length > 1 && (
                <div className="flex flex-wrap gap-2 text-sm">
                  <span className="text-fg-muted">Other matches:</span>
                  {result.matches.slice(1, 3).map((m) => <button key={m.active_ingredient} className="btn-ghost min-h-0 px-3 py-1 text-sm" onClick={() => analyze(m.active_ingredient)}>{m.active_ingredient} ({Math.round(m.confidence * 100)}%)</button>)}
                </div>
              )}
              <div className="grid gap-2 sm:grid-cols-4 text-sm">
                <Tile l="Chemical group" v={result.group?.name ?? "unknown"} />
                <Tile l={<>WHO class <Info k="who_class" /></>} v={result.chosen?.who_class ?? "n/a"} />
                <Tile l={<>Label triangle <Info k="triangle" /></>} v={result.triangle ? `${result.triangle.label} (${result.triangle.signal})` : "not read"} />
                <Tile l="India status (CIB&RC)" v={result.chosen?.india_status ?? "unknown"} />
              </div>
              {result.guarded && <p className="text-sm text-caution">Match confidence below 75 percent: the antidote section is withheld until the product is confirmed.</p>}
              {result.card ? (
                <>
                  {(["identity", "expect", "manage", "cautions"] as const).map((sec) => (
                    <div key={sec} className="space-y-2"><p className="eyebrow">{sec === "identity" ? "What it is" : sec === "expect" ? "What to expect" : sec === "manage" ? "Management, quoted" : "Cautions, quoted"}</p>{result.card![sec].length ? result.card![sec].map((s, i) => <S key={i} s={s} />) : <p className="text-sm text-fg-muted">The indexed guidelines have no sentence on this for this chemical group.</p>}</div>
                  ))}
                  <div className="flex flex-wrap gap-3 text-xs text-fg-muted"><span>Quotes verified {result.citations.verified}/{result.citations.total}</span>{result.audit && <span>Auditor: {result.audit.overall}</span>}<span>{result.latency_ms} ms</span><a className="ml-auto text-accent underline underline-offset-2" download={`antidote-result.json`} href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(result, null, 2))}`}>Download result as JSON</a></div>
                </>
              ) : <p className="text-sm text-fg-muted">{result.notes.join(" ") || "No card (replay mode or no guideline pages)."}</p>}
            </div>
            <div className="card">
              <h3 className="font-semibold">4. Medico-legal register <Info k="mlc" /></h3>
              <p className="mt-1 text-sm text-fg-muted">Substance fields are pre-filled from the label; identifiers and findings are entered by staff in the register.</p>
              <button className="btn-primary mt-3" onClick={save}>Save register row</button>
              {saved && <p className="mt-2 text-sm text-ok">Saved. Row {saved.slice(0, 8)}. <a className="text-accent" href="/register">Open the register</a>.</p>}
            </div>
          </section>
        )}
      </div>
      <aside className="space-y-4">
        {result ? (<>
          <div className="card text-sm"><p className="font-semibold">Trace <Info k="trace" /></p><ul className="mt-1 space-y-1">{result.trace.map((t, i) => <li key={i} className="flex justify-between gap-2 text-fg-muted"><span>{t.model} · {t.purpose}</span><span>{t.tokens_in + t.tokens_out} tok · ${t.usd.toFixed(4)}</span></li>)}</ul></div>
          <div className="card text-sm"><p className="flex items-center gap-2 font-semibold"><FileText className="h-4 w-4" /> Guideline pages used</p><ul className="mt-1 space-y-1 text-fg-muted">{result.retrieved.map((r) => <li key={`${r.doc}-${r.page}`}>{r.title}, p{r.page}</li>)}</ul></div>
          {result.web?.results?.length ? <div className="card text-sm"><p className="font-semibold">Brand lookup via Tavily (unverified)</p><ul className="mt-1 space-y-1">{result.web.results.slice(0, 3).map((r) => <li key={r.url}><a className="text-accent" href={r.url} target="_blank" rel="noreferrer">{r.title}</a></li>)}</ul></div> : null}
        </>) : <div className="card text-sm text-fg-muted">The card, the Trace and the guideline pages appear here.</div>}
      </aside>
    </div>
  );
}
function L({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block text-sm"><span className="mb-1 block text-fg-muted">{label}</span>{children}</label>; }
function Tile({ l, v }: { l: React.ReactNode; v: string }) { return <div className="rounded-xl border border-border p-3"><p className="text-xs text-fg-muted">{l}</p><p className="font-medium">{v}</p></div>; }

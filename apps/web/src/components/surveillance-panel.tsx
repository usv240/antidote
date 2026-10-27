"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Download, Radar } from "lucide-react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Alert = { type: string; chemical_group: string | null; cases: number; from: string; to: string; chemicals: string[]; localities: string[]; row_ids: string[]; why: string };
type Item = { title: string; detail: string; evidence: string[] };
type Brief = { headline: string; clusters: Item[]; regulatory: Item[]; what_published_cases_teach: Item[]; actions: Item[]; confidence_note: string };
type BriefOut = { alerts: Alert[]; brief: Brief; removed_by_rules: { section: string; title: string; rules: string[] }[]; input_tokens_approx: number; case_reports_read: number; register_rows: number; latency_ms: number; trace: { model: string; tokens_in: number; usd: number }[] };

const SECTIONS: [keyof Brief, string][] = [["clusters", "Clusters"], ["regulatory", "Regulatory"], ["what_published_cases_teach", "What published cases teach"], ["actions", "Actions for the district"]];

/** The register as an early-warning signal. Alerts come from fixed rules; the brief is written by Nemotron 3.5 Lightning. */
export function SurveillancePanel() {
  const [alerts, setAlerts] = useState<{ register_rows: number; demo_rows: number; alerts: Alert[] } | null>(null);
  const [brief, setBrief] = useState<BriefOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => { fetch(apiUrl("/v1/surveillance/alerts")).then((r) => r.json()).then(setAlerts).catch(() => setErr("The API could not be reached.")); }, []);

  async function generate() {
    setBusy(true); setErr(null);
    try {
      const r = await fetch(apiUrl("/v1/surveillance/brief"), { method: "POST" });
      if (!r.ok) throw new Error(String(r.status));
      setBrief(await r.json());
    } catch (e) { setErr(`The brief could not be generated right now (${String(e)}). The alerts above are unaffected.`); }
    finally { setBusy(false); }
  }

  return (
    <section aria-labelledby="surv-h" className="card space-y-5">
      <div>
        <h2 id="surv-h" className="flex items-center gap-2 text-xl font-semibold"><Radar className="h-5 w-5 text-accent" aria-hidden /> Surveillance: is this a cluster? <Info term="Surveillance" text="In Yavatmal in 2017 about 800 farm workers were poisoned while spraying cotton, and more than 20 died, before anyone noticed it was one outbreak. Every patient was in a hospital register. Antidote reads the register for that signal: clusters of one chemical in a week, and banned chemicals still reaching patients." /></h2>
        <p className="mt-1 text-sm text-fg-muted">
          {alerts ? <>{alerts.register_rows} register rows, of which {alerts.demo_rows} are made-up demo rows so the alerts have something to find.</> : "Loading the register…"}
        </p>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Alerts <Info term="Alerts" text="Computed by fixed rules, not by a model: three or more cases of one chemical group within seven days is a cluster, and a spraying cluster when they came from skin or inhaled exposure. Any banned chemical reaching a patient is flagged. The same register always gives the same alerts." /></h3>
        {alerts?.alerts.length === 0 && <p className="text-sm text-fg-muted">No clusters or banned chemicals in the register.</p>}
        <ul className="space-y-2">
          {alerts?.alerts.map((a, i) => (
            <li key={i} className={`rounded-xl border-2 p-3 ${a.type.includes("cluster") || a.type.includes("banned") ? "border-stop" : "border-caution"}`}>
              <p className="flex items-center gap-2 font-semibold"><AlertTriangle className="h-4 w-4 shrink-0" aria-hidden /> {a.type[0].toUpperCase() + a.type.slice(1)}</p>
              <p className="mt-1 text-sm">{a.why}.</p>
              <p className="mt-1 text-xs text-fg-muted">{a.from.slice(0, 10)} to {a.to.slice(0, 10)}{a.localities.length ? ` · ${a.localities.join(", ")}` : ""} · rows {a.row_ids.join(", ")}</p>
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">District brief <Info term="District brief" text="NVIDIA Nemotron 3.5 Lightning reads the whole register, the alerts, the regulatory status of every chemical, and the full text of every published case report about those chemicals, about 200,000 tokens, in one call. It explains the alerts and suggests public-health actions. It cannot add or remove an alert, and the same safety rules that guard the bedside card remove any item that breaks them." /></h3>
        <button type="button" className="btn-primary" onClick={generate} disabled={busy}>{busy ? "Lightning is reading the register and the case reports…" : "Generate the district brief"}</button>
        {err && <p role="alert" className="text-sm text-stop">{err}</p>}
        {brief && (
          <div className="space-y-4" aria-live="polite">
            <p className="text-lg font-semibold">{brief.brief.headline}</p>
            {SECTIONS.map(([k, label]) => (brief.brief[k] as Item[]).length ? (
              <div key={k} className="space-y-1">
                <p className="text-sm font-semibold">{label}</p>
                <ul className="list-disc space-y-1 pl-5 text-sm">{(brief.brief[k] as Item[]).map((it, i) => <li key={i}><span className="font-medium">{it.title}.</span> {it.detail}</li>)}</ul>
              </div>
            ) : null)}
            {brief.removed_by_rules.length > 0 && <p className="text-xs text-fg-muted">Removed by the safety rules: {brief.removed_by_rules.map((r) => `"${r.title}" (${r.rules.join(", ")})`).join("; ")}.</p>}
            <p className="text-xs text-fg-muted">{brief.brief.confidence_note}</p>
            <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-fg-muted">
              <span>{brief.case_reports_read} published case reports read in full</span>
              <span>about {brief.input_tokens_approx.toLocaleString()} tokens</span>
              {brief.trace.map((t, i) => <span key={i}>{t.model}: {t.tokens_in.toLocaleString()} tokens in, ${t.usd.toFixed(4)}</span>)}
              <span>{(brief.latency_ms / 1000).toFixed(0)} s</span>
              <a className="ml-auto inline-flex items-center gap-1 text-accent underline underline-offset-2" download="antidote-surveillance-brief.json" href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(brief, null, 2))}`}><Download className="h-3.5 w-3.5" aria-hidden /> Download brief</a>
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

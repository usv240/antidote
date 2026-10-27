import { Info } from "@/components/info";
import { API_BASE } from "@/lib/api";
import { ApiConsole, type Preset } from "@/components/api-console";

const PRESETS: Preset[] = [
  { id: "paraquat", title: "Paraquat bottle", note: "No antidote exists: the stop card comes first, then quoted guidance. About 15 seconds.", method: "POST", path: "/v1/analyze", body: { label: { product_name: "Gramoxone", active_ingredients: [{ name: "Paraquat dichloride", percent: "24" }] }, audit: false } },
  { id: "op", title: "Organophosphate bottle", note: "Chlorpyrifos: the cholinergic toxidrome and quoted atropine guidance. About 15 seconds.", method: "POST", path: "/v1/analyze", body: { label: { product_name: "Dursban", active_ingredients: [{ name: "Chlorpyrifos", percent: "20" }] }, audit: false } },
  { id: "unreadable", title: "Unreadable label", note: "Nothing could be read: guidance is withheld, never guessed. Instant.", method: "POST", path: "/v1/analyze", body: { label: {}, audit: false } },
];

export const metadata = { title: "Antidote API" };

const curl = `curl -X POST ${API_BASE}/v1/analyze \\
  -H "content-type: application/json" \\
  -d '{"label":{"product_name":"Gramoxone","active_ingredients":[{"name":"Paraquat dichloride","percent":"24"}],"triangle_colour":"yellow"},"context":{"route":"ingested"}}'`;
const py = `import httpx
r = httpx.post("${API_BASE}/v1/analyze", json={
    "label": {"product_name": "Dursban", "active_ingredients": [{"name": "Chlorpyriphos", "percent": "20"}], "triangle_colour": "yellow"},
    "context": {"route": "ingested", "time_since_exposure": "1-2 h"},
})
card = r.json()
print(card["chosen"], card["stops"])
for s in card["card"]["manage"]:
    print(s["kind"], s["text"], s["cite"] and s["cite"]["page"])`;
const js = `const r = await fetch("${API_BASE}/v1/analyze", { method: "POST", headers: { "content-type": "application/json" },
  body: JSON.stringify({ label: { product_name: "Celphos", active_ingredients: [{ name: "Aluminium phosphide", percent: "56" }] }, context: {} }) });
const { chosen, stops, card, citations, trace } = await r.json();`;

export default function ApiPage() {
  return (
    <div className="space-y-8 pt-8">
      <div><h1 className="text-3xl font-semibold">Use Antidote as a service <Info k="mcp" /></h1><p className="mt-2 max-w-2xl text-fg-muted">The same pipeline the app uses, over HTTP. OpenAPI at <a className="text-accent" href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">{API_BASE}/docs</a>. Also an MCP server (classify_chemical, read_label_photo, analyze_label, read_guideline_page, file_mlc_record).</p></div>
      <ApiConsole presets={PRESETS} product="Antidote" />
      <div className="grid gap-4 md:grid-cols-2">
        <E m="POST" p="/v1/read-label" d="Multipart photo in; printed fields out. Nothing clinical is asked of the vision model." />
        <E m="POST" p="/v1/analyze" d="Label fields and patient context in; chemical, WHO class, stop cards, quoted card, audit, citations and Trace out." />
        <E m="GET" p="/v1/chemicals" d="The registry: chemicals, groups, WHO classes with verification status, India status." />
        <E m="GET" p="/v1/page/{doc}/{page}" d="The guideline page behind any citation." />
        <E m="POST" p="/v1/records" d="File a medico-legal register row. GET lists the demo register." />
        <E m="GET" p="/v1/evals/latest" d="The published evaluation JSON." />
        <E m="POST" p="/v1/keys" d="Create a signed API key. Shown once; nothing about it is stored on the server." />
        <E m="GET" p="/v1/keys/verify" d="Check a key and see how many requests it has left this minute." />
      </div>
      <div className="space-y-4"><Code title="curl" code={curl} /><Code title="Python" code={py} /><Code title="JavaScript" code={js} /></div>
      <div className="card text-sm text-fg-muted">Decision support for trained clinicians. Responses quote guidelines and never compute doses. Rate limited on the hosted demo.</div>
    </div>
  );
}
function E({ m, p, d }: { m: string; p: string; d: string }) { return <div className="card"><p className="font-mono text-sm"><span className="font-semibold text-accent">{m}</span> {p}</p><p className="mt-1 text-sm text-fg-muted">{d}</p></div>; }
function Code({ title, code }: { title: string; code: string }) { return <div className="card p-0"><p className="border-b border-border px-4 py-2 text-sm font-semibold">{title}</p><pre className="overflow-x-auto p-4 text-xs leading-relaxed">{code}</pre></div>; }

"use client";

import { useState } from "react";
import { apiUrl } from "@/lib/api";
import { UPLOAD_LIMIT_BYTES, UPLOAD_LIMIT_NOTE } from "@/lib/image";

export function UploadProtocol() {
  const [kind, setKind] = useState<"protocol" | "stock">("protocol");
  const [workspace, setWorkspace] = useState("demo");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ doc_id?: string; pages?: number; items?: number; note?: string; error?: string; detail?: string } | null>(null);
  async function upload(file: File) {
    if (file.size > UPLOAD_LIMIT_BYTES) { setResult({ error: UPLOAD_LIMIT_NOTE }); return; }
    setBusy(true); setResult(null);
    const fd = new FormData(); fd.append("file", file);
    try { const r = await fetch(apiUrl(`/v1/upload-protocol?kind=${kind}&workspace=${encodeURIComponent(workspace)}`), { method: "POST", body: fd }); const j = await r.json(); setResult(r.ok ? j : { error: j.detail ?? `upload failed (${r.status})` }); }
    catch { setResult({ error: "upload failed" }); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm"><span className="mb-1 block text-fg-muted">Workspace</span><input className="inp" value={workspace} onChange={(e) => setWorkspace(e.target.value)} /></label>
        <label className="block text-sm"><span className="mb-1 block text-fg-muted">What is it</span><select className="inp" value={kind} onChange={(e) => setKind(e.target.value as "protocol" | "stock")}><option value="protocol">State or hospital protocol (PDF)</option><option value="stock">Antidote stock list (CSV)</option></select></label>
      </div>
      <label className="btn-primary cursor-pointer">{busy ? "Indexing…" : kind === "stock" ? "Upload stock CSV" : "Upload protocol PDF"}<input type="file" accept={kind === "stock" ? ".csv,text/csv" : "application/pdf"} className="sr-only" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} disabled={busy} /></label>
      {result && (result.error || result.detail ? <p className="text-sm text-stop">{result.error || result.detail}</p> : <p className="text-sm text-ok">{result.doc_id ? `Indexed ${result.pages} pages as ${result.doc_id}. ${result.note ?? ""}` : `Stored ${result.items} stock items for this workspace.`}</p>)}
      {result && !(result.error || result.detail) && (
        <p className="text-sm"><a className="btn-ghost" href={`/try?sample=chlorpyrifos&workspace=${encodeURIComponent(workspace)}`}>See it on a card: an organophosphate in workspace {workspace}</a></p>
      )}
    </div>
  );
}

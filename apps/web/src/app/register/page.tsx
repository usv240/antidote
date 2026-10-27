"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";
import { SurveillancePanel } from "@/components/surveillance-panel";

type Rec = { id: string; created_at: number; datetime: string; alleged_history: string; substance_product: string | null; substance_active_ingredient: string | null; who_class: string | null; chemical_group: string | null; banned_or_restricted: boolean; route: string | null; poison_centre_called: boolean };

export default function RegisterPage() {
  const [recs, setRecs] = useState<Rec[]>([]);
  useEffect(() => { fetch(apiUrl("/v1/records")).then((r) => r.json()).then(setRecs).catch(() => {}); }, []);
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Medico-legal register <Info k="mlc" /></h1>
      <SurveillancePanel />
      <p className="max-w-2xl text-fg-muted">Demo workspace. Substance fields come from the label; patient identifiers and examination findings are entered by staff and are not stored here.</p>
      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm"><thead className="text-left text-fg-muted"><tr><th className="p-3">When</th><th className="p-3">Product</th><th className="p-3">Active ingredient</th><th className="p-3">Group</th><th className="p-3">WHO</th><th className="p-3">Route</th><th className="p-3">Flags</th></tr></thead>
          <tbody>{recs.map((r) => <tr key={r.id} className="border-t border-border"><td className="p-3 whitespace-nowrap">{r.datetime}</td><td className="p-3">{r.substance_product}</td><td className="p-3">{r.substance_active_ingredient}</td><td className="p-3">{r.chemical_group}</td><td className="p-3">{r.who_class}</td><td className="p-3">{r.route}</td><td className="p-3">{r.banned_or_restricted ? "banned/restricted" : ""}</td></tr>)}
          {recs.length === 0 && <tr><td className="p-3 text-fg-muted" colSpan={7}>No rows yet. Build a card on the Try page and save it.</td></tr>}</tbody></table>
      </div>
    </div>
  );
}

import { Info } from "@/components/info";

export const metadata = { title: "Data and bring your own" };

export default function DataPage() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Data <Info k="byo" /></h1>
      <section className="card space-y-2">
        <h2 className="font-semibold">What is indexed</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-fg-muted">
          <li>NHSRC and MoHFW poison-management module for medical officers; ISCCM 2024 position statement; NHSRC medico-legal guideline (Government of India and open-access journal material, quoted with attribution).</li>
          <li>WHO Recommended Classification of Pesticides by Hazard 2019, fetched server-side with Tavily and parsed into 649 active ingredients with source lines.</li>
          <li>CIB&RC Major Uses of Pesticides tables for insecticides and herbicides, as on 30 September 2026, fetched the same way.</li>
          <li>Insecticides Rules 1971 for the label fields every product must carry.</li>
        </ul>
      </section>
      <section className="card space-y-3">
        <h2 className="font-semibold">Bring your own data</h2>
        <p className="text-sm text-fg-muted">Three uploads make Antidote yours: the hospital antidote stock list (the card then says what is in stock here), a state or hospital protocol (cited beside the national one, labelled local), and a CSV of regional-language brand names to registration numbers. Workspace-scoped, exportable, deletable. Available once accounts are enabled on the hosted demo; locally, drop files into <code>data/corpus/</code> and run <code>make ingest</code>.</p>
        <button className="btn-ghost" disabled aria-disabled>Upload (hosted accounts coming)</button>
      </section>
    </div>
  );
}

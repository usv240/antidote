import { Info } from "@/components/info";
import { UploadProtocol } from "@/components/upload-protocol";

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
        <p className="text-sm text-fg-muted">Two uploads make Antidote yours. A stock list (CSV with a name and a quantity column): when a card gives antidote guidance, it also says whether that antidote is on your shelf, by a table lookup with no AI. A state or hospital protocol (PDF): its most relevant pages are given to the card beside the national guidance and marked as your protocol. Both apply only to cards built in your workspace; another workspace never sees them. On the hosted demo an upload lasts until the server restarts. No file to hand? <a className="text-accent underline underline-offset-2" href="/samples/sample-stock.csv" download>Download a sample stock list</a>.</p>
        <UploadProtocol />
      </section>
    </div>
  );
}

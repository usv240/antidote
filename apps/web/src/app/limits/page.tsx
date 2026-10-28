import { Info } from "@/components/info";

export const metadata = { title: "Scope and safeguards" };

export default function Limits() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Scope and safeguards</h1>
      <p className="max-w-2xl text-fg-muted">What it covers, who it is for, and the hard rules that hold whatever the model says.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <L t="Scope" v="Identifies the product and retrieves cited guidance for trained clinicians. Does not diagnose, does not compute doses, does not replace the poison-centre call." />
        <L t="Chemical groups" v="Twelve groups covering the common Indian poisonings; 140 registry chemicals, each with its WHO 2019 class and source line; 649 WHO rows parsed. A brand that is not in the registry is looked up on the web and shown as unverified with the antidote section withheld." />
        <L t="Class without a chemical" v="If only the class is known, for example a bottle that says organophosphate but no chemical name is readable, Antidote withholds antidote guidance and shows the syndromic stop: treat the toxidrome you see and call the poison centre. When the clinician records cholinergic signs, Antidote gives the cited guidance for that toxidrome; it guided both such cases in the held-out set correctly. Without those signs, guidance stays withheld." />
        <L t="Labels in regional scripts" v="The registration number and the active-ingredient percentage are printed in Latin script on every label by law, so matching works; the printed antidote statement is shown as read and may be in Hindi or a regional language." />
        <L t="Guideline coverage" v="Cards quote the NHSRC module and the ISCCM 2024 statement. Where neither names the chemical group, the card falls back to the general approach and says so." />
        <L t="Citation integrity" v="Reported per card and on the Evals page; any quote the verifier cannot find on its page is replaced by a link to the page." />
        <L t="Hosted demo" v="Shared, rate-limited; records are a demo workspace. Hospital deployments run the API on their own machine with the open models." />
      </div>
      <h2 className="text-2xl font-semibold">What Antidote refuses <Info k="stop_card" /></h2>
      <ul className="list-disc space-y-1 pl-6 text-fg-muted">
        <li>Atropine or an oxime for any chemical group other than organophosphates and carbamates.</li>
        <li>Supplemental oxygen for paraquat before hypoxia, quoted from ISCCM 2024.</li>
        <li>Induced vomiting or ipecac for any pesticide ingestion.</li>
        <li>Any dose written by the model; doses appear only as quoted spans with their page.</li>
        <li>An antidote section when the product match is below 75 percent confidence.</li>
        <li>Any pesticide guidance for a product that is not a pesticide.</li>
      </ul>
    </div>
  );
}
function L({ t, v }: { t: string; v: string }) { return <div className="card"><h2 className="font-semibold">{t}</h2><p className="mt-1 text-sm text-fg-muted">{v}</p></div>; }

import Link from "next/link";
import { Info } from "@/components/info";
import { Explain } from "@/components/explain-mode";
import { EvalTiles } from "@/components/eval-tiles";
import { SampleGallery } from "@/components/sample-gallery";
import { ShieldAlert, Camera, Search, ClipboardCheck, FileText, Phone, WifiOff } from "lucide-react";

export default function Landing() {
  return (
    <div className="space-y-20 pt-10">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-start">
        <div className="space-y-6">
          <h1 className="max-w-3xl text-balance text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            The chemical was never identified in 94 percent of cases. It was printed on the bottle in the family&apos;s hand.
          </h1>
          <p className="max-w-xl text-lg text-fg">
            In July 2013, 23 children in Bihar died after a school lunch cooked in oil kept in a pesticide container. A forensic report confirmed the poison, monocrotophos, four days later.{" "}
            <a className="text-sm text-accent underline underline-offset-2" href="https://en.wikipedia.org/wiki/Bihar_school_meal_poisoning_incident" target="_blank" rel="noreferrer">Record</a>
          </p>
          <p className="max-w-xl text-fg-muted">
            When the bottle comes with the patient, the answer should take seconds, not days. Antidote reads the label from a photo and gives the doctor the chemical, its hazard class and guidance quoted from the national module, or a stop card when no antidote exists. About 20 seconds from photo to card. Tested on 55 published poisoning cases, and every result is public, including the one card we got wrong.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/try?sample=chlorpyrifos" className="btn-primary">Try it on a sample bottle</Link>
            {process.env.NEXT_PUBLIC_VIDEO_URL ? <a href={process.env.NEXT_PUBLIC_VIDEO_URL} className="btn-ghost" target="_blank" rel="noreferrer">Watch the 3-minute video</a> : null}
          </div>
          <p className="text-sm text-fg-muted">Decision support for trained clinicians. Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117.</p>
        </div>
        <figure className="card space-y-4 lg:mt-2">
          <p className="text-lg font-semibold leading-snug">Gramoxone: paraquat dichloride 24%</p>
          <div role="note" className="rounded-xl border-2 border-stop p-3">
            <p className="font-semibold text-stop">Stop: no specific antidote</p>
            <p className="mt-1 text-sm">Do not give atropine for this exposure. Management is supportive per the cited guidance.</p>
          </div>
          <blockquote className="quote text-sm">
            &ldquo;Administration of excessive oxygen should be avoided in paraquat poisoning because it may worsen its toxicity.&rdquo;
            <footer className="mt-1 text-xs text-fg-muted">ISCCM 2024 position statement, page 10</footer>
          </blockquote>
          <figcaption className="border-t border-border pt-3 text-xs text-fg-muted">
            From a live run on the Gramoxone sample. The stop comes from the registry, not the model; every clinical sentence is the guideline&apos;s own words.{" "}
            <Link href="/try?sample=paraquat" className="text-accent underline underline-offset-2">Run it yourself</Link>
          </figcaption>
        </figure>
      </section>

      <section aria-labelledby="stakes" className="grid gap-4 sm:grid-cols-2">
        <h2 id="stakes" className="sr-only">Why it matters</h2>
        <p className="text-fg-muted"><span className="font-semibold text-fg">110,000 to 168,000</span> pesticide self-poisoning deaths a year worldwide, 14 to 20 percent of all suicides. <a className="text-sm text-accent underline underline-offset-2" href="https://files.givewell.org/files/DWDA%202009/Centre_for_Pesticide_Suicide_Prevention/Mew_et_al_2017.pdf" target="_blank" rel="noreferrer">Mew et al., 2017</a></p>
        <p className="text-fg-muted"><span className="font-semibold text-fg">50 to 90 percent</span> of paraquat patients die in Indian hospitals, and the first error is treating it like something else. <a className="text-sm text-accent underline underline-offset-2" href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12532245/" target="_blank" rel="noreferrer">Indian hospital series, 2023 to 2025</a> <Info k="paraquat" /></p>
      </section>

      <section aria-labelledby="what" className="space-y-4">
        <h2 id="what" className="text-2xl font-semibold">What is this, in one minute</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card title="What" icon={<Camera className="h-5 w-5" />}>A bedside reader for pesticide labels. Photograph the bottle; get the chemical and the cited guidance for it <Info k="quote_rule" />.</Card>
          <Card title="Why" icon={<Search className="h-5 w-5" />}>Every Indian label legally carries the chemical, a toxicity triangle <Info k="triangle" /> and an antidote statement. The registry and the guidelines are public. None of it is at the bedside at 11 pm.</Card>
          <Card title="How" icon={<ClipboardCheck className="h-5 w-5" />}>Photo, confirm the match, a card made only of quoted guideline sentences, stop cards <Info k="stop_card" /> when there is no antidote, and a filled register row <Info k="mlc" />.</Card>
        </div>
      </section>

      <section aria-labelledby="see" className="space-y-4">
        <h2 id="see" className="text-2xl font-semibold">See it work, no bottle needed</h2>
        <p className="text-fg-muted">Pick a sample. The whole flow runs live against Nebius Token Factory; the status strip says so when it is a replay instead.</p>
        <SampleGallery />
      </section>

      <section aria-labelledby="who" className="space-y-4">
        <h2 id="who" className="text-2xl font-semibold">Who it is for</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card title="The medical officer at a health centre">Gets the chemical and the cited guidance in seconds, and a stop when the common error would be lethal.</Card>
          <Card title="The casualty nurse">Knows which questions to ask the family and what to prepare before the doctor arrives.</Card>
          <Card title="The poison-centre pharmacist">Receives a complete proforma instead of &quot;a white bottle with a red triangle&quot;. <Info k="npic" /></Card>
        </div>
      </section>

      <section aria-labelledby="numbers" className="space-y-4">
        <h2 id="numbers" className="text-2xl font-semibold">The numbers <Info k="benchmark" label="Why these numbers and not others?" /></h2>
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="text-left text-fg-muted"><tr><th className="p-4">Number</th><th className="p-4">What it means</th><th className="p-4">Source</th></tr></thead>
            <tbody className="[&_td]:border-t [&_td]:border-border [&_td]:p-4 [&_td]:align-top">
              <Row n="110k to 168k" t="pesticide self-poisoning deaths per year worldwide." s="Mew et al., 2017" u="https://files.givewell.org/files/DWDA%202009/Centre_for_Pesticide_Suicide_Prevention/Mew_et_al_2017.pdf" />
              <Row n="94%" t="of recorded acute unintentional pesticide poisonings in India had the chemical recorded as unknown. An NGO analysis of government data, labelled as such." s="PAN India, 2026" u="https://pan-india.org/wp-content/uploads/2026/01/Acute-Unintentional-Pesticide-poisonings-in-India_.pdf" />
              <Row n="Better survival" t="when the pesticide type and amount were known on admission; the unknown-organophosphate group did worst." s="Scientific Reports, 2022" u="https://www.nature.com/articles/s41598-022-21054-1" />
              <Row n="50.8 to 90.5%" t="paraquat case fatality in three Indian tertiary-hospital series." s="2023 to 2025" u="https://pmc.ncbi.nlm.nih.gov/articles/PMC12532245/" />
              <Row n="25.4%" t="of 170,924 suicides in India in 2022 were by poisoning." s="NCRB ADSI 2022" u="https://www.data.gov.in/catalog/accidental-deaths-suicides-india-adsi-2022" />
              <Row n="Rule 19" t="of the Insecticides Rules 1971: every label must carry a toxicity triangle and an antidote statement." s="Government of India, 1971" u="https://nhsrcindia.org/sites/default/files/2021-05/The%20Insecticides%20rules%201971.pdf" />
            </tbody>
          </table>
        </div>
      </section>

      <section aria-labelledby="how" className="space-y-4">
        <h2 id="how" className="text-2xl font-semibold">How the AI works <Info k="tier_routing" /></h2>
        <p className="max-w-2xl text-fg-muted">Models read. Tables and rules decide.</p>
        <div className="grid gap-3 md:grid-cols-5">
          <Step n={1} title="Read" plain="Reads the label: product, chemical, percentage, registration number, triangle colour, the printed antidote statement." technical="A Token Factory image model (or NVIDIA Nemotron Nano VL on a local GPU) returns fields only; Nemotron 3 Nano normalises spellings to ISO names. Nothing clinical is asked of either." />
          <Step n={2} title="Match" plain="Looks the chemical up in the government registry." technical="Deterministic: registration number, then active ingredient and percent, then brand with a Tavily lookup whose confidence is capped at 0.6 so the antidote row stays hidden until confirmed." />
          <Step n={3} title="Look up" plain="Finds its WHO hazard class and whether an antidote exists." technical="WHO 2019 classification parsed into 458 rows with source lines; chemical groups carry antidote_exists; stop cards come from this table." />
          <Step n={4} title="Compose and check" plain="Assembles the card from quoted guideline sentences, verifies every quote on its page, blocks lethal errors, and has a larger model audit the whole card." technical="Nemotron 3 Super under a quote-only schema; exact-span verifier; YAML rules engine; Nemotron 3 Ultra audit with the national module and the ISCCM statement in context." />
          <Step n={5} title="Record" plain="Fills the medico-legal register row and the poison-centre proforma." technical="NHSRC medico-legal fields pre-filled from the label; patient identifiers and findings are entered by staff; export to PDF." />
        </div>
      </section>

      <section aria-labelledby="refuse" className="space-y-4">
        <h2 id="refuse" className="text-2xl font-semibold">What Antidote refuses <Info k="stop_card" /></h2>
        <p className="max-w-2xl text-fg-muted">These are rules that fire before the model is allowed to speak. We measured them.</p>
        <div className="grid gap-3 md:grid-cols-3">
          <Stop title="Atropine for paraquat" why="Paraquat is not an organophosphate. No antidote exists; atropine has no role." src="NHSRC module; ISCCM 2024" />
          <Stop title="Oxygen for paraquat before hypoxia" why="Oxygen accelerates lung injury. Avoided until saturation falls." src="ISCCM 2024, quoted on the card" />
          <Stop title="Antidote row for an unconfirmed product" why="Below 75 percent match confidence the antidote section is withheld: treat the patient, not the bottle." src="Antidote design rule" />
        </div>
      </section>

      <section aria-labelledby="evals" className="space-y-4">
        <h2 id="evals" className="text-2xl font-semibold">Evaluation results <Info k="negative_control" /></h2>
        <EvalTiles />
        <Link href="/evals" className="btn-ghost">See full results and how to reproduce them</Link>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <Card title={<>Bring your own data <Info k="byo" /></>} icon={<FileText className="h-5 w-5" />}>Upload your antidote stock list and your state protocol. Antidote shows what is in stock here and cites your protocol beside the national one.<div className="mt-3"><Link href="/data" className="btn-ghost">Data and uploads</Link></div></Card>
        <Card title={<>Use Antidote as a service <Info k="mcp" /></>} icon={<ClipboardCheck className="h-5 w-5" />}>Call it from your own software, or let your agent use it as a tool through MCP.<div className="mt-3"><Link href="/api" className="btn-ghost">API and code samples</Link></div></Card>
        <Card title="Works offline" icon={<WifiOff className="h-5 w-5" />}>The registry, the WHO table and the guideline pages are small enough to ship in full; an open Nemotron model on a laptop composes the card without internet.</Card>
        <Card title="Call the poison centre" icon={<Phone className="h-5 w-5" />}>Every card shows 1800-116-117 and prepares the proforma so the call takes thirty seconds.</Card>
      </section>

      <section aria-labelledby="limits" className="space-y-3">
        <h2 id="limits" className="text-2xl font-semibold">Limits, honestly</h2>
        <p className="max-w-2xl text-fg-muted">Antidote identifies the product and retrieves cited guidance for trained clinicians. It does not diagnose, does not compute doses, does not replace a poison-centre call, and no practising doctor has used it yet. Measured limits are on the Limits page.</p>
        <Link href="/limits" className="btn-ghost">Read the limits page</Link>
      </section>
    </div>
  );
}

function Card({ title, icon, children }: { title: React.ReactNode; icon?: React.ReactNode; children: React.ReactNode }) {
  return (<div className="card"><div className="flex items-center gap-2 text-fg"><span className="text-accent">{icon}</span><h3 className="font-semibold">{title}</h3></div><div className="mt-2 text-fg-muted">{children}</div></div>);
}
function Row({ n, t, s, u }: { n: string; t: string; s: string; u: string }) {
  return (<tr><td className="whitespace-nowrap font-semibold">{n}</td><td>{t}</td><td><a className="text-accent underline-offset-2 hover:underline" href={u} target="_blank" rel="noreferrer">{s}</a></td></tr>);
}
function Step({ n, title, plain, technical }: { n: number; title: string; plain: string; technical: string }) {
  return (<div className="card"><p className="eyebrow">Step {n}</p><h3 className="mt-1 font-semibold">{title}</h3><p className="mt-2 text-sm text-fg-muted"><Explain plain={plain} technical={technical} /></p></div>);
}
function Stop({ title, why, src }: { title: string; why: string; src: string }) {
  return (<div className="rounded-[16px] border-2 border-stop bg-bg-elev p-4" role="note"><div className="flex items-center gap-2 font-semibold text-stop"><ShieldAlert className="h-5 w-5" aria-hidden /> Stop: {title}</div><p className="mt-1 text-sm text-fg">{why}</p><p className="mt-1 text-xs text-fg-muted">Source: {src}</p></div>);
}

import Link from "next/link";
import Image from "next/image";
import { Info } from "@/components/info";
import { Reveal } from "@/components/reveal";
import { SampleGallery } from "@/components/sample-gallery";
import { ShieldAlert } from "lucide-react";

const d = (ms: number) => ({ "--d": `${ms}ms` }) as React.CSSProperties;

const JUMP = [
  ["#what", "What it is"],
  ["#why", "Why it matters"],
  ["#how", "How it works"],
  ["#try", "Try it"],
  ["#results", "Results"],
  ["#who", "Who it is for"],
  ["#build", "Beyond the bedside"],
];

export default function Landing() {
  return (
    <div className="pb-8">
      <Reveal />

      {/* Hero: what it is, in one sentence, with the product doing its job beside it */}
      <section className="grid gap-12 pt-20 sm:pt-14 lg:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)] lg:items-center lg:gap-16 lg:pt-16">
        <div>
          <h1 className="rise text-balance text-[2.5rem] font-semibold leading-[1.03] tracking-[-0.03em] sm:text-6xl lg:text-[4.25rem]">
            The answer is on the bottle.
          </h1>
          <p className="rise mt-6 max-w-xl text-xl leading-relaxed" style={d(90)}>
            Antidote is decision support for doctors treating pesticide poisoning. Photograph the label and get the chemical, its WHO hazard class<Info k="who_class" />, and the national guideline&apos;s own words on treatment, or a stop when no antidote exists<Info k="stop_card" />.
          </p>
          <div className="rise mt-8 flex flex-wrap gap-3" style={d(180)}>
            <Link href="/try?sample=chlorpyrifos" className="btn-primary">Try it on a sample bottle</Link>
            <a href="#how" className="btn-ghost">See how it works</a>
            {process.env.NEXT_PUBLIC_VIDEO_URL ? <a href={process.env.NEXT_PUBLIC_VIDEO_URL} className="btn-ghost" target="_blank" rel="noreferrer">Watch the 3-minute video</a> : null}
          </div>
          <p className="rise mt-8 max-w-xl text-base leading-relaxed text-fg-muted" style={d(260)}>
            In 94 percent of recorded pesticide poisonings in India, the chemical went unidentified{" "}
            (<a className="text-accent underline underline-offset-2" href="https://pan-india.org/wp-content/uploads/2026/01/Acute-Unintentional-Pesticide-poisonings-in-India_.pdf" target="_blank" rel="noreferrer">PAN India, 2026</a>). In 2013, 23 children in Bihar died after a school meal; the poison, monocrotophos, was confirmed four days later{" "}
            (<a className="text-accent underline underline-offset-2" href="https://en.wikipedia.org/wiki/Bihar_school_meal_poisoning_incident" target="_blank" rel="noreferrer">record</a>).
          </p>
          <p className="rise mt-4 max-w-xl text-[0.9375rem] leading-relaxed text-fg-muted" style={d(300)}>
            Decision support for trained clinicians. Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117<Info k="npic" />
          </p>
        </div>

        <figure data-ui className="rise rounded-[24px] bg-surface p-6 sm:p-8" style={d(200)}>
          <p className="text-[0.9375rem] text-fg-muted">Label read from a photo</p>
          <p className="mt-2 text-2xl font-semibold leading-snug tracking-[-0.01em]">Gramoxone: paraquat dichloride 24%</p>
          <div role="note" className="mt-5 rounded-[16px] border-2 border-stop bg-bg-elev p-4">
            <p className="flex items-center gap-2 text-lg font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stop: no specific antidote</p>
            <p className="mt-1.5 text-base leading-relaxed">Do not give atropine for this exposure. Management is supportive per the cited guidance.</p>
          </div>
          <blockquote className="quote mt-5 text-base leading-relaxed">
            &ldquo;Administration of excessive oxygen should be avoided in paraquat poisoning because it may worsen its toxicity.&rdquo;
            <footer className="mt-2 text-[0.9375rem] text-fg-muted">ISCCM 2024 position statement, page 10</footer>
          </blockquote>
          <figcaption className="mt-6 text-[0.9375rem] leading-relaxed text-fg-muted">
            From a live run. The stop comes from the registry, not the model; every clinical sentence is the guideline&apos;s own words.{" "}
            <Link href="/try?sample=paraquat" className="text-accent underline underline-offset-2">Run it yourself</Link>
          </figcaption>
        </figure>
      </section>

      <nav aria-label="On this page" className="rise mt-14 flex flex-wrap gap-2" style={d(340)}>
        {JUMP.map(([href, label]) => (
          <a key={href} href={href} className="lift rounded-full bg-surface px-4 py-2 text-[0.9375rem] text-fg-muted hover:text-fg">{label}</a>
        ))}
      </nav>

      {/* What, why, how in one minute */}
      <section id="what" aria-labelledby="what-h" className="scroll-mt-32 pt-28">
        <h2 id="what-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Antidote in one minute</h2>
        <div className="mt-10 grid gap-10 md:grid-cols-3 md:gap-12">
          <div data-reveal style={d(60)}>
            <h3 className="text-xl font-semibold">What it is</h3>
            <p className="mt-3 text-lg leading-relaxed">A bedside card for the doctor in casualty. The family brings the bottle; one photo of the label gives the chemical, how dangerous it is, and the treatment quoted word for word from India&apos;s national guidelines, each sentence with its page<Info k="quote_rule" />.</p>
          </div>
          <div data-reveal style={d(140)}>
            <h3 className="text-xl font-semibold">Why it matters</h3>
            <p className="mt-3 text-lg leading-relaxed">Pesticides look alike in an emergency, but their treatments are opposites. Atropine saves an organophosphate patient<Info k="organophosphate" /> and has no role in paraquat<Info k="paraquat" />, where extra oxygen can make things worse. Every Indian label legally carries the answer.</p>
          </div>
          <div data-reveal style={d(220)}>
            <h3 className="text-xl font-semibold">How it works</h3>
            <p className="mt-3 text-lg leading-relaxed">Open NVIDIA Nemotron models on Nebius Token Factory read the label and assemble the card. A government registry, not the model, decides whether an antidote exists; fixed rules block lethal errors, and a larger model audits every card against both guidelines in full.</p>
          </div>
        </div>
      </section>

      {/* Why: the evidence, with a real bottle */}
      <section id="why" aria-labelledby="why-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] lg:gap-16">
          <figure data-reveal>
            <Image src="/images/paraquat-label.jpg" alt="A large grey paraquat container on a shop shelf; its label lists the active ingredient at 24 percent beside skull-and-crossbones warnings" width={1300} height={1224} sizes="(min-width: 1024px) 440px, 100vw" className="h-auto w-full rounded-[20px] object-cover" />
            <figcaption className="mt-3 text-[0.9375rem] text-fg-muted">A paraquat container on a shop shelf in Changhua, Taiwan. The label prints the chemical, 1,1&apos;-dimethyl-4,4&apos;-bipyridylium dichloride, at 24 percent.</figcaption>
          </figure>
          <div>
            <h2 id="why-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Why it matters</h2>
            <div data-reveal style={d(80)} className="mt-8">
              <p className="text-7xl font-semibold tracking-[-0.04em] text-accent sm:text-8xl">70%</p>
              <p className="mt-3 max-w-xl text-xl leading-relaxed">is about the case fatality for paraquat and for aluminium phosphide, against close to 0 percent for many newer pesticides. The product decides the outcome, and WHO tells families to bring the bottle. <a className="text-accent underline underline-offset-2" href="https://iris.who.int/handle/10665/44020" target="_blank" rel="noreferrer">WHO, 2008</a></p>
            </div>
            <blockquote data-reveal style={d(140)} className="quote mt-10 max-w-xl text-lg leading-relaxed">
              Paraquat was diagnosed by &ldquo;physical verification of the container of the poison or by the pictures of the container on WhatsApp shared by the patient&apos;s relatives&rdquo;; before referral, many had been given atropine, pralidoxime and oxygen.
              <footer className="mt-2 text-[0.9375rem] text-fg-muted"><a className="text-accent underline underline-offset-2" href="https://nmji.in/reasons-for-under-reporting-of-paraquat-poisoning-in-india/" target="_blank" rel="noreferrer">Dambal et al., National Medical Journal of India, 2021</a></footer>
            </blockquote>
            <ul className="mt-12 grid gap-x-8 gap-y-14 sm:grid-cols-3">
              <Stat i={100} n="31.8%" t="of patients in a Bangladesh hospital series were misdiagnosed from their symptoms alone." s="Verma, Eddleston et al., 2024" u="https://pmc.ncbi.nlm.nih.gov/articles/PMC11149373/" />
              <Stat i={160} n="18 of 318" t="pesticides registered in India in 2019 were rated extremely or highly hazardous by WHO." s="Bonvoisin et al., 2020" u="https://link.springer.com/article/10.1186/s12889-020-8339-z" />
              <Stat i={220} n="110,000+" t="pesticide self-poisoning deaths a year worldwide." s="Mew et al., 2017" u="https://files.givewell.org/files/DWDA%202009/Centre_for_Pesticide_Suicide_Prevention/Mew_et_al_2017.pdf" />
            </ul>
            <p className="mt-10 text-base"><Link href="/references" className="font-semibold text-accent underline underline-offset-4">All 20 sources behind the numbers on this site</Link></p>
          </div>
        </div>
      </section>

      {/* How: the five stages, and which model does what */}
      <section id="how" aria-labelledby="how-h" className="scroll-mt-32 pt-36">
        <h2 id="how-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">How it works<Info k="tier_routing" /></h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-xl leading-relaxed">Models read and draft. A registry, rules and a verifier decide what reaches the doctor.</p>
        <div className="mt-12 grid gap-14 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-16">
          <ol className="space-y-9">
            <Stage i={0} title="Read the label" text="Reads the product, the chemical and its percentage, the toxicity triangle and the printed antidote statement from one photo." model="NVIDIA Nemotron 3.5 Super VL and a second reader" tech="The chemical is used only when two different vision models agree and the name appears in the text actually read; otherwise it is left blank for the doctor to confirm from the bottle." />
            <Stage i={1} title="Match the registry" text="Looks the chemical up among 140 chemicals in the registry, each with its WHO 2019 hazard class and source line." model="Registry lookup, with a Tavily brand check" tech="Deterministic matching; when the brand is unfamiliar, Tavily searches registry and retailer pages for its registered composition, and Antidote acts only on a clear winner." />
            <Stage i={2} title="Decide: antidote or stop" text="The registry, not a model, decides whether an antidote exists. Paraquat and phosphides get the stop card first." model="Chemical-group table" tech="Below 75 percent match confidence the antidote section is withheld: treat the patient, not the bottle." />
            <Stage i={3} title="Compose and audit the card" text="Builds the card only from numbered sentences of the national module and the ISCCM 2024 statement, then audits it against both in full." model="NVIDIA Nemotron 3 Super, audited by Nemotron 3 Ultra" tech="Code copies each cited sentence word for word; explanation sentences may carry no drug names or numbers; rules remove any sentence that names atropine or an oxime for a group without an antidote." />
            <Stage i={4} title="Record and watch" text="Fills the medico-legal register row from the label, and turns the register into a district early warning." model="NVIDIA Nemotron 3.5 Lightning for the district brief" tech="Rules flag spraying clusters, banned chemicals and restricted products; Lightning reads the register plus 32 full case reports, about 194,000 tokens, to explain them." />
          </ol>
          <div data-reveal style={d(120)}>
            <div className="rounded-[20px] bg-surface p-5 sm:p-6">
              <h3 className="text-lg font-semibold">Which model does what<Info term="Model routing" text="Each job goes to the smallest model that does it well. Every call, with its tokens and cost, is shown in the Trace panel beside the card." /></h3>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-[0.9375rem]">
                  <thead className="text-left text-fg-muted"><tr><th className="py-2 pr-3 font-medium">Job</th><th className="py-2 pr-3 font-medium">Model</th><th className="py-2 font-medium">Runs on</th></tr></thead>
                  <tbody className="[&_td]:py-2.5 [&_td]:pr-3 [&_td]:align-top">
                    <tr><td>Read the label</td><td>Nemotron 3.5 Super VL, plus a second reader</td><td>Token Factory</td></tr>
                    <tr><td>Tidy the label text</td><td>Nemotron 3 Nano</td><td>Token Factory</td></tr>
                    <tr><td>Check an unknown brand</td><td>Tavily search</td><td>Tavily</td></tr>
                    <tr><td>Compose the card</td><td>Nemotron 3 Super</td><td>Token Factory</td></tr>
                    <tr><td>Audit against both guidelines</td><td>Nemotron 3 Ultra, 1M-token context</td><td>Token Factory</td></tr>
                    <tr><td>District surveillance brief</td><td>Nemotron 3.5 Lightning</td><td>Token Factory</td></tr>
                    <tr><td>Read labels with no internet</td><td>Nemotron Nano 12B v2 VL</td><td>Laptop GPU</td></tr>
                    <tr><td>Verification job, vision endpoint</td><td>Nemotron Nano 12B v2 VL</td><td>Nebius Serverless</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <Link href="/how-it-works" className="btn-ghost mt-5">The full pipeline, step by step</Link>
          </div>
        </div>
      </section>

      {/* Try */}
      <section id="try" aria-labelledby="try-h" className="scroll-mt-32 pt-36">
        <h2 id="try-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Try it, no bottle needed</h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-lg leading-relaxed">Pick a label. Each sample runs the real pipeline live on Nebius Token Factory, from reading the label to the register row. One is not a pesticide at all, to test that Antidote keeps antidotes away from it.</p>
        <div data-reveal style={d(120)} className="mt-10"><SampleGallery /></div>
      </section>

      {/* Safety */}
      <section id="safety" aria-labelledby="safety-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:gap-16">
          <div data-reveal>
            <h2 id="safety-h" className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">What Antidote refuses<Info k="stop_card" /></h2>
            <p className="mt-4 text-lg leading-relaxed">These are rules, not suggestions a model may ignore. They fire before the model is allowed to speak, and every one is tested on each evaluation run.</p>
            <div data-ui role="note" aria-label="Example: the stops a doctor sees for paraquat" className="mt-8 rounded-[20px] bg-surface p-5 sm:p-6">
              <p className="text-[0.9375rem] text-fg-muted">What the doctor sees first for a paraquat label</p>
              <div className="mt-3 space-y-3">
                <div className="rounded-[16px] border-2 border-stop bg-bg-elev p-4">
                  <p className="flex items-center gap-2 text-lg font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stop</p>
                  <p className="mt-1.5 text-base leading-relaxed">No specific antidote for Paraquat (bipyridyl herbicide). Do not give atropine for this exposure. Management is supportive per the cited guidance.</p>
                </div>
                <div className="rounded-[16px] border-2 border-stop bg-bg-elev p-4">
                  <p className="flex items-center gap-2 text-lg font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stop</p>
                  <p className="mt-1.5 text-base leading-relaxed">Paraquat: avoid supplemental oxygen unless the patient is hypoxic; oxygen accelerates lung injury. See the cited guidance.</p>
                </div>
              </div>
            </div>
            <Link href="/limits" className="btn-ghost mt-6">Scope and safeguards</Link>
          </div>
          <ul className="space-y-4">
            <Stop i={0} title="Atropine for paraquat, pyrethroids or phosphides" why="Atropine or an oxime is offered only for organophosphates and carbamates." />
            <Stop i={1} title="Oxygen for paraquat before hypoxia" why="Supplemental oxygen accelerates paraquat lung injury; avoided until saturation falls." />
            <Stop i={2} title="Any dose written by the model" why="Doses appear only inside quoted guideline sentences, with their page." />
            <Stop i={3} title="An antidote for an unconfirmed product" why="Below 75 percent match confidence the antidote section is withheld until the doctor confirms the bottle." />
            <Stop i={4} title="Induced vomiting for any pesticide" why="No ipecac and no induced vomiting for a pesticide ingestion." />
            <Stop i={5} title="Pesticide guidance for something that is not one" why="Fertilisers, cleaners and medicines are routed to the general approach, never to a pesticide antidote." />
          </ul>
        </div>
      </section>

      {/* Results */}
      <section id="results" aria-labelledby="results-h" className="scroll-mt-32 pt-36">
        <h2 id="results-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Results<Info k="benchmark" /></h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-lg leading-relaxed">Tested on what treating doctors have already published, on real label photos, and against a general model asked directly.</p>
        <div className="mt-12 grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <Result i={0} n="0 of 123" t="cards that would point a doctor the wrong way, across 55 published poisoning cases and 68 real label photos." info="Open-access case reports written by the treating doctors, ground truth taken from each paper, plus 68 photos of real Indian pesticide labels annotated before any run. Measured on the code that is live today." />
          <Result i={1} n="10 of 12" t="cases where the treating team first mistook the poison that Antidote would have set right." info="Cases where the published paper documents a misidentification or a wrong first treatment, usually a non-organophosphate treated as one." />
          <Result i={2} n="107 vs 0" t="drug doses with no source: a general model asked directly, against Antidote." info="Nemotron 3 Super asked the same 55 questions with the chemical name typed in for it. Every clinical sentence on an Antidote card is a guideline's own words with its page." />
          <Result i={3} n="10 of 10" t="lethal-error sentences, such as atropine for paraquat, blocked by the rules alone." info="Negative controls run on every evaluation, with no model involved, so they hold offline too." />
        </div>
        <Link href="/evals" className="btn-ghost mt-10">All results and how to reproduce them</Link>
      </section>

      {/* Who */}
      <section id="who" aria-labelledby="who-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center lg:gap-16">
          <figure data-reveal className="order-last lg:order-none">
            <Image src="/images/sprayer.jpg" alt="A farmer pours liquid from a blue jug into a green backpack sprayer beside a field" width={1600} height={1067} sizes="(min-width: 1024px) 500px, 100vw" className="h-auto w-full rounded-[20px] object-cover" />
            <figcaption className="mt-3 text-[0.9375rem] text-fg-muted">Mixing a herbicide into a backpack sprayer.</figcaption>
          </figure>
          <div>
            <h2 id="who-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Who it is for</h2>
            <div className="mt-8 space-y-8">
              <Persona i={0} title="The medical officer at a health centre" text="Gets the chemical and the cited guidance in seconds, and a stop when the common error would be lethal." />
              <Persona i={1} title="The casualty nurse" text="Knows which questions to ask the family and what to prepare before the doctor arrives." />
              <Persona i={2} title="The poison-centre pharmacist" text="Hears the product, chemical, registration number and hazard class read off the label, instead of a white bottle with a red triangle." />
            </div>
          </div>
        </div>
      </section>

      {/* Beyond the bedside */}
      <section id="build" aria-labelledby="build-h" className="scroll-mt-32 pt-36">
        <h2 id="build-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Beyond the bedside</h2>
        <div className="mt-10 grid gap-x-12 gap-y-10 md:grid-cols-2">
          <Feature i={0} title="District early warning" term="District surveillance" info="Rules flag a spraying cluster, a banned chemical still in circulation and restricted products; NVIDIA Nemotron 3.5 Lightning reads the whole register and the published case reports to write the brief." text="The register becomes a signal: clusters of spraying poisonings and banned chemicals still in circulation, explained in a brief for the district officer." href="/register" cta="See the register and the brief" />
          <Feature i={1} title="Bring your own data" k="byo" text="Upload your antidote stock list and your state protocol. The card then says whether the antidote is on your shelf, and draws on your protocol beside the national one." href="/data" cta="Data and uploads" />
          <Feature i={2} title="An API and an agent tool" k="mcp" text="Create a key and call Antidote from your own software, or let an agent use its seven tools through MCP and Hermes Agent." href="/api" cta="Get an API key" />
          <Feature i={3} title="The poison centre, one tap away" k="npic" text="Every card shows 1800-116-117, and the register row filled from the label holds what the poison centre will ask: product, chemical, registration number and hazard class." href="/try?sample=paraquat" cta="See a card" />
        </div>
      </section>
    </div>
  );
}

function Stat({ n, t, s, u, i }: { n: string; t: string; s: string; u: string; i: number }) {
  return (
    <li data-reveal style={d(i)}>
      <p className="text-4xl font-semibold tracking-[-0.03em]">{n}</p>
      <p className="mt-2 text-base leading-relaxed">{t} <a className="text-accent underline underline-offset-2" href={u} target="_blank" rel="noreferrer">{s}</a></p>
    </li>
  );
}

function Stage({ i, title, text, model, tech }: { i: number; title: string; text: string; model: string; tech: string }) {
  return (
    <li data-reveal style={d(60 + i * 70)} className="grid grid-cols-[2.25rem_minmax(0,1fr)] gap-4">
      <span aria-hidden className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-base font-semibold text-accent-fg">{i + 1}</span>
      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="mt-2 text-base leading-relaxed">{text}</p>
        <p className="mt-2 flex flex-wrap items-center gap-1 text-[0.9375rem] text-fg-muted">{model}<Info term={title} text={tech} /></p>
      </div>
    </li>
  );
}

function Stop({ i, title, why }: { i: number; title: string; why: string }) {
  return (
    <li data-reveal style={d(i * 60)} className="rounded-[18px] bg-stop/10 p-5">
      <p className="text-lg font-semibold text-stop">{title}</p>
      <p className="mt-1.5 text-base leading-relaxed">{why}</p>
    </li>
  );
}

function Result({ i, n, t, info }: { i: number; n: string; t: string; info: string }) {
  return (
    <div data-reveal style={d(i * 80)}>
      <p className="text-5xl font-semibold tracking-[-0.035em] text-accent">{n}</p>
      <p className="mt-3 text-base leading-relaxed">{t}<Info term={n} text={info} /></p>
    </div>
  );
}

function Persona({ i, title, text }: { i: number; title: string; text: string }) {
  return (
    <div data-reveal style={d(i * 80)}>
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="mt-2 text-lg leading-relaxed">{text}</p>
    </div>
  );
}

function Feature({ i, title, k, term, info, text, href, cta }: { i: number; title: string; k?: Parameters<typeof Info>[0]["k"]; term?: string; info?: string; text: string; href: string; cta: string }) {
  return (
    <div data-reveal style={d(i * 70)}>
      <h3 className="text-xl font-semibold">{title}{k ? <Info k={k} /> : <Info term={term} text={info} />}</h3>
      <p className="mt-2 text-lg leading-relaxed">{text}</p>
      <Link href={href} className="mt-3 inline-block text-base font-semibold text-accent underline underline-offset-4">{cta}</Link>
    </div>
  );
}

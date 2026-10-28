export const metadata = { title: "About" };

export default function About() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">About Antidote</h1>
      <p className="max-w-2xl text-fg-muted">Built for the Nebius x NVIDIA Global AI Hackathon, October 2026, by a one-person code team. Apache-2.0. Source at <a className="text-accent underline underline-offset-2" href="https://github.com/usv240/antidote">github.com/usv240/antidote</a>.</p>
      <section className="card space-y-2">
        <h2 className="font-semibold">Prior art, named</h2>
        <p className="text-sm text-fg-muted">webPOISONCONTROL triages consumers in the United States from barcodes. SprayWise, a student hackathon project, reads labels for farmers&apos; harvest intervals. Poison-information centres and textbooks hold the knowledge. Nothing reads the bottle for the doctor at the bedside, matches it to the Indian registry and the WHO class, assembles guidance from quoted sentences only, stops on the lethal errors, and fills the medico-legal register.</p>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Where the models run</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-fg-muted">
          <li>Nebius Token Factory: Nemotron 3 Nano (label normalisation), Nemotron 3 Super (card composition from quotes), Nemotron 3 Ultra (audit with the national module and ISCCM statement in a 1M context), plus an image model for label reading.</li>
          <li>Laptop GPU: NVIDIA Nemotron Nano 12B v2 VL via llama.cpp as the NVIDIA vision path; an open Nemotron model for offline composition.</li>
          <li>Tavily: brand-name resolution when the registry has no row, and server-side extraction of the WHO classification and the CIB&RC tables that block automated downloads.</li>
          <li>MCP server with five tools; the same platform as Sieve, our other entry, with a different domain, practitioner, corpus and record.</li>
        </ul>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Validated against real-world evidence</h2>
        <p className="text-sm text-fg-muted">Antidote is checked against what treating doctors have already published: 55 open-access poisoning case reports, each run through Antidote and compared with the authors&apos; own management by two independent judges, and 68 photos of real Indian pesticide labels. Its clinical text comes only from the NHSRC poison-management module and the ISCCM 2024 position statement, quoted word for word with the page. Every result is on the Evals page.</p>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Feedback on the tools</h2>
        <p className="text-sm text-fg-muted">Kept as a running log in the repository (FEEDBACK.md).</p>
      </section>
    </div>
  );
}

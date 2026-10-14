export const metadata = { title: "References" };

const refs = [
  ["Mew EJ et al. The global burden of fatal self-poisoning with pesticides 2006-15: systematic review. J Affect Disord 2017.", "https://files.givewell.org/files/DWDA%202009/Centre_for_Pesticide_Suicide_Prevention/Mew_et_al_2017.pdf"],
  ["PAN India. Acute unintentional pesticide poisonings in India, January 2026 (NGO analysis of government data).", "https://pan-india.org/wp-content/uploads/2026/01/Acute-Unintentional-Pesticide-poisonings-in-India_.pdf"],
  ["Clinical profile and outcome of organophosphate poisoning, Osmania General Hospital. Scientific Reports 2022.", "https://www.nature.com/articles/s41598-022-21054-1"],
  ["Paraquat poisoning case fatality, Indian tertiary-hospital series 2023 to 2025.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12532245/"],
  ["NCRB. Accidental Deaths and Suicides in India 2022.", "https://www.data.gov.in/catalog/accidental-deaths-suicides-india-adsi-2022"],
  ["Insecticides Rules 1971, Rule 19 (labelling).", "https://nhsrcindia.org/sites/default/files/2021-05/The%20Insecticides%20rules%201971.pdf"],
  ["WHO. Recommended Classification of Pesticides by Hazard and Guidelines to Classification, 2019 edition.", "https://iris.who.int/handle/10665/332193"],
  ["CIB&RC. Registered products and Major Uses of Pesticides (as on 30.09.2026).", "https://ppqs.gov.in/divisions/cib-rc/major-uses-of-pesticides"],
  ["NHSRC and MoHFW. Emergency Care for MO: General Approach to Poison Management.", "https://nhsrcindia.org/sites/default/files/2022-11/Emergency%20Care%20for%20MO-%20General%20Approach%20to%20Poison%20Management.pdf"],
  ["ISCCM. Position statement on acute poisoning, Indian J Crit Care Med 2024.", "https://www.ijccm.org/doi/pdf/10.5005/jp-journals-10071-24697"],
  ["NHSRC. Medico-legal guideline.", "https://qi.nhsrcindia.org/sites/default/files/medico_legal.pdf"],
  ["Prior art: webPOISONCONTROL (US consumer barcode triage).", "https://www.webpoisoncontrol.org/"],
  ["Prior art: SprayWise (student hackathon label reader for farmers).", "https://github.com/bhaveshgandhi03/spraywise"],
];

export default function References() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">References</h1>
      <p className="max-w-2xl text-fg-muted">Every statistic on this site links here. The retracted 2020 estimate of 385 million poisonings is deliberately not used.</p>
      <ol className="list-decimal space-y-2 pl-6">{refs.map(([t, u]) => <li key={u}><a className="text-accent underline-offset-2 hover:underline" href={u} target="_blank" rel="noreferrer">{t}</a></li>)}</ol>
    </div>
  );
}

import { StackStrip } from "@/components/stack-strip";

export function SiteFooter() {
  return (
    <footer className="bg-surface">
      <div className="mx-auto max-w-[1100px] px-4 pt-8 sm:px-6"><StackStrip compact /></div>
      <div className="mx-auto max-w-[1100px] px-4 pt-6 text-[0.875rem] text-fg-muted sm:px-6">
        <p className="max-w-3xl leading-relaxed">Photographs, cropped: <a className="underline underline-offset-2 hover:text-fg" href="https://commons.wikimedia.org/wiki/File:Bottle_of_Paraquat_as_pesticide,_at_Changhua_20110829.jpg" target="_blank" rel="noreferrer">Bottle of Paraquat as pesticide, at Changhua</a> by Lordcolus, <a className="underline underline-offset-2 hover:text-fg" href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noreferrer">CC BY 2.0</a>; <a className="underline underline-offset-2 hover:text-fg" href="https://commons.wikimedia.org/wiki/File:A_farmer_mixing_water_with_spraying_chemical_(herbicide)_06.jpg" target="_blank" rel="noreferrer">A farmer mixing water with spraying chemical</a> by Danjuma Anthony, <a className="underline underline-offset-2 hover:text-fg" href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a>. Both via Wikimedia Commons.</p>
      </div>
      <div className="mx-auto flex max-w-[1100px] flex-col gap-3 px-4 pb-8 pt-6 text-sm text-fg-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>Built on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super, Ultra, 3.5 Lightning and 3.5 Super VL. Apache-2.0.</p>
        <nav aria-label="Footer" className="flex flex-wrap gap-4">
          <a className="hover:text-fg" href="https://github.com/usv240/antidote" target="_blank" rel="noreferrer">GitHub</a>
          <a className="hover:text-fg" href="/references">References</a>
          <a className="hover:text-fg" href="/about">About and feedback</a>
        </nav>
      </div>
    </footer>
  );
}

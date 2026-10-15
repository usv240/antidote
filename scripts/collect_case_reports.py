"""Collect published pesticide-poisoning case reports for the case-report benchmark.

Tavily search finds open-access case reports; Tavily extract fetches their text server-side. Raw text stays in
data/corpus/case_reports/ (gitignored). The manifest of URLs is written to data/external/case_reports_manifest.json.

Run: python scripts/collect_case_reports.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from tavily import TavilyClient

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/corpus/case_reports"
MANIFEST = ROOT / "data/external/case_reports_manifest.json"
MANIFEST_V2 = ROOT / "data/external/case_reports_manifest_v2.json"

# Held-out set 2: different queries; any URL already in set 1 is skipped.
QUERIES_V2 = [
    "organophosphorus poisoning case report atropine pralidoxime ICU",
    "unknown insecticide poisoning case report cholinergic",
    "organophosphate compound poisoning case report India rural",
    "carbamate insecticide poisoning case report",
    "quinalphos poisoning case report",
    "profenofos poisoning case report",
    "phorate poisoning case report",
    "methomyl poisoning case report",
    "celphos aluminium phosphide case report survival",
    "paraquat ingestion case report survival India",
    "rodenticide superwarfarin poisoning case report",
    "lambda cyhalothrin poisoning case report",
    "acetamiprid poisoning case report",
    "glufosinate poisoning case report",
    "dichlorvos inhalation poisoning case report",
]

QUERIES = [
    "paraquat poisoning case report India",
    "aluminium phosphide poisoning case report India",
    "zinc phosphide poisoning case report India",
    "chlorpyrifos poisoning case report India",
    "monocrotophos poisoning case report India",
    "dichlorvos poisoning case report India",
    "organophosphate poisoning intermediate syndrome case report India",
    "carbofuran carbamate poisoning case report India",
    "cypermethrin pyrethroid poisoning case report India",
    "glyphosate surfactant herbicide poisoning case report India",
    "bromadiolone rodenticide poisoning case report India",
    "imidacloprid neonicotinoid poisoning case report India",
    "endosulfan poisoning case report India",
    "2,4-D herbicide poisoning case report India",
    "fipronil poisoning case report India",
    "chlorfenapyr poisoning case report India",
    "diquat poisoning case report India",
    "emamectin benzoate poisoning case report India",
    "pesticide poisoning misdiagnosed as organophosphate case report",
    "paraquat poisoning treated with atropine case report",
]
DOMAINS = ["ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "cureus.com", "jfmpc.com", "ijccm.org", "japi.org", "journals.lww.com", "bmj.com", "europepmc.org"]
CASE_HINT = re.compile(r"case report|a case of|case presentation|we report|we present", re.IGNORECASE)


def main(held_out: bool = False) -> None:
    c = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    RAW.mkdir(parents=True, exist_ok=True)
    seen: dict[str, dict] = {}
    exclude: set[str] = set()
    if held_out:
        exclude = {m["url"] for m in json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]}
    elif MANIFEST.exists():
        for m in json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]:
            seen[m["url"]] = m
    for q in (QUERIES_V2 if held_out else QUERIES):
        r = c.search(q, max_results=6, include_domains=DOMAINS)
        for x in r.get("results", []):
            url = x.get("url") or ""
            title = x.get("title") or ""
            if url in seen or url in exclude or not CASE_HINT.search(title + " " + (x.get("content") or "")):
                continue
            seen[url] = {"url": url, "title": title, "query": q, "file": None}
        print(f"{q[:60]:60s} total candidates {len(seen)}", flush=True)
    todo = [m for m in seen.values() if not m.get("file")]
    for i in range(0, len(todo), 10):
        batch = todo[i : i + 10]
        try:
            ex = c.extract(urls=[m["url"] for m in batch])
        except Exception as e:  # noqa: BLE001
            print("extract failed", type(e).__name__)
            continue
        for res in ex.get("results", []):
            text = res.get("raw_content") or ""
            if len(text) < 1500:
                continue
            name = hashlib.sha1(res["url"].encode()).hexdigest()[:12] + ".txt"
            (RAW / name).write_text(text, encoding="utf-8")
            seen[res["url"]]["file"] = name
            seen[res["url"]]["chars"] = len(text)
    items = sorted(seen.values(), key=lambda m: m["url"])
    (MANIFEST_V2 if held_out else MANIFEST).write_text(json.dumps({"source": "Tavily search + extract, open-access case reports", "held_out": held_out, "items": items}, indent=1), encoding="utf-8")
    print("candidates", len(items), "with text", sum(1 for m in items if m.get("file")))


if __name__ == "__main__":
    import sys

    main(held_out="--held-out" in sys.argv)

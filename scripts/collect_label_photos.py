"""Collect real-world photos of Indian pesticide container labels for the label-reading benchmark.

Tavily search with include_images returns image URLs from resale listings, refurbishers and product pages. Images are
fetched, decoded with Pillow (nothing else is ever opened or executed), re-encoded as JPEG and stored under
data/corpus/photos/ (gitignored: third-party photos are never redistributed). The manifest of source URLs is
committed so the set can be rebuilt. Ground truth is annotated by eye in data/external/label_photo_truth.json.

Run: python scripts/collect_photos.py
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

import httpx
from PIL import Image
from tavily import TavilyClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/corpus/label_photos"
MANIFEST = ROOT / "data/external/label_photo_manifest.json"
QUERIES = [
    "Dursban 20 EC chlorpyrifos bottle label",
    "chlorpyriphos 20% EC bottle India label",
    "Gramoxone paraquat dichloride 24 SL bottle",
    "paraquat 24% SL bottle India",
    "Celphos aluminium phosphide tablets",
    "Monocil monocrotophos 36 SL bottle",
    "Nuvan dichlorvos 76 EC bottle",
    "Rogor dimethoate 30 EC bottle",
    "Confidor imidacloprid 17.8 SL bottle",
    "Roundup glyphosate 41 SL bottle India",
    "cypermethrin 10 EC bottle India label",
    "Ratol zinc phosphide rat poison",
    "Furadan carbofuran 3G pack",
    "Ekalux quinalphos 25 EC bottle",
    "Regent fipronil 5 SC bottle",
    "Hamla 550 chlorpyrifos cypermethrin bottle",
    "2,4-D amine salt 58 SL bottle India",
    "profenofos 50 EC bottle India",
]


def main() -> None:
    c = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"items": []}
    seen = {m["url"] for m in manifest["items"]}
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (research benchmark)"}) as http:
        for q in QUERIES:
            try:
                r = c.search(q, include_images=True, max_results=5)
            except Exception as e:  # noqa: BLE001
                print("search failed", q, type(e).__name__)
                continue
            got = 0
            for url in r.get("images", [])[:8]:
                url = url if isinstance(url, str) else url.get("url", "")
                if not url or url in seen:
                    continue
                seen.add(url)
                try:
                    resp = http.get(url)
                    if resp.status_code != 200 or len(resp.content) > 8_000_000:
                        continue
                    img = Image.open(io.BytesIO(resp.content))
                    img.load()
                    if min(img.size) < 200:
                        continue
                    img = img.convert("RGB")
                    img.thumbnail((1600, 1600))
                    name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".jpg"
                    img.save(OUT / name, "JPEG", quality=88)
                    manifest["items"].append({"file": name, "url": url, "query": q, "size": list(img.size)})
                    got += 1
                except Exception as e:  # noqa: BLE001 - one bad image never stops the collection
                    print("  skipped", url[:80], type(e).__name__)
                    continue
            print(f"{q[:60]:60s} +{got}", flush=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("images", len(manifest["items"]))


if __name__ == "__main__":
    main()

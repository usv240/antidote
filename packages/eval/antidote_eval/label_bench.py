"""Label photos to chemical group, through the same path as the app: read the photo, normalise, match the registry.

Ground truth (data/external/label_photo_truth.json) was annotated by eye before any model run. Photos stay local
under data/corpus/label_photos/ (gitignored); rebuild them with scripts/collect_label_photos.py. Run:
  python -m antidote_eval.label_bench --out eval/results/label_bench.json
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

import typer
from antidote_core import ChemRegistry
from antidote_core.pipeline import CONFIDENCE_THRESHOLD, AntidotePipeline
from antidote_llm import Ledger, TokenFactoryClient
from antidote_retrieval import PageStore

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps/api"))

ANTIDOTE_GROUPS = {"organophosphate", "carbamate", "anticoagulant_rodenticide"}


def read_label(image: bytes) -> tuple[dict[str, Any], str, dict[str, Any]]:
    from antidote_api import main as api  # the endpoint's own two-read path

    r = api.read_label_checked(image)
    return r["fields"], r["mode"], r["cross_check"]


def outcome(expected: str, routed: str | None, confident: bool) -> str:
    if not confident or routed is None:
        return "safe_withheld"
    if routed == expected:
        return "correct"
    # a confident wrong route is unsafe if it changes whether an antidote is advised
    return "unsafe" if (routed in ANTIDOTE_GROUPS) != (expected in ANTIDOTE_GROUPS) else "wrong_group_same_advice"


def main(out: Path = typer.Option(ROOT / "eval/results/label_bench.json")) -> None:
    truth = json.loads((ROOT / "data/external/label_photo_truth.json").read_text(encoding="utf-8"))
    pipe = AntidotePipeline(TokenFactoryClient(ledger=Ledger(ROOT / "data/ledger_eval.db")), PageStore(ROOT / "data/index/antidote.db"), ChemRegistry())
    rows: list[dict[str, Any]] = []
    t0 = time.time()
    for it in truth["items"]:
        if "excluded" in it:
            continue
        path = ROOT / "data/corpus/label_photos" / it["file"]
        if not path.exists():
            continue
        fields, mode, check = read_label(path.read_bytes())
        label = pipe.normalise(fields, str(uuid.uuid4()))
        matches, web = pipe.match(label, str(uuid.uuid4()))
        top = matches[0] if matches else None
        confident = bool(top and top.confidence >= CONFIDENCE_THRESHOLD)
        oc = outcome(it["expected_group"], top.group if top else None, confident)
        rows.append({
            "index": it["index"], "expected_group": it["expected_group"], "chemical": it["chemical"], "chemical_legible": it["chemical_legible"],
            "read_product": fields.get("product_name"), "read_ingredients": ", ".join(a.get("name", "") for a in label.active_ingredients),
            "routed_group": top.group if top else None, "confidence": round(top.confidence, 2) if top else None, "via": top.reason if top else None,
            "tavily_used": bool(web.get("results")), "outcome": oc, "mode": mode, "agreed": check.get("agreed"), "first_read": check.get("first"), "second_read": check.get("second"), "url": it["url"],
        })
        print(f"  #{it['index']:>2} {oc:24s} read={rows[-1]['read_ingredients'][:30]!s:30s} -> {rows[-1]['routed_group']} {rows[-1]['confidence']}", flush=True)
    c = Counter(r["outcome"] for r in rows)
    leg = [r for r in rows if r["chemical_legible"]]

    def pct(n: int, d: int) -> float | None:
        return round(100 * n / d, 1) if d else None

    result = {
        "n": len(rows), "outcomes": dict(c), "unsafe": c.get("unsafe", 0),
        "correct": pct(c.get("correct", 0), len(rows)),
        "correct_when_chemical_legible": pct(sum(r["outcome"] == "correct" for r in leg), len(leg)), "legible_n": len(leg),
        "withheld_when_brand_only": pct(sum(r["outcome"] == "safe_withheld" for r in rows if not r["chemical_legible"]), sum(not r["chemical_legible"] for r in rows)),
        "seconds": round(time.time() - t0), "rows": rows,
    }
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print("FINAL", {k: v for k, v in result.items() if k != "rows"})


if __name__ == "__main__":
    typer.run(main)

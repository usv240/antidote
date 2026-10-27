"""Fold both pre-registered case-report sets into the published report without re-running any model call.

Reads eval/results/case_reports.json (set 1) and eval/results/case_reports_v2.json (held-out set 2), replaces the
case-report entries in eval/results/latest.json and rewrites REPORT.md. Run: python -m antidote_eval.fold_cases
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "eval/results"
COLS = ["set", "substance", "expected_group", "routed_group", "outcome", "why", "documented_error", "j1_consistent", "j2_consistent", "url"]


def _agree(rows: list[dict]) -> int:
    return sum(1 for r in rows if r.get("j1_consistent") is not None and r.get("j1_consistent") == r.get("j2_consistent"))


def fold(summary: dict[str, Any], sections: list[dict[str, Any]]) -> None:
    sets = [(name, json.loads((OUT / f).read_text(encoding="utf-8"))) for name, f in (("1", "case_reports.json"), ("2 held-out", "case_reports_v2.json")) if (OUT / f).exists()]
    if not sets:
        return
    for k in [k for k in summary if k.startswith("case_")]:
        del summary[k]
    sections[:] = [s for s in sections if not s["name"].startswith("Published case reports")]
    n = sum(c["n"] for _, c in sets)
    unsafe = sum(c["unsafe_cards"] for _, c in sets)
    correct = sum(c["outcomes"].get("correct", 0) for _, c in sets)
    withheld = sum(c["outcomes"].get("safe_withheld", 0) for _, c in sets)
    doc = sum(c["documented_error_cases"] for _, c in sets)
    doc_ok = sum(c["documented_error_correct"] for _, c in sets)
    doc_held = sum(c["documented_error_safe_withheld"] for _, c in sets)
    per_set = "; ".join(f"set {name}: {c['unsafe_cards']} of {c['n']}" for name, c in sets)
    root = next((c.get("unsafe_root_cause") for _, c in sets if c.get("unsafe_root_cause")), None)
    note = f"pre-registered, {n} verified open-access case reports ({per_set}). {correct} correct and specific, {withheld} withheld until the product is confirmed."
    if root:
        note += " The unsafe card showed the right stop and no antidote advice, but printed the auditor's rejection note, which named oximes. Fixed and regression-tested; the count is not revised."
    summary["case_unsafe"] = {"value": f"{unsafe}/{n}", "unit": "", "label": "Published case reports: unsafe cards", "note": note}
    summary["case_documented"] = {"value": f"{doc_ok}/{doc}", "unit": "", "label": "Documented misidentifications Antidote gets right", "note": f"cases where the paper quotes a misidentification or a wrong first treatment, usually a non-organophosphate treated as one; {doc_held} more withheld safely"}
    rows = [r for _, c in sets for r in c["rows"]]
    j1 = [r["j1_consistent"] for r in rows if r.get("j1_consistent") is not None]
    j2 = [r["j2_consistent"] for r in rows if r.get("j2_consistent") is not None]
    summary["case_concordance"] = {"value": round(100 * sum(j1) / len(j1), 1) if j1 else None, "unit": "%", "label": "Cards consistent with the authors' management",
                                   "note": f"blind Nemotron 3 Super judge across both sets; DeepSeek-V4.1-Flash {round(100 * sum(j2) / len(j2), 1) if j2 else None}%. The judges agree on {_agree(rows)} of {len(rows)} cards."}
    cl = sum(c.get("class_level_fired", 0) for _, c in sets)
    if cl:
        summary["case_class_level"] = {"value": f"{sum(c.get('class_level_correct', 0) for _, c in sets)}/{cl}", "unit": "", "label": "Class-only labels with cholinergic signs, guided correctly", "note": "held-out set 2 only; the rule was written after set 1 and tested on cases it had never seen"}
    sections.append({"name": "Published case reports (pre-registered, two sets)",
                     "description": "Each verified case report's product goes through Antidote. Ground truth comes from the paper, not from Antidote's registry. Set 2 was collected after development with new queries and never used to tune anything. Outcomes: correct and specific, safe but withheld, or unsafe. Two judges compare each card with the authors' own management.",
                     "columns": COLS, "rows": [{"set": name, **{k: r.get(k) for k in COLS if k != "set"}} for name, c in sets for r in c["rows"]]})


def fold_labels(summary: dict[str, Any], sections: list[dict[str, Any]]) -> None:
    for k in [k for k in summary if k.startswith("label_photo_")]:
        del summary[k]
    sections[:] = [s for s in sections if not s["name"].startswith("Real label photos")]
    now, before = OUT / "label_bench.json", OUT / "label_bench_before.json"
    if not now.exists():
        return
    a = json.loads(now.read_text(encoding="utf-8"))
    b = json.loads(before.read_text(encoding="utf-8")) if before.exists() else None
    oc = a["outcomes"]
    note = f"{a['n']} photos of real Indian pesticide labels from product pages and listings, annotated by eye before any run: {oc.get('correct', 0)} correct, {oc.get('safe_withheld', 0)} withheld for the clinician to confirm, {oc.get('wrong_group_same_advice', 0)} wrong group with the same advice."
    mid = OUT / "label_bench_tworead.json"
    m = json.loads(mid.read_text(encoding="utf-8")) if mid.exists() else None
    if b:
        note += f" History: the first run found {b['unsafe']} unsafe cards, because an empty read was normalised to a chemical the model invented."
    if m:
        note += f" With two independent reads, {m['unsafe']} remained, where both vision models invented names from small print. A Tavily check of the brand and a mixture rule brought it to {a['unsafe']}."
    summary["label_photo_unsafe"] = {"value": f"{a['unsafe']}/{a['n']}", "unit": "", "label": "Real label photos: unsafe cards", "note": note}
    summary["label_photo_correct"] = {"value": a.get("correct_when_chemical_legible"), "unit": "%", "label": "Real label photos read correctly when the chemical is legible",
                                      "note": f"{a['legible_n']} photos where the chemical name is readable at photo resolution; {a.get('correct')}% across all {a['n']}"}
    nv = OUT / "label_bench_nano_vl.json"
    if nv.exists():
        n = json.loads(nv.read_text(encoding="utf-8"))
        summary["label_photo_nano_vl"] = {"value": f"{n['unsafe']}/{n['n']}", "unit": "", "label": "Same labels, NVIDIA Nemotron Nano 12B VL alone (no cross-check)",
                                          "note": f"open-weight model on a Nebius Serverless Endpoint: {n['outcomes'].get('correct', 0)} correct, {n['correct_when_chemical_legible']}% when legible. Its one unsafe card (a chlorpyriphos label read as deltamethrin) is why production requires two reads to agree and a brand check, which gave 0 unsafe"}
    cols = ["index", "expected_group", "chemical", "chemical_legible", "read_ingredients", "routed_group", "confidence", "agreed", "outcome"]
    sections.append({"name": "Real label photos (two independent reads)", "description": "Photos of real Indian pesticide containers, not our own. NVIDIA Nemotron 3.5 Super VL and a second model read each label; the chemical is used only when both reads point to the same chemical group and it appears in the text read.",
                     "columns": cols, "rows": [{k: r.get(k) for k in cols} for r in a["rows"]]})


def main() -> None:
    p = OUT / "latest.json"
    report = json.loads(p.read_text(encoding="utf-8"))
    fold(report["summary"], report["sections"])
    fold_labels(report["summary"], report["sections"])
    p.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    md = [f"# Antidote eval report ({report['generated_at']})", ""]
    for v in report["summary"].values():
        md.append(f"- **{v['label']}**: {v['value']}{v.get('unit', '')}  ({v.get('note', '')})")
    (OUT / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print({k: v["value"] for k, v in report["summary"].items() if k.startswith(("case_", "label_photo_"))})


if __name__ == "__main__":
    main()

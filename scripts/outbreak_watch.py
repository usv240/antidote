"""Outbreak watch: an always-on Hermes cron job.

Every morning, run the fixed surveillance rules over the poisoning register. If a cluster or a banned chemical appears
that was not there yesterday, print a short alert for the district surveillance officer; otherwise print nothing, so
Hermes stays silent. No model is called: the alert comes from rules a person can read.

Register (once):  hermes cron create "0 7 * * *" --name antidote-outbreak-watch --no-agent --script antidote_outbreak_watch.py
Run by hand:      uv run python scripts/outbreak_watch.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _root() -> Path:
    for cand in [os.environ.get("ANTIDOTE_ROOT"), os.getcwd(), str(Path(__file__).resolve().parents[1])]:
        if cand and (Path(cand) / "packages/core/antidote_core").exists():
            return Path(cand)
    return Path(__file__).resolve().parents[1]


ROOT = _root()
sys.path[:0] = [str(ROOT / p) for p in ("packages/core", "packages/llm", "packages/retrieval", "packages/rules")]

from antidote_core import ChemRegistry
from antidote_core.surveillance import detect_alerts, load_rows, status_map

STATE = ROOT / "data/outbreak_watch_state.json"


def main() -> None:
    rows = load_rows(ROOT / "data/mlc_register.jsonl", ROOT / "data/samples/register_demo.jsonl")
    alerts = detect_alerts(rows, status_map(ChemRegistry()))
    key = lambda a: f"{a['type']}|{a['chemical_group']}|{','.join(sorted(a['row_ids']))}"
    seen = set(json.loads(STATE.read_text(encoding="utf-8"))) if STATE.exists() else set()
    new = [a for a in alerts if key(a) not in seen]
    STATE.write_text(json.dumps(sorted(seen | {key(a) for a in alerts})), encoding="utf-8")
    if not new:
        return  # silent: Hermes delivers nothing
    print(f"Antidote outbreak watch: {len(new)} new alert(s) in the poisoning register")
    for a in new:
        where = f" in {', '.join(a['localities'])}" if a["localities"] else ""
        print(f"- {a['type'].upper()}: {a['why']}{where}. Dates {a['from'][:10]} to {a['to'][:10]}. Rows {', '.join(a['row_ids'])}.")
    print("Open the Register page for the district brief: https://antidote-bay.vercel.app/register")


if __name__ == "__main__":
    main()

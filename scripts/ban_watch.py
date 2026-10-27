"""Ban watch: a weekly Hermes cron job that keeps the chemical registry honest.

India bans and restricts pesticides by gazette notification. A registry that still lists a banned chemical as
registered would put the wrong regulatory line on a medico-legal record. Every week, Tavily searches government and
agricultural sources for recent ban and restriction notices. Any registry chemical named in a ban notice but not
marked banned in our registry is reported for a person to verify. Nothing is changed automatically.

Register (once):  hermes cron create "0 9 * * 1" --name antidote-ban-watch --no-agent --script antidote_ban_watch.py
Run by hand:      uv run python scripts/ban_watch.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("ANTIDOTE_ROOT") or Path(__file__).resolve().parents[1])
sys.path[:0] = [str(ROOT / p) for p in ("packages/core", "packages/llm", "packages/retrieval", "packages/rules")]
for env in (ROOT / ".env", ROOT.parent / ".env"):
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from antidote_core import ChemRegistry

QUERIES = [
    "pesticides banned in India gazette notification Insecticides Act",
    "CIB&RC banned pesticides list India",
    "India bans pesticides notification Ministry of Agriculture",
]
BAN_WORDS = re.compile(r"\b(ban|banned|banning|prohibit|prohibited|phase[- ]out|withdrawn)\b", re.IGNORECASE)


def main() -> None:
    from tavily import TavilyClient

    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        print("ban watch: TAVILY_API_KEY not set")
        return
    c = TavilyClient(api_key=key)
    reg = ChemRegistry()
    status = {a["name"].lower(): a.get("india_status", "unknown") for a in reg.ais}
    evidence: dict[str, list[str]] = {}
    for q in QUERIES:
        try:
            r = c.search(q, max_results=6, search_depth="advanced")
        except Exception as e:  # noqa: BLE001
            print(f"ban watch: search failed ({type(e).__name__})")
            return
        for res in r.get("results", []):
            text = f"{res.get('title', '')} {res.get('content', '')}"
            for sent in re.split(r"(?<=[.;])\s+", text):
                if not BAN_WORDS.search(sent):
                    continue
                for name in status:
                    if re.search(rf"(?<![a-z]){re.escape(name)}(?![a-z])", sent.lower()):
                        evidence.setdefault(name, []).append(res.get("url", ""))
    flagged = {n: sorted(set(u))[:3] for n, u in evidence.items() if status[n] != "banned" and len(set(u)) >= 2}
    if not flagged:
        return  # silent
    print(f"Antidote ban watch: {len(flagged)} registry chemical(s) named in ban notices but not marked banned. Verify against the CIB&RC list before changing anything.")
    for n, urls in flagged.items():
        print(f"- {n}: registry says '{status[n]}'. Sources: {' ; '.join(urls)}")


if __name__ == "__main__":
    main()

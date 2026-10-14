"""Parse the WHO 2019 hazard classification text (fetched via Tavily extract) into a CSV of active ingredient -> class.

The document lists technical-grade active ingredients in five tables: Table 1 (Ia), Table 2 (Ib), Table 3 (II),
Table 4 (III), Table 5 (U). Rows look like:
  > Chlorpyrifos [ISO] 2921-88-2 2783 OP S I 3 135 ICSC 851 ; JMPR 1999
Some names wrap onto the previous line. Output: packages/core/antidote_core/data/who_hazard_2019.csv with a
line number per row so every class value carries a citation back into the source text.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

SRC = Path("data/corpus/tavily_extract/who2019.txt")
OUT = Path("packages/core/antidote_core/data/who_hazard_2019.csv")

TABLE_RE = re.compile(r"^\s*>?\s*Table\s*(\d)?\.?\s*(EXTREMELY|HIGHLY|MODERATELY|SLIGHTLY|Technical grade active ingredients (?:of )?pesticides unlikely)", re.IGNORECASE)
CLASS_BY_WORD = {"EXTREMELY": "Ia", "HIGHLY": "Ib", "MODERATELY": "II", "SLIGHTLY": "III", "TECHNICAL GRADE ACTIVE INGREDIENTS PESTICIDES UNLIKELY": "U", "TECHNICAL GRADE ACTIVE INGREDIENTS OF PESTICIDES UNLIKELY": "U"}
ROW_RE = re.compile(r"^>\s*(?P<name>[A-Za-z0-9][A-Za-z0-9,\-\(\)' /]+?)\s*(?:\[(?:ISO|C|BSI|ESA|ANSI|JMAF)\]\s*)?(?P<cas>\d{2,7}-\d{2}-\d)\b(?P<rest>.*)$")
WRAP_RE = re.compile(r"^>\s*(?:\[(?:ISO|C|BSI|ESA|ANSI|JMAF)\]\s*)?(?P<cas>\d{2,7}-\d{2}-\d)\b(?P<rest>.*)$")
GROUP_RE = re.compile(r"\b(OP|C|PY|OC|BP|CO|T|TC|NP|AS|OT|PAA|TU|IGR|GR|QA|M|N|PH)\b")
STOP_RE = re.compile(r"^\s*>?\s*(Table\s*6|Annex|Guidelines to classification|References)", re.IGNORECASE)


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    current = None
    rows: list[dict] = []
    prev_name = None
    started = False
    for i, line in enumerate(lines, start=1):
        m = TABLE_RE.match(line)
        if m:
            word = m.group(2).upper()
            current = CLASS_BY_WORD.get(word)
            started = True
            continue
        if started and rows and STOP_RE.match(line) and current == "U":
            break
        if not current:
            continue
        r = ROW_RE.match(line)
        if r:
            name = r.group("name").strip()
            rest = r.group("rest")
        else:
            w = WRAP_RE.match(line)
            if w and prev_name:
                name, rest = prev_name, w.group("rest")
            else:
                cand = line.lstrip("> ").strip()
                prev_name = cand if re.match(r"^[A-Z][A-Za-z0-9,\-\(\)' /]{2,40}$", cand) else None
                continue
        g = GROUP_RE.search(rest)
        rows.append({"active_ingredient": name, "who_class": current, "chemical_type_code": g.group(1) if g else "", "source_line": i})
        prev_name = None
    seen = set()
    uniq = []
    for row in rows:
        k = row["active_ingredient"].lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["active_ingredient", "who_class", "chemical_type_code", "source_line"])
        w.writeheader()
        w.writerows(uniq)
    from collections import Counter

    print(f"{len(uniq)} active ingredients ->", OUT, dict(Counter(r['who_class'] for r in uniq)))
    for probe in ["chlorpyrifos", "monocrotophos", "paraquat", "glyphosate", "cypermethrin", "carbofuran", "phorate", "malathion", "imidacloprid", "zinc phosphide", "endosulfan", "2,4-d"]:
        hit = [r for r in uniq if r["active_ingredient"].lower().startswith(probe)]
        print(f"  {probe:16} -> {[(h['active_ingredient'], h['who_class']) for h in hit[:2]]}")


if __name__ == "__main__":
    main()

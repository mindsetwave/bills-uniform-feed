#!/usr/bin/env python3
"""Updates bills-uniforms-2026.json from the Gridiron Uniform Database.

Fetches the Bills' 2026 season page, reads each game's announced uniform
code, translates it to the MindWave app's uniform names, and writes the
JSON feed the app polls. Unannounced games (TBA/BLANK codes) and unknown
codes are skipped — the app treats missing weeks as "not announced yet".
"""
import json
import re
import sys
import urllib.request

URL = ("https://www.gridiron-uniforms.com/GUD/controller/controller.php"
       "?action=teams-season&team_id=BUF&year=2026")
OUT = "bills-uniforms-2026.json"

# GUD code -> MindWave uniform name (verified against GUD's own images).
CODE_MAP = {
    "A2": "allWhite",      # white helmet / white jersey / white pants
    "K": "allWhite",       # white-out alternate
    "D": "homeRoyal",      # white helmet / royal jersey / white pants
    "E": "allBlue",        # white helmet / royal jersey / blue pants
    "A4": "throwbackRed",  # red helmet / white jersey / white pants
    "L": "classicGrey",    # blue helmet / royal jersey / grey pants
}


def main() -> int:
    request = urllib.request.Request(URL, headers={"User-Agent": "MindWave uniform feed (team app)"})
    html = urllib.request.urlopen(request, timeout=60).read().decode("utf-8", "replace")

    entries = []
    unknown = []
    for block in html.split("weekly-single-matchup-container")[1:]:
        week_match = re.search(r"action=weekly&year=2026&week=(\d+)&league=NFL", block)
        code_match = re.search(r"2026_BUF_([A-Z0-9]+)\.png", block)
        if not week_match or not code_match:
            continue
        week = int(week_match.group(1))
        code = code_match.group(1)
        if not 1 <= week <= 18 or "TBA" in code:
            continue
        uniform = CODE_MAP.get(code)
        if uniform is None:
            unknown.append((week, code))
            continue
        entries.append({"week": week, "uniform": uniform})

    entries.sort(key=lambda e: e["week"])
    with open(OUT, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    print(f"wrote {len(entries)} announced weeks: {entries}")
    if unknown:
        print(f"WARNING unknown GUD codes (add to CODE_MAP): {unknown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

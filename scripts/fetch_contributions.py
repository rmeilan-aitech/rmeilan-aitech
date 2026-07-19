#!/usr/bin/env python3
"""Descarga el calendario público de contribuciones de rmeilan-aitech y calcula estadísticas.

Usa el endpoint HTML público (sin token) que GitHub sirve para embeber el
calendario en perfiles: https://github.com/users/<user>/contributions
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "data" / "contributions.json"
USERNAME = "rmeilan-aitech"
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; profile-art-bot/1.0)"}

COUNT_RE = re.compile(r"^(\d+)\s+contributions?\s+on")


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for td in soup.find_all("td", attrs={"data-date": True}):
        date_str = td["data-date"]
        level = int(td.get("data-level", 0))
        td_id = td.get("id")

        count = 0
        if td_id:
            tooltip = soup.find("tool-tip", attrs={"for": td_id})
            if tooltip:
                match = COUNT_RE.match(tooltip.get_text(strip=True))
                if match:
                    count = int(match.group(1))

        days.append({"date": date_str, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days: list[dict]) -> int:
    idx = len(days) - 1
    if idx >= 0 and days[idx]["count"] == 0:
        idx -= 1  # el día de hoy puede no haber terminado aún

    streak = 0
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    return streak


def compute_longest_streak(days: list[dict]) -> int:
    longest = current = 0
    for day in days:
        if day["count"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def compute_monthly_totals(days: list[dict]) -> dict:
    totals = defaultdict(int)
    for day in days:
        month = day["date"][:7]  # YYYY-MM
        totals[month] += day["count"]
    return dict(sorted(totals.items()))


def build_stats(days: list[dict]) -> dict:
    best_day = max(days, key=lambda d: d["count"]) if days else None
    return {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": sum(d["count"] for d in days),
        "current_streak": compute_current_streak(days),
        "longest_streak": compute_longest_streak(days),
        "best_day": best_day,
        "monthly_totals": compute_monthly_totals(days),
        "days": days,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    days = fetch_days()
    stats = build_stats(days)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Guardado {args.output} ({len(days)} días, racha actual {stats['current_streak']})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Dibuja el heatmap de contribuciones (53x7) a partir de data/contributions.json.

Revelado diagonal con CSS keyframes que se congela al terminar; incluye
leyenda Less -> More y un pie con las estadísticas principales.
"""

import argparse
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "data" / "contributions.json"
DEFAULT_OUTPUT = REPO_ROOT / "heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
STREAK_COLOR = "#69f0a0"

COLS = 53
ROWS = 7
CELL = 11
GAP = 3
MARGIN = 20
LEGEND_H = 24
FOOTER_H = 56
STEP_DELAY = 0.012
CELL_ANIM_DUR = 0.3

BG = "#0d1117"
FG = "#8b949e"
FG_STRONG = "#c9d1d9"


def grid_position(d: date, first: date, first_row: int) -> tuple[int, int]:
    delta = (d - first).days
    row = (first_row + delta) % 7
    col = (first_row + delta) // 7
    return col, row


def streak_dates(days: list[dict], current_streak: int) -> set[str]:
    if current_streak <= 0:
        return set()
    idx = len(days) - 1
    if idx >= 0 and days[idx]["count"] == 0:
        idx -= 1
    picked = []
    while idx >= 0 and len(picked) < current_streak:
        picked.append(days[idx]["date"])
        idx -= 1
    return set(picked)


def build_svg(stats: dict) -> str:
    days = stats["days"]
    first = date.fromisoformat(days[0]["date"])
    first_row = (first.weekday() + 1) % 7  # lunes=0..domingo=6 -> domingo=0

    streak_set = streak_dates(days, stats["current_streak"])

    grid_w = COLS * (CELL + GAP) - GAP
    grid_h = ROWS * (CELL + GAP) - GAP
    width = grid_w + MARGIN * 2
    height = MARGIN + grid_h + LEGEND_H + FOOTER_H + MARGIN

    cells = []
    for day in days:
        d = date.fromisoformat(day["date"])
        col, row = grid_position(d, first, first_row)
        x = MARGIN + col * (CELL + GAP)
        y = MARGIN + row * (CELL + GAP)

        color = STREAK_COLOR if day["date"] in streak_set else PALETTE[min(day["level"], 4)]
        delay = round((col + row) * STEP_DELAY, 3)

        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{color}" style="animation-delay: {delay}s">'
            f'<title>{day["count"]} contribuciones el {day["date"]}</title>'
            f"</rect>"
        )

    legend_y = MARGIN + grid_h + 16
    legend_x = width - MARGIN - (len(PALETTE) * (CELL + GAP) + 70)
    legend_items = [f'<text x="{legend_x}" y="{legend_y + CELL - 1}" fill="{FG}" font-size="11">Less</text>']
    for i, color in enumerate(PALETTE):
        lx = legend_x + 34 + i * (CELL + GAP)
        legend_items.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    more_x = legend_x + 34 + len(PALETTE) * (CELL + GAP) + 6
    legend_items.append(f'<text x="{more_x}" y="{legend_y + CELL - 1}" fill="{FG}" font-size="11">More</text>')

    footer_y = MARGIN + grid_h + LEGEND_H + 24
    best_day = stats.get("best_day") or {"date": "-", "count": 0}
    footer_lines = [
        f'Racha actual: {stats["current_streak"]} días   ·   Racha más larga: {stats["longest_streak"]} días',
        f'Mejor día: {best_day["date"]} ({best_day["count"]} contribuciones)   ·   Total: {stats["total_contributions"]} contribuciones',
    ]
    footer_items = [
        f'<text x="{MARGIN}" y="{footer_y + i * 18}" fill="{FG_STRONG}" font-size="12" '
        f'font-family="SFMono-Regular, Consolas, monospace">{line}</text>'
        for i, line in enumerate(footer_lines)
    ]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Heatmap de contribuciones">
<style>
  .cell {{ opacity: 0; animation: reveal {CELL_ANIM_DUR}s ease-out forwards; }}
  @keyframes reveal {{
    from {{ opacity: 0; transform: scale(0.4); }}
    to   {{ opacity: 1; transform: scale(1); }}
  }}
</style>
<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>
{''.join(cells)}
{''.join(legend_items)}
{''.join(footer_items)}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    stats = json.loads(args.input.read_text(encoding="utf-8"))
    svg = build_svg(stats)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Guardado {args.output}")


if __name__ == "__main__":
    main()

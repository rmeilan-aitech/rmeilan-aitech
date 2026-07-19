#!/usr/bin/env python3
"""Convierte la foto preparada en un retrato ASCII SVG animado (revelado por filas)."""

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "assets" / "photo_prepped.png"
DEFAULT_OUTPUT = REPO_ROOT / "avi-ascii.svg"

COLS = 100
ROWS = 53
RAMP = " .`:-=+*cs#%@"

CHAR_W = 7
CHAR_H = 14
ROW_STAGGER = 0.045  # s entre el inicio de cada fila
ROW_WIPE_DUR = 0.35  # s que tarda cada fila en revelarse


def image_to_chars(path: Path) -> list[str]:
    img = Image.open(path).convert("L").resize((COLS, ROWS), Image.LANCZOS)
    pixels = list(img.getdata())
    ramp_len = len(RAMP) - 1
    rows = []
    for r in range(ROWS):
        row_pixels = pixels[r * COLS:(r + 1) * COLS]
        line = "".join(RAMP[round(p / 255 * ramp_len)] for p in row_pixels)
        rows.append(line)
    return rows


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    defs = []
    groups = []
    for i, line in enumerate(rows):
        row_y = i * CHAR_H
        baseline = row_y + CHAR_H * 0.8
        begin = round(i * ROW_STAGGER, 3)

        defs.append(
            f'<clipPath id="clip-row-{i}">'
            f'<rect x="0" y="{row_y}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{width}" '
            f'dur="{ROW_WIPE_DUR}s" begin="{begin}s" fill="freeze" calcMode="linear"/>'
            f"</rect></clipPath>"
        )
        groups.append(
            f'<g clip-path="url(#clip-row-{i})">'
            f'<text x="0" y="{baseline}" textLength="{width}" lengthAdjust="spacingAndGlyphs">'
            f"{escape(line)}</text></g>"
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Retrato ASCII">
<style>
  text {{
    font-family: "SFMono-Regular", "Consolas", "Liberation Mono", monospace;
    font-size: {CHAR_H}px;
    fill: #c9d1d9;
    white-space: pre;
  }}
  svg {{ background: transparent; }}
</style>
<defs>
{''.join(defs)}
</defs>
<rect width="{width}" height="{height}" fill="#0d1117"/>
{''.join(groups)}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = image_to_chars(args.input)
    svg = build_svg(rows)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Guardado {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera una tarjeta SVG estilo neofetch con filas key/value animadas.

Variable de entorno STATIC=1 -> genera un frame congelado (sin animación),
útil para revisar el resultado final sin esperar a que termine la animación.
"""

import argparse
import os
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "info-card.svg"

TITLE = "rmeilan-aitech@github"
FIELDS = [
    ("OS", "GitHub Actions Runner"),
    ("Stack", "React · Express · Supabase · n8n"),
    ("Focus", "Automatización & IA"),
    ("Languages", "JavaScript/TypeScript · Python"),
    ("Uptime", "shipping since 2023"),
]

WIDTH = 560
PADDING_X = 28
PADDING_Y = 26
ROW_H = 30
FONT_SIZE = 16
ROW_STAGGER = 0.08
FADE_DUR = 0.5

BG = "#0d1117"
ACCENT = "#58a6ff"
FG = "#c9d1d9"
MUTED = "#8b949e"


def build_rows() -> list[tuple[str, str, str]]:
    """Devuelve tuplas (key_markup, value_markup, kind) para cada fila."""
    rows = [(TITLE, TITLE, "title")]
    rows.append(("sep", "-" * len(TITLE), "sep"))
    for key, value in FIELDS:
        rows.append((key, value, "field"))
    return rows


def build_svg(static: bool) -> str:
    rows = build_rows()
    height = PADDING_Y * 2 + len(rows) * ROW_H

    style_block = ""
    if not static:
        style_block = f"""
<style>
  .row {{ opacity: 0; animation: fadeSlide {FADE_DUR}s ease-out forwards; }}
  @keyframes fadeSlide {{
    from {{ opacity: 0; transform: translateX(-14px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}
</style>"""

    body = []
    for i, (key, value, kind) in enumerate(rows):
        y = PADDING_Y + i * ROW_H + ROW_H * 0.65
        delay = round(i * ROW_STAGGER, 3)
        row_style = "" if static else f' style="animation-delay: {delay}s"'

        if kind == "title":
            text = f'<text x="{PADDING_X}" y="{y}" font-weight="700" fill="{ACCENT}">{escape(key)}</text>'
        elif kind == "sep":
            text = f'<text x="{PADDING_X}" y="{y}" fill="{MUTED}">{escape(value)}</text>'
        else:
            text = (
                f'<text x="{PADDING_X}" y="{y}">'
                f'<tspan fill="{ACCENT}" font-weight="600">{escape(key)}</tspan>'
                f'<tspan fill="{MUTED}">:  </tspan>'
                f'<tspan fill="{FG}">{escape(value)}</tspan>'
                f"</text>"
            )

        body.append(f'<g class="row"{row_style}>{text}</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="Info card">
{style_block}
<rect width="{WIDTH}" height="{height}" rx="12" fill="{BG}"/>
<g font-family="SFMono-Regular, Consolas, 'Liberation Mono', monospace" font-size="{FONT_SIZE}">
{''.join(body)}
</g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    static = os.environ.get("STATIC") == "1"
    svg = build_svg(static)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Guardado {args.output} (static={static})")


if __name__ == "__main__":
    main()

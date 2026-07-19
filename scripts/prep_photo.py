#!/usr/bin/env python3
"""Quita el fondo de la foto fuente, sube el contraste local y la deja en gris."""

import argparse
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "assets" / "photo_original.jpg"
DEFAULT_OUTPUT = REPO_ROOT / "assets" / "photo_prepped.png"


def prep_photo(input_path: Path, output_path: Path) -> None:
    source_bytes = input_path.read_bytes()

    print(f"Quitando fondo con rembg ({input_path.name})...")
    cutout_bytes = remove(source_bytes)
    cutout = Image.open(BytesIO(cutout_bytes)).convert("RGBA")

    print("Componiendo sobre blanco puro...")
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composed = Image.alpha_composite(white_bg, cutout).convert("RGB")

    print("Convirtiendo a gris y aplicando CLAHE...")
    gray = np.array(composed.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(output_path)
    print(f"Guardado {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prep_photo(args.input, args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a compact, e-paper-friendly QR code PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

import qrcode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=3,
        border=4,
    )
    code.add_data(args.url)
    code.make(fit=True)
    image = code.make_image(fill_color="black", back_color="white").get_image()
    image = image.convert("RGBA")
    alpha = image.convert("L").point(lambda value: 255 if value < 128 else 0)
    image.putalpha(alpha)
    image.save(args.output)
    width, height = image.size
    print(f"Generated {args.output} ({width}x{height}) -> {args.url}")


if __name__ == "__main__":
    main()

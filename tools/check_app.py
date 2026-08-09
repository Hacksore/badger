#!/usr/bin/env python3
"""Dependency-free checks for the files copied to Badgeware."""

from __future__ import annotations

import ast
import struct
import sys
from pathlib import Path


def check_png(path: Path) -> None:
    with path.open("rb") as image_file:
        header = image_file.read(24)

    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a valid PNG file")

    width, height = struct.unpack(">II", header[16:24])
    if path.name == "avatar.png" and (width > 80 or height > 80):
        raise ValueError(f"{path}: {width}x{height} exceeds Badgeware's 80x80 avatar size")

    print(f"ok: {path} ({width}x{height})")


def check_python(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path))
    compile(source, str(path), "exec")
    print(f"ok: {path} (syntax)")


def main(arguments: list[str]) -> int:
    if not arguments:
        print("error: no app files supplied", file=sys.stderr)
        return 2

    try:
        for name in arguments:
            path = Path(name)
            if not path.is_file():
                raise FileNotFoundError(f"required app file missing: {path}")
            if path.suffix == ".py":
                check_python(path)
            elif path.suffix.lower() == ".png":
                check_png(path)
    except (OSError, SyntaxError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

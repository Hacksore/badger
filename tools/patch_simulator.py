#!/usr/bin/env python3
"""Make Badgeware Desktop's native window match the Badger 2350 aspect ratio."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPLACEMENTS = {
    "window_size.x = 160 * 6;": "window_size.x = 264 * 4;",
    "window_size.y = 120 * 6;": "window_size.y = 176 * 4;",
    "window_aspect.x = 4;": "window_aspect.x = 3;",
    "window_aspect.y = 3;": "window_aspect.y = 2;",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("simulator", type=Path)
    args = parser.parse_args()

    source = args.simulator / "micropython" / "main.c"
    try:
        content = source.read_text(encoding="utf-8")
    except OSError as error:
        print(f"error: cannot read simulator source: {error}", file=sys.stderr)
        return 1

    updated = content
    for original, replacement in REPLACEMENTS.items():
        if replacement in updated:
            continue
        if original not in updated:
            print(f"error: simulator source no longer contains {original!r}", file=sys.stderr)
            return 1
        updated = updated.replace(original, replacement, 1)

    if updated == content:
        print("Simulator window already configured for Badger 2350")
        return 0

    try:
        source.write_text(updated, encoding="utf-8")
    except OSError as error:
        print(f"error: cannot update simulator source: {error}", file=sys.stderr)
        return 1

    print("Configured simulator window for 264x176 Badger output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

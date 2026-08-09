#!/usr/bin/env python3
"""Download and optionally flash the latest official Badger 2350 UF2."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

RELEASE_URL = "https://api.github.com/repos/pimoroni/badger2350/releases/latest"
UF2_MAGIC = b"UF2\nWQ]\x9e"


def validate_uf2(path: Path) -> None:
    with path.open("rb") as firmware_file:
        header = firmware_file.read(len(UF2_MAGIC))
    if header != UF2_MAGIC or path.stat().st_size < 1_000_000:
        raise RuntimeError(f"downloaded file does not look like a complete UF2 image: {path}")


def firmware_asset(with_filesystem: bool) -> tuple[str, str]:
    request = urllib.request.Request(RELEASE_URL, headers={"User-Agent": "badger-makefile"})
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)

    suffix = "-micropython-with-filesystem.uf2" if with_filesystem else "-micropython.uf2"
    matches = [asset for asset in release["assets"] if asset["name"].endswith(suffix)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one release asset ending in {suffix!r}, found {len(matches)}")
    return matches[0]["name"], matches[0]["browser_download_url"]


def download(output_dir: Path, with_filesystem: bool) -> Path:
    name, url = firmware_asset(with_filesystem)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / name
    if destination.exists():
        validate_uf2(destination)
        print(f"Using {destination}")
        return destination

    temporary = destination.with_suffix(".part")
    print(f"Downloading {name}...")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "badger-makefile"})
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        temporary.replace(destination)
        validate_uf2(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Saved {destination}")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("download", "flash"))
    parser.add_argument("--with-filesystem", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("build"))
    parser.add_argument("--mount", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        firmware = download(args.output_dir, args.with_filesystem)
        if args.action == "flash":
            if args.mount is None or not args.mount.is_dir():
                raise RuntimeError("flash requires a mounted RP2350 drive")
            print(f"Flashing {firmware.name} to {args.mount}...")
            shutil.copyfile(firmware, args.mount / firmware.name)
            print("Flash copied; the badge should reboot automatically.")
    except (OSError, KeyError, RuntimeError, urllib.error.URLError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

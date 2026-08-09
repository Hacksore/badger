# Badger 2350 badge app

This repo contains a customized version of the built-in Badgeware `badge` app and a Makefile for checking, previewing, deploying, simulating, and reflashing it.

Local Python and developer tools are managed with [uv](https://docs.astral.sh/uv/):

```sh
make setup           # uv sync; creates .venv from uv.lock
```

## Fast path: deploy the app

1. Connect the Badger over a data-capable USB-C cable.
2. Double-tap **RESET** to enter disk mode. The badge mounts as `BADGER` or `Badger2350`.
3. Run:

   ```sh
   make deploy
   ```

The Makefile validates the Python and PNG files, copies `__init__.py`, `avatar.png`, and the generated social QR into `/apps/badge`, then safely ejects the drive so the badge reboots. It deliberately leaves the firmware-provided app icon and social assets alone.

Useful development commands:

```sh
make                 # list every target
make check           # syntax and asset checks through uv
make lint            # the Ruff version pinned by uv.lock
make deploy-dry-run  # preview the USB copy
make sync-app        # copy without ejecting
make watch           # sync on save; requires fswatch, eject when done
make backup          # copy the installed badge app into ./backups
```

The social screen includes a QR code for `https://seanboult.dev`. Regenerate it for another destination with:

```sh
make qr QR_URL=https://example.com
```

If the volume is mounted somewhere unusual, override it:

```sh
make deploy BADGER_MOUNT=/path/to/Badger2350
```

## Simulator

[Pimoroni's Badgeware simulator](https://github.com/pimoroni/badgeware-simulator) is native software and takes a while to build the first time.

```sh
make sim-setup       # clone beside this repo and build it
make sim             # stage this app, rebuild if needed, and run
make sim-rebuild     # force a native rebuild after simulator changes
```

Set `SIM_DIR=/path/to/badgeware-simulator` when it is not checked out beside this repo. The Makefile creates an isolated simulator filesystem under `build/simulator-root`, so it does not overwrite the simulator checkout's app files or other local changes.

The simulator shim changes Badgeware Desktop's generic 160×120 canvas to the Badger 2350's native 264×176 resolution. `make sim` also applies a small, idempotent window-size patch to the adjacent simulator checkout and rebuilds it when needed; this keeps its native window at the same 3:2 aspect ratio instead of clipping the right side of the Badger framebuffer.

## Firmware updates and factory reflashes

App deployment and firmware flashing are different USB modes:

- Double-tap **RESET** for disk mode and `make deploy`.
- Hold **BOOT**, tap **RESET**, then release **BOOT** for the `RP2350` bootloader drive.

The safe firmware target keeps the current filesystem:

```sh
make firmware         # only download the latest official UF2
make flash-firmware   # download and copy it to a mounted RP2350 drive
```

A full factory image replaces every app and file. Back up first, then opt in explicitly:

```sh
make backup
# Re-enter bootloader mode after the backup.
make flash-firmware-full ALLOW_ERASE=1
make deploy            # restore this customized badge app afterward
```

Firmware is resolved at run time from the [latest official Badger 2350 GitHub release](https://github.com/pimoroni/badger2350/releases/latest). See the [official firmware instructions](https://badgewa.re/docs/introduction/update-your-firmware.md) for the hardware button sequence and current release notes.

## Why desktop Python reports unusual globals

Badgeware injects APIs such as `screen`, `image`, `shape`, `badge`, `run`, and the button constants before importing an app. They are valid on the device but undefined to ordinary CPython. `pyproject.toml` teaches Ruff about these firmware-provided names; `make check` still compiles the source and catches real syntax errors without trying to execute hardware code.

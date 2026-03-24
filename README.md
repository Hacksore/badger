# Badge app (local dev → simulator → USB)

Develop here in Git, test with [badgeware-simulator](https://github.com/pimoroni/badgeware-simulator), push files to the mounted badge with `rsync` (fast, incremental).

Firmware updates and USB workflow: [Update your firmware](https://badgewa.re/docs/introduction/update-your-firmware.md).

## One-time setup

1. **This repo** — your MicroPython / badge app files live here (e.g. `main.py` plus modules, assets).

2. **Simulator** — clone next to this folder (or anywhere; set `BADGEWARE_SIM`):

   ```bash
   cd ..
   git clone https://github.com/pimoroni/badgeware-simulator.git
   cd badgeware-simulator
   make -j    # first build; takes a while
   ```

3. **Optional** — copy env defaults:

   ```bash
   cp .env.example .env
   # edit BADGER_MOUNT / BADGEWARE_SIM if needed
   ```

4. **Git** (if you want version control):

   ```bash
   git init
   git add .
   git commit -m "Initial badge app scaffold"
   ```

## Simulator vs hardware paths

`main.py` is a tiny hello world and does not change the working directory. If you add assets or local imports, set paths explicitly: in the simulator your files usually live at the virtual FS root (`/` after `make deploy-sim`); on hardware they often live under **`/system/apps/badge`** (see stock `system/apps/badge` in badgeware-simulator).

## Editor type checking

`typings/badgeware.pyi` plus `pyrightconfig.json` satisfy Pyright/BasedPyright for `from badgeware import run`. Picovector globals (`screen`, `color`, …) are read with `getattr(builtins, …)` so the checker does not need fake builtins.

## Day-to-day

| Goal | Command |
|------|---------|
| Push to badge USB | `make deploy-badge` (needs `/Volumes/BADGER` mounted) |
| Push to simulator FS | `make deploy-sim` |
| Sync + run sim (`./go root`) | `make sim` |

The simulator’s `./go root` mode uses `root-badgeware` as the fake filesystem; `deploy-sim` rsyncs into that directory. See the upstream `go` script in badgeware-simulator.

## What gets copied

- **Source**: repo root (or `BADGE_SRC` in `.env`), paths listed in **`.badgeignore`** are skipped (so `scripts/`, `README.md`, `.git`, etc. are not sent to the badge).
- **`SYNC_DELETE`**: default is **off** so rsync does **not** `--delete` on the badge (avoids wiping files that only exist on hardware). Set `SYNC_DELETE=1` in `.env` only if you fully trust the destination to mirror the repo.

## Optional: auto-deploy on save

Requires [fswatch](https://emcrisostomo.github.io/fswatch/):

```bash
brew install fswatch
make watch
```

## Migrating from `/Volumes/BADGER`

Copy existing files into this repo once (respecting what you want in Git), then use `make deploy-badge` for updates:

```bash
rsync -av --exclude .Trashes --exclude .fseventsd /Volumes/BADGER/ ./ 
# trim / .gitignore as needed, then commit
```

---

Simulator reference: [pimoroni/badgeware-simulator](https://github.com/pimoroni/badgeware-simulator).

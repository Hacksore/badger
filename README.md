# Badger 2350 badge

Personal [Badgeware](https://badgewa.re/) app for the Badger 2350.

Requirements: macOS, [uv](https://docs.astral.sh/uv/), Git, and a data-capable USB-C cable. Run `make` to see the three available commands.

## Simulator

```sh
make sim
```

The first run clones and builds [Badgeware Desktop](https://github.com/pimoroni/badgeware-simulator) beside this repo. Later runs reuse that build, stage the current app in an isolated filesystem, and launch it at the Badger's 264×176 resolution.

Simulator controls:

- `Space`: Button B; flip between the badge and social/QR screens
- `↑` / `↓`: change the background pattern
- `←` / `→`: Buttons A and C
- `Esc`: hot reload

## Deploy the app

1. Connect the Badger over USB-C.
2. Double-tap **RESET**. Wait for the `BADGER` drive to appear.
3. Run:

   ```sh
   make deploy
   ```

The command validates the app, copies its Python and image files into `/apps/badge`, safely ejects the drive, and lets the badge reboot.

## Update the firmware

This installs the latest official firmware together with its matching system files. It replaces the badge filesystem, so deploy this app again afterward.

1. Connect the Badger over USB-C.
2. Hold **BOOT**, tap **RESET**, then release **BOOT**. Wait for the `RP2350` drive to appear.
3. Run:

   ```sh
   make firmware
   ```

The firmware is downloaded from the [latest official Badger 2350 release](https://github.com/pimoroni/badger2350/releases/latest), copied to the bootloader drive, and the badge reboots automatically.

After it reboots, double-tap **RESET** and run `make deploy` to restore this app.

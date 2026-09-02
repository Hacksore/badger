"""Simulator-only entry point that launches this repo's badge app."""

import builtins

import badgeware
import simulator

# Static declarations for pylsp/Pyflakes. The simulator boot process injects
# these names before this entry point runs.
if False:
    font = framebuffer = image = io = None

BADGER_WIDTH = 264
BADGER_HEIGHT = 176

# The native simulator currently lacks three helpers injected by Badger firmware.
# Let its outer frame loop drive the app instead of Badgeware's on-device loop.
def simulator_run(update):
    return None


def simulator_wait(timeout=None):
    return None


class SimulatorBadge:
    @staticmethod
    def pressed(button):
        return button in io.pressed

    @staticmethod
    def update():
        return None


    @staticmethod
    def battery_level():
        # Desktop has no battery ADC, so keep the preview representative.
        return 75

    @staticmethod
    def battery_voltage():
        return 3.85


class SimulatorRTC:
    @staticmethod
    def set_alarm(hours=0, minutes=0, seconds=0):
        return None

    @staticmethod
    def clear_alarm():
        return None


builtins.run = simulator_run
builtins.clamp = badgeware.clamp
builtins.wait_for_button_or_alarm = simulator_wait
builtins.badge = SimulatorBadge()
builtins.rtc = SimulatorRTC()

# Match the font registry exposed by current Badger firmware.
builtins.font = badgeware.rom_font

for name in ("BUTTON_A", "BUTTON_B", "BUTTON_C", "BUTTON_UP", "BUTTON_DOWN"):
    setattr(builtins, name, getattr(io, name))

# Badgeware Desktop defaults to a generic 160x120 canvas. Match the physical
# Badger 2350 so its pixel-based layouts render exactly as they do on-device.
simulator.resolution(BADGER_WIDTH, BADGER_HEIGHT)
screen = image(BADGER_WIDTH, BADGER_HEIGHT, framebuffer)
builtins.screen = screen
screen.font = badgeware.DEFAULT_FONT
screen.pen = badgeware.BG

app = __import__("/system/apps/badge")


def update():
    if not badgeware._fatal_error:
        screen.pen = badgeware.BG
        screen.clear()
        screen.pen = badgeware.FG
    io.poll()
    app.update()
    screen.monochrome()

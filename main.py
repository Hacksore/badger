import builtins

import badgeware

screen = getattr(builtins, "screen")
rom_font = getattr(builtins, "rom_font")
io = getattr(builtins, "io")

screen.antialias = screen.X2

try:
    __import__("simulator")
    IS_SIM = True
except ImportError:
    IS_SIM = False


def update():
    # Simulator: the native host calls this global every frame (see badgeware-simulator
    # badgeware.c — do not use badgeware.run() here or init never finishes and nothing draws).
    # Hardware: badgeware.run() below wraps update() with the same clear + io.poll each frame.
    if IS_SIM:
        if not getattr(badgeware, "_fatal_error", False):
            screen.pen = badgeware.BG
            screen.clear()
            screen.pen = badgeware.FG
        io.poll()

    screen.font = rom_font.ignore
    msg = "Hello, world"
    w, _ = screen.measure_text(msg)
    x = (screen.width - w) // 2
    y = (screen.height // 2) - 10
    screen.text(msg, x, y)


if not IS_SIM:
    badgeware.run(update)

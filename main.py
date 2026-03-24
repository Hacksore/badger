import builtins

from badgeware import run

screen = getattr(builtins, "screen")
color = getattr(builtins, "color")
rom_font = getattr(builtins, "rom_font")

screen.antialias = screen.X2


def update():
    screen.pen = color.white
    screen.clear()
    screen.pen = color.black
    screen.font = rom_font.ignore
    msg = "Hello, world"
    w, _ = screen.measure_text(msg)
    screen.text(msg, (screen.width / 2) - (w / 2), (screen.height / 2) - 10)


run(update)

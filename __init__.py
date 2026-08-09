import os
import sys

sys.path.insert(0, "/system/apps/badge")
os.chdir("/system/apps/badge")

# Static declarations for pylsp/Pyflakes. Badgeware injects these names before
# running the app, so this block must never execute on the badge or simulator.
if False:
    badge = brush = clamp = color = image = mat3 = None
    rom_font = run = screen = shape = vec2 = None
    wait_for_button_or_alarm = None
    BUTTON_B = BUTTON_DOWN = BUTTON_UP = None

CX = screen.width / 2
screen.antialias = screen.X2

# details to be shown on the card
id_photo = image.load("avatar.png")
id_name = "Sean Boult"
id_role = "Developer @ AWS"

id_window = image(id_photo.width, id_photo.height)
id_window.blit(id_photo, vec2(0, 0))
id_window.dither()
social_qr = image.load("social-qr.png")
name_rocket = image.load("rocket.png")

# These icons ship with the built-in badge app in official Badger firmware.
id_socials = {
    "twitter": {"icon": None, "handle": "@Hacksore"},
    "github": {"icon": None, "handle": "@Hacksore"},
    "discord": {"icon": None, "handle": "@Hacksore"},
}
social_order = ("twitter", "github", "discord")

# load in the social icons
for key in social_order:
    id_socials[key]["icon"] = image.load(
        f"/system/apps/badge/assets/socials/{key}.png"
    )

# id card variables
id_body = shape.rectangle(0, 0, 240, 155)
id_outline = shape.rectangle(0, 0, 240, 155).stroke(2)
rear_view = False
card_pos = (10, 10)
pattern = 25

small_font = rom_font.smart
large_font = rom_font.ignore


def center_text(text, y):
    w, _ = screen.measure_text(text)
    screen.text(text, (screen.width / 2) - (w / 2), y)


def update():
    global rear_view, pattern

    # unpack the x and y for the card
    _, y = card_pos

    # clear the screen
    screen.pen = brush.pattern(color.white, color.black, pattern)
    screen.clear()

    if badge.pressed(BUTTON_B):
        rear_view = not rear_view

    if badge.pressed(BUTTON_UP):
        pattern += 1

    if badge.pressed(BUTTON_DOWN):
        pattern -= 1

    pattern = clamp(pattern, 0, 37)

    # draw the card
    id_body.transform = mat3().translate(CX, y)
    id_outline.transform = mat3().translate(CX, y)
    id_body.transform = id_body.transform.translate(-120, 0)
    id_outline.transform = id_outline.transform.translate(-120, 0)

    screen.pen = color.dark_grey
    id_body.transform = id_body.transform.translate(4, 4)
    screen.shape(id_body)

    screen.pen = color.white
    id_body.transform = id_body.transform.translate(-4, -4)
    screen.shape(id_body)
    screen.pen = color.black
    screen.shape(id_outline)

    photo_y = y + 18 + id_photo.height
    # Draw the card information
    screen.pen = color.black
    if not rear_view:
        screen.font = large_font
        screen.blit(id_window, vec2(CX - id_photo.width / 2, y + 15))
        center_text(id_name, photo_y)
        screen.font = small_font
        center_text(id_role, photo_y + 31)
    else:
        screen.pen = color.black
        screen.font = large_font
        header_gap = 6
        header_width, header_height = screen.measure_text(id_name)
        header_x = (screen.width - header_width - header_gap - name_rocket.width) / 2
        header_y = y + 6
        screen.text(id_name, header_x, header_y)
        screen.blit(
            name_rocket,
            vec2(
                header_x + header_width + header_gap,
                header_y + ((header_height - name_rocket.height) / 2),
            ),
        )
        screen.font = small_font

        qr_quiet_zone = 12
        qr_label_gap = 4
        qr_label = "SOCIALS"
        qr_label_width, qr_label_height = screen.measure_text(qr_label)
        qr_visible_height = social_qr.height - (qr_quiet_zone * 2)
        content_height = qr_visible_height + qr_label_gap + qr_label_height
        content_top = y + 44

        social_icon_height = id_socials["twitter"]["icon"].height
        social_step = int(
            (content_height - social_icon_height) / (len(id_socials) - 1)
        )
        socials_y = content_top
        for key in social_order:
            account = id_socials[key]
            screen.blit(account["icon"], vec2(30, socials_y))
            screen.text(account["handle"], 55, socials_y)
            socials_y += social_step

        qr_x = 149
        qr_y = content_top - qr_quiet_zone
        qr_center_x = qr_x + (social_qr.width // 2)
        screen.blit(social_qr, vec2(qr_x, qr_y))
        screen.text(
            qr_label,
            qr_center_x - (qr_label_width // 2),
            content_top + qr_visible_height + qr_label_gap,
        )

    badge.update()
    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    pass


run(update)

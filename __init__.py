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
linkedin_qr = image.load("linkedin-qr.png")
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
label_font = rom_font.smart
large_font = rom_font.ignore


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

    # Draw the card information
    screen.pen = color.black
    if not rear_view:
        content_left = 20
        photo_y = y + 15
        role_y = photo_y + id_photo.height + 32

        screen.font = large_font
        name_width, _ = screen.measure_text(id_name)
        photo_x = content_left + ((name_width - id_photo.width) / 2)
        screen.blit(id_window, vec2(photo_x, photo_y))
        screen.text(id_name, content_left, photo_y + id_photo.height + 4)
        screen.font = small_font
        screen.text(id_role, content_left, role_y)

        qr_quiet_zone = 12
        qr_label_gap = 4
        qr_label_line_gap = 1
        qr_label_lines = ("SCAN HERE", "FOR LINKEDIN")
        qr_label_sizes = [screen.measure_text(line) for line in qr_label_lines]
        _, role_height = screen.measure_text(id_role)
        qr_visible_height = linkedin_qr.height - (qr_quiet_zone * 2)
        qr_visible_bottom = role_y + role_height
        qr_visible_top = qr_visible_bottom - qr_visible_height
        qr_x = screen.width - content_left - linkedin_qr.width + 6
        qr_y = qr_visible_top - qr_quiet_zone

        screen.blit(linkedin_qr, vec2(qr_x, qr_y))
        qr_label_height = sum(height for _, height in qr_label_sizes)
        qr_label_height += qr_label_line_gap * (len(qr_label_lines) - 1)
        qr_label_y = qr_visible_top - qr_label_gap - qr_label_height
        for line, (line_width, line_height) in zip(qr_label_lines, qr_label_sizes):
            line_x = qr_x + ((linkedin_qr.width - line_width) / 2)
            screen.text(line, line_x, qr_label_y)
            qr_label_y += line_height + qr_label_line_gap
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
        qr_label_line_gap = 1
        qr_label_lines = ("PERSONAL", "WEBSITE")
        _, social_label_height = screen.measure_text("SOCIALS")
        screen.font = label_font
        qr_label_sizes = [screen.measure_text(line) for line in qr_label_lines]
        screen.font = small_font
        qr_visible_height = social_qr.height - (qr_quiet_zone * 2)
        social_content_height = qr_visible_height + qr_label_gap + social_label_height
        content_top = y + 44

        social_icon_height = id_socials["twitter"]["icon"].height
        social_step = int(
            (social_content_height - social_icon_height) / (len(id_socials) - 1)
        )
        socials_y = content_top
        for key in social_order:
            account = id_socials[key]
            screen.blit(account["icon"], vec2(30, socials_y))
            screen.text(account["handle"], 55, socials_y)
            socials_y += social_step

        qr_x = 149
        qr_visible_top = content_top - 5
        qr_y = qr_visible_top - qr_quiet_zone
        screen.blit(social_qr, vec2(qr_x, qr_y))
        qr_label_y = qr_visible_top + qr_visible_height + qr_label_gap
        screen.font = label_font
        for line, (line_width, line_height) in zip(qr_label_lines, qr_label_sizes):
            line_x = qr_x + ((social_qr.width - line_width) / 2)
            screen.text(line, line_x, qr_label_y)
            qr_label_y += line_height + qr_label_line_gap

    badge.update()
    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    pass


run(update)

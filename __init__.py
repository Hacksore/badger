import os
import sys

sys.path.insert(0, "/system/apps/badge")
os.chdir("/system/apps/badge")

# Static declarations for pylsp/Pyflakes. Badgeware injects these names before
# running the app, so this block must never execute on the badge or simulator.
if False:
    badge = color = image = None
    font = rtc = run = screen = shape = vec2 = None
    wait_for_button_or_alarm = None
    BUTTON_B = None

CX = screen.width / 2
screen.antialias = screen.X2

# details to be shown on the card
id_photo = image.load("avatar.png")
id_name = "SEAN BOULT"
id_role_lines = ("DEVELOPER", "AWS")

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

rear_view = False
card_y = 0
content_y_offset = 10
battery_refresh_minutes = 30
battery_curve = (
    (3.30, 0),
    (3.50, 5),
    (3.70, 20),
    (3.80, 50),
    (3.90, 70),
    (4.00, 80),
    (4.10, 90),
    (4.20, 100),
)

small_font = font.smart
large_font = font.ignore
role_font = font.nope


def battery_level_from_voltage(voltage):
    if voltage <= battery_curve[0][0]:
        return battery_curve[0][1]

    for index in range(1, len(battery_curve)):
        upper_voltage, upper_level = battery_curve[index]
        if voltage <= upper_voltage:
            lower_voltage, lower_level = battery_curve[index - 1]
            progress = (voltage - lower_voltage) / (upper_voltage - lower_voltage)
            return round(lower_level + ((upper_level - lower_level) * progress))

    return battery_curve[-1][1]


def draw_battery_indicator(battery_level):
    icon_width = 16
    icon_height = 8
    icon_right_margin = 8
    icon_x = screen.width - icon_width - 1 - icon_right_margin
    icon_y = card_y + 7

    screen.pen = color.black
    screen.shape(shape.rectangle(icon_x, icon_y, icon_width, icon_height))
    screen.shape(shape.rectangle(icon_x + icon_width, icon_y + 2, 1, 4))

    screen.pen = color.white
    screen.shape(shape.rectangle(icon_x + 1, icon_y + 1, icon_width - 2, icon_height - 2))

    fill_width = round(((icon_width - 4) / 100) * battery_level)
    screen.pen = color.black
    screen.shape(shape.rectangle(icon_x + 2, icon_y + 2, fill_width, icon_height - 4))


def draw_screen_border():
    screen.pen = color.black
    screen.shape(
        shape.rounded_rectangle(1, 1, screen.width - 2, screen.height - 2, 6).stroke(1)
    )


def update():
    global rear_view

    battery_voltage = badge.battery_voltage()
    battery_level = battery_level_from_voltage(battery_voltage)

    # clear the screen
    screen.pen = color.white
    screen.clear()

    if badge.pressed(BUTTON_B):
        rear_view = not rear_view

    # Draw the card information
    screen.pen = color.black
    if not rear_view:
        content_left = 20
        photo_y = card_y + content_y_offset + 15
        role_y = photo_y + id_photo.height + 32
        front_name = id_name.upper()

        screen.font = large_font
        name_width, _ = screen.measure_text(front_name)
        front_center_x = content_left + (name_width / 2)
        photo_x = front_center_x - (id_photo.width / 2)
        screen.blit(id_window, vec2(photo_x, photo_y + 5))
        screen.text(front_name, content_left, photo_y + id_photo.height + 4)

        screen.font = role_font
        role_line_gap = 0
        role_sizes = [screen.measure_text(line) for line in id_role_lines]
        for line, (line_width, line_height) in zip(id_role_lines, role_sizes):
            line_x = content_left + ((name_width - line_width) / 2)
            screen.text(line, line_x, role_y)
            role_y += line_height + role_line_gap

        qr_quiet_zone = 12
        qr_label_gap = 4
        qr_label_line_gap = 1
        qr_label_lines = ("SCAN HERE", "FOR LINKEDIN")
        screen.font = role_font
        qr_label_sizes = [screen.measure_text(line) for line in qr_label_lines]
        qr_label_height = sum(height for _, height in qr_label_sizes)
        qr_label_height += qr_label_line_gap * (len(qr_label_lines) - 1)
        qr_group_height = (
            qr_label_height
            + qr_label_gap
            + linkedin_qr.height
            - qr_quiet_zone
        )
        qr_label_y = ((screen.height - qr_group_height) / 2) + 8
        qr_visible_top = qr_label_y + qr_label_height + qr_label_gap
        qr_x = screen.width - content_left - linkedin_qr.width + 10
        qr_y = qr_visible_top - qr_quiet_zone

        screen.blit(linkedin_qr, vec2(qr_x, qr_y))
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
        header_y = card_y + content_y_offset
        screen.text(id_name, header_x, header_y)
        screen.blit(
            name_rocket,
            vec2(
                header_x + header_width + header_gap,
                header_y + ((header_height - name_rocket.height) / 2),
            ),
        )
        screen.font = role_font

        qr_quiet_zone = 12
        qr_label_gap = 4
        qr_label_line_gap = 1
        qr_label_lines = ("WEBSITE",)
        _, social_label_height = screen.measure_text("SOCIALS")
        qr_label_sizes = [screen.measure_text(line) for line in qr_label_lines]
        qr_visible_height = social_qr.height - (qr_quiet_zone * 2)
        social_content_height = qr_visible_height + qr_label_gap + social_label_height
        content_top = card_y + content_y_offset + 44

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
        qr_vertical_offset = 12
        qr_visible_top = content_top - 5 + qr_vertical_offset
        qr_y = qr_visible_top - qr_quiet_zone
        screen.blit(social_qr, vec2(qr_x, qr_y))
        qr_label_y = qr_visible_top + qr_visible_height + qr_label_gap
        screen.font = role_font
        for line, (line_width, line_height) in zip(qr_label_lines, qr_label_sizes):
            line_x = qr_x + ((social_qr.width - line_width) / 2)
            screen.text(line, line_x, qr_label_y)
            qr_label_y += line_height + qr_label_line_gap

    draw_battery_indicator(battery_level)
    draw_screen_border()
    badge.update()
    rtc.set_alarm(minutes=battery_refresh_minutes)
    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    rtc.clear_alarm()


run(update)

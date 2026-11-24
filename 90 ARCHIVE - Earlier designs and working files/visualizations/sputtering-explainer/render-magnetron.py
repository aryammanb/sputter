import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

folder = Path(__file__).parent
sys.path.insert(0, str(folder / "video-deps"))
import imageio_ffmpeg

WIDTH, HEIGHT, FPS = 1280, 720, 24
BACKGROUND = (18, 23, 31)
TEXT = (240, 244, 249)
MUTED = (174, 188, 206)
COLORS = {
    "shield": (87, 190, 131), "ring": (98, 156, 244),
    "target": (204, 215, 233), "cathode": (233, 164, 94),
    "magnet": (180, 145, 237), "yoke": (140, 155, 174),
    "isolation": (235, 205, 125), "flange": (140, 155, 174),
}
FONT_DIR = Path("C:/Windows/Fonts")
title_font = ImageFont.truetype(str(FONT_DIR / "segoeuib.ttf"), 38)
caption_font = ImageFont.truetype(str(FONT_DIR / "segoeui.ttf"), 26)
small_font = ImageFont.truetype(str(FONT_DIR / "segoeui.ttf"), 21)

# The original oblique view uses a 0.40 ellipse ratio and 3 units per mm.
# The shield lift, sideways slide and stack separation use its slider geometry.
SCENES = [
    (0, 4, "Assembled magnetron", "A single 2-inch aluminum target faces the substrate.", None),
    (4, 9, "Grounded shield", "The inward lip covers the powered clamp.\nThe shield seats directly on the grounded flange.", "shield"),
    (9, 14, "Retaining ring", "Three screws draw the ring down so its inner lip\npresses the target against the copper seat.", "ring"),
    (14, 19, "Aluminum target", "Argon ions knock aluminum atoms from the exposed face.\nThose atoms can reach the substrate and build a film.", "target"),
    (19, 24, "Water-cooled copper cathode", "Copper carries power to the target and conducts heat\nto the coolant. The coolant connections are schematic.", "cathode"),
    (24, 29, "Permanent magnets", "The center and outer poles shape a field above the target.\nThe field keeps electrons near the circular erosion track.", "magnet"),
    (29, 34, "Steel yoke", "The steel plate behind the magnets provides\na return path for magnetic flux.", "yoke"),
    (34, 39, "Ceramic isolation", "The ceramic electrically separates the powered cathode\nfrom the grounded mounting flange.", "isolation"),
    (39, 44, "Grounded mounting flange", "The flange mounts the gun to the chamber and provides\na direct metal contact for the shield.", "flange"),
    (44, 50, "Reassembly", "The rear stack and target come together.\nThe shield lowers back onto the flange.", None),
    (50, 57, "Argon plasma forms", "Electrons ionize the low-pressure argon. Positive ions\naccelerate toward the negatively biased aluminum target.", None),
]

def smooth(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)

def mix(first, second, fraction):
    return tuple(round(a + (b - a) * fraction) for a, b in zip(first, second))

def frame(time):
    _, _, title, caption, focus = next(scene for scene in SCENES if time < scene[1])
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    pen = ImageDraw.Draw(image)
    if time < 6:
        gap = .5 * smooth((time - 4) / 2)
    elif time < 44:
        gap = .5 + .5 * smooth((time - 9) / 2.8)
    elif time < 50:
        gap = 1 - smooth((time - 44) / 5.5)
    else:
        gap = 0

    lift = min(1, gap / .20)
    slide = max(0, min(1, (gap - .20) / .30))
    separation = max(0, (gap - .50) / .50)
    shield_x = slide * 240
    shield_y = 215 - lift * 108
    scale = 1.34 - .40 * smooth((gap - .1) / .9)
    cx = WIDTH / 2 - shield_x * scale / 2
    center_y = 266 + 2 * separation
    def project(x, y):
        return (cx + x * scale, center_y + (y - 274) * scale)

    def arc(radius, y, front, x=0):
        return [project(x + radius * math.cos(math.pi * i / 64),
                        y + radius * .40 * math.sin(math.pi * i / 64) * (1 if front else -1))
                for i in range(65)]

    def surface(points, part, side=False):
        strength = .76 if side else .50
        if focus and part != focus:
            strength *= .65
        color = COLORS[part]
        pen.polygon(points, fill=mix(BACKGROUND, color, strength))
        pen.line(points + [points[0]], fill=mix(BACKGROUND, color, .94 if part == focus else .58),
                 width=2 if part == focus else 1)

    def cylinder(part, radius, y, depth, hole=0, x=0):
        front = arc(radius, y, True, x)
        back = arc(radius, y, False, x)
        surface(front + arc(radius, y + depth, True, x)[::-1], part, True)
        if hole:
            inner_back = arc(hole, y, False, x)
            surface(inner_back + arc(hole, y + depth, False, x)[::-1], part, True)
            for outer, half in [(front, True), (back, False)]:
                surface(outer + arc(hole, y, half, x)[::-1], part)
        else:
            surface(front + back[::-1], part)

    def shield(front):
        radius = 119 if front else 109.2
        surface(arc(radius, shield_y, front, shield_x) +
                arc(radius, shield_y + 92, front, shield_x)[::-1], "shield", True)
        if not front:
            surface(arc(70.2, shield_y, False, shield_x) +
                    arc(70.2, shield_y + 6, False, shield_x)[::-1], "shield", True)
        surface(arc(119, shield_y, front, shield_x) +
                arc(70.2, shield_y, front, shield_x)[::-1], "shield")
        if front:
            pen.line(arc(119, shield_y + 92, True, shield_x), fill=(127, 174, 155), width=2)

    body_y = 244
    target_y = body_y - 8 - separation * 88
    ring_y = target_y - 6 - separation * 68
    magnet_y = body_y + 24 + separation * 72
    yoke_y = magnet_y + 16 + separation * 24
    isolation_y = yoke_y + 9 + separation * 42
    flange_y = 307 + separation * 174
    cylinder("flange", 124, flange_y, 17, 57)
    cylinder("isolation", 78, isolation_y, 14, 56)
    cylinder("yoke", 87, yoke_y, 9)
    cylinder("magnet", 82, magnet_y, 16, 62)
    cylinder("magnet", 27, magnet_y, 16)
    shield(False)
    cylinder("cathode", 103.2, body_y, 24)
    cylinder("target", 76.2, target_y, 8)
    cylinder("ring", 103.2, ring_y, 6, 72)
    for angle in [90, 210, 330]:
        theta = math.radians(angle)
        x, y = project(88.2 * math.cos(theta), ring_y + 35.28 * math.sin(theta))
        pen.ellipse((x - 9*scale, y - 3.6*scale, x + 9*scale, y + 3.6*scale),
                    fill=BACKGROUND, outline=COLORS["ring"], width=1)
        pen.line((x-3, y, x+3, y), fill=MUTED)
    shield(True)

    if time >= 50:
        strength = smooth((time - 50) / 1.5)
        glow_y = shield_y - 11
        for radius, weight in [(63, 5), (60, 8), (56, 4)]:
            trace = arc(radius, glow_y, True) + arc(radius, glow_y, False)[::-1]
            pen.line(trace, fill=mix((98, 78, 153), (211, 172, 255), strength),
                     width=max(1, round(weight * strength)))
        for i in range(22):
            angle = i * math.tau / 22
            rise = ((time - 50) * .55 + i * .37) % 1
            x, y = project(59 * math.cos(angle), glow_y + 23.6 * math.sin(angle) - 34 * rise)
            radius = 1 + 2 * strength * (1 - rise)
            pen.ellipse((x-radius, y-radius, x+radius, y+radius),
                        fill=mix(BACKGROUND, (218, 176, 255), strength * (1 - .55 * rise)))
        pen.text((WIDTH / 2, 98), "Plasma shown schematically", font=small_font, fill=MUTED, anchor="mm")

    pen.text((64, 42), "2-INCH SPUTTER MAGNETRON", font=small_font, fill=MUTED)
    pen.line((64, 564, WIDTH - 64, 564), fill=(65, 78, 96), width=1)
    if focus:
        pen.ellipse((64, 588, 82, 606), fill=COLORS[focus])
    pen.text((96 if focus else 64, 572), title, font=title_font, fill=TEXT)
    pen.multiline_text((64, 627), caption, font=caption_font, fill=MUTED, spacing=4)
    return image

if __name__ == "__main__":
    out = folder / "magnetron-exploded-walkthrough.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as encoder:
        for i in range(57 * FPS):
            encoder.stdin.write(frame(i / FPS).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise SystemExit("Video encoding failed")


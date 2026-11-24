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
    (50, 57, "Establish the discharge", "The chamber is evacuated, then fed low-pressure argon.\nA DC supply biases the aluminum target negative relative to ground.", None),
    (57, 65, "Confine electrons near the target", "The magnets bend electron paths near the target, increasing the chance\nof collisions that ionize argon. The glow forms above the erosion track.", None),
    (65, 73, "Argon ions strike the aluminum", "The electric field accelerates positive argon ions toward the target.\nTheir impacts eject aluminum atoms from the surface.", None),
    (73, 83, "Aluminum builds a film", "Some ejected aluminum atoms reach the facing wafer and stick.\nAs more atoms arrive, they build a thin film on its exposed face.", None),
    (83, 90, "From target to thin film", "The magnet pack localizes the discharge, the cooled cathode removes heat,\nand the grounded shield helps keep the powered clamp out of the plasma.", None),
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
    center_y = 266 + 2 * separation + 132 * smooth((time - 50) / 1.4)
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

    if focus:
        anchors = {"shield": (shield_x - 119, shield_y + 47), "ring": (-103.2, ring_y),
                   "target": (-76.2, target_y), "cathode": (-103.2, body_y + 12),
                   "magnet": (-82, magnet_y + 8), "yoke": (-87, yoke_y + 4),
                   "isolation": (-78, isolation_y + 7), "flange": (-124, flange_y + 8)}
        labels = {"shield": "Grounded shield", "ring": "Three-screw clamp",
                  "target": "Aluminum disc", "cathode": "Copper cooling body",
                  "magnet": "Opposite magnetic poles", "yoke": "Magnetic return",
                  "isolation": "Electrical insulation", "flange": "Chamber mount"}
        x, y = project(*anchors[focus])
        # Put the shield label outside the shield; label the stack from the left.
        if focus == "shield":
            x, y = project(shield_x + 119, shield_y + 47)
            direction = 1
        else:
            direction = -1
        tip = x + 38 * direction
        pen.line((x, y, tip, y), fill=COLORS[focus], width=2)
        pen.ellipse((x-3, y-3, x+3, y+3), fill=COLORS[focus])
        pen.text((tip + 10 * direction, y), labels[focus], font=small_font,
                 anchor="lm" if direction == 1 else "rm", fill=TEXT)

    if time >= 50:
        draw_process(pen, project, arc, time, target_y, shield_y, scale)
    pen.text((64, 42), "2-INCH SPUTTER MAGNETRON", font=small_font, fill=MUTED)
    pen.line((64, 564, WIDTH - 64, 564), fill=(65, 78, 96), width=1)
    if focus:
        pen.ellipse((64, 588, 82, 606), fill=COLORS[focus])
    pen.text((96 if focus else 64, 572), title, font=title_font, fill=TEXT)
    pen.multiline_text((64, 627), caption, font=caption_font, fill=MUTED, spacing=4)
    return image

def draw_process(pen, project, arc, time, target_y, shield_y, scale):
    wafer_y = target_y - 150
    top = arc(76.2, wafer_y, True) + arc(76.2, wafer_y, False)[::-1]
    lower = arc(76.2, wafer_y + 5, True)
    pen.polygon(arc(76.2, wafer_y, True) + lower[::-1], fill=(96, 118, 145))
    pen.polygon(top, fill=(137, 157, 183), outline=(203, 216, 232))
    film = smooth((time - 76) / 7)
    if film:
        pen.line(lower, fill=mix((96, 118, 145), (255, 213, 140), film), width=4)

    wafer_x, wafer_screen_y = project(76.2, wafer_y)
    pen.line((wafer_x + 6, wafer_screen_y, wafer_x + 42, wafer_screen_y), fill=MUTED, width=1)
    pen.text((wafer_x + 52, wafer_screen_y), "Wafer" if film < .2 else "Wafer with aluminum film",
             font=small_font, fill=TEXT, anchor="lm")

    strength = smooth((time - 53) / 2.5)
    glow_y = shield_y - 9
    if strength:
        for radius, color, weight in [(64, (94, 66, 140), 9), (60, (151, 106, 219), 7),
                                      (58, (215, 176, 255), 2)]:
            trace = arc(radius, glow_y, True) + arc(radius, glow_y, False)[::-1]
            pen.line(trace, fill=mix(BACKGROUND, color, strength), width=weight)

    def particle(x, y, r, color):
        px, py = project(x, y)
        pen.ellipse((px-r, py-r, px+r, py+r), fill=color)

    def key(color, label, y):
        pen.ellipse((903, y-4, 911, y+4), fill=color)
        pen.text((922, y), label, font=small_font, fill=TEXT, anchor="lm")

    if time < 57:
        for x, y in [(-105, -58), (-41, -82), (14, -120), (90, -49), (102, -96),
                     (-77, -122), (42, -72), (-13, -52)]:
            particle(x, target_y + y, 2, (124, 147, 173))
        key((124, 147, 173), "Argon gas", 268)
        key(COLORS["target"], "Negative target", 300)
        key(COLORS["shield"], "Grounded shield", 332)
    elif time < 65:
        for i in range(14):
            phase = i * math.tau / 14 + (time - 57) * 1.35
            particle(59 * math.cos(phase), glow_y + 23.6 * math.sin(phase) - 7, 2.8,
                     (184, 220, 255))
        key((184, 220, 255), "Electrons near the track", 285)
    elif time < 83:
        for i in range(9):
            angle = i * math.tau / 9 + .17
            phase = ((time - 65) * .72 + i * .19) % 1
            x = 57 * math.cos(angle)
            surface_y = target_y + 22.8 * math.sin(angle)
            particle(x, surface_y - 63 * (1 - phase ** 1.5), 3.5, (219, 174, 255))
            if time >= 73:
                phase = ((time - 73) * .53 + i * .29) % 1
                start = target_y + 22.8 * math.sin(angle)
                landing = wafer_y + 5 + 21 * math.sin(angle)
                spread = 1 + (.18 if i % 2 else -.22) * phase
                particle(x * spread, start + (landing - start) * phase, 3, (255, 213, 140))
        key((219, 174, 255), "Argon ions toward target", 285)
        if time >= 73:
            key((255, 213, 140), "Aluminum toward wafer", 317)

    pen.text((64, 520), "Process and particle paths shown schematically", font=small_font, fill=MUTED)

if __name__ == "__main__":
    out = folder / "magnetron-how-sputtering-works.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as encoder:
        for i in range(90 * FPS):
            encoder.stdin.write(frame(i / FPS).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise SystemExit("Video encoding failed")

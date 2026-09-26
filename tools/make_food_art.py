"""Generate lightweight editorial-style food and place illustrations.

These are intentionally illustrative (not photographs) so the roadbook can
label them honestly as reference art while still matching every stop.
"""

from __future__ import annotations

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 720, 540
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images")

PAPER = (247, 245, 239)
INK = (23, 52, 58)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def new_board(top, bottom, angle=90):
    img = Image.new("RGB", (W, H), top)
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=lerp(top, bottom, y / (H - 1)))
    img = grad

    noise = Image.new("L", (W, H), 0)
    nd = ImageDraw.Draw(noise)
    rng = random.Random(7)
    for _ in range(9000):
        x = rng.randrange(W)
        y = rng.randrange(H)
        nd.point((x, y), fill=rng.randrange(4, 16))
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img, noise.point(lambda v: v * 3))
    return img


def soft_shadow(img, box, radius=26, alpha=70, offset=(0, 14)):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.ellipse(
        [x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]],
        fill=(12, 26, 28, alpha),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.alpha_composite(layer)


def plate(img, d, cx, cy, rx, ry, rim="#ffffff", inner="#f4efe4", shadow=True):
    if shadow:
        soft_shadow(img, (cx - rx, cy - ry, cx + rx, cy + ry), radius=22, alpha=64)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rim)
    d.ellipse(
        [cx - rx * 0.82, cy - ry * 0.82, cx + rx * 0.82, cy + ry * 0.82],
        fill=inner,
    )


def bowl(img, d, cx, cy, rx, ry, outer, inner):
    soft_shadow(img, (cx - rx, cy - ry, cx + rx, cy + ry), radius=24, alpha=72)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=outer)
    d.ellipse(
        [cx - rx * 0.86, cy - ry * 0.8, cx + rx * 0.86, cy + ry * 0.8],
        fill=inner,
    )


def steam(d, cx, cy, count=3):
    for i in range(count):
        x = cx + (i - (count - 1) / 2) * 46
        pts = []
        for step in range(26):
            t = step / 25
            pts.append((x + math.sin(t * math.pi * 1.6 + i) * 16 * (1 - t * 0.4), cy - t * 150))
        d.line(pts, fill=(255, 255, 255, 130), width=9, joint="curve")


def scallion(d, cx, cy, size=12, color=(97, 150, 74)):
    d.ellipse([cx - size, cy - size * 0.55, cx + size, cy + size * 0.55], fill=color)
    d.ellipse(
        [cx - size * 0.62, cy - size * 0.34, cx + size * 0.62, cy + size * 0.34],
        fill=lerp(color, (255, 255, 255), 0.28),
    )


def make_shaomai(img):
    img.paste(new_board((244, 239, 228), (228, 218, 200)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 34, 300, 210)
    base_y = H / 2 + 30
    for i, (x, y, s) in enumerate(
        [(250, base_y - 60, 1.0), (360, base_y - 86, 1.05), (470, base_y - 52, 0.98), (310, base_y + 46, 1.02), (420, base_y + 44, 0.96)]
    ):
        r = 62 * s
        soft_shadow(img, (x - r, y - r * 0.6, x + r, y + r * 0.8), radius=14, alpha=48, offset=(0, 10))
        d.ellipse([x - r, y - r * 0.72, x + r, y + r * 0.72], fill=(245, 235, 214))
        d.polygon(
            [
                (x - r * 0.62, y + r * 0.18),
                (x - r * 0.30, y - r * 0.78),
                (x, y - r * 0.36),
                (x + r * 0.32, y - r * 0.80),
                (x + r * 0.62, y + r * 0.16),
            ],
            fill=(240, 226, 200),
        )
        d.ellipse([x - r * 0.34, y - r * 0.66, x + r * 0.34, y - r * 0.10], fill=(232, 186, 96))
        d.ellipse([x - r * 0.2, y - r * 0.56, x + r * 0.16, y - r * 0.24], fill=(244, 214, 143))
    steam(d, W / 2, H / 2 - 96, 3)


def make_noodle(img):
    img.paste(new_board((238, 233, 222), (222, 212, 194)))
    d = ImageDraw.Draw(img, "RGBA")
    bowl(img, d, W / 2, H / 2 + 40, 286, 194, (39, 66, 74), (216, 176, 112))
    for k in range(26):
        t = k / 25
        y = H / 2 - 84 + t * 176
        amp = 26 * math.sin(t * math.pi)
        pts = []
        for step in range(40):
            p = step / 39
            pts.append(
                (
                    W / 2 - 230 * (1 - t * 0.24) + p * 460 * (1 - t * 0.24),
                    y + math.sin(p * math.pi * 5 + k * 0.7) * amp * 0.5,
                )
            )
        d.line(pts, fill=lerp((235, 206, 150), (206, 163, 96), t), width=13, joint="curve")
    for x, y in [(300, 214), (392, 258), (446, 214), (268, 292), (420, 336)]:
        d.ellipse([x - 30, y - 18, x + 30, y + 18], fill=(122, 63, 40))
        d.ellipse([x - 22, y - 12, x + 22, y + 12], fill=(170, 96, 58))
    for x, y in [(330, 190), (430, 300), (280, 350), (470, 250)]:
        scallion(d, x, y, 16)
    steam(d, W / 2, H / 2 - 92, 3)


def make_casserole(img):
    img.paste(new_board((240, 235, 224), (224, 214, 196)))
    d = ImageDraw.Draw(img, "RGBA")
    soft_shadow(img, (W / 2 - 290, H / 2 - 150, W / 2 + 290, H / 2 + 214), radius=28, alpha=78)
    d.ellipse([W / 2 - 300, H / 2 - 170, W / 2 + 300, H / 2 + 200], fill=(58, 60, 66))
    d.ellipse([W / 2 - 268, H / 2 - 142, W / 2 + 268, H / 2 + 168], fill=(122, 74, 48))
    d.ellipse([W / 2 - 240, H / 2 - 120, W / 2 + 240, H / 2 + 146], fill=(176, 108, 62))
    rng = random.Random(21)
    for _ in range(46):
        ang = rng.uniform(0, math.tau)
        rad = rng.uniform(0, 1) ** 0.6
        x = W / 2 + math.cos(ang) * 218 * rad
        y = H / 2 + 12 + math.sin(ang) * 124 * rad
        r = rng.uniform(20, 40)
        tone = rng.choice([(228, 176, 96), (196, 132, 74), (150, 92, 56), (232, 208, 150)])
        d.ellipse([x - r, y - r * 0.62, x + r, y + r * 0.62], fill=tone)
    for _ in range(12):
        ang = rng.uniform(0, math.tau)
        x = W / 2 + math.cos(ang) * 150
        y = H / 2 + math.sin(ang) * 84
        scallion(d, x, y, rng.uniform(12, 20))
    steam(d, W / 2, H / 2 - 130, 3)


def make_tofu(img):
    img.paste(new_board((242, 237, 226), (226, 216, 198)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 40, 292, 204, rim=(244, 240, 228), inner=(236, 228, 208))
    cubes = [
        (256, 246, 74), (368, 214, 78), (474, 266, 70),
        (300, 348, 76), (418, 358, 72), (536, 350, 54),
    ]
    for x, y, s in cubes:
        soft_shadow(img, (x - s, y - s * 0.7, x + s, y + s * 0.8), radius=12, alpha=52, offset=(0, 8))
        d.polygon([(x - s, y - s * 0.36), (x, y - s * 0.9), (x + s, y - s * 0.36), (x, y + s * 0.2)], fill=(240, 190, 92))
        d.polygon([(x - s, y - s * 0.36), (x, y + s * 0.2), (x, y + s * 0.86), (x - s, y + s * 0.28)], fill=(198, 140, 60))
        d.polygon([(x + s, y - s * 0.36), (x, y + s * 0.2), (x, y + s * 0.86), (x + s, y + s * 0.28)], fill=(166, 110, 48))
    for x, y in [(214, 320), (470, 202), (346, 176), (556, 258)]:
        scallion(d, x, y, 15, color=(96, 140, 70))
    steam(d, W / 2, H / 2 - 96, 2)


def make_popsicle(img):
    img.paste(new_board((242, 238, 228), (226, 218, 200)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 48, 264, 186, rim=(246, 241, 230), inner=(238, 230, 212))
    for offset, tone in [(-118, (226, 190, 108)), (0, (214, 168, 92)), (118, (236, 206, 138))]:
        x = W / 2 + offset
        y = H / 2 - 6
        soft_shadow(img, (x - 54, y - 140, x + 54, y + 136), radius=14, alpha=54, offset=(0, 10))
        d.rounded_rectangle([x - 52, y - 138, x + 52, y + 66], radius=34, fill=tone)
        d.rounded_rectangle([x - 40, y - 126, x + 6, y - 30], radius=24, fill=lerp(tone, (255, 255, 255), 0.32))
        d.rounded_rectangle([x - 16, y + 66, x + 16, y + 156], radius=14, fill=(196, 168, 122))
    steam(d, W / 2, H / 2 - 130, 1)


def make_duck(img):
    img.paste(new_board((240, 234, 222), (222, 210, 190)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 42, 296, 206, rim=(248, 243, 232), inner=(238, 228, 206))
    pieces = [
        (270, 254, 122, 82, 6), (392, 222, 132, 86, -8), (486, 288, 112, 74, 12),
        (322, 358, 118, 78, -4), (444, 380, 104, 68, 8),
    ]
    for x, y, w, h, angle in pieces:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(126, 64, 38))
        ld.ellipse([x - w / 2 + 8, y - h / 2 + 8, x + w / 2 - 10, y + h / 2 - 12], fill=(172, 96, 54))
        ld.ellipse([x - w * 0.2, y - h * 0.34, x + w * 0.38, y + h * 0.1], fill=(208, 148, 92))
        layer = layer.rotate(angle, resample=Image.BICUBIC, center=(x, y))
        img.alpha_composite(layer)
    d.rounded_rectangle([W / 2 - 210, H - 96, W / 2 + 210, H - 44], radius=24, fill=(206, 178, 124))
    for i in range(9):
        x = W / 2 - 180 + i * 44
        scallion(d, x, H - 70, 12, color=(160, 140, 84))


def make_cake(img):
    img.paste(new_board((245, 238, 232), (232, 218, 210)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 44, 288, 202, rim=(250, 246, 238), inner=(244, 236, 222))
    for i, (x, y, s) in enumerate(
        [(276, 246, 1.0), (392, 220, 0.94), (500, 282, 0.9), (322, 360, 0.96), (444, 372, 0.88)]
    ):
        r = 74 * s
        soft_shadow(img, (x - r, y - r * 0.7, x + r, y + r * 0.8), radius=12, alpha=46, offset=(0, 9))
        d.polygon(
            [(x, y - r * 0.92), (x + r * 0.96, y + r * 0.1), (x, y + r * 0.86), (x - r * 0.96, y + r * 0.1)],
            fill=(232, 158, 172),
        )
        d.polygon(
            [(x, y - r * 0.92), (x + r * 0.96, y + r * 0.1), (x, y + r * 0.3), (x - r * 0.2, y - r * 0.1)],
            fill=(246, 196, 204),
        )
        d.ellipse([x - r * 0.22, y - r * 0.2, x + r * 0.22, y + r * 0.22], fill=(190, 96, 112))
    steam(d, W / 2, H / 2 - 110, 2)


def make_pancake(img):
    img.paste(new_board((242, 236, 224), (226, 214, 194)))
    d = ImageDraw.Draw(img, "RGBA")
    plate(img, d, W / 2, H / 2 + 44, 286, 200, rim=(248, 244, 234), inner=(240, 232, 214))
    for x, y, r in [(300, 262, 106), (430, 236, 98), (392, 358, 102)]:
        soft_shadow(img, (x - r, y - r * 0.7, x + r, y + r * 0.8), radius=14, alpha=52, offset=(0, 10))
        d.ellipse([x - r, y - r * 0.74, x + r, y + r * 0.74], fill=(224, 176, 96))
        d.ellipse([x - r * 0.82, y - r * 0.6, x + r * 0.82, y + r * 0.6], fill=(238, 196, 118))
        for k in range(7):
            ang = k * 0.9
            d.line(
                [
                    (x + math.cos(ang) * r * 0.2, y + math.sin(ang) * r * 0.14),
                    (x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.5),
                ],
                fill=(198, 148, 78),
                width=8,
            )
    for x, y in [(232, 344), (486, 202), (330, 210)]:
        scallion(d, x, y, 13, color=(110, 152, 78))


def make_waterway(img):
    sky_bottom = (216, 232, 228)
    img.paste(new_board((208, 228, 226), sky_bottom))
    dd = ImageDraw.Draw(img, "RGBA")
    dd.rectangle([0, int(H * 0.46), W, H], fill=(122, 164, 168))
    for i in range(28):
        y = int(H * 0.48) + i * 4
        dd.line([(0, y), (W, y + math.sin(i) * 2)], fill=(255, 255, 255, 26), width=2)
    for x, w, h, tone in [
        (40, 200, 150, (238, 236, 226)), (268, 190, 128, (228, 226, 214)), (492, 210, 168, (240, 238, 228)),
    ]:
        top = int(H * 0.46) - h
        dd.rectangle([x, top, x + w, int(H * 0.52)], fill=tone)
        dd.polygon([(x - 22, top), (x + w / 2, top - 54), (x + w + 22, top)], fill=(96, 94, 92))
        for wx in range(x + 24, x + w - 20, 52):
            dd.rectangle([wx, top + 32, wx + 26, top + 62], fill=(86, 122, 132))
            dd.rectangle([wx, top + 82, wx + 26, top + 112], fill=(86, 122, 132))
    boat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(boat)
    bd.ellipse([236, 372, 486, 428], fill=(84, 62, 46))
    bd.polygon([(258, 372), (466, 372), (430, 344), (292, 344)], fill=(150, 108, 72))
    bd.line([(300, 368), (410, 260)], fill=(96, 74, 52), width=7)
    img.alpha_composite(boat)


def make_mountain(img):
    img.paste(new_board((198, 224, 230), (222, 238, 232)))
    dd = ImageDraw.Draw(img, "RGBA")
    layers = [
        (int(H * 0.66), (118, 150, 140), 0.9),
        (int(H * 0.72), (86, 122, 116), 1.1),
        (int(H * 0.80), (58, 92, 90), 1.3),
    ]
    for base, tone, scale in layers:
        pts = [(0, H)]
        for x in range(0, W + 1, 30):
            y = base - (math.sin(x / 130 * scale + scale) * 46 + math.sin(x / 61) * 18)
            pts.append((x, y))
        pts.append((W, H))
        dd.polygon(pts, fill=tone)
    dd.rectangle([0, int(H * 0.74), W, H], fill=(126, 168, 168, 200))
    for i in range(3):
        x = 210 + i * 150
        dd.polygon(
            [(x, 330), (x + 34, 250), (x + 68, 330)],
            fill=(236, 244, 244, 235),
        )
        dd.polygon(
            [(x + 18, 330), (x + 40, 288), (x + 62, 330)],
            fill=(210, 232, 232, 245),
        )


def make_palace(img):
    img.paste(new_board((236, 224, 200), (214, 190, 158)))
    dd = ImageDraw.Draw(img, "RGBA")
    dd.rectangle([0, int(H * 0.7), W, H], fill=(196, 168, 132))
    for x, w, h in [(120, 200, 210), (300, 240, 250), (500, 160, 190)]:
        top = int(H * 0.72) - h
        dd.rectangle([x, top, x + w, int(H * 0.74)], fill=(178, 72, 58))
        dd.polygon([(x - 30, top), (x + w / 2, top - 62), (x + w + 30, top)], fill=(120, 60, 46))
        for wx in range(x + 30, x + w - 20, 64):
            dd.rectangle([wx, top + 48, wx + 34, top + 92], fill=(226, 196, 118))
            dd.rectangle([wx, top + 122, wx + 34, top + 166], fill=(226, 196, 118))


GENERATORS = {
    "food-shaomai.png": make_shaomai,
    "food-noodle.png": make_noodle,
    "food-casserole.png": make_casserole,
    "food-tofu.png": make_tofu,
    "food-popsicle.png": make_popsicle,
    "food-duck.png": make_duck,
    "food-cake.png": make_cake,
    "food-pancake.png": make_pancake,
    "place-waterway.png": make_waterway,
    "place-mountain.png": make_mountain,
    "place-palace.png": make_palace,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, builder in GENERATORS.items():
        canvas = Image.new("RGBA", (W, H), (247, 245, 239, 255))
        builder(canvas)
        path = os.path.join(OUT, name)
        canvas.convert("RGB").save(path, "PNG", optimize=True)
        print("wrote", path, os.path.getsize(path))


if __name__ == "__main__":
    main()

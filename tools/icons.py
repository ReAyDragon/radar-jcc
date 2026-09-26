#!/usr/bin/env python3
"""Draw the Radar JCC app icons (original artwork: radar rings + a trading card)."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "icons"
OUT.mkdir(exist_ok=True)
S = 1024  # master size


def gradient(size):
    y, x = np.mgrid[0:size, 0:size] / (size - 1)
    t = (x * 0.55 + y * 0.45)
    stops = [(0.0, (47, 75, 214)), (0.55, (122, 79, 224)), (1.0, (31, 167, 176))]
    img = np.zeros((size, size, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = ((t - t0) / (t1 - t0))[m][:, None]
        img[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return Image.fromarray(img.astype("uint8"), "RGB").convert("RGBA")


def art(size, scale):
    """Radar + card artwork on a transparent layer, content scaled by `scale`."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size / 2
    u = size * scale  # content unit

    # sweep wedge
    sweep = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    r = 0.40 * u
    sd.pieslice([c - r, c - r, c + r, c + r], start=-95, end=-25, fill=(255, 255, 255, 70))
    sweep = sweep.filter(ImageFilter.GaussianBlur(size * 0.004))
    layer.alpha_composite(sweep)

    # rings
    for rr, a in ((0.20, 150), (0.30, 120), (0.40, 95)):
        R = rr * u
        d.ellipse([c - R, c - R, c + R, c + R], outline=(255, 255, 255, a), width=max(2, int(0.016 * u)))

    # card (tilted rounded rectangle)
    cw, ch = 0.25 * u, 0.35 * u
    card = Image.new("RGBA", (int(cw * 1.6), int(ch * 1.6)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    ox, oy = (card.width - cw) / 2, (card.height - ch) / 2
    rad = 0.03 * u
    cd.rounded_rectangle([ox, oy, ox + cw, oy + ch], radius=rad, fill=(255, 255, 255, 255))
    m = 0.022 * u
    cd.rounded_rectangle([ox + m, oy + m, ox + cw - m, oy + ch * 0.58], radius=rad * 0.5, fill=(222, 228, 252, 255))
    # holo stripe inside the art window
    cd.polygon([(ox + m, oy + ch * 0.46), (ox + cw - m, oy + ch * 0.22), (ox + cw - m, oy + ch * 0.32), (ox + m, oy + ch * 0.56)],
               fill=(165, 140, 240, 255))
    for i, w in enumerate((0.62, 0.44)):
        y0 = oy + ch * (0.66 + i * 0.1)
        cd.rounded_rectangle([ox + m, y0, ox + m + (cw - 2 * m) * w, y0 + 0.022 * u], radius=0.011 * u, fill=(47, 75, 214, 255))
    card = card.rotate(-12, resample=Image.BICUBIC, expand=False)
    shadow = card.split()[3].point(lambda v: v * 0.35)
    sh = Image.new("RGBA", card.size, (10, 12, 40, 0))
    sh.putalpha(shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.012))
    px, py = int(c - card.width / 2), int(c - card.height / 2 + 0.01 * u)
    layer.alpha_composite(sh, (px + int(0.012 * u), py + int(0.02 * u)))
    layer.alpha_composite(card, (px, py))

    # blip
    ang = math.radians(-50)
    R = 0.30 * u
    bx, by = c + R * math.cos(ang), c + R * math.sin(ang)
    br = 0.035 * u
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([bx - br * 2, by - br * 2, bx + br * 2, by + br * 2], fill=(242, 184, 75, 110))
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(size * 0.01)))
    d = ImageDraw.Draw(layer)
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 205, 96, 255))
    return layer


def make(full_bleed, scale, rounded):
    img = gradient(S)
    img.alpha_composite(art(S, scale))
    if rounded:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
        out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask)
        img = out
    return img


standard = make(False, 1.0, rounded=True)
maskable = make(True, 0.78, rounded=False)
apple = make(True, 0.9, rounded=False).convert("RGB")

standard.resize((512, 512), Image.LANCZOS).save(OUT / "icon-512.png", optimize=True)
standard.resize((192, 192), Image.LANCZOS).save(OUT / "icon-192.png", optimize=True)
maskable.resize((512, 512), Image.LANCZOS).save(OUT / "icon-maskable-512.png", optimize=True)
apple.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png", optimize=True)
standard.resize((32, 32), Image.LANCZOS).save(OUT / "favicon-32.png", optimize=True)
print("ok", sorted(p.name for p in OUT.iterdir()))

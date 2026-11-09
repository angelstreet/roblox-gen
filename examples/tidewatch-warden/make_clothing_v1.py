#!/usr/bin/env python3
"""Tidewatch Warden - classic shirt + pants texture generator (585x559 RGBA).
UV rectangles come from the official Roblox R15 classic clothing templates.
Usage: python3 make_clothing.py [outdir]
"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)
W, H = 585, 559

# palette
NAVY = (18, 28, 52); NAVY2 = (30, 46, 82); NAVY3 = (10, 16, 32)
PEARL = (232, 238, 240); PEARL2 = (186, 198, 206)
AQUA = (70, 220, 220); AQUA2 = (30, 150, 170)
BRONZE = (196, 142, 74); BRONZE2 = (140, 94, 48)

# face rects (x, y, w, h) from official templates
SHIRT = {
    "t_up": (231, 8, 128, 64), "t_front": (231, 74, 128, 128), "t_back": (427, 74, 128, 128),
    "t_right": (165, 74, 64, 128), "t_left": (361, 74, 64, 128), "t_down": (231, 204, 128, 64),
    "ra_up": (217, 289, 64, 64), "ra_front": (217, 355, 64, 128), "ra_back": (85, 355, 64, 128),
    "ra_right": (151, 355, 64, 128), "ra_left": (19, 355, 64, 128), "ra_down": (217, 485, 64, 64),
    "la_up": (308, 289, 64, 64), "la_front": (308, 355, 64, 128), "la_back": (440, 355, 64, 128),
    "la_right": (506, 355, 64, 128), "la_left": (374, 355, 64, 128), "la_down": (308, 485, 64, 64),
}
# pants use identical layout (legs instead of arms)
PANTS = {k.replace("ra_", "rl_").replace("la_", "ll_"): v for k, v in SHIRT.items()}


def grad(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top)[None, None, :] * (1 - t) + np.array(bot)[None, None, :] * t
    return Image.fromarray(np.broadcast_to(a, (h, w, 3)).astype("uint8"), "RGB")


def noise_overlay(img, amt=6, seed=1):
    rng = np.random.default_rng(seed)
    a = np.array(img.convert("RGB")).astype(int)
    a += rng.integers(-amt, amt + 1, a.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"), "RGB")


def face(w, h, top=NAVY2, bot=NAVY, seed=1):
    return noise_overlay(grad(w, h, top, bot), 5, seed)


def emblem(d, cx, cy, s, col=AQUA, rim=BRONZE):
    """Signature: crescent-wave 'Tidemark' - crescent moon cradling a wave crest + dot."""
    r = s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rim, width=max(2, s // 8))
    d.ellipse([cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62], fill=col)
    d.ellipse([cx - r * .30, cy - r * .78, cx + r * .94, cy + r * .46], fill=NAVY)  # crescent bite
    pts = [(cx - r * .6, cy + r * .5), (cx - r * .2, cy + r * .1), (cx + r * .1, cy + r * .35),
           (cx + r * .45, cy - r * .05), (cx + r * .6, cy + r * .45)]
    d.line(pts, fill=PEARL, width=max(2, s // 9), joint="curve")
    d.ellipse([cx + r * .05, cy - r * .55, cx + r * .27, cy - r * .33], fill=PEARL)


def trim(d, x0, y0, x1, y1, col=BRONZE, w=2):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)


def paste_face(canvas, rect, img):
    x, y, w, h = rect
    canvas.paste(img.resize((w, h)), (x, y))


# ---------------- SHIRT ----------------
def shirt():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seed = 10
    for name, r in SHIRT.items():
        seed += 1
        f = face(r[2], r[3], seed=seed)
        paste_face(c, r, f.convert("RGBA"))
    d = ImageDraw.Draw(c)
    # torso front: pearl inner tunic with V neck, bronze belt zone at bottom (belt ~ y 170-200 local)
    x, y, w, h = SHIRT["t_front"]
    d.polygon([(x + 22, y), (x + w - 22, y), (x + w - 40, y + 70), (x + 40, y + 70)], fill=PEARL)
    d.polygon([(x + 40, y), (x + w - 40, y), (x + w // 2, y + 46)], fill=NAVY3)  # collar V
    d.line([(x + 22, y), (x + 40, y + 70), (x + w // 2, y + 112)], fill=BRONZE, width=3)
    d.line([(x + w - 22, y), (x + w - 40, y + 70), (x + w // 2, y + 112)], fill=BRONZE, width=3)
    d.line([(x + w // 2, y + 46), (x + w // 2, y + 118)], fill=NAVY2, width=2)
    # pauldron-style chest plates
    for sx in (x + 4, x + w - 40):
        d.rounded_rectangle([sx, y + 2, sx + 36, y + 44], 8, fill=NAVY3, outline=BRONZE, width=2)
        d.line([(sx + 6, y + 14), (sx + 30, y + 14)], fill=AQUA2, width=2)
    emblem(d, x + w // 2, y + 82, 14)
    # belt
    d.rectangle([x, y + 108, x + w, y + 128], fill=NAVY3)
    d.line([(x, y + 108), (x + w, y + 108)], fill=BRONZE, width=3)
    d.rectangle([x + w // 2 - 12, y + 108, x + w // 2 + 12, y + 128], fill=BRONZE)
    d.ellipse([x + w // 2 - 6, y + 112, x + w // 2 + 6, y + 124], fill=AQUA)
    # torso back: cape-like panel with big emblem
    x, y, w, h = SHIRT["t_back"]
    d.polygon([(x + 18, y), (x + w - 18, y), (x + w - 30, y + 128), (x + 30, y + 128)], fill=NAVY3)
    d.line([(x + 18, y), (x + 30, y + 128)], fill=BRONZE, width=3)
    d.line([(x + w - 18, y), (x + w - 30, y + 128)], fill=BRONZE, width=3)
    emblem(d, x + w // 2, y + 60, 30)
    for i in range(3):
        d.line([(x + w // 2, y + 98 + i * 7), (x + w // 2, y + 102 + i * 7)], fill=AQUA, width=3)
    d.rectangle([x, y + 108, x + w, y + 128], fill=NAVY3)
    d.line([(x, y + 108), (x + w, y + 108)], fill=BRONZE, width=3)
    # torso sides
    for k in ("t_right", "t_left"):
        x, y, w, h = SHIRT[k]
        d.line([(x + 32, y), (x + 32, y + 108)], fill=NAVY3, width=2)
        d.rectangle([x, y + 108, x + w, y + 128], fill=NAVY3)
        d.line([(x, y + 108), (x + w, y + 108)], fill=BRONZE, width=3)
    # arms: pauldron cap at top, bronze bands, aqua glow stripe, glove (dotted line = y~ local 100)
    for pre in ("ra", "la"):
        for side in ("front", "back", "right", "left"):
            x, y, w, h = SHIRT[f"{pre}_{side}"]
            d.rectangle([x, y, x + w, y + 36], fill=NAVY3)
            d.line([(x, y + 36), (x + w, y + 36)], fill=BRONZE, width=3)
            d.line([(x + 6, y + 14), (x + w - 6, y + 14)], fill=AQUA2, width=2)
            d.line([(x, y + 76), (x + w, y + 76)], fill=BRONZE2, width=2)
            d.line([(x + w // 2, y + 40), (x + w // 2, y + 72)], fill=AQUA2, width=2)
            # gauntlet / glove
            d.rectangle([x, y + 92, x + w, y + 128], fill=PEARL2)
            d.rectangle([x, y + 92, x + w, y + 98], fill=BRONZE)
            d.line([(x + 10, y + 108), (x + w - 10, y + 108)], fill=PEARL, width=2)
        for side in ("up", "down"):
            x, y, w, h = SHIRT[f"{pre}_{side}"]
            d.rectangle([x, y, x + w, y + h], fill=NAVY3 if side == "up" else PEARL2)
    for k in ("t_up", "t_down"):
        x, y, w, h = SHIRT[k]
        d.rectangle([x, y, x + w, y + h], fill=NAVY3)
    return c


# ---------------- PANTS ----------------
def pants():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seed = 40
    for name, r in PANTS.items():
        seed += 1
        paste_face(c, r, face(r[2], r[3], NAVY, NAVY3, seed).convert("RGBA"))
    d = ImageDraw.Draw(c)
    # torso area = hips / waist skirt (front/back/sides top 0..64 local) - belt and tassets
    for k in ("t_front", "t_back"):
        x, y, w, h = PANTS[k]
        d.rectangle([x, y, x + w, y + 20], fill=NAVY3)
        d.line([(x, y + 20), (x + w, y + 20)], fill=BRONZE, width=3)
        # hanging tasset panels
        for px in (x + 8, x + w - 40):
            d.polygon([(px, y + 22), (px + 32, y + 22), (px + 28, y + 112), (px + 16, y + 126), (px + 4, y + 112)], fill=NAVY2, outline=BRONZE)
            d.line([(px + 16, y + 28), (px + 16, y + 100)], fill=AQUA2, width=2)
        d.rectangle([x + w // 2 - 8, y + 26, x + w // 2 + 8, y + 90], fill=PEARL)
        d.line([(x + w // 2, y + 30), (x + w // 2, y + 86)], fill=AQUA, width=2)
        if k == "t_front":
            emblem(d, x + w // 2, y + 106, 10)
    for k in ("t_right", "t_left"):
        x, y, w, h = PANTS[k]
        d.rectangle([x, y, x + w, y + 20], fill=NAVY3)
        d.line([(x, y + 20), (x + w, y + 20)], fill=BRONZE, width=3)
    for k in ("t_up", "t_down"):
        x, y, w, h = PANTS[k]
        d.rectangle([x, y, x + w, y + h], fill=NAVY3)
    # legs: knee guard, bronze greave, boots (dotted line y~ local 100 = max boot height)
    for pre in ("rl", "ll"):
        for side in ("front", "back", "right", "left"):
            x, y, w, h = PANTS[f"{pre}_{side}"]
            d.line([(x + w // 2, y), (x + w // 2, y + 50)], fill=NAVY3, width=2)
            if side in ("front",):
                d.polygon([(x + 12, y + 44), (x + w - 12, y + 44), (x + w - 16, y + 68), (x + w // 2, y + 76), (x + 16, y + 68)], fill=NAVY3, outline=BRONZE)
                d.ellipse([x + w // 2 - 5, y + 52, x + w // 2 + 5, y + 62], fill=AQUA)
            d.line([(x, y + 84), (x + w, y + 84)], fill=BRONZE2, width=2)
            # boots
            d.rectangle([x, y + 92, x + w, y + 128], fill=NAVY3)
            d.rectangle([x, y + 92, x + w, y + 100], fill=BRONZE)
            d.line([(x + 8, y + 112), (x + w - 8, y + 112)], fill=AQUA2, width=2)
        for side in ("up", "down"):
            x, y, w, h = PANTS[f"{pre}_{side}"]
            d.rectangle([x, y, x + w, y + h], fill=NAVY3)
    return c


if __name__ == "__main__":
    s = shirt(); p = pants()
    s.save(os.path.join(OUT, "tidewatch_shirt.png"))
    p.save(os.path.join(OUT, "tidewatch_pants.png"))
    # overlay-on-template check images
    for nm, img, tpl in (("shirt", s, "Template-Shirts-R15.png"), ("pants", p, "Template-Pants-R15.png")):
        tp = os.path.join(os.path.dirname(__file__), "..", "templates_dl", tpl)
        if os.path.exists(tp):
            bg = Image.open(tp).convert("RGBA"); bg.alpha_composite(img)
            bg.save(os.path.join(OUT, f"check_{nm}_on_template.png"))
    print("wrote", OUT, s.size, p.size)

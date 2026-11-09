#!/usr/bin/env python3
"""Crystal Vanguard - classic shirt + pants (585x559) painted on the official template rectangles.
Reuses the 4x Face painter from ../tidewatch-warden/make_clothing.py (copied next to this file as make_clothing.py).
Usage: python3 make_clothing_cv.py  -> out/cv_shirt.png, out/cv_pants.png"""
import os, math
from PIL import Image
from make_clothing import Face, S, SHIRT, PANTS, W, H

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
WHITE_T, WHITE_B = (250, 251, 255), (176, 192, 232)     # silver-white armor  #F8F9FF .. shaded toward #CAD8FF/blue
NAVY_T, NAVY_B = (24, 42, 112), (13, 27, 77)             # deep navy #0D1B4D
DARK_T, DARK_B = (20, 26, 58), (6, 9, 24)
GH, GM, GL = (255, 238, 160), (212, 175, 55), (126, 94, 22)  # gold #D4AF37 ramp
GEM_HI, GEM, GEM_LO = (170, 235, 255), (46, 107, 255), (20, 52, 170)
ICE = (202, 216, 255)


def gold(f, pts, w=2.0):
    f.line(pts, GL, w + 1.0); f.line(pts, GM, w * 0.7); f.line([(x - 0.2, y - 0.3) for x, y in pts], GH, max(0.4, w * 0.25))


def gem(f, cx, cy, r, tall=1.45):
    """faceted diamond gem with gold setting and glow"""
    rt, rb = r * tall, r * tall * 0.9
    f.glowdot(cx, cy, r * 1.1, (60, 150, 255))
    out = [(cx, cy - rt - 1.4), (cx + r + 1.4, cy), (cx, cy + rb + 1.4), (cx - r - 1.4, cy)]
    f.metal(out, top=GH, mid=GM, bot=GL)
    P = [(cx, cy - rt), (cx + r, cy), (cx, cy + rb), (cx - r, cy)]
    f.poly(P, GEM)
    f.poly([P[0], P[1], (cx, cy)], GEM_HI); f.poly([P[0], (cx, cy), P[3]], (96, 180, 255))
    f.poly([P[3], (cx, cy), P[2]], GEM); f.poly([(cx, cy), P[1], P[2]], GEM_LO)
    f.line([(cx - r * .3, cy - rt * .4), (cx - r * .05, cy - rt * .8)], (255, 255, 255), 0.7)


def fil(f, pts):  # thin gold filigree line
    gold(f, pts, 1.0)


def shade(f, pts, amt=150, dy=1.2): f.drop(pts, dy=dy, amt=amt); f.apply_shadow_now()


def plate(f, x0, y0, x1, y1, cut=5):
    poly = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut)]
    shade(f, poly, 170, 1.4)
    f.metal(poly, top=(255, 255, 255), mid=(236, 241, 255), bot=(168, 186, 232), outline_dark=False)
    f.line(poly + [poly[0]], GL, 2.6); f.line(poly + [poly[0]], GM, 1.8); f.line(poly + [poly[0]], GH, 0.6)
    f.line([(x0 + cut + 2, y0 + 4), (x1 - cut - 2, y0 + 4)], (255, 255, 255), 0.8)


def sleeve(f, w, h, seam=False):
    plate(f, 2, 2, w - 2, 56)
    gem(f, w / 2, 29, 5.5, 1.5)
    fil(f, [(8, 12), (w / 2 - 8, 20)]); fil(f, [(w - 8, 12), (w / 2 + 8, 20)])
    fil(f, [(8, 48), (w / 2 - 9, 40)]); fil(f, [(w - 8, 48), (w / 2 + 9, 40)])
    f.grad_rect(0, 58, w, 92, NAVY_T, NAVY_B)                        # navy cuff
    gold(f, [(0, 60), (w, 60)], 2.2); gold(f, [(0, 90), (w, 90)], 1.6)
    for i in range(6, w, 12): fil(f, [(i, 66), (i + 3, 80)])
    gem(f, w / 2, 75, 3.2, 1.3)
    # r5: gauntlet is now navy with gold filigree (was a silver plate), so the sleeve is mostly navy
    f.grad_rect(0, 94, w, 128, NAVY_T, NAVY_B)
    gold(f, [(4, 110), (w - 4, 110)], 1.2)
    for i in range(8, w - 6, 14): fil(f, [(i, 98), (i + 5, 106), (i + 10, 98)]); fil(f, [(i + 3, 118), (i + 8, 124)])


def shirt():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 300
    for name, r in SHIRT.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=WHITE_T, bot=WHITE_B, folds=0.25)
        if name == "t_front":
            cx = w / 2
            # navy under-cloth panel (V) with gold edging
            nav = [(cx - 28, 0), (cx + 28, 0), (cx + 22, 78), (cx, 98), (cx - 22, 78)]
            shade(f, nav, 150); f.metal(nav, top=NAVY_T, mid=NAVY_T, bot=NAVY_B, outline_dark=False)
            gold(f, nav + [nav[0]], 2.0)
            for sg in (-1, 1):                                          # chest plates edged in gold
                pl = [(cx + sg * 30, 0), (cx + sg * 62, 0), (cx + sg * 62, 90), (cx + sg * 24, 80)]
                gold(f, [(cx + sg * 31, 2), (cx + sg * 25, 78)], 1.6)
                fil(f, [(cx + sg * 40, 10), (cx + sg * 52, 30), (cx + sg * 44, 60)]); fil(f, [(cx + sg * 50, 70), (cx + sg * 38, 82), (cx + sg * 30, 76)])
                gem(f, cx + sg * 48, 46, 4, 1.4)
            gem(f, cx, 34, 11, 1.5)
            fil(f, [(cx - 20, 8), (cx - 12, 56), (cx, 78), (cx + 12, 56), (cx + 20, 8)])
            # r5: a few gold swirl lines inside the navy V (concept filigree)
            for sg in (-1, 1): fil(f, [(cx + sg * 6, 14), (cx + sg * 18, 26), (cx + sg * 10, 40), (cx + sg * 20, 52)])
            f.grad_rect(0, 96, w, 108, (214, 224, 250), (150, 168, 214))   # belt
            gold(f, [(0, 96), (w, 96)], 1.8); gold(f, [(0, 108), (w, 108)], 1.8)
            gem(f, cx, 102, 3.6, 1.3)
            for sg in (-1, 1): fil(f, [(cx + sg * 30, 100), (cx + sg * 48, 100)])
            f.grad_rect(cx - 16, 110, cx + 16, 128, NAVY_T, NAVY_B); gold(f, [(cx - 16, 110), (cx - 16, 128)], 1.3); gold(f, [(cx + 16, 110), (cx + 16, 128)], 1.3)
            gold(f, [(0, 126), (w, 126)], 2.0)
        elif name == "t_back":
            cx = w / 2
            plate(f, 4, 4, w - 4, 88, 8); gem(f, cx, 44, 7, 1.6)
            fil(f, [(cx, 6), (cx - 22, 30), (cx - 12, 70)]); fil(f, [(cx, 6), (cx + 22, 30), (cx + 12, 70)])
            f.grad_rect(0, 94, w, 108, NAVY_T, NAVY_B); gold(f, [(0, 94), (w, 94)], 1.8); gold(f, [(0, 108), (w, 108)], 1.8)
            gold(f, [(0, 126), (w, 126)], 2.0)
        elif name in ("t_right", "t_left"):
            gold(f, [(2, 0), (2, 128)], 1.6); gold(f, [(w - 2, 0), (w - 2, 128)], 1.6)
            f.grad_rect(0, 94, w, 108, NAVY_T, NAVY_B); gold(f, [(0, 94), (w, 94)], 1.6); gold(f, [(0, 108), (w, 108)], 1.6)
            gem(f, w / 2, 45, 4, 1.4)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            sleeve(f, w, h)
        elif name == "t_up":
            f.rect(0, 0, w, h, NAVY_T[:3]); gold(f, [(0, h - 1), (w, h - 1)], 2.0)
        elif name.endswith("_up"):
            f.grad_rect(0, 0, w, h, (255, 255, 255), (214, 224, 250)); f.line([(0, 0), (w, 0)], GM, 2)
        elif name.endswith("_down"):
            f.rect(0, 0, w, h, (110, 130, 190))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


def pants():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 400
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=NAVY_T, bot=NAVY_B, folds=0.35)
        if name in ("t_front", "t_back", "t_right", "t_left"):
            f.rect(0, 0, w, h, NAVY_B)
            if name == "t_front":
                cx = w / 2
                for sg in (-1, 1):
                    plate(f, cx + (2 if sg > 0 else -62), 2, cx + (62 if sg > 0 else -2), 72, 6)
                gem(f, cx, 30, 5, 1.4)
            elif name == "t_back": plate(f, 4, 2, w - 4, 72, 8)
            else: plate(f, 4, 2, w - 4, 72, 6)
            f.grad_rect(0, 82, w, 100, NAVY_T, NAVY_B); gold(f, [(0, 82), (w, 82)], 1.8); gold(f, [(0, 100), (w, 100)], 1.8)
            for i in range(10, w, 22): fil(f, [(i, 86), (i + 4, 96)])
            f.grad_rect(0, 101, w, 128, DARK_T, DARK_B)
            for i in range(10, w - 8, 26): fil(f, [(i, 104), (i + 6, 116), (i + 12, 104)])
            gold(f, [(0, 126), (w, 126)], 2.0)
        elif name.endswith("_up"): f.rect(0, 0, w, h, NAVY_B)
        elif name.endswith("_down"): f.rect(0, 0, w, h, (6, 9, 24))
        else:   # legs
            plate(f, 4, 2, w - 4, 42, 5); fil(f, [(10, 12), (w / 2, 34), (w - 10, 12)]); gem(f, w / 2, 20, 4, 1.4)
            for dx in (w * .25, w * .75): f.line([(dx, 44), (dx + 1, 64)], (10, 20, 60), 1.4)
            plate(f, 6, 52, w - 6, 82, 5); gem(f, w / 2, 67, 5, 1.4)          # knee plate
            f.grad_rect(0, 84, w, 98, NAVY_T, NAVY_B)
            f.grad_rect(0, 98, w, 128, DARK_T, DARK_B)                         # boot
            gold(f, [(0, 98), (w, 98)], 2.2); gold(f, [(0, 126), (w, 126)], 2.0)
            fil(f, [(6, 104), (w / 2 - 6, 112), (w / 2, 120)]); fil(f, [(w - 6, 104), (w / 2 + 6, 112), (w / 2, 120)])
            gem(f, w / 2, 108, 3.4, 1.4)
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    shirt().save(os.path.join(OUT, "cv_shirt.png")); pants().save(os.path.join(OUT, "cv_pants.png")); print("wrote", OUT)

#!/usr/bin/env python3
"""Tidewatch Warden - classic shirt + pants v5 (near-black navy, thin bevelled bronze, pearl sparingly).
Reuses the 4x Face painter from make_clothing.py (v2). Usage: python3 make_clothing_v5.py  -> out/v5/
Legs are painted as the lower part of an open robe (front split with bronze piping, double-step hem), so the 3D skirt
and the classic pants read as one long robe.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw
from make_clothing import Face, S, SHIRT, PANTS, W, H

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "v5"); os.makedirs(OUT, exist_ok=True)
C_TOP, C_BOT = (19, 23, 36), (7, 8, 14)            # near-black navy cloth (L* ~ 10-18)
UNDER = (5, 6, 11)                                  # under-robe / shadow
PEARL, PEARL_D = (236, 238, 240), (168, 174, 184)
AQUA = (70, 225, 220)
BR_HI, BR, BR_LO, BR_DK = (255, 222, 150), (206, 146, 66), (122, 78, 30), (40, 24, 10)


def trim(f, pts, w=2.0):
    """thin bevelled bronze piping along a polyline (w in 1x px): dark rim, shadow side, base, highlight side"""
    f.line(pts, BR_DK, w + 1.2)
    f.line([(x + 0.25, y + 0.35) for x, y in pts], BR_LO, w)
    f.line(pts, BR, w * 0.62)
    f.line([(x - 0.22, y - 0.3) for x, y in pts], BR_HI, max(0.35, w * 0.26))


def hband(f, y, w=2.0, x0=0, x1=None):
    trim(f, [(x0, y), (f.w if x1 is None else x1, y)], w)


def shade(f, pts, amt=170, dy=1.0):
    f.drop(pts, dy=dy, amt=amt); f.apply_shadow_now()


def fold(f, x0, y0, x1, y1, k=1.0):
    """soft cloth fold: dark crease plus a faint highlight on the lit side"""
    f.line([(x0, y0), ((x0 + x1) / 2 + 0.6, (y0 + y1) / 2), (x1, y1)], (4, 5, 10), 1.6 * k)
    f.line([(x0 - 1.4, y0), ((x0 + x1) / 2 - 0.8, (y0 + y1) / 2), (x1 - 1.4, y1)], (40, 48, 70), 0.6 * k)


def tidemark(f, cx, cy, r, aqua=True):
    """our emblem: crescent cradling a wave crest, bronze line-work + one aqua dot"""
    d = f.d
    def ring(rr, col, wdt):
        d.arc([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], 25, 335, fill=col + (255,), width=max(1, int(wdt * S)))
    ring(r + 0.6, BR_DK, r * 0.34); ring(r, BR, r * 0.2); ring(r - 0.2, BR_HI, r * 0.06)
    wave = [(cx - r * 0.75 + i * r * 0.15, cy + r * 0.25 - r * 0.35 * math.sin(i / 10 * math.pi * 1.25) - (r * 0.25 if i == 8 else 0)) for i in range(11)]
    f.line(wave, BR_DK, r * 0.26); f.line(wave, BR, r * 0.14)
    if aqua:
        f.glowdot(cx + r * 0.32, cy - r * 0.38, r * 0.22, AQUA)
        d.ellipse([(cx + r * 0.2) * S, (cy - r * 0.5) * S, (cx + r * 0.44) * S, (cy - r * 0.26) * S], fill=AQUA + (255,))


def shirt():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 100
    for name, r in SHIRT.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=C_TOP, bot=C_BOT, folds=0.6)
        if name == "t_front":
            cx = w / 2
            # under-tunic: narrow pearl V framed by dark inner robe
            f.poly([(cx - 22, 0), (cx + 22, 0), (cx, 58)], UNDER)
            f.metal([(cx - 13, 0), (cx + 13, 0), (cx, 44)], top=(250, 250, 252), mid=PEARL, bot=PEARL_D, outline_dark=False)
            f.line([(cx, 2), (cx, 40)], (190, 196, 206), 0.6)
            # crossed lapels (dark, lit edge) with bronze piping
            for sg in (-1, 1):
                lap = [(cx + sg * 13, 0), (cx + sg * 30, 0), (cx + sg * 7, 70), (cx, 76)]
                shade(f, lap, 150, 1.2); f.poly(lap, (20, 25, 40))
                trim(f, [(cx + sg * 13, 0), (cx, 44)], 1.6)
                fold(f, cx + sg * 22, 4, cx + sg * 12, 60, 0.7)
            # chest folds
            for sg in (-1, 1):
                fold(f, cx + sg * 44, 6, cx + sg * 36, 100); fold(f, cx + sg * 58, 20, cx + sg * 54, 104, 0.8)
            # belt: dark leather band, thin double piping, bronze Tidemark clasp
            f.grad_rect(0, 92, w, 106, (20, 22, 32), (6, 7, 12)); hband(f, 92, 1.6); hband(f, 106, 1.6)
            for i in range(2, w, 6): f.line([(i, 99), (i + 3, 99)], (34, 38, 54), 0.5)
            clasp = [(cx - 10, 89), (cx + 10, 89), (cx + 12, 99), (cx, 110), (cx - 12, 99)]
            shade(f, clasp, 220, 1.5); f.metal(clasp, top=BR_HI, mid=BR, bot=BR_LO)
            f.poly([(cx - 6, 93), (cx + 6, 93), (cx + 7, 99), (cx, 105), (cx - 7, 99)], (14, 16, 24))
            f.glowdot(cx, 99, 2.4, AQUA); f.d.ellipse([(cx - 2) * S, 97 * S, (cx + 2) * S, 101 * S], fill=AQUA + (255,))
            # lower torso: robe front opens, bronze edged flaps over a darker under-robe
            f.poly([(cx - 9, 106), (cx + 9, 106), (cx + 13, 128), (cx - 13, 128)], UNDER)
            trim(f, [(cx - 9, 107), (cx - 13, 128)], 1.6); trim(f, [(cx + 9, 107), (cx + 13, 128)], 1.6)
        elif name == "t_back":
            for dx in (-40, -18, 0, 18, 40): fold(f, w / 2 + dx, 2, w / 2 + dx * 1.1, 90, 0.9)
            tidemark(f, w / 2, 40, 16, aqua=False)          # small; the cape carries the big one
            f.grad_rect(0, 92, w, 106, (20, 22, 32), (6, 7, 12)); hband(f, 92, 1.6); hband(f, 106, 1.6)
            for dx in (-30, 0, 30): fold(f, w / 2 + dx, 107, w / 2 + dx * 1.1, 128, 0.8)
        elif name in ("t_right", "t_left"):
            for dx in (16, 34, 50): fold(f, dx, 2, dx + 2, 90)
            f.grad_rect(0, 92, w, 106, (20, 22, 32), (6, 7, 12)); hband(f, 92, 1.6); hband(f, 106, 1.6)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            # long robe sleeve: dark, broad folds, double bronze cuff band, pearl inner cuff line, dark glove
            for dx in (w * 0.3, w * 0.66): fold(f, dx, 8, dx + 2, 84)
            hband(f, 84, 1.8); hband(f, 89, 1.0)
            f.grad_rect(0, 90, w, 96, (26, 32, 48), (12, 14, 22))
            f.line([(0, 96.5), (w, 96.5)], PEARL_D, 0.8)
            f.grad_rect(0, 97, w, 128, (22, 24, 34), (6, 7, 11))   # glove
            f.line([(4, 112), (w - 4, 112)], (40, 44, 60), 0.6); f.line([(0, 98), (w, 98)], (60, 64, 82), 0.5)
        elif name.endswith("_up"):
            f.rect(0, 0, w, h, (16, 19, 30))
        elif name.endswith("_down"):
            f.rect(0, 0, w, h, (6, 7, 11))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


def pants():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 200
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=(17, 21, 33), bot=(6, 7, 12), folds=0.9)
        if name in ("t_front", "t_back", "t_right", "t_left"):
            f.grad_rect(0, 92, w, 106, (20, 22, 32), (6, 7, 12)); hband(f, 92, 1.6); hband(f, 106, 1.6)
        elif name.endswith("_up") or name.endswith("_down"):
            f.rect(0, 0, w, h, (6, 7, 11))
        else:
            # robe skirt over the leg: long folds, double-step bronze hem, dark boot below
            for dx in (w * 0.22, w * 0.5, w * 0.78): fold(f, dx, 0, dx + 1.5, 96, 1.1)
            inner = None
            if name == "rl_front": inner = "R"       # image right = +x = towards the other leg
            if name == "ll_front": inner = "L"
            if inner:                                 # open-robe front: under-robe strip with bronze piping
                x_edge = w - 10 if inner == "R" else 10
                xs = (x_edge, w) if inner == "R" else (0, x_edge)
                f.grad_rect(xs[0], 0, xs[1], 104, (10, 12, 20), (4, 5, 9))
                trim(f, [(x_edge, 0), (x_edge, 104)], 1.8)
            hband(f, 98, 2.4); hband(f, 104, 1.2)
            f.grad_rect(0, 106, w, 128, (24, 26, 36), (5, 6, 10))           # boot
            f.line([(0, 107), (w, 107)], (54, 58, 76), 0.5)
            hband(f, 124, 1.0)
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    s, p = shirt(), pants()
    s.save(os.path.join(OUT, "tidewatch_shirt_v5.png")); p.save(os.path.join(OUT, "tidewatch_pants_v5.png"))
    print("wrote", OUT)

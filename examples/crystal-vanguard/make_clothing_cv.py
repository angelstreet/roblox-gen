#!/usr/bin/env python3
"""Crystal Vanguard - classic shirt + pants (585x559) painted on the official template rectangles.
Uses the shared 4x Face painter in lib/rgen_clothing.py.
Usage: python3 make_clothing_cv.py  -> out/cv_shirt.png, out/cv_pants.png"""
import os, math
from PIL import Image
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
from rgen_clothing import Face, S, SHIRT, PANTS, W, H
from palette import C   # colour theme: edit palette.py for a new set

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
WHITE_T, WHITE_B = C((250, 251, 255)), C((176, 192, 232))     # silver-white armor  #F8F9FF .. shaded toward #CAD8FF/blue
NAVY_T, NAVY_B = C((24, 42, 112)), C((13, 27, 77))             # deep navy #0D1B4D
DARK_T, DARK_B = C((20, 26, 58)), C((6, 9, 24))
GH, GM, GL = C((255, 238, 160)), C((212, 175, 55)), C((126, 94, 22))  # gold #D4AF37 ramp
GEM_HI, GEM, GEM_LO = C((170, 235, 255)), C((46, 107, 255)), C((20, 52, 170))
ICE = C((202, 216, 255))


def gold(f, pts, w=2.0):
    f.line(pts, GL, w + 0.7); f.line(pts, GM, w * 0.95); f.line([(x - 0.2, y - 0.3) for x, y in pts], GH, max(0.5, w * 0.35))


def gem(f, cx, cy, r, tall=1.45):
    """faceted diamond gem with gold setting and glow"""
    rt, rb = r * tall, r * tall * 0.9
    f.glowdot(cx, cy, r * 1.1, C((60, 150, 255)))
    out = [(cx, cy - rt - 1.4), (cx + r + 1.4, cy), (cx, cy + rb + 1.4), (cx - r - 1.4, cy)]
    f.metal(out, top=GH, mid=GM, bot=GL)
    P = [(cx, cy - rt), (cx + r, cy), (cx, cy + rb), (cx - r, cy)]
    f.poly(P, GEM)
    f.poly([P[0], P[1], (cx, cy)], GEM_HI); f.poly([P[0], (cx, cy), P[3]], C((96, 180, 255)))
    f.poly([P[3], (cx, cy), P[2]], GEM); f.poly([(cx, cy), P[1], P[2]], GEM_LO)
    f.line([(cx - r * .3, cy - rt * .4), (cx - r * .05, cy - rt * .8)], C((255, 255, 255)), 0.7)


def fil(f, pts, w=1.4):  # gold filigree line, >= ~2 px outer width at 585 scale
    gold(f, pts, w)


def _curl(pts, s, r, sweep=1.6 * math.pi, n=14):
    """append a shrinking spiral curl to the end of pts; s=+1 curls left of travel, -1 right"""
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    tx, ty = x1 - x0, y1 - y0; L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
    px, py = -ty * s, tx * s
    cx, cy = x1 + px * r, y1 + py * r
    a0 = math.atan2(y1 - cy, x1 - cx); out = list(pts)
    for k in range(1, n + 1):
        t = k / n; a = a0 + s * sweep * t; rr = r * (1 - 0.62 * t)
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def vine(f, a, b, amp=4.0, waves=1.0, curl=(1, -1), r=3.4, w=1.4, n=26, sprig=False):
    """S-curve scroll from a to b built from many short segments, with spiral curls at the ends (curl=(start_side, end_side), 0 = none)"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        t = i / n; o = amp * math.sin(2 * math.pi * waves * t)
        pts.append((a[0] + dx * t + nx * o, a[1] + dy * t + ny * o))
    if sprig:
        i = n // 2; (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]; tx, ty = x1 - x0, y1 - y0; L2 = math.hypot(tx, ty) or 1
        sd = 1 if amp >= 0 else -1; bx, by = ty / L2 * sd, -tx / L2 * sd
        px, py = pts[i]; sp = [(px, py), (px + bx * 2.5, py + by * 2.5), (px + bx * 5, py + by * 5)]
        fil(f, _curl(sp, -sd, 2.2, n=10), 1.2)
    if curl[1]: pts = _curl(pts, curl[1], r)
    if curl[0]: pts = list(reversed(_curl(list(reversed(pts)), curl[0], r)))
    fil(f, pts, w)


def mv(f, cx, a, b, amp=4.0, **kw):
    """mirrored pair: right copy is the exact x-mirror (amp sign and curl sides flipped)"""
    c = kw.pop("curl", (1, -1))
    vine(f, a, b, amp=amp, curl=c, **kw)
    vine(f, (2 * cx - a[0], a[1]), (2 * cx - b[0], b[1]), amp=-amp, curl=(-c[0], -c[1]), **kw)


def frame(f, pts, w=1.6): gold(f, pts + [pts[0]], w)


def shade(f, pts, amt=150, dy=1.2): f.drop(pts, dy=dy, amt=amt); f.apply_shadow_now()


def plate(f, x0, y0, x1, y1, cut=5, bevel=True):
    poly = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut)]
    shade(f, poly, 170, 1.4)
    f.metal(poly, top=C((255, 255, 255)), mid=C((236, 241, 255)), bot=C((168, 186, 232)), outline_dark=False)
    if bevel:                                                           # inner bevel: light top/left, shaded bottom/right
        i = 4.2
        f.line([(x0 + cut + 1, y0 + i), (x1 - cut - 1, y0 + i)], C((255, 255, 255)), 0.9)
        f.line([(x0 + i, y0 + cut + 1), (x0 + i, y1 - cut - 1)], C((246, 249, 255)), 0.7)
        f.line([(x0 + cut + 1, y1 - i), (x1 - cut - 1, y1 - i)], C((132, 152, 208)), 1.0)
        f.line([(x1 - i, y0 + cut + 1), (x1 - i, y1 - cut - 1)], C((150, 168, 220)), 0.9)
    gold(f, poly + [poly[0]], 1.7)


def navy_panel(f, poly, rim=True):
    shade(f, poly, 150)
    f.metal(poly, top=C((30, 52, 132)), mid=NAVY_T, bot=NAVY_B, outline_dark=False)
    if rim: gold(f, poly + [poly[0]], 1.7)


def sleeve(f, w, h):
    cx = w / 2
    # upper arm: navy cloth (mostly hidden by the 3D pauldron), gold rim and a first scroll
    f.grad_rect(0, 0, w, 46, C((30, 52, 130)), NAVY_T)
    gold(f, [(0, 1), (w, 1)], 1.8)
    vine(f, (6, 22), (w - 6, 22), amp=3.5, waves=1.0, r=2.6)
    gold(f, [(0, 44), (w, 44)], 1.6)
    # forearm: navy cloth with a white / silver vambrace plate
    f.grad_rect(0, 46, w, 94, NAVY_T, NAVY_B)
    plate(f, 5, 48, w - 5, 86, 6)
    gem(f, cx, 67, 5.0, 1.45)
    mv(f, cx, (10, 56), (cx - 11, 78), amp=3.0, waves=1.0, r=2.4)
    fil(f, [(9, 53), (cx - 7, 53)]); fil(f, [(w - 9, 53), (cx + 7, 53)])
    # cuff: gold bands
    f.grad_rect(0, 87, w, 96, C((40, 64, 150)), NAVY_B)
    gold(f, [(0, 88), (w, 88)], 1.9); gold(f, [(0, 96), (w, 96)], 2.0)
    for i in range(6, w - 4, 9): f.line([(i, 91), (i + 3, 93)], GM, 1.4)
    # glove (top edge at y=96, under the local-y-100 rule): dark navy + gold scrolls
    f.grad_rect(0, 97, w, 128, C((20, 36, 96)), DARK_B)
    vine(f, (8, 108), (w - 8, 108), amp=3.2, waves=1.0, r=2.6)
    gem(f, cx, 118, 3.0, 1.3)
    gold(f, [(0, 126), (w, 126)], 1.8)


def belt(f, w, y0=94, y1=110, buckle=True):
    cx = w / 2
    f.grad_rect(0, y0, w, y1, C((34, 56, 136)), NAVY_B)
    gold(f, [(0, y0 + 0.5), (w, y0 + 0.5)], 1.9); gold(f, [(0, y1 - 0.5), (w, y1 - 0.5)], 1.9)
    for i in range(6, w, 10): f.line([(i, y0 + 7), (i + 4, y0 + 7)], GM, 1.5)
    if buckle:
        b = [(cx - 11, y0 - 1), (cx + 11, y0 - 1), (cx + 13, y0 + 8), (cx + 11, y1 + 2), (cx - 11, y1 + 2), (cx - 13, y0 + 8)]
        shade(f, b, 190)
        f.metal(b, top=GH, mid=GM, bot=GL); gold(f, b + [b[0]], 1.2)
        gem(f, cx, y0 + 8, 4.5, 1.25)


def shirt():
    c = Image.new("RGBA", (W, H), (C((0, 0, 0)) + (0,))); seed = 300
    for name, r in SHIRT.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=WHITE_T, bot=WHITE_B, folds=0.2)
        cx = w / 2
        if name == "t_front":
            plate(f, 2, 2, 36, 90, 7); plate(f, w - 36, 2, w - 2, 90, 7)       # white chest plates
            # scroll filigree on the plates
            mv(f, cx, (9, 11), (28, 11), amp=2.6, waves=1.0, r=2.4, curl=(1, -1))
            gem(f, 19, 33, 4, 1.4); gem(f, w - 19, 33, 4, 1.4)
            mv(f, cx, (8, 48), (28, 64), amp=3.6, waves=1.0, r=3.0, curl=(-1, 1), sprig=True)
            mv(f, cx, (10, 72), (28, 80), amp=2.6, waves=1.0, r=2.4, curl=(1, -1))
            # navy tabard with the big gem
            nav = [(cx - 29, 0), (cx + 29, 0), (cx + 25, 76), (cx, 101), (cx - 25, 76)]
            navy_panel(f, nav)
            inner = [(cx - 24, 3), (cx + 24, 3), (cx + 20.5, 74), (cx, 94), (cx - 20.5, 74)]
            gold(f, inner + [inner[0]], 1.2)
            frame(f, [(cx, 12), (cx + 17, 36), (cx, 62), (cx - 17, 36)], 1.4)   # diamond frame around the gem
            gem(f, cx, 36, 10.5, 1.5)
            mv(f, cx, (cx - 20, 8), (cx - 19, 66), amp=2.4, waves=2.0, r=2.4, curl=(0, 1), sprig=True)
            mv(f, cx, (cx - 17, 72), (cx - 3, 86), amp=2.0, waves=1.0, r=2.4, curl=(-1, 0))
            belt(f, w)
            # hips / skirt flaps under the belt
            f.grad_rect(0, 111, w, 128, C((232, 238, 255)), C((176, 192, 232)))
            plate(f, 4, 113, cx - 17, 126, 4); plate(f, cx + 17, 113, w - 4, 126, 4)
            navy_panel(f, [(cx - 14, 112), (cx + 14, 112), (cx + 12, 126), (cx - 12, 126)])
            gold(f, [(0, 127), (w, 127)], 1.6)
        elif name == "t_back":
            plate(f, 3, 3, w - 3, 90, 9)
            frame(f, [(cx, 12), (cx + 24, 44), (cx, 80), (cx - 24, 44)], 1.5)
            gem(f, cx, 44, 10, 1.6)                                           # crystal emblem
            mv(f, cx, (cx - 6, 24), (cx - 26, 14), amp=3.0, waves=1.0, r=2.8, curl=(0, 1), sprig=True)
            mv(f, cx, (cx - 6, 66), (cx - 26, 78), amp=3.0, waves=1.0, r=2.6, curl=(0, -1))
            mv(f, cx, (13, 22), (13, 70), amp=4.0, waves=1.5, r=3.0, curl=(1, -1), sprig=True)
            belt(f, w, buckle=False)
            f.grad_rect(0, 111, w, 128, C((232, 238, 255)), C((176, 192, 232)))
            plate(f, 4, 113, cx - 4, 126, 4); plate(f, cx + 4, 113, w - 4, 126, 4)
            gold(f, [(0, 127), (w, 127)], 1.6)
        elif name in ("t_right", "t_left"):
            plate(f, 4, 3, w - 4, 90, 7)
            gem(f, cx, 46, 4.2, 1.4)
            vine(f, (10, 16), (w - 10, 16), amp=3.0, waves=1.0, r=2.6, sprig=True)
            vine(f, (10, 76), (w - 10, 76), amp=3.0, waves=1.0, r=2.4, curl=(-1, 1))
            gold(f, [(1, 0), (1, 128)], 1.8); gold(f, [(w - 1, 0), (w - 1, 128)], 1.8)
            belt(f, w, buckle=False)
            f.grad_rect(0, 111, w, 128, C((232, 238, 255)), C((176, 192, 232)))
            plate(f, 4, 113, w - 4, 126, 4); gold(f, [(0, 127), (w, 127)], 1.6)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            sleeve(f, w, h)
        elif name == "t_up":
            f.rect(0, 0, w, h, NAVY_T[:3]); gold(f, [(0, h - 1), (w, h - 1)], 2.0)
        elif name.endswith("_up"):
            f.grad_rect(0, 0, w, h, C((30, 52, 130)), NAVY_T); f.line([(0, 0), (w, 0)], GM, 2)
        elif name.endswith("_down"):
            f.rect(0, 0, w, h, C((30, 40, 100)))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


def leg(f, w, front):
    cx = w / 2
    f.rect(0, 0, w, 128, NAVY_B)
    f.grad_rect(0, 0, w, 100, NAVY_T, NAVY_B)
    # thigh plate
    plate(f, 4, 2, w - 4, 42, 6)
    gem(f, cx, 21, 4.4, 1.4)
    mv(f, cx, (9, 12), (cx - 9, 30), amp=2.6, waves=1.0, r=2.4)
    # scrollwork between the plates (on navy)
    vine(f, (6, 47), (w - 6, 47), amp=2.6, waves=2.0, r=2.4, curl=(1, -1), sprig=True)
    # knee plate
    plate(f, 6, 52, w - 6, 82, 6)
    gem(f, cx, 67, 5.2, 1.4)
    mv(f, cx, (11, 60), (cx - 13, 74), amp=2.6, waves=1.0, r=2.2, curl=(1, -1))
    # darker navy greave
    f.grad_rect(0, 84, w, 98, C((18, 32, 90)), DARK_T)
    gold(f, [(0, 84), (w, 84)], 1.6)
    for i in range(7, w - 3, 10): fil(f, [(i, 87), (i + 3, 94)], 1.2)
    # boot, dark navy / black with gold trim; top edge at y=98 (<= 100)
    f.grad_rect(0, 98, w, 128, C((24, 32, 70)), C((4, 6, 16)))
    gold(f, [(0, 98), (w, 98)], 2.0); gold(f, [(0, 126), (w, 126)], 2.0)
    gold(f, [(0, 104), (w, 104)], 1.0)
    gem(f, cx, 113, 3.4, 1.4)
    mv(f, cx, (7, 110), (cx - 8, 119), amp=2.2, waves=1.0, r=2.0, curl=(1, -1))


def pants():
    c = Image.new("RGBA", (W, H), (C((0, 0, 0)) + (0,))); seed = 400
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=NAVY_T, bot=NAVY_B, folds=0.35)
        cx = w / 2
        if name in ("t_front", "t_back", "t_right", "t_left"):
            f.rect(0, 0, w, h, NAVY_B)
            gold(f, [(0, 1), (w, 1)], 1.8)
            if name == "t_front":
                for sg in (-1, 1): plate(f, cx + (2 if sg > 0 else -62), 4, cx + (62 if sg > 0 else -2), 72, 6)
                gem(f, cx, 34, 5, 1.4)
                mv(f, cx, (cx - 20, 14), (cx - 20, 58), amp=3.0, waves=1.0, r=2.6)
            elif name == "t_back":
                plate(f, 4, 4, w - 4, 72, 8); gem(f, cx, 36, 5, 1.4)
                mv(f, cx, (cx - 24, 14), (cx - 24, 58), amp=3.0, waves=1.0, r=2.6)
            else:
                plate(f, 4, 4, w - 4, 72, 6); gem(f, cx, 36, 4.4, 1.4)
            belt(f, w, 80, 100, buckle=False)
            f.grad_rect(0, 101, w, 128, DARK_T, DARK_B)
            vine(f, (8, 114), (w - 8, 114), amp=3.2, waves=2.0, r=2.4, curl=(1, -1))
            gold(f, [(0, 126), (w, 126)], 2.0)
        elif name.endswith("_up"): f.rect(0, 0, w, h, NAVY_B)
        elif name.endswith("_down"): f.rect(0, 0, w, h, C((6, 9, 24)))
        else:
            leg(f, w, name.endswith("front"))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    shirt().save(os.path.join(OUT, "cv_shirt.png")); pants().save(os.path.join(OUT, "cv_pants.png")); print("wrote", OUT)

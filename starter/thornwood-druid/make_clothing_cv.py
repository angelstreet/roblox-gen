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
WHITE_T, WHITE_B = C((238, 230, 206)), C((176, 164, 132))     # silver-white armor  #F8F9FF .. shaded toward #CAD8FF/blue
NAVY_T, NAVY_B = C((58, 84, 42)), C((26, 40, 20))             # deep navy #0D1B4D
DARK_T, DARK_B = C((48, 34, 22)), C((20, 14, 9))
GH, GM, GL = C((255, 214, 120)), C((230, 146, 40)), C((130, 72, 18))  # gold #D4AF37 ramp
GEM_HI, GEM, GEM_LO = C((255, 230, 150)), C((255, 170, 50)), C((170, 84, 20))
ICE = C((214, 206, 178))


def gold(f, pts, w=2.0):
    f.line(pts, GL, w + 0.7); f.line(pts, GM, w * 0.95); f.line([(x - 0.2, y - 0.3) for x, y in pts], GH, max(0.5, w * 0.35))


def gem(f, cx, cy, r, tall=1.45):
    """faceted diamond gem with gold setting and glow"""
    rt, rb = r * tall, r * tall * 0.9
    f.glowdot(cx, cy, r * 1.1, C((255, 180, 70)))
    out = [(cx, cy - rt - 1.4), (cx + r + 1.4, cy), (cx, cy + rb + 1.4), (cx - r - 1.4, cy)]
    f.metal(out, top=GH, mid=GM, bot=GL)
    P = [(cx, cy - rt), (cx + r, cy), (cx, cy + rb), (cx - r, cy)]
    f.poly(P, GEM)
    f.poly([P[0], P[1], (cx, cy)], GEM_HI); f.poly([P[0], (cx, cy), P[3]], C((255, 200, 100)))
    f.poly([P[3], (cx, cy), P[2]], GEM); f.poly([(cx, cy), P[1], P[2]], GEM_LO)
    f.line([(cx - r * .3, cy - rt * .4), (cx - r * .05, cy - rt * .8)], C((255, 252, 240)), 0.7)


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
    f.metal(poly, top=C((255, 252, 240)), mid=C((228, 218, 190)), bot=C((170, 156, 120)), outline_dark=False)
    if bevel:                                                           # inner bevel: light top/left, shaded bottom/right
        i = 4.2
        f.line([(x0 + cut + 1, y0 + i), (x1 - cut - 1, y0 + i)], C((255, 252, 240)), 0.9)
        f.line([(x0 + i, y0 + cut + 1), (x0 + i, y1 - cut - 1)], C((240, 232, 210)), 0.7)
        f.line([(x0 + cut + 1, y1 - i), (x1 - cut - 1, y1 - i)], C((150, 130, 90)), 1.0)
        f.line([(x1 - i, y0 + cut + 1), (x1 - i, y1 - cut - 1)], C((150, 168, 220)), 0.9)
    gold(f, poly + [poly[0]], 1.7)


def pplate(f, x0, y0, x1, y1, tip=8, cut=4):
    """armour plate with a pointed bottom (concept: skirt flaps, knee plates end in a point)"""
    cx = (x0 + x1) / 2
    poly = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - tip), (cx, y1), (x0, y1 - tip), (x0, y0 + cut)]
    shade(f, poly, 170, 1.4)
    f.metal(poly, top=C((255, 252, 240)), mid=C((228, 218, 190)), bot=C((170, 156, 120)), outline_dark=False)
    f.line([(x0 + cut + 1, y0 + 4), (x1 - cut - 1, y0 + 4)], C((255, 252, 240)), 0.9)
    f.line([(x0 + 3.5, y1 - tip - 2), (cx, y1 - 4)], C((150, 130, 90)), 1.0); f.line([(cx, y1 - 4), (x1 - 3.5, y1 - tip - 2)], C((150, 130, 90)), 1.0)
    gold(f, poly + [poly[0]], 1.7)
    return poly


def navy_panel(f, poly, rim=True):
    shade(f, poly, 150)
    f.metal(poly, top=C((74, 104, 48)), mid=NAVY_T, bot=NAVY_B, outline_dark=False)
    if rim: gold(f, poly + [poly[0]], 1.7)


def sleeve(f, w, h):
    cx = w / 2
    # upper arm: navy cloth (mostly hidden by the 3D pauldron), gold rim and a first scroll
    f.grad_rect(0, 0, w, 46, C((70, 100, 46)), NAVY_T)
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
    f.grad_rect(0, 87, w, 96, C((64, 96, 46)), NAVY_B)
    gold(f, [(0, 88), (w, 88)], 1.9); gold(f, [(0, 96), (w, 96)], 2.0)
    for i in range(6, w - 4, 9): f.line([(i, 91), (i + 3, 93)], GM, 1.4)
    # glove (top edge at y=96, under the local-y-100 rule): dark navy + gold scrolls
    f.grad_rect(0, 97, w, 128, C((34, 52, 24)), DARK_B)
    vine(f, (8, 108), (w - 8, 108), amp=3.2, waves=1.0, r=2.6)
    gem(f, cx, 118, 3.0, 1.3)
    gold(f, [(0, 126), (w, 126)], 1.8)


def belt(f, w, y0=94, y1=110, buckle=True):
    cx = w / 2
    f.grad_rect(0, y0, w, y1, C((60, 84, 40)), NAVY_B)
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
            plate(f, 2, 2, 44, 62, 7); plate(f, w - 44, 2, w - 2, 62, 7)         # white chest plates
            mv(f, cx, (10, 10), (36, 10), amp=2.6, waves=1.0, r=2.4, curl=(1, -1))
            gem(f, 23, 30, 4.5, 1.4); gem(f, w - 23, 30, 4.5, 1.4)
            mv(f, cx, (9, 44), (34, 56), amp=3.0, waves=1.0, r=2.6, curl=(-1, 1), sprig=True)
            plate(f, 2, 64, 44, 92, 6); plate(f, w - 44, 64, w - 2, 92, 6)       # lower chest plates
            mv(f, cx, (9, 72), (36, 84), amp=3.0, waves=1.0, r=2.6, curl=(1, -1))
            # wide navy V tabard with the big gem (concept: navy centre narrowing to a point at the belt)
            nav = [(cx - 38, 0), (cx + 38, 0), (cx + 30, 56), (cx, 96), (cx - 30, 56)]
            navy_panel(f, nav)
            inner = [(cx - 32, 3), (cx + 32, 3), (cx + 25, 54), (cx, 89), (cx - 25, 54)]
            gold(f, inner + [inner[0]], 1.2)
            frame(f, [(cx, 12), (cx + 19, 36), (cx, 64), (cx - 19, 36)], 1.4)
            gem(f, cx, 36, 11.5, 1.5)
            mv(f, cx, (cx - 27, 8), (cx - 22, 50), amp=2.4, waves=1.5, r=2.4, curl=(0, 1), sprig=True)
            mv(f, cx, (cx - 20, 60), (cx - 4, 82), amp=2.0, waves=1.0, r=2.4, curl=(-1, 0))
            belt(f, w)
            # skirt flaps under the belt: white pointed plates over navy (their tips continue on the pants' legs)
            f.grad_rect(0, 111, w, 128, C((50, 70, 34)), NAVY_B)
            pplate(f, 2, 112, cx - 10, 136, 9, 4); pplate(f, cx + 10, 112, w - 2, 136, 9, 4)
            navy_panel(f, [(cx - 9, 112), (cx + 9, 112), (cx + 7, 128), (cx - 7, 128)])
            gem(f, cx, 120, 3.2, 1.3)
        elif name == "t_back":
            plate(f, 3, 3, w - 3, 92, 9)
            frame(f, [(cx, 14), (cx + 24, 46), (cx, 82), (cx - 24, 46)], 1.5)
            gem(f, cx, 46, 10, 1.6)                                           # crystal emblem
            mv(f, cx, (cx - 6, 26), (cx - 26, 16), amp=3.0, waves=1.0, r=2.8, curl=(0, 1), sprig=True)
            mv(f, cx, (cx - 6, 68), (cx - 26, 80), amp=3.0, waves=1.0, r=2.6, curl=(0, -1))
            mv(f, cx, (13, 24), (13, 72), amp=4.0, waves=1.5, r=3.0, curl=(1, -1), sprig=True)
            belt(f, w, buckle=False)
            f.grad_rect(0, 111, w, 128, C((50, 70, 34)), NAVY_B)
            pplate(f, 2, 112, cx - 2, 136, 9, 4); pplate(f, cx + 2, 112, w - 2, 136, 9, 4)
        elif name in ("t_right", "t_left"):
            plate(f, 4, 3, w - 4, 92, 7)
            gem(f, cx, 48, 4.2, 1.4)
            vine(f, (10, 16), (w - 10, 16), amp=3.0, waves=1.0, r=2.6, sprig=True)
            vine(f, (10, 78), (w - 10, 78), amp=3.0, waves=1.0, r=2.4, curl=(-1, 1))
            gold(f, [(1, 0), (1, 128)], 1.8); gold(f, [(w - 1, 0), (w - 1, 128)], 1.8)
            belt(f, w, buckle=False)
            f.grad_rect(0, 111, w, 128, C((50, 70, 34)), NAVY_B)
            pplate(f, 3, 112, w - 3, 136, 9, 4)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            sleeve(f, w, h)
        elif name == "t_up":
            f.rect(0, 0, w, h, NAVY_T[:3]); gold(f, [(0, h - 1), (w, h - 1)], 2.0)
        elif name.endswith("_up"):
            f.grad_rect(0, 0, w, h, C((70, 100, 46)), NAVY_T); f.line([(0, 0), (w, 0)], GM, 2)
        elif name.endswith("_down"):
            f.rect(0, 0, w, h, C((40, 54, 26)))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


def leg(f, w, front):
    cx = w / 2
    f.rect(0, 0, w, 128, NAVY_B)
    f.grad_rect(0, 0, w, 100, NAVY_T, NAVY_B)
    # skirt flap tip hanging from the torso (white, pointed, gold edge) over the navy thigh
    flap = [(0, 0), (w, 0), (w, 9), (cx, 26), (0, 9)]
    shade(f, flap, 180, 1.6)
    f.metal(flap, top=C((255, 252, 240)), mid=C((228, 218, 190)), bot=C((170, 156, 120)), outline_dark=False)
    gold(f, [(0, 9), (cx, 26), (w, 9)], 1.8); f.line([(4, 9), (cx, 22)], C((150, 130, 90)), 0.9); f.line([(cx, 22), (w - 4, 9)], C((150, 130, 90)), 0.9)
    gem(f, cx, 9, 3.4, 1.3)
    # thigh: navy cloth with a gold scroll
    mv(f, cx, (8, 32), (cx - 4, 50), amp=3.0, waves=1.0, r=2.6, curl=(1, -1))
    # pointed knee plate with a gem
    pplate(f, 8, 52, w - 8, 88, 10, 5)
    gem(f, cx, 66, 5.4, 1.4)
    mv(f, cx, (13, 58), (cx - 12, 74), amp=2.2, waves=1.0, r=2.0, curl=(1, -1))
    # shin: darker navy greave, gold lines
    f.grad_rect(0, 89, w, 98, C((36, 26, 16)), DARK_T)
    gold(f, [(0, 90), (w, 90)], 1.4)
    # boot, dark navy / black with gold trim; top edge at y=98 (<= 100)
    f.grad_rect(0, 98, w, 128, C((50, 36, 22)), C((4, 6, 16)))
    gold(f, [(0, 98), (w, 98)], 2.0); gold(f, [(0, 126), (w, 126)], 2.0)
    gold(f, [(0, 104), (w, 104)], 1.0)
    gem(f, cx, 113, 3.6, 1.4)
    mv(f, cx, (7, 110), (cx - 8, 119), amp=2.2, waves=1.0, r=2.0, curl=(1, -1))


def pants():
    c = Image.new("RGBA", (W, H), (C((0, 0, 0)) + (0,))); seed = 400
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=NAVY_T, bot=NAVY_B, folds=0.35)
        cx = w / 2
        if name in ("t_front", "t_back", "t_right", "t_left"):
            f.rect(0, 0, w, h, NAVY_B); f.grad_rect(0, 101, w, 128, DARK_T, DARK_B)      # under the shirt; dark hem band shows below it
            gold(f, [(0, 126), (w, 126)], 2.0)
        elif name.endswith("_up"): f.rect(0, 0, w, h, NAVY_B)
        elif name.endswith("_down"): f.rect(0, 0, w, h, C((6, 9, 24)))
        else:
            leg(f, w, name.endswith("front"))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    shirt().save(os.path.join(OUT, "cv_shirt.png")); pants().save(os.path.join(OUT, "cv_pants.png")); print("wrote", OUT)

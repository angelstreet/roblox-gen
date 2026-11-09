#!/usr/bin/env python3
"""Ember Warden - classic shirt + pants (585x559) painted on the official template rectangles with the shared 4x Face painter
(lib/rgen_clothing.py): obsidian plate armour, glowing ember cracks, gold trims, flame sigils.
Usage: python3 make_clothing_ew.py  -> out/ew_shirt.png, out/ew_pants.png"""
import os, math, random
from PIL import Image
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
from rgen_clothing import Face, S, SHIRT, PANTS, W, H

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
OBS_T, OBS_B = (46, 41, 56), (12, 10, 17)            # obsidian cloth / under-armour
PL_HI, PL_MI, PL_LO = (104, 94, 122), (42, 37, 52), (13, 11, 19)   # obsidian plate ramp (lit edge, body, shade)
EMB, EMB_HI, EMB_LO, HOT, WHITE = (255, 106, 28), (255, 176, 60), (170, 40, 10), (255, 214, 110), (255, 244, 205)
GH, GM, GL = (255, 226, 140), (222, 172, 60), (118, 78, 16)


def gold(f, pts, w=1.6):
    f.line(pts, GL, w + 0.8); f.line(pts, GM, w * 0.95); f.line([(x - 0.2, y - 0.3) for x, y in pts], GH, max(0.5, w * 0.35))


def mp(pts, w): return [(w - x, y) for x, y in pts]                  # mirror a polygon across the face centre


def crack(f, pts, w=1.1):
    """glowing ember crack: soft glow layer, dark rim, ember body, hot core"""
    f.gd.line(f.s(pts), fill=EMB + (255,), width=int(w * S * 2.4), joint="curve")
    f.line(pts, (30, 6, 2), w + 1.0); f.line(pts, EMB, w); f.line(pts, HOT, max(0.4, w * 0.4))


def jag(a, b, rnd, n=7, amp=3.0):
    pts = [a]
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    for k in range(1, n):
        t = k / n; o = rnd.uniform(-amp, amp); pts.append((a[0] + dx * t + nx * o, a[1] + dy * t + ny * o))
    pts.append(b); return pts


def fork(f, rnd, a, b, w=1.1, amp=3.0, branches=2):
    pts = jag(a, b, rnd, 7, amp); crack(f, pts, w)
    for _ in range(branches):
        i = rnd.randrange(2, 6); (x, y), (x2, y2) = pts[i], pts[i + 1]; ang = math.atan2(b[1] - a[1], b[0] - a[0]) + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.1)
        L = rnd.uniform(6, 13); crack(f, jag((x, y), (x + L * math.cos(ang), y + L * math.sin(ang)), rnd, 4, 1.6), w * 0.7)


def shade(f, pts, amt=170, dy=1.3): f.drop(pts, dy=dy, amt=amt); f.apply_shadow_now()


def plate(f, poly, rnd=None, cracks=0, edge=True, hi=PL_HI, mi=PL_MI, lo=PL_LO):
    """angular obsidian plate: 3-stop ramp, lit top/left bevel, shaded bottom/right bevel, gold edge, optional cracks inside"""
    shade(f, poly, 180, 1.4)
    f.metal(poly, top=hi, mid=mi, bot=lo, outline_dark=False)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; n = len(poly)
    for k in range(n):                                              # bevel: edges facing up/left light, down/right shaded
        p, q = poly[k], poly[(k + 1) % n]; ex, ey = q[0] - p[0], q[1] - p[1]; L = math.hypot(ex, ey) or 1
        nrm = (ey / L, -ex / L)                                     # outward normal for a clockwise polygon in image coords
        lit = -nrm[0] * 0.5 - nrm[1] * 0.8
        cx_, cy_ = sum(xs) / n, sum(ys) / n; mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        inw = (cx_ - mx_, cy_ - my_); il = math.hypot(*inw) or 1; ox, oy = inw[0] / il * 2.4, inw[1] / il * 2.4
        col = (150, 138, 172) if (mx_ - cx_) * -0.5 + (my_ - cy_) * -0.8 > 0 else (22, 18, 30)
        f.line([(p[0] + ox, p[1] + oy), (q[0] + ox, q[1] + oy)], col, 0.8)
    if edge: gold(f, poly + [poly[0]], 1.4)
    if cracks and rnd:
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        for _ in range(cracks):
            a = (rnd.uniform(x0 + 3, x1 - 3), rnd.uniform(y0 + 3, y1 - 3)); b = (a[0] + rnd.uniform(-12, 12), a[1] + rnd.uniform(6, 16))
            b = (min(x1 - 2, max(x0 + 2, b[0])), min(y1 - 2, max(y0 + 2, b[1]))); fork(f, rnd, a, b, 0.9, 2.0, 1)


def ember_gem(f, cx, cy, r, tall=1.35):
    rt, rb = r * tall, r * tall * 0.9
    f.glowdot(cx, cy, r * 1.3, EMB)
    out = [(cx, cy - rt - 1.4), (cx + r + 1.4, cy), (cx, cy + rb + 1.4), (cx - r - 1.4, cy)]
    f.metal(out, top=GH, mid=GM, bot=GL)
    P = [(cx, cy - rt), (cx + r, cy), (cx, cy + rb), (cx - r, cy)]
    f.poly(P, EMB)
    f.poly([P[0], P[1], (cx, cy)], HOT); f.poly([P[0], (cx, cy), P[3]], EMB_HI); f.poly([P[3], (cx, cy), P[2]], EMB); f.poly([(cx, cy), P[1], P[2]], EMB_LO)
    f.line([(cx - r * .3, cy - rt * .4), (cx - r * .05, cy - rt * .8)], WHITE, 0.7)


def sigil(f, cx, cy, h):
    """flame sigil: three tongues in a gold frame (original emblem), ember core"""
    fr = [(cx, cy - h), (cx + h * 0.62, cy - h * 0.1), (cx + h * 0.38, cy + h * 0.78), (cx, cy + h), (cx - h * 0.38, cy + h * 0.78), (cx - h * 0.62, cy - h * 0.1)]
    f.glowdot(cx, cy, h * 0.9, EMB)
    f.metal(fr, top=GH, mid=GM, bot=GL); f.poly([(x * 0.0 + cx + (x - cx) * 0.82, cy + (y - cy) * 0.82) for x, y in fr], (22, 14, 20))
    c = [(cx, cy - h * 0.72), (cx + h * 0.30, cy - h * 0.08), (cx + h * 0.20, cy + h * 0.5), (cx, cy + h * 0.72), (cx - h * 0.20, cy + h * 0.5), (cx - h * 0.30, cy - h * 0.08)]
    f.poly(c, EMB); f.poly([(cx, cy - h * 0.55), (cx + h * 0.15, cy), (cx, cy + h * 0.5), (cx - h * 0.15, cy)], HOT)
    f.poly([(cx, cy - h * 0.25), (cx + h * 0.07, cy + h * 0.1), (cx, cy + h * 0.38), (cx - h * 0.07, cy + h * 0.1)], WHITE)
    f.line([(cx - h * 0.62, cy - h * 0.1), (cx - h * 0.9, cy - h * 0.5)], GM, 1.2); f.line([(cx + h * 0.62, cy - h * 0.1), (cx + h * 0.9, cy - h * 0.5)], GM, 1.2)


def zigzag(f, y, w, amp=2.4, step=6, col=GM, wd=1.3):
    pts = []; x = 0
    while x <= w: pts.append((x, y + (amp if (len(pts) % 2) else -amp))); x += step
    f.line(pts, col, wd)


def belt(f, w, y0=100, y1=114, buckle=True):
    cx = w / 2
    f.grad_rect(0, y0, w, y1, (34, 28, 36), (10, 8, 12))
    gold(f, [(0, y0 + 0.5), (w, y0 + 0.5)], 1.8); gold(f, [(0, y1 - 0.5), (w, y1 - 0.5)], 1.8)
    for i in range(7, w, 11): f.poly([(i - 2, y0 + 5), (i + 2, y0 + 5), (i + 2, y0 + 9), (i - 2, y0 + 9)], GM)
    if buckle:
        b = [(cx - 14, y0 - 1), (cx + 14, y0 - 1), (cx + 17, y0 + 7), (cx + 12, y1 + 3), (cx - 12, y1 + 3), (cx - 17, y0 + 7)]
        shade(f, b, 200); f.metal(b, top=GH, mid=GM, bot=GL); gold(f, b + [b[0]], 1.2); ember_gem(f, cx, y0 + 8, 5.0, 1.2)


def tassets(f, w, y0=115, n=3, rnd=None):
    """pointed obsidian skirt plates under the belt; ember seams"""
    cw = (w - 4) / n
    for k in range(n):
        x0 = 2 + k * cw; x1 = x0 + cw; poly = [(x0 + 1, y0), (x1 - 1, y0), (x1 - 2, y0 + 10), ((x0 + x1) / 2, y0 + 26), (x0 + 2, y0 + 10)]
        plate(f, poly, rnd, 0, True)
        f.line([((x0 + x1) / 2, y0 + 3), ((x0 + x1) / 2, y0 + 20)], EMB, 1.0)


def sleeve(f, w, h, rnd):
    cx = w / 2
    f.grad_rect(0, 0, w, 46, (40, 34, 50), (22, 18, 30)); gold(f, [(0, 1), (w, 1)], 1.8)
    for k in range(3): fork(f, rnd, (6 + k * 20, 8 + 4 * k), (10 + k * 18, 34 + rnd.uniform(-3, 3)), 0.9, 2.2, 1)
    gold(f, [(0, 44), (w, 44)], 1.6)
    f.grad_rect(0, 46, w, 94, (30, 26, 38), (14, 12, 20))
    plate(f, [(5, 49), (w - 5, 49), (w - 8, 80), (cx, 90), (8, 80)], rnd, 3)
    ember_gem(f, cx, 66, 4.2)
    f.line([(10, 54), (cx - 8, 54)], EMB_HI, 1.0); f.line([(w - 10, 54), (cx + 8, 54)], EMB_HI, 1.0)
    f.grad_rect(0, 88, w, 97, (60, 46, 30), (22, 16, 12)); gold(f, [(0, 88), (w, 88)], 1.9); gold(f, [(0, 96), (w, 96)], 2.0); zigzag(f, 92.5, w, 1.6, 5, GH, 0.9)
    f.grad_rect(0, 98, w, 128, (26, 22, 32), (6, 5, 9))
    for k in range(4): f.poly([(6 + k * 14, 106), (12 + k * 14, 106), (9 + k * 14, 114)], EMB)    # knuckle spikes glow
    crack(f, jag((8, 118), (w - 8, 120), rnd, 6, 2.0), 0.9); gold(f, [(0, 126), (w, 126)], 1.8)


def shirt():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 700
    for name, r in SHIRT.items():
        seed += 1; w, h = r[2], r[3]; rnd = random.Random(seed)
        f = Face(w, h, seed, top=OBS_T, bot=OBS_B, folds=0.25); cx = w / 2
        if name == "t_front":
            L1 = [(3, 3), (59, 1), (62, 28), (40, 52), (5, 44)]; plate(f, L1, rnd, 2); plate(f, mp(L1, w), rnd, 2)
            L2 = [(5, 50), (38, 56), (60, 36), (62, 62), (30, 78), (4, 74)]; plate(f, L2, rnd, 2); plate(f, mp(L2, w), rnd, 2)
            core = [(cx - 12, 0), (cx + 12, 0), (cx + 8, 60), (cx, 92), (cx - 8, 60)]                 # glowing sternum rift
            f.glowdot(cx, 40, 22, EMB); shade(f, core, 120, 0.8); f.metal(core, top=(48, 8, 4), mid=(120, 24, 8), bot=(40, 6, 2), outline_dark=False)
            for yy in (12, 30, 50, 68): f.line([(cx - 6 + (yy % 7) * 0.3, yy), (cx + 6, yy + 4)], EMB_HI, 1.0)
            gold(f, core + [core[0]], 1.5); ember_gem(f, cx, 34, 8.5, 1.5); sigil(f, cx, 72, 7)
            belt(f, w, 98, 112); tassets(f, w, 114, 4, rnd)
        elif name == "t_back":
            plate(f, [(3, 3), (w - 3, 3), (w - 6, 60), (cx, 92), (6, 60)], rnd, 7)
            sigil(f, cx, 40, 20)
            for k in range(4): fork(f, rnd, (12 + k * 30, 6), (16 + k * 30 + rnd.uniform(-6, 6), 30 + rnd.uniform(-4, 6)), 1.0, 2.5, 1)
            gold(f, [(cx, 12), (cx, 24)], 1.2)
            belt(f, w, 98, 112, buckle=False); tassets(f, w, 114, 4, rnd)
        elif name in ("t_right", "t_left"):
            plate(f, [(3, 3), (w - 3, 5), (w - 5, 70), (cx, 90), (5, 70)], rnd, 3)
            ember_gem(f, cx, 40, 4.4); gold(f, [(1, 0), (1, 128)], 1.8); gold(f, [(w - 1, 0), (w - 1, 128)], 1.8)
            belt(f, w, 98, 112, buckle=False); tassets(f, w, 114, 2, rnd)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            sleeve(f, w, h, rnd)
        elif name == "t_up": f.rect(0, 0, w, h, OBS_B); gold(f, [(0, h - 1), (w, h - 1)], 2.0)
        elif name.endswith("_up"): f.grad_rect(0, 0, w, h, (40, 34, 50), OBS_T); f.line([(0, 0), (w, 0)], GM, 2)
        elif name.endswith("_down"): f.rect(0, 0, w, h, (20, 14, 18))
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


def leg(f, w, front, rnd):
    cx = w / 2
    f.rect(0, 0, w, 128, OBS_B); f.grad_rect(0, 0, w, 100, (40, 34, 50), OBS_B)
    flap = [(0, 0), (w, 0), (w, 9), (cx, 28), (0, 9)]; shade(f, flap, 180, 1.6); f.metal(flap, top=PL_HI, mid=PL_MI, bot=PL_LO, outline_dark=False)
    gold(f, [(0, 9), (cx, 28), (w, 9)], 1.8); f.line([(cx, 3), (cx, 22)], EMB, 1.0)
    for k in range(3): fork(f, rnd, (10 + k * 20, 34), (12 + k * 18 + rnd.uniform(-3, 3), 52), 0.9, 2.0, 1)
    kn = [(cx, 52), (w - 7, 60), (w - 9, 80), (cx, 94), (9, 80), (7, 60)]                     # spiked knee plate
    plate(f, kn, rnd, 0); ember_gem(f, cx, 72, 5.0, 1.3)
    f.poly([(cx - 6, 54), (cx, 44), (cx + 6, 54)], GM); f.line([(cx - 6, 54), (cx, 44), (cx + 6, 54)], GL, 0.8)
    f.grad_rect(0, 95, w, 98, (20, 16, 24), (10, 8, 14))
    f.grad_rect(0, 98, w, 128, (28, 24, 34), (4, 3, 7))
    gold(f, [(0, 98), (w, 98)], 2.0); gold(f, [(0, 126), (w, 126)], 2.0); zigzag(f, 104, w, 2.0, 6, GM, 1.1)
    f.line([(0, 124), (w, 124)], EMB, 1.2)
    ember_gem(f, cx, 113, 3.6, 1.3); crack(f, jag((6, 118), (cx - 6, 122), rnd, 4, 1.5), 0.8); crack(f, jag((cx + 6, 118), (w - 6, 122), rnd, 4, 1.5), 0.8)


def pants():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 800
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]; rnd = random.Random(seed)
        f = Face(w, h, seed, top=OBS_T, bot=OBS_B, folds=0.35)
        if name in ("t_front", "t_back", "t_right", "t_left"):
            f.rect(0, 0, w, h, OBS_B); f.grad_rect(0, 101, w, 128, (24, 20, 30), (6, 5, 9)); gold(f, [(0, 126), (w, 126)], 2.0)
        elif name.endswith("_up"): f.rect(0, 0, w, h, OBS_B)
        elif name.endswith("_down"): f.rect(0, 0, w, h, (12, 8, 10))
        else: leg(f, w, name.endswith("front"), rnd)
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    shirt().save(os.path.join(OUT, "ew_shirt.png")); pants().save(os.path.join(OUT, "ew_pants.png")); print("wrote", OUT)

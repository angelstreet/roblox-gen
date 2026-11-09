#!/usr/bin/env python3
"""Tidewatch Warden - classic shirt + pants v2: every face is painted at 4x (own canvas) with shading, then downsampled.
Layout rects = official Roblox R15 templates. Usage: python3 make_clothing.py [outdir]   (v1 kept in make_clothing_v1.py)
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = sys.argv[1] if (len(sys.argv) > 1 and __name__ == "__main__") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
W, H, S = 585, 559, 4
CL_TOP, CL_BOT = (30, 44, 78), (9, 14, 28)            # cloth
PEARL, PEARL_D = (240, 244, 246), (170, 184, 196)
AQUA, AQUA_D = (80, 230, 230), (28, 140, 165)
BR_HI, BR, BR_LO = (250, 214, 150), (190, 138, 70), (112, 74, 36)   # metal ramp
INK = (6, 10, 20)

SHIRT = {
    "t_up": (231, 8, 128, 64), "t_front": (231, 74, 128, 128), "t_back": (427, 74, 128, 128),
    "t_right": (165, 74, 64, 128), "t_left": (361, 74, 64, 128), "t_down": (231, 204, 128, 64),
    "ra_up": (217, 289, 64, 64), "ra_front": (217, 355, 64, 128), "ra_back": (85, 355, 64, 128),
    "ra_right": (151, 355, 64, 128), "ra_left": (19, 355, 64, 128), "ra_down": (217, 485, 64, 64),
    "la_up": (308, 289, 64, 64), "la_front": (308, 355, 64, 128), "la_back": (440, 355, 64, 128),
    "la_right": (506, 355, 64, 128), "la_left": (374, 355, 64, 128), "la_down": (308, 485, 64, 64),
}
PANTS = {k.replace("ra_", "rl_").replace("la_", "ll_"): v for k, v in SHIRT.items()}


class Face:
    def __init__(self, w, h, seed=1, top=CL_TOP, bot=CL_BOT, folds=1.0):
        self.w, self.h = w, h; ww, hh = w * S, h * S
        y, x = np.mgrid[0:hh, 0:ww].astype(np.float32); u = x / ww; v = y / hh
        base = np.array(top, np.float32)[None, None] * (1 - v[..., None]) + np.array(bot, np.float32)[None, None] * v[..., None]
        k = 1 + folds * (0.10 * np.sin(u * 2 * math.pi * (w / 22) + 0.5 * np.sin(v * 5 + seed)) + 0.05 * np.sin(u * 2 * math.pi * (w / 9) + seed))
        k *= 1 + 0.10 * (1 - np.abs(u - 0.5) * 2) * (1 - v)             # soft top-centre light
        rng = np.random.default_rng(seed); weave = ((np.sin(x * 1.1) * np.sin(y * 1.1)) * 0.012 + rng.normal(0, 0.012, (hh, ww)))
        a = np.clip(base * (k + weave)[..., None], 0, 255).astype(np.uint8)
        self.im = Image.fromarray(a, "RGB").convert("RGBA"); self.d = ImageDraw.Draw(self.im)
        self.sh = Image.new("L", (ww, hh), 0); self.sd = ImageDraw.Draw(self.sh)
        self.glow = Image.new("RGBA", (ww, hh), (0, 0, 0, 0)); self.gd = ImageDraw.Draw(self.glow)

    def s(self, p): return [(a * S, b * S) for a, b in p]
    def box(self, x0, y0, x1, y1): return [x0 * S, y0 * S, x1 * S - 1, y1 * S - 1]

    def metal(self, poly, top=BR_HI, mid=BR, bot=BR_LO, outline_dark=True):
        """metal-looking fill: 3-stop vertical ramp inside polygon + dark rim + light top edge"""
        pts = self.s(poly); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = int(min(xs)), int(max(xs)) + 1, int(min(ys)), int(max(ys)) + 1
        hh = max(1, y1 - y0); t = np.linspace(0, 1, hh)[:, None, None]
        top_, mid_, bot_ = (np.array(q, np.float32)[None, None] for q in (top, mid, bot))
        c = np.where(t < 0.35, top_ + (mid_ - top_) * (t / 0.35), mid_ + (bot_ - mid_) * ((t - 0.35) / 0.65))
        ramp = Image.fromarray(np.broadcast_to(c, (hh, x1 - x0, 3)).astype(np.uint8), "RGB")
        mask = Image.new("L", self.im.size, 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
        layer = Image.new("RGB", self.im.size, (0, 0, 0)); layer.paste(ramp, (x0, y0))
        self.im.paste(layer, (0, 0), mask); self.d = ImageDraw.Draw(self.im)
        if outline_dark: self.d.line(pts + [pts[0]], fill=BR_LO + (255,), width=max(1, S // 2))

    def drop(self, poly, r=1.5, amt=150, dx=0.0, dy=1.0):
        """AO / drop shadow under a shape"""
        self.sd.polygon([(a + dx * S, b + dy * S) for a, b in self.s(poly)], fill=amt)

    def line(self, p, col, w=1.0): self.d.line(self.s(p), fill=col + (255,), width=max(1, int(w * S)), joint="curve")
    def poly(self, p, col, outline=None): self.d.polygon(self.s(p), fill=col + (255,), outline=(outline + (255,)) if outline else None)
    def rect(self, x0, y0, x1, y1, col): self.d.rectangle(self.box(x0, y0, x1, y1), fill=col + (255,))
    def grad_rect(self, x0, y0, x1, y1, top, bot):
        w, h = int((x1 - x0) * S), int((y1 - y0) * S); t = np.linspace(0, 1, h)[:, None, None]
        a = np.array(top)[None, None] * (1 - t) + np.array(bot)[None, None] * t
        self.im.paste(Image.fromarray(np.broadcast_to(a, (h, w, 3)).astype(np.uint8), "RGB"), (int(x0 * S), int(y0 * S))); self.d = ImageDraw.Draw(self.im)
    def glowdot(self, cx, cy, r, col=AQUA): self.gd.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=col + (255,))

    def emblem(self, cx, cy, r):
        self.glowdot(cx, cy, r * 1.0)
        self.d.ellipse([(cx - r - 1.2) * S, (cy - r - 1.2) * S, (cx + r + 1.2) * S, (cy + r + 1.2) * S], fill=INK + (255,))
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=BR + (255,), width=max(2, int(r * S * 0.13)))
        self.d.ellipse([(cx - r * .60) * S, (cy - r * .60) * S, (cx + r * .60) * S, (cy + r * .60) * S], fill=AQUA + (255,))
        self.d.ellipse([(cx - r * .60) * S, (cy - r * .60) * S, (cx + r * .60) * S, (cy + r * .15) * S], fill=(150, 250, 250, 255))   # sheen
        self.d.ellipse([(cx - r * .60) * S, (cy - r * .60) * S, (cx + r * .60) * S, (cy + r * .60) * S], outline=AQUA_D + (255,), width=S)
        self.d.ellipse([(cx - r * .30) * S, (cy - r * .78) * S, (cx + r * .94) * S, (cy + r * .46) * S], fill=INK + (255,))
        self.d.line(self.s([(cx - r * .6, cy + r * .5), (cx - r * .2, cy + r * .1), (cx + r * .1, cy + r * .35), (cx + r * .45, cy - r * .05), (cx + r * .6, cy + r * .45)]),
                    fill=PEARL + (255,), width=max(2, int(r * S * 0.11)), joint="curve")
        self.d.ellipse([(cx + r * .05) * S, (cy - r * .55) * S, (cx + r * .27) * S, (cy - r * .33) * S], fill=PEARL + (255,))

    def finish(self):
        g = self.glow.filter(ImageFilter.GaussianBlur(S * 3)); g.putalpha(g.getchannel("A").point(lambda a: int(a * 0.55)))
        sh = self.sh.filter(ImageFilter.GaussianBlur(S * 1.6))
        dark = Image.new("RGBA", self.im.size, (0, 0, 0, 255)); dark.putalpha(sh)
        # shadows go UNDER later shapes only if drawn first; here they darken the cloth around shapes, shapes redrawn by caller order
        out = self.im.convert("RGBA")
        out = Image.alpha_composite(out, g)
        return out.resize((self.w, self.h), Image.LANCZOS)

    def apply_shadow_now(self):
        """bake the shadow layer into the cloth before shapes are drawn on top"""
        sh = self.sh.filter(ImageFilter.GaussianBlur(S * 1.6)); dark = Image.new("RGBA", self.im.size, (0, 0, 0, 255)); dark.putalpha(sh.point(lambda a: int(a * 0.9)))
        self.im = Image.alpha_composite(self.im, dark); self.d = ImageDraw.Draw(self.im)
        self.sh = Image.new("L", self.im.size, 0); self.sd = ImageDraw.Draw(self.sh)


def bar(f, x0, y0, x1, y1):                       # horizontal metal trim bar with bevel
    f.drop([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], dy=1.2); f.apply_shadow_now()
    f.metal([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def belt(f, y0, buckle=True):
    w = f.w
    f.grad_rect(0, y0, w, f.h, (26, 30, 46), (8, 10, 18)); f.line([(0, y0 + 0.5), (w, y0 + 0.5)], BR_HI, 0.5)
    f.line([(0, y0 + 2.5), (w, y0 + 2.5)], BR_LO, 1.0)
    for i in range(0, w, 8): f.line([(i + 2, y0 + 6), (i + 5, y0 + 6)], (60, 66, 90), 0.8)       # stitches
    bar(f, 0, y0, w, y0 + 3)
    if buckle:
        cx = w / 2; poly = [(cx - 14, y0 - 1), (cx + 14, y0 - 1), (cx + 11, f.h), (cx - 11, f.h)]
        f.drop(poly, dy=1.5); f.apply_shadow_now(); f.metal(poly)
        f.d.ellipse([(cx - 6) * S, (y0 + 5) * S, (cx + 6) * S, (y0 + 17) * S], fill=INK + (255,)); f.glowdot(cx, y0 + 11, 5)
        f.d.ellipse([(cx - 4.5) * S, (y0 + 6.5) * S, (cx + 4.5) * S, (y0 + 15.5) * S], fill=AQUA + (255,))
        f.d.ellipse([(cx - 3) * S, (y0 + 7.5) * S, (cx + 1) * S, (y0 + 11) * S], fill=(200, 255, 255, 255))


def plate(f, x0, y0, x1, y1, rune=True):          # layered shoulder/chest slab
    poly = [(x0 + 3, y0), (x1 - 3, y0), (x1, y0 + 4), (x1 - 2, y1), (x0 + 2, y1), (x0, y0 + 4)]
    f.drop(poly, dy=2, amt=200); f.apply_shadow_now(); f.metal(poly, mid=(150, 108, 56))
    inner = [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x1 - 4, y1 - 3), (x0 + 4, y1 - 3)]
    f.grad_rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, (32, 44, 76), (10, 14, 28))
    f.line([(x0 + 3, y0 + 3), (x1 - 3, y0 + 3)], (90, 110, 150), 0.5)
    if rune:
        f.glowdot((x0 + x1) / 2, (y0 + y1) / 2, 3, AQUA); f.line([(x0 + 7, (y0 + y1) / 2), (x1 - 7, (y0 + y1) / 2)], AQUA, 0.9)


def satin(f, x0, y0, x1, y1, top_poly):          # pearl satin tunic with highlight streaks
    f.metal(top_poly, top=(252, 254, 255), mid=(222, 230, 236), bot=PEARL_D, outline_dark=False)
    cx = (x0 + x1) / 2
    for dx, a in ((-14, (200, 210, 220)), (-5, (255, 255, 255)), (7, (205, 214, 224)), (16, (255, 255, 255))):
        f.line([(cx + dx, y0 + 1), (cx + dx * 0.8, y0 + 62)], a, 0.8)


# ---------------- SHIRT ----------------
def shirt():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 10
    for name, r in SHIRT.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed)
        if name == "t_front":
            tun = [(24, 0), (w - 24, 0), (w - 42, 74), (w // 2, 112), (42, 74)]
            f.drop(tun, dy=1.5, amt=190); f.apply_shadow_now()
            satin(f, 24, 0, w - 24, 74, tun)
            f.poly([(42, 0), (w - 42, 0), (w // 2, 50)], INK)                               # collar V (dark under-robe)
            f.line([(42, 0), (w // 2, 50), (w - 42, 0)], BR, 1.2)
            f.line([(24, 0), (42, 74), (w // 2, 112), (w - 42, 74), (w - 24, 0)], BR_LO, 2.6); f.line([(24, 0), (42, 74), (w // 2, 112), (w - 42, 74), (w - 24, 0)], BR, 1.6)
            f.line([(25, 1), (43, 74)], BR_HI, 0.5); f.line([(w - 25, 1), (w - 43, 74)], BR_HI, 0.5)
            plate(f, 3, 2, 37, 40); plate(f, w - 37, 2, w - 3, 40)
            plate(f, 5, 36, 33, 52, rune=False); plate(f, w - 33, 36, w - 5, 52, rune=False)       # second stacked slab
            f.emblem(w // 2, 84, 15)
            belt(f, 108)
        elif name == "t_back":
            pan = [(16, 0), (w - 16, 0), (w - 26, 108), (26, 108)]
            f.drop(pan, dy=1, amt=170); f.apply_shadow_now()
            f.grad_rect(16, 0, w - 16, 108, (22, 34, 62), (8, 12, 24)); f.d.polygon(f.s([(0, 0), (16, 0), (26, 108), (0, 108)]), fill=CL_BOT + (255,)); f.d.polygon(f.s([(w, 0), (w - 16, 0), (w - 26, 108), (w, 108)]), fill=CL_BOT + (255,))
            for i, dx in enumerate((-30, -15, 15, 30)): f.line([(w / 2 + dx, 2), (w / 2 + dx * 1.15, 106)], (4, 7, 16), 1.4); f.line([(w / 2 + dx + 1.5, 2), (w / 2 + dx * 1.15 + 1.5, 106)], (44, 62, 100), 0.5)
            f.line([(16, 0), (26, 108)], BR, 2); f.line([(w - 16, 0), (w - 26, 108)], BR, 2)
            f.emblem(w // 2, 50, 28)
            f.line([(w / 2 - 18 + i * 4, 96 + math.sin(i) * 2) for i in range(10)], PEARL, 1.0)
            belt(f, 108, buckle=False)
        elif name in ("t_right", "t_left"):
            for dx in (14, 34, 50): f.line([(dx, 0), (dx + 3, 106)], (4, 7, 16), 1.3)
            belt(f, 108, buckle=False)
        elif name[:2] in ("ra", "la") and name[3:] in ("front", "back", "right", "left"):
            for dx in (w * 0.28, w * 0.62): f.line([(dx, 38), (dx + 2, 90)], (4, 7, 16), 1.3); f.line([(dx + 1.4, 38), (dx + 3.4, 90)], (46, 64, 104), 0.5)
            f.line([(w / 2, 40), (w / 2, 76)], AQUA_D, 1.0); f.glowdot(w / 2, 58, 4, AQUA_D)
            bar(f, 0, 76, w, 79)
            plate(f, 1, 0, w - 1, 22, rune=True); plate(f, 3, 18, w - 3, 36, rune=False)           # layered pauldron
            bar(f, 0, 90, w, 96)
            f.grad_rect(0, 96, w, 128, (232, 238, 244), PEARL_D)                                       # gauntlet
            f.line([(10, 108), (w - 10, 108)], (255, 255, 255), 1.0); f.line([(10, 110), (w - 10, 110)], (150, 164, 178), 0.8)
            f.rect(0, 96, 2, 128, (140, 154, 168)); f.rect(w - 2, 96, w, 128, (140, 154, 168))
        elif name.endswith("_up"):
            f.rect(0, 0, w, h, INK) if name.startswith("t") else f.grad_rect(0, 0, w, h, (60, 44, 24), BR_LO)
        elif name.endswith("_down"):
            f.rect(0, 0, w, h, INK if name.startswith("t") else PEARL_D)
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


# ---------------- PANTS ----------------
def pants():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); seed = 40
    for name, r in PANTS.items():
        seed += 1; w, h = r[2], r[3]
        f = Face(w, h, seed, top=(22, 32, 60), bot=(7, 10, 20), folds=1.3)
        if name in ("t_front", "t_back"):
            bar(f, 0, 0, w, 20) if False else None
            f.grad_rect(0, 0, w, 20, (24, 28, 44), INK); bar(f, 0, 17, w, 21)
            for px in (6, w - 42):
                tas = [(px, 24), (px + 36, 24), (px + 31, 108), (px + 18, 124), (px + 5, 108)]
                f.drop(tas, dy=2, amt=190); f.apply_shadow_now()
                f.metal(tas, top=(70, 90, 140), mid=(34, 48, 86), bot=(14, 20, 40))
                f.line([(px + 18, 30), (px + 18, 104)], AQUA_D, 1.0); f.glowdot(px + 18, 66, 3, AQUA_D)
                f.line([(px + 1.5, 26), (px + 6.5, 108), (px + 18, 122)], BR, 1.4); f.line([(px + 34.5, 26), (px + 29.5, 108), (px + 18, 122)], BR, 1.4)
            sash = [(w / 2 - 9, 24), (w / 2 + 9, 24), (w / 2 + 7, 100), (w / 2, 112), (w / 2 - 7, 100)]
            f.drop(sash, dy=1.5, amt=200); f.apply_shadow_now(); f.metal(sash, top=(252, 254, 255), mid=(224, 232, 238), bot=PEARL_D, outline_dark=False)
            f.line([(w / 2, 28), (w / 2, 98)], AQUA, 1.0)
            if name == "t_front": f.emblem(w // 2, 118, 8) if False else None
        elif name in ("t_right", "t_left"):
            f.grad_rect(0, 0, w, 20, (24, 28, 44), INK); bar(f, 0, 17, w, 21)
        elif name.endswith("_up") or name.endswith("_down"):
            f.rect(0, 0, w, h, INK)
        else:                                                                                      # leg faces
            f.line([(w * 0.3, 0), (w * 0.3 + 1, 56)], (3, 6, 14), 1.3); f.line([(w * 0.7, 0), (w * 0.7 - 1, 56)], (3, 6, 14), 1.3)
            bar(f, 0, 82, w, 85)
            if name.endswith("front"):
                kg = [(10, 40), (w - 10, 40), (w - 13, 66), (w / 2, 78), (13, 66)]
                f.drop(kg, dy=2, amt=210); f.apply_shadow_now(); f.metal(kg)
                f.d.ellipse([(w / 2 - 6) * S, 47 * S, (w / 2 + 6) * S, 59 * S], fill=INK + (255,)); f.glowdot(w / 2, 53, 6); f.d.ellipse([(w / 2 - 4.5) * S, 48.5 * S, (w / 2 + 4.5) * S, 57.5 * S], fill=AQUA + (255,))
            f.grad_rect(0, 92, w, 128, (36, 40, 60), INK)                                           # boots
            bar(f, 0, 92, w, 100); f.line([(8, 112), (w - 8, 112)], AQUA_D, 1.0); f.line([(0, 126), (w, 126)], BR_LO, 1.5)
        c.alpha_composite(f.finish(), (r[0], r[1]))
    return c


if __name__ == "__main__":
    s = shirt(); p = pants()
    s.save(os.path.join(OUT, "tidewatch_shirt.png")); p.save(os.path.join(OUT, "tidewatch_pants.png"))
    for nm, img, tpl in (("shirt", s, "Template-Shirts-R15.png"), ("pants", p, "Template-Pants-R15.png")):
        tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates_dl", tpl)
        if os.path.exists(tp):
            bg = Image.open(tp).convert("RGBA"); bg.alpha_composite(img); bg.save(os.path.join(OUT, f"check_{nm}_on_template.png"))
    print("wrote", OUT, s.size, p.size)

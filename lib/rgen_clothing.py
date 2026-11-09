"""Shared classic-clothing painter for roblox-gen sets (extracted 2026-11-09 from tidewatch-warden/make_clothing.py, unchanged).
Face: paints one template face on its own 4x canvas (cloth gradient + folds, shadows baked first, 3-stop metal ramp, glow,
LANCZOS down). SHIRT/PANTS: official R15 585x559 template rects. Defaults are the Tidewatch palette; pass your own colours.
Import from a set folder:  sys.path.insert(0, os.path.join(HERE, "..", "..", "lib")); from rgen_clothing import Face, S, SHIRT, PANTS, W, H"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

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

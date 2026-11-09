#!/usr/bin/env python3
"""Thornwood Druid textures (1024/2048 per accessory) -> out/tex_<item>.png, emissive masks -> out/emit_<item>.png.
Bottom strip (v 0..0.06) = 8 flat swatches in the order of build_cv.CELLS (bark, moss, amber, bone, leaf, bark_dk, bone_dk, amber_dk).
Physical-space painting (same method as crystal-vanguard r11+): build_cv.py writes out/meta.json (UV rect, grid positions,
distance-to-edge fields per region) and out/ao_<item>.png (Cycles AO). Trims = distance bands, runes = projections through positions.
Emissive: amber cells + amber rune strokes only (no colour thresholds)."""
import os, math, json, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from palette import C
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
N = 1024
BARK, MOSS, AMBER, BONE = C((92, 64, 38)), C((62, 107, 46)), C((255, 178, 58)), C((233, 225, 200))
LEAF, BARK_DK, BONE_DK, AMBER_DK = C((96, 150, 60)), C((46, 32, 20)), C((168, 158, 128)), C((200, 116, 26))
STRIP = [BARK, MOSS, AMBER, BONE, LEAF, BARK_DK, BONE_DK, AMBER_DK]
F = lambda c: np.array(C(c), np.float32)
BARK_L, BARK_D = F((128, 92, 56)), F((44, 30, 18))               # bark, lit / shaded
MOSS_L, MOSS_D = F((86, 138, 60)), F((26, 56, 22))               # moss, lit / shaded
BONE_L, BONE_D = F((244, 238, 218)), F((176, 166, 136))          # pale bone
G_HI, G_MI, G_LO, G_DK = F((255, 214, 120)), F((230, 146, 40)), F((130, 72, 18)), F((64, 34, 10))   # amber trim ramp
META = json.load(open(os.path.join(OUT, "meta.json"))) if os.path.exists(os.path.join(OUT, "meta.json")) else {}


def ramp(stops, t):
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        if t <= t1: return tuple(int(c0[i] + (c1[i] - c0[i]) * (t - t0) / max(1e-6, t1 - t0)) for i in range(3))
    return stops[-1][1]


def up(grid, w, h, vrows=None):
    """bilinear upsample of a per-vertex grid (NV+1 x NU+1 [x C]) to h x w pixels; vrows = per-row v positions 0..1"""
    g = np.asarray(grid, np.float32); NV, NU = g.shape[0] - 1, g.shape[1] - 1
    gy = np.interp(np.linspace(0, 1, h), np.asarray(vrows, np.float32), np.arange(NV + 1, dtype=np.float32)) if vrows else np.linspace(0, NV, h)
    gx = np.linspace(0, NU, w)
    y0 = np.clip(np.floor(gy).astype(int), 0, max(NV - 1, 0)); x0 = np.clip(np.floor(gx).astype(int), 0, max(NU - 1, 0))
    fy = (gy - y0)[:, None]; fx = (gx - x0)[None, :]
    if g.ndim == 3: fy, fx = fy[..., None], fx[..., None]
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def metal_ramp(t):
    t = t[..., None]
    c = np.where(t < 0.3, G_MI + (G_HI - G_MI) * (t / 0.3), G_HI + (G_LO - G_HI) * np.clip((t - 0.3) / 0.5, 0, 1))
    return np.where(t > 0.82, G_DK, c)


def sample_rgba(img, ex, ey):
    S = img.shape[0]; x = (ex + 1) / 2 * (S - 1); y = (ey + 1) / 2 * (S - 1)
    ok = (x >= 0) & (x < S - 1) & (y >= 0) & (y < S - 1)
    x = np.clip(x, 0, S - 2); y = np.clip(y, 0, S - 2); x0 = x.astype(int); y0 = y.astype(int); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    r = (img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy) + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy
    r[~ok] = 0; return r


def rune_img(S=1024, n=7):
    """a row of carved runes (amber strokes with a dark outline) in [-1,1]^2 -> RGBA float 0..255"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S / 2
    P = lambda pts: [(k + x * k, k + y * k) for x, y in pts]
    AMB, OUTL = tuple(int(c) for c in AMBER) + (255,), tuple(int(c * 0.35) for c in AMBER_DK) + (255,)
    glyphs = [[(0, -0.7), (0, 0.7)], [(0, -0.7), (0.4, -0.2), (0, 0.1)], [(-0.3, -0.7), (0, -0.2), (0.3, -0.7)],
              [(0, -0.7), (0, 0.7), (0.35, 0.3)], [(-0.35, -0.2), (0.35, -0.2)], [(0.35, -0.7), (-0.35, 0.0), (0.35, 0.7)],
              [(0, 0.7), (0.4, -0.7), (0, -0.1), (-0.4, -0.7)]]
    for i in range(n):
        dx = -0.8 + 1.6 * i / (n - 1); g = glyphs[i % len(glyphs)]
        pts = [(dx + x * 0.12, y * 0.5) for x, y in g]
        d.line(P(pts), fill=OUTL, width=int(S * 0.05), joint="curve"); d.line(P(pts), fill=AMB, width=int(S * 0.026), joint="curve")
    return np.asarray(im, np.float32)


class Tex:
    """one accessory atlas: canvas (supersampled), swatch strip at the bottom, sheet regions painted from meta.json"""
    def __init__(self, item, size=N, ss=2, fill=BARK):
        self.item = item; self.S = size * ss; self.ss = ss; self.m = META.get(item, {})
        self.c = np.zeros((self.S, self.S, 3), np.float32); self.c[:] = np.asarray(fill, np.float32)
        self.emit = np.zeros((self.S, self.S), np.float32)
        h = int(self.S * 0.06)
        for k, col in enumerate(STRIP): self.c[self.S - h:, k * self.S // 8:(k + 1) * self.S // 8] = col

    def box(self, r):
        x0, x1 = int(round(r[0] * self.S)), int(round(r[2] * self.S)); y0, y1 = int(round((1 - r[3]) * self.S)), int(round((1 - r[1]) * self.S))
        return x0, x1, y0, y1

    def sheet(self, key, light=None, fold_k=1.0, base=(BARK_L, BARK_D), noise=0.02):
        s = self.m[key]; x0, x1, y0, y1 = self.box(s["rect"]); w, h = x1 - x0, y1 - y0
        vr = s.get("vrows"); pos = up(s["pos"], w, h, vr); dist = {k: up(v, w, h, vr) for k, v in s["dist"].items()}
        f = up(s["fold"], w, h, vr) if s.get("fold") else np.zeros((h, w), np.float32)
        lam = np.clip(0.6 + 0.4 * f * fold_k + (light(pos) if light else 0), 0, 1)[..., None]
        col = base[1] + (base[0] - base[1]) * lam
        rng = np.random.default_rng(zlib.crc32(key.encode()) % 999); col *= (1 + rng.normal(0, noise, (h, w)).astype(np.float32))[..., None]
        return {"x0": x0, "y0": y0, "w": w, "h": h, "pos": pos, "dist": dist, "col": col, "key": key}

    def D(self, R, fields): return np.min(np.stack([R["dist"][f] for f in fields if f in R["dist"]]), 0)

    def band(self, R, fields, d0, d1, kind="metal", mask=None, cols=None):
        D = self.D(R, fields); t = (D - d0) / (d1 - d0); inside = (t >= 0) & (t <= 1)
        if mask is not None: inside &= mask
        if kind == "metal": c = metal_ramp(np.clip(t, 0, 1))
        else: c = np.broadcast_to(cols[0], R["col"].shape)
        R["col"] = np.where(inside[..., None], c, R["col"])

    def grain(self, R, k=1.0):
        """bark grain in physical space: long wavy streaks along the surface (no texel-scale noise)"""
        P = R["pos"]; g = 0.5 + 0.5 * np.sin(P[..., 0] * 58.0 + 1.6 * np.sin(P[..., 2] * 4.0 + P[..., 1] * 3.0))
        g2 = 0.5 + 0.5 * np.sin(P[..., 2] * 90.0 + 2.2 * np.sin(P[..., 0] * 7.0))
        R["col"] = R["col"] * (1 - 0.12 * k + 0.12 * k * g[..., None] + 0.08 * k * g2[..., None])

    def emblem(self, R, img, c0, c1, rad, axes=(0, 2), flip=False, facing=None, emit=0.0, aspect=1.0):
        A, Bv = R["pos"][..., axes[0]], R["pos"][..., axes[1]]
        ex = ((-1 if flip else 1) * (A - c0)) / rad; ey = -(Bv - c1) / (rad * aspect)
        s = sample_rgba(img, ex, ey)
        if facing is not None: s[~facing(R["pos"])] = 0
        a = s[..., 3:] / 255; R["col"] = R["col"] * (1 - a) + s[..., :3] * a
        if emit: R.setdefault("emit", np.zeros(a.shape[:2], np.float32)); R["emit"] = np.maximum(R["emit"], a[..., 0] * emit)

    def put(self, R):
        self.c[R["y0"]:R["y0"] + R["h"], R["x0"]:R["x0"] + R["w"]] = R["col"]
        if "emit" in R:
            sl = (slice(R["y0"], R["y0"] + R["h"]), slice(R["x0"], R["x0"] + R["w"]))
            self.emit[sl] = np.maximum(self.emit[sl], R["emit"])

    def save(self, ao_k=0.8, noao=()):
        img = self.c; ao_p = os.path.join(OUT, f"ao_{self.item}.png")
        if os.path.exists(ao_p):
            aoi = Image.open(ao_p).convert("RGBA").resize((self.S, self.S), Image.BILINEAR)
            ao = np.asarray(aoi.convert("L").filter(ImageFilter.GaussianBlur(self.S / 400)), np.float32) / 255
            alpha = np.asarray(aoi.getchannel("A"), np.float32) / 255
            ao = ao * alpha + (1 - alpha)
            ao[self.S - int(self.S * 0.06):] = 1
            for r in noao:
                x0, x1, y0, y1 = self.box(r); ao[y0:y1, x0:x1] = 1
            img = img * ((1 - ao_k) + ao_k * ao)[..., None]
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
        if self.ss > 1: im = im.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        im.save(os.path.join(OUT, f"tex_{self.item}.png")); print("tex", self.item, im.size)
        ek = Image.fromarray(np.clip(self.emit * 255, 0, 255).astype(np.uint8), "L")
        if self.ss > 1: ek = ek.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        _emit_cells(ImageDraw.Draw(ek))
        ek.save(os.path.join(OUT, f"emit_{self.item}.png")); print("emit", self.item)


def _emit_cells(ed):
    """amber (cell 2) full glow, amber_dk (cell 7) half: the strip drives the crystal tips, gems and orb. Bone/bark/moss stay dark."""
    for k, val in ((2, 255), (7, 120)): ed.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=val)


RUNES = rune_img()


def crown():
    t = Tex("cv_crown", 1024, ss=2, fill=BARK)
    R = t.sheet("band", light=lambda p: 0.12 * np.clip(p[..., 2] - 0.3, -0.5, 0.5), base=(BARK_L, BARK_D))
    t.grain(R, 1.0)
    t.band(R, ["v0"], 0.0, 0.025, kind="metal"); t.band(R, ["v1"], 0.0, 0.03, kind="metal")
    t.emblem(R, RUNES, 0.0, 0.88, 0.22, axes=(0, 2), facing=lambda p: p[..., 1] < -0.55, emit=0.9, aspect=0.45)
    t.put(R); t.save(ao_k=0.55)


def pauldron():
    t = Tex("cv_pauldron_r", 2048, ss=1, fill=BARK)
    for k in range(3):
        R = t.sheet(f"shell{k}", light=lambda p: 0.20 * np.clip(p[..., 2] + 0.5, -0.5, 0.6) - 0.08 * np.clip(p[..., 0] + 0.2, -0.4, 0.4),
                    base=(BARK_L, BARK_D), noise=0.03)
        t.grain(R, 1.0)
        t.band(R, ["v1"], 0.0, 0.03, kind="metal")                                   # amber lip on the splintered hem
        t.band(R, ["v1"], 0.03, 0.05, kind="flat", cols=[BONE_D])                    # pale bone line under it
        if k == 0:
            t.emblem(R, RUNES, 0.0, -0.20, 0.42, axes=(1, 2), facing=lambda p: p[..., 0] < -0.55, aspect=0.45, emit=0.9)   # outer face runes
            t.emblem(R, RUNES, 0.0, -0.10, 0.42, axes=(0, 2), facing=lambda p: p[..., 1] < -0.55, aspect=0.45, emit=0.9)   # front runes
        t.put(R)
    t.save(ao_k=0.8)


def cape():
    t = Tex("cv_cape", 2048, ss=1, fill=MOSS)
    O = t.sheet("outer", light=lambda p: 0.14 * np.clip((p[..., 2] + 1.5) / 1.5, -0.5, 0.5), fold_k=1.1, base=(MOSS_L, MOSS_D))
    P = O["pos"]
    vein = np.abs(((P[..., 0] * 5.5 + 0.9 * P[..., 2]) % 1.0) - 0.5) < 0.035                 # leaf midribs, diagonal, physical space
    O["col"] = O["col"] * np.where(vein, 0.72, 1.0)[..., None]
    t.grain(O, 0.5)
    t.band(O, ["v1"], 0.0, 0.05, kind="flat", cols=[MOSS_D])
    t.band(O, ["v1"], 0.05, 0.075, kind="metal")
    t.emblem(O, RUNES, 0.0, -1.2, 0.46, axes=(0, 2), flip=True, facing=lambda p: p[..., 1] > 0.9, aspect=0.45, emit=0.9)
    t.put(O)
    t.save(ao_k=0.75)


def scarf():
    t = Tex("cv_scarf", 1024, ss=2, fill=BARK)
    R = t.sheet("ring", light=lambda p: 0.14 * np.clip(p[..., 2] + 0.1, -0.5, 0.5), base=(BARK_L, BARK_D))
    t.grain(R, 1.0)
    t.band(R, ["v0"], 0.0, 0.035, kind="flat", cols=[BONE_L])                      # pale bone rim on the top edge
    t.put(R); t.save(ao_k=0.7)


def sword():
    """staff shaft: bark with dark knot rings at the three knots (positions from meta z), spiral grain round the shaft"""
    t = Tex("cv_sword", 1024, ss=2, fill=BARK)
    R = t.sheet("shaft", light=lambda p: 0.10 * np.clip(p[..., 2] / 3.0 - 0.5, -0.5, 0.5), base=(BARK_L, BARK_D))
    P = R["pos"]; th = np.arctan2(P[..., 0], P[..., 1])
    spiral = 0.5 + 0.5 * np.sin(th * 3.0 + P[..., 2] * 7.0)
    R["col"] = R["col"] * (0.86 + 0.14 * spiral[..., None])
    for kz in (0.22, 0.52, 0.80):
        ring = np.abs(P[..., 2] - kz * 3.10) < 0.045
        R["col"] = np.where(ring[..., None], BARK_D, R["col"])
    t.put(R); t.save(ao_k=0.0)


if __name__ == "__main__":
    crown(); pauldron(); scarf(); cape(); sword()

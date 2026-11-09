#!/usr/bin/env python3
"""Ember Warden textures -> out/tex_<item>.png + out/emit_<item>.png (emissive masks). Physical-space painting: build_ew.py writes
out/meta.json (UV rect, grid positions, distance-to-edge fields per sheet) and out/ao_<item>.png (Cycles AO); trims are distance bands,
lava cracks are 3D worley-noise edges evaluated on the surface positions (so they continue across UV seams), sigils are projected.
Bottom strip (v 0..0.06) = 8 flat swatches: gold, ember, molten, obsidian, ash, red, hot, gold_dark (emissive: ember, molten, hot, red half)."""
import os, math, random, json, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
N = 1024
META = json.load(open(os.path.join(OUT, "meta.json"))) if os.path.exists(os.path.join(OUT, "meta.json")) else {}
C = lambda c: tuple(int(x) for x in c[:3])
F = lambda c: np.array(c[:3], np.float32)
STRIP = [(222, 172, 60), (255, 106, 28), (255, 190, 60), (22, 19, 28), (96, 88, 96), (170, 36, 10), (255, 236, 170), (118, 78, 16)]
G_HI, G_MI, G_LO, G_DK = F((255, 232, 150)), F((222, 172, 60)), F((140, 92, 20)), F((60, 38, 8))
OB_L, OB_M, OB_D = F((74, 66, 90)), F((34, 30, 42)), F((10, 8, 14))              # obsidian lit / mid / shade
EMBER, MOLTEN, HOTW, REDD = F((255, 106, 28)), F((255, 190, 60)), F((255, 238, 180)), F((150, 30, 8))
ENAMEL = F((150, 30, 8))


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def ramp(stops, t):
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        if t <= t1: return lerp(c0, c1, (t - t0) / max(1e-6, t1 - t0))
    return stops[-1][1]


def vgrad(d, box, stops):
    x0, y0, x1, y1 = box
    for y in range(int(y0), int(y1)): d.line([(x0, y), (x1, y)], fill=ramp(stops, (y - y0) / max(1, y1 - y0)) + (255,))


def hgrad(d, box, stops):
    x0, y0, x1, y1 = box
    for x in range(int(x0), int(x1)): d.line([(x, y0), (x, y1)], fill=ramp(stops, (x - x0) / max(1, x1 - x0)) + (255,))


def base(color=C((24, 44, 120))):
    im = Image.new("RGBA", (N, N), color + (255,)); d = ImageDraw.Draw(im)
    for k, c in enumerate(STRIP): d.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=c + (255,))
    return im, d


def sv(v): return int((1 - v) * N)      # blender v -> pixel y


def save(im, name): im.convert("RGB").save(os.path.join(OUT, f"tex_{name}.png")); print("tex", name)


# --------------------------------------------------------------------------- physical-space painter (meta.json + AO)
def up(grid, w, h, vrows=None):
    """bilinear upsample of a per-vertex grid (NV+1 x NU+1 [x C]) to h x w pixels; vrows = per-row UV v positions 0..1 (non-uniform layouts)"""
    g = np.asarray(grid, np.float32); NV, NU = g.shape[0] - 1, g.shape[1] - 1
    gy = np.interp(np.linspace(0, 1, h), np.asarray(vrows, np.float32), np.arange(NV + 1, dtype=np.float32)) if vrows else np.linspace(0, NV, h)
    gx = np.linspace(0, NU, w)
    y0 = np.clip(np.floor(gy).astype(int), 0, max(NV - 1, 0)); x0 = np.clip(np.floor(gx).astype(int), 0, max(NU - 1, 0))
    fy = (gy - y0)[:, None]; fx = (gx - x0)[None, :]
    if g.ndim == 3: fy, fx = fy[..., None], fx[..., None]
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def metal_ramp(t):
    """t 0..1 across a trim band -> gold with a lit outer edge, body, dark inner edge"""
    t = t[..., None]
    c = np.where(t < 0.3, G_MI + (G_HI - G_MI) * (t / 0.3), G_HI + (G_LO - G_HI) * np.clip((t - 0.3) / 0.5, 0, 1))
    return np.where(t > 0.82, G_DK, c)


def sample_rgba(img, ex, ey):
    """bilinear sample of an RGBA float image at normalised coords ex, ey in [-1, 1] (outside -> transparent)"""
    S = img.shape[0]; x = (ex + 1) / 2 * (S - 1); y = (ey + 1) / 2 * (S - 1)
    ok = (x >= 0) & (x < S - 1) & (y >= 0) & (y < S - 1)
    x = np.clip(x, 0, S - 2); y = np.clip(y, 0, S - 2); x0 = x.astype(int); y0 = y.astype(int); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    r = (img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy) + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy
    r[~ok] = 0; return r


class Tex:
    """one accessory atlas: canvas (ss x supersampled), swatch strip at the bottom, sheet regions painted from meta.json"""
    def __init__(self, item, size=N, ss=2, fill=(22, 19, 28)):
        self.item = item; self.S = size * ss; self.ss = ss; self.m = META.get(item, {})
        self.c = np.zeros((self.S, self.S, 3), np.float32); self.c[:] = F(fill)
        self.emit = np.zeros((self.S, self.S), np.float32)
        self.lava_a = np.zeros((self.S, self.S), np.float32); self.lava_c = np.zeros((self.S, self.S, 3), np.float32)
        self.strip()

    def strip(self):
        h = int(self.S * 0.06)
        for k, col in enumerate(STRIP): self.c[self.S - h:, k * self.S // 8:(k + 1) * self.S // 8] = col

    def box(self, r):
        x0, x1 = int(round(r[0] * self.S)), int(round(r[2] * self.S)); y0, y1 = int(round((1 - r[3]) * self.S)), int(round((1 - r[1]) * self.S))
        return x0, x1, y0, y1

    def sheet(self, key, light=None, fold_k=1.0, base=(OB_L, OB_D), noise=0.02, inner=False):
        """start a region: base colour from the fold map + a light function of the surface position; returns the region dict.
        inner=True paints the sheet's inner shell (rect_in) from the same grid positions (lining)."""
        s = self.m[key]; x0, x1, y0, y1 = self.box(s["rect_in"] if inner else s["rect"]); w, h = x1 - x0, y1 - y0
        vr = s.get("vrows"); pos = up(s["pos"], w, h, vr); dist = {k: up(v, w, h, vr) for k, v in s["dist"].items()}
        f = up(s["fold"], w, h, vr) if s.get("fold") else np.zeros((h, w), np.float32)
        lam = np.clip(0.6 + 0.4 * f * fold_k + (light(pos) if light else 0), 0, 1)[..., None]
        col = base[1] + (base[0] - base[1]) * lam
        rng = np.random.default_rng(zlib.crc32(key.encode()) % 999); col *= (1 + rng.normal(0, noise, (h, w)).astype(np.float32))[..., None]
        return {"x0": x0, "y0": y0, "w": w, "h": h, "pos": pos, "dist": dist, "col": col, "key": key}

    def D(self, R, fields): return np.min(np.stack([R["dist"][f] for f in fields if f in R["dist"]]), 0)

    def band(self, R, fields, d0, d1, kind="metal", mask=None, cols=None):
        """trim band between d0 and d1 studs from the named edges (u0/u1 sides, v0 top, v1 hem)"""
        D = self.D(R, fields); t = (D - d0) / (d1 - d0); inside = (t >= 0) & (t <= 1)
        if mask is not None: inside &= mask
        if kind == "metal": c = metal_ramp(np.clip(t, 0, 1))
        elif kind == "glow":                                                # molten edge: white-hot rim -> ember -> deep red
            tt = np.clip(t, 0, 1)[..., None]; c = np.where(tt < 0.25, HOTW + (MOLTEN - HOTW) * (tt / 0.25), np.where(tt < 0.6, MOLTEN + (EMBER - MOLTEN) * ((tt - 0.25) / 0.35), EMBER + (REDD - EMBER) * ((tt - 0.6) / 0.4)))
            R.setdefault("lava", np.zeros(inside.shape, np.float32)); R.setdefault("lavacol", np.zeros(R["col"].shape, np.float32))
            R["lavacol"] = np.where(inside[..., None], c, R["lavacol"]); R["lava"] = np.maximum(R["lava"], inside.astype(np.float32))
            R["emit"] = np.maximum(R.get("emit", np.zeros(inside.shape, np.float32)), np.where(inside, 1.0 - 0.5 * np.clip(t, 0, 1), 0).astype(np.float32)); return
        else: c = np.broadcast_to(cols[0] if cols else OB_L, R["col"].shape)
        R["col"] = np.where(inside[..., None], c, R["col"])

    def emblem(self, R, img, c0, c1, rad, axes=(0, 2), flip=False, facing=None, emit=0.0, aspect=1.0):
        """project an RGBA image through the surface positions: image x along axes[0], y along -axes[1] (up), radius rad studs"""
        A, Bv = R["pos"][..., axes[0]], R["pos"][..., axes[1]]
        ex = ((-1 if flip else 1) * (A - c0)) / rad; ey = -(Bv - c1) / (rad * aspect)
        s = sample_rgba(img, ex, ey)
        if facing is not None: s[~facing(R["pos"])] = 0
        a = s[..., 3:] / 255; R["col"] = R["col"] * (1 - a) + s[..., :3] * a
        if emit: R.setdefault("emit", np.zeros(a.shape[:2], np.float32)); R["emit"] = np.maximum(R["emit"], a[..., 0] * emit)

    def put(self, R):
        sl = (slice(R["y0"], R["y0"] + R["h"]), slice(R["x0"], R["x0"] + R["w"]))
        self.c[sl] = R["col"]
        if "lava" in R:                                                     # glowing layer: applied AFTER the AO multiply (cracks must not be darkened)
            a = R["lava"]; better = a > self.lava_a[sl]; self.lava_c[sl] = np.where(better[..., None], R["lavacol"], self.lava_c[sl]); self.lava_a[sl] = np.maximum(self.lava_a[sl], a)
        if "emit" in R: self.emit[R["y0"]:R["y0"] + R["h"], R["x0"]:R["x0"] + R["w"]] = np.maximum(self.emit[R["y0"]:R["y0"] + R["h"], R["x0"]:R["x0"] + R["w"]], R["emit"])

    def save(self, ao_k=0.8, emit_cells=True, noao=()):
        img = self.c; ao_p = os.path.join(OUT, f"ao_{self.item}.png")
        if os.path.exists(ao_p):
            aoi = Image.open(ao_p).convert("RGBA").resize((self.S, self.S), Image.BILINEAR)
            ao = np.asarray(aoi.convert("L").filter(ImageFilter.GaussianBlur(self.S / 400)), np.float32) / 255
            alpha = np.asarray(aoi.getchannel("A"), np.float32) / 255
            ao = ao * alpha + (1 - alpha)                                # outside the UV islands (alpha 0) nothing is baked: keep flat
            ao[self.S - int(self.S * 0.06):] = 1                        # swatch strip stays flat
            for r in noao:
                x0, x1, y0, y1 = self.box(r); ao[y0:y1, x0:x1] = 1      # overlapping-UV regions: the bake there is meaningless
            img = img * ((1 - ao_k) + ao_k * ao)[..., None]
        la = self.lava_a[..., None]; img = img * (1 - la) + self.lava_c * la
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
        if self.ss > 1: im = im.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        im.save(os.path.join(OUT, f"tex_{self.item}.png")); print("tex", self.item, im.size)
        ek = Image.fromarray(np.clip(self.emit * 255, 0, 255).astype(np.uint8), "L")
        if self.ss > 1: ek = ek.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        if emit_cells: _emit_cells(ImageDraw.Draw(ek))
        ek.save(os.path.join(OUT, f"emit_{self.item}.png")); print("emit", self.item)




# --------------------------------------------------------------------------- lava cracks: 3D worley edges on the surface positions
def _resize(a, w, h, mode=Image.BILINEAR): return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((w, h), mode), np.float32)


def worley(pos, seed, cell, half=2):
    """F2-F1 (about twice the distance to the nearest cell bisector, in studs) and the id pair, at 1/half resolution of pos (h, w, 3)"""
    h, w, _ = pos.shape; p = pos[::half, ::half]; hh, ww = p.shape[:2]; P = p.reshape(-1, 3)
    rng = np.random.default_rng(seed); lo = P.min(0) - cell; hi = P.max(0) + cell
    K = int(min(260, max(12, np.prod((hi - lo) / cell) * 1.4))); pts = rng.uniform(lo, hi, (K, 3)).astype(np.float32)
    f1 = np.full(len(P), 9e9, np.float32); f2 = f1.copy(); i1 = np.zeros(len(P), np.int32); i2 = i1.copy()
    for k in range(K):
        d = np.sqrt(((P - pts[k]) ** 2).sum(1)); m1 = d < f1; m2 = (~m1) & (d < f2)
        f2 = np.where(m1, f1, np.where(m2, d, f2)); i2 = np.where(m1, i1, np.where(m2, k, i2)); f1 = np.where(m1, d, f1); i1 = np.where(m1, k, i1)
    return (f2 - f1).reshape(hh, ww), (np.minimum(i1, i2) * 977 + np.maximum(i1, i2) * 31).reshape(hh, ww)


def lava(R, seed, cell=0.40, width=0.010, active=0.55, warp=0.05, halo=6.0, gain=1.0, near=None, heat=0.5):
    """glowing ember cracks into R['lava'] (alpha) / R['lavacol'] and a heat halo into R['col']; near(R) -> 0..1 weights crack activity"""
    pos = R["pos"]; h, w = pos.shape[:2]
    wp = pos + warp * np.stack([np.sin(pos[..., 1] * 11 + pos[..., 2] * 7), np.sin(pos[..., 2] * 9 + pos[..., 0] * 8), np.sin(pos[..., 0] * 10 + pos[..., 1] * 6)], -1)
    diff, ids = worley(wp, seed, cell); diff = _resize(diff, w, h)
    act = _resize(((ids % 100) / 100.0 < active).astype(np.float32), w, h, Image.NEAREST)
    if near is not None: act = act * np.clip(near, 0, 1)
    wv = width * (0.55 + 0.45 * np.sin(pos[..., 0] * 17 + pos[..., 2] * 13) ** 2)
    core = np.clip(1 - diff / (2 * wv), 0, 1) * act; hal = np.clip(1 - diff / (2 * wv * halo), 0, 1) ** 2 * act
    R["col"] = R["col"] * (1 - 0.55 * heat * hal[..., None]) + REDD * (0.55 * heat * hal[..., None])
    tt = np.clip(1 - diff / (2 * wv), 0, 1)[..., None]
    c = np.where(tt > 0.72, HOTW, np.where(tt > 0.4, MOLTEN, EMBER)) * 1.0
    a = np.clip(core * 1.4, 0, 1) * gain
    R.setdefault("lava", np.zeros((h, w), np.float32)); R.setdefault("lavacol", np.zeros((h, w, 3), np.float32))
    better = a > R["lava"]; R["lavacol"] = np.where(better[..., None], c, R["lavacol"]); R["lava"] = np.maximum(R["lava"], a)
    R["emit"] = np.maximum(R.get("emit", np.zeros((h, w), np.float32)), np.maximum(a, 0.5 * hal * gain * act))
    return act


def sigil_img(S=512):
    """flame sigil (original emblem): gold hexagonal frame, dark field, three ember tongues with a white-hot core. RGBA float + emit mask"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S / 2; P = lambda p: [(k + x * k, k + y * k) for x, y in p]
    T = lambda a: tuple(int(c) for c in a) + (255,); em = Image.new("L", (S, S), 0); ed = ImageDraw.Draw(em)
    fr = [(0, -0.95), (0.62, -0.10), (0.40, 0.78), (0, 0.95), (-0.40, 0.78), (-0.62, -0.10)]
    d.polygon(P(fr), fill=T(G_DK)); d.polygon(P([(x * 0.93, y * 0.93) for x, y in fr]), fill=T(G_MI)); d.polygon(P([(x * 0.84, y * 0.84) for x, y in fr]), fill=T(F((18, 12, 16))))
    d.polygon(P([(0, -0.62), (0.34, -0.05), (0.22, 0.55), (0, 0.78), (-0.22, 0.55), (-0.34, -0.05)]), fill=T(EMBER)); ed.polygon(P([(0, -0.62), (0.34, -0.05), (0.22, 0.55), (0, 0.78), (-0.22, 0.55), (-0.34, -0.05)]), fill=255)
    d.polygon(P([(0, -0.46), (0.18, 0.0), (0, 0.55), (-0.18, 0.0)]), fill=T(MOLTEN)); d.polygon(P([(0, -0.20), (0.07, 0.12), (0, 0.38), (-0.07, 0.12)]), fill=T(HOTW))
    for sg in (-1, 1):
        d.polygon(P([(sg * 0.40, -0.42), (sg * 0.30, 0.10), (sg * 0.50, 0.32), (sg * 0.58, -0.05)]), fill=T(EMBER)); ed.polygon(P([(sg * 0.40, -0.42), (sg * 0.30, 0.10), (sg * 0.50, 0.32), (sg * 0.58, -0.05)]), fill=230)
        d.line(P([(sg * 0.62, -0.10), (sg * 0.92, -0.40)]), fill=T(G_MI), width=int(S * 0.02))
    return np.asarray(im, np.float32), np.asarray(em, np.float32) / 255


SIGIL, SIGIL_EMIT = sigil_img()


def sigil(R, cx, cy, rad, axes=(0, 2), flip=False, facing=None, aspect=1.0):
    """project the sigil through the surface positions; colour into the lava layer so AO does not dim it"""
    A, Bv = R["pos"][..., axes[0]], R["pos"][..., axes[1]]
    ex = ((-1 if flip else 1) * (A - cx)) / rad; ey = -(Bv - cy) / (rad * aspect)
    s = sample_rgba(SIGIL, ex, ey)
    Sz = SIGIL_EMIT.shape[0]; xx = np.clip(((ex + 1) / 2 * (Sz - 1)).astype(int), 0, Sz - 1); yy = np.clip(((ey + 1) / 2 * (Sz - 1)).astype(int), 0, Sz - 1)
    em = np.where((np.abs(ex) < 1) & (np.abs(ey) < 1), SIGIL_EMIT[yy, xx], 0).astype(np.float32)
    if facing is not None: m = facing(R["pos"]); s[~m] = 0; em = em * m
    a = s[..., 3] / 255
    R.setdefault("lava", np.zeros(a.shape, np.float32)); R.setdefault("lavacol", np.zeros(a.shape + (3,), np.float32))
    better = a > R["lava"]; R["lavacol"] = np.where(better[..., None], s[..., :3], R["lavacol"]); R["lava"] = np.maximum(R["lava"], a)
    R["emit"] = np.maximum(R.get("emit", np.zeros(a.shape, np.float32)), em)


def obs_light(p, up=0.20, out=0.10):
    """obsidian lighting term: lighter up and outward (towards -x for the right shoulder)"""
    return up * np.clip((p[..., 2] + 0.6) / 1.2, -0.5, 0.6) - out * np.clip(p[..., 0], -0.5, 0.5) * 0.0


def strand_rect(t, rect, fn):
    """paint a strand rect: fn(u (0..1 around), f (0 root .. 1 tip)) -> (rgb (h,w,3), emit (h,w), lava alpha (h,w) or None)"""
    x0, x1, y0, y1 = t.box(rect); h, w = y1 - y0, x1 - x0
    f = np.linspace(1, 0, h)[:, None] * np.ones((1, w), np.float32); u = np.ones((h, 1), np.float32) * np.linspace(0, 1, w)[None, :]
    col, em, lv = fn(u, f)
    if lv is None: t.c[y0:y1, x0:x1] = np.clip(col, 0, 255)
    else:
        t.c[y0:y1, x0:x1] = np.clip(col, 0, 255)
    t.emit[y0:y1, x0:x1] = em
    return (x0, x1, y0, y1)


def mixc(stops, f):
    """colour ramp: stops [(t, rgb)] over array f -> (..., 3)"""
    out = np.zeros(f.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m = (f >= t0) & (f <= t1); k = ((f - t0) / max(1e-6, t1 - t0))[..., None]; out = np.where(m[..., None], c0 + (c1 - c0) * k, out)
    return np.where((f < stops[0][0])[..., None], stops[0][1], np.where((f > stops[-1][0])[..., None], stops[-1][1], out))


def _emit_cells(ed):
    """swatch cells that glow: ember (1), molten (2), hot (6) full, red (5) half"""
    for k, val in ((1, 255), (2, 255), (6, 255), (5, 140)): ed.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=val)


def diamonds(R, D, dc, rad, count, pitch=0.40):
    """row of gold-framed ember diamonds along a hem: `count` repeats across the region (UV u), centred dc studs from the edge field D,
    half-size rad studs; pitch = studs per repeat (so the diamonds are not squashed)"""
    h, w = D.shape; xs = np.arange(w)[None, :]; fx = (xs / w * count) % 1.0 - 0.5
    d = (np.abs(fx) * pitch) / rad + np.abs(D - dc) / rad
    fr = d < 1.0; core = d < 0.5
    R.setdefault("lava", np.zeros((h, w), np.float32)); R.setdefault("lavacol", np.zeros((h, w, 3), np.float32)); R["emit"] = R.get("emit", np.zeros((h, w), np.float32))
    R["col"] = np.where(fr[..., None] & ~core[..., None], G_MI, R["col"]); R["lavacol"] = np.where(core[..., None], MOLTEN, R["lavacol"])
    R["lava"] = np.maximum(R["lava"], core.astype(np.float32)); R["emit"] = np.maximum(R["emit"], core.astype(np.float32))


def spike_strand(t, rect, glowtip=False):
    """obsidian spike/shard/horn gradient: lit facet stripe, gold ring at the root, thin ember seam above it, glossy tip"""
    def fn(u, f):
        lit = np.cos(2 * math.pi * (u - 0.25)) * 0.5 + 0.5
        col = OB_D + (OB_L - OB_D) * (0.15 + 0.55 * lit * (0.5 + 0.5 * f))[..., None]
        col = np.where(((f > 0.0) & (f < 0.07))[..., None], G_MI, col); col = np.where(((f > 0.07) & (f < 0.10))[..., None], G_LO, col)
        col = np.where(((f > 0.10) & (f < 0.125))[..., None], EMBER, col)
        em = np.where((f > 0.10) & (f < 0.125), 1.0, 0.0).astype(np.float32)
        if glowtip: tip = np.clip((f - 0.78) / 0.22, 0, 1); col = col * (1 - tip[..., None]) + MOLTEN * tip[..., None]; em = np.maximum(em, tip)
        return col, em, None
    return strand_rect(t, rect, fn)


def helm():
    t = Tex("ew_helm", 1024, ss=2, fill=(22, 19, 28)); m = META["ew_helm"]
    D = t.sheet("dome", light=lambda p: obs_light(p, 0.35), base=(OB_L, OB_D), noise=0.02)
    lava(D, 3, 0.42, 0.010, 0.5, 0.05, 6.0, 1.0)
    t.band(D, ["v1"], 0.0, 0.03, kind="flat", cols=[G_LO]); t.put(D)
    for inner in (False, True):
        Fn = t.sheet("fin", light=lambda p: 0.18 * np.clip((p[..., 2] - 0.8) / 0.6, -0.5, 0.5), base=(OB_L, OB_D), inner=inner, noise=0.02)
        lava(Fn, 11, 0.30, 0.010, 0.6, 0.04, 6.0, 1.0)
        t.band(Fn, ["v0"], 0.0, 0.028, kind="glow"); t.put(Fn)
    def hair(u, f):
        wave = 0.5 + 0.5 * np.sin(u * 2 * math.pi * 3 + f * 6)
        root, mid, tip = F((200, 52, 10)), F((190, 40, 8)), HOTW
        col = mixc([(0, root), (0.2, F((225, 70, 14))), (0.5, EMBER), (0.82, MOLTEN), (1.0, tip)], f)
        col = col * (0.88 + 0.22 * wave[..., None]); em = np.clip(0.15 + 1.1 * f ** 1.2, 0, 1) * (0.7 + 0.3 * wave)
        return col, em.astype(np.float32), None
    strand_rect(t, tuple(m["hair"]["rect_only"]), hair)
    spike_strand(t, tuple(m["horn"]["rect_only"]), glowtip=True); spike_strand(t, tuple(m["spike"]["rect_only"]))
    t.save(ao_k=0.7, noao=[tuple(m["hair"]["rect_only"]), tuple(m["horn"]["rect_only"]), tuple(m["spike"]["rect_only"])])


def pauldron():
    t = Tex("ew_pauldron_r", 2048, ss=1, fill=(22, 19, 28)); m = META["ew_pauldron_r"]
    Rc = t.sheet("core", base=(F((120, 24, 8)), F((50, 8, 4))), noise=0.04)
    lava(Rc, 5, 0.22, 0.030, 0.9, 0.03, 4.0, 1.0, heat=0.8); Rc["emit"] = np.maximum(Rc["emit"], 0.55); t.put(Rc)
    for k in range(3):
        R = t.sheet(f"slab{k}", light=lambda p: obs_light(p, 0.40), base=(OB_L, OB_D), noise=0.025)
        if k == 0:
            sigil(R, -0.05, -0.02, 0.46, axes=(0, 1), flip=False, facing=lambda p: p[..., 2] > 0.12, aspect=1.0)
            near = np.clip((R["pos"][..., 2] + 0.2) * -2.0 + 0.6, 0.35, 1.0)
        else: near = None
        lava(R, 7 + k, 0.60 - 0.06 * k, 0.011, 0.38, 0.06, 6.0, 1.0, near=near)
        t.band(R, ["v1"], 0.0, 0.04, kind="metal"); t.band(R, ["v1"], 0.055, 0.075, kind="glow")
        t.band(R, ["v1"], 0.105, 0.118, kind="metal"); diamonds(R, R["dist"]["v1"], 0.158, 0.05 if k == 0 else 0.04, 14 if k == 0 else 10, 0.40 if k == 0 else 0.42)
        if k > 0: t.band(R, ["v0"], 0.0, 0.03, kind="flat", cols=[G_LO])
        t.put(R)
    spike_strand(t, tuple(m["spike"]["rect_only"]), glowtip=True)
    t.save(ao_k=0.75, noao=[tuple(m["spike"]["rect_only"])])


def cape():
    t = Tex("ew_cape", 2048, ss=1, fill=(30, 26, 34)); m = META["ew_cape"]; rect = m["outer"]["rect"]
    O = t.sheet("outer", light=lambda p: 0.10 * np.clip((p[..., 2] + 2.0) / 2.0, -0.5, 0.5), fold_k=1.4, base=(F((70, 62, 80)), F((16, 14, 22))), noise=0.04)
    h, w = O["col"].shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    O["col"] *= (0.93 + 0.08 * (0.5 + 0.5 * np.sin(xx * 0.9) * np.sin(yy * 0.7)))[..., None]            # fine weave
    nh = np.clip(1.0 - O["dist"]["v1"] / 0.9, 0, 1)                                                  # near the torn hem: more cracks
    lava(O, 21, 0.30, 0.008, 0.7, 0.06, 7.0, 1.0, near=0.25 + 0.75 * nh)
    D = O["dist"]["v1"]
    # charred hem: dark scorch band, then a glowing molten edge
    scorch = np.clip(1 - D / 0.16, 0, 1) ** 1.5; O["col"] = O["col"] * (1 - 0.7 * scorch[..., None]) + REDD * (0.25 * scorch[..., None])
    t.band(O, ["v1"], 0.0, 0.05, kind="glow")
    t.band(O, ["u0", "u1"], 0.0, 0.035, kind="flat", cols=[G_LO]); t.band(O, ["u0", "u1"], 0.035, 0.05, kind="flat", cols=[G_MI * 0.7])
    t.band(O, ["v0"], 0.0, 0.07, kind="metal"); t.band(O, ["v0"], 0.07, 0.085, kind="flat", cols=[G_DK])
    sigil(O, 0.0, -1.35, 0.62, axes=(0, 2), flip=True)
    t.put(O)
    I = t.sheet("outer", inner=True, fold_k=1.2, base=(F((255, 120, 36)), F((110, 18, 6))), noise=0.04, light=lambda p: -0.35 * np.clip((p[..., 2] + 0.3) / -2.4, 0, 1) + 0.25)
    hi, wi = I["col"].shape[:2]; yy, xx = np.mgrid[0:hi, 0:wi]; I["col"] *= (0.9 + 0.12 * (0.5 + 0.5 * np.sin(xx * 0.8) * np.sin(yy * 0.6)))[..., None]
    t.band(I, ["v1"], 0.0, 0.05, kind="glow"); t.band(I, ["u0", "u1"], 0.0, 0.035, kind="flat", cols=[G_LO])
    I["emit"] = np.maximum(I.get("emit", 0), 0.35 * np.clip(0.4 + 0.6 * np.clip((I["pos"][..., 2] + 0.3) / -2.4, 0, 1), 0, 1)).astype(np.float32)
    I["lava"] = I.get("lava", np.zeros(I["emit"].shape, np.float32)); I.setdefault("lavacol", np.zeros(I["col"].shape, np.float32))
    t.put(I); t.save(ao_k=0.6)


def collar():
    t = Tex("ew_collar", 1024, ss=2, fill=(22, 19, 28)); m = META["ew_collar"]
    R = t.sheet("ring", light=lambda p: obs_light(p, 0.4), base=(OB_L, OB_D), noise=0.02)
    lava(R, 31, 0.36, 0.010, 0.5, 0.05, 6.0, 1.0)
    h, w = R["col"].shape[:2]; rows = 6
    for k in range(12):                                                                                # ember rune diamonds around the ring (UV space)
        cx = int((k + 0.5) / 12 * w); cy = int(h * 0.50); r = max(3, int(h * 0.07)); img = Image.new("L", (w, h), 0); ImageDraw.Draw(img).polygon([(cx, cy - r * 1.4), (cx + r, cy), (cx, cy + r * 1.4), (cx - r, cy)], fill=255)
        mk = np.asarray(img, np.float32) / 255; R.setdefault("lava", np.zeros((h, w), np.float32)); R.setdefault("lavacol", np.zeros((h, w, 3), np.float32))
        R["lavacol"] = np.where((mk > 0.5)[..., None], MOLTEN, R["lavacol"]); R["lava"] = np.maximum(R["lava"], mk); R["emit"] = np.maximum(R.get("emit", np.zeros((h, w), np.float32)), mk)
    t.band(R, ["v0", "v1"], 0.0, 0.03, kind="metal"); t.put(R)
    P = t.sheet("plate", light=lambda p: obs_light(p, 0.4), base=(OB_L, OB_D), noise=0.02)
    sigil(P, 0.0, -0.64, 0.17, axes=(0, 2), flip=False, facing=lambda p: np.ones(p[..., 0].shape, bool)); lava(P, 33, 0.2, 0.010, 0.5, 0.03, 5.0, 1.0)
    t.band(P, ["u0", "u1", "v1"], 0.0, 0.035, kind="metal"); t.put(P)
    spike_strand(t, tuple(m["shard"]["rect_only"]), glowtip=True)
    t.save(ao_k=0.75, noao=[tuple(m["shard"]["rect_only"])])


def axe():
    t = Tex("ew_axe", 2048, ss=1, fill=(22, 19, 28)); m = META["ew_axe"]
    B_ = t.sheet("bladeA", light=lambda p: 0.25 * np.clip((p[..., 0] + 1.2) * 0.8, -0.3, 0.6), base=(F((84, 76, 98)), F((18, 15, 24))), noise=0.02)
    pos = B_["pos"]
    lava(B_, 41, 0.34, 0.010, 0.55, 0.05, 6.0, 1.0)
    B_["col"] = B_["col"] * 1.0
    heat = np.clip(1 - B_["dist"]["v0"] / 0.55, 0, 1) ** 1.3                                           # forged heat: molten at the cutting edge, cooling to obsidian at the root
    hc = np.where(heat[..., None] > 0.55, MOLTEN, np.where(heat[..., None] > 0.25, EMBER, REDD)); B_.setdefault("lava", np.zeros(heat.shape, np.float32)); B_.setdefault("lavacol", np.zeros(B_["col"].shape, np.float32))
    ha = np.clip(heat * 1.05, 0, 0.95); better = ha > B_["lava"]; B_["lavacol"] = np.where(better[..., None], hc, B_["lavacol"]); B_["lava"] = np.maximum(B_["lava"], ha)
    B_["emit"] = np.maximum(B_.get("emit", 0), heat * 0.9).astype(np.float32)
    t.band(B_, ["v0"], 0.0, 0.05, kind="glow")                                                        # white-hot cutting edge
    t.band(B_, ["v0"], 0.085, 0.10, kind="metal"); t.band(B_, ["v1"], 0.0, 0.05, kind="metal"); t.band(B_, ["u0", "u1"], 0.0, 0.03, kind="metal")
    sigil(B_, -0.66, 2.25, 0.32, axes=(0, 2), flip=False)
    t.put(B_)
    hx = tuple(m["haft"]["rect_only"]); t.box(hx)
    def haft(u, f):
        z = f * 3.95; lit = 0.5 + 0.5 * np.cos(2 * math.pi * (u * 8 % 1.0 - 0.5))
        col = OB_D + (OB_L - OB_D) * (0.1 + 0.5 * lit)[..., None]
        wrap = ((z > 0.36) & (z < 1.33)); diag = (np.sin((z * 38 + u * 8 * 6.28 * 0.6)) > 0.3)
        col = np.where((wrap & diag)[..., None], F((110, 26, 10)), np.where(wrap[..., None], F((34, 24, 26)) * (0.6 + 0.6 * lit[..., None]), col))
        gold_z = ((z < 0.32) | ((z > 1.38) & (z < 1.56)) | ((z > 1.82) & (z < 1.98)) | ((z > 3.12) & (z < 3.30)))
        col = np.where(gold_z[..., None], G_LO + (G_HI - G_LO) * (0.2 + 0.7 * lit[..., None]), col)
        seam = (np.abs(z - 1.69) < 0.02) | (np.abs(z - 2.05) < 0.02) | (np.abs(z - 3.33) < 0.025); col = np.where(seam[..., None], EMBER, col)
        em = seam.astype(np.float32); return col, em, None
    strand_rect(t, hx, haft)
    t.save(ao_k=0.75, noao=[hx])


if __name__ == "__main__":
    helm(); pauldron(); cape(); collar(); axe()

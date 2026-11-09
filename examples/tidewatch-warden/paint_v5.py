#!/usr/bin/env python3
"""Paint the v5 accessory textures from out/v5/meta.json (grid positions, fold maps, distance-to-edge fields) and the
baked AO maps (out/v5/ao_<item>.png). Trims are painted as distance bands measured in studs on the real surface, so a
bronze edge is the same physical width everywhere; emblems are drawn once and projected through the surface positions.
Usage: python3 paint_v5.py   -> out/v5/tex_<item>.png
"""
import json, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "v5")
META = json.load(open(os.path.join(OUT, "meta.json")))
C_L, C_D = np.array((21, 25, 38), np.float32), np.array((6, 7, 12), np.float32)      # near-black navy cloth
INNER = np.array((6, 7, 11), np.float32)
BR_HI, BR, BR_LO, BR_DK = (np.array(c, np.float32) for c in ((255, 224, 156), (204, 146, 66), (118, 76, 30), (34, 20, 8)))
PEARL = np.array((234, 236, 240), np.float32); AQUA = np.array((80, 228, 222), np.float32)
SWATCH = [(196, 140, 62), (232, 234, 238), (80, 226, 220), (10, 12, 18)]


def up(grid, w, h):
    g = np.asarray(grid, np.float32); NV, NU = g.shape[0] - 1, g.shape[1] - 1
    gy = np.linspace(0, NV, h); gx = np.linspace(0, NU, w)
    y0 = np.clip(np.floor(gy).astype(int), 0, max(NV - 1, 0)); x0 = np.clip(np.floor(gx).astype(int), 0, max(NU - 1, 0))
    fy = (gy - y0)[:, None]; fx = (gx - x0)[None, :]
    if g.ndim == 3: fy, fx = fy[..., None], fx[..., None]
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def metal_ramp(t):
    t = t[..., None]
    c = np.where(t < 0.3, BR + (BR_HI - BR) * (t / 0.3), BR_HI + (BR_LO - BR_HI) * np.clip((t - 0.3) / 0.5, 0, 1))
    return np.where(t > 0.82, BR_DK, c)


def sample_rgba(img, ex, ey):
    """bilinear sample of an RGBA float image at normalised coords ex,ey in [-1,1]"""
    S = img.shape[0]; x = (ex + 1) / 2 * (S - 1); y = (ey + 1) / 2 * (S - 1)
    ok = (x >= 0) & (x < S - 1) & (y >= 0) & (y < S - 1)
    x = np.clip(x, 0, S - 2); y = np.clip(y, 0, S - 2); x0 = x.astype(int); y0 = y.astype(int); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    r = (img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy) + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy
    r[~ok] = 0; return r


def emboss(mask, S, base_top=BR_HI, base_bot=BR_LO, out_px=None, e_px=None):
    """mask (L image) -> RGBA float array: dark outline, vertical metal ramp, lit top-left edge, dark bottom-right edge"""
    out_px = out_px or max(3, S // 90); e_px = e_px or max(2, S // 170)
    m = np.asarray(mask, np.float32) / 255
    dil = np.asarray(mask.filter(ImageFilter.MaxFilter(2 * out_px + 1)), np.float32) / 255
    sh = lambda a, dx, dy: np.roll(np.roll(a, dy, 0), dx, 1)
    lit = np.clip(m - sh(m, e_px, e_px), 0, 1); dark = np.clip(m - sh(m, -e_px, -e_px), 0, 1)
    ys = np.nonzero(m.max(1) > 0)[0]; y0, y1 = (ys.min(), ys.max()) if len(ys) else (0, S)
    t = np.clip((np.arange(S) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    ramp = np.where(t < 0.35, base_top + (BR - base_top) * (t / 0.35), BR + (base_bot - BR) * ((t - 0.35) / 0.65))
    col = np.broadcast_to(ramp, (S, S, 3)).copy()
    col = col * (1 - lit[..., None]) + BR_HI[None, None] * 1.0 * lit[..., None]
    col = col * (1 - dark[..., None]) + BR_DK[None, None] * dark[..., None]
    col = col * m[..., None] + BR_DK[None, None] * (1 - m[..., None])
    return np.concatenate([col, dil[..., None] * 255], -1)


def tidemark(S=1024, aqua=True):
    """our emblem, the Tidemark: a crescent cradling a curling wave crest, two tide lines, one aqua 'moon' dot"""
    k = S / 2; P = lambda x, y: (k + x * k, k + y * k)
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    d.ellipse([*P(-0.80, -0.80), *P(0.80, 0.80)], fill=255)
    d.ellipse([*P(0.26 - 0.66, -0.18 - 0.66), *P(0.26 + 0.66, -0.18 + 0.66)], fill=0)
    wave = [(-0.50, 0.32), (-0.30, 0.16), (-0.10, 0.0), (0.08, -0.14), (0.24, -0.22), (0.38, -0.18), (0.46, -0.06), (0.42, 0.04), (0.32, 0.06), (0.27, -0.02)]
    d.line([P(*p) for p in wave], fill=255, width=int(0.12 * k), joint="curve")
    for p in (wave[0], wave[-1]): d.ellipse([*P(p[0] - 0.06, p[1] - 0.06), *P(p[0] + 0.06, p[1] + 0.06)], fill=255)
    d.line([P(-0.30, 0.50), P(-0.08, 0.42), P(0.14, 0.46), P(0.34, 0.40)], fill=255, width=int(0.06 * k), joint="curve")
    d.line([P(-0.12, 0.64), P(0.06, 0.58), P(0.22, 0.61)], fill=255, width=int(0.045 * k), joint="curve")
    rgba = emboss(m, S)
    if aqua:
        g = Image.new("L", (S, S), 0); ImageDraw.Draw(g).ellipse([*P(0.36 - 0.10, -0.50 - 0.10), *P(0.36 + 0.10, -0.50 + 0.10)], fill=255)
        ga = np.asarray(g, np.float32) / 255; halo = np.asarray(g.filter(ImageFilter.GaussianBlur(S / 40)), np.float32) / 255
        hi = Image.new("L", (S, S), 0); ImageDraw.Draw(hi).ellipse([*P(0.31, -0.57), *P(0.37, -0.51)], fill=255); hi = np.asarray(hi, np.float32) / 255
        col = AQUA * ga[..., None] + np.array((255, 255, 255), np.float32) * hi[..., None] * 0.9
        a = rgba[..., 3:] / 255
        rgba[..., :3] = rgba[..., :3] * (1 - ga[..., None]) + col * ga[..., None] + AQUA * (halo * (1 - ga) * 0.5)[..., None] * (1 - a)
        rgba[..., 3] = np.maximum(rgba[..., 3], np.maximum(ga, halo * 0.5) * 255)
    return rgba


EMB = tidemark(); EMB_NA = tidemark(aqua=False)


class Tex:
    def __init__(self, item, size, ss=2):
        self.item = item; self.S = size * ss; self.ss = ss; self.m = META[item]
        self.c = np.zeros((self.S, self.S, 3), np.float32); self.c[:] = INNER
        h = int(self.S * 0.05)
        for k, col in enumerate(SWATCH): self.c[self.S - h:, k * self.S // 4:(k + 1) * self.S // 4] = col

    def box(self, r):
        x0, x1 = int(round(r[0] * self.S)), int(round(r[2] * self.S)); y0, y1 = int(round((1 - r[3]) * self.S)), int(round((1 - r[1]) * self.S))
        return x0, x1, y0, y1

    def sheet(self, key, light=None, fold_k=1.0, base=(C_L, C_D)):
        s = self.m[key]; x0, x1, y0, y1 = self.box(s["rect"]); w, h = x1 - x0, y1 - y0
        pos = up(s["pos"], w, h); dist = {k: up(v, w, h) for k, v in s["dist"].items()}
        f = up(s["fold"], w, h) if s.get("fold") else np.zeros((h, w), np.float32)
        lam = np.clip(0.55 + 0.42 * f * fold_k + (light(pos) if light else 0), 0, 1)[..., None]
        col = base[1] + (base[0] - base[1]) * lam
        rng = np.random.default_rng(hash(key) % 999); col *= (1 + rng.normal(0, 0.03, (h, w)).astype(np.float32))[..., None]
        if s.get("rect_in"):
            a0, a1, b0, b1 = self.box(s["rect_in"]); fi = up(s["fold"], a1 - a0, b1 - b0) if s.get("fold") else 0
            self.c[b0:b1, a0:a1] = INNER * (1 + 0.15 * fi)[..., None] if s.get("fold") else INNER
        return {"x0": x0, "y0": y0, "w": w, "h": h, "pos": pos, "dist": dist, "col": col}

    def band(self, R, fields, d0, d1, kind="metal", mask=None):
        D = np.min(np.stack([R["dist"][f] for f in fields if f in R["dist"]]), 0)
        t = (D - d0) / (d1 - d0); inside = (t >= 0) & (t <= 1)
        if mask is not None: inside &= mask
        if kind == "metal": c = metal_ramp(np.clip(t, 0, 1))
        else: c = np.broadcast_to(PEARL, R["col"].shape)
        R["col"] = np.where(inside[..., None], c, R["col"])

    def emblem(self, R, img, cx, cz, rad, flip=False, facing=None):
        X, Y, Z = R["pos"][..., 0], R["pos"][..., 1], R["pos"][..., 2]
        ex = ((-1 if flip else 1) * (X - cx)) / rad; ey = -(Z - cz) / rad
        s = sample_rgba(img, ex, ey)
        if facing is not None: s[~facing(R["pos"])] = 0
        a = s[..., 3:] / 255; R["col"] = R["col"] * (1 - a) + s[..., :3] * a

    def put(self, R): self.c[R["y0"]:R["y0"] + R["h"], R["x0"]:R["x0"] + R["w"]] = R["col"]

    def poly_region(self, key, fill_fn):
        s = self.m[key]; x0, x1, y0, y1 = self.box(s["rect"]); amin, amax, bmin, bmax = s["bbox"]
        pts = [(x0 + (a - amin) / (amax - amin) * (x1 - x0), y1 - (b - bmin) / (bmax - bmin) * (y1 - y0)) for a, b in s["pts"]]
        fill_fn(self, x0, x1, y0, y1, pts)

    def save(self, ao_obj=None, ao_k=0.75):
        img = self.c
        ao_p = os.path.join(OUT, f"ao_{ao_obj or self.item}.png")
        if os.path.exists(ao_p):
            ao = np.asarray(Image.open(ao_p).convert("L").resize((self.S, self.S), Image.BILINEAR), np.float32) / 255
            ao[self.S - int(self.S * 0.05):] = 1
            img = img * ((1 - ao_k) + ao_k * ao)[..., None]
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
        if self.ss > 1: im = im.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        im.save(os.path.join(OUT, f"tex_{self.item}.png")); print("tex", self.item, im.size)


def metal_fill(t, x0, x1, y0, y1, pts, inset_frac=0.0, dark_inset=None, pearl_inlay=False):
    S = t.S; m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    rg = emboss(m, S, out_px=max(2, S // 300), e_px=max(2, S // 400))
    a = rg[..., 3:] / 255; reg = (slice(y0, y1), slice(x0, x1))
    t.c[reg] = (t.c * (1 - a) + rg[..., :3] * a)[reg]
    mm = m.filter(ImageFilter.MinFilter(1 + 2 * max(2, S // 260)))
    if dark_inset:
        e = m.filter(ImageFilter.MinFilter(1 + 2 * dark_inset)); ea = np.asarray(e, np.float32)[..., None] / 255
        t.c[reg] = (t.c * (1 - ea) + np.array((14, 16, 26), np.float32) * ea)[reg]
    if pearl_inlay:
        e1 = m.filter(ImageFilter.MinFilter(1 + 2 * (S // 75))); e2 = e1.filter(ImageFilter.MinFilter(1 + 2 * (S // 300)))
        line = np.clip(np.asarray(e1, np.float32) - np.asarray(e2, np.float32), 0, 255)[..., None] / 255
        t.c[reg] = (t.c * (1 - line) + PEARL * line)[reg]


# --------------------------------------------------------------------------- items
def hood():
    t = Tex("tidecrest_hood_v5", 1024)
    R = t.sheet("outer", light=lambda p: 0.12 * np.clip(p[..., 2] - 0.2, -0.6, 0.8), fold_k=1.1)
    t.band(R, ["u0", "u1"], 0.0, 0.058)                        # face-opening edge
    t.band(R, ["v1"], 0.0, 0.036)                              # hem
    front = R["pos"][..., 1] < -0.2
    piping = (np.abs(R["pos"][..., 0]) < 0.013) & (R["pos"][..., 2] > 0.74) & (R["pos"][..., 1] < 0.35)
    R["col"] = np.where(piping[..., None], metal_ramp(np.clip(np.abs(R["pos"][..., 0]) / 0.013, 0, 1) * 0.7), R["col"])
    t.emblem(R, EMB, 0.0, 0.565, 0.17, facing=lambda p: p[..., 1] < -0.3)
    t.put(R); t.save()


def mantle():
    t = Tex("tide_mantle_v5", 1024)
    R = t.sheet("outer", light=lambda p: 0.10 * np.clip(p[..., 2], -0.8, 0.4), fold_k=1.0)
    t.band(R, ["v1"], 0.0, 0.06); t.band(R, ["v1"], 0.085, 0.104); t.band(R, ["v0"], 0.0, 0.03)
    t.put(R); t.save()


def cape():
    t = Tex("warden_cape_v5", 2048, ss=1)
    U = t.sheet("under", fold_k=1.2); t.band(U, ["u0", "u1"], 0.0, 0.04); t.band(U, ["v1"], 0.0, 0.075); t.band(U, ["v1"], 0.105, 0.13); t.put(U)
    P = t.sheet("panel", fold_k=0.8, light=lambda p: 0.06)
    t.band(P, ["u0", "u1", "v1"], 0.0, 0.05); t.band(P, ["u0", "u1", "v1"], 0.08, 0.091, kind="pearl")
    t.emblem(P, EMB, 0.0, -1.80, 0.58, flip=True)
    t.put(P); t.save()


def pauldron():
    t = Tex("tide_pauldron_r_v5", 1024)
    for k in range(3):
        R = t.sheet(f"lame{k}", light=lambda p: 0.18 * np.clip(p[..., 2] + 0.3, -0.7, 0.6), base=(np.array((26, 30, 44), np.float32), C_D))
        t.band(R, ["v1", "u0", "u1"], 0.0, 0.055)
        if k == 0: t.band(R, ["v1"], 0.08, 0.092, kind="pearl")
        t.put(R)
    x0, x1, y0, y1 = t.box(t.m["fin"]["rect"]); u = np.linspace(0, 1, x1 - x0)
    prof = np.clip(1 - np.abs(u - 0.5) * 2, 0, 1)                              # 0 at the edges, 1 on the ridge
    tt_ = np.where(u < 0.5, 0.55 - 0.5 * prof, 0.25 + 0.6 * (1 - prof))         # lit outer slope, darker inner slope
    col = metal_ramp(np.clip(tt_, 0, 1))[None, :, :].repeat(y1 - y0, 0)
    col[:, np.abs(u - 0.5) < 0.035] = PEARL; col[:, (u < 0.04) | (u > 0.96)] = BR_LO
    t.c[y0:y1, x0:x1] = col
    t.save()


def belt():
    t = Tex("tidewatch_belt_v5", 1024)
    B = t.sheet("band", base=(np.array((20, 20, 26), np.float32), np.array((7, 7, 10), np.float32)))
    t.band(B, ["v0", "v1"], 0.0, 0.03); t.put(B)
    T = t.sheet("tabard", light=lambda p: 0.05)
    t.band(T, ["u0", "u1", "v1"], 0.0, 0.038); t.band(T, ["u0", "u1", "v1"], 0.058, 0.067, kind="pearl")
    t.emblem(T, EMB_NA, 0.0, -2.58, 0.17)
    t.put(T)
    t.poly_region("buckle", lambda tt, *a: metal_fill(tt, *a, dark_inset=tt.S // 40))
    t.save()


def skirt():
    t = Tex("tidefall_skirt_v5", 1024)
    R = t.sheet("outer", fold_k=1.15)
    t.band(R, ["u0", "u1"], 0.0, 0.045); t.band(R, ["v1"], 0.0, 0.07); t.band(R, ["v1"], 0.10, 0.122)
    t.put(R); t.save()


if __name__ == "__main__":
    hood(); mantle(); cape(); pauldron(); belt(); skirt()

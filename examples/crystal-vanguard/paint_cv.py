#!/usr/bin/env python3
"""Crystal Vanguard textures (1024x1024 per accessory) -> out/tex_<item>.png. Bottom strip (v 0..0.06) = 8 flat swatches
(gold, silver, crystal, navy, ice, sapphire, white, gold_dark) shared by every item. Run after build_cv.py is NOT required (UV layout is fixed)."""
import os, math, random, json, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from palette import C   # colour theme: edit palette.py for a new set
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
N = 1024
STRIP = [C((212, 175, 55)), C((232, 238, 252)), C((120, 212, 255)), C((24, 44, 120)), C((228, 242, 255)), C((62, 126, 255)), C((248, 249, 255)), C((130, 98, 26))]
GOLD, GOLD_HI, GOLD_LO = C((212, 175, 55)), C((255, 238, 160)), C((128, 94, 22))
GOLD_DK = C((70, 48, 10))
# r11: physical-space painting (same method as tidewatch paint_v5.py): build_cv.py writes out/meta.json (per sheet: UV rect, grid
# positions, distance-to-edge fields in studs) and out/ao_<item>.png (Cycles AO). Trims = distance bands, emblems = projections.
META = json.load(open(os.path.join(OUT, "meta.json"))) if os.path.exists(os.path.join(OUT, "meta.json")) else {}
F = lambda c: np.array(C(c), np.float32)
PLATE_L, PLATE_D = F((250, 251, 255)), F((168, 186, 232))        # silver-white armour, lit / shaded (#F8F9FF .. #CAD8FF side)
ENAMEL_L, ENAMEL_D = F((70, 130, 255)), F((22, 56, 176))         # blue enamel inlay (#2E6BFF)
NAVY_L, NAVY_D = F((34, 58, 146)), F((12, 24, 70))               # navy cloth (#0D1B4D)
G_HI, G_MI, G_LO, G_DK = F((255, 238, 160)), F((212, 175, 55)), F((128, 94, 22)), F((70, 48, 10))


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
def up(grid, w, h):
    """bilinear upsample of a per-vertex grid (NV+1 x NU+1 [x C]) to h x w pixels"""
    g = np.asarray(grid, np.float32); NV, NU = g.shape[0] - 1, g.shape[1] - 1
    gy = np.linspace(0, NV, h); gx = np.linspace(0, NU, w)
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


def gold_lines(d, paths, w):
    """filigree stroke: crisp dark outline, gold body, light highlight offset up-left (PIL draw, pixel coords)"""
    for p in paths:
        d.line(p, fill=tuple(int(c) for c in G_DK) + (255,), width=int(w * 1.6), joint="curve")
    for p in paths:
        d.line(p, fill=tuple(int(c) for c in G_MI) + (255,), width=int(w), joint="curve")
    for p in paths:
        d.line([(x - w * 0.22, y - w * 0.28) for x, y in p], fill=tuple(int(c) for c in G_HI) + (255,), width=max(1, int(w * 0.4)), joint="curve")


def curl(pts, s, r, sweep=1.6 * math.pi, n=14):
    """append a shrinking spiral to a polyline; s=+1 curls left of travel"""
    (x0, y0), (x1, y1) = pts[-2], pts[-1]; tx, ty = x1 - x0, y1 - y0; L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
    px, py = -ty * s, tx * s; cx, cy = x1 + px * r, y1 + py * r; a0 = math.atan2(y1 - cy, x1 - cx); out = list(pts)
    for k in range(1, n + 1):
        t = k / n; a = a0 + s * sweep * t; rr = r * (1 - 0.62 * t); out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def scroll(a, b, amp, waves=1.0, ends=(1, -1), r=0.08, n=28):
    """S-curve from a to b (unit coords) with spiral ends -> list of points"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    pts = [(a[0] + dx * t + nx * amp * math.sin(2 * math.pi * waves * t), a[1] + dy * t + ny * amp * math.sin(2 * math.pi * waves * t)) for t in (i / n for i in range(n + 1))]
    if ends[1]: pts = curl(pts, ends[1], r)
    if ends[0]: pts = list(reversed(curl(list(reversed(pts)), ends[0], r)))
    return pts


def filigree_img(S=1024, kind="corners"):
    """gold scrollwork as an RGBA float image in [-1,1]^2: 4 corner scrolls around an empty centre (frames a gem) or a crest"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S / 2; P = lambda p: [(k + x * k, k + y * k) for x, y in p]
    paths = []
    if kind == "corners":
        for sx in (-1, 1):
            for sy in (-1, 1):
                paths.append(P([(sx * x, sy * y) for x, y in scroll((0.30, 0.62), (0.82, 0.30), 0.09, 1.0, (1 * sx * sy, -1 * sx * sy), 0.10)]))
                paths.append(P([(sx * x, sy * y) for x, y in scroll((0.52, 0.82), (0.86, 0.60), 0.05, 1.0, (0, -1 * sx * sy), 0.07, 16)]))
    elif kind == "top":                                              # cartouche for the cap top: mirrored scroll pairs around a small diamond
        for sx in (-1, 1):
            for sy in (-1, 1):
                paths.append(P([(sx * x, sy * y) for x, y in scroll((0.18, 0.30), (0.78, 0.12), 0.08, 1.0, (0, -sx * sy), 0.11)]))
        paths.append(P([(0, -0.22), (0.14, 0), (0, 0.22), (-0.14, 0), (0, -0.22)]))
    elif kind == "crest":                                            # a pair of mirrored scrolls meeting at the top (for lames)
        for sx in (-1, 1):
            paths.append(P([(sx * x, y) for x, y in scroll((0.05, -0.55), (0.85, 0.20), 0.12, 1.0, (0, -sx), 0.12)]))
            paths.append(P([(sx * x, y) for x, y in scroll((0.25, 0.55), (0.80, 0.35), 0.06, 1.0, (sx, 0), 0.08, 16)]))
    gold_lines(d, paths, S * 0.05)
    return np.asarray(im, np.float32)


def diamond_img(S=512, frame=True):
    """small gold-framed blue enamel diamond with a light facet (inlay motif)"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S / 2; P = lambda p: [(k + x * k, k + y * k) for x, y in p]
    T = lambda a: tuple(int(c) for c in a) + (255,)
    if frame: d.polygon(P([(0, -0.95), (0.62, 0), (0, 0.95), (-0.62, 0)]), fill=T(G_DK)); d.polygon(P([(0, -0.86), (0.54, 0), (0, 0.86), (-0.54, 0)]), fill=T(G_MI))
    d.polygon(P([(0, -0.68), (0.40, 0), (0, 0.68), (-0.40, 0)]), fill=T(ENAMEL_D))
    d.polygon(P([(0, -0.68), (0.40, 0), (0, 0)]), fill=T(ENAMEL_L)); d.polygon(P([(0, -0.68), (0, 0), (-0.40, 0)]), fill=T(F((120, 190, 255))))
    d.polygon(P([(0, 0.68), (-0.40, 0), (0, 0)]), fill=T(F((40, 90, 230))))
    return np.asarray(im, np.float32)


class Tex:
    """one accessory atlas: canvas (ss x supersampled), swatch strip at the bottom, sheet regions painted from meta.json"""
    def __init__(self, item, size=N, ss=2, fill=(224, 234, 255)):
        self.item = item; self.S = size * ss; self.ss = ss; self.m = META.get(item, {})
        self.c = np.zeros((self.S, self.S, 3), np.float32); self.c[:] = F(fill)
        self.emit = np.zeros((self.S, self.S), np.float32)
        self.strip()

    def strip(self):
        h = int(self.S * 0.06)
        for k, col in enumerate(STRIP): self.c[self.S - h:, k * self.S // 8:(k + 1) * self.S // 8] = col

    def box(self, r):
        x0, x1 = int(round(r[0] * self.S)), int(round(r[2] * self.S)); y0, y1 = int(round((1 - r[3]) * self.S)), int(round((1 - r[1]) * self.S))
        return x0, x1, y0, y1

    def sheet(self, key, light=None, fold_k=1.0, base=(PLATE_L, PLATE_D), noise=0.02, inner=False):
        """start a region: base colour from the fold map + a light function of the surface position; returns the region dict.
        inner=True paints the sheet's inner shell (rect_in) from the same grid positions (lining)."""
        s = self.m[key]; x0, x1, y0, y1 = self.box(s["rect_in"] if inner else s["rect"]); w, h = x1 - x0, y1 - y0
        pos = up(s["pos"], w, h); dist = {k: up(v, w, h) for k, v in s["dist"].items()}
        f = up(s["fold"], w, h) if s.get("fold") else np.zeros((h, w), np.float32)
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
        elif kind == "enamel":                                              # blue enamel: darker at both edges, lit centre, inner bevel lines
            tt = np.clip(t, 0, 1)[..., None]; c = ENAMEL_D + (ENAMEL_L - ENAMEL_D) * (1 - (2 * tt - 1) ** 2) ** 0.7
            c = np.where((tt < 0.08) | (tt > 0.92), F((12, 30, 110)), c)
        else: c = np.broadcast_to(cols[0] if cols else PLATE_L, R["col"].shape)
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
        self.c[R["y0"]:R["y0"] + R["h"], R["x0"]:R["x0"] + R["w"]] = R["col"]
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
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
        if self.ss > 1: im = im.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        im.save(os.path.join(OUT, f"tex_{self.item}.png")); print("tex", self.item, im.size)
        ek = Image.fromarray(np.clip(self.emit * 255, 0, 255).astype(np.uint8), "L")
        if self.ss > 1: ek = ek.resize((self.S // self.ss, self.S // self.ss), Image.LANCZOS)
        if emit_cells: _emit_cells(ImageDraw.Draw(ek))
        ek.save(os.path.join(OUT, f"emit_{self.item}.png")); print("emit", self.item)


FIL_CORNERS, FIL_CREST, FIL_TOP, DIAMOND = filigree_img(kind="corners"), filigree_img(kind="crest"), filigree_img(kind="top"), diamond_img()



def crown():
    """r13: dome = white hair with painted strand streaks + AO; strands rect = root (ice/silver) -> tip (white) gradient with streaks."""
    if "cv_crown" not in META:
        im, d = base(); save(im, "cv_crown"); return
    t = Tex("cv_crown", fill=(240, 244, 255))
    D = t.sheet("dome", light=lambda p: 0.16 * np.clip((p[..., 2] - 0.9) / 0.6, -0.6, 0.5), base=(F((252, 252, 255)), F((186, 200, 238))), noise=0.015)
    h, w = D["col"].shape[:2]; rng = np.random.default_rng(7); yy, xx = np.mgrid[0:h, 0:w]
    streak = np.zeros((h, w), np.float32)
    for k in range(140):                                                        # strand streaks: wavy lines from the pole down to the hem
        x0 = rng.uniform(0, w); amp = rng.uniform(4, 14); ph = rng.uniform(0, 6); wd = rng.uniform(1.5, 4.0); dark = rng.uniform(0.25, 1.0)
        xc = x0 + amp * np.sin(yy / h * 6 + ph); dd = np.abs(((xx - xc + w / 2) % w) - w / 2)
        streak = np.maximum(streak, np.clip(1 - dd / wd, 0, 1) * dark * np.clip(yy / h * 2.5, 0, 1))
    D["col"] = D["col"] * (1 - 0.22 * streak[..., None]) + F((150, 172, 225)) * 0.22 * streak[..., None]
    t.put(D)
    x0, x1, y0, y1 = t.box((0.0, 0.50, 1.0, 0.92)); hh, ww = y1 - y0, x1 - x0
    v = np.linspace(1, 0, hh)[:, None]                                          # v=1 (top of rect) = tip, v=0 = root
    root, mid, tip = F((176, 192, 236)), F((240, 244, 255)), F((255, 255, 255))
    col = np.where(v[..., None] < 0.35, root + (mid - root) * (v[..., None] / 0.35), mid + (tip - mid) * np.clip((v[..., None] - 0.35) / 0.65, 0, 1))
    col = np.broadcast_to(col, (hh, ww, 3)).copy(); ys, xs = np.mgrid[0:hh, 0:ww]
    uu = xs / ww; hl = np.cos(2 * math.pi * (uu - 0.25))[..., None]                                             # r19: silver highlight on the outer face, cool shade inside
    col = col * (1 + 0.07 * hl) + (F((255, 255, 255)) - col) * np.clip(hl, 0, 1) * 0.35 * (1 - v[..., None] * 0.5)
    col = col + (F((150, 170, 225)) - col) * np.clip(-hl, 0, 1) * 0.25
    for k in range(40):
        xc = rng.uniform(0, ww); wd = rng.uniform(2, 6); dd = np.abs(((xs - xc + ww / 2) % ww) - ww / 2)
        col -= (np.clip(1 - dd / wd, 0, 1) * (1 - v) * 0.12)[..., None] * F((60, 50, 20))
    t.c[y0:y1, x0:x1] = np.clip(col, 0, 255)
    t.save(ao_k=0.5, noao=[(0.0, 0.50, 1.0, 0.92)])


def pauldron():
    """r11: white plates with AO, gold hem trims + enamel band as distance bands, corner filigree + framed gem area on the outer face,
    enamel diamonds on the front/back faces of the lames."""
    if "cv_pauldron_r" not in META: return pauldron_legacy()
    t = Tex("cv_pauldron_r", 2048, ss=1)                                                                          # r25: 2048 (front face was ~200 px/stud in u at 1024: pixelated in Studio)
    for k in range(2):                                                                                             # r19: shell + one lame
        R = t.sheet(f"lame{k}", light=lambda p: 0.22 * np.clip(p[..., 2] + 0.6, -0.5, 0.6) - 0.10 * np.clip(p[..., 0] + 0.2, -0.4, 0.4))
        if k == 0:
            # r22: outer-face scrolls only on the skirt (projecting along x onto the near-horizontal cap smeared them in Studio);
            # the cap gets its own cartouche projected along z (dense texels, sharp strokes)
            t.emblem(R, FIL_CORNERS, 0.0, -0.22, 0.66, axes=(1, 2), facing=lambda p: (p[..., 0] < -0.6) & (p[..., 2] < 0.08), aspect=0.55)
            t.emblem(R, FIL_TOP, -0.22, 0.0, 0.46, axes=(0, 1), facing=lambda p: p[..., 2] > 0.14, aspect=0.9)
            t.emblem(R, FIL_CREST, 0.0, -0.12, 0.34, axes=(0, 2), facing=lambda p: p[..., 1] < -0.6, aspect=0.8)   # front face
            t.emblem(R, FIL_CREST, 0.0, -0.12, 0.34, axes=(0, 2), facing=lambda p: p[..., 1] > 0.6, aspect=0.8, flip=True)
        else:
            for fy, fl in ((-1, False), (1, True)):
                t.emblem(R, DIAMOND, 0.0, -0.72, 0.09, axes=(0, 2), facing=lambda p, fy=fy: p[..., 1] * fy > 0.45, aspect=1.5, flip=fl, emit=0.8)
            t.emblem(R, DIAMOND, 0.0, -0.71, 0.10, axes=(1, 2), facing=lambda p: p[..., 0] < -0.5, aspect=1.5, emit=0.8)
        # trims: gold hem, thin gold line, enamel band, thin gold line
        outer = R["pos"][..., 0] < 0.25                                                                        # no enamel on the torso-side slope
        e1 = 0.17 if k == 0 else 0.10                                                                          # lame: narrower enamel (white-dominant like the concept)
        t.band(R, ["v1"], 0.0, 0.045); t.band(R, ["v1"], 0.045, e1, kind="enamel", mask=outer); t.band(R, ["v1"], e1, e1 + 0.025, mask=outer)
        if k > 0: t.band(R, ["u0", "u1"], 0.0, 0.035); t.band(R, ["v0"], 0.0, 0.03)
        t.put(R)
    t.save()


def pauldron_legacy():
    im, d = base(C((200, 215, 245))); rnd = random.Random(3)
    for v0, v1 in ((0.70, 1.0), (0.45, 0.68), (0.20, 0.43)):
        y0, y1 = sv(v1), sv(v0); x1 = int(0.6 * N)
        vgrad(d, (0, y0, x1, y1), [(0, C((252, 253, 255))), (0.55, C((228, 237, 255))), (1.0, C((160, 182, 236)))])
        d.rectangle([0, y1 - 34, x1, y1], fill=GOLD + (255,)); d.rectangle([0, y1 - 34, x1, y1 - 26], fill=GOLD_HI + (255,)); d.rectangle([0, y1 - 8, x1, y1], fill=GOLD_LO + (255,)); d.rectangle([0, y0, x1, y0 + 8], fill=GOLD + (255,))
        for k in range(9):                                  # engraved gold filigree in each tier
            x = (k + 0.5) * x1 / 9; d.line([(x, y0 + 12), (x + 14, (y0 + y1) / 2), (x - 6, y1 - 26)], fill=GOLD + (255,), width=3)
        for k in range(18): d.line([(k * x1 / 18, y0), (k * x1 / 18 + 8, y1)], fill=(C((190, 205, 240)) + (90,)), width=2)
    # r6: soft blue halo + light core behind the big gem (outer face of the middle tier: u~0.126, v~0.565)
    gl = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (0,))); gdd = ImageDraw.Draw(gl); gx, gy = 129, sv(0.565)
    gdd.ellipse([gx - 80, gy - 120, gx + 80, gy + 120], fill=(C((110, 190, 255)) + (255,))); gl = gl.filter(ImageFilter.GaussianBlur(38))
    ga = np.array(gl); ga[..., 3] = (ga[..., 3] * 0.8).astype(np.uint8); im = Image.alpha_composite(im.convert("RGBA"), Image.fromarray(ga)); d = ImageDraw.Draw(im)
    # fill the unused right part so mip-filtering does not bleed black
    d.rectangle([int(0.62 * N), 0, N, int(0.94 * N)], fill=(C((224, 234, 255)) + (255,)))
    save(im, "cv_pauldron_r")


def scarf():
    """r13: thick navy wrap: folds + AO + fine knit weave, slightly lighter edge; tail the same with a thin ice-blue hem line."""
    if "cv_scarf" not in META:
        im, d = base(C((24, 44, 120))); save(im, "cv_scarf"); return
    t = Tex("cv_scarf", fill=(20, 38, 110))
    def knit(R):
        h, w = R["col"].shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
        k = 0.5 + 0.5 * np.sin((xx + yy) * 0.9) * np.sin((xx - yy) * 0.9)
        R["col"] *= (0.94 + 0.09 * k)[..., None]
    Rr = t.sheet("ring", light=lambda p: 0.12 * np.clip(p[..., 2] + 0.1, -0.5, 0.5), fold_k=1.0, base=(NAVY_L, NAVY_D)); knit(Rr)
    t.band(Rr, ["v0", "v1"], 0.0, 0.025, kind="flat", cols=[F((48, 76, 170))]); t.put(Rr)
    Rt = t.sheet("tail", fold_k=1.1, base=(NAVY_L, NAVY_D)); knit(Rt)
    t.band(Rt, ["u0", "u1", "v1"], 0.0, 0.02, kind="flat", cols=[F((60, 92, 190))]); t.band(Rt, ["v1"], 0.05, 0.065, kind="metal"); t.put(Rt)
    t.save(ao_k=0.8)


def crystal_emblem_img(S=1024):
    """the cape emblem: tall faceted crystal in a gold frame, two wing shards, three floating shards, ice lines. RGBA + emit mask (L)"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S / 2; P = lambda p: [(k + x * k, k + y * k) for x, y in p]
    T = lambda a: tuple(int(c) for c in a) + (255,)
    em = Image.new("L", (S, S), 0); ed = ImageDraw.Draw(em)
    # soft glow halo behind everything
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse(P([(-0.55, -0.75), (0.55, 0.75)]), fill=T(F((90, 170, 255))))
    halo = halo.filter(ImageFilter.GaussianBlur(S / 9)); ha = np.asarray(halo, np.float32); ha[..., 3] *= 0.75; im = Image.fromarray(ha.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
    def crystal(cx, cy, rx, ry, frame=True, val=255):
        if frame:
            d.polygon(P([(cx, cy - ry * 1.12), (cx + rx * 1.18, cy), (cx, cy + ry * 1.0), (cx - rx * 1.18, cy)]), fill=T(G_DK))
            d.polygon(P([(cx, cy - ry * 1.06), (cx + rx * 1.10, cy), (cx, cy + ry * 0.95), (cx - rx * 1.10, cy)]), fill=T(G_MI))
        Q = [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry * 0.86), (cx - rx, cy)]
        d.polygon(P([Q[0], Q[1], (cx, cy)]), fill=T(F((190, 240, 255)))); d.polygon(P([Q[0], (cx, cy), Q[3]]), fill=T(F((110, 190, 255))))
        d.polygon(P([Q[3], (cx, cy), Q[2]]), fill=T(F((46, 107, 255)))); d.polygon(P([(cx, cy), Q[1], Q[2]]), fill=T(F((25, 60, 190))))
        d.line(P([(cx - rx * 0.3, cy - ry * 0.45), (cx - rx * 0.08, cy - ry * 0.8)]), fill=(255, 255, 255, 255), width=max(2, int(S * 0.008)))
        ed.polygon(P(Q), fill=val)
    crystal(0, -0.05, 0.26, 0.56)
    for sg in (-1, 1):
        crystal(sg * 0.42, 0.22, 0.09, 0.26, frame=False, val=230)
        crystal(sg * 0.60, -0.18, 0.06, 0.16, frame=False, val=210)
        crystal(sg * 0.30, 0.60, 0.05, 0.13, frame=False, val=200)
        for pts in (((0.26, -0.15), (0.40, -0.30), (0.56, -0.52)), ((0.24, 0.18), (0.44, 0.40), (0.60, 0.44)), ((0.10, 0.55), (0.18, 0.80))):
            L = P([(sg * x, y) for x, y in pts]); d.line(L, fill=T(F((200, 240, 255))), width=max(2, int(S * 0.008))); ed.line(L, fill=200, width=max(2, int(S * 0.008)))
    core = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(core).ellipse(P([(-0.12, -0.35), (0.12, 0.18)]), fill=(255, 255, 255, 255)); core = core.filter(ImageFilter.GaussianBlur(S / 40))
    im = Image.alpha_composite(im, core)
    return np.asarray(im, np.float32), np.asarray(em, np.float32) / 255


CAPE_EMB, CAPE_EMB_EMIT = crystal_emblem_img()


def cape():
    """r12: outer = royal blue with folds + AO, gold border bands (sides + zigzag hem) and a thin inner line, projected crystal emblem
    (emissive); lining = silver-white with folds; collar = white, soft fur-like noise."""
    if "cv_cape" not in META: return cape_legacy()
    t = Tex("cv_cape", 2048, ss=1, fill=(40, 70, 170))
    O = t.sheet("outer", light=lambda p: 0.10 * np.clip((p[..., 2] + 2.0) / 2.0, -0.5, 0.5), fold_k=1.1, base=(F((38, 72, 200)), F((10, 22, 92))))
    t.band(O, ["u0", "u1", "v1"], 0.0, 0.07); t.band(O, ["u0", "u1", "v1"], 0.10, 0.118, kind="metal")
    t.band(O, ["v0"], 0.0, 0.04)
    # emblem on the upper third (cape centre x=0, z about -1.35 in the neck frame), flip: the outer face is seen from behind
    t.emblem(O, CAPE_EMB, 0.0, -1.40, 0.85, axes=(0, 2), flip=True, aspect=1.0)
    A, Bv = O["pos"][..., 0], O["pos"][..., 2]; ex = (-(A - 0.0)) / 0.85; ey = -(Bv + 1.40) / 0.85
    S = CAPE_EMB_EMIT.shape[0]; xx = np.clip(((ex + 1) / 2 * (S - 1)).astype(int), 0, S - 1); yy = np.clip(((ey + 1) / 2 * (S - 1)).astype(int), 0, S - 1)
    ok = (np.abs(ex) < 1) & (np.abs(ey) < 1); O["emit"] = np.where(ok, CAPE_EMB_EMIT[yy, xx], 0).astype(np.float32)
    t.put(O)
    I = t.sheet("outer", inner=True, fold_k=0.9, base=(F((226, 232, 250)), F((150, 165, 210))), noise=0.03)
    t.band(I, ["u0", "u1", "v1"], 0.0, 0.07); t.put(I)
    for inner in (False, True):
        Cc = t.sheet("collar", inner=inner, fold_k=0.6, base=(F((252, 252, 255)), F((196, 206, 236))), noise=0.05)
        h, w = Cc["col"].shape[:2]; rng = np.random.default_rng(13); yy, xx = np.mgrid[0:h, 0:w]; fur = np.zeros((h, w), np.float32)
        for k in range(160):                                                    # r22: soft fur strands along the collar height
            x0 = rng.uniform(0, w); amp = rng.uniform(3, 10); ph = rng.uniform(0, 6); wd = rng.uniform(1.5, 3.5); dark = rng.uniform(0.3, 1.0)
            xc = x0 + amp * np.sin(yy / h * 5 + ph); dd = np.abs(xx - xc)
            fur = np.maximum(fur, np.clip(1 - dd / wd, 0, 1) * dark)
        Cc["col"] = Cc["col"] * (1 - 0.18 * fur[..., None]) + F((170, 186, 230)) * 0.18 * fur[..., None]
        t.put(Cc)
    t.save(ao_k=0.75)


def cape_legacy():
    im, d = base(C((24, 44, 120)))
    H = int(0.92 * N)                    # cape rect v 0.08..1.0 maps y 0..0.92N
    arr = np.zeros((H, N, 3), np.float32)
    y, x = np.mgrid[0:H, 0:N].astype(np.float32); t = y / H; u = x / N
    top, mid, bot = np.array(C((52, 100, 235)), np.float32), np.array(C((36, 70, 190)), np.float32), np.array(C((14, 30, 110)), np.float32)
    c = np.where(t[..., None] < 0.5, top + (mid - top) * (t[..., None] / 0.5), mid + (bot - mid) * ((t[..., None] - 0.5) / 0.5))
    folds = 1 + 0.16 * np.sin(u * 2 * math.pi * 3.5 * (1 + 0.25 * t) + 0.5) + 0.07 * np.sin(u * 2 * math.pi * 9 + t * 4)
    arr = np.clip(c * folds[..., None], 0, 255)
    im.paste(Image.fromarray(arr.astype(np.uint8), "RGB"), (0, 0)); d = ImageDraw.Draw(im)
    # gold hem band (follows the scalloped bottom row), double line above it
    d.rectangle([0, H - 26, N, H], fill=GOLD + (255,)); d.rectangle([0, H - 12, N, H], fill=GOLD_HI + (255,)); d.line([(0, H - 44), (N, H - 44)], fill=GOLD + (255,), width=5)
    for k in range(6):                                  # scallop filigree above the hem
        cx = (k + 0.5) * N / 6; d.arc([cx - 70, H - 150, cx + 70, H - 40], 0, 180, fill=GOLD + (255,), width=4)
        d.line([(cx, H - 150), (cx, H - 70)], fill=(C((120, 190, 255)) + (255,)), width=3)
    # vertical gold edge lines
    d.line([(8, 0), (8, H)], fill=GOLD + (255,), width=10); d.line([(N - 8, 0), (N - 8, H)], fill=GOLD + (255,), width=10)
    # glowing crystal emblem (aspect compensated: cape ~2.6 wide x 3.8 long on a 1024 x 942 rect)
    cx, cy = N // 2, int(H * 0.33); kx, ky = 1.0, 1.75   # r10: higher, the longer cape puts the sword over the lower third
    glow = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (0,))); gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - 230, cy - 300, cx + 230, cy + 300], fill=(C((150, 225, 255)) + (255,))); glow = glow.filter(ImageFilter.GaussianBlur(80))
    ga = np.array(glow); ga[..., 3] = (ga[..., 3] * 0.9).astype(np.uint8); im = Image.alpha_composite(im.convert("RGBA"), Image.fromarray(ga)); d = ImageDraw.Draw(im)
    def dm(r_x, r_y, col, dy=0): d.polygon([(cx, cy - r_y + dy), (cx + r_x, cy + dy), (cx, cy + r_y * 0.85 + dy), (cx - r_x, cy + dy)], fill=col + (255,))
    dm(104, 190, GOLD_LO); dm(96, 178, GOLD); dm(84, 160, C((40, 110, 255)))
    P = [(cx, cy - 160), (cx + 84, cy), (cx, cy + 136), (cx - 84, cy)]
    d.polygon([P[0], P[1], (cx, cy)], fill=(C((190, 240, 255)) + (255,))); d.polygon([P[0], (cx, cy), P[3]], fill=(C((110, 190, 255)) + (255,)))
    d.polygon([P[3], (cx, cy), P[2]], fill=(C((46, 107, 255)) + (255,))); d.polygon([(cx, cy), P[1], P[2]], fill=(C((25, 60, 190)) + (255,)))
    for sg in (-1, 1):                                    # small side crystals + branching ice lines
        for (ox, oy, s) in ((150, -60, 0.5), (210, 90, 0.4), (130, 180, 0.35)):
            x = cx + sg * ox; y = cy + oy; r = 40 * s
            d.polygon([(x, y - r * 2.4), (x + r, y), (x, y + r * 1.8), (x - r, y)], fill=(C((150, 220, 255)) + (255,)), outline=GOLD + (255,))
        d.line([(cx + sg * 90, cy - 40), (cx + sg * 150, cy - 70), (cx + sg * 215, cy - 150)], fill=(C((200, 240, 255)) + (255,)), width=4)
        d.line([(cx + sg * 90, cy + 60), (cx + sg * 160, cy + 100), (cx + sg * 215, cy + 90)], fill=(C((200, 240, 255)) + (255,)), width=4)
    d.line([(cx, cy + 150), (cx, cy + 330)], fill=(C((200, 240, 255)) + (255,)), width=5)
    core = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (0,))); cd = ImageDraw.Draw(core); cd.ellipse([cx - 50, cy - 95, cx + 50, cy + 80], fill=(C((255, 255, 255)) + (255,))); core = core.filter(ImageFilter.GaussianBlur(26))
    im = Image.alpha_composite(im.convert("RGBA"), core); d = ImageDraw.Draw(im)
    # r10: emissive mask = the emblem shapes only (crisp crystal, no glow cloud, no white collar)
    ek = Image.new("L", (N, N), 0); ed = ImageDraw.Draw(ek)
    ed.polygon([(cx, cy - 178), (cx + 96, cy), (cx, cy + 151), (cx - 96, cy)], fill=110)          # gold frame: faint
    ed.polygon(P, fill=255)
    for sg in (-1, 1):
        for (ox, oy, sz) in ((150, -60, 0.5), (210, 90, 0.4), (130, 180, 0.35)):
            x = cx + sg * ox; y = cy + oy; r = 40 * sz
            ed.polygon([(x, y - r * 2.4), (x + r, y), (x, y + r * 1.8), (x - r, y)], fill=230)
        ed.line([(cx + sg * 90, cy - 40), (cx + sg * 150, cy - 70), (cx + sg * 215, cy - 150)], fill=200, width=4)
        ed.line([(cx + sg * 90, cy + 60), (cx + sg * 160, cy + 100), (cx + sg * 215, cy + 90)], fill=200, width=4)
    ed.line([(cx, cy + 150), (cx, cy + 330)], fill=200, width=5)
    _emit_cells(ed); ek.filter(ImageFilter.GaussianBlur(1.5)).save(os.path.join(OUT, "emit_cv_cape.png")); print("emit cv_cape (shapes)")
    # re-stamp the swatch strip (the emblem glow could have touched it)
    for k, col in enumerate(STRIP): d.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=col + (255,))
    save(im, "cv_cape")


def sword():
    im = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (255,))); d = ImageDraw.Draw(im)
    bands = {  # 8 horizontal bands, band k at v in [k/8,(k+1)/8] -> y from bottom
        "blade": [(0, C((16, 56, 200))), (0.35, C((40, 140, 250))), (0.7, C((120, 215, 255))), (1, C((235, 252, 255)))],
        "core": [(0, C((150, 225, 255))), (0.5, C((225, 250, 255))), (1, C((255, 255, 255)))],
        "gold": [(0, C((110, 78, 16))), (0.5, GOLD), (1, C((255, 240, 170)))],
        "sapphire": [(0, C((14, 38, 150))), (0.5, C((46, 107, 255))), (1, C((120, 175, 255)))],
        "navy": [(0, C((6, 12, 44))), (0.5, C((20, 38, 110))), (1, C((60, 92, 190)))],
        "crystal": [(0, C((60, 160, 240))), (0.5, C((130, 220, 255))), (1, C((240, 255, 255)))],
        "wrap": [(0, C((10, 20, 70))), (0.35, C((14, 28, 90))), (0.5, C((30, 70, 200))), (0.65, C((60, 120, 255))), (1, C((14, 28, 90)))]}
    for k, nm in enumerate(["blade", "core", "gold", "sapphire", "navy", "crystal", "wrap"]):
        y0 = sv((k + 1) / 8); y1 = sv(k / 8); hgrad(d, (0, y0, N, y1), bands[nm])
    # r15: blade band (k=0, v along the blade: y1 = base, y0 = tip): ice cracks + facet streaks, brighter towards the tip
    y0, y1 = sv(1 / 8), sv(0); rnd = random.Random(9)
    for q in range(14):
        x = rnd.uniform(0.15, 0.85) * N; yy = rnd.uniform(y0 + 10, y1 - 10); L = rnd.uniform(40, 110); a = rnd.uniform(-0.9, 0.9)
        d.line([(x, yy), (x + L * math.sin(a), yy - L * math.cos(a))], fill=(C((205, 245, 255)) + (255,)), width=rnd.choice((2, 3)))
    tipglow = Image.new("RGBA", (N, N), (0, 0, 0, 0)); ImageDraw.Draw(tipglow).rectangle([0, y0, N, y0 + 40], fill=(255, 255, 255, 110)); tipglow = tipglow.filter(ImageFilter.GaussianBlur(18))
    im = Image.alpha_composite(im, tipglow); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, N, sv(7 / 8) - 1], fill=(C((210, 230, 255)) + (255,)))
    save(im, "cv_sword")


def _emit_cells(ed):
    """crystal (cell 2) full glow, sapphire (cell 5) half: the swatch strip drives the crystal facets of every mesh.
    ice (cell 4) stays dark: the hair strands use it."""
    for k, val in ((2, 255), (5, 140)): ed.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=val)


def emissive_masks():
    """r10: grayscale emissive masks (white = glows) for SurfaceAppearance.EmissiveMaskContent -> out/emit_<item>.png.
    Swatch meshes: crystal/sapphire cells only (not colour thresholds: painted halos would glow as blobs).
    Sword: blade/core/crystal bands. Cape: drawn in cape() from the emblem shapes."""
    for name in ("cv_crown", "cv_pauldron_r", "cv_scarf"):
        if name in META: continue                                   # r11: Tex.save() already wrote this item's mask (shapes + cells)
        ek = Image.new("L", (N, N), 0); _emit_cells(ImageDraw.Draw(ek)); ek.save(os.path.join(OUT, f"emit_{name}.png")); print("emit", name)
    ek = Image.new("L", (N, N), 0); ed = ImageDraw.Draw(ek)
    for k, val in ((0, 200), (1, 255), (5, 255)): ed.rectangle([0, sv((k + 1) / 8), N, sv(k / 8)], fill=val)
    ek.save(os.path.join(OUT, "emit_cv_sword.png")); print("emit cv_sword")


if __name__ == "__main__":
    crown(); pauldron(); scarf(); cape(); sword(); emissive_masks()

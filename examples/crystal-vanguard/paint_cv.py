#!/usr/bin/env python3
"""Crystal Vanguard textures (1024x1024 per accessory) -> out/tex_<item>.png. Bottom strip (v 0..0.06) = 8 flat swatches
(gold, silver, crystal, navy, ice, sapphire, white, gold_dark) shared by every item. Run after build_cv.py is NOT required (UV layout is fixed)."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
N = 1024
STRIP = [(212, 175, 55), (232, 238, 252), (120, 212, 255), (24, 44, 120), (228, 242, 255), (62, 126, 255), (248, 249, 255), (130, 98, 26)]
GOLD, GOLD_HI, GOLD_LO = (212, 175, 55), (255, 238, 160), (128, 94, 22)


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


def base(color=(24, 44, 120)):
    im = Image.new("RGBA", (N, N), color + (255,)); d = ImageDraw.Draw(im)
    for k, c in enumerate(STRIP): d.rectangle([k * N // 8, int(N * 0.94), (k + 1) * N // 8, N], fill=c + (255,))
    return im, d


def sv(v): return int((1 - v) * N)      # blender v -> pixel y


def save(im, name): im.convert("RGB").save(os.path.join(OUT, f"tex_{name}.png")); print("tex", name)


def crown():
    im, d = base(); save(im, "cv_crown")


def pauldron():
    im, d = base((200, 215, 245)); rnd = random.Random(3)
    for v0, v1 in ((0.70, 1.0), (0.45, 0.68), (0.20, 0.43)):
        y0, y1 = sv(v1), sv(v0); x1 = int(0.6 * N)
        vgrad(d, (0, y0, x1, y1), [(0, (252, 253, 255)), (0.55, (228, 237, 255)), (1.0, (160, 182, 236))])
        d.rectangle([0, y1 - 34, x1, y1], fill=GOLD + (255,)); d.rectangle([0, y1 - 34, x1, y1 - 26], fill=GOLD_HI + (255,)); d.rectangle([0, y1 - 8, x1, y1], fill=GOLD_LO + (255,)); d.rectangle([0, y0, x1, y0 + 8], fill=GOLD + (255,))
        for k in range(9):                                  # engraved gold filigree in each tier
            x = (k + 0.5) * x1 / 9; d.line([(x, y0 + 12), (x + 14, (y0 + y1) / 2), (x - 6, y1 - 26)], fill=GOLD + (255,), width=3)
        for k in range(18): d.line([(k * x1 / 18, y0), (k * x1 / 18 + 8, y1)], fill=(190, 205, 240, 90), width=2)
    # r6: soft blue halo + light core behind the big gem (outer face of the middle tier: u~0.126, v~0.565)
    gl = Image.new("RGBA", (N, N), (0, 0, 0, 0)); gdd = ImageDraw.Draw(gl); gx, gy = 129, sv(0.565)
    gdd.ellipse([gx - 80, gy - 120, gx + 80, gy + 120], fill=(110, 190, 255, 255)); gl = gl.filter(ImageFilter.GaussianBlur(38))
    ga = np.array(gl); ga[..., 3] = (ga[..., 3] * 0.8).astype(np.uint8); im = Image.alpha_composite(im.convert("RGBA"), Image.fromarray(ga)); d = ImageDraw.Draw(im)
    # fill the unused right part so mip-filtering does not bleed black
    d.rectangle([int(0.62 * N), 0, N, int(0.94 * N)], fill=(224, 234, 255, 255))
    save(im, "cv_pauldron_r")


def scarf():
    im, d = base((24, 44, 120)); rnd = random.Random(5)
    vgrad(d, (0, 0, N, int(0.64 * N)), [(0, (36, 62, 150)), (1, (14, 28, 84))])
    for k in range(40):
        x = rnd.randint(0, N); d.line([(x, 0), (x + rnd.randint(-20, 20), int(0.64 * N))], fill=(70, 100, 190, 90), width=rnd.randint(2, 6))
    save(im.filter(ImageFilter.GaussianBlur(1.2)), "cv_scarf")


def cape():
    im, d = base((24, 44, 120))
    H = int(0.92 * N)                    # cape rect v 0.08..1.0 maps y 0..0.92N
    arr = np.zeros((H, N, 3), np.float32)
    y, x = np.mgrid[0:H, 0:N].astype(np.float32); t = y / H; u = x / N
    top, mid, bot = np.array((52, 100, 235), np.float32), np.array((36, 70, 190), np.float32), np.array((14, 30, 110), np.float32)
    c = np.where(t[..., None] < 0.5, top + (mid - top) * (t[..., None] / 0.5), mid + (bot - mid) * ((t[..., None] - 0.5) / 0.5))
    folds = 1 + 0.16 * np.sin(u * 2 * math.pi * 3.5 * (1 + 0.25 * t) + 0.5) + 0.07 * np.sin(u * 2 * math.pi * 9 + t * 4)
    arr = np.clip(c * folds[..., None], 0, 255)
    im.paste(Image.fromarray(arr.astype(np.uint8), "RGB"), (0, 0)); d = ImageDraw.Draw(im)
    # gold hem band (follows the scalloped bottom row), double line above it
    d.rectangle([0, H - 26, N, H], fill=GOLD + (255,)); d.rectangle([0, H - 12, N, H], fill=GOLD_HI + (255,)); d.line([(0, H - 44), (N, H - 44)], fill=GOLD + (255,), width=5)
    for k in range(6):                                  # scallop filigree above the hem
        cx = (k + 0.5) * N / 6; d.arc([cx - 70, H - 150, cx + 70, H - 40], 0, 180, fill=GOLD + (255,), width=4)
        d.line([(cx, H - 150), (cx, H - 70)], fill=(120, 190, 255, 255), width=3)
    # vertical gold edge lines
    d.line([(8, 0), (8, H)], fill=GOLD + (255,), width=10); d.line([(N - 8, 0), (N - 8, H)], fill=GOLD + (255,), width=10)
    # glowing crystal emblem (aspect compensated: cape ~2.6 wide x 3.8 long on a 1024 x 942 rect)
    cx, cy = N // 2, int(H * 0.33); kx, ky = 1.0, 1.75   # r10: higher, the longer cape puts the sword over the lower third
    glow = Image.new("RGBA", (N, N), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - 230, cy - 300, cx + 230, cy + 300], fill=(150, 225, 255, 255)); glow = glow.filter(ImageFilter.GaussianBlur(80))
    ga = np.array(glow); ga[..., 3] = (ga[..., 3] * 0.9).astype(np.uint8); im = Image.alpha_composite(im.convert("RGBA"), Image.fromarray(ga)); d = ImageDraw.Draw(im)
    def dm(r_x, r_y, col, dy=0): d.polygon([(cx, cy - r_y + dy), (cx + r_x, cy + dy), (cx, cy + r_y * 0.85 + dy), (cx - r_x, cy + dy)], fill=col + (255,))
    dm(104, 190, GOLD_LO); dm(96, 178, GOLD); dm(84, 160, (40, 110, 255))
    P = [(cx, cy - 160), (cx + 84, cy), (cx, cy + 136), (cx - 84, cy)]
    d.polygon([P[0], P[1], (cx, cy)], fill=(190, 240, 255, 255)); d.polygon([P[0], (cx, cy), P[3]], fill=(110, 190, 255, 255))
    d.polygon([P[3], (cx, cy), P[2]], fill=(46, 107, 255, 255)); d.polygon([(cx, cy), P[1], P[2]], fill=(25, 60, 190, 255))
    for sg in (-1, 1):                                    # small side crystals + branching ice lines
        for (ox, oy, s) in ((150, -60, 0.5), (210, 90, 0.4), (130, 180, 0.35)):
            x = cx + sg * ox; y = cy + oy; r = 40 * s
            d.polygon([(x, y - r * 2.4), (x + r, y), (x, y + r * 1.8), (x - r, y)], fill=(150, 220, 255, 255), outline=GOLD + (255,))
        d.line([(cx + sg * 90, cy - 40), (cx + sg * 150, cy - 70), (cx + sg * 215, cy - 150)], fill=(200, 240, 255, 255), width=4)
        d.line([(cx + sg * 90, cy + 60), (cx + sg * 160, cy + 100), (cx + sg * 215, cy + 90)], fill=(200, 240, 255, 255), width=4)
    d.line([(cx, cy + 150), (cx, cy + 330)], fill=(200, 240, 255, 255), width=5)
    core = Image.new("RGBA", (N, N), (0, 0, 0, 0)); cd = ImageDraw.Draw(core); cd.ellipse([cx - 50, cy - 95, cx + 50, cy + 80], fill=(255, 255, 255, 255)); core = core.filter(ImageFilter.GaussianBlur(26))
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
    im = Image.new("RGBA", (N, N), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    bands = {  # 8 horizontal bands, band k at v in [k/8,(k+1)/8] -> y from bottom
        "blade": [(0, (30, 120, 235)), (0.5, (96, 205, 255)), (1, (225, 252, 255))],
        "core": [(0, (150, 225, 255)), (0.5, (225, 250, 255)), (1, (255, 255, 255))],
        "gold": [(0, (110, 78, 16)), (0.5, GOLD), (1, (255, 240, 170))],
        "sapphire": [(0, (14, 38, 150)), (0.5, (46, 107, 255)), (1, (120, 175, 255))],
        "navy": [(0, (6, 12, 44)), (0.5, (20, 38, 110)), (1, (60, 92, 190))],
        "crystal": [(0, (60, 160, 240)), (0.5, (130, 220, 255)), (1, (240, 255, 255))],
        "wrap": [(0, (10, 20, 70)), (0.35, (14, 28, 90)), (0.5, (30, 70, 200)), (0.65, (60, 120, 255)), (1, (14, 28, 90))]}
    for k, nm in enumerate(["blade", "core", "gold", "sapphire", "navy", "crystal", "wrap"]):
        y0 = sv((k + 1) / 8); y1 = sv(k / 8); hgrad(d, (0, y0, N, y1), bands[nm])
    d.rectangle([0, 0, N, sv(7 / 8) - 1], fill=(210, 230, 255, 255))
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
        ek = Image.new("L", (N, N), 0); _emit_cells(ImageDraw.Draw(ek)); ek.save(os.path.join(OUT, f"emit_{name}.png")); print("emit", name)
    ek = Image.new("L", (N, N), 0); ed = ImageDraw.Draw(ek)
    for k, val in ((0, 200), (1, 255), (5, 255)): ed.rectangle([0, sv((k + 1) / 8), N, sv(k / 8)], fill=val)
    ek.save(os.path.join(OUT, "emit_cv_sword.png")); print("emit cv_sword")


if __name__ == "__main__":
    crown(); pauldron(); scarf(); cape(); sword(); emissive_masks()

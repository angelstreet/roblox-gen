#!/usr/bin/env python3
"""Texel density check for ANY set: texels per stud along u and v for every painted sheet region in <set>/out/meta.json.
Usage: python3 scripts/texel_density.py examples/<set>     (after the set's build + paint steps; exit 1 = FAIL)
Why: Roblox samples textures without anisotropic filtering; a region much denser in v than in u gets a low mip and smears
in u (crisp in Blender, blurry in Studio). Keep u/v within 0.8..1.25 (lib/rgen_mesh.py iso_rect() lays out such rects).
Only regions exported with positions ("pos", i.e. sheet(..., key=...)) are checked; swatch-cell parts (gems, strands
coloured by flat cells) carry no ornament and need no density. Textures are expected as out/tex_<item>.png."""
import json, os, sys, numpy as np
from PIL import Image
SET = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "."); OUT = os.path.join(SET, "out")
META = json.load(open(os.path.join(OUT, "meta.json")))
def tex_path(item): return os.path.join(OUT, f"tex_{item}.png")
def dens(item, key, s, mask=None):
    """u density per row (rect width / row length), v density per row band (band height from vrows / mean column segment)"""
    P = np.asarray(s["pos"], np.float32); NV, NU = P.shape[0] - 1, P.shape[1] - 1
    S = Image.open(tex_path(item)).size[0]; r = s["rect"]; wpx, hpx = (r[2] - r[0]) * S, (r[3] - r[1]) * S
    vr = np.asarray(s.get("vrows") or np.linspace(0, 1, NV + 1), np.float32)
    du = np.linalg.norm(P[:, 1:] - P[:, :-1], axis=2)            # segment lengths along u, per row
    dv = np.linalg.norm(P[1:] - P[:-1], axis=2)                   # along v, per column, per band
    if mask is not None:
        mu = mask[:, 1:] & mask[:, :-1]; mv = mask[1:] & mask[:-1]
        du = np.where(mu, du, np.nan); dv = np.where(mv, dv, np.nan)
    rowlen = np.nansum(du, 1) * (NU / np.maximum(1, np.sum(~np.isnan(du), 1)))   # full-row length scaled from the masked part
    bandlen = np.nanmean(dv, 1)                                                    # mean column segment per band
    bandpx = (vr[1:] - vr[:-1]) * hpx
    ok_r = rowlen > 1e-3; ok_b = bandlen > 1e-3
    ud = wpx / rowlen[ok_r]; vd = bandpx[ok_b] / bandlen[ok_b]
    ub = 0.5 * (wpx / np.maximum(rowlen[:-1], 1e-3) + wpx / np.maximum(rowlen[1:], 1e-3))[ok_b]   # u density per band, for the ratio
    ratios = ub / vd
    return S, ud.mean(), ud.min(), vd.mean(), vd.min(), ud.mean() / vd.mean(), ratios.min(), ratios.max()
FAIL = []
print("item/region            tex   u px/stud mean/min   v px/stud mean/min   u/v mean (band min..max)")
for item, regs in META.items():
    for key, s in regs.items():
        if not isinstance(s, dict) or "pos" not in s: continue
        if not os.path.exists(tex_path(item)): print(f"{item + '/' + key:22s} (no tex_{item}.png: skipped)"); continue
        if len(s["pos"]) < 2 or len(s["pos"][0]) < 2: continue
        S, um, umin, vm, vmin, rt, rmin, rmax = dens(item, key, s)
        flag = "" if 0.8 <= rt <= 1.25 else "   <-- ANISOTROPIC"
        if flag: FAIL.append(f"{item}/{key} u/v {rt:.2f}")
        print(f"{item + '/' + key:22s} {S:5d}   {um:6.0f} / {umin:5.0f}       {vm:6.0f} / {vmin:5.0f}      {rt:5.2f} ({rmin:.2f}..{rmax:.2f}){flag}")
import sys
if FAIL: print("FAIL: texel density not isotropic (u/v outside 0.8..1.25):", "; ".join(FAIL)); sys.exit(1)
print("OK: every painted region is isotropic (u/v within 0.8..1.25)")

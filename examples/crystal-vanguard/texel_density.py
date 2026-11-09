#!/usr/bin/env python3
"""Texels per stud for every painted sheet region (from out/meta.json + the texture size): u and v separately, mean and worst row/col,
plus the pauldron shell's front face (positions y < -0.5) alone. Usage: python3 texel_density.py  (after build_cv + paint_cv)."""
import json, os, numpy as np
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); META = json.load(open(os.path.join(OUT, "meta.json")))
def dens(item, key, s, mask=None):
    P = np.asarray(s["pos"], np.float32); NV, NU = P.shape[0] - 1, P.shape[1] - 1
    S = Image.open(os.path.join(OUT, f"tex_{item}.png")).size[0]; r = s["rect"]; wpx, hpx = (r[2] - r[0]) * S, (r[3] - r[1]) * S
    du = np.linalg.norm(P[:, 1:] - P[:, :-1], axis=2)            # segment lengths along u, per row
    dv = np.linalg.norm(P[1:] - P[:-1], axis=2)                   # along v, per column
    if mask is not None:
        mu = mask[:, 1:] & mask[:, :-1]; mv = mask[1:] & mask[:-1]
        du = np.where(mu, du, np.nan); dv = np.where(mv, dv, np.nan)
    rowlen = np.nansum(du, 1) * (NU / np.maximum(1, np.sum(~np.isnan(du), 1)))   # full-row length scaled from the masked part
    collen = np.nansum(dv, 0) * (NV / np.maximum(1, np.sum(~np.isnan(dv), 0)))
    rowlen = rowlen[rowlen > 1e-3]; collen = collen[collen > 1e-3]
    ud = wpx / rowlen; vd = hpx / collen
    return S, ud.mean(), ud.min(), vd.mean(), vd.min()
print("item/region            tex   u px/stud mean/min   v px/stud mean/min")
for item, regs in META.items():
    for key, s in regs.items():
        if not isinstance(s, dict) or "pos" not in s: continue
        S, um, umin, vm, vmin = dens(item, key, s)
        print(f"{item + '/' + key:22s} {S:5d}   {um:6.0f} / {umin:5.0f}       {vm:6.0f} / {vmin:5.0f}")
        if item == "cv_pauldron_r":
            P = np.asarray(s["pos"], np.float32)
            for name, m in (("front face (y<-0.5)", P[..., 1] < -0.5), ("outer face (x<-0.6)", P[..., 0] < -0.6)):
                if m.sum() > 4:
                    S, um, umin, vm, vmin = dens(item, key, s, m)
                    print(f"   {key + ' ' + name:19s} {S:5d}   {um:6.0f} / {umin:5.0f}       {vm:6.0f} / {vmin:5.0f}")

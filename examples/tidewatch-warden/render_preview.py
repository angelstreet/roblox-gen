#!/usr/bin/env python3
"""Software preview: block R15-proportioned avatar + classic shirt/pants textures + hood mesh.
NOT a Roblox render - a quick local check of UV mapping and colour cohesion."""
import os, sys, math, pickle
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
SHIRT = np.array(Image.open(os.path.join(OUT, "tidewatch_shirt.png")).convert("RGBA"))
PANTS = np.array(Image.open(os.path.join(OUT, "tidewatch_pants.png")).convert("RGBA"))
SKIN = np.array([150, 112, 86]); SKINARM = np.array([150, 112, 86]); BASE_CLOTH = np.array([60, 60, 66])
HOOD = pickle.load(open(os.path.join(OUT, "_hood_tris.pkl"), "rb"))
PAL = {"navy": (30, 46, 82), "navy_dark": (10, 16, 32), "bronze": (196, 142, 74), "aqua": (70, 220, 220), "pearl": (232, 238, 240),
       "inner": (14, 20, 38), "bronze_dark": (140, 94, 48), "aqua_dark": (30, 150, 170)}

# part: (centre, size, shirt prefix, pants prefix)
R = {"t": (231, 8), }  # unused
SHIRT_R = {"t_up": (231, 8, 128, 64), "t_front": (231, 74, 128, 128), "t_back": (427, 74, 128, 128), "t_right": (165, 74, 64, 128),
           "t_left": (361, 74, 64, 128), "t_down": (231, 204, 128, 64)}
ARM_R = {"up": (217, 289, 64, 64), "front": (217, 355, 64, 128), "back": (85, 355, 64, 128), "right": (151, 355, 64, 128),
         "left": (19, 355, 64, 128), "down": (217, 485, 64, 64)}
LARM_R = {"up": (308, 289, 64, 64), "front": (308, 355, 64, 128), "back": (440, 355, 64, 128), "right": (506, 355, 64, 128),
          "left": (374, 355, 64, 128), "down": (308, 485, 64, 64)}
TORSO_R = {k[2:]: v for k, v in SHIRT_R.items()}


def box_faces(c, s):
    """returns dict face -> (origin, u_axis_vec, v_axis_vec, normal) ; u,v cover full face (vectors incl. length)."""
    cx, cy, cz = c; w, h, d = s
    x0, x1, y0, y1, z0, z1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, cz - d / 2, cz + d / 2
    # character faces +z; char's right = -x
    return {
        "front": (np.array([x0, y1, z1]), np.array([w, 0, 0]), np.array([0, -h, 0]), (0, 0, 1)),
        "back": (np.array([x1, y1, z0]), np.array([-w, 0, 0]), np.array([0, -h, 0]), (0, 0, -1)),
        "right": (np.array([x0, y1, z0]), np.array([0, 0, d]), np.array([0, -h, 0]), (-1, 0, 0)),
        "left": (np.array([x1, y1, z1]), np.array([0, 0, -d]), np.array([0, -h, 0]), (1, 0, 0)),
        "up": (np.array([x0, y1, z0]), np.array([w, 0, 0]), np.array([0, 0, d]), (0, 1, 0)),
        "down": (np.array([x0, y0, z1]), np.array([w, 0, 0]), np.array([0, 0, -d]), (0, -1, 0)),
    }


def sample(tex, rect, u, v, extra=None):
    x, y, w, h = rect
    px = np.clip((x + u * w).astype(int), 0, tex.shape[1] - 1); py = np.clip((y + v * h).astype(int), 0, tex.shape[0] - 1)
    return tex[py, px]


PARTS = [  # name, centre, size, base colour, overlays [(tex, rects)]
    ("torso", (0, 0, 0), (2.0, 2.0, 1.0), BASE_CLOTH, [(SHIRT, TORSO_R, 0), (PANTS, TORSO_R, 1)]),
    ("rarm", (-1.5, 0, 0), (1.0, 2.0, 1.0), SKINARM, [(SHIRT, ARM_R, 0)]),
    ("larm", (1.5, 0, 0), (1.0, 2.0, 1.0), SKINARM, [(SHIRT, LARM_R, 0)]),
    ("rleg", (-0.5, -2.0, 0), (1.0, 2.0, 1.0), BASE_CLOTH, [(PANTS, ARM_R, 0)]),
    ("lleg", (0.5, -2.0, 0), (1.0, 2.0, 1.0), BASE_CLOTH, [(PANTS, LARM_R, 0)]),
    ("head", (0, 1.6, 0), (1.2, 1.2, 1.2), SKIN, []),
]
# torso: pants texture covers lower torso only (top 20 px) - give pants priority only on belt rows by blending; shirt on top.
# arms/torso: R15 shirt overlays pants on torso, so order pants then shirt.
PARTS[0] = ("torso", (0, 0, 0), (2.0, 2.0, 1.0), BASE_CLOTH, [(PANTS, TORSO_R, 1), (SHIRT, TORSO_R, 0)])

LIGHT = np.array([0.35, 0.65, 0.75]); LIGHT /= np.linalg.norm(LIGHT)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def render(yaw, size=640, scale=95, hood=True, pitch=0.12):
    img = np.zeros((size, size, 4), float); zb = np.full((size, size), -1e9)
    Rm = rot_y(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    M = Rx @ Rm
    cx0, cy0 = size / 2, size * 0.54

    def project(P):
        Q = P @ M.T
        return Q[..., 0] * scale + cx0, -Q[..., 1] * scale + cy0 + 0, Q[..., 2]

    for name, c, s, base, overlays in PARTS:
        c = np.array(c, float)
        for fname, (o, uax, vax, n) in box_faces(c, s).items():
            N = np.array(n, float)
            nr = M @ N
            if nr[2] <= -0.0001: continue
            shade = 0.45 + 0.55 * max(0, float(nr @ LIGHT))
            res = 220
            uu, vv = np.meshgrid(np.linspace(0, 1, res), np.linspace(0, 1, res))
            P = o + uu[..., None] * uax + vv[..., None] * vax
            col = np.zeros((res, res, 4)); col[..., :3] = base; col[..., 3] = 255
            for tex, rects, _k in overlays:
                key = fname if rects is not TORSO_R or True else fname
                rect = rects[key] if key in rects else None
                if rect is None: continue
                t = sample(tex, rect, uu, vv)
                a = t[..., 3:4] / 255.0
                col[..., :3] = col[..., :3] * (1 - a) + t[..., :3] * a
            X, Y, Z = project(P)
            xi = X.astype(int); yi = Y.astype(int)
            ok = (xi >= 0) & (xi < size) & (yi >= 0) & (yi < size)
            for k in range(2):  # splat 2x2 to avoid holes
                for l in range(2):
                    xs = np.clip(xi + k, 0, size - 1)[ok]; ys = np.clip(yi + l, 0, size - 1)[ok]; zs = Z[ok]
                    cs = col[..., :3][ok] * shade
                    order = np.argsort(zs)
                    xs, ys, zs, cs = xs[order], ys[order], zs[order], cs[order]
                    m = zs > zb[ys, xs]
                    zb[ys[m], xs[m]] = zs[m]; img[ys[m], xs[m], :3] = cs[m]; img[ys[m], xs[m], 3] = 255
    if hood:
        head_c = np.array([0, 1.6, 0])
        buf = Image.new("RGB", (size, size));
        for a, b, c_, mat in HOOD:
            P = np.array([a, b, c_]) + head_c
            Q = P @ M.T
            nrm = np.cross(Q[1] - Q[0], Q[2] - Q[0]); ln = np.linalg.norm(nrm)
            if ln < 1e-9: continue
            nrm /= ln
            # inside faces share mat 'inner' and are viewed from interior: draw both sides, shade abs
            shade = 0.5 + 0.5 * abs(float(nrm @ (M @ LIGHT / 1)))
            if nrm[2] < 0: nrm = -nrm; shade *= 0.8
            colr = np.array(PAL[mat]) * (0.55 + 0.45 * max(0, float(nrm @ LIGHT)))
            X = Q[:, 0] * scale + cx0; Y = -Q[:, 1] * scale + cy0; Z = Q[:, 2]
            minx, maxx = int(max(0, math.floor(X.min()))), int(min(size - 1, math.ceil(X.max())))
            miny, maxy = int(max(0, math.floor(Y.min()))), int(min(size - 1, math.ceil(Y.max())))
            if minx > maxx or miny > maxy: continue
            gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            den = (Y[1] - Y[2]) * (X[0] - X[2]) + (X[2] - X[1]) * (Y[0] - Y[2])
            if abs(den) < 1e-9: continue
            l1 = ((Y[1] - Y[2]) * (gx - X[2]) + (X[2] - X[1]) * (gy - Y[2])) / den
            l2 = ((Y[2] - Y[0]) * (gx - X[2]) + (X[0] - X[2]) * (gy - Y[2])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
            z = l1 * Z[0] + l2 * Z[1] + l3 * Z[2]
            sub = zb[miny:maxy + 1, minx:maxx + 1]
            m = inside & (z > sub + 0.002)
            sub[m] = z[m]
            img[miny:maxy + 1, minx:maxx + 1][m, :3] = colr
            img[miny:maxy + 1, minx:maxx + 1][m, 3] = 255
    out = Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGBA")
    return out


def sheet():
    views = [("FRONT", 0), ("SIDE (right)", -math.pi / 2), ("BACK", math.pi), ("3/4", math.radians(35))]
    W = 640; bg = (44, 46, 52)
    sheet = Image.new("RGB", (W * len(views), W + 40), bg)
    d = ImageDraw.Draw(sheet)
    for i, (nm, yaw) in enumerate(views):
        im = render(yaw)
        sheet.paste(im, (i * W, 0), im)
        d.text((i * W + 20, W + 10), nm, fill=(220, 220, 220))
    sheet.save(os.path.join(OUT, "preview_sheet.png"))
    r = render(math.radians(25)); bg2 = Image.new("RGB", r.size, bg); bg2.paste(r, (0, 0), r); bg2.save(os.path.join(OUT, "preview_hero.png"))


if __name__ == "__main__":
    sheet(); print("ok")

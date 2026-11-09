#!/usr/bin/env python3
"""Tidecrest Hood - procedural Roblox accessory (OBJ + palette texture).
No Blender required. Same script logic can be pasted into Blender's scripting tab later.
Frame: +y up, character faces +z, units = studs, origin = head centre.
Exports with origin at HatAttachment (top of head, y = +0.6 above head centre).
"""
import os, sys, math
import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

PALETTE = {  # name -> rgb ; texture is an 4x2 grid of flat colour cells
    "navy": (30, 46, 82), "navy_dark": (10, 16, 32), "bronze": (196, 142, 74), "aqua": (70, 220, 220),
    "pearl": (232, 238, 240), "inner": (14, 20, 38), "bronze_dark": (140, 94, 48), "aqua_dark": (30, 150, 170),
}
NAMES = list(PALETTE)

tris = []   # (v0,v1,v2, material)  each v = np.array(3)


def add_quad(a, b, c, d, mat):
    tris.append((a, b, c, mat)); tris.append((a, c, d, mat))


def hood_point(theta, phi, rx, ry, rz, cy):
    """theta: around y (0 = front +z), phi: from bottom(-1) to top(+1) mapped to latitude."""
    lat = phi * math.pi / 2
    x = rx * math.cos(lat) * math.sin(theta)
    z = rz * math.cos(lat) * math.cos(theta)
    y = cy + ry * math.sin(lat)
    return np.array([x, y, z])


def build_shell(rx, ry, rz, cy, n_theta=28, n_phi=12, mat="navy", flip=False, open_front=True, lat0=-0.35):
    for i in range(n_theta):
        t0 = 2 * math.pi * i / n_theta; t1 = 2 * math.pi * (i + 1) / n_theta
        tc = (t0 + t1) / 2
        for j in range(n_phi):
            p0 = lat0 + (1 - lat0) * j / n_phi; p1 = lat0 + (1 - lat0) * (j + 1) / n_phi
            pc = (p0 + p1) / 2
            # face opening: front wedge, from chin line up to forehead
            ang = math.atan2(math.sin(tc), math.cos(tc))
            if open_front and abs(ang) < math.radians(52) and -0.2 < pc < 0.55:
                continue
            a = hood_point(t0, p0, rx, ry, rz, cy); b = hood_point(t1, p0, rx, ry, rz, cy)
            c = hood_point(t1, p1, rx, ry, rz, cy); d = hood_point(t0, p1, rx, ry, rz, cy)
            if flip:
                add_quad(a, d, c, b, mat)
            else:
                add_quad(a, b, c, d, mat)


def rim_ring(rx, ry, rz, cy, rx2, ry2, rz2, cy2, n=20, mat="bronze"):
    """Bronze trim along the face opening: connect outer and inner shell edges."""
    edge = []
    for k in range(n + 1):
        # path around opening: left cheek -> up over forehead -> right cheek (in (theta,phi) space)
        s = k / n
        ang = math.radians(52) * (1 - 2 * s) if s < 0 else None
    # cheeks (vertical edges) and forehead arc
    pts_o, pts_i = [], []
    th_edge = math.radians(52)
    for sign in (1, -1):
        for j in range(7):
            ph = -0.2 + 0.75 * j / 6
            pts_o.append((sign, hood_point(sign * th_edge, ph, rx, ry, rz, cy)))
            pts_i.append((sign, hood_point(sign * th_edge, ph, rx2, ry2, rz2, cy2)))
    for sign in (1, -1):
        seg_o = [p for s, p in pts_o if s == sign]; seg_i = [p for s, p in pts_i if s == sign]
        for k in range(len(seg_o) - 1):
            add_quad(seg_o[k], seg_o[k + 1], seg_i[k + 1], seg_i[k], mat)
            add_quad(seg_o[k], seg_i[k], seg_i[k + 1], seg_o[k + 1], mat)
    # forehead arc along phi=0.55
    arc_o = [hood_point(th, 0.55, rx, ry, rz, cy) for th in np.linspace(th_edge, -th_edge, 14)]
    arc_i = [hood_point(th, 0.55, rx2, ry2, rz2, cy2) for th in np.linspace(th_edge, -th_edge, 14)]
    for k in range(len(arc_o) - 1):
        add_quad(arc_o[k], arc_o[k + 1], arc_i[k + 1], arc_i[k], mat)
        add_quad(arc_o[k], arc_i[k], arc_i[k + 1], arc_o[k + 1], mat)


def extrude_poly(poly2d, z0, z1, mat_front, mat_side, xform):
    """Extrude a convex-ish polygon (list of (x,y)) along z, using fan triangulation of front/back."""
    n = len(poly2d)
    cx = sum(p[0] for p in poly2d) / n; cy = sum(p[1] for p in poly2d) / n
    for k in range(n):
        p = poly2d[k]; q = poly2d[(k + 1) % n]
        f = lambda pt, z: xform(np.array([pt[0], pt[1], z]))
        tris.append((f((cx, cy), z1), f(p, z1), f(q, z1), mat_front))
        tris.append((f((cx, cy), z0), f(q, z0), f(p, z0), mat_front))
        add_quad(f(p, z0), f(q, z0), f(q, z1), f(p, z1), mat_side)


def crescent_poly(R=0.42, r=0.34, off=0.16, n=18):
    """Crescent opening upward: outer circle minus offset inner circle (as a ring-strip polygon)."""
    outer = [(R * math.cos(a), R * math.sin(a)) for a in np.linspace(math.radians(200), math.radians(340), n)]
    inner = [(r * math.cos(a), off + r * math.sin(a)) for a in np.linspace(math.radians(340), math.radians(200), n)]
    # crescent tips: where circles intersect is approximated by blending inner tips to outer tips
    return outer + inner


def build():
    # outer & inner shell
    build_shell(1.02, 1.08, 1.04, 0.02, mat="navy")
    build_shell(0.93, 1.0, 0.95, 0.02, mat="inner", flip=True)
    rim_ring(1.02, 1.08, 1.04, 0.02, 0.93, 1.0, 0.95, 0.02)
    # peaked tip of hood (cone) pointing up/back for silhouette
    tip_base = hood_point(math.pi, 0.62, 1.02, 1.08, 1.04, 0.02)
    tip_top = np.array([0.0, 1.55, -0.65])
    ring = [hood_point(th, 0.62, 1.02, 1.08, 1.04, 0.02) for th in np.linspace(0, 2 * math.pi, 13)[:-1]]
    for k in range(len(ring)):
        tris.append((ring[k], ring[(k + 1) % len(ring)], tip_top, "navy"))
    # back drape (cloak tail) - tapered panel hanging behind the head/neck
    top_l = np.array([-0.78, -0.30, -0.86]); top_r = np.array([0.78, -0.30, -0.86])
    bot_l = np.array([-0.55, -1.5, -0.72]); bot_r = np.array([0.55, -1.5, -0.72])
    tip = np.array([0.0, -1.95, -0.68])
    add_quad(top_l, bot_l, bot_r, top_r, "navy")          # outside (faces -z)
    add_quad(top_r, bot_r, bot_l, top_l, "inner")         # inside
    tris.append((bot_l, tip, bot_r, "navy")); tris.append((bot_r, tip, bot_l, "inner"))
    # bronze hem strips
    add_quad(bot_l, tip, tip + np.array([0, 0.08, 0.0]), bot_l + np.array([0.0, 0.08, 0.0]), "bronze")
    add_quad(tip, bot_r, bot_r + np.array([0.0, 0.08, 0.0]), tip + np.array([0, 0.08, 0.0]), "bronze")
    # signature crescent crown on the forehead, aqua glow inset with bronze frame
    def place(p):
        # tilt slightly back, place at forehead front/top
        ang = math.radians(-18)
        y = p[1] * math.cos(ang) - p[2] * math.sin(ang); z = p[1] * math.sin(ang) + p[2] * math.cos(ang)
        return np.array([p[0], y + 0.80, z + 0.60])
    big = crescent_poly(0.46, 0.36, 0.17)
    extrude_poly(big, -0.05, 0.07, "bronze", "bronze_dark", place)
    small = crescent_poly(0.38, 0.30, 0.14)
    extrude_poly(small, 0.07, 0.10, "aqua", "aqua_dark", place)
    # glowing gem at the tip of the hood
    gem_c = tip_top + np.array([0, -0.03, 0])
    for sgn in (1, -1):
        top = gem_c + np.array([0, 0.22 * sgn, 0])
        eq = [gem_c + np.array([0.09 * math.cos(a), 0, 0.09 * math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 5)[:-1]]
        for k in range(4):
            if sgn > 0:
                tris.append((eq[k], eq[(k + 1) % 4], top, "aqua"))
            else:
                tris.append((eq[(k + 1) % 4], eq[k], top, "aqua"))


def uv_for(mat):
    k = NAMES.index(mat); col = k % 4; row = k // 4
    u = (col + 0.5) / 4; v = 1 - (row + 0.5) / 2
    return u, v


def export_obj(path, y_off):
    verts, uvs, lines = [], [], []
    vi = {}
    face_lines = []
    for a, b, c, mat in tris:
        idxs = []
        for p in (a, b, c):
            key = (round(float(p[0]), 4), round(float(p[1] - y_off), 4), round(float(p[2]), 4), mat)
            if key not in vi:
                vi[key] = len(verts) + 1
                verts.append(key[:3]); uvs.append(uv_for(mat))
            idxs.append(vi[key])
        face_lines.append(f"f {idxs[0]}/{idxs[0]} {idxs[1]}/{idxs[1]} {idxs[2]}/{idxs[2]}")
    with open(path, "w") as f:
        f.write("# Tidecrest Hood - generated by make_hood.py\nmtllib tidecrest_hood.mtl\nusemtl palette\n")
        for v in verts: f.write("v %.4f %.4f %.4f\n" % v)
        for t in uvs: f.write("vt %.5f %.5f\n" % t)
        f.write("\n".join(face_lines) + "\n")
    with open(os.path.splitext(path)[0] + ".mtl", "w") as f:
        f.write("newmtl palette\nKd 1 1 1\nmap_Kd tidecrest_hood_tex.png\n")
    return len(verts)


def palette_png(path):
    img = Image.new("RGB", (256, 128))
    for k, n in enumerate(NAMES):
        col, row = k % 4, k // 4
        for x in range(col * 64, col * 64 + 64):
            for y in range(row * 64, row * 64 + 64):
                img.putpixel((x, y), PALETTE[n])
    img.save(path)


if __name__ == "__main__":
    build()
    n = export_obj(os.path.join(OUT, "tidecrest_hood.obj"), 0.6)
    palette_png(os.path.join(OUT, "tidecrest_hood_tex.png"))
    import pickle
    pickle.dump([(a.tolist(), b.tolist(), c.tolist(), m) for a, b, c, m in tris], open(os.path.join(OUT, "_hood_tris.pkl"), "wb"))
    print("triangles:", len(tris), "unique verts:", n, "(Roblox limit: 4000 tris for accessories)")

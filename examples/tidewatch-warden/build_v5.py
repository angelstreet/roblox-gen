"""Tidewatch Warden v5 - all accessories rebuilt as clean two-shell sheets with real UV atlases.
Run: Blender -b -P build_v5.py            (then python3 paint_v5.py, then Blender -b -P render_v5.py)
Frame: x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment
(top centre of UpperTorso). Every grid is built row by row so edges (face opening, hems) are grid lines: no boolean
cuts, no decimate, so no jagged or sawtooth edges.
Writes out/v5/v5_build.blend, out/v5/meta.json (fold maps + UV rects for the painter), out/v5/ao_<item>.png.
"""
import bpy, bmesh, math, os, json
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out", "v5"); os.makedirs(OUT, exist_ok=True)
HEAD_C = Vector((0, 0, 0.576))      # measured in Studio: Head centre 0.576 above NeckAttachment
import sys
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from rgen_mesh import Builder, META, SW, sm, spow, SHIRT, FACES, tbox   # shared helpers (lib/rgen_mesh.py)


# ------------------------------------------------------------------ HOOD (HatAttachment)
def build_hood():
    b = Builder("tidecrest_hood_v5")
    E = 2.6; Z_HEM, Z_S, Z_PK = -0.50, 0.30, 1.10; Y_PK = 0.50
    A_MID, A_HEM, BF, BB, YC = 0.80, 0.84, 0.88, 0.78, 0.05
    NU = 36
    # rows: peak -> hem, dense around the arch top of the face opening
    zs = [Z_PK - (Z_PK - 0.62) * (k / 6) ** 1.25 for k in range(6)]
    zs += [0.62 - (0.62 - 0.39) * k / 4 for k in range(4)] + [0.385, 0.37, 0.345, 0.31]
    zs += [0.27 - (0.27 - Z_HEM) * (k / 9) ** 1.1 for k in range(10)]
    NV = len(zs) - 1
    def xo(z):     # face-opening half width at height z (arch, top at z=0.44)
        zt = 0.38
        if z >= zt: return 0.0
        if z > 0.0: return 0.46 * max(0.0, 1 - (z / zt) ** 2.2) ** 0.42
        return 0.46 + 0.10 * sm(-z / 0.6)          # opens a bit wider towards the chin
    def section(z):
        if z > Z_S:
            t = (z - Z_S) / (Z_PK - Z_S); r = max(0.0, 1 - t ** 1.5) ** 0.80
            yc = YC + (Y_PK - YC) * t ** 1.9
        else:
            r = 1.0; yc = YC; t = 0
        lo = sm((Z_S - z) / (Z_S - Z_HEM))
        a = (A_MID + (A_HEM - A_MID) * lo ** 2) * r
        return a, BF * r, BB * r, yc, t
    def point(phi, z):
        a, bf, bb, yc, t = section(z)
        s, c = math.sin(phi), math.cos(phi)
        x = a * spow(s, 2 / E); cy = spow(c, 2 / E)
        y = yc - (bf if cy > 0 else bb) * cy
        return Vector((x, y, z)), yc
    grid, closed, folds = [], [], []
    for j, z in enumerate(zs):
        a, bf, bb, yc, t = section(z)
        w = xo(z); pm = 0.0
        if w > 0 and a > 1e-4:
            pm = math.asin(min(1.0, (min(w, a * 0.98) / a) ** (E / 2)))
        closed.append(pm == 0.0)
        row, frow = [], []
        for i in range(NU + 1):
            phi = pm + (2 * math.pi - 2 * pm) * i / NU
            p, yc = point(phi, z)
            if j == 0: row.append(Vector((0, Y_PK, Z_PK))); frow.append(0.0); continue
            back = sm((-math.cos(phi) + 0.1) / 0.9)
            low = sm((0.35 - z) / 0.9)
            edge = sm(min(phi - pm, 2 * math.pi - pm - phi) / 0.45) if pm > 0 else 1.0
            crown = sm((Z_PK - 0.08 - z) / 0.35)
            d = (0.030 * math.sin(6 * phi + 0.6) * low + 0.022 * math.sin(4 * phi + 1.1) * back * sm((z + 0.1) / 0.5)) * edge * crown
            lip = 0.022 * (1 - sm(min(phi - pm, 2 * math.pi - pm - phi) / 0.12)) if pm > 0 else 0.0
            hem = 0.018 * sm((z - (Z_HEM + 0.08)) / -0.08)
            rad = Vector((p.x, p.y - yc, 0))
            rad = rad.normalized() if rad.length > 1e-6 else Vector((0, 1, 0))
            p = p + rad * (d + lip + hem)
            if pm > 0: p.y -= 0.03 * (1 - sm(min(phi - pm, 2 * math.pi - pm - phi) / 0.2))   # opening edge rolls forward
            row.append(p); frow.append(d / 0.03)
        grid.append(row); folds.append(frow)
    hint = lambda p: Vector((p.x, p.y - 0.1, p.z - 0.2))
    b.sheet(grid, 0.035, (0, 0.36, 1, 1), (0, 0.07, 1, 0.33), rim="bronze", closed_rows=closed, normal_hint=hint,
            fold=folds, key="outer", pole_row0=True)
    META[b.name]["rows"] = [{"z": z, "closed": c, "len": sum((grid[j][i + 1] - grid[j][i]).length for i in range(NU))} for j, (z, c) in enumerate(zip(zs, closed))]
    META[b.name]["phimin"] = [0 if c else 1 for c in closed]
    ob = b.finish(); ob.location = HEAD_C; return ob


# ------------------------------------------------------------------ MANTLE (NeckAttachment)
def build_mantle():
    b = Builder("tide_mantle_v5")
    NU, NV, E = 48, 14, 3.2
    grid, folds = [], []
    for j in range(NV + 1):
        v = j / NV; row, frow = [], []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU          # seam at the back centre
            s, c = math.sin(phi), math.cos(phi)
            a = 0.64 + 0.60 * v; bb = 0.64 + 0.10 * v
            x = a * spow(s, 2 / E); y = -bb * spow(c, 2 / E)
            fb = abs(c) ** (3 if c > 0 else 1.4)           # 1 at front/back centre; broad at the back so it covers the cape top
            z = 0.06 + 0.24 * (1 - sm(v / 0.34))          # cowl collar rises inside the hood, then rests on the shoulders
            if v > 0.62: z -= (0.55 + 0.30 * fb) * sm((v - 0.62) / 0.38) ** 0.8
            z -= 0.12 * fb * sm((v - 0.8) / 0.2) * (1 if c > 0 else 0.6)     # pointed front/back lappet
            d = 0.024 * math.sin(14 * phi + 0.3) * sm((v - 0.55) / 0.45) + 0.012 * math.sin(7 * phi) * sm(v / 0.6)
            rad = Vector((x, y, 0)).normalized()
            p = Vector((x, y, z)) + rad * d
            row.append(p); frow.append(d / 0.03)
        grid.append(row); folds.append(frow)
    hint = lambda p: Vector((p.x, p.y, (p.z + 0.6)))
    b.sheet(grid, 0.035, (0, 0.36, 1, 1), (0, 0.07, 1, 0.33), closed_u=True, normal_hint=hint, fold=folds, key="outer")
    # clasp at the sternum: pearl disc in a bronze ring + aqua gem
    p = grid[int(NV * 0.78)][NU // 2] + Vector((0, -0.04, 0))
    ring = [(0.17 * math.cos(k * math.pi / 8), 0.17 * math.sin(k * math.pi / 8)) for k in range(16)]
    b.extrude(ring, p, Vector((1, 0, 0)), Vector((0, 0, 1)), 0.05, 0.015, "bronze")
    disc = [(0.115 * math.cos(k * math.pi / 8), 0.115 * math.sin(k * math.pi / 8)) for k in range(16)]
    b.extrude(disc, p + Vector((0, -0.03, 0)), Vector((1, 0, 0)), Vector((0, 0, 1)), 0.04, 0.012, "pearl", uv_side="pearl")
    b.gem(p + Vector((0, -0.07, 0)), 0.055, 0.075, Vector((0, -1, 0)))
    return b.finish()


# ------------------------------------------------------------------ CAPE (BodyBackAttachment)
def cape_layer(top_w, bot_w, z0, z1, y0, flare, NU, NV, wave_hem, fold_amp, n_folds, hem_shape):
    grid, folds = [], []
    for j in range(NV + 1):
        v = j / NV; row, frow = [], []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.2)
            z = z0 + (z1 - z0) * v + hem_shape(u) * sm((v - 0.75) / 0.25)
            wrap = 0.22 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2          # wraps around the shoulders at the top
            ph = (u - 0.5) * 2 * math.pi * n_folds * (1 + 0.25 * v) + 0.5
            d = fold_amp * math.sin(ph) * (0.15 + 0.85 * v ** 1.3)
            y = y0 + flare * v ** 1.5 - wrap + d + 0.12 * (2 * (u - 0.5)) ** 2 * v
            row.append(Vector((x, y, z))); frow.append(math.sin(ph) * (0.15 + 0.85 * v ** 1.3))
        grid.append(row); folds.append(frow)
    return grid, folds


def build_cape():
    b = Builder("warden_cape_v5")
    # under-cloak: long, flares; straight hem (double bronze step painted)
    # r4 (2026-11-09): tops tucked under the mantle. Studio showed the panel top (y 0.70 + 0.03 shell) poking through the
    # mantle back (0.72) as a tab; panel now starts at z -0.45 / y 0.64, under-cloak at y 0.58 (torso back face is 0.50).
    gB, fB = cape_layer(1.85, 2.75, -0.22, -4.08, 0.58, 0.76, 22, 24, False, 0.06, 3.0, lambda u: 0.0)
    b.sheet(gB, 0.03, (0, 0.06, 0.5, 1), (0.5, 0.06, 0.75, 0.38), normal_hint=lambda p: Vector((0, 1, 0)), fold=fB, key="under")
    # emblem panel on top: shorter, crisp wave-crest hem (one low point off-centre = our tide motif)
    hem = lambda u: -0.32 * (1 - abs(2 * u - 1) ** 1.6) + 0.06 * math.sin(u * math.pi * 2)
    gA, fA = cape_layer(1.45, 1.95, -0.45, -2.90, 0.64, 0.50, 16, 16, True, 0.025, 1.5, hem)
    b.sheet(gA, 0.03, (0.5, 0.40, 1, 1), (0.75, 0.06, 1, 0.38), normal_hint=lambda p: Vector((0, 1, 0)), fold=fA, key="panel")
    ob = b.finish()
    META[b.name]["panel_dims"] = [1.45, 1.95, 2.48]; META[b.name]["under_dims"] = [1.85, 2.75, 3.64]
    return ob


# ------------------------------------------------------------------ SHOULDERS (Right/LeftShoulderAttachment)
def build_shoulder():
    """authored for the RIGHT shoulder (outward = -x) relative to its attachment (arm top centre).
    Three stacked box-caps (bell shells with boxy superellipse sections): top tier closed dome, lower tiers open on the
    torso side; plus a bronze tide-crest crescent behind the shoulder."""
    b = Builder("tide_pauldron_r_v5"); E = 4.0
    tiers = [  # (z top, z hem outer, half x, half y, closed top, uv v0, v1)
        (0.24, -0.42, 0.64, 0.64, True, 0.70, 1.00),
        (-0.20, -0.74, 0.71, 0.70, False, 0.45, 0.68),
        (-0.50, -1.04, 0.78, 0.76, False, 0.20, 0.43)]
    for k, (zt, zh, hx, hy, top, v0, v1) in enumerate(tiers):
        NU = 28; grid = []
        if top:
            NV = 12
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
                    inner = sm((s + 0.2) / 1.2)                 # s>0 -> +x local = towards the torso for the right shoulder
                    if v < 0.4:                                 # dome: rounded top
                        t = v / 0.4; r = math.sin(t * math.pi / 2); z = zt - 0.16 * (1 - math.cos(t * math.pi / 2))
                    else:
                        t = (v - 0.4) / 0.6; r = 1.0 + 0.05 * t
                        zb = zh + (0.05 - zh) * inner ** 1.5     # inner side stays above the torso top
                        z = (zt - 0.16) + (zb - (zt - 0.16)) * t
                    hx_ = hx * (1 - 0.18 * inner)
                    p = Vector((hx_ * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z))
                    row.append(p if j else Vector((0, 0, zt)))
                grid.append(row)
            b.sheet(grid, 0.06, (0, v0, 0.6, v1), "dark", closed_u=True, pole_row0=True,
                    normal_hint=lambda p: Vector((p.x, p.y, p.z + 0.3)), key=f"lame{k}")
        else:
            NV = 6
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = math.radians(205) + math.radians(310) * i / NU      # skip the torso side (phi ~ 90deg)
                    s, c = math.sin(phi), math.cos(phi)
                    z = zt + (zh - zt) * v - 0.05 * (1 - v) * 0
                    r = 0.80 + 0.20 * math.sin(v * math.pi / 2)
                    p = Vector((hx * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z))
                    row.append(p)
                grid.append(row)
            b.sheet(grid, 0.06, (0, v0, 0.6, v1), "dark", normal_hint=lambda p: Vector((p.x, p.y, 0)), key=f"lame{k}")
    # tide-crest crescent fin behind the shoulder top: quad strip (outer edge, raised ridge, inner edge), no n-gons
    C = Vector((-0.12, 0.30, 0.38)); R, w, A0, A1, N = 0.66, 0.19, -25, 150, 26
    ax_a = Vector((1, 0, 0)); ax_b = Vector((0, -0.22, 0.975)).normalized(); n = ax_a.cross(ax_b).normalized()
    grid = []
    for k in range(N + 1):
        a = math.radians(A0 + (A1 - A0) * k / N); t = k / N
        ww = max(0.012, w * math.sin(math.pi * t) ** 0.7); row = []
        for i, (rr, hh) in enumerate(((R, 0.0), (R - ww * 0.5, 0.035 * math.sin(math.pi * t) ** 0.5), (R - ww, 0.0))):
            dx = -0.06 * math.sin(math.pi * t) * (i / 2)
            row.append(C + ax_a * (-rr * math.cos(a) + dx) + ax_b * (rr * math.sin(a)) + n * hh)
        grid.append(row)
    b.sheet(grid, 0.07, (0.62, 0.20, 1.0, 1.0), (0.62, 0.20, 1.0, 1.0), normal_hint=lambda p, n=n: n)
    META.setdefault(b.name, {})["fin"] = {"rect": (0.62, 0.20, 1.0, 1.0)}
    b.gem(Vector((-0.66, -0.02, -0.05)), 0.07, 0.09, Vector((-1, -0.25, 0.1)))
    return b.finish()


# ------------------------------------------------------------------ BELT + TABARD (WaistFrontAttachment)
def build_belt():
    b = Builder("tidewatch_belt_v5"); NU, E = 40, 4.0
    grid = []
    for j, z in enumerate((-1.56, -1.68, -1.82, -1.94)):
        row = []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
            row.append(Vector((1.07 * spow(s, 2 / E), -0.57 * spow(c, 2 / E), z)))
        grid.append(row)
    b.sheet(grid, 0.04, (0, 0.88, 1, 1), "dark", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)), key="band")
    # tabard blade hanging from the buckle: dark field, bronze border, pearl inner line (painted)
    NU2, NV2 = 6, 16; g2 = []
    for j in range(NV2 + 1):
        v = j / NV2; row = []
        for i in range(NU2 + 1):
            u = i / NU2; half = 0.26 + 0.07 * math.sin(math.pi * min(1, v / 0.8)) - 0.26 * sm((v - 0.8) / 0.2)
            x = (u - 0.5) * 2 * max(half, 0.0)
            z = -1.74 - 1.86 * v - 0.18 * sm((v - 0.8) / 0.2) * (1 - abs(2 * u - 1))
            y = -0.63 - 0.10 * v ** 1.3 - 0.03 * (1 - (2 * u - 1) ** 2)
            row.append(Vector((x, y, z)))
        g2.append(row)
    b.sheet(g2, 0.035, (0, 0.30, 0.3, 0.86), "dark", normal_hint=lambda p: Vector((0, -1, 0)), key="tabard")
    # buckle: wave-crest plate (original shape), bronze with dark inset painted, aqua gem
    bk = [(-0.34, 0.06), (-0.22, 0.22), (0.0, 0.17), (0.22, 0.24), (0.34, 0.06), (0.24, -0.16), (0.0, -0.26), (-0.24, -0.16)]
    b.extrude(bk, Vector((0, -0.66, -1.74)), Vector((1, 0, 0)), Vector((0, 0, 1)), 0.08, 0.025, (0.35, 0.30, 0.95, 0.86), key="buckle")
    b.gem(Vector((0, -0.72, -1.73)), 0.06, 0.08, Vector((0, -1, 0)))
    return b.finish()


# ------------------------------------------------------------------ ROBE SKIRT (WaistCenterAttachment)
def build_skirt():
    b = Builder("tidefall_skirt_v5"); NU, NV, E = 40, 16, 3.0
    grid, folds = [], []
    for j in range(NV + 1):
        v = j / NV; row, frow = [], []
        # r4: open-front tail skirt. Studio walk test: with a 13 deg opening the forward thigh cut through the front panels.
        # Opening half-angle 72..80 deg keeps the panels' front edges at x >= 1.08, outside the legs (outer faces +-1.0),
        # and legs swing only fore/aft. The pants texture already paints the robe legs at the front.
        gap = 1.25 + 0.15 * v ** 1.2                    # front opening half-angle (was 0.22 + 0.30 v^1.2)
        for i in range(NU + 1):
            phi = gap + (2 * math.pi - 2 * gap) * i / NU; s, c = math.sin(phi), math.cos(phi)
            a = 1.10 + 0.42 * v ** 1.3; bb = 0.62 + 0.36 * v ** 1.3
            x = a * spow(s, 2 / E); y = -bb * spow(c, 2 / E) + 0.14 * v ** 1.5 * max(0, -c)
            z = -1.76 - 2.28 * v
            nf = math.sin(9 * phi + 0.4) * sm(v / 0.7) + 0.5 * math.sin(17 * phi) * sm((v - 0.4) / 0.6)
            d = 0.035 * nf * (0.3 + 0.7 * v)
            edge = sm(min(phi - gap, 2 * math.pi - gap - phi) / 0.35)
            rad = Vector((x, y, 0)).normalized(); p = Vector((x, y, z)) + rad * d * edge
            p += rad * 0.05 * sm((v - 0.9) / 0.1)        # hem rolls out (step)
            row.append(p); frow.append(nf * (0.3 + 0.7 * v) * edge)
        grid.append(row); folds.append(frow)
    b.sheet(grid, 0.035, (0, 0.36, 1, 1), (0, 0.07, 1, 0.33), normal_hint=lambda p: Vector((p.x, p.y, 0)), fold=folds, key="outer")
    return b.finish()


# ------------------------------------------------------------------ BODY PROXY (classic shirt/pants on R15 blocks)
def body():
    sh = bpy.data.images.load(os.path.join(OUT, "tidewatch_shirt_v5.png")); pa = bpy.data.images.load(os.path.join(OUT, "tidewatch_pants_v5.png"))
    PANTS = {"t": SHIRT["t"], "rl": SHIRT["ra"], "ll": SHIRT["la"]}
    objs = [tbox("torso", (2, 1, 2.1), (0, 0, -1.05), SHIRT["t"], sh), tbox("armR", (1, 1, 2.1), (-1.5, 0, -1.05), SHIRT["ra"], sh),
            tbox("armL", (1, 1, 2.1), (1.5, 0, -1.05), SHIRT["la"], sh), tbox("legR", (1, 1, 2.19), (-0.5, 0, -3.195), PANTS["rl"], pa),
            tbox("legL", (1, 1, 2.19), (0.5, 0, -3.195), PANTS["ll"], pa)]
    bpy.ops.mesh.primitive_cube_add(size=1); hd = bpy.context.object; hd.name = "head"; hd.scale = (1.16, 1.16, 1.18); hd.location = HEAD_C
    bv = hd.modifiers.new("b", "BEVEL"); bv.width = 0.14; bv.segments = 3
    m = bpy.data.materials.new("skin"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.29, 0.21, 1)
    hd.data.materials.append(m)
    for o in objs + [hd]: o["body"] = True
    return objs + [hd]


def bake_ao(ob, size, others):
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.device = "CPU"
    if sc.world is None: sc.world = bpy.data.worlds.new("bakeworld")
    sc.world.light_settings.distance = 0.45          # local occlusion only: folds, contact, inner hood
    for o in others: o.hide_render = True
    ob.hide_render = False
    img = bpy.data.images.new("ao_" + ob.name, size, size); mat = ob.data.materials[0]; nt = mat.node_tree
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; nt.nodes.active = t
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    sc.render.bake.margin = 6
    bpy.ops.object.bake(type="AO")
    img.filepath_raw = os.path.join(OUT, f"ao_{ob.name}.png"); img.file_format = "PNG"; img.save()
    nt.nodes.remove(t)
    for o in others: o.hide_render = False


def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    items = [build_hood(), build_mantle(), build_cape(), build_shoulder(), build_belt(), build_skirt()]
    cape = bpy.data.objects["warden_cape_v5"]
    # mirrored left pauldron (render + export); built from the right one
    r = bpy.data.objects["tide_pauldron_r_v5"]; l = r.copy(); l.data = r.data.copy(); l.name = "tide_pauldron_l_v5"; bpy.context.collection.objects.link(l)
    l.data.transform(__import__("mathutils").Matrix.Scale(-1, 4, (1, 0, 0))); l.data.flip_normals()
    r.location = (-1.5, 0, 0); l.location = (1.5, 0, 0)
    bodies = body()
    bpy.context.view_layer.update()
    for o in items + [l]:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        dims = [max(v[k] for v in bb) - min(v[k] for v in bb) for k in range(3)]
        nm = sum(1 for e in o.data.edges if False)
        print("ITEM", o.name, "tris", tris(o), "W %.2f D %.2f H %.2f" % tuple(dims))
        META.setdefault(o.name, {})["tris"] = tris(o); META[o.name]["dims"] = dims
    with open(os.path.join(OUT, "meta.json"), "w") as fh: json.dump(META, fh)
    if os.environ.get("NOBAKE") != "1":
        for o in items:
            bake_ao(o, 1024, [x for x in items + [l] if x is not o])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "v5_build.blend"))
    print("DONE")

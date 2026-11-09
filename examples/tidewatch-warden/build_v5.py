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
META = {}
# constant-colour swatches on the bottom strip of every atlas (u-centre, v-centre)
SW = {"bronze": (0.125, 0.025), "pearl": (0.375, 0.025), "aqua": (0.625, 0.025), "dark": (0.875, 0.025)}


def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def spow(x, p): return math.copysign(abs(x) ** p, x)


class Builder:
    """collects geometry for one accessory in a bmesh with one UV layer"""
    def __init__(self, name):
        self.name = name; self.bm = bmesh.new(); self.uv = self.bm.loops.layers.uv.new("UVMap"); self.sheets = []
        self.fl = self.bm.faces.layers.int.new("flat"); self.flat_mode = 0

    def face(self, verts, uvs):
        try: f = self.bm.faces.new(verts)
        except ValueError: return None
        for lp, uv in zip(f.loops, uvs): lp[self.uv].uv = uv
        f[self.fl] = self.flat_mode
        return f

    def sheet(self, grid, thick, r_out, r_in=None, rim="bronze", closed_u=False, closed_rows=None, normal_hint=None,
              fold=None, key=None, rim_skip_cols=False, pole_row0=False):
        """grid[j][i] Vectors (j rows top->bottom, i cols). Outer UV rect r_out=(u0,v0,u1,v1); inner rect or swatch name.
        closed_rows[j]=True: col 0 and col N coincide (welded later). normal_hint(p)->Vector pointing outward."""
        NV, NU = len(grid) - 1, len(grid[0]) - 1
        cr = closed_rows or [False] * (NV + 1)
        nrm = [[None] * (NU + 1) for _ in range(NV + 1)]
        for j in range(NV + 1):
            for i in range(NU + 1):
                if pole_row0 and j == 0:
                    cen = sum((grid[1][k] for k in range(NU + 1)), Vector()) / (NU + 1); nrm[j][i] = (grid[0][i] - cen).normalized(); continue
                if closed_u or cr[j]:
                    il = (i - 1) if i > 0 else NU - 1; ir = (i + 1) if i < NU else 1
                else:
                    il, ir = max(0, i - 1), min(NU, i + 1)
                jd, ju = max(0, j - 1), min(NV, j + 1)
                du = grid[j][ir] - grid[j][il]; dv = grid[ju][i] - grid[jd][i]
                n = du.cross(dv)
                if n.length < 1e-9: n = Vector((0, 0, 1))
                n.normalize()
                if normal_hint is not None and n.dot(normal_hint(grid[j][i])) < 0: n = -n
                nrm[j][i] = n
        outer = [[self.bm.verts.new(grid[j][i]) for i in range(NU + 1)] for j in range(NV + 1)]
        inner = [[self.bm.verts.new(grid[j][i] - nrm[j][i] * thick) for i in range(NU + 1)] for j in range(NV + 1)]
        def uvr(r, i, j): return (r[0] + (r[2] - r[0]) * i / NU, r[3] - (r[3] - r[1]) * j / NV)
        def uvi(i, j): return SW[r_in] if isinstance(r_in, str) else uvr(r_in, i, j)
        rim_uv = SW[rim]
        for j in range(NV):
            for i in range(NU):
                q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                self.face([outer[b][a] for a, b in q], [uvr(r_out, a, b) for a, b in q])
                qi = q[::-1]
                self.face([inner[b][a] for a, b in qi], [uvi(a, b) for a, b in qi])
        segs = []
        if not closed_u:
            for j in range(NV):
                if cr[j] and cr[j + 1]: continue
                segs.append(((0, j), (0, j + 1))); segs.append(((NU, j + 1), (NU, j)))
        for i in range(NU):
            segs.append(((i + 1, NV), (i, NV)))
            if not pole_row0: segs.append(((i, 0), (i + 1, 0)))
        for (a1, b1), (a2, b2) in segs:
            self.face([outer[b1][a1], outer[b2][a2], inner[b2][a2], inner[b1][a1]], [rim_uv] * 4)
        if key:
            def dens(vs):
                out = []
                for a1, a2 in zip(vs[:-1], vs[1:]):
                    for k in range(6): out.append(a1.lerp(a2, k / 6))
                if vs: out.append(vs[-1])
                return out
            bnd = {}
            if not closed_u:
                keep = [j for j in range(NV + 1) if not cr[j] or (j < NV and not cr[j + 1]) or (j > 0 and not cr[j - 1])]
                runs = [[]]
                for j in keep:
                    if runs[-1] and j != runs[-1][-1] + 1: runs.append([])
                    runs[-1].append(j)
                bnd["u0"] = sum((dens([grid[j][0] for j in r]) for r in runs if r), [])
                bnd["u1"] = sum((dens([grid[j][NU] for j in r]) for r in runs if r), [])
            if not pole_row0: bnd["v0"] = dens(list(grid[0]))
            bnd["v1"] = dens(list(grid[NV]))
            dist = {k: [[round(min((grid[j][i] - q).length for q in pts), 4) if pts else 9.0 for i in range(NU + 1)] for j in range(NV + 1)]
                    for k, pts in bnd.items()}
            META.setdefault(self.name, {})[key] = {"rect": r_out, "rect_in": r_in if not isinstance(r_in, str) else None,
                                                   "NU": NU, "NV": NV, "fold": fold, "dist": dist,
                                                   "pos": [[[round(c, 4) for c in grid[j][i]] for i in range(NU + 1)] for j in range(NV + 1)]}
        return outer, inner

    def extrude(self, pts, origin, ax_a, ax_b, thick, chamfer, uv_front, uv_side="bronze", both=True, key=None):
        """2D polygon (CCW in a,b) -> bevelled slab. uv_front: rect (u0,v0,u1,v1) for planar mapping of the polygon bbox, or swatch name."""
        n = ax_a.cross(ax_b).normalized(); N = len(pts)
        A = [p[0] for p in pts]; B = [p[1] for p in pts]; amin, amax, bmin, bmax = min(A), max(A), min(B), max(B)
        def inset(k, d):
            p0, p1, p2 = Vector(pts[k - 1]), Vector(pts[k]), Vector(pts[(k + 1) % N])
            e1 = (p1 - p0).normalized(); e2 = (p2 - p1).normalized()
            n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x)); m = (n1 + n2)
            if m.length < 1e-6: m = n1
            m.normalize(); c = max(0.35, m.dot(n1)); q = p1 + m * (d / c); return (q.x, q.y)
        def P(ab, h): return origin + ax_a * ab[0] + ax_b * ab[1] + n * h
        def puv(ab):
            if isinstance(uv_front, str): return SW[uv_front]
            r = uv_front; return (r[0] + (r[2] - r[0]) * (ab[0] - amin) / (amax - amin + 1e-9), r[1] + (r[3] - r[1]) * (ab[1] - bmin) / (bmax - bmin + 1e-9))
        ins = [inset(k, chamfer) for k in range(N)]; self.flat_mode = 1
        if key: META.setdefault(self.name, {})[key] = {"rect": uv_front, "pts": pts, "bbox": [amin, amax, bmin, bmax]}
        lay = [(pts, -thick / 2), (pts, thick / 2 - chamfer), (ins, thick / 2)]
        if both: lay = [(ins, -thick / 2)] + [(pts, -thick / 2 + chamfer)] + lay[1:]
        rings = [[self.bm.verts.new(P(p, h)) for p in ps] for ps, h in lay]
        uvs = [[puv(p) for p in ps] for ps, h in lay]
        for r in range(len(rings) - 1):
            side = (r == len(rings) - 3) if both else (r == 0)
            for k in range(N):
                k2 = (k + 1) % N
                vs = [rings[r][k], rings[r][k2], rings[r + 1][k2], rings[r + 1][k]]
                self.face(vs, [SW[uv_side]] * 4 if side else [uvs[r][k], uvs[r][k2], uvs[r + 1][k2], uvs[r + 1][k]])
        self.face(rings[-1], uvs[-1]); self.face(rings[0][::-1], uvs[0][::-1]); self.flat_mode = 0

    def gem(self, c, rx, rz, depth_dir, col="aqua"):
        d = depth_dir.normalized(); up = Vector((0, 0, 1)); side = d.cross(up).normalized(); self.flat_mode = 1
        eq = [c + side * rx, c + up * rz, c - side * rx, c - up * rz]
        vs = [self.bm.verts.new(p) for p in eq]; t = self.bm.verts.new(c + d * rx * 0.9); b = self.bm.verts.new(c - d * rx * 0.3)
        for k in range(4):
            self.face([vs[k], vs[(k + 1) % 4], t], [SW[col]] * 3); self.face([vs[(k + 1) % 4], vs[k], b], [SW[col]] * 3)
        self.flat_mode = 0

    def finish(self, weld=True):
        if weld: bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts[:], dist=1e-5)
        bmesh.ops.dissolve_degenerate(self.bm, edges=self.bm.edges[:], dist=1e-6)
        bmesh.ops.triangulate(self.bm, faces=self.bm.faces[:])
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free()
        ob = bpy.data.objects.new(self.name, me); bpy.context.collection.objects.link(ob)
        fa = me.attributes.get("flat")
        for p in me.polygons: p.use_smooth = not (fa and fa.data[p.index].value)
        mat = bpy.data.materials.new("mat_" + self.name); mat.use_nodes = True; me.materials.append(mat)
        return ob


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
    gB, fB = cape_layer(1.85, 2.75, -0.22, -4.08, 0.60, 0.74, 22, 24, False, 0.06, 3.0, lambda u: 0.0)
    b.sheet(gB, 0.03, (0, 0.06, 0.5, 1), (0.5, 0.06, 0.75, 0.38), normal_hint=lambda p: Vector((0, 1, 0)), fold=fB, key="under")
    # emblem panel on top: shorter, crisp wave-crest hem (one low point off-centre = our tide motif)
    hem = lambda u: -0.32 * (1 - abs(2 * u - 1) ** 1.6) + 0.06 * math.sin(u * math.pi * 2)
    gA, fA = cape_layer(1.45, 1.95, -0.30, -2.90, 0.70, 0.44, 16, 16, True, 0.025, 1.5, hem)
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
        gap = 0.22 + 0.30 * v ** 1.2                    # front opening half-angle
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
SHIRT = {"t": {"up": (231, 8, 128, 64), "front": (231, 74, 128, 128), "back": (427, 74, 128, 128), "right": (165, 74, 64, 128), "left": (361, 74, 64, 128), "down": (231, 204, 128, 64)},
         "ra": {"up": (217, 289, 64, 64), "front": (217, 355, 64, 128), "back": (85, 355, 64, 128), "right": (151, 355, 64, 128), "left": (19, 355, 64, 128), "down": (217, 485, 64, 64)},
         "la": {"up": (308, 289, 64, 64), "front": (308, 355, 64, 128), "back": (440, 355, 64, 128), "right": (506, 355, 64, 128), "left": (374, 355, 64, 128), "down": (308, 485, 64, 64)}}
FACES = {"front": (Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))), "back": (Vector((0, 1, 0)), Vector((-1, 0, 0)), Vector((0, 0, 1))),
         "right": (Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))), "left": (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
         "up": (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))), "down": (Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, -1, 0)))}


def tbox(name, size, centre, rects, img):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); h = Vector(size) / 2; c = Vector(centre)
    for fn, (n, U, V) in FACES.items():
        hn = abs(n.dot(h)); hu = abs(U.dot(h)); hv = abs(V.dot(h)); x, y, w, hh = rects[fn]
        corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        vs = [bm.verts.new(c + n * hn + U * hu * s + V * hv * t) for s, t in corners]
        f = bm.faces.new(vs)
        for lp, (s, t) in zip(f.loops, corners):
            ss, tt = (s + 1) / 2, (t + 1) / 2; lp[uvl].uv = ((x + ss * w) / 585, 1 - (y + (1 - tt) * hh) / 559)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    m = bpy.data.materials.new("m_" + name); m.use_nodes = True; nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Linear"
    bs = nt.nodes["Principled BSDF"]; nt.links.new(t.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.75
    me.materials.append(m); return ob


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

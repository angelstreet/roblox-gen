"""Shared Blender mesh helpers for roblox-gen sets (extracted 2026-11-09 from tidewatch-warden/build_v5.py, unchanged).
Builder: one accessory as a bmesh with one UV layer (sheet = two-shell parametric cloth grid with rims, extrude, gem, finish).
SW: swatch name -> (u, v) on the bottom strip of every atlas; META: per-item data written to meta.json for the painters.
Both are module-level dicts shared by reference: a set may clear/extend SW (crystal-vanguard does) before building.
tbox/SHIRT/FACES: textured R15 block proxy for renders (official 585x559 template rects).
Import from a set folder:  sys.path.insert(0, os.path.join(HERE, "..", "..", "lib")); import rgen_mesh as B
Frame: x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment."""
import bpy, bmesh, math
from mathutils import Vector

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

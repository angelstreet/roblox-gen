"""Ember Warden - accessories built in Blender: horned flame helm (Hair), two rock-slab pauldrons, tattered cape (Back),
spiked obsidian collar (Neck), molten battle-axe (Waist). Run: Blender -b -P build_ew.py (after make_clothing_ew.py + make_face_ew.py).
Frame (same as the other sets): x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment.
Writes out/ew_build.blend, out/meta.json (UV regions, positions, edge distances for paint_ew.py) and Cycles AO bakes.
Every non-weapon atlas has an 8-swatch strip at the bottom (v 0..0.06) painted by paint_ew.py."""
import bpy, bmesh, math, os, random, sys, json, time
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
import rgen_mesh as B                     # shared Builder / swatches / body proxy (lib/rgen_mesh.py)
from rgen_mesh import Builder, sm, spow

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
HC = 0.576
CELLS = ["gold", "ember", "molten", "obsidian", "ash", "red", "hot", "gold_dark"]
B.SW.clear()
for k, n in enumerate(CELLS): B.SW[n] = ((k + 0.5) / 8, 0.03)
B.SW.update({"bronze": B.SW["gold"], "pearl": B.SW["ash"], "aqua": B.SW["ember"], "dark": B.SW["obsidian"]})
def cell(n):
    u = B.SW[n][0]; return (u - 0.05, 0.012, u + 0.05, 0.048)
def V(*a): return Vector(a[0] if len(a) == 1 else a)


def iso_rect(grid, u0, u1, v1, S, min_frac=0.5, v_scale=1.0):
    """UV rect + per-row v positions giving the SAME texel density along u and v (Studio has no anisotropic filtering).
    (copied from crystal-vanguard/build_cv.py: this helper is not in lib/)"""
    NV, NU = len(grid) - 1, len(grid[0]) - 1
    rowlen = [sum((grid[j][i + 1] - grid[j][i]).length for i in range(NU)) for j in range(NV + 1)]
    mx = max(rowlen); eff = [max(l, min_frac * mx) for l in rowlen]; wpx = (u1 - u0) * S; bands = []
    for j in range(NV):
        col = sum((grid[j + 1][i] - grid[j][i]).length for i in range(NU + 1)) / (NU + 1)
        bands.append(col * wpx / ((eff[j] + eff[j + 1]) / 2))
    tot = sum(bands) * v_scale; cum = [0.0]
    for h in bands: cum.append(cum[-1] + h * v_scale / tot)
    return (u0, v1 - tot / S, u1, v1), cum, tot / S


class Atlas:
    """hands out UV rects top-down: take(grid, u0, u1) -> (rect, v_rows); rects may share a row when given the same vtop"""
    def __init__(self, S, floor=0.07): self.S = S; self.v = 1.0; self.floor = floor
    def take(self, grid, u0, u1, vtop=None, advance=True, **kw):
        vt = self.v if vtop is None else vtop
        rect, vr, h = iso_rect(grid, u0, u1, vt, self.S, **kw)
        if advance: self.v = rect[1] - 0.006
        assert rect[1] > self.floor, f"atlas overflow: rect {rect}"
        return rect, vr
    def fixed(self, u0, u1, h, vtop=None, advance=True):
        vt = self.v if vtop is None else vtop; r = (u0, vt - h, u1, vt)
        if advance: self.v = r[1] - 0.006
        assert r[1] > self.floor, f"atlas overflow: rect {r}"
        return r


def tex_material(me, name):
    mat = bpy.data.materials.new("mat_" + name); mat.use_nodes = True; me.materials.append(mat)


def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def strand(b, path, w0, rect, flat=1.0, sides=5, shade=False, clamp=None, taper=1.0, base_cap=True, rad0=None):
    """closed tapered spike/horn/flame along a polyline: ONE frame per strand, cap at the base, sharp tip. UV rect: u around, v root->tip.
    shade=True: flat-shaded facets (crystal / rock look). Optional clamp(p)->p keeps every vertex inside a Marketplace box."""
    path = [clamp(p) if clamp else p for p in path]; n = len(path) - 1
    if rad0 is None: rad0 = V((0, 0, 1))
    rings, vuv = [], []
    for k, c in enumerate(path[:-1]):
        d = (path[k + 1] - c).normalized() if k == 0 else (path[k + 1] - path[k - 1]).normalized()
        side = d.cross(rad0)
        if side.length < 1e-4: side = d.cross(V((0, 1, 0)))
        side.normalize(); s2 = side.cross(d).normalized()
        w = w0 * (1 - k / n) ** taper
        rings.append([b.bm.verts.new(clamp(c + (side * math.cos(2 * math.pi * q / sides) * flat + s2 * math.sin(2 * math.pi * q / sides)) * w) if clamp else
                                     c + (side * math.cos(2 * math.pi * q / sides) * flat + s2 * math.sin(2 * math.pi * q / sides)) * w) for q in range(sides)])
        vuv.append(rect[1] + (rect[3] - rect[1]) * k / n)
    tip = b.bm.verts.new(path[-1]); uvt = (rect[0] + (rect[2] - rect[0]) * 0.5, rect[3])
    def uvq(q, k): return (rect[0] + (rect[2] - rect[0]) * (q / sides), vuv[k])
    b.flat_mode = 1 if shade else 0
    if base_cap: b.face(rings[0][::-1], [uvq(q, 0) for q in range(sides)][::-1])
    for k, (r0, r1) in enumerate(zip(rings[:-1], rings[1:])):
        for q in range(sides):
            q2 = (q + 1) % sides; b.face([r0[q], r0[q2], r1[q2], r1[q]], [uvq(q, k), uvq(q + 1, k), uvq(q + 1, k + 1), uvq(q, k + 1)])
    for q in range(sides): b.face([rings[-1][q], rings[-1][(q + 1) % sides], tip], [uvq(q, n - 1), uvq(q + 1, n - 1), uvt])
    b.flat_mode = 0


def bez(p0, p1, p2, n=6): return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (k / n for k in range(n + 1))]
def bez3(p0, p1, p2, p3, n=8): return [p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3 for t in (k / n for k in range(n + 1))]


def register_rect(name, key, rect):
    B.META.setdefault(name, {})[key] = {"rect_only": rect}


# ------------------------------------------------------------------ HELM + FLAME HAIR (Hair type, HatAttachment frame)
def build_helm():
    """open-face obsidian war-helm: faceted dome with a gold-rolled hem, serrated glowing crest fin, two swept horns, flame-lick hair
    (rising plume + hanging locks, glowing root->tip), brow gem. Dome/fin/band carry real UV regions (meta.json) for physical painting."""
    b = Builder("ew_helm"); rnd = random.Random(5); at = Atlas(1024)
    HAIR = (0.0, 0.84, 0.20, 1.0); HORN = (0.22, 0.84, 0.50, 1.0); SPIKE = (0.52, 0.84, 0.66, 1.0)
    for k, r in (("hair", HAIR), ("horn", HORN), ("spike", SPIKE)): register_rect("ew_helm", k, r)
    at.v = 0.83
    NU, NV, E, R, RZ = 20, 6, 4.5, 0.75, 0.80
    def hemz(phi):
        c = math.cos(phi); s = abs(math.sin(phi)); return 0.44 * max(0, c) ** 0.9 - 0.44 * max(0, -c) + 0.06 * s ** 1.5
    def th_end(phi): return math.acos(max(-0.97, min(0.97, spow(hemz(phi) / RZ, E / 2))))
    def dome_pt(phi, th, r=R):
        return V((r * spow(math.sin(th), 2 / E) * spow(math.sin(phi), 2 / E), -r * spow(math.sin(th), 2 / E) * spow(math.cos(phi), 2 / E), HC + RZ * spow(math.cos(th), 2 / E)))
    grid = []
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            phi = 2 * math.pi * i / NU; rib = 1 + 0.035 * (i % 2) * sm(v * 2) * (1 if i < NU else 0)
            row.append(dome_pt(phi, th_end(phi) * v, R * rib) if j else V((0, 0, HC + RZ)))
        grid.append(row)
    rect, vr = at.take(grid, 0.0, 1.0)
    b.flat_mode = 1
    b.sheet(grid, 0.045, rect, "obsidian", rim="gold", closed_u=True, pole_row0=True, normal_hint=lambda p: V((p.x, p.y, p.z - HC)), key="dome", v_rows=vr)
    b.flat_mode = 0
    # gold rolled hem band following the dome hem all round (rows are offsets in z from the hem: th is very sensitive to z near the equator)
    g = []
    for dz, dr in ((0.07, 0.0), (0.03, 0.025), (-0.01, 0.03), (-0.05, 0.0)):
        row = []
        for i in range(NU * 2 + 1):
            phi = 2 * math.pi * i / (NU * 2); zz = hemz(phi) + dz
            th = math.acos(max(-0.97, min(0.97, spow(zz / RZ, E / 2)))); row.append(dome_pt(phi, th, R + dr + 0.012))
        g.append(row)
    b.sheet(g, 0.028, cell("gold"), "gold_dark", rim="gold_dark", closed_u=True, normal_hint=lambda p: V((p.x, p.y, 0)))
    # serrated crest fin over the top, front -> back, glowing edge
    NF = 28; fg = []
    def fin_pt(t):
        phi = 0.0 if t < 0.5 else math.pi; th = th_end(phi) * abs(1 - 2 * t) if t < 0.5 else th_end(phi) * (2 * t - 1)
        p = dome_pt(phi, th, R * 0.995); n = V((0, p.y, p.z - HC)).normalized(); return p, n
    CLf = lambda p: V((p.x, min(1.12, p.y), min(HC + 1.80, p.z)))
    top, mid, base = [], [], []
    for i in range(NF + 1):
        t = i / NF; p, n = fin_pt(t); fr = (t * 6) % 1.0; tooth = 0.25 * fr ** 1.4 * (0.6 + 0.4 * math.sin(math.pi * t))
        h = 0.08 + 0.36 * math.sin(math.pi * t) ** 0.7 + 0.7 * tooth
        top.append(CLf(p + n * h + V((0, 0.45 * tooth, 0)))); mid.append(p + n * (h * 0.5) + V((0, 0.15 * tooth, 0))); base.append(p - n * 0.02)
    fg = [top, mid, base]
    rect_f, vr_f = at.take(fg, 0.0, 0.5, advance=False)
    b.flat_mode = 1
    b.sheet(fg, 0.07, rect_f, (0.5, rect_f[1], 1.0, rect_f[3]), rim="obsidian", normal_hint=lambda p: V((1, 0, 0)), key="fin", v_rows=vr_f)
    b.flat_mode = 0
    at.v = rect_f[1] - 0.006
    # brow: gold-framed ember gem + 4 small obsidian flame points on the band
    b.extrude([(0, 0.24), (0.17, 0.0), (0, -0.20), (-0.17, 0.0)], V((0, -0.745, HC + 0.38)), V((1, 0, 0)), V((0, 0, 1)), 0.05, 0.015, "gold")
    b.gem(V((0, -0.775, HC + 0.38)), 0.10, 0.17, V((0, -1, 0)), "ember")
    for ang in (30, -30, 58, -58):
        a = math.radians(ang); base_p = dome_pt(a % (2 * math.pi), th_end(a % (2 * math.pi)) * 0.82, R + 0.01); out = V((math.sin(a), -math.cos(a), 0))
        strand(b, bez(base_p - out * 0.03, base_p + out * 0.06 + V((0, 0.03, 0.22)), base_p + out * 0.10 + V((0, 0.14, 0.46)), 4), 0.075, SPIKE, flat=1.4, sides=4, shade=True)
    CLs = lambda p: V((max(-0.88, min(0.88, p.x)), max(-0.92, min(1.17, p.y)), max(HC - 1.2, min(HC + 1.85, p.z))))
    # swept horns from the temples (ridged, flat shaded)
    for sg in (-1, 1):
        p0 = V((sg * 0.80, -0.02, HC + 0.30)); p1 = V((sg * 0.97, 0.10, HC + 0.52)); p2 = V((sg * 0.90, 0.55, HC + 1.02)); p3 = V((sg * 0.58, 0.98, HC + 1.50))
        strand(b, bez3(p0 - V((sg * 0.04, 0, 0)), p1, p2, p3, 10), 0.19, HORN, flat=1.0, sides=6, shade=True, clamp=CLs, taper=0.9)
    # flame hair: rising plume from the back of the crown + hanging locks over the nape, wavy flat blades
    def flame(base_p, dirv, L, amp, freq, sidev, flick, w0, rect=HAIR, n=8, sides=5):
        pts = []
        for k in range(n + 1):
            t = k / n; pts.append(base_p + dirv * L * t + sidev * amp * math.sin(2 * math.pi * freq * t + 0.6) * t + flick * t ** 2)
        strand(b, pts, w0, rect, flat=1.9, sides=sides, clamp=CLs, taper=1.0, rad0=V((0, 1, 0)) if abs(dirv.z) > 0.6 else V((0, 0, 1)))
    for k in range(7):                                                       # rising plume: fan of fire tongues swept up and back
        ang = (k - 3) * 0.36; phi = math.pi + ang * 0.7; base_p = dome_pt(phi, 0.55 + 0.05 * abs(k - 3), R * 1.04)
        dirv = V((math.sin(ang) * 0.85, 0.50 * math.cos(ang), 0.80)).normalized(); L = 1.25 - 0.17 * abs(k - 3) + (0.06 if k % 2 else 0.0)
        flame(base_p, dirv, L, 0.18, 1.5, V((math.cos(ang), -math.sin(ang) * 0.3, 0)), V((math.sin(ang) * 0.30, 0.55, -0.10)), 0.085, n=10)
    for k in range(7):                                                       # hanging locks over the nape (separate flame tongues, uneven lengths)
        phi = math.pi + (k - 3) * 0.27 + rnd.uniform(-0.03, 0.03); base_p = dome_pt(phi, th_end(phi) * 0.78, R * 1.04)
        out = V((base_p.x, base_p.y, 0)).normalized(); L = (1.20, 0.80, 1.00, 1.30, 0.90, 0.75, 1.15)[k] * (1 - 0.10 * abs(k - 3) / 3)
        dirv = (out * 0.30 + V((0, 0, -0.95))).normalized()
        flame(base_p, dirv, L, 0.10, 1.2, V((out.y, -out.x, 0)), out * 0.30 + V((0, 0.10, 0.15)), 0.115)
    ob = b.finish(); tex_material(ob.data, "ew_helm"); return ob


# ------------------------------------------------------------------ PAULDRON (Right/LeftShoulderAttachment)
def build_pauldron():
    """stacked obsidian rock slabs (flat-shaded, irregular outline), glowing magma core showing in the gaps, gold-rimmed hems,
    a fan of flat-shaded spikes on the top slab and hem points on the lower slabs. Right shoulder; the left one is the mirror."""
    b = Builder("ew_pauldron_r"); rnd = random.Random(21); at = Atlas(2048, floor=0.125); E = 2.4; NU = 16
    SP = (0.0, 0.065, 0.16, 0.12); register_rect("ew_pauldron_r", "spike", SP)
    jit = [rnd.uniform(-0.035, 0.035) for _ in range(NU)]; jit.append(jit[0])
    def inner_f(s): return sm((s + 0.15) / 1.0)                         # 1 on the torso side (+x local)
    def pt_xy(phi, hx, hy, r=1.0):
        s, c = math.sin(phi), math.cos(phi); inn = inner_f(s); i = int(round(phi / (2 * math.pi) * NU)) % (NU + 1)
        k = (1 + jit[i]) * r; return V((hx * (1 - 0.45 * inn) * k * spow(s, 2 / E), hy * k * spow(c, 2 / E), 0)), inn, s
    def slab(zt, zh, hx, hy, pt, key, closed, A0=0, A1=360, NV=7, thick=0.07, tilt=0.0, yaw=0.0):
        grid = []
        for j in range(NV + 1):
            v = j / NV; row = []
            for i in range(NU + 1):
                phi = math.radians(A0 + (A1 - A0) * i / NU); p, inn, s = pt_xy(phi, hx, hy)
                if closed:                                            # cap: plateau + bevel, then flared wall
                    if v < 0.55:
                        t = v / 0.55; r = math.sin(t * math.pi / 2) ** 0.55
                        z = zt - 0.30 * (1 - math.cos(t * math.pi / 2)) ** 1.2
                    else:
                        t = (v - 0.55) / 0.45; r = 1.0 + 0.10 * t
                        zb = zh - pt * max(0, -s) ** 3; zb = zb + (0.02 - zb) * inn ** 1.5; z = (zt - 0.30) + (zb - (zt - 0.30)) * t
                    row.append(V((p.x * r, p.y * r, z)) if j else V((-0.10, 0, zt)))
                else:
                    r = 0.94 + 0.12 * math.sin(v * math.pi / 2); z = zt + (zh - zt) * v - pt * max(0, -s) ** 3 * v - 0.12 * inn * v
                    row.append(V((p.x * r, p.y * r, z)))
            grid.append(row)
        rect, vr = at.take(grid, 0.0, 1.0 if closed else (0.85 if key == 'slab1' else 0.7), v_scale=1.12 if closed else 1.0)
        b.flat_mode = 1
        b.sheet(grid, thick, rect, "obsidian", rim="gold", closed_u=closed, pole_row0=closed, normal_hint=(lambda p: V((p.x, p.y, p.z + 0.4))) if closed else (lambda p: V((p.x, p.y, 0))), key=key, v_rows=vr)
        b.flat_mode = 0
        return grid
    # magma core visible in the gaps
    cg = []
    for z in (0.00, -0.30, -0.70, -1.05, -1.20):
        row = []
        for i in range(NU + 1):
            phi = 2 * math.pi * i / NU; p, inn, s = pt_xy(phi, 0.60, 0.56, 1.0); row.append(V((p.x, p.y, z)))
        cg.append(row)
    cr, cvr = at.take(cg, 0.0, 0.5)
    b.sheet(cg, 0.05, cr, "red", rim="red", closed_u=True, normal_hint=lambda p: V((p.x, p.y, 0)), key="core", v_rows=cvr)
    g0 = slab(0.40, -0.40, 0.98, 0.82, 0.34, "slab0", True)
    g1 = slab(-0.34, -0.80, 0.88, 0.74, 0.22, "slab1", False, A0=125, A1=415, NV=4, thick=0.06)
    g2 = slab(-0.72, -1.14, 0.74, 0.62, 0.15, "slab2", False, A0=135, A1=405, NV=4, thick=0.055)
    b.extrude([(0.20 * math.cos(k * math.pi / 4 + math.pi / 8), 0.20 * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)], V((-0.10, 0.0, 0.405)), V((1, 0, 0)), V((0, 1, 0)), 0.07, 0.02, "gold")
    strand(b, [V((-0.10, 0.0, 0.43)), V((-0.10, 0.0, 0.62))], 0.13, cell("molten"), flat=1.0, sides=6, shade=True, taper=1.0)
    # spikes: fan on the outer/back rim of the top slab (flat-shaded rock horns)
    for bx, by, bz, d, L, w in ((-0.50, 0.50, 0.30, (-0.20, 0.38, 1.0), 0.66, 0.22), (-0.78, 0.12, 0.26, (-0.40, 0.10, 1.0), 0.58, 0.20),
                                (-0.62, -0.38, 0.26, (-0.35, -0.30, 1.0), 0.44, 0.18), (-0.14, 0.62, 0.30, (0.0, 0.40, 1.0), 0.48, 0.17)):
        d = V(d).normalized(); base_p = V((bx, by, bz)); mid = base_p + d * L * 0.5 + V((d.x * 0.06, d.y * 0.06, 0)); tip = base_p + d * L + V((d.x * 0.25 * L, d.y * 0.2 * L, -0.05))
        strand(b, bez(base_p - d * 0.10, mid, tip, 5), w, SP, flat=1.0, sides=5, shade=True, taper=0.85)
    for gx, zz, pt, cnt in ((g1, -0.80, 0.22, 3), (g2, -1.14, 0.15, 3)):     # hem points on the lower slabs (outer side)
        for k in range(cnt):
            i = 4 + k * 3 if gx is g1 else 4 + k * 3; p = gx[-1][min(NU, i)]
            if p.x > 0.1: continue
            out = V((p.x, p.y, 0)).normalized(); base_p = p - V((0, 0, 0.02))
            strand(b, bez(base_p, base_p + out * 0.10 + V((0, 0, -0.14)), base_p + out * 0.22 + V((0, 0, -0.34)), 3), 0.10, SP, flat=1.3, sides=4, shade=True, taper=0.9)
    ob = b.finish(); tex_material(ob.data, "ew_pauldron_r"); return ob


# ------------------------------------------------------------------ CAPE (BodyBackAttachment): tattered
def build_cape():
    """tattered cloak: asymmetric flutter, deep irregular torn hem (nine uneven tatters), charred glowing edge, ember lining,
    gold braid at the neckline. Outer face UV rect left half, lining right half (same grid)."""
    b = Builder("ew_cape"); NU, NV = 40, 18; at = Atlas(2048); rnd = random.Random(8)
    top_w, bot_w, z0, zbase, y0, flare = 1.20, 2.80, -0.30, -2.75, 0.62, 1.05
    tat = [(0.06, 0.07, 0.35), (0.16, 0.08, 0.95), (0.27, 0.07, 0.55), (0.37, 0.08, 1.20), (0.50, 0.09, 0.80), (0.62, 0.07, 1.30), (0.73, 0.08, 0.60), (0.84, 0.07, 1.05), (0.94, 0.07, 0.45)]
    def hem(u):
        d = 0.0
        for c, hw, dep in tat: d = max(d, dep * max(0.0, 1 - abs(u - c) / hw) ** 0.9)
        return -d - 0.04 * math.sin(u * 61.0) * 0.5
    grid, folds = [], []
    for j in range(NV + 1):
        v = j / NV; row, frow = [], []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.5) + 0.22 * v * v
            zb = zbase + hem(u); z = z0 + (zb - z0) * v
            wrap = 0.05 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2
            ph = (u - 0.5) * 2 * math.pi * 3.0 * (1 + 0.3 * v) + 0.8
            fd = math.sin(ph) * (0.15 + 0.85 * v ** 1.3); d = 0.12 * fd + 0.04 * math.sin(ph * 2.1 + 1.0) * v
            flut = 0.10 * math.sin(u * 19 + 1.3) * sm((v - 0.55) / 0.45)
            y = y0 + flare * v ** 1.8 - wrap + d + flut + 0.12 * (2 * (u - 0.5)) ** 2 * v
            row.append(V((x, y, z))); frow.append(fd)
        grid.append(row); folds.append(frow)
    rect, vr = at.take(grid, 0.0, 0.5, v_scale=1.45)
    b.sheet(grid, 0.03, rect, (0.5, rect[1], 1.0, rect[3]), rim="ember", normal_hint=lambda p: V((0, 1, 0)), fold=folds, key="outer", v_rows=vr)
    ob = b.finish(); tex_material(ob.data, "ew_cape"); return ob


# ------------------------------------------------------------------ COLLAR (NeckAttachment): spiked obsidian gorget
def build_collar():
    """gorget: faceted obsidian ring with a gold-rimmed yoke, a flare of tall flat-shaded shards at the sides/back (open at the
    front), small front points, and a hanging chest plate with a molten gem."""
    b = Builder("ew_collar"); at = Atlas(1024); NU = 24
    SH = at.fixed(0.0, 0.18, 0.12); register_rect("ew_collar", "shard", SH)
    rows = [(0.22, 0.76, 0.74), (0.15, 0.79, 0.77), (0.02, 0.82, 0.79), (-0.12, 0.85, 0.81), (-0.24, 0.88, 0.83), (-0.34, 0.91, 0.83)]
    GAP = 0.95; g = []
    for j, (z, rx, ry) in enumerate(rows):
        row = []
        for i in range(NU + 1):
            phi = math.pi + GAP + (2 * math.pi - 2 * GAP) * i / NU; s_, c = math.sin(phi), math.cos(phi); rib = 1 + 0.03 * (i % 2)
            row.append(V((rx * rib * spow(s_, 2 / 4.5), -ry * rib * spow(c, 2 / 4.5), z - 0.18 * max(0.0, -c) ** 2.0 * (1 if j > 1 else 0.3))))
        g.append(row)
    rect, vr = at.take(g, 0.0, 1.0, v_scale=1.0)
    b.flat_mode = 1
    b.sheet(g, 0.06, rect, "obsidian", rim="gold", normal_hint=lambda p: V((p.x, p.y, 0.15)), key="ring", v_rows=vr)
    b.flat_mode = 0
    for a_deg, h, w in ((62, 0.40, 0.12), (84, 0.52, 0.14), (104, 0.56, 0.15)):
        for sg in (-1, 1):
            a = math.radians(a_deg) * sg; rx_, ry_ = 0.78, 0.76
            base_p = V((rx_ * spow(math.sin(a), 2 / 4.5), -ry_ * spow(math.cos(a), 2 / 4.5), 0.06)); out = V((math.sin(a), -math.cos(a), 0)); tang = V((math.cos(a), math.sin(a), 0))
            tip = base_p + out * (0.16 + 0.12 * h) + V((0, 0, h)) + tang * (-0.05 * sg)
            mid = base_p + out * (0.15 + 0.06 * h) + V((0, 0, h * 0.45))
            strand(b, bez(base_p - V((0, 0, 0.06)), mid, tip, 5), w, SH, flat=1.5, sides=4, shade=True, taper=0.8, rad0=out)
    # chest plate hanging from the front of the ring
    NU2, NV2 = 8, 8; g2 = []
    for j in range(NV2 + 1):
        v = j / NV2; row = []
        for i in range(NU2 + 1):
            u = i / NU2; half = 0.30 * (1 - v) ** 0.7 + 0.04
            row.append(V(((u - 0.5) * 2 * half, -0.90 + 0.32 * v + 0.05 * (1 - (2 * u - 1) ** 2), -0.38 - 0.78 * v)))
        g2.append(row)
    rect2, vr2 = at.take(g2, 0.0, 0.17, v_scale=1.3)
    b.flat_mode = 1
    b.sheet(g2, 0.06, rect2, "obsidian", rim="gold", normal_hint=lambda p: V((0, -1, 0)), key="plate", v_rows=vr2)
    b.flat_mode = 0
    b.extrude([(0, 0.17), (0.12, 0.0), (0, -0.17), (-0.12, 0.0)], V((0, -0.80, -0.55)), V((1, 0, 0)), V((0, 0, 1)), 0.05, 0.015, "gold")
    b.gem(V((0, -0.83, -0.55)), 0.075, 0.13, V((0, -1, 0)), "molten")
    ob = b.finish(); tex_material(ob.data, "ew_collar"); return ob


# ------------------------------------------------------------------ AXE (WaistBackAttachment): molten battle-axe
def lathe(b, prof, sides, rect, flat=True):
    """closed surface of revolution about +Z: prof = [(z, r)] bottom->top (r may be 0 at the ends). UV u around, v along z."""
    z0, z1 = prof[0][0], prof[-1][0]; rings = []
    for z, r in prof:
        if r > 1e-5: rings.append([b.bm.verts.new(V((r * math.cos(2 * math.pi * q / sides), r * math.sin(2 * math.pi * q / sides), z))) for q in range(sides)])
        else: rings.append([b.bm.verts.new(V((0, 0, z)))])
    def uv(q, z): return (rect[0] + (rect[2] - rect[0]) * (q / sides), rect[1] + (rect[3] - rect[1]) * (z - z0) / (z1 - z0))
    b.flat_mode = 1 if flat else 0
    for k in range(len(prof) - 1):
        (za, ra), (zb, rb) = prof[k], prof[k + 1]; A, Bn = rings[k], rings[k + 1]
        for q in range(sides):
            q2 = (q + 1) % sides
            if ra <= 1e-5 and rb <= 1e-5: continue
            if ra <= 1e-5: b.face([A[0], Bn[q2], Bn[q]], [uv(q, za), uv(q + 1, zb), uv(q, zb)])
            elif rb <= 1e-5: b.face([A[q], A[q2], Bn[0]], [uv(q, za), uv(q + 1, za), uv(q, zb)])
            else: b.face([A[q], A[q2], Bn[q2], Bn[q]], [uv(q, za), uv(q + 1, za), uv(q + 1, zb), uv(q, zb)])
    b.flat_mode = 0


def build_axe():
    """upright (haft along +Z, head toward -X, blade thickness along Y): crescent double-plate blade with a glowing edge,
    socket gem, back spike, octagonal haft with gold collars and a spear-tip top; placed on the back by place_axe()."""
    b = Builder("ew_axe"); at = Atlas(2048)
    HAFT = (0.50, 0.30, 0.66, 0.98); register_rect("ew_axe", "haft", HAFT)
    z_top, z_bot = 3.30, 1.20; NR, NC = 10, 16          # rows run edge -> root, columns tip -> tip: every row is a long arc, so the UV rect is near-isotropic
    def surf(sgn):
        g = []
        for j in range(NR + 1):
            f = j / NR; row = []
            for i in range(NC + 1):
                t = i / NC; z = z_top + (z_bot - z_top) * t; sn = math.sin(math.pi * t)
                xe = -(1.62 - 0.62 * sn ** 1.1) + 0.03 * math.sin(t * 31); xr = xe + 0.07 + 0.86 * sn ** 0.9
                row.append(V((xe + (xr - xe) * f, sgn * (0.012 + 0.13 * sm(f * 1.25) * sm(min(1.0, sn * 5))), z)))
            g.append(row)
        return g
    ga, gb = surf(1), surf(-1)
    rect, vr = at.take(ga, 0.0, 0.45)
    b.sheet(ga, 0.03, rect, "obsidian", rim="molten", normal_hint=lambda p: V((0, 1, 0)), key="bladeA", v_rows=vr)
    b.sheet(gb, 0.03, rect, "obsidian", rim="molten", normal_hint=lambda p: V((0, -1, 0)), v_rows=vr)
    # haft: octagonal obsidian with gold collars, pointed pommel, spear tip
    prof = [(0.0, 0.0), (0.0, 0.07), (0.10, 0.105), (0.26, 0.11), (0.32, 0.08), (1.35, 0.08), (1.41, 0.115), (1.52, 0.115), (1.58, 0.08), (1.80, 0.08), (1.84, 0.12), (1.96, 0.12), (2.0, 0.08),
            (3.10, 0.08), (3.15, 0.115), (3.25, 0.115), (3.32, 0.07), (3.95, 0.0)]
    lathe(b, prof, 8, HAFT)
    # back spike of the head (opposite the blade) and a molten orb in the socket
    strand(b, bez(V((0.05, 0, 2.25)), V((0.40, 0, 2.28)), V((0.85, 0, 2.38)), 4), 0.15, HAFT, flat=1.0, sides=4, shade=True, rad0=V((0, 1, 0)))
    b.extrude([(0, 0.26), (0.14, 0.0), (0, -0.26), (-0.14, 0.0)], V((-0.10, 0.145, 2.25)), V((1, 0, 0)), V((0, 0, 1)), 0.06, 0.02, "gold")
    b.extrude([(0, 0.26), (0.14, 0.0), (0, -0.26), (-0.14, 0.0)], V((-0.10, -0.145, 2.25)), V((1, 0, 0)), V((0, 0, 1)), 0.06, 0.02, "gold")
    b.gem(V((-0.10, 0.20, 2.25)), 0.08, 0.19, V((0, 1, 0)), "molten"); b.gem(V((-0.10, -0.20, 2.25)), 0.08, 0.19, V((0, -1, 0)), "molten")
    ob = b.finish(); tex_material(ob.data, "ew_axe"); return ob


def place_axe(ob):
    """worn on the lower back (WaistBackAttachment): haft diagonal over the cape, head at the upper outer end, tilted with the cape flare.
    Auto-fits the Waist box (Slender 3.76 wide, 1.414 up / 1.885 down of the attachment at neck z -2.098)."""
    me = ob.data; me.transform(Matrix.Translation((0, 0, -1.95)))               # centre the haft about the origin
    R = Matrix.Rotation(math.radians(16), 3, "X") @ Matrix.Rotation(math.radians(-48), 3, "Y"); me.transform(R.to_4x4())
    xs = [v.co.x for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    sc = min(1.0, 3.60 / (max(xs) - min(xs)), 3.20 / (max(zs) - min(zs)))
    me.transform(Matrix.Scale(sc, 4))
    xs = [v.co.x for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    cx = (max(xs) + min(xs)) / 2; cz = (max(zs) + min(zs)) / 2
    zc = (-2.098 - 1.885 + -2.098 + 1.414) / 2 - 0.02
    me.transform(Matrix.Translation((-cx, AXE_Y, zc - cz))); print("axe scale", round(sc, 3))


AXE_Y = 1.82


def bake_ao(ob, size, others, samples=24):
    """Cycles AO bake into the item's UV atlas -> out/ao_<item>.png (world distance 0.45 = local occlusion; copied from build_cv.py)"""
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.device = "CPU"
    if sc.world is None: sc.world = bpy.data.worlds.new("bakeworld")
    sc.world.light_settings.distance = 0.45
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


def body_proxy(shirt_png, pants_png):
    """block R15 proxy for renders (copied from build_cv.py)"""
    sh = bpy.data.images.load(shirt_png); pa = bpy.data.images.load(pants_png)
    P = {"t": B.SHIRT["t"], "rl": B.SHIRT["ra"], "ll": B.SHIRT["la"]}
    objs = [B.tbox("torso", (2, 1, 2.1), (0, 0, -1.05), B.SHIRT["t"], sh), B.tbox("armR", (1, 1, 2.1), (-1.5, 0, -1.05), B.SHIRT["ra"], sh),
            B.tbox("armL", (1, 1, 2.1), (1.5, 0, -1.05), B.SHIRT["la"], sh), B.tbox("legR", (1, 1, 2.19), (-0.5, 0, -3.195), P["rl"], pa),
            B.tbox("legL", (1, 1, 2.19), (0.5, 0, -3.195), P["ll"], pa)]
    bpy.ops.mesh.primitive_cube_add(size=1); hd = bpy.context.object; hd.name = "head"; hd.scale = (1.16, 1.16, 1.18); hd.location = (0, 0, HC)
    bv = hd.modifiers.new("b", "BEVEL"); bv.width = 0.14; bv.segments = 3
    m = bpy.data.materials.new("skin"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.42, 0.32, 1)
    hd.data.materials.append(m)
    fp = os.path.join(OUT, "ew_face.png")
    if os.path.exists(fp):
        bpy.ops.mesh.primitive_plane_add(size=1); fc = bpy.context.object; fc.name = "face"
        fc.rotation_euler = (math.radians(90), 0, 0); fc.scale = (1.16, 1.18, 1.0); fc.location = (0, -0.585, HC)
        fm = bpy.data.materials.new("face"); fm.use_nodes = True; nt = fm.node_tree; bs = nt.nodes["Principled BSDF"]
        ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(fp)
        nt.links.new(ti.outputs["Color"], bs.inputs["Base Color"]); nt.links.new(ti.outputs["Alpha"], bs.inputs["Alpha"])
        try: fm.surface_render_method = "DITHERED"
        except Exception: fm.blend_method = "HASHED"
        fc.data.materials.append(fm); objs.append(fc)
    return objs + [hd]


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    helm = build_helm(); r = build_pauldron(); cape = build_cape(); collar = build_collar(); axe = build_axe()
    disp = axe.copy(); disp.data = axe.data.copy(); disp.name = "ew_axe_display"; bpy.context.collection.objects.link(disp); disp.data.transform(Matrix.Translation((0, 0, -2.0))); disp.hide_render = True
    place_axe(axe)
    l = r.copy(); l.data = r.data.copy(); l.name = "ew_pauldron_l"; bpy.context.collection.objects.link(l)
    l.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); l.data.flip_normals()
    r.location = (-1.5, 0, 0); l.location = (1.5, 0, 0)
    body_proxy(os.path.join(OUT, "ew_shirt.png"), os.path.join(OUT, "ew_pants.png"))
    for o in (helm, r, l, cape, collar, axe): print("ITEM", o.name, "tris", tris(o))
    for it, regs in B.META.items():
        for k, s in regs.items():
            if isinstance(s, dict) and "rect" in s and "pos" in s: print("UVRECT", it, k, tuple(round(x, 3) for x in s["rect"]))
    with open(os.path.join(OUT, "meta.json"), "w") as fh: json.dump(B.META, fh)
    if os.environ.get("NOBAKE") != "1":
        items = [o for o in (helm, r, cape, collar, axe) if o.name in B.META]; t0 = time.time()
        for o in items: bake_ao(o, 2048 if o.name == "ew_pauldron_r" else 1024, [x for x in (helm, r, l, cape, collar, axe, disp) if x is not o])
        print("AO baked", [o.name for o in items], "in %.1fs" % (time.time() - t0))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "ew_build.blend")); print("DONE")

"""Crystal Vanguard - accessories (crown+hair, pauldron R/L, cape, scarf, sword) built in Blender.
Run: Blender -b -P build_cv.py   (after make_clothing_cv.py and paint_cv.py has NOT to run first: textures are loaded lazily by render_cv.py)
Frame (same as tidewatch): x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment.
Writes out/cv_build.blend. UV layout: every non-sword item uses an 8-swatch strip at the bottom of its atlas (v 0..0.06)."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
import rgen_mesh as B                     # shared Builder / swatches / body proxy (lib/rgen_mesh.py)
from rgen_mesh import Builder, sm, spow

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
GLB = os.path.join(HERE, "..", "..", "starter", "crystal-vanguard", "3d", "crystal_vanguard_sword_blockout.glb")
HC = 0.576
# 8 swatch cells (u centre, v centre) -- painted by paint_cv.py (strip_colors)
CELLS = ["gold", "silver", "crystal", "navy", "ice", "sapphire", "white", "gold_dark"]
B.SW.clear()
for k, n in enumerate(CELLS): B.SW[n] = ((k + 0.5) / 8, 0.03)
B.SW.update({"bronze": B.SW["gold"], "pearl": B.SW["silver"], "aqua": B.SW["crystal"], "dark": B.SW["navy"]})
def cell(n, a=0.2, b=0.8):       # small rect inside a swatch cell (for sheet() r_out/r_in)
    u = B.SW[n][0]; return (u - 0.05, 0.012, u + 0.05, 0.048)


def iso_rect(grid, u0, u1, v1, S, min_frac=0.5, v_scale=1.0):
    """r26: UV rect + per-row v positions giving the SAME texel density along u and v (GPU mip selection without anisotropic
    filtering follows the denser direction, so an anisotropic layout smears the other one in Studio). The rect spans u0..u1 at the
    top edge v1; its height follows from the grid's physical row/column lengths and the atlas size S. Rows shorter than min_frac of
    the longest row (fan rows near a pole) are treated as min_frac long: a fan cannot be isotropic at its pole.
    Returns (rect, v_rows, height_frac)."""
    NV, NU = len(grid) - 1, len(grid[0]) - 1
    rowlen = [sum((grid[j][i + 1] - grid[j][i]).length for i in range(NU)) for j in range(NV + 1)]
    mx = max(rowlen); eff = [max(l, min_frac * mx) for l in rowlen]; wpx = (u1 - u0) * S; bands = []
    for j in range(NV):
        col = sum((grid[j + 1][i] - grid[j][i]).length for i in range(NU + 1)) / (NU + 1)
        bands.append(col * wpx / ((eff[j] + eff[j + 1]) / 2))
    tot = sum(bands) * v_scale; cum = [0.0]                       # v_scale > 1: a little more v density (for faces whose columns are stretched, e.g. a pointed hem)
    for h in bands: cum.append(cum[-1] + h * v_scale / tot)
    return (u0, v1 - tot / S, u1, v1), cum, tot / S


def tex_material(me, name):
    mat = bpy.data.materials.new("mat_" + name); mat.use_nodes = True; me.materials.append(mat)


def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def bipyramid(b, base, axis, w, h, sides=6, mid=0.35, swatches=("crystal", "ice", "sapphire", "crystal", "ice", "sapphire")):
    """faceted crystal: apex bottom at base, widest ring at mid*h, apex top at base+axis*h"""
    ax = axis.normalized(); t = ax.cross(Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))).normalized(); s = ax.cross(t)
    ring = [b.bm.verts.new(base + ax * h * mid + (t * math.cos(2 * math.pi * k / sides) + s * math.sin(2 * math.pi * k / sides)) * w) for k in range(sides)]
    top = b.bm.verts.new(base + ax * h); bot = b.bm.verts.new(base)
    b.flat_mode = 1
    for k in range(sides):
        k2 = (k + 1) % sides; sw = swatches[k % len(swatches)]
        b.face([ring[k], ring[k2], top], [B.SW[sw]] * 3); b.face([ring[k2], ring[k], bot], [B.SW[sw if k % 2 else "sapphire"]] * 3)
    b.flat_mode = 0


# ------------------------------------------------------------------ CROWN + HAIR (HatAttachment)
def build_crown():
    """r19: concept hair = smooth white dome + FEW large clean swept spikes (anime), smooth-shaded closed strands with one frame each,
    spiky back locks hanging down/out over the nape (the cape collar sits under their tips, no skin band), side locks over the ears;
    crown = low gold band with a big centre crystal in a gold diamond frame + smaller side crystals. Dome + strands have real UVs."""
    b = Builder("cv_crown"); rnd = random.Random(11)
    NU, NV, E = 28, 7, 3.0; R = 0.74
    def hemz(phi):            # hem height above the head centre: forehead high, ears and nape low (locks continue below)
        c = math.cos(phi); return 0.26 * max(0, c) ** 0.8 - 0.32 * max(0, -c) ** 1.0 - 0.16 * abs(math.sin(phi)) ** 1.5   # r21: nape covered down to the collar
    grid = []
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            phi = 2 * math.pi * i / NU
            cz = max(-0.5, min(0.97, hemz(phi) / R)); th = math.acos(cz) * v
            n = 0.02 * math.sin(9 * phi + 1.3) * sm(v * 1.6) + 0.015 * math.sin(5 * phi) * v
            r = R + n
            x = r * spow(math.sin(th), 2 / E) * spow(math.sin(phi), 2 / E)
            y = -r * spow(math.sin(th), 2 / E) * spow(math.cos(phi), 2 / E) + 0.04 * v
            z = HC + (R + 0.06) * spow(math.cos(th), 2 / E)
            row.append(Vector((x, y, z)) if j else Vector((0, 0.04, HC + R + 0.06)))
        grid.append(row)
    b.sheet(grid, 0.04, (0, 0.08, 1, 0.46), "silver", rim="silver", closed_u=True, pole_row0=True, normal_hint=lambda p: Vector((p.x, p.y, p.z - HC)), key="dome")
    def dome(phi, th, r=R + 0.05):
        return Vector((r * spow(math.sin(th), 2 / E) * spow(math.sin(phi), 2 / E), -r * spow(math.sin(th), 2 / E) * spow(math.cos(phi), 2 / E), HC + r * spow(math.cos(th), 2 / E)))
    HR = (0.0, 0.50, 1.0, 0.92)                                        # strand UV rect: u around the strand (0.25 = outer face), v root -> tip
    def strand(path, w0, flat=1.5, sides=7):
        """closed tapered spike: flattened rings (wide along the dome surface, thin radially) with ONE frame per strand, smooth shaded,
        capped base, sharp tip; every vertex clamped to the Hair box (|x| 0.88, y -0.92..1.17)"""
        CL = lambda p: Vector((max(-0.88, min(0.88, p.x)), max(-0.92, min(1.17, p.y)), p.z))
        path = [CL(p) for p in path]; n = len(path) - 1
        rad0 = path[0] - Vector((0, 0.04, HC)); rad0.z *= 0.4; rad0.normalize()
        rings, vs_uv = [], []
        for k, c in enumerate(path[:-1]):
            d = (path[k + 1] - c).normalized() if k == 0 else (path[k + 1] - path[k - 1]).normalized()
            side = d.cross(rad0)
            if side.length < 1e-4: side = d.cross(Vector((0, 0, 1)))
            side.normalize(); s2 = side.cross(d).normalized()
            w = w0 * (1 - k / n) ** 0.85                          # r22: sharper tips
            rings.append([b.bm.verts.new(CL(c + (side * math.cos(2 * math.pi * q / sides) * flat + s2 * math.sin(2 * math.pi * q / sides) * 0.5) * w)) for q in range(sides)])
            vs_uv.append(HR[1] + (HR[3] - HR[1]) * k / n)
        tip = b.bm.verts.new(path[-1]); uvt = (HR[0] + 0.5, HR[3])
        def uvq(q, k): return (HR[0] + (HR[2] - HR[0]) * (q / sides), vs_uv[k])
        b.face(rings[0][::-1], [uvq(q, 0) for q in range(sides)][::-1])
        for k, (r0, r1) in enumerate(zip(rings[:-1], rings[1:])):
            for q in range(sides):
                q2 = (q + 1) % sides; b.face([r0[q], r0[q2], r1[q2], r1[q]], [uvq(q, k), uvq(q + 1, k), uvq(q + 1, k + 1), uvq(q, k + 1)])
        for q in range(sides):
            b.face([rings[-1][q], rings[-1][(q + 1) % sides], tip], [uvq(q, n - 1), uvq(q + 1, n - 1), uvt])
    def bez(p0, p1, p2, n=5):
        return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (k / n for k in range(n + 1))]
    HEADC = Vector((0, 0.04, HC))
    # 1) 9 big spikes around the upper dome, rising up and sweeping back (front ones sweep back most)
    for k in range(9):
        phi = -math.pi + 2 * math.pi * (k + 0.5) / 9 + rnd.uniform(-0.08, 0.08); th = rnd.uniform(0.40, 0.58)
        base = dome(phi, th, R * 0.97); out = (base - HEADC).normalized()
        back = max(0.0, math.cos(phi))
        L = rnd.uniform(0.62, 0.82) * (0.85 + 0.3 * back)
        mid = base + out * L * 0.45 + Vector((0, 0.20 * back + 0.08, 0.28)) * L
        tip = mid + Vector((out.x * 0.25, 0.32 + 0.2 * back, 0.20 - 0.1 * (1 - back))) * L * 1.4
        strand(bez(base - out * 0.08, mid, tip), rnd.uniform(0.16, 0.20))
    # 2) 6 silhouette spikes lower on the dome (sides/back), flaring out, tips kicking up
    for k in range(6):
        phi = math.radians(70 + 220 * k / 5) + rnd.uniform(-0.08, 0.08); th = rnd.uniform(0.88, 1.05)
        base = dome(phi, th, R * 0.97); out = (base - HEADC).normalized(); out.z = 0; out.normalize()
        L = rnd.uniform(0.44, 0.58)
        mid = base + out * L * 0.55 + Vector((0, 0.06, 0.04)); tip = mid + out * L * 0.45 + Vector((0, 0.10, 0.24))
        strand(bez(base - out * 0.08, mid, tip), rnd.uniform(0.14, 0.17))
    # 3) back locks: spiky layered locks from the nape hem DOWN and OUT over the cape collar (tips outside the collar surface,
    #    y up to 1.12 < Hair box 1.18), staggered lengths so they read as separate locks
    for k in range(7):
        side = (k - 3) / 3.0                                           # -1..1 across the back
        phi = math.pi - side * 1.2 + rnd.uniform(-0.05, 0.05); th = rnd.uniform(1.0, 1.15)
        base = dome(phi, th, R * 0.95)
        out = Vector((base.x, base.y - 0.04, 0)).normalized()
        long = k % 2 == 0                                              # alternate long / short locks (layered, not a curtain)
        zt = HC - (0.52 if long else 0.36) - 0.05 * (1 - abs(side)) + rnd.uniform(-0.03, 0.03)
        yt = (1.10 if long else 0.98) + 0.04 * (1 - abs(side))
        tip = Vector((base.x * 1.3 + side * 0.22, min(1.12, yt), zt))   # tips flick outward and back
        mid = Vector(((base.x + tip.x) / 2, (base.y + tip.y) / 2 + 0.10, (base.z + tip.z) / 2 + 0.08))
        strand(bez(base - out * 0.06, mid, tip), 0.19 if long else 0.15, flat=1.8)
    # 4) side locks over the ears (sideburns), down to cheek height
    for sg in (-1, 1):
        for k in range(2):
            phi = sg * math.radians(92 + 16 * k); base = dome(phi, 1.1, R * 0.95)
            tip = Vector((sg * 0.80, base.y + 0.10 + 0.1 * k, HC - 0.30 - 0.06 * k))
            mid = Vector((sg * 0.84, (base.y + tip.y) / 2, (base.z + tip.z) / 2 + 0.04))
            strand(bez(base - Vector((sg * 0.05, 0, 0)), mid, tip), 0.12, flat=1.6)
    # 5) bangs: three locks swept across the forehead under the band
    for k, (a0, a1, zt) in enumerate(((-12, 30, 0.30), (-28, 8, 0.33), (6, 44, 0.27))):
        p0 = math.radians(a0); p1 = math.radians(a1)
        base = Vector((0.60 * math.sin(p0), -0.66 * math.cos(p0), HC + 0.52))
        tip = Vector((0.70 * math.sin(p1), -0.74 * math.cos(p1), HC + zt))
        mid = (base + tip) / 2 + Vector((0, -0.10, 0.04))
        strand(bez(base, mid, tip), 0.12, flat=1.7)
    # --- gold band (closed ring) low on the forehead, slightly higher at the back
    NUb = 32; g = []
    for dz in (0.16, 0.12, 0.04, 0.0):
        row = []
        for i in range(NUb + 1):
            phi = 2 * math.pi * i / NUb; r = 0.745 + (0.02 if dz in (0.16, 0.0) else 0)
            zb = HC + 0.36 + 0.10 * max(0, -math.cos(phi))
            row.append(Vector((r * spow(math.sin(phi), 0.5) * 0.99, -r * spow(math.cos(phi), 0.5), zb + dz)))
        g.append(row)
    b.sheet(g, 0.03, cell("gold"), "gold_dark", rim="gold_dark", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)))
    for ang in (36, -36, 72, -72):                                      # small gems on the band
        a = math.radians(ang); c = Vector((0.775 * math.sin(a), -0.765 * math.cos(a), HC + 0.44))
        b.gem(c, 0.045, 0.06, Vector((math.sin(a), -math.cos(a), 0)), "crystal")
    # --- centre crystal in a gold diamond frame on the front of the band (concept), smaller crystals to the sides, temple shards
    b.extrude([(0, 0.26), (0.17, 0.02), (0, -0.14), (-0.17, 0.02)], Vector((0, -0.745, HC + 0.50)), Vector((1, 0, 0)), Vector((0, 0, 1)), 0.05, 0.015, "gold")
    for ang, hh, w, z0 in ((0, .74, .14, 0.50), (24, .44, .10, 0.50), (-24, .44, .10, 0.50), (50, .32, .085, 0.50), (-50, .32, .085, 0.50), (92, .40, .09, 0.50), (-92, .40, .09, 0.50)):
        a = math.radians(ang); r = 0.74 if abs(ang) > 10 else 0.76
        base = Vector((r * math.sin(a), -r * math.cos(a), HC + z0)); out = Vector((math.sin(a), -math.cos(a), 0))
        axis = (Vector((0, 0, 1)) + out * (0.14 + 0.08 * (abs(ang) > 80))).normalized()
        bipyramid(b, base, axis, w, hh, 6)
    ob = b.finish(); tex_material(ob.data, "cv_crown"); return ob


# ------------------------------------------------------------------ PAULDRON (Right/LeftShoulderAttachment)
def build_pauldron():
    """r11: angular layered plates like the concept. Top plate = wide boxy shell (superellipse E=5) that overhangs the shoulder,
    outer edge dipping to a point; two thinner lames below, each narrower, open on the torso side, pointed outward; navy
    underlayer in the gaps; protruding gold rim on every hem; big framed gem on the OUTER face of the top plate; 2 crystal
    shards at the back. Plates carry real UV regions (meta.json pos/dist) for the physical-space painter + AO."""
    b = Builder("cv_pauldron_r"); E = 5.0; NU = 24
    def inner_f(s): return sm((s + 0.15) / 1.0)            # 1 on the torso side (+x local = towards the torso for the right shoulder)
    # navy underlayer (visible in the gaps between the plates)
    g = []
    for z in (-0.08, -0.50, -0.86, -0.98):
        g.append([Vector((0.56 * spow(math.sin(2 * math.pi * i / NU), 2 / E), 0.54 * spow(math.cos(2 * math.pi * i / NU), 2 / E), z)) for i in range(NU + 1)])
    b.sheet(g, 0.05, cell("navy"), "navy", rim="navy", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)))
    def rim_ring(z, hx, hy, arc=None, pt=0.0, zin=None):
        """sharp gold rim under a hem: 3-row ring protruding 0.05 beyond the plate, following the outer point"""
        g = []
        for dz, dr in ((0.07, 0.0), (0.0, 0.055), (-0.04, 0.045)):
            row = []
            for i in range(NU + 1):
                phi = math.radians(arc[0]) + math.radians(arc[1] - arc[0]) * i / NU if arc else 2 * math.pi * i / NU
                s, c = math.sin(phi), math.cos(phi)
                zz = z + dz - pt * max(0, -s) ** 3
                kx = 1.0
                if zin is not None: zz += (zin - z) * inner_f(s) ** 1.5; kx = 1 - 0.37 * inner_f(s)   # r24: follow the shell's inner shrink (the rim reached into the torso)
                row.append(Vector(((hx + dr) * kx * spow(s, 2 / E), (hy + dr) * spow(c, 2 / E), zz)))
            g.append(row)
        b.sheet(g, 0.03, cell("gold"), "gold_dark", rim="gold", closed_u=(arc is None), normal_hint=lambda p: Vector((p.x, p.y, 0)))
    # (z top, z hem, half x, half y, outer point depth, uv v0, v1)
    # r19: ONE dominant broad curved shell (deep cap, flaring skirt, sharp outer point) + one small lame tucked under it
    tiers = [(0.36, -0.52, 0.94, 0.80, 0.28, 0.30, 1.00), (-0.60, -0.86, 0.70, 0.64, 0.14, 0.08, 0.28)]   # r25: UV v ranges rebalanced for a 2048 atlas
    for k, (zt, zh, hx, hy, pt, v0, v1) in enumerate(tiers):
        grid = []
        if k == 0:
            NV = 11
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi); inn = inner_f(s)
                    if v < 0.45:                                   # deep curved cap
                        t = v / 0.45; r = math.sin(t * math.pi / 2) ** 0.75; z = zt - 0.24 * (1 - math.cos(t * math.pi / 2))
                    else:                                          # skirt: flares, outer hem dips to a sharp point, inner hem stays above the torso
                        t = (v - 0.45) / 0.55; r = 1.0 + 0.08 * t
                        zb = zh - pt * max(0, -s) ** 3; zb = zb + (0.02 - zb) * inn ** 1.5
                        z = (zt - 0.24) + (zb - (zt - 0.24)) * t
                    hx_ = hx * (1 - 0.37 * inn)                 # r22: inner edge further from the head (fall pose grazed the hair)
                    row.append(Vector((hx_ * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z)) if j else Vector((-0.10, 0, zt)))
                grid.append(row)
            rect, vr, hfrac = iso_rect(grid, 0.0, 1.0, 1.0, 2048, v_scale=1.15); lame_top = rect[1] - 0.02   # r26/r27: isotropic texels (2048 atlas); 1.15 keeps the pointed outer face <= 1.25
            b.sheet(grid, 0.06, rect, "navy", rim="silver", closed_u=True, pole_row0=True, normal_hint=lambda p: Vector((p.x, p.y, p.z + 0.4)), key="lame0", v_rows=vr)   # r22: navy interior
            rim_ring(zh, hx * 1.04, hy * 1.04, pt=pt, zin=0.02)
        else:
            NV = 4; A0, A1 = 130, 410                               # open on the torso side (phi 90 deg)
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = math.radians(A0 + (A1 - A0) * i / NU); s, c = math.sin(phi), math.cos(phi)
                    z = zt + (zh - zt) * v - pt * max(0, -s) ** 3 * v; r = 0.92 + 0.10 * math.sin(v * math.pi / 2)
                    row.append(Vector((hx * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z)))
                grid.append(row)
            rect, vr, hfrac = iso_rect(grid, 0.0, 1.0, lame_top, 2048)
            b.sheet(grid, 0.055, rect, "navy", rim="silver", normal_hint=lambda p: Vector((p.x, p.y, 0)), key=f"lame{k}", v_rows=vr)
            rim_ring(zh, hx * 1.04, hy * 1.04, arc=(A0, A1), pt=pt)
    # big gem in a gold diamond frame on the outer face of the top plate
    xo = -0.94 * 1.04
    b.extrude([(0, 0.42), (0.27, 0), (0, -0.42), (-0.27, 0)], Vector((xo + 0.02, -0.02, -0.16)), Vector((0, 1, 0)), Vector((0, 0, 1)), 0.08, 0.025, "gold")
    b.gem(Vector((xo - 0.03, -0.02, -0.16)), 0.18, 0.31, Vector((-1, -0.05, 0)), "crystal")
    # two crystal shards rising at the back of the shell
    for dx, hh, tilt in ((-0.34, 0.42, -0.3), (-0.04, 0.34, 0.1)):
        bipyramid(b, Vector((dx, 0.48, 0.16)), Vector((tilt * 0.5, 0.35, 1.0)), 0.07, hh, 6)
    ob = b.finish(); tex_material(ob.data, "cv_pauldron_r"); return ob


# ------------------------------------------------------------------ CAPE (BodyBackAttachment) + high collar
def build_cape():
    """r12: concept cape = deep blue outer with a silver lining, gold border, pointed zigzag hem, big crystal emblem, and a tall
    white collar standing behind the neck. Outer face UV (0,0.08,0.5,1), lining UV (0.5,0.08,1,1) (painted from the same
    grid positions), fold map exported for the painter. Shoulders-wide at the top, flared back so the run back-kick only grazes it."""
    b = Builder("cv_cape"); NU, NV = 28, 26; grid, folds = [], []
    top_w, bot_w, z0, z1, y0, flare = 1.90, 2.70, -0.30, -3.62, 0.60, 1.15
    def hem(u):                                                   # 7 triangular points + a longer centre point
        tri = 1 - abs((u * 7 + 0.5) % 1.0 * 2 - 1)
        return -0.22 * tri - 0.22 * max(0, 1 - abs(2 * u - 1) * 5)
    for j in range(NV + 1):
        v = j / NV; row, frow = [], []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.15)
            z = z0 + (z1 - z0) * v + hem(u) * sm((v - 0.82) / 0.18)
            wrap = 0.30 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2            # wraps forward around the shoulders at the top
            ph = (u - 0.5) * 2 * math.pi * 3.5 * (1 + 0.25 * v) + 0.5
            fd = math.sin(ph) * (0.15 + 0.85 * v ** 1.3)
            d = 0.10 * fd + 0.03 * math.sin(ph * 2.3 + 1.0) * v
            y = y0 + flare * v ** 1.8 - wrap + d + 0.14 * (2 * (u - 0.5)) ** 2 * v
            row.append(Vector((x, y, z))); frow.append(fd)
        grid.append(row); folds.append(frow)
    rect, vr, hfrac = iso_rect(grid, 0.0, 0.5, 1.0, 2048)                                               # r26: isotropic texels
    b.sheet(grid, 0.03, rect, (0.5, rect[1], 1, 1), rim="gold", normal_hint=lambda p: Vector((0, 1, 0)), fold=folds, key="outer", v_rows=vr)
    collar_top = rect[1] - 0.02
    # tall collar: half ring behind the neck, bottom row resting on the shoulders, leaning back; own UV rects below the cape rects
    gc, fc = [], []; NU2 = 24
    # r19: folded hood lying on the shoulders under the hair tips: lower (top 0.20), dips at the back centre, bigger folds
    rows = ((0.24, 0.74, 0.78), (0.19, 0.80, 0.84), (0.02, 0.86, 0.86), (-0.16, 0.90, 0.82), (-0.34, 0.92, 0.74), (-0.42, 0.90, 0.70))
    for j, (z, rx, ry) in enumerate(rows):
        row, frow = [], []
        for i in range(NU2 + 1):
            phi = math.radians(-92 + 184 * i / NU2); lump = 0.045 * math.sin(i * 1.7 + j * 0.8) * (1 if 0 < j < 4 else 0.4)
            dip = -0.03 * math.cos(phi) ** 2 * (1 if j < 2 else 0.3)
            tuft = (0.05 if i % 2 else -0.01) * (1 if j == 0 else 0.3 if j == 1 else 0)     # r22: fur-like tufted rim
            row.append(Vector(((rx + lump) * math.sin(phi), (ry + lump) * math.cos(phi) + 0.02, z + dip + tuft))); frow.append(math.sin(i * 1.7 + j * 0.8))
        gc.append(row); fc.append(frow)
    rect, vr, hfrac = iso_rect(gc, 0.02, 0.48, collar_top, 2048)
    b.sheet(gc, 0.07, rect, (0.52, rect[1], 0.98, rect[3]), rim="silver", normal_hint=lambda p: Vector((p.x, p.y, 0.15)), fold=fc, key="collar", v_rows=vr)
    # gem clasps at the collar ends
    for sg in (-1, 1):
        b.gem(Vector((sg * 0.90, 0.08, -0.30)), 0.055, 0.075, Vector((sg, -0.6, 0.0)), "crystal")
    ob = b.finish(); tex_material(ob.data, "cv_cape"); return ob


# ------------------------------------------------------------------ SCARF (NeckAttachment)
def build_scarf():
    """r13: thick navy wrap around the neck up to the chin (concept), lower at the back under the cape collar, a wide bib tail
    hanging on the chest with folds, gold clasp + small crystal. Ring UV (0,0.36,1,0.66), tail UV (0,0.70,1,1); fold maps exported."""
    b = Builder("cv_scarf"); NU = 32; grid, folds = [], []
    rows = [(0.26, 0.60, 0.56), (0.20, 0.68, 0.62), (0.08, 0.74, 0.68), (-0.08, 0.77, 0.72), (-0.20, 0.78, 0.74), (-0.26, 0.76, 0.72)]   # r24: sides narrower (crossed the cape collar ends)
    for j, (z, rx, ry) in enumerate(rows):
        row, frow = [], []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
            fd = math.sin(7 * phi + 0.4 + j * 0.5); d = 0.035 * fd * (0.4 + j / 6)
            back = max(0.0, -c) ** 1.5                                  # back of the ring sits lower (under the collar)
            tuck = 1 - 0.18 * max(0.0, -c) ** 0.7                       # r22: back half smaller so it stays inside the cape collar (navy showed through it)
            row.append(Vector(((rx + d) * tuck * spow(s, 2 / 2.6), -(ry + d) * tuck * spow(c, 2 / 2.6), z - 0.22 * back * (1 if j < 3 else 0.5)))); frow.append(fd)
        grid.append(row); folds.append(frow)
    rect, vr, hfrac = iso_rect(grid, 0.0, 1.0, 1.0, 1024)                                               # r26: isotropic texels
    b.sheet(grid, 0.09, rect, "navy", rim="navy", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0.1)), fold=folds, key="ring", v_rows=vr)
    tail_top = rect[1] - 0.02
    # bib tail: wide at the top, pointed, lying on the chest, folds
    NU2, NV2 = 8, 10; g2, f2 = [], []
    for j in range(NV2 + 1):
        v = j / NV2; row, frow = [], []
        for i in range(NU2 + 1):
            u = i / NU2; half = 0.24 * (1 - 0.1 * v) - 0.17 * sm((v - 0.72) / 0.28)
            x = 0.42 + 0.14 * v + (u - 0.5) * 2 * half; fd = math.sin(u * math.pi * 3 + v * 2); d = 0.025 * fd * sm(v / 0.5)
            row.append(Vector((x, -0.70 - 0.03 * (1 - (2 * u - 1) ** 2) + 0.10 * v + d, -0.16 - 0.72 * v))); frow.append(fd)
        g2.append(row); f2.append(frow)
    rect, vr, hfrac = iso_rect(g2, 0.0, 0.25, tail_top, 1024)
    b.sheet(g2, 0.04, rect, "navy", rim="navy", normal_hint=lambda p: Vector((0, -1, 0)), fold=f2, key="tail", v_rows=vr)
    # clasp: gold disc on the front + small crystal
    b.extrude([(0.12 * math.cos(k * math.pi / 4), 0.12 * math.sin(k * math.pi / 4)) for k in range(8)], Vector((0.30, -0.76, -0.10)),
              Vector((1, 0, 0)), Vector((0, 0, 1)), 0.05, 0.015, "gold")
    bipyramid(b, Vector((0.30, -0.80, -0.18)), Vector((0, -0.2, 1)), 0.05, 0.17, 4)
    ob = b.finish(); tex_material(ob.data, "cv_scarf"); return ob


# ------------------------------------------------------------------ SWORD (WaistBackAttachment), built from the 28-part blockout GLB
GROUPS = {   # blockout part-name keyword -> (texture band, shading mode)
    "Crystal_Blade": "blade", "Blade_Core": "core", "Blue_Blade_Base": "sapphire", "Blade_Base_Socket": "gold", "Guard_Center_Gold": "gold",
    "Guard_Center_Blue": "navy", "Guard_Center_Crystal": "crystal", "Gold_Wing": "gold", "Blue_Spike": "sapphire", "Right_Gem": "crystal", "Left_Gem": "crystal",
    "Grip_Core": "navy", "Grip_Wrap": "wrap", "Collar": "gold", "Pommel_Gold": "gold", "Pommel_Crystal": "crystal"}
BANDS = ["blade", "core", "gold", "sapphire", "navy", "crystal", "wrap"]      # 7 bands, each 1/8 of the atlas height (band k: v in [k/8, (k+1)/8]); band 7 = swatch cell


def build_sword():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=GLB)
    new = [o for o in bpy.data.objects if o not in before]
    parts = [o for o in new if o.type == "MESH"]
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); n_in = 0
    # rotation x,y,z(world, blockout: length along -y) -> local (x, depth, L): (x, z, -y)
    for o in sorted(parts, key=lambda o: o.name):
        grp = next((v for k, v in GROUPS.items() if k in o.name), None)
        if grp is None: raise RuntimeError("unmapped blockout part " + o.name)
        if grp in ("blade",): continue                  # replaced by the refined blade below
        me = o.data.copy(); me.transform(o.matrix_world); me.transform(Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))))
        tmp = bmesh.new(); tmp.from_mesh(me); bmesh.ops.remove_doubles(tmp, verts=tmp.verts[:], dist=1e-5)
        # refine: bevel the sharp edges of gold/navy parts slightly so highlights catch (bevel only on larger parts)
        if grp in ("gold",) and len(tmp.faces) > 6:
            bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=0.012, segments=1, affect="EDGES")
        n_in += 1
        vmap = {v.index: bm.verts.new(v.co) for v in (tmp.verts.ensure_lookup_table() or tmp.verts)}   # r11: shared verts -> closed shells
        for f in tmp.faces:
            n = f.normal; ctr = f.calc_center_median()
            vs = [vmap[v.index] for v in f.verts]
            try: nf = bm.faces.new(vs)
            except ValueError: continue
            # facet shading u: normal dot light direction; v band centre
            u = 0.5 + 0.42 * n.dot(Vector((-0.5, -0.6, 0.62)).normalized()); band = BANDS.index(grp)
            if grp == "wrap": u = 0.5 + 0.4 * math.sin(ctr.z * 60)       # alternating blue rings
            for lp in nf.loops: lp[uvl].uv = (min(0.98, max(0.02, u)), (band + 0.5) / 8)
        tmp.free()
    # refined blade: 10-gon cross sections with a central ridge, irregular crystal facets and notch steps (blockout: 8-gon, 4 stations)
    ST = [(1.40, .22, .085), (1.62, .29, .115), (1.95, .305, .125), (2.10, .27, .12), (2.36, .295, .12), (2.58, .27, .113), (2.82, .25, .11),
          (3.12, .22, .095), (3.40, .19, .08), (3.66, .13, .06), (3.90, .07, .03)]
    rings = []
    for k, (L, w, t) in enumerate(ST):
        jit = 1 + 0.06 * math.sin(k * 2.3); jx = 0.012 * math.sin(k * 1.7)
        pts = [(jx, t), (0.52 * w * jit, 0.6 * t), (0.96 * w, 0.07 * t), (0.96 * w, -0.07 * t), (0.52 * w * jit, -0.6 * t), (jx, -t),
               (-0.52 * w / jit, -0.6 * t), (-0.96 * w, -0.07 * t), (-0.96 * w, 0.07 * t), (-0.52 * w / jit, 0.6 * t)]
        rings.append([bm.verts.new((px, pz, L)) for px, pz in pts])
    tipv = bm.verts.new((0, 0, 4.12)); N = 10
    def addf(vs, shade):
        f = bm.faces.new(vs)
        for lp in f.loops:                                   # r15: v runs along the blade (1.4 -> 4.12) inside the blade band so facets/streaks can be painted
            lp[uvl].uv = (min(0.98, max(0.02, shade)), (0.08 + 0.84 * min(1.0, max(0.0, (lp.vert.co.z - 1.4) / 2.72))) / 8)
    for r in range(len(rings) - 1):
        for k in range(N):
            k2 = (k + 1) % N; sh = [0.92, 0.7, 0.3, 0.15, 0.4, 0.97, 0.9, 0.3, 0.12, 0.45][k] + 0.03 * math.sin(r * 1.7)
            addf([rings[r][k], rings[r][k2], rings[r + 1][k2], rings[r + 1][k]][::-1] if False else [rings[r][k2], rings[r][k], rings[r + 1][k], rings[r + 1][k2]], sh)
    addf(rings[0][::-1], 0.5)                       # r10: close the blade base (watertight)
    for k in range(N):
        k2 = (k + 1) % N; addf([rings[-1][k2], rings[-1][k], tipv], [0.92, 0.7, 0.3, 0.15, 0.4, 0.97, 0.9, 0.3, 0.12, 0.45][k])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("cv_sword"); bm.to_mesh(me); bm.free()
    for o in new: bpy.data.objects.remove(o)       # drops the imported meshes and the glTF empties
    ob = bpy.data.objects.new("cv_sword", me); bpy.context.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = False
    tex_material(me, "cv_sword")
    print("sword parts used", n_in)
    return ob


def place_sword(ob):
    """wearable pose: pommel low on the back (WaistBackAttachment frame is the export origin), blade rising diagonally over the right shoulder, hilt tilted back to follow the cape flare"""
    R = Matrix.Rotation(math.radians(-36), 3, "Y") @ Matrix.Rotation(math.radians(18), 3, "X"); sc = 0.80
    P0 = Vector((0.80, 1.85, -2.95))   # r18: RotX +18 deg (blade forward over the shoulder, pommel back near the flared hem) + y 1.85: lies along the long cape's flare, clip_check.py 0 overlaps (the r10 pose y 1.40 cut through the cape folds)
    ob.data.transform(Matrix.Translation(P0) @ (R.to_4x4() @ Matrix.Scale(sc, 4)))
    # r10: Waist box (Slender) allows only 1.414 up from WaistBackAttachment (z -2.098): drop the sword so its top is 1.36 up
    ztop = max(v.co.z for v in ob.data.vertices); dz = min(0.0, (-2.098 + 1.36) - ztop)
    ob.data.transform(Matrix.Translation((0, 0, dz))); print("sword lowered", round(dz, 3))


def bake_ao(ob, size, others, samples=24):
    """Cycles AO bake into the item's UV atlas -> out/ao_<item>.png (same recipe as tidewatch build_v5.py; world distance 0.45 = local occlusion)"""
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
    sh = bpy.data.images.load(shirt_png); pa = bpy.data.images.load(pants_png)
    P = {"t": B.SHIRT["t"], "rl": B.SHIRT["ra"], "ll": B.SHIRT["la"]}
    objs = [B.tbox("torso", (2, 1, 2.1), (0, 0, -1.05), B.SHIRT["t"], sh), B.tbox("armR", (1, 1, 2.1), (-1.5, 0, -1.05), B.SHIRT["ra"], sh),
            B.tbox("armL", (1, 1, 2.1), (1.5, 0, -1.05), B.SHIRT["la"], sh), B.tbox("legR", (1, 1, 2.19), (-0.5, 0, -3.195), P["rl"], pa),
            B.tbox("legL", (1, 1, 2.19), (0.5, 0, -3.195), P["ll"], pa)]
    bpy.ops.mesh.primitive_cube_add(size=1); hd = bpy.context.object; hd.name = "head"; hd.scale = (1.16, 1.16, 1.18); hd.location = (0, 0, HC)
    bv = hd.modifiers.new("b", "BEVEL"); bv.width = 0.14; bv.segments = 3
    m = bpy.data.materials.new("skin"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.55, 0.42, 1)
    hd.data.materials.append(m)
    # r10: face decal (make_face_cv.py) on a plane just in front of the head's front face
    fp = os.path.join(OUT, "cv_face.png")
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
    crown = build_crown(); r = build_pauldron(); cape = build_cape(); scarf = build_scarf(); sword = build_sword()
    disp = sword.copy(); disp.data = sword.data.copy(); disp.name = "cv_sword_display"; bpy.context.collection.objects.link(disp); disp.data.transform(Matrix.Translation((0, 0, -2.0))); disp.hide_render = True
    place_sword(sword)
    l = r.copy(); l.data = r.data.copy(); l.name = "cv_pauldron_l"; bpy.context.collection.objects.link(l)
    l.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); l.data.flip_normals()
    r.location = (-1.5, 0, 0); l.location = (1.5, 0, 0)
    body_proxy(os.path.join(OUT, "cv_shirt.png"), os.path.join(OUT, "cv_pants.png"))
    for o in (crown, r, l, cape, scarf, sword): print("ITEM", o.name, "tris", tris(o))
    for it, regs in B.META.items():
        for k, s in regs.items():
            if isinstance(s, dict) and "rect" in s and "pos" in s: print("UVRECT", it, k, tuple(round(x, 3) for x in s["rect"]))
    import json, time
    with open(os.path.join(OUT, "meta.json"), "w") as fh: json.dump(B.META, fh)     # UV regions + positions + edge distances for paint_cv.py
    if os.environ.get("NOBAKE") != "1":                                              # r11: per-item AO (NOBAKE=1 skips, textures then have no AO)
        items = [o for o in (crown, r, cape, scarf) if o.name in B.META]; t0 = time.time()
        for o in items: bake_ao(o, 1024 if o.name in ('cv_pauldron_r', 'cv_cape') else 512, [x for x in (crown, r, l, cape, scarf, sword, disp) if x is not o])
        print("AO baked", [o.name for o in items], "in %.1fs" % (time.time() - t0))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cv_build.blend")); print("DONE")

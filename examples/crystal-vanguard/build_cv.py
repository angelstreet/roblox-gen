"""Crystal Vanguard - accessories (crown+hair, pauldron R/L, cape, scarf, sword) built in Blender.
Run: Blender -b -P build_cv.py   (after make_clothing_cv.py and paint_cv.py has NOT to run first: textures are loaded lazily by render_cv.py)
Frame (same as tidewatch): x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment.
Writes out/cv_build.blend. UV layout: every non-sword item uses an 8-swatch strip at the bottom of its atlas (v 0..0.06)."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_v5 as B
from build_v5 import Builder, sm, spow

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
    b = Builder("cv_crown"); rnd = random.Random(11)
    # --- hair cap: superellipsoid dome, hem higher at the front (forehead fringe), lower at the back
    NU, NV, E = 36, 8, 3.2; R = 0.71
    def hem_z(phi):   # phi=0 front(-y). hem height above head centre
        c = math.cos(phi); return HC + (0.26 if c > 0 else -0.28) * abs(c) ** 0.7 * (1 if c > 0 else 1) + (0.0 if c > 0 else 0) - (0.0)
    grid = []
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            phi = 2 * math.pi * i / NU
            hz = HC + 0.30 * max(0, math.cos(phi)) - 0.30 * max(0, -math.cos(phi)) - 0.06 * abs(math.sin(phi)) * 0 - 0.1 * abs(math.sin(phi))
            cz = max(-0.2, min(0.97, (hz - HC) / R)); th_max = math.acos(cz)
            th = th_max * v
            n = 0.025 * math.sin(7 * phi + 1.3) * sm(v * 1.4)
            x = (R + n) * spow(math.sin(th), 2 / E) * spow(math.sin(phi), 2 / E)
            y = -(R + n) * spow(math.sin(th), 2 / E) * spow(math.cos(phi), 2 / E)
            z = HC + (R + 0.02) * spow(math.cos(th), 2 / E)
            row.append(Vector((x, y, z)) if j else Vector((0, 0, HC + R + 0.02)))
        grid.append(row)
    b.sheet(grid, 0.035, cell("white"), "silver", rim="silver", closed_u=True, pole_row0=True,
            normal_hint=lambda p: Vector((p.x, p.y, p.z - HC)))
    # --- hair spikes (tufts) on the dome
    def dome(phi, th, r=R + 0.02):
        return Vector((r * spow(math.sin(th), .5) * spow(math.sin(phi), .5), -r * spow(math.sin(th), .5) * spow(math.cos(phi), .5), HC + r * spow(math.cos(th), .5)))
    # r10: swept mane made of CLOSED tapered strands (5-gon rings + capped base -> watertight), four groups.
    # Hair box (Rthro Slender/Normal, attachment = HC + 0.635): |x| <= 0.89, behind <= 1.19, front <= 0.94 -> keep x 0.86, y -0.90..1.15.
    AZ = HC + 0.635; XMAX, YBACK, YFRONT = 0.86, 1.15, -0.90
    def strand(path, w0, sw, sides=5):
        """path: list of points base..tip (>= 3); ring radius tapers from w0 to 0 at the tip; base ring capped"""
        path = [Vector((max(-XMAX, min(XMAX, p.x)), max(YFRONT, min(YBACK, p.y)), p.z)) for p in path]
        rings = []
        for k, c in enumerate(path[:-1]):
            d = (path[k + 1] - c).normalized() if k == 0 else (path[k + 1] - path[k - 1]).normalized()
            t = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))).normalized(); s2 = d.cross(t)
            w = w0 * (1 - k / (len(path) - 1)) ** 0.8
            rings.append([b.bm.verts.new(c + (t * math.cos(2 * math.pi * q / sides) * 1.35 + s2 * math.sin(2 * math.pi * q / sides) * 0.75) * w) for q in range(sides)])
        tip = b.bm.verts.new(path[-1]); uv = [B.SW[sw]] * 4
        b.flat_mode = 1
        b.face(rings[0][::-1], [B.SW[sw]] * sides)                               # base cap
        for r0, r1 in zip(rings[:-1], rings[1:]):
            for q in range(sides):
                q2 = (q + 1) % sides; b.face([r0[q], r0[q2], r1[q2], r1[q]], uv)
        for q in range(sides):
            b.face([rings[-1][q], rings[-1][(q + 1) % sides], tip], uv[:3])
        b.flat_mode = 0
    def bez(p0, p1, p2, n=3):
        return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (k / n for k in range(n + 1))]
    cols = ("white", "silver", "ice", "white", "silver")
    # 1) crown of swept-up spikes on the top (concept: spiky white hair rising above the band, sweeping back)
    for k in range(28):
        phi = rnd.uniform(-math.pi, math.pi); th = rnd.uniform(0.05, 0.85)
        base = dome(phi, th, R * 0.97); out = (base - Vector((0, 0, HC))).normalized()
        L = rnd.uniform(0.38, 0.62) * (1.1 if math.cos(phi) > 0 else 0.95)
        mid = base + out * L * 0.45 + Vector((rnd.uniform(-.06, .06), 0.10, 0.22)) * L * 2
        tip = mid + Vector((out.x * 0.15, 0.30 + 0.1 * rnd.random(), 0.12)) * L * 1.6
        strand(bez(base - out * 0.04, mid, tip), rnd.uniform(0.07, 0.10), cols[k % 5])
    # 2) back mane: spiky layered locks that follow the back of the head down to the nape; tips flick outward and up
    #    (staggered lengths, varied side angle) so the back reads as separate spikes, not a curtain
    for k in range(20):
        side = (k % 5 - 2) / 2.0 + rnd.uniform(-.15, .15)                      # -1..1 across the back
        phi = math.pi - side * 1.1; th = rnd.uniform(0.5, 1.25) if k < 10 else rnd.uniform(1.05, 1.45)
        base = dome(phi, th, R * 0.96)
        zt = HC - (rnd.uniform(0.05, 0.25) if k < 10 else rnd.uniform(0.30, 0.55))
        yb = min(YBACK - 0.02, 0.74 + 0.22 * (1 - abs(side)) + rnd.uniform(0, .12))
        mid = Vector((base.x * 1.1 - side * 0.05, yb, (base.z + zt) / 2 + 0.05))
        tip = Vector((base.x * 1.05 - side * 0.22, yb + 0.02, zt))
        strand(bez(base, mid, tip), rnd.uniform(0.08, 0.115), cols[(k + 2) % 5])
    # 3) side locks: thin, set behind the temple so the face stays clear, ending at cheek height
    for sg in (-1, 1):
        for k in range(2):
            phi = sg * math.radians(100 + 12 * k); base = dome(phi, rnd.uniform(1.0, 1.25), R * 0.96)
            tip = Vector((sg * 0.69, base.y + 0.08, HC - 0.12 - 0.08 * k))
            mid = Vector((sg * 0.78, (base.y + tip.y) / 2, (base.z + tip.z) / 2 + 0.05))
            strand(bez(base, mid, tip), 0.065, cols[k % 5])
    # 4) fringe: short spikes poking out under the band over the forehead (eyes at HC+0.04 stay clear)
    for k, ang in enumerate((-38, -18, 0, 16, 34)):
        a = math.radians(ang); base = Vector((0.62 * math.sin(a), -0.62 * math.cos(a), HC + 0.47))
        tip = Vector((0.66 * math.sin(a) + 0.05 * (1 if ang >= 0 else -1), -0.67 * math.cos(a), HC + rnd.uniform(0.22, 0.30)))
        strand(bez(base, (base + tip) / 2 + Vector((0, -0.05, 0)), tip), 0.075, cols[k % 5])
    # --- gold band (closed ring of 2 rows) around the forehead + rim
    zb0, zb1 = HC + 0.40, HC + 0.56; NUb = 40
    g = []
    for z in (zb1, zb1 - 0.04, zb0 + 0.04, zb0):
        row = []
        for i in range(NUb + 1):
            phi = 2 * math.pi * i / NUb; r = 0.70 + (0.02 if z in (zb1, zb0) else 0)
            row.append(Vector((r * spow(math.sin(phi), 0.5) * 0.99, -r * spow(math.cos(phi), 0.5), z - 0.0)))
        g.append(row)
    b.sheet(g, 0.03, cell("gold"), "gold_dark", rim="gold_dark", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)))
    # small blue gems on the band
    for ang in (0, 55, -55, 115, -115):
        a = math.radians(ang); c = Vector((0.73 * math.sin(a), -0.72 * math.cos(a), (zb0 + zb1) / 2))
        b.gem(c, 0.05, 0.065, Vector((math.sin(a), -math.cos(a), 0)), "crystal")
    # --- crystal crown spikes on the band
    zt = zb1 - 0.02
    spec = [(0, .62), (28, .44), (-28, .44), (56, .36), (-56, .36), (88, .30), (-88, .30), (125, .30), (-125, .30), (160, .32), (-160, .32), (180, .38)]
    for ang, hh in spec:
        a = math.radians(ang); r = 0.71
        base = Vector((r * math.sin(a), -r * math.cos(a), zt)); out = Vector((math.sin(a), -math.cos(a), 0))
        axis = (Vector((0, 0, 1)) + out * 0.16).normalized()
        bipyramid(b, base, axis, 0.085 + 0.1 * hh * 0.4 + (0.03 if ang == 0 else 0), hh, 6)
    # r10: temple wings removed (they made the item 2.24 wide; Hair limit 1.78)
    ob = b.finish(); tex_material(ob.data, "cv_crown"); return ob


# ------------------------------------------------------------------ PAULDRON (Right/LeftShoulderAttachment)
def build_pauldron():
    """r2: 3 separate layered plates (gap between tiers shows a navy underlayer), sharp gold rim ring on each tier, big gem in a gold frame."""
    b = Builder("cv_pauldron_r"); E = 4.0
    # (z_top, z_bottom, half_x, half_y, texture v0, v1)  -- visible gaps 0.10 between tiers, each lower tier wider
    tiers = [(0.26, -0.28, 0.66, 0.66, 0.70, 1.00), (-0.40, -0.74, 0.70, 0.70, 0.45, 0.68), (-0.86, -1.18, 0.78, 0.78, 0.20, 0.43)]
    NU = 26
    # navy underlayer (visible in the gaps)
    g = []
    for z in (-0.10, -0.55, -1.05, -1.18):
        g.append([Vector((0.58 * spow(math.sin(2 * math.pi * i / NU), 2 / E), 0.58 * spow(math.cos(2 * math.pi * i / NU), 2 / E), z)) for i in range(NU + 1)])
    b.sheet(g, 0.05, cell("navy"), "navy", rim="navy", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)))
    def rim_ring(z, hx, hy, zs=0.0, arc=None, pt=0.0):
        """sharp gold rim: 3-row ring, protrudes 0.05 beyond the plate, pointed at the outer side"""
        g = []
        for dz, dr in ((0.07, 0.0), (0.0, 0.055), (-0.04, 0.045)):
            row = []
            for i in range(NU + 1):
                if arc: phi = math.radians(arc[0]) + math.radians(arc[1]) * i / NU
                else: phi = 2 * math.pi * i / NU
                s, c = math.sin(phi), math.cos(phi); inner = sm((s + 0.2) / 1.2) if arc is None else 0
                zz = z + dz - (0.05 + 0.35 * inner) * 0 - pt * max(0, -s) ** 3
                if arc is None: zz = z + dz + (0.05 - z) * 0 - 0.0
                row.append(Vector(((hx + dr) * spow(s, 2 / E), (hy + dr) * spow(c, 2 / E), zz)))
            g.append(row)
        b.sheet(g, 0.03, cell("gold"), "gold_dark", rim="gold", closed_u=(arc is None), normal_hint=lambda p: Vector((p.x, p.y, 0)))
    for k, (zt, zb, hx, hy, v0, v1) in enumerate(tiers):
        grid = []
        if k == 0:
            NV = 12
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
                    if v < 0.45:
                        t = v / 0.45; r = math.sin(t * math.pi / 2); z = zt - 0.10 * (1 - math.cos(t * math.pi / 2))
                    else:
                        t = (v - 0.45) / 0.55; r = 1.0 + 0.04 * t; z = (zt - 0.10) + (zb - (zt - 0.10)) * t
                    p = Vector((hx * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z))
                    row.append(p if j else Vector((0, 0, zt)))
                grid.append(row)
            b.sheet(grid, 0.07, (0.0, v0, 0.6, v1), "silver", rim="silver", closed_u=True, pole_row0=True, normal_hint=lambda p: Vector((p.x, p.y, p.z + 0.3)))
            rim_ring(zb, hx * 1.04, hy * 1.04)
        else:
            NV = 5
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = math.radians(205) + math.radians(310) * i / NU; s, c = math.sin(phi), math.cos(phi)
                    z = zt + (zb - zt) * v; r = 0.90 + 0.14 * math.sin(v * math.pi / 2)
                    pt = 0.20 * max(0, -s) ** 3 * v
                    row.append(Vector((hx * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z - pt)))
                grid.append(row)
            b.sheet(grid, 0.06, (0.0, v0, 0.6, v1), "silver", rim="silver", normal_hint=lambda p: Vector((p.x, p.y, 0)))
            rim_ring(zb, hx * 1.04, hy * 1.04, arc=(205, 310), pt=0.20)
    # big gem in a gold diamond frame on the outer face of the middle tier
    cen = Vector((-0.80, -0.02, -0.57))
    b.extrude([(0, 0.40), (0.26, 0), (0, -0.40), (-0.26, 0)], Vector((-0.74, -0.02, -0.57)), Vector((0, 1, 0)), Vector((0, 0, 1)), 0.07, 0.02, "gold")
    b.gem(cen + Vector((-0.04, 0, 0)), 0.17, 0.30, Vector((-1, -0.05, 0)), "crystal")
    for dx, hh, tilt in ((-0.26, 0.40, -0.25), (0.0, 0.34, 0.0), (0.24, 0.28, 0.2)):
        bipyramid(b, Vector((dx * 0.8 - 0.05, 0.05, 0.1)), Vector((tilt * 0.6, 0.15, 1.0)), 0.07, hh, 6)
    ob = b.finish(); tex_material(ob.data, "cv_pauldron_r"); return ob


# ------------------------------------------------------------------ CAPE (BodyBackAttachment) + fur collar
def build_cape():
    b = Builder("cv_cape"); NU, NV = 28, 26; grid = []
    # r10: long flowing cape like the concept (hem near the ankles), flared back so the run back-kick only grazes it.
    # Back box (Slender): 3.95 down / 2.886 behind BodyBackAttachment (0, 0.502, -1.061) -> lowest point -3.95 is 2.9 down.
    top_w, bot_w, z0, z1, y0, flare = 1.50, 2.55, -0.30, -3.70, 0.60, 1.15
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.15)
            scal = -0.20 * (1 - abs(math.sin(u * math.pi * 6))) * sm((v - 0.85) / 0.15)
            ctr = -0.25 * max(0, 1 - abs(2 * u - 1) * 4.5) * sm((v - 0.85) / 0.15)    # long centre point
            z = z0 + (z1 - z0) * v + scal + ctr
            wrap = 0.26 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2
            ph = (u - 0.5) * 2 * math.pi * 3.5 * (1 + 0.25 * v) + 0.5
            d = 0.09 * math.sin(ph) * (0.15 + 0.85 * v ** 1.3)
            y = y0 + flare * v ** 1.8 - wrap + d + 0.14 * (2 * (u - 0.5)) ** 2 * v
            row.append(Vector((x, y, z)))
        grid.append(row)
    b.sheet(grid, 0.03, (0, 0.08, 1, 1), "navy", rim="gold", normal_hint=lambda p: Vector((0, 1, 0)))
    # fur-like collar: back half of a thick ring over the shoulders
    gc = []; NU2 = 24
    for j, (z, rx, ry, th) in enumerate(((0.28, 0.80, 0.60, 0.0), (0.14, 0.98, 0.72, 0.06), (-0.10, 1.12, 0.80, 0.08), (-0.38, 1.10, 0.84, 0.0))):
        row = []
        for i in range(NU2 + 1):
            phi = math.radians(-100 + 200 * i / NU2); lump = 0.035 * math.sin(i * 1.9 + j) * (1 if 0 < j < 3 else 0)
            # r3: collar scaled to 0.7 in x/y and 0.75 in z (was a big block), thinner shell
            row.append(Vector(((rx + lump) * 0.7 * math.sin(phi), (ry + lump) * 0.7 * math.cos(phi), z * 0.75)))
        gc.append(row)
    b.sheet(gc, 0.06, cell("white"), "silver", rim="silver", normal_hint=lambda p: Vector((p.x, p.y, 0.1)))
    # gem clasp holders at the front of the collar ends (moved in with the smaller collar)
    for sg in (-1, 1):
        b.gem(Vector((sg * 0.65, 0.02, -0.09)), 0.05, 0.07, Vector((sg, -0.5, 0.0)), "crystal")
    ob = b.finish(); tex_material(ob.data, "cv_cape"); return ob


# ------------------------------------------------------------------ SCARF (NeckAttachment)
def build_scarf():
    """r4: small neat neck scarf (ring around the head base, sits on the shoulders), short tail on the chest, gold clasp + small gem."""
    b = Builder("cv_scarf"); NU = 32; grid = []
    rows = [(0.34, 0.62, 0.60), (0.24, 0.67, 0.64), (0.10, 0.76, 0.68), (-0.02, 0.84, 0.72), (-0.07, 0.84, 0.72)]
    for j, (z, rx, ry) in enumerate(rows):
        row = []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
            d = 0.02 * math.sin(8 * phi + 0.4) * (0.3 + j / 5)
            row.append(Vector(((rx + d) * spow(s, 2 / 3.0), -(ry + d) * spow(c, 2 / 3.0), z)))
        grid.append(row)
    b.sheet(grid, 0.04, (0, 0.36, 1, 1), "navy", rim="navy", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0.1)))
    # short tail, off-centre to the left of the clasp, lying on the chest
    NU2, NV2 = 4, 6; g2 = []
    for j in range(NV2 + 1):
        v = j / NV2; row = []
        for i in range(NU2 + 1):
            u = i / NU2; half = 0.13 * (1 - 0.35 * v)
            row.append(Vector((0.22 + (u - 0.5) * 2 * half, -0.74 + 0.17 * v - 0.0, 0.02 - 0.62 * v)))
        g2.append(row)
    b.sheet(g2, 0.03, (0, 0.36, 1, 1), "navy", rim="gold", normal_hint=lambda p: Vector((0, -1, 0)))
    # clasp: gold disc on the front of the ring + small crystal
    b.extrude([(0.11 * math.cos(k * math.pi / 4), 0.11 * math.sin(k * math.pi / 4)) for k in range(8)], Vector((0, -0.745, 0.12)),
              Vector((1, 0, 0)), Vector((0, 0, 1)), 0.05, 0.015, "gold")
    bipyramid(b, Vector((0, -0.79, 0.12 - 0.08)), Vector((0, -0.2, 1)), 0.05, 0.17, 4)
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
        tmp = bmesh.new(); tmp.from_mesh(me)
        # refine: bevel the sharp edges of gold/navy parts slightly so highlights catch (bevel only on larger parts)
        if grp in ("gold",) and len(tmp.faces) > 6:
            bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=0.012, segments=1, affect="EDGES")
        n_in += 1
        ib = {}
        for f in tmp.faces:
            n = f.normal; ctr = f.calc_center_median()
            vs = [bm.verts.new(v.co) for v in f.verts]
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
        for lp in f.loops: lp[uvl].uv = (min(0.98, max(0.02, shade)), 0.5 / 8)
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
    """wearable pose: pommel low on the back (WaistBackAttachment frame is the export origin), blade rising diagonally over the right shoulder"""
    R = Matrix.Rotation(math.radians(-36), 3, "Y") @ Matrix.Rotation(math.radians(6.5), 3, "X"); sc = 0.80
    P0 = Vector((0.80, 1.40, -2.95))   # r7: y 1.95 -> 1.80 (closer to the smaller cape; 0 BVH overlaps, see clip_check.py)
    ob.data.transform(Matrix.Translation(P0) @ (R.to_4x4() @ Matrix.Scale(sc, 4)))
    # r10: Waist box (Slender) allows only 1.414 up from WaistBackAttachment (z -2.098): drop the sword so its top is 1.36 up
    ztop = max(v.co.z for v in ob.data.vertices); dz = min(0.0, (-2.098 + 1.36) - ztop)
    ob.data.transform(Matrix.Translation((0, 0, dz))); print("sword lowered", round(dz, 3))


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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cv_build.blend")); print("DONE")

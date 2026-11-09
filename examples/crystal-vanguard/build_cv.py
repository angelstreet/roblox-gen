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
    NU, NV, E = 36, 8, 4.0; R = 0.71
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
    for k in range(46):
        phi = rnd.uniform(0, 2 * math.pi) if k < 26 else rnd.uniform(0.5 * math.pi, 1.5 * math.pi); th = rnd.uniform(0.2, 1.15) if k < 26 else rnd.uniform(0.7, 1.7)
        if math.cos(phi) > 0.2 and th > 0.95: th = 0.9
        base = dome(phi, th, R * 0.98); out = (base - Vector((0, 0, HC))).normalized()
        d = (out + Vector((0, 0.35, 0.55)) + Vector((rnd.uniform(-.25, .25), rnd.uniform(-.2, .2), rnd.uniform(0, .3)))).normalized()
        hgt = rnd.uniform(0.28, 0.5) * (1.1 if th < 0.6 else 0.9) * (1.5 if k >= 26 else 1.0); wd = rnd.uniform(0.07, 0.11)
        t = d.cross(Vector((0, 0, 1))).normalized(); s = d.cross(t); sw = ("silver", "white", "ice")[k % 3]
        ring = [b.bm.verts.new(base - d * 0.03 + (t * math.cos(a) + s * math.sin(a)) * wd) for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
        tip = b.bm.verts.new(base + d * hgt + Vector((0, 0.05, 0.0)))
        b.flat_mode = 1
        for q in range(4): b.face([ring[q], ring[(q + 1) % 4], tip], [B.SW[sw]] * 3)
        b.flat_mode = 0
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
    # temple wings: two angled crystals
    for sg in (-1, 1):
        base = Vector((sg * 0.70, -0.1, HC + 0.46)); bipyramid(b, base, Vector((sg * 0.8, -0.1, 0.5)), 0.07, 0.5, 6)
    ob = b.finish(); tex_material(ob.data, "cv_crown"); return ob


# ------------------------------------------------------------------ PAULDRON (Right/LeftShoulderAttachment)
def build_pauldron():
    b = Builder("cv_pauldron_r"); E = 4.0
    tiers = [(0.26, -0.42, 0.66, 0.66, True, 0.70, 1.00), (-0.18, -0.76, 0.76, 0.74, False, 0.45, 0.68), (-0.50, -1.08, 0.84, 0.80, False, 0.20, 0.43)]
    for k, (zt, zh, hx, hy, top, v0, v1) in enumerate(tiers):
        NU = 30; grid = []
        if top:
            NV = 12
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi); inner = sm((s + 0.2) / 1.2)
                    if v < 0.4:
                        t = v / 0.4; r = math.sin(t * math.pi / 2); z = zt - 0.17 * (1 - math.cos(t * math.pi / 2))
                    else:
                        t = (v - 0.4) / 0.6; r = 1.0 + 0.05 * t; zb = zh + (0.05 - zh) * inner ** 1.5; z = (zt - 0.17) + (zb - (zt - 0.17)) * t
                    p = Vector((hx * (1 - 0.18 * inner) * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z))
                    row.append(p if j else Vector((0, 0, zt)))
                grid.append(row)
            b.sheet(grid, 0.06, (0.0, v0, 0.6, v1), "silver", rim="gold", closed_u=True, pole_row0=True, normal_hint=lambda p: Vector((p.x, p.y, p.z + 0.3)))
        else:
            NV = 6
            for j in range(NV + 1):
                v = j / NV; row = []
                for i in range(NU + 1):
                    phi = math.radians(205) + math.radians(310) * i / NU; s, c = math.sin(phi), math.cos(phi)
                    z = zt + (zh - zt) * v; r = 0.80 + 0.20 * math.sin(v * math.pi / 2)
                    # pointed hem at the outer side: plates flare into a point
                    pt = 0.16 * max(0, -s) ** 3 * v
                    row.append(Vector((hx * r * spow(s, 2 / E), hy * r * spow(c, 2 / E), z - pt)))
                grid.append(row)
            b.sheet(grid, 0.06, (0.0, v0, 0.6, v1), "silver", rim="gold", normal_hint=lambda p: Vector((p.x, p.y, 0)))
    # gem set in a gold diamond on the outer face, plus 3 crystal shards on top
    cen = Vector((-0.80, -0.02, -0.18))
    b.gem(cen, 0.10, 0.17, Vector((-1, -0.1, 0)), "crystal")
    for dx, hh, tilt in ((-0.28, 0.46, -0.25), (0.0, 0.38, 0.0), (0.25, 0.32, 0.2)):
        bipyramid(b, Vector((dx * 0.8 - 0.05, 0.05, 0.1)), Vector((tilt * 0.6, 0.15, 1.0)), 0.075, hh, 6)
    ob = b.finish(); tex_material(ob.data, "cv_pauldron_r"); return ob


# ------------------------------------------------------------------ CAPE (BodyBackAttachment) + fur collar
def build_cape():
    b = Builder("cv_cape"); NU, NV = 28, 26; grid = []
    top_w, bot_w, z0, z1, y0, flare = 1.95, 3.35, -0.30, -4.10, 0.60, 0.80
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.15)
            scal = -0.26 * (1 - abs(math.sin(u * math.pi * 6))) * sm((v - 0.85) / 0.15)
            ctr = -0.40 * max(0, 1 - abs(2 * u - 1) * 4.5) * sm((v - 0.85) / 0.15)    # long centre point
            z = z0 + (z1 - z0) * v + scal + ctr
            wrap = 0.26 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2
            ph = (u - 0.5) * 2 * math.pi * 3.5 * (1 + 0.25 * v) + 0.5
            d = 0.07 * math.sin(ph) * (0.15 + 0.85 * v ** 1.3)
            y = y0 + flare * v ** 1.5 - wrap + d + 0.14 * (2 * (u - 0.5)) ** 2 * v
            row.append(Vector((x, y, z)))
        grid.append(row)
    b.sheet(grid, 0.03, (0, 0.08, 1, 1), "navy", rim="gold", normal_hint=lambda p: Vector((0, 1, 0)))
    # fur-like collar: back half of a thick ring over the shoulders
    gc = []; NU2 = 24
    for j, (z, rx, ry, th) in enumerate(((0.28, 0.80, 0.60, 0.0), (0.14, 0.98, 0.72, 0.06), (-0.10, 1.12, 0.80, 0.08), (-0.38, 1.10, 0.84, 0.0))):
        row = []
        for i in range(NU2 + 1):
            phi = math.radians(-100 + 200 * i / NU2); lump = 0.035 * math.sin(i * 1.9 + j) * (1 if 0 < j < 3 else 0)
            row.append(Vector(((rx + lump) * math.sin(phi), (ry + lump) * math.cos(phi), z)))
        gc.append(row)
    b.sheet(gc, 0.10, cell("white"), "silver", rim="silver", normal_hint=lambda p: Vector((p.x, p.y, 0.1)))
    # gem clasp holders at the front of the collar ends
    for sg in (-1, 1):
        b.gem(Vector((sg * 0.93, 0.02, -0.12)), 0.06, 0.09, Vector((sg, -0.5, 0.0)), "crystal")
    ob = b.finish(); tex_material(ob.data, "cv_cape"); return ob


# ------------------------------------------------------------------ SCARF (NeckAttachment)
def build_scarf():
    b = Builder("cv_scarf"); NU = 40; grid = []
    rows = [(0.30, 0.66, 0.64), (0.22, 0.70, 0.66), (0.05, 0.80, 0.68), (-0.15, 0.92, 0.70), (-0.34, 1.04, 0.72), (-0.44, 1.08, 0.74)]
    for j, (z, rx, ry) in enumerate(rows):
        row = []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
            d = 0.025 * math.sin(10 * phi + 0.4) * (0.3 + j / 5) + (0.05 if j == 3 and abs(c) > 0.9 else 0)
            row.append(Vector(((rx + d) * spow(s, 2 / 3.0), -(ry + d) * spow(c, 2 / 3.0), z)))
        grid.append(row)
    b.sheet(grid, 0.04, (0, 0.36, 1, 1), "navy", rim="navy", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0.1)))
    # V front lappet hanging over the chest, gold edge
    NU2, NV2 = 6, 8; g2 = []
    for j in range(NV2 + 1):
        v = j / NV2; row = []
        for i in range(NU2 + 1):
            u = i / NU2; half = 0.40 * (1 - v) ** 0.9 + 0.03
            row.append(Vector(((u - 0.5) * 2 * half, -0.77 - 0.06 * v, -0.30 - 0.85 * v)))
        g2.append(row)
    b.sheet(g2, 0.03, (0, 0.36, 1, 1), "navy", rim="gold", normal_hint=lambda p: Vector((0, -1, 0)))
    # clasp: gold plate + big crystal
    b.extrude([(0.17 * math.cos(k * math.pi / 4), 0.17 * math.sin(k * math.pi / 4)) for k in range(8)], Vector((0, -0.78, -0.32)),
              Vector((1, 0, 0)), Vector((0, 0, 1)), 0.05, 0.015, "gold")
    bipyramid(b, Vector((0, -0.84, -0.32 - 0.13)), Vector((0, -0.2, 1)), 0.075, 0.30, 4)
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
    R = Matrix.Rotation(math.radians(-36), 3, "Y") @ Matrix.Rotation(math.radians(6.5), 3, "X"); sc = 0.85
    P0 = Vector((0.80, 1.30, -2.95))
    ob.data.transform(Matrix.Translation(P0) @ (R.to_4x4() @ Matrix.Scale(sc, 4)))


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
    # simple face: eyes + brows (dark quads) on the front of the head
    for sg in (-1, 1):
        for (dz, w, h) in ((0.04, 0.16, 0.14), (0.20, 0.2, 0.04)):
            bpy.ops.mesh.primitive_cube_add(size=1); e = bpy.context.object; e.scale = (w, 0.01, h); e.location = (sg * 0.22, -0.595, HC + dz)
            em = bpy.data.materials.new("eye"); em.use_nodes = True; em.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1); e.data.materials.append(em)
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

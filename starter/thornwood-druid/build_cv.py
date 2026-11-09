"""Thornwood Druid - accessories built in Blender (same frame and file layout as crystal-vanguard/build_cv.py).
Items (object names keep the cv_ prefix on purpose, see README "Make your own set"):
  cv_crown      antler crown (HatAttachment, submitted as Hair)  bone antlers, bark band, amber gems
  cv_pauldron_r/l  bark shoulder plates: three shingled curved plates with a splintered hem + moss leaf cluster (RightShoulder/LeftShoulder)
  cv_cape       moss mantle: short back mantle with leaf-lobed hem and hanging moss strands (BodyBackAttachment)
  cv_scarf      bone gorget: bark ring at the neck with a bone crest and an amber clasp (NeckAttachment)
  cv_sword      gnarled staff with a bone sickle head and amber crystal (WaistBackAttachment); the name is kept, it is a staff
Frame: x lateral (+x = character's left), y depth (front = -y), z up, 1 unit = 1 stud, origin = NeckAttachment.
Writes out/cv_build.blend. Every non-staff item uses an 8-swatch strip at the bottom of its atlas (v 0..0.06)."""
import bpy, bmesh, math, os, random, sys, json, time
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
import rgen_mesh as B
from rgen_mesh import Builder, sm, spow, iso_rect, tex_material, tris, bipyramid

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
HC = 0.576
# 8 swatch cells (u centre, v centre) -- painted by paint_cv.py (STRIP there must list the same order)
CELLS = ["bark", "moss", "amber", "bone", "leaf", "bark_dk", "bone_dk", "amber_dk"]
B.SW.clear()
for k, n in enumerate(CELLS): B.SW[n] = ((k + 0.5) / 8, 0.03)
B.SW.update({"bronze": B.SW["bark"], "pearl": B.SW["bone"], "aqua": B.SW["amber"], "dark": B.SW["bark_dk"], "gold": B.SW["amber"],
             "gold_dark": B.SW["amber_dk"], "navy": B.SW["bark_dk"], "crystal": B.SW["amber"], "silver": B.SW["bone"],
             "ice": B.SW["bone"], "sapphire": B.SW["moss"]})
def cell(n):                       # small rect inside a swatch cell (flat colour, for sheet()/tube() r_out)
    u = B.SW[n][0]; return (u - 0.05, 0.012, u + 0.05, 0.048)


def bez(p0, p1, p2, p3, n):
    return [p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3 for t in (k / n for k in range(n + 1))]


def tube(b, path, radii, sides=6, r_out=None, r_in="bark_dk", key=None, rim="bark_dk"):
    """closed tube along path (list of Vector centres) with radius per sample; a sheet with closed_u, open ends get rims.
    Returns the grid (for iso_rect) and the sheet's outer verts."""
    n = len(path); grid = []
    for j, c in enumerate(path):
        t = (path[min(j + 1, n - 1)] - path[max(j - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized(); bb = a.cross(t).normalized()
        grid.append([c + (a * math.cos(2 * math.pi * i / sides) + bb * math.sin(2 * math.pi * i / sides)) * radii[j] for i in range(sides + 1)])
    def hint(p):
        k = min(range(n), key=lambda q: (path[q] - p).length); return p - path[k]
    thick = min(radii) * 0.45
    if r_out is None: r_out = cell("bark")
    return b.sheet(grid, thick, r_out, r_in, rim=rim, closed_u=True, normal_hint=hint, key=key), grid


def leaf(b, base, d, up, L, W, curl=0.15, n=6):
    """lens-shaped leaf: rows along the length (NV=n), 3 columns across (margin rims), flat moss swatch, curled upward"""
    d = d.normalized(); side = d.cross(up).normalized(); nrm = side.cross(d).normalized()
    grid = []
    for j in range(n + 1):
        t = j / n; c = base + d * (t * L) + up * (curl * L * t * t); w = W * math.sin(math.pi * (0.04 + 0.92 * t)) ** 0.8
        grid.append([c + side * (-w), c, c + side * w])
    b.sheet(grid, 0.012, cell("leaf"), "moss", rim="moss", normal_hint=lambda p: nrm)


# ------------------------------------------------------------------ ANTLER CROWN (HatAttachment, submitted as Hair)
def build_crown():
    """antler crown: a bark circlet with three amber gems, two branching bone antlers (main beam + two tines each, closed tubes),
    amber crystal tips. The circlet is painted (key "band"); antlers and tips use flat bone/amber swatches (AO from the bake)."""
    b = Builder("cv_crown")
    NUb = 32; g = []
    for dz, dr in ((0.12, 0.0), (0.07, 0.025), (0.0, 0.02), (-0.05, 0.0)):
        row = []
        for i in range(NUb + 1):
            phi = 2 * math.pi * i / NUb
            row.append(Vector(((0.70 + dr) * math.sin(phi), -(0.66 + dr) * math.cos(phi), HC + 0.30 + dz)))
        g.append(row)
    rect, vr, _ = iso_rect(g, 0.0, 1.0, 0.92, 1024)
    b.sheet(g, 0.03, rect, "bark_dk", rim="bark_dk", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0)), key="band", v_rows=vr)
    for ang in (-34, 0, 34):                                          # amber gems on the front of the circlet
        a = math.radians(ang); c = Vector((0.70 * math.sin(a), -0.66 * math.cos(a), HC + 0.30 + 0.02))
        b.gem(c, 0.06, 0.08, Vector((math.sin(a), -math.cos(a), 0)), "amber")
    def CL(p): return Vector((max(-0.86, min(0.86, p.x)), max(-0.86, min(0.86, p.y)), p.z))
    tips = []
    for sg in (-1, 1):
        P0 = Vector((sg * 0.60, 0.00, HC + 0.30)); P1 = Vector((sg * 0.76, 0.02, HC + 0.60))
        P2 = Vector((sg * 0.84, 0.00, HC + 0.94)); P3 = Vector((sg * 0.74, -0.06, HC + 1.22))
        beam = [CL(p) for p in bez(P0, P1, P2, P3, 8)]
        radii = [0.115 - 0.065 * (k / 8) for k in range(9)]
        tube(b, beam, radii, sides=6, r_out=cell("bone"), r_in="bone_dk", rim="bone_dk")
        tips.append((beam[-1], (beam[-1] - beam[-2]).normalized()))
        for k, (dirv, L) in ((2, (Vector((sg * 0.20, -0.30, 1.0)), 0.40)), (4, (Vector((sg * 0.14, -0.18, 1.0)), 0.34)), (6, (Vector((sg * 0.08, -0.36, 1.0)), 0.30))):
            base = beam[k]; d = dirv.normalized()
            tine = [CL(base + d * (L * s / 4) + Vector((0, 0, 0.06 * (s / 4) ** 2 * L))) for s in range(5)]
            tube(b, tine, [0.065 - 0.035 * (s / 4) for s in range(5)], sides=6, r_out=cell("bone"), r_in="bone_dk", rim="bone_dk")
    for tip, d in tips:                                              # amber crystal on each beam tip
        b.gem(tip + d * 0.02, 0.035, 0.05, d, "amber")
    ob = b.finish(); tex_material(ob.data, "cv_crown"); return ob


# ------------------------------------------------------------------ BARK SHOULDER PLATES (Right/LeftShoulderAttachment)
def build_pauldron():
    """three shingled bark plates, each a curved arc (open on the torso side) with a splintered hem: the hem zig-zags with
    four teeth round the arc and the outer tip dips. Each lower plate is smaller and its teeth are staggered. A cluster of six
    moss leaves sits on the top plate, two bone spikes at the back, one amber gem on the outer face. Plates keep real UV regions
    (META "shell0..2") for the painter; the leaves and spikes use flat swatches."""
    b = Builder("cv_pauldron_r"); NU = 24; E = 2.4; A0, A1 = math.radians(130), math.radians(410)
    def tooth(f): return abs(((f * 4) % 1.0) * 2 - 1)                 # triangle wave, 4 teeth round the arc
    def inner_f(s): return sm((s + 0.15))
    tiers = [(0.36, -0.46, 0.92, 0.76, 0.22, 0.0), (-0.20, -0.60, 0.90, 0.74, 0.18, 0.5), (-0.62, -0.92, 0.82, 0.66, 0.14, 0.25)]
    top_v = 1.0; rects = []
    for k, (zt, zb, hx, hy, pt, ph) in enumerate(tiers):
        NV = 6; grid = []
        for j in range(NV + 1):
            v = j / NV; row = []
            for i in range(NU + 1):
                phi = A0 + (A1 - A0) * i / NU; s, c = math.sin(phi), math.cos(phi); inn = inner_f(s)
                zh = zb - 0.11 * tooth(i / NU + ph) - pt * max(0, -s) ** 3
                zh = zh + ((zt - 0.16) - zh) * inn ** 1.5                 # inner hem lifted clear of the torso
                z = zt + (zh - zt) * v - 0.05 * math.sin(math.pi * v)
                r = 1.0 + 0.09 * v
                row.append(Vector((hx * r * (1 - 0.30 * inn) * spow(s, 2 / E), hy * r * spow(c, 2 / E), z)))
            grid.append(row)
        rect, vr, _ = iso_rect(grid, 0.0, 1.0, top_v, 2048)
        b.sheet(grid, 0.05, rect, "bark_dk", rim="bark_dk", normal_hint=lambda p: Vector((p.x, p.y, 0.25)), key=f"shell{k}", v_rows=vr)
        rects.append(rect); top_v = rect[1] - 0.02
    assert top_v > 0.08, "pauldron atlas overflow (the strip needs v 0..0.06)"
    # moss leaf cluster on the outer top of the first plate
    for (base, d, L, W) in ((Vector((-0.30, -0.10, 0.34)), Vector((-0.55, -0.35, 0.55)), 0.46, 0.12),
                             (Vector((-0.42, 0.05, 0.36)), Vector((-0.72, 0.00, 0.40)), 0.44, 0.11),
                             (Vector((-0.40, 0.25, 0.33)), Vector((-0.60, 0.50, 0.38)), 0.40, 0.11),
                             (Vector((-0.20, 0.30, 0.34)), Vector((-0.20, 0.72, 0.42)), 0.42, 0.12),
                             (Vector((-0.10, -0.30, 0.36)), Vector((-0.10, -0.62, 0.42)), 0.40, 0.11),
                             (Vector((-0.30, -0.38, 0.30)), Vector((-0.46, -0.70, 0.36)), 0.36, 0.10)):
        leaf(b, base, d, Vector((0, 0, 1)), L, W, curl=0.25)
    # two bone spikes rising from the back of the top plate
    for dx, hh, tilt in ((-0.12, 0.44, 0.10), (-0.42, 0.34, -0.25)):
        bipyramid(b, Vector((dx, 0.46, 0.28)), Vector((tilt, 0.40, 1.0)), 0.065, hh, 6, swatches=("bone", "bone_dk", "bone", "bone_dk", "bone", "bone_dk"))
    # amber gem on the outer face of the top plate
    b.gem(Vector((-0.98, -0.02, -0.12)), 0.16, 0.26, Vector((-1, -0.05, 0)), "amber")
    ob = b.finish(); tex_material(ob.data, "cv_pauldron_r"); return ob


# ------------------------------------------------------------------ MOSS MANTLE (BodyBackAttachment)
def build_cape():
    """short back mantle: shoulder yoke at the neck, a flared body whose hem is seven leaf lobes, five hanging moss strands
    from the lobe tips. Outer face painted (key "outer"); lining = dark bark swatch."""
    b = Builder("cv_cape"); NU, NV = 28, 14; grid = []
    top_w, bot_w, z0, z1, y0, flare = 1.70, 2.40, -0.12, -2.55, 0.58, 0.95
    def lobe(u):
        tri = 1 - abs((u * 7 + 0.5) % 1.0 * 2 - 1)
        return -0.30 * tri ** 0.7
    for j in range(NV + 1):
        v = j / NV; row = []
        for i in range(NU + 1):
            u = i / NU; x = (u - 0.5) * (top_w + (bot_w - top_w) * v ** 1.1)
            z = z0 + (z1 - z0) * v + lobe(u) * sm((v - 0.80) / 0.20)
            wrap = 0.26 * (2 * (u - 0.5)) ** 2 * (1 - v) ** 2
            d = 0.05 * math.sin((u - 0.5) * 2 * math.pi * 4.0 + v * 2.0) * v
            y = y0 + flare * v ** 1.6 - wrap + d
            row.append(Vector((x, y, z)))
        grid.append(row)
    rect, vr, _ = iso_rect(grid, 0.0, 0.70, 1.0, 2048)   # u 0..0.7: full width overflowed the atlas (height 2196 px)
    assert rect[1] > 0.08, 'mantle atlas overflow'
    b.sheet(grid, 0.04, rect, "bark_dk", rim="moss", normal_hint=lambda p: Vector((0, 1, 0)), key="outer", v_rows=vr)
    # hanging moss strands from five lobe tips
    for u in (0.10, 0.30, 0.50, 0.70, 0.90):
        x = (u - 0.5) * (top_w + (bot_w - top_w)); y = y0 + flare - 0.05
        zt = z1 + lobe(u) - 0.02
        path = [Vector((x + 0.05 * math.sin(s * 2.1 + u * 9), y + 0.04 * s, zt - 0.09 * s)) for s in range(6)]
        tube(b, path, [0.040 - 0.006 * s for s in range(6)], sides=4, r_out=cell("moss"), r_in="moss", rim="moss")
    ob = b.finish(); tex_material(ob.data, "cv_cape"); return ob


# ------------------------------------------------------------------ BONE GORGET (NeckAttachment)
def build_scarf():
    """bark ring round the neck (painted, key "ring") with a rough top edge, five bone crest spikes rising from the back,
    and an amber clasp on the chest."""
    b = Builder("cv_scarf"); NU = 32; g = []
    rows = [(0.30, 0.62, 0.60), (0.24, 0.68, 0.66), (0.08, 0.72, 0.70), (-0.08, 0.74, 0.72), (-0.22, 0.72, 0.70)]
    for j, (z, rx, ry) in enumerate(rows):
        row = []
        for i in range(NU + 1):
            phi = math.pi + 2 * math.pi * i / NU; s, c = math.sin(phi), math.cos(phi)
            rough = 0.03 * (1 if j == 0 else 0) * (1 if i % 2 else -1)
            back = max(0.0, -c) ** 1.5
            row.append(Vector(((rx + rough) * spow(s, 2 / 2.6), -(ry + rough) * spow(c, 2 / 2.6), z - 0.10 * back)))
        g.append(row)
    rect, vr, _ = iso_rect(g, 0.0, 1.0, 1.0, 1024)
    b.sheet(g, 0.08, rect, "bark_dk", rim="bark_dk", closed_u=True, normal_hint=lambda p: Vector((p.x, p.y, 0.1)), key="ring", v_rows=vr)
    for k in range(5):                                                 # bone crest on the back
        phi = math.pi + (k - 2) * 0.32; s, c = math.sin(phi), math.cos(phi)
        base = Vector((0.66 * s, -0.66 * c, 0.26)); out = Vector((s, -c, 0)).normalized()
        axis = (Vector((0, 0, 1)) + out * (0.25 + 0.1 * abs(k - 2))).normalized()
        bipyramid(b, base, axis, 0.07, 0.50 - 0.07 * abs(k - 2), 5, swatches=("bone", "bone_dk", "bone", "bone_dk", "bone"))
    b.gem(Vector((0.0, -0.74, -0.02)), 0.07, 0.10, Vector((0, -1, 0)), "amber")
    ob = b.finish(); tex_material(ob.data, "cv_scarf"); return ob


# ------------------------------------------------------------------ GNARLED STAFF (WaistBackAttachment)
def build_sword():
    """staff built along +z from the butt (z 0) to the sickle joint (z STAFF_L): shaft tube with three knots, bone sickle hook
    bent over the top, amber crystal at the joint. Shaft is painted (key "shaft"; u-narrow rect so the texels stay isotropic)."""
    b = Builder("cv_sword"); L = 3.10; N = 26; path = [Vector((0, 0, L * j / N)) for j in range(N + 1)]
    radii = []
    for j in range(N + 1):
        t = j / N
        r = 0.125 * (1 - 0.25 * t)
        for k, c in ((0.22, 0.045), (0.52, 0.04), (0.80, 0.05)): r += c * math.exp(-((t - k) / 0.04) ** 2)
        radii.append(r)
    _, grid = tube(b, path, radii, sides=8, r_out=(0.0, 0.0, 0.22, 1.0), r_in="bark_dk", key="shaft", rim="bark_dk")
    # bone sickle hook: arc over the top, sweeping out to +x
    R = 0.46; hook = []
    for k in range(17):
        a = math.radians(120 * k / 16)
        hook.append(Vector((R * math.sin(a) * 0.9, 0.0, L - 0.10 + R * (1 - math.cos(a)) * 0.9)))
    tube(b, hook, [0.085 - 0.03 * (k / 16) for k in range(17)], sides=6, r_out=cell("bone"), r_in="bone_dk", rim="bone_dk")
    bipyramid(b, Vector((0, 0, L - 0.02)), Vector((0, 0, 1)), 0.17, 0.40, 8, swatches=("amber", "amber_dk", "amber", "amber_dk", "amber", "amber_dk", "amber", "amber_dk"))
    ob = b.finish(); tex_material(ob.data, "cv_sword"); return ob


def place_sword(ob):
    """pose: butt low behind the right hip, staff leaning back and up across the back, sickle over the left shoulder.
    WaistBackAttachment (neck frame z -2.098): Waist box allows 1.414 up and 1.885 down, depth +-3.36, so the lean is
    chosen from that box and checked by clip_check.py against the mantle and body."""
    d = Vector((-0.20, 0.68, 0.70)).normalized(); P0 = Vector((0.45, 0.85, -3.80))
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    ob.data.transform(Matrix.Translation(P0) @ rot)
    top = max(v.co.z for v in ob.data.vertices)
    ys = [v.co.y for v in ob.data.vertices]; xs = [v.co.x for v in ob.data.vertices]
    print("staff top z", round(top, 3), "(limit -0.684 abs)", "butt z", round(min(v.co.z for v in ob.data.vertices), 3), "(limit -3.983)",
          "y", round(min(ys), 2), round(max(ys), 2), "x", round(min(xs), 2), round(max(xs), 2))


def bake_ao(ob, size, others, samples=24): return B.bake_ao(ob, size, others, OUT, samples)
def body_proxy(shirt_png, pants_png): return B.body_proxy(shirt_png, pants_png, os.path.join(OUT, "cv_face.png"), HC)


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    crown = build_crown(); r = build_pauldron(); cape = build_cape(); scarf = build_scarf(); sword = build_sword()
    disp = sword.copy(); disp.data = sword.data.copy(); disp.name = "cv_sword_display"; bpy.context.collection.objects.link(disp); disp.hide_render = True
    place_sword(sword)
    l = r.copy(); l.data = r.data.copy(); l.name = "cv_pauldron_l"; bpy.context.collection.objects.link(l)
    l.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); l.data.flip_normals()
    r.location = (-1.5, 0, 0); l.location = (1.5, 0, 0)
    body_proxy(os.path.join(OUT, "cv_shirt.png"), os.path.join(OUT, "cv_pants.png"))
    for o in (crown, r, l, cape, scarf, sword): print("ITEM", o.name, "tris", tris(o))
    for it, regs in B.META.items():
        for k, s in regs.items():
            if isinstance(s, dict) and "rect" in s and "pos" in s: print("UVRECT", it, k, tuple(round(x, 3) for x in s["rect"]))
    with open(os.path.join(OUT, "meta.json"), "w") as fh: json.dump(B.META, fh)
    if os.environ.get("NOBAKE") != "1":
        items = [o for o in (crown, r, cape, scarf) if o.name in B.META]; t0 = time.time()
        for o in items: bake_ao(o, 1024 if o.name in ("cv_pauldron_r", "cv_cape") else 512, [x for x in (crown, r, l, cape, scarf, sword, disp) if x is not o])
        print("AO baked", [o.name for o in items], "in %.1fs" % (time.time() - t0))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cv_build.blend")); print("DONE")

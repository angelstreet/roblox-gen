"""Tidecrest Hood v2 - fitted cowl hood, headless Blender.
Run: Blender -b -P hood_v2.py
Frame in Blender: x lateral, y depth (front = -y), z up, origin = head centre, 1 unit = 1 stud.
Exports with origin moved to HatAttachment (head top, +0.59 up). Spec: QUALITY_PLAN.md item A.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else __file__))
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
OUT = os.path.join(HERE, "out", "v2"); os.makedirs(OUT, exist_ok=True)

HEAD_W, HEAD_H = 1.16, 1.18
ATTACH_Z = HEAD_H / 2          # HatAttachment height above head centre
PALETTE = [("navy", (30, 46, 82)), ("navy_dark", (10, 16, 32)), ("bronze", (196, 142, 74)), ("aqua", (70, 220, 220)),
           ("pearl", (232, 238, 240)), ("inner", (14, 20, 38)), ("bronze_dark", (140, 94, 48)), ("aqua_dark", (30, 150, 170))]
MAT = {n: i for i, (n, _) in enumerate(PALETTE)}

NT, NR = 48, 30                  # segments around / rings up
Z0, Z1 = -0.65, 0.68             # hem and crown (dome)
A_MAX = 0.775                    # half width  -> 1.55
B_FRONT, B_BACK, YC = 0.75, 0.75, -0.03   # depth: front reach, back reach, centre shift to the back


def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)


def radii(z):
    if z >= 0:
        k = max(0.0, 1 - (z / Z1) ** 3.2) ** (1 / 3.2); a = A_MAX * k; bf = B_FRONT * k; bb = B_BACK * k
    else:
        t = (-z / -Z0) ** 1.5; a = A_MAX - 0.15 * t; bf = B_FRONT - 0.06 * t; bb = B_BACK - 0.10 * t
    return a, bf, bb


def surf(theta, z):
    a, bf, bb = radii(z)
    s, c = math.sin(theta), math.cos(theta)
    e = 2.9                       # superellipse squareness
    sx = math.copysign(abs(s) ** (2 / e), s); cy = math.copysign(abs(c) ** (2 / e), c)
    x = a * sx
    y = YC - bf * cy if cy > 0 else YC - bb * cy     # theta=0 -> front (-y)
    zz = z
    # wave crest: swept up and back at the rear top
    back = max(0.0, -c)                                  # 1 at the back
    top = sstep(0.15, 0.66, z)
    crest = back ** 2 * top
    zz += 0.15 * crest; y += 0.15 * crest * (1 if True else 0)
    # broad folds: 3 radiating from crest, 2 temple-to-jaw
    fold = 0.016 * math.sin(3 * theta * 1.0 + 0.6) * (1 - top) * sstep(-0.6, -0.1, z)
    fold += 0.014 * math.sin(5 * theta) * top
    return Vector((x, y, zz)), fold


def build_mesh():
    me = bpy.data.meshes.new("hood"); bm = bmesh.new()
    grid = []
    for j in range(NR + 1):
        z = Z0 + (Z1 - Z0) * (j / NR) ** 0.85
        row = []
        for i in range(NT):
            th = 2 * math.pi * i / NT
            p, f = surf(th, z)
            n = Vector((p.x, p.y - YC, 0.0)).normalized() if abs(z) < Z1 - 1e-6 else Vector((0, 0, 1))
            row.append(bm.verts.new(p + n * f))
        grid.append(row)
    for j in range(NR):
        for i in range(NT):
            a, b = grid[j][i], grid[j][(i + 1) % NT]
            c, d = grid[j + 1][(i + 1) % NT], grid[j + 1][i]
            if j == NR - 1 and a.co.z >= Z1 - 1e-6 and False: continue
            try: bm.faces.new((a, b, c, d))
            except ValueError: pass
    bm.faces.ensure_lookup_table()
    # outward normals
    cen = Vector((0, YC, 0.0)); s = sum(1 if (f.calc_center_median() - cen).dot(f.normal) > 0 else -1 for f in bm.faces)
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    # face opening: arch 0.95 wide x 0.95 tall on the front
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.y > YC - 0.1: continue                       # front half only
        zc, zr, xr = -0.07, 0.48, 0.475
        if c.z < -0.52 + 0.0: pass
        if -0.55 < c.z < 0.41:
            if c.z > zc: lim = xr * math.sqrt(max(0, 1 - ((c.z - zc) / zr) ** 2))
            else: lim = xr
            if abs(c.x) < lim: kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    zc, zr, xr = -0.07, 0.48, 0.475
    for v in bm.verts:
        if not any(len(e.link_faces) == 1 for e in v.link_edges): continue
        if v.co.y > YC - 0.1 or not (-0.62 < v.co.z < 0.5): continue
        if v.co.z <= zc:
            if v.co.z > Z0 + 0.1: v.co.x = math.copysign(xr, v.co.x)
        else:
            ph = math.atan2((v.co.z - zc) / zr, v.co.x / xr)
            v.co.x = xr * math.cos(ph); v.co.z = zc + zr * math.sin(ph)
    bm.to_mesh(me); bm.free()
    return me


def finish():
    me = build_mesh()
    ob = bpy.data.objects.new("tidecrest_hood", me); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    for n, rgb in PALETTE:
        m = bpy.data.materials.new(n); m.diffuse_color = (*(c / 255 for c in rgb), 1); ob.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    md = ob.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.04; md.offset = -1; md.use_rim = True
    bpy.ops.object.modifier_apply(modifier="solid")
    n0 = tri_count(ob); dm = ob.modifiers.new("dec", "DECIMATE"); dm.ratio = min(1.0, 2150 / max(n0, 1)); dm.use_collapse_triangulate = False
    bpy.ops.object.modifier_apply(modifier="dec")
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table(); bm.normal_update()
    cen = Vector((0, YC, 0.1)); hem_z = Z0 + 0.04
    # materials: outer navy, inner dark, rim + hem bronze, crown accents
    bm.edges.ensure_lookup_table()
    for f in bm.faces:
        c = f.calc_center_median(); out = (c - cen).dot(f.normal) > 0
        f.material_index = MAT["navy"] if out else MAT["inner"]
        rimmed = any(len(e.link_faces) == 2 and False for e in f.edges)
        if c.z < Z0 + 0.06 and out: f.material_index = MAT["bronze"]       # hem band
    # opening rim: faces whose vertices all lie within 0.05 of the arch outline
    zc, zr, xr = -0.07, 0.48, 0.475
    def adist(v):
        if v.y > YC - 0.1 or not (-0.62 < v.z < 0.5): return 9
        if v.z <= zc: return abs(abs(v.x) - xr)
        return abs(math.hypot(v.x / xr, (v.z - zc) / zr) - 1) * 0.5
    for f in bm.faces:
        if f.material_index in (MAT["navy"], MAT["inner"]) and all(adist(v.co) < 0.05 for v in f.verts):
            f.material_index = MAT["bronze"]
    # gem at crest tip + crown crescent inlay (aqua)
    tip = Vector((0, YC + 0.15 + 0.62, Z1 + 0.14)) + Vector((0, 0.0, 0.0))
    gem = []
    for sg in (1, -1):
        top = tip + Vector((0, 0, 0.13 * sg)); eq = [tip + Vector((0.07 * math.cos(a), 0.07 * math.sin(a), 0)) for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
        vs = [bm.verts.new(v) for v in eq]; tv = bm.verts.new(top)
        for k in range(4):
            fa = bm.faces.new((vs[k], vs[(k + 1) % 4], tv) if sg > 0 else (vs[(k + 1) % 4], vs[k], tv)); fa.material_index = MAT["aqua"]
    # crescent on the brow: thin arc strip hugging the surface above the opening
    arc = []
    for k in range(13):
        t = -0.9 + 1.8 * k / 12; th = t * 0.72
        p0, _ = surf(th, 0.46); p1, _ = surf(th, 0.46 + 0.17 * (1 - abs(t) * 0.8))
        n = Vector((p0.x, p0.y - YC, 0)).normalized() * 0.09
        arc.append((bm.verts.new(p0 + n), bm.verts.new(p1 + n)))
    arc2 = [(bm.verts.new(a.co), bm.verts.new(b.co)) for a, b in arc]
    for k in range(12):
        fa = bm.faces.new((arc[k][0], arc[k + 1][0], arc[k + 1][1], arc[k][1])); fa.material_index = MAT["aqua"]
        fb = bm.faces.new((arc2[k][1], arc2[k + 1][1], arc2[k + 1][0], arc2[k][0])); fb.material_index = MAT["aqua"]
    # fix: inner shell must still face inward after recalc (recalc is topology based, fine for closed shell)
    bm.to_mesh(ob.data); bm.free()
    # UVs: every loop -> palette cell centre
    uv = ob.data.uv_layers.new(name="UVMap")
    for p in ob.data.polygons:
        k = p.material_index; u = ((k % 4) + 0.5) / 4; v = 1 - ((k // 4) + 0.5) / 2
        for li in p.loop_indices: uv.data[li].uv = (u, v)
    return ob


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def proxy():
    objs = []
    bpy.ops.mesh.primitive_cube_add(size=1); h = bpy.context.object; h.scale = (HEAD_W, HEAD_W, HEAD_H); h.name = "headproxy"
    bv = h.modifiers.new("b", "BEVEL"); bv.width = 0.14; bv.segments = 3; bpy.ops.object.modifier_apply(modifier="b")
    m = bpy.data.materials.new("skin"); m.diffuse_color = (0.59, 0.44, 0.34, 1); h.data.materials.append(m)
    bpy.ops.mesh.primitive_cube_add(size=1); t = bpy.context.object; t.scale = (2.0, 1.0, 1.7); t.location = (0, 0, -HEAD_H / 2 - 0.85 - 0.2)
    m2 = bpy.data.materials.new("torso"); m2.diffuse_color = (0.08, 0.1, 0.16, 1); t.data.materials.append(m2)
    return [h, t]


def render_views(ob):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_cavity = True
    sc.render.resolution_x = 700; sc.render.resolution_y = 800; sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.17, 0.18, 0.2)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 4.6
    views = {"front": (0, -10, 0), "side": (10, 0, 0), "back": (0, 10, 0), "q34": (7, -7, 3.5)}
    tgt = Vector((0, 0, -0.55))
    for n, loc in views.items():
        cam.location = Vector(loc) + tgt * 0
        d = tgt - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, f"hood_{n}.png"); bpy.ops.render.render(write_still=True)


def export(ob):
    # move origin to HatAttachment and export OBJ (+z front like v1) and FBX
    ob.location = (0, 0, -(ATTACH_Z + 0.045))   # +0.045: measured in Studio, hood sat that much high
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True)
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, "tidecrest_hood_v2.obj"), export_selected_objects=True, forward_axis="Z", up_axis="Y", export_materials=False)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "tidecrest_hood_v2.fbx"), use_selection=True, axis_forward="-Z", axis_up="Y", apply_unit_scale=True, global_scale=0.01, bake_space_transform=False)
    ob.location = (0, 0, ATTACH_Z + 0.045); bpy.ops.object.transform_apply(location=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
hood = finish()
bb = [hood.matrix_world @ Vector(c) for c in hood.bound_box]
xs, ys, zs = [v.x for v in bb], [v.y for v in bb], [v.z for v in bb]
print("HOOD_V2 tris", tri_count(hood), "bbox W %.3f D %.3f H %.3f" % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)),
      "z rel attach: %.3f .. %.3f" % (min(zs) - ATTACH_Z, max(zs) - ATTACH_Z))
nm = sum(1 for e in hood.data.edges if len([p for p in hood.data.polygons if e.index in [pe for pe in p.edge_keys]]) == 1) if False else 0
proxy(); render_views(hood); export(hood)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hood_v2.blend"))

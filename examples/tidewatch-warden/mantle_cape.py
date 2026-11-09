"""Tide Mantle (NeckAttachment) + Warden Cape (BodyBackAttachment). Headless Blender: Blender -b -P mantle_cape.py
Frame: x lateral, y depth (front = -y, back = +y), z up, 1 unit = 1 stud. Render frame origin = NeckAttachment (top of UpperTorso).
Each item is exported with its origin at its own attachment point (FBX global_scale 0.01, same as the hood).
"""
import bpy, bmesh, math, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out", "v3"); os.makedirs(OUT, exist_ok=True)
PALETTE = ["navy", "navy_dark", "bronze", "aqua", "pearl", "inner", "bronze_dark", "aqua_dark"]
MAT = {n: i for i, n in enumerate(PALETTE)}
PAL_RGB = {"navy": (30, 46, 82), "navy_dark": (10, 16, 32), "bronze": (196, 142, 74), "aqua": (70, 220, 220), "pearl": (232, 238, 240),
           "inner": (14, 20, 38), "bronze_dark": (140, 94, 48), "aqua_dark": (30, 150, 170)}
NECK_Z_TO_BACKATT = -1.06     # BodyBackAttachment sits ~0.8 below the neck, on the back surface (y=+0.5)
HEAD_CENTER_Z = 0.9


def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def sm(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)


def solidify(ob, th):
    md = ob.modifiers.new("s", "SOLIDIFY"); md.thickness = th; md.offset = -1; md.use_rim = True
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier="s")


def palette_uv(ob):
    uv = ob.data.uv_layers.new(name="UVMap")
    for p in ob.data.polygons:
        k = p.material_index; u = ((k % 4) + 0.5) / 4; v = 1 - ((k // 4) + 0.5) / 2
        for li in p.loop_indices: uv.data[li].uv = (u, v)


def make_mantle():
    NT, NR = 40, 9
    a_h, b_h = 1.2, 0.72         # hem half-width / half-depth
    a_c, b_c = 0.58, 0.55        # collar
    z_c = 0.22
    me = bpy.data.meshes.new("mantle"); bm = bmesh.new(); grid = []
    for j in range(NR + 1):
        t = j / NR; row = []
        for i in range(NT):
            th = 2 * math.pi * i / NT
            s_, c_ = math.sin(th), math.cos(th)           # c_>0 front(-y)
            a = a_c + (a_h - a_c) * t ** 0.9; b = b_c + (b_h - b_c) * t ** 0.9
            hem = -0.04 - 0.50 * abs(c_) ** 1.4
            z = z_c + (hem - z_c) * t ** 1.6
            fold = 0.022 * math.sin(7 * th + 0.5) * sm(t * 1.5) + 0.012 * math.sin(11 * th) * t
            r = 1 + fold / 0.8
            row.append(bm.verts.new((a * s_ * r, -b * c_ * r, z + 0.03 * math.sin(5 * th) * t * t)))
        grid.append(row)
    for j in range(NR):
        for i in range(NT):
            f = bm.faces.new((grid[j][i], grid[j][(i + 1) % NT], grid[j + 1][(i + 1) % NT], grid[j + 1][i]))
            f.material_index = MAT["navy"]
            if j == 0 or j == NR - 1 and False: f.material_index = MAT["bronze"]
            if j >= NR - 1: f.material_index = MAT["bronze"]          # hem piping
            if j == NR - 3: f.material_index = MAT["navy_dark"]
    bm.normal_update()
    cen = Vector((0, 0, 0.9)); s = sum(1 if (f.calc_center_median() - cen).dot(f.normal) > 0 else -1 for f in bm.faces)
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])        # normals out/up
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("tide_mantle", me); bpy.context.collection.objects.link(ob)
    for n in PALETTE:
        m = bpy.data.materials.new("m_" + n); m.diffuse_color = (*(c / 255 for c in PAL_RGB[n]), 1); ob.data.materials.append(m)
    solidify(ob, 0.035)
    # inner faces dark
    bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    for f in bm.faces:
        if f.material_index == MAT["navy"] and f.normal.z < -0.2 and False: f.material_index = MAT["inner"]
    # pearl clasp + aqua gem at the sternum (front, -y)
    cx, cy, cz = 0.0, -0.60, -0.28
    ring = [bm.verts.new((cx + 0.16 * math.cos(a), cy - 0.03, cz + 0.16 * math.sin(a))) for a in [k * math.pi / 3 for k in range(6)]]
    ctr = bm.verts.new((cx, cy - 0.06, cz))
    for k in range(6):
        fa = bm.faces.new((ring[k], ring[(k + 1) % 6], ctr)); fa.material_index = MAT["pearl"]
        fb = bm.faces.new((ring[(k + 1) % 6], ring[k], bm.verts.new((cx, cy - 0.015, cz)))); fb.material_index = MAT["bronze_dark"]
    gem = [bm.verts.new((cx + 0.075 * math.cos(a), cy - 0.075, cz + 0.075 * math.sin(a))) for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
    gt = bm.verts.new((cx, cy - 0.16, cz)); gb = bm.verts.new((cx, cy - 0.045, cz))
    for k in range(4):
        fa = bm.faces.new((gem[k], gem[(k + 1) % 4], gt)); fa.material_index = MAT["aqua"]
        fb = bm.faces.new((gem[(k + 1) % 4], gem[k], gb)); fb.material_index = MAT["aqua_dark"]
    bm.to_mesh(me); bm.free()
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.shade_smooth()
    palette_uv(ob); return ob


def make_cape(tex_path):
    NC, NR = 14, 20; L = 3.2; z_top = 0.50
    me = bpy.data.meshes.new("cape"); bm = bmesh.new(); grid = []
    for j in range(NR + 1):
        v = j / NR; w = 1.7 + 0.2 * v; row = []
        for i in range(NC + 1):
            u = i / NC; x = (u - 0.5) * w
            scal = 0.10 * (0.5 + 0.5 * math.cos(2 * math.pi * u * 5)) * sm((v - 0.9) / 0.1)       # wave scallop hem
            z = z_top - L * v - scal
            y = 0.12 + 0.30 * v ** 1.5 + 0.07 * math.sin((u - 0.5) * 2 * math.pi * 3.5 * (1 + 0.35 * v) + 0.4) * (0.3 + 0.7 * v)
            y += 0.10 * (2 * (u - 0.5)) ** 2 * v          # edges swing back a little
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(NR):
        for i in range(NC):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.faces.ensure_lookup_table()
    # normals facing +y (back/outward)
    if sum(f.normal.y for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    uvl = bm.loops.layers.uv.new("UVMap")
    for j in range(NR):
        for i in range(NC):
            f = bm.faces[j * NC + i]
            for lp in f.loops:
                idx = grid.index if False else None
            # map by vertex position in grid
    bm.verts.index_update(); pos = {}
    for j in range(NR + 1):
        for i in range(NC + 1): pos[grid[j][i].index] = (i / NC, 1 - j / NR)
    for f in bm.faces:
        for lp in f.loops: lp[uvl].uv = pos[lp.vert.index]
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("warden_cape", me); bpy.context.collection.objects.link(ob)
    m = bpy.data.materials.new("cape"); m.use_nodes = True
    n = m.node_tree.nodes; img = n.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(tex_path)
    m.node_tree.links.new(img.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); ob.data.materials.append(m)
    solidify(ob, 0.03); bpy.context.view_layer.objects.active = ob; bpy.ops.object.shade_smooth()
    # solidify duplicates UVs on the inner side (same texture, mirrored read is fine for cloth)
    return ob


def bbox(ob):
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [(min(v[k] for v in bb), max(v[k] for v in bb)) for k in range(3)]


def export(ob, name, origin):
    ob.location = Vector(origin) * 0; bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    ob.location = -Vector(origin); bpy.ops.object.transform_apply(location=True)
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, name + ".obj"), export_selected_objects=True, forward_axis="Z", up_axis="Y", export_materials=False)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, global_scale=0.01, bake_space_transform=False)
    ob.location = Vector(origin); bpy.ops.object.transform_apply(location=True)


def proxies():
    def box(name, size, loc, col):
        bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = name; o.scale = size; o.location = loc
        m = bpy.data.materials.new(name); m.diffuse_color = (*col, 1); o.data.materials.append(m); return o
    box("head", (1.16, 1.16, 1.18), (0, 0, HEAD_CENTER_Z), (0.59, 0.44, 0.34))
    box("torso", (2, 1, 2), (0, 0, -1), (0.12, 0.14, 0.2)); box("armL", (1, 1, 2), (1.5, 0, -1), (0.59, 0.44, 0.34)); box("armR", (1, 1, 2), (-1.5, 0, -1), (0.59, 0.44, 0.34))
    box("legL", (1, 1, 2), (0.5, 0, -3), (0.1, 0.12, 0.18)); box("legR", (1, 1, 2), (-0.5, 0, -3), (0.1, 0.12, 0.18))


def render(tag):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "TEXTURE"; sc.display.shading.show_cavity = True
    sc.render.resolution_x = 700; sc.render.resolution_y = 900; sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.17, 0.18, 0.2)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 7.6
    tgt = Vector((0, 0, -1.2))
    for n, loc in {"front": (0, -12, 0), "side": (12, 0, 0), "back": (0, 12, 0), "q34back": (8, 8, 3.5), "q34": (8, -8, 3.5)}.items():
        cam.location = tgt + Vector(loc); cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, f"{tag}_{n}.png"); bpy.ops.render.render(write_still=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
mantle = make_mantle(); cape = make_cape(os.path.join(OUT, "cape_tex.png"))
cape.location = (0, 0.5, NECK_Z_TO_BACKATT); bpy.context.view_layer.update()
for o, n in ((mantle, "mantle"), (cape, "cape")):
    b = bbox(o); print(n.upper(), "tris", tris(o), "W %.2f D %.2f H %.2f" % (b[0][1] - b[0][0], b[1][1] - b[1][0], b[2][1] - b[2][0]))
# hood from v2 blend for the fit check
with bpy.data.libraries.load(os.path.join(HERE, "out", "v2", "hood_v2.blend")) as (src, dst): dst.objects = [x for x in src.objects if x == "tidecrest_hood"]
for o in dst.objects: bpy.context.collection.objects.link(o); o.location = (0, 0, HEAD_CENTER_Z + 0.59)
proxies(); render("set")
hood = bpy.data.objects["tidecrest_hood"]; hood.hide_render = True
bpy.data.objects.remove(hood)
export(mantle, "tide_mantle", (0, 0, 0)); export(cape, "warden_cape", (0, 0, 0))   # cape mesh is already authored relative to its attachment
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "mantle_cape.blend"))

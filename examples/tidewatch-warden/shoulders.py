"""Layered shoulder plates (Right/LeftShoulderAttachment). Blender -b -P shoulders.py
Origin = shoulder attachment (arm top centre). Right plate outward = +x; left = mirror. Palette texture, FBX scale 0.01.
Real R15: arm centre x=+-1.47 from torso centre, arm top 0.80 above torso centre (= 0.05 below NeckAttachment), arm 1 wide.
"""
import bpy, bmesh, math, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out", "v4"); os.makedirs(OUT, exist_ok=True)
PALETTE = ["navy", "navy_dark", "bronze", "aqua", "pearl", "inner", "bronze_dark", "aqua_dark"]
RGB = {"navy": (30, 46, 82), "navy_dark": (10, 16, 32), "bronze": (196, 142, 74), "aqua": (70, 220, 220), "pearl": (232, 238, 240), "inner": (14, 20, 38), "bronze_dark": (140, 94, 48), "aqua_dark": (30, 150, 170)}
M = {n: i for i, n in enumerate(PALETTE)}
# lames: (x_in, x_out, half_depth, lift)  upper lames sit on top and are shorter
LAMES = [(-0.40, 0.34, 0.60, 0.13), (-0.30, 0.66, 0.65, 0.065), (-0.20, 0.92, 0.70, 0.00)]
NX, NY, TH = 6, 12, 0.07


def zsurf(x, y, w, lift):
    z = 0.06 + lift - 0.42 * (max(x - 0.15, 0) / 0.80) ** 1.8
    return z - 0.16 * (abs(y) / w) ** 3.0


def lame(bm, k, xa, xb, w, lift):
    g = []
    for i in range(NX + 1):
        x = xa + (xb - xa) * i / NX; row = []
        for j in range(NY + 1):
            s = -1 + 2 * j / NY; y = w * s * (1 - 0.10 * (i / NX) ** 2)      # slightly narrower at the outer edge
            row.append(bm.verts.new((x, y, zsurf(x, y, w, lift))))
        g.append(row)
    faces = []
    for i in range(NX):
        for j in range(NY):
            f = bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
            edge = (i == NX - 1) or j == 0 or j == NY - 1
            f.material_index = M["bronze"] if edge else (M["navy_dark"] if (i + j) % 2 == 0 and False else M["navy"])
            if i == 0 and k > 0: f.material_index = M["navy_dark"]
            faces.append(f)
    return g


def build():
    bm = bmesh.new()
    for k, (xa, xb, w, lift) in enumerate(LAMES): lame(bm, k, xa, xb, w, lift)
    bm.normal_update()
    if sum(f.normal.z for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("pl"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("shoulder_r", me); bpy.context.collection.objects.link(ob)
    for n in PALETTE:
        m = bpy.data.materials.new(n); m.diffuse_color = (*(c / 255 for c in RGB[n]), 1); ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    md = ob.modifiers.new("s", "SOLIDIFY"); md.thickness = TH; md.offset = -1; md.use_rim = True; bpy.ops.object.modifier_apply(modifier="s")
    bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    # glowing rune gem on the top lame + bronze spine ridge
    gx, gz = 0.0, zsurf(0.0, 0, 0.60, 0.13) + 0.015
    ring = [bm.verts.new((gx + 0.11 * math.cos(a), 0.15 * math.sin(a), gz)) for a in [t * math.pi / 2 for t in range(4)]]
    top = bm.verts.new((gx, 0, gz + 0.11)); bot = bm.verts.new((gx, 0, gz - 0.02))
    for t in range(4):
        a = bm.faces.new((ring[t], ring[(t + 1) % 4], top)); a.material_index = M["aqua"]
        b = bm.faces.new((ring[(t + 1) % 4], ring[t], bot)); b.material_index = M["aqua_dark"]
    bm.to_mesh(me); bm.free(); bpy.ops.object.shade_smooth()
    uv = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        k = p.material_index; u = ((k % 4) + 0.5) / 4; v = 1 - ((k // 4) + 0.5) / 2
        for li in p.loop_indices: uv.data[li].uv = (u, v)
    return ob


def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def export(ob, name):
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, axis_forward="-Z", axis_up="Y", apply_unit_scale=True, global_scale=0.01, bake_space_transform=False)


bpy.ops.wm.read_factory_settings(use_empty=True)
R = build()
bb = [Vector(c) for c in R.bound_box]; print("PLATE tris", tris(R), "W %.2f D %.2f H %.2f" % tuple(max(v[k] for v in bb) - min(v[k] for v in bb) for k in range(3)))
# left = mirrored copy
L = R.copy(); L.data = R.data.copy(); L.name = "shoulder_l"; bpy.context.collection.objects.link(L); L.scale.x = -1
bpy.context.view_layer.objects.active = L; L.select_set(True); bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new(); bm.from_mesh(L.data); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(L.data); bm.free()
export(R, "shoulder_right"); export(L, "shoulder_left")
# preview on proxy
L.location = (-1.47, 0, -0.05); R.location = (1.47, 0, -0.05)
def box(n, size, loc, col):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = n; o.scale = size; o.location = loc
    m = bpy.data.materials.new(n); m.diffuse_color = (*col, 1); o.data.materials.append(m)
box("head", (1.16, 1.16, 1.18), (0, 0, 0.9), (0.59, 0.44, 0.34)); box("torso", (2, 1, 2), (0, 0, -1), (0.12, 0.14, 0.2))
box("armL", (1, 1, 2), (1.5, 0, -1), (0.59, 0.44, 0.34)); box("armR", (1, 1, 2), (-1.5, 0, -1), (0.59, 0.44, 0.34))
with bpy.data.libraries.load(os.path.join(HERE, "out", "v3", "mantle_cape.blend")) as (s_, d_): d_.objects = [x for x in s_.objects if x == "tide_mantle"]
for o in d_.objects: bpy.context.collection.objects.link(o)
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_cavity = True
sc.render.resolution_x = 800; sc.render.resolution_y = 600; sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.17, 0.18, 0.2)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"; cam.data.ortho_scale = 5.8
tgt = Vector((0, 0, 0.0))
for n, loc in {"front": (0, -12, 1), "side": (12, 0, 1), "q34": (8, -8, 5)}.items():
    cam.location = tgt + Vector(loc); cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, f"sh_{n}.png"); bpy.ops.render.render(write_still=True)

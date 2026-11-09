"""Render + export for v5. Run: Blender -b out/v5/v5_build.blend -P render_v5.py [-- views=front,back export=1 tag=x]
Textures: out/v5/tex_<item>.png (from paint_v5.py); falls back to flat dark if missing.
Lighting imitates a product shot: dark grey backdrop, big soft key from front-left-top, cool fill, warm rim.
Exports FBX per item with origin = its attachment (global_scale 0.01, -Z forward, Y up)."""
import bpy, os, sys, math
from mathutils import Vector, Matrix

OUT = os.path.join(os.path.dirname(bpy.data.filepath))
args = dict(a.split("=") for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
VIEWS = args.get("views", "front,back,side,q34,q34back").split(","); TAG = args.get("tag", "v5")
ITEMS = ["tidecrest_hood_v5", "tide_mantle_v5", "warden_cape_v5", "tide_pauldron_r_v5", "tide_pauldron_l_v5", "tidewatch_belt_v5", "tidefall_skirt_v5"]
HIDE = args.get("hide", "").split(",")
# attachment positions in the neck frame (x, y=depth front -y, z up). Hood: HatAttachment (+0.045 measured offset)
ATT = {"tidecrest_hood_v5": (0, 0, 0.576 + 0.635), "tide_mantle_v5": (0, 0, 0), "warden_cape_v5": (0, 0.502, -1.061),
       "tide_pauldron_r_v5": (-1.5, 0, 0), "tide_pauldron_l_v5": (1.5, 0, 0),
       "tidewatch_belt_v5": tuple(float(x) for x in args.get("waistfront", "0,-0.502,-2.098").split(",")),
       "tidefall_skirt_v5": tuple(float(x) for x in args.get("waistcenter", "0,0,-2.098").split(","))}

sc = bpy.context.scene
for nm in ITEMS:
    ob = bpy.data.objects[nm]; ob.hide_render = nm in HIDE
    tex = os.path.join(OUT, "tex_" + nm.replace("_l_", "_r_") + ".png")
    mat = ob.data.materials[0]; nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
    bs.inputs["Roughness"].default_value = 0.8
    try: bs.inputs["Specular IOR Level"].default_value = 0.25
    except Exception: pass
    if os.path.exists(tex):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(tex); nt.links.new(t.outputs["Color"], bs.inputs["Base Color"])
    else:
        bs.inputs["Base Color"].default_value = (0.012, 0.016, 0.03, 1)

sc.render.engine = "BLENDER_EEVEE_NEXT"
try: sc.eevee.taa_render_samples = 48
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 760, 1000
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.034, 0.034, 0.036, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
# world light is kept low; the backdrop colour comes from film below

sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"


def light(name, kind, loc, energy, size, col=(1, 1, 1)):
    L = bpy.data.lights.new(name, kind); L.energy = energy; L.color = col
    if kind == "AREA": L.size = size
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, -0.8)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o


rig = bpy.data.objects.new("rig", None); sc.collection.objects.link(rig)
for o in (light("key", "AREA", (-5, -7, 6), 1700, 7), light("fill", "AREA", (7, -5, 1), 500, 9, (0.85, 0.9, 1.0)),
          light("rim", "AREA", (3, 8, 5), 1400, 5, (1.0, 0.93, 0.82)), light("rim2", "AREA", (-6, 6, 2), 900, 5)):
    o.parent = rig
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 6.9
tgt = Vector((0, 0, -1.25))
ANG = {"front": 0, "q34": 35, "side": 90, "q34back": 145, "back": 180}
for n in VIEWS:
    a = math.radians(ANG[n])
    # rotate the camera and the light rig together so every view is lit like the front one
    cam.location = tgt + Vector((-12 * math.sin(a), -12 * math.cos(a), 1.6 if n.startswith("q34") else 0.6))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    rig.rotation_euler = (0, 0, -a)
    sc.render.filepath = os.path.join(OUT, f"{TAG}_{n}.png"); bpy.ops.render.render(write_still=True)

if args.get("export") == "1":
    for nm in ITEMS:
        ob = bpy.data.objects[nm]
        if nm == "tide_pauldron_l_v5": continue   # exported separately below (mirror)
        tmp = ob.copy(); tmp.data = ob.data.copy(); sc.collection.objects.link(tmp)
        tmp.data.transform(ob.matrix_world); tmp.matrix_world = Matrix.Identity(4)
        tmp.data.transform(Matrix.Translation(-Vector(ATT[nm]))); tmp.data.materials.clear()
        bpy.ops.object.select_all(action="DESELECT"); tmp.select_set(True); bpy.context.view_layer.objects.active = tmp
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, nm + ".fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_unit_scale=True, global_scale=0.01, bake_space_transform=False, mesh_smooth_type="FACE")
        bb = [Vector(c) for c in tmp.bound_box]
        print("EXPORT", nm, "tris", sum(len(p.vertices) - 2 for p in tmp.data.polygons),
              "bbox rel attachment x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (min(v.x for v in bb), max(v.x for v in bb), min(v.y for v in bb), max(v.y for v in bb), min(v.z for v in bb), max(v.z for v in bb)))
        if nm == "tide_pauldron_r_v5":
            tmp.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); tmp.data.flip_normals()
            bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "tide_pauldron_l_v5.fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                                     apply_unit_scale=True, global_scale=0.01, bake_space_transform=False, mesh_smooth_type="FACE")
        bpy.data.objects.remove(tmp)
print("RENDERED")

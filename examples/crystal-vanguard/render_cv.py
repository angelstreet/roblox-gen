"""Render + FBX export. Run: Blender -b out/cv_build.blend -P render_cv.py -- tag=r1 export=1 [closeup=1]
Same recipe as tidewatch render_v5.py: Eevee, orthographic cam rotating with the light rig, FBX per accessory with origin = attachment."""
import bpy, os, sys, math
from mathutils import Vector, Matrix
OUT = os.path.dirname(bpy.data.filepath)
args = dict(a.split("=") for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
VIEWS = args.get("views", "front,back,side,q34,q34back").split(","); TAG = args.get("tag", "r1")
ITEMS = ["cv_crown", "cv_scarf", "cv_cape", "cv_pauldron_r", "cv_pauldron_l", "cv_sword"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from palette import NAMES
FBX = NAMES["fbx"]                     # export file names: edit them in palette.py
ATT = {"cv_crown": (0, 0, 0.576 + 0.635), "cv_scarf": (0, 0, 0), "cv_cape": (0, 0.502, -1.061), "cv_pauldron_r": (-1.5, 0, 0),
       "cv_pauldron_l": (1.5, 0, 0), "cv_sword": (0, 0.502, -2.098)}
sc = bpy.context.scene
for nm in ITEMS + ["cv_sword_display"]:
    ob = bpy.data.objects[nm]; tn = {"cv_pauldron_l": "cv_pauldron_r", "cv_sword_display": "cv_sword"}.get(nm, nm)
    tex = os.path.join(OUT, "tex_" + tn + ".png"); mat = ob.data.materials[0]; nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
    bs.inputs["Roughness"].default_value = 0.45 if nm in ("cv_sword", "cv_sword_display", "cv_crown", "cv_pauldron_r", "cv_pauldron_l") else 0.7
    try: bs.inputs["Specular IOR Level"].default_value = 0.5
    except Exception: pass
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(tex); nt.links.new(t.outputs["Color"], bs.inputs["Base Color"])
    if nm in ("cv_sword", "cv_sword_display"):     # render-only glow so the crystal blade reads as lit (FBX has no emission)
        nt.links.new(t.outputs["Color"], bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = 0.35
sc.render.engine = "BLENDER_EEVEE_NEXT"
try: sc.eevee.taa_render_samples = 48
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 760, 1000
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.045, 0.10, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"


def light(name, kind, loc, energy, size, col=(1, 1, 1)):
    L = bpy.data.lights.new(name, kind); L.energy = energy; L.color = col
    if kind == "AREA": L.size = size
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, -0.8)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o


rig = bpy.data.objects.new("rig", None); sc.collection.objects.link(rig)
K = float(args.get("light", "0.55"))
for o in (light("key", "AREA", (-5, -7, 6), 1700 * K, 7), light("fill", "AREA", (7, -5, 1), 600 * K, 9, (0.8, 0.88, 1.0)),
          light("rim", "AREA", (3, 8, 5), 1400 * K, 5, (0.85, 0.92, 1.0)), light("rim2", "AREA", (-6, 6, 2), 900 * K, 5)):
    o.parent = rig
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 7.0
tgt = Vector((0, 0.1, -1.25)); ANG = {"front": 0, "q34": 35, "side": 90, "q34back": 145, "back": 180}
bpy.data.objects["cv_sword_display"].hide_render = True
for n in VIEWS:
    a = math.radians(ANG[n])
    cam.location = tgt + Vector((-12 * math.sin(a), -12 * math.cos(a), 1.6 if n.startswith("q34") else 0.6))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler(); rig.rotation_euler = (0, 0, -a)
    sc.render.filepath = os.path.join(OUT, f"{TAG}_{n}.png"); bpy.ops.render.render(write_still=True)
if args.get("preview2d") == "1":     # clothing only on the block R15 proxy
    for nm in ITEMS + ["cv_sword_display"]: bpy.data.objects[nm].hide_render = True
    for n in ("front", "q34", "back"):
        a = math.radians(ANG[n]); cam.location = tgt + Vector((-12 * math.sin(a), -12 * math.cos(a), 0.6))
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler(); rig.rotation_euler = (0, 0, -a)
        sc.render.filepath = os.path.join(OUT, f"pv_{n}.png"); bpy.ops.render.render(write_still=True)
    sys.exit(0)
if args.get("closeup") == "1":      # sword alone, upright, front and 3/4
    for nm in list(ITEMS) + [o.name for o in bpy.data.objects if o.get("body") or o.name in ("torso", "armR", "armL", "legR", "legL", "head", "face") or o.name.startswith(("Cube", "eye"))]:
        if nm in bpy.data.objects: bpy.data.objects[nm].hide_render = True
    bpy.data.objects["cv_sword_display"].hide_render = False
    cam.data.ortho_scale = 5.0; sc.render.resolution_x, sc.render.resolution_y = 600, 1000
    t2 = Vector((0, 0, -2.0 + 2.0))
    for n, aa in (("sword_front", 0), ("sword_q34", 40)):
        a = math.radians(aa); cam.location = t2 + Vector((-12 * math.sin(a), -12 * math.cos(a), 0.5))
        cam.rotation_euler = (t2 - cam.location).to_track_quat("-Z", "Y").to_euler(); rig.rotation_euler = (0, 0, -a)
        sc.render.filepath = os.path.join(OUT, f"{TAG}_{n}.png"); bpy.ops.render.render(write_still=True)
if args.get("export") == "1":
    for nm in ITEMS:
        ob = bpy.data.objects[nm]; tmp = ob.copy(); tmp.data = ob.data.copy(); sc.collection.objects.link(tmp)
        tmp.data.transform(ob.matrix_world); tmp.matrix_world = Matrix.Identity(4)
        tmp.data.transform(Matrix.Translation(-Vector(ATT[nm]))); tmp.data.materials.clear()
        bpy.ops.object.select_all(action="DESELECT"); tmp.select_set(True); bpy.context.view_layer.objects.active = tmp
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, FBX[nm] + ".fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_unit_scale=True, global_scale=0.01, bake_space_transform=False, mesh_smooth_type="FACE")
        bb = [Vector(c) for c in tmp.bound_box]
        print("EXPORT", FBX[nm], "tris", sum(len(p.vertices) - 2 for p in tmp.data.polygons), "bbox rel attachment x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f (size %.2f x %.2f x %.2f)" % (
            min(v.x for v in bb), max(v.x for v in bb), min(v.y for v in bb), max(v.y for v in bb), min(v.z for v in bb), max(v.z for v in bb),
            max(v.x for v in bb) - min(v.x for v in bb), max(v.y for v in bb) - min(v.y for v in bb), max(v.z for v in bb) - min(v.z for v in bb)))
        bpy.data.objects.remove(tmp)
print("RENDERED")

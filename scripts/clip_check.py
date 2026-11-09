"""Interpenetration check for ANY set (run inside Blender on the set's build .blend):
    blender -b examples/<set>/out/<set>_build.blend -P scripts/clip_check.py [-- items=a,b,c]
Prints BVH triangle-pair overlap counts for every pair of accessory items and for every item against the block body proxy
(torso, armR, armL, legR, legL, head). Items default to every visible mesh that is not a body part. 0 = no contact.
Small counts where an item is meant to sit ON the body (collar on the torso, shoulder piece around the arm) are normal;
a large count between two ITEMS usually shows in Studio (r21: the scarf poked through the collar). Judge by a render.
Rest pose only: animation clipping is tested in Studio with docs/studio/pose_anim.lua."""
import bpy, sys
from mathutils.bvhtree import BVHTree
BODY = ["torso", "armR", "armL", "legR", "legL", "head"]
args = dict(a.split("=", 1) for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
def bvh(o):
    me = o.data.copy(); me.transform(o.matrix_world)
    t = BVHTree.FromPolygons([v.co[:] for v in me.vertices], [p.vertices[:] for p in me.polygons]); bpy.data.meshes.remove(me); return t
if "items" in args: items = args["items"].split(",")
else: items = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.hide_render and o.name not in BODY + ["face"] and not o.name.startswith(("Cube", "eye")) and not o.name.endswith("_display")]
T = {n: bvh(bpy.data.objects[n]) for n in items + [b for b in BODY if b in bpy.data.objects]}
print("CLIP items:", ", ".join(items))
for i, a in enumerate(items):
    for b in items[i + 1:]:
        n = len(T[a].overlap(T[b])); print(f"CLIP {a} vs {b}: {n}")
for a in items:
    hits = {b: len(T[a].overlap(T[b])) for b in BODY if b in T}
    print(f"CLIP {a} vs body: " + ", ".join(f"{b} {n}" for b, n in hits.items() if n) if any(hits.values()) else f"CLIP {a} vs body: 0")

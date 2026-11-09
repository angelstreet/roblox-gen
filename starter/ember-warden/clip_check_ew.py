"""Blender -b out/ew_build.blend -P clip_check_ew.py : BVH overlap (triangle pairs) between every pair of items and each item vs the body proxy.
0 = clean. The axe is posed on the lower back; the neck/hair/cape/pauldron pairs are checked in the rest pose."""
import bpy, itertools
from mathutils.bvhtree import BVHTree
def bvh(o):
    me = o.data.copy(); me.transform(o.matrix_world); return BVHTree.FromPolygons([v.co[:] for v in me.vertices], [p.vertices[:] for p in me.polygons])
items = ["ew_helm", "ew_collar", "ew_cape", "ew_pauldron_r", "ew_pauldron_l", "ew_axe"]; body = ["torso", "armR", "armL", "legR", "legL", "head"]
T = {n: bvh(bpy.data.objects[n]) for n in items + body}
for a, b in itertools.combinations(items, 2): print("CLIP", a, "vs", b, len(T[a].overlap(T[b])))
for a in items:
    print("CLIP", a, "vs body", {n: len(T[a].overlap(T[n])) for n in body if len(T[a].overlap(T[n]))})

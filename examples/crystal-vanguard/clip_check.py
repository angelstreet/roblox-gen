"""Blender -b out/cv_build.blend -P clip_check.py : BVH overlap of the posed sword against cape, pauldrons, scarf, crown, body proxy (prints triangle-pair counts)."""
import bpy
from mathutils.bvhtree import BVHTree
def bvh(o):
    me = o.data.copy(); me.transform(o.matrix_world); return BVHTree.FromPolygons([v.co[:] for v in me.vertices], [p.vertices[:] for p in me.polygons])
sw = bvh(bpy.data.objects["cv_sword"])
for n in ("cv_cape", "cv_pauldron_r", "cv_pauldron_l", "cv_scarf", "cv_crown", "torso", "armR", "armL", "legR", "legL", "head"):
    print("CLIP sword vs", n, len(sw.overlap(bvh(bpy.data.objects[n]))))
# r22: other item pairs in the rest pose (the scarf showed through the cape collar in Studio r21)
for a, b in (("cv_scarf", "cv_cape"), ("cv_crown", "cv_cape"), ("cv_crown", "cv_pauldron_r"), ("cv_crown", "cv_pauldron_l"), ("cv_scarf", "cv_pauldron_r"), ("cv_scarf", "cv_pauldron_l")):
    print("CLIP", a, "vs", b, len(bvh(bpy.data.objects[a]).overlap(bvh(bpy.data.objects[b]))))

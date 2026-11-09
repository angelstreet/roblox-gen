import bpy, sys, os
out=os.path.abspath("out")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(out,"tidecrest_hood.obj"))
o=bpy.context.selected_objects[0]
print("OBJ imported:", o.name, "tris:", sum(len(p.vertices)-2 for p in o.data.polygons), "dims(studs):", tuple(round(x,2) for x in o.dimensions))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,"tidecrest_hood.blend"))

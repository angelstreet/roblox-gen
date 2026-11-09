# Builder cheat sheet (lib/rgen_mesh.py) - read this instead of the code
Import from a set folder: `sys.path.insert(0, os.path.join(HERE, "..", "..", "lib")); import rgen_mesh as B`.

`Builder(name)`: one accessory = one bmesh + one UV layer "UVMap". Y-up Blender scene, UV v=0 is the BOTTOM of the texture.
Meshes are authored relative to their attachment (origin = attachment point). The block R15 proxy is `body()`.

| Call | Use |
|---|---|
| `b.face(verts, uvs)` | one polygon with per-corner UVs |
| `b.sheet(grid, thick, r_out, r_in=None, rim="bronze", closed_u=False, closed_rows=None, normal_hint=None, fold=None, key=None)` | thick cloth/plate patch from a grid of Vectors `grid[row][col]` (rows top->bottom). `r_out=(u0,v0,u1,v1)` UV rect of the outer face, `r_in` rect or swatch name for the inner face, `rim` swatch for edges. `closed_u=True` wraps a ring |
| `b.extrude(pts, origin, ax_a, ax_b, thick, chamfer, uv_front, uv_side="bronze")` | flat 2D polygon (CCW in axes a,b) -> bevelled slab (trims, crowns, plates) |
| `b.gem(center, rx, rz, depth_dir, col="aqua")` | small bipyramid crystal on a surface |
| `b.finish(weld=True)` | weld, fix normals, return the Blender object |
| `sm(t)`, `spow(x,p)` | smoothstep and signed power helpers for height profiles |
| `tris(ob)` | triangle count |

Palette swatches: a bottom strip of flat colours (`SW` dict in lib/rgen_mesh.py, shared by reference; the Crystal Vanguard example overrides it with 8 swatches). Name a swatch string where a UV rect is expected.
Simple path (about 17-30 s, no AO bakes, no meta.json): `examples/crystal-vanguard/run_all.sh <tag>` runs make_clothing_cv -> paint_cv -> build_cv -> render_cv -> compose_cv in that order.
`sheet()` also accepts `pole_row0=True` (collapse the first row to a point, for domes) and `rim_skip_cols`. Heavy path (distance-band trims, AO): `examples/tidewatch-warden/`.

## Importing a GLB blockout safely
Snapshot `set(bpy.data.objects)` before `bpy.ops.import_scene.gltf(filepath=...)`, take only the new MESH objects, then delete empties/"world" parent. Delete children before parents.
Axis: the starter sword imports lying along **-Y** (tip y=-4.12, pommel y=+0.14). Map to Roblox-up with (x, y, z) -> (x, z, -y) before exporting.

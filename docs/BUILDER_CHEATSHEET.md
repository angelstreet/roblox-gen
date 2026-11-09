# Builder cheat sheet (lib/rgen_mesh.py) - read this instead of the code
Import from a set folder: `sys.path.insert(0, os.path.join(HERE, "..", "..", "lib")); import rgen_mesh as B`.

`Builder(name)`: one accessory = one bmesh + one UV layer "UVMap". Y-up Blender scene, UV v=0 is the BOTTOM of the texture.
Meshes are authored relative to their attachment (origin = attachment point). The block R15 proxy is `body()`.

| Call | Use |
|---|---|
| `b.face(verts, uvs)` | one polygon with per-corner UVs |
| `b.sheet(grid, thick, r_out, r_in=None, rim="bronze", closed_u=False, closed_rows=None, normal_hint=None, fold=None, key=None, v_rows=None)` | thick cloth/plate patch from a grid of Vectors `grid[row][col]` (rows top->bottom). `r_out=(u0,v0,u1,v1)` UV rect of the outer face, `r_in` rect or swatch name for the inner face, `rim` swatch for edges. `closed_u=True` wraps a ring |
| `b.extrude(pts, origin, ax_a, ax_b, thick, chamfer, uv_front, uv_side="bronze")` | flat 2D polygon (CCW in axes a,b) -> bevelled slab (trims, crowns, plates) |
| `b.gem(center, rx, rz, depth_dir, col="aqua")` | small bipyramid crystal on a surface (any depth_dir; before 2026-11-09 a vertical one came out open) |
| `b.flat_mode = 1` ... `= 0` | faces added in between are flat-shaded (facets: crystals, rock, spikes); default 0 = smooth |
| `b.finish(weld=True)` | weld, fix normals, return the Blender object |
| `sm(t)`, `spow(x,p)` | smoothstep and signed power helpers for height profiles |
| `tris(ob)` | triangle count |

Palette swatches: a bottom strip of flat colours (`SW` dict in lib/rgen_mesh.py, shared by reference; the Crystal Vanguard example overrides it with 8 swatches). Name a swatch string where a UV rect is expected. Colours of the Crystal Vanguard example come from `examples/crystal-vanguard/palette.py` (`C()` themes every authored colour; edit `THEME` for a new set).
Simple path (about 1 min; since r11 it also writes meta.json and bakes Cycles AO at 512 px, ~4 s for 4 items): `examples/crystal-vanguard/run_all.sh <tag>` runs make_clothing_cv -> make_face_cv -> build_cv -> paint_cv -> render_cv -> compose_cv -> release_cv in that order (build BEFORE paint: the painter reads meta.json). `render_cv.py export=1` prints per item tris, bbox, open edges and PASS/FAIL against the Slender boxes; `texel_density.py` prints px/stud per painted region (u and v) and fails if the u/v ratio leaves 0.8..1.25 (Studio has no anisotropic filtering: anisotropic UVs smear); `sheet(..., v_rows=)` + `iso_rect()` (build_cv.py) give isotropic layouts; `clip_check.py` (Blender, on out/cv_build.blend) counts overlapping triangle pairs between items.
`sheet()` also accepts `pole_row0=True` (collapse the first row to a point, for domes) and `rim_skip_cols`. Heavy path (distance-band trims, AO): `examples/tidewatch-warden/`.

## Importing a GLB blockout safely
Snapshot `set(bpy.data.objects)` before `bpy.ops.import_scene.gltf(filepath=...)`, take only the new MESH objects, then delete empties/"world" parent. Delete children before parents.
Axis: the starter sword imports lying along **-Y** (tip y=-4.12, pommel y=+0.14). Map to Roblox-up with (x, y, z) -> (x, z, -y) before exporting.

## Shared helpers in lib/rgen_mesh.py (moved out of crystal-vanguard 2026-11-09; import them, never copy)
| Helper | Use |
|---|---|
| `iso_rect(grid, u0, u1, v1, S, min_frac=0.5, v_scale=1.0)` | UV rect + per-row v positions with EQUAL texel density in u and v (pass `v_rows=` to `sheet()`); Studio smears anisotropic layouts |
| `bipyramid(b, base, axis, w, h, sides=6, mid=0.35, swatches=...)` | faceted crystal / spike / shard |
| `bake_ao(ob, size, others, out_dir, samples=24)` | Cycles AO bake into the item's atlas -> out_dir/ao_<item>.png |
| `body_proxy(shirt_png, pants_png, face_png=None, head_c=0.576)` | textured block R15 body (+ face plane) for renders and clip checks |
| `tex_material(me, name)`, `tris(ob)` | empty node material for painters; triangle count |

## Swatch names the helpers expect (alias them in your set's SW, as build_cv.py does)
`extrude(..., uv_side="bronze")`, `gem(col="aqua")`, `sheet(rim="bronze")` default to Tidewatch names; `bipyramid()` defaults to
`crystal`, `ice`, `sapphire`. A new set either keeps Crystal Vanguard's 8 cells (gold, silver, crystal, navy, ice, sapphire,
white, gold_dark + aliases bronze/pearl/aqua/dark) and recolours them in its painter, or passes its own names explicitly.

## Long thin parts (staff shafts, antlers, tubes)
Build them as `sheet()` grids around a path (closed_u=True); for isotropic UVs give the rect a u width proportional to the
circumference: `iso_rect()` computes the height, and raises if the rect would not fit; widen u0..u1 rather than shrink it.

## Checks for any set (run them every round; crystal-vanguard/run_all.sh runs both at the end)
- `python3 scripts/texel_density.py examples/<set>`: u/v texel density per painted region, exit 1 outside 0.8..1.25.
- `blender -b examples/<set>/out/<build>.blend -P scripts/clip_check.py` (the .blend your build_*.py saves, e.g. out/cv_build.blend): every item pair + item vs body overlap counts.
- Export check: copy `render_cv.py`'s export block (tris, open edges, size box per item vs `LIMITS`, PASS/FAIL).
- Blender exits 0 when a script raises: always call it with `--python-exit-code 1` in run scripts.

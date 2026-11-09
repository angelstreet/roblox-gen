# Pipeline overview

| Stage | Skill | Output | Gate |
|---|---|---|---|
| 1. 2D assets | `skills/roblox-2d-concept` | concept refs, `SPEC.md`, shirt/pants PNG, 2D preview | spec + 585x559 PNGs + template overlay |
| 2. 3D assets | `skills/roblox-avatar-fashion` | Blender meshes, UV textures, FBX per accessory, render sheet | triangle budgets, bbox limits, render sheet with 5 views |
| 3. Test | same skill (Studio section) | private upload, worn on R15/R6/Rthro rigs, animation poses, screenshots, `ugc_check.lua` | fit, scale, textures, clipping noted honestly, Marketplace limits pass |
| 4. Experiences | `experiences/README.md` | Studio-built places (showroom with try-on) | Play-mode test with screenshots |

Shared code: `lib/rgen_mesh.py` (Blender Builder, swatches, body proxy) and `lib/rgen_clothing.py` (Face painter). One-command builds: `examples/<set>/run_all.sh <tag>`.

Starter sets live in `starter/` (`starter/crystal-vanguard/` is the input kit; its finished build is `examples/crystal-vanguard/`). Worked examples live in `examples/`. Publishing and fees are never automatic.

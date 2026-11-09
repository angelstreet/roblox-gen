---
name: roblox-2d-concept
description: Stage 1 of the roblox-gen pipeline - turn a text brief and AI concept art into a canonical design spec and the 2D assets (turnaround references, palette, classic shirt/pants PNGs painted on the official templates, weapon orthographic sheet). Use BEFORE any Blender work, or when asked to make Roblox concept art, clothing textures or a design spec.
---

# Stage 1: 2D assets first (concept -> spec -> 2D textures), then 3D

Full pipeline: **1. 2D** (this skill) -> **2. 3D** (`roblox-avatar-fashion` skill: Blender meshes, FBX, upload) -> **3. Studio test**.
Never start 3D before the 2D gate below is passed. A concept image is NOT a UV texture and NOT geometry.

## Inputs
- A text brief or the starter kit in `starter/<set>/` (concept PNGs, prompts, optional blockout GLB).
- Official Roblox classic clothing templates (585x559). The face rectangles are in the `roblox-avatar-fashion` skill; `examples/tidewatch-warden/make_clothing.py` already has the `Face` painter and the exact rectangles.

## Steps
1. **Concept art** (human or image AI; an agent without an image generator asks the human). Prompts live in `starter/crystal-vanguard/crystal_vanguard_prompts.md` (A avatar, B weapon, C materials, D clothing, E consistency). Save approved front/side/back images under `starter/<set>/2d/`.
2. **Canonical spec** `starter/<set>/SPEC.md`: palette hex list, motifs, one row per product (shirt, pants, each 3D accessory, weapon) with its Roblox attachment, silhouette notes, triangle budget. Extract colours from the images with Pillow (`Image.quantize`), do not guess.
3. **Clothing PNGs**: paint on the official template UV regions with the 4x-per-face method (shadows baked first, 3-stop metal ramp, glow layer, LANCZOS down). Outputs `shirt.png` and `pants.png`, 585x559 RGBA. Overlay the template to check alignment.
4. **Weapon/accessory sheets**: if the human supplied orthographic sheets, keep them as references; otherwise derive simple front/side silhouettes from the spec.
5. **2D gate (all must be true)**: palette in SPEC.md; shirt/pants PNG exactly 585x559; template overlay image saved; every 3D accessory listed with attachment; a `2d_preview.png` that shows shirt+pants mapped on a block R15 (use the Blender proxy: `examples/crystal-vanguard/render_cv.py ... preview2d=1`; `render_preview.py` belongs to the old v1 pipeline and does not work for new sets). Then go to stage 2.

## Using the Face painter with a new palette
`from make_clothing import Face` paints one template face on a 4x canvas; its defaults are Tidewatch bronze/aqua. Pass your own colours: `metal()` takes a 3-stop ramp `top/mid/bot` (see `examples/crystal-vanguard/make_clothing_cv.py` for gold, silver and sapphire ramps). Check palette use with `python3 scripts/check_palette.py <png> <hex>...`.

## Rules
- Originality: no franchise characters, logos, text. References are a quality bar only.
- Honest status: say what is generated vs. only drafted. Do not claim Studio tests you did not run.

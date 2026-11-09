# Ember Warden (cold Sonnet test, 2026-11-09)

Original obsidian-and-ember set, built by a Sonnet agent working only from this repo's docs: horned helm with flame locks,
spiked rock pauldrons, tattered cape, obsidian collar, crescent molten axe, plus shirt, pants and face.

- Checks: every item passes size boxes (Classic/Normal/Slender), tris, watertight, texel density and clip_check.
- Studio: uploaded privately and tested on R15 (`docs/studio/wear_ember_warden.lua`); clean apart from a small nape
  sliver under the helm. Painted detail is about 80% of Crystal Vanguard r27.
- Textures: `textures/tex_ew_*.png` (colour) and `textures/emit_ew_*.png` (emissive masks); the left pauldron uses the right one's.
- Rebuild: `./run_all.sh <tag>` (Blender headless, ~2 min; `NOBAKE=1` skips AO). Glow tint: `Color3.fromRGB(255, 130, 40)`.

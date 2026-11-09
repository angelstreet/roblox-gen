# Handover (2026-11-09, end of session 3) - continue roblox-gen

Repo: https://github.com/angelstreet/roblox-gen (public, MIT). Local clone: `~/roblox-gen`. Read `AGENTS.md`, `docs/PIPELINE.md`,
then the two skills in `skills/`. This file is the owner's working note for the next agent session.

## State
- Pipeline: 2D (`skills/roblox-2d-concept`) -> 3D (`skills/roblox-avatar-fashion`) -> Studio test -> experiences (`experiences/`).
- Studio MCP works (`execute_luau`, `screen_capture`, `start_stop_play`, ...): call `list_roblox_studios` first, a place must be open.
  All Studio work in session 3 was done through it, no screen driving.
- **Crystal Vanguard r10** (`examples/crystal-vanguard/`): swept mane (watertight, Hair box), long flared cape, sword lowered into the
  Waist box, emissive glow (SurfaceAppearance masks), face decal, richer clothing filigree. Passes `docs/studio/ugc_check.lua`
  (size boxes at Classic/Rthro Normal/Slender, <= 4000 tris, watertight, 1024 textures). Tested in Studio on R15, R6, Rthro
  scales and walk/run/jump/fall poses (`STUDIO_TEST.md`). Colours are one file: `palette.py` (`THEME`, `SET_NAME`).
- **Tidewatch r4** (`examples/tidewatch-warden/`): cape tucked under the mantle (tab fixed), open-front tail skirt (walk clip fixed),
  side view checked; `run_all.sh <tag>` (~10 min, `NOBAKE=1` ~2.5 min).
- Shared code in `lib/` (`rgen_mesh.py` Builder/swatches/body proxy, `rgen_clothing.py` Face painter); both examples import it.
- **Experiences**: `experiences/showroom/build_showroom.lua` (plinths, turntable, bloom, "Try on" prompt), tested in Play.
- Marketplace limits and fees: `docs/MARKETPLACE_RULES.md` (read 2026-11-09). Nothing was published or paid.
- Cold-agent tests on commit b431738: Haiku 6/10, Sonnet 7/10. Their findings (Linux BLENDER override, tag drift, stale paths,
  ugc_check rig name, emissive cost, palette spread over 3 files, wrong "make your own set" path, title overlap) were fixed after.

## Rules from the owner
- Autonomous: do the next step, do not ask "should I continue". Ask only for money, credentials, publishing, deleting shared data.
- Never publish to the Marketplace or pay fees. Private uploads to the owner's account are fine (Open Cloud key in
  `~/.config/tidewatch/.env`, never print it). Private asset ids live in the wear scripts and STUDIO_TEST.md / README files.
- References are a quality bar only; no copying other creators' outfits. Keep reference comparison images private.
- Use cheaper models for builds when possible (Haiku/Sonnet) and judge results by looking at renders / Studio screenshots.

## Next steps (in order)
1. Re-run a cold Haiku and a cold Sonnet on a fresh clone (scratch dir, no uploads, no Studio) to confirm the fixes; target 9/10.
2. Rigid cape/skirt vs the run back-kick: try layered clothing (cages via the Studio Accessory Fitting Tool / WrapLayer) for the
   Crystal Vanguard cape and Tidewatch skirt; compare clipping with `docs/studio/pose_anim.lua`.
3. Crystal Vanguard polish: hair side view is a dense block over the ear; pauldrons cover the whole torso side; decide which items
   really need emissive (each emissive upload is 500 Robux and the advances are 5x, see MARKETPLACE_RULES.md).
4. Tidewatch: R6/Rthro test, emissive masks for its aqua gems, a face decal; port it to `palette.py`-style theming.
5. Experiences: a photo booth (emote poses + camera path) and a human press-E check of the showroom prompt (MCP key presses do
   not reach ProximityPrompts; the automated test uses the `TryOn` BindableFunction).
6. Ask the owner before any Marketplace step: which items to list, glow or not, crown as Hair (1000) or Hat (1500 advance).

## Known traps (details in the skill and experiences/README.md)
- Decal id != image id (resolve with `InsertService:LoadAsset`); fresh uploads need a few seconds ("content representation is being generated").
- Edit-mode animation: `Animator:StepAnimations(dt)` poses a rig; stopping tracks does not restore part CFrames: re-wear the rig.
- Default R15 head is a dynamic MeshPart head: face decals go on a welded plate with Transparency 0.98 (1 = not drawn).
- `Lighting.Technology` is not readable/writable from the MCP thread; `_G` is not shared between Scripts and MCP code.
- macOS: `sed -i ''`; no pipes after `git push` in this machine's shell hook.

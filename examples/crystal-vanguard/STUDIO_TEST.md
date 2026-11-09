# Crystal Vanguard r7 - Studio fit test

**Status (2026-11-09): uploads DONE, Studio wear test NOT DONE.** The Studio step was blocked: Studio opened on its Home screen
(a canvas with no accessibility elements), the background `app_*` tools cannot click the "Baseplate" template tile, and the
full-screen control approval prompt timed out twice (nobody at the keyboard). Nothing below was measured in Studio.
No measurements, screenshots, clipping or scale findings exist yet; do not treat the set as Studio-verified.

## Private test uploads (owner account, 2026-11-09, Open Cloud, moderation not checked yet)
| Item | FBX Model id | Texture Decal id (resolve to image id with InsertService) |
|---|---|---|
| Crystal crown + hair | 103085628642625 | 134139041954755 |
| Pauldron R | 101325492073648 | 99098738461939 (shared with L) |
| Pauldron L | 91788567476911 | 99098738461939 |
| Sapphire cape | 129063076131913 | 94334699278170 |
| Navy scarf | 89732359696876 | 139046121543345 |
| Crystal Vanguard blade | 127694122813832 | 83328938307996 |
| Shirt | - | 73359961877284 |
| Pants | - | 95673074413632 |
Pauldron L has no texture of its own: `paint_cv.py` writes only `tex_cv_pauldron_r.png`, the L mesh is its mirror and reuses it.

## To finish the test (about 5 minutes)
1. In Studio: Home screen > Baseplate (a human click is enough; or open any place).
2. Paste `docs/studio/wear_crystal_vanguard.lua` into the command bar and Run (command bar needs `overwrite_existing` when driven by an agent).
3. Check front/back/3-4/side views; read each MeshPart `Size` in Output and compare with the Blender numbers in NOTES.md
   (crown 2.24 x 2.45 x 1.56, pauldron 1.86 x 1.69 x 1.91, cape 2.25 x 1.43 x 3.16 [x, y(depth), z(height) in Blender axes; Studio reports Roblox axes], scarf 1.70 x 1.58 x 0.94, sword 2.14 x 0.51 x 2.92; importer sizes differ a few percent).
4. Record: clipping (sword vs cape/pauldrons, hair vs crown), floating parts, textures missing, scale. Add screenshots under `docs/studio/`.

## Expected risks to look at first (from the Blender side, unverified)
- Crown depth 2.45 is close to the 2.5 hat limit.
- Sword pose offsets were derived from the Tidewatch WaistFront attachment, not measured on WaistBackAttachment.
- Cape 3.16 tall: back-accessory limits are unchecked.

## Result (2026-11-09, Roblox Studio 0.746, R15 rig, private uploads, run by hand)
Worn with `docs/studio/wear_crystal_vanguard.lua`: shirt, pants, crown, both pauldrons, cape, scarf, sword. Screenshots in `docs/studio/` (cv_front, cv_back, cv_side_before/after_sword_fix).

| Check | Result |
|---|---|
| Textures on all meshes, shirt and pants on the template | OK (first load printed "Asset content representation is being generated": the meshes need a few seconds after upload, re-run if parts are bare) |
| Front view | Matches the Blender sheet: layered pauldrons with gold rims and gems, navy sleeves with gold lines, white chest armor, crown and hair sit correctly on the head |
| Back view | Cape with emblem and scalloped hem, sword diagonal over the cape: matches Blender |
| Side view | **Problem found**: with the r7 pose the sword floated about 1 stud behind the cape (sword centre 1.66 studs behind the UpperTorso centre). Cause: pose offset y=1.80 was too far back. Fixed in `build_cv.py` (P0 y 1.80 -> 1.40, clip_check: 0 overlaps), re-uploaded, sword centre now 1.25 behind the torso centre and touching the cape. |
| Measured sizes in Studio (x, y, z studs) | cape 2.19 x 3.36 x 1.43; neck/scarf 1.65 x 1.00 x 1.59; sword 2.13 x 2.92 x 0.51; crown 2.17 x 1.53 x 2.37 (Blender 2.24 x 2.45 x 1.56: Studio y/z are swapped vs Blender z/y) |

Sword v2 FBX asset id: 114719164350379 (the earlier 127694122813832 had the floating pose).

Not tested: animations (walk, jump), R6, Rthro, UGC validation tool, in-game camera. The cape is 3.36 studs tall; the marketplace limits for back accessories were not checked, verify before any listing.

## Re-run through the Studio MCP (2026-11-09, no clicking)
`docs/studio/wear_crystal_vanguard.lua` run with `execute_luau` (Edit datamodel), views taken with `screen_capture` and
explicit camera/look-at positions (rig at (0,5,0), faces -Z). Screenshots: `docs/studio/mcp_cv_{front,back,side,q34}.jpg`.
- All six meshes, shirt and pants loaded and textured on the first run.
- Sizes (Studio x, y, z): crown 2.17 x 1.53 x 2.37, pauldrons 1.86 x 2.03 x 1.69, cape 2.19 x 3.36 x 1.43,
  scarf 1.65 x 1.00 x 1.59, sword 2.13 x 2.92 x 0.51 (same as the hand run; the pauldron's y/z order is the importer's).
- Front/back/3-4 match the Blender sheet. Side: sword lies against the cape (r9 pose holds). Seen for the quality pass:
  hair spikes stick straight back like a comb, pauldrons cover the whole torso side, a scarf strap hangs right of the collar.

## Animations, R6, Rthro (2026-11-09, Studio MCP, edit mode)
Method: `docs/studio/pose_anim.lua` plays a default R15 animation on the anchored rig and steps it to one frame with
`Animator:StepAnimations` (no Play mode needed), then `screen_capture` from fixed cameras. Screenshots in `docs/studio/anim/`.

| Pose (default R15 anim, frame) | Result |
|---|---|
| Walk 0.17 / 0.50 | OK. Pauldrons follow the arms, cape and sword stay clear of the legs (legs reach <= 0.47 behind torso centre). `walk_q34back.jpg` |
| Run 0.12 | OK |
| Run 0.37 (back kick) | **Clips.** Right shin/foot reach 1.43/1.74 studs behind the torso centre, the cape's back face is ~1.3: the boot passes through the lower cape (`run_back_clip.jpg`, `run_side_clip.jpg`). Same problem every rigid Roblox cape has; fixes: flare the lower cape further back (>= 1.8) or end it above the knee-kick zone, or make it layered clothing. |
| Jump 0.15 | OK, legs tuck under the cape, sword clear (`jump_q34back.jpg`); pauldron inner rims touch the chest edge a little (`jump_front.jpg`) |
| Fall 0.30 (arms up) | Minor: the raised pauldron reaches head height and touches the crown band from the side (`fall_side.jpg`) |

Bodies (`docs/studio/wear_crystal_vanguard.lua` with its CONFIG block):
| Body | Result |
|---|---|
| R6 | OK, every item attaches (R6 has the same attachment names); sizes stay at the raw Blender values (`r6_q34.jpg`) |
| R15 Rthro Normal (BodyTypeScale 1, ProportionScale 0) | OK, accessories auto-scale (cape 4.14 tall, pauldrons 2.10 x 2.56) (`rthro_normal_q34.jpg`) |
| R15 Rthro Slender (BodyTypeScale 1, ProportionScale 1, Height 1.05) | OK (`rthro_slender_q34back.jpg`) |
Not covered: real Rthro mesh bundles (only Rthro body scales on the blocky parts), in-game Play mode, emotes.

## Marketplace pre-check (2026-11-09, `docs/studio/ugc_check.lua` on the unscaled R6 rig, rules in `docs/MARKETPLACE_RULES.md`)
| Item (type) | Box W x H x D, extents from attachment | Classic | Rthro Normal | Rthro Slender | Tris | Watertight | Texture |
|---|---|---|---|---|---|---|---|
| Crown + hair (Hat) | 2.24 x 1.56 x 2.45; 1.58 behind | FAIL (behind 1.58 > 1.50) | FAIL (W, D) | FAIL | 2768 | **NO** (256 open edges) | 1024 |
| Crown + hair (as Hair) | same | ok | FAIL (W 2.24 > 1.87, behind 1.58 > 1.25) | FAIL | | | |
| Pauldron R / L (Shoulder) | 1.86 x 1.91 x 1.69 | ok | ok | ok | 3976 | yes | 1024 |
| Cape (Back) | 2.25 x 3.16 x 1.43; 1.89 down | ok | ok | ok | 3540 | yes | 1024 |
| Scarf (Neck) | 1.70 x 0.94 x 1.58 | ok | ok | ok | 844 | yes | 1024 |
| Sword (Waist) | 2.14 x 2.92 x 0.51; 1.96 up | FAIL (up > 1.5) | FAIL (up > 1.84) | FAIL (up > 1.41) | 1858 | **NO** (10 open edges) | 1024 |
All Plastic, Transparency 0; the only extra child is the engine-added `OriginalSize` (added by Humanoid scaling, not in the asset).
To fix in the next build: crown+hair <= 1.78 wide and <= 1.19 behind its attachment (submit as Hair), closed shells;
sword moved down >= 0.55 so it stays <= 1.41 above WaistBack, closed shells. The cape may grow ~1.6 studs longer (Back: 3.5 down Classic).
The real validator (Save to Roblox > Avatar Asset) was not run: it is the paid upload flow.

## r10 (2026-11-09, Studio MCP; shots `docs/studio/r10/`; wear script = r10 ids)
New private uploads: crown+mane FBX 129396675939617, cape FBX 117927101168588 + texture Decal 84307101637758, sword FBX 107433499133729,
shirt 137926471035226, pants 128873900212839, face 135398494225892, emissive masks (Decal) crown 125615870753450,
pauldron 111757635753589, scarf 90049570495779, cape 111720663243190, sword 92076649973247.
- `ugc_check.lua` on R6: every item passes Classic/Normal/Slender (crown as Hair), 0 open edges, all <= 3976 tris.
- Looks (front/back/3-4): matches the r10 Blender sheet; emblem and crystals glow crisply; face reads; long cape visible beside the legs from 3/4.
- Run 0.34 (peak back-kick): the boot still passes through the lower cape (`run_kick_clip.jpg`). Walk/jump/fall not re-shot (cape and sword changed only below/behind the r9 positions).
- Face trap: the default R15 head is a dynamic MeshPart head; a Decal on it maps into the mesh UVs (a speck on the cheek) and its TextureID carries the default face.
  Fix used: TextureID = "" and the face Decal on a 0.05-thick plate welded in front, Transparency 0.98 (at 1 the decal is not drawn).

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

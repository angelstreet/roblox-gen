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

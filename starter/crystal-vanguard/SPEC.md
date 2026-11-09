# Crystal Vanguard - canonical spec (the exact target)

Original silver-white crystal knight. Source art: `2d/crystal_vanguard_full_concept.png`, `2d/crystal_vanguard_avatar_reference.png`, `2d/crystal_vanguard_weapon_reference.png`, blockout `3d/crystal_vanguard_sword_blockout.glb`.
Only the concept art's *design language* is the target; build everything fresh (no tracing of the AI image into textures).

## Palette (use exactly)
| Role | Hex |
|---|---|
| silver-white armor | #F8F9FF |
| pale ice highlight | #CAD8FF |
| gem / glow blue | #2E6BFF |
| deep navy cloth | #0D1B4D |
| gold trim | #D4AF37 |
Extra shades may be derived (darker/lighter) from these; blade core cyan about #42B2FF..#90E3FF as in the blockout.

## Products
| # | Product | Type | Attachment | Notes |
|---|---|---|---|---|
| 1 | Crystal Vanguard Shirt | classic shirt 585x559 | - | white armor chest plate, gold edging, central diamond gem, navy undercloth/sleeve cuffs, shoulder plate print |
| 2 | Crystal Vanguard Pants | classic pants 585x559 | - | navy leggings, white/gold knee+thigh plates, dark boots with gold trim and small gems |
| 3 | Crystal Crown | 3D accessory | HatAttachment | angular crown of small ice-blue crystal spikes with gold band, fits over messy white hair (hair is part of the mesh or omitted: say which) |
| 4 | Vanguard Pauldrons R/L | 3D accessory x2 | Right/LeftShoulderAttachment | layered white plates, gold rim, blue diamond gem |
| 5 | Sapphire Cape | 3D accessory | BodyBackAttachment | royal blue, gold scalloped hem, glowing crystal emblem on the back, optional white fur-like collar |
| 6 | Navy Scarf | 3D accessory | NeckAttachment | navy cloth, small gem clasp (may be merged with cape collar) |
| 7 | Crystal Vanguard Blade | 3D accessory (wearable on back) | WaistBackAttachment | built from the blockout, see below |
Optional stretch: the sword as a handheld Tool (`Handle` + grip), documented separately.

## Sword (Crystal Vanguard Blade)
Faceted translucent cyan blade with central ridge, gold-and-sapphire crossguard with large central diamond crystal and two wings with gems, deep-blue wrapped grip (rings), gold collars, diamond pommel.
Start from the 28-part GLB: import with Blender (`bpy.ops.import_scene.gltf`), refine facets (add bevels/ridge), join by material, UV unwrap, 1 texture or palette atlas, <= 4000 tris, origin at the attachment point. Real blockout numbers: total length 4.26 units (blade 2.65, guard 1.7 wide, grip about 0.82). It imports lying along -Y (tip y=-4.12): rotate it upright, scale it (about 0.85) so it stays within accessory limits, and pose it diagonally behind the cape (a cold Sonnet run used tilt about 35 deg, offset +0.9 behind the attachment). Snapshot scene objects before importing the GLB, see docs/BUILDER_CHEATSHEET.md.
WaistBackAttachment in neck-frame coordinates: (0, 0.502, -2.098) (mirror of WaistFront).

## Size limits (verify on create.roblox.com before publishing)
Hat-class accessories: about 1.87 x 2.5 x 1.87 studs, <= 4000 tris each. Back/waist/shoulder items have their own limits: keep them close to the body and tell the human the measured bbox. Keep the white collar a separate item or small: a merged collar made the cold-agent cape 5 studs tall, probably too big.
Write one line in NOTES.md saying whether the hair is part of the crown mesh.

## Quality bar for the render sheet
Front, 3/4, side, 3/4 back, back on the block R15 proxy; palette recognisably the same as the concept (white/blue/gold); every product visible; no black or empty frames. Compare against `2d/crystal_vanguard_full_concept.png` privately.

## How to build it
A first cold-agent build exists in `examples/crystal-vanguard/` (`./run_all.sh <tag>`, about 20 s; uses `blender` on PATH, or set `BLENDER=/path/to/blender`). Improve it, do not start over. Weak points are listed in its NOTES.md. API: `docs/BUILDER_CHEATSHEET.md`. Follow `skills/roblox-2d-concept` first, then `skills/roblox-avatar-fashion`. Do not upload or spend anything without the human's yes.

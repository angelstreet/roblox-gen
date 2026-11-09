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
Start from the 28-part GLB: import with Blender (`bpy.ops.import_scene.gltf`), refine facets (add bevels/ridge), join by material, UV unwrap, 1 texture or palette atlas, <= 4000 tris, origin at the attachment point. Same length proportions as the blockout (blade about 2.5 units, guard 1.7 wide).

## Quality bar for the render sheet
Front, 3/4, side, 3/4 back, back on the block R15 proxy; palette recognisably the same as the concept (white/blue/gold); every product visible; no black or empty frames. Compare against `2d/crystal_vanguard_full_concept.png` privately.

## How to build it
Copy `examples/tidewatch-warden/` to `examples/crystal-vanguard/` and replace palette, emblem and meshes (see `build_v5.py` item builders, `paint_v5.py` textures, `make_clothing_v5.py` for the shirt/pants). Follow `skills/roblox-2d-concept` first, then `skills/roblox-avatar-fashion`. Do not upload or spend anything without the human's yes.

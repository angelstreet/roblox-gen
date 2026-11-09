# Crystal Vanguard (built by a cold agent from SPEC.md)
Run `./run_all.sh r3` (make_clothing_cv.py -> paint_cv.py -> build_cv.py -> render_cv.py -> compose_cv.py, ~30 s total). Outputs go to `out/`; the
files in this folder are copies of the final ones. Render sheet: `render_sheet.png`. 2D preview: `2d_preview.png` (block R15 front/3/4/back + both PNGs).

| Product | File | Attachment | Tris | Notes |
|---|---|---|---|---|
| Shirt / Pants | crystal_vanguard_shirt.png / _pants.png (585x559) | - | - | painted on the official rects with the Face painter |
| Crystal Crown | crystal_crown.fbx | HatAttachment | 2184 | gold band + 12 crystal spikes + 2 temple crystals; **hair IS part of the mesh** (cap + ~46 spikes) |
| Pauldron R / L | vanguard_pauldron_r.fbx / _l.fbx | Right/LeftShoulderAttachment | 3212 each | 3 white tiers, gold rims, blue gem, 3 crystal shards |
| Sapphire Cape | sapphire_cape.fbx | BodyBackAttachment | 3540 | royal blue, scalloped gold hem, crystal emblem texture, white fur-like collar (in the same mesh, makes the bbox 5.05 tall) |
| Navy Scarf | navy_scarf.fbx | NeckAttachment | 1276 | high collar ring + V lappet + gold clasp with crystal |
| Crystal Vanguard Blade | crystal_vanguard_blade.fbx | WaistBackAttachment | 1858 | 27 blockout parts kept (gold parts bevelled) + blade rebuilt (10-gon ridge sections, 11 stations); scaled 0.85, posed diagonally on the back |

## Weak points
- Hair is a boxy cap with spikes; no hand-sculpted strands. Face is two black squares (proxy only).
- Pauldrons read as puffy white pillows, not layered plates; engraving is texture only. Gems are small.
- Crystals are not truly glowing in the FBX (no emission in FBX); the render adds emission only to the sword. No bloom.
- Cape is one big sheet with collar; bbox 3.35 x 1.78 x 5.05 probably exceeds Roblox accessory size limits (not checked). Sword 2.14 x 0.51 x 2.92.
- Not tested in Studio, no cages/layered clothing, attachment offsets (sword y +0.9 behind the attachment) unverified.
- Shirt/pants: gem and filigree small, lacks the concept's navy-heavy sleeves and swirling gold lines. Pants torso region only partly visible.

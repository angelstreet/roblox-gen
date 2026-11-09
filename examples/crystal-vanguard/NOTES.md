# Crystal Vanguard (built by a cold agent from SPEC.md)
Run `./run_all.sh <tag>` (the tag, e.g. r1, is required; on Linux set BLENDER=; order is make_clothing_cv -> paint_cv -> build_cv -> render_cv -> compose_cv) (make_clothing_cv.py -> paint_cv.py -> build_cv.py -> render_cv.py -> compose_cv.py, ~30 s total). Outputs go to `out/`; the
files in this folder are copies of the final ones. Render sheet: `render_sheet.png`. 2D preview: `2d_preview.png` (block R15 front/3/4/back + both PNGs).

| Product | File | Attachment | Tris | Notes |
|---|---|---|---|---|
| Shirt / Pants | crystal_vanguard_shirt.png / _pants.png (585x559) | - | - | painted on the official rects with the Face painter |
| Crystal Crown | crystal_crown.fbx | HatAttachment | 2768 | gold band + 12 crystal spikes + 2 temple crystals; **hair IS part of the mesh** (rounder cap + 64 curved swept-back tufts) |
| Pauldron R / L | vanguard_pauldron_r.fbx / _l.fbx | Right/LeftShoulderAttachment | 3976 each | 3 separate plates with gaps over a navy underlayer, gold rim ring per tier, big gem in gold frame, 3 shards |
| Sapphire Cape | sapphire_cape.fbx | BodyBackAttachment | 3540 | royal blue, scalloped gold hem, glowing crystal emblem texture, small white collar in the same mesh; 2.25 x 3.16 |
| Navy Scarf | navy_scarf.fbx | NeckAttachment | 844 | small neck ring + short chest tail + gold clasp with small crystal |
| Crystal Vanguard Blade | crystal_vanguard_blade.fbx | WaistBackAttachment | 1858 | 27 blockout parts kept (gold parts bevelled) + blade rebuilt (10-gon ridge sections, 11 stations); scaled 0.85, posed diagonally on the back |

## Round 2 (Haiku, 4 targeted edits, each re-rendered and checked)
Sword lifted clear of the cape (P0 y 1.30 -> 1.95); cape collar shrunk to a thin band; pauldron gem bigger and gold rim visible (still pillow-like tiers); sleeves now navy with gold filigree, chest swirls added. Cape still about 5 studs tall (too big).

## Weak points
- Hair is a boxy cap with spikes; no hand-sculpted strands. Face is two black squares (proxy only).
- Pauldrons read as puffy white pillows, not layered plates; engraving is texture only. Gems are small.
- Crystals are not truly glowing in the FBX (no emission in FBX); the render adds emission only to the sword. No bloom.
- Cape is one big sheet with collar; bbox 3.35 x 1.78 x 5.05 probably exceeds Roblox accessory size limits (not checked). Sword 2.14 x 0.51 x 2.92.
- Not tested in Studio, no cages/layered clothing, attachment offsets (sword pommel placed at y=1.95 in `place_sword()` of build_cv.py) unverified.
- Shirt/pants: gem and filigree small, lacks the concept's navy-heavy sleeves and swirling gold lines. Pants torso region only partly visible.

## Round 3 (Sonnet, r2..r7, each re-rendered and looked at; sheet `render_sheet.png` = r7)
Measured with `render_cv.py` export (bbox relative to the attachment, studs; FBX scale 0.01):
| FBX | Tris | bbox x / y / z (size) |
|---|---|---|
| crystal_crown | 2768 | -1.12..1.12 / -0.86..1.58 / -0.98..0.58 (2.24 x 2.45 x 1.56) |
| vanguard_pauldron_r / _l | 3976 each | -0.99..0.86 / -0.82..0.87 / -1.42..0.49 (1.86 x 1.69 x 1.91), L mirrored |
| sapphire_cape | 3540 | -1.12..1.13 / -0.62..0.81 / -1.89..1.27 (**2.25 wide x 3.16 tall**, 1.43 deep) |
| navy_scarf | 844 | -0.85..0.85 / -0.85..0.73 / -0.60..0.34 (1.70 x 1.58 x 0.94) |
| crystal_vanguard_blade | 1858 | -1.25..0.89 / 0.90..1.40 / -0.95..1.96 (2.14 x 0.51 x 2.92) |
1. r2 Pauldrons: 3 distinct plates (top dome z 0.26..-0.28, tiers at -0.40..-0.74 and -0.86..-1.18, each wider) with 0.10 gaps showing a navy underlayer; a separate protruding gold rim ring (pointed on the outer side) under every tier; gem 0.17 x 0.30 in a gold diamond frame on the middle tier. Clearly better than pillows. Tris went 3212 -> 3976 (kept under 4000 with 26 segments).
2. r3 Cape: top/bottom width 1.95/3.35 -> 1.50/2.25, length 3.8 -> 2.2, flare 0.8 -> 0.5, shallower scallops; emblem moved up in the texture. bbox 5.05 -> 3.16 tall, 3.35 -> 2.25 wide. Hem now ends at the hips; the sword covers part of the lower emblem area.
3. r4 Scarf: big bib replaced by a ring around the head base (rows z 0.34..-0.07) plus a 0.13 wide short tail and a 0.11 gold clasp with a small crystal. 1276 -> 844 tris. Reads as a neat scarf, thinner than the concept's thick wrap.
4. r5 Hair: superellipse exponent 4 -> 3.2 (rounder), 46 straight 4-sided spikes -> 64 curved 3-ring tufts swept back/up (tips curl back). Reads as messy swept-back spikes from front/side; the back view is still a clumpy mass. Head fit unchanged (cap R 0.71 around the 1.16 head box, nothing floating); the longest back tufts reach y +1.58 (crown depth 2.45, close to the 2.5 hat limit).
5. r6 Glow (textures only): swatches crystal/ice/sapphire lightened (crystal 70,180,255 -> 120,212,255; ice -> 228,242,255), white core + larger halo behind the cape emblem, blue halo behind the pauldron gem, lighter blade/core/crystal bands. Render-only emission on the sword (0.35) is unchanged and is NOT in the FBX. Modest gain: gems are lighter, halos are weak in-engine-like lighting.
6. r7 Sword pose (WaistBackAttachment, neck frame): sword mesh scaled 0.85, rotated RotY(-36 deg) then RotX(+6.5 deg), translated P0 = (0.80, 1.80, -2.95) (was y 1.95). `clip_check.py` (BVH overlap, run with `Blender -b out/cv_build.blend -P clip_check.py`) reports 0 intersecting triangle pairs against cape, both pauldrons, scarf, crown and body proxy. Visible from the back and side; hidden behind the body in front view, as intended. Gap to cape about 0.1 stud.
Still open: no Studio test, no cages, sword pose unverified in Roblox, face is a proxy, pants/shirt untouched this round.

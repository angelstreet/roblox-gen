# Crystal Vanguard (current: r21, see Rounds 5-6 at the end; Studio results in STUDIO_TEST.md are from r10)
The tables and "Weak points" right below are the round-1 cold-agent build (history, oldest first); numbers there are not current.
Run `./run_all.sh <tag>` (tag required, e.g. r10; uses `blender` on PATH, else the macOS app; override with `BLENDER=/path/to/blender`).
Order: make_clothing_cv -> make_face_cv -> build_cv (meshes, meta.json, Cycles AO) -> paint_cv -> render_cv -> compose_cv -> release_cv (~1 min; `NOBAKE=1` skips the AO bakes). Outputs go to `out/`; the files in this folder are
copies of the final ones under release names: out/cv_shirt.png -> crystal_vanguard_shirt.png, out/cv_pants.png -> crystal_vanguard_pants.png,
out/cv_face.png -> crystal_vanguard_face.png, out/<name>.fbx -> <name>.fbx, out/<tag>_sheet.png -> render_sheet.png. Render sheet: `render_sheet.png`. 2D preview: `2d_preview.png` (block R15 front/3/4/back + both PNGs).

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

## Round 4 (r10, Opus + a Sonnet subagent for the clothing, 2026-11-09; sheet `render_sheet.png` = r10, Studio shots `docs/studio/r10/`)
Driven by the Studio tests (animation clipping, `docs/studio/ugc_check.lua`) and the handover quality list.
Sizes below are Studio order W x H x D (x, y up, z depth); the build's EXPORT lines print Blender order x, y (depth), z (up).
| Item | Change | Result |
|---|---|---|
| Crown + hair | 64 open tufts + temple wings replaced by 70 CLOSED tapered 5-gon strands in 4 groups (swept-up top spikes, back mane of spiky locks flicking outward, thin side locks behind the temples, short fringe under the band), clamped to the Hair box | 3572 tris, watertight, 1.64 x 1.89 x 2.01, passes Hair at Classic/Normal/Slender (as Hat it still fails Normal/Slender depth: submit as **Hair**) |
| Cape | length 2.2 -> 3.4 (hem near the ankles like the concept), bottom 2.25 -> 2.55 wide, flare 0.5 -> 1.15 (v^1.8), deeper folds; emblem moved up (0.40 -> 0.33 of the height) | 4.37 tall, 3.10 below BodyBack (limit 3.5 Classic); run back-kick still grazes it at the peak frame (all long rigid capes do) |
| Sword | blade base capped (was 10 open edges), scale 0.85 -> 0.80, lowered 0.44 so its top is 1.36 above WaistBack | watertight, passes Waist at all three scales |
| Glow | `paint_cv.py` writes emissive masks `out/emit_<item>.png`: crystal + sapphire swatch cells, sword blade/core/crystal bands, cape emblem shapes. In Studio: SurfaceAppearance ColorMapContent + EmissiveMaskContent, strength 1.5, tint (150,215,255) | crisp glowing crystals; first try with colour-threshold masks lit the painted halos and the white collar as blobs (rejected) |
| Face | `make_face_cv.py`: original determined face (silver brows, ice-blue eyes, small smirk) -> proxy head plane in Blender, FacePlate decal on the Studio rig | display only: classic faces are not UGC items |
| Shirt / pants | (Sonnet subagent) gold scroll filigree (S-curves with curls), bevelled plates, navy sleeves with white vambraces, gem belt buckle, dark boots with gold trim | richer; weak: pants torso faces hidden under the shirt, upper sleeves plain (covered by the pauldrons) |
Still open: the run back-kick clip (needs layered clothing or a shorter cape), hair side view is a dense block over the ear, pauldrons cover the whole torso side, emissive items cost 500 Robux to upload instead of 80.

## Round 5 (r11-r18, Fable, 2026-11-09; superseded by Round 6 below) - close the quality gap to the concept and to Tidewatch v5
Method: every round rendered and put next to the owner's concept turnaround (`compare_cv.py <tag>` -> `out/<tag>_vs_concept.png`, private, not
committed) and judged by eye. Ranked gaps at r10: pauldrons (puffy white cylinders), hair (sea-urchin spikes), cape (no lining, no collar, round
scallops, weak emblem), flat swatch materials everywhere (no AO), scarf too thin, legs too white, and the sword FBX was an unwelded triangle soup
(3996 open edges: the blockout parts were copied with fresh verts per face; r10's "watertight" came from a check that did not count edges).
Pipeline change: `build_cv.py` now writes `out/meta.json` (per sheet: UV rect, grid positions, distance-to-edge fields, fold map) and bakes
Cycles AO per item (512 px, ~1 s each, `bake_ao()` as in tidewatch) and `paint_cv.py` paints in physical space (`Tex` class: trims as distance
bands in studs, emblems/filigree projected through positions, AO multiplied with the bake's alpha as the island mask). Build runs BEFORE paint.
`render_cv.py export=1` prints per item tris / bbox / open edges / PASS-FAIL against the Slender boxes. Emissive masks still come from the
swatch cells (crystal, sapphire) plus the projected emblem shapes (cape) and the sword bands.
| Round | Change | Decision |
|---|---|---|
| r11 | Pauldron rebuilt: wide boxy top plate (superellipse E=5) overhanging the shoulder with its outer edge dipping to a point, inner hem raised above the torso, two thinner narrower lames below (open on the torso side), navy underlayer, protruding gold rim per hem, big framed gem on the OUTER face of the top plate, 2 shards at the back. Texture: white + AO, gold hem bands + blue enamel band as distance bands, corner filigree around the gem, enamel diamonds on the lames. Sword parts welded. | kept (3976 -> 3180 tris); fixes: AO outside the UV islands darkened the atlas (use the bake alpha), tier rects widened to the full atlas width (120 -> 200 px/stud), filigree stroke 0.05, enamel only on the outer 3/4 |
| r12 | Cape: top 1.5 -> 1.9 wide (shoulders), 7 triangular hem points + long centre point instead of round scallops, deeper folds exported as a fold map, lining = real UV rect (silver-white, painted from the same positions), tall white collar standing behind the neck (own rects), gold border bands (sides + hem) + inner line, crystal emblem (tall faceted crystal in a gold frame, wing shards, ice lines) projected on the outer face with its own emissive shape mask; 2048 texture | kept; collar was a white cube (too big/boxy) -> r13 |
| r13 | Collar smaller, rounder, rolled. Hair rebuilt: one smooth dome (R 0.74, hem above the collar at the back, over the ears, forehead fringe) + 27 big flat tufts (14 swept up/back, 10 silhouette, 3 bangs) with real UVs (dome rect with painted strand streaks + AO, strand rect root->tip gradient), crown = low gold band, 5 gems, 7 crystals (tall centre, 2 medium, 2 small, 2 temple). Scarf: thick wrap with folds, fold maps + AO + knit weave | kept the direction; rejected details: tufts read as crumpled lumps (frame twisted per ring), scarf covered the mouth and its bib hid the chest gem, crown x 0.91 and scarf y 0.99 out of the box |
| r14 | Tufts: ONE frame per strand (wide along the dome surface, thin radially), longer/thinner (w 0.12-0.15, L 0.55-0.78), 6 sides, every vertex clamped to the Hair box; scarf ring lowered to chin height, tail narrowed and draped to the character's left, clasp moved in | kept: all six items PASS |
| r15 | Clothing: wide navy V tabard with the big gem, white chest plates with scrolls, pointed white skirt flaps over navy below the belt (their tips continue on the pants' legs), legs navy with one pointed knee plate + gem, dark boots with gold trim + gem (was 2 white tile plates per leg); pants torso plain navy under the shirt. Sword blade UVs run along the blade so the band carries ice streaks + a brighter tip, deeper blue -> white ridge ramp | kept |
| r16 | Polish: crown AO 0.5 (dome was grey under the tufts), cape blue deeper (38,72,200)/(10,22,92), lower lames' enamel band narrower (white-dominant like the concept) | kept |
| r17 | Sword pose vs the long cape: `clip_check.py` showed the r10 pose (RotX 6.5, y 1.40) cutting through the cape folds (809 overlapping triangle pairs; the long flared cape of r10 was never re-checked). RotX -36 / y 1.65 was clean but the blade tip stuck out 3 studs behind the shoulders | rejected |
| r18 | RotX +18 (blade forward over the right shoulder, hilt back near the flared hem) + y 1.85: lies along the cape flare, 0 overlaps with cape, pauldrons, scarf, crown and body | kept = final |
Final export (`render_cv.py export=1`, attachment frame, Blender axes x / y depth (+y behind) / z up; all watertight = 0 open edges):
| FBX | Tris | bbox x / y / z | Box (Slender) |
|---|---|---|---|
| crystal_crown (Hair) | 3210 | -0.88..0.88 / -0.89..1.17 / -0.90..0.69 | PASS |
| navy_scarf | 1228 | -0.89..0.91 / -0.86..0.75 / -0.89..0.26 | PASS |
| sapphire_cape | 3740 | -1.35..1.35 / -0.55..1.51 / -2.86..1.42 | PASS |
| vanguard_pauldron_r / _l | 3180 | -1.05..0.93 / -0.82..0.82 / -1.26..0.51 (L mirrored) | PASS |
| crystal_vanguard_blade | 1866 | -1.04..0.89 / 0.33..1.45 / -1.28..1.36 | PASS |
Textures: 1024 (crown, pauldron, scarf, sword), 2048 (cape); shirt/pants 585x559. Hair is still part of the crown mesh.
Still different from the concept (and why): pauldrons still read as three stacked bands rather than one sculpted shell (tri budget and the
two-shell sheet method); hair tufts are low-poly facets, not smooth anime locks (4000 tris for dome + band + crystals + 27 strands); the cape
emblem is smaller than the concept's because the sword crosses the cape's lower half; the sword is 0.80 scale and posed on the back (Waist
box), the concept shows it held; the blade glow is only an emissive mask (no bloom in Studio); shirt/pants are 2D paint only (no 3D
breastplate or boots allowed for classic clothing); the collar is a smooth roll, not fur. Not done this round: Studio re-test (wear script,
animation clipping of the new collar/scarf/tufts), cages/layered clothing, hand-sculpted strands.

## Round 6 (r19-r21, Fable, 2026-11-09; sheet `render_sheet.png` = r21) - coordinator review of r18: back of head, spikes, pauldron silhouette
Judged on `out/<tag>_vs_concept.png` and a head close-up from the back / 3/4 back (`out/r21_head_back_closeup.png`).
| Round | Change | Decision |
|---|---|---|
| r19 | Hair: 9 big spikes (was 13) + 6 silhouette spikes, 7-sided rings, 5 segments, SMOOTH shading (flat shading was the faceted look), silver highlight on the outer face of every strand in the texture; 9 back locks hanging down/out over the nape; 2 side locks per ear; centre crown crystal bigger (0.74) in a gold diamond frame on the band. Collar lowered to a folded hood (top 0.20, dip at the back centre, thicker folds). Pauldron: ONE dominant shell (hx 0.94, cap depth 0.24, flare 0.08, outer point 0.28, NV 11) + one small tucked lame (hx 0.70, z -0.60..-0.86); underlayer shortened; painter for 2 tiers | kept; crown FAILED the Hair front box by 3 cm (centre crystal + frame at y -0.96) |
| r20 | Centre crystal r 0.76, frame at y -0.745 (PASS); back locks 7, alternating long/short, tips flick outward and back | kept, but a skin band still showed at the nape centre between the lock tips and the collar dip |
| r21 | Dome hem reaches the collar at the nape (hem HC-0.32 at the back, hem clamp -0.2 -> -0.5 so the superellipse can go below the equator), collar dip 0.08 -> 0.03 and top row 0.22, lock tips 0.06 lower | kept = final: no skin between hair and collar from any view |
Final export (attachment frame, Blender axes x / y depth (+y behind) / z up; all 0 open edges; `clip_check.py` sword vs cape/pauldrons/scarf/crown/body all 0):
| FBX | Tris | bbox x / y / z | Box (Slender) |
|---|---|---|---|
| crystal_crown (Hair) | 3412 | -0.88..0.88 / -0.92..1.17 / -1.21..0.79 | PASS |
| navy_scarf | 1228 | -0.89..0.91 / -0.86..0.75 / -0.89..0.26 | PASS |
| sapphire_cape | 3740 | -1.35..1.35 / -0.55..1.51 / -2.86..1.28 | PASS |
| vanguard_pauldron_r / _l | 2580 | -1.17..1.03 / -0.89..0.89 / -1.04..0.55 (L mirrored) | PASS |
| crystal_vanguard_blade | 1866 | -1.04..0.89 / 0.33..1.45 / -1.28..1.36 | PASS |
Still different from the concept: spikes are smooth petals rather than razor-sharp anime locks (7-sided tapered tubes, ~70 tris each); the back
locks are 7 tubes, the concept has finer layered strands; the pauldron shell is a superellipse cap, the concept's has a sculpted ridge; the
folded collar is smooth cloth, not fur. Not re-tested in Studio (collar/lock clipping in animation unknown).

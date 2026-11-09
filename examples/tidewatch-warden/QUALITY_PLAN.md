# Tidewatch – path to reference-level quality (plan, 2026-11-08)

Rule for everything below: the reference image is a **quality bar**, not a source. Every shipped piece
(silhouette, emblem, trims, staff, names) must be our own design. "Overly similar to existing items" is an
explicit Marketplace violation, not only an IP risk.

## 0. Official limits used in this plan (checked on create.roblox.com today)

| Item | Limit | Source |
|---|---|---|
| Rigid accessory | 1 mesh, **4,000 tris**, texture <= 2048x2048, Material Plastic, Transparency 0, VertexColor 1,1,1, no extra objects/scripts, no skinning | art/accessories/specifications |
| Layered clothing | 1 mesh, **4,000 tris**, watertight, R15-skinned (<= 4 bones/vertex), `<Name>_InnerCage` + `<Name>_OuterCage`, cage UVs must match Roblox cage templates, max 8x8x8 studs | art/accessories/clothing-specifications |
| Hat box (normal / slender / classic scale) | 1.87x2.5x1.87 / 1.78x2.5x1.78 / 3x4x3 studs, centred on HatAttachment | specifications |
| Hair box (normal) | 1.87 x 3.12 x 2.18 (not centred) | specifications |
| Shoulder via NeckAttachment (normal) | 6.90 x 3.68 x 3.24 | specifications |
| Back (BodyBackAttachment, normal) | 9.86 x 8.59 x 4.87 | specifications |
| Waist (WaistFront/Center/BackAttachment, normal) | 3.94 x 4.29 x 7.57 | specifications |
| Front (BodyFrontAttachment, normal) | 2.95 x 3.68 x 3.24 | specifications |
| Attachment names | HatAttachment, HairAttachment, BodyBackAttachment, BodyFrontAttachment, Waist{Front,Center,Back}Attachment, Right/LeftShoulderAttachment, Right/LeftCollarAttachment, NeckAttachment, FaceFront/CenterAttachment | specifications |
| Fees / access (agent-reported 2026-11-08; current, sourced version: docs/MARKETPLACE_RULES.md) | 80 Robux upload fee, 10–2,500 Robux publishing advance, gov ID + 2-step to upload/publish, **Premium 1000/2200 (or Plus) to publish and keep on sale** | marketplace/marketplace-policy |
| Validation | Runs automatically at upload from Studio: schema, tri budget, bbox, surface area, centring, min thickness, watertight, no N-gons/vertex colours, texture max res, UVs, attachment names/position, cage checks | art/validation-errors |

**Corrections to our README:** the README says 10 Robux per clothing upload; the official policy page now says
80 Robux upload + publishing advance (third-party sites disagree; confirm in Creator Dashboard before paying).
**Our current hood would fail validation:** it is 2.04 studs wide (> 1.87) and its drape reaches ~3.5 studs
below the attachment (> 2.5 box). The fix is to split it into hat + mantle + back cape (section 2a).

**Not verified:** exact Studio menu path for a pre-upload validation run in 0.746 (the docs only say validation
runs on upload; the Accessory Fitting Tool / "Avatar" tab is where it appears in practice); whether classic
Shirt/Pants still have their own size checks beyond 585x559; FBX unit scale on import (measure on first import);
whether Open Cloud "Model" upload of an FBX produces a MeshPart usable as an accessory Handle (test once).

## 1. Gap analysis – what makes the reference look good

Legend: **2D** = classic Shirt/Pants texture · **RIGID** = 3D rigid accessory · **LC** = layered clothing with
cages · **SCULPT** = needs hand sculpt/modelling skill (the procedural route will look cheap).

| # | Element in reference | Why it reads as quality | Route | Our POC today |
|---|---|---|---|---|
| 1 | Hood as **cloth**: tight crown, soft peak, deep shadowed face opening, falls onto shoulders | Mass hugs the head; one big shape; inner shadow frames face | RIGID (hat) + SCULPT for folds | Sphere + cone, 1.7x too big |
| 2 | Hood front trim + forehead sigil | Thin raised bevel catches light; sigil painted, not modelled | RIGID mesh + painted texture | Extruded crescent stuck on front |
| 3 | Mantle/cowl falling over chest and back | Bridges head to torso, hides blocky neck | RIGID (Shoulder/NeckAttachment) | Missing; hood drape tries to do it |
| 4 | Layered shoulder plates (2–3 stacked bevelled slabs with trim edge) | Hard-surface, big readable silhouette, gold rim | RIGID x2 (Left/RightShoulderAttachment), box-modelled (scriptable) | Painted squares on chest |
| 5 | Crossed gold blades / ring behind shoulders | Breaks the box silhouette | RIGID (back or shoulder), scriptable | None |
| 6 | Belt piece with horns, medallion, hanging tabard blade | Strong focal point at the waist | RIGID (WaistFrontAttachment); horns = SCULPT, plate/blade = box-model | Painted belt line |
| 7 | Robe skirt panels that flare past the legs | Volume below waist; on a blocky body this is a **rigid waist accessory**, not 2D | RIGID (waist) or LC DressSkirt on non-blocky bodies | None (flat pants) |
| 8 | Hair: long white strands with beads | Separate tufts, bead accessories | RIGID (hair) + SCULPT; buy-not-make for us | None |
| 9 | Back cape: long panel, gold hem, big emblem, sits *on top* of the hood tail | Emblem is on the cape mesh texture, not on the shirt | RIGID (BodyBackAttachment) + texture | Emblem on shirt, hidden by drape |
| 10 | Staff with lantern and chains | Large hero prop, separate sale item | RIGID (back), heavy hard-surface + chain modelling | None |
| 11 | Trim lines: 2–3 px gold with light top edge and dark bottom edge | Reads as metal piping, not paint | 2D (and on mesh textures) | 2–3 px flat lines |
| 12 | Shading painted into classic textures: top-lit gradients, AO under plates, fold shadows, panel edges darker | Makes flat boxes look sewn | 2D | Flat gradient + noise |
| 13 | Material contrast: matte black cloth / satin white / glossy gold | Value contrast (very dark vs bright) + sheen difference | 2D + mesh textures (all Plastic material, so sheen must be *painted*) | Mid navy vs mid bronze: low contrast |
| 14 | Palette discipline: 1 dark, 1 light, 1 metal, 1 accent used sparingly | Calm, premium | Design | Aqua used everywhere |
| 15 | Presentation: soft studio light, 3/4 shadows, dark backdrop | Sells the item | Blender/Studio render | Own block render |

Honest read: ~60% of the reference's impact is **3D accessories (items 1,3,4,6,7,9,10)**, ~30% is **painted
shading and contrast (11–14)**, ~10% presentation. Classic 2D alone cannot reach it; 2D done well plus 4–5
clean rigid pieces can get close. Layered clothing is not needed for a blocky look; it matters only if we target
Rthro/slender bodies (do that from collection 3 on, not now).

## 2. Spec for Tidewatch v2

Frame: Blender Z-up, Roblox Y-up, -Z forward; export FBX with `axis_forward='-Z', axis_up='Y'`, apply transforms.
Units: model 1 Blender unit = 1 stud, then check `Handle.Size` after first import and fix the export scale once
(record the factor in README). Head proxy: 1.16 (H) x 1.16 (W) x 1.16 (D) rounded box; HatAttachment = top centre.

### 2a. Hood split into three items (all original shapes: tidal cowl, not the reference's pointed hood)

**Item A – Tidecrest Hood (Hat, HatAttachment)**
- Outer size: width 1.55 (1.34x head), depth 1.65, chin-to-crown 1.45, plus a soft swept-back crest that rises
  0.15 and leans back 0.25 (a wave curl, our signature – not a cone). Must stay inside 1.78x2.5x1.78 (slender box,
  the strictest) centred on HatAttachment: Y range -1.25…+1.25 means the hood may hang ~0.09 below the chin and no lower.
- Gap to head: 0.05–0.07 at crown/sides, 0.12 at back; face opening = rounded arch 0.95 wide x 0.95 tall,
  starts 0.05 above the brow line, inner rim recessed 0.08 so the face sits in shadow.
- Thickness: 0.04 (Solidify), rim band 0.06 wide x 0.025 proud, bronze.
- Silhouette rule: from front it is a soft shield shape wider at the cheeks than at the crown; from side the back
  is rounded, never a spike. Nothing below the jaw except two short lappets.
- Folds: 3 broad folds radiating from crest to back-of-neck + 2 from temple to jaw. No noise wrinkles.
- Budget: 1,800–2,500 tris.

**Item B – Tide Mantle (Shoulder, NeckAttachment)**: short capelet over the shoulders and top of chest/back,
2.4 wide x 0.9 high x 1.4 deep, hem with bronze piping and a pearl clasp at the sternum. 1,200–1,800 tris.
It hides the neck gap and carries the hood mass onto the torso.

**Item C – Warden Cape (Back, BodyBackAttachment)**: one panel 1.7 wide at top, 1.9 at hem, 3.2 long, hanging
0.10 off the torso back, starting *below* the mantle line so the hood never covers it. Two-step hem (our motif:
wave scallop, not a straight double hem). Emblem (Tidemark) painted on its texture at ~45% of panel width.
800–1,500 tris. This replaces the shirt-back emblem as the main back read.

**Headless bpy/bmesh pipeline (AI can do all of this):**
1. `make_proxies.py`: R15 block proxies (head 1.16 cube with 0.1 bevel, torso 2x2x1, arms/legs 1x2x1) and an
   Rthro-normal proxy if available as FBX from Roblox's avatar samples (else blocky only).
2. Hood base: draw the side profile as a 2D polyline (12–16 points), `bmesh.ops.spin` 360° with 24 segments, then
   per-vertex radial scaling from a lookup curve (front narrower, cheeks wider) – produces a cowl, not a sphere.
3. Face opening: boolean DIFFERENCE with an extruded arch, then `bmesh.ops.bridge_loops` outer→inner rim; rim
   band = inset + extrude of the opening loop, assigned to material slot "trim".
4. Folds: **Cloth sim headless** – pin crown/crest vertices, collision on head+shoulder proxy, gravity, bake ~40
   frames, apply. Then `Corrective Smooth`, then a Displace with a hand-authored 3-band sine (fold directions
   above) at 0.02 amplitude. Cloth sim gives believable drape; the bands give the stylized folds.
5. Solidify 0.04, Weld, `Decimate` (collapse) to the budget, triangulate, recalc normals, check watertight
   (`bmesh` non-manifold edge count = 0), no N-gons, remove vertex colours.
6. UV: `uv.smart_project(angle_limit=66°, island_margin=0.02)`, or seam along back centre + cylinder unwrap for
   cleaner trim strips; pack to 1024x1024 (2048 allowed, 1024 is enough and lighter).
7. Texture: Cycles headless bake of **AO** and a top-light **diffuse-direct** pass at 1024, multiply onto a base
   colour; trims and emblem drawn in UV space by PIL from the rim UV island coordinates; save `*_albedo.png`.
8. Export FBX + PNG; run our own `validate_local.py` (tri count, bbox vs table in section 0 for normal + slender,
   single mesh, texture <= 2048, attachment origin) before any upload.

**What still needs a human hand (or a bought asset):** the crest curl and the hero folds will look "simulated"
until someone spends 1–2 h in Sculpt mode (Grab, Snake Hook, Crease, Smooth) on the result of step 4; the
belt horns and any organic ornament; hair (buy a licensed hair or skip – it is a separate Hair item anyway).
Shoulder plates, cape, mantle, belt plate and tabard blade are hard-surface boxes + bevels: fully scriptable.

### 2b. Painting the 585x559 classic textures programmatically

Work at **4x (2340x2236), draw each face rect separately, downsample with LANCZOS** – this alone removes the
jagged "MS Paint" look. Keep the face-rect table already in `make_clothing.py`.

| Effect | Technique (PIL/numpy) |
|---|---|
| Global top light | per face: vertical gradient, top +12% value, bottom -18%; side faces 8% darker than front; back 4% darker; down faces 30% darker. Continuous across arm faces so seams vanish. |
| Fake AO | for each drawn shape, render its alpha mask, `GaussianBlur(r=6 at 4x)`, offset 2–4 px down, multiply 0.55 under the shape (drop shadow under plates, belt, collar); also darken 6–10 px inside every face border (blurred inverted rect mask) = the "sewn box" look. |
| Bevel / piping | trims as 3 strokes: 1 px highlight (metal_light) on top, 2 px base, 1 px shadow below; for raised panels, inner 1 px light on top-left edges and dark on bottom-right (emboss via `ImageFilter.EMBOSS` on the mask, blended 25%). |
| Metal (gold/bronze) | not flat colour: vertical 3-stop gradient dark→base→**narrow bright band at 35%**→base→dark, plus 1–2 px specular dots at corners. Painted sheen is the only "material" on Plastic. |
| Cloth folds | Bezier/arc strokes 6 px wide at 4x in shadow colour, `GaussianBlur(4)`, alpha 35%; paired highlight stroke offset 3 px toward light, alpha 20%. Folds radiate from belt and shoulders, 3–5 per face, never parallel. |
| Fabric | very low noise: numpy normal noise sigma 2–3 values, blurred r=0.6, plus a 1-in-4 diagonal weave pattern at 3% – avoid visible grain at 1x. |
| Stitching | dashed 1 px lines 3 px inside panel edges, 2 on / 2 off at 1x, colour = base + 15% value. |
| Symmetry | draw left half of front/back, `ImageOps.mirror`, paste – then break symmetry on purpose only for the clasp/emblem. |
| Value contrast | new palette rule: cloth L* 10–18 (near-black navy), pearl L* 85–92, bronze L* 55–65 with highlight L* 85, aqua only on 3 spots (gem, emblem core, one pipe). |
| Edge seams | after downsample, copy the 1–2 px border column of each face to its neighbour (front↔side, arm faces) so lines meet across corners. |

Better by hand in GIMP (30–60 min per garment): placing 3–4 hero fold highlights, emblem polish, fixing the
spots where shading looks mechanical, a final Curves pass for contrast. The AI writes everything as layers
(`base`, `ao`, `trim`, `folds`, `emblem`) saved separately so the human only edits one layer and re-runs a
`compose.py` that flattens them – hand edits survive regeneration.

### 2c. Production pipeline for collections 2–6

Per collection: 1 shirt, 1 pants, hood (hat), mantle (shoulder), cape (back), 2 shoulder plates (or 1 symmetrical
pair as one NeckAttachment item), 1 waist piece. Optional hero prop later.

| Step | Who | Time (after v2 tools exist) |
|---|---|---|
| Mood board of *own* sketches + palette + emblem SVG (original, checked against reverse image search) | human + AI | 2 h |
| Edit `collection.yaml` (palette, emblem, shapes, parameters) | AI | 0.5 h |
| Generate textures (layers + compose) | AI | 0.5 h |
| GIMP polish shirt + pants | human | 1–2 h |
| Generate hood/mantle/cape/plates/waist in Blender headless | AI | 1 h |
| Sculpt pass on hood + one ornament | human (after learning) | 2–3 h |
| Bake AO, paint mesh textures, export FBX | AI | 1 h |
| Local validation + Blender turntable renders | AI | 0.5 h |
| Studio import (file picker = human), fit on 3 bodies, fix | human + AI | 1–2 h |
| Upload, thumbnails, names/descriptions, pricing | human (ID, 2FA, fees) | 1 h |
| **Total** | | **~11–14 h per collection; ~4 h is AI-only** |

First collection after v2 will take ~2x this (tool building); collections 4–6 should hit the lower bound.

### 2d. Acceptance checks (a piece is "done" only when all pass)

1. `validate_local.py`: tris <= 4,000 (target <= 2,500), single mesh, watertight, no N-gons, no vertex colours,
   bbox inside the **slender** box for its type, texture <= 2048 (we use 1024), origin = attachment.
2. Blender renders, same light rig as presentation shots: front, side, back, 3/4 at 1024 px on blocky proxy.
   Side view must show no spike, no floating gap > 0.08 studs, cape visible below mantle in back view.
3. Overlay test: our render vs reference at the same scale – compare *proportions only* (hood width : torso width,
   plate overhang, cape length). Targets: hood width 0.75–0.8 of torso width; plates overhang arms by 0.25–0.4.
4. Studio: wear on blocky R15, Rthro normal, Rthro slender (HumanoidDescription body scales) + R6; check clipping
   with 3 popular hairs and a default face; walk/jump/sit animations; nothing hides the cape emblem.
5. Studio upload validation passes with zero warnings (first time only through Studio upload; then trust local).
6. Thumbnail readable at 150x150: emblem and silhouette identifiable.
7. Originality check: side-by-side with the reference and top 20 search results for "hooded warden roblox";
   no shape or emblem a buyer could mistake for someone else's.

### Study replica – worth it, with limits

Worth it **once, small, and only in Blender** (never uploaded, not even privately to Roblox: a private upload
still lands on Roblox servers). Replicate just the hood + one shoulder plate (~3 h). It teaches the things our
eyes keep getting wrong: hood-to-head ratio, how far the cowl sits off the head, plate thickness and overhang,
how thin the gold trim actually is, how dark the cloth value really is. Write the measured ratios into this file,
delete the .blend. Do not replicate the staff/lantern or emblem: zero learning value, pure IP risk.

## 3. Ten highest-impact actions (ordered)

| # | Action | Effort | AI alone | Needs human |
|---|---|---|---|---|
| 1 | Measure reference proportions in head units (from image) and write `proportions.yaml` | 1 h | yes | review |
| 2 | Build `validate_local.py` + body proxies + 4-view Blender render script | 3 h | yes | – |
| 3 | Rebuild hood in Blender headless (spin profile, boolean opening, cloth sim, solidify, decimate) inside the Hat box | 4 h | yes | judge silhouette |
| 4 | Split drape into Mantle (NeckAttachment) and Cape (BodyBackAttachment); emblem on the cape texture | 3 h | yes | – |
| 5 | Repaint shirt/pants at 4x with gradients, AO, 3-stroke trims, metal bands, folds; darker palette, aqua on 3 spots only | 4 h | yes | GIMP polish 1–2 h |
| 6 | Shoulder plates (stacked bevelled slabs, original wave-edge shape) as rigid pair | 3 h | yes | – |
| 7 | Waist piece: belt plate + tabard blade (box-modelled), skirt flare panels | 3 h | mostly | horns/ornament sculpt |
| 8 | Prove the FBX route: Blender FBX → Open Cloud Model upload → MeshPart in Studio; otherwise human uses File > Import 3D | 1 h | partly | file picker clicks |
| 9 | Human learns sculpt basics (section 4) and does a 1–2 h sculpt pass on the hood crest/folds | 8–10 h learning | no | yes |
| 10 | Presentation renders (dark backdrop, 3-point light, front+back like the reference layout) for thumbnails/socials | 2 h | yes | pick shots |

Skip for now: hair (buy/skip), staff (separate hero item, ~15–20 h of hard-surface work), layered clothing cages
(only when targeting non-blocky bodies, collection 3+).

## 4. Blunt assessment

- **AI + beginner, no sculpting:** can reach roughly "good mid-tier Marketplace" – clean hard-surface plates,
  capes, belts, well-shaded classic textures, correctly sized hoods. That is a large step up from v1 and is
  sellable. It will **not** reach the reference: its hood folds, horns, hair and lantern are hand-made by someone
  with hundreds of hours in Blender. Procedural cloth sim gets ~70% of a hood; the last 30% (crisp intentional
  folds, a confident crest) is hand work.
- The AI cannot: drive the Studio file picker, judge "does this look premium" reliably from renders (it can
  measure, not taste), pass ID/2FA/Premium steps, or guarantee originality against the whole catalogue.
- Biggest quick wins are not 3D: value contrast, trims with highlight+shadow, AO under shapes, 4x supersampling.
  Do those first; they cost hours, not weeks.
- **What to learn first (in this order, ~20 h total):** (1) Blender navigation + edit mode basics: extrude, inset,
  bevel, loop cut, mirror modifier – enough to tweak AI-generated meshes (4 h); (2) Sculpt mode: Grab, Draw,
  Crease, Smooth, Snake Hook, Dyntopo/Remesh, on a hood (6 h); (3) UV seams + texture paint for fixing bake
  seams (4 h); (4) Roblox Accessory Fitting Tool + reading validation errors (2 h); (5) GIMP layers, Curves,
  soft brushes for highlights (4 h). Layered-clothing caging and rigging come later.
- Business reality: each item costs 80 Robux to upload plus a publishing advance, and selling requires Premium and
  ID verification. Five collections x ~8 items = ~40 uploads – budget roughly 3,200 Robux in upload fees alone
  before any sale (verify current fees first).

# Tidewatch Warden – POC collection #1

Original design: deep navy armour-robe, pearl tunic, bronze trim, aqua glow. Signature feature: the **Tidemark**
(a crescent cradling a wave crest) on chest, back and the hood's crescent crown + aqua gem tip.
Inspiration taken from the reference only for *structure* (hooded silhouette, trim colours, emblem on the back,
layered plates). No shapes, emblem, staff or lantern are copied.

## Files (all in `out/`)
| File | Status |
|---|---|
| `tidewatch_shirt.png`, `tidewatch_pants.png` | Generated, 585x559 RGBA, UV rects taken from the official Roblox R15 templates. Overlaid check images: `check_*_on_template.png`. |
| `tidecrest_hood.obj/.mtl`, `tidecrest_hood_tex.png` | Generated, 1,538 tris, palette texture, origin = HatAttachment. **Not yet imported into Roblox.** |
| `preview_sheet.png`, `preview_hero.png` | Own software render of a block avatar (not a Roblox render). |

## Repeat for the next set
1. Edit palette/emblem in `make_clothing.py` and `make_hood.py`.
2. `python3 make_clothing.py out && python3 make_hood.py out && python3 render_preview.py`
3. Look at `preview_sheet.png`, iterate.

## Test locally (before paying anything)
1. Install **Roblox Studio** (not installed on this Mac; only the Roblox player is).
2. Hood: Studio > Avatar tab > *Import 3D* (File > Import 3D), pick the OBJ, texture = `tidecrest_hood_tex.png`.
   Then Avatar > *Accessory Fitting Tool* / or add an `Attachment` named `HatAttachment` to the Handle and parent to an R15 rig.
   Check scale (hood should wrap the 1.2-stud head); resize in the importer if needed.
3. Clothing: in a Baseplate, insert an R15 rig (Avatar > Rig Builder), add a `Shirt` and `Pants` object to it,
   set `ShirtTemplate` / `PantsTemplate` to the PNG. Local file upload to Studio's asset window is the
   free-for-preview route; **upload fees are NOT 10 Robux: see QUALITY_PLAN.md (agent-reported 80 Robux upload fee + advance, ID verification, Premium to sell; verify on create.roblox.com).
4. Fix list: crescent crown sits close to hood front, check for clipping with hair; cape tail vs. backpacks.

## Honest limits
- No Blender here; mesh is procedural Python. A Blender pass would add smoother hood folds and proper vertex weights.
- Accessory is a rigid mesh, so it is not layered clothing. Marketplace sale rules (ID verification, fees, Premium) were not re-verified this session.
- Textures are flat/procedural; hand-polishing in GIMP (installed) would raise quality a lot.

## Studio test result (2026-11-08, Roblox Studio 0.746, R15 rig, Place1 unsaved)
- Tested: hood imported via File > Import (3D Importer, private upload), worn as Accessory on rig head via HatAttachment; shirt + pants applied.
- Open Cloud upload of PNG gives a **Decal** id (shirt 120231614215221, pants 131695632321595). Clothing needs the **image** id:
  resolve with `InsertService:LoadAsset(decalId)` -> Decal.Texture (shirt 107518626267824, pants 132216199313486). Using the raw Decal id left the rig black.
- Works: all texture regions map correctly (front, arms, belt, boots); hood fits head; crescent + gem visible.
- Problems seen: hood back drape hides the torso back emblem; head has default face under hood; hood is a plain mesh (not layered clothing).
- Not tested: Marketplace publishing, UGC validation tool, R6, side view, avatar in a running game.
- Tooling: ~/.config/tidewatch/.env holds the Open Cloud key (not in repo). python needs SSL_CERT_FILE=/etc/ssl/cert.pem.

## Hood v2 (hood_v2.py, headless Blender) - tested in Studio 2026-11-08
- 2,206 tris, 1.63 x 1.59 x 1.54 studs (inside the 1.87 normal-body limit), arch face opening, bronze rim, aqua brow band, crest gem.
- Open Cloud FBX upload works (needs model/fbx, global_scale 0.01, position-only HatAttachment CFrame). See the skill file.
- Still crude vs the reference: no hand sculpt, flat palette colours, pinched crown, no mantle/cape yet (Items B and C in QUALITY_PLAN.md).

## Mantle + Cape + hood v2b (2026-11-09) - tested in Studio
- `make_cape_tex.py` paints the 512x768 cape texture at 4x (fold shading, bronze hem, Tidemark emblem). `mantle_cape.py` builds both meshes in headless Blender, renders `out/v3/set_*.png` on a block proxy and exports FBX with the origin at the attachment.
- Tide Mantle (NeckAttachment): 1,620 tris, 2.37 x 0.83 x 1.50 studs in Studio, palette texture, pearl clasp + aqua gem. FBX asset 77575261005586.
- Warden Cape (BodyBackAttachment): 1,256 tris, 1.85 x 3.51 x 0.48 studs, scalloped hem, emblem on the cape. FBX asset 119974011674369, texture Decal 100394198674657.
- Hood v2b: export origin lowered 0.045. FBX asset 93959761768467.
- Verified in Studio: front, back and 3/4-back views show hood + mantle + cape together on the R15 rig. Not verified: side view, R6, Rthro, walking animation clipping, UGC validation.
- Real R15 attachment positions (UpperTorso local): NeckAttachment (0, 0.849, 0), BodyBackAttachment (0, -0.212, 0.502). The mesh origin must be authored relative to the attachment itself: exporting the cape with an extra offset put it inside the torso.
- Still open: shirt/pants repaint (4x, shading), shoulder plates, belt, UGC validation, other body types, fee check.

## Clothing v2 (2026-11-09)
- `make_clothing.py` rewritten: each face painted at 4x on its own canvas (cloth folds, weave, metal ramp trim with bevel, drop shadows, glow, satin tunic, layered plates), then LANCZOS downsample. v1 kept as `make_clothing_v1.py`.
- Uploaded: shirt v2 Decal 124998475294083, pants v2 Decal 118828004608765 (resolve image ids with InsertService). Verified on the Studio rig, front view.
- Next polish: darker/blacker cloth for more contrast vs the reference, bigger shoulder overhang (needs 3D plates), side/back check.

## Shoulder plates (2026-11-09) - tested in Studio
- `shoulders.py`: 3 stacked lames per shoulder, bronze rims, aqua rune gem; 1,088 tris each, 1.32 x 0.87 x 1.40 studs in Studio. Right = outward +x (RightShoulderAttachment), left = mirrored copy.
- FBX assets: right 124961827929497, left 131411170280941 (palette texture 87705801382377).
- Real R15: arm centre x=+-1.47 from torso centre, LeftShoulderAttachment at arm-local (0, 0.62, 0) = arm top centre; UpperTorso 1.94 x 1.70 x 1.00.
- Verified on the rig in a 3/4 front view. Not checked: arm swing clipping in animation, validation limits for shoulder accessories.

## v5 quality pass (2026-11-09) - full set rebuilt, tested in Studio
Pipeline (all in this folder, outputs in `out/v5/`):
`python3 make_clothing_v5.py` -> `Blender -b -P build_v5.py` (meshes, meta.json, Cycles AO bakes) -> `python3 paint_v5.py`
(UV textures) -> `Blender -b out/v5/v5_build.blend -P render_v5.py -- tag=r3 export=1` (Eevee views + FBX) -> `python3 compose_v5.py r3`.
Render sheet: `out/v5/v5_sheet.png` (front, 3/4, side, 3/4 back, back). `out/v5/r3_vs_reference.png` is a private comparison only.

What changed: near-black navy cloth (~(21,25,38) lit / (6,7,12) shade), thin bevelled bronze trims painted as distance bands in studs
(same width everywhere), pearl only as thin inner lines + clasp, aqua only on gems and the emblem dot. Every cloth piece is a clean
two-shell grid (edges are grid lines, no boolean/decimate, so no sawtooth). Real UV textures with fold shading + baked AO on every mesh.

| Item | Attachment | Tris | FBX (Model) | Texture Decal |
|---|---|---|---|---|
| Shirt v5 (robe torso, belt, narrow pearl V, sleeves with double cuff) | classic | - | - | 116898490125752 |
| Pants v5 (robe skirt legs, open front with bronze piping, double-step hem) | classic | - | - | 99844070548048 |
| Tidecrest Hood v5 (big cowl, smooth back-leaning peak, bronze opening edge, brow Tidemark) | HatAttachment | 3,364 | 125983264677959 | 110127265892794 |
| Tide Mantle v5 (cowl collar under the hood, double bronze hem, pearl/aqua clasp) | NeckAttachment | 3,136 | 134418525303305 | 71445317143304 |
| Warden Cape v5 (flared under-cloak with double-step hem + emblem panel with large Tidemark) | BodyBackAttachment | 3,448 | 127866209640438 | 114446047262121 |
| Tide Pauldron R / L v5 (3 stacked box-cap tiers + bronze tide-crest crescent with pearl ridge) | Right/LeftShoulderAttachment | 3,288 each | 124776217777333 / 71062800685242 | 127618188419787 (shared) |
| Tidewatch Belt v5 (band, wave-crest buckle, hanging tabard blade) | WaistFrontAttachment | 1,180 | 85906048945961 | 101424587573912 |
| Tidefall Skirt v5 (open-front flared robe skirt, double-step hem) | WaistCenterAttachment | 2,784 | 76247706672366 | 111374505658014 |

Hood bbox relative to HatAttachment: x +-0.86, y -0.86..0.87, z -1.14..+0.47 (inside 1.87 x 2.5 x 1.87).
Studio (2026-11-09): all 7 accessories + shirt/pants worn on workspace.TidewatchRig, front and back views checked, fits match the Blender
renders. Measured rig: head centre 0.576 above NeckAttachment, LowerTorso 0.40 tall, waist attachments at LowerTorso-local (0,-0.2,+-0.502/0).
Still weak / not done: no hand sculpt (folds are procedural, hood still reads "clean CG" rather than soft cloth); no hair, face or hero prop;
lower arms are plain boxes; cape panel top shows a small tab above the mantle at the back centre; skirt is rigid on LowerTorso so it will
clip legs/arms in walk animations; Studio's lighting makes the bronze a little paler than the render; not checked: side view in Studio,
animations, R6/Rthro, UGC validation tool, Marketplace rules.

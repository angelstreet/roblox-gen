---
name: roblox-avatar-fashion
description: Build and test Roblox avatar fashion (classic shirt/pants textures, 3D accessories) on Mac or Linux - official 585x559 template UVs, Blender headless, Open Cloud uploads, and Roblox Studio testing via the command bar. Use when making, fixing, uploading or previewing Roblox clothing or accessories, or when the Studio MCP / file dialogs / Decal-vs-image ids cause trouble.
---

# Roblox avatar fashion pipeline (verified 2026-11-08)

Project files (in this repo): `examples/tidewatch-warden/` (all pipeline scripts, README.md with asset IDs, QUALITY_PLAN.md, `ref/` with the v5 render sheet and v2 shirt/pants). Scripts write to `out/` next to them.
Start here for a new set: copy tidewatch/, change palette/emblem/name in `make_clothing_v5.py` + `build_v5.py`/`paint_v5.py`, then run the v5 pipeline (see "v5 pipeline" below). Open Cloud key lives in `~/.config/tidewatch/.env` (ROBLOX_API_KEY, ROBLOX_USER_ID=<numeric id>, never print it).
Workflow that worked: build with Blender headless, review the render sheet, upload privately via Open Cloud, test on a Studio rig via the command bar, compare to the reference only privately. For a big quality jump, delegate to an Opus subagent with the reference image + this skill (it produced v5 from v4).
Rule: references are a QUALITY BAR only. Ship original designs, names, emblems. Never sell a copy of someone's outfit.

## Facts that were verified
- Official templates: Classic-Clothing-Templates.zip in Roblox/creator-docs (git-lfs: fetch from media.githubusercontent.com, not raw). 585x559 RGBA.
  Face rects (x,y,w,h): torso up 231,8,128,64 / front 231,74,128,128 / back 427,74 / right 165,74,64,128 / left 361,74 / down 231,204,128,64.
  Right arm|leg: left 19,355 back 85,355 right 151,355 front 217,355 (64x128), up 217,289, down 217,485. Left arm|leg: front 308,355 left 374 back 440 right 506, up 308,289, down 308,485.
  Dotted line = local y 100 (max glove/boot height, R15).
- Blender 4.5 runs headless: `/Applications/Blender.app/Contents/MacOS/Blender -b -P script.py` (OBJ import = bpy.ops.wm.obj_import).
- Open Cloud upload (python, `SSL_CERT_FILE=/etc/ssl/cert.pem`): POST apis.roblox.com/assets/v1/assets, key+numeric userId in ~/.config/tidewatch/.env. userId must be NUMERIC (lookup via users.roblox.com/v1/usernames/users). PNG -> assetType Decal. OBJ not accepted (FBX only, as Model).
- A Decal id is NOT an image id. Resolve in Studio: `InsertService:LoadAsset(decalId)` -> `:FindFirstChildWhichIsA("Decal",true).Texture`, put that in Shirt.ShirtTemplate / Pants.PantsTemplate. The raw decal id renders black.
- Studio local files: app content folder is write-protected, so avatars cannot load local files; upload is required.


## Studio MCP (preferred over screen driving) - verified 2026-11-09
Roblox Studio ships its own MCP server: `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` (stdio proxy to the running Studio; Studio shows "MCP - 1" at the bottom right when connected).
It was NOT available in earlier sessions because nothing registered it with Claude. Register once:
```bash
claude mcp add --scope user roblox-studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP
claude mcp list   # roblox-studio: ... Connected   (Studio must be running)
```
MCP tools only load at session start: start a NEW session after adding it. Tools (35 in `~/Library/Roblox/StudioMCP/tools-cache.json`) include `execute_luau`, `get_console_output`, `inspect_instance`, `insert_asset`, `screen_capture`, `search_game_tree`, `get_studio_state`, `start_stop_play`, `auto_setup_avatar`, `generate_mesh/texture/avatar`, `http_get`, `open_cloud_invoke`.
With these, run the wear script (`docs/studio/wear_crystal_vanguard.lua`) via `execute_luau` and take views with `screen_capture`: no clicking, no command-bar typing. Verified 2026-11-09:
- Call `list_roblox_studios` first; every tool needs its `studio_id`. A place must be open (Home screen = no tools).
- `execute_luau` with `datamodel_type: "Edit"`; `return` a string to get results back (prints go to `get_console_output`). Remove an old rig with `.Parent = nil` before re-running.
- Animation clipping without Play mode: `docs/studio/pose_anim.lua` (`Animator:StepAnimations` in edit mode, default R15 anim ids, leg-behind-torso probe). Rigid capes clip the run back-kick (shin reaches 1.74 behind the torso centre).
- Glow: SurfaceAppearance.ColorMapContent + EmissiveMaskContent (+ EmissiveStrength ~1.5, EmissiveTint). Draw masks from swatch cells / shapes, never colour thresholds (painted halos glow as blobs). Emissive items cost 500 Robux to upload.
- Face on the default (dynamic MeshPart) head: decals land in the mesh UVs. Clear Head.TextureID and put the Decal on a welded plate with Transparency 0.98 (1 = not drawn).
- Bodies: `wear_crystal_vanguard.lua` CONFIG takes R6/R15 and HumanoidDescription scales (Rthro Normal/Slender); accessories auto-scale on Rthro.
- `screen_capture` with `camera_position` + `look_at_position` gives exact views: rig at (0,5,0) facing -Z -> front (0,5.5,-9), back (0,5.5,9), side (9,5.5,0), 3/4 (6.5,6,-6.5). The returned JPG is saved under the session's tool-results folder; copy it into `docs/studio/`. Fall back to the computer-use method above only if the tools are missing.

## Studio (computer-use fallback, grant RobloxStudio)
- MCP toggle: bottom-right "MCP off" label -> Assistant Settings > MCP Servers > Enable Studio as MCP server. Session must restart to see MCP tools.
- Command bar at bottom runs Luau: app_type (mode replace) into it, then click the Run button by coordinate (Return only adds a newline).
- Output panel: Window > Output (not View). Use it to read errors/prints.
- Avoid `:Destroy()` in commands: Studio shows a native "Dangerous Command" sheet that the agent cannot click. Use `.Parent=nil`.
- System file pickers (File > Import) are another process; agent cannot drive them. Ask the user to select the file, or use Open Cloud.
- Rig: `Players:CreateHumanoidModelFromDescription(Instance.new("HumanoidDescription"), Enum.HumanoidRigType.R15)`; set part Colors to a skin tone.
- Accessory from imported mesh: rename MeshPart "Handle", add Attachment "HatAttachment" with CFrame = mp.PivotOffset, parent into Accessory, `Humanoid:AddAccessory`.

## Known quality limits
- Procedural sphere+cone hoods look crude; hood must be sized ~1.2-1.4x head (head 1.16 studs), sculpted in Blender, with cloth folds and a real cowl. Layered clothing needs cages (not done yet).
- Not yet tested: UGC validation tool, Marketplace publish, R6, in-game.
- Limits and fees (read 2026-11-09): `docs/MARKETPLACE_RULES.md` (per-type boxes in the attachment frame, 4k tris, watertight, 2048 textures; 80 Robux upload + 1000-1500 advance per rigid item, ID verification; Premium to publish unverified). Pre-check every set with `docs/studio/ugc_check.lua` before any upload talk. Re-verify before paying.

## FBX via Open Cloud -> Studio (verified 2026-11-08, hood_v2.py)
- Open Cloud accepts FBX as assetType Model only with content type `model/fbx` (upload_assets.py does this). No file picker needed.
- Blender FBX export needs `global_scale=0.01` (else the mesh arrives 100x: 162 studs). axis_forward='-Z', axis_up='Y'.
- Imported MeshPart.PivotOffset carries a 90 deg X rotation: build the accessory attachment with `CFrame.new(mp.PivotOffset.Position)` (position only). With the rotation the hood lies on its side.
- Mesh arrives untextured: upload the palette PNG (Decal), resolve its image id via InsertService, set mp.TextureID. "Asset content representation is being generated" = mesh still processing, wait a few seconds.
- Accessory: Humanoid:AddAccessory(acc); RemoveAccessories() destroys them (re-load assets to re-add).
- Result: hood_v2 measured 1.63x1.61x1.61, 2206 tris, sits ~0.045 high (origin rounding); fix by lowering export origin 0.045.

## Body accessories (mantle, cape) - verified 2026-11-09, tidewatch/mantle_cape.py
- Real R15 UpperTorso attachments: NeckAttachment (0,0.849,0), BodyBackAttachment (0,-0.212,0.502); rig front is -Z local, back +Z (Blender -y front, +y back).
- Author each mesh relative to its own attachment (origin = attachment) and export with no extra offset. A double offset hid the cape inside the torso.
- Meshes with a real texture (cape emblem): paint PNG, upload as Decal, resolve image id with InsertService, set mp.TextureID. Set UVs per vertex after `bm.verts.index_update()` (stale indices collapsed all UVs onto one texel).
- Studio command bar via app_type needs `overwrite_existing: true`; click Run (element index) after. Re-running an old command re-adds accessories: remove duplicates with `.Parent=nil`.
- Sizes measured in Studio: mantle 2.37x0.83x1.50, cape 1.85x3.51x0.48 (importer reports a few percent different from Blender).

## Clothing painting v2 (tidewatch/make_clothing.py)
- Paint each template face on its own 4x canvas, shadows baked before shapes (`apply_shadow_now`), metal = 3-stop ramp + dark rim, glow = blurred layer, then downsample per face. Much closer to a pro look than flat fills.
- Shoulder accessories: Right/LeftShoulderAttachment sit at the arm-top centre (arm-local y=0.62, arm centre x=+-1.47 from torso centre). Author the plate relative to that point, mirror for the other side, same FBX/pivot recipe.

## v5 pipeline lessons (2026-11-09, tidewatch/build_v5.py + paint_v5.py + render_v5.py)
- Real blocky R15 rig (measured in Studio): Head centre is 0.576 above NeckAttachment (not 0.9); UpperTorso 1.70 tall, LowerTorso 0.40 tall (torso spans 2.1 below the neck); Waist{Front,Center,Back}Attachment = LowerTorso-local (0,-0.2,-0.502/0/+0.502) = neck frame z -2.098; feet bottom ~ -4.29 below the neck; arm top ~ -0.05. Hat box bottom (attach -1.25) means a hood hem cannot go below head-centre -0.615, and the torso top (neck z 0) means it should stay above head-centre -0.52.
- Clean edges: build every cloth piece as a parametric grid whose borders ARE grid lines (face opening = per-row angular range, seam rows welded with remove_doubles), two shells + rim quads. No boolean cuts, no decimate -> no sawtooth hems.
- Shells: offset the inner shell along finite-difference normals; for welded seam rows use wrap-around differences or the inner shell cracks. recalc_face_normals works once the shell is closed.
- Concave extrusions (crescents) as n-gons triangulate wrongly after a miter inset (filled half-disc). Build them as quad strips instead.
- Texture painting in physical space: export per-vertex positions + distance-to-edge fields (meta.json), bilinear-upsample them per UV region, then trims = distance bands in studs (uniform width everywhere) and emblems = projected through the positions. Cycles AO bake per item with world.light_settings.distance ~0.45 (default distance gives blocky contact blobs from the body boxes).
- Box-like pauldrons must have closed fronts (cap shells), an arc sheet extruded in depth reads as a thin line from the front.
- Contrast check: cloth texture ~(21,25,38) lit / (6,7,12) shade renders near-black; (30,36,54) already reads mid grey under a product light.

## v5 pipeline (run all commands from `examples/tidewatch-warden/`; the Open Cloud key is needed only for step 6; on Linux use `blender` on PATH; run order, from examples/tidewatch-warden/README.md)
1. `python3 make_clothing_v5.py` (classic shirt/pants)
2. `/Applications/Blender.app/Contents/MacOS/Blender -b -P build_v5.py` (meshes, meta.json, Cycles AO bakes -> out/v5/)
3. `python3 paint_v5.py` (UV textures)
4. `Blender -b out/v5/v5_build.blend -P render_v5.py -- tag=r3 export=1` (Eevee views + FBX)
5. `python3 compose_v5.py r3` -> `out/v5/r3_sheet.png` (without a tag argument the name is `v5_sheet.png`) (front, 3/4, side, 3/4 back, back)
6. `SSL_CERT_FILE=/etc/ssl/cert.pem python3 upload_assets.py <files>`; resolve Decal -> image ids in Studio; wear on rig.
Tidewatch v5 asset IDs are in README.md (hood 125983264677959, mantle 134418525303305, cape 127866209640438, pauldrons 124776217777333/71062800685242, belt 85906048945961, skirt 76247706672366, textures as Decals).

## Known gaps after v5 (next work)
- Folds are procedural (no hand sculpt), hood reads smooth CG; no hair/face/hero prop (staff); plain lower arms; cape tab above mantle; rigid skirt clips legs in walk animations (needs layered clothing/cages or split skirt).
- Not tested: side view in Studio, animations, R6/Rthro, UGC validation tool, Marketplace publish.
- Fees/rules: see `docs/MARKETPLACE_RULES.md`; re-verify on create.roblox.com before paying.
- Reference image (roblox1.jpeg) = quality bar only; never ship a copy. Keep comparison images private.

## Driving Studio with computer-use (trap, 2026-11-09)
- If Studio opens on its Home screen (no place open), the template tiles are a canvas: background `app_click`/`app_key` cannot press them and File > New is disabled. A human click or full-screen control (`request_full_control`, needs the user at the keyboard) is required. Keep a place open before starting an unattended agent run.
- Ready-made wear script: `docs/studio/wear_crystal_vanguard.lua`.

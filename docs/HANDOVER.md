# Handover (2026-11-09) - continue roblox-gen

Repo: https://github.com/angelstreet/roblox-gen (public, MIT). Local clone: `~/roblox-gen`. Read `AGENTS.md`, `docs/PIPELINE.md`, then the two skills in `skills/`.

## State
- Pipeline: 2D first (`skills/roblox-2d-concept`), then 3D (`skills/roblox-avatar-fashion`), then Studio test.
- Set 1 `examples/tidewatch-warden/`: original hooded outfit, v5 pipeline, tested in Studio (front/back).
- Set 2 `examples/crystal-vanguard/` (spec in `starter/crystal-vanguard/SPEC.md`): built by Sonnet, refined by Haiku and Sonnet (r1-r9), worn and checked in Studio on an R15 rig (front, back, side, results in `examples/crystal-vanguard/STUDIO_TEST.md`, screenshots `docs/studio/`). About 75% of the concept art's polish.
- Cold-agent tests: Haiku 7/10, MiniMax M3.1-Flash 6/10 (Linux), Sonnet 6/10; their findings are already fixed in the repo.
- Studio MCP: `claude mcp add --scope user roblox-studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` was run (Connected). Tools load only in a NEW session. First job: check you have `execute_luau` / `screen_capture`; if yes, use them instead of screen driving.

## Rules from the owner
- Autonomous: do the next step, do not ask "should I continue". Ask only for money, credentials, publishing, deleting shared data.
- Never publish to the Marketplace or pay fees. Private uploads to the owner's account are fine (Open Cloud key in `~/.config/tidewatch/.env`, never print it).
- References are a quality bar only; no copying other creators' outfits. Keep reference comparison images private.
- Use cheaper models for builds when possible (Haiku/Sonnet/MiniMax) and judge results by looking at the renders.

## Next steps (in order)
1. DONE 2026-11-09 (MCP works, see STUDIO_TEST.md). Confirm the Studio MCP tools work; re-run `docs/studio/wear_crystal_vanguard.lua` through `execute_luau`, take front/back/side/3-4 screenshots with `screen_capture`.
2. Test walk/jump animation clipping (cape, sword, pauldrons), then R6 and Rthro.
3. Check Roblox accessory size limits for back/shoulder/hat items (cape is 3.36 studs tall, crown 2.37 deep) from official docs; run Roblox's UGC validation tool; verify current Marketplace fees and requirements on create.roblox.com.
4. Quality: replace the placeholder face, hair as real swept mane, real glow (emissive via SurfaceAppearance/neon parts or particles in-experience), richer shirt/pants filigree, longer flowing cape.
5. Tidewatch: fix cape tab above the mantle, rigid skirt clipping, side view.
6. Repo: add a `run_all.sh` for tidewatch, merge the duplicated scripts in the two examples into shared modules, add an experiences (places/scripts) track.
7. Re-run a cold Haiku and a cold Sonnet on the repo after each doc change to keep the score up; target 9/10.

## Known traps
- Decal id is not an image id (resolve with `InsertService:LoadAsset`); meshes need a few seconds after upload ("content representation is being generated").
- Headless Linux needs Xvfb + `blender-softwaregl` (`docs/LINUX_HEADLESS.md`).
- On macOS use `sed -i ''`, no pipes after `git push` in this machine's shell hook, Edit needs a prior Read.
- The Crystal Vanguard sword pose: P0 y=1.40 in `build_cv.py` (1.80 floated; 1.05 clipped the cape).

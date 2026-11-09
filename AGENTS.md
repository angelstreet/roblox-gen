# Instructions for AI agents (Claude Code, Codex, etc.)

This repo teaches you to generate Roblox avatar content: classic shirts/pants, 3D accessories (hood, cape, mantle,
shoulder plates, belt, skirt, hair, sword) and experiences (`experiences/`: a try-on showroom).

1. Read `skills/roblox-avatar-fashion/SKILL.md` first. It holds every verified fact and trap (template UVs, Decal vs
   image ids, FBX settings, Studio command-bar tricks, attachment measurements).
   Claude Code users: copy that folder to `~/.claude/skills/roblox-avatar-fashion/` to install it as a skill.
2. Pipeline order: 2D first (`skills/roblox-2d-concept`), then 3D (`skills/roblox-avatar-fashion`); overview in `docs/PIPELINE.md`. Starter set to build: `starter/crystal-vanguard/SPEC.md`.
2b. Examples: `examples/tidewatch-warden/` (default, heavy pipeline) and `examples/crystal-vanguard/` (fast). Build either
   with its `run_all.sh <tag>`. To make a new set follow README "Make your own set" (copy crystal-vanguard, edit `palette.py`).
3. Check prerequisites with `python3 scripts/check_prereqs.py`. Only the "build locally" group blocks you; Studio and the Open Cloud key are
   needed only to upload/test. On headless Linux read `docs/LINUX_HEADLESS.md`. Never print or commit the API key.
4. Upload privately and test in Roblox Studio first. Do NOT publish to the Marketplace or pay fees without the human's
   explicit yes. Re-verify current fees/rules on create.roblox.com.
5. Originality: references are a quality bar only. Never copy another creator's outfit, emblem or name.

Studio: prefer the Studio MCP tools; see the skill's "Studio MCP" section. Wear scripts, animation poses and the Marketplace
pre-check live in `docs/studio/`; experiences (stage 4) in `experiences/`. Shared Python lives in `lib/`: import it, never copy it into a set.

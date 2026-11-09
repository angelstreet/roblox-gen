# Instructions for AI agents (Claude Code, Codex, etc.)

This repo teaches you to generate Roblox avatar content: classic shirts/pants, 3D accessories (hood, cape, mantle,
shoulder plates, belt, skirt) and, later, experiences.

1. Read `skills/roblox-avatar-fashion/SKILL.md` first. It holds every verified fact and trap (template UVs, Decal vs
   image ids, FBX settings, Studio command-bar tricks, attachment measurements).
   Claude Code users: copy that folder to `~/.claude/skills/roblox-avatar-fashion/` to install it as a skill.
2. Pipeline order: 2D first (`skills/roblox-2d-concept`), then 3D (`skills/roblox-avatar-fashion`); overview in `docs/PIPELINE.md`. Starter set to build: `starter/crystal-vanguard/SPEC.md`.
2b. The default example is `examples/tidewatch-warden/` (original "Tidewatch Warden" outfit). To generate the default
   set, follow "v5 pipeline" in the skill. To make a new set, copy the example folder and change palette, emblem and names.
3. Check prerequisites with `python3 scripts/check_prereqs.py`. Only the "build locally" group blocks you; Studio and the Open Cloud key are
   needed only to upload/test. On headless Linux read `docs/LINUX_HEADLESS.md`. Never print or commit the API key.
4. Upload privately and test in Roblox Studio first. Do NOT publish to the Marketplace or pay fees without the human's
   explicit yes. Re-verify current fees/rules on create.roblox.com.
5. Originality: references are a quality bar only. Never copy another creator's outfit, emblem or name.

Studio: prefer the Studio MCP tools; see the skill's "Studio MCP" section.

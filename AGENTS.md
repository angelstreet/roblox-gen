# Instructions for AI agents (Claude Code, Codex, etc.)

This repo teaches you to generate Roblox avatar content: classic shirts/pants, 3D accessories (hood, cape, mantle,
shoulder plates, belt, skirt) and, later, experiences.

1. Read `skills/roblox-avatar-fashion/SKILL.md` first. It holds every verified fact and trap (template UVs, Decal vs
   image ids, FBX settings, Studio command-bar tricks, attachment measurements).
   Claude Code users: copy that folder to `~/.claude/skills/roblox-avatar-fashion/` to install it as a skill.
2. The default example is `examples/tidewatch-warden/` (original "Tidewatch Warden" outfit). To generate the default
   set, follow "v5 pipeline" in the skill. To make a new set, copy the example folder and change palette, emblem and names.
3. Check prerequisites with `python3 scripts/check_prereqs.py` before building. Ask the human for anything missing
   (Open Cloud key, Studio login). Never print or commit the API key.
4. Upload privately and test in Roblox Studio first. Do NOT publish to the Marketplace or pay fees without the human's
   explicit yes. Re-verify current fees/rules on create.roblox.com.
5. Originality: references are a quality bar only. Never copy another creator's outfit, emblem or name.

# roblox-gen

Help creators, and the AI agents that work for them, **generate Roblox content**: avatar clothing, 3D accessories
and (next) experiences. The repo is both a human guide and an agent skill: point an AI coding agent at it and it
can reproduce the default example, then make your own set.

![Tidewatch Warden v5 render sheet](docs/tidewatch-v5-sheet.png)

*Default example: "Tidewatch Warden", an original hooded outfit (classic shirt + pants, hood, mantle, cape, shoulder
plates, belt, skirt). Rendered on a block R15 proxy in Blender.*

![Crystal Vanguard sheet](docs/crystal-vanguard-sheet.png)

*Second set: Crystal Vanguard, built by Sonnet, refined by Haiku from the same repo.*

## What you can generate
| Output | How | Status |
|---|---|---|
| Classic shirt / pants (585x559 PNG) | Python painting on the official template UVs | works, tested in Studio |
| 3D accessories (hat, back, shoulder, waist) | Blender headless -> FBX -> Open Cloud upload -> worn in Studio | works, tested in Studio |
| Layered clothing, hair, faces, props | not done yet | open |
| Experiences (places, scripts) | not done yet | planned |

## Prerequisites
1. **Roblox account** and **Roblox Studio** (create.roblox.com), for testing before you pay anything.
2. **Open Cloud API key** with Assets read+write (create.roblox.com/dashboard/credentials) and your **numeric** user id.
   Put both in `~/.config/tidewatch/.env` (see `.env.example`). Never commit it.
3. **Blender 4.x** (free), run headless (`Blender -b -P script.py`).
4. **Python 3** with `pillow` and `numpy`.
5. Optional: an AI coding agent (Claude Code, Codex, ...).

Headless Linux: see `docs/LINUX_HEADLESS.md`. Needs Blender 4.2 or newer. Check everything (run from the repo root): `python3 scripts/check_prereqs.py`

The API key is only needed to **upload**. Generating and rendering the outfit locally needs only Blender and Python.
The key file path `~/.config/tidewatch/.env` is outside the repo on purpose (the folder name is historical, create it with `mkdir -p ~/.config/tidewatch`).

## Starter sets
- `examples/tidewatch-warden/`: finished default example.
- `examples/crystal-vanguard/`: first cold-agent build of the set below (Sonnet, about 60% of the concept's polish; weak points in its NOTES.md).
- `starter/crystal-vanguard/`: concept art, prompts, sword blockout GLB and an exact spec for a second set. Agents: build it with `skills/roblox-2d-concept` (2D first) then `skills/roblox-avatar-fashion` (3D). See `docs/PIPELINE.md`.

## For AI agents
Read [`AGENTS.md`](AGENTS.md), then [`skills/roblox-avatar-fashion/SKILL.md`](skills/roblox-avatar-fashion/SKILL.md).
For Claude Code, install the skill with:
```bash
cp -R skills/roblox-avatar-fashion ~/.claude/skills/
```
Then ask: *"Generate the default Tidewatch Warden set and show me the render sheet."*

## Run the default example
All commands run from `examples/tidewatch-warden/` (after the repo-root prerequisites check). On Linux/Windows use the `blender` on your PATH instead of the macOS path; flags after `--` are `key=value` pairs.
```bash
# macOS: use /Applications/Blender.app/Contents/MacOS/Blender where it says blender
cd examples/tidewatch-warden
python3 make_clothing_v5.py
blender -b -P build_v5.py
python3 paint_v5.py
blender -b out/v5/v5_build.blend -P render_v5.py -- tag=r3 export=1
python3 compose_v5.py r3          # writes out/v5/r3_sheet.png (the render sheet)
```
Outputs land in `out/v5/`: `r3_sheet.png`, `tidewatch_shirt_v5.png`, `tidewatch_pants_v5.png`, one `.fbx` per accessory. If `ROBLOX_GEN_REFERENCE` is set, a private `r3_vs_reference.png` is also written: never commit or ship it.

Upload privately and test in Studio (needs the key): `SSL_CERT_FILE=/etc/ssl/cert.pem python3 upload_assets.py out/v5/*.fbx out/v5/*.png`.
Details, measurements and every trap found are in the skill file.

## Make your own set
Copy `examples/tidewatch-warden/`, then change the palette, emblem and names in `make_clothing_v5.py`, `build_v5.py`
and `paint_v5.py`. Keep the same pipeline.

## Rules and honesty
- Originality: use references as a quality bar only. Never copy another creator's outfit, emblem or name.
- Upload is private by default. Selling on the Marketplace has fees and requirements (reported: ID verification,
  Premium, an upload fee). **Verify on create.roblox.com before paying.** Nothing here publishes for you.
- Known gaps: procedural folds (no hand sculpt), no hair/face/prop, rigid skirt clips in walk animations, not yet
  tested on R6/Rthro or with Roblox's UGC validation tool. Contributions welcome.
- Not affiliated with Roblox Corporation.

## License
MIT

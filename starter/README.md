# Starter sets

| Folder | What it is | Status |
|---|---|---|
| `crystal-vanguard/` | The original brief: 2D concept art, prompts, sword blockout. Built version: `examples/crystal-vanguard/` | brief |
| `ember-warden/` | Obsidian-and-ember set built from scratch by a cold **Sonnet** agent from the repo docs only (2026-11-09) | passes every check, Studio-tested (private uploads, `docs/studio/wear_ember_warden.lua`) |
| `thornwood-druid/` | Bark-and-moss set built from scratch by a cold **Haiku** agent (2026-11-09) | passes the checks, below the quality bar (see its README); not uploaded |

Each built set holds its source scripts, the release files (`*.fbx`, shirt/pants/face PNGs, `render_sheet.png`) and the
painted `textures/` (`tex_*` colour, `emit_*` emissive mask) so they can be uploaded without Blender. Rebuild with
`./run_all.sh <tag>` (`NOBAKE=1` for a fast check); note the release step overwrites the shipped files.

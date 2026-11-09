# Tidewatch Warden (default example)

An original hooded outfit: near-black navy robe cloth, thin bronze trims, pearl clasp, aqua gems, a crescent-and-wave
"Tidemark" emblem. Seven 3D accessories plus a classic shirt and pants. Built by the v5 pipeline.

## Run (from this folder)
Needs only Blender >= 4.2, Python 3, `pillow`, `numpy`. No Roblox key or Studio for rendering. Use `blender` on PATH
(macOS: `/Applications/Blender.app/Contents/MacOS/Blender`). On headless Linux read `../../docs/LINUX_HEADLESS.md` first.

| Step | Command | Time | Writes (in `out/v5/`) |
|---|---|---|---|
| 1 | `python3 make_clothing_v5.py` | 2 s | `tidewatch_shirt_v5.png`, `tidewatch_pants_v5.png` |
| 2 | `blender -b -P build_v5.py` | ~2 min | `v5_build.blend`, `meta.json`, `ao_*.png` |
| 3 | `python3 paint_v5.py` | ~2 min | `tex_*.png` |
| 4 | `blender -b out/v5/v5_build.blend -P render_v5.py -- tag=r3 export=1` | ~6 min (software GL) | `r3_*.png`, one `.fbx` per accessory |
| 5 | `python3 compose_v5.py r3` | 2 s | `r3_sheet.png` (**the render sheet**) |

Optional: `ROBLOX_GEN_REFERENCE=/path/to/image.jpg python3 compose_v5.py r3` also writes a private `r3_vs_reference.png`. Never commit or ship it.
Upload (needs the key): `SSL_CERT_FILE=/etc/ssl/cert.pem python3 upload_assets.py out/v5/*.fbx out/v5/tex_*.png`.

## Accessories
| Item | Attachment |
|---|---|
| Tidecrest Hood | HatAttachment |
| Tide Mantle | NeckAttachment |
| Warden Cape | BodyBackAttachment |
| Tide Pauldron R / L | Right/LeftShoulderAttachment |
| Tidewatch Belt | WaistFrontAttachment |
| Tidefall Skirt | WaistCenterAttachment |

Triangle counts (verified by a cold agent on Linux): hood 3,364, mantle 3,136, cape 3,448, pauldron 3,288 each, belt 1,180, skirt 2,784.
Hood bbox relative to HatAttachment: x +-0.86, y -0.86..0.87, z -1.14..+0.47 (limit 1.87 x 2.5 x 1.87).

## Studio test (2026-11-09, private uploads)
All accessories + shirt/pants worn on an R15 rig; front and back checked. Measured rig numbers and every trap are in
`../../skills/roblox-avatar-fashion/SKILL.md`. Private test asset IDs (only usable by the uploader): see `docs/HISTORY_v1-v4.md`.

## Known gaps
Procedural folds (no hand sculpt), no hair/face/prop, rigid skirt clips in walk animations, not tested on R6/Rthro or with the UGC validation tool, no side view in Studio.
Earlier iterations (v1-v4) are in `docs/HISTORY_v1-v4.md` and `make_clothing_v1.py`, `hood_v2.py`, `mantle_cape.py`, `shoulders.py`.

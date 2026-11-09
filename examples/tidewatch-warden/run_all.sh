#!/bin/sh
# Tidewatch Warden v5 full build. usage: ./run_all.sh r4   (tag required; Blender on PATH or macOS default; ~10 min)
# Order: make_clothing_v5 -> build_v5 (meshes + Cycles AO bakes) -> paint_v5 -> render_v5 (views + FBX) -> compose_v5 (sheet)
# Outputs in out/v5/: <tag>_sheet.png (render sheet), one .fbx per accessory, tex_*.png. NOBAKE=1 skips the AO bakes (fast preview).
set -e
[ -n "$1" ] || { echo "usage: $0 <tag>"; exit 1; }
B=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}; command -v blender >/dev/null 2>&1 && [ -z "$BLENDER" ] && B=blender
[ -x "$B" ] || command -v "$B" >/dev/null 2>&1 || B=/Applications/Blender.app/Contents/MacOS/Blender
cd "$(dirname "$0")"
python3 make_clothing_v5.py
"$B" -b -P build_v5.py
python3 paint_v5.py
"$B" -b out/v5/v5_build.blend -P render_v5.py -- tag="$1" export=1
python3 compose_v5.py "$1"
echo "sheet: out/v5/$1_sheet.png"

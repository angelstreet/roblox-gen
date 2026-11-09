#!/bin/sh
# Ember Warden full build. usage: ./run_all.sh r1   (tag required)
# Blender: $BLENDER if set, else `blender` on PATH, else the macOS app.
# Order: make_clothing_ew -> make_face_ew -> build_ew (meshes, meta.json, AO bakes) -> paint_ew -> render_ew -> texel_density -> clip_check -> compose_ew -> release_ew.
set -e
[ -n "$1" ] || { echo "usage: $0 <tag>"; exit 1; }
if [ -n "$BLENDER" ]; then B=$BLENDER; elif command -v blender >/dev/null 2>&1; then B=blender; else B=/Applications/Blender.app/Contents/MacOS/Blender; fi
cd "$(dirname "$0")"
# NOTE: Blender exits 0 when a script raises, so every Blender step is checked for its success marker
mkdir -p out; rm -f out/ew_build.blend
python3 make_clothing_ew.py && python3 make_face_ew.py
"$B" -b -P build_ew.py > out/build.log 2>&1; grep -E "ITEM|AO baked|Error|Traceback|assert" out/build.log; grep -q "^DONE" out/build.log || { echo "BUILD FAILED (see out/build.log)"; exit 1; }
python3 paint_ew.py
"$B" -b out/ew_build.blend -P render_ew.py -- tag=$1 export=1 closeup=1 detail=1 > out/render.log 2>&1; grep -E "EXPORT|Error|Traceback" out/render.log; grep -q "^RENDERED" out/render.log || { echo "RENDER FAILED (see out/render.log)"; exit 1; }
python3 texel_density.py || echo "TEXEL DENSITY CHECK FAILED"
"$B" -b out/ew_build.blend -P clip_check_ew.py | grep CLIP
python3 compose_ew.py $1 && python3 release_ew.py $1

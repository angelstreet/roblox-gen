#!/bin/sh
# Crystal Vanguard full build. usage: ./run_all.sh r10   (tag required; ~20 s)
# Blender: $BLENDER if set, else `blender` on PATH, else the macOS app.
# Order: make_clothing_cv -> make_face_cv -> paint_cv -> build_cv -> render_cv -> compose_cv -> release_cv.
# Outputs in out/ (<tag>_sheet.png, *.fbx); release_cv copies them to the release names in palette.NAMES (this folder).
set -e
[ -n "$1" ] || { echo "usage: $0 <tag>"; exit 1; }
if [ -n "$BLENDER" ]; then B=$BLENDER; elif command -v blender >/dev/null 2>&1; then B=blender; else B=/Applications/Blender.app/Contents/MacOS/Blender; fi
cd "$(dirname "$0")"
python3 make_clothing_cv.py && python3 make_face_cv.py && python3 paint_cv.py && "$B" -b -P build_cv.py && "$B" -b out/cv_build.blend -P render_cv.py -- tag=$1 export=1 closeup=1 && python3 compose_cv.py $1 && python3 release_cv.py $1

#!/bin/sh
# usage: ./run_all.sh r2   (Blender on PATH or macOS default)
B=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}; cd "$(dirname "$0")"
python3 make_clothing_cv.py && python3 make_face_cv.py && python3 paint_cv.py && $B -b -P build_cv.py && $B -b out/cv_build.blend -P render_cv.py -- tag=$1 export=1 closeup=1 && python3 compose_cv.py $1

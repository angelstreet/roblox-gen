#!/usr/bin/env python3
"""Copy the build outputs in out/ to the set's release files (names from palette.NAMES), last step of run_all.sh.
Usage: python3 release_cv.py <tag>  -> <fbx names>.fbx, shirt/pants/face PNGs and render_sheet.png in this folder.
A copied set: delete the old release files first (they carry the old names), this step writes the new ones."""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); sys.path.insert(0, HERE)
from palette import NAMES
tag = sys.argv[1] if len(sys.argv) > 1 else None
pairs = [(f"{n}.fbx", f"{n}.fbx") for n in NAMES["fbx"].values()]
pairs += [("cv_shirt.png", NAMES["shirt"]), ("cv_pants.png", NAMES["pants"]), ("cv_face.png", NAMES["face"])]
if tag: pairs.append((f"{tag}_sheet.png", "render_sheet.png"))
for src, dst in pairs:
    shutil.copy(os.path.join(OUT, src), os.path.join(HERE, dst)); print("release", dst)

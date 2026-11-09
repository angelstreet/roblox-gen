"""Wrapper: Blender -b out/cv_build.blend -P clip_check.py  ->  scripts/clip_check.py (generic, any set)."""
import os, runpy
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "clip_check.py"), run_name="__main__")

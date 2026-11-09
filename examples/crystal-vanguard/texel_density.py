#!/usr/bin/env python3
"""Wrapper: the generic check lives in scripts/texel_density.py (works for any set)."""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = [sys.argv[0], HERE]
runpy.run_path(os.path.join(HERE, "..", "..", "scripts", "texel_density.py"), run_name="__main__")

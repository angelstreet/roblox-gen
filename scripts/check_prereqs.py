#!/usr/bin/env python3
"""Check that the roblox-gen prerequisites are present. Exit 1 if a required one is missing."""
import os, shutil, subprocess, sys
ok = True
def row(name, good, hint=""):
    global ok
    print(("[ok]   " if good else "[MISS] ") + name + ("" if good else "  -> " + hint)); ok = ok and good
blender = shutil.which("blender") or next((p for p in ("/Applications/Blender.app/Contents/MacOS/Blender", "C:/Program Files/Blender Foundation/Blender 4.5/blender.exe") if os.path.exists(p)), None)
row("Blender 4.x (headless)", bool(blender), "install from blender.org")
try:
    import PIL, numpy; row("Python Pillow + numpy", True)
except ImportError:
    row("Python Pillow + numpy", False, "pip install pillow numpy")
studio = any(os.path.exists(p) for p in ("/Applications/RobloxStudio.app", os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")))
row("Roblox Studio (for testing)", studio, "install from create.roblox.com")
env = os.path.expanduser("~/.config/tidewatch/.env")
has = os.path.exists(env) and "ROBLOX_API_KEY" in open(env).read() and "ROBLOX_USER_ID" in open(env).read()
row("Open Cloud key in ~/.config/tidewatch/.env", has, "see .env.example; create a key at create.roblox.com/dashboard/credentials with Assets read+write")
sys.exit(0 if ok else 1)

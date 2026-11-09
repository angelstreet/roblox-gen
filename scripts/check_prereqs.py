#!/usr/bin/env python3
"""Check roblox-gen prerequisites in two groups. Exit 1 only if something needed to BUILD locally is missing.
Set $BLENDER to a custom Blender path."""
import os, shutil, subprocess, sys
def find_blender():
    for c in (os.environ.get("BLENDER"), shutil.which("blender"), os.path.expanduser("~/blender/blender"),
              "/Applications/Blender.app/Contents/MacOS/Blender", r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"):
        if c and os.path.exists(c): return c
build_ok = True
def row(name, good, hint="", build=True):
    global build_ok
    print(("[ok]   " if good else ("[MISS] " if build else "[later]")) + " " + name + ("" if good else "  -> " + hint))
    if build and not good: build_ok = False
print("== Needed to build and render locally ==")
b = find_blender(); ver = ""
if b:
    try: ver = subprocess.run([b, "--version"], capture_output=True, text=True, timeout=60).stdout.splitlines()[0]
    except Exception: pass
row(f"Blender >= 4.2 ({ver or b or 'not found'})", bool(b), "install from blender.org or set $BLENDER")
try:
    import PIL, numpy; row("Python Pillow + numpy", True)
except ImportError:
    row("Python Pillow + numpy", False, "pip install pillow numpy")
if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    print("[note] Linux without DISPLAY: the render step needs a virtual display, see docs/LINUX_HEADLESS.md")
print("== Needed only to upload / test in Studio (not for rendering) ==")
studio = any(os.path.exists(p) for p in ("/Applications/RobloxStudio.app", os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")))
row("Roblox Studio", studio, "install from create.roblox.com", build=False)
env = os.path.expanduser("~/.config/tidewatch/.env")
has = os.path.exists(env) and "ROBLOX_API_KEY" in open(env).read() and "ROBLOX_USER_ID" in open(env).read()
row("Open Cloud key in ~/.config/tidewatch/.env", has, "see .env.example (mkdir -p ~/.config/tidewatch)", build=False)
print("\nBuild prerequisites OK." if build_ok else "\nBuild prerequisites MISSING (see [MISS]).")
sys.exit(0 if build_ok else 1)

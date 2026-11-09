# Running on headless Linux (verified by a cold MiniMax M3.1-Flash agent, Debian 12, no GPU)

Steps 2-3 and 5 of the pipeline need no display. Only the EEVEE render step (step 4) needs a GL context; without one
Blender aborts with `Couldn't open libEGL.so.1` (exit 134).

1. Portable Blender, no root:
   ```bash
   curl -sSL -o b.tar.xz https://download.blender.org/release/Blender4.5/blender-4.5.15-linux-x64.tar.xz
   mkdir -p ~/blender && tar -xf b.tar.xz -C ~/blender --strip-components=1
   ```
2. Virtual display + Blender's bundled software GL wrapper for the render step:
   ```bash
   Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
   DISPLAY=:99 ~/blender/blender-softwaregl -b out/v5/v5_build.blend -P render_v5.py -- tag=r3 export=1
   ```
   (`xvfb-run` needs `xauth`; if missing, start `Xvfb` by hand as above.) About 1 min per view on 6 CPU cores.
3. Fonts: `compose_v5.py` tries DejaVu / Liberation if Helvetica is missing (`apt install fonts-dejavu-core`).

#!/usr/bin/env python3
"""Crystal Vanguard face decal (r10): original determined face for the blocky head, transparent PNG.
Used on the Blender proxy head (render) and as the Head "face" Decal on the Studio test rig. NOT a sellable item:
classic faces are not UGC; it only replaces the placeholder squares so the renders/screenshots judge the whole look.
Usage: python3 make_face_cv.py -> out/cv_face.png (512x512)"""
import os, shutil
from PIL import Image, ImageDraw, ImageFilter
from palette import C   # colour theme: edit palette.py for a new set

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
S = 4; N = 512 * S
INK, IRIS_D, IRIS, IRIS_L = C((28, 22, 40)), C((20, 70, 170)), C((60, 150, 245)), C((170, 230, 255))

im = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (0,))); d = ImageDraw.Draw(im)
def P(pts): return [(x * S, y * S) for x, y in pts]
for sg in (-1, 1):
    cx = 256 + sg * 92                                   # eye centre (decal space: head front face spans the whole square)
    # eye white with a flat, slightly angled top (determined look), rounded bottom
    top_in, top_out = 236 + 0, 226                       # inner corner a bit lower than the outer -> slight frown
    white = P([(cx - sg * 40, top_in), (cx + sg * 44, top_out), (cx + sg * 48, 262), (cx + sg * 30, 292), (cx, 300), (cx - sg * 28, 290), (cx - sg * 42, 262)])
    d.polygon(white, fill=(C((250, 252, 255)) + (255,)))
    # iris: ice-blue gradient circle clipped by the eye, dark pupil, two highlights
    ir = Image.new("RGBA", (N, N), (C((0, 0, 0)) + (0,))); di = ImageDraw.Draw(ir)
    for k in range(30):
        t = k / 29; r = (34 - 20 * t) * S
        c = tuple(int(IRIS_D[i] + (IRIS_L[i] - IRIS_D[i]) * t ** 1.6) for i in range(3))
        di.ellipse([cx * S - r, (268 + 8 * t) * S - r * 1.15, cx * S + r, (268 + 8 * t) * S + r * 1.15], fill=c + (255,))
    di.ellipse([(cx - 11) * S, 255 * S, (cx + 11) * S, 281 * S], fill=INK + (255,))
    di.ellipse([(cx - sg * 4 - 9) * S, 248 * S, (cx - sg * 4 + 3) * S, 260 * S], fill=(C((255, 255, 255)) + (255,)))
    di.ellipse([(cx + sg * 12) * S, 282 * S, (cx + sg * 12 + 6) * S, 288 * S], fill=(C((220, 245, 255)) + (255,)))
    mask = Image.new("L", (N, N), 0); ImageDraw.Draw(mask).polygon(white, fill=255)
    im.paste(ir, (0, 0), Image.composite(ir, Image.new("RGBA", (N, N)), mask).getchannel("A"))
    d = ImageDraw.Draw(im)
    # thick upper lash line + thin lower line
    d.line(P([(cx - sg * 46, top_in + 6), (cx - sg * 40, top_in), (cx + sg * 44, top_out), (cx + sg * 54, top_out + 8)]), fill=INK + (255,), width=9 * S, joint="curve")
    d.line(P([(cx - sg * 28, 292), (cx, 301), (cx + sg * 30, 293)]), fill=INK + (200,), width=3 * S, joint="curve")
    # brows: thick, angled down toward the nose (determined), silver-white to match the hair, dark outline
    brow = P([(cx - sg * 44, 212), (cx + sg * 46, 186), (cx + sg * 52, 196), (cx - sg * 40, 224)])
    d.polygon(brow, fill=INK + (255,))
    d.polygon(P([(cx - sg * 40, 213), (cx + sg * 44, 190), (cx + sg * 47, 195), (cx - sg * 38, 219)]), fill=(C((214, 226, 245)) + (255,)))
# small confident mouth: short line with a slight smirk on one side
d.line(P([(232, 352), (262, 356), (284, 349)]), fill=INK + (255,), width=6 * S, joint="curve")
d.line(P([(284, 349), (290, 344)]), fill=INK + (255,), width=5 * S)
im = im.resize((512, 512), Image.LANCZOS)
im.save(os.path.join(OUT, "cv_face.png"))   # release copy (palette.NAMES["face"]) is made by release_cv.py
print("face ->", os.path.join(OUT, "cv_face.png"))

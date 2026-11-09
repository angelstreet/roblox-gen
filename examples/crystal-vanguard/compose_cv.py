#!/usr/bin/env python3
"""Compose the Crystal Vanguard render sheet (front, 3/4, side, 3/4 back, back).
Usage: python3 compose_cv.py <tag>  -> out/<tag>_sheet.png"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
views = ["front", "q34", "side", "q34back", "back"]
ims = [Image.open(os.path.join(OUT, f"{tag}_{v}.png")).convert("RGB") for v in views]
w, h = ims[0].size
sheet = Image.new("RGB", (w * 5, h + 60), (8, 12, 26)); d = ImageDraw.Draw(sheet)
FONTS = ("/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "C:/Windows/Fonts/arial.ttf")
try: font = next(ImageFont.truetype(p, 30) for p in FONTS if os.path.exists(p))
except Exception: font = ImageFont.load_default()
for k, im in enumerate(ims):
    sheet.paste(im, (k * w, 60)); d.text((k * w + 20, 14), views[k], fill=(200, 200, 200), font=font)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from palette import SET_NAME
title = f"{SET_NAME} (Eevee, block R15 proxy)"   # right-aligned so it never overlaps a view label or the edge
d.text((w * 5 - 20 - d.textlength(title, font=font), 14), title, fill=(212, 175, 55), font=font)
sheet.save(os.path.join(OUT, f"{tag}_sheet.png"))
ref = os.environ.get("ROBLOX_GEN_REFERENCE", "")  # optional private quality-bar image; comparison output is never shipped
if ref and os.path.exists(ref):
    r = Image.open(ref).convert("RGB"); r = r.resize((int(r.width * h / r.height), h))
    pair = Image.new("RGB", (r.width + 2 * w, h), (8, 12, 26)); pair.paste(r, (0, 0)); pair.paste(ims[0], (r.width, 0)); pair.paste(ims[4], (r.width + w, 0))
    pair.save(os.path.join(OUT, f"{tag}_vs_reference.png"))
print("sheet", os.path.join(OUT, f"{tag}_sheet.png"))

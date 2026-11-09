#!/usr/bin/env python3
"""Compose the v5 render sheet (front, 3/4, side, 3/4 back, back) and a private side-by-side with the quality reference.
Usage: python3 compose_v5.py [tag]  -> out/v5/<tag>_sheet.png, out/v5/<tag>_vs_reference.png (comparison only, never shipped)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "v5"); tag = sys.argv[1] if len(sys.argv) > 1 else "v5"
views = ["front", "q34", "side", "q34back", "back"]
ims = [Image.open(os.path.join(OUT, f"{tag}_{v}.png")).convert("RGB") for v in views]
w, h = ims[0].size
sheet = Image.new("RGB", (w * 5, h + 60), (27, 27, 28)); d = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
except Exception: font = ImageFont.load_default()
for k, im in enumerate(ims):
    sheet.paste(im, (k * w, 60)); d.text((k * w + 20, 14), views[k], fill=(200, 200, 200), font=font)
d.text((w * 5 - 520, 14), "Tidewatch Warden v5 (Eevee, block R15 proxy)", fill=(200, 170, 110), font=font)
sheet.save(os.path.join(OUT, f"{tag}_sheet.png"))
ref = os.environ.get("ROBLOX_GEN_REFERENCE", "")  # optional private quality-bar image; comparison output is never shipped
if ref and os.path.exists(ref):
    r = Image.open(ref).convert("RGB"); r = r.resize((int(r.width * h / r.height), h))
    pair = Image.new("RGB", (r.width + 2 * w, h), (27, 27, 28)); pair.paste(r, (0, 0)); pair.paste(ims[0], (r.width, 0)); pair.paste(ims[4], (r.width + w, 0))
    pair.save(os.path.join(OUT, f"{tag}_vs_reference.png"))
print("sheet", os.path.join(OUT, f"{tag}_sheet.png"))

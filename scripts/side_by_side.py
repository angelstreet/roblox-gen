#!/usr/bin/env python3
"""Make one image with the concept art next to your render sheet, for the visual comparison step.
Usage: python3 scripts/side_by_side.py concept.png render_sheet.png out.png (private, never ship the concept comparison)"""
import sys
from PIL import Image
a, b = Image.open(sys.argv[1]).convert("RGB"), Image.open(sys.argv[2]).convert("RGB")
w = 1800; a = a.resize((w, int(a.height * w / a.width))); b = b.resize((w, int(b.height * w / b.width)))
o = Image.new("RGB", (w, a.height + b.height), (20, 20, 22)); o.paste(a, (0, 0)); o.paste(b, (0, a.height)); o.save(sys.argv[3]); print("wrote", sys.argv[3])

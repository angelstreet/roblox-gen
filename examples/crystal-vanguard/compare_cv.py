#!/usr/bin/env python3
"""PRIVATE side-by-side of a render sheet against the owner's concept turnaround (quality bar, never shipped or committed).
Usage: python3 compare_cv.py <tag>  -> out/<tag>_vs_concept.png  (row 1: concept hero + turnaround, row 2: our sheet views)"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); tag = sys.argv[1]
REF = os.path.join(HERE, "..", "..", "starter", "crystal-vanguard", "2d", "crystal_vanguard_avatar_reference.png")
ref = Image.open(REF).convert("RGB")
hero = ref.crop((0, 0, 430, 436)); turn = ref.crop((440, 185, 1065, 432))
views = ["front", "q34", "side", "q34back", "back"]
ims = [Image.open(os.path.join(OUT, f"{tag}_{v}.png")).convert("RGB") for v in views]
w, h = ims[0].size
H1 = 700
hero = hero.resize((int(hero.width * H1 / hero.height), H1)); turn = turn.resize((int(turn.width * H1 / turn.height), H1))
top = Image.new("RGB", (hero.width + turn.width + 20, H1), (10, 14, 30)); top.paste(hero, (0, 0)); top.paste(turn, (hero.width + 20, 0))
# our views scaled so the whole row is as wide as the concept row
sw = top.width / 5; sh = int(h * sw / w)
bottom = Image.new("RGB", (top.width, sh), (10, 14, 30))
for k, im in enumerate(ims): bottom.paste(im.resize((int(sw), sh)), (int(k * sw), 0))
out = Image.new("RGB", (top.width, H1 + sh + 10), (10, 14, 30)); out.paste(top, (0, 0)); out.paste(bottom, (0, H1 + 10))
p = os.path.join(OUT, f"{tag}_vs_concept.png"); out.save(p); print(p)

#!/usr/bin/env python3
"""Report how much of an image's opaque pixels are near each target hex colour.
Usage: python3 scripts/check_palette.py image.png '#F8F9FF' '#2E6BFF' ...  (tolerance 60 in RGB distance)"""
import sys
from PIL import Image
import numpy as np
im = np.asarray(Image.open(sys.argv[1]).convert("RGBA")).astype(int); px = im[im[..., 3] > 0][:, :3]
for h in sys.argv[2:]:
    c = np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)])
    near = (np.linalg.norm(px - c, axis=1) < 60).mean() * 100
    print(f"{h}: {near:5.1f}% of pixels within 60 of target")

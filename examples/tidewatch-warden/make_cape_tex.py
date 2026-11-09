"""Cape texture 512x768, painted at 4x then downsampled. Navy cloth, fold shading, bronze hem, Tidemark emblem."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H, S = 512, 768, 4
NAVY=(30,46,82); NAVY3=(10,16,32); PEARL=(232,238,240); AQUA=(70,220,220); BRONZE=(196,142,74); BRONZE2=(140,94,48)
w, h = W*S, H*S
y, x = np.mgrid[0:h, 0:w].astype(np.float32); u = x/w; v = y/h
# base: lighter at top centre, darker to edges and hem
base = np.array(NAVY, np.float32)[None,None,:]*np.ones((h,w,1),np.float32)
light = 1.0 + 0.35*(1-v)*(1-np.abs(u-0.5)*1.6) - 0.35*v - 0.25*np.abs(u-0.5)
# folds: 7 vertical folds that widen toward the hem (match geometry folds in mantle_cape.py)
fold = np.sin((u-0.5)*2*math.pi*3.5*(1+0.35*v) + 0.4) * (0.10 + 0.14*v)
light += fold
rng = np.random.default_rng(3); light += rng.normal(0, 0.012, (h,w)).astype(np.float32)
img = np.clip(base*light[...,None], 0, 255).astype(np.uint8)
im = Image.fromarray(img, "RGB"); d = ImageDraw.Draw(im)
# bronze hem band with bevel lines, bronze side edging
hem0 = int(h*0.935)
d.rectangle([0, hem0, w, h], fill=BRONZE)
d.rectangle([0, hem0, w, hem0+int(h*0.008)], fill=(235,190,120))
d.rectangle([0, h-int(h*0.012), w, h], fill=BRONZE2)
for k in range(0, 24):   # stitched pattern in hem
    cx = int((k+0.5)/24*w); d.polygon([(cx, hem0+h*0.02), (cx+w*0.012, hem0+h*0.035), (cx, hem0+h*0.05), (cx-w*0.012, hem0+h*0.035)], fill=BRONZE2)
e = int(w*0.012); d.rectangle([0,0,e,hem0], fill=BRONZE2); d.rectangle([w-e,0,w,hem0], fill=BRONZE2)
# collar band at the top
d.rectangle([0,0,w,int(h*0.025)], fill=BRONZE)
# Tidemark emblem, centred, upper third
cx, cy, r = w//2, int(h*0.34), int(w*0.20)
d.ellipse([cx-r-6*S, cy-r-6*S, cx+r+6*S, cy+r+6*S], fill=NAVY3)
d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=BRONZE, width=int(r*0.12))
d.ellipse([cx-r*.62, cy-r*.62, cx+r*.62, cy+r*.62], fill=AQUA)
d.ellipse([cx-r*.30, cy-r*.78, cx+r*.94, cy+r*.46], fill=NAVY3)
pts=[(cx-r*.6,cy+r*.5),(cx-r*.2,cy+r*.1),(cx+r*.1,cy+r*.35),(cx+r*.45,cy-r*.05),(cx+r*.6,cy+r*.45)]
d.line(pts, fill=PEARL, width=int(r*0.11), joint="curve")
d.ellipse([cx+r*.05, cy-r*.55, cx+r*.27, cy-r*.33], fill=PEARL)
# thin pearl wave line above the hem
pts=[(i/200*w, hem0-h*0.03+math.sin(i/200*math.pi*10)*h*0.008) for i in range(201)]
d.line(pts, fill=PEARL, width=int(h*0.004))
im = im.filter(ImageFilter.GaussianBlur(0.6*S/2)).resize((W,H), Image.LANCZOS)
im.save("out/v3/cape_tex.png"); print("ok")

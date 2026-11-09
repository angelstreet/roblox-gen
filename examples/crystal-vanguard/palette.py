"""Crystal Vanguard colour theme: the ONE file to edit when you copy this example for a new set.

Every colour in paint_cv.py, make_clothing_cv.py and make_face_cv.py is written as C((r, g, b)): an authored Crystal
Vanguard colour passed through this theme. C() sorts a colour into one of four families by hue/saturation/value and applies
that family's rule. Neutral black/white/greys are never changed. With every rule at its default the output is the authored
Crystal Vanguard look, pixel for pixel.

Rule per family: hue shift in degrees, saturation multiplier, value (brightness) multiplier.
  metal   : gold trims, rims, filigree, buckles          (authored hue ~45 deg)
  plate   : silver-white armour plates, hair              (authored: pale, low saturation blue-white)
  cloth   : navy cloth, scarf, cape, boots                (authored: dark saturated blue)
  crystal : gems, crystal facets, blade, glow, eyes       (authored: bright saturated blue/cyan)
Example, tested 2026-11-09 on a copy (cape, sword, scarf, gems, eyes all turned emerald, gold trims silver):
  emerald + silver: THEME = {"metal": (0, 0.08, 1.05), "plate": (0, 1, 1), "cloth": (-85, 0.9, 0.95), "crystal": (-80, 1, 1)}
Emissive masks follow automatically (they are shape-based). The Studio glow tint is NOT themed: set CONFIG.glowTint in your
wear script to your crystal colour.
"""
import colorsys

SET_NAME = "Crystal Vanguard"    # shown on the render sheet; FBX file names are the FBX dict in render_cv.py
THEME = {"metal": (0, 1, 1), "plate": (0, 1, 1), "cloth": (0, 1, 1), "crystal": (0, 1, 1)}


def family(rgb):
    r, g, b = (c / 255 for c in rgb[:3]); h, s, v = colorsys.rgb_to_hsv(r, g, b); hd = h * 360
    if s < 0.06 or v < 0.03: return None                       # neutral: black, white, greys
    if 15 <= hd <= 75: return "metal"                          # golds / bronzes
    if s < 0.36 and v > 0.55: return "plate"                   # pale blue-whites
    if v < 0.62: return "cloth"                                # dark blues
    return "crystal"                                           # bright blues / cyans


def C(rgb):
    """theme an authored colour; returns an (r, g, b) tuple of ints (alpha is added by the caller)"""
    fam = family(rgb)
    if fam is None: return tuple(rgb[:3])
    dh, ks, kv = THEME[fam]
    if dh == 0 and ks == 1 and kv == 1: return tuple(rgb[:3])  # identity: exact authored colour
    r, g, b = (c / 255 for c in rgb[:3]); h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + dh / 360) % 1.0; s = min(1.0, s * ks); v = min(1.0, v * kv)
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s, v))

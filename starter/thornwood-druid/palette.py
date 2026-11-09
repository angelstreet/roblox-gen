"""Thornwood Druid colour set: the ONE file to edit for colours and release names.

Thornwood uses IDENTITY themes: every colour below is authored exactly, C() returns it unchanged. Reason (found 2026-11-09):
C() sorts colours by hue, and bark brown (hue ~29 deg) and amber (~39 deg) both fall in the "metal" family (hue 15-75),
so one shift for that family would move bark and amber together. Author the final colours here or in the painters instead.
Palette: bark brown #5C4026 / #3A2818, moss green #3E6B2E / #22401A, amber rune glow #FFB23A / #C8741A, pale bone #E9E1C8 / #B9AE8E.
"""
import colorsys

SET_NAME = "Thornwood Druid"     # shown on the render sheet
NAMES = {
    "fbx": {"cv_crown": "thornwood_antler_crown", "cv_scarf": "bone_gorget", "cv_cape": "moss_mantle",
            "cv_pauldron_r": "bark_pauldron_r", "cv_pauldron_l": "bark_pauldron_l", "cv_sword": "gnarled_staff"},
    "shirt": "thornwood_shirt.png", "pants": "thornwood_pants.png", "face": "thornwood_face.png",
}
THEME = {"metal": (0, 1, 1), "plate": (0, 1, 1), "cloth": (0, 1, 1), "crystal": (0, 1, 1)}   # identity, see docstring


def family(rgb):
    r, g, b = (c / 255 for c in rgb[:3]); h, s, v = colorsys.rgb_to_hsv(r, g, b); hd = h * 360
    if s < 0.06 or v < 0.03: return None
    if 15 <= hd <= 75: return "metal"
    if s < 0.36 and v > 0.55: return "plate"
    if v < 0.62: return "cloth"
    return "crystal"


def C(rgb):
    """identity for Thornwood (THEME all (0,1,1)): returns the authored colour as an int tuple"""
    fam = family(rgb)
    if fam is None: return tuple(rgb[:3])
    dh, ks, kv = THEME[fam]
    if dh == 0 and ks == 1 and kv == 1: return tuple(rgb[:3])
    r, g, b = (c / 255 for c in rgb[:3]); h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + dh / 360) % 1.0; s = min(1.0, s * ks); v = min(1.0, v * kv)
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s, v))

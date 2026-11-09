"""Ember Warden colour theme + release names. All colours in the *_ew.py scripts are authored directly in the Ember palette,
so C() is the identity here (kept so the copied painter code runs unchanged); this file holds SET_NAME and the release NAMES.
Ember palette: obsidian (13,11,17) .. (84,76,98), ember orange (255,110,30), molten yellow (255,190,60), white-hot (255,236,170),
deep red (150,30,8), gold (222,172,60), ash grey (96,88,92)."""
SET_NAME = "Ember Warden"
NAMES = {
    "fbx": {"ew_helm": "ember_helm", "ew_collar": "obsidian_collar", "ew_cape": "tattered_cape", "ew_pauldron_r": "ember_pauldron_r",
            "ew_pauldron_l": "ember_pauldron_l", "ew_axe": "molten_axe"},
    "shirt": "ember_warden_shirt.png", "pants": "ember_warden_pants.png", "face": "ember_warden_face.png",
}
THEME = {"metal": (0, 1, 1), "plate": (0, 1, 1), "cloth": (0, 1, 1), "crystal": (0, 1, 1)}


def C(rgb):
    return tuple(int(c) for c in rgb[:3])

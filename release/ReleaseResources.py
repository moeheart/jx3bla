"""The sole 50-level formal-server resource set used by both build entries."""

from pathlib import Path


# openpyxl accepts ordinary Python numbers without its optional NumPy adapter.
# The client uses PNG/ICO icons; the automatic AVIF plugin adds an unused codec.
EXCLUDED_MODULES = ("numpy", "PIL.AvifImagePlugin", "PIL._avif")
OBSOLETE_MODULES = ("replayer.NameCangsheng", "replayer.NameCangshengTest", "equip.AttributeData")

CANGSHENG_FILES = tuple(
    "equip/resources/cangshengtf/" + filename
    for filename in (
        "Custom_Trinket.tab", "Custom_Armor.tab", "Custom_Weapon.tab",
        "attrib.tab", "enchant.tab", "item.txt", "other.tab", "Set.tab",
        "StrengthableAttrib.tab", "xinfa50.json", "global_parameters.json",
        "luoyang_npc_defense.json", "average_equipment.json",
    )
)

def bundle_datas(root):
    """Return only the current tables; GenerateFiles supplies the static icons."""
    root = Path(root)
    return [(str(root / name), str(Path(name).parent)) for name in CANGSHENG_FILES]

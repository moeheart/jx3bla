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
        "luoyang_npc_defense.json", "luoyang_heroic_npc_defense.json",
        "average_equipment.json", "equipment_effects.json",
    )
)

def bundle_datas(root):
    """Bundle the current tables and GUI images without mutable icon caches."""
    root = Path(root)
    assets = [(str(root / name), str(Path(name).parent)) for name in (*CANGSHENG_FILES, "jx3bla.ico")]
    assets.extend((str(path), "icons") for path in sorted((root / "icons").iterdir())
                  if path.is_file() and path.suffix.lower() in (".png", ".ico"))
    return assets

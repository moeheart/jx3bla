"""Exact local data required by the standard Cangsheng runtime."""

CANGSHENG_FILES = tuple(
    "equip/resources/cangshengtf/" + filename
    for filename in (
        "Custom_Trinket.tab", "Custom_Armor.tab", "Custom_Weapon.tab",
        "attrib.tab", "enchant.tab", "item.txt", "other.tab", "Set.tab",
        "StrengthableAttrib.tab", "xinfa50.json", "luoyang_npc_defense.json",
    )
)

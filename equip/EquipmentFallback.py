"""Reference equipment averages for missing current-season JCL equipment."""
from copy import deepcopy
from functools import lru_cache
import json
import math

from equip.CangshengAttributeData import RESOURCE_ROOT, make_base_attributes
from tools.Attribute import CURRENT_GAME_EDITION


EQUIPMENT_FALLBACK_WARNING = "装备读取失败，数值仅供参考"
REQUIRED_EQUIPMENT_SLOTS = frozenset(map(str, range(2, 13))) | {"0"}


def missing_equipment_slots(equipment):
    return sorted(slot for slot in REQUIRED_EQUIPMENT_SLOTS
                  if not isinstance(equipment.get(slot), dict)
                  or str(equipment[slot].get("id", "")).strip() in ("", "0"))


@lru_cache(maxsize=1)
def average_equipment_data():
    return json.loads((RESOURCE_ROOT / "average_equipment.json").read_text(encoding="utf-8"))


def make_average_base_attributes(occ):
    """Average equipment only, then apply this exact kungfu's client profile.

    Normal and 悟 kungfus can share an equipment sample but retain their own
    native naked attributes and conversions. Without a same-family sample,
    leave the missing input unresolved instead of mixing unrelated kungfus.
    """
    data = average_equipment_data()
    if data.get("gameEdition") != CURRENT_GAME_EDITION or data.get("level") != 50:
        raise ValueError("Average equipment is not a current formal 50-level profile")
    sample_occ = occ if occ in data["occupations"] else data.get("aliases", {}).get(occ)
    sample = data["occupations"].get(sample_occ)
    if sample is None:
        return None
    equipment = sample["equipment"]
    if (sample["sampleCount"] <= 0 or not equipment or
            any(not key.startswith("at") or isinstance(value, bool) or
                not isinstance(value, (int, float)) or not math.isfinite(value)
                for key, value in equipment.items())):
        raise ValueError("Invalid average equipment profile: " + occ)
    base = make_base_attributes(equipment, occ)
    base["_estimated"] = {
        "kind": "average-equipment", "occ": occ, "sampleOcc": sample_occ,
        "sampleCount": sample["sampleCount"],
        "sourceDates": deepcopy(sample.get("sourceDates", data.get("sourceDates", []))),
        "warning": EQUIPMENT_FALLBACK_WARNING,
    }
    base["_baseSource"] += "; average equipment from current formal-server JCL"
    return base

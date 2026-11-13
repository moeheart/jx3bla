"""Verify/export current Luoyang NPC defenses independently of rDPS code.

The critical_files NPC cache predates the current raw unpack and must not be
used as the source for this export. No runtime formula is changed here.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "equip/resources/cangshengtf/luoyang_npc_defense.json"
MAIN_IDS = ("139306", "139329", "139319", "139322", "139323", "139312")
HEROIC_MAIN_IDS = ("139360", "139382", "139373", "139376", "139378", "139365")
SCHOOLS = {"Physics": "PhysicsShieldBase", "Solar": "SolarMagicDefence",
           "Lunar": "LunarMagicDefence", "Neutral": "NeutralMagicDefence",
           "Poison": "PoisonMagicDefence"}


def integer(value):
    return int(value) if value.strip() else None


def extract(source, map_id="835", client_version="1.6.0.10009"):
    if map_id not in ("835", "836"):
        raise ValueError("Unverified Luoyang difficulty: " + map_id)
    raw = source.read_bytes()
    try:
        content = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        content = raw.decode("gb18030")
        encoding = "gb18030"
    parameters = json.loads((ROOT / "equip/resources/cangshengtf/source_manifest.json").read_text(encoding="utf-8"))["parameters"]
    global_params = parameters["scripts/skill/GlobalParam.lua"]
    compression = parameters["scripts/Include/数值压缩参数.lua"]
    profiles = {}
    for lineno, row in enumerate(csv.DictReader(io.StringIO(content), delimiter="\t"), 2):
        if not row.get("ID"):
            continue
        profiles[row["ID"]] = {
            "name": row["Name"], "level": integer(row["Level"]),
            "adjustLevel": integer(row["AdjustLevel"]), "maxLife": integer(row["MaxLife"]),
            "shieldBase": {school: integer(row[field]) for school, field in SCHOOLS.items()},
            "script": row["ScriptName"], "sourceLine": lineno,
            "decreaseDamagePercent": integer(row["DecreaseDamagePercent"]),
            "damageCompressCoef": integer(row["DamageCompressCoef"]),
        }
    return {
        "schemaVersion": 1, "gameEdition": 161, "clientVersion": client_version,
        "map": "25人英雄洛阳之战" if map_id == "836" else "25人普通洛阳之战",
        "mapId": map_id, "playerLevel": 50,
        "source": {"path": str(source), "encoding": encoding,
                   "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                   "mtimeUtc": datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat()},
        "scope": "Raw client NPC base values, before encounter scripts and logged defense debuffs; null means absent, not zero.",
        "staleCacheWarning": "critical_files/result_exp/npc_templates contains older rows and is not the source of this export.",
        "parameters": {
            "physicsShieldParam": global_params["values"]["fPhysicsShieldParam"],
            "magicShieldParam": global_params["values"]["fMagicShieldParam"],
            "strainParam": global_params["values"]["fInsightParam"],
            "levelFactors": compression["level_factors"],
            "globalParamsSha256": global_params["sha256"],
            "compressionParamsSha256": compression["sha256"],
        },
        "mainTemplates": list(HEROIC_MAIN_IDS if map_id == "836" else MAIN_IDS), "profiles": profiles,
    }


def verify(data, source=None):
    assert data["gameEdition"] == 161 and data["playerLevel"] == 50
    if source:
        expected = extract(source, data["mapId"], data["clientVersion"])
        for key in ("profiles", "parameters", "mainTemplates", "gameEdition", "clientVersion"):
            assert data[key] == expected[key], "Export differs from current source: " + key
        for key in ("sha256", "bytes"):
            assert data["source"][key] == expected["source"][key], "Source file differs: " + key
    heroic = data["mapId"] == "836"
    main_ids = HEROIC_MAIN_IDS if heroic else MAIN_IDS
    level, shield = (54, 6592) if heroic else (53, 6399)
    for template in main_ids:
        profile = data["profiles"][template]
        assert profile["level"] == level, (template, profile["level"])
        assert set(profile["shieldBase"].values()) == {shield}, (template, profile["shieldBase"])
    p = data["parameters"]
    player_strain_denominator = p["strainParam"] * p["levelFactors"]["50"]
    target_shield_denominator = p["physicsShieldParam"] * p["levelFactors"][str(level)]
    assert abs(player_strain_denominator-7045.83) < 1e-7
    assert abs(target_shield_denominator-(12243.264 if heroic else 11883.168)) < 1e-7
    return {"verifiedMainTemplates": len(main_ids), "allProfiles": len(data["profiles"]),
            "playerStrainDenominator": player_strain_denominator,
            "target%dShieldDenominator" % level: target_shield_denominator,
            "baseMitigation": shield/(shield+target_shield_denominator)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Current raw unpack sNpcTemplate.tab (not the old cache)")
    parser.add_argument("--write", action="store_true", help="Export the explicitly supplied source to the repository JSON")
    parser.add_argument("--heroic", action="store_true", help="Verify/export the formal 10082 heroic NPC table")
    args = parser.parse_args()
    if args.write:
        if not args.source:
            parser.error("--write requires --source")
        data = extract(args.source, "836" if args.heroic else "835",
                       "1.6.0.10082" if args.heroic else "1.6.0.10009")
        verify(data)
        output = OUTPUT.with_name("luoyang_heroic_npc_defense.json") if args.heroic else OUTPUT
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    output = OUTPUT.with_name("luoyang_heroic_npc_defense.json") if args.heroic else OUTPUT
    data = json.loads(output.read_text(encoding="utf-8"))
    print(json.dumps(verify(data, args.source), ensure_ascii=False))


if __name__ == "__main__":
    main()

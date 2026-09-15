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
SCHOOLS = {"Physics": "PhysicsShieldBase", "Solar": "SolarMagicDefence",
           "Lunar": "LunarMagicDefence", "Neutral": "NeutralMagicDefence",
           "Poison": "PoisonMagicDefence"}


def integer(value):
    return int(value) if value.strip() else None


def extract(source):
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
        "schemaVersion": 1, "gameEdition": 160, "clientVersion": "1.6.0.9503",
        "map": "25人普通洛阳之战", "mapId": "835", "playerLevel": 50,
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
        "mainTemplates": list(MAIN_IDS), "profiles": profiles,
    }


def verify(data, source=None):
    assert data["gameEdition"] == 160 and data["playerLevel"] == 50
    if source:
        assert data == extract(source), "Export differs from current source or parameters"
    for template in MAIN_IDS:
        profile = data["profiles"][template]
        assert profile["level"] == 53, (template, profile["level"])
        assert set(profile["shieldBase"].values()) == {6399}, (template, profile["shieldBase"])
    p = data["parameters"]
    player_strain_denominator = p["strainParam"] * p["levelFactors"]["50"]
    target_shield_denominator = p["physicsShieldParam"] * p["levelFactors"]["53"]
    assert abs(player_strain_denominator-7045.83) < 1e-7
    assert abs(target_shield_denominator-11883.168) < 1e-7
    return {"verifiedMainTemplates": len(MAIN_IDS), "allProfiles": len(data["profiles"]),
            "playerStrainDenominator": player_strain_denominator,
            "target53ShieldDenominator": target_shield_denominator,
            "baseMitigation": 6399/(6399+target_shield_denominator)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Current raw unpack sNpcTemplate.tab (not the old cache)")
    parser.add_argument("--write", action="store_true", help="Export the explicitly supplied source to the repository JSON")
    args = parser.parse_args()
    if args.write:
        if not args.source:
            parser.error("--write requires --source")
        data = extract(args.source)
        verify(data)
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    print(json.dumps(verify(data, args.source), ensure_ascii=False))


if __name__ == "__main__":
    main()

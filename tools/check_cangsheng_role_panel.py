"""Read current client panel literals and branch evidence from original Lua 5.1.

No Lua VM, host calls or decompiled source is used. Only the root's literal
initialization instructions are interpreted, stopping at its first closure.
Instruction offsets below are zero-based and tied to the recorded SHA256.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from release.Lua51Evidence import Chunk

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "equip/resources/cangshengtf"
RAW = FOLDER / "role_attribute.luac"
OUTPUT = FOLDER / "role_panel_evidence.json"
EXPECTED_SHA256 = "162d3e5041f08419cc22f6f6f0d3c54315b6d72537313ca166ae70b85301b0cb"
OPS = ("MOVE LOADK LOADBOOL LOADNIL GETUPVAL GETGLOBAL GETTABLE SETGLOBAL SETUPVAL "
       "SETTABLE NEWTABLE SELF ADD SUB MUL DIV MOD POW UNM NOT LEN CONCAT JMP EQ LT LE "
       "TEST TESTSET CALL TAILCALL RETURN FORLOOP FORPREP TFORLOOP SETLIST CLOSE CLOSURE VARARG").split()


def constants(proto):
    result = []
    for tag, raw in proto["constants"]:
        if tag == b"\4":
            result.append(raw[:-1].decode("gb18030"))
        elif tag == b"\3":
            result.append(struct.unpack("<d", raw)[0])
        elif tag == b"\1":
            result.append(bool(raw[0]))
        else:
            result.append(None)
    return result


def decode(raw):
    word = int.from_bytes(raw, "little")
    return word & 63, (word >> 6) & 255, word >> 23, (word >> 14) & 511, word >> 14


def literal_tables(chunk):
    keys = constants(chunk.root)
    registers = {}
    # These symbols are table keys only; no client API is called.
    globals_ = {"EQUIPMENT_INVENTORY": {key: key for key in (
        "BOOTS RANGE_WEAPON PANTS RIGHT_RING BANGLE CHEST PENDANT HELM AMULET "
        "LEFT_RING WAIST MELEE_WEAPON BIG_SWORD").split()}}
    writes = []
    def rk(value):
        return keys[value - 256] if value >= 256 else registers[value]
    for pc, raw in enumerate(chunk.root["code"]):
        op, a, b, c, bx = decode(raw)
        if op == 36:
            assert pc == 1501, "Literal initialization boundary changed"
            break
        if op == 0:
            registers[a] = registers[b]
        elif op == 1:
            registers[a] = keys[bx]
        elif op == 2:
            assert c == 0
            registers[a] = bool(b)
        elif op == 3:
            for index in range(a, b + 1):
                registers[index] = None
        elif op == 5:
            registers[a] = globals_[keys[bx]]
        elif op == 6:
            registers[a] = registers[b][rk(c)]
        elif op == 7:
            globals_[keys[bx]] = registers[a]
        elif op == 9:
            key, value = rk(b), rk(c)
            registers[a][key] = value
            if (500 <= pc <= 545 or 1495 <= pc <= 1500):
                writes.append(dict(pc=pc, register=a, key=key, value=value))
        elif op == 10:
            registers[a] = {}
        elif op == 14:
            registers[a] = rk(b) * rk(c)
        elif op == 15:
            registers[a] = rk(b) / rk(c)
        elif op == 34:
            assert b > 0 and c > 0
            for index in range(1, b + 1):
                registers[a][(c - 1) * 50 + index] = registers[a + index]
        else:
            raise ValueError(("Unsupported literal instruction", pc, op))
    return registers, globals_, writes


def disassemble(proto, start=0, stop=None):
    keys = constants(proto)
    result = []
    def rk(value):
        return repr(keys[value - 256]) if value >= 256 else "R%d" % value
    for pc, raw in enumerate(proto["code"]):
        if pc < start or (stop is not None and pc >= stop):
            continue
        op, a, b, c, bx = decode(raw)
        description = ""
        if op in (1, 5, 7):
            description = repr(keys[bx])
        elif op in (6, 9, 12, 13, 14, 15, 16, 17, 23, 24, 25):
            description = "%s %s" % (rk(b), rk(c))
        elif op == 36:
            description = "child %d" % bx
        elif op in (22, 31, 32):
            description = "goto %d" % (pc + 1 + bx - 131071)
        result.append("%d %s A=%d B=%d C=%d %s" % (pc, OPS[op], a, b, c, description))
    return result


def audit(raw):
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, "Client panel bytecode changed; review offsets before exporting"
    chunk = Chunk(raw)  # Also verifies byte-for-byte serialization round trip.
    registers, globals_, writes = literal_tables(chunk)
    assert registers[36] == "youluo"
    assert registers[44]["lijing"]["BaseHealPlus"] == 686 / 1024
    assert registers[44]["lijing"]["BaseCritPlus"] == 82 / 1024
    assert registers[44]["yunshang"]["BaseHealPlus"] == 727 / 1024
    assert registers[57]["YouluoPhysicsAPToMagicAPCof"] == 1
    assert registers[57]["YouluoWeaponToMagicAPCof"] == 6
    for child in (30, 35):
        assert not any("Weapon" in str(key) or "PhysicsAPToMagic" in str(key)
                       for key in constants(chunk.root["children"][child]))
    return {
        "schemaVersion": 1, "gameEdition": 160, "clientVersion": "1.6.0.9503",
        "source": {"origin": "ui/Script/common/role_attribute.lua", "file": RAW.name,
                   "sha256": digest, "bytes": len(raw), "roundTripExact": True},
        "scope": "Client panel computation evidence; actual skill Lua has priority if it disagrees.",
        "playerKungfuName": globals_["PlayerKungfuName"],
        "xinfaCoefficientsR44": registers[44], "basePanelR54": registers[54],
        "xinfaLevelBasePanelR56": registers[56], "refinementRatesR47": registers[47],
        "youluoConversionsR57": registers[57],
        "literalBindingInstructions": writes,
        "conversionScope": {
            "onlyKungfu": "youluo", "xinfaId": 10821,
            "formula": "lunarAP += max(solarAP, neutralAP, poisonAP, physicsAP + 6*(weaponBase + weaponRand/2), 0); remove the converted source AP fields",
            "rootBinding": "R36='youluo'; child39 upvalue5=R36, upvalue11=child32; child32 upvalue3=child31",
            "condition": "child39 pc43..57 calls child32 and returns only when argument0 equals 'youluo'",
            "conversion": "child32 pc20..27 calls child31 with weapon conversion enabled; child31 pc47..70 takes max(existing, physical+weapon conversion)",
            "ordinaryMagic": "child30 and child35 consume their own school AP plus main-stat coefficients; they do not call child31",
        },
        "instructionEvidence": {
            "rootYouluoConstants": disassemble(chunk.root, 1455, 1501),
            "rootClosureBindings": disassemble(chunk.root, 1641, 1674) + disassemble(chunk.root, 1685, 1711),
            "youluoConversionChild31": disassemble(chunk.root["children"][31]),
            "youluoPanelChild32": disassemble(chunk.root["children"][32], 0, 75),
            "panelDispatchChild39": disassemble(chunk.root["children"][39], 37, 59),
            "commonShieldBaseChild4": disassemble(chunk.root["children"][4]),
            "equipmentRefinementAndGemsChild22": disassemble(chunk.root["children"][22], 113, 189),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raw = (args.source or RAW).read_bytes()
    data = audit(raw)
    if args.write:
        RAW.write_bytes(raw)
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        assert json.loads(OUTPUT.read_text(encoding="utf-8")) == json.loads(json.dumps(data)), "Evidence export differs"
    print(json.dumps({"sha256": data["source"]["sha256"], "bytes": len(raw),
                      "xinfaPanels": len(data["xinfaCoefficientsR44"]),
                      "physicalWeaponConversion": "youluo only", "roundTripExact": True}))


if __name__ == "__main__":
    main()

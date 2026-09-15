"""Verify read-only PE evidence for the current client's gem attribute scaling.

This does not load or execute a DLL. The binary may be supplied with --source;
otherwise the committed instruction/constant evidence is checked on its own.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "equip/resources/cangshengtf/native_gem_evidence.json"
EXPECTED_SHA256 = "ba4d8adbd13ec4850b068c0f7523d77c3f4f6127b08a5d4efb6ec16091962d37"
CONSTANTS = {"lowLevelFactor": 0x455d8, "highLevelFactor": 0x40fc8,
             "highLevelOffset": 0x40fd8, "highLevelScale": 0x40fd0,
             "compressionNumerator": 0x41000, "compressionDenominator": 0x41008}
FUNCTIONS = {"KGItemInfoList_AttribStrength": (0x216c0, 0x217e7),
             "KGLuaItemInfo_LuaGetSlotAttrib": (0x351f0, 0x353da),
             "KGItem_LuaGetSlotAttrib": (0x33300, 0x334e4),
             "KGItem_AttribStrengthWrapper": (0x3550, 0x356a),
             "GetAttributeValue": (0x23b90, 0x23cc4)}


def rva_bytes(raw, rva, count):
    pe = struct.unpack_from("<I", raw, 0x3c)[0]
    assert raw[pe:pe + 4] == b"PE\0\0"
    sections = struct.unpack_from("<H", raw, pe + 6)[0]
    optional_size = struct.unpack_from("<H", raw, pe + 20)[0]
    start = pe + 24 + optional_size
    for i in range(sections):
        row = start + i * 40
        _, virtual, size, offset = struct.unpack_from("<IIII", raw, row + 8)
        if virtual <= rva and rva + count <= virtual + size:
            return raw[offset + rva - virtual:offset + rva - virtual + count]
    raise ValueError("RVA is not backed by file bytes: %x" % rva)


def gem_value(value, level):
    factor = level * .195 if level <= 6 else (level * .65 - 3.2) * 1.3
    # Preserve SSE2 mul/mul/div order and cvttsd2si truncation.
    result = float(value) * factor
    result *= 1355.0
    result /= 27800.0
    return int(result)


def extract(raw):
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, "DLL changed; review machine code before regenerating"
    constants = {}
    for name, rva in CONSTANTS.items():
        value = rva_bytes(raw, rva, 8)
        constants[name] = dict(rva=hex(rva), bytes=value.hex(), value=struct.unpack("<d", value)[0])
    functions = {}
    for name, (start, end) in FUNCTIONS.items():
        value = rva_bytes(raw, start, end - start)
        functions[name] = dict(startRva=hex(start), endRvaExclusive=hex(end),
                               bytes=value.hex(), sha256=hashlib.sha256(value).hexdigest())
    imagebase = 0x180000000
    assert struct.unpack("<Q", rva_bytes(raw, 0x412c0, 8))[0] == imagebase + 0x3550
    assert rva_bytes(raw, 0x4f928, 13).startswith(b".?AVKGItem@@")
    assert struct.unpack("<Q", rva_bytes(raw, 0x4f410, 8))[0] == imagebase + 0x46188
    assert struct.unpack("<Q", rva_bytes(raw, 0x4f420, 8))[0] == imagebase + 0x351f0
    return {
        "schemaVersion": 1, "gameEdition": 160,
        "source": {"file": "SO3ItemHouseX64.dll", "bytes": len(raw), "sha256": digest,
                   "location": "JX3_EXP/bin/zhcn_exp/bin64", "imageBase": hex(imagebase),
                   "inspection": "Static PE bytes and GNU objdump disassembly; no DLL load or game process access"},
        "constants": constants, "functions": functions,
        "callChain": [
            "KGLuaItemInfo::LuaGetSlotAttrib RVA351F0 reads slot's DiamondAttributeID, calls RVA23B90 with seed0 to get raw attribute, calls RVA216C0 with diamond level and attribute",
            "KGItem::LuaGetSlotAttrib RVA33300 calls RVA23B90 with item seed, then vtable+0x150",
            "KGItem RTTI vtable RVA41170+0x150 contains RVA3550; wrapper calls the same RVA216C0",
        ],
        "formula": {"factor": "level <= 6 ? level * .195 : (level * .65 - 3.2) * 1.3",
                    "value": "int_truncate_toward_zero(((double(rawParam) * factor) * 1355.0) / 27800.0)",
                    "condition": "StrengthableAttrib.tab AttribType match; Value1Strable modifies Param0, Value2Strable modifies Param1; absent/zero flags leave that param unchanged",
                    "itemDependence": "No item level, quality, equip requirement, white damage or refinement level is read by RVA216C0",
                    "truncationRva": ["0x217b3", "0x217d5"]},
        "examples225": {str(level): gem_value(225, level) for level in range(0, 9)},
        "boundaries": "This proves local client getter behavior. Runtime/server comparison is outside this static audit; the DLL is retained only in ignored local backups.",
    }


def verify(data):
    assert data["source"]["sha256"] == EXPECTED_SHA256
    expected = dict(lowLevelFactor=.195, highLevelFactor=.65, highLevelOffset=3.2,
                    highLevelScale=1.3, compressionNumerator=1355.0, compressionDenominator=27800.0)
    for name, record in data["constants"].items():
        assert record["value"] == struct.unpack("<d", bytes.fromhex(record["bytes"]))[0] == expected[name]
    for record in data["functions"].values():
        raw = bytes.fromhex(record["bytes"])
        assert len(raw) == int(record["endRvaExclusive"], 16) - int(record["startRva"], 16)
        assert hashlib.sha256(raw).hexdigest() == record["sha256"]
    body = bytes.fromhex(data["functions"]["KGItemInfoList_AttribStrength"]["bytes"])
    assert body[0x217b3 - 0x216c0:0x217b7 - 0x216c0] == bytes.fromhex("f20f2cc0")
    assert body[0x217d5 - 0x216c0:0x217d9 - 0x216c0] == bytes.fromhex("f20f2cc0")
    assert data["examples225"] == {str(level): gem_value(225, level) for level in range(9)}
    assert gem_value(225, 8) == 28


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        if not args.source:
            parser.error("--write requires --source")
        data = extract(args.source.read_bytes())
        verify(data)
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    verify(data)
    if args.source:
        assert data == extract(args.source.read_bytes())
    print(json.dumps({"verified": True, "examples225": data["examples225"],
                      "compression": "1355 / 27800", "nativeFunctions": len(data["functions"])}))


if __name__ == "__main__":
    main()

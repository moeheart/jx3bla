"""Audit historical 9503 xinfa AddAttribute calls using original Lua 5.1 bytecode.

Requires lupa (Lua 5.1 module) only for regeneration, never at replay runtime.
Original chunks are authoritative; decompiler differences are reported.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

from release.Lua51Evidence import Chunk
from release.XinfaAttributes import normalize_attributes


def skill_level_evidence(root, rows):
    """Resolve the selected xinfa levels from the actual auto-learning tables."""
    levels = {}
    for row in rows:
        school = row['ScriptFile'].replace('\\', '/').split('/')[0]
        origin = 'settings/skill/SkillAutoLearning/' + school + '.tab'
        path = root / 'unpack_result' / origin
        with path.open(encoding='gb18030', newline='') as handle:
            candidates = [item for item in csv.DictReader(handle, delimiter='\t')
                          if item.get('SkillID') == row['SkillID']
                          and int(item.get('RequirePlayerLevel') or 0) <= 50]
        learned = max(candidates, key=lambda item: int(item['SkillLevel']))
        if learned['RequirePlayerLevel'] != '50' or learned['SkillLevel'] != '5':
            raise ValueError(('Unexpected level-50 xinfa level', row['SkillID'], learned))
        levels[row['SkillID']] = dict(origin=origin, row=learned,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return levels


def audit(root, deps):
    if deps:
        sys.path.insert(0, str(deps.resolve()))
    from lupa.lua51 import LuaRuntime
    rows = json.loads((root / 'mount_skills.json').read_text(encoding='utf-8'))
    names = json.loads((root / 'occ_names.json').read_text(encoding='utf-8'))
    levels = skill_level_evidence(root, rows)
    records = {}
    shared_path = 'scripts/Include/Skill.lh'
    shared = Chunk((root / 'unpack_result' / shared_path).read_bytes())
    common = shared.named_function('AdditionalAttribute')
    common_readable = (root / 'lua_readable' / shared_path).read_text(encoding='utf-8')
    import re
    common_body = re.search(r'(function AdditionalAttribute\([^\n]+\).*?\nend)', common_readable, re.S).group(1)

    for row in rows:
        origin = 'scripts/skill/' + row['ScriptFile'].replace('\\', '/')
        raw = (root / 'unpack_result' / origin).read_bytes()
        parsed = Chunk(raw)
        all_outputs = []
        decompiler_issue = None
        for mode in ('bytecode', 'decompiled'):
            lua = LuaRuntime(encoding=None, register_eval=False, register_builtins=False)
            # No host/file/network APIs are available to the captured functions.
            lua.execute(b'os=nil; io=nil; package=nil; python=nil; dofile=nil; loadfile=nil')
            g = lua.globals()
            enum = lua.eval(b'function() return setmetatable({}, {__index=function(t,k) return k end}) end')
            for name in (b'ATTRIBUTE_EFFECT_MODE', b'ATTRIBUTE_TYPE', b'PLAYER_ARENA_TYPE', b'SKILL_KIND_TYPE',
                         b'CHARACTER_ENERGY_TYPE'):
                g[name] = enum()
            g[b'Include'] = lambda path: None
            kungfu_path = 'scripts/skill/include/kungfuConst.lh'
            if mode == 'bytecode':
                lua.execute(Chunk((root / 'unpack_result' / kungfu_path).read_bytes()).serialize())
                g[b'AdditionalAttribute'] = lua.eval(b'loadstring')(shared.serialize(proto=common))
                lua.execute(parsed.serialize())
            else:
                lua.execute((root / 'lua_readable' / kungfu_path).read_bytes())
                lua.execute(common_body.encode('utf-8'))
                lua.execute((root / 'lua_readable' / origin).read_bytes())
            output = []
            def capture(mode, attr, value_a, value_b):
                def clean(value):
                    if isinstance(value, bytes):
                        try:
                            return value.decode('utf-8')
                        except UnicodeDecodeError:
                            return value.decode('gb18030')
                    return value
                output.append(dict(mode=clean(mode), attribute=clean(attr),
                                   value_a=clean(value_a), value_b=clean(value_b)))
            actor = lua.table_from({b'dwLevel': int(levels[row['SkillID']]['row']['SkillLevel']),
                                   b'dwSkillID': int(row['SkillID']), b'AddAttribute': capture})
            try:
                result = g[b'GetSkillLevelData'](actor)
            except Exception as error:
                if mode == 'bytecode':
                    raise RuntimeError((row['SkillID'], row['SkillName'], mode)) from error
                decompiler_issue = str(error)
                all_outputs.append(None)
                continue
            if result is not True:
                raise ValueError((row['SkillID'], 'GetSkillLevelData did not return true'))
            all_outputs.append(output)
        if all_outputs[1] is not None and all_outputs[0] != all_outputs[1]:
            decompiler_issue = 'decompiled/original AddAttribute mismatch'
        by_enum = {}
        for call in all_outputs[0]:
            if isinstance(call['value_a'], (int, float)):
                key = call['attribute']
                by_enum[key] = by_enum.get(key, 0) + call['value_a']
        base, conversions = normalize_attributes(all_outputs[0])
        records[row['SkillName']] = dict(skill_id=int(row['SkillID']), skill_level=5,
            learning_source=levels[row['SkillID']],
            raw_attributes=all_outputs[0], summed_enum_attributes=by_enum,
            base_attributes=base, conversions=conversions,
            source=dict(origin=origin, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)),
            original_bytecode_matches_decompiled=decompiler_issue is None,
            decompiler_issue=decompiler_issue)
    return dict(schema_version=1, game_edition=160, client_version='1.6.0.9503', player_level=50,
                status='raw_xinfa_verified',
                shared_source=dict(origin=shared_path, sha256=hashlib.sha256(shared.data).hexdigest(),
                                   function='AdditionalAttribute'),
                occupations={occ: dict(name=name, **records[name]) for occ, name in names.items()},
                alternate_xinfa={'10145': records['山居剑意']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--deps', type=Path)
    parser.add_argument('--output', type=Path, default=Path('docs/160/evidence/legacy9506/xinfa50.json'))
    args = parser.parse_args()
    report = audit(args.evidence_root, args.deps)
    # Current portable mobile evidence must survive a full ordinary regeneration.
    mobile_evidence = args.evidence_root.parent / 'wujie_evidence'
    if mobile_evidence.is_dir():
        from release.WujieXinfa50Generator import audit as audit_mobile, merge_profiles
        mobile_profiles = audit_mobile(mobile_evidence, args.deps)
        report = merge_profiles(report, mobile_profiles)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    newline = '\r\n' if args.output.is_file() and b'\r\n' in args.output.read_bytes() else '\n'
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline=newline)
    print(json.dumps({'occupations': len(report['occupations']), 'output': str(args.output)}))


if __name__ == '__main__':
    main()

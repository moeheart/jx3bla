"""Audit current xinfa AddAttribute calls using original Lua 5.1 bytecode.

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


BASE_ATTRIBUTE_NAMES = {
    'MAGIC_ATTACK_POWER_BASE': 'atMagicAttackPowerBase',
    'PHYSICS_ATTACK_POWER_BASE': 'atPhysicsAttackPowerBase',
    'SOLAR_ATTACK_POWER_BASE': 'atSolarAttackPowerBase',
    'LUNAR_ATTACK_POWER_BASE': 'atLunarAttackPowerBase',
    'NEUTRAL_ATTACK_POWER_BASE': 'atNeutralAttackPowerBase',
    'POISON_ATTACK_POWER_BASE': 'atPoisonAttackPowerBase',
    'THERAPY_POWER_BASE': 'atTherapyPowerBase',
    'MAGIC_SHIELD': 'atMagicShield',
    'PHYSICS_SHIELD_BASE': 'atPhysicsShieldBase',
    'PHYSICS_CRITICAL_STRIKE': 'atPhysicsCriticalStrike',
    'SOLAR_CRITICAL_STRIKE': 'atSolarCriticalStrike',
    'LUNAR_CRITICAL_STRIKE': 'atLunarCriticalStrike',
    'NEUTRAL_CRITICAL_STRIKE': 'atNeutralCriticalStrike',
    'POISON_CRITICAL_STRIKE': 'atPoisonCriticalStrike',
    'PHYSICS_OVERCOME_BASE': 'atPhysicsOvercomeBase',
    'POISON_OVERCOME_BASE': 'atPoisonOvercomeBase',
    'PARRY_BASE': 'atParryBase', 'PARRYVALUE_BASE': 'atParryValueBase',
    'DODGE': 'atDodge', 'MAX_LIFE_PERCENT_ADD': 'atMaxLifePercentAdd',
    'DST_NPC_DAMAGE_COEFFICIENT': 'atDstNpcDamageCoefficient',
    'DECRITICAL_DAMAGE_POWER_BASE_KILONUM_RATE': 'atDecriticalDamagePowerBaseKiloNumRate',
    'LIFE_REPLENISH_EXT': 'atLifeReplenishExt',
}
MAIN_ATTRIBUTES = {'STRENGTH': '力道', 'AGILITY': '身法', 'SPIRIT': '根骨',
                   'SPUNK': '元气', 'VITALITY': '体质'}
DERIVED_ATTRIBUTES = {'ATTACK_POWER': '攻击', 'CRITICAL_STRIKE': '会心', 'OVERCOME': '破防',
                      'THERAPY_POWER': '治疗', 'MAX_LIFE': '气血', 'MAX_MANA': '内力',
                      'SHIELD': '防御', 'PARRY': '招架', 'PARRY_VALUE': '拆招', 'DODGE': '闪避'}


def normalize_attributes(calls):
    base, conversions = {}, []
    for call in calls:
        name, value = call['attribute'], call['value_a']
        if name in BASE_ATTRIBUTE_NAMES:
            target = BASE_ATTRIBUTE_NAMES[name]
            base[target] = base.get(target, 0) + value
        if '_TO_' not in name or not name.endswith('_COF'):
            continue
        source, destination = name[:-4].split('_TO_', 1)
        if source not in MAIN_ATTRIBUTES:
            continue
        school = 'All'
        for prefix in ('SOLAR_AND_LUNAR', 'PHYSICS', 'SOLAR', 'NEUTRAL', 'LUNAR', 'POISON', 'MAGIC'):
            if destination.startswith(prefix + '_'):
                school, destination = prefix, destination[len(prefix) + 1:]
                break
        if destination not in DERIVED_ATTRIBUTES:
            raise ValueError(('Unknown conversion', name))
        conversions.append(dict(source=MAIN_ATTRIBUTES[source], target=DERIVED_ATTRIBUTES[destination],
            school=school, raw=value, denominator=1024, coefficient=value / 1024, enum=name,
            denominator_basis='Original client role_attribute.lua: R44 lijing 686/1024 and 82/1024, yunshang 727/1024 and 41/1024; current skill Lua controls the numerator'))
    return base, conversions


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
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.evidence_root, args.deps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'occupations': len(report['occupations']), 'output': str(args.output)}))


if __name__ == '__main__':
    main()

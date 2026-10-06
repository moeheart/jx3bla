"""Regenerate current Wujie kungfu attributes from portable original Lua 5.1.

The original GB18030 PlatformKungfu/skill/auto-learning tables select the
formal mobile kungfus. Captured AddAttribute calls come from original chunks,
not from decompiled source; the latter is retained as a separate cross-check.
Only these new profiles replace or extend xinfa50.json. Existing 9503 profiles
and their original shared-source evidence remain unchanged.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from release.GenerateXinfa50 import normalize_attributes
from release.Lua51Evidence import Chunk
from tools.Functions import getOccDetailFromXinfaCode, getOccType


CLIENT_VERSION = '1.6.0.9517'
EXTRACTION_DATE = '2026-10-06'
SCHOOLS = {
    '1d': 'Solar', '1t': 'Solar', '2d': 'Neutral', '2h': 'Neutral',
    '3d': 'Physics', '3t': 'Physics', '4p': 'Physics', '4m': 'Neutral',
    '5d': 'Lunar', '5h': 'Lunar', '6d': 'Poison', '6h': 'Poison',
    '7p': 'Physics', '7m': 'Poison', '8': 'Physics', '9': 'Physics',
    '10d': 'Solar', '10t': 'Solar', '21d': 'Physics', '21t': 'Physics',
    '22d': 'Lunar', '22h': 'Lunar', '23': 'Physics', '24': 'Physics',
    '25': 'Physics', '211': 'Neutral', '212d': 'Poison', '212h': 'Poison',
    '213': 'Physics', '214': 'Physics', '215': 'Neutral', '34': 'Lunar',
}
SHARED_ORIGINS = ('scripts/Include/Skill.lh', 'scripts/skill/include/kungfuConst.lh')
TABLE_ORIGINS = ('settings/skill/PlatformKungfu.tab', 'settings/skill/skills.tab',
                 'settings/skill_mobile/skills.tab')
PANEL_ORIGIN = 'ui/Script/common/role_attribute.lua'
PANEL_SHA256 = 'd7987af32bf1df9bd865f69a8edec91b21555023ef2e9aefca55e569550af25f'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    newline = '\r\n' if path.is_file() and b'\r\n' in path.read_bytes() else '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline=newline)


def read_table(path):
    """Decode original client table bytes, never the older UTF-8 projections."""
    raw = path.read_bytes()
    decoded = raw.decode('gb18030')
    if decoded.encode('gb18030') != raw:
        raise ValueError(('Table encoding did not round-trip', str(path)))
    return list(csv.DictReader(io.StringIO(decoded), delimiter='\t'))


def select_rows(unpacked):
    platform = read_table(unpacked / TABLE_ORIGINS[0])
    mobile = {row['SkillID']: row for row in read_table(unpacked / TABLE_ORIGINS[2])}
    normal = {row['SkillID']: row for row in read_table(unpacked / TABLE_ORIGINS[1])}
    rows, by_id = [], {}
    for relation in platform:
        skill_id = relation['MobileKungfuID']
        normal_occ = getOccDetailFromXinfaCode(relation['HDKungfuID'])
        if normal_occ not in SCHOOLS:
            raise ValueError(('Unknown formal platform kungfu', relation))
        occ = normal_occ + 'w'
        if getOccDetailFromXinfaCode(skill_id) != occ:
            raise ValueError(('Formal mobile ID disagrees with runtime mapping', relation, occ))
        if skill_id in by_id:
            if by_id[skill_id]['occ'] != occ:
                raise ValueError(('Mobile ID maps to two occupations', relation))
            by_id[skill_id]['platform_rows'].append(relation)
            continue
        source = mobile[skill_id]
        if source['IsMountAble'] != '1':
            raise ValueError(('Platform kungfu is not mountable', skill_id))
        script_file = source['ScriptFile'].replace('\\', '/')
        school_folder = script_file.split('/')[0]
        row = dict(occ=occ, name=('山居问水剑' if occ == '8w' else relation['Desc']) + '·悟',
                   SkillID=skill_id, SkillName=source['SkillName'], ScriptFile=script_file,
                   school=SCHOOLS[normal_occ], role=getOccType(occ),
                   origin='scripts/skill_mobile/' + script_file,
                   learning_origin='settings/skill_mobile/SkillAutoLearning/' + school_folder + '.tab',
                   platform_rows=[relation], source_row=source)
        rows.append(row)
        by_id[skill_id] = row
    if len(rows) != 32:
        raise ValueError(('Expected all 32 formal Wujie kungfus', len(rows)))
    source = normal['10821']
    script_file = source['ScriptFile'].replace('\\', '/')
    rows.append(dict(occ='34', name='幽罗引', SkillID='10821', SkillName=source['SkillName'],
                     ScriptFile=script_file, school='Lunar', role=getOccType('34'),
                     origin='scripts/skill/' + script_file,
                     learning_origin='settings/skill/SkillAutoLearning/' + script_file.split('/')[0] + '.tab',
                     platform_rows=[], source_row=source))
    return rows


def learning_evidence(unpacked, row):
    path = unpacked / row['learning_origin']
    candidates = [item for item in read_table(path) if item['SkillID'] == row['SkillID']
                  and item.get('IsEnableAutoLearning') == '1'
                  and int(item['RequirePlayerLevel'] or 0) <= 50]
    learned = max(candidates, key=lambda item: int(item['SkillLevel']))
    if learned['RequirePlayerLevel'] != '50' or learned['SkillLevel'] != '5':
        raise ValueError(('Unexpected current level-50 learning row', row['SkillID'], learned))
    return dict(origin=row['learning_origin'], row=learned,
                sha256=digest(path.read_bytes()), encoding='GB18030')


def prepare_evidence(source_root, evidence_root, java, unluac):
    """Preserve exact current originals and independently decode readable Lua."""
    rows = select_rows(source_root)
    origins = set(TABLE_ORIGINS + SHARED_ORIGINS + (PANEL_ORIGIN,))
    for row in rows:
        origins.update((row['origin'], row['learning_origin']))
    manifest = dict(client_version=CLIENT_VERSION, mode='zhcn_exp',
                    source_client='C:/SeasunGame/Game/JX3_EXP',
                    unpack_tool='C:/Develop/26/jx3decrypt/unpack.exe',
                    extraction_date=EXTRACTION_DATE, source_encoding='GB18030',
                    selection='32 unique mobile IDs from original PlatformKungfu.tab; ordinary 10821',
                    unluac_jar=str(unluac), files=[])
    for origin in sorted(origins):
        source = source_root / origin
        raw = source.read_bytes()
        destination = evidence_root / 'unpack_result' / origin
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entry = dict(origin=origin, sha256=digest(raw), bytes=len(raw),
                     mtime_ns=source.stat().st_mtime_ns)
        if raw.startswith(b'\x1bLua'):
            Chunk(raw)  # Includes the required exact 32-bit bytecode round-trip.
            process = subprocess.run([java, '-jar', str(unluac), '--rawstring', str(destination)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=45)
            readable = process.stdout.decode('gb18030')
            readable_path = evidence_root / 'lua_readable' / origin
            readable_path.parent.mkdir(parents=True, exist_ok=True)
            readable_path.write_text(readable, encoding='utf-8', newline='\n')
            entry.update(format='Lua51 bytecode', readable_sha256=digest(readable_path.read_bytes()),
                         readable_method='unluac --rawstring; GB18030 to UTF-8')
        else:
            read_table(destination)
            entry.update(format='client TSV', encoding='GB18030')
        manifest['files'].append(entry)
    write_json(evidence_root / 'mount_skills.json', rows)
    write_json(evidence_root / 'occ_names.json', {row['occ']: row['name'] for row in rows})
    write_json(evidence_root / 'source_manifest.json', manifest)
    return rows


def verify_portable_evidence(evidence_root):
    manifest = json.loads((evidence_root / 'source_manifest.json').read_text(encoding='utf-8'))
    if manifest['client_version'] != CLIENT_VERSION:
        raise ValueError(('Evidence version differs', manifest['client_version']))
    for entry in manifest['files']:
        raw = (evidence_root / 'unpack_result' / entry['origin']).read_bytes()
        if len(raw) != entry['bytes'] or digest(raw) != entry['sha256']:
            raise ValueError(('Original differs from portable manifest', entry['origin']))
        if 'readable_sha256' in entry:
            readable = (evidence_root / 'lua_readable' / entry['origin']).read_bytes()
            if digest(readable) != entry['readable_sha256']:
                raise ValueError(('Readable copy differs from manifest', entry['origin']))
    selected = select_rows(evidence_root / 'unpack_result')
    saved = json.loads((evidence_root / 'mount_skills.json').read_text(encoding='utf-8'))
    if selected != saved:
        raise ValueError('Saved mount rows differ from original platform and skill tables')
    names = json.loads((evidence_root / 'occ_names.json').read_text(encoding='utf-8'))
    if names != {row['occ']: row['name'] for row in selected}:
        raise ValueError('Saved occupation names differ from formal kungfu selection')
    return selected


def audit(evidence_root, deps=None):
    if deps:
        sys.path.insert(0, str(deps.resolve()))
    from lupa.lua51 import LuaRuntime
    rows = verify_portable_evidence(evidence_root)
    unpacked = evidence_root / 'unpack_result'
    shared = Chunk((unpacked / SHARED_ORIGINS[0]).read_bytes())
    common = shared.named_function('AdditionalAttribute')
    common_text = (evidence_root / 'lua_readable' / SHARED_ORIGINS[0]).read_text(encoding='utf-8')
    common_body = re.search(r'(function AdditionalAttribute\([^\n]+\).*?\nend)', common_text, re.S).group(1)
    shared_source = {origin: digest((unpacked / origin).read_bytes()) for origin in SHARED_ORIGINS}
    profiles = {}
    for row in rows:
        raw = (unpacked / row['origin']).read_bytes()
        parsed = Chunk(raw)
        level = learning_evidence(unpacked, row)
        outputs, decompiler_issue = [], None
        for mode in ('bytecode', 'decompiled'):
            lua = LuaRuntime(encoding=None, register_eval=False, register_builtins=False)
            lua.execute(b'os=nil; io=nil; package=nil; python=nil; dofile=nil; loadfile=nil')
            globals_ = lua.globals()
            enum = lua.eval(b'function() return setmetatable({}, {__index=function(t,k) return k end}) end')
            for name in (b'ATTRIBUTE_EFFECT_MODE', b'ATTRIBUTE_TYPE', b'PLAYER_ARENA_TYPE',
                         b'SKILL_KIND_TYPE', b'CHARACTER_ENERGY_TYPE'):
                globals_[name] = enum()
            globals_[b'Include'] = lambda path: None
            if mode == 'bytecode':
                lua.execute(Chunk((unpacked / SHARED_ORIGINS[1]).read_bytes()).serialize())
                globals_[b'AdditionalAttribute'] = lua.eval(b'loadstring')(shared.serialize(proto=common))
                lua.execute(parsed.serialize())
            else:
                lua.execute((evidence_root / 'lua_readable' / SHARED_ORIGINS[1]).read_bytes())
                lua.execute(common_body.encode('utf-8'))
                lua.execute((evidence_root / 'lua_readable' / row['origin']).read_bytes())
            captured = []
            def capture(effect_mode, attribute, value_a, value_b):
                def clean(value):
                    if isinstance(value, bytes):
                        try:
                            return value.decode('utf-8')
                        except UnicodeDecodeError:
                            return value.decode('gb18030')
                    return value
                captured.append(dict(mode=clean(effect_mode), attribute=clean(attribute),
                                     value_a=clean(value_a), value_b=clean(value_b)))
            actor = lua.table_from({b'dwLevel': int(level['row']['SkillLevel']),
                                   b'dwSkillID': int(row['SkillID']), b'AddAttribute': capture})
            try:
                result = globals_[b'GetSkillLevelData'](actor)
            except Exception as error:
                if mode == 'bytecode':
                    raise RuntimeError((row['SkillID'], row['name'], mode)) from error
                decompiler_issue = str(error)
                outputs.append(None)
                continue
            if result is not True:
                raise ValueError((row['SkillID'], mode, 'GetSkillLevelData did not return true'))
            outputs.append(captured)
        if outputs[1] is not None and outputs[0] != outputs[1]:
            decompiler_issue = 'decompiled/original AddAttribute mismatch'
        summed = {}
        for call in outputs[0]:
            if isinstance(call['value_a'], (int, float)):
                attribute = call['attribute']
                summed[attribute] = summed.get(attribute, 0) + call['value_a']
        base, conversions = normalize_attributes(outputs[0])
        profiles[row['occ']] = dict(name=row['name'], skill_id=int(row['SkillID']), skill_level=5,
            school=row['school'], role=row['role'], client_version=CLIENT_VERSION,
            learning_source=level, raw_attributes=outputs[0], summed_enum_attributes=summed,
            base_attributes=base, conversions=conversions,
            source=dict(origin=row['origin'], sha256=digest(raw), bytes=len(raw),
                        evidence_root='wujie_evidence', client_version=CLIENT_VERSION,
                        extraction_date=EXTRACTION_DATE, shared_sources=shared_source),
            platform_rows=row['platform_rows'],
            original_bytecode_matches_decompiled=decompiler_issue is None,
            decompiler_issue=decompiler_issue)
    return profiles


def merge_profiles(existing, profiles):
    merged = dict(existing)
    merged['occupations'] = dict(existing['occupations'], **profiles)
    merged['client_version_scope'] = ('Retained ordinary profiles and original shared_source: 1.6.0.9503; '
                                      '32 Wujie profiles and ordinary 34: 1.6.0.9517')
    merged['profile_sources'] = {
        'retained': dict(client_version='1.6.0.9503', manifest='xinfa_evidence/source_manifest.json',
                         occupations=31, reextracted=False),
        'wujie_and_youluo': dict(client_version=CLIENT_VERSION, manifest='wujie_evidence/source_manifest.json',
                                occupations=len(profiles), extraction_date=EXTRACTION_DATE,
                                selected_from='original GB18030 settings/skill/PlatformKungfu.tab'),
    }
    return merged


def youluo_panel_evidence(evidence_root, profiles):
    """Record the ordinary UI branch separately from the mobile inference."""
    from tools.check_cangsheng_role_panel import disassemble, literal_tables
    raw = (evidence_root / 'unpack_result' / PANEL_ORIGIN).read_bytes()
    if digest(raw) != PANEL_SHA256:
        raise ValueError('Current Youluo panel bytecode changed; review instruction offsets')
    chunk = Chunk(raw)
    registers, globals_, _ = literal_tables(chunk)
    parameters = registers[57]
    if registers[36] != 'youluo' or globals_['PlayerKungfuName'].get(10821) != 'youluo':
        raise ValueError('Ordinary Youluo panel dispatch differs')
    if 102393 in globals_['PlayerKungfuName']:
        raise ValueError('Mobile Youluo now has a direct UI branch; review the inference')
    if (parameters['YouluoPhysicsAPToMagicAPCof'], parameters['YouluoWeaponToMagicAPCof']) != (1, 6):
        raise ValueError('Youluo attack conversion coefficients changed')
    flags = {occ: [call for call in profiles[occ]['raw_attributes']
                   if call['attribute'] == 'ADAPT_ATTRIBUTE_TYPE'] for occ in ('34', '34w')}
    if any(len(calls) != 1 or calls[0]['value_a'] != 1 for calls in flags.values()):
        raise ValueError('Ordinary/mobile adaptive-attribute flags differ')
    mapping = profiles['34w']['platform_rows']
    if len(mapping) != 1 or (mapping[0]['HDKungfuID'], mapping[0]['MobileKungfuID']) != ('10821', '102393'):
        raise ValueError('Ordinary/mobile Youluo platform relationship differs')
    return dict(schema_version=1, game_edition=160, client_version=CLIENT_VERSION,
        source=dict(origin=PANEL_ORIGIN, sha256=digest(raw), bytes=len(raw),
                    round_trip_exact=True, evidence_root='wujie_evidence'),
        youluo_conversions_R57=parameters,
        dispatch=dict(ordinary_skill_id=10821, ordinary_panel_name='youluo',
                      mobile_skill_id=102393, mobile_has_direct_ui_mapping=False),
        platform_mapping=mapping, adaptive_attribute_type_calls=flags,
        interpretation={
            'ordinary_model': 'Direct current client UI bytecode for 10821/youluo.',
            'mobile_model': ('Inference: 102393 has the same ADAPT_ATTRIBUTE_TYPE=1 flag and is mapped '
                             'to ordinary 10821 by PlatformKungfu.tab. Apply the ordinary adaptive model; '
                             'the UI PlayerKungfuName table does not directly contain mobile 102393.'),
            'equipment_primary': 'equipmentSpirit += max(equipmentStrength, equipmentSpunk, equipmentAgility, 0), before adding default player primary stats',
            'attack': 'lunarAP += max(solarAP, neutralAP, poisonAP, physicsAP + 6*(weaponBase + weaponRand/2), 0); clear converted source AP fields',
            'critical_strike': 'lunarCriticalStrike += max(physics, solar, neutral, poison critical-strike ratings, 0); clear converted source fields',
            'critical_damage': 'lunarCriticalDamagePowerBase += max(physics, solar, neutral, poison critical-damage ratings, 0); clear converted source fields',
            'overcome': 'lunarOvercomeBase += max(physics, solar, neutral, poison overcome ratings, 0); clear converted source fields',
            'boundary': 'Client panel evidence and static kungfu flags; no manual mobile-client panel comparison.'},
        instruction_evidence=dict(
            root_youluo_constants=disassemble(chunk.root, 1455, 1501),
            root_closure_bindings=disassemble(chunk.root, 1641, 1674) + disassemble(chunk.root, 1685, 1711),
            equipment_primary_child21=disassemble(chunk.root['children'][21]),
            attribute_conversion_child31=disassemble(chunk.root['children'][31]),
            youluo_panel_child32=disassemble(chunk.root['children'][32]),
            panel_dispatch_child39=disassemble(chunk.root['children'][39])))


def update_resource_manifest(resources, output, profiles):
    path = resources / 'source_manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    for entry in manifest['files']:
        if entry['name'] == 'xinfa50.json':
            raw = output.read_bytes()
            entry.update(bytes=len(raw), sha256=digest(raw), client_version='mixed: 1.6.0.9503 + 1.6.0.9517',
                         retained_evidence=True, added_profile_client_version=CLIENT_VERSION,
                         added_profile_count=len(profiles),
                         added_profile_source='wujie_evidence/source_manifest.json',
                         extraction_date=EXTRACTION_DATE)
            break
    else:
        raise ValueError('Runtime manifest has no xinfa50.json entry')
    manifest['runtime_status']['kungfu'] = '64_verified_profiles: 31_retained_9503 + 32_wujie_and_1_youluo_9517'
    manifest['attribute_evidence']['wujie_originals'] = 'wujie_evidence/source_manifest.json'
    manifest['attribute_evidence']['youluo_adaptive_panel'] = 'wujie_evidence/youluo_panel_evidence.json'
    manifest['attribute_evidence']['kungfu_client_version_scope'] = '31 retained 9503 ordinary profiles; 32 Wujie + ordinary 34 verified from 9517'
    manifest['client_version_scope'] = ('14 core tables retained from 2026-09-20 extraction (9506); '
                                        '31 ordinary kungfus, NPC and other retained evidence from 9503; '
                                        '32 Wujie kungfus and ordinary 34 added from 2026-10-06 extraction (9517)')
    manifest['retained_evidence']['description'] = ('The 31 prior ordinary kungfu profiles, NPC defenses, parameter Lua, '
        'role panel and native gem evidence remain from 9503. The 14 core tables remain from 9506. '
        'Only 32 Wujie kungfu profiles and ordinary Youluo were added from the isolated 9517 extraction.')
    write_json(path, manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, help='Current isolated unpack_result; omit to use portable evidence')
    parser.add_argument('--resources', type=Path, default=Path('equip/resources/cangshengtf'))
    parser.add_argument('--evidence-root', type=Path)
    parser.add_argument('--deps', type=Path)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--java', default='java')
    parser.add_argument('--unluac', type=Path, default=Path('C:/Develop/26/jx3decrypt/legacy/unluac/unluac.jar'))
    parser.add_argument('--check', action='store_true', help='Compare regenerated profiles without writing runtime data')
    args = parser.parse_args()
    evidence = args.evidence_root or args.resources / 'wujie_evidence'
    if args.source_root:
        prepare_evidence(args.source_root, evidence, args.java, args.unluac)
    profiles = audit(evidence, args.deps)
    panel = youluo_panel_evidence(evidence, profiles)
    panel_path = evidence / 'youluo_panel_evidence.json'
    if args.check:
        if json.loads(panel_path.read_text(encoding='utf-8')) != json.loads(json.dumps(panel)):
            raise ValueError('Regenerated Youluo panel evidence differs')
    else:
        write_json(panel_path, panel)
    output = args.output or args.resources / 'xinfa50.json'
    existing = json.loads((args.input or output).read_text(encoding='utf-8'))
    report = merge_profiles(existing, profiles)
    if args.check:
        retained = json.loads(output.read_text(encoding='utf-8'))
        if retained != report:
            raise ValueError('Regenerated original-bytecode kungfu data differs from xinfa50.json')
    else:
        write_json(output, report)
        if output.resolve() == (args.resources / 'xinfa50.json').resolve():
            update_resource_manifest(args.resources, output, profiles)
    print(json.dumps(dict(added_profiles=len(profiles), total_profiles=len(report['occupations']),
                          decompiler_issues={occ: profile['decompiler_issue'] for occ, profile in profiles.items()
                                             if profile['decompiler_issue']},
                          evidence=str(evidence), output=str(output)), ensure_ascii=True))


if __name__ == '__main__':
    main()

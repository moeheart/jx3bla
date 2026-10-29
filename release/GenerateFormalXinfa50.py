"""Rebuild formal-server level-50 attributes from portable Lua 5.1 originals.

The pre-release xinfa50.json stays frozen. This generator produces the 161+
profile from verified 10009 chunks; lupa is needed only for regeneration.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

from release.GenerateXinfa50 import normalize_attributes
from release.Lua51Evidence import Chunk

VERSION = '1.6.0.10009'
SHARED = 'scripts/Include/Skill.lh'
KUNGFU = 'scripts/skill/include/kungfuConst.lh'
GLOBAL = 'scripts/skill/GlobalParam.lua'
COMPRESSION = 'scripts/Include/数值压缩参数.lua'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def verify_evidence(evidence):
    manifest = json.loads((evidence / 'source_manifest.json').read_text(encoding='utf-8'))
    if manifest['client_version'] != VERSION or manifest['client_mode'] != 'zhcn_hd':
        raise ValueError('Wrong formal-server source')
    for entry in manifest['files']:
        raw = (evidence / 'unpack_result' / entry['origin']).read_bytes()
        if len(raw) != entry['bytes'] or digest(raw) != entry['sha256']:
            raise ValueError('Source hash mismatch: ' + entry['origin'])
        if raw.startswith(b'\x1bLua') and Chunk(raw).serialize(4) != raw:
            raise ValueError('Bytecode round-trip failed: ' + entry['origin'])
    selection = (evidence / 'selection.json').read_bytes()
    if digest(selection) != manifest['selection_sha256']:
        raise ValueError('Selection hash mismatch')
    return manifest, json.loads(selection)


def clean(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('gb18030')
    return value


def runtime():
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(encoding=None, register_eval=False, register_builtins=False)
    lua.execute(b'os=nil; io=nil; package=nil; python=nil; dofile=nil; loadfile=nil')
    return lua


def global_parameters(root):
    lua = runtime()
    globals_ = lua.globals()
    captured = lua.table()
    captured[b'LoadDamageCompressTables'] = lambda *args: None
    globals_[b'GetSkillGlobalParam'] = lambda: captured
    globals_[b'Log'] = lambda *args: None
    raw = (root / GLOBAL).read_bytes()
    lua.execute(Chunk(raw).serialize())
    globals_[b'Load']()
    values = {clean(key): value for key, value in captured.items() if isinstance(value, (int, float))}
    compression_raw = (root / COMPRESSION).read_bytes()
    compression = runtime()
    compression.execute(Chunk(compression_raw).serialize())
    factors = {str(level): compression.globals()[b'GetCofValue50ByLevel'](level)
               for level in (30, 31, 50, 51, 52, 53, 54)}
    return dict(client_version=VERSION, game_edition=161, values=values,
                level_factors=factors, sources=[dict(origin=origin, sha256=digest((root / origin).read_bytes()))
                    for origin in (GLOBAL, COMPRESSION)])


def generate(evidence, previous):
    manifest, rows = verify_evidence(evidence)
    root = evidence / 'unpack_result'
    shared = Chunk((root / SHARED).read_bytes())
    additional = shared.serialize(proto=shared.named_function('AdditionalAttribute'))
    kungfu = Chunk((root / KUNGFU).read_bytes()).serialize()
    profiles, alternate = {}, {}
    for row in rows:
        occ = row['occ']
        old = previous['alternate_xinfa']['10145'] if occ == 'alternate_10145' else previous['occupations'][occ]
        if row['source_row']['SkillID'] != str(old['skill_id']) or row['source_row']['IsMountAble'] != '1':
            raise ValueError('Invalid mountable skill selection: ' + occ)
        if row['origin'].split('/', 2)[2] != row['source_row']['ScriptFile'].replace('\\', '/'):
            raise ValueError('Selected script differs from current table: ' + occ)
        learning_raw = (root / row['learning_origin']).read_bytes()
        learning_rows = csv.DictReader(io.StringIO(learning_raw.decode('gb18030')), delimiter='\t')
        candidates = [item for item in learning_rows if item.get('SkillID') == str(row['skill_id'])
                      and int(item.get('RequirePlayerLevel') or 0) <= 50
                      and item.get('IsEnableAutoLearning', '1') == '1']
        learned = max(candidates, key=lambda item: int(item['SkillLevel']))
        if (learned['RequirePlayerLevel'], learned['SkillLevel']) != ('50', '5'):
            raise ValueError('Unexpected level-50 learning row: ' + occ)
        lua = runtime()
        globals_ = lua.globals()
        enum = lua.eval(b'function() return setmetatable({}, {__index=function(t,k) return k end}) end')
        for name in (b'ATTRIBUTE_EFFECT_MODE', b'ATTRIBUTE_TYPE', b'PLAYER_ARENA_TYPE', b'SKILL_KIND_TYPE', b'CHARACTER_ENERGY_TYPE'):
            globals_[name] = enum()
        globals_[b'Include'] = lambda path: None
        lua.execute(kungfu)
        globals_[b'AdditionalAttribute'] = lua.eval(b'loadstring')(additional)
        raw = (root / row['origin']).read_bytes()
        lua.execute(Chunk(raw).serialize())
        calls = []
        def capture(mode, attribute, value_a, value_b):
            calls.append(dict(mode=clean(mode), attribute=clean(attribute), value_a=clean(value_a), value_b=clean(value_b)))
        actor = lua.table_from({b'dwLevel': 5, b'dwSkillID': row['skill_id'], b'AddAttribute': capture})
        if globals_[b'GetSkillLevelData'](actor) is not True:
            raise ValueError('Original GetSkillLevelData failed: ' + occ)
        summed = {}
        for call in calls:
            if isinstance(call['value_a'], (int, float)):
                key = call['attribute']
                summed[key] = summed.get(key, 0) + call['value_a']
        base, conversions = normalize_attributes(calls)
        profile = dict(name=row['name'], skill_id=row['skill_id'], skill_level=5,
                       client_version=VERSION, raw_attributes=calls, summed_enum_attributes=summed,
                       base_attributes=base, conversions=conversions,
                       learning_source=dict(origin=row['learning_origin'], sha256=digest(learning_raw), row=learned),
                       source=dict(origin=row['origin'], sha256=digest(raw), bytes=len(raw),
                           evidence_root='xinfa10009_evidence', client_version=VERSION,
                           method='Original Lua 5.1 GetSkillLevelData captured at learned level 5',
                           shared_sources=[dict(origin=origin, sha256=digest((root / origin).read_bytes()))
                                           for origin in (SHARED, KUNGFU)]))
        for key in ('school', 'role', 'platform_rows'):
            if key in old:
                profile[key] = old[key]
        if occ == 'alternate_10145':
            alternate['10145'] = profile
        else:
            profiles[occ] = profile
    if len(profiles) != 64 or len(alternate) != 1:
        raise ValueError('Incomplete formal kungfu set')
    return (dict(schema_version=1, game_edition=161, client_version=VERSION, player_level=50,
                 status='raw_xinfa_verified', occupations=profiles, alternate_xinfa=alternate,
                 evidence_manifest='xinfa10009_evidence/source_manifest.json'), global_parameters(root))


def npc_profiles(evidence, parameters):
    from tools.check_luoyang_npc_defense import extract
    origin = 'settings/NpcTemplate/25RenPuTongLuoYangZhiZhan/sNpcTemplate.tab'
    data = extract(evidence / 'unpack_result' / origin)
    data['gameEdition'] = 161
    data['clientVersion'] = VERSION
    data['source']['path'] = 'xinfa10009_evidence/unpack_result/' + origin
    # Timestamps do not affect the portable generated artifact.
    data['source'].pop('mtimeUtc', None)
    data['staleCacheWarning'] = 'Uses preserved 10009 raw client table; no shared NPC cache.'
    values = parameters['values']
    hashes = {row['origin']: row['sha256'] for row in parameters['sources']}
    data['parameters'] = dict(physicsShieldParam=values['fPhysicsShieldParam'],
        magicShieldParam=values['fMagicShieldParam'], strainParam=values['fInsightParam'],
        levelFactors=parameters['level_factors'], globalParamsSha256=hashes[GLOBAL],
        compressionParamsSha256=hashes[COMPRESSION])
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, default=Path('equip/resources/cangshengtf'))
    parser.add_argument('--deps', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.deps:
        sys.path.insert(0, str(args.deps.resolve()))
    previous = json.loads((args.resources / 'xinfa50.json').read_text(encoding='utf-8'))
    profiles, parameters = generate(args.resources / 'xinfa10009_evidence', previous)
    npc = npc_profiles(args.resources / 'xinfa10009_evidence', parameters)
    for filename, data in (('xinfa50_hd.json', profiles), ('global_parameters_hd.json', parameters),
                           ('luoyang_npc_defense_hd.json', npc)):
        output = args.resources / filename
        if args.check:
            if json.loads(output.read_text(encoding='utf-8')) != data:
                raise ValueError('Regeneration differs: ' + filename)
        else:
            write_json(output, data)
    print(json.dumps(dict(occupations=len(profiles['occupations']), client_version=VERSION, checked=args.check)))


if __name__ == '__main__':
    main()

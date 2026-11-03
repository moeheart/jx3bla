"""Build equipment-only fallback means from selected current 50-level JCLs.

Example:
    python -X utf8 -m release.AverageEquipmentGenerator combat_logs . --since 2026-10-29 \
        --audit .tmp/average-equipment-fallback/sampling-audit.json

Only complete gear with fully supported attributes enters the average. Each
server+character name+kungfu contributes its latest such snapshot once, so repeated boss
attempts do not increase that character's weight. Client kungfu/base attributes
are deliberately omitted; the runtime must add the missing player's own profile.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from equip.AttributeCal import AttributeCal
from equip.CangshengAttributeData import kungfu_data, profile_school
from equip.EquipmentFallback import REQUIRED_EQUIPMENT_SLOTS
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from tools.Functions import getOccDetailFromXinfaCode, getOccType
from tools.LoadData import LuaTableAnalyserToDict
from tools.Attribute import CURRENT_GAME_EDITION


REQUIRED_SLOTS = REQUIRED_EQUIPMENT_SLOTS
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'equip' / 'resources' / 'cangshengtf' / 'average_equipment.json'


def read_player_equipment(path):
    """Read only PLAYER_INFO; leave the JCL and combat events untouched."""
    raw = path.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('gb18030')
    players = {}
    server = ''
    client_mode = ''
    parser = LuaTableAnalyserToDict()
    for line in text.splitlines():
        fields = line.split('\t', 5)
        if len(fields) != 6 or fields[4] not in ('1', '4'):
            continue
        row = parser.analyse(fields[5], delta=1)
        if fields[4] == '1':
            if not server:
                parts = row.get('2', '').strip('"').split(':')
                client_mode = parts[0]
                if len(parts) > 2:
                    server = parts[2]
            continue
        player_id = row['1']
        name = row.get('2', '').strip('"')
        previous_name = players.get(player_id, {}).get('name', '')
        if player_id not in players or row.get('6'):
            players[player_id] = {'occ': getOccDetailFromXinfaCode(row['4']),
                                  'equipment': row.get('6', {}), 'score': row.get('5', '0'),
                                  'name': name or previous_name}
        elif name:
            players[player_id]['name'] = name
    for player in players.values():
        player['server'] = server
    return {'file': path.name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'clientMode': client_mode}, players


def collect_paths(inputs, since):
    paths = set()
    for path in inputs:
        if path.is_dir():
            paths.update(path.glob('*.jcl'))
        elif path.is_file():
            paths.add(path)
        else:
            raise FileNotFoundError(path)
    # The current shipped NPC/equipment profile is the 50-level Luoyang client.
    # The caller chooses a bounded date range rather than importing legacy logs.
    return sorted((path for path in paths if path.suffix.lower() == '.jcl'
                   and '(835)' in path.name and path.name[:10] >= since),
                  key=lambda path: (path.name, str(path)))


def build_average_equipment(paths):
    cal = AttributeCal(CURRENT_GAME_EDITION)
    converter = EquipmentAnalyser()
    exporter = ExcelExportEquipment()
    profiles = kungfu_data()['occupations']
    sources, excluded = [], []
    latest = {}
    seen_log_hashes = set()
    complete_snapshots = Counter()
    for path in paths:
        source, players = read_player_equipment(path)
        if source['clientMode'] != 'zhcn_hd':
            raise ValueError('Average equipment requires a formal-server (zhcn_hd) JCL: ' + str(path))
        if source['sha256'] in seen_log_hashes:
            continue
        seen_log_hashes.add(source['sha256'])
        sources.append(source)
        for player_id, player in players.items():
            occ = player['occ']
            reason, warnings, missing_slots = None, [], []
            if occ not in profiles:
                reason = 'unsupported_xinfa'
            elif not player['equipment']:
                reason = 'missing_equipment'
            else:
                try:
                    equips = converter.convert2(player['equipment'], player['score'])
                    present = {pos for pos, row in equips.items() if isinstance(row, dict)
                               and str(row.get('id', '')).strip() not in ('', '0')}
                    missing_slots = sorted(REQUIRED_SLOTS - present)
                    if missing_slots:
                        reason = 'missing_slots'
                    else:
                        equip_str = exporter.export(equips)
                        raw_attributes = cal.CalculateAll(equip_str)
                        warnings = list(cal.lastWarnings)
                        if warnings:
                            reason = 'unsupported_effects'
                        elif not raw_attributes:
                            reason = 'missing_attributes'
                except (KeyError, ValueError, IndexError, TypeError) as exc:
                    reason = 'calculation_error:' + str(exc)
            if reason:
                excluded.append({'file': path.name, 'player': player_id, 'occ': occ,
                                 'reason': reason, 'warnings': warnings, 'missingSlots': missing_slots})
                continue
            complete_snapshots[occ] += 1
            # JCL runtime actor IDs can be reused between sessions. A nonempty
            # server+name is the stable character identity available in JCL.
            identity = (player.get('server', ''), player.get('name', ''))
            if not identity[1]:
                identity = (source['sha256'], player_id)
            latest[(*identity, occ)] = {'file': path.name, 'sha256': source['sha256'],
                                       'player': player_id, 'occ': occ,
                                       'characterKeySHA256': hashlib.sha256('\0'.join(identity).encode()).hexdigest(),
                                       'equipment': raw_attributes,
                                       'equipStrSha256': hashlib.sha256(equip_str.encode()).hexdigest()}
    grouped = defaultdict(list)
    for sample in latest.values():
        grouped[sample['occ']].append(sample)
    occupations = {}
    for occ, samples in sorted(grouped.items()):
        keys = sorted(set().union(*(sample['equipment'] for sample in samples)))
        mean = {key: sum(sample['equipment'].get(key, 0) for sample in samples) / len(samples) for key in keys}
        occupations[occ] = {
            'equipment': mean, 'sampleCount': len(samples),
            'sourceDates': sorted({sample['file'][:10] for sample in samples}),
            'school': profile_school(occ), 'role': getOccType(occ),
            'completeSnapshotCount': complete_snapshots[occ],
        }
    aliases = {}
    for occ in sorted(set(profiles) - set(occupations)):
        sibling = occ[:-1] if occ.endswith('w') else occ + 'w'
        if sibling in occupations and profile_school(occ) == profile_school(sibling) and getOccType(occ) == getOccType(sibling):
            aliases[occ] = sibling
    summary = dict(Counter(row['reason'] for row in excluded))
    result = {
        'schema': 1, 'gameEdition': CURRENT_GAME_EDITION, 'profile': 'cangsheng50', 'level': 50,
        'clientVersion': '1.6.0.10009', 'clientMode': 'zhcn_hd',
        'method': 'Arithmetic mean of equipment-only raw at* attributes, one latest complete supported snapshot per server+character name+kungfu. Runtime player IDs are not reused as cross-session identities; unnamed snapshots are not deduplicated across logs. Missing numeric fields contribute zero. Normal/mobile aliases share equipment only; own client kungfu attributes must be added at runtime.',
        'requiredSlots': sorted(REQUIRED_SLOTS), 'optionalSlots': ['1'],
        'sourceDates': sorted({source['file'][:10] for source in sources}),
        'sourceFiles': sources, 'sourceFileCount': len(sources),
        'sampleCount': len(latest), 'exclusionCounts': summary,
        'occupations': occupations, 'aliases': aliases,
        'unavailableOccupations': sorted(set(profiles) - set(occupations) - set(aliases)),
    }
    audit = {
        'gameEdition': CURRENT_GAME_EDITION, 'method': result['method'],
        'sourceFiles': [dict(source, sourcePaths=[str(path.resolve()) for path in paths
                       if path.name == source['file']]) for source in sources],
        'selectedSamples': [{key: value for key, value in sample.items() if key != 'equipment'} for sample in latest.values()],
        'excludedSnapshots': excluded, 'exclusionCounts': summary,
    }
    return result, audit


def update_source_manifest(output, result):
    """Keep provenance in sync when replacing the shipped average profile."""
    manifest_path = output.parent / 'source_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    raw = output.read_bytes()
    metadata = dict(name=output.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                    client_version=result['clientVersion'], client_mode=result['clientMode'],
                    source_dates=result['sourceDates'], source_files=result['sourceFileCount'],
                    supported_samples=result['sampleCount'], method=result['method'])
    for entry in manifest['files']:
        if entry['name'] == output.name:
            entry.update(metadata)
            break
    else:
        manifest['files'].append(metadata)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path, nargs='+', help='JCL files or directories containing them')
    parser.add_argument('--since', default='2026-10-29', help='Earliest selected formal-season JCL date (YYYY-MM-DD)')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--audit', type=Path)
    args = parser.parse_args()
    paths = collect_paths(args.inputs, args.since)
    result, audit = build_average_equipment(paths)
    if not result['sampleCount']:
        raise ValueError('No complete, supported current-season equipment samples were found')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.output.resolve() == DEFAULT_OUTPUT.resolve():
        update_source_manifest(args.output, result)
    if args.audit:
        args.audit.parent.mkdir(parents=True, exist_ok=True)
        args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sourceFiles': len(result['sourceFiles']), 'samples': result['sampleCount'],
                      'occupations': {occ: row['sampleCount'] for occ, row in result['occupations'].items()},
                      'aliases': len(result['aliases']), 'unavailable': result['unavailableOccupations'],
                      'excluded': result['exclusionCounts']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

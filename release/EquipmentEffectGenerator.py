"""Build the bounded equipment-effect catalogue from reviewed portable evidence."""
import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/160/evidence/equipment_effects'
HEROIC_EVIDENCE = ROOT / 'docs/160/evidence/heroic_equipment10082'
OUTPUT = ROOT / 'equip/resources/cangshengtf/equipment_effects.json'
HANDLINGS = {'logged_event', 'skill_coefficient', 'inactive_mobile',
             'inactive_ordinary', 'static_attributes', 'non_combat'}
SOURCE_VERSIONS = ['1.6.0.10009', '1.6.0.10072', '1.6.0.10082', '1.6.0.10086']


def build_catalogue(evidence=EVIDENCE, supplemental=HEROIC_EVIDENCE):
    """Never infer support from the effect's at* category or an ID interval."""
    effects, sources = {}, []
    for directory in (Path(evidence), Path(supplemental)) if supplemental is not None else (Path(evidence),):
        seen = set()
        for name in ('recipe-models.json', 'script-models.json', 'event-models.json'):
            path = directory / name
            raw = path.read_bytes()
            label = name if directory == Path(evidence) else '../' + directory.name + '/' + name
            sources.append({'file': label, 'sha256': hashlib.sha256(raw).hexdigest()})
            for row in json.loads(raw):
                key = (row['type'], row['value1'], row['value2'])
                if key in seen or row['ordinaryHandling'] not in HANDLINGS:
                    raise ValueError('Invalid or repeated effect: %r' % (key,))
                if not row.get('name') or not row.get('evidence'):
                    raise ValueError('Effect has no evidence/name: %r' % (key,))
                if directory != Path(evidence):
                    row = dict(row, evidence='../' + directory.name + '/' + row['evidence'])
                if 'wujieHandling' in row and (
                        row['wujieHandling'] not in HANDLINGS or not isinstance(row.get('wujieOccupations'), list)
                        or not row['wujieOccupations']
                        or not all(isinstance(occ, str) and occ.endswith('w') for occ in row['wujieOccupations'])):
                    raise ValueError('Wujie effect has no reviewed specialization scope: %r' % (key,))
                for attribute, value in row.get('staticAttributes', {}).items():
                    if not attribute.startswith('at') or type(value) is not int:
                        raise ValueError('Invalid audited static attribute')
                if key in effects:
                    previous = effects[key]
                    if (previous['ordinaryHandling'] != row['ordinaryHandling'] or
                            previous.get('staticAttributes', {}) != row.get('staticAttributes', {})):
                        raise ValueError('Supplement changes existing ordinary semantics: %r' % (key,))
                    row = dict(previous, **row)
                seen.add(key)
                effects[key] = row
    return {'schemaVersion': 1, 'profile': 'cangsheng50',
            'scope': 'Exact audited effects; Wujie requires separate handling and an explicit specialization scope. Unlisted identities remain unverified.',
            'sourceVersions': SOURCE_VERSIONS if supplemental is not None else SOURCE_VERSIONS[:2],
            'evidenceSources': sources,
            'effects': sorted(effects.values(), key=lambda row: (row['type'], row['value1'], row['value2']))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = json.dumps(build_catalogue(), ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if OUTPUT.read_text(encoding='utf-8') != generated:
            raise ValueError('Equipment effect catalogue differs from audited evidence')
    else:
        OUTPUT.write_text(generated, encoding='utf-8', newline='\n')
        manifest_path = OUTPUT.parent / 'source_manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['files'] = [row for row in manifest['files'] if row['name'] != OUTPUT.name]
        manifest['files'].append({
            'name': OUTPUT.name, 'bytes': OUTPUT.stat().st_size,
            'sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
            'client_versions': SOURCE_VERSIONS,
            'client_mode': 'zhcn_hd', 'generation': 'release.EquipmentEffectGenerator',
            'evidence': '../../../docs/160/evidence/equipment_effects',
        })
        manifest['runtime_status']['equipment_effects'] = 'audited_exact_identities_with_explicit_platform_scopes'
        manifest['equipment_effect_update'] = {
            'prepared_version': '8.16.7',
            'publication_record': '../../../docs/160/8.16.7发布记录.md',
            'source_versions': SOURCE_VERSIONS,
            'boundary': 'Heroic equipment rows compared against formal 10082 tables; newly extracted Lua and recipe paths are 10086 evidence. Wujie requires exact reviewed effect and specialization scope; unlisted effects remain unverified.',
            'supplemental_evidence': '../../../docs/160/evidence/heroic_equipment10082',
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Verified %d equipment effect identities' % len(build_catalogue()['effects']))


if __name__ == '__main__':
    main()

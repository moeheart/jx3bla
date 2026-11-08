"""Build the bounded equipment-effect catalogue from reviewed portable evidence."""
import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/160/evidence/equipment_effects'
OUTPUT = ROOT / 'equip/resources/cangshengtf/equipment_effects.json'
HANDLINGS = {'logged_event', 'skill_coefficient', 'inactive_mobile',
             'static_attributes', 'non_combat'}


def build_catalogue(evidence=EVIDENCE):
    """Never infer support from the effect's at* category or an ID interval."""
    effects, sources, keys = [], [], set()
    for name in ('recipe-models.json', 'script-models.json', 'event-models.json'):
        path = Path(evidence) / name
        raw = path.read_bytes()
        sources.append({'file': name, 'sha256': hashlib.sha256(raw).hexdigest()})
        for row in json.loads(raw):
            key = (row['type'], row['value1'], row['value2'])
            if key in keys or row['ordinaryHandling'] not in HANDLINGS:
                raise ValueError('Invalid or repeated effect: %r' % (key,))
            if not row.get('name') or not row.get('evidence'):
                raise ValueError('Effect has no evidence/name: %r' % (key,))
            for attribute, value in row.get('staticAttributes', {}).items():
                if not attribute.startswith('at') or type(value) is not int:
                    raise ValueError('Invalid audited static attribute')
            keys.add(key)
            effects.append(row)
    return {'schemaVersion': 1, 'profile': 'cangsheng50',
            'scope': 'Audited ordinary-kungfu effects; Wujie and unknown identities remain unverified.',
            'sourceVersions': ['1.6.0.10009', '1.6.0.10072'],
            'evidenceSources': sources,
            'effects': sorted(effects, key=lambda row: (row['type'], row['value1'], row['value2']))}


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
            'client_versions': ['1.6.0.10009', '1.6.0.10072'],
            'client_mode': 'zhcn_hd', 'generation': 'release.EquipmentEffectGenerator',
            'evidence': '../../../docs/160/evidence/equipment_effects',
        })
        manifest['runtime_status']['equipment_effects'] = 'audited_exact_identities_for_ordinary_kungfu'
        manifest['equipment_effect_update'] = {
            'prepared_version': '8.16.6', 'published': False,
            'source_versions': ['1.6.0.10009', '1.6.0.10072'],
            'boundary': 'Relevant archived and fresh table rows compared; newly extracted Lua bodies are 10072 evidence. Wujie effects and unlisted identities stay unverified.',
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Verified %d equipment effect identities' % len(build_catalogue()['effects']))


if __name__ == '__main__':
    main()

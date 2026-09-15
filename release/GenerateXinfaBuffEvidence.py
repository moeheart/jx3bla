"""Export exact current buff rows supporting temporary attribute conversions.

This is audit evidence, not another runtime buff table. Runtime data continues
to come from NameGenerator/NameCangsheng, including all unrelated attributes.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re


CRITICAL_EFFECTS = {'atUnlimitCriticalDamagePowerKiloNumRate',
                    'atMagicCriticalDamagePowerPercent'}


def export(root):
    names = {}
    with (root / 'buff.txt').open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            names[(row['BuffID'], row['Level'])] = row
    conversions, critical = [], []
    with (root / 'buff.tab').open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            effects = []
            for key, attribute in row.items():
                if not attribute or not re.fullmatch('BeginAttrib[0-9]+', key):
                    continue
                if re.fullmatch(r'at(Vitality|TherapyPower)To.+Cof', attribute) or attribute in CRITICAL_EFFECTS:
                    number = key[len('BeginAttrib'):]
                    effects.append(dict(attribute=attribute,
                        value_a=row.get('BeginValue' + number + 'A'),
                        value_b=row.get('BeginValue' + number + 'B')))
            if not effects:
                continue
            display = names.get((row['ID'], row['Level']))
            display_level = row['Level']
            if display is None:
                # This only selects UI text. Effect values never fall back.
                display = names.get((row['ID'], '0'), {})
                display_level = '0' if display else None
            record = dict(buff_id=int(row['ID']), level=int(row['Level']),
                effects=effects, source_row={k: v for k, v in row.items() if v},
                display_level=display_level, name=display.get('Name'), description=display.get('Desc'))
            if any(item['attribute'] in CRITICAL_EFFECTS for item in effects):
                critical.append(record)
            if any(item['attribute'] not in CRITICAL_EFFECTS for item in effects):
                conversions.append(record)
    return dict(schema_version=1, game_edition=160, client_version='1.6.0.9503',
        sources=[dict(file=name, sha256=hashlib.sha256((root / name).read_bytes()).hexdigest())
                 for name in ('buff.tab', 'buff.txt')],
        conversion_rows=conversions, critical_effect_rows=critical,
        interpretation={
            'conversion_denominator': 1024,
            'unlimited_critical_effect_denominator': 1024,
            'magic_critical_effect_percent_denominator': 10000,
            'tank_application': 'Use the exact logged 17885/29938 ID and level; do not compress again or apply another x3.',
            'critical_effect_cap': 'The source rows and tooltip percentages do not establish the native cap or overflow order.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, default=Path('equip/resources/cangshengtf'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = export(args.resources)
    path = args.resources / 'xinfa_buff_evidence.json'
    if args.check:
        assert json.loads(path.read_text(encoding='utf-8')) == data, 'Buff evidence differs from current tables'
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'conversions': len(data['conversion_rows']),
                      'critical_effects': len(data['critical_effect_rows'])}))


if __name__ == '__main__':
    main()

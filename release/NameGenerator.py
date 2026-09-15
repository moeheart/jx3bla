"""Generate replay tables from versioned extraction; old output stays separate."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
from tools.Attribute import ATTRIB_TYPE
from equip.CangshengAttributeData import conversion_spec

EXTRA_ATTRIBUTE_TYPES = {'atPVXAllRound', 'atTherapyPVXAllRound',
                       'atMaxLifeBase', 'atMaxLifePercentAdd', 'atTherapyPowerBasePercentAdd',
                       'atDstNpcDamageCoefficient', 'atUnlimitCriticalDamagePowerKiloNumRate'}

DAMAGE_SCHOOLS = ('Physics', 'Solar', 'Neutral', 'Lunar', 'Poison')
ABSORB_ATTRIBUTES = {
    'atGlobalDamageAbsorb', 'atPhysicsDamageAbsorb', 'atMagicDamageAbsorb',
    'atSolarDamageAbsorb', 'atLunarDamageAbsorb', 'atNeutralDamageAbsorb',
    'atPoisonDamageAbsorb', 'atGlobalDamageAbsorbBySelfMaxLife',
    'atGlobalDamageAbsorbBySelfSpirit', 'atGlobalDamageAbsorbBySelfAgility',
    'atGlobalDamageAbsorbBySelfVitality', 'atGlobalDamageAbsorbBySpirit',
    'atGlobalDamageAbsorbByAgility', 'atAddGlobalAbsorbShieldByParryValue',
}
THERAPY_ATTRIBUTES = {
    'atTherapyPowerBase', 'atTherapyPowerPercent', 'atTherapyCoefficient',
    'atAllTherapyAddPercent', 'atAllDamageAddPercent', 'atBeTherapyCoefficient',
    'atDamageAbsorbShieldCoefficient',
}


def read_rows(path, required):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        missing = set(required) - set(reader.fieldnames or ())
        if missing:
            raise ValueError('%s: missing columns %s' % (path, sorted(missing)))
        for line, row in enumerate(reader, 2):
            if None in row:
                raise ValueError('%s:%d: row has extra columns' % (path, line))
            yield row


def numeric(value, context):
    # Never silently truncate fractions or swallow a malformed buff value.
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('%s: invalid numeric value %r' % (context, value)) from error
    if not result.is_finite():
        raise ValueError('%s: nonfinite numeric value' % context)
    return int(result) if result == result.to_integral_value() else float(result)


def begin_attributes(row):
    # Active and EndTime entries are periodic/expiration actions, not effects
    # that remain throughout the buff lifetime.
    fields = sorted((key for key in row if re.fullmatch(r'BeginAttrib\d+', key)),
                    key=lambda key: int(key[11:]))
    for field in fields:
        attribute = (row[field] or '').strip()
        if attribute:
            yield attribute, (row.get('BeginValue%sA' % field[11:]) or '').strip()


def parse_buff(row):
    boost, therapy, raw = {}, {}, {}
    absorb = False
    for attribute, value in begin_attributes(row):
        absorb = absorb or attribute in ABSORB_ATTRIBUTES
        is_boost = attribute in ATTRIB_TYPE or attribute in EXTRA_ATTRIBUTE_TYPES or conversion_spec(attribute) is not None
        relevant = (is_boost or attribute in THERAPY_ATTRIBUTES
                    or attribute == 'atGlobalResistPercent'
                    or any(attribute in ('at%sDamageCoefficient' % school,
                                         'at%sResistPercent' % (school if school == 'Physics' else school + 'Magic'))
                           for school in DAMAGE_SCHOOLS))
        if not relevant or value == '':
            continue
        number = numeric(value, 'buff %s.%s %s' % (row['ID'], row['Level'], attribute))
        raw[attribute] = raw.get(attribute, 0) + number
        if is_boost:
            boost[attribute] = boost.get(attribute, 0) + number
        if attribute in THERAPY_ATTRIBUTES:
            therapy[attribute] = therapy.get(attribute, 0) + number
    resistance = {}
    for school in DAMAGE_SCHOOLS:
        attribute = 'at%sResistPercent' % (school if school == 'Physics' else school + 'Magic')
        value = raw.get('atGlobalResistPercent', 0) + raw.get(attribute, 0)
        value -= raw.get('at%sDamageCoefficient' % school, 0)
        if value:
            resistance[school] = value
    return absorb, boost, resistance, therapy


def build_tables(resources):
    resources = Path(resources)
    names, buffs = {}, {}
    for filename, scheme, id_column in (('buff.txt', 2, 'BuffID'), ('buff2.txt', 2, 'BuffID'),
                                        ('skill.txt', 1, 'SkillID'), ('skill2.txt', 1, 'SkillID')):
        for row in read_rows(resources / filename, (id_column, 'Level', 'Name')):
            if not row[id_column].isdigit() or not row['Level'].isdigit():
                continue
            names['%s,%s,%s' % (scheme, row[id_column], row['Level'])] = row['Name'] or ''
    for filename in ('buff.tab', 'buff2.tab'):
        for row in read_rows(resources / filename, ('ID', 'Level', 'BeginAttrib1', 'BeginValue1A')):
            if not row['ID'].isdigit() or not row['Level'].isdigit():
                continue
            key = '2,%s,%s' % (row['ID'], row['Level'])
            # A later empty row also replaces an earlier effect.
            buffs[key] = parse_buff(row)
    tables = {'SKILL_NAME': names, 'ABSORB_DICT': {}, 'RESIST_DICT': {},
              'BOOST_DICT': {}, 'RESIST_BY_SCHOOL_DICT': {}, 'THERAPY_DICT': {}}
    for key, (absorb, boost, resistance, therapy) in buffs.items():
        if absorb:
            tables['ABSORB_DICT'][key] = 1
        if boost:
            tables['BOOST_DICT'][key] = boost
        if resistance:
            tables['RESIST_BY_SCHOOL_DICT'][key] = resistance
            values = [resistance.get(school, 0) for school in DAMAGE_SCHOOLS]
            if len(set(values)) == 1 and values[0] > 0:
                tables['RESIST_DICT'][key] = values[0]
        if therapy:
            tables['THERAPY_DICT'][key] = therapy
    return tables


def write_tables(tables, output):
    output = Path(output)
    temporary = output.with_suffix(output.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write('# [Auto-Generated File] See release/NameGenerator.py and source_manifest.json.\n')
        for name, mapping in tables.items():
            stream.write(name + ' = {\n')
            for key, value in mapping.items():
                stream.write('    %r: %r,\n' % (key, value))
            stream.write('}\n')
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, default=Path('equip/resources'))
    parser.add_argument('--output', type=Path, default=Path('replayer/Name.py'))
    args = parser.parse_args()
    tables = build_tables(args.resources)
    write_tables(tables, args.output)
    print({key: len(value) for key, value in tables.items()})


if __name__ == '__main__':
    main()

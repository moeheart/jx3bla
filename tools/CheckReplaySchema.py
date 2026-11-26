"""Verify replay columns and engines from a MySQL information_schema TSV export."""
import argparse
from pathlib import Path


# The service inserts by position and the ranking worker reads by ordinal.
EXPECTED_COLUMNS = {
    'ReplayProStat': (
        'server id occ score battledate mapdetail boss hash shortid public edition '
        'editionfull replayedition userid battletime submittime battleid scorerank '
        'rhps rhpsrank hps hpsrank rdps rdpsrank ndps ndpsrank mrdps mrdpsrank '
        'mndps mndpsrank hold gameedition'
    ).split(),
    'ActorStat': (
        'server boss battledate mapdetail edition hash win editionfull userid '
        'battletime submittime instanceid gameedition team length'
    ).split(),
    'ReplayProStatRank': ['name', 'number', 'records'],
    'PreloadInfo': ['datakey', 'datavalue'],
    'ReplayProInfo': ['dataname', 'datavalue', 'datavalueint'],
}


def check_schema(text):
    errors, databases, wrong_engines = [], set(), set()
    columns = {name: {} for name in EXPECTED_COLUMNS}
    for line_number, line in enumerate(text.splitlines(), 1):
        fields = line.split('\t')
        if len(fields) != 5:
            return [f'Line {line_number}: expected five tab-separated fields without a header']
        database, table, ordinal, column, engine = fields
        databases.add(database)
        if table not in columns:
            errors.append(f'Line {line_number}: unexpected table {table!r}')
            continue
        if ordinal in columns[table]:
            errors.append(f'{table}: duplicate ordinal position {ordinal!r}')
        columns[table][ordinal] = column.lower()
        if engine.lower() != 'innodb':
            wrong_engines.add(table)

    if len(databases) != 1 or '' in databases:
        errors.append('Expected an export from exactly one named database')
    for table, expected in EXPECTED_COLUMNS.items():
        if table in wrong_engines:
            errors.append(f'{table}: expected InnoDB')
        if not columns[table]:
            errors.append(f'{table}: missing table')
        elif columns[table] != {str(i): name for i, name in enumerate(expected, 1)}:
            errors.append(f'{table}: column names or ordinal positions differ')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', type=Path, help='UTF-8 output from database/replay-columns.sql')
    args = parser.parse_args()
    try:
        errors = check_schema(args.export.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f'Cannot read metadata export: {exc}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'Verified column order and InnoDB for {len(EXPECTED_COLUMNS)} replay tables.')


if __name__ == '__main__':
    main()

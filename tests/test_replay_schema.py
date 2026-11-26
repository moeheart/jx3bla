"""The metadata export is the row-oriented output of database/replay-columns.sql."""
import sqlite3
import unittest
from pathlib import Path

from tools.CheckReplaySchema import check_schema


# Representative metadata for the positional contract used by the service.
SAMPLE_COLUMNS = {
    'ReplayProStat': ('server id occ score battledate mapdetail boss hash shortID public edition '
                      'editionfull replayedition userid battletime submittime battleID scoreRank '
                      'rhps rhpsRank hps hpsRank rdps rdpsRank ndps ndpsRank mrdps mrdpsRank '
                      'mndps mndpsRank hold gameEdition'),
    'ActorStat': ('server boss battledate mapdetail edition hash win editionfull userid '
                  'battletime submittime instanceid gameEdition team length'),
    'ReplayProStatRank': 'name number records',
    'PreloadInfo': 'datakey datavalue',
    'ReplayProInfo': 'dataname datavalue datavalueint',
}


class ReplaySchemaTests(unittest.TestCase):
    def setUp(self):
        self.rows = [(name, str(i), column, 'InnoDB') for name, columns in SAMPLE_COLUMNS.items()
                     for i, column in enumerate(columns.split(), 1)]

    def export(self, rows, database='restored'):
        return '\n'.join('\t'.join((database, *row)) for row in rows)

    def test_five_tables_and_ordinal_values(self):
        self.assertEqual(len(self.rows), 55)
        self.assertEqual(check_schema(self.export(reversed(self.rows))), [])
        self.assertEqual(self.rows[8], ('ReplayProStat', '9', 'shortID', 'InnoDB'))

    def test_engine_for_each_table(self):
        for table in SAMPLE_COLUMNS:
            with self.subTest(table=table):
                rows = [(*row[:3], 'MyISAM') if row[0] == table else row for row in self.rows]
                self.assertTrue(any(table in err and 'InnoDB' in err for err in check_schema(self.export(rows))))

    def test_mutations_to_ordinal_columns_and_missing_tables(self):
        permuted = [self.rows[0][:2] + self.rows[1][2:], self.rows[1][:2] + self.rows[0][2:], *self.rows[2:]]
        for rows in [permuted, self.rows[:-1], self.rows + [self.rows[0]],
                     [row for row in self.rows if row[0] != 'PreloadInfo']]:
            with self.subTest(length=len(rows)):
                self.assertTrue(check_schema(self.export(rows)))

    def test_schema_ambiguity_and_bad_export_format(self):
        text = self.export(self.rows)
        for bad in [text.replace('restored', 'other', 1), text.replace('restored', ''),
                    text.replace('\t1\t', '\tno\t', 1), text.replace('\t1\t', '\t0\t', 1),
                    text.replace('\t', ',', 1), text.replace('ActorStat', 'actorstat'), '']:
            with self.subTest(sample=bad[:40]):
                self.assertTrue(check_schema(bad))

    def test_metadata_query_exports_only_the_selected_database_and_tables(self):
        query = (Path(__file__).resolve().parents[1] / 'database/replay-columns.sql').read_text(encoding='utf-8')
        # Exercise the SELECT on two synthetic catalogs; no MySQL installation is needed.
        with sqlite3.connect(':memory:') as db:
            db.create_function('DATABASE', 0, lambda: 'restored')
            db.execute("ATTACH DATABASE ':memory:' AS information_schema")
            db.execute('CREATE TABLE information_schema.COLUMNS (TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION INT, COLUMN_NAME)')
            db.execute('CREATE TABLE information_schema.TABLES (TABLE_SCHEMA, TABLE_NAME, ENGINE)')
            for catalog in ('other', 'restored'):
                rows = self.rows + [('Unrelated', '1', 'ignored', 'MyISAM')]
                db.executemany('INSERT INTO information_schema.COLUMNS VALUES (?,?,?,?)',
                               [(catalog, name, int(i), col) for name, i, col, _ in rows])
                db.executemany('INSERT INTO information_schema.TABLES VALUES (?,?,?)',
                               {(catalog, name, engine) for name, _, _, engine in rows})
            metadata = db.execute(query).fetchall()
        self.assertEqual(len(metadata), 55)
        self.assertEqual({row[0] for row in metadata}, {'restored'})
        self.assertEqual(metadata, sorted(metadata, key=lambda row: (row[1], row[2])))
        tsv = '\n'.join('\t'.join(map(str, row)) for row in metadata)
        self.assertEqual(check_schema(tsv), [])

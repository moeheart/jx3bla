import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from data.BattleLogData import BattleLogData
from replayer.boss.luoyangzhizhan.WinEvidence import LuoyangWinEvidence


class TuliCorpseJclTests(unittest.TestCase):
    def load(self, records, boss="突利和顺(139306)"):
        lines = [f"{i}\t{i}\t1795673544\t{time}\t{kind}\t{body}"
                 for i, (time, kind, body) in enumerate(records)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / f"2026-11-26-14-07-57-25人普通洛阳之战(835)-{boss}.jcl"
            path.write_text("\n".join(lines), encoding="utf8")
            data = BattleLogData()
            with contextlib.redirect_stdout(io.StringIO()):
                data.loadFromJcl(str(path))
        return data

    boss = '{20,"突利和顺",139306,0,11,12,13,8}'
    corpse = '{299,1392,11,12,13,14}'

    def test_metadata_and_first_entry_in_either_order_preserve_combat_boundaries(self):
        for metadata in (1150, 1152):
            with self.subTest(metadata=metadata):
                records = [(1000, 8, self.boss), (1100, 9, "{20,true,100,100,0,0}"),
                           (1151, 10, "{299}"), (metadata, 12, self.corpse),
                           (1200, 12, self.corpse), (1210, 10, "{299}")]
                battle = self.load(sorted(records))
                self.assertEqual(battle.tuliCorpseSpawns, [(1151, "20", "299")])
                self.assertEqual([(event.dataType, event.time) for event in battle.log], [("Battle", 1100)])

    def test_old_corpses_clones_and_later_coordinates_do_not_match(self):
        records = [(1000, 8, self.boss),
                   (1010, 12, self.corpse), (1900, 12, self.corpse), (1901, 10, "{299}"),
                   (1920, 12, '{300,1392,11,12,20,14}'), (1921, 10, '{300}'),
                   (1930, 8, '{20,"突利和顺",139306,0,11,12,20,8}'),
                   (1935, 8, '{21,"突利和顺",139352,0,11,12,13,8}'),
                   (1940, 12, '{301,1392,11,12,13,14}'), (1941, 10, '{301}'),
                   (1950, 7, '{20}'), (1960, 12, '{302,1392,11,12,20,14}'), (1961, 10, '{302}'),
                   (1980, 8, '{20,"突利和顺",139306,0,0,0,0,8}'),
                   (1981, 12, '{303,1392,0,0,0,14}'), (1982, 10, '{303}'),
                   (2000, 8, self.boss), (2010, 12, '{304,1392,11,12,13,14}'),
                   (2011, 11, '{304}'), (2012, 10, '{304}'),
                   (2600, 6, '{20}'), (2610, 12, '{305,1392,11,12,13,14}'), (2611, 10, '{305}')]
        self.assertEqual(self.load(records).tuliCorpseSpawns, [])

    def test_merge_reconstructs_a_spawn_split_across_fragments(self):
        first = self.load([(1000, 8, self.boss), (1150, 10, '{299}')])
        second = self.load([(1151, 12, self.corpse), (1200, 12, self.corpse)])
        self.assertEqual(first.tuliCorpseSpawns, [])
        self.assertEqual(second.tuliCorpseSpawns, [])
        for part in (first, second):
            part.info.battleTime, part.info.sumTime, part.info.server = 0, 0, "测试"
        self.assertEqual(second.merge(first), 0)
        self.assertEqual(second.tuliCorpseSpawns, [(1150, "20", "299")])
        self.assertEqual(second.log, [])

    def test_corpse_after_the_final_hit_confirms_victory_without_extending_combat(self):
        data = self.load([(1000, 8, self.boss), (1100, 9, "{20,true,100,100,0,0}"),
                          (1500, 21, "{10,20,0,1,2477,1,0,0,{[13]=100}}"),
                          (1711, 12, self.corpse), (1711, 10, "{299}")])
        r = SimpleNamespace(bld=data, startTime=1100, finalTime=data.log[-1].time, trimmedFinalTime=0,
                            statDict={"10": {}})
        evidence = LuoyangWinEvidence(r, "突利和顺", ("139306",))
        for event in data.log:
            evidence.observe(event)
        win = evidence.resolve()
        self.assertEqual((win["time"], win["corpseTime"]), (1500, 1711))
        r.trimmedFinalTime = 1500
        self.assertIsNone(evidence.resolve())

    def test_other_encounter_does_not_collect_tuli_events(self):
        data = self.load([(1000, 8, self.boss), (1200, 12, self.corpse), (1200, 10, '{299}')],
                         boss="田承嗣(139329)")
        self.assertEqual(data.tuliCorpseSpawns, [])
        self.assertEqual(data._tuliWorldEvents, [])


if __name__ == "__main__":
    unittest.main()

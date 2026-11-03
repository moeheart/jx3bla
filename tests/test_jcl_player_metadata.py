"""Repeated JCL player records retain talents that arrive after equipment."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

from data.BattleLogData import BattleLogData


ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP = ROOT / ".tmp/weakness-source-audit/test-temp"
JCL_NAME = "2026-11-02-20-16-04-25人普通洛阳之战(835)-阿史那承庆(139323).jcl"
WITH_EQUIPMENT = '{100,"tank",21,10389,18000,{{24,8,17561}}}'
SHUBIAN = '{100,"tank",21,10389,18000,{}, {[5]={1,44566,1}}}'
OTHER_TALENT = '{100,"tank",21,10389,18000,{}, {[5]={3,39045,1}}}'
EMPTY_TALENTS = '{100,"tank",21,10389,18000,{}, {}}'
NO_TALENTS = '{100,"tank",21,10389,18000}'


class JclPlayerMetadataTests(unittest.TestCase):
    def load(self, records):
        # Keep all generated input inside the task's designated temporary root.
        self.assertTrue(TEST_TEMP.resolve().is_relative_to(ROOT))
        TEST_TEMP.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_TEMP) as directory:
            path = Path(directory) / JCL_NAME
            lines = []
            for index, record in enumerate(records):
                kind, payload = record if isinstance(record, tuple) else (4, record)
                lines.append("%d\t%d\t1793664964\t%d\t%d\t%s" %
                             (index, index, 1000 + index, kind, payload))
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            battle = BattleLogData()
            with redirect_stdout(io.StringIO()):
                battle.loadFromJcl(str(path))
        return battle

    def test_talents_arriving_after_equipment_survive_empty_or_missing_snapshots(self):
        for tail in ([], [EMPTY_TALENTS], [NO_TALENTS], [EMPTY_TALENTS, NO_TALENTS]):
            with self.subTest(tail=tail):
                battle = self.load([WITH_EQUIPMENT, SHUBIAN] + tail)
                player = battle.info.player["100"]
                self.assertEqual(player.equip, {"1": {"1": "24", "2": "8", "3": "17561"}})
                self.assertEqual(player.qx, {"5": {"1": "1", "2": "44566", "3": "1"}})
                self.assertEqual(player.xf, "10389")

    def test_later_nonempty_talent_snapshot_replaces_the_previous_snapshot(self):
        battle = self.load([WITH_EQUIPMENT, SHUBIAN, EMPTY_TALENTS, NO_TALENTS,
                            OTHER_TALENT, EMPTY_TALENTS, NO_TALENTS])
        player = battle.info.player["100"]
        self.assertEqual(player.qx, {"5": {"1": "3", "2": "39045", "3": "1"}})
        self.assertEqual(player.equip, {"1": {"1": "24", "2": "8", "3": "17561"}})

    def test_late_talents_preserve_upstream_late_pet_owner_repair(self):
        battle = self.load([
            WITH_EQUIPMENT,
            (21, '{333,444,0,1,2477,1,0,0,{[0]=7898,[13]=7898}}'),
            (8, '{333,"pet",9998,100,0,0,0,0}'),
            SHUBIAN,
            EMPTY_TALENTS,
        ])
        self.assertEqual(battle.log[0].caster, "100")
        self.assertEqual(battle.log[0].damageEff, 7898)
        self.assertEqual(battle.info.player["100"].qx["5"]["2"], "44566")


if __name__ == "__main__":
    unittest.main()

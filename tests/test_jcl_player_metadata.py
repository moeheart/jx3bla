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

    def test_midfight_slots_score_and_gems_survive_late_partial_and_empty_updates(self):
        records = [
            '{100,"tank",21,10389,0,{{24,8,17561}}}',
            '{100,"tank",21,10389,18400,{{0,6,42,6,{[0]={0,15204}},16486,0}}}',
            '{100,"tank",21,10389,0,{{0,6,42},{12,7,7,5,{},16554,16667}}}',
            '{100,"tank",21,10389,0,{}}',
        ]
        player = self.load(records).info.player["100"]
        slots = {row["1"]: row for row in player.equip.values()}
        self.assertEqual(set(slots), {"0", "12", "24"})
        self.assertEqual((player.equipScore, slots["0"]["4"], slots["0"]["6"]), ("18400", "6", "16486"))
        records.append('{100,"tank",21,10389,19000,{{0,6,99,0,{},0,0}}}')
        player = self.load(records).info.player["100"]
        weapon = next(row for row in player.equip.values() if row["1"] == "0")
        self.assertEqual((weapon["3"], weapon["4"], weapon["5"], player.equipScore), ("99", "0", {}, "19000"))

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

    def test_full_combat_set_accepts_late_details_without_adopting_a_swapped_weapon_or_score(self):
        from data.DataContent import NPCdata
        player = NPCdata()
        gear = {str(slot): {"1": str(slot), "2": "6" if slot == 0 else "7", "3": str(400 + slot)}
                for slot in (0, *range(2, 13))}
        player.updateEquipment(0, gear)
        weapon = {**gear["0"], "4": "8", "5": {"0": {"2": "74044"}}, "6": "16236"}
        player.updateEquipment(None, {"1": weapon})
        player.updateEquipment("19000", {})
        swapped = {**weapon, "3": "999", "4": "6"}
        player.updateEquipment(None, {"1": swapped})
        player.updateEquipment("20000", {})
        result = next(row for row in player.equip.values() if row["1"] == "0")
        self.assertEqual(result, weapon)
        self.assertEqual(player.equipScore, 0)
        player.updateEquipment("21954", gear)
        self.assertEqual(player.equipScore, "21954")
        player.updateEquipment("17000", {"1": swapped})
        self.assertEqual(player.equipScore, "21954")

    def test_whetstone_applied_midfight_does_not_override_starting_weapon(self):
        from data.DataContent import NPCdata
        player = NPCdata()
        weapon = {"1": "0", "2": "6", "3": "46557", "4": "6", "5": {}, "6": "0", "7": "0", "8": "0"}
        later = {**weapon, "7": "16475", "8": "1407"}
        player.updateEquipment("18000", {"1": weapon})
        player.updateEquipment("18000", {"1": later})
        self.assertEqual(player.equip["1"]["7"], "0")
        partial = NPCdata()
        partial.updateEquipment("18000", {"1": {k: v for k, v in weapon.items() if k not in ("7", "8")}})
        partial.updateEquipment("18000", {"1": later})
        self.assertEqual(partial.equip["1"]["7"], "16475")

    def test_second_kungfu_requires_its_own_matching_equipment_snapshot(self):
        slots = (0, *range(2, 13))
        def record(xf, equipped, weapon=47527):
            gear = ",".join("{%d,%d,%d,6,{},0,0}" % (slot, 6 if slot == 0 else 7,
                            weapon if slot == 0 else 400 + slot) for slot in equipped)
            return '{100,"同一角色",6,%d,21275,{%s}}' % (xf, gear)
        primary = record(10175, slots)
        for secondary in (record(100654, []), record(100654, [0]), record(100654, slots, 123)):
            with self.subTest(secondary=secondary):
                self.assertFalse(self.load([primary, secondary]).info.player["100"].matchingEquipmentXinfa)
        same = record(100654, slots)
        self.assertEqual(self.load([primary, same]).info.player["100"].matchingEquipmentXinfa, {"100654"})
        changed = record(100654, [0], 123)
        self.assertFalse(self.load([primary, same, changed]).info.player["100"].matchingEquipmentXinfa)


if __name__ == "__main__":
    unittest.main()

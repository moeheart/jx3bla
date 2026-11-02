"""Late JCL NPC snapshots must not drop the first owned summon hit."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from data.BattleLogData import BattleLogData


def row(kind, time, payload):
    return "0\t0\t0\t%d\t%d\t%s\n" % (time, kind, payload)


def player(player_id):
    return row(4, 900, '{%d,"测试者%d",6,10176}' % (player_id, player_id))


def pet(owner, time=1100, template=9998, name="灵蛇"):
    return row(8, time, '{333,"%s",%d,%d,0,0,0,0}' % (name, template, owner))


def damage(time=1000):
    return row(21, time, '{333,444,0,1,2477,1,0,0,{[0]=7898,[13]=7898}}')


class LatePetOwnerTests(unittest.TestCase):
    def load(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"2026-11-02-20-05-46-25人普通洛阳之战(835)-田承嗣(139329).jcl"
            path.write_text("".join(rows), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                result = BattleLogData()
                result.loadFromJcl(str(path))
        return result

    def test_first_hit_before_explicit_owner_snapshot_is_credited(self):
        result = self.load([player(111), damage(), pet(111)])
        self.assertEqual(result.log[0].caster, "111")
        self.assertEqual(result.log[0].damageEff, 7898)
        self.assertEqual(result.info.npc["333"].templateID, "9998")
        self.assertEqual(result.log[0].time, 1000)

    def test_unknown_or_non_player_owner_does_not_rewrite_early_hit(self):
        for owner in (0, 555):
            with self.subTest(owner=owner):
                result = self.load([player(111), damage(), pet(owner)])
                self.assertEqual(result.log[0].caster, "333")

    def test_reused_id_with_different_owners_keeps_early_hit_unassigned(self):
        result = self.load([player(111), player(222), damage(), pet(111), pet(222, 1200), damage(1300)])
        self.assertEqual([event.caster for event in result.log], ["333", "222"])

    def test_reused_id_with_different_templates_keeps_early_hit_unassigned(self):
        result = self.load([player(111), damage(), pet(111), pet(111, 1200, template=9956)])
        self.assertEqual(result.log[0].caster, "333")

    def test_display_name_does_not_establish_retrospective_ownership(self):
        result = self.load([player(111), damage(), pet(0, name="测试者111的灵蛇")])
        self.assertEqual(result.log[0].caster, "333")

    def test_repeated_same_owner_snapshots_and_late_player_metadata(self):
        result = self.load([damage(), pet(111), player(111), pet(111, 1200)])
        self.assertEqual(result.log[0].caster, "111")


if __name__ == "__main__":
    unittest.main()

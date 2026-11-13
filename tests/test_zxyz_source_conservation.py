"""Left-rotation buff attribution before the first logged cast is conserved."""
import math
from types import SimpleNamespace as NS
import unittest

import test_target_boost_sources as fixtures


def buff(caster, time=1000, instance=17):
    return NS(id="20938", level=1, full_id="2,20938,1", caster=caster, target="self",
              time=time, stack=1, isValid=True, delete="false", instanceID=instance,
              frame=0, end=0)


class LeftRotationSourceTests(unittest.TestCase):
    def tracker(self):
        return fixtures.TargetBoostSourceTests().tracker("25人普通洛阳之战")

    def assert_conserved(self, tracker, provider):
        fixture = fixtures.TargetBoostSourceTests()
        hit = fixture.skill(identifier="999", caster="self", time=2000, damage=100000)
        tracker.recordSkill(hit)
        for direct, credited in ((tracker.ndpsCast, tracker.rdpsCast),
                                 (tracker.mndpsCast, tracker.mrdpsCast)):
            self.assertAlmostEqual(math.fsum(skill["sum"] for row in direct.values() for skill in row.skill.values()),
                                   math.fsum(skill["sum"] for row in credited.values() for skill in row.skill.values()), places=7)
        self.assertGreater(sum(skill["sum"] for skill in tracker.rdpsCast[provider].skill.values()), 0)

    def test_buff_before_first_cast_credits_recorded_provider(self):
        tracker = self.tracker()
        self.assertEqual(tracker.zxyzCaster, "0")
        tracker.recordBuff(buff("solar"))
        self.assert_conserved(tracker, "solar")

    def test_another_cast_does_not_steal_explicit_buff_provider(self):
        tracker = self.tracker()
        tracker.recordSkill(fixtures.TargetBoostSourceTests().skill("6251", "monk_a", time=500))
        tracker.recordBuff(buff("solar"))
        self.assert_conserved(tracker, "solar")
        self.assertEqual(tracker.rdpsCast["monk_a"].skill, {})

    def test_missing_provider_uses_only_a_known_cast_fallback(self):
        for known in (False, True):
            with self.subTest(known=known):
                tracker = self.tracker()
                if known:
                    tracker.recordSkill(fixtures.TargetBoostSourceTests().skill("6251", "solar", time=500))
                tracker.recordBuff(buff("unknown"))
                self.assert_conserved(tracker, "solar" if known else "self")
                sources = {row["source"] for row in tracker.boostCounter["self"].boost.values()}
                self.assertEqual(sources, {"solar" if known else "self"})


if __name__ == "__main__":
    unittest.main()

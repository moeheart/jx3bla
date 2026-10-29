"""Formal-server Buff application preserves launch boundaries and damage credit."""
from types import SimpleNamespace
import unittest

from data.DataContent import OverallData, SingleDataBuff
from replayer import Name, NameCangsheng, NameCangshengTest
from replayer.CombatTracker import CombatTracker
from tools.Attribute import COEFF50


LAUNCH = 1793228400  # 2026-10-29 07:00:00 Asia/Shanghai.
PROFILE = {"level": 53, "shieldBase": {school: 6399 for school in
           ("Physics", "Solar", "Neutral", "Lunar", "Poison")}}


class FormalServerBuffTests(unittest.TestCase):
    def tracker(self, timestamp, map_name="25人普通洛阳之战"):
        info = OverallData()
        info.map, info.battleTime, info.skill = map_name, timestamp, {}
        info.player = {key: SimpleNamespace(name=key, occ="4p")
                       for key in ("target", "provider")}
        info.npc = {"boss": SimpleNamespace(name="阿史那承庆", templateID="139323")}
        history = SimpleNamespace(badPeriodDpsLog=[], badPeriodHealerLog=[],
                                  critPeriodHealerLog=[], critPeriodSum=0,
                                  mainTargets=["boss"], startTime=0, finalTime=10000)
        base = {key: {"_raw": {"atPhysicsAttackPowerBase": 1000, "atStrainBase": 1000}}
                for key in info.player}
        tracker = CombatTracker(info, history, {key: "4p" for key in info.player}, {}, {},
                                {key: {"id": "0", "stack": 0} for key in ("zxyz", "qs", "zzm")},
                                base)
        for counter in tracker.boostCounter.values():
            counter.boost.clear()
            counter.targetBoost = {"all": {}}
            counter.targetProfiles = {"boss": PROFILE}
        return tracker

    def buff(self, stack=80, time=1000):
        event = SingleDataBuff()
        event.setByJcl(["0", "0", "0", str(time), "13", {
            "1": "target", "2": "false", "3": "17", "4": "true",
            "5": "20854", "6": str(stack), "7": "0", "9": "1",
            "10": "provider", "11": "true"}])
        return event

    def damage(self, time=2000):
        return SimpleNamespace(id="999999", level=1, scheme=1, full_id="1,999999,1",
                               caster="target", target="boss", time=time, damage=10000,
                               damageEff=10000, heal=0, healEff=0, effect=0,
                               fullResult={"0": "10000"})

    def test_all_difficulties_select_tables_at_launch(self):
        for difficulty in ("10人普通", "25人普通", "25人英雄"):
            for timestamp, edition, table in (
                    (LAUNCH - 1, 160, NameCangshengTest),
                    (LAUNCH, 161, NameCangsheng),
                    (LAUNCH + 1, 161, NameCangsheng)):
                with self.subTest(difficulty=difficulty, timestamp=timestamp):
                    tracker = self.tracker(timestamp, difficulty + "洛阳之战")
                    self.assertEqual(tracker.gameEdition, edition)
                    self.assertIs(tracker.boostDict, table.BOOST_DICT)
                    self.assertIs(tracker.absorbDict, table.ABSORB_DICT)
                    self.assertIs(tracker.resistDict, table.RESIST_BY_SCHOOL_DICT)
                    self.assertIs(tracker.therapyDict, table.THERAPY_DICT)
        legacy = self.tracker(LAUNCH, "25人普通阆风悬城")
        self.assertIs(legacy.boostDict, Name.BOOST_DICT)

    def test_logged_piaohuang_stack_changes_credit_and_preserves_total_damage(self):
        credited = {}
        # Interleave instances so a formal replay cannot mutate a historical replay.
        trackers = [(160, 8, self.tracker(LAUNCH - 1)),
                    (161, 10, self.tracker(LAUNCH))]
        for edition, per_stack, tracker in trackers:
            tracker.recordBuff(self.buff())
            active = tracker.boostCounter["target"].boost
            instance = ("2,20854,1", "slot", "17")
            self.assertEqual(active[instance]["effect"], {"atStrainBase": 80 * per_stack})
            self.assertEqual(active[instance]["source"], "provider")
            tracker.recordSkill(self.damage())
            provider = tracker.rdpsCast["provider"].skill["6,2,20854,1"]["sum"]
            own = tracker.rdpsCast["target"].skill["1,999999,1"]["sum"]
            expected = 10000 * (80 * per_stack) / (COEFF50["无双"] + 1000 + 80 * per_stack)
            self.assertAlmostEqual(provider, expected)
            self.assertAlmostEqual(provider + own, 10000)
            self.assertAlmostEqual(tracker.mrdpsCast["provider"].skill["6,2,20854,1"]["sum"], provider)
            tracker.recordBuff(self.buff(stack=0, time=3000))
            self.assertNotIn(instance, active)
            tracker.recordSkill(self.damage(time=4000))
            self.assertAlmostEqual(tracker.rdpsCast["provider"].skill["6,2,20854,1"]["sum"], provider)
            self.assertAlmostEqual(tracker.rdpsCast["target"].skill["1,999999,1"]["sum"], own + 10000)
            credited[edition] = provider
        self.assertGreater(credited[161], credited[160])
        self.assertEqual(NameCangshengTest.BOOST_DICT["2,20854,1"], {"atStrainBase": 8})
        self.assertEqual(NameCangsheng.BOOST_DICT["2,20854,1"], {"atStrainBase": 10})

    def test_other_healer_strain_buffs_keep_their_own_values(self):
        for identifier in (29294, 20938, 23543):
            self.assertEqual(NameCangsheng.BOOST_DICT["2,%d,1" % identifier], {"atStrainBase": 7})
        self.assertEqual(NameCangsheng.BOOST_DICT["2,24742,1"], {"atStrainBase": 26})
        self.assertEqual(NameCangshengTest.BOOST_DICT["2,24742,1"], {"atStrainBase": 28})

    def test_names_follow_log_version_but_explicit_log_names_take_priority(self):
        old = self.tracker(LAUNCH - 1).info
        current = self.tracker(LAUNCH).info
        key = "2,30605,1"
        self.assertEqual(old.getSkillName(key), "测试服阆风悬城竞速")
        self.assertEqual(current.getSkillName(key), "测试服洛阳之战竞速")
        for info in (old, current):
            info.skill[key] = {"1": "日志记录的名称"}
            self.assertEqual(info.getSkillName(key), "日志记录的名称")


if __name__ == "__main__":
    unittest.main()

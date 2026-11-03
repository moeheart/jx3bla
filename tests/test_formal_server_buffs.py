"""Formal-server Buff application preserves damage credit without date routing."""
from types import SimpleNamespace
import unittest

from data.DataContent import OverallData, SingleDataBuff
from replayer import Name
from replayer.CombatTracker import CombatTracker
from tools.Attribute import COEFF50, CURRENT_GAME_EDITION


TIMESTAMPS = (0, 1793228400)
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

    def test_all_difficulties_use_formal_tables_without_date_routing(self):
        for difficulty in ("10人普通", "25人普通", "25人英雄"):
            for timestamp in TIMESTAMPS:
                with self.subTest(difficulty=difficulty, timestamp=timestamp):
                    tracker = self.tracker(timestamp, difficulty + "洛阳之战")
                    self.assertEqual(tracker.rdpsStatus['gameEdition'], CURRENT_GAME_EDITION)
                    self.assertTrue(all(counter.gameEdition == CURRENT_GAME_EDITION
                                        for counter in tracker.boostCounter.values()))
                    self.assertIs(tracker.boostDict, Name.BOOST_DICT)
                    self.assertIs(tracker.absorbDict, Name.ABSORB_DICT)
                    self.assertIs(tracker.resistDict, Name.RESIST_BY_SCHOOL_DICT)
                    self.assertIs(tracker.therapyDict, Name.THERAPY_DICT)

    def test_logged_piaohuang_stack_changes_credit_and_preserves_total_damage(self):
        credited = []
        # Interleave independent instances to detect mutation of shared tables.
        trackers = [self.tracker(timestamp) for timestamp in TIMESTAMPS]
        per_stack = 10
        for tracker in trackers:
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
            credited.append(provider)
        self.assertEqual(credited[0], credited[1])
        self.assertEqual(Name.BOOST_DICT["2,20854,1"], {"atStrainBase": 10})

    def test_other_healer_strain_buffs_keep_their_own_values(self):
        for identifier in (29294, 20938, 23543):
            self.assertEqual(Name.BOOST_DICT["2,%d,1" % identifier], {"atStrainBase": 7})
        self.assertEqual(Name.BOOST_DICT["2,24742,1"], {"atStrainBase": 26})

    def test_formal_names_preserve_explicit_log_name_priority(self):
        key = "2,30605,1"
        for timestamp in TIMESTAMPS:
            info = self.tracker(timestamp).info
            self.assertEqual(info.getSkillName(key), "测试服洛阳之战竞速")
            info.skill[key] = {"1": "日志记录的名称"}
            self.assertEqual(info.getSkillName(key), "日志记录的名称")


if __name__ == "__main__":
    unittest.main()

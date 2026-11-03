"""NPC source isolation, inferred refresh/expiry, and damage conservation.

Formal 10009 buff.tab has Exclude=0 and MaxStackNum=1 for 8248/1-2 and 566/6;
its intervals are 400 and 320 frames. The 2026-11-02 JCL samples contain the
triggering skills and selected talents, but no 8248/566 NPC Buff updates and
only one source of each. Multi-source fixtures below test the inferred model,
not an in-game confirmation that multiple copies coexist.
"""
from types import SimpleNamespace
import unittest

from data.DataContent import OverallData
from replayer.CombatTracker import CombatTracker


MAPS = ("25人普通洛阳之战",)
PROFILE = {"level": 53, "shieldBase": {school: 6399 for school in
           ("Physics", "Solar", "Neutral", "Lunar", "Poison")}}


class TargetBoostSourceTests(unittest.TestCase):
    def tracker(self, map_name):
        occupations = {"self": "3d", "solar": "1d", "fs": "21d", "fs2": "21d", "fs3": "21d",
                       "tg": "21t", "monk_a": "1d", "monk_b": "1d",
                       "ax": "3d", "tc": "3t", "tc2": "3t"}
        info = OverallData()
        info.map, info.battleTime, info.skill = map_name, 1793577600, {}
        info.player = {source: SimpleNamespace(name=source, occ=occ)
                       for source, occ in occupations.items()}
        # JCL PLAYER_INFO stores selected talents as slot -> (choice, ID, level).
        # Synthetic fixtures include both the base and enhanced talent choice.
        for source in ("fs", "fs2", "fs3", "tg"):
            talent = "44566" if source == "tg" else "21281"
            info.player[source].qx = {"5": {"1": "1", "2": talent, "3": "1"}}
        info.npc = {target: SimpleNamespace(name="阿史那承庆", templateID="139323")
                    for target in ("boss", "other")}
        history = SimpleNamespace(badPeriodDpsLog=[], badPeriodHealerLog=[],
                                  critPeriodHealerLog=[], critPeriodSum=0,
                                  mainTargets=["boss"], startTime=0, finalTime=9000000)
        # Current calculation requires raw client attributes.
        base = {source: {"_raw": {"atPhysicsAttackPowerBase": 1000,
                                  "atSolarAttackPowerBase": 1000}}
                for source in occupations}
        tracker = CombatTracker(info, history, occupations, {}, {},
                                {key: {"id": "0", "stack": 0}
                                 for key in ("zxyz", "qs", "zzm")}, base)
        for counter in tracker.boostCounter.values():
            # Isolate the effect under test from the inferred team buff.
            counter.boost.clear()
            counter.targetProfiles = {target: PROFILE for target in info.npc}
        return tracker

    def skill(self, identifier="13050", caster="fs", time=1000,
              target="boss", damage=0, school="0"):
        return SimpleNamespace(id=identifier, level=15, scheme=1,
                               full_id="1,%s,15" % identifier, caster=caster,
                               target=target, time=time, damage=damage,
                               damageEff=damage, heal=0, healEff=0, effect=0,
                               fullResult={school: str(damage)} if damage else {})

    def sources(self, tracker, player="self", target="boss"):
        return {record["source"]: record for record in
                tracker.boostCounter[player].targetBoost.get(target, {}).values()}

    def test_two_source_window_keeps_independent_refresh_and_expiry(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.info.player["tg"].qx["5"] = {"1": "3", "2": "39045", "3": "1"}
                tracker.recordSkill(self.skill(caster="fs", time=1000))
                tracker.recordSkill(self.skill(caster="tg", time=6000))
                records = self.sources(tracker)
                self.assertEqual(set(records), {"fs", "tg"})
                self.assertEqual(records["fs"]["id"], "2,8248,1")
                self.assertEqual(records["tg"]["id"], "2,8248,1")
                tracker.recordSkill(self.skill(caster="fs", time=10000))
                self.assertEqual(len(self.sources(tracker)), 2)
                self.assertEqual(tracker.boostRemove[("boss", ("8248", "source", "fs"))]["time"], 35000)
                self.assertEqual(tracker.boostRemove[("boss", ("8248", "source", "tg"))]["time"], 31000)
                tracker.checkRemoveBuff(26000)  # Superseded first fs expiry.
                self.assertEqual(set(self.sources(tracker)), {"fs", "tg"})
                tracker.checkRemoveBuff(30999)
                self.assertEqual(set(self.sources(tracker)), {"fs", "tg"})
                tracker.checkRemoveBuff(31000)
                self.assertEqual(set(self.sources(tracker)), {"fs"})
                tracker.checkRemoveBuff(35000)
                self.assertEqual(self.sources(tracker), {})

    def test_four_source_window_preserves_all_sources_without_extra_stacks(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                for source, time in (("fs", 1000), ("fs2", 2250),
                                     ("fs3", 2350), ("tg", 8750)):
                    tracker.recordSkill(self.skill(caster=source, time=time))
                tracker.recordSkill(self.skill(caster="fs", time=12000))
                records = self.sources(tracker)
                self.assertEqual(set(records), {"fs", "fs2", "fs3", "tg"})
                for source, record in records.items():
                    self.assertEqual(record["stack"], 1)
                    self.assertEqual(record["effect"], tracker.boostDict[record["id"]])
                self.assertEqual(len(tracker.boostRemove), 4)

    def test_same_caster_different_targets_have_separate_lifetimes(self):
        for map_name in MAPS:
            for identifier, duration in (("13050", 25000), ("203", 20000)):
                with self.subTest(map=map_name, skill=identifier):
                    tracker = self.tracker(map_name)
                    caster = "fs" if identifier == "13050" else "monk_a"
                    tracker.recordSkill(self.skill(identifier, caster, 1000))
                    tracker.recordSkill(self.skill(identifier, caster, 2000, target="other"))
                    tracker.recordSkill(self.skill(identifier, caster, 3000))
                    tracker.checkRemoveBuff(2000 + duration)
                    self.assertIn(caster, self.sources(tracker, target="boss"))
                    self.assertEqual(self.sources(tracker, target="other"), {})
                    tracker.checkRemoveBuff(3000 + duration)
                    self.assertEqual(self.sources(tracker), {})

    def test_caster_level_change_replaces_only_its_own_copy(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.recordSkill(self.skill(caster="fs", time=1000))
                tracker.recordSkill(self.skill(caster="tg", time=2000))
                tracker.recordSkill(self.skill(caster="tg", time=2500, target="other"))
                tracker.buffAppearCounter["tg"]["9889"] = 1
                tracker.info.player["tg"].qx["5"]["2"] = "39045"
                tracker.recordSkill(self.skill(caster="tg", time=3000))
                records = self.sources(tracker)
                self.assertEqual(set(records), {"fs", "tg"})
                self.assertEqual(records["tg"]["id"], "2,8248,1")
                self.assertEqual(self.sources(tracker, target="other")["tg"]["id"], "2,8248,2")
                tracker.buffAppearCounter["tg"]["9889"] = 0
                tracker.info.player["tg"].qx["5"]["2"] = "44566"
                tracker.recordSkill(self.skill(caster="tg", time=4000))
                self.assertEqual(self.sources(tracker)["tg"]["id"], "2,8248,2")
                self.assertEqual(self.sources(tracker)["fs"]["id"], "2,8248,1")
                self.assertEqual(len(tracker.boostRemove), 3)
                tracker.checkRemoveBuff(26000)
                self.assertEqual(set(self.sources(tracker)), {"tg"})

    def test_current_weakness_strength_uses_selected_shubian_talent(self):
        tracker = self.tracker(MAPS[0])
        # Specialization alone does not establish the enhanced talent choice.
        tracker.info.player["tg"].qx["5"] = {"1": "3", "2": "39045", "3": "1"}
        tracker.recordSkill(self.skill(caster="tg", time=1000))
        self.assertEqual(self.sources(tracker)["tg"]["id"], "2,8248,1")
        # Archived 13540 Lua checks learned 44566 independently of the 9889 buff.
        tracker.info.player["tg"].qx["5"] = {"1": "1", "2": "44566", "3": "1"}
        tracker.buffAppearCounter["tg"]["9889"] = 1
        tracker.recordSkill(self.skill(caster="tg", time=2000))
        self.assertEqual(self.sources(tracker)["tg"]["id"], "2,8248,2")
        self.assertEqual(len(self.sources(tracker)), 1)
        tracker.info.player["tg"].qx["5"]["3"] = "2"
        tracker.recordSkill(self.skill(caster="tg", time=3000))
        self.assertEqual(self.sources(tracker)["tg"]["id"], "2,8248,1")
        del tracker.info.player["tg"].qx
        tracker.recordSkill(self.skill(caster="tg", time=4000))
        self.assertEqual(self.sources(tracker)["tg"]["id"], "2,8248,1")

    def test_lidi_all_trigger_skills_refresh_only_their_caster(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.recordSkill(self.skill("201", "monk_a", 1000))
                tracker.recordSkill(self.skill("202", "monk_b", 2000))
                tracker.recordSkill(self.skill("203", "monk_a", 3000))
                records = self.sources(tracker)
                self.assertEqual(set(records), {"monk_a", "monk_b"})
                self.assertTrue(all(record["id"] == "2,566,6" and record["stack"] == 1
                                    for record in records.values()))
                tracker.checkRemoveBuff(21000)
                self.assertEqual(set(self.sources(tracker)), {"monk_a", "monk_b"})
                tracker.checkRemoveBuff(22000)
                self.assertEqual(set(self.sources(tracker)), {"monk_a"})
                tracker.checkRemoveBuff(23000)
                self.assertEqual(self.sources(tracker), {})

    def test_formal_log_refresh_gap_invalidates_cached_credit_and_conserves_damage(self):
        # First three 13050 events in the 2026-11-02 Ashina JCL, shifted by
        # 30342559 ms. Its caster selects 44566/1. Damage probes are synthetic.
        tracker = self.tracker(MAPS[0])
        counter = tracker.boostCounter["self"]
        tracker.recordSkill(self.skill(caster="tg", time=1000))
        first = self.skill("999", "self", 2000, damage=100000)
        tracker.recordSkill(first)
        initial_credit = tracker.rdpsCast["tg"].skill["6,2,8248,2"]["sum"]
        self.assertGreater(initial_credit, 0)

        # The first copy expires before the next observed cast. Reusing the
        # same attacker/target/school must discard the cached enhanced rate.
        gap = self.skill("999", "self", 26000, damage=100000)
        tracker.recordSkill(gap)
        self.assertEqual(tracker.rdpsCast["tg"].skill["6,2,8248,2"]["sum"], initial_credit)
        self.assertEqual(counter.getRateForEvent(gap, "damage"),
                         {"self": {"source": "self", "id": "self", "rate": 1.0}})
        tracker.recordSkill(self.skill(caster="tg", time=27207))
        tracker.recordSkill(self.skill("999", "self", 28000, damage=100000))
        tracker.recordSkill(self.skill(caster="tg", time=38745))
        tracker.checkRemoveBuff(52207)  # Superseded second-cast expiry.
        self.assertIn("tg", self.sources(tracker))
        tracker.checkRemoveBuff(63745)
        self.assertEqual(self.sources(tracker), {})
        self.assertEqual(counter.boostCover["2,8248,2"].buffTimeIntegral(), 61538)

        credited = sum(skill["sum"] for recorder in tracker.rdpsCast.values()
                       for skill in recorder.skill.values())
        main_credited = sum(skill["sum"] for recorder in tracker.mrdpsCast.values()
                            for skill in recorder.skill.values())
        self.assertAlmostEqual(credited, 300000)
        self.assertAlmostEqual(main_credited, 300000)

    def test_canonical_coverage_remains_until_last_source_or_target_expires(self):
        for map_name in MAPS:
            for identifier, caster, second, canonical, duration in (
                    ("13050", "fs", "fs2", "2,8248,1", 25000),
                    ("203", "monk_a", "monk_b", "2,566,6", 20000)):
                with self.subTest(map=map_name, skill=identifier):
                    tracker = self.tracker(map_name)
                    tracker.recordSkill(self.skill(identifier, caster, 1000))
                    tracker.recordSkill(self.skill(identifier, second, 2000))
                    tracker.recordSkill(self.skill(identifier, caster, 3000, target="other"))
                    cover = tracker.boostCounter["self"].boostCover[canonical]
                    tracker.checkRemoveBuff(1000 + duration)
                    self.assertEqual(cover.checkState(1000 + duration), 1)
                    tracker.checkRemoveBuff(2000 + duration)
                    self.assertEqual(self.sources(tracker), {})
                    self.assertEqual(cover.checkState(2000 + duration), 1)
                    tracker.checkRemoveBuff(3000 + duration)
                    self.assertEqual(cover.checkState(3000 + duration), 0)
                    self.assertEqual(cover.buffTimeIntegral(), duration + 2000)

    def test_rdps_credits_each_source_under_canonical_id_and_name(self):
        for map_name in MAPS:
            for identifier, first, second, attacker, school, expected_name in (
                    ("13050", "fs", "tg", "self", "0", "虚弱"),
                    ("203", "monk_a", "monk_b", "solar", "1", "立地成佛")):
                with self.subTest(map=map_name, skill=identifier):
                    tracker = self.tracker(map_name)
                    tracker.recordSkill(self.skill(identifier, first, 1000))
                    tracker.recordSkill(self.skill(identifier, second, 2000))
                    damage = self.skill("999", attacker, 3000, damage=100000, school=school)
                    counter = tracker.boostCounter[attacker]
                    rates = counter.getRateForEvent(damage, "damage")
                    external = {value["source"]: value for key, value in rates.items() if key != "self"}
                    expected_sources = {first, second} - {attacker}
                    self.assertEqual(set(external), expected_sources)
                    self.assertTrue(all(value["rate"] > 0 for value in external.values()))
                    self.assertAlmostEqual(sum(value["rate"] for value in rates.values()), 1)
                    tracker.recordSkill(damage)
                    credited = 0
                    for source, value in external.items():
                        canonical = "6," + value["id"]
                        record = tracker.rdpsCast[source]
                        self.assertIn(canonical, record.skill)
                        self.assertGreater(record.skill[canonical]["sum"], 0)
                        self.assertEqual(record.getSkillName(canonical, tracker.info), expected_name + "(增益)")
                        credited += record.skill[canonical]["sum"]
                    credited += tracker.rdpsCast[attacker].skill[damage.full_id]["sum"]
                    self.assertAlmostEqual(credited, damage.damageEff)
                    self.assertTrue(all(isinstance(key, str) for recorder in tracker.rdpsCast.values()
                                        for key in recorder.skill))
                    self.assertEqual(tracker.rdpsCast["*低等级增益"].skill, {})

    def test_late_expiry_scan_preserves_order_and_coverage_integral(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.recordSkill(self.skill(caster="fs", time=0))
                tracker.recordSkill(self.skill(caster="fs2", time=1000))
                tracker.recordSkill(self.skill(caster="fs", time=5000))
                tracker.checkRemoveBuff(31000)
                cover = tracker.boostCounter["self"].boostCover["2,8248,1"]
                self.assertEqual(self.sources(tracker), {})
                self.assertEqual([row[0] for row in cover.log], sorted(row[0] for row in cover.log))
                self.assertEqual(cover.checkState(29999), 1)
                self.assertEqual(cover.checkState(30000), 0)
                self.assertEqual(cover.buffTimeIntegral(), 30000)

    def test_own_weakness_stays_in_self_damage_and_external_source_keeps_credit(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.recordSkill(self.skill(caster="fs", time=1000))
                tracker.recordSkill(self.skill(caster="tg", time=2000))
                damage = self.skill("999", "fs", 3000, damage=100000)
                rates = tracker.boostCounter["fs"].getRateForEvent(damage, "damage")
                self.assertNotIn(("8248", "source", "fs"), rates)
                self.assertEqual(rates[("8248", "source", "tg")]["source"], "tg")
                tracker.recordSkill(damage)
                self.assertNotIn("6,2,8248,1", tracker.rdpsCast["fs"].skill)
                self.assertGreater(tracker.rdpsCast["tg"].skill["6,2,8248,2"]["sum"], 0)
                self.assertEqual(tracker.rdpsCast["*低等级增益"].skill, {})

    def test_pofeng_keeps_high_level_priority_and_same_level_overwrite(self):
        for map_name in MAPS:
            with self.subTest(map=map_name):
                tracker = self.tracker(map_name)
                tracker.recordSkill(self.skill("403", "ax", 1000))
                records = tracker.boostCounter["self"].targetBoost["boss"]
                self.assertEqual(set(records), {"2,661,30"})
                self.assertEqual(records["2,661,30"]["source"], "*低等级增益")
                tracker.recordSkill(self.skill("403", "tc", 2000))
                records = tracker.boostCounter["self"].targetBoost["boss"]
                self.assertEqual(set(records), {"2,12717,30"})
                self.assertEqual(records["2,12717,30"]["source"], "tc")
                tracker.recordSkill(self.skill("403", "ax", 3000))
                self.assertEqual(set(records), {"2,12717,30"})
                tracker.recordSkill(self.skill("403", "tc2", 4000))
                self.assertEqual(set(records), {"2,12717,30"})
                self.assertEqual(records["2,12717,30"]["source"], "tc2")
                tracker.checkRemoveBuff(16000)  # Old high-level expiry is superseded.
                self.assertEqual(set(records), {"2,12717,30"})
                tracker.checkRemoveBuff(18000)
                self.assertEqual(self.sources(tracker), {})
                tracker.recordSkill(self.skill("403", "ax", 19000))
                self.assertEqual(set(tracker.boostCounter["self"].targetBoost["boss"]), {"2,661,30"})


if __name__ == "__main__":
    unittest.main()

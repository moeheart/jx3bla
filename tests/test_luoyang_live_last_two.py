"""Live Luoyang evidence: source identity, measured phases, and non-kill exits."""
import unittest
from tools.ValidateLuoyangLastTwo import replayer, event, damage
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi


class LiveLastTwoTests(unittest.TestCase):
    def test_live_xuansun_name_and_template_are_counted(self):
        r = replayer(Ashina, [("boss", "139323", Ashina.BOSS), ("bird", "139349", "玄隼")])
        r.analyseSecondStage(event("Scene", 2000, id="bird", enter=1))
        r.analyseSecondStage(damage(3000, target="bird"))
        r.analyseSecondStage(event("Death", 5000, id="bird"))
        r.countFinal()
        self.assertEqual(r.statDict["p"]["battle"]["constructDamage"], 100)
        self.assertEqual(r.detail["constructPeriods"][0]["duration"], 3)
        self.assertEqual(r.win, 0)

    def test_soul_cast_and_following_shout_are_one_cycle(self):
        r = replayer(Ashina)
        r.analyseSecondStage(event("Cast", 2000, id="45916"))
        r.analyseSecondStage(event("Shout", 2048, id="boss", content='"聚邪成渊，尔命休矣！"'))
        r.analyseSecondStage(event("Buff", 4000, id="34251", stack=1))
        r.analyseSecondStage(event("Buff", 9042, id="34251", stack=0))
        r.countFinal()
        self.assertEqual(len(r.detail["soulPeriods"]), 1)
        self.assertEqual(r.detail["soulPeriods"][0]["start"], 2000)
        self.assertEqual(r.detail["soulPeriods"][0]["duration"], 7.042)
        self.assertEqual(r.detail["phaseTimes"]["聚邪"], 7.04)
        periods = [e for e in r.bh.log["environment"] if e["type"] == "phase" and e["start"] == 2000]
        self.assertEqual(periods[0]["duration"], 7042)

    def test_soul_shout_can_replace_missing_cast_but_not_player_message(self):
        r = replayer(Ashina)
        r.analyseSecondStage(event("Shout", 2000, id="p", content="聚邪成渊，尔命休矣！"))
        self.assertEqual(r.phase, 1)
        r.analyseSecondStage(event("Shout", 3000, id="boss", content='"聚邪成渊，尔命休矣！"'))
        self.assertEqual(r.phase, 2)
        r.countFinal()
        self.assertEqual(len(r.detail["shouts"]), 1)

    def test_shi_uses_owned_shout_before_first_second_phase_skill(self):
        r = replayer(Shi)
        r.analyseSecondStage(event("Shout", 6000, id="boss", content='"'+Shi.TRANSITION_START+'"'))
        r.analyseSecondStage(event("Shout", 13997, id="boss", content='"'+Shi.TRANSITION_END+'"'))
        r.analyseSecondStage(event("Cast", 16000, id="45711"))
        r.countFinal()
        self.assertEqual(r.detail["P1Time"], 5)
        self.assertEqual(r.detail["P2Time"], 15)
        self.assertEqual(r.detail["P3Time"], 0)
        self.assertEqual(r.detail["phaseChanges"][0]["time"], 6000)
        self.assertEqual(r.detail["transitionPeriods"][0]["duration"], 7.997)
        self.assertFalse(r.detail["transitionPeriods"][0]["truncated"])
        bars = [e for e in r.bh.log["environment"] if e["type"] == "transition"]
        self.assertEqual(bars[0]["duration"], 7997)
        self.assertEqual(r.bh.sumTime("dps"), 20000)

    def test_same_named_shi_clone_cannot_switch_phase(self):
        r = replayer(Shi, [("boss", "139312", Shi.BOSS), ("clone", "139346", Shi.BOSS)])
        r.analyseSecondStage(event("Shout", 6000, id="clone", content=Shi.TRANSITION_START))
        self.assertEqual(r.phase, 1)
        self.assertNotIn("shouts", r.detail)

    def test_shi_first_skill_remains_a_fallback(self):
        r = replayer(Shi)
        r.analyseSecondStage(event("Cast", 6000, id="45711"))
        r.countFinal()
        self.assertEqual(r.detail["P1Time"], 5)
        self.assertEqual(r.detail["transitionPeriods"], [])

    def test_boss_combat_exit_trims_without_confirming_kill(self):
        for cls in (Ashina, Shi):
            with self.subTest(cls=cls):
                r = replayer(cls)
                r.analyseSecondStage(damage(5000))
                r.analyseSecondStage(event("Battle", 5500, id="boss", fight=0))
                r.trimTime(); r.getResult()
                self.assertEqual(r.win, 0)
                self.assertEqual(r.finalTime, 5500)
                self.assertEqual(r.statDict["p"]["battle"]["mainDamage"], 100)
                self.assertEqual(r.detail["endEvidence"][0]["template"], cls.MAIN_IDS[0])

    def test_temporary_combat_exit_is_cancelled_by_damage_or_reentry(self):
        for later in (damage(6000), event("Battle", 6000, id="boss", fight=1)):
            r = replayer(Shi)
            r.analyseSecondStage(damage(5000))
            r.analyseSecondStage(event("Battle", 5500, id="boss", fight=0))
            r.analyseSecondStage(later)
            r.trimTime(); r.getResult()
            self.assertEqual(r.finalTime, 21000)
            self.assertEqual(r.detail["endEvidence"], [])

    def test_combat_exit_preserves_earlier_failure_cutoff(self):
        r = replayer(Shi)
        r.trimmedFinalTime = 5300
        r.analyseSecondStage(damage(5000))
        r.analyseSecondStage(event("Battle", 5500, id="boss", fight=0))
        r.trimTime(); r.getResult()
        self.assertEqual(r.finalTime, 5300)
        self.assertEqual(r.detail["endEvidence"], [])

    def test_combat_exit_rejects_clone_or_stale_combat(self):
        for sender, time in (("clone", 5500), ("boss", 12000)):
            r = replayer(Shi, [("boss", "139312", Shi.BOSS), ("clone", "139346", Shi.BOSS)])
            r.analyseSecondStage(damage(5000))
            r.analyseSecondStage(event("Battle", time, id=sender, fight=0))
            r.countFinal()
            self.assertEqual(r.finalTime, 21000)
            self.assertEqual(r.win, 0)

    def test_praise_after_combat_exit_is_not_kill_evidence(self):
        r = replayer(Shi)
        r.analyseSecondStage(damage(5000))
        r.analyseSecondStage(event("Battle", 5500, id="boss", fight=0))
        r.analyseSecondStage(event("Shout", 6900, id="0", content='"恭喜大侠，获得 [赞·群龙之首]。"'))
        r.analyseSecondStage(event("Scene", 7000, id="boss", enter=0))
        r.countFinal()
        self.assertEqual((r.win, r.finalTime), (0, 5500))

    def test_unfinished_transition_closes_at_combat_exit(self):
        r = replayer(Shi)
        r.analyseSecondStage(event("Shout", 3000, id="boss", content=Shi.TRANSITION_START))
        r.analyseSecondStage(damage(5000))
        r.analyseSecondStage(event("Battle", 5500, id="boss", fight=0))
        r.countFinal()
        self.assertEqual(r.detail["transitionPeriods"][0]["end"], 5500)
        self.assertTrue(r.detail["transitionPeriods"][0]["truncated"])
        self.assertEqual(r.detail["P1Time"]+r.detail["P2Time"], 4.5)


if __name__ == "__main__":
    unittest.main()

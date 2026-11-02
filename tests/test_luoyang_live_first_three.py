"""Formal-server dialogue and observed phase-edge regressions."""
import unittest
from types import SimpleNamespace as NS

from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer


def encounter(cls, templates):
    players = {key: NS(name=key) for key in ("p", "q")}
    info = NS(player=players, npc={key: NS(name=name, templateID=template)
                                  for key, (template, name) in templates.items()})
    info.getName = lambda key: (info.player.get(key) or info.npc.get(key)).name
    replay = cls(NS(info=info), {key: "1d" for key in players}, 1000, 31000, 30000,
                 cls.__name__, NS(item={"actor": {"filter": ""}}))
    replay.recordEquipment({})
    replay.initBattle()
    return replay


def event(kind, time, **fields):
    defaults = dict(id="", caster="", target="", damage=0, damageEff=0, stack=0,
                    enter=0, content="", full_id="", fight=0, hp=0, hpMax=100)
    defaults.update(fields)
    return NS(dataType=kind, time=time, **defaults)


class FormalFirstThreeTests(unittest.TestCase):
    def test_tuli_field_ends_on_last_observed_remove_without_33755(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺")})
        r.analyseSecondStage(event("Cast", 2000, caster="boss", id="45489"))
        for target in ("p", "q"):
            r.analyseSecondStage(event("Buff", 2100, caster="boss", target=target, id="34490", stack=1))
        r.analyseSecondStage(event("Buff", 6000, caster="boss", target="p", id="34490"))
        self.assertEqual(r.phase, 2)
        r.analyseSecondStage(event("Buff", 6200, caster="boss", target="q", id="34490"))
        self.assertEqual(r.phase, 1)
        r.trimTime()
        r.getResult()
        self.assertEqual(r.detail["phaseTimes"]["死水微澜"], 4.2)
        self.assertEqual(r.detail["effectiveTime"], 30000)

    def test_tuli_owned_shouts_and_casts_describe_mechanic_cycles(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺"),
                                           "clone": ("139352", "突利和顺")})
        line = "玄溟作薪，烈焰为牢，此地即为尔等葬身之所！"
        r.analyseSecondStage(event("Shout", 2000, id="clone", content=line))
        self.assertEqual(r.phase, 1)
        self.assertFalse(r.detail.get("shouts"))
        r.analyseSecondStage(event("Shout", 3000, id="boss", content=line))
        self.assertEqual(r.phase, 4)
        r.analyseSecondStage(event("Shout", 5000, id="boss", content="仪式已成，尔等，皆为祭品！"))
        self.assertEqual(r.phase, 3)
        r.analyseSecondStage(event("Cast", 9000, caster="boss", id="45485"))
        self.assertEqual(r.phase, 1)
        self.assertEqual(len(r.detail["shouts"]), 2)

    def test_tian_sword_preparation_is_not_sword_lifetime(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣"),
                                            "sword": ("140384", "天陨巨剑")})
        r.analyseSecondStage(event("Shout", 2000, id="boss", content="抬头看好了——这一剑，送你们上路！"))
        self.assertEqual(r.phase, 5)
        r.analyseSecondStage(event("Scene", 5000, id="sword", enter=1))
        r.analyseSecondStage(event("Death", 8000, id="sword"))
        r.analyseSecondStage(event("Shout", 9000, id="boss", content="小看你们了，狼牙军，全军准备！"))
        r.trimTime()
        r.getResult()
        self.assertEqual(r.detail["phaseTimes"]["天陨一剑准备"], 3)
        self.assertEqual(r.detail["swords"][0]["duration"], 3)
        self.assertEqual(r.detail["phaseTimes"]["巨剑击破后"], 1)
        self.assertEqual(r.win, 0)

    def test_tian_recent_damage_and_disengage_trim_without_inventing_win(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
        r.analyseSecondStage(event("Skill", 19000, caster="p", target="boss", damageEff=100))
        # No low-health assumption: the event is only an encounter-end boundary.
        r.analyseSecondStage(event("Battle", 20000, id="boss", fight=0, hp=99))
        r.trimTime()
        r.getResult()
        self.assertEqual(r.finalTime, 20000)
        self.assertEqual(r.win, 0)
        self.assertIn("combatEndEvidence", r.detail)

    def test_tian_end_candidate_preserves_an_earlier_actor_cutoff(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
        r.analyseSecondStage(event("Skill", 19000, caster="p", target="boss", damageEff=100))
        r.analyseSecondStage(event("Battle", 20000, id="boss", fight=0))
        r.trimmedFinalTime = 15000
        r.trimTime()
        self.assertEqual(r.finalTime, 15000)

    def test_tian_sword_lifetimes_respect_the_final_cutoff(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣"),
                                            "sword": ("140384", "天陨巨剑"),
                                            "late": ("140384", "天陨巨剑")})
        r.analyseSecondStage(event("Scene", 15000, id="sword", enter=1))
        r.analyseSecondStage(event("Skill", 19000, caster="p", target="boss", damageEff=100))
        r.analyseSecondStage(event("Battle", 20000, id="boss", fight=0))
        r.analyseSecondStage(event("Death", 21000, id="sword"))
        r.analyseSecondStage(event("Scene", 22000, id="late", enter=1))
        r.trimTime()
        r.getResult()
        self.assertEqual(len(r.detail["swords"]), 1)
        record = r.detail["swords"][0]
        self.assertEqual((record["end"], record["duration"]), (20000, 5))
        self.assertTrue(record["truncated"])
        self.assertFalse(record["killed"])
        self.assertEqual(r.detail["phaseTimes"]["天陨巨剑"], 5)
        self.assertEqual(sum(r.phaseTime), r.finalTime-r.startTime)
        for phase, seconds in r.detail["phaseTimes"].items():
            observed = sum(row["end"]-row["start"] for row in r.detail["phasePeriods"] if row["name"] == phase)
            self.assertAlmostEqual(seconds, observed/1000)

    def test_tian_resumed_damage_or_combat_cancels_disengage_candidate(self):
        for later in (event("Skill", 21000, caster="p", target="boss", damageEff=100),
                      event("Battle", 21000, id="boss", fight=1)):
            with self.subTest(later=later.dataType):
                r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
                r.analyseSecondStage(event("Skill", 19000, caster="p", target="boss", damageEff=100))
                r.analyseSecondStage(event("Battle", 20000, id="boss", fight=0))
                r.analyseSecondStage(later)
                r.trimTime()
                self.assertEqual(r.finalTime, 31000)

    def test_tian_stale_damage_does_not_trim(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
        r.analyseSecondStage(event("Skill", 2000, caster="p", target="boss", damageEff=100))
        r.analyseSecondStage(event("Battle", 20000, id="boss", fight=0))
        r.trimTime()
        self.assertEqual(r.finalTime, 31000)

    def test_twins_preparation_and_solo_dialogue_are_owner_scoped(self):
        r = encounter(YimanTwinsReplayer, {"night": ("139319", "伊曼·寂夜"),
                                          "fire": ("139322", "伊曼·逐焰"),
                                          "ring": ("139718", "")})
        prep = "妹妹！让无尽的圣火，熊熊燃烧吧！"
        r.analyseSecondStage(event("Shout", 2000, id="fire", content=prep))
        self.assertEqual(r.phase, 1)
        r.analyseSecondStage(event("Shout", 3000, id="night", content=prep))
        self.assertEqual(r.phase, 3)
        r.analyseSecondStage(event("Scene", 5000, id="ring", enter=1))
        self.assertEqual(r.phase, 2)
        r.analyseSecondStage(event("Shout", 10000, id="fire", content="姐姐！！—炸碎你们,统统炸碎！！！"))
        self.assertEqual(r.phase, 4)
        r.analyseSecondStage(event("Scene", 12000, id="ring", enter=0))
        self.assertEqual(r.phase, 4)
        self.assertEqual(r.win, 0)

    def test_twins_defeat_requires_owned_dialogue_and_recent_main_damage(self):
        line = "竟敢伤我们到这种程度。黑暗，定会吞噬你们！"
        r = encounter(YimanTwinsReplayer, {"night": ("139319", "伊曼·寂夜"),
                                          "fire": ("139322", "伊曼·逐焰")})
        r.analyseSecondStage(event("Shout", 2000, id="fire", content=line))
        self.assertEqual(r.win, 0)
        r.analyseSecondStage(event("Skill", 3000, caster="p", target="fire", damageEff=100))
        r.analyseSecondStage(event("Shout", 4000, id="night", content=line))
        self.assertEqual(r.win, 0)
        r.analyseSecondStage(event("Shout", 5000, id="fire", content=line))
        self.assertEqual((r.win, r.winTime), (1, 5000))


if __name__ == "__main__":
    unittest.main()

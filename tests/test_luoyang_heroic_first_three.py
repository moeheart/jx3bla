"""Heroic encounter identities and mechanics observed on 2026-11-13."""
import unittest
from types import SimpleNamespace as NS

from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer


def encounter(cls, templates):
    players = {key: NS(name=key) for key in ("p", "q")}
    info = NS(map="25人英雄洛阳之战", player=players,
              npc={key: NS(name=name, templateID=template)
                   for key, (template, name) in templates.items()})
    info.getName = lambda key: (info.player.get(key) or info.npc.get(key)).name
    replay = cls(NS(info=info, systemMessages=[]), {key: "1d" for key in players},
                 1000, 31000, 30000, cls.__name__, NS(item={"actor": {"filter": ""}}))
    replay.recordEquipment({})
    replay.initBattle()
    return replay


def event(kind, time, **fields):
    defaults = dict(id="", caster="", target="", damage=0, damageEff=0, stack=0,
                    enter=0, content="", full_id="", fight=0, hp=0, hpMax=100)
    defaults.update(fields)
    return NS(dataType=kind, time=time, **defaults)


def finish(replay):
    replay.trimTime()
    replay.getResult()


class HeroicFirstThreeTests(unittest.TestCase):
    def test_tuli_main_and_helper_identity_and_heroic_skill_axis(self):
        replay = encounter(TuliHeshunReplayer, {"boss": ("139360", "突利和顺"),
                          "wave": ("139412", "突利和顺"), "surge": ("139411", "突利和顺"),
                          "fire": ("139405", "突利和顺")})
        replay.analyseSecondStage(event("Skill", 2000, caster="p", target="boss", damageEff=1000))
        replay.analyseSecondStage(event("Skill", 2100, caster="p", target="wave", damageEff=9000))
        replay.analyseSecondStage(event("Cast", 3000, caster="boss", id="45490"))
        for time, caster, skill in ((4000, "wave", "45494"), (5000, "surge", "45493"),
                                    (6000, "fire", "46024"), (7000, "boss", "45496")):
            replay.analyseSecondStage(event("Skill", time, caster=caster, target="p", id=skill,
                                             damage=100, damageEff=100))
        replay.analyseSecondStage(event("Death", 8000, id="wave"))
        finish(replay)
        self.assertEqual(replay.win, 0)
        self.assertEqual(set(replay.bh.mainTargets), {"boss"})
        self.assertEqual(replay.statDict["p"]["bossDamage"], 1000)
        self.assertEqual([replay.statDict["p"][key] for key in
                          ("waveHits", "surgeHits", "fireHits", "collapseHits")], [1, 1, 1, 1])
        self.assertIn("黯穹崩天", [entry["skillname"] for entry in replay.bh.log["environment"]])

    def test_heroic_tian_records_both_swords_and_chest_before_tail_combat(self):
        replay = encounter(TianChengsiReplayer, {"boss": ("139382", "田承嗣"),
                          "first": ("140386", "天陨巨剑"), "second": ("141799", "天陨巨剑"),
                          "box": ("140091", "田承嗣宝箱")})
        for time, target, damage in ((2000, "first", 17819000), (6000, "second", 12473000)):
            replay.analyseSecondStage(event("Scene", time, id=target, enter=1))
            replay.analyseSecondStage(event("Skill", time+1000, caster="p", target=target, damageEff=damage))
            replay.analyseSecondStage(event("Death", time+2000, id=target))
        self.assertEqual(replay.win, 0)
        replay.analyseSecondStage(event("Scene", 10000, id="box", enter=1))
        replay.analyseSecondStage(event("Battle", 11000, id="boss", fight=1))
        replay.analyseSecondStage(event("Skill", 12000, caster="p", target="boss", damageEff=9000))
        finish(replay)
        self.assertEqual((replay.win, replay.finalTime), (1, 10000))
        self.assertEqual(replay.statDict["p"]["swordDamage"], 30292000)
        self.assertNotIn("bossDamage", replay.statDict["p"])
        self.assertEqual([row["duration"] for row in replay.detail["swords"]], [2, 2])
        self.assertTrue(all(row["killed"] for row in replay.detail["swords"]))

    def test_heroic_tian_carrier_buff_counts_second_sword_and_merges_control(self):
        replay = encounter(TianChengsiReplayer, {"boss": ("139382", "田承嗣")})
        for time, player, skill, stack in ((2000, "p", "34329", 1), (3000, "p", "34866", 1),
                                           (4000, "p", "34866", 1), (6000, "p", "34329", 0),
                                           (7000, "p", "34866", 0), (9000, "q", "34866", 1),
                                           (11000, "q", "34329", 0), (12000, "q", "34866", 0)):
            replay.analyseSecondStage(event("Buff", time, caster="boss", target=player, id=skill, stack=stack))
        finish(replay)
        self.assertEqual([replay.statDict[player]["swordCalls"] for player in ("p", "q")], [1, 1])
        self.assertEqual([replay.stunCounter[player].buffTimeIntegral() for player in ("p", "q")], [5000, 3000])

    def test_heroic_tian_soldiers_and_returning_sword_appear_on_axis(self):
        replay = encounter(TianChengsiReplayer, {"boss": ("139382", "田承嗣"),
                          "arrow": ("139392", "弓兵"), "spear": ("139393", "枪兵"),
                          "hammer": ("139396", "骨朵兵")})
        replay.analyseSecondStage(event("Cast", 2000, caster="boss", id="45976"))
        for time, caster, skill in ((3000, "arrow", "46030"), (4000, "spear", "46001"),
                                   (5000, "hammer", "46439"), (6000, "boss", "46438"),
                                   (7000, "boss", "46557")):
            replay.analyseSecondStage(event("Skill", time, caster=caster, target="p", id=skill,
                                             damage=100, damageEff=100))
        finish(replay)
        self.assertEqual(replay.statDict["p"]["spearHits"], 1)
        self.assertEqual({entry["skillid"] for entry in replay.bh.log["environment"]},
                         {"45976", "46030", "46001", "46439", "46438", "46557"})

    def test_heroic_twins_damage_separates_chain_main_and_inert(self):
        replay = encounter(YimanTwinsReplayer, {"night": ("139373", "伊曼·寂夜"),
                          "fire": ("139376", "伊曼·逐焰"), "chain": ("139716", "锁链"),
                          "ring": ("139717", ""), "inert": ("139374", "")})
        replay.analyseSecondStage(event("Scene", 2000, id="chain", enter=1))
        for target in ("night", "fire", "chain", "ring", "inert"):
            replay.analyseSecondStage(event("Skill", 3000, caster="p", target=target, damageEff=1000))
        replay.analyseSecondStage(event("Scene", 6000, id="chain", enter=0))
        finish(replay)
        self.assertEqual(set(replay.bh.mainTargets), {"night", "fire"})
        self.assertEqual([replay.statDict["p"][key] for key in
                          ("nightDamage", "fireDamage", "chainDamage", "inertDamage")], [1000, 1000, 1000, 2000])
        self.assertEqual(replay.detail["chains"][0]["duration"], 4)
        self.assertFalse(replay.detail["chains"][0]["killed"])
        self.assertEqual(replay.win, 0)

    def test_heroic_prison_refresh_and_overlapping_stun_keep_control_union(self):
        replay = encounter(YimanTwinsReplayer, {"night": ("139373", "伊曼·寂夜")})
        for time, skill, stack in ((2000, "34270", 1), (3000, "34270", 1), (4000, "34504", 1),
                                   (5000, "34504", 0), (7000, "34270", 0)):
            replay.analyseSecondStage(event("Buff", time, caster="night", target="p", id=skill, stack=stack))
        finish(replay)
        self.assertEqual(replay.statDict["p"]["prisonCalls"], 1)
        self.assertEqual(replay.stunCounter["p"].buffTimeIntegral(), 5000)
        prisons = [row for row in replay.detail["mechanics"] if row["id"] == "34270"]
        self.assertEqual(len(prisons), 1)
        self.assertEqual(prisons[0]["end"]-prisons[0]["start"], 5000)

    def test_heroic_twins_ring_cycles_and_both_deaths(self):
        replay = encounter(YimanTwinsReplayer, {"night": ("139373", "伊曼·寂夜"),
                          "fire": ("139376", "伊曼·逐焰"), "ring": ("139717", "")})
        replay.analyseSecondStage(event("Scene", 2000, id="ring", enter=1))
        self.assertEqual(replay.phase, 2)
        replay.analyseSecondStage(event("Scene", 4000, id="ring", enter=0))
        self.assertEqual(replay.phase, 1)
        replay.analyseSecondStage(event("Death", 6000, id="night"))
        self.assertEqual(replay.win, 0)
        replay.analyseSecondStage(event("Death", 8000, id="fire"))
        finish(replay)
        self.assertEqual((replay.win, replay.finalTime), (1, 8000))

    def test_chain_period_and_control_are_clipped_at_heroic_chest(self):
        replay = encounter(YimanTwinsReplayer, {"night": ("139373", "伊曼·寂夜"),
                          "chain": ("139716", "锁链"), "box": ("140097", "伊曼寂夜宝箱")})
        replay.analyseSecondStage(event("Scene", 2000, id="chain", enter=1))
        replay.analyseSecondStage(event("Buff", 3000, caster="night", target="p", id="34270", stack=1))
        replay.analyseSecondStage(event("Scene", 6000, id="box", enter=1))
        replay.analyseSecondStage(event("Scene", 9000, id="chain", enter=0))
        finish(replay)
        self.assertEqual(replay.detail["chains"][0]["duration"], 4)
        self.assertTrue(replay.detail["chains"][0]["truncated"])
        self.assertEqual(replay.stunCounter["p"].buffTimeIntegral(), 3000)


if __name__ == "__main__":
    unittest.main()

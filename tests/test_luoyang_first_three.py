"""Encounter regressions: event identity, partial clears, trims and controls."""
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer


def encounter(cls, npc_templates):
    info = NS(player={"p": NS(name="测试者")},
              npc={key: NS(name=name, templateID=template)
                   for key, (template, name) in npc_templates.items()})
    info.getName = lambda key: (info.player.get(key) or info.npc.get(key)).name
    replay = cls(NS(info=info), {"p": "1d"}, 1000, 21000, 20000, cls.__name__,
                 NS(item={"actor": {"filter": ""}}))
    replay.recordEquipment({})
    replay.initBattle()
    return replay


def event(kind, time, **fields):
    defaults = dict(id="", caster="", target="", damage=0, damageEff=0,
                    stack=0, enter=0, content="", full_id="")
    defaults.update(fields)
    return NS(dataType=kind, time=time, **defaults)


def finish(replay):
    replay.trimTime()
    return replay.getResult()


class LuoyangEncounterTests(unittest.TestCase):
    def test_homonymous_tuli_helper_never_becomes_main_or_win(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺"),
                                            "clone": ("139352", "突利和顺")})
        r.analyseSecondStage(event("Skill", 2000, caster="p", target="clone", damage=999, damageEff=999))
        r.analyseSecondStage(event("Death", 3000, id="clone"))
        self.assertEqual(r.win, 0)
        self.assertEqual(set(r.bh.mainTargets), {"boss"})
        self.assertNotIn("bossDamage", r.statDict["p"])

    def test_calls_refresh_and_missing_remove_at_win(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺"),
                                            "box": ("140044", "突利和顺宝箱6")})
        for time, stack in ((2000, 1), (2500, 1), (4000, 0), (6000, 1)):
            r.analyseSecondStage(event("Buff", time, caster="boss", target="p", id="34238", stack=stack))
        r.analyseSecondStage(event("Scene", 8000, id="box", enter=1))
        r.analyseSecondStage(event("Skill", 9000, caster="p", target="boss", damageEff=999))
        finish(r)
        self.assertEqual(r.statDict["p"]["stingCalls"], 2)
        self.assertEqual([c["duration"] for c in r.bh.log["call"]["p"]], [2000, 2000])
        self.assertEqual(r.detail["effectiveTime"], 7000)
        self.assertEqual(r.statDict["p"]["bossDamageDps"], 0)
        self.assertEqual(r.finalTime, 8000)

    def test_field_slow_does_not_exclude_output_time(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺")})
        r.analyseSecondStage(event("Cast", 2000, caster="boss", id="45489"))
        r.analyseSecondStage(event("Buff", 2100, caster="boss", target="p", id="34490", stack=1))
        r.analyseSecondStage(event("Buff", 5000, caster="boss", target="p", id="33755", stack=1))
        finish(r)
        self.assertEqual(r.detail["phaseTimes"]["死水微澜"], 3)
        self.assertEqual(r.detail["effectiveTime"], 20000)
        self.assertEqual(r.stunCounter["p"].buffTimeIntegral(), 0)

    def test_sword_death_is_only_a_phase_transition(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣"),
                                             "sword": ("140384", "天陨巨剑")})
        r.analyseSecondStage(event("Scene", 2000, id="sword", enter=1))
        r.analyseSecondStage(event("Skill", 3000, caster="p", target="sword", damageEff=1000))
        r.analyseSecondStage(event("Death", 4000, id="sword"))
        finish(r)
        self.assertEqual(r.win, 0)
        self.assertEqual(r.statDict["p"]["swordDamage"], 1000)
        self.assertNotIn("bossDamage", r.statDict["p"])
        self.assertEqual(r.detail["swords"][0]["duration"], 2)

    def test_tian_reset_trims_without_fabricating_clear(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
        shout = "来战！正好让本将看看唐廷的斤两！"
        r.analyseSecondStage(event("Shout", 1500, id="boss", content=shout))
        r.analyseSecondStage(event("Shout", 12000, id="boss", content=shout))
        r.analyseSecondStage(event("Skill", 13000, caster="p", target="boss", damageEff=1000))
        finish(r)
        self.assertEqual((r.win, r.finalTime), (0, 12000))
        self.assertEqual(r.statDict["p"]["bossDamageDps"], 0)

    def test_tian_control_is_clipped_at_clear(self):
        r = encounter(TianChengsiReplayer, {"boss": ("139329", "田承嗣")})
        r.analyseSecondStage(event("Buff", 2000, caster="boss", target="p", id="34329", stack=1))
        r.analyseSecondStage(event("Death", 5000, id="boss"))
        finish(r)
        self.assertEqual(r.stunCounter["p"].buffTimeIntegral(), 3000)

    def test_twins_require_both_deaths_and_owner_scoped_dialogue(self):
        r = encounter(YimanTwinsReplayer, {"a": ("139319", "伊曼·寂夜"),
                                           "b": ("139322", "伊曼·逐焰")})
        r.analyseSecondStage(event("Death", 2000, id="a"))
        r.analyseSecondStage(event("Shout", 3000, id="p", content='"一切都结束了"'))
        self.assertEqual(r.win, 0)
        r.analyseSecondStage(event("Death", 4000, id="b"))
        self.assertEqual(r.win, 1)

    def test_twins_ignore_next_encounter_and_inert_targets(self):
        r = encounter(YimanTwinsReplayer, {"a": ("139319", "伊曼·寂夜"),
                                           "b": ("139322", "伊曼·逐焰"),
                                           "ctrl": ("139327", "3号_场控"),
                                           "inert": ("139320", ""),
                                           "next": ("139323", "阿史那承庆")})
        for target in ("a", "b", "inert"):
            r.analyseSecondStage(event("Skill", 2000, caster="p", target=target, damageEff=1000))
        r.analyseSecondStage(event("Shout", 5000, id="ctrl", content='"一切都结束了"'))
        r.analyseSecondStage(event("Skill", 9000, caster="next", target="p", damage=1000, id="45912"))
        finish(r)
        self.assertEqual(set(r.bh.mainTargets), {"a", "b"})
        self.assertEqual(r.detail["effectiveTime"], 4000)
        self.assertNotIn("ringHits", r.statDict["p"])
        self.assertEqual(r.statDict["p"]["inertDamageDps"], 250)

    def test_environment_icons_are_bundled(self):
        for cls in (TuliHeshunReplayer, TianChengsiReplayer, YimanTwinsReplayer):
            for name, icon, color in cls.ENVIRONMENT.values():
                self.assertTrue((Path(__file__).resolve().parents[1] / "icons" / (icon + ".png")).exists(), (name, icon))

    def test_observations_obey_pot_window_contract(self):
        r = encounter(TuliHeshunReplayer, {"boss": ("139306", "突利和顺")})
        r.analyseSecondStage(event("Skill", 2000, caster="boss", target="p", id="46024", damage=500))
        r.analyseSecondStage(event("Skill", 2010, caster="boss", target="p", id="46024", damage=500))
        finish(r)
        self.assertEqual(len(r.potList), 1)
        self.assertEqual(len(r.potList[0]), 7)
        self.assertEqual(r.potList[0][2], 0)
        self.assertEqual(r.potList[0][6], 0)
        self.assertEqual(r.statDict["p"]["fireHits"], 1)


if __name__ == "__main__":
    unittest.main()

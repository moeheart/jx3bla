"""Deterministic mechanic regressions plus optional read-only real-log replay."""
import argparse
import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.BattleLogData import BattleLogData
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi


def event(kind, time, **kwargs):
    fields = dict(dataType=kind, time=time, id="0", caster="boss", target="p", damage=0,
                  damageEff=0, heal=0, healEff=0, effect=0, stack=0, enter=0,
                  full_id="1,0,1", content="", level=1)
    fields.update(kwargs)
    return NS(**fields)


def replayer(cls, templates=None):
    bld = BattleLogData()
    bld.info.map = "25人普通洛阳之战"
    bld.info.skill = {}
    bld.info.addPlayer("p", '"测试"', "2", "0")
    for key, template, name in templates or [("boss", cls.MAIN_IDS[0], cls.BOSS)]:
        bld.info.addNPC(key, '"'+name+'"')
        bld.info.npc[key].templateID = template
    obj = cls(bld, {"p": "2"}, 1000, 21000, 20000, cls.BOSS, NS(item={"actor": {"filter": ""}}))
    obj.initBattle()
    obj.recordEquipment({})
    return obj


def damage(time=2000, target="boss"):
    return event("Skill", time, caster="p", target=target, damage=100, damageEff=100)


class MechanicsTest(unittest.TestCase):
    def test_same_named_clone_never_main_or_win(self):
        r = replayer(Ashina, [("boss", "139323", Ashina.BOSS), ("clone", "139331", Ashina.BOSS)])
        r.analyseSecondStage(damage(target="clone"))
        r.analyseSecondStage(event("Death", 3000, id="clone"))
        r.countFinal()
        self.assertEqual(r.win, 0)
        self.assertNotIn("mainDamage", r.statDict["p"]["battle"])

    def test_death_wins_and_trims_tail(self):
        r = replayer(Ashina)
        r.analyseSecondStage(damage())
        r.analyseSecondStage(event("Death", 5000, id="boss"))
        r.trimTime(); r.getResult()
        self.assertEqual((r.win, r.finalTime, r.bh.sumTime("dps")), (1, 5000, 4000))

    def test_refresh_is_one_call_and_truncated_call_closed(self):
        r = replayer(Ashina)
        for t, stack in [(2000, 1), (3000, 2), (4000, 3)]:
            r.analyseSecondStage(event("Buff", t, id="34256", stack=stack))
        r.countFinal()
        self.assertEqual(r.statDict["p"]["battle"]["bombCalls"], 1)
        self.assertEqual(len(r.bh.log["call"]["p"]), 1)
        self.assertEqual(r.bh.log["call"]["p"][0]["duration"], 19000)

    def test_lost_soul_threshold_and_reset(self):
        r = replayer(Ashina)
        for t, stack in [(2000, 4), (3000, 5), (4000, 5)]:
            r.analyseSecondStage(event("Buff", t, id="34376", stack=stack))
        self.assertEqual(len(r.potList), 1)

    def test_soul_loop_and_repeated_soak(self):
        r = replayer(Ashina)
        r.analyseSecondStage(event("Cast", 2000, id="45916"))
        r.analyseSecondStage(event("Buff", 2500, id="34251", stack=1))
        r.analyseSecondStage(event("Buff", 3000, id="34252", stack=1))
        r.analyseSecondStage(event("Skill", 3000, id="45932", damage=20))
        self.assertEqual(len(r.potList), 0)
        r.analyseSecondStage(event("Skill", 4000, id="45932", damage=20))
        r.analyseSecondStage(event("Buff", 4500, id="34251", stack=0))
        r.countFinal()
        self.assertEqual(sum(pot[2] > 0 for pot in r.potList), 1)
        self.assertEqual(r.detail["P2Time"], 2.5)

    def test_failed_final_file_despawn_and_rewards_do_not_win(self):
        for content in ['"获得了150点历练值。"', '""']:
            r = replayer(Shi)
            r.analyseSecondStage(damage())
            r.analyseSecondStage(event("Shout", 3000, content=content))
            r.analyseSecondStage(event("Scene", 4000, id="boss", enter=0))
            r.countFinal()
            self.assertEqual(r.win, 0)

    def test_reward_requires_system_sender_main_exit_and_recent_combat(self):
        content = '"书剑天涯活动期间，侠士完成【击杀25人普通秘境首领】，额外获得四乡风物5个。"'
        for sender, exit_time, expected in [("0", 4000, 1), ("p", 4000, 0), ("0", 20000, 0), ("0", None, 0)]:
            r = replayer(Shi)
            r.analyseSecondStage(damage())
            r.analyseSecondStage(event("Shout", 3000, id=sender, content=content))
            if exit_time:
                r.analyseSecondStage(event("Scene", exit_time, id="boss", enter=0))
            r.trimTime(); r.countFinal()
            self.assertEqual(r.win, expected)
            if expected:
                self.assertEqual((r.finalTime, r.bh.sumTime("dps")), (3000, 2000))

    def test_phase_detection_never_invents_third_phase(self):
        r = replayer(Shi)
        r.analyseSecondStage(event("Skill", 5000, id="45607"))
        r.analyseSecondStage(event("Cast", 9000, id="45711"))
        r.countFinal()
        self.assertEqual((r.detail["P1Time"], r.detail["P2Time"], r.detail["P3Time"]), (4, 16, 0))
        r = replayer(Shi)
        r.analyseSecondStage(event("Cast", 5000, id="45726"))
        self.assertEqual(r.phase, 3)

    def test_strong_explosion_is_observation_not_blame(self):
        r = replayer(Shi)
        for t in [2000, 2100]:
            r.analyseSecondStage(event("Skill", t, id="45707", damage=10))
        self.assertEqual(len(r.potList), 0)
        self.assertEqual(r.statDict["p"]["battle"]["strongSplitHits"], 1)

    def test_add_only_attempt_keeps_main_identity_and_separate_damage(self):
        r = replayer(Shi, [("boss", "139312", Shi.BOSS), ("add", "139308", "煞将"),
                           ("clone", "139314", Shi.BOSS)])
        r.analyseSecondStage(damage(target="add"))
        r.countFinal()
        self.assertEqual(set(r.bh.mainTargets), {"boss"})
        self.assertEqual(r.statDict["p"]["battle"]["shaDamage"], 100)
        self.assertEqual(r.statDict["p"]["battle"]["mainDps"], 0)
        self.assertEqual(r.win, 0)

    def test_delayed_win_clips_closed_call_and_late_add_damage_once(self):
        r = replayer(Shi, [("boss", "139312", Shi.BOSS), ("add", "139308", "煞将")])
        r.analyseSecondStage(damage())
        r.analyseSecondStage(damage(2200, "add"))
        r.analyseSecondStage(event("Buff", 2500, id="34115", stack=1))
        r.analyseSecondStage(event("Shout", 3000, id="0",
                                  content='"侠士完成【击杀25人普通秘境首领】"'))
        r.analyseSecondStage(event("Buff", 3500, id="34115", stack=0))
        r.analyseSecondStage(damage(3600, "add"))
        r.analyseSecondStage(event("Scene", 4000, id="boss", enter=0))
        r.trimTime(); r.getResult()
        self.assertEqual(r.bh.log["call"]["p"][0]["duration"], 500)
        self.assertEqual(r.detail["mechanics"][0]["end"], 3000)
        self.assertTrue(r.detail["mechanics"][0]["truncated"])
        self.assertEqual(r.statDict["p"]["battle"]["shaDamage"], 100)
        before = (list(r.phaseTime), len(r.potList), len(r.detail["winEvidence"]))
        r.trimTime(); r.getResult()
        self.assertEqual(before, (r.phaseTime, len(r.potList), len(r.detail["winEvidence"])))
        self.assertEqual(r.statDict["p"]["battle"]["shaDamage"], 100)

    def test_failed_attempt_cutoff_agrees_with_history_calls_and_dps(self):
        r = replayer(Ashina)
        r.trimmedFinalTime = 10000
        r.bh.setBadPeriod(10000, r.bh.finalTime, True, True)
        r.analyseSecondStage(damage())
        r.analyseSecondStage(event("Buff", 5000, id="34208", stack=1))
        r.analyseSecondStage(event("Buff", 6000, id="34226", stack=1))
        r.trimTime(); r.getResult()
        self.assertEqual((r.battleTime, r.bh.sumTime("dps"), r.detail["effectiveTime"]), (9000, 9000, 9000))
        self.assertEqual(r.bh.log["call"]["p"][0]["duration"], 5000)
        self.assertEqual(r.stunCounter["p"].buffTimeIntegral(), 4000)
        self.assertEqual(sum(r.phaseTime), 9000)


def replay_logs(folder):
    rows = []
    pattern = re.compile(r'\((139323|139312|139332|139308|139324)\)\.jcl$')
    for path in sorted(Path(folder).glob('*洛阳之战*.jcl')):
        match = pattern.search(path.name)
        if not match:
            continue
        cls = Ashina if match.group(1) == '139323' else Shi
        with contextlib.redirect_stdout(io.StringIO()):
            b = BattleLogData(); b.loadFromJcl(str(path))
            start, end = b.log[0].time, b.log[-1].time
            r = cls(b, {key: value.occ for key, value in b.info.player.items()}, start, end,
                    end-start, cls.BOSS, NS(item={"actor": {"filter": ""}}))
            r.initBattle(); r.recordEquipment({})
            for e in b.log:
                r.analyseSecondStage(e)
            r.trimTime(); r.getResult()
        row = {"file": path.name, "win": r.win, "rule": r.detail["winReason"],
               "phases": r.detail["phaseTimes"], "calls": sum(map(len, r.bh.log["call"].values())),
               "failureCount": sum(pot[2] > 0 for pot in r.potList),
               "observations": sum(pot[2] == 0 for pot in r.potList), "effectiveMs": r.bh.sumTime("dps"),
               "mainDamage": sum(x["battle"].get("mainDamage", 0) for x in r.statDict.values()),
               "addDamage": sum(x["battle"].get("constructDamage", 0)+x["battle"].get("shaDamage", 0) for x in r.statDict.values())}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logs')
    parser.add_argument('--output')
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MechanicsTest))
    if not result.wasSuccessful():
        sys.exit(1)
    if args.logs:
        rows = replay_logs(args.logs)
        if args.output:
            Path(args.output).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')

"""Victory needs local completion corroboration, not capped reward messages."""
import contextlib
import io
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import mock_open, patch

from data.BattleLogData import BattleLogData
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer as Tian
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi
from tools.ValidateLuoyangLastTwo import event, damage


ROOT = Path(__file__).resolve().parents[1]
CASES = ((Tian, "田承嗣", "139329", "140384", 2),
         (Ashina, "阿史那承庆", "139323", "139331", 4),
         (Shi, "史朝义", "139312", "139346", 5))
REAL_CASES = (
    (CASES[0], "2026-11-02-20-05-46-25人普通洛阳之战(835)-田承嗣(139329).jcl", 203193),
    (CASES[1], "2026-11-02-20-16-04-25人普通洛阳之战(835)-阿史那承庆(139323).jcl", 240022),
    (CASES[2], "2026-11-02-20-23-43-25人普通洛阳之战(835)-史朝义(139312).jcl", 263702),
)


def completion(case, time=19500, **fields):
    text = "[全胜！25人普通洛阳之战]：%d/5，击败%s！25人普通(完成)\\n" % (case[4], case[1])
    values = dict(channel="MSG_SYS", content=text)
    values.update(fields)
    return event("System", time, **values)


def exit_event(time=20000, **fields):
    values = dict(id="boss", fight=0, hp=1, hpMax=100)
    values.update(fields)
    return event("Battle", time, **values)


def pressure(time=19500, **fields):
    values = dict(id="35875", stack=1, isValid=True, delete="false", frame=1000, end=2087)
    values.update(fields)
    return event("Buff", time, **values)


def make_replayer(case, bld=None):
    cls, name, template, clone, _ = case
    if bld is None:
        bld = BattleLogData()
        bld.info.map = "25人普通洛阳之战"
        bld.info.skill = {}
        bld.info.addPlayer("p", '"测试"', "2", "0")
        for key, tid in (("boss", template), ("other", template), ("clone", clone)):
            bld.info.addNPC(key, '"'+name+'"')
            bld.info.npc[key].templateID = tid
        start, end = 1000, 31000
    else:
        start, end = bld.log[0].time, bld.log[-1].time
    r = cls(bld, {key: player.occ for key, player in bld.info.player.items()},
            start, end, end-start, name, NS(item={"actor": {"filter": ""}}))
    r.initBattle()
    r.recordEquipment({})
    return r


def finish(r, events):
    for e in sorted(events, key=lambda e: e.time):
        r.analyseSecondStage(e)
    r.trimTime()
    r.getResult()
    return r


class CompletionParsingTests(unittest.TestCase):
    def load_lines(self, lines):
        bld = BattleLogData()
        with patch("builtins.open", mock_open(read_data=("\n".join(lines)+"\n").encode("utf-8"))):
            with contextlib.redirect_stdout(io.StringIO()):
                bld.loadFromJcl(REAL_CASES[0][1])
        return bld

    def test_type18_retains_channel_without_becoming_npc_shout(self):
        content = completion(CASES[0]).content
        lines = [
            '1\t1\t1793664964\t19500\t18\t{"%s","MSG_SYS"}' % content,
            '2\t2\t1793664964\t19501\t18\t{"%s","MSG_OTHER"}' % content,
            '3\t3\t1793664964\t19502\t14\t{"%s",123,0,"田承嗣"}' % content,
        ]
        bld = self.load_lines(lines)
        self.assertEqual([e.dataType for e in bld.log], ["Shout"])
        self.assertEqual([e.dataType for e in bld.systemMessages], ["System", "System"])
        self.assertEqual((bld.systemMessages[0].time, bld.systemMessages[0].content, bld.systemMessages[0].channel),
                         (19500, content, "MSG_SYS"))
        self.assertEqual(bld.systemMessages[1].channel, "MSG_OTHER")
        self.assertEqual(bld.log[0].id, "123")

    def test_leading_and_trailing_system_messages_do_not_extend_combat(self):
        content = completion(CASES[0]).content
        bld = self.load_lines([
            '1\t1\t1793664964\t1000\t18\t{"消息","MSG_SYS"}',
            '2\t2\t1793664964\t19000\t21\t{10,20,0,1,2477,1,0,0,{[0]=100,[13]=100}}',
            '3\t3\t1793664964\t20000\t9\t{20,false,100,100,0,0}',
            '4\t4\t1793664964\t20500\t18\t{"%s","MSG_SYS"}' % content,
            '5\t5\t1793664964\t30000\t18\t{"尾录消息","MSG_SYS"}',
            '6\t6\t1793664964\t30001\t4\t{10,"测试",2,0,0,{}}',
            '7\t7\t1793664964\t30002\t8\t{20,"田承嗣",139329,0,0,0,0,0}',
        ])
        self.assertEqual((bld.log[0].time, bld.log[-1].time), (19000, 20000))
        self.assertEqual([e.time for e in bld.systemMessages], [1000, 20500, 30000])
        r = finish(make_replayer(CASES[0], bld), bld.log)
        self.assertEqual((r.win, r.finalTime), (1, 20000))

    def test_merge_keeps_both_message_collections_separate_from_combat(self):
        def part(time):
            bld = self.load_lines([
                '1\t1\t1793664964\t%d\t9\t{20,false,100,100,0,0}' % time,
                '2\t2\t1793664964\t%d\t18\t{"消息","MSG_SYS"}' % (time+1),
            ])
            bld.info.server = "测试服"
            bld.info.battleTime = time
            bld.info.sumTime = 0
            return bld
        previous, current = part(1000), part(2000)
        self.assertEqual(current.merge(previous), 0)
        self.assertEqual([e.time for e in current.log], [1000, 2000])
        self.assertEqual([e.time for e in current.systemMessages], [1001, 2001])


class CompletionEvidenceTests(unittest.TestCase):
    def test_completion_before_or_after_exit_wins_at_exit_even_with_full_hp(self):
        for case in CASES:
            for time in (19500, 20500):
                with self.subTest(boss=case[1], completionTime=time):
                    r = finish(make_replayer(case), [damage(19000), completion(case, time),
                                                     exit_event(hp=100)])
                    self.assertEqual((r.win, r.finalTime), (1, 20000))
                    self.assertEqual(r.detail["winReason"], "boss_completion_and_combat_exit")
                    evidence = r.detail["winEvidence"][-1]
                    self.assertEqual((evidence["npcID"], evidence["completionTime"]), ("boss", time))
                    self.assertEqual(sum(r.phaseTime), 19000)
                    self.assertEqual(r.bh.sumTime("dps"), 19000)

    def test_wrong_message_source_or_content_never_confirms(self):
        for case in CASES:
            correct = completion(case).content
            noises = [
                event("Shout", 19500, id=sender, content=correct) for sender in ("boss", "p", "0")
            ] + [completion(case, channel="MSG_OTHER"),
                 completion(case, content=correct.replace(case[1], "错误首领")),
                 completion(case, content=correct.replace("25人普通", "25人英雄")),
                 completion(case, content=correct.replace("洛阳之战", "其他副本")),
                 completion(case, content=correct.replace("(完成)", "(未完成)")),
                 completion(case, content="转发："+correct),
                 completion(case, content=correct+"其他文字"),
                 completion(case, content="获得了150点历练值。"),
                 completion(case, content="获得了150点祈愿值。"),
                 completion(case, content="[茗伊插件]正在分享：击败%s！25人普通" % case[1]),
                 completion(case, content="[茗伊插件]成功分享：击败%s！25人普通" % case[1])]
            for noise in noises:
                with self.subTest(boss=case[1], noise=vars(noise)):
                    r = finish(make_replayer(case), [damage(19000), noise, exit_event()])
                    self.assertEqual(r.win, 0)

    def test_wrong_map_and_unconfirmed_low_hp_exit_do_not_win(self):
        for case in CASES:
            for map_name in ("25人英雄洛阳之战", "10人普通洛阳之战", "25人普通其他副本"):
                with self.subTest(boss=case[1], map=map_name):
                    r = make_replayer(case)
                    r.bld.info.map = map_name
                    self.assertEqual(finish(r, [damage(19000), completion(case), exit_event()]).win, 0)
            r = finish(make_replayer(case), [damage(19000), exit_event()])
            self.assertEqual(r.win, 0)

    def test_recent_damage_and_exit_must_belong_to_same_main_entity(self):
        for case in CASES:
            cases = {
                "no_damage": [completion(case), exit_event()],
                "stale_damage": [damage(13000), completion(case), exit_event()],
                "no_exit": [damage(19000), completion(case)],
                "different_main_entity": [damage(19000), completion(case), exit_event(id="other")],
                "same_name_clone_exit": [damage(19000), completion(case), exit_event(id="clone")],
                "same_name_clone_damage": [damage(19000, target="clone"), completion(case), exit_event()],
                "non_player_damage": [event("Skill", 19000, caster="clone", target="boss", damageEff=100),
                                      completion(case), exit_event()],
                "zero_damage": [event("Skill", 19000, caster="p", target="boss", damageEff=0),
                                completion(case), exit_event()],
                "completion_before_damage": [completion(case, 18000), damage(19000), exit_event()],
                "stale_completion": [damage(19000), exit_event(), completion(case, 26000)],
            }
            for label, events in cases.items():
                with self.subTest(boss=case[1], case=label):
                    self.assertEqual(finish(make_replayer(case), events).win, 0)

    def test_resumed_combat_cancels_candidates_and_old_completion(self):
        for case in CASES:
            for later in (damage(21000), exit_event(21000, fight=1)):
                with self.subTest(boss=case[1], resumed=later.dataType):
                    r = finish(make_replayer(case), [damage(19000), completion(case), exit_event(), later])
                    self.assertEqual((r.win, r.finalTime), (0, 31000))
            r = finish(make_replayer(case), [damage(19000), completion(case), exit_event(),
                                             exit_event(21000, fight=1), damage(22000), exit_event(23000)])
            self.assertEqual(r.win, 0)

    def test_earlier_actor_cutoff_is_not_promoted_by_later_completion(self):
        for case in CASES:
            with self.subTest(boss=case[1]):
                r = make_replayer(case)
                r.trimmedFinalTime = 18000
                finish(r, [damage(19000), completion(case), exit_event()])
                self.assertEqual((r.win, r.finalTime), (0, 18000))


class PressureEvidenceTests(unittest.TestCase):
    def test_long_pressure_is_independent_of_reward_or_completion_and_prefers_exit(self):
        for events, end in (([damage(19000), pressure()], 19500),
                            ([damage(19000), pressure(), exit_event()], 20000)):
            with self.subTest(end=end):
                r = finish(make_replayer(CASES[1]), events)
                self.assertEqual((r.win, r.finalTime), (1, end))
                self.assertEqual(r.detail["winReason"], "long_pressure_buff")
                self.assertEqual(r.detail["winEvidence"][-1]["remainingFrames"], 1087)

    def test_short_invalid_or_unrelated_pressure_cannot_win(self):
        invalid = [dict(end=1032), dict(end=1960), dict(stack=0), dict(isValid=False),
                   dict(delete="true"), dict(caster="other"), dict(caster="clone"),
                   dict(target="unknown"), dict(id="34226")]
        for values in invalid:
            with self.subTest(values=values):
                r = finish(make_replayer(CASES[1]), [damage(19000), pressure(**values), exit_event()])
                self.assertEqual(r.win, 0)
        for missing in ("frame", "end"):
            with self.subTest(missing=missing):
                buff = pressure()
                delattr(buff, missing)
                self.assertEqual(finish(make_replayer(CASES[1]), [damage(19000), buff, exit_event()]).win, 0)

    def test_pressure_requires_map_boss_and_recent_damage(self):
        for case in (CASES[0], CASES[2]):
            with self.subTest(boss=case[1]):
                self.assertEqual(finish(make_replayer(case), [damage(19000), pressure(), exit_event()]).win, 0)
        for map_name in ("25人英雄洛阳之战", "10人普通洛阳之战"):
            r = make_replayer(CASES[1])
            r.bld.info.map = map_name
            self.assertEqual(finish(r, [damage(19000), pressure(), exit_event()]).win, 0)
        for events in ([pressure(), exit_event()], [damage(13000), pressure(), exit_event()]):
            self.assertEqual(finish(make_replayer(CASES[1]), events).win, 0)

    def test_pressure_cancelled_by_resumed_combat_or_earlier_cutoff(self):
        for later in (damage(21000), exit_event(21000, fight=1)):
            r = finish(make_replayer(CASES[1]), [damage(19000), pressure(), exit_event(), later])
            self.assertEqual((r.win, r.finalTime), (0, 31000))
        r = make_replayer(CASES[1])
        r.trimmedFinalTime = 18000
        self.assertEqual(finish(r, [damage(19000), pressure(), exit_event()]).win, 0)
        self.assertEqual(r.finalTime, 18000)


@unittest.skipUnless(all((ROOT / name).is_file() for _, name, _ in REAL_CASES),
                     "Optional original 2026-11-02 JCL fixtures are not installed")
class OriginalTeamVictoryTests(unittest.TestCase):
    def test_three_missed_clears_without_reward_messages(self):
        for case, name, expected_duration in REAL_CASES:
            with self.subTest(boss=case[1]):
                bld = BattleLogData()
                with patch("socket.socket.connect", side_effect=AssertionError("Offline regression")):
                    with contextlib.redirect_stdout(io.StringIO()):
                        bld.loadFromJcl(str(ROOT / name))
                        r = finish(make_replayer(case, bld), bld.log)
                self.assertFalse(any("历练值" in e.content or "祈愿值" in e.content
                                     for e in bld.systemMessages))
                self.assertEqual((r.win, r.battleTime), (1, expected_duration))
                self.assertEqual(sum(r.phaseTime), expected_duration)
                self.assertTrue(all(e["start"]+e["duration"] <= r.finalTime for e in r.bh.log["environment"]))
                # Ashina's ending remains identifiable when every message is absent.
                if case[0] is Ashina:
                    bld.systemMessages = []
                    r = finish(make_replayer(case, bld), bld.log)
                    self.assertEqual((r.win, r.battleTime), (1, expected_duration))
                    self.assertEqual(r.detail["winReason"], "long_pressure_buff")


if __name__ == "__main__":
    unittest.main()

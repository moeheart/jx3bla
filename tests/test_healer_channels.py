import unittest
from types import SimpleNamespace

from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.occ.Healer import HealerReplay
from replayer.occ.LiJingYiDao import LiJingYiDaoReplayer
from replayer.occ.HealingChannel import HealingChannel, channel_efficiencies
from tools.Functions import SkillCounterAdvance


class HealerChannelTests(unittest.TestCase):
    def test_longwu_multitarget_pulses_completion_dispel_and_excluded_cast(self):
        healer = LiJingYiDaoReplayer.__new__(LiJingYiDaoReplayer)
        healer.occ, healer.mykey = "lijingyidao", "caster"
        healer.startTime, healer.finalTime, healer.haste = 0, 6000, 0
        healer.ss = SingleSkill(0, 0)
        healer.bh, healer.bossBh = BattleHistory(0, 6000), BattleHistory(0, 6000)
        healer.bossBh.badPeriodHealerLog = [[0, 0], [4500, 1]]
        healer.bossBh.critPeriodDesc, healer.bossBh.critPeriodSum = "", 0
        healer.act = SimpleNamespace(rhps={"player": {}})
        healer.result = {"skill": {}, "overall": {"sumTimeEff": 4500}}
        line = [None, "泷雾", ["28541", "28540", "45815", "45816"], "16221", True, 12, True, True, 0, 1]
        line[0] = SkillCounterAdvance(line, 0, 6000, 0, exclude=healer.bossBh.badPeriodHealerLog)
        healer.skillInfo = [line]
        healer.gcdSkillIndex = dict.fromkeys(line[2], 0)
        healer.nonGcdSkillIndex, healer.gcdChannelLog = {}, HealingChannel()

        def cast(time):
            healer.eventInSecondState(SimpleNamespace(dataType="Cast", id="28540", caster="caster", time=time))

        def hit(skill, time, level=1, heal=0):
            healer.eventInSecondState(SimpleNamespace(
                dataType="Skill", id=skill, caster="caster", target="target", time=time, level=level,
                heal=heal, healEff=heal, damage=0, damageEff=0, scheme=1, effect=0))

        cast(1000)
        hit("28538", 1001)
        for t in (1750, 2500, 3250, 4000):
            hit("28540", t)
            hit("45815", t + 5, heal=10)
            hit("28541", t + 10)
        hit("28541", 4200, level=2)
        cast(5000)
        healer.completeSecondState()
        healer.calculateSkillInfo("longwu", "28541")
        card = healer.result["skill"]["longwu"]
        self.assertEqual((card["num"], card["delaySamples"], card["delay"]), (1, 1, 1000))
        self.assertEqual((card["ticks"], card["healingEvents"], card["heal"], card["healEff"]),
                         (4, 4, 40, 40))
        self.assertEqual([(r["start"], r["duration"], r["num"], r["ticks"], r["heal"], r["iconid"])
                          for r in healer.bh.log["normal"]],
                         [(1000, 3000, 1, 4, 40, "16221"), (5000, 0, 1, 0, 0, "16221")])

    def test_quick_recasts_are_separate_but_one_multitarget_cast_has_one_icon(self):
        healer = HealerReplay.__new__(HealerReplay)
        healer.occ, healer.mykey = "test", "caster"
        healer.ss, healer.bh = SingleSkill(0, 0), BattleHistory(0, 5000)
        healer.skillInfo = [[None, "群疗", ["10"], "123", True, 0, False, True, 0, 1]]
        healer.gcdSkillIndex, healer.nonGcdSkillIndex = {"10": 0}, {}
        healer.lastNormalImpact, healer.normalTargets = None, set()
        healer.bld = SimpleNamespace(info=SimpleNamespace(player={}, npc={}))

        def hit(time, target):
            healer.eventInSecondState(SimpleNamespace(
                dataType="Skill", id="10", caster="caster", time=time, target=target,
                heal=5, healEff=3, damage=0, damageEff=0, scheme=1, effect=0))

        hit(1000, "A")
        hit(1010, "B")
        hit(1020, "A")
        healer.eventInSecondState(SimpleNamespace(dataType="Cast", id="10", caster="caster", time=1030))
        hit(1040, "C")
        hit(2540, "C")
        self.assertEqual([(r["start"], r["num"], r["heal"]) for r in healer.bh.log["normal"]],
                         [(1000, 1, 10), (1020, 1, 5), (1040, 1, 5), (2540, 1, 5)])

    def test_jiguang_uses_talents_before_timing(self):
        trace = HealingChannel()
        trace.cast(1000)
        self.assertTrue(trace.jiguang({"available": 1, "3": "吉光"}))
        self.assertFalse(trace.jiguang({"available": 0}))
        trace.tick(1001)
        self.assertTrue(trace.jiguang({"available": 0}))
        self.assertFalse(trace.jiguang({"available": 1, "3": "霞绡"}))
        self.assertFalse(trace.jiguang({"available": 0, "3": "妍姿"}))

    def test_one_cast_despite_shell_multitarget_ticks_or_early_interrupt(self):
        trace = HealingChannel()
        trace.cast(1000)
        trace.cast(1004, shell=True)
        for time in (1006, 1021, 1390, 1410, 1710, 1715):
            trace.tick(time)
        trace.cast(3000)  # interrupted before a tick, still triggers 吉光 GCD
        log, starts = trace.intervals(0, 5000, 750, immediate=True, ticks_per_cast=4)
        self.assertEqual(starts, [1000, 3000])
        self.assertEqual(log, [[0, 0], [1000, 1], [1710, 0], [5000, 0]])

    def test_native_recast_and_same_frame_targets(self):
        trace = HealingChannel()
        # Even a late-arriving native marker must split the preceding pulse.
        trace.cast(990, shell=True)
        trace.tick(1001, 125, 100)
        trace.cast(1000)
        trace.cast(1050)
        trace.tick(1051, 200, 180)
        trace.tick(1051, 250, 200)
        trace.tick(1070, 75, 5)
        trace.tick(1400, damage=60, damageeff=45)
        trace.cast(2000)
        groups = trace.groups(0, 3000, 400, immediate=True, ticks_per_cast=4)
        self.assertEqual([cast.replay() for cast in groups], [
            {"start": 1000, "end": 1001, "ticks": 1},
            {"start": 1050, "end": 1400, "ticks": 2},
            {"start": 2000, "end": 2000, "ticks": 0}])
        self.assertEqual((groups[1].heal, groups[1].healeff,
                          groups[1].damage, groups[1].damageeff), (525, 385, 60, 45))

    def test_off_gcd_channel_counts_eligible_starts_and_pulses_independently(self):
        trace = HealingChannel()
        trace.tick(100)  # 治疗残段从战前延续进来
        trace.cast(1000)
        trace.tick(1100)
        trace.tick(1600)
        trace.cast(2200)  # 起手在排除时段，第三跳在有效时段
        for time in (2200, 2600, 3200):
            trace.tick(time)
        trace.cast(4000)  # 中断但已确认起手
        casts = trace.groups(0, 5000, 500, immediate=True, ticks_per_cast=4)
        self.assertTrue(casts[0].partial)
        healer = HealerReplay.__new__(HealerReplay)
        healer.bh, healer.startTime = BattleHistory(0, 5000), 0
        healer.bh.badPeriodHealerLog = [[1500, 1], [3000, 0]]
        healer.bh.log["normal"] = [dict(start=200, duration=500), dict(start=3450, duration=400)]
        self.assertEqual(healer.channelUseStats(casts),
                         {"num": 2, "ticks": 3, "delay": 225, "delaySamples": 2})

    def test_dropped_pulse_and_partial_marker_logs(self):
        trace = HealingChannel()
        trace.cast(1000)
        # Muted intermediate pulses do not split a marked channel.
        for t in (1500, 2600, 3070, 8000, 8500, 9000, 9500, 10000):
            trace.tick(t)
        groups = trace.groups(0, 12000, 500, ticks_per_cast=4)
        self.assertEqual([(cast.start, cast.ticks) for cast in groups], [
            (1000, [1500, 2600, 3070]), (7500, [8000, 8500, 9000, 9500]),
            (9500, [10000])])

    def test_channel_buff_keeps_four_delayed_lingsu_ticks_in_one_cast(self):
        trace = HealingChannel()
        trace.cast(7487427)
        # 11/26 一号：日志卡顿，第三跳距第二跳超过两秒，但引导仍在持续。
        for offset in (386, 755, 2882, 3057):
            trace.tick(7487427 + offset)
        trace.finish(7487427 + 3090)
        groups = trace.groups(7487000, 7492000, 437.5, ticks_per_cast=4)
        self.assertEqual([cast.replay() for cast in groups],
                         [{"start": 7487427, "end": 7490484, "ticks": 4}])

    def test_jcl_frames_keep_pulses_through_recorder_stall_and_catchup(self):
        trace = HealingChannel()
        # 11/26 一号回雪：第三、四跳在文件中间隔约四秒，之后一轮
        # 的前两跳却只相差88毫秒。服务器逻辑帧仍按正常间隔增长。
        trace.cast(76178, frame=385536)
        trace.cast(81037, frame=385564)
        for time, frame in ((76183, 385536), (76491, 385541), (76875, 385548),
                            (80877, 385555), (81038, 385564), (81126, 385572),
                            (81239, 385583)):
            trace.tick(time, frame=frame)
        self.assertEqual([cast.replay() for cast in trace.groups(0, 82000, 625, True, 4)],
                         [{"start": 76178, "end": 80877, "ticks": 4},
                          {"start": 81037, "end": 81239, "ticks": 3}])

    def test_effect_only_log_and_clipped_open_exclusions(self):
        trace = HealingChannel()
        for time in (300, 320, 600):
            trace.tick(time)
        log, _ = trace.intervals(0, 1000, 300)
        self.assertEqual(log, [[0, 1], [600, 0], [1000, 0]])
        battle = BattleHistory(0, 1000)
        battle.log["normal"] = [{"start": 200, "duration": 300}]
        battle.badPeriodHealerLog = [[-100, 1], [100, 0], [800, 1]]
        result = channel_efficiencies(battle, log)
        self.assertAlmostEqual(result["efficiency"], 300 / 700)
        self.assertAlmostEqual(result["efficiencyNonGcd"], 500 / 700)
        battle.badPeriodHealerLog = [[-500, 0], [800, 1], [1600, 0]]
        battle.log["normal"] = [{"start": -100, "duration": 1500}]
        self.assertEqual(channel_efficiencies(battle, log), {"efficiency": 1, "efficiencyNonGcd": 1})
        battle.badPeriodHealerLog = [[0, 1]]
        self.assertEqual(channel_efficiencies(battle, log), {"efficiency": 0, "efficiencyNonGcd": 0})

    def test_distinct_labels_in_personal_header_and_skill_table(self):
        from tests.test_qt_results import QApplication, BattleViewTests, fixture, cells
        if QApplication is None:
            self.skipTest("PySide6 is required")
        from PySide6.QtWidgets import QLabel, QTableView, QVBoxLayout, QWidget
        BattleViewTests.setUpClass()
        from window.QtResults import BattleView
        actor = fixture()
        actor.occResult['云裳乙']['result']['skill']['general'].update(efficiency=.2, efficiencyNonGcd=.8)
        view = BattleView(actor)
        self.addCleanup(view.deleteLater)
        view.open_player('云裳乙')
        text = [label.text() for label in view.findChildren(QLabel)]
        for value in ('仅GCD效率', '战斗效率', '20%', '80%'):
            self.assertIn(value, text)
        details = QWidget()
        self.addCleanup(details.deleteLater)
        view._skills(QVBoxLayout(details))
        metrics = cells(details.findChild(QTableView))
        self.assertIn('仅GCD效率', str(metrics))
        self.assertIn('战斗效率', str(metrics))

    def test_overlapping_casts_bracketing_multiple_exclusions(self):
        battle = BattleHistory(0, 100)
        battle.badPeriodHealerLog = [[28, 1], [54, 0], [72, 1]]
        battle.log["normal"] = [dict(start=s, duration=d) for s, d in
                                [(2, 30), (-4, 29), (65, 25), (28, 26), (46, 44), (44, 12), (1, 33)]]
        self.assertEqual(channel_efficiencies(battle, [[0, 1]]), {"efficiency": 1, "efficiencyNonGcd": 1})

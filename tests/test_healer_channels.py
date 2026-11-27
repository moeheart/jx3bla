import unittest

from replayer.BattleHistory import BattleHistory
from replayer.occ.HealingChannel import HealingChannel, channel_efficiencies


class HealerChannelTests(unittest.TestCase):
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
        trace.cast(1004)
        for time in (1006, 1021, 1390, 1410, 1710, 1715):
            trace.tick(time)
        trace.cast(3000)  # interrupted before a tick, still triggers 吉光 GCD
        log, starts = trace.intervals(0, 5000, 750, immediate=True, ticks_per_cast=4)
        self.assertEqual(starts, [1000, 3000])
        self.assertEqual(log, [[0, 0], [1000, 1], [1710, 0], [5000, 0]])

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

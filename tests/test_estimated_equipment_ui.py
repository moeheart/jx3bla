"""Hidden Tk checks for estimated attributes without presenting them as gear."""
from copy import deepcopy
from types import SimpleNamespace
import tkinter as tk
import unittest
from unittest.mock import patch

from equip.EquipmentFallback import EQUIPMENT_FALLBACK_WARNING
from replayer.TableConstructor import TableConstructor
from window.CombatTrackerWindow import CombatTrackerWindow
from window.DpsDisplayWindow import DpsDisplayWindow
from window.HealerDisplayWindow import HealerDisplayWindow
from window.SpecificBossWindow import SpecificBossWindow


def labels(widget):
    result = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Label):
            result.append(child)
        result.extend(labels(child))
    return result


def estimated_status(mixed=False):
    status = {"status": "estimated", "estimatedPlayers": {"player": {"samples": 2}},
              "warning": EQUIPMENT_FALLBACK_WARNING}
    if mixed:
        status.update(status="incomplete", reason="部分受击目标缺少当前防御数据。")
    return status


class EstimatedEquipmentWindowTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        original = tk.Toplevel

        def hidden_window(*args, **kwargs):
            window = original(*args, **kwargs)
            window.withdraw()
            return window

        self.patch = patch("tkinter.Toplevel", side_effect=hidden_window)
        self.patch.start()
        self.addCleanup(self.root.destroy)
        self.addCleanup(self.patch.stop)

    def boss(self, status):
        window = SpecificBossWindow.__new__(SpecificBossWindow)
        window.detail = {"attributeStatus": status}
        window.mask = 0
        window.bh = SimpleNamespace()
        window.act = SimpleNamespace(rdpsStatus=status)
        window.constructWindow("田承嗣", "900x300")
        return window

    def boss_row(self, window, healer=False, estimated=True):
        frame = tk.Frame(window.window)
        frame.pack()
        table = TableConstructor(None, frame)
        window.constructCommonHeader(table)
        table.EndOfLine()
        window.constructCommonLine(table, {
            "name": "玩家", "occ": "5h" if healer else "4p", "rdps": 1234,
            "ndps": 987, "hps": 321, "score": 88, "rdpsRank": 99, "scoreRank": 90,
            "rdpsStatus": window.detail["attributeStatus"]["status"],
            "equipmentEstimated": {"samples": 2} if estimated else None,
            "equip": {"score": "", "sketch": "", "forge": ""},
        })
        return {int(label.grid_info()["column"]): label.cget("text")
                for label in frame.winfo_children()
                if int(label.grid_info()["row"]) == 1}

    def test_estimated_boss_retains_rdps_and_hides_rank(self):
        window = self.boss(estimated_status())
        row = self.boss_row(window)
        self.assertEqual(row[0], "玩家*")
        self.assertEqual(row[1], "1234")
        self.assertEqual(row[2], "仅供参考")
        self.assertIn(EQUIPMENT_FALLBACK_WARNING,
                      [label.cget("text") for label in labels(window.window)])
        self.assertEqual(window.window.state(), "withdrawn")

    def test_mixed_boss_retains_other_calibration_warning(self):
        status = estimated_status(mixed=True)
        window = self.boss(status)
        row = self.boss_row(window, healer=True, estimated=False)
        self.assertEqual(row[0], "玩家")
        self.assertEqual(row[1], "88")
        self.assertEqual(row[2], "仅供参考")
        banner = "\n".join(label.cget("text") for label in labels(window.window))
        self.assertIn(EQUIPMENT_FALLBACK_WARNING, banner)
        self.assertIn(status["reason"], banner)

    def test_incomplete_without_estimate_keeps_measured_metric(self):
        window = self.boss({"status": "incomplete", "reason": "属性待校准"})
        row = self.boss_row(window, estimated=False)
        self.assertEqual(row[1], "987")
        self.assertEqual(row[2], "待校准")

    def tracker(self, status):
        def metric(healing=False):
            player = {"name": "玩家", "occ": "4p", "sumPerSec": 1234,
                      "sumTime": 10000, "effectiveTime": 10000, "adjustedTime": 10000,
                      "namedSkill": {"攻击": {"num": 1, "sum": 12340, "percent": 1}},
                      "namedSource": {}, "namedTarget": {}}
            player["hps" if healing else "dps"] = 1234
            return {"player": {"player": player}}

        act = SimpleNamespace(time=10000, rdpsStatus=status)
        for stat in ("rhps", "hps", "ahps", "ohps", "chps", "rdps", "ndps", "mrdps", "mndps"):
            data = metric(stat.endswith("hps"))
            if stat in ("rdps", "mrdps"):
                data.update(deepcopy(status))
            setattr(act, stat, data)
        window = CombatTrackerWindow(act)
        window.loadWindow()
        return window

    def test_tracker_keeps_values_details_and_warning_when_switching_stats(self):
        window = self.tracker(estimated_status(mixed=True))
        for stat in ("rdps", "mrdps"):
            window.setStat(stat)
            self.assertIn("仅供参考", window.rightTitle.cget("text"))
            self.assertEqual(window.bars[0][2].cget("text"), "1234")
            self.assertEqual(window.table[0][0].cget("text"), "攻击")
            self.assertEqual(window.table[0][2].cget("text"), "12340")
        window.setStat("ndps")
        self.assertEqual(window.rightTitle.cget("text"), "nDPS")
        self.assertIn(EQUIPMENT_FALLBACK_WARNING, window.attributeWarningLabel.cget("text"))
        self.assertIn("缺少当前防御数据", window.attributeWarningLabel.cget("text"))
        self.assertEqual(window.window.state(), "withdrawn")
        self.root.update_idletasks()
        self.assertLessEqual(window.attributeWarningLabel.winfo_reqheight(), 60)

    def test_failed_equipment_views_keep_warning_inside_the_panel(self):
        for cls, width in ((DpsDisplayWindow, 200), (HealerDisplayWindow, 170)):
            with self.subTest(window=cls.__name__):
                window = cls.__new__(cls)
                window.window = tk.Toplevel()
                window.themeColor = "#0000ff"
                window.result = {"equip": {"available": 0}}
                window.renderEquipment()
                self.root.update_idletasks()
                notices = [label for label in labels(window.window)
                           if EQUIPMENT_FALLBACK_WARNING in label.cget("text")]
                self.assertEqual(len(notices), 1)
                self.assertLessEqual(notices[0].winfo_reqwidth(), width)
                self.assertLessEqual(notices[0].winfo_reqheight(), 230)
                self.assertEqual(window.result["equip"]["available"], 0)
                self.assertEqual(window.window.state(), "withdrawn")

    def test_complete_equipment_detail_still_marks_team_rdps_as_reference(self):
        status = estimated_status(mixed=True)
        overall = {"edition": "test", "playerID": "玩家", "server": "正式服",
                   "battleTimePrint": "2026-11-02", "generateTimePrint": "2026-11-03",
                   "map": "25人普通洛阳之战", "boss": "田承嗣", "sumTimePrint": "10秒",
                   "dataType": "JCL", "attributeStatus": status}
        for cls in (DpsDisplayWindow, HealerDisplayWindow):
            with self.subTest(window=cls.__name__):
                window = cls.__new__(cls)
                window.window = tk.Toplevel()
                window.themeColor = "#0000ff"
                window.config = None
                window.result = {"overall": deepcopy(overall), "equip": {"available": 1}}
                with patch("replayer.TableConstructor.ToolTip") as tips:
                    window.renderOverall()
                self.root.update_idletasks()
                notices = [label for label in labels(window.window) if label.cget("text") == "JCL/rDPS参考"]
                self.assertEqual(len(notices), 1)
                self.assertEqual(notices[0].cget("fg"), "#995500")
                self.assertLessEqual(notices[0].winfo_reqwidth(), 130)
                hint = tips.call_args.args[1]
                self.assertIn(EQUIPMENT_FALLBACK_WARNING, hint)
                self.assertIn(status["reason"], hint)
                self.assertEqual(window.result["equip"]["available"], 1)

    def test_incomplete_without_estimates_marks_personal_views(self):
        status = {"status": "incomplete", "reason": "该心法缺少可用装备样本。"}
        overall = {"edition": "test", "playerID": "玩家", "server": "正式服",
                   "battleTimePrint": "2026-11-02", "generateTimePrint": "2026-11-03",
                   "map": "25人普通洛阳之战", "boss": "田承嗣", "sumTimePrint": "10秒",
                   "dataType": "JCL", "attributeStatus": status}
        for cls in (DpsDisplayWindow, HealerDisplayWindow):
            with self.subTest(window=cls.__name__):
                window = cls.__new__(cls)
                window.window = tk.Toplevel()
                window.themeColor = "#0000ff"
                window.config = None
                window.result = {"overall": deepcopy(overall)}
                with patch("replayer.TableConstructor.ToolTip") as tips:
                    window.renderOverall()
                self.assertIn("JCL/rDPS待校准", [label.cget("text") for label in labels(window.window)])
                self.assertIn(status['reason'], tips.call_args.args[1])

    def test_unreliable_score_is_explicitly_reference_even_with_stale_rank(self):
        for status in (estimated_status(), {"status": "incomplete"}):
            with self.subTest(status=status):
                window = HealerDisplayWindow.__new__(HealerDisplayWindow)
                window.window = tk.Toplevel()
                window.themeColor = "#0000ff"
                window.result = {"overall": {"attributeStatus": status}, "review": {"score": 88, "num": 0}}
                window.rank = {"review": {"score": {"num": 100, "percent": 99}}}
                with patch("window.HealerDisplayWindow.ToolTip") as tips, \
                        patch("window.HealerDisplayWindow.ReviewerWindow"):
                    window.renderRate()
                self.assertIn("参考评分：", [label.cget("text") for label in labels(window.window)])
                self.assertEqual(tips.call_args.args[1], "仅供参考，不参与正式排名。")


if __name__ == "__main__":
    unittest.main()

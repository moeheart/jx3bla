"""Settings path discovery must not save failed results or create a Tk window."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from ServerAddress import FALLBACK_ADDRESS

# Constants resolves the address service at import time; this UI unit test is offline.
with patch("ServerAddress.get_address_config", return_value=deepcopy(FALLBACK_ADDRESS)):
    from window.ConfigWindow import ConfigWindow


class EntryFixture:
    def __init__(self, value):
        self.value = value
        self.options = {"values": ("旧候选角色",)}

    def get(self):
        return self.value

    def delete(self, start, end):
        self.value = ""

    def insert(self, index, value):
        self.value = value

    def __getitem__(self, key):
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value


class ConfigPathLookupTests(unittest.TestCase):
    def setUp(self):
        self.window = ConfigWindow.__new__(ConfigWindow)
        self.window.config = SimpleNamespace(item={
            "general": {
                "playername": "已保存角色",
                "jx3path": r"C:\SavedGame",
                "basepath": r"C:\SavedLogs",
                "datatype": "jx3dat",
                "team": "保留的团队名",
            },
            "user": {"id": "保留的用户"},
        }, printSettings=Mock())
        self.saved_config = deepcopy(self.window.config.item)
        self.original_basepath = r"D:\ManualLogs"
        self.entries = {
            "playername": EntryFixture("当前角色"),
            "jx3path": EntryFixture(r"D:\CurrentGame"),
            "basepath": EntryFixture(self.original_basepath),
        }
        self.datatype = "jcl"
        self.window.frameInfo = {"Frame1": {
            name: {"entry": entry} for name, entry in self.entries.items()
        }}
        self.window.frameInfo["Frame1"]["datatype"] = {
            "var": SimpleNamespace(get=lambda: self.datatype),
        }
        lookup_patch = patch("window.ConfigWindow.FileLookUp")
        warning_patch = patch("window.ConfigWindow.messagebox.showwarning")
        self.lookup = lookup_patch.start().return_value
        self.warning = warning_patch.start()
        self.addCleanup(lookup_patch.stop)
        self.addCleanup(warning_patch.stop)
        self.players = ["最近角色", "当前角色"]
        self.lookup.getAllPlayers.return_value = self.players
        self.real_directory = str(Path(__file__).resolve().parent)

    def assert_unsaved(self):
        self.assertEqual(self.window.config.item, self.saved_config)
        self.window.config.printSettings.assert_not_called()

    def assert_players_refreshed(self):
        self.lookup.getAllPlayers.assert_called_once_with()
        self.assertEqual(list(self.entries["playername"]["values"]), self.players)

    def test_success_uses_current_controls_and_only_replaces_displayed_path(self):
        self.lookup.initFromConfig.return_value = self.real_directory

        self.window.get_path()

        self.lookup.initFromConfig.assert_called_once()
        temporary_config = self.lookup.initFromConfig.call_args.args[0]
        self.assertIsNot(temporary_config, self.window.config)
        general = temporary_config.item["general"]
        self.assertIsNot(general, self.window.config.item["general"])
        self.assertEqual(general["playername"], "当前角色")
        self.assertEqual(general["jx3path"], r"D:\CurrentGame")
        self.assertEqual(general["basepath"], "")
        self.assertEqual(general["datatype"], "jcl")
        self.assertEqual(self.entries["basepath"].get(), self.real_directory)
        self.assertEqual(self.entries["playername"].get(), "当前角色")
        self.assert_players_refreshed()
        self.warning.assert_not_called()
        self.assert_unsaved()

    def test_missing_player_warns_instead_of_accepting_current_directory(self):
        self.entries["playername"].value = ""
        self.lookup.initFromConfig.return_value = "."

        self.window.get_path()

        self.assertEqual(self.entries["basepath"].get(), self.original_basepath)
        self.assertEqual(self.entries["playername"].get(), "")
        self.assert_players_refreshed()
        self.warning.assert_called_once()
        self.assert_unsaved()

    def test_invalid_results_keep_manual_path_and_refresh_role_choices(self):
        missing_directory = str(Path(self.real_directory) / "missing-path-lookup-fixture")
        self.assertFalse(Path(missing_directory).exists())
        for result in ("", "查找角色失败，请检查记录者角色名是否正确。",
                       missing_directory, str(Path(__file__).resolve())):
            with self.subTest(result=result):
                self.lookup.reset_mock()
                self.warning.reset_mock()
                self.lookup.initFromConfig.return_value = result

                self.window.get_path()

                self.assertEqual(self.entries["basepath"].get(), self.original_basepath)
                self.assert_players_refreshed()
                self.warning.assert_called_once()
                self.assert_unsaved()

    def test_new_attempt_uses_edited_controls_after_a_failed_lookup(self):
        self.lookup.initFromConfig.return_value = "自动读取剑三路径失败。"
        self.window.get_path()
        self.entries["jx3path"].value = r"E:\CorrectedGame"
        self.entries["playername"].value = "重新选择的角色"
        self.datatype = "jx3dat"
        self.lookup.initFromConfig.return_value = self.real_directory

        self.window.get_path()

        general = self.lookup.initFromConfig.call_args.args[0].item["general"]
        self.assertEqual(general["jx3path"], r"E:\CorrectedGame")
        self.assertEqual(general["playername"], "重新选择的角色")
        self.assertEqual(general["datatype"], "jx3dat")
        self.assertEqual(general["basepath"], "")
        self.assertEqual(self.entries["basepath"].get(), self.real_directory)
        self.assertEqual(self.entries["playername"].get(), "重新选择的角色")
        self.warning.assert_called_once()
        self.assert_unsaved()


if __name__ == "__main__":
    unittest.main()

"""Regression coverage for offline first use and Qt settings editing."""
import os
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ConfigTools import Config, ensure_user_uuid

try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QDialogButtonBox, QLineEdit, QSpinBox
    from window.QtSettings import LicenseDialog, SettingsDialog, load_desktop_config
except ModuleNotFoundError as error:
    if error.name != "PySide6":
        raise
    QApplication = None


class OfflineConfigTests(unittest.TestCase):
    def test_downloaded_channel_report_opens_with_current_server_ranks(self):
        from window import ConfigWindow

        panel = Mock()
        panel.entry2_8.get.return_value = "42"
        projected = {"overall": {"playerID": "小'云"}, "skill": {"dgsn": {"HPS": 90}, "dgsnCast": {"num": 12}},
                     "rank": {"dgsnCast": {"num": {"num": 0, "percent": 0}}}}
        old = {"overall": {}, "skill": {"dgsn": {"num": 198}}}
        for raw, ranks, expected in ((projected, {"dgsnCast": {"num": {"num": 20, "percent": 42}}}, 12),
                                     (old, {"dgsn": {"num": {"num": 20, "percent": 42}}}, 198)):
            reply = {"available": 1, "text": "请求成功", "raw": json.dumps(raw), "rank": json.dumps(ranks)}
            with self.subTest(expected=expected), patch.object(ConfigWindow, "get_api_url", return_value="offline"), \
                    patch.object(ConfigWindow.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(reply).encode())), \
                    patch.object(ConfigWindow, "LingSuWindow") as viewer:
                ConfigWindow.ConfigWindow.show_replay(panel)
                viewer.return_value.start.assert_called_once_with()
                report = viewer.call_args.args[1]
                self.assertEqual(report["result"]["skill"]["dgsn"]["num"], expected)
                self.assertEqual(report["rank"]["dgsn"]["num"]["percent"], 42)
                self.assertNotIn("dgsnCast", report["result"].get("rank", {}))

    def test_gbk_unicode_percent_and_unknown_settings_survive_incremental_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chosen-settings.ini"
            path.write_bytes("[General]\nteam=原团队\nCaseKey=80%\n[Extension]\nExtra=未知字段\n".encode("gbk"))
            with patch("ConfigTools.request_user_uuid", side_effect=AssertionError("offline")):
                config = Config(path, offline=True)
                self.assertEqual(config.item["general"]["team"], "原团队")
                config.saveSettings({"general": {"team": "新团队"}})
                actual = path.read_text("utf-8")
                self.assertIn("CaseKey=80%", actual)
                self.assertIn("Extra=未知字段", actual)
                self.assertEqual(Config(path, offline=True).item["general"]["team"], "新团队")

    def test_legacy_healer_stacking_setting_is_retired_on_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.ini"
            path.write_text("[LingSuAnalysis]\nStack=3\n[Extension]\nStack=keep\n", encoding="utf-8")
            config = Config(path, offline=True)
            self.assertNotIn("stack", config.item["lingsu"])
            config.saveSettings({"general": {"team": "test"}})
            self.assertNotIn("Stack=3", path.read_text("utf-8"))
            self.assertIn("Stack=keep", path.read_text("utf-8"))

    def test_failed_atomic_replace_keeps_both_config_and_original_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"settings.ini"
            path.write_text("[General]\nteam=before\n", encoding="utf-8")
            config = Config(path, offline=True)
            with patch("ConfigTools.os.replace", side_effect=PermissionError("busy")), self.assertRaises(PermissionError):
                config.saveSettings({"general": {"team": "after"}})
            self.assertEqual(config.item["general"]["team"], "before")
            self.assertEqual(path.read_text("utf-8"), "[General]\nteam=before\n")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_two_config_objects_share_the_online_identity_and_unrelated_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            first, second = Config(path, offline=True), Config(path, offline=True)
            with patch("ConfigTools.request_user_uuid", return_value="sample-id") as request:
                self.assertEqual(ensure_user_uuid(first), "sample-id")
                second.saveSettings({"general": {"team": "second"}})
                self.assertEqual(ensure_user_uuid(second), "sample-id")
            request.assert_called_once_with()
            self.assertEqual(Config(path, offline=True).item["general"]["team"], "second")


@unittest.skipUnless(QApplication, "Qt desktop dependencies required")
class SettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "config.ini"
        self.config = load_desktop_config(self.path)

    def dialog(self):
        result = SettingsDialog(self.config)
        self.addCleanup(result.deleteLater)
        result.show()
        return result

    def wait_for(self, condition):
        for _ in range(200):
            self.app.processEvents()
            if condition():
                return
            QTest.qWait(5)
        self.fail("Qt worker did not complete")

    def test_license_requires_explicit_check(self):
        dialog = LicenseDialog()
        button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        self.assertFalse(button.isEnabled())
        dialog.findChild(QCheckBox).setChecked(True)
        self.assertTrue(button.isEnabled())
        dialog.reject()
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)

    def test_reject_leaves_inputs_and_saved_file_untouched(self):
        before = self.path.read_bytes()
        dialog = self.dialog()
        dialog.findChild(QLineEdit, "general.team").setText("draft")
        dialog.findChild(QCheckBox, "general.autoupload").setChecked(False)
        dialog.reject()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.config.item["general"]["team"], "")
        self.assertEqual(self.config.item["general"]["autoupload"], 1)

    def test_saved_fields_include_per_healer_settings_and_preserve_external_edits(self):
        dialog = self.dialog()
        dialog.findChild(QCheckBox, "general.autoupload").setChecked(False)
        dialog.findChild(QCheckBox, "lijing.public").setChecked(False)
        spin = dialog.findChild(QSpinBox, "lingsu.speed")
        spin.setValue(-20)
        self.assertEqual(spin.value(), 0)
        spin.setValue(18000)
        self.path.write_text(self.path.read_text("utf-8") + "\n[OtherModule]\nMixedCase=100%\n", encoding="utf-8")
        dialog.accept()
        saved = Config(self.path, offline=True)
        self.assertEqual(saved.item["general"]["autoupload"], 0)
        self.assertEqual(saved.item["lijing"]["public"], 0)
        self.assertEqual(saved.item["lingsu"]["speed"], 18000)
        self.assertIn("MixedCase=100%", self.path.read_text("utf-8"))
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_user_information_is_lazy_and_runs_off_the_gui_thread(self):
        import threading
        self.config.saveSettings({"user": {"uuid": "sample", "id": "name"}})
        gui = threading.get_ident()
        def respond(endpoint, **fields):
            self.assertNotEqual(threading.get_ident(), gui)
            self.assertEqual((endpoint, fields), ("/getUserInfo", {"uuid": "sample"}))
            return {"exist": 1, "exp": 40, "lvl": 0, "score": 7}
        with patch("window.QtSettings._account_request", side_effect=respond) as request:
            dialog = self.dialog()
            request.assert_not_called()
            dialog.tabs.setCurrentIndex(dialog.account_tab)
            self.wait_for(lambda: "account" not in dialog.jobs)
            self.assertEqual(dialog.user_status.text(), "用户标识有效。")
            self.assertFalse(hasattr(dialog, "level_up"))
            dialog.reject()

    def test_binding_is_deferred_until_saved_and_only_persists_accepted_name(self):
        self.config.saveSettings({"user": {"uuid": "sample"}})
        with patch("window.QtSettings._account_request", side_effect=[{"result":"dupid"},{"result":"success"}]) as request:
            dialog = self.dialog()
            dialog.username.setText("bound")
            request.assert_not_called()
            dialog.accept()
            self.wait_for(lambda: "save_user" not in dialog.jobs)
            self.assertIn("已被使用", dialog.status.text())
            self.assertEqual(Config(self.path, offline=True).userId, "")
            dialog.username.setText("available")
            dialog.accept()
            self.wait_for(lambda: "save_user" not in dialog.jobs)
            self.assertEqual(Config(self.path, offline=True).userId, "available")
            self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_missing_online_identity_is_replaced_only_after_saving(self):
        self.config.saveSettings({"user": {"uuid": "old", "id": "previous"}})
        with patch("window.QtSettings._account_request", return_value={"exist": 0}), \
                patch("ConfigTools.request_user_uuid", return_value="renewed") as create:
            for save in (False, True):
                dialog = self.dialog()
                dialog.tabs.setCurrentIndex(dialog.account_tab)
                self.wait_for(lambda: "account" not in dialog.jobs)
                self.assertTrue(dialog.make_uuid.isVisible())
                dialog.make_uuid.setChecked(True)
                if save:
                    dialog.accept()
                    self.wait_for(lambda: "save_user" not in dialog.jobs)
                else:
                    dialog.reject()
                    create.assert_not_called()
                    self.assertEqual(Config(self.path, offline=True).userUuid, "old")
            self.assertEqual(self.config.userUuid, "renewed")
            self.assertEqual(Config(self.path, offline=True).userId, "")


if __name__ == "__main__":
    unittest.main()

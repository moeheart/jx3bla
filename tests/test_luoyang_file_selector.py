"""A long progression session must retain its early bosses in manual selection."""
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from FileLookUp import FileLookUp, FileSelector


class FileSelectorTests(unittest.TestCase):
    def test_61_attempts_preserve_first_three_and_sort_os_listing(self):
        with tempfile.TemporaryDirectory() as folder:
            bosses = (["突利和顺(139306)"] * 3 + ["田承嗣(139329)"] * 6 +
                      ["伊曼·寂夜(139319)"] + ["阿史那承庆(139323)"] * 5 +
                      ["煞将(139308)"] * 45 + ["史朝义(139312)"])
            start = datetime(2026, 9, 15, 20)
            names = [(start + timedelta(minutes=i)).strftime("%Y-%m-%d-%H-%M-%S") +
                     "-25人普通洛阳之战(835)-" + boss + ".jcl"
                     for i, boss in enumerate(bosses)]
            for name in reversed(names):
                (Path(folder) / name).touch()
            (Path(folder) / "unrelated.json").touch()
            selected = FileSelector.GetOptions(SimpleNamespace(basepath=folder, dataType="jcl"))
            self.assertEqual(selected, names)

    def _files(self, folder, date, hour=20, map_name="25人普通洛阳之战(835)"):
        names = ["%s-%02d-%02d-00-%s-%s.jcl" % (date, hour, i, map_name, boss)
                 for i, boss in enumerate(("突利和顺(139306)", "田承嗣(139329)",
                                            "伊曼·寂夜(139319)", "阿史那承庆(139323)", "史朝义(139312)"))]
        for name in names:
            (Path(folder) / name).touch()
        return names

    def test_auto_latest_batch_excludes_previous_day_and_other_map(self):
        with tempfile.TemporaryDirectory() as folder:
            self._files(folder, "2026-09-14")
            (Path(folder) / "2026-09-15-19-00-00-25人普通阆风悬城(794)-阿史那承庆(137017).jcl").touch()
            expected = self._files(folder, "2026-09-15")
            lookup = FileLookUp()
            lookup.basepath, lookup.dataType = folder, "jcl"
            latest, attempts, map_name = lookup.getLocalFile()
            self.assertEqual([item[0] for item in attempts], expected)
            self.assertEqual(len(latest), 5)
            self.assertEqual(map_name, "洛阳之战")

    def test_auto_two_runs_same_day_does_not_pull_old_first_boss(self):
        with tempfile.TemporaryDirectory() as folder:
            self._files(folder, "2026-09-15", hour=18)
            expected = self._files(folder, "2026-09-15", hour=20)
            lookup = FileLookUp()
            lookup.basepath, lookup.dataType = folder, "jcl"
            latest, attempts, _ = lookup.getLocalFile()
            self.assertEqual([item[0] for item in attempts], expected)
            self.assertEqual(len(latest), 5)

    def test_explicit_multiday_selection_preserves_user_choices(self):
        with tempfile.TemporaryDirectory() as folder:
            first = self._files(folder, "2026-09-14")
            second = self._files(folder, "2026-09-15")
            lookup = FileLookUp()
            lookup.basepath, lookup.dataType = folder, "jcl"
            lookup.specifyFiles(first + second)
            latest, attempts, _ = lookup.getLocalFile()
            self.assertEqual([item[0] for item in attempts], first + second)
            self.assertEqual(len(latest), 10)


if __name__ == "__main__":
    unittest.main()

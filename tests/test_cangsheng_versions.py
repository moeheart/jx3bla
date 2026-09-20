"""Cangsheng stage boundaries use Beijing time, independent of the host timezone."""
from datetime import datetime, timedelta, timezone
import unittest

from tools.Names import GAMEEDITION_RAW, getGameEditionFromTime, getIDFromMap


BEIJING = timezone(timedelta(hours=8))
LAUNCH = int(datetime(2026, 10, 29, 7, tzinfo=BEIJING).timestamp())
# Scheduled estimate confirmed by the user; update if the actual nerf date moves.
FIRST_NERF_EXPECTED = int(datetime(2026, 12, 21, 7, tzinfo=BEIJING).timestamp())
MAP_IDS = ("828", "835", "836")


class CangshengVersionTests(unittest.TestCase):
    def test_explicit_beijing_timestamps(self):
        self.assertEqual(LAUNCH, 1793228400)
        self.assertEqual(FIRST_NERF_EXPECTED, 1797807600)
        self.assertEqual(datetime.fromtimestamp(LAUNCH, timezone.utc),
                         datetime(2026, 10, 28, 23, tzinfo=timezone.utc))
        self.assertEqual(datetime.fromtimestamp(FIRST_NERF_EXPECTED, timezone.utc),
                         datetime(2026, 12, 20, 23, tzinfo=timezone.utc))

    def test_launch_boundary_for_all_difficulties(self):
        for map_id in MAP_IDS:
            for offset, expected in ((-1, "160"), (0, "161"), (1, "161")):
                with self.subTest(map_id=map_id, offset=offset):
                    self.assertEqual(getGameEditionFromTime(map_id, LAUNCH + offset), expected)

    def test_expected_nerf_boundary_for_all_difficulties(self):
        for map_id in MAP_IDS:
            for offset, expected in ((-1, "161"), (0, "162"), (1, "162")):
                with self.subTest(map_id=map_id, offset=offset):
                    self.assertEqual(getGameEditionFromTime(map_id, FIRST_NERF_EXPECTED + offset), expected)

    def test_stage_labels_and_contiguous_ranges(self):
        expected = (
            ("160", "苍生铸世（测试）", [0, LAUNCH]),
            ("161", "苍生铸世（初版）", [LAUNCH, FIRST_NERF_EXPECTED]),
            ("162", "苍生铸世（一削）", [FIRST_NERF_EXPECTED, 2147483647]),
        )
        for edition, label, period in expected:
            with self.subTest(edition=edition):
                self.assertEqual(GAMEEDITION_RAW[edition], [label, list(MAP_IDS), [period]])
                for map_id in MAP_IDS:
                    self.assertEqual(getGameEditionFromTime(map_id, period[0]), edition)
                    self.assertEqual(getGameEditionFromTime(map_id, period[1] - 1), edition)

    def test_existing_test_logs_and_map_names_still_resolve(self):
        timestamp = int(datetime(2026, 9, 15, 20, 12, 21, tzinfo=BEIJING).timestamp())
        for map_id, difficulty in zip(MAP_IDS, ("10人普通", "25人普通", "25人英雄")):
            with self.subTest(map_id=map_id):
                self.assertEqual(getIDFromMap(difficulty + "洛阳之战"), map_id)
                self.assertEqual(getGameEditionFromTime(map_id, timestamp), "160")

    def test_other_maps_and_outside_time_range_are_unchanged(self):
        for timestamp in (LAUNCH - 1, LAUNCH, FIRST_NERF_EXPECTED):
            self.assertEqual(getGameEditionFromTime("794", timestamp), "152")
            self.assertEqual(getGameEditionFromTime("829", timestamp), "0")
        for map_id in MAP_IDS:
            self.assertEqual(getGameEditionFromTime(map_id, -1), "0")
            self.assertEqual(getGameEditionFromTime(map_id, 2147483647), "0")


if __name__ == "__main__":
    unittest.main()

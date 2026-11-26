"""Delay evidence and atomic publication, without a running database or HTTP service."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch

from replayer.ReplayerBase import RankCalculator
from serverFunc import UpdateReplayRank as refresh
from test_cangsheng_rank_collection import replay_record
from tools.Functions import SkillCounter
from tools import Preload


class DelayPercentileTests(unittest.TestCase):
    def test_unobserved_zero_and_measured_zero_are_distinct(self):
        counter = SkillCounter("1", 0, 10000, 0)
        self.assertEqual(counter.getDelayStats(), {"delay": 0, "delaySamples": 0})
        counter.recordSkill(4000)
        self.assertEqual(counter.getDelayStats(), {"delay": 0, "delaySamples": 0})
        counter.recordSkill(6000, lastTime=5500, delta=500)
        counter.recordSkill(6040, lastTime=5500, delta=500)  # another target
        self.assertEqual(counter.getDelayStats(), {"delay": 0, "delaySamples": 1})
        counter.recordSkill(7000, lastTime=6300, delta=499)
        self.assertEqual(counter.getDelayStats(), {"delay": 100, "delaySamples": 2})
        self.assertEqual(counter.getAverageDelay(), 100.5)

    def test_client_lookup_and_daily_samples_use_the_same_delay(self):
        skills = [
            {"delay": 0, "delaySamples": 0}, {"delay": 0, "num": 3},  # legacy zero is ambiguous
            {"delay": 0, "delaySamples": 2}, {"delay": 100}, {"delay": 200, "delaySamples": 1},
        ]
        records = []
        payloads = {}
        for i, skill in enumerate(skills):
            row = replay_record("8.16.8", "161")
            row[1], row[8] = str(i), i
            records.append(row)
            payloads[i] = {"overall": {"playerID": str(i), "map": row[5], "boss": row[6]}, "skill": {"cast": skill}}
        def read_sample(path, *args, **kwargs):
            return mock_open(read_data=json.dumps(payloads[int(path.rsplit("/", 1)[1])]))()
        with patch.object(refresh, "open", side_effect=read_sample, create=True):
            percentiles = refresh.getPercent(records)
        self.assertEqual(percentiles["lingsu-835-史朝义-cast-delay-161"]["num"], 3)
        self.assertFalse(any("delaySamples" in key for key in percentiles))
        for i, expected in enumerate([(0, -1), (0, -1), (3, 100), (3, 50), (3, 0)]):
            rc = RankCalculator(payloads[i], percentiles, "161")
            result = rc.getRankFromStat("lingsu")["cast"]
            self.assertNotIn("delaySamples", result)
            self.assertEqual((result["delay"]["num"], result["delay"]["percent"]), expected)


class SnapshotTests(unittest.TestCase):
    def test_file_is_read_under_its_committed_rows_lock_and_used_for_both_phases(self):
        row = replay_record("8.16.8", "161")
        row[22] = 500
        payload = {"overall": {"playerID": row[1]}, "skill": {"general": {"rdps": 500}}}
        reader = Mock()
        cursor = reader.cursor.return_value
        cursor.fetchall.side_effect = [[(row[7],), ("removed",)], [row]]
        locked = False

        def execute(statement, params):
            nonlocal locked
            locked = "LOCK IN SHARE MODE" in statement
            if locked:
                self.assertEqual(params[:-1], (row[7], "removed"))

        def unlock():
            nonlocal locked
            locked = False

        def read(locked_row):
            self.assertTrue(locked)
            self.assertIs(locked_row, row)
            return json.dumps(payload)

        cursor.execute.side_effect = execute
        reader.rollback.side_effect = unlock
        with patch.object(refresh, "_read_replay", side_effect=read) as source:
            percentiles, candidates = refresh._collect_snapshot(reader)
            self.assertFalse(locked)
            self.assertEqual(percentiles["lingsu-835-史朝义-general-rdps-161"],
                             percentiles["lingsu-835-史朝义-stat-rdps-161"])
            refresh.updatePercent(percentiles, Mock(), candidates)
            source.assert_called_once_with(row)

    def test_read_failure_releases_share_locks_and_propagates(self):
        reader = Mock()
        row = replay_record("8.16.8", "161")
        reader.cursor.return_value.fetchall.side_effect = [[(row[7],)], [row]]
        with patch.object(refresh, "_read_replay", side_effect=OSError("read failed")):
            with self.assertRaisesRegex(OSError, "read failed"):
                refresh._collect_snapshot(reader)
        self.assertEqual(reader.rollback.call_count, 2)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.cursor = self.db.cursor.return_value
        self.previous = "9999999999"
        self.entries = {"a": {"num": 2, "value": "[0]"}, "b": {"num": 2, "value": "[1]"}}
        self.cursor.fetchall.side_effect = [
            [("ReplayProStat", "InnoDB"), ("PreloadInfo", "InnoDB"), ("ReplayProStatRank", "InnoDB")],
        ]
        self.cursor.fetchone.side_effect = [(1,), (2, 8), (self.previous,)]
        self.open_url = self.enterPatch(patch.object(refresh.urllib.request, "urlopen",
                                                     return_value=io.BytesIO(b'{"result":"success"}')))
        self.calculate = self.enterPatch(patch.object(refresh, "_collect_snapshot", return_value=(self.entries, [])))
        self.enterPatch(patch.object(refresh.pymysql, "connect", side_effect=[self.db, Mock()]))
        self.enterPatch(patch.object(refresh, "open", mock_open(read_data="[jx3bla]\nusername=u\npassword=p"), create=True))

    def enterPatch(self, patcher):
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def test_complete_publication_commits_before_notification(self):
        self.open_url.side_effect = lambda *a, **kw: self._after_commit()
        refresh.RefreshStat()
        self.db.rollback.assert_not_called()
        self.cursor.execute.assert_called_with(
            "INSERT INTO PreloadInfo (datakey, datavalue) VALUES ('rateEdition', %s)", ("10000000000",))
        self.open_url.assert_called_once()

    def _after_commit(self):
        self.db.commit.assert_called_once_with()
        self.db.close.assert_called_once_with()
        return io.BytesIO(b'{"result":"success"}')

    def test_failed_insert_never_advances_version_or_refreshes(self):
        self.cursor.executemany.side_effect = ValueError("second insert failed")
        with self.assertRaisesRegex(ValueError, "second insert failed"):
            refresh.RefreshStat()
        self.db.rollback.assert_called_once_with()
        self.db.commit.assert_not_called()
        self.open_url.assert_not_called()
        self.assertFalse(any("DELETE FROM PreloadInfo" in c.args[0] for c in self.cursor.execute.call_args_list))

    def test_empty_population_preserves_previous_table(self):
        self.calculate.return_value = {}, []
        with self.assertRaisesRegex(ValueError, "No eligible"):
            refresh.RefreshStat()
        self.db.rollback.assert_called_once_with()
        self.assertFalse(any("DELETE FROM ReplayProStatRank" in c.args[0] for c in self.cursor.execute.call_args_list))
        self.open_url.assert_not_called()

    def test_truncated_values_roll_back_and_skip_cache_refresh(self):
        self.cursor.fetchone.side_effect = [(1,), (2, 7)]
        with self.assertRaisesRegex(ValueError, "truncated"):
            refresh.RefreshStat()
        self.db.rollback.assert_called_once_with()
        self.db.commit.assert_not_called()
        self.open_url.assert_not_called()

    def test_concurrent_refresh_does_not_publish(self):
        self.cursor.fetchone.side_effect = [(0,)]
        with self.assertRaisesRegex(RuntimeError, "already running"):
            refresh.RefreshStat()
        self.cursor.execute.assert_called_once()
        self.open_url.assert_not_called()

    def test_rejects_nontransactional_storage_before_touching_rank_data(self):
        self.cursor.fetchall.side_effect = [[("ReplayProStat", "InnoDB"), ("PreloadInfo", "MyISAM"),
                                            ("ReplayProStatRank", "InnoDB")]]
        with self.assertRaisesRegex(RuntimeError, "InnoDB"):
            refresh.RefreshStat()
        self.calculate.assert_not_called()
        self.open_url.assert_not_called()


class DownloadVersionTests(unittest.TestCase):
    def test_cache_uses_downloaded_generation_and_reads_legacy_responses(self):
        for response, expected in (({"data": {"new": 1}, "rateEdition": "101"}, "101"),
                                   ({"data": {"new": 1}}, "100")):
            with self.subTest(response=response), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "rate.dat"
                path.write_text(json.dumps({"edition": "99", "data": {"old": 1}}), encoding="utf-8")
                with patch.object(Preload, "get_writable_path", return_value=path), \
                        patch.object(Preload, "get_resource_path", return_value=path), \
                        patch.object(Preload, "get_api_url", return_value="http://example.invalid"), \
                        patch.object(Preload.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(response).encode())):
                    self.assertEqual(Preload.checkRateEdition("100"), {"new": 1})
                self.assertEqual(json.loads(path.read_text())["edition"], expected)


if __name__ == "__main__":
    unittest.main()

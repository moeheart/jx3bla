"""Cangsheng percentile inputs exclude clients predating the calibrated model."""
import json
import unittest
from unittest.mock import Mock, mock_open, patch

from serverFunc.UpdateReplayRank import getSingleStat, isReplayRankEligible, updatePercent
from tools.Functions import parseEdition


def replay_record(edition, game_edition="160", record_hash="sample"):
    row = [None] * 32
    row[0:3] = ["test-server", "test-player", "lingsu"]
    row[5:9] = ["25人普通洛阳之战", "史朝义", record_hash, 1]
    row[10] = edition
    row[11] = parseEdition(edition)
    row[22] = 50
    row[30] = 1
    row[31] = game_edition
    return row


class CangshengRankCollectionTests(unittest.TestCase):
    def test_new_season_requires_8160_for_all_three_stages(self):
        for stage in ("160", "161", "162", 160, 161, 162):
            for client, eligible in (("8.15.5", False), ("8.16.0", True), ("8.16.1", True)):
                with self.subTest(stage=stage, client=client):
                    self.assertEqual(isReplayRankEligible(replay_record(client, stage)), eligible)

    def test_beta_clients_never_enter_percentile_samples(self):
        for stage in ("152", "160", "161", "162"):
            for client in ("8.16.0-beta.2", "8.17.0-beta.1"):
                with self.subTest(stage=stage, client=client):
                    self.assertFalse(isReplayRankEligible(replay_record(client, stage)))

    def test_old_season_keeps_8130_threshold(self):
        for stage in ("0", "130", "143", "152"):
            for client, eligible in (("8.12.9", False), ("8.13.0", True), ("8.15.5", True)):
                with self.subTest(stage=stage, client=client):
                    self.assertEqual(isReplayRankEligible(replay_record(client, stage)), eligible)

    def test_invalid_client_version_is_not_an_eligible_sample(self):
        record = replay_record("8.16.0")
        for client in (None, "", "8.16", "invalid", "8.16.preview"):
            with self.subTest(client=client):
                record[10] = client
                self.assertFalse(isReplayRankEligible(record))

    def test_single_stat_rejects_old_new_season_client_before_open(self):
        with patch("builtins.open", side_effect=AssertionError("Rejected rows must not load replay files")) as reader:
            for stage in ("160", "161", "162"):
                self.assertEqual(getSingleStat(replay_record("8.15.5", stage)), {})
            reader.assert_not_called()

    def test_single_stat_collects_calibrated_new_season_client(self):
        payload = json.dumps({"overall": {"playerID": "test-player"}, "skill": {"general": {"rdps": 50}}})
        for stage in ("160", "161", "162"):
            with self.subTest(stage=stage), patch("builtins.open", mock_open(read_data=payload)):
                result = getSingleStat(replay_record("8.16.0", stage))
                self.assertEqual(result["lingsu-835-史朝义-general-rdps-" + stage], 50)
                self.assertEqual(result["lingsu-835-史朝义-stat-rdps-" + stage], 50)

    def test_percent_updates_skip_old_clients_but_keep_broad_sql(self):
        for stage in ("160", "161", "162"):
            with self.subTest(stage=stage):
                cursor, db = Mock(), Mock()
                cursor.fetchall.return_value = [replay_record("8.15.5", stage, "old"),
                                                replay_record("8.16.0", stage, "calibrated"),
                                                replay_record("8.17.0-beta.1", stage, "beta")]
                table = {"lingsu-835-史朝义-stat-rdps-" + stage: {"value": json.dumps(list(range(101)))}}
                updatePercent(table, cursor, db)
                statements = [call.args[0] for call in cursor.execute.call_args_list]
                self.assertEqual(statements[0], "SELECT * FROM ReplayProStat WHERE editionFull>=8013000 AND hold=1")
                self.assertEqual(statements[1:], ["UPDATE ReplayProStat SET rdpsRank = 50 WHERE hash = 'calibrated'"])
                db.commit.assert_called_once_with()

    def test_percent_updates_still_accept_older_client_for_old_season(self):
        cursor, db = Mock(), Mock()
        record = replay_record("8.13.0", "152", "legacy")
        record[5:7] = ["25人普通阆风悬城", "阿史那承庆"]
        cursor.fetchall.return_value = [record]
        table = {"lingsu-794-阿史那承庆-stat-rdps-152": {"value": json.dumps(list(range(101)))}}
        updatePercent(table, cursor, db)
        self.assertEqual(cursor.execute.call_args.args[0], "UPDATE ReplayProStat SET rdpsRank = 50 WHERE hash = 'legacy'")
        db.commit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

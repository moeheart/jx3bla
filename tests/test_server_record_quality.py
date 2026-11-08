"""End-to-end Flask/SQL contract regressions with fake DB and isolated files."""
import builtins
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, mock_open

import test_server_collection as fixtures
import tools.RecordQuality as quality_module
from tools.RecordQuality import get_record_quality, invalidate_quality_cache


class ServerRecordQualityTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.ServerCollectionTests.setUpClass.__func__)
    setUp = fixtures.ServerCollectionTests.setUp
    replay = fixtures.ServerCollectionTests.replay
    battle = fixtures.ServerCollectionTests.battle

    def status(self, kind):
        return {"status": kind, "staticAttributes": "available" if kind == "supported" else "estimated" if kind == "estimated" else "missing"}

    def row(self, identifier=1, player="same-player", value=50):
        row = [0] * 32
        row[0:4] = ["test-server", player, "lingsu", value]
        row[4:12] = ["2026-11-06", fixtures.MAPS["835"], "史朝义", "hash-%s" % identifier, identifier, 1, "8.16.5", self.server.parseEdition("8.16.5")]
        row[14:17] = [1793952000 + identifier, 1793953000, "battle-id"]
        for metric, index in self.server.STAT_ID.items():
            row[index] = value
            row[self.server.RANK_ID[metric]] = value
        row[30:32] = [1, "161"]
        return row

    def replay_existing(self, payload, previous):
        ordinary = self.cursor.fetchall
        def fetch():
            if "SELECT shortID, public" in self.cursor.last:
                return [(42, 1, payload["editionfull"], 80)]
            return ordinary()
        self.stack.enter_context(patch.object(self.cursor, "fetchall", side_effect=fetch))
        self.stack.enter_context(patch.object(self.server, "load_record_quality", return_value=get_record_quality(previous)))

    def test_upload_ranks_each_measured_value_and_masks_only_sensitive(self):
        for kind in ("supported", "estimated", "incomplete"):
            payload = self.replay()
            payload["statistics"]["overall"]["attributeStatus"] = self.status(kind)
            with self.subTest(kind=kind), patch.object(self.server, "getRankFromKeys", return_value=77) as rank:
                result = self.server.receiveReplay(payload, self.cursor)
                self.assertEqual(result["result"], "success")
                values = {call.args[5]: call.args[0] for call in rank.call_args_list}
                self.assertEqual({key: values[key] for key in ("hps", "rhps", "ndps", "mndps")},
                                 {"hps": 1500, "rhps": 1200, "ndps": 2000, "mndps": 1600})
                row = self.cursor.inserted("ReplayProStat")
                for metric in ("score", "rdps", "mrdps"):
                    self.assertEqual(int(row[self.server.RANK_ID[metric]]), 77 if kind == "supported" else -1)
                self.assertEqual(float(row[self.server.STAT_ID["rdps"]]), 2200)

    def test_battle_json_preserves_apostrophe_quotes_and_unicode(self):
        payload = self.battle()
        payload["statistics"]["attributeStatus"] = {"status": "estimated", "warning": "player's 装备 \"unknown\""}
        with patch.object(self.server, "_write_statistics") as writer:
            self.assertEqual(self.server.receiveBattle(payload, self.cursor)["result"], "success")
        text = writer.call_args.args[1]
        self.assertEqual(json.loads(text), payload["statistics"])
        self.assertEqual(self.server.parse_statistics(text), payload["statistics"])

    def test_get_battle_exports_quality_and_replay_privacy_guard_stays_closed(self):
        data = {"act": {"rdpsStatus": self.status("estimated")}}
        with patch.object(self.cursor, "fetchall", return_value=[("server", "boss", "date", "835", "8.16.5", 1, 2, "161")]), patch.object(self.server, "open", mock_open(read_data=json.dumps(data)), create=True):
            response = self.client.get("/getBattle", query_string={"hash": "test"}).get_json()
        self.assertFalse(response["quality"]["precise"])
        with patch.object(self.cursor, "fetchall", return_value=[(42, 0, "8.16.5", "lingsu", "battle", "161")]), patch.object(self.server, "open", side_effect=AssertionError("private raw must not be read"), create=True):
            response = self.client.get("/getReplayPro", query_string={"id": 42}).get_json()
        self.assertEqual(response["available"], 0)

    def test_same_version_estimated_to_precise_keeps_short_id(self):
        payload = self.replay()
        payload["statistics"]["overall"]["attributeStatus"] = self.status("supported")
        self.replay_existing(payload, self.status("estimated"))
        result = self.server.receiveReplay(payload, self.cursor)
        self.assertEqual((result["result"], result["shortID"]), ("success", 42))
        self.assertFalse(any("ReplayProInfo" in query for query in self.cursor.queries))
        self.assertIn("FOR UPDATE", self.cursor.queries[0])

    def test_precise_cannot_be_downgraded_even_by_new_client(self):
        payload = self.replay()
        self.replay_existing(payload, self.status("supported"))
        payload["editionfull"] += 100
        payload["statistics"]["overall"]["attributeStatus"] = self.status("estimated")
        result = self.server.receiveReplay(payload, self.cursor)
        self.assertEqual(result["result"], "dupid")
        self.assertFalse(any(query.startswith("DELETE") for query in self.cursor.queries))
        self.writer.assert_not_called()

    def test_average_can_upgrade_to_known_static_but_not_downgrade(self):
        payload = self.replay()
        known = {"status": "incomplete", "staticAttributes": "available", "unmodeledEffects": ["atExecuteScript"]}
        self.replay_existing(payload, self.status("estimated"))
        payload["statistics"]["overall"]["attributeStatus"] = known
        self.assertEqual(self.server.receiveReplay(payload, self.cursor)["result"], "success")
        with patch.object(self.server, "load_record_quality", return_value=get_record_quality(known)):
            payload["statistics"]["overall"]["attributeStatus"] = self.status("estimated")
            payload["editionfull"] += 100
            self.assertEqual(self.server.receiveReplay(payload, self.cursor)["result"], "dupid")

    def test_unreadable_previous_file_blocks_downgrade_but_allows_precise_repair(self):
        payload = self.replay()
        self.replay_existing(payload, {"status": "unavailable"})
        payload["statistics"]["overall"]["attributeStatus"] = self.status("estimated")
        self.assertEqual(self.server.receiveReplay(payload, self.cursor)["result"], "dupid")
        payload["statistics"]["overall"]["attributeStatus"] = self.status("supported")
        self.assertEqual(self.server.receiveReplay(payload, self.cursor)["result"], "success")

    def test_battle_same_version_upgrade_and_precise_downgrade(self):
        payload = self.battle()
        previous = ["server", "boss", "date", "835", payload["edition"], payload["hash"], 1, 0, "uuid", 0, payload["time"], "", "161", "team", 600]
        ordinary = self.cursor.fetchall
        def fetch():
            return [previous] if "SELECT * from ActorStat" in self.cursor.last else ordinary()
        with patch.object(self.cursor, "fetchall", side_effect=fetch), patch.object(self.server, "load_record_quality") as quality:
            quality.return_value = get_record_quality(self.status("estimated"))
            payload["statistics"]["attributeStatus"] = self.status("supported")
            self.assertEqual(self.server.receiveBattle(payload, self.cursor)["result"], "success")
            quality.return_value = get_record_quality(self.status("supported"))
            payload["statistics"]["attributeStatus"] = self.status("estimated")
            self.assertEqual(self.server.receiveBattle(payload, self.cursor)["result"], "dupid")

    def test_quality_filter_precedes_dedup_and_pagination_measured_is_kept(self):
        rows = [self.row(1, value=99), self.row(2, value=70), self.row(3, player="other", value=60)]
        def quality(path):
            return get_record_quality(self.status("estimated" if path.endswith("/1") else "supported"))
        with patch.object(self.cursor, "fetchall", return_value=rows), patch.object(self.server, "load_record_quality", side_effect=quality):
            base = {"map": fixtures.MAPS["835"], "boss": "史朝义", "occ": "lingsu", "gameEdition": "161"}
            exact = self.client.get("/getRank", query_string=dict(base, orderby="rdps")).get_json()["result"]
            self.assertEqual([row["shortID"] for row in exact["table"]], [2, 3])
            measured = self.client.get("/getRank", query_string=dict(base, orderby="hps")).get_json()["result"]
            self.assertEqual([row["shortID"] for row in measured["table"]], [1, 3])
            self.assertEqual(measured["table"][0]["hpsRank"], 99)
            self.assertEqual(measured["table"][0]["rdpsRank"], -1)

    def test_battletime_numeric_sort_and_measured_page_reads_at_most_50(self):
        rows = [self.row(index, player=str(index)) for index in range(1, 121)]
        with patch.object(self.cursor, "fetchall", return_value=rows), patch.object(self.server, "load_record_quality", return_value=get_record_quality({})) as reader:
            result = self.client.get("/getRank", query_string={"orderby": "battletime", "page": 1}).get_json()["result"]
            self.assertEqual(result["num"], 120)
            self.assertEqual(result["table"][0]["shortID"], 120)
            self.assertEqual(reader.call_count, 50)

    def test_rank_mode_zero_means_percentile_and_missing_rank_is_omitted(self):
        rows = [self.row(1, value=99), self.row(2, player="other", value=60)]
        rows[0][self.server.RANK_ID["hps"]] = -1
        with patch.object(self.cursor, "fetchall", return_value=rows), patch.object(self.server, "load_record_quality", return_value=get_record_quality({})):
            result = self.client.get("/getRank", query_string={"orderby": "hps", "alltime": "0"}).get_json()["result"]
            self.assertEqual([row["shortID"] for row in result["table"]], [2])

    def test_single_and_bulk_summary_exclude_minus_one_and_estimated_score(self):
        rows = [self.row(1, value=80), self.row(2, value=100)]
        rows[0][self.server.RANK_ID["hps"]] = -1
        def quality(path):
            return get_record_quality(self.status("estimated" if path.endswith("/2") else "supported"))
        with patch.object(self.cursor, "fetchall", return_value=rows), patch.object(self.server, "load_record_quality", side_effect=quality):
            for route in ("/getSinglePlayer", "/getMultiPlayer"):
                result = self.client.get(route, query_string={"server": "server", "id": "p", "ids": "p"}).get_json()["result"]
                if route == "/getMultiPlayer":
                    result = result["p"]
                self.assertEqual(result["stat"]["史朝义"]["average"], 80)
                self.assertEqual(result["stat"]["史朝义"]["num"], 2)
                self.assertEqual(result["stat"]["史朝义"]["eligibleNum"], 1)
                self.assertEqual(result["rank"]["hps"]["overallAverage"], 100)
                self.assertEqual(result["rank"]["score"]["overallAverage"], 80)
        with patch.object(self.server, "load_record_quality", return_value=get_record_quality(self.status("estimated"))):
            result = self.server._summarize_replay_records(rows)
            self.assertIsNone(result["stat"]["overall"]["average"])
            self.assertIsNone(result["rank"]["score"]["overallAverage"])

    def test_percentile_samples_filter_general_stat_but_keep_healer(self):
        row = self.row()
        data = self.replay()["statistics"]
        data["overall"].update(playerID=row[1], attributeStatus=self.status("estimated"))
        data["healer"] = {"table": [{"name": row[1], "heal": 100, "healEff": 90, "hps": 1500}]}
        with patch.object(self.rank, "open", mock_open(read_data=repr(data)), create=True):
            result = self.rank.getSingleStat(row)
        self.assertTrue(any("-general-ndps-" in key for key in result))
        self.assertTrue(any("-stat-hps-" in key for key in result))
        self.assertTrue(any("-healer-healEff-" in key for key in result))
        self.assertFalse(any(any("-" + metric + "-" in key for metric in ("score", "rdps", "mrdps")) for key in result))

    def test_refresh_invalidates_sensitive_existing_ranks_only(self):
        row = self.row()
        cursor, db = Mock(), Mock()
        cursor.fetchall.return_value = [row]
        table = {"lingsu-835-史朝义-stat-hps-161": {"value": json.dumps(list(range(101)))}}
        with patch.object(self.rank, "load_record_quality", return_value=get_record_quality(self.status("estimated"))):
            self.rank.updatePercent(table, cursor, db)
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        for metric in ("score", "rdps", "mrdps"):
            self.assertTrue(any("SET %sRank = -1" % metric in sql for sql in statements))
        self.assertTrue(any("SET hpsRank = 50" in sql for sql in statements))

    def test_rank_calculator_uses_shared_unmodeled_effect_rule(self):
        calculator = self.server.RankCalculator.__new__(self.server.RankCalculator)
        calculator.result = {"overall": {"attributeStatus": {"status": "supported", "staticAttributes": "available", "unmodeledEffects": ["atExecuteScript"]}}}
        calculator.percent_data = {"lingsu-835-史朝义-healer-hps-161": {"num": 5, "value": str(list(range(101)))}}
        calculator.game_edition = "161"
        self.assertEqual(calculator.getSkillPercent("lingsu", "835", "史朝义", "general", "rdps", 50), (0, -1))
        self.assertEqual(calculator.getSkillPercent("lingsu", "835", "史朝义", "healer", "hps", 50), (5, 50))

    def test_same_version_model_upgrade_replaces_values_and_enters_both_rank_modes(self):
        """A modeled replay replaces its old record, not merely its quality flag."""
        payload = self.replay(when=fixtures.INITIAL + 3600)
        payload.update(edition="8.16.6", editionfull=self.server.parseEdition("8.16.6"),
                       replayedition="8.16.6", score=95)
        payload["statistics"]["review"] = {"score": 95}
        payload["statistics"]["skill"]["general"]["score"] = 95
        payload["statistics"]["overall"]["attributeStatus"] = self.status("supported")
        battle = self.battle(when=payload["battletime"])
        battle["edition"] = payload["edition"]
        battle["statistics"].update(attributeStatus=self.status("supported"),
                                    act={"rdpsStatus": self.status("supported")})
        old_status = {"status": "incomplete", "staticAttributes": "available",
                      "unmodeledEffects": ["fixture equipment effect"]}
        previous = copy.deepcopy(payload["statistics"])
        previous["overall"]["attributeStatus"] = old_status
        previous["review"]["score"] = 40
        previous["skill"]["general"].update(score=40, rdps=1800)
        replay_row = self.row(identifier=42, player=payload["id"], value=40)
        replay_row[0:3] = [payload["server"], payload["id"], payload["occ"]]
        replay_row[4:8] = [payload["battledate"], payload["mapdetail"], payload["boss"], payload["hash"]]
        replay_row[10:17] = [payload["edition"], payload["editionfull"], payload["replayedition"],
                             payload["userid"], payload["battletime"], payload["submittime"], payload["battleID"]]
        replay_row[self.server.STAT_ID["rdps"]] = 1800
        for metric in ("score", "rdps", "mrdps"):
            replay_row[self.server.RANK_ID[metric]] = -1
        battle_row = [battle["server"], battle["boss"], battle["battledate"], "835", battle["edition"],
                      battle["hash"], 1, payload["editionfull"], battle["userid"], battle["begintime"],
                      battle["time"], "", "161", battle["team"], battle["length"]]
        state = {"replay": replay_row, "battle": battle_row}
        original_execute, original_fetch = self.cursor.execute, self.cursor.fetchall

        def execute(sql, *args):
            original_execute(sql, *args)
            if sql.startswith("INSERT INTO ReplayProStat "):
                row = self.cursor.inserted("ReplayProStat")
                for index in self.server.STAT_ID.values():
                    row[index] = float(row[index])
                for index in set(self.server.RANK_ID.values()) | {8, 9, 11, 14, 15, 30}:
                    row[index] = int(row[index])
                state["replay"] = row
            elif sql.startswith("INSERT INTO ActorStat "):
                row = self.cursor.inserted("ActorStat")
                for index in (6, 7, 9, 10, 14):
                    row[index] = int(row[index])
                state["battle"] = row

        def fetch():
            if "SELECT shortID, public" in self.cursor.last:
                row = state["replay"]
                return [(row[8], row[9], row[11], row[17])]
            if "SELECT * FROM ReplayProStat" in self.cursor.last:
                return [state["replay"]]
            if "SELECT * from ActorStat" in self.cursor.last:
                return [state["battle"]]
            if "from ScoreInfo" in self.cursor.last:
                return [(1,)]  # The original upload already received its honor.
            return original_fetch()

        query = {"map": payload["mapdetail"], "boss": payload["boss"], "occ": payload["occ"],
                 "gameEdition": "161"}
        combined = {"data": [{"type": "replay", "id": 0, "data": payload},
                              {"type": "battle", "id": 1, "data": battle}]}
        table = {"lingsu-835-史朝义-stat-%s-161" % metric:
                 {"num": 101, "value": json.dumps([index * (100 if metric != "score" else 1)
                                                    for index in range(101)])}
                 for metric in self.server.STAT_ID}
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / ".tmp") as directory, \
                patch.object(self.server, "open", builtins.open), \
                patch.object(self.server, "_atomic_write_statistics", self.real_atomic_writer), \
                patch.object(self.server, "_write_statistics", wraps=self.server._write_statistics) as writer, \
                patch.object(self.cursor, "execute", side_effect=execute), \
                patch.object(self.cursor, "fetchall", side_effect=fetch), \
                patch.object(self.server.app, "percent_data", table):
            try:
                os.chdir(directory)
                replay_path = Path("database/ReplayProStat/42")
                battle_path = Path("database/ActorStat") / battle["hash"]
                for path, data in ((replay_path, previous), (battle_path, {"attributeStatus": old_status})):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(data), encoding="utf-8")
                    self.assertFalse(self.server.load_record_quality(path)["precise"])
                    self.assertIn(str(path.resolve()), quality_module._quality_cache)
                for metric in ("score", "rdps"):
                    response = self.client.get("/getRank", query_string=dict(query, orderby=metric)).get_json()
                    self.assertEqual(response["result"]["num"], 0)

                self.db.reset_mock()
                result = self.client.post("/uploadCombinedData", data={"jdata": json.dumps(combined)}).get_json()
                self.assertEqual(result["status"], "success")
                self.assertEqual([row["result"] for row in result["data"]], ["success", "success"])
                self.assertEqual(result["data"][0]["shortID"], 42)
                self.assertEqual(result["data"][1]["scoreStatus"], "dupid")
                self.db.commit.assert_called_once_with()
                self.db.rollback.assert_not_called()
                self.assertEqual(writer.call_count, 2)
                self.assertFalse(any("from ReplayProInfo" in sql for sql in self.cursor.queries))
                for path in (replay_path, battle_path):
                    self.assertNotIn(str(path.resolve()), quality_module._quality_cache)
                    self.assertTrue(self.server.load_record_quality(path)["precise"])
                saved = json.loads(replay_path.read_text(encoding="utf-8"))
                self.assertEqual(saved["review"]["score"], 95)
                self.assertEqual(saved["skill"]["general"]["rdps"], 2200)
                self.assertEqual(state["replay"][3], 95)
                self.assertEqual(state["replay"][22], 2200)
                for metric in ("score", "rdps"):
                    for alltime in ("1", "0"):
                        response = self.client.get("/getRank", query_string=dict(query, orderby=metric, alltime=alltime)).get_json()
                        rows = response["result"]["table"]
                        self.assertEqual([row["shortID"] for row in rows], [42])
                        self.assertEqual(rows[0][metric], payload["score"] if metric == "score" else 2200)
                        self.assertGreaterEqual(rows[0][metric + "Rank"], 0)

                saved_bytes = {path: path.read_bytes() for path in (replay_path, battle_path)}
                self.cursor.queries.clear()
                result = self.client.post("/uploadCombinedData", data={"jdata": json.dumps(combined)}).get_json()
                self.assertEqual([row["result"] for row in result["data"]], ["dupid", "dupid"])
                self.assertEqual(result["data"][0]["shortID"], 42)
                self.assertEqual(writer.call_count, 2)
                self.assertFalse(any(sql.startswith(("DELETE", "INSERT")) for sql in self.cursor.queries))
                self.assertEqual({path: path.read_bytes() for path in saved_bytes}, saved_bytes)
            finally:
                os.chdir(original_cwd)
                invalidate_quality_cache()

    def test_sql_failure_restores_overwrite_and_removes_new_combined_files(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory, patch.object(self.server, "open", builtins.open), patch.object(self.server, "_atomic_write_statistics", self.real_atomic_writer):
            try:
                os.chdir(directory)
                Path("database/ActorStat").mkdir(parents=True)
                Path("database/ReplayProStat").mkdir(parents=True)
                replay_path = Path("database/ReplayProStat/42")
                previous = repr({"overall": {"attributeStatus": self.status("estimated")}}).encode("utf-8")
                replay_path.write_bytes(previous)
                payload = self.replay()
                self.replay_existing(payload, self.status("estimated"))
                self.cursor.fail_on = "INSERT INTO ReplayProStat"
                with patch.object(self.server.traceback, "print_exc"):
                    result = self.client.post("/uploadCombinedData", data={"jdata": json.dumps({"data": [
                        {"type": "battle", "id": 1, "data": self.battle()},
                        {"type": "replay", "id": 2, "data": payload}]})}).get_json()
                self.assertEqual(result["status"], "fail")
                self.assertEqual(replay_path.read_bytes(), previous)
                self.assertEqual(list(Path("database/ActorStat").iterdir()), [])
                self.db.rollback.assert_called_once()
                self.assertIsNone(self.server._statistics_undo.get())
            finally:
                os.chdir(original_cwd)
                invalidate_quality_cache()


if __name__ == "__main__":
    unittest.main()

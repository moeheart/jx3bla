"""Heroic replay receipt through the real client and Flask protocol, offline.

Set JX3BLA_HEROIC_LOG_DIR to exercise the optional 2026-11-13 local logs.
SQL and replay files are isolated in memory; no player data leaves the machine.
"""
import copy
import csv
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import re
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs

import test_server_collection as fixtures


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(os.environ.get("JX3BLA_HEROIC_LOG_DIR", ROOT))
MAP = "25人英雄洛阳之战"
LOGS = (
    ("2026-11-13-20-03-48-25人英雄洛阳之战(836)-突利和顺(139360).jcl", "突利和顺"),
    ("2026-11-13-20-12-53-25人英雄洛阳之战(836)-田承嗣(139382).jcl", "田承嗣"),
    ("2026-11-13-20-20-55-25人英雄洛阳之战(836)-伊曼·寂夜(139373).jcl", "伊曼双子"),
    ("2026-11-13-21-37-44-25人英雄洛阳之战(836)-阿史那承庆(139378).jcl", "阿史那承庆"),
    ("2026-11-13-22-49-04-25人英雄洛阳之战(836)-史朝义(139365).jcl", "史朝义"),
)


class HeroicReceiptCursor(fixtures.RecordingCursor):
    """Retain inserted rows and allocate unique IDs like ReplayProInfo does."""
    def __init__(self):
        super().__init__()
        self.next_id = 100
        self.battles = {}
        self.replays = {}

    def execute(self, sql, *args):
        super().execute(sql, *args)
        for table, destination, hash_index, numbers in (
                ("ActorStat", self.battles, 5, (6, 7, 9, 10, 14)),
                ("ReplayProStat", self.replays, 7, (3, 8, 9, 11, 14, 15, *range(17, 31)))):
            if sql.startswith("INSERT INTO " + table + " "):
                values = re.search(r"VALUES\s*\((.*)\)\s*;?\s*$", sql, re.S).group(1)
                row = next(csv.reader([values.replace("\n", " ")], skipinitialspace=True))
                for index in numbers:
                    row[index] = float(row[index]) if "." in row[index] else int(row[index])
                destination[row[hash_index]] = row
        match = re.search(r"UPDATE ReplayProInfo SET datavalueint=(\d+)", sql)
        if match:
            self.next_id = int(match.group(1))

    def fetchall(self):
        sql = self.last
        if "from ReplayProInfo" in sql:
            return [("num", "", self.next_id)]
        match = re.search(r'WHERE hash = "([^"]+)"', sql)
        if match and "FOR UPDATE" in sql:
            key = match.group(1)
            if "from ActorStat" in sql:
                return [self.battles[key]] if key in self.battles else []
            if "from ReplayProStat" in sql:
                return [(row[8], row[9], row[11], row[17])
                        for row in self.replays.values() if row[7] == key]
        return super().fetchall()


class HeroicUploadTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.ServerCollectionTests.setUpClass.__func__)
    battle = fixtures.ServerCollectionTests.battle
    replay = fixtures.ServerCollectionTests.replay
    validation_results = []

    def setUp(self):
        fixtures.ServerCollectionTests.setUp(self)
        self.cursor = HeroicReceiptCursor()
        self.db.cursor.return_value = self.cursor
        self.files = {}

        def read_file(path, mode="r", **kwargs):
            if path not in self.files:
                raise FileNotFoundError(path)
            data = self.files[path]
            return io.BytesIO(data) if "b" in mode else io.StringIO(data.decode("utf-8"))

        self.stack.enter_context(patch.object(self.server, "open", side_effect=read_file, create=True))
        self.stack.enter_context(patch.object(self.server, "_atomic_write_statistics",
                                             side_effect=self.files.__setitem__))
        self.stack.enter_context(patch.object(self.server, "load_record_quality",
            side_effect=lambda path: self.server.get_record_quality(json.loads(self.files[path]))))

    def _upload(self, window):
        from MainWindow import get_upload_timeout

        received = []
        sizes = []

        def local_upload(url, *, data, timeout):
            self.assertEqual(url, "offline://heroic/uploadCombinedData")
            self.assertEqual(timeout, get_upload_timeout(len(data)))
            form = parse_qs(data.decode("utf-8"))
            response = self.client.post("/uploadCombinedData", data={"jdata": form["jdata"][0]})
            self.assertEqual(response.status_code, 200)
            received.append(response.get_json())
            sizes.append(len(data))
            return io.BytesIO(response.data)

        pending_ids = [row["id"] for row in window.uploadData]
        self.db.reset_mock()
        with patch("MainWindow.get_api_url", return_value="offline://heroic/uploadCombinedData"), \
                patch("MainWindow.urllib.request.urlopen", side_effect=local_upload) as request:
            window.executeUploadData()
        request.assert_called_once()
        self.assertEqual(received[0]["status"], "success")
        self.assertEqual([row["id"] for row in received[0]["data"]], pending_ids)
        self.assertTrue(all(row["result"] in ("success", "noteam", "dupid")
                            for row in received[0]["data"]))
        self.db.commit.assert_called_once_with()
        self.db.rollback.assert_not_called()
        self.db.close.assert_called_once_with()
        self.assertEqual(window.uploadData, [])
        return received[0], sizes[0]

    def _assert_readback(self, battle, replay):
        battle_row = self.cursor.battles[battle["hash"]]
        self.assertEqual((battle_row[3], battle_row[12]), ("836", "161"))
        with patch.object(self.cursor, "fetchall", return_value=[
                tuple(battle_row[index] for index in (0, 1, 2, 3, 4, 9, 10, 12))]):
            result = self.client.get("/getBattle", query_string={"hash": battle["hash"]}).get_json()
        self.assertEqual((result["available"], result["mapDetail"], result["gameEdition"]), (1, "836", "161"))
        self.assertEqual(result["act"], json.loads(json.dumps(battle["statistics"]["act"])))
        self.assertEqual(result["quality"], self.server.get_record_quality(battle["statistics"]))

        row = self.cursor.replays[replay["hash"]]
        self.assertEqual((row[5], row[6], row[16], row[31]), (MAP, battle["boss"], battle["hash"], "161"))
        peers = [(item[1], item[8]) for item in self.cursor.replays.values() if item[16] == battle["hash"]]
        with patch.object(self.cursor, "fetchall", side_effect=[
                [tuple(row[index] for index in (8, 9, 12, 2, 16, 31))], peers]):
            result = self.client.get("/getReplayPro", query_string={"id": row[8]}).get_json()
        self.assertEqual((result["available"], result["gameEdition"], result["battleID"]), (1, "161", battle["hash"]))
        raw = json.loads(result["raw"])
        expected = json.loads(json.dumps(replay["statistics"]))
        expected["overall"]["shortID"] = row[8]
        self.assertEqual(raw, expected)
        self.assertEqual(result["quality"], self.server.get_record_quality(expected))
        self.assertEqual(ast.literal_eval(result["teammate"]), dict(peers))

    def test_heroic_receipt_preserves_quality_and_public_replay_ids(self):
        from MainWindow import MainWindow

        window = MainWindow.__new__(MainWindow)
        window.uploadData = []
        window.setNotice = Mock()
        for index, (_, boss) in enumerate(LOGS):
            battle = self.battle(MAP, 1794576000)
            battle.update(boss=boss, hash="heroic-battle-%d" % index)
            battle["statistics"]["act"] = {"rdpsStatus": {"status": "incomplete", "staticAttributes": "available"}}
            record = self.replay(MAP, 1794576000)
            record.update(boss=boss, hash="heroic-replay-%d" % index, battleID=battle["hash"])
            record["statistics"]["overall"].update(map=MAP, boss=boss,
                attributeStatus={"status": "incomplete", "staticAttributes": "available"})
            window.addUploadData({"type": "replay", "data": record, "anchor": copy.deepcopy(record["statistics"])})
            window.addUploadData({"type": "battle", "data": battle, "anchor": None})
            pending = list(window.uploadData)
            response, _ = self._upload(window)
            self.assertEqual(response["data"][0]["scoreRank"], -1)
            self._assert_readback(battle, record)
            window.uploadData = pending
            repeat, _ = self._upload(window)
            self.assertEqual(response["data"][0]["shortID"], repeat["data"][0]["shortID"])
            self.assertTrue(all(row["result"] == "dupid" for row in repeat["data"]))
        self.assertEqual(len({row[8] for row in self.cursor.replays.values()}), 5)

    def test_heroic_map_bosses_and_rank_queries_remain_separate(self):
        self.assertEqual(self.client.get("/getMaps").get_json()["result"]["836"]["name"], MAP)
        bosses = self.client.get("/getBossesFromMap", query_string={"map": MAP}).get_json()
        self.assertEqual(bosses["available"], 1)
        self.assertEqual(set(bosses["result"]), {boss for _, boss in LOGS})
        for map_name, map_id in ((MAP, "836"), (fixtures.MAPS["835"], "835")):
            with self.subTest(map=map_name), patch.object(self.cursor, "fetchall", return_value=[]):
                result = self.client.get("/getRank", query_string={
                    "map": map_name, "boss": "史朝义", "occ": "lingsu", "gameEdition": "161"}).get_json()
                self.assertEqual(result["available"], 1)
                self.assertIn('mapdetail = "%s"' % map_name, self.cursor.last)
                self.assertIn('gameEdition = "161"', self.cursor.last)
                result = self.client.get("/getHoFRank", query_string={
                    "map": map_name, "boss": "史朝义", "orderby": "speedrun"}).get_json()
                self.assertEqual(result["available"], 1)
                self.assertIn('mapdetail = "%s"' % map_id, self.cursor.last)

    def test_heroic_equipment_upgrade_enters_score_and_rdps_ranks_without_changing_id(self):
        from MainWindow import MainWindow

        window = MainWindow.__new__(MainWindow)
        window.uploadData = []
        window.setNotice = Mock()
        record = self.replay(MAP, 1794576000)
        record.update(edition='8.16.7', replayedition='8.16.7',
                      editionfull=self.server.parseEdition('8.16.7'))
        record['statistics']['overall']['attributeStatus'] = {
            'status': 'incomplete', 'staticAttributes': 'available',
            'unmodeledEffects': ['audited equipment pending recomputation']}
        window.addUploadData({'type': 'replay', 'data': copy.deepcopy(record),
                              'anchor': copy.deepcopy(record['statistics'])})
        initial, _ = self._upload(window)
        identifier = initial['data'][0]['shortID']
        self.assertEqual(initial['data'][0]['scoreRank'], -1)

        # Use actual percentile lookup with an isolated heroic-only population.
        self.server.app.percent_data.update({
            'lingsu-836-史朝义-stat-%s-161' % metric: {
                'num': 101, 'value': json.dumps([index * scale for index in range(101)])}
            for metric, scale in (('score', 1), ('rdps', 100))})
        record['statistics']['overall']['attributeStatus'] = {
            'status': 'supported', 'staticAttributes': 'available'}
        window.addUploadData({'type': 'replay', 'data': copy.deepcopy(record),
                              'anchor': copy.deepcopy(record['statistics'])})
        upgraded, _ = self._upload(window)
        self.assertEqual(upgraded['data'][0]['shortID'], identifier)
        self.assertEqual(upgraded['data'][0]['result'], 'success')
        row = self.cursor.replays[record['hash']]
        for metric in ('score', 'rdps'):
            self.assertGreaterEqual(row[self.server.RANK_ID[metric]], 0)
            with patch.object(self.cursor, 'fetchall', return_value=[row]):
                ranked = self.client.get('/getRank', query_string={
                    'map': MAP, 'boss': record['boss'], 'occ': record['occ'],
                    'gameEdition': '161', 'orderby': metric}).get_json()
            self.assertEqual([item['shortID'] for item in ranked['result']['table']], [identifier])
        saved = dict(self.files)
        record['statistics']['overall']['attributeStatus'] = {
            'status': 'estimated', 'staticAttributes': 'estimated'}
        window.addUploadData({'type': 'replay', 'data': record,
                              'anchor': copy.deepcopy(record['statistics'])})
        restricted, _ = self._upload(window)
        self.assertEqual(restricted['data'][0]['result'], 'dupid')
        self.assertEqual(restricted['data'][0]['shortID'], identifier)
        self.assertEqual(self.files, saved)

    def _check_actor_boundaries(self, actor):
        start, end = actor.startTime, actor.finalTime
        self.assertGreater(end, start)
        self.assertAlmostEqual(actor.battleTime, end - start, delta=0.000001)
        self.assertEqual((actor.bossAnalyser.startTime, actor.bossAnalyser.finalTime), (start, end))
        self.assertLessEqual(actor.bld.log[0].time, start)
        self.assertLessEqual(end, actor.bld.log[-1].time)
        self.assertAlmostEqual(sum(actor.bossAnalyser.phaseTime), actor.battleTime)
        self.assertTrue(all(value >= 0 for value in actor.bossAnalyser.phaseTime))
        periods = actor.detail["phasePeriods"]
        self.assertTrue(periods)
        self.assertEqual((periods[0]["start"], periods[-1]["end"]), (start, end))
        self.assertTrue(all(left["end"] == right["start"] for left, right in zip(periods, periods[1:])))
        self.assertAlmostEqual(sum(row["end"] - row["start"] for row in periods), actor.battleTime, delta=0.000001)
        for row in periods:
            self.assertGreaterEqual(row["end"], row["start"])
            self.assertAlmostEqual(row["duration"] * 1000, row["end"] - row["start"], delta=0.001)
        for row in (actor.bh.log["environment"] +
                    [event for events in actor.bh.log["call"].values() for event in events]):
            self.assertLessEqual(start, row["start"])
            self.assertGreaterEqual(row["duration"], 0)
            self.assertLessEqual(row["start"] + row["duration"], end)
        for key in ("phaseTransitions", "phaseChanges"):
            self.assertTrue(all(start <= row["time"] <= end for row in actor.detail.get(key, [])))
        self.assertTrue(actor.bh.mainTargets)
        self.assertTrue(all(counter.buffTimeIntegral() <= actor.battleTime + 1
                            for counter in actor.battleDict.values()))
        self.assertTrue(all(len(row) == 7 for row in actor.potList))
        return [{"phase": row["phase"], "name": row["name"],
                 "start": (row["start"] - start) / 1000,
                 "end": (row["end"] - start) / 1000} for row in periods]

    @unittest.skipUnless(all((LOG_DIR / name).is_file() for name, _ in LOGS),
                         "Set JX3BLA_HEROIC_LOG_DIR to the local 2026-11-13 heroic JCL directory")
    def test_five_real_heroic_clears_upload_readback_and_duplicate_ids(self):
        from MainWindow import MainWindow
        from release.SmokeTest import check_damage_conservation, check_upload_payloads
        from tools.ValidateLuoyang import check_windows, replay

        window = MainWindow.__new__(MainWindow)
        window.playerEquipment = {}
        window.playerEquipmentAnalysed = {}
        window.lastBld = None
        window.stat_percent = {}
        window.uploadData = []
        window.setNotice = Mock()
        reports = []
        type(self).validation_results = reports
        # The preceding wipe has all 25 equipment snapshots. The real batch
        # carries those owner-checked snapshots into the clear, whose JCL omits
        # one player's gear. Never borrow equipment from a later encounter.
        previous = LOG_DIR / "2026-11-13-20-01-33-25人英雄洛阳之战(836)-突利和顺(139360).jcl"
        if previous.is_file():
            failed = replay(previous, window, healers=False)
            self.assertEqual(failed.win, 0)
            self.assertEqual(window.uploadData, [])
            del failed
        for filename, boss in LOGS:
            with self.subTest(boss=boss):
                # A failed independent invariant must not leak a previous
                # encounter's pending queue into the next upload assertion.
                window.uploadData = []
                path = LOG_DIR / filename
                actor = replay(path, window, healers=True)
                quality = self.server.get_record_quality({"attributeStatus": actor.attributeStatus,
                                                          "rdpsStatus": actor.combatTracker.rdpsStatus})
                # Keep diagnostics anonymous and available even if a later
                # boundary, layout or receipt assertion fails.
                quality.pop("unmodeledEffects", None)
                warnings = {warning for base in actor.baseAttribDict.values() if base
                            for warning in base.get("_warnings", [])}
                unmodeled = {warning for base in actor.baseAttribDict.values() if base
                             for warning in base.get("_unmodeledEffects", [])}
                report = {"file": filename, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "boss": boss, "map": "836", "gameEdition": "161", "status": "validating",
                    "win": actor.win, "winReason": actor.detail.get("winReason"),
                    "seconds": actor.battleTime / 1000, "quality": quality,
                    "unresolvedTemplates": sorted({str(actor.bld.info.npc[target].templateID)
                        for target in actor.combatTracker.rdpsStatus.get("unresolvedTargets", [])
                        if target in actor.bld.info.npc}),
                    "equipmentWarningTypes": sorted({warning.rsplit(": ", 1)[-1] for warning in warnings}),
                    "equipmentWarningCount": len(warnings),
                    "equipmentWarnings": sorted(warnings),
                    "unmodeledEquipmentEffects": sorted(unmodeled)}
                reports.append(report)
                self.assertFalse(unmodeled, sorted(unmodeled))
                if not quality['estimatedPlayerCount'] and not quality['missingEquipmentPlayerCount']:
                    self.assertTrue(quality['precise'], quality)
                    self.assertTrue(all(quality['rankEligible'].values()))
                else:
                    self.assertFalse(quality['precise'])
                self.assertEqual((actor.bossAnalyseName, actor.win), (boss, 1))
                self.assertEqual(actor.bld.info.map, MAP)
                periods = self._check_actor_boundaries(actor)
                # These independent anonymous totals come from native result[5]
                # rows, not from the tracker or an inferred set bonus ratio.
                reflected_damage = {'突利和顺': 0, '田承嗣': 71246, '伊曼双子': 12608,
                                    '阿史那承庆': 33013, '史朝义': 148150}[boss]
                reflection_totals = {
                    name: sum(value['sum'] for counter in getattr(actor.combatTracker, name).values()
                              for key, value in counter.skill.items() if key.startswith('7,'))
                    for name in ('ndpsCast', 'rdpsCast', 'mndpsCast', 'mrdpsCast')}
                self.assertEqual(reflection_totals['ndpsCast'], reflected_damage)
                self.assertEqual(reflection_totals['rdpsCast'], reflected_damage)
                self.assertEqual(reflection_totals['mndpsCast'], reflection_totals['mrdpsCast'])
                report['reflectionDamage'] = reflection_totals
                try:
                    conservation = check_damage_conservation(actor.combatTracker)
                    conserved = True
                except AssertionError as error:
                    conservation = error.args[0]
                    conserved = False
                ui = check_windows(actor)
                report.update(ui=ui, phasePeriods=periods, conservation=conservation)
                summary, _ = check_upload_payloads(window, actor)
                self.assertEqual((summary["battle"], summary["replay"]), (1, 25))
                self.assertTrue(all(row["data"]["mapdetail"] == MAP for row in window.uploadData))
                battle = next(row["data"] for row in window.uploadData if row["type"] == "battle")
                personal = [copy.deepcopy(row["data"]) for row in window.uploadData if row["type"] == "replay"]
                precise_count = sum(self.server.get_record_quality(row['statistics'])['precise'] for row in personal)
                self.assertEqual(precise_count, 25 if quality['precise'] else 0)
                anchors = [row["anchor"] for row in window.uploadData if row["type"] == "replay"]
                pending = list(window.uploadData)
                response, size = self._upload(window)
                ids = [row["shortID"] for row in response["data"] if "shortID" in row]
                self.assertEqual(len(set(ids)), 25)
                self.assertEqual([row["overall"]["shortID"] for row in anchors], ids)
                for record in personal:
                    persisted = json.loads(self.files["database/ReplayProStat/%d" %
                                                       self.cursor.replays[record["hash"]][8]])
                    self.assertEqual(self.server.get_record_quality(persisted),
                                     self.server.get_record_quality(record["statistics"]))
                self._assert_readback(battle, personal[0])
                # Same-version reuploads retain both the data and public URLs.
                before_files = dict(self.files)
                window.uploadData = pending
                repeat, _ = self._upload(window)
                self.assertEqual([row["shortID"] for row in repeat["data"] if "shortID" in row], ids)
                self.assertEqual(self.files, before_files)
                self.assertTrue(all(row["result"] == "dupid" for row in repeat["data"]))
                report.update({"status": "passed" if conserved else "failed_conservation",
                    "players": len(personal), "phasePeriods": periods,
                    "timelineEvents": len(actor.bh.log["environment"]),
                    "calls": sum(map(len, actor.bh.log["call"].values())), "ui": ui,
                    "requestBytes": size, "uniqueReplayIDs": len(set(ids)),
                    "preciseReplayCount": precise_count,
                    "readback": "passed", "duplicateIDs": "stable", "conservation": conservation})
                self.assertTrue(conserved, conservation)
        self.assertEqual((len(self.cursor.battles), len(self.cursor.replays)), (5, 125))


if __name__ == "__main__":
    unittest.main()

"""Real 2026-11-02 clears through replay, client upload and local Flask receipt.

The optional local JCL fixtures are never uploaded: the client HTTP call is
redirected to Flask's test client, and SQL/file persistence uses isolated fakes.
"""
import hashlib
import json
from collections import Counter
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs

import test_server_collection as fixtures


ROOT = Path(__file__).resolve().parents[1]
LOGS = (
    ("2026-11-02-20-01-34-25人普通洛阳之战(835)-突利和顺(139306).jcl",
     "突利和顺", "1bc04c976192b1784ec906725b82df00eb21389a0378f3489bbc0f2104bbcaeb"),
    ("2026-11-02-20-05-46-25人普通洛阳之战(835)-田承嗣(139329).jcl",
     "田承嗣", "ec184c380f2d487e7f10c82eb8476e6584daeff853c379cc8536b932d61e22ec"),
    ("2026-11-02-20-12-08-25人普通洛阳之战(835)-伊曼·寂夜(139319).jcl",
     "伊曼双子", "58dce3209f1412d0104dd0b38c3e95fc253a55e91515f1f6c5889bccd01268b1"),
    ("2026-11-02-20-16-04-25人普通洛阳之战(835)-阿史那承庆(139323).jcl",
     "阿史那承庆", "99df0aa823deef3db5560411b235bd43b9706f6ff951a83ede439aba97576a3c"),
    ("2026-11-02-20-23-43-25人普通洛阳之战(835)-史朝义(139312).jcl",
     "史朝义", "2e5d0fc856395e2ee73644ef5568f628474c0583165f0b12737f259e9977e5f2"),
)


class LuoyangUploadPipelineTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.ServerCollectionTests.setUpClass.__func__)
    # Shared setup captures stdout and forbids socket connections and HTTP for
    # the entire test; only local_upload below replaces HTTP with Flask locally.
    setUp = fixtures.ServerCollectionTests.setUp
    battle = fixtures.ServerCollectionTests.battle

    def test_large_urlencoded_replay_form_reaches_upload_handler(self):
        payload = self.battle()
        payload["statistics"]["timeline"] = "x" * 600_000
        response = self.client.post("/uploadCombinedData", data={"jdata": json.dumps({"data": [
            {"id": 0, "type": "battle", "data": payload}]})})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")
        self.assertEqual(response.get_json()["data"][0]["result"], "success")
        self.db.commit.assert_called_once_with()

    def test_configured_form_and_total_body_limits_still_apply(self):
        for key in ("MAX_FORM_MEMORY_SIZE", "MAX_CONTENT_LENGTH"):
            with self.subTest(limit=key), patch.dict(self.server.app.config, {key: 1024}):
                response = self.client.post("/uploadCombinedData", data={"jdata": "x" * 2048})
                self.assertEqual(response.status_code, 413)
        self.connect.assert_not_called()

    @unittest.skipUnless(all((ROOT / name).is_file() for name, _, _ in LOGS),
                         "Local 2026-11-02 JCL fixtures are unavailable")
    def test_five_modeled_clears_are_precise_and_receive_server_ids(self):
        from MainWindow import MainWindow, get_upload_timeout
        from replayer.CombatTracker import BoostCounter
        from release.SmokeTest import check_damage_conservation, check_upload_payloads
        from tools.RecordQuality import get_record_quality
        from tools.ValidateLuoyang import replay

        window = MainWindow.__new__(MainWindow)
        window.playerEquipment = {}
        window.playerEquipmentAnalysed = {}
        window.lastBld = None
        window.stat_percent = {}
        window.uploadData = []
        window.setNotice = Mock()
        replay_count = 0
        self.fixed_damage_observations = []
        for filename, boss, expected_hash in LOGS:
            with self.subTest(boss=boss):
                path = ROOT / filename
                if expected_hash:
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected_hash)
                fixed = {"boss": boss, "skills": {}}
                actual_rates = BoostCounter.getRateForEvent

                def observed_rates(counter, event, skill_name):
                    rates = actual_rates(counter, event, skill_name)
                    if event.scheme != 1 or str(event.id) not in ("37561", "37562") or event.level != 1:
                        return rates
                    if counter.occ.endswith("w"):
                        return rates
                    observation = fixed["skills"].setdefault(str(event.id), Counter())
                    observation["events"] += 1
                    observation["quotedFullIDs"] += int(event.full_id.startswith('"'))
                    observation["effectiveDamage"] += event.damageEff
                    final_keys = ("atGamePlayDamageFinalCof", "atActivityDamageFinalCof")
                    ordinary_external = [entry for entry in counter.boost.values()
                                         if entry["source"] != counter.playerid
                                         and not any(entry["effect"].get(key, 0) for key in final_keys)]
                    observation["eventsWithOrdinaryExternalBoosts"] += bool(ordinary_external)
                    for key, value in rates.items():
                        if key == "self" or value["rate"] == 0:
                            continue
                        entry = counter.boost.get(key)
                        allowed = entry and any(entry["effect"].get(name, 0) for name in final_keys)
                        # A conserved total alone cannot detect incorrect
                        # transfers from a fixed hit to ordinary attribute buffs.
                        self.assertTrue(allowed, "Fixed equipment damage credited an ordinary source")
                        observation["externalFinalRateTotal"] += value["rate"]
                    self.assertAlmostEqual(sum(value["rate"] for value in rates.values()), 1.0)
                    return rates

                with patch.object(BoostCounter, "getRateForEvent", observed_rates):
                    actor = replay(path, window, healers=True)
                self.assertEqual(set(fixed["skills"]), {"37561", "37562"})
                self.assertTrue(all(row["eventsWithOrdinaryExternalBoosts"] > 0 for row in fixed["skills"].values()))
                self.assertTrue(all(row["quotedFullIDs"] == row["events"] for row in fixed["skills"].values()))
                self.fixed_damage_observations.append(fixed)
                self.assertEqual(actor.bossAnalyseName, boss)
                self.assertEqual(actor.win, 1)
                # Full logs exercise the actual equipment audit and dynamic
                # attribution; no quality flag is mocked or rewritten here.
                self.assertEqual(actor.attributeStatus["status"], "supported")
                self.assertFalse(actor.attributeStatus.get("unmodeledEffects"))
                self.assertTrue(get_record_quality(actor.combatTracker.rdpsStatus)["precise"])
                check_damage_conservation(actor.combatTracker)
                summary, _ = check_upload_payloads(window, actor)
                self.assertEqual((summary["battle"], summary["replay"]), (1, 25))
                replay_count += summary["replay"]
                for queued in window.uploadData:
                    quality = get_record_quality(queued["data"]["statistics"])
                    self.assertTrue(quality["precise"])
                    self.assertTrue(all(quality["rankEligible"].values()))
                    self.assertEqual(quality["estimatedPlayerCount"], 0)
                    self.assertEqual(quality["missingEquipmentPlayerCount"], 0)
                    self.assertFalse(quality.get("unmodeledEffects"))
                anchors = [row["anchor"] for row in window.uploadData if row["type"] == "replay"]
                received = []

                def local_upload(url, *, data, timeout):
                    self.assertEqual(url, "offline://uploadCombinedData")
                    self.assertEqual(timeout, get_upload_timeout(len(data)))
                    self.assertGreater(timeout, 120)
                    form = parse_qs(data.decode("utf-8"))
                    response = self.client.post("/uploadCombinedData", data={"jdata": form["jdata"][0]})
                    self.assertEqual(response.status_code, 200,
                                     "payload=%d bytes; %s" % (len(data), response.get_data(as_text=True)))
                    received.append(response.get_json())
                    return BytesIO(response.data)

                self.db.reset_mock()
                self.cursor.queries.clear()
                with patch("MainWindow.get_api_url", return_value="offline://uploadCombinedData"), \
                        patch("MainWindow.urllib.request.urlopen", side_effect=local_upload) as request:
                    window.executeUploadData()
                request.assert_called_once()
                self.assertEqual(received[0]["status"], "success")
                self.assertEqual(len(received[0]["data"]), 26)
                self.assertEqual([row["result"] for row in received[0]["data"]],
                                 ["success"] * 25 + ["noteam"])
                self.assertEqual(sum(sql.startswith("INSERT INTO ActorStat ") for sql in self.cursor.queries), 1)
                self.assertEqual(sum(sql.startswith("INSERT INTO ReplayProStat ") for sql in self.cursor.queries), 25)
                self.db.commit.assert_called_once_with()
                self.db.rollback.assert_not_called()
                self.assertEqual(window.uploadData, [])
                self.assertTrue(all(isinstance(anchor["overall"].get("shortID"), int) for anchor in anchors))
                # Eligibility is independent of percentile availability: the
                # fixture deliberately provides no percentile reference table.
                self.assertTrue(all(anchor["overall"]["scoreRank"] == -1 for anchor in anchors))
        self.assertEqual(replay_count, 125)


if __name__ == "__main__":
    unittest.main()

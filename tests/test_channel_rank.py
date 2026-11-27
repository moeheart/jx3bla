import json
import unittest
from types import SimpleNamespace

from replayer.ReplayerBase import RankCalculator, ReplayerBase
from serverFunc.UpdateReplayRank import _sample
from test_cangsheng_rank_collection import replay_record
from tools.ChannelRank import CHANNEL_GROUPS, channel_upload_result, display_channel_result


class ChannelRankTests(unittest.TestCase):
    def test_new_and_historical_cards_only_read_their_own_distribution(self):
        overall = {"playerID": "test-player", "map": "25人普通洛阳之战", "boss": "史朝义"}
        for group in CHANNEL_GROUPS:
            with self.subTest(group=group):
                old = {"skill": {group: {"num": 9, "numPerSec": 0.3, "delay": 75, "HPS": 20}}, "overall": overall}
                new = {"skill": {group: {**old["skill"][group], "ticks": 28, "delaySamples": 8}}, "overall": overall}
                pool = {}
                def add_pool(name, count):
                    for metric in ("num", "numPerSec", "delay", "HPS"):
                        key = f"occ-835-史朝义-{name}-{metric}-161"
                        pool[key] = {"num": count, "value": json.dumps([0] * 101)}
                def counts(result):
                    rank = RankCalculator(result, pool, 161).getRankFromStat("occ")
                    return [rank[group][key]["num"] for key in ("num", "numPerSec", "delay", "HPS")]
                add_pool(group, 23)
                self.assertEqual(counts(old), [23, 23, 23, 23])
                self.assertEqual(counts(new), [0, 0, 0, 23])
                add_pool(group + "Cast", 4)
                self.assertEqual(counts(new), [4, 4, 4, 23])
                self.assertEqual(counts(old), [23, 23, 23, 23])
                self.assertIs(channel_upload_result(old), old)

    def test_upload_queue_isolates_cast_metrics_from_legacy_sampler(self):
        row = replay_record("8.16.8", "161")
        queued = []
        replay = ReplayerBase.__new__(ReplayerBase)
        replay.win, replay.actorData, replay.public = 1, {}, 1
        replay.window = SimpleNamespace(addUploadData=queued.append)
        replay.config = SimpleNamespace(item={"user": {"uuid": ""}})
        replay.occ, replay.battleID = row[2], ""
        replay.getHash = lambda: row[7]
        replay.result = {"overall": {"map": row[5], "boss": row[6], "playerID": row[1],
                                     "edition": "test", "battleTime": 1, "server": row[0]},
                         "skill": {"dgsn": {"ticks": 30, "num": 8, "numPerSec": 0.2, "delay": 0,
                                            "delaySamples": 7, "HPS": 55}},
                         "rank": {"dgsn": {"num": {"num": 4, "percent": 85}}}}
        original = json.loads(json.dumps(replay.result))
        replay.prepareUpload()
        self.assertIs(queued[0]["anchor"], replay.result)
        payload = queued[0]["data"]["statistics"]
        samples, _ = _sample(row, json.dumps(payload))
        prefix = "lingsu-835-史朝义-dgsn"
        for key, value in (("num", 8), ("numPerSec", 0.2), ("delay", 0)):
            self.assertNotIn(f"{prefix}-{key}-161", samples)
            self.assertEqual(samples[f"{prefix}Cast-{key}-161"], value)
        self.assertEqual(samples[f"{prefix}-HPS-161"], 55)
        self.assertNotIn(f"{prefix}Cast-delaySamples-161", samples)
        self.assertEqual(replay.result, original)
        self.assertEqual(display_channel_result(payload), original)
        self.assertEqual(channel_upload_result(payload), payload)

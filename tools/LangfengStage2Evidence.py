# Created by moeheart at 03/30/2026
# Emit structured stage-2 win evidence summaries for Langfeng Xuancheng.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.BattleLogData import BattleLogData
import replayer.ActorReplayPro as ActorReplayModule


class DummyADR:

    def GetGroupAttributeAttrib(self, requests):
        return {}


ActorReplayModule.AttributeDisplayRemote = DummyADR


class DummyConfig:

    def __init__(self):
        self.item = {
            "general": {"mask": 0, "datatype": "jcl"},
            "actor": {"failthreshold": 10, "filter": ""},
            "user": {"uuid": "stage2-evidence"},
        }


class DummyWindow:

    def __init__(self):
        self.playerEquipment = {}
        self.playerEquipmentAnalysed = {}
        self.lastBld = None
        self.uploadData = []
        self.stat_percent = {}

    def setNotice(self, *args, **kwargs):
        pass

    def addUploadData(self, data):
        self.uploadData.append(data)


def run_actor_replay(path):
    config = DummyConfig()
    window = DummyWindow()

    bld = BattleLogData(window)
    bld.loadFromJcl(str(path))

    actor = ActorReplayModule.ActorProReplayer(config, [str(path), 0, 1], "", {str(path): bld}, window)
    actor.FirstStageAnalysis()
    actor.SecondStageAnalysis()
    return actor


def get_sample_tag(path, group):
    if path == group[-1]:
        return "CLEAR_REFERENCE"
    return "TRY_REFERENCE"


def main():
    boss_order = ["笑妆娘", "唐醉", "柳公子", "阿史那承庆"]
    files = sorted(Path(".").glob("*阆风悬城*.jcl"))
    groups = {boss: [] for boss in boss_order}

    for path in files:
        bld = BattleLogData()
        bld.loadFromJcl(str(path))
        boss = bld.info.boss
        if boss in groups:
            groups[boss].append(path)

    for boss in boss_order:
        group = sorted(groups[boss])
        if not group:
            continue
        print("========== %s ==========" % boss)
        for path in group:
            actor = run_actor_replay(path)
            detail = actor.detail
            recommendation = detail.get("winEvidenceRecommendation", {})
            print("%s | %s | %s | recommended=%s | available=%s | need_shout_hook=%s" % (
                get_sample_tag(path, group),
                path.name,
                actor.bossAnalyseName,
                recommendation.get("recommended", "undetermined"),
                ",".join(recommendation.get("available", [])),
                recommendation.get("needShoutHook", 1),
            ))
            print(detail.get("winEvidenceReport", ""))
            print("")


if __name__ == "__main__":
    main()

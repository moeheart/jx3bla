"""Replay backed-up local JCLs through the real actor pipeline, without network I/O.

python -X utf8 -m tools.ValidateLuoyang --manifest backups/luoyang-20260915/manifest.json
"""
import argparse
import contextlib
import gc
import hashlib
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from data.BattleLogData import BattleLogData
from FileLookUp import FileLookUp
from tools.Names import getJclEncounter


class ValidationWindow:
    def __init__(self):
        self.playerEquipment = {}
        self.playerEquipmentAnalysed = {}
        self.lastBld = None
        self.stat_percent = {}
        self.uploadData = []

    def setNotice(self, *args, **kwargs):
        pass

    def addUploadData(self, data):
        raise AssertionError("Validation must not enqueue uploads")


def make_config(healers=False):
    from ConfigTools import Config
    config = Config.__new__(Config)
    config.skipUser = True
    config.item = {key: {} for key in ("general", "actor", "user", "xiangzhi", "lingsu", "lijing", "butian", "yunchang")}
    config.item["user"]["uuid"] = "local-luoyang-validation"
    config.checkItems()
    for key in ("xiangzhi", "lingsu", "lijing", "butian", "yunchang"):
        config.item[key]["active"] = int(healers)
    return config


def replay(path, window=None, healers=False):
    from replayer.ActorReplayPro import ActorProReplayer
    bld = BattleLogData()
    bld.loadFromJcl(str(path))
    actor = ActorProReplayer(make_config(healers), [str(path), 0, 1], "", {str(path): bld}, window or ValidationWindow())
    actor.replay()
    return actor


def check_windows(actor):
    """Construct actual Tk widgets while keeping the test windows hidden."""
    import tkinter as tk
    from window.SingleBossWindow import SingleBossWindow
    from window.CombatTrackerWindow import CombatTrackerWindow
    root = tk.Tk()
    root.withdraw()
    original = tk.Toplevel

    def hidden_window(*args, **kwargs):
        window = original(*args, **kwargs)
        window.withdraw()
        return window

    try:
        with patch("tkinter.Toplevel", side_effect=hidden_window):
            selector = SingleBossWindow.__new__(SingleBossWindow)
            selector.mainWindow = SimpleNamespace(config=actor.config)
            selector.setDetail(actor.potList, actor.statDict, actor.detail, actor.occResult, actor.actorData)
            window = selector.specificBossWindow
            assert type(window).__module__.startswith("replayer.boss.luoyangzhizhan.")
            window.loadWindow()
            tracker = CombatTrackerWindow(actor.combatTracker)
            tracker.loadWindow()
            tracker.setStat("rdps")
            assert "待校准" in tracker.rightTitle.cget("text")
            tracker.setStat("ndps")
            root.update_idletasks()
            return {"bossWindow": type(window).__name__, "widgets": "constructed", "rdps": "marked incomplete"}
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/160/luoyang-validation.json"))
    parser.add_argument("--latest", action="store_true", help="Replay only the latest attempt of each boss")
    parser.add_argument("--healers", action="store_true", help="Also exercise the configured healer replay paths")
    parser.add_argument("--ui", action="store_true", help="Construct hidden boss and combat-statistic Tk windows")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    if args.latest:
        lookup = FileLookUp()
        lookup.dataType = "jcl"
        lookup.specifyFiles([row["source"] for row in manifest])
        latest = {row[0] for row in lookup.getLocalFile()[0]}
        manifest = [row for row in manifest if row["source"] in latest]
    results = []
    window = ValidationWindow()
    for row in manifest:
        path = Path(row["source"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"].lower():
            raise AssertionError("Source changed since backup: " + path.name)
        with patch("socket.socket.connect", side_effect=AssertionError("Network disabled in validation")):
            with contextlib.redirect_stdout(io.StringIO()):
                actor = replay(path, window, args.healers)
        assert actor.bossAnalyseName == getJclEncounter(path)[1]
        assert actor.bossAnalyser.__class__.__module__.startswith("replayer.boss.luoyangzhizhan.")
        assert 0 < actor.battleTime <= actor.bld.log[-1].time - actor.bld.log[0].time + 6001
        assert actor.bh is not None and actor.bh.mainTargets
        assert actor.win in (0, 1)
        assert all(len(record) == 7 for record in actor.potList), "Battle-event rows must fit the seven-field UI contract"
        assert actor.combatTracker.rdpsStatus["gameEdition"] == 160
        assert actor.combatTracker.rdpsStatus["status"] == "incomplete"
        assert not actor.combatTracker.rdps["player"]
        assert all(counter.buffTimeIntegral() <= actor.battleTime + 1 for counter in actor.battleDict.values())
        assert all(event["start"] <= actor.finalTime for event in actor.bh.log["environment"])
        metrics = {key: getattr(actor.combatTracker, key)["sum"] for key in ("ndps", "mndps", "hps", "ahps", "rhps")}
        assert all(math.isfinite(value) and value >= 0 for value in metrics.values())
        summary = {
            "file": path.name, "sha256": row["sha256"].lower(),
            "boss": actor.bossAnalyseName, "class": type(actor.bossAnalyser).__name__,
            "win": actor.win, "seconds": round(actor.battleTime / 1000, 3),
            "players": len(actor.statDict), "timelineEvents": len(actor.bh.log["environment"]),
            "calls": sum(len(events) for events in actor.bh.log["call"].values()), "mechanicRecords": len(actor.potList),
            "mainTargets": len(actor.bh.mainTargets),
            "attributeStatus": actor.detail.get("attributeStatus"),
            "rdpsStatus": getattr(actor.combatTracker, "rdpsStatus", None),
            "healerReplays": len(actor.occResult),
            "metricTotalsPerSecond": metrics,
        }
        results.append(summary)
        if args.ui:
            summary["ui"] = check_windows(actor)
        print("%d/%d %s win=%d %.3fs" % (len(results), len(manifest), summary["boss"], actor.win, summary["seconds"]), flush=True)
        del actor
        gc.collect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"network": "disabled", "count": len(results), "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

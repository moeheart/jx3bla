"""Replay backed-up local JCLs through the real actor pipeline, without network I/O.

Supply a manifest of explicitly selected current formal-server logs.
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
from tools.Attribute import CURRENT_GAME_EDITION

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
            supported = actor.combatTracker.rdpsStatus['status'] == 'supported'
            estimated = bool(actor.combatTracker.rdpsStatus.get('estimatedPlayers'))
            assert ("待校准" not in tracker.rightTitle.cget("text")) == (supported or estimated)
            if estimated:
                assert "仅供参考" in tracker.rightTitle.cget("text")
            tracker.setStat("ndps")
            # A withdrawn Toplevel has no allocated viewport (often 1x1).
            # Map it fully transparent so actual pack/grid geometry is checked.
            window.window.attributes("-alpha", 0)
            window.window.deiconify()
            root.update()
            table_layout = {}
            if hasattr(window, "statsCanvas"):
                canvas = window.statsCanvas
                tables = [child for child in canvas.winfo_children() if isinstance(child, tk.Frame)]
                assert len(tables) == 1, "Expected one scrollable encounter table"
                table = tables[0]
                bounds = canvas.bbox("all")
                region = tuple(map(float, canvas.cget("scrollregion").split()))
                assert region[0] <= bounds[0] and region[1] <= bounds[1]
                assert region[2] >= bounds[2] and region[3] >= bounds[3], "Scroll region must cover every table cell"
                assert bounds[2] - bounds[0] >= table.winfo_reqwidth()
                assert bounds[3] - bounds[1] >= table.winfo_reqheight()
                assert canvas.cget("xscrollcommand") and canvas.cget("yscrollcommand")
                canvas.xview_moveto(1)
                canvas.yview_moveto(1)
                assert canvas.xview()[1] == 1.0 and canvas.yview()[1] == 1.0
                canvas.xview_moveto(0)
                canvas.yview_moveto(0)
                if table.winfo_reqwidth() <= canvas.winfo_width():
                    assert abs(bounds[0] - (canvas.winfo_width()-bounds[2])) <= 1, "Table must remain centered"
                assert window.window.winfo_width() <= window.window.winfo_screenwidth()
                assert window.window.winfo_height() <= window.window.winfo_screenheight()-80
                chrome = window.window.winfo_height()-canvas.winfo_height()
                fits_screen = table.winfo_reqheight()+chrome <= window.window.winfo_screenheight()-80
                if fits_screen:
                    assert table.winfo_reqheight() <= canvas.winfo_height(), "Full roster should fit without scrolling"
                table_layout = {"scrollable": True, "tableWidth": table.winfo_reqwidth(),
                                "tableHeight": table.winfo_reqheight(), "scrollRegion": list(region),
                                "viewportWidth": canvas.winfo_width(), "viewportHeight": canvas.winfo_height(),
                                "allRowsVisible": table.winfo_reqheight() <= canvas.winfo_height()}
            return {"bossWindow": type(window).__name__, "widgets": "constructed",
                    "rdps": actor.combatTracker.rdpsStatus['status'],
                    "requestedWidth": window.window.winfo_reqwidth(),
                    "requestedHeight": window.window.winfo_reqheight(),
                    "configuredGeometry": window.window.geometry(),
                    "screenWidth": window.window.winfo_screenwidth(),
                    "screenHeight": window.window.winfo_screenheight(),
                    "table": table_layout}
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("build/validation/luoyang.json"))
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
            with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'):
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, window, args.healers)
        assert actor.bossAnalyseName == getJclEncounter(path)[1]
        assert actor.bossAnalyser.__class__.__module__.startswith("replayer.boss.luoyangzhizhan.")
        assert 0 < actor.battleTime <= actor.bld.log[-1].time - actor.bld.log[0].time + 6001
        assert actor.bh is not None and actor.bh.mainTargets
        assert actor.win in (0, 1)
        assert all(len(record) == 7 for record in actor.potList), "Battle-event rows must fit the seven-field UI contract"
        status = actor.combatTracker.rdpsStatus
        assert status["gameEdition"] == CURRENT_GAME_EDITION
        assert status["status"] in ("supported", "incomplete", "estimated"), status
        if status["status"] == "incomplete":
            assert status.get("reason"), status
        if status["status"] == "estimated":
            assert status.get("estimatedPlayers") and status.get("warning"), status
        assert all(counter.buffTimeIntegral() <= actor.battleTime + 1 for counter in actor.battleDict.values())
        assert all(event["start"] <= actor.finalTime for event in actor.bh.log["environment"])
        metrics = {key: getattr(actor.combatTracker, key)["sum"] for key in ("ndps", "mndps", "rdps", "mrdps", "hps", "ahps", "rhps")}
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

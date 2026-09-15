"""Offline encounter-level replay for backed-up Luoyang JCL files; no uploads."""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.BattleLogData import BattleLogData
from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer


def run(path):
    bld = BattleLogData()
    with contextlib.redirect_stdout(io.StringIO()):
        bld.loadFromJcl(str(path))
    cls = (TuliHeshunReplayer if "突利和顺" in path.name else
           TianChengsiReplayer if "田承嗣" in path.name else YimanTwinsReplayer)
    config = SimpleNamespace(item={"actor": {"filter": ""}})
    start, end = bld.log[0].time, bld.log[-1].time
    replay = cls(bld, {key: value.occ for key, value in bld.info.player.items()},
                 start, end, end - start, bld.info.boss, config)
    replay.recordEquipment({})
    replay.initBattle()
    for event in bld.log:
        replay.analyseSecondStage(event)
    replay.trimTime()
    rows, pots, detail, controls = replay.getResult()
    assert 0 <= replay.finalTime - replay.startTime <= end - start
    assert all(0 <= counter.buffTimeIntegral() <= replay.battleTime for counter in controls.values())
    assert all(call["duration"] >= 0 and call["start"] + call["duration"] <= replay.finalTime
               for calls in replay.bh.log["call"].values() for call in calls)
    assert all(event["start"] <= replay.finalTime for event in replay.bh.log["environment"])
    assert all((Path(__file__).resolve().parents[1] / "icons" / (event["iconid"] + ".png")).is_file()
               for event in replay.bh.log["environment"])
    return {"file": path.name, "win": replay.win, "reason": detail["winReason"],
            "recordedSeconds": (end - start) / 1000, "trimmedSeconds": replay.battleTime / 1000,
            "effectiveSeconds": detail["effectiveTime"] / 1000, "phases": detail["phaseTimes"],
            "mainTargets": len(replay.bh.mainTargets), "environmentEvents": len(replay.bh.log["environment"]),
            "calls": len(detail.get("mechanics", [])), "hitRecords": len(detail.get("mechanicHits", [])),
            "damage": {key: sum(row.get(key, 0) for row in rows)
                       for key in ("bossDamage", "swordDamage", "nightDamage", "fireDamage", "inertDamage")
                       if any(key in row for row in rows)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = sorted(path for path in args.logs.glob("2026-09-15-*洛阳之战*.jcl")
                   if any(name in path.name for name in ("突利和顺", "田承嗣", "伊曼")))
    results = [run(path) for path in paths]
    summary = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary)

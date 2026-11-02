"""Validate the 2026-11-02 official Luoyang reference batch offline.

The manifest and original logs stay in local backups. Reports contain encounter
aggregates only; player names, IDs, equipment and individual scores are omitted.
"""
import argparse
import contextlib
import gc
import hashlib
import io
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

from FileLookUp import FileLookUp
from tools.Functions import getOccType
from tools.Names import getJclEncounter
from tools.ValidateLuoyang import ValidationWindow, check_windows, replay


EXPECTED_BOSSES = ("突利和顺", "田承嗣", "伊曼双子", "阿史那承庆", "史朝义")
# These live logs do not all carry an explicit victory event. Boundary checks
# must not turn the absence of a victory marker into a fabricated clear.
EXPECTED_WINS = {"突利和顺": 1, "田承嗣": 0, "伊曼双子": 1, "阿史那承庆": 0, "史朝义": 0}
EXPECTED_DURATIONS = {"田承嗣": 203193, "阿史那承庆": 240022, "史朝义": 263702}


def actor_summary(actor, entry, healers=False, ui=False):
    """Check independent replay invariants and return anonymous aggregates."""
    errors = []

    def check(label, condition):
        if not condition:
            errors.append(label)

    tracker = actor.combatTracker
    analyser = actor.bossAnalyser
    end = actor.finalTime
    start = actor.startTime
    status = tracker.rdpsStatus
    check("encounter routing", actor.bossAnalyseName == getJclEncounter(Path(entry["source"]))[1])
    check("dedicated encounter module", type(analyser).__module__.startswith("replayer.boss.luoyangzhizhan."))
    check("valid clear state", actor.win in (0, 1))
    if actor.bossAnalyseName in EXPECTED_WINS:
        check("evidence-backed clear state", actor.win == EXPECTED_WINS[actor.bossAnalyseName])
    if actor.bossAnalyseName in EXPECTED_DURATIONS:
        check("observed combat-exit boundary", abs(actor.battleTime-EXPECTED_DURATIONS[actor.bossAnalyseName]) < 1e-6)
    check("25 players", len(actor.statDict) == 25)
    check("official-server version", status["gameEdition"] >= 161)
    bases = actor.baseAttribDict
    missing_bases = sum(bases.get(player) is None for player in actor.bld.info.player)
    warnings = {warning for base in bases.values() if base for warning in base.get("_warnings", [])}
    warning_types = sorted({warning.rsplit(": ", 1)[-1] for warning in warnings})
    known_scripts = {"atSetEquipmentRecipe", "atSkillEventHandler", "atExecuteScript"}
    check("all logged equipment bases", missing_bases == 0 and len(bases) == 25)
    check("known equipment-script calibration boundary", bool(warnings) and set(warning_types) <= known_scripts)
    check("explicit incomplete status", status["status"] == "incomplete" and status.get("reason") == "部分玩家装备或当前地图首领属性缺少验证数据。")
    check("all damaged targets calibrated", not status.get("unresolvedTargets"))
    check("positive duration", actor.battleTime > 0 and abs(actor.battleTime-(end-start)) < 1e-6)
    check("encounter boundary", analyser.startTime == start and analyser.finalTime == end)
    check("log boundary", actor.bld.log[0].time <= start < end <= actor.bld.log[-1].time)
    phase_time = list(analyser.phaseTime)
    check("phase duration conservation", abs(sum(phase_time)-actor.battleTime) < 1e-6 and all(t >= 0 for t in phase_time))
    periods = actor.detail.get("phasePeriods", [])
    check("phase intervals exist", bool(periods))
    if periods:
        check("phase interval coverage", periods[0]["start"] == start and periods[-1]["end"] == end)
        check("phase interval continuity", all(left["end"] == right["start"] for left, right in zip(periods, periods[1:])))
        check("phase interval conservation", abs(sum(row["end"]-row["start"] for row in periods)-actor.battleTime) < 1e-6)
        check("phase interval duration", all(row["end"] >= row["start"] and abs(row["duration"]*1000-(row["end"]-row["start"])) < 0.001 for row in periods))
    for event in actor.bh.log["environment"]:
        check("environment boundary", start <= event["start"] <= end and event["start"]+event["duration"] <= end)
    for calls in actor.bh.log["call"].values():
        for event in calls:
            check("call boundary", start <= event["start"] <= end and event["duration"] >= 0 and event["start"]+event["duration"] <= end)
    for key in ("phaseTransitions", "phaseChanges"):
        for event in actor.detail.get(key, []):
            check("phase event boundary", start <= event["time"] <= end)
    check("battle counter boundary", all(counter.buffTimeIntegral() <= actor.battleTime+1 for counter in actor.battleDict.values()))
    check("main targets", bool(actor.bh.mainTargets))
    if actor.bossAnalyseName == "突利和顺":
        check("observed dead-water interval", any(row["phase"] == 2 and row["end"]-row["start"] == 13016 for row in periods))
    elif actor.bossAnalyseName == "阿史那承庆":
        souls = actor.detail.get("soulPeriods", [])
        check("observed soul interval", any(row["end"]-row["start"] == 7042 for row in souls))
    elif actor.bossAnalyseName == "史朝义":
        transitions = actor.detail.get("transitionPeriods", [])
        check("observed armour transition", any(row["start"]-start == 106187 and row["end"]-start == 114184 for row in transitions))
        check("transition remains effective", abs(actor.bh.sumTime("dps")-actor.battleTime) < 1e-6)
    check("event UI contract", all(len(record) == 7 for record in actor.potList))
    metrics = {key: getattr(tracker, key)["sum"] for key in ("ndps", "mndps", "rdps", "mrdps", "hps", "ahps", "rhps")}
    check("finite nonnegative metrics", all(math.isfinite(value) and value >= 0 for value in metrics.values()))
    direct = sum(row.get("sum", 0) for row in tracker.ndps["player"].values())
    redistributed = sum(row.get("sum", 0) for row in tracker.rdps["player"].values())
    check("damage redistribution conservation", math.isclose(direct, redistributed, abs_tol=0.001, rel_tol=1e-12))
    healer_count = sum(getOccType(row["occ"]) == "healer" for row in actor.occResult.values())
    roster_healers = sum(getOccType(occ) == "healer" for occ in actor.occDetailList.values())
    if healers:
        check("all specialization replays", len(actor.occResult) == len(actor.statDict))
        check("all healer replays", healer_count == roster_healers)
    summary = {
        "boss": actor.bossAnalyseName,
        "file": Path(entry["source"]).name,
        "sha256": entry["sha256"].lower(),
        "class": type(analyser).__name__,
        "win": actor.win,
        "winReason": actor.detail.get("winReason"),
        "seconds": round(actor.battleTime/1000, 3),
        "effectiveDpsSeconds": round(actor.bh.sumTime("dps")/1000, 3),
        "players": len(actor.statDict),
        "specializationReplays": len(actor.occResult),
        "healerReplays": healer_count,
        "gameEdition": status["gameEdition"],
        "attributeStatus": status["status"],
        "attributeReason": status.get("reason"),
        "unresolvedTargetCount": len(status.get("unresolvedTargets", [])),
        "equipmentBases": len(bases)-missing_bases,
        "unmodeledEquipmentEffectTypes": warning_types,
        "unmodeledEquipmentWarnings": len(warnings),
        "calibrationBoundary": "equipment_script_effects_unmodeled",
        "phaseTimes": actor.detail.get("phaseTimes", {}),
        "transitionPeriods": [dict(name=row["name"], start=round((row["start"]-start)/1000, 3), end=round((row["end"]-start)/1000, 3), seconds=row["duration"], truncated=row.get("truncated", False)) for row in actor.detail.get("transitionPeriods", [])],
        "phaseMilliseconds": phase_time,
        "phasePeriods": [dict(name=row["name"], phase=row["phase"], start=round((row["start"]-start)/1000, 3), end=round((row["end"]-start)/1000, 3), seconds=row["duration"]) for row in periods],
        "phaseEvents": [dict(time=round((event["time"]-start)/1000, 3), phase=event.get("phase"), name=event.get("name"))
                        for event in actor.detail.get("phaseTransitions", actor.detail.get("phaseChanges", []))],
        "timelineEvents": len(actor.bh.log["environment"]),
        "calls": sum(map(len, actor.bh.log["call"].values())),
        "mechanicRecords": len(actor.potList),
        "directDamage": direct,
        "redistributedDamage": redistributed,
        "conservationError": redistributed-direct,
        "metricTotalsPerSecond": metrics,
        "errors": sorted(set(errors)),
    }
    if ui:
        summary["ui"] = check_windows(actor)
    summary["status"] = "failed" if errors else "passed"
    return summary


def validate_live_manifest(manifest_path, healers=True, ui=True, strict=True):
    """Replay the latest five encounters with shared gear context, offline."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    for entry in manifest:
        assert hashlib.sha256(Path(entry["source"]).read_bytes()).hexdigest() == entry["sha256"].lower(), "Manifest source hash mismatch"
    lookup = FileLookUp()
    lookup.dataType = "jcl"
    lookup.specifyFiles([entry["source"] for entry in manifest])
    selected = {row[0] for row in lookup.getLocalFile()[0]}
    entries = [entry for entry in manifest if entry["source"] in selected
               and getJclEncounter(Path(entry["source"]))[1] in EXPECTED_BOSSES]
    bosses = [getJclEncounter(Path(entry["source"]))[1] for entry in entries]
    assert tuple(bosses) == EXPECTED_BOSSES, "Latest-encounter selection must yield the five bosses in order"
    results = []
    attempts = []
    window = ValidationWindow()
    # Keep the network guard active for parsing, replay and hidden UI creation.
    with patch("socket.socket.connect", side_effect=AssertionError("Live validation: network disabled")):
        with patch("replayer.ActorReplayPro.ActorProReplayer.prepareUpload"), patch("replayer.ReplayerBase.ReplayerBase.prepareUpload"):
            for entry in entries:
                path = Path(entry["source"])
                assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"].lower(), "Manifest source hash mismatch"
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, window, healers)
                    summary = actor_summary(actor, entry, healers=healers, ui=ui)
                results.append(summary)
                print("%s: %s, %.3fs, %d specialization replays" % (summary["boss"], summary["status"], summary["seconds"], summary["specializationReplays"]), flush=True)
                if summary["errors"]:
                    print("  failed invariants:", ", ".join(summary["errors"]), flush=True)
                del actor
                gc.collect()
            # The short Li Fu pull is a separate failed attempt, not a clear.
            for entry in manifest:
                path = Path(entry["source"])
                if "-李复(139332).jcl" not in path.name:
                    continue
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, window, False)
                errors = []
                if actor.bossAnalyseName != "史朝义":
                    errors.append("short-attempt routing")
                if actor.win != 0:
                    errors.append("short attempt must not be a clear")
                if not 0 < actor.battleTime <= actor.bld.log[-1].time-actor.bld.log[0].time+1e-6:
                    errors.append("short-attempt boundary")
                if abs(sum(actor.bossAnalyser.phaseTime)-actor.battleTime) >= 1e-6:
                    errors.append("short-attempt phase duration")
                attempts.append({"file": path.name, "sha256": entry["sha256"].lower(), "boss": actor.bossAnalyseName,
                                 "win": actor.win, "seconds": actor.battleTime/1000, "errors": errors,
                                 "status": "failed" if errors else "passed"})
                print("Short Li Fu attempt: %s, %.3fs, win=%d" % (attempts[-1]["status"], attempts[-1]["seconds"], actor.win), flush=True)
                del actor
                gc.collect()
    report = {"status": "passed" if all(row["status"] == "passed" for row in results+attempts) else "failed",
              "frozen": bool(getattr(sys, "frozen", False)), "network": "disabled", "upload": "disabled",
              "inputLogs": len(manifest), "nonBossLogs": sum(getJclEncounter(Path(row["source"]))[1] not in EXPECTED_BOSSES for row in manifest),
              "count": len(results), "results": results, "otherAttempts": attempts}
    if strict:
        assert report["status"] == "passed", [(row["boss"], row["errors"]) for row in results+attempts if row["errors"]]
    return report


def write_report(report, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-healers", action="store_true")
    parser.add_argument("--no-ui", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="Record failed invariants for a baseline audit")
    args = parser.parse_args()
    report = validate_live_manifest(args.manifest, healers=not args.no_healers, ui=not args.no_ui, strict=False)
    write_report(report, args.output)
    if not args.report_only and report["status"] != "passed":
        raise AssertionError([(row["boss"], row["errors"]) for row in report["results"]+report["otherAttempts"] if row["errors"]])


if __name__ == "__main__":
    main()

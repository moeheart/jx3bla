"""Read-only, anonymous LingSu contribution/coverage audit of five clear JCLs."""
import argparse
from collections import Counter, defaultdict
import contextlib
import gc
import hashlib
import io
import json
from pathlib import Path

from data.BattleLogData import BattleLogData
from tools.Functions import getOccDetailFromXinfaCode, getOccType


def analyze(row, path):
    source_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    assert source_sha == row["sha256"].lower(), "JCL differs from the backed-up input"
    with contextlib.redirect_stdout(io.StringIO()):
        bld = BattleLogData()
        bld.loadFromJcl(str(path))
    healer = next(p for p in row["players"] if p["occ"] == "212h")
    player = healer["id"]
    start, end = bld.log[0].time, bld.log[0].time + round(row["seconds"] * 1000)
    state = {p: 0 for p in bld.info.player}
    buff_caster = {}
    buff_update_time = {}
    last_actual_buff_caster = {}
    last_zyhr_caster = None
    proc_source_audit = Counter()
    proc_source_ranges = {}
    instance_state = defaultdict(dict)
    last = start
    coverage_ms = Counter()
    stack_ms = Counter()
    raw_skills = defaultdict(lambda: Counter(events=0, damage=0, heal=0, effectiveHeal=0))
    skill_names = {}
    buff_events, buff_sources, levels = Counter(), Counter(), Counter()
    casts, deaths, damage_times, onsets = [], [], [], []
    recovery, proc_events, buffed_hits = [], [], []
    other_zyhr_casts = []
    source_windows = []
    active_source_window = None
    pending_death = None
    procs = Counter()
    proc_targets = defaultdict(Counter)
    dmg = Counter()
    target_damage = defaultdict(Counter)
    bins = defaultdict(Counter)
    mismatches = 0
    before_first_cast = 0
    spell_targets = defaultdict(set)
    total_buff_events = 0
    for event in bld.log:
        if event.time > end:
            break
        t = max(start, event.time)
        dt = t - last
        if dt:
            for recipient, stack in state.items():
                if stack > 0:
                    coverage_ms[recipient] += dt
                    stack_ms[recipient] += stack * dt
            last = t
        seconds = (event.time - start) / 1000
        interval = int(max(0, seconds) // 30)
        if event.dataType == "Death" and event.id == player:
            deaths.append(round(seconds, 3))
            pending_death = seconds
        elif event.dataType == "Battle" and event.id == player and event.hp > 0 and pending_death is not None:
            recovery.append(dict(death=round(pending_death, 3), firstPositiveHp=round(seconds, 3),
                                 seconds=round(seconds-pending_death, 3)))
            pending_death = None
        elif event.dataType == "Buff" and event.id == "20854" and event.target in state:
            total_buff_events += 1
            active = event.stack > 0 and getattr(event, "isValid", True) and event.delete not in (True, "true", 1, "1")
            levels[str(event.level)] += 1
            buff_events["active" if active else "inactive"] += 1
            source = "lingsu" if event.caster == player else "recipient_self" if event.caster == event.target else "other_player" if event.caster in state else "non_player"
            buff_sources[source] += 1
            if active_source_window is not None:
                key = source + ("_active" if active else "_inactive")
                active_source_window["buffEventsAfterCast"][key] += 1
                active_source_window["buffEventTimeRanges"].setdefault(key, [round(seconds, 3), round(seconds, 3)])[1] = round(seconds, 3)
            if active:
                last_actual_buff_caster[event.target] = event.caster
                if not casts:
                    before_first_cast += 1
                if state[event.target] == 0:
                    onsets.append((seconds, event.target))
                bins[interval]["buffOnUpdates"] += 1
            slot = str(getattr(event, "instanceID", "none"))
            instance_state[event.target][slot] = event.stack if active else 0
            state[event.target] = event.stack if active else 0
            buff_caster[event.target] = event.caster if active else None
            buff_update_time[event.target] = round(seconds, 3)
            if max(instance_state[event.target].values(), default=0) != state[event.target]:
                mismatches += 1
        elif event.dataType == "Skill":
            if event.id == "27674":
                last_zyhr_caster = event.caster
            if event.id == "27674" and active_source_window is not None and seconds - active_source_window["time"] > .3:
                active_source_window["end"] = round(seconds, 3)
                active_source_window = None
            if event.id == "27674" and event.caster != player:
                meta = bld.info.player.get(event.caster)
                occ = getOccDetailFromXinfaCode(meta.xf) if meta else "non_player"
                other_zyhr_casts.append(dict(time=round(seconds, 3), occ=occ))
                if active_source_window is None:
                    source_counts = Counter("lingsu" if buff_caster.get(p) == player else "new_caster" if buff_caster.get(p) == event.caster else "other" for p, stack in state.items() if stack)
                    active_source_window = dict(time=round(seconds, 3), end=round(row["seconds"], 3), casterOcc=occ,
                                                targetIsCaster=event.target == event.caster,
                                                activeBuffSources=dict(source_counts),
                                                activeBuffStacks=dict(Counter(str(stack) for stack in state.values() if stack)),
                                                buffEventsAfterCast=Counter(), buffEventTimeRanges={},
                                                procsByBuffSource=defaultdict(Counter), procTargets=defaultdict(Counter))
                    source_windows.append(active_source_window)
                    active_times = [buff_update_time[p] for p, stack in state.items() if stack]
                    if active_times:
                        active_source_window["existingBuffApplicationTimeRange"] = [min(active_times), max(active_times)]
            if event.caster == player:
                s = raw_skills[event.id]
                skill_names.setdefault(event.id, bld.info.getSkillName(event.full_id))
                s.update(events=1, damage=event.damageEff, heal=event.heal, effectiveHeal=event.healEff)
                spell_targets[event.id].add(event.target)
                bins[interval]["lingsuEffectiveHeal"] += event.healEff
                if event.id == "27674" and (not casts or seconds - casts[-1] > .3):
                    casts.append(seconds)
                    bins[interval]["zyhrCasts"] += 1
            if event.damageEff > 0 and event.caster in state and event.target in bld.info.npc:
                template = str(bld.info.npc[event.target].templateID)
                dmg["all"] += event.damageEff
                target_damage[template]["all"] += event.damageEff
                bins[interval]["teamDamage"] += event.damageEff
                damage_times.append(seconds)
                if state[event.caster] > 0:
                    buffed_hits.append((seconds, event.damageEff))
                    dmg["buffed"] += event.damageEff
                    dmg["stackWeighted"] += event.damageEff * state[event.caster]
                    dmg["buffedEvents"] += 1
                    target_damage[template]["buffed"] += event.damageEff
                    bins[interval]["buffedDamage"] += event.damageEff
                if 29532 <= int(event.id) <= 29537:
                    labels = ["withActiveBuff" if state[event.caster] > 0 else "withoutActiveBuff"]
                    if event.caster not in last_actual_buff_caster:
                        labels.append("beforeFirstActual20854")
                    if last_actual_buff_caster.get(event.caster) != last_zyhr_caster:
                        labels.append("actualBuffCasterDiffersFromLast27674Caster")
                    for label in labels:
                        proc_source_audit[label] += 1
                        proc_source_ranges.setdefault(label, [round(seconds, 3), round(seconds, 3)])[1] = round(seconds, 3)
                    proc_events.append((seconds, event.damageEff))
                    procs.update(events=1, damage=event.damageEff)
                    proc_targets[template].update(events=1, damage=event.damageEff)
                    bins[interval]["zyhrProcEvents"] += 1
                    bins[interval]["zyhrProcDamage"] += event.damageEff
                    if active_source_window is not None:
                        source = "lingsu" if state[event.caster] > 0 and buff_caster.get(event.caster) == player else "other" if state[event.caster] > 0 else "inactive"
                        active_source_window["procsByBuffSource"][source].update(events=1, damage=event.damageEff)
                        active_source_window["procTargets"][template].update(events=1, damage=event.damageEff)
                        active_source_window.setdefault("procTimeRange", [round(seconds, 3), round(seconds, 3)])[1] = round(seconds, 3)
    dt = max(0, end-last)
    for recipient, stack in state.items():
        if stack:
            coverage_ms[recipient] += dt
            stack_ms[recipient] += dt*stack
    duration = end-start
    recipient_data = []
    for recipient, meta in bld.info.player.items():
        occ = getOccDetailFromXinfaCode(meta.xf)
        recipient_data.append(dict(occ=occ, role=getOccType(occ), cover=coverage_ms[recipient]/duration,
                                   meanStacks=stack_ms[recipient]/duration))
    intervals = []
    for index, cast in enumerate(casts):
        targets = {target for t, target in onsets if cast <= t < cast+20}
        cutoff = casts[index+1] if index+1<len(casts) else row["seconds"]
        proc_values = [value for t,value in proc_events if cast <= t < cutoff]
        intervals.append(dict(time=round(cast, 3), freshRecipients20s=len(targets),
                              secondsBeforeEnd=round(row["seconds"]-cast,3),
                              procEvents=len(proc_values), rawProcDamage=sum(proc_values),
                              buffedTeamDamage=sum(value for t,value in buffed_hits if cast<=t<cutoff)))
    skills = []
    for skill, counts in raw_skills.items():
        skills.append(dict(id=skill, name=skill_names[skill],
                           targets=len(spell_targets[skill]), **counts))
    result = dict(boss=row["boss"], file=path.name, sourceJclSha256=source_sha, seconds=row["seconds"],
        effectiveSeconds=healer["effectiveSeconds"], rdps=healer["rdps"],
        mrdps=healer["mrdps"], hps=healer["hps"], rhps=healer["rhps"],
        panel=healer["panel"], creditedSkills=healer["creditedSkills"], deaths=deaths, recovery=recovery,
        zyhrCasts=intervals, zyhrProcRaw=dict(procs), zyhrProcTargets=dict(proc_targets),
        otherZyhrCasts=other_zyhr_casts,
        sourceWindowsAfterOtherCasts=source_windows,
        procSourceAudit=dict(proc_source_audit), procSourceRanges=proc_source_ranges,
        zyhrCreditsByOcc=[dict(occ=p["occ"], **p["creditedSkills"]["逐云寒蕊(增益)"])
                          for p in row["players"] if "逐云寒蕊(增益)" in p["creditedSkills"]],
        buff20854=dict(events=total_buff_events, eventStatus=dict(buff_events), sources=dict(buff_sources),
                       levels=dict(levels), beforeFirstZyhrCast=before_first_cast,
                       maxInstanceVsTrackerMismatchEvents=mismatches,
                       coveredPlayerSeconds=sum(coverage_ms.values())/1000,
                       meanCoveredPlayers=sum(coverage_ms.values())/duration,
                       meanStacksPerPlayer=sum(stack_ms.values())/duration/len(state),
                       recipients=recipient_data),
        teamDamage=dict(dmg), targetDamage=dict(target_damage),
        skills=sorted(skills, key=lambda s: -s["events"]),
        thirtySecondBins=[dict(start=k*30, **v) for k,v in sorted(bins.items())],
        validation=dict(teamDamageDelta=dmg["all"]-row["directDamage"],
                        creditedProcCountDelta=sum(p["creditedSkills"].get("逐云寒蕊(增益)", {}).get("num", 0) for p in row["players"])-procs["events"],
                        recipientCoverageWithinBounds=all(0 <= ms <= duration for ms in coverage_ms.values())),
        scope="Raw logged NPC hits within the replay start/end; no private player identities exported; coverage uses the same last-event state as current numeric buff accounting")
    del bld
    gc.collect()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("backups/luoyang-20260915/rdps/clear-rdps.json"))
    parser.add_argument("--manifest", type=Path, default=Path("backups/luoyang-20260915/manifest.json"))
    parser.add_argument("--output", type=Path, default=Path("backups/luoyang-20260915/rdps/lingsu-audit.json"))
    args = parser.parse_args()
    report_bytes = args.report.read_bytes()
    report = json.loads(report_bytes)
    report_sha = hashlib.sha256(report_bytes).hexdigest()
    paths = {Path(e["source"]).name:Path(e["source"]) for e in json.loads(args.manifest.read_text(encoding="utf-8-sig"))}
    results = []
    for row in report["results"]:
        result = analyze(row, paths[row["file"]])
        result["reportSnapshotSha256"] = report_sha
        results.append(result)
        print(json.dumps({k:result[k] for k in ("boss", "rdps", "effectiveSeconds", "deaths", "zyhrCasts", "zyhrProcRaw")},ensure_ascii=False), flush=True)
        print(json.dumps({"buff20854":{k:v for k,v in result["buff20854"].items() if k!="recipients"},"teamDamage":result["teamDamage"]},ensure_ascii=False),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()

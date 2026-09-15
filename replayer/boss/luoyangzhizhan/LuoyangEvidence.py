"""Small recording helpers; encounter rules stay in each boss module."""
import tkinter as tk

from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import parseTime


def npc_matches(replayer, npc_id, templates, names=()):
    npc = replayer.bld.info.npc.get(npc_id)
    if npc is None:
        return False
    # Names are only a fallback for logs without a template. Several bosses
    # have identically named, invulnerable mechanics NPCs.
    template = str(npc.templateID)
    return template in templates or (template in ("", "0") and npc.name in names)


def record_target_damage(replayer, event, key):
    if event.caster in replayer.statDict and event.damageEff > 0:
        line = replayer.statDict[event.caster]
        line[key] = line.get(key, 0) + event.damageEff


def record_call_buff(replayer, event, label, icon="341"):
    """Pair observed apply/remove edges; refreshing stacks is not a new call."""
    if event.target not in replayer.statDict:
        return False
    active = replayer.__dict__.setdefault("_luoyangCalls", {})
    key = (event.target, event.id)
    if event.stack > 0:
        if key not in active:
            active[key] = (event.time, label, icon)
            return True
    elif key in active:
        start, label, icon = active.pop(key)
        _close_call(replayer, key, start, event.time, label, icon, False)
    return False


def _close_call(replayer, key, start, end, label, icon, truncated):
    end = min(end, replayer.trimmedFinalTime or replayer.finalTime)
    if end < start:
        return
    target, skill = key
    replayer.bh.setCall(skill, label, icon, start, end - start, target, "机制点名")
    replayer.detail.setdefault("mechanics", []).append({
        "player": replayer.bld.info.getName(target), "playerID": target,
        "id": skill, "name": label, "start": start, "end": end,
        "truncated": truncated,
    })


def finish_calls(replayer):
    for key, (start, label, icon) in replayer.__dict__.get("_luoyangCalls", {}).items():
        _close_call(replayer, key, start, replayer.finalTime, label, icon, True)
    replayer.__dict__.get("_luoyangCalls", {}).clear()


def set_confirmed_win(replayer, event_time, rule):
    """Only call for boss-owned death/chest/end dialogue, never file ordering."""
    replayer.detail.setdefault("winEvidence", []).append({"time": event_time, "rule": rule})
    previous = replayer.__dict__.get("winTime")
    if previous is None or event_time < previous:
        replayer.win = 1
        replayer.winTime = event_time
        replayer.trimmedFinalTime = event_time
        replayer.detail["winReason"] = rule
        replayer.bh.setBadPeriod(event_time, replayer.finalTime, True, True)


def record_environment(replayer, event, mapping):
    """Record only researched encounter skills, with per-ID repeat coalescing."""
    item = mapping.get((event.dataType, str(event.id)))
    if item is None:
        return
    if event.dataType == "Skill" and (event.target not in replayer.statDict or event.damage <= 0):
        return
    key = (event.dataType, event.id)
    if event.time - replayer.bhTime.get(key, -100000) < 3000:
        return
    replayer.bhTime[key] = event.time
    label, icon, color = item
    replayer.bh.setEnvironment(event.id, label, icon, event.time, 0, 1,
                              "运功开始" if event.dataType == "Cast" else "实际命中",
                              event.dataType.lower(), color)


def record_hit(replayer, event, key, label):
    """Observed exposure, never an assertion that the player caused a failure."""
    if event.target not in replayer.statDict or event.damage <= 0:
        return
    seen = replayer.__dict__.setdefault("_luoyangHitTimes", {})
    identity = (event.target, key)
    if event.time - seen.get(identity, -100000) < 500:
        return
    seen[identity] = event.time
    line = replayer.statDict[event.target]
    line[key] = line.get(key, 0) + 1
    replayer.detail.setdefault("mechanicHits", []).append({
        "player": replayer.bld.info.getName(event.target), "playerID": event.target,
        "time": event.time, "id": event.id, "name": label,
        "damage": event.damageEff, "judgement": "仅记录命中，不自动判责",
    })


def record_phase(replayer, time, phase, label):
    if replayer.phase == phase:
        return
    replayer.changePhase(time, phase)
    replayer.detail.setdefault("phaseTransitions", []).append({"time": time, "phase": phase, "name": label})
    replayer.bh.setEnvironment("0", label, "340", time, 0, 1, "事件确认阶段切换", "phase", "#9467bd")


def finalize_evidence(replayer, phase_names, damage_keys=()):
    finish_calls(replayer)
    for counter in replayer.stunCounter.values():
        counter.finalTime = replayer.finalTime
    replayer.detail["win"] = replayer.win
    replayer.detail.setdefault("winReason", "未观测到通关事件")
    replayer.detail["phaseTimes"] = {name: round(replayer.phaseTime[index] / 1000, 3)
                                    for index, name in phase_names.items()}
    duration = max(1, replayer.bh.sumTime("dps"))
    replayer.detail["effectiveTime"] = duration
    for line in replayer.statDict.values():
        for key in damage_keys:
            line[key + "Dps"] = int(line.get(key, 0) * 1000 / duration)
    groups = {}
    for hit in replayer.detail.get("mechanicHits", []):
        groups.setdefault((hit["playerID"], hit["name"]), []).append(hit)
    for (player, name), hits in groups.items():
        times = [parseTime((hit["time"] - replayer.startTime) / 1000) for hit in hits]
        replayer.addPot([replayer.bld.info.getName(player), replayer.occDetailList[player], 0,
                         replayer.bossNamePrint, "%s命中%d次（观察记录）" % (name, len(hits)),
                         ["仅记录日志中实际命中，不据此判定玩家失误。", "时间：" + "、".join(times)], 0])


def render_boss_window(window, title, columns):
    """Shared table layout; labels and encounter columns supplied by the boss."""
    window.constructWindow(title, "1450x850")
    phases = " / ".join("%s %.1f秒" % (name, value)
                         for name, value in window.detail.get("phaseTimes", {}).items())
    tk.Label(window.window, text=("通关" if window.detail.get("win") else "未确认通关") +
             "  |  " + phases + "  |  点名与命中详情见时间轴、战斗事件记录").pack()
    frame = tk.Frame(window.window)
    frame.pack()
    table = TableConstructorMeta(window.config, frame)
    window.constructCommonHeader(table, "")
    for key, label, description in columns:
        table.AppendHeader(label, description)
    table.AppendHeader("心法复盘", "心法专属复盘")
    table.EndOfLine()
    for line in window.effectiveDPSList:
        window.constructCommonLine(table, line)
        for key, label, description in columns:
            table.AppendContext(line.get(key, line.get("battle", {}).get(key, 0)))
        if line["name"] in window.occResult:
            table.GenerateXinFaReplayButton(window.occResult[line["name"]], line["name"])
        else:
            table.AppendContext("")
        table.EndOfLine()
    window.constructNavigator()

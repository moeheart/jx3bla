"""Small recording helpers; encounter rules stay in each boss module."""
import tkinter as tk

from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import parseTime
from data.DataContent import get_reflected_damage


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
        record_stat(replayer, event.time, event.caster, key, event.damageEff)


def reflected_contributions(replayer, event, groups):
    """Classify an evidenced reverse damage component without changing the event."""
    if not replayer.startTime <= event.time <= replayer.finalTime:
        return
    reflected = get_reflected_damage(event, replayer.bld.info)
    if reflected is None:
        return
    player, target, amount = reflected
    if player not in replayer.statDict:
        return
    for key, targets in groups.items():
        matched = targets(target) if callable(targets) else npc_matches(replayer, target, targets)
        if matched:
            yield player, key, amount


def record_reflected_target_damage(replayer, event, groups):
    """Use the same reversible ledger as direct damage, without win evidence."""
    for player, key, amount in reflected_contributions(replayer, event, groups):
        record_stat(replayer, event.time, player, key, amount)


def record_stat(replayer, time, player, key, amount=1):
    """First-three counters retain time so a later cutoff can remove tail events."""
    line = replayer.statDict[player]
    line[key] = line.get(key, 0) + amount
    replayer.__dict__.setdefault("_luoyangContributions", []).append((time, player, key, amount))


def record_call_buff(replayer, event, label, icon="341", stat_key=None):
    """Pair observed apply/remove edges; refreshing stacks is not a new call."""
    if event.target not in replayer.statDict:
        return False
    active = replayer.__dict__.setdefault("_luoyangCalls", {})
    key = (event.target, event.id)
    if event.stack > 0:
        if key not in active:
            active[key] = (event.time, label, icon)
            if stat_key is not None:
                record_stat(replayer, event.time, event.target, stat_key)
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
    cutoff = min(replayer.finalTime, replayer.trimmedFinalTime or replayer.finalTime)
    if event_time > cutoff:
        return
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
    record_stat(replayer, event.time, event.target, key)
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


def record_shout(replayer, event, label):
    """Record dialogue after the encounter has checked speaker and exact content."""
    content = event.content.strip('"')
    key = (str(event.id), content)
    seen = replayer.__dict__.setdefault("_luoyangShoutTimes", {})
    if event.time - seen.get(key, -10**15) < 1000:
        return False
    seen[key] = event.time
    npc = replayer.bld.info.npc.get(event.id)
    replayer.detail.setdefault("shouts", []).append({
        "time": event.time, "name": label, "content": content,
        "sourceTemplate": str(npc.templateID) if npc else "",
    })
    replayer.bh.setEnvironment("0", label, "340", event.time, 0, 1,
                               content, "shout", "#996633")
    return True


def finalize_phase_periods(replayer, phase_names, transitions_key="phaseTransitions"):
    """Keep each observed phase interval, including repeated cycles and cutoffs."""
    start, end = replayer.startTime, replayer.finalTime
    transitions = [{"time": start, "phase": 1, "name": phase_names.get(1, "阶段1")}]
    for entry in sorted(replayer.detail.get(transitions_key, []), key=lambda item: item["time"]):
        if entry.get("phase") not in phase_names or entry["time"] > end:
            continue
        entry = dict(entry, time=max(start, entry["time"]))
        entry.setdefault("name", phase_names[entry["phase"]])
        if entry["time"] == transitions[-1]["time"]:
            transitions[-1] = entry
        elif entry["phase"] != transitions[-1]["phase"]:
            transitions.append(entry)
    periods = []
    for index, entry in enumerate(transitions):
        finish = transitions[index+1]["time"] if index+1 < len(transitions) else end
        if finish <= entry["time"]:
            continue
        periods.append(dict(entry, start=entry["time"], end=finish,
                            duration=round((finish-entry["time"])/1000, 3)))
    replayer.detail["phasePeriods"] = periods
    # A boundary can be confirmed after later events were observed. Rebuild the
    # phase totals from the clipped intervals so summaries and bars agree.
    replayer.phaseTime = [0] * max(len(replayer.phaseTime), max(phase_names, default=0)+1)
    for period in periods:
        replayer.phaseTime[period["phase"]] += period["end"]-period["start"]
    # Existing phase markers become interval bars on the replay timeline.
    by_start = {entry["start"]: entry for entry in periods}
    for entry in replayer.bh.log["environment"]:
        if entry["type"] == "phase" and entry["start"] in by_start:
            entry["duration"] = by_start[entry["start"]]["end"] - entry["start"]
    # All timeline entries obey the same confirmed encounter boundary.
    for key in ("shouts", "phaseTransitions", "phaseChanges"):
        if key in replayer.detail:
            replayer.detail[key] = [entry for entry in replayer.detail[key] if entry["time"] <= end]
    replayer.bh.log["environment"] = [entry for entry in replayer.bh.log["environment"]
                                      if entry["start"] <= end]
    for entry in replayer.bh.log["environment"]:
        entry["duration"] = min(entry["duration"], max(0, end-entry["start"]))


def finalize_evidence(replayer, phase_names, damage_keys=()):
    if replayer.__dict__.get("_luoyangEvidenceFinalized"):
        return
    replayer._luoyangEvidenceFinalized = True
    end = replayer.finalTime
    finish_calls(replayer)
    # Completion and combat-exit evidence can be resolved only after all events
    # are scanned. Closed calls and counters must obey that same late boundary.
    for player, calls in replayer.bh.log["call"].items():
        replayer.bh.log["call"][player] = [entry for entry in calls if entry["start"] <= end]
        for entry in replayer.bh.log["call"][player]:
            entry["duration"] = min(entry["duration"], max(0, end-entry["start"]))
    if "mechanics" in replayer.detail:
        replayer.detail["mechanics"] = [entry for entry in replayer.detail["mechanics"] if entry["start"] <= end]
        for entry in replayer.detail["mechanics"]:
            if entry["end"] > end:
                entry["truncated"] = True
            entry["end"] = max(entry["start"], min(entry["end"], end))
    for time, player, key, amount in replayer.__dict__.pop("_luoyangContributions", []):
        if time > end:
            replayer.statDict[player][key] -= amount
    replayer.detail["mechanicHits"] = [entry for entry in replayer.detail.get("mechanicHits", [])
                                       if entry["time"] <= end]
    finalize_phase_periods(replayer, phase_names)
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
    periods = window.detail.get("phasePeriods", [])
    if periods:
        text = "分段：" + " / ".join("%s %s—%s（%.3f秒）" % (
            entry["name"], parseTime((entry["start"]-periods[0]["start"])/1000),
            parseTime((entry["end"]-periods[0]["start"])/1000), entry["duration"])
            for entry in periods)
        tk.Label(window.window, text=text, wraplength=1400, justify="left").pack()
    transitions = window.detail.get("transitionPeriods", [])
    if transitions:
        tk.Label(window.window, text="转场观测：" + " / ".join(
            "%s %.3f秒%s" % (entry["name"], entry["duration"],
                              "（截至记录结束）" if entry.get("truncated") else "")
            for entry in transitions), wraplength=1400, justify="left").pack()
    # Heroic mechanics add columns and a full 25-player roster can exceed the
    # fixed window height. Keep the entire table reachable at any screen size.
    viewport = tk.Frame(window.window)
    viewport.pack(fill="both", expand=True)
    canvas = tk.Canvas(viewport, height=450, width=1400, highlightthickness=0)
    vertical = tk.Scrollbar(viewport, orient="vertical", command=canvas.yview)
    horizontal = tk.Scrollbar(viewport, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    viewport.rowconfigure(0, weight=1)
    viewport.columnconfigure(0, weight=1)
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    window.statsCanvas = canvas
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
    def bind_scroll(widget):
        widget.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"))
        widget.bind("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(-int(event.delta / 120), "units"))
        for child in widget.winfo_children():
            bind_scroll(child)
    bind_scroll(canvas)
    window.constructNavigator()

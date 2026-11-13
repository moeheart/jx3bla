"""Reward-independent victory evidence observed in formal 25-player JCLs.

The local completion message is corroborated by damage and combat exit from
the same boss entity. Neither generic rewards nor low HP/exit alone is a win.
Candidates are resolved after the event scan so resumed combat invalidates them.
"""
import re


class LuoyangWinEvidence:
    def __init__(self, replayer, boss, templates):
        self.replayer = replayer
        self.boss = boss
        self.templates = templates
        self.lastDamage = {}
        self.exits = {}
        self.departures = {}
        self.pressure = {}
        self.completions = []
        self.mapName = getattr(replayer.bld.info, "map", "")
        difficulty = self.mapName.removesuffix("洛阳之战")
        self.completionPattern = re.compile(
            r"\[全胜！" + re.escape(self.mapName) + r"\]：[1-5]/5，击败" + re.escape(boss)
            + r"！" + re.escape(difficulty) + r"\(完成\)")
        for event in getattr(replayer.bld, "systemMessages", []):
            self.observe(event)

    def template(self, npc_id):
        npc = self.replayer.bld.info.npc.get(npc_id)
        return str(npc.templateID) if npc else ""

    def observe(self, event):
        if (self.mapName not in ("25人普通洛阳之战", "25人英雄洛阳之战")
                or getattr(self.replayer.bld.info, "map", "") != self.mapName):
            return
        if (event.dataType == "Skill" and event.caster in self.replayer.statDict
                and self.template(event.target) in self.templates and event.damageEff > 0):
            self.lastDamage[event.target] = event.time
            self.exits.pop(event.target, None)
            self.departures.pop(event.target, None)
            self.pressure.pop(event.target, None)
        elif event.dataType == "Battle" and self.template(event.id) in self.templates:
            if event.fight:
                self.lastDamage.pop(event.id, None)
                self.exits.pop(event.id, None)
                self.departures.pop(event.id, None)
                self.pressure.pop(event.id, None)
            elif (event.id in self.lastDamage
                  and 0 <= event.time - self.lastDamage[event.id] <= 5000):
                self.exits[event.id] = event.time
        elif (self.mapName == "25人英雄洛阳之战" and self.boss == "突利和顺"
              and event.dataType == "Scene" and self.template(event.id) in self.templates):
            # Heroic Tuli has a delayed despawn but no Battle exit. Resets,
            # reappearances and later damage invalidate this candidate.
            if event.enter:
                self.lastDamage.pop(event.id, None)
                self.exits.pop(event.id, None)
                self.pressure.pop(event.id, None)
                self.departures.pop(event.id, None)
            elif event.id in self.lastDamage:
                self.departures[event.id] = event.time
        elif (event.dataType == "System" and event.channel == "MSG_SYS"
              and self.completionPattern.fullmatch(event.content.replace("\\n", "\n").strip())):
            self.completions.append(event.time)
        elif (self.boss == "阿史那承庆"
              and event.dataType == "Buff" and event.id == "35875"
              and self.template(event.caster) in self.templates
              and event.target in self.replayer.statDict
              and event.stack > 0 and getattr(event, "isValid", False)
              and getattr(event, "delete", "true") in (False, "false", 0)
              and isinstance(getattr(event, "frame", None), int)
              and isinstance(getattr(event, "end", None), int)
              and event.end - event.frame > 60 * 16
              and event.caster in self.lastDamage
              and 0 <= event.time - self.lastDamage[event.caster] <= 5000):
            self.pressure.setdefault(event.caster, {
                "pressureTime": event.time, "remainingFrames": event.end - event.frame})

    def resolve(self):
        candidates = []
        for npc_id, time in self.exits.items():
            last = self.lastDamage[npc_id]
            for completion in self.completions:
                if 0 <= completion - last <= 5000 and abs(time - completion) <= 5000:
                    candidates.append({"time": time, "rule": "boss_completion_and_combat_exit",
                                       "npcID": npc_id, "template": self.template(npc_id),
                                       "lastMainDamage": last, "completionTime": completion})
                    break
        for npc_id, pressure in self.pressure.items():
            candidate = dict(pressure, time=self.exits.get(npc_id, pressure["pressureTime"]),
                             rule="long_pressure_buff", npcID=npc_id,
                             template=self.template(npc_id), lastMainDamage=self.lastDamage[npc_id])
            if self.mapName == "25人英雄洛阳之战":
                matching = [completion for completion in self.completions
                            if 0 <= completion - self.lastDamage[npc_id] <= 5000
                            and abs(completion - pressure["pressureTime"]) <= 5000]
                if not matching:
                    continue
                candidate.update(rule="long_pressure_and_boss_completion", completionTime=min(matching))
            candidates.append(candidate)
        for npc_id, departure in self.departures.items():
            last = self.lastDamage[npc_id]
            for completion in self.completions:
                if 0 <= completion - last <= 5000 and 0 <= departure - completion <= 10000:
                    candidates.append({"time": completion, "rule": "boss_completion_and_scene_exit",
                                       "npcID": npc_id, "template": self.template(npc_id),
                                       "lastMainDamage": last, "completionTime": completion,
                                       "departureTime": departure})
                    break
        # An earlier reset/wipe cutoff must never be promoted by later evidence.
        cutoff = min(self.replayer.finalTime,
                     self.replayer.trimmedFinalTime or self.replayer.finalTime)
        candidates = [row for row in candidates if self.replayer.startTime <= row["time"] <= cutoff]
        return min(candidates, key=lambda row: row["time"]) if candidates else None

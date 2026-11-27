"""Reward-independent victory evidence observed in formal 25-player JCLs.

Local completion or exact native seasonal boss-credit messages are corroborated
by damage and combat exit from the same boss entity. Tuli can also leave a
boss corpse at his recorded position shortly after the final hit.
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
        self.honors = []
        self.mapName = getattr(replayer.bld.info, "map", "")
        difficulty = self.mapName.removesuffix("洛阳之战")
        self.completionPattern = re.compile(
            r"\[全胜！" + re.escape(self.mapName) + r"\]：[1-5]/5，击败" + re.escape(boss)
            + r"！" + re.escape(difficulty) + r"\(完成\)")
        # Observed in normal and heroic clears even when the once-completed
        # full-clear task no longer emits its message. These are boss credits,
        # not arbitrary seasonal progress, rewards or plugin announcements.
        self.honorPattern = re.compile(
            r"赛季荣誉\[" + re.escape(difficulty)
            + r"首领击伤·(入门|精通|大师)\]：([1-9][0-9]*)/([1-9][0-9]*)")
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
        elif event.dataType == "Scene" and self.template(event.id) in self.templates:
            # Tuli can disappear several seconds after defeat without a Battle exit.
            if event.enter:
                self.lastDamage.pop(event.id, None)
                self.exits.pop(event.id, None)
                self.pressure.pop(event.id, None)
                self.departures.pop(event.id, None)
            elif self.boss == "突利和顺" and event.id in self.lastDamage:
                self.departures[event.id] = event.time
        elif event.dataType == "System" and event.channel == "MSG_SYS":
            content = event.content.replace("\\n", "\n").strip()
            if self.completionPattern.fullmatch(content):
                self.completions.append(event.time)
            elif self.boss in ("突利和顺", "田承嗣", "阿史那承庆", "史朝义"):
                match = self.honorPattern.fullmatch(content)
                if match:
                    tier, progress, target = match.groups()
                    progress, target = int(progress), int(target)
                    if (target == {"入门": 15, "精通": 25, "大师": 50}[tier] and progress <= target
                            and (tier != "大师" or self.boss == "突利和顺")):
                        self.honors.append({"honorTime": event.time, "honorContent": content,
                                            "honorTier": tier, "honorProgress": progress,
                                            "honorTarget": target})
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
                # An exact map/boss completion can arrive after the combat
                # cutoff. The corroborated boss exit defines the clear time.
                if 0 <= completion - last <= 5000 and abs(time - completion) <= 5000:
                    candidates.append({"time": time, "rule": "boss_completion_and_combat_exit",
                                       "npcID": npc_id, "template": self.template(npc_id),
                                       "lastMainDamage": last, "completionTime": completion})
                    break
            if self.boss == "突利和顺":
                continue  # Its seasonal credit is corroborated by a corpse or scene departure below.
            for honor in self.honors:
                if (0 <= honor["honorTime"] - last <= 5000
                        and abs(time - honor["honorTime"]) <= 5000
                        and (not self.replayer.trimmedFinalTime
                             or honor["honorTime"] <= self.replayer.trimmedFinalTime)):
                    # System messages can arrive after log[-1], but evidence
                    # after an explicit reset/wipe cutoff cannot revive it.
                    candidates.append(dict(honor, time=time,
                        rule="seasonal_boss_credit_and_combat_exit", npcID=npc_id,
                        template=self.template(npc_id), lastMainDamage=last))
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
        if not candidates and self.boss == "突利和顺":
            candidates = list(self._tuli_victories(cutoff))
        return min(candidates, key=lambda row: row["time"]) if candidates else None

    def _tuli_victories(self, cutoff):
        """A new boss corpse at Tuli's position, or boss credit followed by his despawn."""
        if self.mapName not in ("25人普通洛阳之战", "25人英雄洛阳之战"):
            return
        spawns = getattr(self.replayer.bld, "tuliCorpseSpawns", ())
        log = getattr(self.replayer.bld, "log", ())
        # World metadata may follow the final combat event. It can confirm a kill
        # at the end of the recording, but cannot override an explicit cutoff.
        at_recording_end = not self.replayer.trimmedFinalTime and log and log[-1].time == cutoff
        for npc_id, last in self.lastDamage.items():
            if not self.replayer.startTime <= last <= cutoff:
                continue
            latest = last + 5000 if at_recording_end else min(last + 5000, cutoff)
            corpse = next(((time, obj) for time, boss, obj in spawns
                           if boss == npc_id and last <= time <= latest), None)
            departure = self.departures.get(npc_id)
            honor = next((row for row in self.honors if last <= row["honorTime"] <= latest
                          and (corpse or (departure is not None and
                               0 <= departure - row["honorTime"] <= 10000 and departure <= cutoff))), None)
            if not corpse and not honor:
                continue
            result = dict(npcID=npc_id, template=self.template(npc_id), lastMainDamage=last)
            if departure is not None and departure <= cutoff:
                result["departureTime"] = departure
            if corpse:
                result.update(time=min(corpse[0], cutoff), rule="boss_corpse_at_main_position",
                              corpseTime=corpse[0], corpseID=corpse[1], corpseTemplate="1392")
            else:
                result["rule"] = "seasonal_boss_credit_and_scene_exit"
            if honor:
                result.update(honor)
                result["time"] = min(result.get("time", honor["honorTime"]), honor["honorTime"])
            yield result

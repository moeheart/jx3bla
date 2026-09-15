"""Small recording helpers shared by the two final Luoyang encounters."""
import tkinter as tk

from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from tools.Functions import parseTime
from replayer.boss.luoyangzhizhan.LuoyangEvidence import record_call_buff, finish_calls, render_boss_window


class EncounterWindow(SpecificBossWindow):
    COLUMNS = ()
    TITLE = "洛阳之战"

    def loadWindow(self):
        render_boss_window(self, self.TITLE, self.COLUMNS)
        tk.Label(self.window, text=self.detail.get("mechanicNote", ""), wraplength=1250,
                 justify="left").pack()


class EncounterReplayer(GeneralReplayer):
    """Bookkeeping only; each boss implements its own phase/win/mechanic rules."""
    BOSS = ""
    MAIN_IDS = ()

    def initBattle(self):
        super().initBattle()
        self.activeBoss = self.BOSS
        self.lastHits = {}
        self.confirmedEnd = None
        self.detail["mechanicEvents"] = []
        self.detail["winEvidence"] = []
        self.finalized = False
        self.lastMainDamage = None
        self.damageContributions = []
        # Identity exists independently of whether the party managed to hit it.
        for npc_id in self.bld.info.npc:
            if self.template(npc_id) in self.MAIN_IDS:
                self.bh.setMainTarget(npc_id)

    def template(self, npc_id):
        npc = self.bld.info.npc.get(npc_id)
        return str(npc.templateID) if npc else ""

    def increment(self, player, key, amount=1):
        if player in self.statDict:
            stats = self.statDict[player]["battle"]
            stats[key] = stats.get(key, 0) + amount

    def recordDamage(self, event, targets, key):
        if (event.caster in self.statDict and self.template(event.target) in targets
                and event.damageEff > 0):
            self.recordContribution(event, key)
            if targets == self.MAIN_IDS:
                self.lastMainDamage = event.time
                self.bh.setMainTarget(event.target)
            return True
        return False

    def recordContribution(self, event, key):
        self.increment(event.caster, key, event.damageEff)
        self.damageContributions.append((event.time, event.caster, key, event.damageEff))

    def callBuff(self, event, label, icon="341"):
        return record_call_buff(self, event, label, icon)

    def observedHit(self, event, key, label, cooldown=1000):
        """Record the victim and source without assigning responsibility."""
        if event.target not in self.statDict or event.damage <= 0:
            return False
        hitkey = (event.target, key)
        if event.time - self.lastHits.get(hitkey, -10**15) < cooldown:
            return False
        self.lastHits[hitkey] = event.time
        self.increment(event.target, key)
        self.detail["mechanicEvents"].append({
            "time": event.time, "player": self.bld.info.getName(event.target),
            "playerID": event.target,
            "skill": event.id, "mechanic": label, "damage": event.damage,
            "kind": "hit", "responsibility": "未据此判定"})
        return True

    def confirmedFailure(self, player, time, label, evidence):
        self.detail["mechanicEvents"].append({
            "time": time, "player": self.bld.info.getName(player),
            "mechanic": label, "kind": "failure", "evidence": evidence})
        self.addPot([self.bld.info.getName(player), self.occDetailList[player], 1,
                     self.bossNamePrint, "%s %s" % (parseTime((time-self.startTime)/1000), label),
                     [evidence], 0])

    def confirmWin(self, time, rule):
        evidence = {"time": time, "rule": rule}
        if evidence not in self.detail["winEvidence"]:
            self.detail["winEvidence"].append(evidence)
        if self.confirmedEnd is None or time < self.confirmedEnd:
            self.confirmedEnd = time
            self.trimmedFinalTime = time
        self.win = 1
        self.detail["winReason"] = rule

    def encounterEnd(self):
        end = min(self.finalTime, self.trimmedFinalTime or self.finalTime,
                  self.confirmedEnd if self.confirmedEnd is not None else self.finalTime)
        return max(self.startTime, end)

    def finishEncounter(self):
        """Run before General's finalization, retaining original history bounds."""
        end = self.encounterEnd()
        self.finalTime = end
        finish_calls(self)
        if end < self.bh.finalTime:
            self.bh.setBadPeriod(end, self.bh.finalTime, True, True)
        # A reward can precede the confirming departure. Close/removal events and
        # add damage observed in that short gap must honor the earlier cutoff too.
        for player, calls in self.bh.log["call"].items():
            self.bh.log["call"][player] = [entry for entry in calls if entry["start"] <= end]
            for entry in self.bh.log["call"][player]:
                entry["duration"] = min(entry["duration"], max(0, end-entry["start"]))
        for key in ("mechanics", "soulPeriods", "constructPeriods", "shaPeriods"):
            if key in self.detail:
                self.detail[key] = [entry for entry in self.detail[key] if entry["start"] <= end]
                for entry in self.detail[key]:
                    if key == "mechanics" and entry["end"] > end:
                        entry["truncated"] = True
                    entry["end"] = max(entry["start"], min(entry["end"], end))
        for time, player, key, amount in self.damageContributions:
            if time > end:
                self.increment(player, key, -amount)
        self.battleTime = max(0, self.finalTime-self.startTime)
        self.detail["win"] = self.win
        self.detail.setdefault("winReason", "未观测到通关事件")
        self.detail["effectiveTime"] = self.battleTime
        for counter in self.stunCounter.values():
            counter.finalTime = self.finalTime
        observations = {}
        for entry in self.detail["mechanicEvents"]:
            if entry["kind"] == "hit":
                observations.setdefault((entry["playerID"], entry["mechanic"]), []).append(entry["time"])
        for (player, label), times in observations.items():
            self.addPot([self.bld.info.getName(player), self.occDetailList[player], 0,
                         self.bossNamePrint, "%s受击%d次（观察记录）" % (label, len(times)),
                         ["受击者未必是机制责任人，本条不判责。", "时间：" + "、".join(
                             parseTime((time-self.startTime)/1000) for time in times)], 0])
        for stats in self.statDict.values():
            stats["battle"]["mainDps"] = int(stats["battle"].get("mainDamage", 0) * 1000 /
                                               max(1, self.battleTime))

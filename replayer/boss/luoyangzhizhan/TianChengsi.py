"""田承嗣：本体/天陨巨剑、军阵点名、承剑控制与真实通关证据。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, finalize_evidence, render_boss_window,
)


class TianChengsiWindow(SpecificBossWindow):
    def loadWindow(self):
        render_boss_window(self, "田承嗣", [
            ("bossDamageDps", "本体DPS", "田承嗣本体有效伤害/有效战斗时间。"),
            ("swordDamageDps", "巨剑DPS", "天陨巨剑有效伤害/有效战斗时间；不混入本体。"),
            ("arrowCalls", "鸣镝点名", "鸣镝连珠点名次数。"),
            ("hammerCalls", "千钧点名", "千钧锤落点名次数；不能仅凭点名判责。"),
            ("swordCalls", "承剑次数", "以身承剑的点名次数；控制区间计入个人被控。"),
            ("slashHits", "横斩命中", "断岳横斩实际命中，观察记录。"),
        ])


class TianChengsiReplayer(GeneralReplayer):
    MAIN = ("139329",)
    SWORD = ("140384",)
    SOURCES = MAIN + SWORD + ("139341", "139343", "139345", "139338", "139334")
    ENVIRONMENT = {
        ("Cast", "45972"): ("断岳横斩", "2123", "#cc5533"),
        ("Cast", "46424"): ("天陨一剑", "2123", "#aa3377"),
        ("Skill", "46030"): ("鸣镝连珠", "340", "#aa8833"),
        ("Skill", "45971"): ("雷霆震岳", "2123", "#7755aa"),
        ("Skill", "46016"): ("千钧锤落", "2123", "#cc7733"),
        ("Skill", "45989"): ("千钧之压", "2123", "#aa5555"),
        ("Skill", "46095"): ("苍天坠剑", "2123", "#aa3377"),
        ("Skill", "46001"): ("枪林突刺", "340", "#3377aa"),
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "田承嗣"
        self.initPhase(4, 1)
        self.openingSeen = False
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "交战"}]
        self.detail["swords"] = []
        self.swordRecords = {}
        self.detail["limitations"] = "按喊话、巨剑出场与重伤划段；受击只作观察，不推断重叠分摊的责任人。"
        for npc_id in self.bld.info.npc:
            if npc_matches(self, npc_id, self.MAIN):
                self.bh.setMainTarget(npc_id)

    def analyseSecondStage(self, event):
        if event.dataType in ("Scene", "Death"):
            if npc_matches(self, event.id, ("140050",)) and (event.dataType == "Death" or event.enter):
                set_confirmed_win(self, event.time, "田承嗣专属宝箱")
            elif event.dataType == "Death" and npc_matches(self, event.id, self.MAIN):
                set_confirmed_win(self, event.time, "田承嗣本体重伤")
        if (self.win and event.time > self.winTime) or event.time > self.detail.get("resetTime", event.time):
            return
        if event.dataType == "Shout" and npc_matches(self, event.id, self.MAIN):
            content = event.content.strip('"')
            if content == "小看你们了，狼牙军，全军准备！":
                record_phase(self, event.time, 2, "全军准备")
            elif content == "来战！正好让本将看看唐廷的斤两！":
                if self.openingSeen and event.time - self.startTime > 10000:
                    self.detail["resetTime"] = event.time
                    self.trimmedFinalTime = event.time
                    self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.openingSeen = True
        elif event.dataType in ("Scene", "Death") and npc_matches(self, event.id, self.SWORD):
            if event.dataType == "Scene" and event.enter:
                record_phase(self, event.time, 3, "天陨巨剑")
                self.swordRecords[event.id] = {"start": event.time, "end": None, "killed": False}
            elif event.dataType == "Death":
                record = self.swordRecords.setdefault(event.id, {"start": self.startTime})
                record.update(end=event.time, killed=True)
                record_phase(self, event.time, 4, "巨剑击破后")
        elif event.dataType == "Skill":
            if npc_matches(self, event.target, self.MAIN):
                record_target_damage(self, event, "bossDamage")
            elif npc_matches(self, event.target, self.SWORD):
                record_target_damage(self, event, "swordDamage")
            if npc_matches(self, event.caster, self.SOURCES):
                record_environment(self, event, self.ENVIRONMENT)
                if event.id == "45972":
                    record_hit(self, event, "slashHits", "断岳横斩")
                elif event.id == "46001":
                    record_hit(self, event, "spearHits", "枪林突刺")
        elif event.dataType == "Cast" and npc_matches(self, event.caster, self.SOURCES):
            record_environment(self, event, self.ENVIRONMENT)
        elif event.dataType == "Buff" and npc_matches(self, event.caster, self.SOURCES):
            calls = {"34255": ("鸣镝连珠", "340", "arrowCalls"),
                     "34254": ("千钧锤落", "2123", "hammerCalls"),
                     "34329": ("以身承剑", "2123", "swordCalls")}
            if event.id in calls:
                label, icon, key = calls[event.id]
                if record_call_buff(self, event, label, icon):
                    self.statDict[event.target][key] = self.statDict[event.target].get(key, 0) + 1
                if event.id == "34329" and event.target in self.stunCounter:
                    self.stunCounter[event.target].setState(event.time, int(event.stack > 0))

    def countFinal(self):
        for npc_id, record in self.swordRecords.items():
            self.detail["swords"].append(dict(record, npcID=npc_id,
                                             duration=((record.get("end") or self.finalTime) - record["start"]) / 1000))
        super().countFinal()
        finalize_evidence(self, {1: "交战", 2: "全军准备", 3: "天陨巨剑", 4: "巨剑击破后"},
                          ("bossDamage", "swordDamage"))

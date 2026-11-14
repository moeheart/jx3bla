"""田承嗣：本体/天陨巨剑、军阵点名、承剑控制与真实通关证据。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.WinEvidence import LuoyangWinEvidence
from replayer.boss.luoyangzhizhan.FirstThreeDowntime import FirstThreeDowntime
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_reflected_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, record_shout, finalize_evidence, render_boss_window,
)


class TianChengsiWindow(SpecificBossWindow):
    def loadWindow(self):
        render_boss_window(self, "田承嗣", [
            ("bossDamageDps", "本体DPS", "田承嗣本体有效伤害/有效战斗时间。"),
            ("swordDamageDps", "巨剑DPS", "天陨巨剑有效伤害/有效战斗时间；不混入本体。"),
            ("arrowCalls", "鸣镝点名", "鸣镝连珠点名次数。"),
            ("hammerCalls", "千钧点名", "千钧锤落点名次数；不能仅凭点名判责。"),
            ("swordCalls", "承剑次数", "普通按34329、英雄按34866实际承剑气劲计数；重叠气劲的控制时间合并。"),
            ("slashHits", "横斩命中", "断岳横斩实际命中，观察记录。"),
            ("spearHits", "突刺命中", "枪林突刺实际命中，观察记录。"),
        ])


class TianChengsiReplayer(GeneralReplayer):
    MAIN = ("139329", "139382")
    SWORD = ("140384", "140386", "141799")
    SOURCES = MAIN + SWORD + ("139341", "139343", "139345", "139338", "139334",
                              "139392", "139393", "139396")
    ENVIRONMENT = {
        ("Cast", "45972"): ("断岳横斩", "2123", "#cc5533"),
        ("Cast", "45972", 2): ("裂剑·前式", "2031", "#b91c1c"),
        ("Cast", "45972", 3): ("裂剑·前式", "2031", "#b91c1c"),
        ("Cast", "46424"): ("天陨一剑", "2123", "#aa3377"),
        ("Cast", "45976"): ("裂剑·回式", "2123", "#aa3377"),
        ("Skill", "46030"): ("鸣镝连珠", "340", "#aa8833"),
        ("Skill", "46030", 2): ("三军围猎", "2033", "#0369a1"),
        ("Skill", "45971"): ("雷霆震岳", "2123", "#7755aa"),
        ("Skill", "46016"): ("千钧锤落", "2123", "#cc7733"),
        ("Skill", "46439"): ("千钧锤落", "2123", "#cc7733"),
        ("Skill", "45989"): ("电扫千军", "4516", "#a16207"),
        ("Skill", "45989", 4): ("千钧之压", "4516", "#a16207"),
        ("Skill", "46095"): ("苍天坠剑", "2123", "#aa3377"),
        # Heroic 46438 pressure / 46557 wave are continuing components of the
        # sword phase, already marked by its cast and actual sword appearance.
        ("Skill", "46438"): ("苍天坠剑", "16396", "#7e22ce", {"burstGap": 5000}),
        ("Skill", "46557"): ("苍天坠剑", "16396", "#7e22ce", {"burstGap": 5000}),
        ("Skill", "46001"): ("枪林突刺", "340", "#3377aa"),
    }

    SHOUTS = {
        "来战！正好让本将看看唐廷的斤两！": "开战",
        "长枪兵！列阵准备，捅穿他们！": "长枪兵列阵",
        "弓箭手！放箭！一个活口都别留！": "弓箭手放箭",
        "狼牙军！听我号令！": "狼牙军号令",
        "抬头看好了——这一剑，送你们上路！": "天陨一剑准备",
        "小看你们了，狼牙军，全军准备！": "全军准备",
        "垂死挣扎！将士们，给我砸碎他们！": "军阵号令·砸碎",
        "呵呵，就这点本事？将士们，给我捅穿了他们！": "军阵号令·捅穿",
        "看你们能撑多久！将士们，给我射穿他们！": "军阵号令·射穿",
        "骨朵兵！连甲带人，给老子砸烂！": "骨朵兵列阵",
        "哼哼！不错，那么第二剑呢？": "第二剑准备",
        "还有一剑！": "裂剑·回式",
        "呵，不自量力！将士们，全军压上，谁也别想逃！": "军阵号令·全军压上",
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "田承嗣"
        self.victoryEvidence = LuoyangWinEvidence(self, self.activeBoss, self.MAIN)
        self.initPhase(5, 1)
        self.lastMainDamage = None
        self.combatEndCandidate = None
        self.openingSeen = False
        self.heroic = any(npc_matches(self, npc_id, ("139382",)) for npc_id in self.bld.info.npc)
        self.controlBuffs = {player: set() for player in self.statDict}
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "交战"}]
        self.detail["swords"] = []
        self.swordRecords = {}
        self.downtime = FirstThreeDowntime(self, 'tian')
        self.detail["limitations"] = "按喊话、巨剑出场与重伤划段；仅巨剑准备喊话至实体出场且无有效伤害的区间扣除输出时间，巨剑与军阵交战及治疗时间保留；普通脱战不单独判胜。"
        for npc_id in self.bld.info.npc:
            if npc_matches(self, npc_id, self.MAIN):
                self.bh.setMainTarget(npc_id)

    def analyseSecondStage(self, event):
        self.victoryEvidence.observe(event)
        if event.dataType in ("Scene", "Death"):
            if npc_matches(self, event.id, ("140050", "140091")) and (event.dataType == "Death" or event.enter):
                set_confirmed_win(self, event.time, "田承嗣专属宝箱")
            elif event.dataType == "Death" and npc_matches(self, event.id, self.MAIN):
                set_confirmed_win(self, event.time, "田承嗣本体重伤")
        if (self.win and event.time > self.winTime) or event.time > self.detail.get("resetTime", event.time):
            return
        self.downtime.observe(event)
        if event.dataType == "Shout" and npc_matches(self, event.id, self.MAIN):
            content = event.content.strip('"')
            label = self.SHOUTS.get(content)
            if label:
                record_shout(self, event, label)
            if content in ("抬头看好了——这一剑，送你们上路！", "哼哼！不错，那么第二剑呢？"):
                record_phase(self, event.time, 5, "天陨一剑准备")
            elif content == "小看你们了，狼牙军，全军准备！":
                record_phase(self, event.time, 2, "全军准备")
            elif content == "来战！正好让本将看看唐廷的斤两！":
                if self.openingSeen and event.time - self.startTime > 10000:
                    self.detail["resetTime"] = event.time
                    self.trimmedFinalTime = event.time
                    self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.openingSeen = True
        elif event.dataType == "Battle" and npc_matches(self, event.id, self.MAIN):
            if event.fight:
                self.combatEndCandidate = None
            elif (self.lastMainDamage is not None and
                  0 <= event.time - self.lastMainDamage <= 5000 and
                  event.time - self.startTime > 10000):
                self.combatEndCandidate = event.time
        elif event.dataType in ("Scene", "Death") and npc_matches(self, event.id, self.SWORD):
            if event.dataType == "Scene" and event.enter:
                record_phase(self, event.time, 3, "天陨巨剑")
                self.swordRecords[event.id] = {"start": event.time, "end": None, "killed": False}
            elif event.dataType == "Death":
                record = self.swordRecords.setdefault(event.id, {"start": self.startTime})
                record.update(end=event.time, killed=True)
                record_phase(self, event.time, 4, "巨剑击破后")
        elif event.dataType == "Skill":
            record_reflected_target_damage(self, event, {"bossDamage": self.MAIN, "swordDamage": self.SWORD})
            if npc_matches(self, event.target, self.MAIN):
                record_target_damage(self, event, "bossDamage")
                if event.caster in self.statDict and event.damageEff > 0:
                    self.lastMainDamage = event.time
                    self.combatEndCandidate = None
            elif npc_matches(self, event.target, self.SWORD):
                record_target_damage(self, event, "swordDamage")
            if npc_matches(self, event.caster, self.SOURCES):
                record_environment(self, event, self.ENVIRONMENT)
                if event.id == "45972":
                    record_hit(self, event, "slashHits", "断岳横斩")
                elif event.id == "46001":
                    record_hit(self, event, "spearHits", "枪林突刺")
        elif event.dataType == "Cast" and npc_matches(self, event.caster, self.SOURCES):
            if event.id != '46424' or npc_matches(self, event.caster, self.MAIN):
                record_environment(self, event, self.ENVIRONMENT)
        elif event.dataType == "Buff" and npc_matches(self, event.caster, self.SOURCES):
            calls = {"34255": ("鸣镝连珠", "340", "arrowCalls"),
                     "34254": ("千钧锤落", "2123", "hammerCalls"),
                     "34329": ("承剑准备" if self.heroic else "以身承剑", "2123",
                               "swordPreparationCalls" if self.heroic else "swordCalls"),
                     "34866": ("以身承剑", "2123", "swordCalls")}
            if event.id in calls:
                label, icon, key = calls[event.id]
                record_call_buff(self, event, label, icon, stat_key=key)
                if event.id in ("34329", "34866") and event.target in self.stunCounter:
                    active = self.controlBuffs[event.target]
                    if event.stack > 0:
                        active.add(event.id)
                    else:
                        active.discard(event.id)
                    self.stunCounter[event.target].setState(event.time, int(bool(active)))

    def trimTime(self):
        evidence = self.victoryEvidence.resolve()
        if evidence is not None and not self.win and not self.detail.get("resetTime"):
            set_confirmed_win(self, evidence["time"], evidence["rule"])
            self.detail["winEvidence"][-1].update(evidence)
        if self.combatEndCandidate is not None and not self.win and not self.detail.get("resetTime"):
            self.trimmedFinalTime = min(self.trimmedFinalTime or self.combatEndCandidate,
                                        self.combatEndCandidate)
            self.detail["combatEndEvidence"] = {
                "time": self.combatEndCandidate,
                "rule": "近期本体有效伤害后本体脱战；仅裁剪尾录，未据此确认通关",
            }
            self.bh.setBadPeriod(self.combatEndCandidate, self.finalTime, True, True)
        return super().trimTime()

    def countFinal(self):
        if self.__dict__.get("_luoyangEvidenceFinalized"):
            return
        self.downtime.finalize()
        for npc_id, record in self.swordRecords.items():
            if record["start"] > self.finalTime:
                continue
            observed_end = record.get("end")
            end = min(observed_end or self.finalTime, self.finalTime)
            self.detail["swords"].append(dict(
                record, npcID=npc_id, end=end,
                killed=bool(record.get("killed") and observed_end is not None and observed_end <= self.finalTime),
                truncated=observed_end is None or observed_end > self.finalTime,
                duration=max(0, end-record["start"]) / 1000))
        super().countFinal()
        finalize_evidence(self, {1: "交战", 2: "全军准备", 3: "天陨巨剑", 4: "巨剑击破后", 5: "天陨一剑准备"},
                          ("bossDamage", "swordDamage"))

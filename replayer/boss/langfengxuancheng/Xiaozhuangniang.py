import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.boss.langfengxuancheng.WinEvidence import append_unique, filter_relevant_candidates, \
    filter_chest_candidates, filter_tail_scene_candidates, build_damage_candidates, build_recommendation, \
    format_evidence_report
from replayer.boss.langfengxuancheng.TimelineDebug import recordDebugShout, printDebugTimeline
from replayer.boss.langfengxuancheng.Trivia import LangfengTriviaRecorder


class XiaozhuangniangWindow(SpecificBossWindow):

    def loadWindow(self):
        self.constructWindow("笑妆娘", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        tb = TableConstructorMeta(self.config, frame1)
        self.constructCommonHeader(tb, "")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for line in self.effectiveDPSList:
            self.constructCommonLine(tb, line)
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class XiaozhuangniangReplayer(GeneralReplayer):
    TARGET_HP = 22117633925
    DAMAGE_THRESHOLD = 0.98
    BH_BLACKLIST_EXTRA = [
        "s44021",  # 普通攻击
        "s44149",  # 与读条同名的命中事件，时间轴保留读条
        "s44589",  # 与读条同名的后续伤害
        "b33259",
    ]
    BH_INFO = {
        "s44022": ["2019", "#ff5555", 0],   # 祭跪双坟
        "b32976": ["3330", "#3355ff", 0],   # 灵簪锁魂
        "c44238": ["3330", "#3355ff", 0],   # 灵簪锁魂
        "c44290": ["12449", "#ff00aa", 0],  # 悲音恸潮
    }

    def recordDeath(self, item, deathSource):
        pass

    def recordTriviaDeath(self, event):
        if self.triviaRecorder.enabled and event.id in self.bld.info.player:
            self.triviaRecorder.record_event("Dead", self.bld.info.getName(event.id), event.time)

    def collectShoutCandidates(self, event):
        if event.content not in ['""', ""]:
            append_unique(self.shoutCandidates, {"time": event.time, "content": event.content})

    def collectDeathCandidates(self, event):
        if event.id in self.bld.info.npc:
            npc = self.bld.info.npc[event.id]
            append_unique(self.deathCandidates, {
                "time": event.time,
                "npcID": event.id,
                "name": self.bld.info.getName(event.id),
                "templateID": npc.templateID,
            })

    def collectChestCandidates(self, event):
        if event.id in self.bld.info.npc and event.enter:
            npc = self.bld.info.npc[event.id]
            name = self.bld.info.getName(event.id)
            item = {
                "time": event.time,
                "npcID": event.id,
                "name": name,
                "templateID": npc.templateID,
                "enter": event.enter,
            }
            append_unique(self.chestCandidates, item)
            if name in self.chestNames and self.chestWinTime == 0:
                self.chestWinTime = event.time

    def collectSceneCandidates(self, event):
        if event.id in self.bld.info.npc:
            npc = self.bld.info.npc[event.id]
            append_unique(self.sceneCandidates, {
                "time": event.time,
                "npcID": event.id,
                "name": self.bld.info.getName(event.id),
                "templateID": npc.templateID,
                "enter": event.enter,
            })

    def collectDamageCandidates(self, event):
        if event.caster not in self.bld.info.player or event.target not in self.bld.info.npc or event.damageEff <= 0:
            return

        npc = self.bld.info.npc[event.target]
        if event.target not in self.damageByNpc:
            self.damageByNpc[event.target] = {
                "npcID": event.target,
                "name": self.bld.info.getName(event.target),
                "templateID": npc.templateID,
                "damage": 0,
                "lastTime": 0,
            }
        self.damageByNpc[event.target]["damage"] += event.damageEff
        self.damageByNpc[event.target]["lastTime"] = event.time

        if npc.templateID == self.mainBossTemplateID:
            self.mainBossDamage += event.damageEff
            if self.damageFallbackTime == 0 and self.mainBossDamage >= self.TARGET_HP * self.DAMAGE_THRESHOLD:
                self.damageFallbackTime = event.time

    def resolveWinCondition(self):
        if self.resolvedWinReason is not None:
            return

        if self.chestWinTime:
            self.resolvedWinReason = {
                "rule": "chest",
                "eventTime": self.chestWinTime,
                "trimTime": 0,
                "backupRule": "damage",
                "needShoutHook": 1,
            }
        elif self.damageFallbackTime:
            self.resolvedWinReason = {
                "rule": "damage",
                "eventTime": self.damageFallbackTime,
                "trimTime": self.damageFallbackTime,
                "backupRule": "",
                "needShoutHook": 1,
            }

    def trimTime(self):
        self.resolveWinCondition()
        if self.resolvedWinReason is not None and self.resolvedWinReason["trimTime"] != 0:
            self.trimmedFinalTime = self.resolvedWinReason["trimTime"]
        return super().trimTime()

    def recordMainTarget(self, event):
        if self.mainTargetRecorded:
            return
        if event.dataType != "Skill":
            return
        if event.caster not in self.bld.info.player or event.target not in self.bld.info.npc:
            return

        npc = self.bld.info.npc[event.target]
        if npc.templateID == self.mainBossTemplateID and self.bld.info.getName(event.target) == self.bossName:
            self.bh.setMainTarget(event.target)
            self.mainTargetRecorded = 1

    def analyseSecondStage(self, event):
        self.recordMainTarget(event)
        if event.dataType == "Shout":
            recordDebugShout(self, event)
            self.collectShoutCandidates(event)
        elif event.dataType == "Death":
            self.collectDeathCandidates(event)
            self.recordTriviaDeath(event)
        elif event.dataType == "Scene":
            self.collectChestCandidates(event)
            self.collectSceneCandidates(event)
        elif event.dataType == "Skill":
            self.collectDamageCandidates(event)
        super().analyseSecondStage(event)

    def countFinal(self):
        self.resolveWinCondition()
        if self.resolvedWinReason is not None:
            self.win = 1
            self.detail["winReason"] = self.resolvedWinReason["rule"]
            self.detail["winRule"] = self.resolvedWinReason
            self.bh.setBadPeriod(self.resolvedWinReason["eventTime"], self.finalTime, True, True)

        super().countFinal()

        evidence = {
            "shouts": self.shoutCandidates,
            "deaths": filter_relevant_candidates(self.deathCandidates, self.bossName, self.bossTemplateIDs,
                                                 self.extraBossNames),
            "chests": filter_chest_candidates(self.chestCandidates, self.chestNames, []),
            "scenes": filter_tail_scene_candidates(self.sceneCandidates, self.finalTime, self.bossName,
                                                   self.sceneTemplateIDs, self.extraBossNames),
            "damage": build_damage_candidates(self.damageByNpc, self.finalTime, self.bossName,
                                              self.damageTemplateIDs, self.extraBossNames),
        }
        recommendation = build_recommendation(evidence)
        self.detail["winEvidence"] = evidence
        self.detail["winEvidenceRecommendation"] = recommendation
        self.detail["winEvidenceReport"] = format_evidence_report(self.bossName, evidence, recommendation)
        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        printDebugTimeline(self)
        self.triviaRecorder.flush(self.finalTime, self.battleTime, self.win)

    def initBattle(self):
        self.initBattleBase()
        self.initPhase(1, 1)

        self.activeBoss = "笑妆娘"
        self.debug = 0
        self.bhBlackList.extend(self.BH_BLACKLIST_EXTRA)
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = dict(self.BH_INFO)

        self.bossName = "笑妆娘"
        self.mainBossTemplateID = "137088"
        self.extraBossNames = ["笑妆娘宝箱", "笑妆娘寶箱"]
        self.bossTemplateIDs = [self.mainBossTemplateID]
        self.chestNames = ["笑妆娘宝箱", "笑妆娘寶箱"]
        self.chestTemplateIDs = []
        self.sceneTemplateIDs = ["137088", "137095", "137099", "137108"]
        self.damageTemplateIDs = [self.mainBossTemplateID]

        self.resolvedWinReason = None
        self.chestWinTime = 0
        self.damageFallbackTime = 0
        self.mainBossDamage = 0
        self.mainTargetRecorded = 0

        self.shoutCandidates = []
        self.deathCandidates = []
        self.chestCandidates = []
        self.sceneCandidates = []
        self.damageByNpc = {}
        self.triviaRecorder = LangfengTriviaRecorder(self.config, self.bossName, self.bld.info.battleTime,
                                                     self.startTime)
        self.triviaRecorder.add_player_names(self.statDict)

import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.boss.langfengxuancheng.WinEvidence import append_unique, filter_relevant_candidates, \
    filter_chest_candidates, filter_tail_scene_candidates, build_damage_candidates, build_recommendation, \
    format_evidence_report
from replayer.boss.langfengxuancheng.TimelineDebug import recordDebugShout, printDebugTimeline
from replayer.boss.langfengxuancheng.Trivia import LangfengTriviaRecorder


class AshinaChengqingWindow(SpecificBossWindow):

    def loadWindow(self):
        self.constructWindow("阿史那承庆", "1200x800")
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


class AshinaChengqingReplayer(GeneralReplayer):
    TARGET_HP = 28671061364
    DAMAGE_THRESHOLD = 0.98
    BH_BLACKLIST_EXTRA = [
        "s44171",  # 普通攻击
        "s44170",  # 开山 - 普通攻击
        "s44176",
        "s44178",
        "s44179",
        "s44182",
        "s44190",
        "s44415",
        "s44444",
        "s43975",
        "s44622",
        "b32949",
        "b32939",
        "b33102",
        "b32943",
        "b32944",
        "b32945",
        "b32946",
        "b32953",
        "b32999",
        "b32937",
        "b32996",
        "b32938",
        "s45000",  # 风（格挡成功）
        "s45001",  # 暴（格挡失败）
    ]
    BH_INFO = {
        "n137054": ["12449", "#33aa66", 0],  # 魂火
        "n137047": ["2019", "#ff5555", 0],   # 处决鬼手
        "n137202": ["340", "#7744ff", 0],    # 鬼手
        "b32954": ["18462", "#33aa66", 0],   # 唤醒
        # "s44170": ["2028", "#3355ff", 0],    # 开山
        "s44303": ["2028", "#3355ff", 0],    # 连击
        "s32953": ["3431", "#ff8800", 0],    # 巨刃掠影
        "s44196": ["3452", "#ff3333", 0],    # 碾碎
        "s44191": ["433", "#aa33ff", 0],     # 黄泉破
        "c44410": ["4531", "#ff5555", 0],    # 斩
        "c44411": ["3452", "#ffaa00", 0],    # 破
    }

    def recordDeath(self, item, deathSource):
        pass

    def recordTriviaDeath(self, event):
        if self.triviaRecorder.enabled and event.id in self.bld.info.player:
            self.triviaRecorder.record_event("Dead", self.bld.info.getName(event.id), event.time)

    def collectTriviaSkillHits(self, event):
        if not self.triviaRecorder.enabled:
            return
        if event.target not in self.bld.info.player or event.caster not in self.bld.info.npc:
            return

        if event.id == "44415":
            self.triviaRecorder.record_event("Ashina44415", self.bld.info.getName(event.target), event.time)

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

    def recordSceneTimeline(self, event):
        if event.dataType != "Scene" or event.id not in self.bld.info.npc or event.enter != 1:
            return

        npc = self.bld.info.npc[event.id]
        template_id = npc.templateID
        name = self.bld.info.getName(event.id)
        key = "n%s" % template_id
        if key not in self.bhInfo:
            return
        if event.time - self.bhTime.get(key, 0) <= 3000:
            return

        self.bhTime[key] = event.time
        description = "%s现身" % name
        color = self.bhInfo[key][1]
        self.bh.setEnvironment(template_id, name, self.bhInfo[key][0], event.time, 0, 1, description, "npc", color=color)

        if template_id == "137202" and not self.phase2Started:
            self.changePhase(event.time, 2)
            self.phase2Started = 1

    def analyseSecondStage(self, event):
        self.recordMainTarget(event)
        self.recordSceneTimeline(event)
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
            self.collectTriviaSkillHits(event)
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
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)
        printDebugTimeline(self)
        self.triviaRecorder.flush(self.finalTime, self.battleTime, self.win)

    def initBattle(self):
        self.initBattleBase()
        self.initPhase(2, 1)

        self.activeBoss = "阿史那承庆"
        self.debug = 1
        self.bhBlackList.extend(self.BH_BLACKLIST_EXTRA)
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = dict(self.BH_INFO)

        self.bossName = "阿史那承庆"
        self.mainBossTemplateID = "137017"
        self.extraBossNames = ["阿史那承庆宝箱", "阿史那承庆寶箱"]
        self.bossTemplateIDs = [self.mainBossTemplateID]
        self.chestNames = ["阿史那承庆宝箱", "阿史那承庆寶箱"]
        self.chestTemplateIDs = []
        self.sceneTemplateIDs = [self.mainBossTemplateID, "137054", "137047", "137202"]
        self.damageTemplateIDs = [self.mainBossTemplateID]

        self.resolvedWinReason = None
        self.chestWinTime = 0
        self.damageFallbackTime = 0
        self.mainBossDamage = 0
        self.mainTargetRecorded = 0
        self.phase2Started = 0

        self.shoutCandidates = []
        self.deathCandidates = []
        self.chestCandidates = []
        self.sceneCandidates = []
        self.damageByNpc = {}
        self.triviaRecorder = LangfengTriviaRecorder(self.config, self.bossName, self.bld.info.battleTime,
                                                     self.startTime)
        self.triviaRecorder.add_player_names(self.statDict)

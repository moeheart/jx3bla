import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.boss.langfengxuancheng.WinEvidence import append_unique, filter_relevant_candidates, \
    filter_chest_candidates, filter_tail_scene_candidates, build_damage_candidates, build_recommendation, \
    format_evidence_report
from replayer.boss.langfengxuancheng.TimelineDebug import recordDebugShout, printDebugTimeline
from replayer.boss.langfengxuancheng.Trivia import LangfengTriviaRecorder, bool_flag


class TangZuiWindow(SpecificBossWindow):

    def loadWindow(self):
        self.constructWindow("唐醉", "1200x800")
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


class TangZuiReplayer(GeneralReplayer):
    TARGET_HP = 23312900000
    SCENE_THRESHOLD = 0.95
    DAMAGE_THRESHOLD = 0.98
    REENTER_WINDOW = 5000
    TRIVIA_WAVE_WINDOW = 200
    TRIVIA_GROUP_THRESHOLD = 7
    BH_BLACKLIST_EXTRA = [
        "s43923",  # 普通攻击
        "s43924",
        "s43934",
        "s43964",
        "s43965",
        "s43990",
        "s43995",
        "s44018",
        "s44050",
        "s44305",
        "b31979",
        "b33133",
        "b32808",
    ]
    BH_INFO = {
        "b32851": ["15522", "#aa33ff", 0],  # 翎刃毒
        "c43933": ["3452", "#ff3333", 0],   # 透骨刺
        "c43925": ["2028", "#ff8800", 0],   # 三叠杀
        "c43969": ["12453", "#3355ff", 0],  # 碎星
        "c43937": ["12452", "#33aa66", 0],  # 魂锁牵
    }

    def recordDeath(self, item, deathSource):
        pass

    def recordTriviaDeath(self, event):
        if self.triviaRecorder.enabled and event.id in self.bld.info.player:
            self.triviaRecorder.record_event("Dead", self.bld.info.getName(event.id), event.time)

    def flush33133Wave(self):
        if not self.triviaRecorder.enabled or not self.buff33133WavePlayers:
            return
        if len(self.buff33133WavePlayers) < self.TRIVIA_GROUP_THRESHOLD:
            for player_name in sorted(self.buff33133WavePlayers):
                self.triviaRecorder.record_event("TangZui33133", player_name, self.buff33133WaveTime)
        self.buff33133WaveTime = 0
        self.buff33133WaveLast = 0
        self.buff33133WavePlayers = set()

    def collectTrivia33133(self, event):
        if not self.triviaRecorder.enabled:
            return
        if event.target not in self.bld.info.player or event.caster not in self.bld.info.npc:
            return
        if event.id != "33133" or bool_flag(event.delete):
            return

        player_name = self.bld.info.getName(event.target)
        if not self.buff33133WavePlayers:
            self.buff33133WaveTime = event.time
            self.buff33133WaveLast = event.time
            self.buff33133WavePlayers = {player_name}
            return

        if event.time - self.buff33133WaveLast <= self.TRIVIA_WAVE_WINDOW:
            self.buff33133WavePlayers.add(player_name)
            self.buff33133WaveLast = event.time
            return

        self.flush33133Wave()
        self.buff33133WaveTime = event.time
        self.buff33133WaveLast = event.time
        self.buff33133WavePlayers = {player_name}

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
        if event.id not in self.bld.info.npc:
            return

        npc = self.bld.info.npc[event.id]
        name = self.bld.info.getName(event.id)
        append_unique(self.sceneCandidates, {
            "time": event.time,
            "npcID": event.id,
            "name": name,
            "templateID": npc.templateID,
            "enter": event.enter,
        })

        if npc.templateID == self.mainBossTemplateID and name == self.bossName:
            if event.enter == 0:
                self.lastMainBossLeaveTime = event.time
            elif self.lastMainBossLeaveTime and event.time - self.lastMainBossLeaveTime <= self.REENTER_WINDOW:
                self.lastMainBossLeaveTime = 0

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
        elif self.lastMainBossLeaveTime and self.mainBossDamage >= self.TARGET_HP * self.SCENE_THRESHOLD:
            self.resolvedWinReason = {
                "rule": "scene",
                "eventTime": self.lastMainBossLeaveTime,
                "trimTime": self.lastMainBossLeaveTime,
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
        elif event.dataType == "Buff":
            self.collectTrivia33133(event)
        elif event.dataType == "Skill":
            self.collectDamageCandidates(event)
        super().analyseSecondStage(event)

    def countFinal(self):
        self.flush33133Wave()
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

        self.activeBoss = "唐醉"
        self.debug = 0
        self.bhBlackList.extend(self.BH_BLACKLIST_EXTRA)
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = dict(self.BH_INFO)

        self.bossName = "唐醉"
        self.mainBossTemplateID = "137005"
        self.extraBossNames = ["唐醉宝箱", "唐醉寶箱"]
        self.bossTemplateIDs = [self.mainBossTemplateID]
        self.chestNames = ["唐醉宝箱", "唐醉寶箱"]
        self.chestTemplateIDs = []
        self.sceneTemplateIDs = [self.mainBossTemplateID, "137044", "137049"]
        self.damageTemplateIDs = [self.mainBossTemplateID]

        self.resolvedWinReason = None
        self.chestWinTime = 0
        self.lastMainBossLeaveTime = 0
        self.damageFallbackTime = 0
        self.mainBossDamage = 0
        self.mainTargetRecorded = 0
        self.buff33133WaveTime = 0
        self.buff33133WaveLast = 0
        self.buff33133WavePlayers = set()

        self.shoutCandidates = []
        self.deathCandidates = []
        self.chestCandidates = []
        self.sceneCandidates = []
        self.damageByNpc = {}
        self.triviaRecorder = LangfengTriviaRecorder(self.config, self.bossName, self.bld.info.battleTime,
                                                     self.startTime)
        self.triviaRecorder.add_player_names(self.statDict)

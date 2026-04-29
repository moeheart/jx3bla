import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.boss.langfengxuancheng.WinEvidence import append_unique, filter_relevant_candidates, \
    filter_chest_candidates, filter_tail_scene_candidates, build_damage_candidates, build_recommendation, \
    format_evidence_report, find_shout_win_reason, allow_damage_win_fallback, template_id_match
from replayer.boss.langfengxuancheng.TimelineDebug import recordTimelineScene, recordTimelineShout, \
    printDebugTimeline
from replayer.boss.langfengxuancheng.Trivia import LangfengTriviaRecorder


class TangHuairenWindow(SpecificBossWindow):
    '''
    唐怀仁的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用 tkinter 绘制详细复盘窗口。
        '''
        self.constructWindow("唐怀仁", "1200x800")
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


class TangHuairenReplayer(GeneralReplayer):
    TARGET_HP_P1 = 10762847454
    TARGET_HP_P2 = 25230692033
    SCENE_THRESHOLD = 0.95
    DAMAGE_THRESHOLD = 0.98
    BH_BLACKLIST_EXTRA = [
        "s44052",  # 普攻：残夜·射击
        "s44047",  # 普攻：破阵·攻击
        "s44230",
        "s44587",
        "s45174",
        "b32959",
        "b32960",
        "b33223",
    ]
    BH_INFO = {
        "c44037": ["12453", "#3355ff", 0],  # 磁震
        "c44041": ["3405", "#ffaa00", 0],   # 千机匣·连弩
        "c44043": ["3330", "#33aa66", 0],   # 修缮
        "c44076": ["12452", "#66aa33", 0],  # 千机匣·毒刹
        "c44152": ["3405", "#ffaa00", 0],   # 连弩扫射
        "c44153": ["2028", "#aa33ff", 0],   # 玄阴霹雳弹
        "c44180": ["3452", "#ff5555", 0],   # 瞬杀箭
        "c44197": ["12449", "#33aaff", 0],  # 牵机磁荡
        "c44207": ["4531", "#3355ff", 0],   # 玄阴·震鸣
        "c44208": ["4531", "#ff3333", 0],   # 赤阳·震鸣
        "c44209": ["340", "#ffaa00", 0],    # 蓄能横扫
        "c44491": ["12451", "#ff3333", 0],  # 毁灭
        "c44754": ["12449", "#7733ff", 0],  # 天机雷印
        "s44040": ["3452", "#ff5555", 0],   # 索命箭
        "s44154": ["2028", "#aa33ff", 0],   # 玄阴霹雳弹
        "s44198": ["12449", "#33aaff", 0],  # 牵机磁荡
        "s44207": ["4531", "#3355ff", 0],   # 玄阴·震鸣
        "s44208": ["4531", "#ff3333", 0],   # 赤阳·震鸣
        "s44223": ["340", "#ffaa00", 0],    # 蓄能横扫
        "s44231": ["12451", "#ff3333", 0],  # 赤阳陨星
        "s44491": ["12451", "#ff3333", 0],  # 毁灭
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
            if (name in self.chestNames or npc.templateID in self.chestTemplateIDs) and self.chestWinTime == 0:
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

        if name == self.bossName and template_id_match(npc.templateID, self.mainBossTemplateIDs) and event.enter == 0:
            self.lastPhase1BossLeaveTime = event.time
        elif name == self.phase2BossName and template_id_match(npc.templateID, self.phase2BossTemplateIDs) and event.enter == 0:
            self.lastPhase2BossLeaveTime = event.time

    def triggerPhase2(self, event, npc):
        if self.phase2Started:
            return
        if not template_id_match(npc.templateID, self.phase2BossTemplateIDs):
            return

        self.changePhase(event.time, 2)
        self.phase2Started = 1

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

        if template_id_match(npc.templateID, self.mainBossTemplateIDs):
            self.mainBossDamageP1 += event.damageEff
            if self.damageFallbackTimeP1 == 0 and self.mainBossDamageP1 >= self.TARGET_HP_P1 * self.DAMAGE_THRESHOLD:
                self.damageFallbackTimeP1 = event.time
        elif template_id_match(npc.templateID, self.phase2BossTemplateIDs):
            self.triggerPhase2(event, npc)
            self.mainBossDamageP2 += event.damageEff
            if self.damageFallbackTimeP2 == 0 and self.mainBossDamageP2 >= self.TARGET_HP_P2 * self.DAMAGE_THRESHOLD:
                self.damageFallbackTimeP2 = event.time

    def resolveWinCondition(self):
        if self.resolvedWinReason is not None:
            return

        damageFallbackTime = self.damageFallbackTimeP2 if self.phase2Started else self.damageFallbackTimeP1
        shoutWinReason = find_shout_win_reason(self.shoutCandidates, self.bossWinShouts, damageFallbackTime)
        if shoutWinReason is not None:
            self.resolvedWinReason = shoutWinReason
        elif self.phase2Started:
            if self.chestWinTime:
                self.resolvedWinReason = {
                    "rule": "chest",
                    "eventTime": self.chestWinTime,
                    "trimTime": 0,
                    "backupRule": "scene",
                    "needShoutHook": 1,
                }
            elif self.lastPhase2BossLeaveTime and self.mainBossDamageP2 >= self.TARGET_HP_P2 * self.SCENE_THRESHOLD and allow_damage_win_fallback(self):
                self.resolvedWinReason = {
                    "rule": "confirmed_scene",
                    "eventTime": self.lastPhase2BossLeaveTime,
                    "trimTime": self.lastPhase2BossLeaveTime,
                    "backupRule": "damage",
                    "needShoutHook": 1,
                }
            elif self.damageFallbackTimeP2 and allow_damage_win_fallback(self):
                self.resolvedWinReason = {
                    "rule": "damage",
                    "eventTime": self.damageFallbackTimeP2,
                    "trimTime": self.damageFallbackTimeP2,
                    "backupRule": "",
                    "needShoutHook": 1,
                }
        else:
            if self.lastPhase1BossLeaveTime and self.mainBossDamageP1 >= self.TARGET_HP_P1 * self.SCENE_THRESHOLD and allow_damage_win_fallback(self):
                self.resolvedWinReason = {
                    "rule": "confirmed_scene",
                    "eventTime": self.lastPhase1BossLeaveTime,
                    "trimTime": self.lastPhase1BossLeaveTime,
                    "backupRule": "damage",
                    "needShoutHook": 1,
                }
            elif self.damageFallbackTimeP1 and allow_damage_win_fallback(self):
                self.resolvedWinReason = {
                    "rule": "damage",
                    "eventTime": self.damageFallbackTimeP1,
                    "trimTime": self.damageFallbackTimeP1,
                    "backupRule": "",
                    "needShoutHook": 1,
                }

    def trimTime(self):
        self.resolveWinCondition()
        if self.resolvedWinReason is not None and self.resolvedWinReason["trimTime"] != 0:
            self.trimmedFinalTime = self.resolvedWinReason["trimTime"]
        return super().trimTime()

    def recordMainTarget(self, event):
        if event.dataType != "Skill":
            return
        if event.caster not in self.bld.info.player or event.target not in self.bld.info.npc:
            return

        npc = self.bld.info.npc[event.target]
        name = self.bld.info.getName(event.target)
        if template_id_match(npc.templateID, self.mainBossTemplateIDs) and name == self.bossName:
            if self.mainBossTemplateID not in self.mainTargetRecorded:
                self.bh.setMainTarget(event.target)
                self.mainTargetRecorded.add(self.mainBossTemplateID)
        elif template_id_match(npc.templateID, self.phase2BossTemplateIDs) and name == self.phase2BossName:
            if self.phase2BossTemplateID not in self.mainTargetRecorded:
                self.bh.setMainTarget(event.target)
                self.mainTargetRecorded.add(self.phase2BossTemplateID)

    def analyseSecondStage(self, event):
        self.recordMainTarget(event)
        if event.dataType == "Shout":
            recordTimelineShout(self, event)
            self.collectShoutCandidates(event)
        elif event.dataType == "Death":
            self.collectDeathCandidates(event)
            self.recordTriviaDeath(event)
        elif event.dataType == "Scene":
            recordTimelineScene(self, event)
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
                                                 self.deathExtraNames),
            "chests": filter_chest_candidates(self.chestCandidates, self.chestNames, self.chestTemplateIDs),
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
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000) if self.phase2Started else 0
        printDebugTimeline(self)
        self.triviaRecorder.flush(self.finalTime, self.battleTime, self.win)

    def initBattle(self):
        self.initBattleBase()
        self.initPhase(2, 1)

        self.activeBoss = "唐怀仁"
        self.debug = 1
        self.bhBlackList.extend(self.BH_BLACKLIST_EXTRA)
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = dict(self.BH_INFO)

        self.bossName = "唐怀仁"
        self.phase2BossName = "须罗巨傀"
        self.mainBossTemplateIDs = ["137058", "137163"]
        self.phase2BossTemplateIDs = ["137067", "137175"]
        self.mainBossTemplateID = self.mainBossTemplateIDs[0]
        self.phase2BossTemplateID = self.phase2BossTemplateIDs[0]
        self.extraBossNames = [self.phase2BossName, "陷阵机卒", "蕴雷机瓮"]
        self.deathExtraNames = []
        self.bossTemplateIDs = self.mainBossTemplateIDs + self.phase2BossTemplateIDs
        self.chestNames = ["唐怀仁宝箱", "唐怀仁寶箱"]
        self.chestTemplateIDs = []
        self.sceneTemplateIDs = self.bossTemplateIDs + ["137064", "137041", "137085", "137145", "137166", "137128", "137120"]
        self.damageTemplateIDs = self.bossTemplateIDs + ["137027", "137023", "137145"]
        self.bossWinShouts = []

        self.resolvedWinReason = None
        self.chestWinTime = 0
        self.lastPhase1BossLeaveTime = 0
        self.lastPhase2BossLeaveTime = 0
        self.damageFallbackTimeP1 = 0
        self.damageFallbackTimeP2 = 0
        self.mainBossDamageP1 = 0
        self.mainBossDamageP2 = 0
        self.phase2Started = 0
        self.mainTargetRecorded = set()

        self.shoutCandidates = []
        self.deathCandidates = []
        self.chestCandidates = []
        self.sceneCandidates = []
        self.damageByNpc = {}
        self.triviaRecorder = LangfengTriviaRecorder(self.config, self.bossName, self.bld.info.battleTime,
                                                     self.startTime)
        self.triviaRecorder.add_player_names(self.statDict)

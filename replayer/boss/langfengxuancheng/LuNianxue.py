import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.boss.langfengxuancheng.WinEvidence import append_unique, filter_relevant_candidates, \
    filter_chest_candidates, filter_tail_scene_candidates, build_damage_candidates, build_recommendation, \
    format_evidence_report, normalize_shout_content, allow_damage_win_fallback, template_id_match
from replayer.boss.langfengxuancheng.TimelineDebug import recordTimelineShout, printDebugTimeline
from replayer.boss.langfengxuancheng.Trivia import LangfengTriviaRecorder


class LuNianxueWindow(SpecificBossWindow):
    '''
    鲁念雪的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用 tkinter 绘制详细复盘窗口。
        '''
        self.constructWindow("鲁念雪", "1200x800")
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


class LuNianxueReplayer(GeneralReplayer):
    '''
    鲁念雪的定制复盘类。
    '''
    TARGET_HP = 153270177984
    DAMAGE_THRESHOLD = 0.98
    BH_BLACKLIST_EXTRA = [
        "s44968",  # 雷劲，高频环境伤害
        "s44395",  # 磁雷外泄
        "s44015",  # 雷元归枢命中，时间轴保留读条
        "s44277",  # 雷元归枢·结
        "s44135",  # 失控雷电
        "s33088",  # 流血
        "s33090",  # 阴攻击
        "s33091",  # 阳攻击
        "s44006",  # 风切
        "s44007",  # 电刃
        "s44008",  # 风旋
        "s44009",  # 雷曜
        "s44130",  # 穿空电击
        "s44319",  # 雷曜磁暴
        "s44376",  # 雷罗电网命中，时间轴保留读条
        "s44377",  # 雷罗电网·残电
        "s44388",  # 磁雷聚合·阴命中，时间轴保留读条
        "s44389",  # 磁雷聚合·阳命中，时间轴保留读条
        "s44391",  # 钢羽铁壁命中，时间轴保留读条
        "s44379",  # 双鸟截杀
        "s44429",  # 阴·攻击
        "s44430",  # 阳·攻击
        "s44435",  # 钢翼刃旋
        "s44736",  # 中和电击
        "b33034",  # 强磁，高频状态
        "b33088",  # 流血
        "b32872",  # 烧伤
        "b32873",  # 麻痹
        "b33092",  # 破甲
        "b33093",  # 扑倒
        "b33090",  # 阴
        "b33091",  # 阳
        "c42925",  # 生地狱
        "c44433",  # 扑跃爪切
    ]
    BH_INFO = {
        "c44031": ["4531", "#33aaff", 0],  # 淬电
        "c44293": ["3452", "#ff5555", 0],  # 四劫电刃
        "c44015": ["12453", "#3355ff", 0],  # 雷元归枢
        "c44367": ["12453", "#3355ff", 0],  # 雷元归枢
        "c44371": ["12453", "#3355ff", 0],  # 雷元归枢
        "c44316": ["3405", "#ffaa00", 0],  # 雷曜磁旋
        "c44318": ["3405", "#ffaa00", 0],  # 雷曜磁旋
        "c44320": ["12449", "#aa33ff", 0],  # 强磁激荡
        "c44407": ["12449", "#aa33ff", 0],  # 强磁激荡
        "c44375": ["2028", "#33aa66", 0],  # 雷罗电网
        "c44388": ["3330", "#7733ff", 0],  # 磁雷聚合·阴
        "c44389": ["3330", "#ff8833", 0],  # 磁雷聚合·阳
        "c44693": ["3452", "#ff3333", 0],  # 电刃双刃
        "c44733": ["12451", "#ff33aa", 0],  # 淬电·机鸾出动
        "c44391": ["12452", "#33aaff", 0],  # 钢羽铁壁
        "b33480": ["3330", "#888888", 0],  # 磁雷弱化
    }

    def recordDeath(self, item, deathSource):
        pass

    def recordTriviaDeath(self, event):
        if self.triviaRecorder.enabled and event.id in self.bld.info.player:
            self.triviaRecorder.record_event("Dead", self.bld.info.getName(event.id), event.time)

    def collectShoutCandidates(self, event):
        if event.content not in ['""', ""]:
            append_unique(self.shoutCandidates, {"time": event.time, "content": event.content})

    def findBossWinShoutReason(self):
        normalized_win_shouts = set([normalize_shout_content(line) for line in self.bossWinShouts])
        if not normalized_win_shouts:
            return None

        for item in self.shoutCandidates:
            text = normalize_shout_content(item.get("content", ""))
            if text not in normalized_win_shouts:
                continue

            event_time = item.get("time", 0)
            trim_time = 0
            if self.damageFallbackTime and self.damageFallbackTime <= event_time:
                event_time = self.damageFallbackTime
                trim_time = self.damageFallbackTime

            return {
                "rule": "boss_win_shout",
                "eventTime": event_time,
                "trimTime": trim_time,
                "backupRule": "damage" if trim_time else "",
                "needShoutHook": 0,
                "shoutTime": item.get("time", 0),
                "shout": text,
            }
        return None

    def collectDeathCandidates(self, event):
        if event.id not in self.bld.info.npc:
            return

        npc = self.bld.info.npc[event.id]
        name = self.bld.info.getName(event.id)
        append_unique(self.deathCandidates, {
            "time": event.time,
            "npcID": event.id,
            "name": name,
            "templateID": npc.templateID,
        })

        if name == self.bossName and template_id_match(npc.templateID, self.mainBossTemplateIDs) and self.deathWinTime == 0:
            self.deathWinTime = event.time

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

        if template_id_match(npc.templateID, self.mainBossTemplateIDs):
            self.mainBossDamage += event.damageEff
            if self.damageFallbackTime == 0 and self.mainBossDamage >= self.TARGET_HP * self.DAMAGE_THRESHOLD:
                self.damageFallbackTime = event.time

    def resolveWinCondition(self):
        if self.resolvedWinReason is not None:
            return

        shoutWinReason = self.findBossWinShoutReason()
        if shoutWinReason is not None:
            self.resolvedWinReason = shoutWinReason
        elif self.deathWinTime:
            self.resolvedWinReason = {
                "rule": "death",
                "eventTime": self.deathWinTime,
                "trimTime": self.deathWinTime,
                "backupRule": "chest" if self.chestWinTime else "damage",
                "needShoutHook": 1,
            }
        elif self.chestWinTime:
            self.resolvedWinReason = {
                "rule": "chest",
                "eventTime": self.chestWinTime,
                "trimTime": 0,
                "backupRule": "damage",
                "needShoutHook": 1,
            }
        elif self.damageFallbackTime and allow_damage_win_fallback(self):
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
        if template_id_match(npc.templateID, self.mainBossTemplateIDs) and self.bld.info.getName(event.target) == self.bossName:
            self.bh.setMainTarget(event.target)
            self.mainTargetRecorded = 1

    def analyseSecondStage(self, event):
        self.recordMainTarget(event)
        if event.dataType == "Shout":
            recordTimelineShout(self, event)
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
            "deaths": filter_relevant_candidates(self.deathCandidates, self.bossName, self.bossTemplateIDs, []),
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
        printDebugTimeline(self)
        self.triviaRecorder.flush(self.finalTime, self.battleTime, self.win)

    def initBattle(self):
        self.initBattleBase()
        self.initPhase(1, 1)

        self.activeBoss = "鲁念雪"
        self.debug = 1
        self.bhBlackList.extend(self.BH_BLACKLIST_EXTRA)
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = dict(self.BH_INFO)

        self.bossName = "鲁念雪"
        self.mainBossTemplateIDs = ["136483"]
        self.mainBossTemplateID = self.mainBossTemplateIDs[0]
        self.extraBossNames = ["鲁念雪宝箱", "鲁念雪寶箱"]
        self.bossTemplateIDs = self.mainBossTemplateIDs
        self.chestNames = ["鲁念雪宝箱", "鲁念雪寶箱"]
        self.chestTemplateIDs = []
        self.sceneTemplateIDs = self.mainBossTemplateIDs + ["136484", "136673", "136763", "136802", "136891", "137279"]
        self.damageTemplateIDs = self.mainBossTemplateIDs + ["136802", "136891"]
        self.bossWinShouts = []

        self.resolvedWinReason = None
        self.deathWinTime = 0
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

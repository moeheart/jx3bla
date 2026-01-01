# Created by moeheart at 09/25/2025
# 阿里曼幻身的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk


class AlimanhuanshenWindow(SpecificBossWindow):
    '''
    阿里曼幻身的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("阿里曼幻身", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("P1DPS", "在P1的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "在P2的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("P3DPS", "在P3的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P3Time"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["P1DPS"]))
            tb.AppendContext(int(line["battle"]["P2DPS"]))
            tb.AppendContext(int(line["battle"]["P3DPS"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class AlimanhuanshenReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()
        # print(self.bh.log)

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)
        self.detail["P3Time"] = int(self.phaseTime[3] / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                res = self.getBaseList(id)
                res["battle"]["P1DPS"] = int(safe_divide(res["battle"]["P1Damage"], self.detail["P1Time"]))
                res["battle"]["P2DPS"] = int(safe_divide(res["battle"]["P2Damage"], self.detail["P2Time"]))
                res["battle"]["P3DPS"] = int(safe_divide(res["battle"]["P3Damage"], self.detail["P3Time"]))
                bossResult.append(res)
        self.statList = bossResult

        # if self.win == 1:
        #     print("[Debug] Win!!! Yet disabled for debugging")
        #     self.win = 0

        return self.statList, self.potList, self.detail, self.stunCounter

    def recordDeath(self, item, deathSource):
        '''
        在有玩家重伤时的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        - deathSource 重伤来源。
        '''
        pass

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

        self.checkTimer(event.time)

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                if event.caster in self.bld.info.npc and event.heal == 0 and event.scheme == 1:
                    # 尝试记录技能事件
                    name = "s%s" % event.id
                    if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                        self.bhTime[name] = event.time
                        skillName = self.bld.info.getSkillName(event.full_id)
                        if "," not in skillName:
                            key = "s%s" % event.id
                            if key in self.bhInfo or self.debug:
                                self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家",
                                                       "skill")

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["阿里曼幻身"]:
                            self.bh.setMainTarget(event.target)
                        if self.phase == 1:
                            self.statDict[event.caster]["battle"]["P1Damage"] += event.damageEff
                        elif self.phase == 2:
                            self.statDict[event.caster]["battle"]["P2Damage"] += event.damageEff
                        elif self.phase == 3:
                            self.statDict[event.caster]["battle"]["P3Damage"] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 5000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

            # if event.id == "28050":  # 红宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28050", "红宝石", "2654", event.time, 5000, event.target, "红宝石点名")
            #
            # if event.id == "28052":  # 蓝宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28052", "蓝宝石", "2653", event.time, 5000, event.target, "蓝宝石点名")
            #
            # if event.id == "28054":  # 绿宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28054", "绿宝石", "2652", event.time, 5000, event.target, "绿宝石点名")

        elif event.dataType == "Shout":
            if event.content in ['"嗷——"', '"嗷——"']:
                self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
            elif event.content in ['"一境既破，万障新生。不过是拆了纸枷，又戴金镣。"', '"一境既破，萬障新生。不過是拆了紙枷，又戴金鐐。"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setCritPeriod(self.cszzStart, event.time, False, True)
            elif event.content in ['"你来了……欢迎……坠入吾之渊薮。"', '"你來了……歡迎……墜入吾之淵藪。"']:
                pass
            elif event.content in ['"此境非虚非实，乃众生心相所铸之牢..."', '"此境非虛非實，乃衆生心相所鑄之牢..."']:
                pass
            elif event.content in ['"尔等所见之焰，非火非光，乃是亘古未灭的因果业障..."', '"爾等所見之焰，非火非光，乃是亙古未滅的因果業障..."']:
                pass
            elif event.content in ['"你的剑，斩得开自己的愚妄吗？"', '"你的劍，斬得開自己的愚妄嗎？"']:
                pass
            elif event.content in ['"哈，你以为赢了？"', '"哈，你以爲贏了？"']:
                self.changePhase(event.time,0)
                self.changePhase(event.time + 22000, 2)
                self.bh.setBadPeriod(event.time, event.time + 22000, True, True)
            elif event.content in ['"破？你连真假都分不清。"', '"破？你連真假都分不清。"']:
                self.changePhase(event.time, 3)
            elif event.content in ['"嗷——呜————"', '"嗷——嗚————"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["阿里曼幻身宝箱", "巴圖仁欽寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        # if key in self.bhInfo or self.debug:
                        #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                        #                        1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.getName(event.id) in ["阿里曼幻身"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 2000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "c%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")
                if event.id == "41585":
                    self.changePhase(event.time, 0)
                    self.bh.setBadPeriod(event.time, event.time + 40000, True, True)

    def analyseFirstStage(self, item):
        '''
        处理单条复盘数据时的流程，在第一阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        '''
        self.initBattleBase()
        self.activeBoss = "阿里曼幻身"
        self.debug = 1

        self.initPhase(3, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.cszzStart = 0

        self.bhBlackList.extend(["s42063", "s42195",  # 赤劫焚罪
                                 "s42194",  # 赤焰焚身
                                 "s42502",  # 玄焰（其实是大圈）
                                 "s43464",  # 震慑
                                 "s42215", "s42214", "s42213", "b31913",  # 靛劫刑焰
                                 "b32386", "s43463",  # 罚罪
                                 "s42226",  # 金焱刑骸·小
                                 "s41606", "s41611", "s41622", "s41603", "s41624", "s41620",  # 业火
                                 "s43443", "s43444", "s43448", "s43465", "s43449", "s43420", "s43431", "s43430", "s43466", "s43429",  # 裂魂
                                 "s43433", "s43424", "s43450", "s43455", "s43454", "s43428", "s43440", "s43460", "s43447", "s43436", "s43459",  # 摧骨
                                 "s43462",  # 罚（也是二阶段的本体技能）
                                 "s42230", "s42229",  # 玄焰
                                 "s43467",  # 金焱刑骸·解
                                 "s42378",  # 崩（玄焰击飞）
                                 "b31323",  # 封印（迷宫封轻功）
                                 "b31604", "s41581",  # 火狱同心劫
                                 "s41767", "s41772", "s41806", "s41808",  # 灼烧
                                 "s41586",  # 剑狱焚城
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"b31587": ["25109", "#ff0000", 0],  # 赤焰
                       "c43430": ["4491", "#777777", 0],  # 裂魂
                       "c43429": ["4491", "#777777", 0],  # 裂魂
                       "c43420": ["4492", "#777777", 0],  # 裂魂
                       "c43422": ["4495", "#777777", 0],  # 裂魂
                       "c43431": ["4492", "#777777", 0],  # 裂魂
                       "c43448": ["4496", "#777777", 0],  # 裂魂
                       # "c43424": ["4498", "#777777", 0],  # 裂魂
                       # "c43428": ["4498", "#777777", 0],  # 裂魂
                       "b31327": ["25086", "#ff7700", 0],  # 业火
                       "b31734": ["25110", "#ffff00", 0],  # 金焰
                       "c43667": ["4576", "#000000", 0],  # 圣火熄灭
                       "b31735": ["25110", "#ffff00", 0],  # 金焰
                       "b31589": ["25079", "#ff0000", 0],  # 赤焰
                       "c43433": ["4528", "#777777", 0],  # 摧骨
                       "c43424": ["4529", "#777777", 0],  # 摧骨
                       "c43428": ["4529", "#777777", 0],  # 摧骨
                       "c43436": ["4530", "#777777", 0],  # 摧骨
                       "c43455": ["4531", "#777777", 0],  # 摧骨
                       "c43459": ["4532", "#777777", 0],  # 摧骨
                       "c43460": ["4532", "#777777", 0],  # 摧骨
                       "c41585": ["2185", "#00ff00", 0],  # 剑狱焚城
                       }

        # 阿里曼幻身数据格式：
        # ？


        # if self.bld.info.map == "会战弓月城":
        #     self.bh.critPeriodDesc = "暂无."
        # if self.bld.info.map == "25人普通会战弓月城":
        #     self.bh.critPeriodDesc = "暂无."
        # if self.bld.info.map == "25人英雄会战弓月城":
        #     self.bh.critPeriodDesc = "暂无."
        self.bh.critPeriodDesc = "暂无."

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"P1Damage": 0,
                                             "P2Damage": 0,
                                             "P3Damage": 0,
                                             "hit": 0,}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config
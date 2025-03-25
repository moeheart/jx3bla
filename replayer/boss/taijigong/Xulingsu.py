# Created by moeheart at 03/21/2025
# 许灵素的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk


class XulingsuWindow(SpecificBossWindow):
    '''
    许灵素的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("许灵素", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        # tb.AppendHeader("图腾伤害", "对图腾造成的伤害。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            # tb.AppendContext(int(line["battle"]["yztzDamage"]), color="#000000")

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class XulingsuReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()
        # print(self.bh.log)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                res = self.getBaseList(id)
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
                        if self.bld.info.getName(event.target) in ["许灵素"]:
                            self.bh.setMainTarget(event.target)

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
            if event.content in ['"祈天福，降灾厄，皆在一念之间。尔等既犯禁地，便以蛊咒为罚，永堕幽冥！"', '""']:
                self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
            elif event.content in ['"今日竟败于尔等之手……天命难违，罢了……"', '""']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"灾厄随行！"', '""']:
                pass
            elif event.content in ['"噬心为罚！"', '""']:
                pass
            elif event.content in ['"聚灵成刃！"', '""']:
                pass
            elif event.content in ['"天灵护佑！"', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["许灵素宝箱", "许灵素寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        if key in ["n131723"]:
                            self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, "天灵卫", "344", event.time, 0,
                                               1, "NPC出现", "npc")
                        elif key in self.bhInfo or self.debug:
                            # self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                            #                    1, "NPC出现", "npc")
                            pass

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.getName(event.id) in ["许灵素"]:
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
        self.activeBoss = "许灵素"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.hlszStart = 0
        self.hlszNum = 0

        self.bhBlackList.extend(["s39749",  # 普攻
                                 "b29962",  # 通用易伤
                                 "b29961", "s39755", "s39757",  # 灵蛊引
                                 "s39759", "s39760", "b29964", "b29963", "b29966",  # 灵咒令
                                 "s39762",  # 聚灵杀
                                 "s40272",  # 蛊灭劫
                                 "s39768", "b30000",  # 天灵卫

                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c39756": ["16379", "#ff0000", 4000],  # 灵蛊引
                       "c39758": ["2138", "#00ff00", 4000],  # 灵咒令
                       "c39761": ["342", "#ff7700", 2000],  # 聚灵杀
                       "c39879": ["16389", "#00ff00", 0],  # 蛊灭劫
                       "n131723": ["344", "#00ff77", 0],  # 天灵卫
                       "c39782": ["16366", "#ff0077", 3000],  # 怒吼
                       "c39765": ["3446", "#ff7777", 2000],  # 起死回生

                       }

        # 许灵素数据格式：
        # ？


        if self.bld.info.map == "太极宫":
            self.bh.critPeriodDesc = "待定."
        if self.bld.info.map == "25人普通太极宫":
            self.bh.critPeriodDesc = "待定."  # [垂死挣扎]期间.
        if self.bld.info.map == "25人英雄太极宫":
            self.bh.critPeriodDesc = "待定."

        for line in self.bld.info.player:
            pass
            # self.statDict[line]["battle"] = {"yztzDamage": 0}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config
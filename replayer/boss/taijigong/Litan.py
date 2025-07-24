# Created by moeheart at 06/03/2025
# 李倓的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk


class LitanWindow(SpecificBossWindow):
    '''
    李倓的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("李倓", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("P2伤害", "在P2期间（转P伤害出现后）对BOSS的有效伤害。此处为原始伤害，暂不支持rdps的单独统计。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["P2Damage"]), color="#000000")

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class LitanReplayer(SpecificReplayerPro):

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
                    if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 800:
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
                        if self.bld.info.getName(event.target) in ["李倓"]:
                            self.bh.setMainTarget(event.target)
                    if self.phase == 2:
                        self.statDict[event.caster]["battle"]["P2Damage"] += event.damageEff

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
            if event.content in ['"让你认清自己的斤两!"', '"讓你認清自己的斤兩!"']:
                self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
            elif event.content in ['"呼呼……是我轻看了你们……"', '"呼呼……是我輕看了你們……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                if self.P2shout + 40000 < event.time:
                    self.bh.setCritPeriod(self.P2shout + 40000, event.time, False, True)
            elif event.content in ['"有些本事！那这招又如何?"', '"有些本事！那這招又如何?"']:
                self.P2shout = event.time
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
                pass
            elif event.content in ['"吃我一枪!"', '"吃我一槍!"']:
                pass
            elif event.content in ['"双蛟出渊!"', '"雙蛟出淵!"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
            elif event.content in ['"要你付出代价!"', '"要你付出代價!"']:
                pass
            elif event.content in ['"受死!"', '""']:
                pass
            elif event.content in ['"太慢了！看招！"', '""']:
                pass
            elif event.content in ['"化影分形!"', '""']:
                pass
            elif event.content in ['"接我这招!"', '""']:
                pass
            elif event.content in ['"让本王瞧瞧你们的手段。"', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["李倓宝箱", "李倓寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter: # and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList: # and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        # icon = "341"
                        # if key in ["n131426", "n131413"]:
                        #     if key == "n131426":
                        #         key = "怒潮碎岳"
                        #         icon = "2146"
                        #     elif key == "n131413":
                        #         key = "螺旋激流"
                        #         icon = "3405"
                        #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, key, icon, event.time, 0,
                        #                        1, "NPC出现", "npc")
                        if skillName == "真龙":
                            skillName = "%s,%d,%d,%d" % (skillName, self.bld.info.npc[event.id].x, self.bld.info.npc[event.id].y, self.bld.info.npc[event.id].z)
                        if self.bld.info.npc[event.id].templateID == "132131":
                            self.f.write("%d %d %d %d\n" % (event.time, self.bld.info.npc[event.id].x, self.bld.info.npc[event.id].y, self.bld.info.npc[event.id].z))
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.getName(event.id) in ["李倓"]:
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
        self.activeBoss = "李倓"
        self.debug = 1

        self.initPhase(2, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.P2shout = 0

        self.bhBlackList.extend(["s39963", "s40825", "",  # 普攻
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c39882": ["3293", "#0000ff", 2000],  # 龙牙
                       }

        # 李倓数据格式：
        # ？


        # if self.bld.info.map == "太极宫":
        #     self.bh.critPeriodDesc = "[垂死挣扎]期间."
        # if self.bld.info.map == "25人普通太极宫":
        #     self.bh.critPeriodDesc = "[垂死挣扎]期间."
        # if self.bld.info.map == "25人英雄太极宫":
        #     self.bh.critPeriodDesc = "[垂死挣扎]期间."
        self.bh.critPeriodDesc = "转阶段喊话之后第40秒，到战斗结束."

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"P2Damage": 0}

        self.f = open("litanLogs.txt", "w")



    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config
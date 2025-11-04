# Created by moeheart at 09/25/2025
# 叶葵的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk


class YekuiWindow(SpecificBossWindow):
    '''
    叶葵的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("叶葵", "1200x800")
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


class YekuiReplayer(SpecificReplayerPro):

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

                if event.id == "41899":
                    self.bh.setCritPeriod(event.time, event.time + 4000, False, True)

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["叶葵"]:
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
            if event.content in ['"乖乖受死吧！"', '"乖乖受死吧！"']:
                if not self.firstShout:
                    self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
                    self.firstShout = 1
            elif event.content in ['"不……不想死……叫……叫太医……"', '"不……不想死……叫……叫太醫……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                # self.bh.setCritPeriod(self.cszzStart, event.time, False, True)
            elif event.content in ['"手牵手进棺材去吧！"', '"手牽手進棺材去吧！"']:
                pass
            elif event.content in ['"想化为灰烬，还是碎成冰渣？"', '"想化為灰燼，還是碎成冰渣？"']:
                pass
            elif event.content in ['"给老子变成碎肉！"', '"給老子變成碎肉！"']:
                pass
            elif event.content in ['"嘿嘿嘿……这下可是有点疼的！"', '"嘿嘿嘿……這下可是有點痛的！"']:
                pass
            elif event.content in ['"切……这速成的东西果然靠不住……"', '"切……這速成的東西果然靠不住……"']:
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
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["弓月城宝箱", "弓月城寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                # print("[YekuiDebug]", parseTime((event.time - self.startTime) / 1000), event.id, name,
                #       self.bld.info.npc[event.id].x, self.bld.info.npc[event.id].y)
                # if name == "n134212":
                #     with open("yekui.txt", "a") as f:
                #         f.write("%s %s %s\n" % (event.time, self.bld.info.npc[event.id].firstX, self.bld.info.npc[event.id].firstY))
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        # if key in self.bhInfo or self.debug:
                        #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                        #                        1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            pass
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].templateID in ["133457", "134224", "134282"]:
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
        self.activeBoss = "叶葵"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.firstShout = 0

        self.bhBlackList.extend(["s41854",  # 普攻
                                 "s41868", "s41869", "s41870",  # 坠刃
                                 "b31502", "b31758", "s41861", "s41862", "s41863",  # 锁影缠身
                                 "b31706", "s42272", "s42270", "s42321", "s42322", "s42315", "s42316", "s42317", "s42318", "s42319",  # 索命旋刃
                                 "s41899", "s41900", "s41901",  # 裂空旋刃杀
                                 "s42003", "s42699", "s42004", "s42005", "s42006",  # 链命
                                 "b31506", "s41975", "b31507", "s41974",  # 寒冰，烈焰
                                 "s41865", "s41866",  # 断魂扫

                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c41867": ["3426", "#ff0000", 3000],  # 坠刃
                       "c41860": ["4498", "#00ff00", 3000],  # 锁影缠身
                       "c42269": ["3436", "#0077ff", 2000],  # 索命旋刃
                       "c41897": ["4224", "#0000ff", 5000],  # 裂空旋刃杀
                       "c41898": ["4224", "#3300ff", 5000],  # 裂空旋刃杀
                       "c41998": ["733", "#ff7700", 3000],  # 链命
                       "c41864": ["3429", "#ff0077", 5000],  # 断魂扫
                       }

        # 叶葵数据格式：
        # ？


        if self.bld.info.map == "会战弓月城":
            self.bh.critPeriodDesc = "暂无."
        if self.bld.info.map == "25人普通会战弓月城":
            self.bh.critPeriodDesc = "[裂空旋刃杀]期间."
        if self.bld.info.map == "25人英雄会战弓月城":
            self.bh.critPeriodDesc = "[裂空旋刃杀]期间."

        for line in self.bld.info.player:
            pass
            # self.statDict[line]["battle"] = {"yztzDamage": 0}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config
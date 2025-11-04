# Created by moeheart at 09/25/2025
# 尹雪尘的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk


class YinxuechenWindow(SpecificBossWindow):
    '''
    尹雪尘的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("尹雪尘", "1200x800")
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


class YinxuechenReplayer(SpecificReplayerPro):

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
                        if self.bld.info.getName(event.target) in ["尹雪尘"]:
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
            if event.content in ['"若是让我玩尽兴了，我可以大发慈悲让你们死得痛快一些！"', '"若是讓我玩盡興了，我可以大發慈悲讓你們死得痛快一些！"']:
                self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
            elif event.content in ['"不……不想死……叫……叫太医……"', '"不……不想死……叫……叫太醫……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setCritPeriod(self.cszzStart, event.time, False, True)
            elif event.content in ['"尝尝天罚的滋味吧！"', '"嚐嚐天罰的滋味吧！"']:
                pass
            elif event.content in ['"哼！这回可没那畜生护着你们了！"', '"哼！這回可沒那畜生護著你們了！"']:
                pass
            elif event.content in ['"世间最有趣的戏码莫过于挚友相残，而我手里正好有个剧本， 等你们上演！"', '"世間最有趣的戲碼莫過於摯友相殘，而我手上正好有個劇本， 等你們上演！"']:
                pass
            elif event.content in ['"哼！算你们机灵。"', '"哼！算你們機靈。"']:
                pass
            elif event.content in ['""', '""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["尹雪尘宝箱", "尹雪塵寶箱"]:
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
            if event.id in self.bld.info.npc and self.bld.info.getName(event.id) in ["尹雪尘", "尹雪塵"]:
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
        self.activeBoss = "尹雪尘"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.cszzStart = 0

        self.bhBlackList.extend(["s42832", "s41687", "b31408",  # 普攻
                                 "s41690", "s42676", "s41691",  # 破阵曲·徵
                                 "s41688", "b31411", "b31388", "s41853", "s41689", "s41842",  # 破阵曲·角
                                 "s41699", "s41852", "s41700",  # 巽风掌
                                 "s41695", "b31391", "s41696",  # 艮山掌·一式
                                 "s41698",  # 艮山掌·二式
                                 "s41692", "b31389", "s41693", "s41694", "s41851",  # 震雷引
                                 "b31409",  # 脆弱
                                 "b31413", "s41704", "s41705", "b31414",  # 定波抵澜
                                 "s41701", "s41702", "s41703",  # 击水三千
                                 "b31395", "s41711", "s41710",  # 浮游天地
                                 "b31399",  # 逐波灵游
                                 "s42352", "s42351", "s41709", "s41708", "b31400",  # 驰风震域
                                 "b31401", "s41715", "s41716",  # 凝视
                                 "s42354", "s41707",  # 澹然若海
                                 "s41718",  # 飞倾列缺
                                 "s41720", "b31404", "b31402",  # 无相玄机
                                 "b31407", "s41726",  # 破阵曲·羽
                                 "s42353", "s41724",  # 艮山掌·一式
                                 "s41725",  # 艮山掌
                                 "s41722", "b31390", "s42650", "s41723",  # 震雷引
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c41690": ["4501", "#ff0000", 3000],  # 破阵曲·徵
                       "c41688": ["4492", "#ff7700", 2000],  # 破阵曲·角
                       "c41699": ["4496", "#00ff77", 3000],  # 巽风掌
                       "c41692": ["3420", "#ff0077", 3000],  # 震雷引
                       "c41695": ["3428", "#7777ff", 3000],  # 艮山掌·一式
                       "c41698": ["3428", "#0000ff", 10000],  # 艮山掌·二式
                       "c41704": ["4221", "#ff3300", 3000],  # 定波抵澜
                       "c41705": ["4221", "#ff3300", 8000],  # 定波抵澜
                       "c41701": ["4548", "#00ff00", 3000],  # 击水三千·一式
                       "c41702": ["4548", "#00ff00", 2000],  # 击水三千·二式
                       "c41703": ["4548", "#00ff00", 1000],  # 击水三千·三式
                       "c41710": ["3404", "#ff0033", 5000],  # 浮游天地
                       "s41713": ["2027", "#ff3377", 0],  # 逐波灵游
                       "c41715": ["3431", "#77ff00", 6000],  # 跃潮斩波
                       "c41720": ["2009", "#3300ff", 5000],  # 无相玄机
                       "c41726": ["4564", "#7733ff", 5000],  # 破阵曲·羽
                       "c41724": ["3428", "#7777ff", 7000],  # 艮山掌·一式
                       "c41725": ["3428", "#0000ff", 1000],  # 艮山掌
                       "c41721": ["335", "#ff3377", 5000],  # 木落雁归
                       "c41722": ["3420", "#ff0077", 3000],  # 震雷引
                       }

        # 尹雪尘数据格式：
        # ？


        if self.bld.info.map == "会战弓月城":
            self.bh.critPeriodDesc = "暂无."
        if self.bld.info.map == "25人普通会战弓月城":
            self.bh.critPeriodDesc = "暂无."
        if self.bld.info.map == "25人英雄会战弓月城":
            self.bh.critPeriodDesc = "暂无."

        for line in self.bld.info.player:
            pass
            # self.statDict[line]["battle"] = {"yztzDamage": 0}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config
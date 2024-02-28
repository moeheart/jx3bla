# Created by moeheart at 09/16/2023
# 钟不归的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class ZhongBuguiWindow(SpecificBossWindow):
    '''
    钟不归的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("钟不归", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("1组剑", "对第1组剑的伤害量，红/蓝表示不同的分组。如果剑没有打掉，则会显示为浅色。")
        tb.AppendHeader("2组剑", "对第2组剑的伤害量，红/蓝表示不同的分组。如果剑没有打掉，则会显示为浅色。")
        tb.AppendHeader("3组剑", "对第3组剑的伤害量，红/蓝表示不同的分组。如果剑没有打掉，则会显示为浅色。")
        tb.AppendHeader("4组剑", "对第4组剑的伤害量，红/蓝表示不同的分组。如果剑没有打掉，则会显示为浅色。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            for j in range(1, 5):
                if line["battle"]["hsjGroup%d" % j] == 1:
                    tb.AppendContext(int(line["battle"]["hsjDam%d" % j]), color="#0000ff")
                elif line["battle"]["hsjGroup%d" % j] == 2:
                    tb.AppendContext(int(line["battle"]["hsjDam%d" % j]), color="#ff0000")
                elif line["battle"]["hsjGroup%d" % j] == 3:
                    tb.AppendContext(int(line["battle"]["hsjDam%d" % j]), color="#7777ff")
                elif line["battle"]["hsjGroup%d" % j] == 4:
                    tb.AppendContext(int(line["battle"]["hsjDam%d" % j]), color="#ff7777")
                else:
                    tb.AppendContext(int(line["battle"]["hsjDam%d" % j]), color="#000000")
            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class ZhongBuguiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

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
                                self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

                if event.id == "35691":
                    for key in self.hsjOwner:
                        if self.hsjOwner[key] == event.caster and self.hsjRound in [1,2,3,4] and self.statDict[key]["battle"]["hsjGroup%d" % self.hsjRound] < 3:
                            self.statDict[key]["battle"]["hsjGroup%d" % self.hsjRound] += 2

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["钟不归", "鐘不歸"]:
                            self.bh.setMainTarget(event.target)
                        if self.bld.info.getName(event.target) in ["寒山剑", "寒山劍"] and event.damageEff > 0 and self.hsjRound in [1,2,3,4]:
                            self.statDict[event.caster]["battle"]["hsjDam%d" % self.hsjRound] += event.damageEff
                            self.hsjOwner[event.caster] = event.target
                            if self.hsj1 == 0:
                                self.hsj1 = event.target
                            if self.statDict[event.caster]["battle"]["hsjGroup%d" % self.hsjRound] < 3:
                                if self.hsj1 == event.target:
                                    self.statDict[event.caster]["battle"]["hsjGroup%d" % self.hsjRound] = 1
                                else:
                                    self.statDict[event.caster]["battle"]["hsjGroup%d" % self.hsjRound] = 2

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

        elif event.dataType == "Shout":
            if event.content in ['"破解不了老夫的剑法，一个也不许走！"']:
                pass
            elif event.content in ['"原来是这样破的……老夫……明白了……"', '"原來是這樣破的……老夫……明白了……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"气神相望，剑行如浪。"']:
                pass
            elif event.content in ['"气行周天，寒星其间。"']:
                pass
            elif event.content in ['"拨云见山寒日照，孤峰藏骨白茫中！"']:
                pass
            elif event.content in ['"气汇丹田，冷霜凝拳。"']:
                pass
            elif event.content in ['"苍松立岿霜气浓，烈风拨云两眼空！"']:
                pass
            elif event.content in ['"霜雾环身，坚不可摧！"']:
                pass
            elif event.content in ['"极晶灭却，无坚不摧！"']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["翁幼之宝箱", "??寶箱"]:
            #     self.win = 1
            #     self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            pass

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
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")
            # if self.bld.info.getSkillName(event.full_id) in ["血影坠击", "怨·黄泉鬼步"]:
            #     print("[Xueyingzhuiji]", event.id, parseTime((event.time - self.startTime) / 1000))
            if event.id == "35698":
                self.hsjRound += 1
                self.hsj1 = 0
                    
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
        self.activeBoss = "钟不归"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["s35650", "s35652", "s35653", "b26836", "b26833", "n124603", "s35655", "s35691",
                                 "n123688", "b26835", "s35658", "b26815", "n124967", "n125468", "n124894", "s35825",
                                 "n124966", "n122406", "n125205", "n125211", "s35701", "b26775", "b26783", "b26811",
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       "c35651": ["4552", "#0000ff", 5000],  # 太阴剑法·远山式
                       "c35654": ["3408", "#ff0000", 2000],  # 太阴剑法·寒星式
                       # b26836寒颤
                       "c35667": ["12436", "#ff00ff", 0],  # 绝式·寒山峯现
                       "c35656": ["3431", "#00ff77", 5000],  # 太阴剑法·冷涧式
                       "c35692": ["3430", "#77ff00", 5000],  # 绝式·云尽寒灭
                       "c35837": ["3430", "#77ff00", 10000],  # 云尽寒灭
                       # b26815寒灭锢身
                       "c35698": ["2038", "#7700ff", 3000],  # 太阴神功·守势
                       "c35699": ["2037", "#ff0077", 3000],  # 太阴神功·灭势
                       }

        # 翁幼之数据格式：
        # 7 ？

        self.hsjRound = 0
        self.hsj1 = 0
        self.hsjOwner = {}

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"hsjDam1": 0,
                                             "hsjDam2": 0,
                                             "hsjDam3": 0,
                                             "hsjDam4": 0,
                                             "hsjGroup1": 0,
                                             "hsjGroup2": 0,
                                             "hsjGroup3": 0,
                                             "hsjGroup4": 0,}
            self.hsjOwner[line] = 0


    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


# Created by moeheart at 09/16/2023
# 鬼筹的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class GuiChouWindow(SpecificBossWindow):
    '''
    鬼筹的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("鬼筹", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("搬运用时1", "第一次搬运的用时。\n这个用时包括捡起石头的时间和拿在手里的时间。为0代表这一轮没有参与。")
        tb.AppendHeader("搬运用时2", "第二次搬运的用时。\n这个用时包括捡起石头的时间和拿在手里的时间。为0代表这一轮没有参与。")
        tb.AppendHeader("搬运用时3", "第三次搬运的用时。\n这个用时包括捡起石头的时间和拿在手里的时间。为0代表这一轮没有参与。")
        tb.AppendHeader("树木伤害", "对树木的伤害，注意这个伤害没有除以时间。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)
            if line["battle"]["banyun1"] == 0:
                tb.AppendContext(0, color="#777777")
            else:
                tb.AppendContext(int(line["battle"]["banyun1"] / 10) / 100)
            if line["battle"]["banyun2"] == 0:
                tb.AppendContext(0, color="#777777")
            else:
                tb.AppendContext(int(line["battle"]["banyun2"] / 10) / 100)
            if line["battle"]["banyun3"] == 0:
                tb.AppendContext(0, color="#777777")
            else:
                tb.AppendContext(int(line["battle"]["banyun3"] / 10) / 100)
            tb.AppendContext(int(line["battle"]["shumuDPS"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class GuiChouReplayer(SpecificReplayerPro):

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

        idRemoveList = []
        for id in self.shumu:
            if self.shumu[id]["alive"] == 0 and event.time - self.shumu[id]["lastDamage"] > 500:
                time = parseTime((event.time - 500 - self.startTime) / 1000)
                self.addPot([self.bld.info.getName(self.shumu[id]["lastID"]),
                             self.occDetailList[self.shumu[id]["lastID"]],
                             0,
                             self.bossNamePrint,
                             "%s树木被击破" % time,
                             self.shumu[id]["damageList"],
                             0])
                idRemoveList.append(id)
        for id in idRemoveList:
            del self.shumu[id]

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

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["鬼筹"]:
                            self.bh.setMainTarget(event.target)
                        if self.bld.info.getName(event.target) in ["树木"]:
                            self.statDict[event.caster]["battle"]["shumuDPS"] += event.damageEff
                            if event.target not in self.shumu:
                                self.shumu[event.target] = {"lastDamage": event.time, "alive": 1, "damageList": [], "lastName": "未知"}
                            if event.damage > 0:
                                skillName = self.bld.info.getSkillName(event.full_id)
                                name = self.bld.info.getName(event.caster)
                                resultStr = ""
                                value = event.damage
                                self.shumu[event.target]["damageList"] = ["-%s, %s:%s%s(%d)" % (
                                        parseTime((int(event.time) - self.startTime) / 1000), name, skillName, resultStr, value)] + self.shumu[event.target]["damageList"]
                                if len(self.shumu[event.target]["damageList"]) > 20:
                                    del self.shumu[event.target]["damageList"][20]
                                self.shumu[event.target]["lastDamage"] = event.time
                                self.shumu[event.target]["lastID"] = event.caster

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 15000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

                        if key == "b26720":
                            self.bh.setEnvironment(event.id, "寒风消失", "341", event.time + 20000, 0, 1, "寒风消失", "buff")

            if event.id == "26839" and self.round in [1,2,3]:  # 搬运
                if event.stack == 1:
                    if self.prevThrow == 0:
                        self.prevThrow = event.time
                else:
                    # 计算本次用时
                    thisTime = event.time - self.prevThrow
                    self.prevThrow = event.time
                    self.statDict[event.target]["battle"]["banyun%d" % self.round] = thisTime

        elif event.dataType == "Shout":
            if event.content in ['""']:
                pass
            elif event.content in ['"……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"嗯……是何处出了差错？"']:
                pass
            elif event.content in ['"月泉宗主已经到达太极逆境，就算没有我，他也会用掩日魔剑污染龙脉，以求见到九老洞底的秘密……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"不过如果是你的话，或许真有可能阻止那个人……"']:
                pass
            elif event.content in ['"就让我看看吧，你究竟能做到什么地步……"']:
                pass
            elif event.content in ['"让我看看你们实力如何！"']:
                pass
            elif event.content in ['"你们无法改变失败的结局！"']:
                pass
            elif event.content in ['""']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["鬼筹宝箱", "??寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
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
            if event.id in self.bld.info.npc:
                if self.bld.info.npc[event.id].templateID == "125062" and event.enter == 0 and self.finalTime - event.time > 10000:
                    # print("[NPC]", parseTime((event.time - self.startTime) / 1000), event.id, self.bld.info.npc[event.id].templateID, self.bld.info.getName(event.id), event.enter,
                    #   self.bld.info.npc[event.id].x, self.bld.info.npc[event.id].y, self.bld.info.npc[event.id].z, self.bld.info.npc[event.id].dir)
                    with open("outputStone.txt", "a") as f:
                        s = "%d %d %d %d %d\n" % (event.time - self.startTime, self.bld.info.npc[event.id].x, self.bld.info.npc[event.id].y, self.bld.info.npc[event.id].z, self.bld.info.npc[event.id].dir)
                        f.write(s)
            else:
                pass
                # print("[badNPC]", parseTime((event.time - self.startTime) / 1000), event.id)

        elif event.dataType == "Death":  # 重伤记录
            pass
            if event.id in self.shumu:
                self.shumu[event.id]["alive"] = 0
                self.shumu[event.id]["lastDamage"] = event.time

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
            if event.id == "35939":
                self.round += 1
                self.prevThrow = 0

                    
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
        self.activeBoss = "鬼筹"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["s35931", "n124304", "s35935", "s35818", "s35640", "b26681", "b26769", "n124615",
                                 "b26809", "s35817", "b26896", "s35933", "s32392", "n124010", "n124880", "b26839",
                                 "s35937", "n125062", "n124887", "n125424", "b26770", "n124637", "s35800", "n125060",
                                 "s35863", "n124961", "s35637", "n125056", "n125044", "s35942", "n125054", "n124975",
                                 "n125476", "n122406", "n125103", "n125160", "n125372", "n125810", "n124020", "b8272",
                                 "n125295", "n125108"
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       "c35934": ["18446", "#ff00ff", 7000],  # 奔星
                       # b26896奔星
                       "c35933": ["2026", "#7700ff", 3000],  # 天震逆退
                       "b26720": ["3412", "#00ff00", 0],  # 寒风
                       "c36124": ["16837", "#77ff00", 3000],  # 堪舆
                       "c35939": ["16837", "#77ff00", 3000],  # 窥天
                       "c35936": ["11432", "#ff7700", 3000],  # 符海
                       "c35941": ["4504", "#ff0000", 3000],  # 星坠
                       "c36425": ["344", "#0000ff", 5000],  # 天星定命
                       # b26839 搬运
                       }

        # 数据格式：
        # 7 ？

        self.shumu = {}
        self.round = 0
        self.prevThrow = 0

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"shumuDPS": 0,
                                             "banyun1": 0,
                                             "banyun2": 0,
                                             "banyun3": 0}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


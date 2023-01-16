# Created by moeheart at 11/03/2022
# 刘展的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class LiuZhanWindow(SpecificBossWindow):
    '''
    刘展的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("刘展", "1200x900")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("刘展DPS", "对刘展的DPS。\n常规阶段时间：%s，包括40%%血量之前与40%%血量之后的两部分之和。" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("枪卫DPS", "对枪卫的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("斧卫DPS", "对斧卫的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["lzDPS"]))
            tb.AppendContext(int(line["battle"]["qwDPS"]))
            tb.AppendContext(int(line["battle"]["fwDPS"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("射箭复盘", "")
        tb.EndOfLine()
        num = 0
        for line in self.detail["shejian"]:
            tb.AppendContext(line["time"])
            tb.AppendContext(line["target"], color="#ff0000")
            num += 1
            if num % 5 == 0:
                tb.EndOfLine()
        if num % 5 != 0:
            tb.EndOfLine()
        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class LiuZhanReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        self.detail["P1Time"] = int((self.phaseTime[1] + self.phaseTime[3]) / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                # line = self.stat[id]
                res = self.getBaseList(id)
                res["battle"]["lzDPS"] = int(safe_divide(res["battle"]["lzDPS"], self.detail["P1Time"]))
                res["battle"]["qwDPS"] = int(safe_divide(res["battle"]["qwDPS"], self.detail["P2Time"]))
                res["battle"]["fwDPS"] = int(safe_divide(res["battle"]["fwDPS"], self.detail["P2Time"]))
                bossResult.append(res)
        # bossResult.sort(key=lambda x: -x[2])
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
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    # self.stat[event.caster][2] += event.damageEff
                    if self.bld.info.getName(event.target) in ["刘展", "劉展"]:
                        self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["lzDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["枪卫首领", "槍衛首領"]:
                        self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["qwDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["斧卫首领", "斧衛首領"]:
                        self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["fwDPS"] += event.damageEff

                if event.id == "33084":  # 射手援助
                    self.detail["shejian"].append({"time": parseTime((event.time - self.startTime) / 1000), "target": self.bld.info.getName(event.target)})

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
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

            if event.id == "23777":  # 飞挑·余劲
                if event.stack == 1:
                    self.xiazhuiStart[event.target] = event.time
                    # self.stunCounter[event.target].setState(event.time, 1)
                else:
                    self.bh.setCall("23777", "飞挑·余劲", "3428", self.xiazhuiStart[event.target], event.time - self.xiazhuiStart[event.target], event.target, "飞挑下坠")
                    # self.stunCounter[event.target].setState(event.time, 0)

            if event.id == "23771":  # 利斧断躯
                if event.stack == 1:
                    self.lifuStart[event.target] = event.time
                    self.stunCounter[event.target].setState(event.time, 1)
                else:
                    self.bh.setCall("23771", "利斧断躯", "2034", self.lifuStart[event.target], event.time - self.lifuStart[event.target], event.target, "利斧断躯点名承伤")
                    self.stunCounter[event.target].setState(event.time, 0)

            if event.id == "24601":  # 神射协助 TODO 以后用来分锅
                pass

        elif event.dataType == "Shout":
            if event.content in ['"尔等必葬身于此！"']:
                pass
            elif event.content in ['"山崩！"']:
                pass
            elif event.content in ['"石碎！"']:
                pass
            elif event.content in ['"枪斧卫出阵！速将这群狂徒拿下！"']:
                self.changePhase(event.time - 2000, 0)
                self.setTimer("phase", event.time + 7000, 2)
                self.bh.setBadPeriod(event.time - 2000, event.time + 7000, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"是！"']:
                pass
            elif event.content in ['"枪卫！列阵冲刺！"']:
                pass
            elif event.content in ['"感受这大地的震颤"']:
                pass
            elif event.content in ['"呃……"']:
                self.changePhase(event.time, 0)
                self.setTimer("phase", event.time + 6000, 3)
                self.bh.setBadPeriod(event.time, event.time + 6000, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"将军……"']:
                pass
            elif event.content in ['"唔……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"剁碎你们！"']:
                pass
            elif event.content in ['"将军……"']:
                pass
            elif event.content in ['"将军……"']:
                pass
            elif event.content in ['"大势已去了嘛……哼，来吧！"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["刘展宝箱", "劉展寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
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
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
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
        self.activeBoss = "刘展"

        self.initPhase(3, 1)

        self.bhBlackList.extend(["s31978", "n111991", "b23779", "s31998", "s31979", "b23370", "b23379", "s31982",
                                 "b24565", "n112050", "s31983", "s31987", "n110498", "s31984", "n112863", "s31986",
                                 "s31989", "b23769", "b23770", "n112051", "s32120",
                                 "s31991", "n110496", "n112041", "b23778", "n112067", "n112017",
                                 "n112032", "n110495", "s31995", "c32107", "n112472", "n112488", "n112505", "n112514",
                                 "n112527", "s32392", "n112543", "n112533"])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c32002": ["3452", "#773333", 6000],  # 山崩石碎斩
                       "c31995": ["3319", "#00ff00", 6000],  # 箭雨
                       "c31981": ["3430", "#ff00ff", 18000],  # 飞挑
                       "c31990": ["2034", "#ff7733", 11000],  # 利斧断躯
                       "c31992": ["3293", "#7700ff", 0],  # 指挥·坠鸟
                       "c31996": ["16", "#00ffff", 0],  # 枪气横扫
                       "c31994": ["3319", "#00ff00", 0],  # 指挥·万箭齐发
                       "c31988": ["3398", "#007700", 0],  # 重斧震地
                       'c31985': ["2144", "#0000ff", 0],  # 枪阵冲锋
                       }

        # 刘展数据格式：
        # 7 ？

        self.xiazhuiStart = {}
        self.lifuStart = {}

        for line in self.bld.info.player:
            # self.stat[line].extend([0, 0, 0])
            self.statDict[line]["battle"] = {"lzDPS": 0,
                                             "qwDPS": 0,
                                             "fwDPS": 0}
            self.xiazhuiStart[line] = 0
            self.lifuStart[line] = 0

        self.detail["shejian"] = []  # 射箭复盘

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


# Created by moeheart at 10/17/2021
# 雷域大泽4号-尤珈罗摩的复盘库。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class YoujiaLuomoWindow(SpecificBossWindow):
    '''
    尤珈罗摩复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.constructWindow("尤珈罗摩", "1200x1000")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("血瘤DPS", "对四个血瘤的DPS，这相当于P1的本体DPS。\nP1持续时间：%s，包含母蛊激活的垃圾时间。" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("鬼虫DPS", "对鬼虫的DPS，分母以P1总时间计算。")
        tb.AppendHeader("勇虫DPS", "对勇虫的DPS，分母以P1总时间计算。")
        tb.AppendHeader("毒尸DPS", "对毒尸的DPS，分母以P1总时间计算。")
        tb.AppendHeader("P2DPS", "对血蛊巢心的DPS。\nP2持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line[7]))
            tb.AppendContext(int(line[8]))
            tb.AppendContext(int(line[9]))
            tb.AppendContext(int(line[10]))
            tb.AppendContext(int(line[11]))

            # 心法复盘
            if line[0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line[0]], line[0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class YoujiaLuomoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        if self.phase != 0:
            self.phaseTime[self.phase] = self.finalTime - self.phaseStart

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)

        for line in self.dgxl:
            self.bh.setEnvironment("27747", "毒蛊血露", "4504", line[0], line[1]-line[0], 1, "")

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.stat:
                line = self.stat[id]
                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = "%s|%s"%(self.equipmentDict[id]["sketch"], self.equipmentDict[id]["forge"])
                else:
                    line[5] = "|"
                
                if getOccType(self.occDetailList[id]) == "healer":
                    line[3] = int(self.hps[id] / self.battleTime * 1000)

                line[6] = self.stunCounter[id].buffTimeIntegral() / 1000

                dps = int(line[2] / self.battleTime * 1000)
                bossResult.append([line[0],
                                   line[1],
                                   dps, 
                                   line[3],
                                   line[4],
                                   line[5],
                                   line[6],
                                   line[7] / (self.detail["P1Time"] + 1e-10),
                                   line[8] / (self.detail["P1Time"] + 1e-10),
                                   line[9] / (self.detail["P1Time"] + 1e-10),
                                   line[10] / (self.detail["P1Time"] + 1e-10),
                                   line[11] / (self.detail["P2Time"] + 1e-10),
                                   ])
        bossResult.sort(key=lambda x:-x[2])
        self.effectiveDPSList = bossResult

        return self.effectiveDPSList, self.potList, self.detail
        
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

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff
                    
            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.npc[event.target].name in ["赐恩血瘤", "賜恩血瘤"]:
                            self.stat[event.caster][7] += event.damageEff
                            # 瘤子的开怪检测
                            if event.target not in self.xueLiuFirstHit:
                                self.xueLiuFirstHit[event.target] = 1
                                self.xueLiuActiveNum += 1
                                if self.xueLiuActiveNum == 3 and self.xueLiuFirstDown != 1:  # 分锅
                                    self.potList.append([self.bld.info.player[event.caster].name,
                                                         self.occDetailList[event.caster],
                                                         0,
                                                         self.bossNamePrint,
                                                         "%s提前开对场瘤子" % (parseTime((event.time - self.startTime) / 1000)),
                                                         []])

                        elif self.bld.info.npc[event.target].name in ["摄魂鬼虫", "攝魂鬼蟲"]:
                            self.stat[event.caster][8] += event.damageEff
                        elif self.bld.info.npc[event.target].name in ["秽血勇虫", "穢血勇蟲"]:
                            self.stat[event.caster][9] += event.damageEff
                        elif self.bld.info.npc[event.target].name in ["毒尸", "毒屍"]:
                            self.stat[event.caster][10] += event.damageEff
                        elif self.bld.info.npc[event.target].name in ["血蛊巢心", "血蠱巢心"]:
                            if event.damageEff > 0 and self.phase != 2:
                                self.phaseTime[1] = event.time - self.startTime
                                self.phase = 2
                                self.phaseStart = event.time
                                self.bh.setEnvironment("0", "血蛊巢心激活", "3398", event.time - 15000, 15000, 1, "")
                            self.stat[event.caster][11] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "20289" and event.stack == 1:  # 凝视
                self.bh.setCall("20289", "毒痰目标", "330", event.time, 0, event.target, "点名排蓝圈")

            if event.id in ["20775", "20180"]:  # 鬼虫点名
                self.stunCounter[event.target].setState(event.time, event.stack)

        elif event.dataType == "Shout":
            pass

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["血蛊巢心", "血蠱巢心"]:
                self.win = 1
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["赐恩血瘤", "賜恩血瘤"]:
                self.xueLiuFirstDown = 1

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].templateID == "106070":
                if event.enter:
                    if event.time - self.dgxl[-1][0] > 2000:
                        self.dgxl.append([event.time, self.finalTime])
                else:
                    self.dgxl[-1][1] = event.time
                    
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
        self.activeBoss = "尤珈罗摩"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 尤珈罗摩数据格式：
        # 7 血瘤DPS, 8 鬼虫DPS, 9 勇虫DPS, 10 毒尸DPS, 11 P2DPS
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.stunCounter = {}
        self.xueLiuFirstHit = {}
        self.xueLiuActiveNum = 0
        self.xueLiuFirstDown = 0

        self.phase = 1
        self.phaseStart = self.startTime
        self.phaseTime = [0, 0, 0]

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.dgxl = [[0, 0]]  # 毒蛊血露
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0, 0]
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


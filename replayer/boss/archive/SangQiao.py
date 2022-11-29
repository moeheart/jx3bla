# Created by moeheart at 10/17/2021
# 雷域大泽2号-桑乔的复盘库。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class SangQiaoWindow(SpecificBossWindow):
    '''
    桑乔复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.constructWindow("桑乔", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("本体DPS", "对桑乔本体的DPS。")
        tb.AppendHeader("丝魂缚锁", "对蜘蛛网的DPS，分母以总时间计算。")
        tb.AppendHeader("真蜘蛛茧", "对真蜘蛛茧的伤害，只有救人成功的蜘蛛茧才被视为真蜘蛛茧。")
        tb.AppendHeader("假蜘蛛茧", "对假蜘蛛茧的伤害，错误的蜘蛛茧或是没打掉的蜘蛛茧均为假蜘蛛茧。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line[7]))
            tb.AppendContext(int(line[8]))
            tb.AppendContext(int(line[9]))

            color10 = "#000000"
            if line[10] > line[9]:
                color10 = "#ff0000"
            tb.AppendContext(int(line[10]), color=color10)

            # 心法复盘
            if line[0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class SangQiaoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        # 结算蜘蛛茧伤害
        for line2 in self.zzl:
            for line in self.zzl[line2]["dps"]:
                if self.zzl[line2]["status"] == 1:
                    self.stat[line][9] += self.zzl[line2]["dps"][line]
                else:
                    self.stat[line][10] += self.zzl[line2]["dps"][line]
        for line in self.tscj:
            self.bh.setEnvironment("27803", "吐丝成茧", "371", line[0], line[1]-line[0], 1, "")

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
                                   int(line[7] / self.battleTime * 1000),
                                   int(line[8] / self.battleTime * 1000),
                                   int(line[9] / self.battleTime * 1000),
                                   int(line[10] / self.battleTime * 1000),
                                   ])
        bossResult.sort(key=lambda x: -x[2])
        self.effectiveDPSList = bossResult

        return self.effectiveDPSList, self.potList, self.detail, self.stunCounter
        
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
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps: #非化解
                    self.hps[event.caster] += event.healEff
                    
            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["桑乔""", "桑喬"]:
                            self.stat[event.caster][7] += event.damageEff
                        elif self.bld.info.getName(event.target) in ["蜘蛛网", "蜘蛛網"]:
                            self.stat[event.caster][8] += event.damageEff
                        elif self.bld.info.getName(event.target) in ["蜘蛛茧", "蜘蛛繭"]:
                            self.zzl[event.target]["dps"][event.caster] += event.damageEff
                
        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "20139":  # 吐丝成茧
                self.stunCounter[event.target].setState(event.time, event.stack)
                if event.stack == 1:
                    if event.time - self.tscj[-1][0] > 1000:
                        self.tscj.append([event.time, 0])
                    self.zzlCount += 1
                    self.bh.setCall("20139", "吐丝成茧", "371", event.time, 0, event.target, "点名内场")
                else:
                    self.zzlCount -= 1
                    if self.zzlCount == 0:
                        self.tscj[-1][1] = event.time + 5000

            if event.id == "20112":  # 丝魂缚锁
                self.stunCounter[event.target].setState(event.time, event.stack)

            if event.id == "20163":
                print("[Sangqiao]", event.id, event.level, event.stack, event.time, event.target, self.bld.info.player[event.target].name)
                    
        elif event.dataType == "Shout":
            return
                
        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ['桑乔', "桑喬"]:
                self.win = 1  # 击杀判定
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["蜘蛛茧", "蜘蛛繭"]:
                if event.time - self.xzzTime > 100:
                    self.zzl[event.id]["status"] = 1  # 正确
                    self.zzl[event.id]["time"] = event.time
                else:
                    self.zzl[event.id]["status"] = 2  # 错误

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["小蜘蛛"] and event.enter:
                self.xzzTime = event.time
                for line in self.zzl:
                    if self.zzl[line]["status"] == 1 and event.time - self.zzl[line]["time"] < 100:
                        self.zzl[line]["status"] = 2
            
        elif event.dataType == "Battle":  # 战斗状态变化
            pass
                    
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
        self.activeBoss = "桑乔"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 桑乔数据格式：
        # 7 本体DPS 8 丝魂缚锁 9 真蜘蛛茧 10 假蜘蛛茧
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.stunCounter = {}

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.tscj = [[0, 0]]
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0]
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

        # 统计蜘蛛茧
        self.zzl = {}
        self.zzlCount = 0
        self.xzzTime = 0  # 小蜘蛛出现
        for line2 in self.bld.info.npc:
            # print(self.bld.info.npc[line2].name)
            if self.bld.info.npc[line2].name in ["蜘蛛茧", "蜘蛛繭"]:
                self.zzl[line2] = {"dps": {}, "status": 0, "time": 0}
                for line in self.bld.info.player:
                    self.zzl[line2]["dps"][line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


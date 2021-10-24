# Created by moeheart at 03/29/2021
# 宇文灭的定制复盘方法库. 已重置为新的数据形式.
# 宇文灭是白帝江关5号首领，复盘主要集中在以下几个方面：
# 分阶段的DPS，传染分锅

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class YuwenMieWindow(SpecificBossWindow):
    '''
    宇文灭的专有复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('宇文灭详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #宇文灭数据格式：
        #7 P1DPS 8 玄冰1 9 玄冰2 10 群攻玄冰 11 P2DPS 12 关键治疗量
        
        tb = TableConstructorMeta(frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。")
        
        tb.AppendHeader("P1DPS", "P1的DPS，包括对宇文灭及九阴玄冰的输出。\nP1时长：%s"%parseTime(self.detail["P1Time"]))
        tb.AppendHeader("玄冰1", "对第一次玄冰夺命掌·夺魄生成的玄冰的DPS，分母为整个P1的时间。")
        tb.AppendHeader("玄冰2", "对第二次玄冰夺命掌·夺魄生成的玄冰的DPS，分母为整个P1的时间。")
        tb.AppendHeader("群攻玄冰", "对非玄冰夺命掌·夺魄生成的玄冰的DPS，分母为整个P1的时间。")
        tb.AppendHeader("P2DPS", "P2的DPS，包括对宇文灭及九阴玄冰的输出。\nP2时长：%s"%parseTime(self.detail["P2Time"]))
        tb.AppendHeader("关键治疗", "对寒劫与寒狱目标的治疗量。减伤会被等效。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            name = self.effectiveDPSList[i][0]
            color = getColor(self.effectiveDPSList[i][1])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(int(self.effectiveDPSList[i][2]))

            if getOccType(self.effectiveDPSList[i][1]) != "healer":
                text3 = str(self.effectiveDPSList[i][3]) + '%'
                color3 = "#000000"
            else:
                text3 = self.effectiveDPSList[i][3]
                color3 = "#00ff00"
            tb.AppendContext(text3, color=color3)
            
            text4 = "-"
            if self.effectiveDPSList[i][4] != -1:
                text4 = int(self.effectiveDPSList[i][4])
            tb.AppendContext(text4)
            
            tb.AppendContext(self.effectiveDPSList[i][5])
            tb.AppendContext(int(self.effectiveDPSList[i][6]))
            
            tb.AppendContext(int(self.effectiveDPSList[i][7]))
            tb.AppendContext(int(self.effectiveDPSList[i][8]))
            tb.AppendContext(int(self.effectiveDPSList[i][9]))
            tb.AppendContext(int(self.effectiveDPSList[i][10]))
            tb.AppendContext(int(self.effectiveDPSList[i][11]))
            
            color12 = "#000000"
            if self.effectiveDPSList[i][12] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color12 = "#00ff00"
            tb.AppendContext(int(self.effectiveDPSList[i][12]), color = color12)
            
            # 心法复盘
            if self.effectiveDPSList[i][0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[self.effectiveDPSList[i][0]], self.effectiveDPSList[i][0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()
            
        frame2 = tk.Frame(window)
        frame2.pack()
        
        tb = TableConstructorMeta(frame2)
        
        tb.AppendHeader("P2传染次数", "代表P2的寒劫与寒狱从每名玩家传染出去的次数，主要用于寒狱进冰进晚的分锅。")
        for i in range(len(self.detail["P2fire"])):
            if i % 5 == 0:
                tb.EndOfLine()
            name = self.detail["P2fire"][i][0]
            color = getColor(self.detail["P2fire"][i][1])
            num = self.detail["P2fire"][i][2]
            tb.AppendContext(name, color=color)
            tb.AppendContext(num)
            
        tb.EndOfLine()
        tb.AppendHeader("最后一次传染", "代表P2最后一次传染的起点与终点，主要用于buff传丢的分锅。")
        name1 = self.detail["P2last"][0]
        color1 = getColor(self.detail["P2last"][1])
        name2 = self.detail["P2last"][2]
        color2 = getColor(self.detail["P2last"][3])
        tb.AppendContext(name1, color=color1)
        tb.AppendContext(name2, color=color2)

        frame3 = tk.Frame(window)
        frame3.pack()
        buttonPrev = tk.Button(frame3, text='<<', width=2, height=1, command=self.openPrev)
        submitButton = tk.Button(frame3, text='战斗事件记录', command=self.openPot)
        buttonNext = tk.Button(frame3, text='>>', width=2, height=1, command=self.openNext)
        buttonPrev.grid(row=0, column=0)
        submitButton.grid(row=0, column=1)
        buttonNext.grid(row=0, column=2)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, effectiveDPSList, detail, occResult={}):
        super().__init__(effectiveDPSList, detail, occResult)

class YuwenMieReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        for line in self.bjbp:
            self.bh.setEnvironment("26803", "冰晶爆破", "3448", line[0], line[1]-line[0], 1, "")
        for line in self.xbgn:
            self.bh.setEnvironment("26229", "玄冰功·凝", "3448", line[0], line[1]-line[0], 1, "")

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()
        
        self.phaseStart[1] = self.startTime
        if self.phaseEnd[2] == 0:
            self.phaseEnd[2] = self.finalTime
        self.phaseTime = [1e+20] * 3
        for i in range(1, 3):
            if self.phaseStart[i] != 0 and self.phaseEnd[i] != 0:
                self.phaseTime[i] = (self.phaseEnd[i] - self.phaseStart[i]) / 1000
                
        self.detail["P1Time"] = self.phaseTime[1]
        self.detail["P2Time"] = self.phaseTime[2]

        bossResult = []
        for id in self.bld.info.player:
            if id in self.stat:
                line = self.stat[id]
                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = self.equipmentDict[id]["sketch"]
                
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
                                   int(line[7] / self.phaseTime[1]),
                                   int(line[8] / self.phaseTime[1]),
                                   int(line[9] / self.phaseTime[1]),
                                   int(line[10] / self.phaseTime[1]),
                                   int(line[11] / self.phaseTime[2]),
                                   int(line[12]),
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        for line in self.P2fire:
            self.detail["P2fire"].append([self.bld.info.player[line].name, self.occDetailList[line], self.P2fire[line]])
        self.detail["P2fire"].sort(key = lambda x:-x[2])
            
        return self.effectiveDPSList, self.potList, self.detail
        
    def recordDeath(self, item, deathSource):
        '''
        在有玩家重伤时记录狂热值的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        - deathSource 重伤来源。
        '''
        pass

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - event 复盘数据，意义同茗伊复盘。
        '''
        
        if self.chuanRanQueue != [] and event.time - self.chuanRanQueue[0][0] >= 1000:
            chuanRanTime = self.chuanRanQueue[0][0]
            chuanRanType = self.chuanRanQueue[0][1]
            source = self.chuanRanQueue[0][2]
            target = self.chuanRanQueue[0][3]
            if chuanRanType == 1:
                if self.hanJieCounter[target].checkState(chuanRanTime-500) == 0 and self.hanJieCounter[target].checkState(chuanRanTime+1000) == 1:  # 传染寒劫
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.bld.info.player[target].name
                        self.potList.append([self.bld.info.player[potID].name,
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫传染：%s" % (potTime, victimName),
                                             ["接锅者中寒劫并靠近没有中buff的队友，导致目标也被传染寒劫。"]])

                elif self.hanJieCounter[target].checkState(chuanRanTime-500) == 1 and self.hanYuCounter[target].checkState(chuanRanTime+1000) == 1:  # 寒劫变寒狱
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.bld.info.player[target].name
                        self.potList.append([self.bld.info.player[potID].name,
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫升级：%s" % (potTime, victimName),
                                             ["接锅者中寒劫并靠近中寒劫的队友，导致两人的寒劫被升级为寒狱。"]])
                        self.potList.append([victimName,
                                             self.occDetailList[target],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫升级：%s" % (potTime, self.bld.info.player[potID].name),
                                             ["接锅者中寒劫并靠近中寒劫的队友，导致两人的寒劫被升级为寒狱。"]])
            elif chuanRanType == 2:
                if self.hanYuCounter[target].checkState(chuanRanTime-500) == 0 and self.hanYuCounter[target].checkState(chuanRanTime+1000) == 1:  # 传染寒狱
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.bld.info.player[target].name
                        self.potList.append([self.bld.info.player[potID].name,
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒狱传染：%s" % (potTime, victimName),
                                             ["接锅者中寒狱并靠近没有中buff的队友，导致目标也被传染寒狱。"]])
            del self.chuanRanQueue[0]

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                healRes = self.criticalHealCounter[event.target].recordHeal(event)
                if healRes != {}:
                    for line in healRes:
                        if line in self.bld.info.player:
                            self.stat[line][12] += healRes[line]

                if event.id == "26224":  # 寒劫传染
                    self.chuanRanQueue.append([event.time, 1, event.caster, event.target])

                if event.id == "26225":  # 寒狱传染
                    self.chuanRanQueue.append([event.time, 2, event.caster, event.target])

                if event.id in ["26224", "26225"] and self.phase == 2:
                    if event.caster not in self.P2fire:
                        self.P2fire[event.caster] = 0
                    self.P2fire[event.caster] += 1
                    self.detail["P2last"] = [self.bld.info.player[event.caster].name, self.occDetailList[event.caster],
                                             self.bld.info.player[event.target].name, self.occDetailList[event.target]]

                if event.id == "26803":  # 冰晶爆破
                    if event.time - self.bjbp[-1][1] > 3000:
                        self.bjbp.append([event.time - 5000, event.time])

                if event.id == "26229":  # 玄冰功·凝
                    if event.time - self.xbgn[-1][1] > 3000:
                        self.xbgn.append([event.time - 5000, event.time])

            else:

                if event.caster in self.bld.info.player:
                    self.stat[event.caster][2] += event.damageEff
                    if self.phase == 1:
                        self.stat[event.caster][7] += event.damageEff
                    elif self.phase == 2:
                        self.stat[event.caster][11] += event.damageEff

                    if event.target in self.xuanBingDamage:
                        if event.caster not in self.xuanBingDamage[event.target]:
                            self.xuanBingDamage[event.target][event.caster] = 0
                        self.xuanBingDamage[event.target][event.caster] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return
            # 记录自身寒劫，寒狱，玄冰夺命掌
            if event.id == "18861":
                self.hanJieCounter[event.target].setState(event.time, event.stack)
                if event.stack == 1:
                    self.criticalHealCounter[event.target].active()
                    self.criticalHealCounter[event.target].setCriticalTime(-1)
                    self.bh.setCall("18861", "九阴玄冰劲·寒劫", "4552", event.time, 0, event.target, "寒劫点名或被传染")
                else:
                    self.criticalHealCounter[event.target].unactive()

            if event.id == "18862":
                self.hanYuCounter[event.target].setState(event.time, event.stack)
                if event.stack == 1:
                    self.criticalHealCounter[event.target].active()
                    self.criticalHealCounter[event.target].setCriticalTime(-1)
                    self.bh.setCall("18862", "九阴玄冰劲·寒狱", "4534", event.time, 0, event.target, "寒狱点名或被传染")
                else:
                    self.criticalHealCounter[event.target].unactive()

            if event.id in ["19364", "18863"]:  # 冻结
                self.stunCounter[event.target].setState(event.time, event.stack)

            if event.id == "19042" and event.stack == 1:  # 夺命掌的目标
                self.bh.setCall("19042", "夺命掌的目标", "3448", event.time, 0, event.target, "夺命掌的目标")

            if event.id == "18863" and self.phase == 1 and event.stack == 1:
                # 判断是否是不可避免的结冰
                timeSafe = 0
                xuanBingTime = event.time - self.startTime
                if xuanBingTime >= 50000 and xuanBingTime <= 75000:
                    timeSafe = 1
                elif xuanBingTime >= 160000 and xuanBingTime <= 185000:
                    timeSafe = 1
                elif xuanBingTime >= 250000 and xuanBingTime <= 265000:
                    timeSafe = 1
                if timeSafe == 0:
                    potTime = parseTime((event.time - self.startTime) / 1000)
                    potID = event.target
                    self.potList.append([self.bld.info.player[potID].name,
                                         self.occDetailList[potID],
                                         0,
                                         self.bossNamePrint,
                                         "%s意外结冰" % (potTime),
                                         ["在挡线、寒狱+打断以外的P1阶段结冰"]])
                    
        elif event.dataType == "Shout":
                
            if event.content in ['"今日便拼个你死我活！"']:
                self.phase = 2
                self.phaseEnd[1] = event.time
                self.phaseStart[2] = event.time
                self.bh.setEnvironment("26842", "九阴破灭枪罡", "2028", event.time, 5000, 1, "")
                
        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "宇文灭":
                self.win = 1
                self.phaseEnd[2] = event.time
            pass
            
        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "九阴玄冰":
                if event.enter:
                    self.xuanBingDamage[event.id] = {'sum': 0, 'time': event.time}
                else:
                    xuanBingType = 0
                    xuanBingTime = self.xuanBingDamage[event.id]['time'] - self.startTime
                    if xuanBingTime >= 50000 and xuanBingTime <= 75000:
                        xuanBingType = 8
                    elif xuanBingTime >= 160000 and xuanBingTime <= 185000:
                        xuanBingType = 9
                    elif self.phase == 1:
                        xuanBingType = 10
                    if xuanBingType != 0:
                        for line in self.xuanBingDamage[event.id]:
                            if line != 'sum' and line != 'time':
                                self.stat[line][xuanBingType] += self.xuanBingDamage[event.id][line]
            
        elif event.dataType == "Battle": #战斗状态变化
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
        self.activeBoss = "宇文灭"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #宇文灭数据格式：
        #7 P1DPS 8 玄冰1 9 玄冰2 10 群攻玄冰 11 P2DPS 12 关键治疗量
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "宇文灭"
        self.win = 0
        self.stunCounter = {}
        
        self.phase = 1
        self.phaseStart = [0, 0, 0]
        self.phaseEnd = [0, 0, 0]
        self.xuanBingDamage = {}
        
        self.hanJieCounter = {}
        self.hanYuCounter = {}
        self.chuanRanQueue = []
        
        self.P2fire = {}
        self.detail["P2fire"] = []
        self.detail["P2last"] = ["未知", "0", "未知", "0"]
        
        self.criticalHealCounter = {}

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.bjbp = [[0, 0]]
        self.xbgn = [[0, 0]]
        
        for line in self.bld.info.player:
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0, 0, 0]
            self.hps[line] = 0
            self.hanJieCounter[line] = BuffCounter(18861, self.startTime, self.finalTime)
            self.hanYuCounter[line] = BuffCounter(18862, self.startTime, self.finalTime)
            self.criticalHealCounter[line] = CriticalHealCounter()
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


# Created by moeheart at 03/29/2021
# 姜集苦的定制复盘方法库。
# 姜集苦是白帝江关4号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class JiangJikuWindow(SpecificBossWindow):
    '''
    姜集苦的专有复盘窗口类。
    ''' 

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('姜集苦详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。")
        tb.AppendHeader("P1DPS", "70%%血量之前阶段的DPS。\nP1时长：%s"%parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "70%%血量之后阶段的DPS。这部分DPS同样包括易伤阶段。\nP2时长：%s"%parseTime(self.detail["P2Time"]))
        tb.AppendHeader("易伤DPS", "易伤阶段的DPS，指走圈结束的20秒易伤时间中产生的DPS。\n时长：%s"%parseTime(self.detail["P3Time"]))
        tb.AppendHeader("关键治疗", "对走圈阶段时站桩T的治疗。减伤会被等效。")
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
            
            color10 = "#000000"
            if self.effectiveDPSList[i][10] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color10 = "#00ff00"
            tb.AppendContext(int(self.effectiveDPSList[i][10]), color=color10)
            
            # 心法复盘
            if self.effectiveDPSList[i][0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[self.effectiveDPSList[i][0]], self.effectiveDPSList[i][0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        buttonPrev = tk.Button(frame2, text='<<', width=2, height=1, command=self.openPrev)
        submitButton = tk.Button(frame2, text='战斗事件记录', command=self.openPot)
        buttonNext = tk.Button(frame2, text='>>', width=2, height=1, command=self.openNext)
        buttonPrev.grid(row=0, column=0)
        submitButton.grid(row=0, column=1)
        buttonNext.grid(row=0, column=2)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, effectiveDPSList, detail, occResult):
        super().__init__(effectiveDPSList, detail, occResult)

class JiangJikuReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        for line in self.sqhf:
            self.bh.setEnvironment("26611", "三清化符", "11432", line[0], line[1]-line[0], 1, "")
        for line in self.qsqhf:
            self.bh.setEnvironment("26743", "炁·三清化符", "11432", line[0], line[1]-line[0], 1, "")

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()
        
        self.phaseStart[1] = self.startTime
        self.phaseEnd[2] = self.finalTime
        if self.phaseEnd[3] > self.finalTime:
            self.phaseEnd[3] = self.finalTime
        self.phaseTime = [1e+20] * 4
        for i in range(1, 4):
            if self.phaseStart[i] != 0 and self.phaseEnd[i] != 0:
                self.phaseTime[i] = int((self.phaseEnd[i] - self.phaseStart[i]) / 1000)
                
        self.detail["P1Time"] = self.phaseTime[1]
        self.detail["P2Time"] = self.phaseTime[2]
        self.detail["P3Time"] = self.phaseTime[3]

        bossResult = []
        for id in self.bld.info.player:
            if id in self.stat:
                line = self.stat[id]
                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = self.equipmentDict[id]["sketch"]
                
                if getOccType(self.occDetailList[id]) == "healer":
                    line[3] = int(self.hps[id] / self.battleTime * 1000)

                dps = int(line[2] / self.battleTime * 1000)
                bossResult.append([line[0],
                                   line[1],
                                   dps, 
                                   line[3],
                                   line[4],
                                   line[5],
                                   line[6],
                                   int(line[7] / self.phaseTime[1]),
                                   int(line[8] / self.phaseTime[2]),
                                   int(line[9] / self.phaseTime[3]),
                                   line[10]
                                   ])
        bossResult.sort(key=lambda x: -x[2])
        self.effectiveDPSList = bossResult
            
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
        
        if self.yiShang and event.time > self.phaseEnd[3]:
            self.yiShang = 0
        
        if event.dataType == "Skill":

            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff
                        
                healRes = self.criticalHealCounter[event.target].recordHeal(event)
                if healRes != {}:
                    if self.zouQuan:
                        for line in healRes:
                            if line in self.bld.info.player:
                                self.stat[line][10] += healRes[line]

                if event.id == "26611":  # 三清化符
                    if event.time - self.sqhf[-1][1] > 3000:
                        self.sqhf.append([event.time - 5000, event.time])

                if event.id == "26743":  # 炁·三清化符
                    if event.time - self.qsqhf[-1][1] > 3000:
                        self.qsqhf.append([event.time - 5000, event.time])

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if self.phase == 1:
                        self.stat[event.caster][7] += event.damageEff
                    elif self.phase == 2:
                        self.stat[event.caster][8] += event.damageEff
                    if self.yiShang:
                        self.stat[event.caster][9] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return
                
            if event.id == "19367":  # 速符
                if event.stack == 1:
                    self.criticalHealCounter[event.target].active()
                    self.criticalHealCounter[event.target].setCriticalTime(-1)
                elif event.stack == 0:
                    self.criticalHealCounter[event.target].unactive()
                    
        elif event.dataType == "Shout":
                
            if event.content in ['"就让你们见识下这金符的威力！"']:
                self.phase = 2
                self.phaseEnd[1] = event.time
                self.phaseStart[2] = event.time
                self.bh.setEnvironment("26842", "金符凝炁", "325", event.time, 5000, 1, "")
                
            if event.content in ['"唔...岂有此理！"']:
                self.yiShang = 1
                self.phaseStart[3] = event.time
                self.phaseEnd[3] = event.time + 20000
                self.zouQuan = 0

            # print(event.content, event.time)
                
            if event.content in ['"黑云密布，电火奔星。天令一下，速震速轰！"']:
                if self.phase == 2:
                    self.zouQuan = 1
                    self.bh.setEnvironment("26840", "炁·混雷天诀", "8315", event.time, 62000, 1, "")

            if event.content in ['"太上火铃，炎帝之精。随吾三炁，焚灭邪精，急急如律令！"']:
                if self.phase == 1:
                    self.bh.setEnvironment("26612", "缠地烈火咒", "8317", event.time, 12000, 1, "")
                elif self.phase == 2:
                    self.bh.setEnvironment("26744", "炁·缠地烈火咒", "8317", event.time, 17000, 1, "")

            if event.content in ['"你们这些缠人的妖孽，见我道术！"']:
                if self.phase == 2:
                    self.bh.setEnvironment("26746", "炁·退邪剑气", "12457", event.time, 6000, 1, "")

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "姜集苦":
                self.win = 1

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
        self.activeBoss = "姜集苦"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #姜集苦数据格式：
        #7 P1DPS, 8 P2DPS, 9 爆发DPS, 10 关键治疗量
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "姜集苦"
        self.win = 0
        self.phase = 1
        self.yiShang = 0
        self.zouQuan = 0
        
        self.criticalHealCounter = {}
        
        self.phaseStart = [0, 0, 0, 0]
        self.phaseEnd = [0, 0, 0, 0]

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.sqhf = [[0, 0]]
        self.qsqhf = [[0, 0]]
        
        for line in self.bld.info.player:
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0]
            self.hps[line] = 0
            self.criticalHealCounter[line] = CriticalHealCounter()

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


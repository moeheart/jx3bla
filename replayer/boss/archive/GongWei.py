# Created by moeheart at 03/29/2021
# 宫威的定制复盘方法库. 已重置为新的数据形式.
# 宫威是白帝江关6号首领.

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk

class GongWeiWindow(SpecificBossWindow):
    '''
    宫威的专有复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('宫威详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("强化", "装备强化列表，表示[精炼满级装备数量]/[插8]-[插7]-[插6]/[五彩石等级]/[紫色附魔]-[蓝色附魔]/[大附魔：手腰脚头衣裤]")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            name = self.getMaskName(self.effectiveDPSList[i][0])
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
            color4 = "#000000"
            if "大橙武" in self.effectiveDPSList[i][5]:
                color4 = "#ffcc00"
            tb.AppendContext(text4, color=color4)
            
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[0])
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[1])
            tb.AppendContext(int(self.effectiveDPSList[i][6]))

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

    def __init__(self, config, effectiveDPSList, detail, occResult):
        super().__init__(config, effectiveDPSList, detail, occResult)

class GongWeiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        for line in self.bhlc:
            self.bh.setEnvironment("26438", "捭阖连锤", "3450", line[0], line[1]-line[0], 1, "")

        if self.kjbss[0][0] != 0 and self.kjbss[0][1] != 0:
            self.bh.setEnvironment("26626", "狂劲搬山摔", "4544", self.kjbss[0][0], self.kjbss[0][1] - self.kjbss[0][0], 1, "")

        if self.kjldzd[0][0] != 0 and self.kjldzd[0][1] != 0:
            self.bh.setEnvironment("26347", "狂劲裂地重蹬", "4006", self.kjldzd[0][0], self.kjldzd[0][1] - self.kjldzd[0][0], 1, "")

        if self.kjbss[1][0] != 0 and self.kjbss[1][1] != 0:
            self.bh.setEnvironment("26626", "狂劲搬山摔", "4544", self.kjbss[1][0], self.kjbss[1][1] - self.kjbss[1][0], 1, "")

        if self.kjldzd[1][0] != 0 and self.kjldzd[1][1] != 0:
            self.bh.setEnvironment("26347", "狂劲裂地重蹬", "4006", self.kjldzd[1][0], self.kjldzd[1][1] - self.kjldzd[1][0], 1, "")

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

                dps = int(line[2] / self.battleTime * 1000)
                bossResult.append([line[0],
                                   line[1],
                                   dps,
                                   line[3],
                                   line[4],
                                   line[5],
                                   line[6],
                                   ])
        bossResult.sort(key=lambda x: -x[2])
        self.effectiveDPSList = bossResult
            
        return self.effectiveDPSList, self.potList, self.detail, self.stunCounter

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - event 复盘数据，意义同茗伊复盘。
        '''

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                if event.id == "26438":  # 捭阖连锤·终
                    if event.time - self.bhlc[-1][0] > 50000:
                        self.bhlc.append([event.time - 22000, event.time])

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "19424":  # 怯懦
                if event.stack == 1:
                    if self.kjbss[0][0] == 0:
                        self.kjbss[0][0] = event.time
                    elif event.time - self.kjbss[0][0] > 100000:  # 间隔至少100秒
                        self.kjbss[1][0] = event.time
                else:
                    if self.kjbss[0][1] == 0:
                        self.kjbss[0][1] = event.time
                    elif event.time - self.kjbss[0][1] < 100000 and self.kjbss[1][0] == 0:  # 间隔至少100秒
                        self.kjbss[0][1] = event.time
                    else:
                        self.kjbss[1][1] = event.time

            if event.id == "18912":  # 动弹不得
                if event.stack == 1:
                    if self.kjldzd[0][0] == 0:
                        self.kjldzd[0][0] = event.time
                    elif event.time - self.kjldzd[0][0] > 100000 and self.kjldzd[1][0] == 0:  # 间隔至少100秒
                        self.kjldzd[1][0] = event.time
                else:
                    if self.kjldzd[0][1] == 0:
                        self.kjldzd[0][1] = event.time
                    elif event.time - self.kjldzd[0][1] < 100000:  # 间隔至少100秒
                        self.kjldzd[0][1] = event.time
                    else:
                        self.kjldzd[1][1] = event.time

        elif event.dataType == "Shout":
            if event.content in ['"喝啊……看！这疤痕，就是俺的忠诚！"']:
                self.phase = 2
                
        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "宫威":
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
        self.activeBoss = "宫威"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 宫威数据格式：
        # 待实现
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "宫威"
        self.win = 0
        self.phase = 1

        # 记录BOSS技能轴
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.kjbss = [[0, 0], [0, 0]]
        self.kjldzd = [[0, 0], [0, 0]]
        self.bhlc = [[0, 0]]
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                []

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


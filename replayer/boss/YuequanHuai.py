# Created by moeheart at 10/17/2021
# 雷域大泽5号-月泉淮的复盘库。

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class YuequanHuaiWindow(SpecificBossWindow):
    '''
    月泉淮复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        #window = tk.Tk()
        window.title('月泉淮复盘')
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
        tb.AppendHeader("幻象DPS", "对幻象（也即大团主要的输出目标）的DPS。")
        tb.AppendHeader("内力球DPS", "对蓄积的内力的DPS，分母以全流程计算。")
        tb.AppendHeader("天锁DPS", "对天锁的DPS，分母以全流程计算。")
        tb.AppendHeader("关键治疗", "对天锁目标的有效治疗量，减伤会被等效计算。")
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
            tb.AppendContext(text4)
            
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[0])
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[1])
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

    def __init__(self, config, effectiveDPSList, detail, occResult):
        super().__init__(config, effectiveDPSList, detail, occResult)

class YuequanHuaiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        if self.phase == 2 and self.finalTime - self.yqjqTime < 35000:  # 分片判定
            self.yqhInterrupt = 1

        for line in self.xjdnl:
            self.bh.setEnvironment("28284", "蓄积的内力", "3427", line[0], line[1]-line[0], 1, "")
        for line in self.yqts:
            self.bh.setEnvironment("28440", "月泉天锁", "733", line[0], line[1]-line[0], 1, "")

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
                                   int(line[7] / self.battleTime * 1000),
                                   int(line[8] / self.battleTime * 1000),
                                   int(line[9] / self.battleTime * 1000),
                                   line[10]
                                   ])
        bossResult.sort(key = lambda x:-x[2])
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
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps: #非化解
                    self.hps[event.caster] += event.healEff

                healRes = self.criticalHealCounter[event.target].recordHeal(event)
                if healRes != {}:
                    for line in healRes:
                        if line in self.bld.info.player:
                            self.stat[line][10] += healRes[line]

                if event.id in ["28292"]:  # 曲云蝶鸾
                    self.potList.append([self.bld.info.player[event.target].name,
                                         self.occDetailList[event.target],
                                         1,
                                         self.bossNamePrint,
                                         "%s曲云蝶鸾" % (parseTime((event.time - self.startTime) / 1000)),
                                         []])

                if event.id in ["28284"]:  # 内力炸裂
                    self.xjdnl[-1][1] = event.time

                # if event.damageEff > 0:
                #     print("[Damage]", event.time, event.id, event.damageEff)

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.npc[event.target].name == "月泉淮":
                            self.stat[event.caster][7] += event.damageEff
                        elif self.bld.info.npc[event.target].name == "蓄积的内力":
                            self.stat[event.caster][8] += event.damageEff
                        elif self.bld.info.npc[event.target].name == "天锁":
                            self.stat[event.caster][9] += event.damageEff
                
        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "20650":  # 月泉天锁
                if event.stack == 1:
                    self.criticalHealCounter[event.target].active()
                    self.criticalHealCounter[event.target].setCriticalTime(-1)
                elif event.stack == 0: #buff消失
                    self.criticalHealCounter[event.target].unactive()
                    self.yqts[-1][1] = event.time

            if event.id in ["20544"] and event.stack == 1:  # 中焦土
                if event.time - self.lastJiaotu[event.target] > 2000:
                    self.potList.append([self.bld.info.player[event.target].name,
                                         self.occDetailList[event.target],
                                         0,
                                         self.bossNamePrint,
                                         "%s中赤炎焦土" % (parseTime((event.time - self.startTime) / 1000)),
                                         []])
                self.lastJiaotu[event.target] = event.time

        elif event.dataType == "Shout":
            if event.content in ['"就到这里吧……我玩够了。"']:
                self.win = 1

            if event.content in ['"让老夫品尝品尝你们的内力吧……"']:
                self.phase = 2
                self.yqjqTime = event.time
                self.bh.setEnvironment("28289", "九十九月泉汲取", "2036", event.time, 25000, 1, "")

            if event.content in ['"够了够了！余兴节目到此结束。"']:
                self.phase = 3
                self.bh.setEnvironment("28566", "千八百万凰炎冲", "4531", event.time, 16000, 1, "")

            if event.content in ['"丢下兵刃乖乖等死吧。"']:
                self.xjdnl.append([event.time, 0])

            if event.content in ['"哈哈……站那儿别动。"']:
                self.yqts.append([event.time, 0])

        elif event.dataType == "Death":  # 重伤记录
            pass

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
        self.activeBoss = "月泉淮"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        #7 幻象DPS, 8 内力球DPS, 9 天锁DPS, 10 关键治疗量
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.xjdnl = [[0, 0]]
        self.yqts = [[0, 0]]

        self.phase = 0
        self.yqjqTime = 0
        self.buffCounter = {}
        self.criticalHealCounter = {}
        self.lastJiaotu = {}

        self.yqhInterrupt = 0
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0]
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            self.criticalHealCounter[line] = CriticalHealCounter()
            self.lastJiaotu[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


# Created by moeheart at 03/29/2021
# 宫傲的定制复盘方法库。
# 宫傲是白帝江关7号首领，复盘主要集中在以下几个方面：
# 各阶段伤害，水球承伤

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class GongAoWindow(SpecificBossWindow):
    '''
    宫傲的专有复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('宫傲详细复盘')
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
        tb.AppendHeader("水球DPS", "对源流之心的DPS，分母以场上全部水球计算。")
        tb.AppendHeader("常规DPS", "均衡水体与不带易伤的盈满水体期间的DPS，系数为100%%。\n阶段持续时间：%s"%parseTime(self.detail["P1Time"]))
        tb.AppendHeader("脱水DPS", "脱水水体期间的DPS，系数为50%%。\n阶段持续时间：%s"%parseTime(self.detail["P2Time"]))
        tb.AppendHeader("水下DPS", "尚水迷界期间的DPS，系数为1000%%。\n阶段持续时间：%s"%parseTime(self.detail["P4Time"]))
        tb.AppendHeader("浴血DPS", "浴血水体期间的DPS，系数为350%%。\n阶段持续时间：%s"%parseTime(self.detail["P5Time"]))
        tb.AppendHeader("关键治疗量", "对邪水之握玩家的治疗量。")
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
            tb.AppendContext(int(self.effectiveDPSList[i][10]))
            tb.AppendContext(int(self.effectiveDPSList[i][11]))
            color12 = "#000000"
            if self.effectiveDPSList[i][12] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color12 = "#00ff00"
            tb.AppendContext(int(self.effectiveDPSList[i][12]), color=color12)
            
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

class GongAoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        self.EndOfPhase(self.finalTime)

        for line in self.ymzs:
            self.bh.setEnvironment("26338", "月明之时", "10783", line[0], line[1]-line[0], 1, "")
        for line in self.gl:
            if line[2] != 5:
                self.bh.setEnvironment("26318", "甘霖", "10442", line[0], line[1]-line[0], 1, "")
            else:
                self.bh.setEnvironment("26318", "甘霖·血雨", "10442", line[0], line[1]-line[0], 1, "")


    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()
        
        if self.shuiqiuStartTime != 0:
            self.shuiqiuSumTime += self.finalTime - self.shuiqiuStartTime

        self.detail["P1Time"] = int((self.phaseTime[1] + self.phaseTime[3]) / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)
        self.detail["P4Time"] = int(self.phaseTime[4] / 1000)
        self.detail["P5Time"] = int(self.phaseTime[5] / 1000)

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
                                   int(line[7] / self.shuiqiuSumTime * 1000),
                                   int(line[8] / self.detail["P1Time"]),
                                   int(line[9] / self.detail["P2Time"]),
                                   int(line[10] / self.detail["P4Time"]),
                                   int(line[11] / self.detail["P5Time"]),
                                   line[12]
                                   ])
        bossResult.sort(key = lambda x:-x[2])
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

    def EndOfPhase(self, time):
        '''
        阶段结束，处理时间统计.
        params:
        - time: 当前阶段结束的时间
        '''
        self.phaseTime[self.phase] += time - self.phaseStart
        self.phaseStart = time

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - event 复盘数据，意义同茗伊复盘。
        '''
        
        if self.luanliuTime != 0 and event.time - self.luanliuTime >= 500:
            # 结算水球
            if abs(self.luanliuTime - self.huiShuiTime) < 500 and (self.bld.info.map != "25人英雄白帝江关" or len(self.luanliuID) >= 3):
                if len(self.luanliuID) >= 2:
                    victims = ["受害者名单："]
                    for line in self.luanliuID:
                        victims.append(self.bld.info.player[line].name)
                    potTime = parseTime((event.time - self.startTime) / 1000)
                    self.potList.append([self.bld.info.player[self.huiShuiID].name,
                                         self.occDetailList[self.huiShuiID],
                                         1,
                                         self.bossNamePrint,
                                         "%s水球害人：%d个" % (potTime, len(self.luanliuID)),
                                         victims])
                else:
                    potTime = parseTime((event.time - self.startTime) / 1000)
                    potID = self.luanliuID[0] 
                    self.potList.append([self.bld.info.player[potID].name,
                                         self.occDetailList[potID],
                                         0,
                                         self.bossNamePrint,
                                         "%s被水球击中，来源：%s" % (potTime, self.bld.info.player[self.huiShuiID].name),
                                         ["水球只命中一个人时，由被命中者背锅。"]])
            self.luanliuTime = 0
            self.luanliuID = []
            self.huiShuiTime = 0
            self.huiShuiID = "0"
            
        if self.shuiqiuBurstTime != 0 and event.time - self.shuiqiuBurstTime >= 500:
            #结算源流之心爆炸
            for shuiqiuID in self.shuiqiuDps:
                if event.time - self.shuiqiuDps[shuiqiuID]["time"] <= 20000:
                    #合法伤害量
                    damageStd = 1900000
                    if self.bld.info.map == "25人英雄白帝江关":
                        damageStd = 4132500
                    elif self.bld.info.map == "10人普通白帝江关":
                        damageStd = 307500
                    if self.shuiqiuDps[shuiqiuID]["sum"] != damageStd:
                        #开始分锅
                        damageSet = []
                        potSet = []
                        lastPlayer = "0"
                        lastPlayerPercent = 1
                        for player in self.shuiqiuDps[shuiqiuID]:
                            if player in ["sum", "time"]:
                                continue
                            percent = self.shuiqiuDps[shuiqiuID][player] / damageStd
                            damageSet.append([percent, self.bld.info.player[player].name, parseCent(percent)])
                            if percent > 0.05:
                                if percent < 0.15:
                                    potSet.append([player, parseCent(percent)])
                                else:
                                    if percent < lastPlayerPercent:
                                        lastPlayer = player
                                        lastPlayerPercent = percent
                        if potSet == [] and lastPlayer != "0":
                            potSet.append([lastPlayer, parseCent(lastPlayerPercent)])
                        damageSet.sort(key = lambda x:-x[0])
                            
                        potDes = ["对应水球转火记录："]
                        for line in damageSet:
                            potDes.append("%s: %s%%"%(line[1], line[2]))
                        for line in potSet:
                            potTime = parseTime((event.time - self.startTime) / 1000)
                            potID = line[0]
                            self.potList.append([self.bld.info.player[potID].name,
                                                 self.occDetailList[potID],
                                                 1,
                                                 self.bossNamePrint,
                                                 "%s水球承伤不足并爆炸：%s%%" % (potTime, line[1]),
                                                 potDes])

            self.shuiqiuBurstTime = 0
                        
        
        if event.dataType == "Skill":

            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                healRes = self.criticalHealCounter[event.target].recordHeal(event)
                if healRes != {}:
                    for line in healRes:
                        if line in self.bld.info.player:
                            self.stat[line][12] += healRes[line]
                        
                if event.id == "26596":
                    self.shuiqiuBurstTime = event.time
                    
                if event.id == "26526":
                    potID = event.target
                    potTime = parseTime((event.time - self.startTime) / 1000)
                    self.potList.append([self.bld.info.player[potID].name,
                                         self.occDetailList[potID],
                                         1,
                                         self.bossNamePrint,
                                         "%s额外邪水之握" % (potTime),
                                         ["由于在邪水之握时没有出蓝圈/红圈，被额外选为邪水之握的目标。"]])

                if event.id == "26338":  # 月明之时
                    if event.time - self.ymzs[-1][1] > 2000:
                        self.ymzs.append([event.time - 20000, event.time])

                if event.id in ["26319", "26570", "26653", "26940"]:  # 甘霖
                    if event.time - self.gl[-1][1] > 5000:
                        self.gl.append([event.time - 1000, event.time, self.phase])
                    elif event.time - self.gl[-1][1] > 100:
                        self.gl[-1][1] = event.time
                    
            else:
            
                if event.caster in self.bld.info.player:
                    self.stat[event.caster][2] += event.damageEff
                    
                    if event.target in self.shuiqiuDps:
                        if event.caster not in self.shuiqiuDps[event.target]:
                            self.shuiqiuDps[event.target][event.caster] = 0
                        self.shuiqiuDps[event.target][event.caster] += event.damageEff
                        self.shuiqiuDps[event.target]['sum'] += event.damageEff
                        self.stat[event.caster][7] += event.damageEff

                    if self.phase in [1, 3]:
                        self.stat[event.caster][8] += event.damageEff
                    elif self.phase in [2]:
                        self.stat[event.caster][9] += event.damageEff
                    elif self.phase in [4]:
                        self.stat[event.caster][10] += event.damageEff
                    elif self.phase in [5]:
                        self.stat[event.caster][11] += event.damageEff
                
        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return
            if event.id in ["19130"]:
                if event.stack == 0:
                    self.huiShuiTime = event.time
                    self.huiShuiID = event.target
                
            if event.id in ["18892"]:
                self.luanliuTime = event.time
                self.luanliuID.append(event.target)
                
            if event.id in ["19083"] and event.stack == 1:  # 污浊之水
                self.wushuiLast[event.target] = event.time
                
            if event.id in ["8510"]:  # 好团长点赞
                self.win = 1

            if event.id == "19053":  # 邪水之握
                if event.stack == 1:
                    self.criticalHealCounter[event.target].active()
                    self.criticalHealCounter[event.target].setCriticalTime(-1)

                elif event.stack == 0:  # buff消失
                    self.criticalHealCounter[event.target].unactive()
                    
        elif event.dataType == "Shout":
            if event.content in ['"水！我要水！！！"']:
                self.EndOfPhase(event.time)
                self.phase = 2
                self.bh.setEnvironment("26690", "脱水水体", "14835", event.time - 5000, 5000, 1, "")
            if event.content in ['"哈哈哈哈~"'] and event.time - self.phaseStart > 20000:
                self.EndOfPhase(event.time)
                self.phase = 3
                self.bh.setEnvironment("26691", "盈满水体", "14834", event.time - 5000, 5000, 1, "")
            if event.content in ['"沉溺吧！挣扎吧！消失吧~哈哈哈哈哈~"']:
                self.EndOfPhase(event.time)
                self.phase = 4
                self.bh.setEnvironment("26682", "尚水迷界", "3400", event.time, 5000, 1, "")  # ID随便写的
            if event.content in ['"呃啊......."']:
                self.EndOfPhase(event.time)
                self.phase = 1
                self.bh.setEnvironment("26681", "均衡水体", "14832", event.time - 5000, 5000, 1, "")
            if event.content in ['"大....大侠饶命，我这就奉上尚水宝典！"']:
                self.EndOfPhase(event.time)
                self.phase = 0
            if event.content in ['"啊！！！这味道比水更鲜美~~哈哈哈！鲜血，在体内翻涌!"']:
                self.EndOfPhase(event.time)
                self.phase = 5
                self.bh.setEnvironment("26692", "浴血水体", "14833", event.time - 5000, 5000, 1, "")  # ID随便写的
            if event.content in ['"嘿嘿嘿嘿......"', '"尚水神功可远远不止如此~"']:
                if self.phase != 5:
                    self.bh.setEnvironment("26527", "邪水之握", "8317", event.time, 9000, 1, "")
                else:
                    self.bh.setEnvironment("26527", "邪水之握·血", "8317", event.time, 9000, 1, "")
                
        elif event.dataType == "Death":  # 重伤记录
            pass
            
        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["宫傲宝箱", "叶鸦", "公孙二娘"]:
                self.win = 1
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "源流之心":
                if event.enter:
                    self.shuiqiuDps[event.id] = {'sum': 0, 'time': event.time}
                    if self.shuiqiuNum == 0:
                        self.shuiqiuStartTime = event.time
                    self.shuiqiuNum += 1
                else:
                    self.shuiqiuNum -= 1
                    if self.shuiqiuNum == 0:
                        self.shuiqiuSumTime += event.time - self.shuiqiuStartTime
                        self.shuiqiuStartTime = 0
            
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
        self.activeBoss = "宫傲"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #宫傲数据格式：
        #7 水球DPS, 8 常规DPS, 9 脱水DPS, 10 水下DPS, 11 浴血DPS, 12 水肿治疗量
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "宫傲"
        self.win = 0
        self.phase = 1  # 1 均衡 2 脱水 3 盈满 4 水下 5 浴血
        self.phaseStart = self.startTime
        self.phaseTime = [0, 0, 0, 0, 0, 0]
        
        self.huiShuiTime = 0
        self.huiShuiID = "0"
        self.luanliuTime = 0
        self.luanliuID = []
        self.wushuiLast = {}
        self.shuiqiuDps = {}
        self.shuiqiuNum = 0
        self.shuiqiuBurstTime = 0
        self.shuiqiuStartTime = 0
        self.shuiqiuSumTime = 1e-10
        self.criticalHealCounter = {}

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.ymzs = [[0, 0]]
        self.gl = [[0, 0, 0]]
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0, 0, 0]
            self.wushuiLast[line] = 0
            self.criticalHealCounter[line] = CriticalHealCounter()

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)

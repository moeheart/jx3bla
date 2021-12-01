# Created by moeheart at 10/17/2021
# 雷域大泽3号-悉达罗摩的复盘库。

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *
from Constants import *

import tkinter as tk
        
class XidaLuomoWindow(SpecificBossWindow):
    '''
    悉达罗摩复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        #window = tk.Tk()
        window.title('悉达罗摩复盘')
        window.geometry('1200x1000')
        
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
        tb.AppendHeader("本体DPS", "对悉达罗摩的DPS。")
        tb.AppendHeader("灵虫DPS", "对灵虫的DPS。时间仍然按照整场战斗计算。")
        tb.AppendHeader("主动踩花", "在花出现1秒之后踩花的次数，代表主动踩花。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            name = self.getMaskName(self.getMaskName(self.effectiveDPSList[i][0]))
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

            tb.AppendContext(int(self.effectiveDPSList[i][7]))
            tb.AppendContext(int(self.effectiveDPSList[i][8]))
            tb.AppendContext(int(self.effectiveDPSList[i][9]))

            # 心法复盘
            if self.effectiveDPSList[i][0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[self.effectiveDPSList[i][0]], self.effectiveDPSList[i][0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("灵虫打断复盘", "打断复盘测试中，结果仅供参考。\n标记需要使用南宫伯/浅歌的DBM，如果不是的话标记可能不对应。\n每个区域分别代表：打断者ID，打断时间，打断时灵虫读条百分比，打断技能。")
        tb.EndOfLine()

        j = 0
        for wave in self.detail["lingchong"]:
            first = 1
            j += 1
            for i in range(len(wave)):
                record = wave[i]
                if first == 1:
                    tb.AppendContext("第%d组" % j)
                    first = 2
                elif first == 2:
                    tb.AppendContext(record["time"])
                    first = 0
                else:
                    tb.AppendContext("")
                label = ["白云", "小剑", "斧头", "钩子"][i]
                tb.AppendContext(label)
                num = 0
                for line in record["log"]:
                    name = line[0]
                    color = getColor(line[1])
                    tb.AppendContext(name, color=color)
                    color3 = "#000000"
                    p = int(line[3][:-1])
                    if p < 40:
                        color3 = "#ff0000"
                    tb.AppendContext(line[2], color=color3)
                    tb.AppendContext(line[3], color=color3)
                    tb.AppendContext(line[4], color=color3)
                    tb.AppendContext("|")
                    num += 1
                if num < 3:
                    for k in range(3-num):
                        tb.AppendContext("")
                        tb.AppendContext("")
                        tb.AppendContext("")
                        tb.AppendContext("")
                        tb.AppendContext("|")
                if record["success"] == 0:
                    tb.AppendContext("消灭")
                else:
                    tb.AppendContext("回血", color="#ff0000")
                tb.AppendContext(record["vanish"])
                tb.EndOfLine()

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

    def __init__(self, config, effectiveDPSList, detail, occResult):
        super().__init__(config, effectiveDPSList, detail, occResult)

class XidaLuomoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        for line in self.sgzh:
            self.bh.setEnvironment("28804", "蚀骨之花", "3124", line[0], line[1]-line[0], 1, "")
        for line in self.edbf:
            self.bh.setEnvironment("27858", "厄毒爆发", "2129", line[0], line[1]-line[0], 1, "")
        for line in self.lczj:
            self.bh.setEnvironment("28247", "灵虫召集", "4718", line[0], line[1]-line[0], 1, "")
        for line in self.ymdw:
            self.bh.setEnvironment("28098", "幽冥毒雾", "341", line[0], line[1]-line[0], 1, "")

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
                                   line[9],
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
                # if event.damageEff > 0:
                #     print(event.time, event.damageEff, event.full_id, self.bld.info.getSkillName(event.full_id), self.bld.info.player[event.target].name)

                if event.id == "27858":  # 厄毒爆发
                    if event.time - self.edbf[-1][1] > 2000:
                        self.edbf.append([event.time - 5000, event.time])

                if event.id in ["27859", "29715"]:  # 幽冥毒雾
                    if event.time - self.ymdw[-1][1] > 5000:
                        self.ymdw.append([event.time - 1000, event.time])
                    elif event.time - self.ymdw[-1][1] > 100:
                        self.ymdw[-1][1] = event.time

                if event.id == "27985":  # 种子破裂
                    # 记录主动踩种子
                    if event.time > self.sgzh[-1][0] + 1000 and event.time < self.sgzh[-1][1]:
                        self.stat[event.target][9] += 1
                    
            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == "悉达罗摩":
                        self.stat[event.caster][7] += event.damageEff
                    if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == "灵虫":
                        self.stat[event.caster][8] += event.damageEff

                if event.target in self.lingchongIdDict and event.id in INTERRUPT_DICT:
                    id = self.lingchongIdDict[event.target]
                    num = self.lingchongCastNum[id]
                    nowNum = max(0, num-1)
                    prevNum = max(0, num-2)
                    # print("[Inter]", event.time, self.bld.info.player[event.caster].name, INTERRUPT_DICT[event.id], event.target, event.damageEff)
                    # print(self.lingchongCasting[id], self.lingchongCastStart[id], num)
                    # 过滤过短时间的连续打断技能
                    repeatFlag = False
                    if event.id == self.prevSkillTime[event.caster][0] and event.target == self.prevSkillTime[event.caster][2] and \
                        event.time - self.prevSkillTime[event.caster][1] < 50:
                            repeatFlag = True

                    if self.lingchongCasting[id] == 1 and not repeatFlag:
                        t = (event.time - self.lingchongCastStart[id][prevNum]) / 3500
                        if t <= 1 and num >= 2 and num <= 4:
                            castPercent = parseCent(t, 0) + '%'
                            self.detail["lingchong"][-1][id]["log"].append([self.bld.info.player[event.caster].name,
                                                                            self.occDetailList[event.caster],
                                                                            parseTime((event.time - self.startTime) / 1000),
                                                                            castPercent,
                                                                            INTERRUPT_DICT[event.id]])
                            self.prevSkillTime[event.caster] = [event.id, event.time, event.target]
                            self.lingchongCastStart[id][prevNum] = 0
                        elif num <= 3:
                            t = (event.time - self.lingchongCastStart[id][nowNum]) / 3500
                            if t <= 1:
                                castPercent = parseCent(t, 0) + '%'
                                self.detail["lingchong"][-1][id]["log"].append([self.bld.info.player[event.caster].name,
                                                                                self.occDetailList[event.caster],
                                                                                parseTime((event.time - self.startTime) / 1000),
                                                                                castPercent,
                                                                                INTERRUPT_DICT[event.id]])
                                self.prevSkillTime[event.caster] = [event.id, event.time, event.target]
                                self.lingchongCastStart[id][nowNum] = 0
                                self.lingchongCasting[id] = 0
                
        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

        elif event.dataType == "Shout":
            if event.content in ['"来吧，进餐时间到了！"']:
                self.win = 1

        elif event.dataType == "Death":  # 重伤记录
            pass
            
        elif event.dataType == "Battle": # 战斗状态变化
            pass

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["悉达罗摩宝箱"]:
                self.win = 1
            # if event.id in self.bld.info.npc:
            #     print(event.time, self.bld.info.npc[event.id].name)
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].templateID in ["106108", "107022", "107185", "107065", "106141"] and event.enter:
                # 种子出现事件
                if event.time - self.sgzh[-1][0] > 10000:
                    self.sgzh.append([event.time, event.time + 10000])  # 10秒蚀骨之花

            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "灵虫" and event.enter:
                # print("[Lingchong]", self.bld.info.npc[event.id].templateID, event.time)
                pass

            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].templateID in ["107202", "107111", "107115", "107065", "106141"] and event.enter:
                # 灵虫出现事件
                # print("[Lingchong]", event.time, event.id, self.bld.info.npc[event.id].templateID)

                # 判断是否是新的一波
                if event.time - self.lczj[-1][1] > 10000:
                    self.lczj.append([event.time - 5000, event.time])
                    lingchongSum = 4
                    if self.bld.info.map in ["10人普通雷域大泽", "雷域大泽"]:
                        lingchongSum = 3
                    self.detail["lingchong"].append([])
                    for j in range(lingchongSum):
                        self.detail["lingchong"][-1].append({})
                    self.lingchongNum = 0
                    self.lingchongID = [""] * lingchongSum
                    self.lingchongIdDict = {}
                    self.lingchongCasting = [0] * lingchongSum
                    self.lingchongCastNum = [0] * lingchongSum
                    self.lingchongCastStart = []
                    for j in range(lingchongSum):
                        self.lingchongCastStart.append([0, 0, 0, 0])

                # 记录灵虫ID
                if self.bld.info.map != "25人英雄雷域大泽":
                    self.detail["lingchong"][-1][self.lingchongNum] = {"time": parseTime((event.time - self.startTime) / 1000), "log": [], "success": 0, "vanish": ""}
                    self.lingchongID[self.lingchongNum] = event.id
                    self.lingchongIdDict[event.id] = self.lingchongNum
                    self.lingchongNum += 1
                else:
                    lingchongType = {"107202": 0, "107115": 1, "107111": 2}[self.bld.info.npc[event.id].templateID]
                    if self.detail["lingchong"][-1][lingchongType] == {}:
                        self.detail["lingchong"][-1][lingchongType] = {"time": parseTime((event.time - self.startTime) / 1000), "log": [], "success": 0, "vanish": ""}
                        self.lingchongID[lingchongType] = event.id
                        self.lingchongIdDict[event.id] = lingchongType
                    else:
                        self.detail["lingchong"][-1][3] = {"time": parseTime((event.time - self.startTime) / 1000), "log": [], "success": 0, "vanish": ""}
                        self.lingchongID[3] = event.id
                        self.lingchongIdDict[event.id] = 3
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].templateID in ["107202", "107111", "107115", "107065", "106141"] and not event.enter:
                # 灵虫消失事件
                if event.id in self.lingchongIdDict:
                    id = self.lingchongIdDict[event.id]
                    num = self.lingchongCastNum[id]
                    nowNum = max(0, num-1)
                    if self.lingchongCasting[id] == 1 and event.time - self.lingchongCastStart[id][nowNum] > 3500:
                        self.detail["lingchong"][-1][id]["success"] = 1
                    self.detail["lingchong"][-1][id]["vanish"] = parseTime((event.time - self.startTime) / 1000)

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.lingchongIdDict and event.id == "28049":  # 生命反哺
                # 找到施放者并标记
                id = self.lingchongIdDict[event.caster]
                num = self.lingchongCastNum[id]
                # print(self.lingchongCastStart, num)
                self.lingchongCasting[id] = 1
                self.lingchongCastStart[id][num] = event.time
                if self.lingchongCastNum[id] <= 2:
                    self.lingchongCastNum[id] += 1
                    
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
        self.activeBoss = "悉达罗摩"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 悉达罗摩数据格式：
        # 7 本体DPS, 8 灵虫DPS, 9 主动踩花

        # 打断复盘
        # 第X=[1,2,...]组-第Y=[1,2,3,4]只-第Z=[1,2,3]次打断: [玩家名，心法，时间，读条进度，技能]
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0

        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.sgzh = [[0, 0]]  # 蚀骨之花
        self.edbf = [[0, 0]]  # 厄毒爆发
        self.lczj = [[0, 0]]  # 灵虫召集
        self.ymdw = [[0, 0]]  # 幽冥毒雾

        # 灵虫打断复盘
        self.detail["lingchong"] = []
        self.lingchongNum = 0
        self.lingchongID = [""]
        self.lingchongIdDict = {}
        self.lingchongCasting = [0]
        self.lingchongCastNum = [0]
        self.lingchongCastStart = [[0, 0, 0, 0]]
        self.prevSkillTime = {}
        
        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0]
            self.prevSkillTime[line] = ["", 0, ""]


    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


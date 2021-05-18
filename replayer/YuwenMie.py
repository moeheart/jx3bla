# Created by moeheart at 03/29/2021
# 宇文灭的定制复盘方法库。
# 宇文灭是白帝江关5号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class YuwenMieWindow():
    '''
    宇文灭的专有复盘窗口类。
    ''' 
    
    def final(self):
        '''
        关闭窗口。
        '''
        self.windowAlive = False
        self.window.destroy()

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        #window = tk.Tk()
        window.title('宇文灭详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #宇文灭数据格式：
        #7 P1DPS 8 玄冰1 9 玄冰2 10 群攻玄冰 11 P2DPS 12 关键治疗量
        
        tb = TableConstructor(frame1)
        
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
            
            tb.EndOfLine()
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def alive(self):
        return self.windowAlive

    def __init__(self, effectiveDPSList, detail):
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail

class YuwenMieReplayer(SpecificReplayer):

    def countFinal(self, nowTime):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        pass

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        
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
        for id in self.playerIDList:
            if id in self.stat:
                line = self.stat[id]
                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = self.equipmentDict[id]["sketch"]
                
                if getOccType(self.occDetailList[id]) == "healer":
                    line[3] = int(self.hps[id] / self.battleTime)

                dps = int(line[2] / self.battleTime)
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
        
        #for line in self.shuiqiuDps:
        #    print(self.shuiqiuDps[line])
            
        return self.effectiveDPSList, self.potList, self.detail
        
    def recordDeath(self, item, deathSource):
        '''
        在有玩家重伤时记录狂热值的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        - deathSource 重伤来源。
        '''
        pass

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        
        if self.chuanRanQueue != [] and int(item[2]) - self.chuanRanQueue[0][0] >= 1000:
            chuanRanTime = self.chuanRanQueue[0][0]
            chuanRanType = self.chuanRanQueue[0][1]
            source = self.chuanRanQueue[0][2]
            target = self.chuanRanQueue[0][3]
            if chuanRanType == 1:
                if self.hanJieCounter[target].checkState(chuanRanTime-500) == 0 and self.hanJieCounter[target].checkState(chuanRanTime+1000) == 1:  # 传染寒劫
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.namedict[target][0].strip('"')
                        self.potList.append([self.namedict[potID][0],
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫传染：%s" % (potTime, victimName),
                                             ["接锅者中寒劫并靠近没有中buff的队友，导致目标也被传染寒劫。"]])
                
                elif self.hanJieCounter[target].checkState(chuanRanTime-500) == 1 and self.hanYuCounter[target].checkState(chuanRanTime+1000) == 1:  # 寒劫变寒狱
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.namedict[target][0].strip('"')
                        self.potList.append([self.namedict[potID][0],
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫升级：%s" % (potTime, victimName),
                                             ["接锅者中寒劫并靠近中寒劫的队友，导致两人的寒劫被升级为寒狱。"]])
                        self.potList.append([victimName,
                                             self.occDetailList[target],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒劫升级：%s" % (potTime, self.namedict[potID][0].strip('"')),
                                             ["接锅者中寒劫并靠近中寒劫的队友，导致两人的寒劫被升级为寒狱。"]])
            elif chuanRanType == 2:
                if self.hanYuCounter[target].checkState(chuanRanTime-500) == 0 and self.hanYuCounter[target].checkState(chuanRanTime+1000) == 1:  # 传染寒狱
                    if self.phase == 1:
                        potTime = parseTime((chuanRanTime - self.startTime) / 1000)
                        potID = source
                        victimName = self.namedict[target][0].strip('"')
                        self.potList.append([self.namedict[potID][0],
                                             self.occDetailList[potID],
                                             0,
                                             self.bossNamePrint,
                                             "%s寒狱传染：%s" % (potTime, victimName),
                                             ["接锅者中寒狱并靠近没有中buff的队友，导致目标也被传染寒狱。"]])
            del self.chuanRanQueue[0]
        
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                        
                if item[7] == "26224":  # 寒劫传染
                    self.chuanRanQueue.append([int(item[2]), 1, item[4], item[5]])
                                         
                if item[7] == "26225":  # 寒狱传染
                    self.chuanRanQueue.append([int(item[2]), 2, item[4], item[5]])
                    
            else:
            
                if item[4] in self.playerIDList:
                    self.stat[item[4]][2] += int(item[14])
                    if self.phase == 1:
                        self.stat[item[4]][7] += int(item[14])
                    elif self.phase == 2:
                        self.stat[item[4]][11] += int(item[14])
                    
                    if item[5] in self.xuanBingDamage:
                        if item[4] not in self.xuanBingDamage[item[5]]:
                            self.xuanBingDamage[item[5]][item[4]] = 0
                        self.xuanBingDamage[item[5]][item[4]] += int(item[14])
     
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if item[6] == "18861":
                self.hanJieCounter[item[5]].setState(int(item[2]), int(item[10]))
                
            if item[6] == "18862":
                self.hanYuCounter[item[5]].setState(int(item[2]), int(item[10]))
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
            if item[4] in ['"今日便拼个你死我活！"']:
                self.phase = 2
                self.phaseEnd[1] = int(item[2])
                self.phaseStart[2] = int(item[2])
                
        elif item[3] == '3': #重伤记录
            if item[6] == '"宇文灭"':
                self.win = 1
                self.phaseEnd[2] = int(item[2])
                
            pass
            
        elif item[3] == '6':  # 进入、离开场景
            if len(item) >= 8 and item[7] == '"九阴玄冰"' and item[4] == '1':
                self.xuanBingDamage[item[6]] = {'sum': 0, 'time': int(item[2])}
                
            if len(item) >= 8 and item[7] == '"九阴玄冰"' and item[4] == '0':
                xuanBingType = 0
                xuanBingTime = self.xuanBingDamage[item[6]]['time'] - self.startTime 
                if xuanBingTime >= 50000 and xuanBingTime <= 75000:
                    xuanBingType = 8
                elif xuanBingTime >= 160000 and xuanBingTime <= 185000:
                    xuanBingType = 9
                elif self.phase == 1:
                    xuanBingType = 10
                if xuanBingType != 0:
                    for line in self.xuanBingDamage[item[6]]:
                        if line != 'sum' and line != 'time':
                            self.stat[line][xuanBingType] += self.xuanBingDamage[item[6]][line]
            
        elif item[3] == "10": #战斗状态变化
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
        
        self.phase = 1
        self.phaseStart = [0, 0, 0]
        self.phaseEnd = [0, 0, 0]
        self.xuanBingDamage = {}
        
        self.hanJieCounter = {}
        self.hanYuCounter = {}
        self.chuanRanQueue = []
        
        for line in self.playerIDList:
            self.stat[line] = [self.namedict[line][0].strip('"'), self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0, 0, 0]
            self.hps[line] = 0
            self.hanJieCounter[line] = BuffCounter(18861, self.startTime, self.finalTime)
            self.hanYuCounter[line] = BuffCounter(18862, self.startTime, self.finalTime)

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


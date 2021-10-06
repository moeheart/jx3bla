# Created by moeheart at 03/29/2021
# 宫傲的定制复盘方法库。
# 宫傲是白帝江关7号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.boss.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *
        
class GongAoWindow():
    '''
    宫傲的专有复盘窗口类。
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
        window.title('宫傲详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructor(frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。")
        tb.AppendHeader("水球DPS", "对源流之心的DPS，分母以场上全部水球计算。")
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

class GongAoReplayer(SpecificReplayer):

    def countFinal(self, nowTime):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        pass
        #self.phase = 0

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        
        if self.shuiqiuStartTime != 0:
            self.shuiqiuSumTime += self.finalTime - self.shuiqiuStartTime

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
                                   int(line[7] / self.shuiqiuSumTime * 1000)
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
        
        if self.luanliuTime != 0 and int(item[2]) - self.luanliuTime >= 500:
            # 结算水球
            if abs(self.luanliuTime - self.huiShuiTime) < 500 and (self.mapDetail != "25人英雄白帝江关" or len(self.luanliuID) >= 3): 
                if len(self.luanliuID) >= 2:
                    victims = ["受害者名单："]
                    for line in self.luanliuID:
                        victims.append(self.namedict[line][0].strip('"'))
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    self.potList.append([self.namedict[self.huiShuiID][0],
                                         self.occDetailList[self.huiShuiID],
                                         1,
                                         self.bossNamePrint,
                                         "%s水球害人：%d个" % (potTime, len(self.luanliuID)),
                                         victims])
                else:
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    potID = self.luanliuID[0] 
                    self.potList.append([self.namedict[potID][0],
                                         self.occDetailList[potID],
                                         0,
                                         self.bossNamePrint,
                                         "%s被水球击中，来源：%s" % (potTime, self.namedict[self.huiShuiID][0].strip('"')),
                                         ["水球只命中一个人时，由被命中者背锅。"]])
            self.luanliuTime = 0
            self.luanliuID = []
            self.huiShuiTime = 0
            self.huiShuiID = "0"
            
        if self.shuiqiuBurstTime != 0 and int(item[2]) - self.shuiqiuBurstTime >= 500:
            #结算源流之心爆炸
            for shuiqiuID in self.shuiqiuDps:
                if int(item[2]) - self.shuiqiuDps[shuiqiuID]["time"] <= 20000:
                    #合法伤害量
                    damageStd = 1900000
                    if self.mapDetail == "25人英雄白帝江关":
                        damageStd = 4132500
                    elif self.mapDetail == "10人普通白帝江关":
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
                            damageSet.append([percent, self.namedict[player][0].strip('"'), parseCent(percent)])
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
                            potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                            potID = line[0]
                            self.potList.append([self.namedict[potID][0],
                                                 self.occDetailList[potID],
                                                 1,
                                                 self.bossNamePrint,
                                                 "%s水球承伤不足并爆炸：%s%%" % (potTime, line[1]),
                                                 potDes])

            self.shuiqiuBurstTime = 0
                        
        
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                        
                if item[7] == "26596":
                    self.shuiqiuBurstTime = int(item[2])
                    
                if item[7] == "26526":
                    potID = item[5]
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    self.potList.append([self.namedict[potID][0],
                                         self.occDetailList[potID],
                                         1,
                                         self.bossNamePrint,
                                         "%s额外邪水之握" % (potTime),
                                         ["由于在邪水之握时没有出蓝圈/红圈，被额外选为邪水之握的目标。"]])
                                         
                #if item[7] == "26527":
                #    print(item)
                    
            else:
            
                if item[4] in self.playerIDList:
                    self.stat[item[4]][2] += int(item[14])
                    
                    if item[5] in self.shuiqiuDps:
                        if item[4] not in self.shuiqiuDps[item[5]]:
                            self.shuiqiuDps[item[5]][item[4]] = 0
                        self.shuiqiuDps[item[5]][item[4]] += int(item[14])
                        self.shuiqiuDps[item[5]]['sum'] += int(item[14])
                        self.stat[item[4]][7] += int(item[14])
     
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if item[6] in ["19130"]:
                if int(item[10]) == 0:
                    self.huiShuiTime = int(item[2])
                    self.huiShuiID = item[5]
                
            if item[6] in ["18892"]:
                self.luanliuTime = int(item[2])
                self.luanliuID.append(item[5])
                
            if item[6] in ["19083"] and int(item[10]) == 1: #污浊之水
                self.wushuiLast[item[5]] = int(item[2])
                
            if item[6] in ["8510"]: #好团长点赞
                self.win = 1
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
        elif item[3] == '3': #重伤记录
                
            pass
            
        elif item[3] == '6': #进入、离开场景
            
            if len(item) >= 8 and item[7] == '"宫傲宝箱"':
                self.win = 1
                
            if len(item) >= 8 and item[7] == '"源流之心"' and item[4] == '1':
                self.shuiqiuDps[item[6]] = {'sum': 0, 'time': int(item[2])}
                if self.shuiqiuNum == 0:
                    self.shuiqiuStartTime = int(item[2])
                self.shuiqiuNum += 1
                
            if len(item) >= 8 and item[7] == '"源流之心"' and item[4] == '0':
                self.shuiqiuNum -= 1
                if self.shuiqiuNum == 0:
                    self.shuiqiuSumTime += int(item[2]) - self.shuiqiuStartTime
                    self.shuiqiuStartTime = 0
            
            pass
            
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
        self.activeBoss = "宫傲"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #宫傲数据格式：
        #7 水球DPS (TODO)待英雄实装后更新
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "宫傲"
        self.win = 0
        
        self.huiShuiTime = 0
        self.huiShuiID = "0"
        self.luanliuTime = 0
        self.luanliuID = []
        self.wushuiLast = {}
        self.shuiqiuDps = {}
        self.shuiqiuNum = 0
        self.shuiqiuBurstTime = 0
        self.shuiqiuStartTime = 0
        self.shuiqiuSumTime = 0
        
        for line in self.playerIDList:
            self.hps[line] = 0
            self.stat[line] = [self.namedict[line][0].strip('"'), self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0]
            self.wushuiLast[line] = 0

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


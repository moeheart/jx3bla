# Created by moeheart at 03/29/2021
# 海荼的定制复盘方法库。
# 海荼是白帝江关3号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class HaiTuWindow():
    '''
    海荼的专有复盘窗口类。
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
        window.title('海荼详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #海荼数据格式：
        #7 P1等效 8 P2单体 9 P2水鬼 10 下水次数 11 P3单体 12 P3水鬼 13 P3关键治疗
        
        #海荼详细数据
        # 0 水枪ID，次数
        # 1 时间，QTE按错/挣脱
        
        tb = TableConstructor(frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。\n海荼复盘中只包含眼中钉点名。")
        tb.AppendHeader("P1等效", "P1的等效DPS，指P1的伤害减去BOSS因汲取而回复的数值。\nP1时长：%s"%parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2单体", "对P2海荼的DPS。\nP2时长：%s"%parseTime(self.detail["P2Time"]))
        tb.AppendHeader("P2水鬼", "对P2水鬼的DPS，已经包括易伤部分。")
        tb.AppendHeader("下水次数", "P2下水的次数。每进入一次QTE界面算一次。")
        tb.AppendHeader("P3单体", "对P3的四把枪与BOSS的DPS。P3的时间从第一次有效伤害开始计算。\nP3时长：%s"%parseTime(self.detail["P3Time"]))
        tb.AppendHeader("P3水鬼", "对P3水鬼的DPS。")
        tb.AppendHeader("P3关键治疗", "对P3手持锁链玩家的治疗。减伤会被等效。")
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
            
            color7 = "#000000"
            if self.effectiveDPSList[i][7] < 0:
                color7 = "#ff0000"
            tb.AppendContext(int(self.effectiveDPSList[i][7]), color = color7)
            
            tb.AppendContext(int(self.effectiveDPSList[i][8]))
            tb.AppendContext(int(self.effectiveDPSList[i][9]))
            
            color10 = "#000000"
            if self.effectiveDPSList[i][10] > 0:
                color10 = "#ff0000"
            tb.AppendContext(int(self.effectiveDPSList[i][10]), color = color10)
            
            tb.AppendContext(int(self.effectiveDPSList[i][11]))
            tb.AppendContext(int(self.effectiveDPSList[i][12]))
            
            color13 = "#000000"
            if self.effectiveDPSList[i][13] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color13 = "#00ff00"
            tb.AppendContext(int(self.effectiveDPSList[i][13]), color = color13)
            
            tb.EndOfLine()
            
        frame2 = tk.Frame(window)
        frame2.pack()
        
        tb = TableConstructor(frame2)
        
        tb.AppendHeader("锁链复盘", "")
        tb.EndOfLine()
        
        for line in self.detail["suolian"]:
            if line["type"] == 0:
                for key in line["log"]:
                    res = line["log"][key]
                    name = res[0]
                    occ = res[1]
                    start = res[2]
                    count = res[3]
                    color = getColor(occ)
                    tb.AppendContext(name, color=color)
                    tb.AppendContext(start)
                    tb.AppendContext("QTE*%d"%count)
            elif line["type"] <= 4:
                if line["type"] == 1:
                    tb.AppendContext("QTE按错")
                elif line["type"] == 2:
                    tb.AppendContext("QTE超时")
                elif line["type"] == 3:
                    tb.AppendContext("锁链错位")
                elif line["type"] == 4:
                    tb.AppendContext("玩家重伤")
                tb.AppendContext(line["time"])
                for reason in line["log"]:
                    name = reason[0]
                    occ = reason[1]
                    color = getColor(occ)
                    tb.AppendContext(name, color=color)
            else:
                if line["type"] == 5:
                    tb.AppendContext("锁链超时")
                if line["type"] == 6:
                    tb.AppendContext("未知原因挣脱")
                tb.AppendContext(line["time"])
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

class HaiTuReplayer(SpecificReplayer):

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
        self.phaseEnd[3] = self.finalTime
        self.phaseTime = [1e+20] * 4
        for i in range(1, 4):
            if self.phaseStart[i] != 0 and self.phaseEnd[i] != 0:
                self.phaseTime[i] = (self.phaseEnd[i] - self.phaseStart[i]) / 1000
                
        self.detail["P1Time"] = self.phaseTime[1]
        self.detail["P2Time"] = self.phaseTime[2]
        self.detail["P3Time"] = self.phaseTime[3]

        bossResult = []
        for id in self.playerIDList:
            if id in self.stat:
                line = self.stat[id]

                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = self.equipmentDict[id]["sketch"]
                
                if getOccType(self.occDetailList[id]) == "healer":
                    line[3] = int(self.hps[id] / self.battleTime)
                    
                line[6] = self.buffCounter[id].sumTime() / 1000

                dps = int(line[2] / self.battleTime)
                bossResult.append([line[0],
                                   line[1],
                                   dps, 
                                   line[3],
                                   line[4],
                                   line[5],
                                   line[6], 
                                   int(line[7] / self.phaseTime[1]),
                                   int(line[8] / self.phaseTime[2]),
                                   int(line[9] / self.phaseTime[2]),
                                   line[10],
                                   int(line[11] / self.phaseTime[3]),
                                   int(line[12] / self.phaseTime[3]),
                                   int(line[13])
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        #print(self.detail["suolian"])
            
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
        
        if self.failTime != 0 and int(item[2]) - self.failTime > 300 and self.mapDetail == "25人英雄白帝江关":  # 缓冲并结算锁链失败的复盘
        
            if self.failFlag == 1:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 1, "time": parseTime((self.failTime - self.startTime)/1000), "log": []}) #按错QTE
                for line in self.failReason:
                    self.detail["suolian"][self.suolianNum]["log"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]])
                    
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    potID = line
                    self.potList.append([self.namedict[potID][0],
                                         self.occDetailList[potID],
                                         1,
                                         self.bossNamePrint,
                                         "%s按错QTE" % (potTime),
                                         ["在锁链阶段按错QTE导致海荼挣脱"]])
                    
                
            elif self.failFlag == 2:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 2, "time": parseTime((self.failTime - self.startTime)/1000), "log": []}) #QTE超时
                for line in self.failReason:
                    self.detail["suolian"][self.suolianNum]["log"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]])
                    
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    potID = line
                    self.potList.append([self.namedict[potID][0],
                                         self.occDetailList[potID],
                                         1,
                                         self.bossNamePrint,
                                         "%sQTE超时" % (potTime),
                                         ["在锁链阶段QTE超时导致海荼挣脱"]])
                    
            elif self.failFlag == 3:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 3, "time": parseTime((self.failTime - self.startTime)/1000), "log": []}) #锁链错位
                for line in self.failReason:
                    self.detail["suolian"][self.suolianNum]["log"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]])
                    
                    potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    potID = line
                    self.potList.append([self.namedict[potID][0],
                                         self.occDetailList[potID],
                                         1,
                                         self.bossNamePrint,
                                         "%s锁链错位" % (potTime),
                                         ["在锁链阶段夹角过小产生错位debuff，导致海荼挣脱"]])

            elif self.failFlag == 4:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 4, "time": parseTime((self.failTime - self.startTime)/1000), "log": []}) #玩家重伤
                for line in self.failReason:
                    self.detail["suolian"][self.suolianNum]["log"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]]) 
                    
            elif self.failFlag == 5:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 5, "time": parseTime((self.failTime - self.startTime)/1000)}) #锁链超时
                    
            else:
                self.suolianNum += 1
                self.detail["suolian"].append({"type": 6, "time": parseTime((self.failTime - self.startTime)/1000)}) #其它原因导致挣脱
            
            self.suolianActive = 0
            self.failFlag = 0
            self.failTime = 0
            self.failReason = []
            
        if self.yanZhongDingTime != 0 and int(item[2]) - self.yanZhongDingTime > 5000:
            if self.yanZhongDingNum >= 5:
                potTime = parseTime((int(item[2]) - self.startTime) / 1000)
                potID = self.yanZhongDingPlayer
                self.potList.append([self.namedict[potID][0],
                                     self.occDetailList[potID],
                                     1,
                                     self.bossNamePrint,
                                     "面向害人：%d个" % (self.yanZhongDingNum),
                                     ["受害者名单："] + self.yanZhongDingVictim])
        
            self.yanZhongDingTime = 0
            self.yanZhongDingNum = 0
            self.yanZhongDingPlayer = "0"
            self.yanZhongDingVictim = []
        
        if item[3] == '1':  # 技能
        
            if item[7] in ["26781", "26782"]: #向左拉/向右拉
                
                correct = 1
                if self.qteStat[item[5]]["time"] != 0:
                    if int(item[7]) - self.qteStat[item[5]]["dir"] != 26780:
                        correct = 0
                        
                if correct:
                    if item[5] in self.detail["suolian"][self.suolianNum]["log"]:
                        self.detail["suolian"][self.suolianNum]["log"][item[5]][3] += 1
                elif self.suolianActive:
                    if self.failFlag > 1:  # 按错QTE由于判定诡异，拥有最高优先级
                        self.failReason = []
                    self.failFlag = 1
                    self.failTime = int(item[2])
                    self.failReason.append(item[5])
                    
                self.qteStat[item[5]]["time"] = 0
                self.qteStat[item[5]]["dir"] = 0
                

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                        
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    for line in healRes:
                        if line in self.playerIDList:
                            self.stat[line][13] += healRes[line]
                        
                if item[7] == "26439" and self.mapDetail == "25人英雄白帝江关":
                    if item[5] in self.stat:
                        self.stat[item[5]][7] -= 3 * int(item[14])
                        
                if item[7] == "26819" and item[8] == "1" and self.suolianActive: #BOSS挣脱反噬
                
                    if self.failFlag == 0:
                        self.failTime = int(item[2])
                    
                    if self.failFlag == 0:
                        for line in self.cuoweiStatus:
                            if (int(item[2]) - self.cuoweiStatus[line]) < 4000:
                                self.failFlag = 3
                                self.failReason.append(line)
                    
                    if self.failFlag == 0:
                        for line in self.qteStat:
                            if self.qteStat[line]["time"] != 0 and int(item[2]) - self.qteStat[line]["time"] > 2500 and int(item[2]) - self.qteStat[line]["time"] < 5500:
                                self.failFlag = 2
                                self.failReason.append(line)
                                
                    if self.failFlag == 0:
                        if int(item[2]) - self.suolianLast > 19000:
                            self.failFlag = 5
                            
                if item[7] == "26234" and '5' not in item[15]:
                    self.yanZhongDingNum += 1
                    self.yanZhongDingVictim.append(self.namedict[item[5]][0].strip('"'))

            else:
            
                if item[4] in self.playerIDList:
                    self.stat[item[4]][2] += int(item[14])
                    
                    if item[5] in self.namedict and self.namedict[item[5]][0] == '"天怒惊霆戟"':
                        if self.phase == 2.5:
                            self.phase = 3
                            self.phaseStart[3] = int(item[2])
                        if self.phase == 3:
                            self.stat[item[4]][11] += int(item[14])
                        elif self.phase == 1:
                            self.stat[item[4]][7] += int(item[14])
                    
                    if item[5] in self.namedict and self.namedict[item[5]][0] == '"海荼"':
                        if self.phase == 2:
                            self.stat[item[4]][8] += int(item[14])
                        elif self.phase == 3:
                            self.stat[item[4]][11] += int(item[14])
                    
                    if item[5] in self.namedict and self.namedict[item[5]][0] == '"水鬼"':
                        if self.phase == 2:
                            self.stat[item[4]][9] += int(item[14])
                        elif self.phase == 3:
                            self.stat[item[4]][12] += int(item[14])
                
            #if item[7] == "26656":
            #    self.phase = 2.5
            #    self.phaseEnd[2] = int(item[2])
     
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if item[6] in ["18901"]:
                layer = int(item[10])
                if layer > 1:
                    layer = 1
                self.buffCounter[item[5]].setState(int(item[2]), layer)
            
            if item[6] == "18946" and int(item[10]) >= 1 and self.phase == 2:
            
                if int(item[2]) - self.xiashuiTime[item[5]] > 15000:
                    self.xiashuiTime[item[5]] = int(item[2])
                    self.stat[item[5]][10] += 1
                    
            if item[6] == "19218" and self.mapDetail == "25人英雄白帝江关":
                if int(item[10]) == 1: #手持锁链buff
                    self.criticalHealCounter[item[5]].active()
                    self.criticalHealCounter[item[5]].setCriticalTime(-1)
                    
                    if self.suolianActive == 0:
                        self.suolianActive = 1
                        self.suolianNum += 1
                        self.detail["suolian"].append({"type": 0, "log": {}})
                    
                    self.detail["suolian"][self.suolianNum]["log"][item[5]] = [self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]], 
                        parseTime((int(item[2]) - self.startTime)/1000), 0]
                    self.suolianLast = int(item[2])

                
                elif int(item[10]) == 0: #buff消失
                    self.criticalHealCounter[item[5]].unactive()
                    
            if item[6] == "19343": #QTE开始标记

                if int(item[10]) == 1:
                    self.qteStat[item[5]]["time"] = int(item[2])
                    self.qteStat[item[5]]["dir"] = int(item[7])
                else:
                    pass
                
            if item[6] == "19426": #错位
                if int(item[10]) == 1:
                    self.cuoweiStatus[item[5]] = int(item[2])
                    
            if item[6] == "18901" and int(item[10]) == 1:  # 眼中钉
                self.yanZhongDingTime = int(item[2])
                self.yanZhongDingPlayer = item[5]
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
            if item[4] in ['"…… ……"', '"吾，海鬼之首海荼，来会会尔等。一起上吧！"']:
                self.phase = 2
                self.phaseEnd[1] = int(item[2])
                self.phaseStart[2] = int(item[2])
                
            if item[4] in ['"吾之大业还未……"', '"吾夙愿方达，绝……绝不能……死……"']:
                self.win = 1
                if len(self.detail["suolian"]) > 0 and self.detail["suolian"][-1]["type"] != 0:
                    del self.detail["suolian"][-1]
                    self.suolianNum -= 1
                
            if item[4] in ['"哼哼哈哈哈，进了水里便是吾等的天下！"']:
                self.phase = 2.5
                self.phaseEnd[2] = int(item[2])
                
            if item[4] in ['"哼……用这种玩意儿，就想擒住我？"']:
                pass
                
        elif item[3] == '3': #重伤记录
                
            if item[4] in self.occdict and int(self.occdict[item[4]][0]) != 0 and len(self.detail["suolian"]) > 0 and self.failFlag == 0:
            
                if "log" in self.detail["suolian"][self.suolianNum] and item[4] in self.detail["suolian"][self.suolianNum]["log"]:
                    self.failFlag = 4
                    self.failTime = int(item[2])
                    self.failReason.append(item[4])
            
                    
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
        self.activeBoss = "海荼"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #海荼数据格式：
        #7 P1等效 8 P2单体 9 P2水鬼 10 下水次数 11 P3单体 12 P3水鬼 13 P3关键治疗
        
        #海荼详细数据
        # 0 水枪ID，次数
        # 1 时间，QTE按错/挣脱
                
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "海荼"
        self.win = 0
        self.phase = 1
        self.buffCounter = {}
        self.criticalHealCounter = {}
        
        self.phaseStart = [0, 0, 0, 0]
        self.phaseEnd = [0, 0, 0, 0]
        
        self.xiashuiTime = {}
        
        self.qteStat = {}
        self.detail["suolian"] = []
        self.suolianActive = 0
        self.suolianNum = -1
        self.failFlag = 0
        self.failTime = 0
        self.failReason = []
        self.cuoweiStatus = {}
        self.suolianLast = 0  # 最后一次锁链时间
        
        self.yanZhongDingTime = 0
        self.yanZhongDingPlayer = "0"
        self.yanZhongDingNum = 0
        self.yanZhongDingVictim = []
        
        for line in self.playerIDList:
            self.stat[line] = [self.namedict[line][0].strip('"'), self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0, 0, 0, 0]
            self.hps[line] = 0
            self.xiashuiTime[line] = 0
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            self.criticalHealCounter[line] = CriticalHealCounter()
            self.qteStat[line] = {"time": 0, "dir": 0}
            self.cuoweiStatus[line] = 0

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


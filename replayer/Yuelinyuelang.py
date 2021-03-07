# Created by moeheart at 03/07/2021
# 岳琳&岳琅的定制复盘方法库。
# 岳琳&岳琅是达摩洞6号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class YuelinyuelangWindow():
    '''
    岳琳&岳琅的专有复盘窗口类。
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
        window.title('岳琳&岳琅详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #数据格式：
        #4 被控时间 5 常规BOSS 6 蟊贼DPS 7 传功DPS 8 莽夫DPS 9 传功顺序 10 P4DPS 11 P4停手1 12 P4停手2 13 P4停手3 14 P4爆发 15 P2关键治疗量 16 P4关键治疗量
        label01 = tk.Label(frame1, text="玩家名", width = 13, height=1)
        label01.grid(row=0, column=0)
        label02 = tk.Label(frame1, text="有效DPS", height=1)
        label02.grid(row=0, column=1)
        ToolTip(label02, "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。\n在岳琳&岳琅，会同时排除曳影剑·爆杀的伤害。")
        label03 = tk.Label(frame1, text="团队-心法DPS", height=1)
        label03.grid(row=0, column=2)
        ToolTip(label03, "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        label04 = tk.Label(frame1, text="被控", height=1)
        label04.grid(row=0, column=3)
        ToolTip(label04, "受到影响无法正常输出的时间，以秒计，包括强力磁石点名、传功。")
        label05 = tk.Label(frame1, text="常规BOSS", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "在P1与P2（开始战斗到传功之前）对BOSS的DPS。")
        label06 = tk.Label(frame1, text="蟊贼DPS", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "在P2（岳琅出现后到传功之前）对蜂群蟊贼的DPS。")
        label07 = tk.Label(frame1, text="传功DPS", height=1)
        label07.grid(row=0, column=6)
        ToolTip(label07, "在传功阶段，对凶贼、胖墩、莽夫的DPS。")
        label08 = tk.Label(frame1, text="莽夫DPS", height=1)
        label08.grid(row=0, column=7)
        ToolTip(label08, "在传功阶段，对莽夫的DPS。\n注意这一项也被包含在“传功DPS”中。")
        label09 = tk.Label(frame1, text="传功顺序", height=1)
        label09.grid(row=0, column=8)
        ToolTip(label09, "在传功阶段进行传功的次序。如果未传功则即为0。")
        label10 = tk.Label(frame1, text="P4DPS", height=1)
        label10.grid(row=0, column=9)
        ToolTip(label10, "在P4（曳影剑激活后）的整体DPS。")
        label11 = tk.Label(frame1, text="P4停手1", height=1)
        label11.grid(row=0, column=10)
        ToolTip(label11, "在43%-31%之间，如果发生停手，则表示在停手期间的DPS。\n停手的时间点会自动推断，如果采用的打法不停手或停手时间点不一致，则本项失去意义，仅供参考。")
        label12 = tk.Label(frame1, text="P4停手2", height=1)
        label12.grid(row=0, column=11)
        ToolTip(label12, "在31%-22%之间，如果发生停手，则表示在停手期间的DPS。\n停手的时间点会自动推断，如果采用的打法不停手或停手时间点不一致，则本项失去意义，仅供参考。")
        label13 = tk.Label(frame1, text="P4停手3", height=1)
        label13.grid(row=0, column=12)
        ToolTip(label13, "在22%-10%之间，如果发生停手，则表示在停手期间的DPS。\n停手的时间点会自动推断，如果采用的打法不停手或停手时间点不一致，则本项失去意义，仅供参考。")
        label14 = tk.Label(frame1, text="P4爆发", height=1)
        label14.grid(row=0, column=13)
        ToolTip(label14, "在22%-10%之间的DPS。\n对大部分团队，这段时间的需要爆发DPS，因此这项数值十分关键。")
        label15 = tk.Label(frame1, text="P2关键治疗量", height=1)
        label15.grid(row=0, column=14)
        ToolTip(label15, "在P2（岳琅出现后到传功之前）对T的治疗数值。\n减伤会被等效算在其中。")
        label15 = tk.Label(frame1, text="P4关键治疗量", height=1)
        label15.grid(row=0, column=15)
        ToolTip(label15, "在P4（曳影剑激活后）对T的治疗数值。\n减伤会被等效算在其中。")
        
        for i in range(len(self.effectiveDPSList)):
            name = self.effectiveDPSList[i][0]
            color = getColor(self.effectiveDPSList[i][1])
            label1 = tk.Label(frame1, text=name, width = 13, height=1, fg=color)
            label1.grid(row=i+1, column=0)
            label2 = tk.Label(frame1, text=int(self.effectiveDPSList[i][2]), height=1)
            label2.grid(row=i+1, column=1)
            label3 = tk.Label(frame1, text=parseCent(self.effectiveDPSList[i][3], 0) + '%', height=1)
            label3.grid(row=i+1, column=2)
            label4 = tk.Label(frame1, text=int(self.effectiveDPSList[i][4]), height=1)
            label4.grid(row=i+1, column=3)
            label5 = tk.Label(frame1, text=int(self.effectiveDPSList[i][5]), height=1)
            label5.grid(row=i+1, column=4)
            label6 = tk.Label(frame1, text=int(self.effectiveDPSList[i][6]), height=1)
            label6.grid(row=i+1, column=5)
            label7 = tk.Label(frame1, text=int(self.effectiveDPSList[i][7]), height=1)
            label7.grid(row=i+1, column=6)
            label8 = tk.Label(frame1, text=int(self.effectiveDPSList[i][8]), height=1)
            label8.grid(row=i+1, column=7)
            label9 = tk.Label(frame1, text=int(self.effectiveDPSList[i][9]), height=1)
            label9.grid(row=i+1, column=8)
            label10 = tk.Label(frame1, text=int(self.effectiveDPSList[i][10]), height=1)
            label10.grid(row=i+1, column=9)
            label11 = tk.Label(frame1, text=int(self.effectiveDPSList[i][11]), height=1)
            label11.grid(row=i+1, column=10)
            label12 = tk.Label(frame1, text=int(self.effectiveDPSList[i][12]), height=1)
            label12.grid(row=i+1, column=11)
            label13 = tk.Label(frame1, text=int(self.effectiveDPSList[i][13]), height=1)
            label13.grid(row=i+1, column=12)
            label14 = tk.Label(frame1, text=int(self.effectiveDPSList[i][14]), height=1)
            label14.grid(row=i+1, column=13)
            label15 = tk.Label(frame1, text=int(self.effectiveDPSList[i][15]), height=1)
            label15.grid(row=i+1, column=14)
            label16 = tk.Label(frame1, text=int(self.effectiveDPSList[i][16]), height=1)
            label16.grid(row=i+1, column=15)
            
        frame2 = tk.Frame(window)
        frame2.pack()
        label01 = tk.Label(frame2, text="控剑复盘", height=1)
        label01.grid(row=0, column=0)
        
        rowNum = 0
        
        for line in self.detail["kongjian"]:
            rowNum += 1
            item = self.detail["kongjian"][line]
            color = getColor(item["player"][2])
            name = item["player"][1]
            label10 = tk.Label(frame2, text=name, height=1, fg=color)
            label10.grid(row=rowNum, column=0)
            
            columnNum = 0
            for log in item["log"]:
                columnNum += 1
                text11 = log[0]
                label11 = tk.Label(frame2, text=text11, height=1)
                label11.grid(row=rowNum, column=columnNum)
                
                columnNum += 1
                text12 = log[1]
                label12 = tk.Label(frame2, text=text12, height=1)
                label12.grid(row=rowNum, column=columnNum)
        
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

class YuelinyuelangReplayer(SpecificReplayer):

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
        
        if self.phaseFinal[self.phase] == 0:
            self.phaseFinal[self.phase] = self.finalTime
        if self.P4CoreStart != 0 and self.P4CoreFinal == 0:
            self.P4CoreFinal = self.finalTime
            
            
        phaseTime = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(1, 8):
            phaseTime[i] = (self.phaseFinal[i] - self.phaseStart[i]) / 1000
            if phaseTime[i] <= 0:
                phaseTime[i] = 1e+20
                
        #print(self.phaseStart)
        #print(self.phaseFinal)
                
        P4CoreTime = (self.P4CoreFinal - self.P4CoreStart) / 1000
        if P4CoreTime <= 0:
            P4CoreTime = 1e+20

        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:

                self.dps[line][2] = self.buffCounter[line].sumTime() / 1000

                dps = int(self.dps[line][0] / self.battleTime)
                bossResult.append([self.namedict[line][0].strip('"'),
                                   self.occDetailList[line],
                                   dps, 
                                   0,
                                   self.dps[line][2],
                                   int(self.dps[line][3] / (phaseTime[1] + phaseTime[2])),
                                   int(self.dps[line][4] / phaseTime[2]),
                                   int(self.dps[line][5] / phaseTime[3]),
                                   int(self.dps[line][6] / phaseTime[3]),
                                   self.dps[line][7],
                                   int(self.dps[line][8] / phaseTime[4]),
                                   int(self.dps[line][9] / phaseTime[5]),
                                   int(self.dps[line][10] / phaseTime[6]),
                                   int(self.dps[line][11] / phaseTime[7]),
                                   int(self.dps[line][12] / P4CoreTime),
                                   self.dps[line][13],
                                   self.dps[line][14], 
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
        if deathSource == "未知" and self.yuelinSource != "未知" and int(item[2]) - self.yuelinStack[item[4]][1] > 500:
            cycleTime = 1
            if self.yuelinSource == "狂雁！":
                cycleTime = 2
            if self.yuelinSource == "落鹰！":
                cycleTime = 3

            if int(item[2]) - self.yuelinTime > 5000:
                cycleTime = 0
                
            for i in range(cycleTime):
                self.yuelinBuff += 1
                lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                severe = 1
                if self.yuelinBuff > 60:
                    severe = 0
                self.potList.append([self.namedict[item[4]][0],
                                     self.occDetailList[item[4]],
                                     severe,
                                     self.bossNamePrint,
                                     "%s，第%d层：%s（推测）" % (lockTime, self.yuelinBuff, self.yuelinSource),
                                     ["层数从50层开始计算，等效于对结果的影响。", "此条根据重伤记录推测，不一定准确。"]])

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    if self.phase == 2:
                        for line in healRes:
                            if line in self.playerIDList:
                                self.dps[line][13] += healRes[line]
                    elif self.phase == 4:
                        for line in healRes:
                            if line in self.playerIDList:
                                self.dps[line][14] += healRes[line]  

                if item[7] in ["25425", "25426", "25427"]:
                    if item[4] not in self.detail["kongjian"]:
                        self.detail["kongjian"][item[4]] = {"player": ([item[4], self.namedict[item[4]][0].strip('"'), self.occDetailList[item[4]]]), "log": []}
                    if item[7] == "25425":
                        self.kongjianNum[item[4]] += 1
                        if self.kongjianNum[item[4]] == 1:
                            self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "驱影"])
                        else:
                            self.detail["kongjian"][item[4]]["log"][-1][1] = "驱影*%d"%self.kongjianNum[item[4]]
                    elif item[7] == "25426":
                        self.kongjianNum[item[4]] = 0
                        self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "爆杀"])
                    elif item[7] == "25427":
                        self.kongjianNum[item[4]] = 0
                        self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "留痕"])
                    
            else:
            
                if item[7] in ["25425", "25426", "25427"]:
                    if item[4] not in self.detail["kongjian"]:
                        self.detail["kongjian"][item[4]] = {"player": ([item[4], self.namedict[item[4]][0].strip('"'), self.occDetailList[item[4]]]), "log": []}
                    if item[7] == "25425":
                        self.kongjianNum[item[4]] += 1
                        if self.kongjianNum[item[4]] == 1:
                            self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "驱影"])
                        else:
                            self.detail["kongjian"][item[4]]["log"][-1][1] = "驱影*%d"%self.kongjianNum[item[4]]
                    elif item[7] == "25426":
                        self.kongjianNum[item[4]] = 0
                        self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "爆杀"])
                    elif item[7] == "25427":
                        self.kongjianNum[item[4]] = 0
                        self.detail["kongjian"][item[4]]["log"].append([parseTime((int(item[2]) - self.startTime)/1000), "留痕"])
            
                if item[4] in self.playerIDList:
                    if self.phase != 0 and item[7] not in ["25445"]:
                        self.dps[item[4]][0] += int(item[14])
                        if self.phase in [1,2] and item[5] in self.namedict and self.namedict[item[5]][0] in ['"岳琳"']:
                            self.dps[item[4]][3] += int(item[14])
                        if self.phase in [1,2] and item[5] in self.namedict and self.namedict[item[5]][0] in ['"蜂群蟊贼"']:
                            self.dps[item[4]][4] += int(item[14])
                        if self.phase == 3:
                            self.dps[item[4]][5] += int(item[14])
                            if item[5] in self.namedict and self.namedict[item[5]][0] in ['"蜂群莽夫"']:
                                self.dps[item[4]][6] += int(item[14])
                        if self.phase == 4:
                            self.dps[item[4]][8] += int(item[14])
                            if self.P4sub == 3:
                                self.dps[item[4]][12] += int(item[14])
                        if self.stoppedCheck:
                            self.dps[item[4]][8+self.P4sub] += int(item[14])
                                
                if not self.stoppedExist and self.phase == 4 and self.P4sub < 4:
                    stopped = self.shift.checkItem(item)
                    if stopped:
                        self.stoppedCheck = 1
                        self.stoppedExist = 1
                        stopDpsDict = self.shift.calSetADps()
                        for line in stopDpsDict:
                            self.dps[line][8+self.P4sub] += stopDpsDict[line]
                        self.phaseStart[4+self.P4sub] = int(item[2]) - 5000
                        self.detail["stop"].append(int(item[2]))
            
                pass       
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if item[6] in ["17899", "17732"]:
                self.buffCounter[item[5]].setState(int(item[2]), int(item[10]))
                
            if item[6] in ["17899"]:
                if self.dps[item[5]][7] == 0:
                    self.pushCount += 1
                    self.dps[item[5]][7] = self.pushCount
                
            if item[6] in ["17899"] and int(item[10]) in [9]:
                lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                self.potList.append([self.namedict[item[5]][0],
                                     self.occDetailList[item[5]],
                                     0,
                                     self.bossNamePrint,
                                     "%s传功失败：%d层" % (lockTime, int(item[10])),
                                     ["9层通常不影响通关，无伤大雅。"]])
            if item[6] in ["17899"] and int(item[10]) in [1,2,3,4,5,6,7,8]:
                lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                self.potList.append([self.namedict[item[5]][0],
                                     self.occDetailList[item[5]],
                                     1,
                                     self.bossNamePrint,
                                     "%s传功失败：%d层" % (lockTime, int(item[10])),
                                     ["8层以下通常为纯演员，建议分锅。"]])

            if self.mapDetail == "25人英雄达摩洞":
                if item[6] in ["17675"]:
                    if int(item[10]) > self.yuelinStack[item[5]][0] and int(item[2]) - self.yuelinStack[item[5]][1] > 500:
                        if self.yuelinSource != "未知":
                            self.yuelinBuff += 1
                            lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                            severe = 1
                            if self.yuelinBuff > 60:
                                severe = 0
                            self.potList.append([self.namedict[item[5]][0],
                                                 self.occDetailList[item[5]],
                                                 severe,
                                                 self.bossNamePrint,
                                                 "%s，第%d层：%s" % (lockTime, self.yuelinBuff, self.yuelinSource),
                                                 ["层数从50层开始计算，等效于对结果的影响。"]])
                    self.yuelinStack[item[5]][0] = int(item[10])
                    self.yuelinStack[item[5]][1] = int(item[2])
                
                    
        elif item[3] == '8':
            #print(item)
        
            if len(item) <= 4:
                return

            if item[4] in ['"飞隼！"', '"狂雁！"', '"落鹰！"', '"伏鹫！"']:
                self.yuelinSource = item[4].strip('"')
                self.yuelinTime = int(item[2])
            if item[4] in ['"让冰冷与黑暗吞噬你们……"']:
                self.yuelinSource = "未知"
                self.yuelinTime = int(item[2])
                
            if item[4] in ['"蜂群！蛰死这些俗人！誓死保护曳影剑！"']:
                self.phase = 2
                self.phaseFinal[1] = int(item[2])
                self.phaseStart[2] = int(item[2])
                
            if item[4] in ['"！"']:
                self.phase = 3
                self.phaseFinal[2] = int(item[2])
                self.phaseStart[3] = int(item[2])
                
            if item[4] in ['"小影！可恶！姐姐快救小影！"']:
                self.phase = 4
                self.P4sub = 1
                self.phaseFinal[3] = int(item[2])
                self.phaseStart[4] = int(item[2])
                self.MonsterCount = 0
                self.shift = DpsShiftWindow(self.playerIDList.keys(), 5, 5, 0.3, int(item[2]))
                
            if item[4] in ['"冥翎，为亡者开路！"']:
                if self.stoppedCheck:
                    self.stoppedCheck = 0
                    self.stoppedExist = 0
                    self.phaseFinal[4+self.P4sub] = int(item[2])
                self.P4sub += 1
                if self.P4sub == 3:
                    self.P4CoreStart = int(item[2])
                if self.P4sub == 4:
                    self.P4CoreFinal = int(item[2])
                self.MonsterCount = 0
                self.shift = DpsShiftWindow(self.playerIDList.keys(), 5, 5, 0.3, int(item[2]))
                
            if item[4] == '"你们竟敢染指琅弟心中所好，通通该死！"':
                self.win = 1
                self.phaseFinal[4] = int(item[2])
                
        elif item[3] == '3': #重伤记录
            pass
            
        elif item[3] == "10": #战斗状态变化
            if item[5] in self.namedict and item[6] == 'true':
                if self.namedict[item[5]][0] in ['"蜂群弩手"']:
                    self.MonsterCount += 1
                    if self.MonsterCount == 3 and self.stoppedCheck and self.P4sub < 4:
                        self.stoppedCheck = 0
                        self.stoppedExist = 0
                        self.phaseFinal[4+self.P4sub] = int(item[2])
                    
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
        self.activeBoss = "岳琳&岳琅"
        
        #岳琳&岳琅数据格式：
        #4 被控时间 5 常规BOSS 6 蟊贼DPS 7 传功DPS 8 莽夫DPS 9 传功顺序 10 P4DPS 11 P4停手1 12 P4停手2 13 P4停手3 14 P4爆发 15 P2关键治疗量 16 P4关键治疗量
        
        self.dps = {}
        self.detail["boss"] = "岳琳&岳琅"
        self.win = 0
        self.phase = 0
        self.P4sub = 0
        
        self.phaseStart = [0, 0, 0, 0, 0, 0, 0, 0]
        self.phaseFinal = [0, 0, 0, 0, 0, 0, 0, 0]
        self.P4CoreStart = 0
        self.P4CoreFinal = 0
        self.MonsterCount = 0
        
        self.phaseStart[1] = self.startTime

        self.stoppedExist = 0
        self.stoppedCheck = 0
        
        self.pushCount = 0
        self.detail["stop"] = []
        self.detail["kongjian"] = {}
        self.kongjianNum = {}
        
        self.yuelinBuff = 50
        self.yuelinSource = "未知"
        self.yuelinStack = {}
        for line in self.playerIDList:
            self.yuelinStack[line] = [0, 0]
        self.yuelinTime = 0
        
        self.criticalHealCounter = {}
        self.buffCounter = {}
        
        for line in self.playerIDList:
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            self.criticalHealCounter[line] = CriticalHealCounter()
            if self.occDetailList[line] in ['1t', '3t', '10t', '21t']:
                self.criticalHealCounter[line].active()
                self.criticalHealCounter[line].setCriticalTime(-1)
            self.kongjianNum[line] = 0
        

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


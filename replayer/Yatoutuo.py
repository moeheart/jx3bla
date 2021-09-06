# Created by moeheart at 02/14/2021
# 哑头陀的定制复盘方法库。
# 哑头陀是达摩洞5号首领，复盘主要集中在以下几个方面：
# 被控时间、真假剑、打醒迷神钉(TODO)、机甲详细复盘

from replayer.Base import *
from replayer.utils import CriticalHealCounter
from tools.Functions import *
        
class YatoutuoWindow():
    '''
    哑头陀的专有复盘窗口类。
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
        window.title('哑头陀详细复盘')
        window.geometry('1200x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #哑头陀数据格式：
        #4 被控时间 5 广目DPS 6 增长DPS 7 真剑DPS 8 假剑DPS 9 核心DPS 10 多闻DPS 11 持国P1DPS 12 持国P2DPS 13 持国P3DPS 14 P1木人DPS 15 P2木人DPS
        label01 = tk.Label(frame1, text="玩家名", width = 13, height=1)
        label01.grid(row=0, column=0)
        label02 = tk.Label(frame1, text="有效DPS", height=1)
        label02.grid(row=0, column=1)
        ToolTip(label02, "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。\n在哑头陀，会同时排除机甲的伞击与挥拳伤害。")
        label03 = tk.Label(frame1, text="团队-心法DPS", height=1)
        label03.grid(row=0, column=2)
        ToolTip(label03, "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        label04 = tk.Label(frame1, text="被控", height=1)
        label04.grid(row=0, column=3)
        ToolTip(label04, "受到影响无法正常输出的时间，以秒计，包括净天眼的点名。")
        label05 = tk.Label(frame1, text="增长DPS", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "对增长天王（万剑阵BOSS）造成的DPS。")
        label06 = tk.Label(frame1, text="广目DPS", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "对增长天王（净天眼BOSS）造成的DPS。")
        label07 = tk.Label(frame1, text="真剑DPS", height=1)
        label07.grid(row=0, column=6)
        ToolTip(label07, "在卍剑阵阶段，对真剑造成的DPS。")
        label08 = tk.Label(frame1, text="假剑DPS", height=1)
        label08.grid(row=0, column=7)
        ToolTip(label08, "在卍剑阵阶段，对假剑造成的DPS。")
        label09 = tk.Label(frame1, text="核心DPS", height=1)
        label09.grid(row=0, column=8)
        ToolTip(label09, "在充能核心阶段，对核心造成的DPS。")
        label10 = tk.Label(frame1, text="多闻DPS", height=1)
        label10.grid(row=0, column=9)
        ToolTip(label10, "在最终阶段，多闻天王100%-80%期间的DPS。")
        label11 = tk.Label(frame1, text="持国P1", height=1)
        label11.grid(row=0, column=10)
        ToolTip(label11, "在最终阶段，持国天王100%-80%期间的DPS。\n这段时间的DPS很危险，可能会导致伞击次数不够。")
        label12 = tk.Label(frame1, text="持国P2", height=1)
        label12.grid(row=0, column=11)
        ToolTip(label12, "在最终阶段，持国天王80%-35%期间的DPS。\n这段时间的DPS是安全的，可以为机甲增加容错。")
        label13 = tk.Label(frame1, text="持国P3", height=1)
        label13.grid(row=0, column=12)
        ToolTip(label13, "在最终阶段，持国天王35%-0%期间的DPS。\n这段时间的DPS是安全的，可以为机甲增加容错。")
        label14 = tk.Label(frame1, text="P1木人", height=1)
        label14.grid(row=0, column=13)
        ToolTip(label14, "P1阶段对木人的DPS，包括木人·鸠盘茶与木人·龙王。")
        label15 = tk.Label(frame1, text="P2木人", height=1)
        label15.grid(row=0, column=14)
        ToolTip(label15, "P1阶段对木人的DPS，包括木人·乾闼婆与木人·夜叉。\n时间只按乾闼婆出现的时间计算。")
        
        for i in range(len(self.effectiveDPSList)):
            name = self.effectiveDPSList[i][0]
            color = getColor(self.effectiveDPSList[i][1])
            label1 = tk.Label(frame1, text=name, width = 13, height=1, fg=color)
            label1.grid(row=i+1, column=0)
            label2 = tk.Label(frame1, text=int(self.effectiveDPSList[i][2]), height=1)
            label2.grid(row=i+1, column=1)
            
            if getOccType(self.effectiveDPSList[i][1]) != "healer":
                text3 = str(self.effectiveDPSList[i][3]) + '%'
                color3 = "#000000"
            else:
                text3 = self.effectiveDPSList[i][3]
                color3 = "#00ff00"
            label3 = tk.Label(frame1, text=text3, height=1, fg=color3)
            label3.grid(row=i+1, column=2)
            
            label4 = tk.Label(frame1, text=int(self.effectiveDPSList[i][4]), height=1)
            label4.grid(row=i+1, column=3)
            label5 = tk.Label(frame1, text=int(self.effectiveDPSList[i][5]), height=1)
            label5.grid(row=i+1, column=4)
            label6 = tk.Label(frame1, text=int(self.effectiveDPSList[i][6]), height=1)
            label6.grid(row=i+1, column=5)
            color78 = "#000000"
            if self.effectiveDPSList[i][8] > self.effectiveDPSList[i][7]:
                color78 = "#ff0000" #若假剑DPS比真剑DPS高，则以红色显示
            label7 = tk.Label(frame1, text=int(self.effectiveDPSList[i][7]), height=1, fg=color78)
            label7.grid(row=i+1, column=6)
            label8 = tk.Label(frame1, text=int(self.effectiveDPSList[i][8]), height=1, fg=color78)
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
            
        frame2 = tk.Frame(window)
        frame2.pack()
        label01 = tk.Label(frame2, text="机甲复盘", height=1)
        label01.grid(row=0, column=0)
        
        label11 = tk.Label(frame2, text="驾驶员", height=1)
        label11.grid(row=1, column=0)
        name = self.detail["jijia"]["player"][0]
        color = getColor(self.detail["jijia"]["player"][1])
        label12 = tk.Label(frame2, text=name, height=1, fg=color)
        label12.grid(row=1, column=1)
        
        rowNum = 1
        
        for i in range(3):
            rowNum += 1
            label21 = tk.Label(frame2, text="第%d阶段"%(i+1), height=1)
            label21.grid(row=rowNum, column=0)
            
            phaseDescription = ["100%-80%阶段", "80%-35%阶段", "35%-0%阶段"][i]
            ToolTip(label21, phaseDescription)
            
            label22 = tk.Label(frame2, text="用时", height=1)
            label22.grid(row=rowNum, column=1)
            
            label23 = tk.Label(frame2, text=self.detail["jijia"]["action"][i][0], height=1)
            label23.grid(row=rowNum, column=2)
            
            label24 = tk.Label(frame2, text="伞击次数", height=1)
            label24.grid(row=rowNum, column=3)
            
            label25 = tk.Label(frame2, text=self.detail["jijia"]["action"][i][1], height=1)
            label25.grid(row=rowNum, column=4)
            
            label26 = tk.Label(frame2, text="挥拳次数", height=1)
            label26.grid(row=rowNum, column=5)
            
            label27 = tk.Label(frame2, text=self.detail["jijia"]["action"][i][2], height=1)
            label27.grid(row=rowNum, column=6)
        
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

class YatoutuoReplayer(SpecificReplayer):

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
        phaseTime = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        for line in self.zijian:
            for player in self.zijian[line]:
                if player in self.dps:
                    if self.zijian[line]["sum"] > 4700000:
                        self.dps[player][5] += self.zijian[line][player]
                    else:
                        self.dps[player][6] += self.zijian[line][player]
        
        if self.phaseFinal[self.phase] == 0:
            self.phaseFinal[self.phase] = self.finalTime

        for i in range(1, 12):
            phaseTime[i] = (self.phaseFinal[i] - self.phaseStart[i]) / 1000
            if phaseTime[i] <= 0:
                phaseTime[i] = 1e+20
                
        for i in range(3):
            self.detail["jijia"]["action"][i][0] = parseTime(phaseTime[7+i])
        
        playerEscapeDict = {}
        for line in self.playerIDList:
            playerEscapeDict[line] = []
            for i in range(self.burstCount):
                if i+1 not in self.playerBurstLog[line]:
                    playerEscapeDict[line].append(str(i+1))

        for id in playerEscapeDict:
            if len(playerEscapeDict[id]) > 0:
                s = ",".join(playerEscapeDict[id])
                self.potList.append([self.namedict[id][0],
                                     self.occdict[id][0],
                                     0,
                                     self.bossNamePrint,
                                     "承伤逃课，次数：%d" %len(playerEscapeDict[id]),
                                     ["总承伤次数：%d"%self.burstCount, "逃课记录：%s"%s]])  
        for id in self.playerWork:
            if self.playerWork[id] > 0:
                self.potList.append([self.namedict[id][0],
                                     self.occdict[id][0],
                                     3,
                                     self.bossNamePrint,
                                     "控制戏龙珠，次数：%d" %self.playerWork[id],
                                     ["大部分推拉技能都会被计入这项统计中，用于补贴"]])
        
  
        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:

                self.dps[line][2] = int(self.buffCounter[line].sumTime() / 1000)
                
                if getOccType(self.occDetailList[line]) == "healer":
                    self.dps[line][1] = int(self.hps[line] / self.battleTime)

                dps = int(self.dps[line][0] / self.battleTime)
                bossResult.append([self.namedict[line][0].strip('"'),
                                   self.occDetailList[line],
                                   dps, 
                                   self.dps[line][1],
                                   self.dps[line][2],
                                   int(self.dps[line][3] / phaseTime[1]),
                                   int(self.dps[line][4] / phaseTime[2]),
                                   int(self.dps[line][5] / phaseTime[3]),
                                   int(self.dps[line][6] / phaseTime[4]),
                                   int(self.dps[line][7] / phaseTime[5]),
                                   int(self.dps[line][8] / phaseTime[6]),
                                   int(self.dps[line][9] / phaseTime[7]),
                                   int(self.dps[line][10] / phaseTime[8]),
                                   int(self.dps[line][11] / phaseTime[9]),
                                   int(self.dps[line][12] / phaseTime[10]),
                                   int(self.dps[line][13] / phaseTime[11]),
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
            
        return self.effectiveDPSList, self.potList, self.detail

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
            
                if item[7] == "24650":
                    if int(item[14]) != 0:
                    
                        if int(item[2]) - self.burstTime > 1000:
                            self.burstTime = int(item[2])
                            self.burstCount += 1
                        self.playerBurstCnt[item[5]] += 1
                        self.playerBurstLog[item[5]].append(self.burstCount)
                        
                if item[7] == "24706": #琶音
                    if not self.phase7Appear:
                        self.phase = 7
                        self.phase7Appear = 1
                        self.phaseFinal[6] = int(item[2])
                        self.phaseStart[7] = int(item[2])
                        
                if item[7] == "24703" and int(item[2]) - self.senluoTime > 5000: #森罗壁垒
                    self.senluoTime = int(item[2])
                    if self.phase in [7,8]:
                        self.phaseFinal[self.phase] = int(item[2])
                        self.phase += 1
                        self.phaseStart[self.phase] = int(item[2])
                    
            else:
            
                if item[5] in self.namedict and self.namedict[item[5]][0] in ['"毗留博叉"'] and item[14] != '0':
                    if not self.phase2Appear:
                        self.phase2Appear = 1
                        if self.phase == 1:
                            self.phaseFinal[1] = int(item[2])
                        self.phase = 2
                        self.phaseStart[2] = int(item[2])
                        
                if item[5] in self.namedict and self.namedict[item[5]][0] in ['"毗流驮迦"'] and item[14] != '0':
                    if not self.phase1Appear:
                        self.phase1Appear = 1
                        if self.phase == 2:
                            self.phaseFinal[2] = int(item[2])
                        self.phase = 1
                        self.phaseStart[1] = int(item[2])
                        
                if item[5] in self.namedict and self.namedict[item[5]][0] in ['"毗沙门"'] and item[14] != '0':
                    if not self.phase6Appear:
                        self.phase = 6
                        self.phase6Appear = 1
                        self.phaseStart[6] = int(item[2])
                        
                if item[5] in self.namedict and self.namedict[item[5]][0] in ['"戏龙珠"']:
                    self.longzhuID.append(item[5])
                    
                if item[5] in self.namedict and self.namedict[item[5]][0] in ['"子剑"'] and item[5] not in self.zijian:
                    self.zijian[item[5]] = {"sum": 0}
            
                if item[4] in self.playerIDList:
                    if self.phase != 0 and item[7] not in ["24710", "24730"]:
                        self.dps[item[4]][0] += int(item[14])
                        if self.phase in [1,2,5,6]:
                            self.dps[item[4]][2 + self.phase] += int(item[14])
                        if item[5] in self.namedict:
                            if self.namedict[item[5]][0] in ['"木人·龙王"', '"木人·鸠盘茶"']:
                                self.dps[item[4]][12] += int(item[14])
                            if self.namedict[item[5]][0] in ['"木人·夜叉"', '"木人·乾闼婆"']:
                                self.dps[item[4]][13] += int(item[14])
                            if self.namedict[item[5]][0] in ['"提多罗吒"']:
                                if self.phase in [7,8,9]:
                                    self.dps[item[4]][2 + self.phase] += int(item[14])
                            if item[5] in self.zijian:
                                self.zijian[item[5]]["sum"] += int(item[14])
                                if item[4] not in self.zijian[item[5]]:
                                    self.zijian[item[5]][item[4]] = 0
                                self.zijian[item[5]][item[4]] += int(item[14])
                                if int(item[14]) > 0:
                                    if int(item[2]) - self.phase3Start > 50000:
                                        self.phase3Start = int(item[2])
                                        self.zijianLeft = 3
                            
                if item[5] == self.longzhuID and item[7] in ["242", "546", "305", "1613", "2479", "3971", "22341"]:
                    playerWork[item[4]] += 1
                    
                if item[7] == "24710" and int(item[14]) > 0 and self.phase in [7,8,9]: #统计伞击
                    self.detail["jijia"]["action"][self.phase-7][1] += 1
                    
                if item[7] == "24730" and int(item[14]) > 0 and self.phase in [7,8,9]: #统计挥拳
                    self.detail["jijia"]["action"][self.phase-7][2] += 1
                    
                if item[7] == "24731" and self.phase == 9:
                    self.phaseFinal[9] = int(item[2])
                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return    
                
            if item[6] in ["15774", "17200"]:  # buff精神匮乏
                stack = int(item[10])
                if stack >= 20 and self.jingshenkuifa[item[5]] == 0:
                    lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    self.jingshenkuifa[item[5]] = 1
                    self.potList.append([self.namedict[item[5]][0],
                                         self.occDetailList[item[5]],
                                         0,
                                         self.bossNamePrint,
                                         "%s减疗叠加20层" % lockTime,
                                         ["不间断的减疗只计算一次"]])
                if stack < 20 and self.jingshenkuifa[item[5]] == 1:
                    self.jingshenkuifa[item[5]] = 0
                    
            if item[6] == "17798" and item[10] == "1": #以获得蒸汽buff判定进入充能核心阶段
                if not self.phase5Appear:
                    self.phase5Appear = 1
                    self.phaseFinal[self.phase] = int(item[2])
                    self.phase = 5
                    self.phaseStart[5] = int(item[2])
                    self.hexinNum = 2
                    
            if item[6] == "17929":
                self.buffCounter[item[5]].setState(int(item[2]), int(item[10]))
                
            if item[6] == "17736":
                self.detail["jijia"]["player"] = [self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]]
                    
        elif item[3] == '8':
            if len(item) <= 4:
                return
            if item[4] == '"…… …… …… ……"':
                self.win = 1
                
        elif item[3] == '3': #重伤记录
            if item[4] in self.namedict and (item[4] not in self.occdict or self.occdict[item[4]][0] == '0'):
                if self.namedict[item[4]][0] in ['"充能核心"']:
                    self.hexinNum -= 1
                    if self.hexinNum == 0:
                        self.phase = 0
                        self.phaseFinal[5] = int(item[2])
                if self.namedict[item[4]][0] in ['"木人·龙王"', '"木人·鸠盘茶"']:
                    if self.phase10Start != 0:
                        self.phaseFinal[10] += int(item[2]) - self.phase10Start
                        self.phase10Start = 0
                if self.namedict[item[4]][0] in ['"木人·乾闼婆"']:
                    if self.phase11Start != 0:
                        self.phaseFinal[11] += int(item[2]) - self.phase11Start
                        self.phase11Start = 0
                if self.namedict[item[4]][0] in ['"子剑"']:
                    if self.phase3Start != 0 and self.zijianLeft > 0:
                        self.zijianLeft -= 1
                        if self.zijianLeft == 0:
                            self.phaseFinal[3] += int(item[2]) - self.phase3Start
                            self.phaseFinal[4] += int(item[2]) - self.phase3Start
            
        elif item[3] == "10": #战斗状态变化
            if item[5] in self.namedict and item[6] == 'true':
                if self.namedict[item[5]][0] in ['"木人·龙王"', '"木人·鸠盘茶"'] and self.phase10Start == 0:
                    self.phase10Start = int(item[2])
                if self.namedict[item[5]][0] in ['"木人·乾闼婆"'] and self.phase11Start == 0:
                    self.phase11Start = int(item[2])

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
        self.activeBoss = "哑头陀"
        
        #哑头陀数据格式：
        #4 被控时间 5 广目DPS 6 增长DPS 7 真剑DPS 8 假剑DPS 9 核心DPS 10 多闻DPS 11 持国P1DPS 12 持国P2DPS 13 持国P3DPS 14 P1木人DPS 15 P2木人DPS
        #机甲：玩家ID、门派；每个阶段的时间、伞击数量、挥拳数量
        
        self.dps = {}
        self.hps = {}
        self.detail["boss"] = "哑头陀"
        self.detail["jijia"] = {"player": ["未知", "0"], "action": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}
        self.win = 0
        self.phase = 0
        
        self.phase1Appear = 0
        self.phase2Appear = 0
        self.phase5Appear = 0
        self.phase6Appear = 0
        self.phase7Appear = 0
        self.senluoTime = 0
        
        self.zijian = {}
        
        self.phase3Start = 0
        self.zijianLeft = 0
        self.phase10Start = 0
        self.phase11Start = 0
        
        self.phaseStart = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.phaseFinal = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.playerWork = {}
        self.jingshenkuifa = {}
        
        self.playerBurstCnt = {}
        self.playerBurstLog = {}
        self.burstCount = 0
        self.burstTime = 0
        
        self.buffCounter = {}
        
        self.longzhuID = []
        self.hexinNum = 0
        for line in self.playerIDList:
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.hps[line] = 0
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            self.playerWork[line] = 0
            self.jingshenkuifa[line] = 0
            self.playerBurstCnt[line] = 0
            self.playerBurstLog[line] = []
        

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


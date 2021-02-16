# Created by moeheart at 1/11/2021
# 余晖的定制复盘方法库。
# 余晖是达摩洞1号首领，复盘主要集中在以下几个方面：
# 1. 狂热崇拜值的层数。
# 2. 引导情况。
# 3. 寒刃绞杀承伤情况。
# 余晖的各种处理较为简单，可以作为例程来参考。

from replayer.Base import *

class YuHuiWindow():
    '''
    余晖的专有复盘窗口类。
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
        window.title('余晖详细复盘')
        window.geometry('1000x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        label01 = tk.Label(frame1, text="玩家名", width = 13, height=1)
        label01.grid(row=0, column=0)
        label02 = tk.Label(frame1, text="有效DPS", height=1)
        label02.grid(row=0, column=1)
        ToolTip(label02, "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        label03 = tk.Label(frame1, text="团队-心法DPS", height=1)
        label03.grid(row=0, column=2)
        ToolTip(label03, "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        label04 = tk.Label(frame1, text="P1DPS", height=1)
        label04.grid(row=0, column=3)
        ToolTip(label04, "余晖第一阶段，也即100%-60%血量阶段的DPS。")
        label05 = tk.Label(frame1, text="P2DPS", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "余晖第二阶段，也即60%-0%血量阶段的DPS。")
        label06 = tk.Label(frame1, text="狂热崇拜层数", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "由该玩家产生的狂热崇拜值。\n注意，无尽刀狱会被计算为8层。")
        
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
            color6 = "#000000"
            if self.effectiveDPSList[i][6] > 0:
                color6 = "#ff0000"
            label6 = tk.Label(frame1, text=self.effectiveDPSList[i][6], height=1, fg=color6)
            label6.grid(row=i+1, column=5)
            
        frame2 = tk.Frame(window)
        frame2.pack()
        label01 = tk.Label(frame2, text="寒刃绞杀承伤记录", height=1)
        label01.grid(row=0, column=0)
        rowNum = 0
        for i in range(len(self.detail["jiaosha"])):
            rowNum += 1
            single = self.detail["jiaosha"][i]
            text11 = "第%d组"%(i+1)
            label11 = tk.Label(frame2, text=text11, height=1)
            label11.grid(row=rowNum, column=0)
            
            for k in [0, 1]:
                text12 = "点名"
                label12 = tk.Label(frame2, text=text12, height=1)
                label12.grid(row=rowNum, column=1)
                color = getColor(single[k][0][2])
                name = single[k][0][1]
                label13 = tk.Label(frame2, text=name, height=1, fg=color)
                label13.grid(row=rowNum, column=2)
                text14 = "承伤"
                label14 = tk.Label(frame2, text=text14, height=1)
                label14.grid(row=rowNum, column=3)
                for j in range(1, len(single[k])):
                    color = getColor(single[k][j][2])
                    name = single[k][j][1]
                    label15 = tk.Label(frame2, text=name, width = 8, height=1, fg=color)
                    label15.grid(row=rowNum, column=3+j)
                rowNum += 1
                
            text32 = "逃课"
            label32 = tk.Label(frame2, text=text32, height=1)
            label32.grid(row=rowNum, column=1)
            for j in range(len(single[2])):
                color = getColor(single[2][j][2])
                name = single[2][j][1]
                label33 = tk.Label(frame2, text=name, width = 8, height=1, fg=color)
                label33.grid(row=rowNum, column=2+j)
       
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

class YuhuiReplayer(SpecificReplayer):

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        
        if self.mapDetail != "10人普通达摩洞":
            playerHitList = []
            for line in self.playerHitDict:
                if self.playerHitDict[line]["num"] != 0:
                    playerHitList.append([line, self.playerHitDict[line]["num"], self.playerHitDict[line]["log"]])
            playerHitList.sort(key = lambda x:-x[1])
            for i in range(len(playerHitList)):
                id = playerHitList[i][0]
                if playerHitList[i][1] >= 10:
                    self.potList.append([self.namedict[id][0],
                                         self.occdict[id][0],
                                         1,
                                         self.bossNamePrint,
                                         "狂热崇拜值叠加：%d层" %playerHitList[i][1],
                                         playerHitList[i][2]])
                elif playerHitList[i][1] > 0:
                    self.potList.append([self.namedict[id][0],
                                         self.occdict[id][0],
                                         0,
                                         self.bossNamePrint,
                                         "狂热崇拜值叠加：%d层" %playerHitList[i][1],
                                         playerHitList[i][2]])
            
            for line in self.playerUltDict:
                id = line
                if self.playerUltDict[line]["num"] > 0:
                    self.potList.append([self.namedict[id][0],
                                         self.occdict[id][0],
                                         3,
                                         self.bossNamePrint,
                                         "完成引导，次数：%d" %self.playerUltDict[line]["num"],
                                         self.playerUltDict[line]["log"]])
                                         
        recordGORate = 1
        bossResult = []
        P1Time = (self.P1FinalTime - self.startTime) / 1000 + 1e-10
        P2Time = (self.P2FinalTime - self.P1FinalTime) / 1000 + 1e-10
        
        for line in self.playerIDList:
            if line in self.dps:
                dps = self.dps[line][0] / self.battleTime
                P1dps = self.dps[line][2] / P1Time
                P2dps = self.dps[line][3] / P2Time
                chongBai = self.playerHitDict[line]["num"]
                bossResult.append([self.namedict[line][0].strip('"'),
                                   self.occDetailList[line],
                                   dps,
                                   0,
                                   P1dps,
                                   P2dps,
                                   chongBai
                                   ])
                bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        return self.effectiveDPSList, self.potList, self.detail
        
    def recordDeath(self, item):
        '''
        在有玩家重伤时记录狂热值的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if self.countHit:
            self.playerHitDict[item[4]]["num"] += 10
            self.playerHitDict[item[4]]["log"].append("%s，重伤：10层"%parseTime((int(item[2]) - self.startTime) / 1000)) 

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if item[3] == '1':  # 技能
            if self.occdict[item[5]][0] != '0':
                ultCount = 2
                if self.mapDetail == "25人英雄达摩洞":
                    ultCount = 5
                if item[7] == "24438":
                    self.playerHitDict[item[5]]["num"] += 3
                    self.playerHitDict[item[5]]["log"].append("%s，血海寒刀：3层"%parseTime((int(item[2]) - self.startTime) / 1000))
                if item[7] == "24464":
                    self.playerHitDict[item[5]]["num"] += ultCount
                    self.playerHitDict[item[5]]["log"].append("%s，摧城盾冲：%d层"%(parseTime((int(item[2]) - self.startTime) / 1000), ultCount))
                if item[7] in ["24471", "24533"]:
                    self.playerHitDict[item[5]]["num"] += 8
                    self.playerHitDict[item[5]]["log"].append("%s，无尽刀狱：8层"%parseTime((int(item[2]) - self.startTime) / 1000))
                if item[7] == "24472":
                    self.playerHitDict[item[5]]["num"] += ultCount
                    self.playerHitDict[item[5]]["log"].append("%s，寒刃血莲：%d层"%(parseTime((int(item[2]) - self.startTime) / 1000), ultCount))
                if item[7] == "24497" and self.phase == 1:
                    self.phase = 2
                    self.P1FinalTime = int(item[2])
                
                if item[7] == "24469": #寒刃绞杀
                    if int(item[2]) - self.jiaoshaTime > 500 and self.jiaoshaNum <= 3:
                        self.jiaoshaNum += 1
                    self.jiaoshaTime = int(item[2])
                    if self.jiaoshaNum == 3:
                        if item[5] not in self.detail["jiaosha"][-1][0][0][0] and item[5] not in self.detail["jiaosha"][-1][0][-1][0]:
                            self.detail["jiaosha"][-1][0].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                    elif self.jiaoshaNum == 4:
                        if item[5] not in self.detail["jiaosha"][-1][1][0][0] and item[5] not in self.detail["jiaosha"][-1][1][-1][0]:
                            self.detail["jiaosha"][-1][1].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        
            else:
                if item[4] in self.playerIDList:
                    self.dps[item[4]][0] += int(item[14])
                    if self.phase == 1:
                        self.dps[item[4]][2] += int(item[14])
                    else:
                        self.dps[item[4]][3] += int(item[14])
                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
            if self.jiaoshaNum >= 4 and int(item[2]) - 3000 > self.jiaoshaTime:
                for line in self.playerIDList:
                    leave = 1
                    for line2 in self.detail["jiaosha"][-1][0]:
                        if line2[0] == line:
                            leave = 0
                    for line2 in self.detail["jiaosha"][-1][1]:
                        if line2[0] == line:
                            leave = 0
                    if leave:
                        self.detail["jiaosha"][-1][2].append([line, self.namedict[line][0].strip('"'), self.occDetailList[line]])
                self.jiaoshaNum = 0
            if item[6] == "17685" and int(item[10]) > 0:
                self.playerHitDict[item[5]]["num"] += 5
                self.playerHitDict[item[5]]["log"].append("%s，易怒之人：5层"%parseTime((int(item[2]) - self.startTime) / 1000))
            if item[6] == "17613" and int(item[10]) > 0:
                self.playerUltDict[item[5]]["num"] += 1
                self.playerUltDict[item[5]]["log"].append("%s，引导：震天血盾"%parseTime((int(item[2]) - self.startTime) / 1000)) 
            if item[6] == "17911" and int(item[10]) > 0:
                self.playerUltDict[item[5]]["num"] += 1
                self.playerUltDict[item[5]]["log"].append("%s，引导：血莲绽放"%parseTime((int(item[2]) - self.startTime) / 1000))
            if item[6] == "17616" and int(item[10]) > 0:
                if self.jiaoshaNum == 0:
                    self.detail["jiaosha"].append([[], [], []])
                    self.detail["jiaosha"][-1][0].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                    self.jiaoshaNum += 1
                elif self.jiaoshaNum == 1:
                    self.detail["jiaosha"][-1][1].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                    self.jiaoshaNum += 1
                    
        elif item[3] == '8':
            if len(item) <= 4:
                return
            if item[4] == '"是时候用你们的鲜血来换取最高的欢呼声了！"':
                self.countHit = 0
            if item[4] == '"不可能！我才是……血斗场的……王者……"':
                self.P2FinalTime = int(item[2])
                if self.P1FinalTime == 0:
                    self.P1FinalTime = self.P2FinalTime - 1
                self.win = 1
        
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
        self.activeBoss = "余晖"
        self.win = 0
        
        self.dps = {}
        self.playerHitDict = {}
        self.playerUltDict = {}
        for line in self.playerIDList:
            self.playerHitDict[line] = {"num": 0, "log": []}
            self.playerUltDict[line] = {"num": 0, "log": []}
            self.dps[line] = [0, 0, 0, 0, 0]
        self.countHit = 1
        
        #余晖数据格式：
        #4 P1dps; 5 P2dps; 6 狂热层数;
        #绞杀：点名+1组ID(list)，点名+2组ID(list)，逃课ID
        
        self.detail["boss"] = "余晖"
        self.detail["jiaosha"] = []
        self.jiaoshaNum = 0
        self.jiaoshaTime = 0
        
        self.P1FinalTime = 0
        self.P2FinalTime = 0
        self.phase = 1

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


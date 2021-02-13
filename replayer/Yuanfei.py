# Created by moeheart at 02/08/2021
# 猿飞的定制复盘方法库。
# 猿飞是达摩洞4号首领，复盘主要集中在以下几个方面：
# （TODO 文档待补充）

from replayer.Base import *
from replayer.utils import CriticalHealCounter
from Functions import *
        
class YuanFeiWindow():
    '''
    猿飞的专有复盘窗口类。
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
        window.title('猿飞详细复盘')
        window.geometry('1400x800')
        
        frame1 = tk.Frame(window)
        frame1.pack(side = tk.LEFT, anchor = tk.N)
        
        #4 被控时间; 5 P1DPS; 6 P2DPS; 7 P3DPS; 8 P4DPS; 9 关键治疗量
        label01 = tk.Label(frame1, text="玩家名", width = 13, height=1)
        label01.grid(row=0, column=0)
        label02 = tk.Label(frame1, text="有效DPS", height=1)
        label02.grid(row=0, column=1)
        ToolTip(label02, "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        label03 = tk.Label(frame1, text="团队-心法DPS", height=1)
        label03.grid(row=0, column=2)
        ToolTip(label03, "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        label04 = tk.Label(frame1, text="被控", height=1)
        label04.grid(row=0, column=3)
        ToolTip(label04, "受到影响无法正常输出的时间，以秒计，包括点名上天、闪腿的沉默，与承伤的击倒。")
        label05 = tk.Label(frame1, text="P1DPS", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "在100%-80%血量之间的DPS。")
        label06 = tk.Label(frame1, text="P2DPS", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "在80%-55%血量之间的DPS。")
        label07 = tk.Label(frame1, text="P3DPS", height=1)
        label07.grid(row=0, column=6)
        ToolTip(label07, "在55%-30%血量之间的DPS。")
        label08 = tk.Label(frame1, text="P4DPS", height=1)
        label08.grid(row=0, column=7)
        ToolTip(label08, "在30%-0%血量之间的DPS。")
        label09 = tk.Label(frame1, text="关键治疗量", height=1)
        label09.grid(row=0, column=8)
        ToolTip(label09, "对被击倒状态的玩家的治疗数值。\nP2只持续5秒，而P3持续到奶满为止，与游戏中一致。")
        
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
            
        frame2 = tk.Frame(window)
        frame2.pack(side = tk.TOP)
        label01 = tk.Label(frame2, text="堕天腿承伤记录", height=1)
        label01.grid(row=0, column=0)
        rowNum = 0
        for i in range(len(self.detail["duotian"])):
            rowNum += 1
            single = self.detail["duotian"][i]
            text11 = "第%d组"%(i+1)
            label11 = tk.Label(frame2, text=text11, height=1)
            label11.grid(row=rowNum, column=0)
            
            for k in [0, 1, 2, 3]:
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
                
            '''
            text32 = "逃课"
            label32 = tk.Label(frame2, text=text32, height=1)
            label32.grid(row=rowNum, column=1)
            for j in range(len(single[4])):
                color = getColor(single[4][j][2])
                name = single[4][j][1]
                label33 = tk.Label(frame2, text=name, width = 8, height=1, fg=color)
                label33.grid(row=rowNum, column=2+j)
            '''
                
        frame3 = tk.Frame(window)
        frame3.pack(side = tk.TOP)
        label01 = tk.Label(frame3, text="踢球回放", height=1)
        label01.grid(row=0, column=0)
        rowNum = 0
        for i in range(len(self.detail["ball"])):
            rowNum += 1
            single = self.detail["ball"][i]
            
            j = 0
            for kick in single:
                color = getColor(kick[1])
                name = kick[0]
                label10 = tk.Label(frame3, text=name, height=1, fg=color)
                label10.grid(row=rowNum, column=j)
                j += 1
                
                text11 = kick[2]
                label11 = tk.Label(frame3, text=text11, height=1)
                label11.grid(row=rowNum, column=j)
                j += 1
                
                text11 = kick[3]
                color = "#000000"
                if text11 != "踢球":
                    color = "#ff0000"
                label11 = tk.Label(frame3, text=text11, height=1, fg=color)
                label11.grid(row=rowNum, column=j)
                j += 1
        
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

class YuanfeiReplayer(SpecificReplayer):

    def countFinal(self, nowTime):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        self.phase = 0

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        
        '''
            for line in ballDict:
                player1 = str(ballDict[line]["player1"])
                player2 = str(ballDict[line]["player2"])
                time1 = int(ballDict[line]["time1"])
                time2 = int(ballDict[line]["time2"])
                if ballDict[line]["status"] == 1:
                    playerBallDict[player1]["log"].append([time1, "%s手球犯规！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 2:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s手球犯规！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 3:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 5:
                    playerBallDict[player1]["log"].append([time1, "%s传球出界！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 6:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 7:
                    playerBallDict[player1]["log"].append([time1, "%s乌龙球！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 8:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门成功！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] += 1
                elif ballDict[line]["status"] == 9:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
            
            playerBallList = []
            for line in playerBallDict:
                if playerBallDict[line]["log"] != []:
                    playerBallDict[line]["log"].sort(key = lambda x:x[0])
                    ballActualLog = []
                    for t in playerBallDict[line]["log"]:
                        ballActualLog.append(t[1])
                    playerBallList.append([line, playerBallDict[line]["score"], ballActualLog])
            playerBallList.sort(key = lambda x:-x[1])
            scoreRank = 0
            highScore = 1
            for i in range(len(playerBallList)):
                scoreRank += 1
                if scoreRank <= 3 and playerBallList[i][1] > 0:
                    highScore = playerBallList[i][1]
                if scoreRank >= 4:
                    break
            for i in range(len(playerBallList)):
                id = playerBallList[i][0]
                if playerBallList[i][1] >= highScore:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         3,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：梅西" %playerBallList[i][1],
                                         playerBallList[i][2]])
                elif playerBallList[i][1] >= 0:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         0,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：正常" %playerBallList[i][1],
                                         playerBallList[i][2]])
                else:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         1,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：国足" %playerBallList[i][1],
                                         playerBallList[i][2]])
        '''
  
        phaseTime = [0, 0, 0, 0, 0]
        
        if self.phaseFinal[self.phaseStep] == 0:
            self.phaseFinal[self.phaseStep] = self.finalTime

        for i in range(1, 5):
            phaseTime[i] = (self.phaseFinal[i] - self.phaseStart[i]) / 1000
            if phaseTime[i] <= 0:
                phaseTime[i] = 1e+20
  
        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:

                self.dps[line][2] = self.buffCounter[line].sumTime() / 1000

                dps = int(self.dps[line][0] / self.battleTime)
                bossResult.append([self.namedict[line][0],
                                   self.occDetailList[line],
                                   dps, 
                                   0,
                                   self.dps[line][2], 
                                   int(self.dps[line][3] / phaseTime[1]), 
                                   int(self.dps[line][4] / phaseTime[2]),
                                   int(self.dps[line][5] / phaseTime[3]),
                                   int(self.dps[line][6] / phaseTime[4]),
                                   self.dps[line][7]
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        #print(self.dps)
        #for line in self.effectiveDPSList:
        #    print(line)
            
        ballList = []
        
        for line in self.ballDict:
            if self.ballDict[line]["kick"] != []:
                ballList.append({"ball": line, "kick": self.ballDict[line]["kick"]})
                
        ballList.sort(key=lambda x:x["kick"][0][2]) #按照第一次踢球时间排序
        
        for line in ballList:
            res = []
            for l in line["kick"]:
                kickStatus = "未知"
                if l[3] == 1:
                    kickStatus = "踢球"
                elif l[3] == 2:
                    kickStatus = "手球"
                elif l[3] == 3:
                    kickStatus = "出界"
                res.append([l[0], l[1], parseTime((l[2] - self.startTime)/1000), kickStatus])
        
            self.detail["ball"].append(res)

        #for line in self.detail["ball"]:
        #    print(line)
            
        #for line in self.detail["duotian"]:
        #    print(line)
                                 
        return self.effectiveDPSList, self.potList, self.detail

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
                        
                if item[7] == "24590":
                    self.shanTuiID = item[5]
                    self.shanTuiTime = int(item[2])
                        
                if item[7] == "24648":
                    self.shanTuiLog.append([int(item[2]), self.namedict[item[5]][0].strip('"'), self.occdict[item[5]][0]])
                    
                if self.shanTuiTime != 0 and int(item[2]) - self.shanTuiTime > 5000:
                    shanTuiVictims = ["受害者名单："]
                    numVictims = 0
                    for i in range(len(self.shanTuiLog)):
                        line = self.shanTuiLog[i]
                        numVictims += 1
                        shanTuiVictims.append(line[1])
                    if numVictims > 0:
                        self.potList.append([self.namedict[self.shanTuiID][0],
                                             self.occdict[self.shanTuiID][0],
                                             1,
                                             self.bossNamePrint,
                                             "%s闪腿害人：%d个" %(parseTime((int(item[2]) - self.startTime - 5000)/1000), numVictims),
                                             shanTuiVictims])
                    self.shanTuiLog = []
                    self.shanTuiTime = 0
            
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    for line in healRes:
                        if line in self.playerIDList:
                            self.dps[line][7] += healRes[line]
            
                if item[7] == "24655" and item[4] in self.ballDict and int(item[2]) - self.ballDict[item[4]]["lastHit"] > 500:  #球撞人
                
                    self.ballDict[item[4]]["lastHit"] = int(item[2])
                    self.ballDict[item[4]]["kick"].append([self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]], int(item[2]), 2])  #2代表撞球
                    
                elif item[7] == "25421" and item[4] in self.ballDict and int(item[2]) - self.ballDict[item[4]]["lastHit"] > 500: #球出界并爆炸
                    
                    self.ballDict[item[4]]["lastHit"] = int(item[2])
                    self.ballDict[item[4]]["kick"].append(["", "0", int(item[2]), 3]) #3代表爆炸
                    
                if item[7] == "24646": #堕天腿
                    if int(item[2]) - self.duotianTime > 500 and self.duotianNum in [4,5,6,7]:
                        self.duotianNum += 1
                    if self.duotianNum >= 5:
                        self.duotianTime = int(item[2])
                        duotianOrder = self.duotianNum-5
                        if item[5] not in self.detail["duotian"][-1][duotianOrder][0][0] and item[5] not in self.detail["duotian"][-1][duotianOrder][-1][0]:
                            self.detail["duotian"][-1][duotianOrder].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]]) 

                if item[7] == "24639": #凌空腿
                    if self.duotianNum != 0 and int(item[2]) - self.duotianTime > 30000:
                        self.duotianNum = 0
                        del self.detail["duotian"][-1]
                    if self.duotianNum == 0:
                        self.detail["duotian"].append([[], [], [], [], []])
                        self.detail["duotian"][-1][0].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        self.duotianNum += 1
                        self.duotianTime = int(item[2])
                    elif self.duotianNum in [1, 2, 3]:
                        self.detail["duotian"][-1][self.duotianNum].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        self.duotianNum += 1
                        self.duotianTime = int(item[2]) 
                        
            else:
            
                if item[4] in self.playerIDList:
                    if self.phase != 0:
                        self.dps[item[4]][0] += int(item[14])
                        if self.phaseStep in [1,2,3,4]:
                            self.dps[item[4]][2 + self.phaseStep] += int(item[14])
            
                if item[7] in ["25459", "24654"] and item[5] in self.ballDict and int(item[2]) - self.ballDict[item[5]]["lastHit"] > 500: #人踢到球
                
                    self.ballDict[item[5]]["lastHit"] = int(item[2])
                    self.ballDict[item[5]]["kick"].append([self.namedict[item[4]][0].strip('"'), self.occDetailList[item[4]], int(item[2]), 1]) #1代表踢球
                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if self.duotianNum >= 8 and int(item[2]) - 3000 > self.duotianTime: #结算
                for line in self.playerIDList:
                    leave = 1
                    for line2 in self.detail["duotian"][-1][0]:
                        if line2[0] == line:
                            leave = 0
                    for line2 in self.detail["duotian"][-1][1]:
                        if line2[0] == line:
                            leave = 0
                    if leave:
                        self.detail["duotian"][-1][4].append([line, self.namedict[line][0].strip('"'), self.occDetailList[line]])
                self.duotianNum = 0
                
            if item[6] in ["18205", "17699", "17694"]: #紧张、沉默、上天
                self.buffCounter[item[5]].setState(int(item[2]), int(item[10]))
                
            if item[6] == "17699":
                if int(item[10]) == 1:
                    self.criticalHealCounter[item[5]].active()
                elif int(item[10]) == 0:
                    self.criticalHealCounter[item[5]].unactive()       
                    
        elif item[3] == '8':

            if item[4] == '"呃啊...啊，这双腿...还是...大不如....从前了...."':
                self.phase = 0
                self.phaseFinal[self.phaseStep] = int(item[2])
                if self.phaseStep == 4 or self.mapDetail != "25人英雄达摩洞": #防止将自动刷新的战斗记录识别为通关
                    self.win = 1
                
            if "睁大你的眼睛！" in item[4] or "看看老子这招！" in item[4] or "来尝尝老子的气劲！" in item[4] or "能接下老子这招么？" in item[4]:
                if self.phase == 1:
                    self.phase = 2
                    self.phaseFinal[self.phaseStep] = int(item[2])
                    
            if item[4] == '"....."':
                if self.phase == 2:
                    self.phase = 1
                    self.phaseStep += 1
                    self.phaseStart[self.phaseStep] = int(item[2])
                
        elif item[3] == '3': #重伤记录
            pass
            
        elif item[3] == "10": #战斗状态变化
            if item[5] in self.ballDict and self.ballDict[item[5]]["appear"] == 0:
                self.ballDict[item[5]]["appear"] = int(item[2])

                    
        
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
        self.activeBoss = "猿飞"
        
        #猿飞数据格式：
        #4 被控时间; 5 P1DPS; 6 P2DPS; 7 P3DPS; 8 P4DPS; 9 关键治疗量
        #承伤 第X次 第Y组 点名+承伤
        #踢球 time: 发球时间; kick: ID，心法，时间，踢球状态
        
        self.dps = {}
        self.detail["boss"] = "猿飞"
        self.win = 0
        
        self.detail["ball"] = []
        
        self.phase = 1 #1与2代表常规与踢球阶段
        self.phaseStep = 1 #1、2、3、4代表第几个常规阶段
        
        self.phaseStart = [0, 0, 0, 0, 0]
        self.phaseFinal = [0, 0, 0, 0, 0]
        self.phaseStart[1] = self.startTime
        
        self.detail["duotian"] = []
        self.duotianNum = 0
        self.duotianTime = 0
        
        self.criticalHealCounter = {}
        self.buffCounter = {}
        
        self.shanTuiID = ""
        self.shanTuiTime = 0
        self.shanTuiLog = []
        
        self.playerBallDict = {}
        for line in self.playerIDList:
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.criticalHealCounter[line] = CriticalHealCounter()
            self.playerBallDict[line] = {"score": 0, "log": []}
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            
        self.ballDict = {}
        for line in self.namedict:
            if self.namedict[line][0].strip('"') == "横绝气劲":
                self.ballDict[line] = {"appear": 0, "kick": [], "lastHit": 0}
                #ballDict[line] = {"player1": 0, "player2": 0, "time1": 0, "time2": 0, "lastHit": 0, "status": 0}
        

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


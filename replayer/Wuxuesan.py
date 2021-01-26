# Created by moeheart at 1/24/2021
# 武雪散的定制复盘方法库。
# 武雪散是达摩洞3号首领，复盘主要集中在以下几个方面：
# （TODO 文档待补充）

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class WuXueSanWindow():
    '''
    武雪散的专有复盘窗口类。
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
        window.title('武雪散详细复盘')
        window.geometry('1000x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #4 被控时间; 5 停手DPS; 6 鬼门针1; 7 鬼门针2; 8 鬼门针3; 9 千丝乱技能数; 10 最后阶段DPS; 11 跳绳崴脚; 12 关键治疗量; 13 穿脊牵肌HPS
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
        ToolTip(label04, "受到影响无法正常输出的时间，以秒计，包括鬼门针、跳绳、穿脊牵肌推人。\n对于近战，在第一次穿脊牵肌推人后就会记为被控，而远程则是第二次。")
        label05 = tk.Label(frame1, text="停手DPS", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "在90%血量之前大团停手后，到血量判断前的DPS。\n这里会根据团队DPS详情，自动识别到停手的时间点。")
        label06 = tk.Label(frame1, text="鬼门针1", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "在第一个鬼门针阶段，对鬼门针的DPS。\nX标记表示这一次被点名。")
        label07 = tk.Label(frame1, text="鬼门针2", height=1)
        label07.grid(row=0, column=6)
        ToolTip(label07, "在第二个鬼门针阶段，对鬼门针的DPS。\nX标记表示这一次被点名。")
        label08 = tk.Label(frame1, text="鬼门针3", height=1)
        label08.grid(row=0, column=7)
        ToolTip(label08, "在第三个鬼门针阶段，对鬼门针的DPS。\nX标记表示这一次被点名。")
        label09 = tk.Label(frame1, text="千丝乱技能数", height=1)
        label09.grid(row=0, column=8)
        ToolTip(label09, "千丝乱阶段对武雪散施放的技能数量。\n这一项仅供参考，且不同门派心法的表现会有很大不同。")
        label10 = tk.Label(frame1, text="最后阶段DPS", height=1)
        label10.grid(row=0, column=9)
        ToolTip(label10, "千丝乱结束后，最终rush阶段的DPS。")
        label11 = tk.Label(frame1, text="跳绳崴脚", height=1)
        label11.grid(row=0, column=10)
        ToolTip(label11, "银丝千织阶段受到伤害的次数。")
        label12 = tk.Label(frame1, text="关键治疗量", height=1)
        label12.grid(row=0, column=11)
        ToolTip(label12, "对被鬼门针点名的玩家的治疗数值。\n减伤会被等效算在其中。")
        label13 = tk.Label(frame1, text="穿脊牵肌HPS", height=1)
        label13.grid(row=0, column=12)
        ToolTip(label13, "穿脊牵肌阶段的HPS。")
        
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
            label5 = tk.Label(frame1, text=int(self.effectiveDPSList[i][5]))
            label5.grid(row=i+1, column=4)
            
            text6 = int(self.effectiveDPSList[i][6])
            color6 = "#000000"
            if text6 == -1:
                color6 = "#ff0000"
                text6 = "X"
            label6 = tk.Label(frame1, text=text6, height=1, fg=color6)
            label6.grid(row=i+1, column=5)
            
            text7 = int(self.effectiveDPSList[i][7])
            color7 = "#000000"
            if text7 == -1:
                color7 = "#ff0000"
                text7 = "X"
            label7 = tk.Label(frame1, text=text7, height=1, fg=color7)
            label7.grid(row=i+1, column=6)
            
            text8 = int(self.effectiveDPSList[i][8])
            color8 = "#000000"
            if text8 == -1:
                color8 = "#ff0000"
                text8 = "X"
            label8 = tk.Label(frame1, text=text8, height=1, fg=color8)
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

class WuXueSanReplayer(SpecificReplayer):

    def countFinal(self, nowTime):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        self.phase = 0

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        
        stoppedTime = 1e+20
        if self.stoppedStart != 0 and self.stoppedFinal > self.stoppedStart:
            stoppedTime = self.stoppedFinal - self.stoppedStart
            self.detail["stopLast"] = stoppedTime
            
        gmzTime = [0, 0, 0]
        for i in range(0, 3):
            gmzTime[i] = self.gmzFinalTime[i] - self.gmzStartTime[i] + 1e-10
            
        P2Time = 1e-10
        if self.P2Final != 0:
            P2Time = self.P2Final - self.P2Start
            
        
        if self.cjjqFinal < self.cjjqStart:
            self.cjjqSumTime += self.finalTime - self.cjjqStart
        cjjqTime = self.cjjqSumTime
        
        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:

                self.dps[line][2] = self.buffCounter[line].sumTime() / 1000
                gmzDps = [0, 0, 0]
                for i in range(0, 3):
                    gmzDps[i] = self.dps[line][i+4] / gmzTime[i] * 1000
                    if gmzDps[i] < 0:
                        gmzDps[i] = -1

                dps = self.dps[line][0] / self.battleTime
                bossResult.append([self.namedict[line][0],
                                   self.occDetailList[line],
                                   dps, 
                                   0,
                                   self.dps[line][2], 
                                   self.dps[line][3] / stoppedTime * 1000, 
                                   gmzDps[0],
                                   gmzDps[1],
                                   gmzDps[2],
                                   self.dps[line][7],
                                   self.dps[line][8] / P2Time * 1000,
                                   self.dps[line][9],
                                   self.dps[line][10],
                                   self.dps[line][11] / cjjqTime * 1000,
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        #print(self.dps)
        #for line in self.effectiveDPSList:
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
            
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    for line in healRes:
                        if line in self.playerIDList:
                            self.dps[line][10] += healRes[line]
                        
                if item[11] != '0' and item[10] != '7': #非化解
                    if self.cjjqPhase:
                        self.dps[item[4]][11] += int(item[12])
            
                #根据击退次数判断控制时间
                if item[7] == "24503": #穿脊牵肌击退
                    self.cjjqCount[item[5]] += 1
                    if self.cjjqCount[item[5]] == 1 and self.occdict[item[5]][0] in ['1d', '3d', '4p', '8', '9', '10d', '21d', '23', '24', '25']: #所有近战门派
                        self.buffCounter[item[5]].setState(int(item[2]), 1)
                    elif self.cjjqCount[item[5]] == 2 and self.occdict[item[5]][0] in ['2d', '4m', '5p', '6d', '7p', '7m', '22d', '211']: #所有远程门派
                        self.buffCounter[item[5]].setState(int(item[2]), 1)
                        
                if item[7] == "24388": #银丝千织
                    self.dps[item[5]][9] += 1
                    
                if item[7] == "17514": #鬼门针保护
                    self.gmzProtectTime = int(item[2])
                
                if self.gmzPhase == 1 and int(item[2]) - self.gmzProtectTime > 2000:
                    self.gmzNum = 0
                    self.gmzPhase = 0
                    for line in self.gmzSet:
                        self.dps[line][self.gmzLabel] = -1
                    self.gmzFinalTime[self.gmzLabel - 4] = int(item[2])
                    for line in self.criticalHealCounter:
                        self.criticalHealCounter[line].unactive()
                        
            else:
            
                if not self.stoppedExist:
                    stopped = self.shift.checkItem(item)
                    if stopped:
                        self.stoppedCheck = 1
                        self.stoppedExist = 1
                        stopDpsDict = self.shift.calSetADps()
                        for line in stopDpsDict:
                            self.dps[line][3] += stopDpsDict[line]
                        self.stoppedStart = int(item[2])
                        self.detail["stop"] = int(item[2])
                        
                #战斗时间为47秒时，停手限制解除
                if int(item[2]) - self.startTime > 47000 and self.stoppedCheck:
                    self.stoppedCheck = 0
                    self.stoppedExist = 1
                    self.stoppedFinal = int(item[2])
                
                #计算DPS
                if item[4] in self.playerIDList:
                    if self.phase != 0:
                        self.dps[item[4]][0] += int(item[14])
                    if self.phase == 2:
                        self.dps[item[4]][8] += int(item[14])
                        
                    #处于停手状态
                    if self.stoppedCheck:
                        self.dps[item[4]][3] += int(item[14])
                    if self.gmzPhase and item[5] in self.namedict and self.namedict[item[5]][0] in ['"鬼门针"']:
                        self.dps[item[4]][self.gmzLabel] += int(item[14])
                    
                    #计算千丝乱技能个数
                    if self.qslPhase and item[5] in self.namedict and self.namedict[item[5]][0] in ['"武雪散"']:
                        self.dps[item[4]][7] += 1

                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return

            if item[6] in ["17514", "17602"]: #鬼门针，跳绳
                self.buffCounter[item[5]].setState(int(item[2]), int(item[10]))
                
            if item[6] == "17632" and int(item[10]) == 0: #穿脊牵肌消失
                self.buffCounter[item[5]].setState(int(item[2]), 0)
                self.cjjqPhase = 0
                self.cjjqFinal = int(item[2])
                self.cjjqSumTime += self.cjjqFinal - self.cjjqStart
                self.cjjqStart = self.cjjqFinal
                
            if item[6] == "17632" and int(item[10]) == 1: #穿脊牵肌出现
                self.cjjqPhase = 1
                self.cjjqStart = int(item[2])
                
            if item[6] == "17514":
                if int(item[10]) == 1: #获得鬼门针
                    if self.gmzPhase == 0:
                        self.gmzPhase = 1
                        self.gmzSet = []
                        self.gmzLabel += 1
                        if self.gmzLabel >= 7:
                            self.gmzPhase = 0
                            self.gmzNum = -999
                            return
                        self.gmzStartTime[self.gmzLabel - 4] = int(item[2])
                    self.gmzNum += 1
                    self.gmzSet.append(item[5])
                    self.criticalHealCounter[item[5]].active()
                    self.gmzProtectTime = int(item[2])
                
                elif int(item[10]) == 0: #鬼门针消失
                    self.gmzNum -= 1
                    if self.gmzPhase == 1 and self.gmzNum == 0:
                        self.gmzPhase = 0
                        for line in self.gmzSet:
                            self.dps[line][self.gmzLabel] = -1
                        self.gmzFinalTime[self.gmzLabel - 4] = int(item[2])
                    self.criticalHealCounter[item[5]].unactive()
                    
        elif item[3] == '8':
                
            if item[4] == '"出乎意料...你们竟然还未死绝，是我大意了。"':
                self.qslPhase = 1
                
            if item[4] == '"呃..."':
                self.qslPhase = 0
                self.phase = 2
                self.P2Start = int(item[2])

            if item[4] == '"想不到我武雪散竟亡于这……畜生道……可悲啊……"':
                self.phase = 0
                self.P2Final = int(item[2])
                self.win = 1
                
        elif item[3] == '3': #重伤记录
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
        self.activeBoss = "武雪散"
        
        #武雪散数据格式：
        #4 被控时间; 5 停手DPS; 6 鬼门针1; 7 鬼门针2; 8 鬼门针3; 9 千丝乱技能数; 10 最后阶段DPS; 11 跳绳崴脚; 12 关键治疗量; 13 穿脊牵肌HPS
        
        self.dps = {}
        self.detail["boss"] = "武雪散"
        self.win = 0
        
        self.phase = 1
        
        self.detail["stop"] = 0
        self.detail["stopLast"] = 0
        self.stoppedExist = 0
        self.stoppedCheck = 0
        self.stoppedStart = 0
        self.stoppedFinal = 0
        self.shift = DpsShiftWindow(self.playerIDList.keys(), 5, 5, 0.3, self.startTime)
        
        self.buffCounter = {}
        
        self.gmzNum = 0 #鬼门针个数
        self.gmzPhase = 0 #是否处于鬼门针阶段
        self.gmzLabel = 3 #鬼门针所属脚标，对应DPS数据格式
        self.gmzSet = [] #鬼门针被点名的ID
        self.gmzProtectTime = 0 #鬼门针伤害的时间，用于保护鬼门针消失不受丢失buff的影响
        self.gmzStartTime = [0, 0, 0, 0]
        self.gmzFinalTime = [0, 0, 0, 0]
        
        self.qslPhase = 0 #是否处于千丝乱阶段
        self.P2Start = 0
        self.P2Final = 0
        
        self.cjjqPhase = 0 #是否处于穿脊牵肌阶段
        self.cjjqCount = {} #穿脊牵肌被推次数
        self.cjjqStart = 0
        self.cjjqFinal = 0
        self.cjjqSumTime = 1e-10
        
        self.criticalHealCounter = {}
        
        for line in self.playerIDList:
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.buffCounter[line] = BuffCounter(0, self.startTime, self.finalTime)
            self.cjjqCount[line] = 0
            self.criticalHealCounter[line] = CriticalHealCounter()

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


# Created by moeheart at 03/29/2021
# 姜集苦的定制复盘方法库。
# 姜集苦是白帝江关4号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *
        
class JiangJikuWindow():
    '''
    姜集苦的专有复盘窗口类。
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
        window.title('姜集苦详细复盘')
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
        tb.AppendHeader("P1DPS", "70%%血量之前阶段的DPS。\nP1时长：%s"%parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "70%%血量之后阶段的DPS。这部分DPS同样包括易伤阶段。\nP2时长：%s"%parseTime(self.detail["P2Time"]))
        tb.AppendHeader("易伤DPS", "易伤阶段的DPS，指走圈结束的20秒易伤时间中产生的DPS。\n时长：%s"%parseTime(self.detail["P3Time"]))
        tb.AppendHeader("关键治疗", "对走圈阶段时站桩T的治疗。减伤会被等效。")
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
            
            color10 = "#000000"
            if self.effectiveDPSList[i][10] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color10 = "#00ff00"
            tb.AppendContext(int(self.effectiveDPSList[i][10]), color = color10)
            
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

class JiangJikuReplayer(SpecificReplayer):

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
        self.phaseEnd[2] = self.finalTime
        if self.phaseEnd[3] > self.finalTime:
            self.phaseEnd[3] = self.finalTime
        self.phaseTime = [1e+20] * 4
        for i in range(1, 4):
            if self.phaseStart[i] != 0 and self.phaseEnd[i] != 0:
                self.phaseTime[i] = int((self.phaseEnd[i] - self.phaseStart[i]) / 1000)
                
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
                                   int(line[9] / self.phaseTime[3]),
                                   line[10]
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

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        
        if self.yiShang and int(item[2]) > self.phaseEnd[3]:
            self.yiShang = 0
        
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                        
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    if self.zouQuan:
                        for line in healRes:
                            if line in self.playerIDList:
                                self.stat[line][10] += healRes[line]

            else:
            
                if item[4] in self.playerIDList:
                    self.stat[item[4]][2] += int(item[14])
                    
                    if self.phase == 1:
                        self.stat[item[4]][7] += int(item[14])
                    elif self.phase == 2:
                        self.stat[item[4]][8] += int(item[14])
                    if self.yiShang:
                        self.stat[item[4]][9] += int(item[14])
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                
            if item[6] == "19367":  # 速符
                if int(item[10]) == 1:
                    self.criticalHealCounter[item[5]].active()
                    self.criticalHealCounter[item[5]].setCriticalTime(-1)
                elif int(item[10]) == 0:
                    self.criticalHealCounter[item[5]].unactive()
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
            if item[4] in ['"就让你们见识下这金符的威力！"']:
                self.phase = 2
                self.phaseEnd[1] = int(item[2])
                self.phaseStart[2] = int(item[2])
                
            if item[4] in ['"唔...岂有此理！"']:
                self.yiShang = 1
                self.phaseStart[3] = int(item[2])
                self.phaseEnd[3] = int(item[2]) + 20000
                self.zouQuan = 0
                
            if item[4] in ['"黑云密布，电火奔星。天令一下，速震速轰！"']:
                if self.phase == 2:
                    self.zouQuan = 1
                
        elif item[3] == '3': #重伤记录
            if item[6] == '"姜集苦"':
                self.win = 1
                
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
        self.activeBoss = "姜集苦"
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #姜集苦数据格式：
        #7 P1DPS, 8 P2DPS, 9 爆发DPS, 10 关键治疗量
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "姜集苦"
        self.win = 0
        self.phase = 1
        self.yiShang = 0
        self.zouQuan = 0
        
        self.criticalHealCounter = {}
        
        self.phaseStart = [0, 0, 0, 0]
        self.phaseEnd = [0, 0, 0, 0]
        
        for line in self.playerIDList:
            self.stat[line] = [self.namedict[line][0].strip('"'), self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0]
            self.hps[line] = 0
            self.criticalHealCounter[line] = CriticalHealCounter()


    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


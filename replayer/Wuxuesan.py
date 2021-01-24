# Created by moeheart at 1/24/2021
# 武雪散的定制复盘方法库。
# 武雪散是达摩洞3号首领，复盘主要集中在以下几个方面：
# （TODO 文档待补充）

from replayer.Base import *
from replayer.utils import CriticalHealCounter
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
        window.title('宓桃详细复盘')
        window.geometry('1000x800')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #4 被控时间; 5 易伤层数; 6 常规阶段dps; 7 小怪阶段dps; 8 引导次数; 9 小怪阶段hps; 10 关键治疗; 11 有效驱散次数
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
        ToolTip(label04, "受到影响无法正常输出的时间，以秒计，包括魅惑、引导、嗜血缥缈。")
        label05 = tk.Label(frame1, text="易伤", height=1)
        label05.grid(row=0, column=4)
        ToolTip(label05, "第一次进入引导阶段时的易伤层数。")
        label06 = tk.Label(frame1, text="P1DPS", height=1)
        label06.grid(row=0, column=5)
        ToolTip(label06, "对BOSS的DPS。时间按常规阶段计算。")
        label07 = tk.Label(frame1, text="P2DPS", height=1)
        label07.grid(row=0, column=6)
        ToolTip(label07, "对小怪的DPS。时间按引导阶段计算。")
        label08 = tk.Label(frame1, text="引导", height=1)
        label08.grid(row=0, column=7)
        ToolTip(label08, "完成引导的次数。")
        label09 = tk.Label(frame1, text="P2HPS", height=1)
        label09.grid(row=0, column=8)
        ToolTip(label09, "引导阶段的HPS。时间按引导阶段计算。")
        label10 = tk.Label(frame1, text="关键治疗", height=1)
        label10.grid(row=0, column=9)
        ToolTip(label10, "对处于引导状态的玩家的治疗数值。\n减伤会被等效算在其中。")
        label11 = tk.Label(frame1, text="有效驱散次数", height=1)
        label11.grid(row=0, column=10)
        ToolTip(label11, "有效驱散的次数。\n计算[虐恋]与[魅惑]。")
        
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
            color5 = "#000000"
            if self.effectiveDPSList[i][5] >= 2:
                color5 = "#ff0000"
            label5 = tk.Label(frame1, text=int(self.effectiveDPSList[i][5]), height=1, fg=color5)
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
            
        frame2 = tk.Frame(window)
        frame2.pack()
        label01 = tk.Label(frame2, text="引导流水", height=1)
        label01.grid(row=0, column=0)
        rowNum = 0
        for i in range(len(self.detail["lead"])):
            rowNum += 1
            single = self.detail["lead"][i]
        
            text10 = single[4]
            label10 = tk.Label(frame2, text=text10, height=1)
            label10.grid(row=rowNum, column=0)
        
            text11 = "驱散"
            label11 = tk.Label(frame2, text=text11, height=1)
            label11.grid(row=rowNum, column=1)
            color = getColor(single[3])
            name = single[2]
            label12 = tk.Label(frame2, text=name, height=1, fg=color)
            label12.grid(row=rowNum, column=2)
            
            text13 = "引导"
            label13 = tk.Label(frame2, text=text13, height=1)
            label13.grid(row=rowNum, column=3)
            color = getColor(single[1])
            name = single[0]
            label14 = tk.Label(frame2, text=name, height=1, fg=color)
            label14.grid(row=rowNum, column=4)


        
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
        
        #4 被控时间; 5 易伤层数; 6 常规阶段dps; 7 小怪阶段dps; 8 引导次数; 9 小怪阶段hps; 10 关键治疗; 11 有效驱散次数
        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:
            
                self.dps[line][2] = self.buffCounter[line].sumTime() / 1000
            
                dps = self.dps[line][0] / self.battleTime
                bossResult.append([self.namedict[line][0],
                                   self.occDetailList[line],
                                   dps, 
                                   0, 
                                   self.dps[line][2], 
                                   self.dps[line][3], 
                                   self.dps[line][4] / self.P1SumTime * 1000, 
                                   self.dps[line][5] / self.P2SumTime * 1000, 
                                   self.dps[line][6], 
                                   self.dps[line][7] / self.P2SumTime * 1000, 
                                   self.dps[line][8], 
                                   self.dps[line][9], 
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
                pass
            else:
                pass
                    
                #计算DPS
                if item[4] in self.playerIDList:
                    self.dps[item[4]][0] += int(item[14])
                    if self.phase == 1:
                        self.dps[item[4]][4] += int(item[14])
                    elif self.phase == 2:
                        self.dps[item[4]][5] += int(item[14])
                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return

            pass
                    
        elif item[3] == '8':
        
            if item[4] == '"人多的时候更有乐趣，大家一起来嘛~"':
                pass

            if item[4] == '"想不到我武雪散竟亡于这……畜生道……可悲啊……"':
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
        
        #宓桃数据格式：
        #4 被控时间; 5 易伤层数; 6 常规阶段dps; 7 小怪阶段dps; 8 引导次数; 9 小怪阶段hps; 10 关键治疗; 11 有效驱散次数
        #引导：引导ID，驱散ID
        
        self.dps = {}
        self.detail["boss"] = "武雪散"
        self.win = 0
        
        for line in self.playerIDList:
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


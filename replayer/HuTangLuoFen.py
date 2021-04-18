# Created by moeheart at 03/29/2021
# 胡汤&罗芬的定制复盘方法库。
# 胡汤&罗芬是白帝江关1号首领，复盘主要集中在以下几个方面：
# (TODO)

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class HuTangLuoFenWindow():
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
            label7 = tk.Label(frame1, text=int(self.effectiveDPSList[i][7]), height=1)
            label7.grid(row=i+1, column=6)
            label8 = tk.Label(frame1, text=int(self.effectiveDPSList[i][8]), height=1)
            label8.grid(row=i+1, column=7)
            
            color = "#000000"
            if int(self.effectiveDPSList[i][9]) == 0:
                color = ConvertRgbToStr((160, 160, 160))
            else:
                n = (int(self.effectiveDPSList[i][9]) - 1) * 12
                color = ConvertRgbToStr((n, n, n))
            label9 = tk.Label(frame1, text=int(self.effectiveDPSList[i][9]), height=1, fg=color)
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
            
            color = "#000000"
            if self.effectiveDPSList[i][15] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color = "#00ff00"
            label15 = tk.Label(frame1, text=int(self.effectiveDPSList[i][15]), height=1, fg=color)
            label15.grid(row=i+1, column=14)
            
            color = "#000000"
            if self.effectiveDPSList[i][16] > 0 and getOccType(self.effectiveDPSList[i][1]) == "healer":
                color = "#00ff00"
            label16 = tk.Label(frame1, text=int(self.effectiveDPSList[i][16]), height=1, fg=color)
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
                color = "#000000"
                if text12 == "爆杀":
                    color = "#ff0000"
                elif text12 == "留痕":
                    color = "#0000ff"
                label12 = tk.Label(frame2, text=text12, height=1, fg=color)
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

class HuTangLuoFenReplayer(SpecificReplayer):

    def countFinal(self, nowTime):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        pass

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:
                
                if getOccType(self.occDetailList[line]) == "healer":
                    self.dps[line][1] = int(self.hps[line] / self.battleTime)

                dps = int(self.dps[line][0] / self.battleTime)
                bossResult.append([self.namedict[line][0].strip('"'),
                                   self.occDetailList[line],
                                   dps, 
                                   self.dps[line][1],
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
        
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                    
            else:
            
                if item[4] in self.playerIDList:
                    self.dps[item[4]][0] += int(item[14])
     
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
            if item[4] in ['"喝啊……看！这疤痕，就是俺的忠诚！"']:
                self.phase = 2
                
        elif item[3] == '3': #重伤记录
            if item[6] == '"罗芬"':
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
        self.activeBoss = "胡汤&罗芬"
        
        #海荼数据格式：
        #(TODO)待英雄实装后更新
        
        self.dps = {}
        self.hps = {}
        self.detail["boss"] = "胡汤&罗芬"
        self.win = 0
        
        for line in self.playerIDList:
            self.dps[line] = [0, 0]
            self.hps[line] = 0

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


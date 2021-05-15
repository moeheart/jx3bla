# Created by moeheart at 03/29/2021
# 胡汤&罗芬的定制复盘方法库。
# 胡汤&罗芬是白帝江关1号首领，复盘主要集中在以下几个方面：
# 三种承伤的次数，与可能出现问题时的分锅。

from replayer.Base import *
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from Functions import *
        
class HuTangLuoFenWindow():
    '''
    胡汤&罗芬的专有复盘窗口类。
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
        window.title('胡汤&罗芬详细复盘')
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
        tb.AppendHeader("利爪承伤", "参与利爪承伤（面向）的次数。")
        tb.AppendHeader("面粉承伤", "参与面粉承伤（小圈）的次数。")
        tb.AppendHeader("手劲承伤", "参与手劲承伤（点名）的次数。")
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
            
            tb.EndOfLine()
            
        frame2 = tk.Frame(window)
        frame2.pack()
        
        tb = TableConstructor(frame2)
        
        tb.AppendHeader("承伤失败复盘", "")
        tb.EndOfLine()
        
        for line in self.detail["chengshangFail"]:
            tb.AppendContext(line["description"])
            tb.AppendContext(line["time"])
            for player in line["player"]:
                name = player[0]
                color = getColor(player[1])
                tb.AppendContext(name, color=color)
            tb.EndOfLine()
            
            tb.AppendContext("")
            tb.AppendContext("推测接锅者")
            if line["fail"] == []:
                tb.AppendContext("未知")
            else:
                for player in line["fail"]:
                    name = player[0]
                    color = getColor(player[1])
                    tb.AppendContext(name, color=color)
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
                                   line[7],
                                   line[8],
                                   line[9], 
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
        
        if self.chengShang[0]["num"] > 0 and int(item[2]) - self.chengShang[0]["time"] > 500:
            if self.chengShang[0]["num"] <= 8 and self.chengShang[0]["num"] != 1:
                tmp = {}
                res = {"description": "利爪承伤失败", "time": parseTime((self.chengShang[0]["time"] - self.startTime)/1000), "player": [], "fail": []}
                for line in self.chengShang[0]["player"]:
                    res["player"].append([line[1], line[2]])
                    tmp[line[0]] = 0
                for line in self.liZhuaList:
                    if self.liZhuaList[line] == self.liZhuaOrder and line not in tmp:
                        res["fail"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]])
                self.detail["chengshangFail"].append(res)
            self.chengShang[0] = {"time": 0, "num": 0, "player": []}
            self.lastLiZhuaTime = int(item[2])
        
        if self.chengShang[1]["num"] > 0 and int(item[2]) - self.chengShang[1]["time"] > 4000:
            if self.mianfenFailFlag == 1:
                res = {"description": "面粉承伤失败", "time": parseTime((self.chengShang[1]["time"] - self.startTime)/1000), "player": [], "fail": []}
                for line in self.chengShang[1]["player"]:
                    res["player"].append([line[1], line[2]])
                    tmp[line[0]] = 0
                for line in self.mianFenList:
                    if self.mianFenList[line] == self.mianFenOrder and line not in tmp:
                        res["fail"].append([self.namedict[line][0].strip('"'), self.occDetailList[line]])
                self.detail["chengshangFail"].append(res)
            self.chengShang[1] = {"time": 0, "num": 0, "player": []}
            self.mianfenFailFlag = 0
            self.mianFenOrder = 0
            
        if self.chengShang[2]["num"] > 0 and int(item[2]) - self.chengShang[2]["time"] > 200:
            if self.chengShang[2]["num"] <= 3:
                res = {"description": "手劲承伤失败", "time": parseTime((self.chengShang[2]["time"] - self.startTime)/1000), "player": [], "fail": []}
                for line in self.chengShang[2]["player"]:
                    res["player"].append([line[1], line[2]])
                self.detail["chengshangFail"].append(res)
            self.chengShang[2] = {"time": 0, "num": 0, "player": []}
        
        if item[3] == '1':  # 技能

            if self.occdict[item[5]][0] != '0':
            
                if item[11] != '0' and item[10] != '7': #非化解
                    if item[4] in self.playerIDList:
                        self.hps[item[4]] += int(item[12])
                        
                if '5' not in item[15]:
                    if item[7] == "26199":  # 利爪承伤，用0代表
                        self.stat[item[5]][7] += 1
                        if self.chengShang[0]["time"] == 0:
                            if self.liZhuaOrder == 0:
                                self.liZhuaOrder = 1
                            elif int(item[2]) - self.lastLiZhuaTime < 30000:
                                self.liZhuaOrder = 3 - self.liZhuaOrder
                            else:
                                self.liZhuaOrder = 1
                        self.liZhuaList[item[5]] = self.liZhuaOrder
                        self.chengShang[0]["time"] = int(item[2])
                        self.chengShang[0]["num"] += 1
                        self.chengShang[0]["player"].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        
                    if item[7] == "26350":  # 面粉承伤，用1代表
                        self.stat[item[5]][8] += 1
                        if int(item[2]) - self.chengShang[1]["time"] > 500:
                            self.mianFenOrder += 1
                        self.mianFenList[item[5]] = self.mianFenOrder
                        self.chengShang[1]["time"] = int(item[2])
                        self.chengShang[1]["num"] += 1
                        self.chengShang[1]["player"].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        
                    if item[7] == "26238":  # 手劲承伤，用2代表
                        self.stat[item[5]][9] += 1
                        self.chengShang[2]["time"] = int(item[2])
                        self.chengShang[2]["num"] += 1
                        self.chengShang[2]["player"].append([item[5], self.namedict[item[5]][0].strip('"'), self.occDetailList[item[5]]])
                        
                    if item[7] == "26563":  # 震荡
                        if int(item[2]) - self.chengShang[1]["time"] > 500:
                            self.mianFenOrder += 1
                        self.chengShang[1]["time"] = int(item[2])
                        self.mianfenFailFlag = self.mianFenOrder
                    
            else:
            
                if item[4] in self.playerIDList:
                    self.stat[item[4]][2] += int(item[14])
     
                
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
                    
        elif item[3] == '8':
        
            if len(item) <= 4:
                return
                
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
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        #胡汤&罗芬数据格式：
        #7 利爪承伤, 8 面粉承伤, 9 手劲承伤
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = "胡汤&罗芬"
        self.win = 0
        
        self.mianfenFailFlag = 0
        self.detail["chengshangFail"] = []
        self.chengShang = [{"time": 0, "num": 0, "player": []}] * 3
        self.liZhuaList = {}
        self.liZhuaOrder = 0
        self.mianFenList = {}
        self.mianFenOrder = 0
        self.lastLiZhuaTime = 0
        
        for line in self.playerIDList:
            self.stat[line] = [self.namedict[line][0].strip('"'), self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0]
            self.hps[line] = 0

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)


# Created by moeheart at 1/11/2021
# 宓桃的定制复盘方法库。
# 余晖是达摩洞2号首领，复盘主要集中在以下几个方面：
# 文档待补充

from replayer.Base import *

class PurgeCounter():
    '''
    检测特定角色对于特定buff的驱散类。
    '''
    
    def recordPurge(self, item):
        '''
        记录对应的item中的驱散技能。
        这里的item必须经过检验，确定是技能类别。
        '''
        if item[7] in self.purgeSkill:
            self.player = item[4]
            self.time = int(item[2])
    
    def checkPurge(self, item):
        '''
        检测对应的item是否是监控buff消失事件，若是则结算，并返回
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if item[6] in self.targetBuff and int(item[10]) == 0:
            #以500毫秒为界限，避免数据丢失导致错乱
            if int(item[2]) - self.time < 500:
                return self.player
        return "0" 
    
    def __init__(self, buffList):
        self.targetBuff = buffList
        self.purgeSkill = ["133", #清风垂露
                           "2654", #利针
                           "138", #提针
                           "566", #跳珠憾玉
                           "3052", #蝶鸾子技能
                           "14169", #一指回鸾
                          ]
        self.player = "0"
        self.time = 0
        
class CriticalHealCounter():
    '''
    检测特定角色的关键治疗量类。
    除了传统的治疗量，还会同时记录减伤所等效的治疗量。
    '''
    
    def setCriticalTime(self, time):
        '''
        设定关键治疗的过期时间。
        '''
        if time > self.expireTime:
            self.expireTime = time
    
    def recordHeal(self, item):
        '''
        记录对应的item中的治疗量。
        这里的item必须经过检验，确定是技能类别。
        '''
        if int(item[2]) > self.expireTime:
            self.unactive()
        
        if not self.activeNum:
            return {}
            
        result = {}
        heal = int(item[12])
        damage = int(item[14])
        if heal > 0:
            result[item[4]] = heal
        
        if damage > 0:
            deductRate = 0
            for line in self.deductStatus:
                if self.deductStatus[line] != "0":
                    deductRate += self.deductDict[line]
            #若减伤系数总和大于1，则跳过处理
            if deductRate < 1:
                originDamage = damage / (1 - deductRate)
                for line in self.deductStatus:
                    if self.deductStatus[line] != "0":
                        if self.deductStatus[line] not in result:
                            result[self.deductStatus[line]] = 0
                        result[self.deductStatus[line]] += originDamage * self.deductDict[line]
                        
        return result
        
    def checkDeduct(self, item):
        '''
        记录对应的item中，减伤的获得或消失。
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if item[6] in self.deductDict:
            if int(item[10]) > 0:
                #添加减伤
                self.deductStatus[item[6]] = item[4]
            else:
                #移除减伤
                self.deductStatus[item[6]] = "0"
        
    def unactive(self):
        '''
        关闭计数。
        '''
        self.activeNum = 0
        
    def active(self):
        '''
        开启计数。
        '''
        self.activeNum = 1
    
    def __init__(self):
        #仅列举大部分治疗心法给队友的减伤。
        self.deductDict = {"9336": 0.3, #寒梅
                           "9337": 0.3, #寒梅
                           "6636": 0.45, #圣手织天
                           "122": 0.45, #春泥护花
                           "6264": 0.6, #南柯
                           "9933": 0.3, #折叶
                           "684": 0.4, #风袖（天地）
                          }
                          
        self.deductStatus = {}
        
        self.activeNum = 0
        self.expireTime = 0
        
class MiTaoWindow():
    '''
    宓桃的专有复盘窗口类。
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

class MitaoReplayer(SpecificReplayer):

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        for id in self.leadDict:
            timeList = []
            for row in self.leadDict[id]:
                timeList.append(parseTime((row - self.startTime) / 1000))
            self.potList.append([self.namedict[id][0],
                                 self.occdict[id][0],
                                 3,
                                 self.bossNamePrint,
                                 "完成引导，次数：%d" %len(timeList),
                                 timeList])
                                 
        bossResult = []
        for line in self.playerIDList:
            if line in self.dps:
                dps = self.dps[line][0] / self.battleTime
                bossResult.append([self.namedict[line][0],
                                   self.occDetailList[line],
                                   dps
                                   ])
        bossResult.sort(key = lambda x:-x[2])
        self.effectiveDPSList = bossResult
        
        #for line in self.dps:
        #    print(self.namedict[line][0], self.dps[line])
                                 
        return self.effectiveDPSList, self.potList, self.detail

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        if item[3] == '1':  # 技能
        

            if self.occdict[item[5]][0] != '0':
                self.purgeCounter[item[5]].recordPurge(item)
                
                #检测关键治疗
                healRes = self.criticalHealCounter[item[5]].recordHeal(item)
                if healRes != {}:
                    for line in healRes:
                        self.dps[line][7] += healRes[line] 
                    #print(int(item[2]) - self.startTime, healRes, self.namedict[item[5]][0], self.criticalHealCounter[item[5]].activeNum)
                
            else:
                #开始引导的判定
                if item[7] in ["24704", "24705"]:
                    self.criticalHealCounter[item[4]].active()
                    self.criticalHealCounter[item[4]].setCriticalTime(int(item[2]) + 8000) #8秒后解除
                        
        elif item[3] == '5': #气劲
            if self.occdict[item[5]][0] == '0':
                return
            
            self.criticalHealCounter[item[5]].checkDeduct(item)
                
            purgeRes = self.purgeCounter[item[5]].checkPurge(item)
            if purgeRes != "0":
                #有效驱散计数
                self.dps[purgeRes][8] += 1
                #name = self.namedict[purgeRes][0]
                #print(name, item[2])
                
            if item[6] in ["17767", "17919"] and int(item[10]) > 0:
                self.criticalHealCounter[item[5]].active()
                self.criticalHealCounter[item[5]].setCriticalTime(int(item[2]) + 3000) #3秒后解除
                    
            if item[6] in ["17768", "17769"] and int(item[10]) > 0:
                self.criticalHealCounter[item[5]].active()
                self.criticalHealCounter[item[5]].setCriticalTime(int(item[2]) + 10000) #10秒后解除
                
            if item[5] in self.dizzyDict and self.dizzyDict[item[5]] != [] and self.dizzyDict[item[5]][0][0] <= int(item[2]):
                lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                self.potList.append([self.namedict[item[5]][0],
                                     self.occDetailList[item[5]],
                                     0,
                                     self.bossNamePrint,
                                     "%s进迷雾被魅惑" % lockTime,
                                     ["会计算因引导而被魅惑的情况"]])
                del self.dizzyDict[item[5]][0]
                    
        elif item[3] == '8':

            if item[4] == '"能和妾身玩这么久的人你们还是第一个，不过妾身一心只惦记着小将军……"':
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
        self.activeBoss = "宓桃"
        
        #宓桃数据格式：
        #4 易伤层数; 5 常规阶段dps; 6 小怪阶段dps; 7 引导次数; 8 小怪阶段hps; 9 关键治疗; 10 有效驱散次数
        #
        
        self.dps = {}
        self.detail["boss"] = "宓桃"
        
        self.purgeCounter = {}
        self.criticalHealCounter = {}
        for line in self.playerIDList:
            self.purgeCounter[line] = PurgeCounter(["17760", "17767", "17919"])
            self.criticalHealCounter[line] = CriticalHealCounter()
            self.dps[line] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint, dizzyDict, leadDict):
        '''
        对类本身进行初始化。
        '''
        super().__init__(playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.dizzyDict = dizzyDict
        self.leadDict = leadDict


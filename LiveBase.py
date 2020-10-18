# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time
import tkinter as tk
from win10toast import ToastNotifier

from ActorReplay import ActorStatGenerator

class SingleBossWindow():
        
    def getColor(self, occ):
        if occ[-1] in ['d', 't', 'h', 'p', 'm']:
            occ = occ[:-1]
        colorDict = {"0": (0, 0, 0), 
                     "1": (210, 180, 0),#少林
                     "2": (127, 31, 223),#万花
                     "4": (56, 175, 255),#纯阳
                     "5": (255, 127, 255),#七秀
                     "3": (160, 0, 0),#天策
                     "8": (255, 255, 0),#藏剑
                     "9": (205, 133, 63),#丐帮
                     "10": (253, 84, 0),#明教
                     "6": (63, 31, 159),#五毒
                     "7": (0, 133, 144),#唐门
                     "21": (180, 60, 0),#苍云
                     "22": (100, 250, 180),#长歌
                     "23": (71, 73, 166),#霸刀
                     "24": (195, 171, 227),#蓬莱
                     "25": (161, 9, 34)#凌雪
                    }
        res = (0, 0, 0)
        if occ in colorDict:
            res = colorDict[occ]
        return "#%s%s%s"%(str(hex(res[0]))[-2:].replace('x', '0'), 
                          str(hex(res[1]))[-2:].replace('x', '0'),
                          str(hex(res[2]))[-2:].replace('x', '0'))
        
    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"
            
    def getPot(self, tmp, num):
        '''
        分锅结果变化的处理函数。
        params
        - tmp 记录编号
        - num 锅数
        '''
        self.scoreList[tmp] += num
        scoreStr = ""
        scoreColor = "#000000"
        if self.scoreList[tmp] > 0:
            scoreStr = "+%d"%self.scoreList[tmp]
            scoreColor = "#007700"
        elif self.scoreList[tmp] < 0:
            scoreStr = "%d"%self.scoreList[tmp]
            scoreColor = "#ff0000"
        self.scoreLabels[tmp].config(text=scoreStr, fg=scoreColor)
        
    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''
        self.potListScore = []
        for i in range(len(self.potList)):
            self.potListScore.append(self.potList[i] + [self.scoreList[i]])
        print(self.potListScore)
        self.analyser.addResult(self.potListScore)
        self.window.destroy()

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('战斗复盘')
        window.geometry('600x700')
        
        numPot = len(self.potList)
        
        canvas=tk.Canvas(window,width=550,height=500,scrollregion=(0,0,530,numPot*30)) #创建canvas
        canvas.place(x = 25, y = 25) #放置canvas的位置
        frame=tk.Frame(canvas) #把frame放在canvas里
        frame.place(width=530, height=500) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas,orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x = 530,width=20,height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set) #设置  
        canvas.create_window((265,numPot*15), window=frame)  #create_window
        
        self.scoreLabels = []
        self.scoreList = []
        
        for i in range(numPot):
            line = self.potList[i]
            name = line[0].strip('"')
            occ = line[1]
            color = self.getColor(occ)
            nameLabel = tk.Label(frame, text=name, width = 13, height=1, fg=color)
            nameLabel.grid(row=i, column=0)
            pot = line[4]
            color = self.getPotColor(line[2])
            potLabel = tk.Label(frame, text=pot, height=1, fg=color)
            potLabel.grid(row=i, column=1)
            
            scoreLabel = tk.Label(frame, text="", width=5, height=1, font=("Arial", 12, "bold"))
            scoreLabel.grid(row=i, column=2)
            self.scoreLabels.append(scoreLabel)
            
            tmp = i
            button1 = tk.Button(frame, text='接锅', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, -1), bg='#ffcccc')
            button1.grid(row=i, column=3)
            button2 = tk.Button(frame, text='领赏', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, 1), bg='#ccffcc')
            button2.grid(row=i, column=4)
            
            self.scoreList.append(0)
            
        buttonFinal = tk.Button(window, text='分锅完成', width=10, height=1, command=self.final)
        buttonFinal.place(x = 250, y = 540)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def addPotList(self, potList):
        self.potList = potList

    def __init__(self, analyser):
        self.analyser = analyser

class LiveActorStatGenerator(ActorStatGenerator):
    
    def __init__(self, filename, path="", myname="", failThreshold=0, battleDate="", mask=0, dpsThreshold={}):
        super().__init__(filename, path, rawdata={}, failThreshold=failThreshold, 
            battleDate=battleDate, mask=mask, dpsThreshold=dpsThreshold)

class LiveActorAnalysis():

    def getPlayer(self):
        '''
        从结果记录中提取所有ID与门派，按门派顺序排序
        return
        - playerListSort 排好序的ID列表
        '''
        player = {}
        for line in self.potListScore:
            if line[0] not in player:
                occ = line[1]
                if occ[-1] in ['d', 't', 'h', 'p', 'm']:
                    occ = occ[:-1]
                player[line[0]] = int(occ)
        playerList = []
        for line in player:
            playerList.append([line, player[line]])
        playerList.sort(key = lambda x:x[1])
        playerListSort = []
        for line in playerList:
            playerListSort.append(line[0])
        return playerListSort

    def getPlayerPotList(self):
        playerPot = {}
        for line in self.potListScore:
            if line[0] not in playerPot:
                playerPot[line[0]] = {"occ": line[1], "numPositive": 0, "numNegative": 0, "pot": []}
            playerPot[line[0]]["pot"].append([line[1:]])
            if line[-1] > 0:
                playerPot[line[0]]["numPositive"] += line[-1]
            elif line[-1] < 0:
                playerPot[line[0]]["numNegative"] += line[-1]
        return playerPot

    def addResult(self, potListScore):
        self.potListScore.extend(potListScore)
    
    def __init__(self):
        self.potListScore = []

class LiveListener():

    def getNewBattleLog(self, basepath, lastFile):
        '''
        params
        - basepath: 监控的路径
        - lastFile: 新增的文件，通常是刚刚完成的战斗复盘
        '''
        battleDate = '-'.join(lastFile.split('-')[0:3])
        liveGenerator = LiveActorStatGenerator([lastFile, 0, 1], basepath, failThreshold=self.config.failThreshold, 
                battleDate=battleDate, mask=self.config.mask, dpsThreshold=self.dpsThreshold)
        liveGenerator.firstStageAnalysis()
        liveGenerator.secondStageAnalysis()
        
        window = SingleBossWindow(self.analyser)
        window.addPotList(liveGenerator.potList)
        window.start()
        
        toaster = ToastNotifier()
        toaster.show_toast("分锅结果已生成", "[%s]的战斗复盘已经解析完毕，请打开结果界面分锅。"%liveGenerator.bossname)
        

    def listenPath(self, basepath):
        '''
        开始监控对应的路径。
        params
        - basepath: 监控的路径
        '''
        filelist = os.listdir(basepath)
        dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
        if dataList != []:
            newestFile = dataList[-1]
        else:
            newestFile = ""
        while(True):
            time.sleep(3)
            filelist = os.listdir(basepath)
            dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
            if dataList != []:
                lastFile = dataList[-1]
            else:
                lastFile = ""
            if lastFile != newestFile:# or True:  #调试入口
                newestFile = lastFile
                print("Newest File: %s"%lastFile)
                time.sleep(0.5)
                self.getNewBattleLog(basepath, lastFile)
            #while(True):
            #    time.sleep(5)
            #time.sleep(987654)

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenThread = threading.Thread(target = self.listenPath, args = (self.basepath,)) 
        self.listenThread.setDaemon(True);
        self.listenThread.start()
    
    def __init__(self, basepath, config, analyser):
        '''
        构造方法。
        params
        - basepath: 战斗记录生成的路径。
        '''
        self.basepath = basepath
        self.config = config
        self.dpsThreshold = {"qualifiedRate": config.qualifiedRate,
                             "alertRate": config.alertRate,
                             "bonusRate": config.bonusRate}
        self.analyser = analyser
                             

class AllStatWindow():
    
    def getColor(self, occ):
        if occ[-1] in ['d', 't', 'h', 'p', 'm']:
            occ = occ[:-1]
        colorDict = {"0": (0, 0, 0), 
                     "1": (210, 180, 0),#少林
                     "2": (127, 31, 223),#万花
                     "4": (56, 175, 255),#纯阳
                     "5": (255, 127, 255),#七秀
                     "3": (160, 0, 0),#天策
                     "8": (255, 255, 0),#藏剑
                     "9": (205, 133, 63),#丐帮
                     "10": (253, 84, 0),#明教
                     "6": (63, 31, 159),#五毒
                     "7": (0, 133, 144),#唐门
                     "21": (180, 60, 0),#苍云
                     "22": (100, 250, 180),#长歌
                     "23": (71, 73, 166),#霸刀
                     "24": (195, 171, 227),#蓬莱
                     "25": (161, 9, 34)#凌雪
                    }
        res = (0, 0, 0)
        if occ in colorDict:
            res = colorDict[occ]
        return "#%s%s%s"%(str(hex(res[0]))[-2:].replace('x', '0'), 
                          str(hex(res[1]))[-2:].replace('x', '0'),
                          str(hex(res[2]))[-2:].replace('x', '0'))
        
    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"
            
    def getPot(self, tmp):
        '''
        分锅结果变化的处理函数。
        params
        - tmp 玩家编号
        '''
        pass
        
    def final(self):
        '''
        关闭窗口。
        '''
        self.window.destroy()

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('分锅统计')
        window.geometry('600x700')
        
        numPlayer = len(self.playerID)
        
        i = 0
        
        for player in self.playerID:
            line = self.playerPotList[player]

            name = player.strip('"')
            occ = line["occ"]
            color = self.getColor(occ)
            nameLabel = tk.Label(window, text=name, width = 13, fg=color)
            nameLabel.grid(row=i, column=0)
            
            posNumText = ""
            if line["numPositive"] > 0:
                posNumText = "+%s"%str(line["numPositive"])
            positiveLabel = tk.Label(window, text=posNumText, width=5, fg="#007700", font=("Arial", 12, "bold"))
            positiveLabel.grid(row=i, column=1)
            
            negNumText = ""
            if line["numNegative"] < 0:
                negNumText = "%s"%str(line["numNegative"])
            negativeLabel = tk.Label(window, text=negNumText, width=5, fg="#ff0000", font=("Arial", 12, "bold"))
            negativeLabel.grid(row=i, column=2)
            
            tmp = i
            # button1 = tk.Button(window, text='调整', width=6)
            button1 = tk.Button(window, bitmap="warning", text="调整", width=60, height=15, compound=tk.LEFT, command=lambda tmp=tmp: self.getPot(tmp))
            button1.grid(row=i, column=3)
            
            i += 1
            
        buttonFinal = tk.Button(window, text='查看完成', width=10, height=1, command=self.final)
        buttonFinal.place(x = 250, y = 640)
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def addPotList(self):
        self.potListScore = self.analyser.potListScore
        self.playerPotList = self.analyser.getPlayerPotList()
        self.playerID = self.analyser.getPlayer()

    def __init__(self, analyser):
        self.analyser = analyser
        self.addPotList()
    
    
    
        
        
# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time
import tkinter as tk

from ActorReplay import ActorStatGenerator

class SingleBossWindow():

    def getPot(self):
        print("Pot!")

    def loadWindow(self):
        window = tk.Tk()
        window.title('战斗复盘')
        window.geometry('500x700')
        for i in range(len(self.potList)):
            line = self.potList[i]
            name = line[0].strip('"')
            nameLabel = tk.Label(window, text=name, height=1)
            nameLabel.grid(row=i, column=0)
            occ = line[1]
            pot = line[4]
            potLabel = tk.Label(window, text=pot, height=1)
            potLabel.grid(row=i, column=1)
            button1 = tk.Button(window, text='接锅', width=6, height=1, command=self.getPot)
            button1.grid(row=i, column=2)
            button2 = tk.Button(window, text='领赏', width=6, height=1, command=self.getPot)
            button2.grid(row=i, column=3)
        window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def addPotList(self, potList):
        self.potList = potList

    def __init__(self):
        pass

class LiveActorStatGenerator(ActorStatGenerator):
    
    def __init__(self, filename, path="", myname="", failThreshold=0, battleDate="", mask=0, dpsThreshold={}):
        super().__init__(filename, path, rawdata={}, failThreshold=failThreshold, 
            battleDate=battleDate, mask=mask, dpsThreshold=dpsThreshold)

class LiveActorAnalysis():
    
    def __init__(self):
        pass

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
        print(liveGenerator.potList)
        window = SingleBossWindow()
        window.addPotList(liveGenerator.potList)
        window.start()
        

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
            if lastFile != newestFile or True:  #调试入口
                newestFile = lastFile
                print("Newest File: %s"%lastFile)
                self.getNewBattleLog(basepath, lastFile)
            time.sleep(987654)

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenThread = threading.Thread(target = self.listenPath, args = (self.basepath,))    
        self.listenThread.start()
        
    
    def __init__(self, basepath, config):
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
        
        
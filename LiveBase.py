# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time
import tkinter as tk
from tkinter import messagebox
from win10toast import ToastNotifier

from ActorReplay import ActorStatGenerator
from replayer.Base import SpecificBossWindow
from replayer.Yuhui import YuHuiWindow
from replayer.Mitao import MiTaoWindow
from replayer.Wuxuesan import WuXueSanWindow

class ToolTip(object):
    def build(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
 
    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
 
        self.label = tk.Label(tw, text=text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("Aaril", "10", "normal"))
        self.label.pack(ipadx=1)
 
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def createToolTip(self, widget, text):
        toolTip = self.build(widget)
        def enter(event):
            self.showtip(text)
        def leave(event):
            self.hidetip()
        self.widget = widget
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def remove(self):
        self.widget.unbind('<Enter>')
        self.widget.unbind('<Leave>')
        
    def __init__(self, widget, text):
        self.createToolTip(widget, text)

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
                     "25": (161, 9, 34),#凌雪
                     "211": (166, 83, 251),#衍天
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
        
        #self.analyser.potListScore[-self.numPot + tmp][-1] = self.scoreList[tmp]
        
        self.analyser.setSinglePotScore(self.bossNum, tmp, self.scoreList[tmp])
        
        self.analyser.getPlayerPotList()
        
        text = self.analyser.getPlayerText(self.nameList[tmp])
        self.toolTips[tmp].remove()
        toopTip = ToolTip(self.toolTips[tmp].widget, text)
        self.toolTips[tmp] = toopTip
        
        
    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''
        self.windowAlive = False
        self.potListScore = []
        for i in range(len(self.potList)):
            self.potListScore.append(self.potList[i] + [self.scoreList[i]])
        self.analyser.changeResult(self.potListScore, self.bossNum)
        self.window.destroy()
        
    def finalPrev(self):
        '''
        收集分锅结果并关闭窗口，尝试打开前一个BOSS的窗口。
        '''
        prevNum = self.bossNum - 1
        if self.analyser.checkBossExists(prevNum):
            self.final()
            self.bossNum = prevNum
            self.addPotList(self.analyser.potContainer.getBoss(prevNum))
            self.start()
        else:
            messagebox.showinfo(title='嘶', message='前序BOSS未找到。')
    
    def finalNext(self):
        '''
        收集分锅结果并关闭窗口，尝试打开后一个BOSS的窗口。
        '''
        nextNum = self.bossNum + 1
        if self.analyser.checkBossExists(nextNum):
            self.final()
            self.bossNum = nextNum
            self.addPotList(self.analyser.potContainer.getBoss(nextNum))
            self.start()
        else:
            messagebox.showinfo(title='嘶', message='后继BOSS未找到。')
            
    def setDetail(self, potList, effectiveDPSList, detail):
        '''
        初始化详细复盘的数据。
        - params
        potList 分锅记录。
        effectiveDPSList DPS详细统计，包括每名玩家在特定算法下的DPS。
        detail 详细复盘记录。
        '''
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.hasDetail = 1
        if "boss" in detail:
            if detail["boss"] == "余晖":
                self.specificBossWindow = YuHuiWindow(effectiveDPSList, detail)
            elif detail["boss"] == "宓桃":
                self.specificBossWindow = MiTaoWindow(effectiveDPSList, detail)
            elif detail["boss"] == "武雪散":
                self.specificBossWindow = WuXueSanWindow(effectiveDPSList, detail)
            else:
                self.specificBossWindow = SpecificBossWindow()
                self.hasDetail = 0
        
    def showDetail(self):
        '''
        显示战斗统计详情。
        '''
        if self.hasDetail:
            self.specificBossWindow.start()
        else:
            messagebox.showinfo(title='嘶', message='制作中，敬请期待！')

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        #window = tk.Tk()
        window.title('战斗复盘')
        window.geometry('600x700')
        
        numPot = len(self.potList)
        self.numPot = numPot
        
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
        self.toolTips = []
        self.nameList = []
        
        self.potListScore = []

        for i in range(len(self.potList)):
            if len(self.potList[i]) <= 6:
                self.potListScore.append(self.potList[i] + [0])
                self.scoreList.append(0)
            else:
                self.potListScore.append(self.potList[i])
                self.scoreList.append(self.potList[i][-1])
                
        if not self.analyser.checkBossExists(self.bossNum):
            self.analyser.addResult(self.potListScore, self.bossNum)
        
        self.analyser.getPlayerPotList()
        
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
            
            if len(line) > 5:
                potDetail = '\n'.join(line[5])
                if potDetail != "":
                    toolTip = ToolTip(potLabel, potDetail)
            
            scoreLabel = tk.Label(frame, text="", width=5, height=1, font=("Arial", 12, "bold"))
            scoreLabel.grid(row=i, column=2)
            self.scoreLabels.append(scoreLabel)
            
            tmp = i
            button1 = tk.Button(frame, text='接锅', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, -1), bg='#ffcccc')
            button1.grid(row=i, column=3)
            button2 = tk.Button(frame, text='领赏', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, 1), bg='#ccffcc')
            button2.grid(row=i, column=4)
            
            text = self.analyser.getPlayerText(name)
            toolTip = ToolTip(nameLabel, text)
            self.toolTips.append(toolTip)
            self.nameList.append(name)
            
        for i in range(len(self.potList)):
            self.getPot(i, 0)
            
        buttonFinal = tk.Button(window, text='分锅完成', width=10, height=1, command=self.final)
        buttonFinal.place(x = 250, y = 540)
        
        buttonPrev = tk.Button(window, text='<<', width=2, height=1, command=self.finalPrev)
        buttonPrev.place(x = 220, y = 540)
        
        buttonNext = tk.Button(window, text='>>', width=2, height=1, command=self.finalNext)
        buttonNext.place(x = 340, y = 540)
        
        buttonDetail = tk.Button(window, text='数据统计', width=10, height=1, command=self.showDetail)
        buttonDetail.place(x = 250, y = 570)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def addPotList(self, potList):
        self.potList = potList
        
    def alive(self):
        return self.windowAlive

    def __init__(self, analyser, bossNum):
        self.analyser = analyser
        self.bossNum = bossNum

class LiveActorStatGenerator(ActorStatGenerator):
    
    def __init__(self, filename, path="", myname="", failThreshold=0, battleDate="", mask=0, dpsThreshold={}, uploadTiantiFlag=0, window=None):
        super().__init__(filename, path, rawdata={}, failThreshold=failThreshold, 
            battleDate=battleDate, mask=mask, dpsThreshold=dpsThreshold, uploadTiantiFlag=uploadTiantiFlag, window=window)
            
class PotContainer():
    '''
    锅的记录类。
    '''
    
    def getAll(self):
        '''
        查找所有的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        result = []
        for line in self.pot:
            result.extend(self.pot[line])
        return result
    
    def getBoss(self, bossid):
        '''
        查找对应boss的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        bossidStr = str(bossid)
        return self.pot[bossidStr]
    
    def addBoss(self, bossid, potListScore):
        '''
        当一个BOSS结束时，把分锅记录加入总记录中。
        或是当修改锅时，按对应的bossid取代原有的分锅记录。
        params
        - bossid 按时间顺序的BOSS编号。
        - potListScore 分锅与打分的列表，list格式
        '''
        bossidStr = str(bossid)
        self.pot[bossidStr] = potListScore
    
    def __init__(self):
        self.pot = {}

class LiveActorAnalysis():

    def getPlayer(self):
        '''
        从结果记录中提取所有ID与门派，按门派顺序排序
        return
        - playerListSort 排好序的ID列表
        '''
        player = {}
        self.potListScore = self.potContainer.getAll()
        for line in self.potListScore:
            if line[0] not in player:
                occ = line[1]
                if occ[-1] in ['d', 't', 'h', 'p', 'm']:
                    occ = occ[:-1]
                player[line[0].strip('"')] = int(occ)
        playerList = []
        for line in player:
            playerList.append([line.strip('"'), player[line]])
        playerList.sort(key = lambda x:x[1])
        playerListSort = []
        for line in playerList:
            playerListSort.append(line[0])
        return playerListSort

    def getPlayerPotList(self):
        playerPot = {}
        self.potListScore = self.potContainer.getAll()
        for line in self.potListScore:
            name = line[0].strip('"')
            if name not in playerPot:
                playerPot[name] = {"occ": line[1], "numPositive": 0, "numNegative": 0, "pot": []}
            playerPot[name]["pot"].append(line[1:])
            if line[-1] > 0:
                playerPot[name]["numPositive"] += line[-1]
            elif line[-1] < 0:
                playerPot[name]["numNegative"] += line[-1]
        self.playerPotList = playerPot
        return playerPot
        
    def getPlayerText(self, player):
        first = 1
        s = ""
        if player in self.playerPotList:
            for line in self.playerPotList[player]["pot"]:
                if first:
                    first = 0
                else:
                    s += '\n'
                s += "%s %s %s"%(line[2], line[3], str(line[-1]))
            
        return s
        
    def setSinglePotScore(self, bossNum, pos, pot):
        '''
        设定单个分锅记录的锅数。
        params
        - bossNum BOSS编号
        - tmp 记录的位置
        - pot 修改后的锅数
        '''
        bossidStr = str(bossNum)
        self.potContainer.pot[bossidStr][pos][-1] = pot
        
    def changeResult(self, potListScore, bossNum):
        self.potContainer.addBoss(bossNum, potListScore)
        #if len(potListScore) != 0:
        #    del self.potListScore[-len(potListScore):]
        #    self.potListScore.extend(potListScore)

    def addResult(self, potListScore, bossNum):
        #self.potListScore.extend(potListScore)
        self.potContainer.addBoss(bossNum, potListScore)
        
    def checkBossExists(self, bossNum):
        bossNumStr = str(bossNum)
        return bossNumStr in self.potContainer.pot
    
    def __init__(self):
        #self.potListScore = []
        self.potContainer = PotContainer()

class LiveListener():

    def getNewBattleLog(self, basepath, lastFile):
        '''
        params
        - basepath: 监控的路径
        - lastFile: 新增的文件，通常是刚刚完成的战斗复盘
        '''
        battleDate = '-'.join(lastFile.split('-')[0:3])
        liveGenerator = LiveActorStatGenerator([lastFile, 0, 1], basepath, failThreshold=self.config.failThreshold, 
                battleDate=battleDate, mask=self.config.mask, dpsThreshold=self.dpsThreshold, uploadTiantiFlag=self.config.uploadTianti, window=self.mainwindow)
                
        analysisExitCode = liveGenerator.firstStageAnalysis()
        if analysisExitCode == 1:
            raise Exception("实时模式下数据格式错误，请再次检查设置。如不能解决问题，尝试重启程序。")
        liveGenerator.secondStageAnalysis()
        if liveGenerator.upload:
            liveGenerator.prepareUpload()
            
        self.bossNum += 1
        
        if self.window is not None and self.window.alive():
            self.window.final()
        
        if self.mainwindow is not None:
            self.mainwindow.setNotice({"t1": "[%s]分析完成！"%liveGenerator.bossname, "c1": "#000000", "t2": ""})
        
        window = SingleBossWindow(self.analyser, self.bossNum)
        self.window = window
        window.addPotList(liveGenerator.potList)
        window.setDetail(liveGenerator.potList, liveGenerator.effectiveDPSList, liveGenerator.detail)
        window.start()
        
        toaster = ToastNotifier()
        toaster.show_toast("分锅结果已生成", "[%s]的战斗复盘已经解析完毕，请打开结果界面分锅。"%liveGenerator.bossname, icon_path='jx3bla.ico')
        
        self.mainwindow.setTianwangInfo(liveGenerator.ids, liveGenerator.server)
        
        if liveGenerator.uploadTianti:
            liveGenerator.prepareUploadTianti()

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
                print("检测到新的复盘记录: %s"%lastFile)
                time.sleep(0.5)
                self.getNewBattleLog(basepath, lastFile)
            #while(True):
            #    time.sleep(5)

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenThread = threading.Thread(target = self.listenPath, args = (self.basepath,)) 
        self.listenThread.setDaemon(True);
        self.listenThread.start()
    
    def __init__(self, basepath, config, analyser, mainwindow):
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
        self.mainwindow = mainwindow
        
        self.bossNum = 0
        self.window = None
                             

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
        
        self.toolTips = []
        
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
            
            text = self.analyser.getPlayerText(name)
            toopTip = ToolTip(nameLabel, text)
            self.toolTips.append(toopTip)
            
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
        
        
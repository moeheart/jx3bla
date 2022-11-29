# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time
import traceback
import tkinter as tk
from tkinter import messagebox
from tools.Functions import *
import pyperclip

from data.DataController import DataController
from replayer.ActorReplayPro import ActorProReplayer

from window.CommentWindow import CommentWindow
from window.SingleBossWindow import SingleBossWindow

class ToolTip(object):
    '''
    浮动标签类，用于实现简单的浮动标签。
    '''
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
        
        tf = tk.Frame(tw, relief=tk.SOLID, borderwidth=1, bg="#ffffe0")
        tf.pack(ipadx=1)
        
        textList = text.split('\n')
        
        for line in textList:
            if line == "":
                fg = "#000000"
            if line[0] == "-":
                fg = "#ff0000"
            elif line[0] == "+":
                fg = "#007700"
            else:
                fg = "#000000"
            label = tk.Label(tf, text=line, fg=fg, justify=tk.LEFT,
                          background="#ffffe0", anchor='nw', 
                          font=("Aaril", "10", "normal"))
            label.pack(anchor=tk.NW)
 
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
            
class PotContainer():
    '''
    锅的记录类。
    '''
    
    def getAll(self):
        '''
        返回所有的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        result = []
        for line in self.pot:
            result.extend(self.pot[line])
        return result
        
    def getPlayerOcc(self):
        '''
        获取记录中的角色与门派。用effectiveDpsList作为信息来源。
        return
        - list格式的角色与门派组合。
        '''
        playerOcc = {}
        playerOccNum = {}
        for key in self.statDict:
            statList = self.statDict[key]
            for line in statList:
                if line["name"] not in playerOcc:
                    playerOcc[line["name"]] = line["occ"]
                    occ = line["occ"]
                    if occ[-1] in ['d', 't', 'h', 'p', 'm']:
                        occ = occ[:-1]
                    playerOccNum[line["name"]] = int(occ)
                        
        playerList = []
        for line in playerOccNum:
            playerList.append([line.strip('"'), playerOccNum[line], playerOcc[line]])
        playerList.sort(key=lambda x:x[1])
        
        playerListSort = []
        for line in playerList:
            playerListSort.append([line[0], line[2]])
            
        return playerListSort
        
    def getDetail(self, bossid):
        '''
        返回对应boss的详细记录。
        return
        - 分锅与打分的列表，list格式
        - 战斗复盘中的DPS列表
        - 战斗复盘中的特定BOSS细节
        '''
        bossidStr = str(bossid)
        return self.pot[bossidStr], self.statDict[bossidStr], self.detail[bossidStr], \
               self.occResult[bossidStr], self.analysedBattleData[bossidStr]
    
    def getBoss(self, bossid):
        '''
        返回对应boss的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        bossidStr = str(bossid)
        return self.pot[bossidStr]
        
    def getBossName(self, bossid):
        '''
        查找对应boss的名称。
        return
        - 字符串格式的BOSS名。
        '''
        bossidStr = str(bossid)
        return self.detail[bossidStr]["boss"]
    
    def addBoss(self, bossid, potListScore, statDict=[], detail={}, occResult={}, bh=None, analysedBattleData={}, change=1):
        '''
        当一个BOSS结束时，把分锅记录加入总记录中。
        或是当修改锅时，按对应的bossid取代原有的分锅记录。
        params
        - bossid 按时间顺序的BOSS编号。
        - potListScore 分锅与打分的列表，list格式
        - statDict 战斗复盘中的DPS列表
        - detail 战斗复盘中的特定BOSS细节
        '''
        bossidStr = str(bossid)
        self.pot[bossidStr] = potListScore
        if change:
            self.statDict[bossidStr] = statDict
            self.detail[bossidStr] = detail
            self.occResult[bossidStr] = occResult
            self.analysedBattleData[bossidStr] = analysedBattleData
    
    def __init__(self):
        self.pot = {}
        self.statDict = {}
        self.detail = {}
        self.occResult = {}
        self.analysedBattleData = {}

class LiveActorAnalysis():
    '''
    实时演员信息类。维护当前结果信息的存储与获取。
    '''

    def getBossName(self):
        '''
        从结果记录中提取所有BOSS的名称，记录为字典形式。
        return
        - bossDict key为数字，value为boss名称。
        '''
        bossDict = {}
        lastNum = int(list(self.potContainer.pot.keys())[-1])
        for i in range(1, lastNum + 1):
            bossDict[str(i)] = self.potContainer.getBossName(i)
        return bossDict

    def getPlayer(self):
        '''
        从结果记录中提取所有ID与门派，按门派顺序排序
        return
        - playerListSort 排好序的ID与门派列表
        '''
        return self.potContainer.getPlayerOcc()

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
        
    def setServer(self, server):
        self.server = server
        
    def getServer(self):
        return self.server
        
    def setMapDetail(self, mapDetail):
        self.mapDetail = mapDetail
        
    def getMapDetail(self):
        return self.mapDetail
        
    def setBeginTime(self, beginTime):
        self.beginTime = beginTime
        
    def getBeginTime(self):
        return self.beginTime
        
    def changeResult(self, potListScore, bossNum):
        self.potContainer.addBoss(bossNum, potListScore, change=0)

    def addResult(self, potListScore, bossNum, statDict, detail, occResult, analysedBattleData):
        #self.potListScore.extend(potListScore)
        self.potContainer.addBoss(bossNum, potListScore, statDict, detail, occResult, analysedBattleData=analysedBattleData)
        
    def checkBossExists(self, bossNum):
        bossNumStr = str(bossNum)
        return bossNumStr in self.potContainer.pot
        
    def getLastBossNum(self):
        return list(self.potContainer.pot.keys())[-1]

    def checkEmpty(self):
        return list(self.potContainer.pot.keys()) == []
    
    def __init__(self):
        #self.potListScore = []
        self.potContainer = PotContainer()
        self.server = "未知"

class LiveListener():
    '''
    复盘监听类，在实时模式中控制开始复盘的时机。
    '''

    def getOneBattleLog(self, basepath, fileName):
        '''
        在对一条战斗记录进行复盘。
        params
        - basepath 监控的路径
        - lastFile 复盘数据对应的文件名
        - raw raw文件。如果是实时模式则为空，现场读取；否则从之前的记录中继承。
        return
        - liveGenerator 实时复盘对象，用于后续处理流程。
        '''
        controller = DataController(self.config)
        if self.mainWindow.bldDict != {}:
            controller.setRawData(self.mainWindow.bldDict)
        controller.getSingleData(self.mainWindow, fileName)  # 此处将MainWindow类本身传入
        
        try:
            fileNameInfo = [fileName, 0, 1]
            # print(self.mainWindow.bldDict)
            # print(fileNameInfo)
            # print(basepath)
            actorRep = ActorProReplayer(self.config, fileNameInfo, basepath, self.mainWindow.bldDict, self.mainWindow)

            analysisExitCode = actorRep.FirstStageAnalysis()
            if analysisExitCode == 1:
                messagebox.showinfo(title='提示', message='数据格式错误，请再次检查设置。如不能解决问题，尝试重启程序。\n在此状态下，大部分功能将不能正常使用。')
                raise Exception("数据格式错误，请再次检查设置。如不能解决问题，尝试重启程序。")
                
            actorRep.SecondStageAnalysis()
            if not actorRep.available:
                # 分片，记录
                self.mainWindow.lastBld = actorRep.bld
                return actorRep
            actorRep.ThirdStageAnalysis()
            actorRep.OccAnalysis()
            
            self.analyser.setServer(actorRep.bld.info.server)
            self.analyser.setMapDetail(actorRep.bld.info.map)
            self.analyser.setBeginTime(actorRep.bld.info.battleTime)
            
            if actorRep.upload:
                actorRep.prepareUpload()

            self.mainWindow.executeUploadData()
            # if liveGenerator.win:  # TODO 移除失败的复盘
            #     self.mainwindow.addRawData(fileName, liveGenerator.getRawData())
            # else:
            #     DestroyRaw(liveGenerator.getRawData())
        except Exception as e:
            traceback.print_exc()
            self.mainWindow.setNotice({"t1": "[%s]分析失败！"%actorRep.bld.info.boss, "c1": "#000000", "t2": "请保留数据，并反馈给作者~", "c2": "#ff0000"})
            return actorRep
            
        self.bossNum += 1
        self.mainWindow.setTianwangInfo(actorRep.ids, actorRep.server)
        return actorRep

    def getAllBattleLog(self, basepath, fileList):
        '''
        复盘模式中对所有战斗记录进行复盘。
        params
        - basepath 监控的路径
        - fileList 需要复盘的文件名列表.
        '''

        for file in fileList:
            actorRep = self.getOneBattleLog(basepath, file)
            if not actorRep.available:
                continue
            #print("[Detail]", actorRep.detail)
            potListScore = []
            for i in range(len(actorRep.potList)):
                if len(actorRep.potList[i]) <= 6:
                    potListScore.append(actorRep.potList[i] + [0])
                else:
                    potListScore.append(actorRep.potList[i])
            self.analyser.addResult(potListScore, self.bossNum, actorRep.statDict, actorRep.detail, actorRep.occResult, actorRep.actorData)

    def getNewBattleLog(self, basepath, lastFile):
        '''
        实时模式中复盘战斗记录，并控制窗口弹出、数据记录。
        params
        - basepath: 监控的路径
        - lastFile: 新增的文件，通常是刚刚完成的战斗复盘
        '''
        actorRep = self.getOneBattleLog(basepath, lastFile)
        if not actorRep.available:
            self.mainWindow.setNotice({"t1": "[%s]分析中断，等待完整记录..." % actorRep.bossname, "c1": "#000000"})
            return

        if self.window is not None and self.window.alive():
            self.window.final()
        
        if self.mainWindow is not None:
            self.mainWindow.setNotice({"t1": "[%s]分析完成！"%actorRep.bossname, "c1": "#000000"})
        
        window = SingleBossWindow(self.analyser, self.bossNum, self.mainWindow)
        self.window = window
        window.addPotList(actorRep.potList)
        window.setDetail(actorRep.potList, actorRep.statDict, actorRep.detail, actorRep.occResult, actorRep.actorData)
        window.openDetailWindow()

        potListScore = []
        for i in range(len(actorRep.potList)):
            if len(actorRep.potList[i]) <= 6:
                potListScore.append(actorRep.potList[i] + [0])
            else:
                potListScore.append(actorRep.potList[i])
        self.analyser.addResult(potListScore, self.bossNum, actorRep.statDict, actorRep.detail, actorRep.occResult, actorRep.actorData)

        self.mainWindow.notifier.show("分锅结果已生成", "[%s]的战斗复盘已经解析完毕，请打开结果界面分锅。"%actorRep.bossname)

    def listenPath(self, basepath):
        '''
        开始监控对应的路径。
        params
        - basepath: 监控的路径
        '''
        filelist = os.listdir(basepath)
        if self.config.item["general"]["datatype"] == "jx3dat":
            dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
        else:
            dataList = [x for x in filelist if x[-4:] == '.jcl']
        if dataList != []:
            newestFile = dataList[-1]
        else:
            newestFile = ""
        while(self.listenFlag):
            time.sleep(3)
            filelist = os.listdir(basepath)
            if self.config.item["general"]["datatype"] == "jx3dat":
                dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
            else:
                dataList = [x for x in filelist if x[-4:] == '.jcl']
            if dataList != []:
                lastFile = dataList[-1]
            else:
                lastFile = ""
            if lastFile != newestFile:
                newestFile = lastFile
                print("检测到新的复盘记录: %s"%lastFile)
                time.sleep(0.5)
                self.getNewBattleLog(basepath, lastFile)

    def stopListen(self):
        '''
        中止监听。
        '''
        self.listenFlag = False

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenFlag = True
        self.listenThread = threading.Thread(target=self.listenPath, args = (self.basepath,))
        self.listenThread.setDaemon(True)
        self.listenThread.start()
    
    def __init__(self, basepath, config, analyser, mainWindow):
        '''
        构造方法。
        params
        - basepath: 战斗记录生成的路径。
        '''
        self.basepath = basepath
        self.config = config
        # self.dpsThreshold = {"qualifiedRate": config.item["actor"]["qualifiedrate"],
        #                      "alertRate": config.item["actor"]["alertrate"],
        #                      "bonusRate": config.item["actor"]["bonusrate"]}
        self.analyser = analyser
        self.mainWindow = mainWindow
        
        self.bossNum = 0
        self.window = None

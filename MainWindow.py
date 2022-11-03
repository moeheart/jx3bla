import tkinter as tk
from tkinter import messagebox
import threading
import re
import os
import time
from tools.Notifier import Notifier
import traceback
import urllib
import json
import webbrowser

from GenerateFiles import *
from FileLookUp import FileLookUp, FileSelector
from ConfigTools import Config
from window.ConfigWindow import ConfigWindow
from window.LicenseWindow import LicenseWindow
from window.AnnounceWindow import AnnounceWindow
from LiveBase import LiveListener, LiveActorAnalysis
from window.AllStatWindow import AllStatWindow
from window.SingleBossWindow import SingleBossWindow
from Constants import *
from tools.Functions import *
from tools.Preload import *

class SingleBlockLocker():
    '''
    维护一个简单的锁，可以在对象之间传递
    '''
    def Lock(self):
        self.s = 1
    
    def Unlock(self):
        self.s = 0
        
    def state(self):
        return self.s
    
    def __init__(self):
        self.s = 0

class MainWindow():

    def closeWindow(self):
        ans = messagebox.askyesno(title='提示', message='确定要关闭吗？')
        if ans:
            self.window.destroy()
        else:
            return
            
    def setNotice(self, d):
        '''
        使通知栏显示对应的文本提示。
        params
        - d 以字典形式表示需要显示的内容，对应的含义见下面的代码。
        '''
        if "t1" in d:
            self.var1.set(d["t1"])
        if "c1" in d:
            self.text1.config(fg=d["c1"])
        if "t2" in d:
            self.var2.set(d["t2"])
        if "c2" in d:
            self.text2.config(fg=d["c2"])

    def clearIfRunning(self):
        '''
        如果通知栏的文本以...结尾，就将其移除。
        '''
        if self.var1.get()[-1] == '.':
            self.var1.set("")
        if self.var2.get()[-1] == '.':
            self.var2.set("")

    def addUploadData(self, uploadData):
        '''
        增加一个需要上传的数据.
        '''
        n = len(self.uploadData)
        uploadData["id"] = n
        self.uploadData.append(uploadData)

    def executeUploadData(self):
        '''
        执行数据上传.
        '''

        if "beta" in EDITION:
            return

        actualData = {"data": []}
        for line in self.uploadData:
            singleData = {"type": line["type"], "data": line["data"], "id": line["id"]}
            actualData["data"].append(singleData)

        self.setNotice({"t1": "正在上传数据……", "c1": "#000000"})

        Jdata = json.dumps(actualData)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://%s:8009/uploadCombinedData' % IP, data=jparse)
        res = json.load(resp)

        # print("[res]", res)

        # 解析返回的数据

        if res["status"] == "fail":
            self.setNotice({"t2": "上传数据失败！", "c2": "#ff0000"})
        else:
            for i in range(len(self.uploadData)):
                if self.uploadData[i]["type"] == "replay":
                    # 复盘. 需要更新复盘编号.
                    if res["data"][i]["result"] != "fail":
                        self.uploadData[i]["anchor"]["overall"]["shortID"] = res["data"][i]["shortID"]
                        self.uploadData[i]["anchor"]["overall"]["numReplays"] = res["data"][i]["num"]
                        self.uploadData[i]["anchor"]["overall"]["scoreRank"] = res["data"][i]["scoreRank"]
                    else:
                        self.uploadData[i]["anchor"]["overall"]["shortID"] = "数据保存出错"
                elif self.uploadData[i]["type"] == "battle":
                    # 战斗信息. 需要在主界面显示内容.
                    if res["data"][i]["scoreStatus"] == "illegal":
                        self.setNotice({"t2": "未增加荣誉值，原因：非指定地图", "c2": "#ff0000"})
                    elif res["data"][i]["scoreStatus"] == "notwin":
                        self.setNotice({"t2": "未增加荣誉值，原因：未击败BOSS", "c2": "#ff0000"})
                    elif res["data"][i]["scoreStatus"] == "expire":
                        self.setNotice({"t2": "未增加荣誉值，原因：数据已被他人上传", "c2": "#ff0000"})
                    elif res["data"][i]["scoreStatus"] == "dupid":
                        self.setNotice({"t2": "未增加荣誉值，原因：数据已被自己上传", "c2": "#ff0000"})
                    elif res["data"][i]["scoreStatus"] == "nologin":
                        self.setNotice({"t2": "未增加荣誉值，原因：未注册用户名", "c2": "#ff0000"})
                    elif res["data"][i]["scoreStatus"] == "success":
                        self.setNotice({"t2": "数据上传成功，荣誉值增加：%d" % res["data"][i]["scoreAdd"], "c2": "#00ff00"})

        # 清空上传数据
        self.uploadData = []

            
    def setTianwangInfo(self, playerIDList, server):
        self.server = server
        for id in playerIDList:
            if id not in self.playerIDs:
                self.playerIDs.append(id)
                
    def addBattleLogData(self, filename, bld):
        '''
        向主窗体类中加入Rawdata，用于在复盘模式与实时模式中共享数据。
        '''
        self.bldDict[filename] = bld
            
    def setBattleLogData(self, bldDict):
        '''
        将BattleLogData设定为对应结果。用于复盘模式得到数据后向主界面上报。
        params
        - bldDict 对应的BattleLogData数据。
        '''
        self.bldDict = bldDict
        
    def liveForReplay(self):
        '''
        用存储的数据进行所有实时模式的复盘。
        '''
        if not self.hasReplayed and not self.startLive:
            self.liveListener.getAllBattleLog(self.fileLookUp.basepath, self.bldDict)
            self.hasReplayed = True

    # def checkAttendence(self):
    #     rawList = self.rawData
    #     mapDict = {}
    #     for key in rawList:
    #         mapDict[key] = []
    #         raw = rawList[key]
    #         name = raw['9'][0]
    #         occ = raw['10'][0]
    #         for line in raw['12'][0]['4'][0].keys():
    #             if line in name and line in occ and occ[line][0] != '0':
    #                 finalName = name[line][0].strip('"')
    #                 mapDict[key].append(finalName)
    #
    #     #print(mapDict)
    #     #g = open("result.txt", "w")
    #     #g.write(str(mapDict))
    #     #g.close()

    def replay(self, selectionFileList=[]):
        replayFileList = []
        config = Config("config.ini")
        fileLookUp = FileLookUp()
        fileLookUp.initFromConfig(config)
        self.config = config
        self.fileLookUp = fileLookUp
        self.dataType = self.config.item["general"]["datatype"]
        # 如需在复盘模式后接实时模式，则使用这个逻辑
        if self.liveListener is None:
            liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
            self.liveListener = liveListener

        if selectionFileList != []:
            replayFileList = selectionFileList
        else:
            filelist, allFilelist, map = fileLookUp.getLocalFile()
            if config.item["actor"]["checkall"]:
                # bldDict = RawDataLoader(config, allFilelist, fileLookUp.basepath, window, self.bldDict).bldDict
                replayFileList = allFilelist
            else:
                # bldDict = RawDataLoader(config, filelist, fileLookUp.basepath, window).bldDict
                replayFileList = filelist

        replayFileNameList = [x[0] for x in replayFileList]
        self.liveListener.getAllBattleLog(fileLookUp.basepath, replayFileNameList)

        if not self.analyser.checkEmpty():
            self.setNotice({"t1": "复盘完成！", "c1": "#000000"})
            self.show_history()
            self.clearIfRunning()
            self.hasReplayed = True

        #self.checkAttendence()

    def replay_select(self):
        '''
        手选文件的复盘模式.
        '''
        config = Config("config.ini")
        self.fileSelector = FileSelector(config, self)
        self.fileSelector.start()

    def start_replay(self):
        if self.lock.state():
            return
        self.setNotice({"t1": "复盘中，请稍候……（时间较久，请耐心等待）", "c1": "#000000"})
        refreshThread = threading.Thread(target=self.replay)
        refreshThread.start()
        
    def check_live(self):
        if self.liveListener is None:
            liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
            self.liveListener = liveListener
        self.liveListener.startListen()
        
    def check_live_quick(self):
        if self.lock.state():
            return
        if self.liveListener is None:
            liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
            self.liveListener = liveListener
        messagebox.showinfo(title='警告', message='快速实时模式主要用于调试，如果不了解原理，有极大概率无法正常运行。')
        
        self.liveListener.startListen()
        self.setNotice({"t1": "快速实时模式已开启，请关注终端界面……", "c1": "#000000", "t2": "快速模式仅用于调试，新手勿入QAQ", "c2": "#ff0000"})
        
    def start_live(self):
        if self.lock.state():
            return

        if not self.startLive:
            config = Config("config.ini")
            self.startLive = True
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            self.config = config
            self.dataType = self.config.item["general"]["datatype"]
            self.fileLookUp = fileLookUp

            if self.dataType == "jcl" and "combat_logs" not in fileLookUp.basepath:
                self.setNotice(
                    {"t1": "实时模式已开启。", "c1": "#000000", "t2": "jcl路径可能有误，请确认。", "c2": "#ff0000"})

            elif self.dataType == "jx3dat" and "fight_stat" not in fileLookUp.basepath:
                self.setNotice(
                    {"t1": "实时模式已开启。", "c1": "#000000", "t2": "jx3dat路径可能有误，请确认。", "c2": "#ff0000"})
            else:
                self.setNotice(
                    {"t1": "实时模式已开启。", "c1": "#000000", "t2": "", "c2": "#000000"})

            self.listenThread = threading.Thread(target=self.check_live)
            self.listenThread.start()
            self.liveVar.set("中止")

        else:
            self.startLive = False
            self.liveListener.stopListen()
            self.setNotice(
                {"t1": "实时模式已中止。", "c1": "#000000", "t2": "不过真的需要中止的话为什么不关了呢", "c2": "#ff0000"})
            self.liveVar.set("实时模式")
                
    def log_once(self, lastFile):
        if self.lock.state():
            return
        self.liveListener.getNewBattleLog(self.fileLookUp.basepath, lastFile)
                
    def live_once(self):
        if self.lock.state():
            return
        if not self.startLive:
            config = Config("config.ini")
            self.startLive = True
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            
            self.config = config
            self.fileLookUp = fileLookUp
            
            self.listenThread = threading.Thread(target = self.check_live_quick)
            self.listenThread.start()
            
            self.startLive = True
            
        filelist = os.listdir(self.fileLookUp.basepath)
        dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
        if dataList != []:
            lastFile = dataList[-1]
        else:
            lastFile = ""
        if lastFile != "":
            newestFile = lastFile
            print("Newest File: %s"%lastFile)
            self.listenThread = threading.Thread(target=self.log_once, args = (lastFile,))
            self.listenThread.setDaemon(True);
            self.listenThread.start()
            
    def show_logs(self):
        if self.lock.state():
            return
        if self.playerIDs == [] or True:
            url = "http://%s" % IP
            webbrowser.open(url)
        else:
            # TODO 等logs更新功能后加入
            ids = "+".join(self.playerIDs)
            url = "http://%s/getMultiRank.html?server=%s&ids=%s"%(IP, self.server, ids)
            webbrowser.open(url)
        
    def show_history(self):
        if self.lock.state():
            return
        empty = self.analyser.checkEmpty()
        if empty:
            messagebox.showinfo(title='？', message='还没有成功复盘，请使用“复盘模式”进行记录。')
        else:
            allStatWindow = AllStatWindow(self.analyser, self)
            allStatWindow.start()
        
    def show_last_replay(self):
        if self.lock.state():
            return
        if self.startLive or self.hasReplayed:
            replayWindow = SingleBossWindow(self.liveListener.analyser, -1, self)
            replayWindow.constructReplayByNum(-1)
        else:
            messagebox.showinfo(title='？', message='还没有成功复盘，请使用“复盘模式”进行记录。')
        
    def show_config(self):
        if self.lock.state():
            return
        configWindow = ConfigWindow(self.window)
        configWindow.start()
        
    def show_license(self):
        if self.lock.state():
            return
        licenseWindow = LicenseWindow(self.window, self.lock)
        licenseWindow.start()
        
    def show_announcement(self):
        if self.lock.state():
            return
        announceWindow = AnnounceWindow(self.announcement, self)
        announceWindow.start()
        
    def manual_update(self):
        if self.lock.state():
            return
        webbrowser.open(self.updateurl)
        
    def checkConfig(self):
        if not os.path.isfile("config.ini"):
            time.sleep(0.5)
            configThread = threading.Thread(target=self.show_license)
            configThread.start()
            self.lock.Lock()
        
    def loadWindow(self):
        window = tk.Tk()
        window.title('剑三警长')
        window.geometry('300x220')

        if parseEdition(EDITION) == 0:  # 非联机版本跳过加载步骤
            res = {"announcement": "", "version": "0.0.0", "url": "", "rateEdition": 0}
        else:
            resp = urllib.request.urlopen('http://%s:8009/getAnnouncement' % IP)
            res = json.load(resp)

        self.announcement = res["announcement"]
        self.newestEdition = res["version"]
        self.updateurl = res["url"]
        self.rateEdition = res["rateEdition"]
        checkAndWriteFiles()
        self.stat_percent = checkRateEdition(self.rateEdition)

        self.var1 = tk.StringVar()
        self.var2 = tk.StringVar()

        self.liveVar = tk.StringVar()
        self.liveVar.set("实时模式")

        l = tk.Label(window, text='剑三警长', font=('Arial', 24), width=30, height=2)
        l.pack()

        b1 = tk.Button(window, text='复盘模式', bg='#ccffcc', width=12, height=1, command=self.start_replay)
        b1.pack()
        b2 = tk.Button(window, textvariable=self.liveVar, bg='#ffcccc', width=12, height=1, command=self.start_live)
        b2.pack()

        text1 = tk.Label(window, textvariable=self.var1, width=40, height=1)
        text1.pack()
        self.text1 = text1
        
        text2 = tk.Label(window, textvariable=self.var2, width=40, height=1)
        text2.pack()
        self.text2 = text2
        
        b3 = tk.Button(window, text='总结', height=1, command=self.show_history)
        b3.place(x=180, y=180)
        
        b32 = tk.Button(window, text='复盘', height=1, command=self.show_last_replay)
        b32.place(x=215, y=180)
        
        b4 = tk.Button(window, text='设置', height=1, command=self.show_config)
        b4.place(x=250, y=180)
        
        b5 = tk.Button(window, text='公告', height=1, command=self.show_announcement)
        b5.place(x=250, y=20)
        
        b6 = tk.Button(window, text='logs', height=1, command=self.show_logs)
        b6.place(x=20, y=20)
        
        b7 = tk.Button(window, text='+', bg='#ffcccc', width=1, height=1, command=self.live_once)
        b7.place(x=200, y=108)

        b8 = tk.Button(window, text='+', bg='#ccffcc', width=1, height=1, command=self.replay_select)
        b8.place(x=200, y=78)
        
        showEdition = EDITION
        if parseEdition(EDITION) < parseEdition(self.newestEdition):
            showEdition = "%s(有更新)"%EDITION
            
            b6 = tk.Button(window, text='更新', height=1, command=self.manual_update)
            b6.place(x = 140, y = 180)
            
        l3 = tk.Label(window, text="版本号：%s"%showEdition, height=1)
        l3.place(x = 20, y = 180) 

        self.window = window

        window.protocol('WM_DELETE_WINDOW', self.closeWindow)
        
        self.checkConfig()
        
        window.mainloop()
        
    def __init__(self):
        self.analyser = LiveActorAnalysis()
        self.startLive = False
        self.hasReplayed = False
        self.lock = SingleBlockLocker()  # 简易的互斥锁，用于防止重复启动
        self.playerIDs = []  # 存储玩家ID，用于总榜
        self.hasNoticeXiangzhi = 0  #
        self.bldDict = {}  # 存储处理后的数据，格式为{'文件名': 数据内容}。
        self.playerEquipment = {}  # 存储角色装备，用于导出，将在未来删除
        self.notifier = Notifier()  # 用于win10的通知窗口
        self.dataType = "jx3dat"  # 数据种类，jx3dat为茗伊战斗统计的结果，jcl为茗伊团队工具的子功能
        self.liveListener = None  # 实时模式数据存储，初始时默认为空
        self.lastBld = None  # 中断的战斗记录，默认为空
        self.uploadData = []  # 上传的数据列表，初始为空
        
if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.loadWindow()


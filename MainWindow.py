import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image
import re
import os
import time
#from win10toast import ToastNotifier
from tools.Notifier import Notifier
import traceback
import urllib
import json
import webbrowser

from FileLookUp import FileLookUp
from ConfigTools import Config, ConfigWindow, LicenseWindow, AnnounceWindow
from LiveBase import LiveListener, AllStatWindow, LiveActorAnalysis, SingleBossWindow
from main import OverallReplayer
from Constants import *
from data.DataController import DataController
from tools.Functions import *
from GenerateFiles import *

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
                
    def NoticeXiangZhi(self):
        '''
        在关底BOSS打完后提醒进行奶歌复盘。由BOSS复盘窗口调用。
        '''
        ans = messagebox.askyesno(title='提示', message='副本的关底BOSS已复盘完毕，要进行奶歌复盘吗？')
        if ans:
            self.start_replay()
        else:
            return
            
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

    '''
    def checkAttendence(self):
        rawList = self.rawData
        mapDict = {}
        for key in rawList:
            mapDict[key] = []
            raw = rawList[key]
            name = raw['9'][0]
            occ = raw['10'][0]
            for line in raw['12'][0]['4'][0].keys():
                if line in name and line in occ and occ[line][0] != '0':
                    finalName = name[line][0].strip('"')
                    mapDict[key].append(finalName)
        
        #print(mapDict)
        #g = open("result.txt", "w")
        #g.write(str(mapDict))
        #g.close()
    '''

    def replay(self):
        config = Config("config.ini")
        fileLookUp = FileLookUp()
        fileLookUp.initFromConfig(config)
        self.config = config
        self.fileLookUp = fileLookUp
        self.dataType = self.config.datatype
        # 如需在复盘模式后接实时模式，则使用这个逻辑
        #liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
        #self.liveListener = liveListener
        controller = DataController(self.config)
        if self.bldDict != {}:
            controller.setRawData(self.bldDict)
        controller.replay(self) # 此处将MainWindow类本身传入
        self.setNotice({"t1": "复盘完成！", "c1": "#000000", "t2": ""})
        #self.checkAttendence()

    def start_replay(self):
        if self.lock.state():
            return
        self.setNotice({"t1": "复盘中，请稍候……（时间较久，请耐心等待）", "c1": "#000000"})
        refreshThread = threading.Thread(target = self.replay)    
        refreshThread.start()
        
    def check_live(self):
        numSwitch = 2
        nowStatus = "true"
        if True: # 调试入口
            file = open("%s/config.jx3dat"%self.fileLookUp.basepath, "r")
            s = file.read()
            file.close()
            s = re.sub(r'^(.*)bRecEverything=.{4,5}(.*)bSaveEverything1?=.{4,5}(.*)bREOnlyDungeon=.{4,5},(.*)$', "\\1bRecEverything=false\\2bSaveEverything=false\\3bREOnlyDungeon=true,\\4", s)
            file = open("%s/config.jx3dat"%self.fileLookUp.basepath, "w")
            file.write(s)
            file.close()
        while(True): # 调试入口
            #break
            time.sleep(1)
            try:
                file = open("%s/config.jx3dat"%self.fileLookUp.basepath, "r")
                s = file.read()
                res = re.search(r'bRecEverything=(.{4,5}).*bSaveHistoryOnExFi=(.{4,5}).*nMaxHistory=([0-9]+),nMinFightTime=([0-9\-]+),bSaveEverything1?=(.{4,5}).*bREOnlyDungeon=(.{4,5}),', s)
                file.close()
                if res:
                    if res.group(1) == "false":
                        self.setNotice({"t1": "请勾选[记录所有复盘数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    elif res.group(5) == "false":
                        self.setNotice({"t1": "请取消[不保存历史复盘数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    elif res.group(2) == "false":
                        self.setNotice({"t1": "请勾选[脱离战斗时保存数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    elif int(res.group(3)) < 50 and self.config.plugindetail:
                        self.setNotice({"t1": "请将[最大历史记录设置]设为50以上。", "c1": "#000000", "t2": "可以在[设置]中设定跳过本步。", "c2": "#ff0000"})
                    elif int(res.group(4)) > 10 and self.config.plugindetail:
                        self.setNotice({"t1": "请将[过滤短时战斗]设为10秒以下。", "c1": "#000000", "t2": "可以在[设置]中设定跳过本步。", "c2": "#ff0000"})
                    else:
                        if res.group(6) == "true" and nowStatus == "false":
                            nowStatus = "true"
                            numSwitch -= 1
                        elif res.group(6) == "false" and nowStatus == "true":
                            nowStatus = "false"
                            numSwitch -= 1
                        if numSwitch > 0:
                            self.setNotice({"t1": "请改变[仅在秘境中启用复盘]，剩余：%d"%numSwitch, "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                        else:
                            break
                else:
                    self.setNotice({"t1": "设置文件结构不正确，请尝试更新茗伊插件集。", "c1": "#000000", "t2": "通常这是因为角色路径没有选取正确。", "c2": "#ff0000"})
            except:
                print("文件读取错误，稍后重试……")
                traceback.print_exc()
        self.setNotice({"t1": "选项设置完成，开始实时模式……", "c1": "#000000", "t2": "开启成功！", "c2": "#00ff00"})

        #toaster = ToastNotifier()
        #toaster.show_toast("选项设置完成", "选项验证正确，可以在游戏中开战并分锅啦~", icon_path='jx3bla.ico')
        self.notifier.show("选项设置完成", "选项验证正确，可以在游戏中开战并分锅啦~")
        
        liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
        self.liveListener = liveListener
        liveListener.startListen()
        
    def check_live_quick(self):
        if self.lock.state():
            return
        liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser, self)
        self.liveListener = liveListener
        messagebox.showinfo(title='警告', message='快速实时模式主要用于调试，如果不了解原理，有极大概率无法正常运行。')
        
        liveListener.startListen()
        self.setNotice({"t1": "快速实时模式已开启，请关注终端界面……", "c1": "#000000", "t2": "快速模式仅用于调试，新手勿入QAQ", "c2": "#ff0000"})
        
    def start_live(self):
        if self.lock.state():
            return
        if not self.startLive:
            config = Config("config.ini")
            self.startLive = True
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            self.dataType = self.config.datatype
            self.config = config
            self.fileLookUp = fileLookUp
            
            l = os.listdir(fileLookUp.basepath)
            if "config.jx3dat" not in l:# and False: # 调试入口
                self.setNotice({"t1": "实时模式需要设置路径为实时路径。", "c1": "#000000", "t2": "通常应当选取fight_stat为基准目录", "c2": "#ff0000"})
                self.startLive = False
            else:
                self.setNotice({"t1": "请在游戏中设置复盘选项，才能开启实时模式。", "c1": "#000000"})
                self.listenThread = threading.Thread(target = self.check_live)
                self.listenThread.start()
                
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
            self.listenThread = threading.Thread(target = self.log_once, args = (lastFile,)) 
            self.listenThread.setDaemon(True);
            self.listenThread.start()
            
    def show_tianwang(self):
        if self.lock.state():
            return
        if self.playerIDs == []:
            url = "http://139.199.102.41:8009/TianwangSearch.html"
            webbrowser.open(url)
            #messagebox.showinfo(title='提示', message='需要有实时战斗记录才能使用天网系统。在目前的版本中，建议取消最短战斗时间限制，使用七苦一乐宝箱作为检测工具。')
        else:
            ids = "+".join(self.playerIDs)
            url = "http://139.199.102.41:8009/Tianwang.html?server=%s&ids=%s"%(self.server, ids)
            webbrowser.open(url)
        
    def show_history(self):
        if self.lock.state():
            return
        allStatWindow = AllStatWindow(self.analyser, self)
        allStatWindow.start()
        
    def show_last_replay(self):
        if self.lock.state():
            return
        if self.startLive or self.hasReplayed:
            replayWindow = SingleBossWindow(self.liveListener.analyser, -1, self)
            replayWindow.constructReplayByNum(-1)
        
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
            configThread = threading.Thread(target = self.show_license)    
            configThread.start()
            self.lock.Lock()
        
    def loadWindow(self):
        window = tk.Tk()
        window.title('剑三警长')
        window.geometry('300x220')
        
        #resp = urllib.request.urlopen('http://139.199.102.41:8009/getAnnouncement')
        #res = json.load(resp)
        res = {"announcement": "", "version": "0.0.0", "url": ""}  #TODO: 联机版中fix this
        self.announcement = res["announcement"]
        self.newestEdition = res["version"]
        self.updateurl = res["url"]
        checkAndWriteFiles()

        self.var1 = tk.StringVar()
        self.var2 = tk.StringVar()

        l = tk.Label(window, text='剑三警长', font=('Arial', 24), width=30, height=2)
        l.pack()

        b1 = tk.Button(window, text='复盘模式', bg='#ccffcc', width=12, height=1, command=self.start_replay)
        b1.pack()
        b2 = tk.Button(window, text='实时模式', bg='#ffcccc', width=12, height=1, command=self.start_live)
        b2.pack()

        text1 = tk.Label(window, textvariable=self.var1, width=40, height=1)
        text1.pack()
        self.text1 = text1
        
        text2 = tk.Label(window, textvariable=self.var2, width=40, height=1)
        text2.pack()
        self.text2 = text2
        
        b3 = tk.Button(window, text='总结', height=1, command=self.show_history)
        b3.place(x = 180, y = 180)
        
        b32 = tk.Button(window, text='复盘', height=1, command=self.show_last_replay)
        b32.place(x = 215, y = 180)
        
        b4 = tk.Button(window, text='设置', height=1, command=self.show_config)
        b4.place(x = 250, y = 180)
        
        b5 = tk.Button(window, text='公告', height=1, command=self.show_announcement)
        b5.place(x = 250, y = 20)
        
        b6 = tk.Button(window, text='天网', height=1, command=self.show_tianwang)
        b6.place(x = 20, y = 20)
        
        b7 = tk.Button(window, text='+', bg='#ffcccc', width=1, height=1, command=self.live_once)
        b7.place(x = 200, y = 108)
        
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
        
if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.loadWindow()


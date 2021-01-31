import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image
import re
import os
import time
from win10toast import ToastNotifier
import traceback
import urllib
import json
import webbrowser

from FileLookUp import FileLookUp
from ConfigTools import Config, ConfigWindow, LicenseWindow, AnnounceWindow
from LiveBase import LiveListener, AllStatWindow, LiveActorAnalysis
from main import replay_by_window
from Constants import *
from Functions import *
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

    def replay(self):
        replay_by_window(self)
        self.setNotice({"t1": "复盘完成！", "c1": "#000000", "t2": ""})

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
                res = re.search(r'bRecEverything=(.{4,5}).*bSaveHistoryOnExFi=(.{4,5}).*bSaveEverything1?=(.{4,5}).*bREOnlyDungeon=(.{4,5}),', s)
                file.close()
                if res:
                    if res.group(1) == "false":
                        self.setNotice({"t1": "请勾选[记录所有复盘数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    elif res.group(3) == "false":
                        self.setNotice({"t1": "请取消[不保存历史复盘数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    elif res.group(2) == "false":
                        self.setNotice({"t1": "请勾选[脱离战斗时保存数据]。", "c1": "#000000", "t2": "点击[公告]以获取教程。", "c2": "#ff0000"})
                    else:
                        if res.group(4) == "true" and nowStatus == "false":
                            nowStatus = "true"
                            numSwitch -= 1
                        elif res.group(4) == "false" and nowStatus == "true":
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
        self.setNotice({"t1": "选项设置完成，开始实时模式……", "c1": "#000000"})
        #print("由于图标设置异常，请忽略与jx3bla.ico相关的报错，其对使用不会产生实质性影响。")
        toaster = ToastNotifier()
        toaster.show_toast("选项设置完成", "选项验证正确，可以在游戏中开战并分锅啦~", icon_path='jx3bla.ico')
        
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
        
    def show_history(self):
        if self.lock.state():
            return
        allStatWindow = AllStatWindow(self.analyser)
        allStatWindow.start()
        
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
        announceWindow = AnnounceWindow(self.announcement)
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
        
        resp = urllib.request.urlopen('http://139.199.102.41:8009/getAnnouncement')
        res = json.load(resp)
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
        
        b3 = tk.Button(window, text='分锅结果', height=1, command=self.show_history)
        b3.place(x = 180, y = 180)
        
        b4 = tk.Button(window, text='设置', height=1, command=self.show_config)
        b4.place(x = 250, y = 180)
        
        b5 = tk.Button(window, text='公告', height=1, command=self.show_announcement)
        b5.place(x = 250, y = 20)
        
        b6 = tk.Button(window, text='+', bg='#ffcccc', width=1, height=1, command=self.live_once)
        b6.place(x = 200, y = 108)
        
        showEdition = EDITION
        if parseEdition(EDITION) < parseEdition(self.newestEdition):
            showEdition = "%s(有更新)"%EDITION
            
            b6 = tk.Button(window, text='更新', height=1, command=self.manual_update)
            b6.place(x = 140, y = 180)
            
        l3 = tk.Label(window, text="版本号：%s"%showEdition, height=1)
        l3.place(x = 20, y = 180) 
        
        #b5 = tk.Button(window, text='协议', height=1, command=self.show_license)
        #b5.place(x = 120, y = 180)
        
        self.window = window

        window.protocol('WM_DELETE_WINDOW', self.closeWindow)
        
        self.checkConfig()
        
        window.mainloop()
        
    def __init__(self):
        self.analyser = LiveActorAnalysis()
        self.startLive = False
        self.lock = SingleBlockLocker()
        
if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.loadWindow()


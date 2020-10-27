import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image
import re
import os
import time
from win10toast import ToastNotifier
import traceback

from FileLookUp import FileLookUp
from ConfigTools import Config, ConfigWindow, LicenseWindow
from LiveBase import LiveListener, AllStatWindow, LiveActorAnalysis
from main import replay_by_window

class MainWindow():

    def closeWindow(self):
        ans = messagebox.askyesno(title='提示', message='确定要关闭吗？')
        if ans:
            self.window.destroy()
        else:
            return

    def replay(self):
        replay_by_window()
        self.var.set("复盘完成！")

    def start_replay(self):
        self.var.set("复盘中，请稍候……（时间较久，请耐心等待）")
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
            time.sleep(3)
            try:
                file = open("%s/config.jx3dat"%self.fileLookUp.basepath, "r")
                s = file.read()
                res = re.search(r'bRecEverything=(.{4,5}).*bSaveHistoryOnExFi=(.{4,5}).*bSaveEverything1?=(.{4,5}).*bREOnlyDungeon=(.{4,5}),', s)
                file.close()
                if res:
                    if res.group(1) == "false":
                        self.var.set("请勾选[记录所有复盘数据]。")
                    elif res.group(3) == "false":
                        self.var.set("请取消[不保存历史复盘数据]。")
                    elif res.group(2) == "false":
                        self.var.set("请勾选[脱离战斗时保存数据]。")
                    else:
                        if res.group(4) == "true" and nowStatus == "false":
                            nowStatus = "true"
                            numSwitch -= 1
                        elif res.group(4) == "false" and nowStatus == "true":
                            nowStatus = "false"
                            numSwitch -= 1
                        if numSwitch > 0:
                            self.var.set("请改变[仅在秘境中启用复盘]，剩余：%d"%numSwitch)
                        else:
                            break
                else:
                    self.var.set("设置文件结构不正确，请尝试更新茗伊插件集。")
            except:
                print("文件读取错误，稍后重试……")
                traceback.print_exc()
        self.var.set("选项设置完成，开始实时模式……")
        toaster = ToastNotifier()
        toaster.show_toast("选项设置完成", "选项验证正确，可以在游戏中开战并分锅啦~", icon_path='')
        
        liveListener = LiveListener(self.fileLookUp.basepath, self.config, self.analyser)
        liveListener.startListen()
        
    def start_live(self):
        if not self.startLive:
            #try:
            config = Config("config.ini")
            #except:
            #    var.set("配置文件错误，请按指示设置")
            #    return
            self.startLive = True
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            
            self.config = config
            self.fileLookUp = fileLookUp
            
            l = os.listdir(fileLookUp.basepath)
            if "config.jx3dat" not in l:# and False: # 调试入口
                self.var.set("实时模式需要设置路径为实时路径。")
                self.startLive = False
            else:
                self.var.set("请在游戏中设置复盘选项，才能开启实时模式。")
                self.listenThread = threading.Thread(target = self.check_live)
                self.listenThread.start()
        
    def show_history(self):
        allStatWindow = AllStatWindow(self.analyser)
        allStatWindow.start()
        
    def show_config(self):
        configWindow = ConfigWindow()
        configWindow.start()
        
    def show_license(self):
        licenseWindow = LicenseWindow()
        licenseWindow.start()
        
    def loadWindow(self):
        window = tk.Tk()
        window.title('剑三警长')
        window.geometry('300x200')

        self.var = tk.StringVar()

        l = tk.Label(window, text='剑三警长', font=('Arial', 24), width=30, height=2)
        l.pack()

        b1 = tk.Button(window, text='复盘模式', bg='#ccffcc', width=12, height=1, command=self.start_replay)
        b1.pack()
        b2 = tk.Button(window, text='实时模式', bg='#ffcccc', width=12, height=1, command=self.start_live)
        b2.pack()

        l = tk.Label(window, textvariable=self.var, width=40, height=1)
        l.pack()
        
        b3 = tk.Button(window, text='分锅结果', height=1, command=self.show_history)
        b3.place(x = 180, y = 160)
        
        b4 = tk.Button(window, text='设置', height=1, command=self.show_config)
        b4.place(x = 250, y = 160)
        
        b5 = tk.Button(window, text='协议', height=1, command=self.show_license)
        b5.place(x = 120, y = 160)
        
        self.window = window

        window.protocol('WM_DELETE_WINDOW', self.closeWindow)
        window.mainloop()
        
    def __init__(self):
        self.analyser = LiveActorAnalysis()
        self.startLive = False
        
if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.loadWindow()


# Created by moeheart at 08/08/2022
# 添加锅的窗口实现类.

import tkinter as tk
from tkinter import ttk
from window.Window import Window

class PotExtendWindow(Window):
    '''
    锅的扩展窗口类。用于维护添加锅的窗体.
    '''

    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''
        self.windowAlive = False
        self.singleBossWindow.potExtendRunning = False
        self.window.destroy()

    def Act(self):
        '''
        实施加锅。
        '''
        playerID = self.playerValue.get()
        potLevel = self.lvlValue.get()
        potDescription = "[手动]" + self.descEntry.get()
        try:
            score = int(self.scoreEntry.get())
        except:
            score = 0

        potLevelNum = 1
        if potLevel == "轻微":
            potLevelNum = 0
        elif potLevel == "严重":
            potLevelNum = 1
        elif potLevel == "补贴":
            potLevelNum = 3

        if playerID in self.playerIDDict:
            playerOcc = self.playerIDDict[playerID]
            self.pot = [playerID, playerOcc, potLevelNum, self.bossName, potDescription, []]
            self.singleBossWindow.AddPot(self.pot, score)
        self.final()

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('加锅')
        window.geometry('300x120')

        tk.Label(window, text="玩家ID", height=1).grid(row=0, column=0)
        self.playerValue = tk.StringVar()
        playerCombobox = ttk.Combobox(window, textvariable=self.playerValue)
        playerCombobox["values"] = self.playerIDList
        playerCombobox.current(0)
        playerCombobox.grid(row=0, column=1)

        tk.Label(window, text="分锅描述", height=1).grid(row=1, column=0)
        self.descEntry = tk.Entry(window, show=None)
        self.descEntry.grid(row=1, column=1)

        tk.Label(window, text="分锅等级", height=1).grid(row=2, column=0)
        self.lvlValue = tk.StringVar()
        lvlCombobox = ttk.Combobox(window, textvariable=self.lvlValue)
        lvlCombobox["values"] = ("严重", "轻微", "补贴")
        lvlCombobox.current(0)
        lvlCombobox.grid(row=2, column=1)

        tk.Label(window, text="评分", height=1).grid(row=3, column=0)
        self.scoreEntry = tk.Entry(window, show=None)
        self.scoreEntry.grid(row=3, column=1)

        tk.Button(window, text='加锅', width=10, height=1, command=self.Act).grid(row=4, column=0)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, singleBossWindow):
        super().__init__()
        self.singleBossWindow = singleBossWindow
        self.playerList = singleBossWindow.analyser.getPlayer()
        self.playerIDDict = {}
        self.playerIDList = []
        for line in self.playerList:
            self.playerIDDict[line[0]] = line[1]
            self.playerIDList.append(line[0])
        self.bossName = singleBossWindow.detail["boss"]
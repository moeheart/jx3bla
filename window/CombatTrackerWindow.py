# Created by moeheart at 07/30/2022
# 数值统计的窗口文件.

import tkinter as tk
from tkinter import ttk
import os
import re
from tools.Functions import *
import threading
from tkinter import messagebox
from tools.StaticJson import *
from functools import partial
from replayer.TableConstructor import ToolTip

class CombatTrackerWindow():
    '''
    专案组窗口的展示类.
    '''

    def final(self):
        '''
        关闭窗口。
        '''
        if self.windowAlive:
            self.window.destroy()
            self.windowAlive = False

    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def handler_adaptor(self, fun,  **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

    def handler(self, event, id):
        """事件处理函数"""
        self.setPlayer(id)

    def setStat(self, stat):
        '''
        使上半部分显示指定的统计类型.
        '''
        self.stat = stat
        assert stat in ["rhps", "hps", "ahps", "ohps"]
        if stat == "rhps":
            data = self.act.rhps
        elif stat == "hps":
            data = self.act.hps
        elif stat == "ahps":
            data = self.act.ahps
        elif stat == "ohps":
            data = self.act.ohps
        self.data = data
        dataT = []
        for key in data["player"]:
            dataT.append([key, data["player"][key]])
        dataT.sort(key=lambda x:-x[1]["sum"])

        max = 0
        maxID = ""
        highlightAppear = 0
        for i in range(25):
            if i < len(dataT):
                name = dataT[i][1]["name"]
                self.bars[i][0].configure(text=name)
                value = dataT[i][1]["hps"]
                self.bars[i][2].configure(text="%d" % value)
                if max == 0:
                    max = value
                    maxID = dataT[i][0]
                rate = value / max
                self.bars[i][1]['value'] = rate
                occ = dataT[i][1]["occ"]
                self.bars[i][1].configure(style="bar%s.Horizontal.TProgressbar" % occ)
                self.bars[i][1].bind('<Button-1>', self.handler_adaptor(self.handler, id=dataT[i][0]))
                self.bars[i][3] = dataT[i][0]
                if dataT[i][0] == self.highlightPlayer:
                    highlightAppear = 1
            else:
                self.bars[i][0].configure(text="")
                self.bars[i][2].configure(text="")
                self.bars[i][1]['value'] = 0
                self.bars[i][3] = ""

        if highlightAppear:
            self.setPlayer(self.highlightPlayer)
        elif maxID != "":
            self.setPlayer(maxID)

    def setPlayer(self, id):
        '''
        使下半部分显示对应玩家的统计类型.
        '''
        data = self.data
        dataT = []
        for key in data["player"][id]["namedSkill"]:
            dataT.append([key, data["player"][id]["namedSkill"][key]])
        dataT.sort(key=lambda x: -x[1]["sum"])
        for i in range(50):
            if i < len(dataT):
                name = dataT[i][0]
                self.table[i][0].configure(text=name)
                num = dataT[i][1]["num"]
                self.table[i][1].configure(text="%d" % num)
                sum = dataT[i][1]["sum"]
                self.table[i][2].configure(text="%d" % sum)
                sumPerSec = int(sum / self.act.time * 1000)
                self.table[i][3].configure(text="%d" % sumPerSec)
                percent = dataT[i][1]["percent"]
                self.table[i][4].configure(text=parseCent(percent) + '%')
            else:
                self.table[i][0].configure(text="")
                self.table[i][1].configure(text="")
                self.table[i][2].configure(text="")
                self.table[i][3].configure(text="")
                self.table[i][4].configure(text="")

        for i in range(25):
            if self.bars[i][3] == id:
                self.bars[i][0].configure(bg='#777777')
                self.bars[i][2].configure(bg='#777777')
            else:
                self.bars[i][0].configure(bg='#f0f0f0')
                self.bars[i][2].configure(bg='#f0f0f0')
        self.highlightPlayer = id

    def loadWindow(self):
        '''
        使用tkinter绘制窗口。
        '''

        window = tk.Toplevel()
        window.title('战斗统计')
        window.geometry('580x700')
        window.protocol('WM_DELETE_WINDOW', self.final)
        self.window = window

        # 上半部分

        frameUp = tk.Frame(window, width=560, height=300)
        frameUp.place(x=0, y=0)

        frameButtons = tk.Frame(frameUp, width=560, height=50)
        frameButtons.place(x=0, y=0)

        f = partial(self.setStat, "rhps")
        b = tk.Button(frameButtons, text='rHPS', height=1, command=f, bg='#00ff77')
        ToolTip(b, "全称raid HPS，是综合考虑有效治疗量、化解、减伤、以及安全范围内的溢出治疗量后得到的值。\nrHPS与对团血的贡献程度完全成正比。在承伤与配置不变的情况下，使rHPS更高的手法就能使团血更稳。")
        b.place(x=30, y=20)
        f = partial(self.setStat, "hps")
        b2 = tk.Button(frameButtons, text='HPS', height=1, command=f, bg='#00ff77')
        ToolTip(b2, "与游戏中[有效HPS]接近的值。相比于插件的统计，其考虑了吸血、蛊惑等隐藏数值，因此与游戏中会有细微的不同。")
        b2.place(x=80, y=20)
        f = partial(self.setStat, "ahps")
        b3 = tk.Button(frameButtons, text='aHPS', height=1, command=f, bg='#00ff77')
        ToolTip(b3, "全称absorb HPS，包括化解、减伤、响应式治疗。游戏中的APS漏洞百出，而aHPS可以更准确地反应这些被抵消的伤害。")
        b3.place(x=130, y=20)
        f = partial(self.setStat, "ohps")
        b4 = tk.Button(frameButtons, text='oHPS', height=1, command=f, bg='#00ff77')
        ToolTip(b4, "全称over HPS，指包含溢出的治疗量，也即游戏中的虚条。oHPS与aHPS之和决定了承伤的上限。")
        b4.place(x=180, y=20)

        canvas = tk.Canvas(frameUp, width=560, height=250, scrollregion=(0, 0, 540, 25*25)) #创建canvas
        canvas.place(x=0, y=50)  # 放置canvas的位置
        frameBar = tk.Frame(canvas)  # 把frame放在canvas里
        frameBar.place(width=540, height=250) #frame的长宽，和canvas差不多的
        vbar = tk.Scrollbar(canvas, orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x=540, width=20, height=250)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置
        canvas.create_window((270, 25*25*0.5), window=frameBar)  #create_window

        s = ttk.Style()
        s.theme_use('clam')
        s.configure("TProgressbar", thickness=30)
        for i in [0,1,2,3,4,5,6,7,8,9,10,21,22,23,24,25,211,212]:
            color = getColor(str(i))
            s.configure("bar%d.Horizontal.TProgressbar" % i, background=color, lightcolor=color,
                darkcolor=color)

        self.frameBar = frameBar
        self.bars = []
        for i in range(25):
            frameSingleBar = tk.Frame(frameBar)
            name = tk.Label(frameSingleBar, text="placeholder", width=20)
            name.grid(row=0, column=0)

            progressBar = ttk.Progressbar(frameSingleBar, style="bar0.Horizontal.TProgressbar",
                                          orient="horizontal", length=200)
            progressBar['maximum'] = 1
            progressBar['value'] = 0.5
            progressBar.grid(row=0, column=1)

            value = tk.Label(frameSingleBar, text="0", width=20)
            value.grid(row=0, column=2)

            frameSingleBar.grid(row=i, column=0)
            self.bars.append([name, progressBar, value, "", frameSingleBar])

        # 下半部分
        frameDown = tk.Frame(window, width=560, height=350)
        frameDown.place(x=0, y=300)

        canvas = tk.Canvas(frameDown, width=560, height=350, scrollregion=(0, 0, 540, 24*50)) #创建canvas
        canvas.place(x=0, y=50)  # 放置canvas的位置
        frameTable = tk.Frame(canvas)  # 把frame放在canvas里
        frameTable.place(width=540, height=350) #frame的长宽，和canvas差不多的
        vbar = tk.Scrollbar(canvas, orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x=540, width=20, height=350)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置
        canvas.create_window((270, 24*50*0.5), window=frameTable)  #create_window

        l = tk.Label(frameTable, text="技能")
        l.grid(row=0, column=0)
        l = tk.Label(frameTable, text="次数")
        l.grid(row=0, column=1)
        l = tk.Label(frameTable, text="数值")
        l.grid(row=0, column=2)
        l = tk.Label(frameTable, text="每秒")
        l.grid(row=0, column=3)
        l = tk.Label(frameTable, text="比例")
        l.grid(row=0, column=4)
        self.table = []
        for i in range(50):
            l1 = tk.Label(frameTable, text="xxx", width=20)
            l1.grid(row=i+1, column=0)
            l2 = tk.Label(frameTable, text="xxx", width=5)
            l2.grid(row=i+1, column=1)
            l3 = tk.Label(frameTable, text="xxx", width=20)
            l3.grid(row=i+1, column=2)
            l4 = tk.Label(frameTable, text="xxx", width=10)
            l4.grid(row=i+1, column=3)
            l5 = tk.Label(frameTable, text="xxx", width=10)
            l5.grid(row=i+1, column=4)
            self.table.append([l1, l2, l3, l4, l5])

        self.setStat("rhps")

    def __init__(self, act):
        '''
        构造方法.
        '''
        self.act = act
        self.highlightPlayer = ""
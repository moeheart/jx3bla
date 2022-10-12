# Created by moeheart at 08/08/2022
# 协议窗口类.

import tkinter as tk
from tkinter import messagebox

from ConfigTools import Config
from window.Window import Window

class LicenseWindow(Window):
    """
    用户协议窗口类，用于展示用户协议与交互。
    """

    license_fake = """
************************************************************
|                     剑三警长 使用协议                      |
************************************************************
    剑三警长是一款剑网三战斗日志分析工具，在使用本工具之前，我
们需要部分授权，需要您的同意：
    1. 您授权将游戏账号下的所有不绑定道具，包括但不限于：金币、
五行石、不绑定装备、外观礼盒，全部邮寄给开发者作为开发报酬。
    2. 您知晓并同意，本协议只用于测试您是否认真阅读了条款，请
点击下方复选框10次以获取真实的协议。
    3. 为了数据对比，您授权将自己及情缘的所有信息向作者公开，
并对之后可能引发的818放弃所有保留的权利。
    4. 本协议仅对jx3bla主仓库的主分支有效，开发者如果需要修改
代码，需要同时维护此协议，否则视为本协议无效。
************************************************************
"""
    license_true = """
************************************************************
|                     剑三警长 使用协议                      |
************************************************************
    剑三警长是一款剑网三战斗日志分析工具，在使用本工具之前，我
们需要部分授权，需要您的同意：
    1. 本工具会读取茗伊插件集生成的战斗复盘日志，其中的信息包
括但不限于：全部技能与buff的时间与数值、玩家ID与门派、区服、
重伤记录。这些读取的内容只会在本地进行运算。
    2. 本工具会上传战斗复盘结果图中的所有信息到作者的服务器，
包括但不限于：DPS/HPS统计，区服，玩家ID与门派，打分，犯错记录。
收集这些信息是为了进行进一步研究，对之后的的开发提供数据支持。
由于上传的数据只有全局信息，因此您无需担心打法被泄漏。
    3. 对于上传的数据，可能会以HPS天梯/评分百分比的形式，进行
数据公开。作者在公开数据时，有对玩家个人信息进行保密的义务，
包括玩家ID与团队构建等信息，应在去特征化后再发布。但演员不在此
列，对于表现明显低于正常水平的玩家，可能会有其它安排。
    4. 即使没有显式同意本协议，使用本工具依然需要协议的内容经
过授权。尝试绕过本协议并不能免除您的义务。
    5. 本协议仅对jx3bla主仓库的主分支有效，开发者如果需要修改
代码，需要同时维护此协议，否则视为本协议无效。
************************************************************
"""

    def final(self):
        messagebox.showinfo(title='杯具了', message='本工具依赖于用户协议中的部分项目，必须同意才可以运行。')
        self.window.destroy()
        self.mainWindow.destroy()

    def init_checkbox(self, box, value):
        if value == 0:
            box.deselect()
        else:
            box.select()

    def hit_ok(self):
        if not self.genius:
            messagebox.showinfo(title='你是认真的吗', message='请认真阅读用户协议。')
            self.window.destroy()
            self.mainWindow.destroy()
        elif not self.var.get():
            self.final()
        else:
            Config("config.ini", 1)
            self.lock.Unlock()
            self.window.destroy()

    def hit_cancel(self):
        self.final()

    def hit_box(self, dummy):
        self.numBox += 1
        if self.numBox >= 10 and not self.genius:
            self.genius = 1
            self.cb.deselect()
            self.label.configure(text=self.license_true)

    def loadWindow(self):
        '''
        弹出用户协议界面。
        '''
        self.numBox = 0
        self.genius = 0
        window = tk.Toplevel()
        window.title('用户协议')
        window.geometry('500x400')

        l = tk.Label(window, text=self.license_fake, font=('宋体', 10), width=60, bg='#ffffff', anchor='nw',
                     justify=tk.LEFT)
        l.pack()
        self.label = l

        self.var = tk.IntVar(window)
        self.cb = tk.Checkbutton(window, text="同意上述协议", variable=self.var, onvalue=1, offvalue=0)
        self.cb.bind("<Button-1>", self.hit_box)
        self.cb.pack()

        b1 = tk.Button(window, text='完成', height=1, command=self.hit_ok)
        b1.place(x=200, y=350)

        b2 = tk.Button(window, text='关闭', height=1, command=self.hit_cancel)
        b2.place(x=250, y=350)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, mainWindow, lock):
        super().__init__()
        self.mainWindow = mainWindow
        self.lock = lock
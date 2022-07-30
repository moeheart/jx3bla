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

    def loadWindow(self):
        '''
        使用tkinter绘制窗口。
        '''

        print("[LoadWindowTest]", self.act.rhps["sumHps"])

        window = tk.Toplevel()
        window.title('战斗统计')

        window.geometry('580x800')
        window.protocol('WM_DELETE_WINDOW', self.final)
        self.window = window

    def __init__(self, act):
        '''
        构造方法.
        '''
        self.act = act
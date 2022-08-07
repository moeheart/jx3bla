# Created by moeheart at 08/07/2022
# 所有“子窗口”(tk.Toplevel)的基类。实现了子窗口的基本功能。所有窗口类都应该由此派生.

import threading
import tkinter as tk

class Window():
    '''
    窗口基类.
    '''

    def final(self):
        '''
        关闭窗口.
        '''
        self.windowAlive = False
        self.window.destroy()

    def start(self):
        '''
        显示窗口.
        '''
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def alive(self):
        '''
        判断窗口是否存活.
        '''
        return self.windowAlive

    def __init__(self):
        '''
        初始化.
        '''
        self.windowAlive = False
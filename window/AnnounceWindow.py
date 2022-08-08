# Created by moeheart at 08/08/2022
# 公告窗口类.

import tkinter as tk
import webbrowser

from window.Window import Window

class AnnounceWindow(Window):
    '''
    公告窗口类，提供公告窗口的展示。
    现有的公告窗口拼凑了较多的功能，之后可能会改名。
    '''

    def show_tutorial(self):
        webbrowser.open("https://www.jx3box.com/bps/31349")

    def show_help(self):
        webbrowser.open("https://wwe.lanzouy.com/iKY8Ayggt4j")

    def show_update(self):
        webbrowser.open("https://github.com/moeheart/jx3bla/blob/master/update.md")

    def loadWindow(self):
        '''
        使用tkinter绘制公告窗口。
        '''
        window = tk.Toplevel()
        window.title('公告')
        window.geometry('400x200')

        self.window = window

        l = tk.Message(window, text=self.announcement, font=('宋体', 10), width=380, anchor='nw', justify=tk.LEFT)
        l.pack()
        self.label = l

        l2 = tk.Message(window, text="反馈QQ群：418483739", font=('宋体', 10), width=380, anchor='nw', justify=tk.LEFT)
        l2.place(x=30, y=140)

        b3 = tk.Button(window, text='复盘指南', height=1, command=self.show_tutorial)
        b3.place(x=50, y=160)

        b4 = tk.Button(window, text='帮助文档', height=1, command=self.show_help)
        b4.place(x=123, y=160)

        b5 = tk.Button(window, text='更新内容', height=1, command=self.show_update)
        b5.place(x=196, y=160)

        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, announcement, mainWindow):
        super().__init__()
        self.announcement = announcement
        self.mainWindow = mainWindow
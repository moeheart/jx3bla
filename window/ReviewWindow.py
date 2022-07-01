# Created by moeheart at 07/01/2022
# 专案组模块的窗口文件.

import tkinter as tk
from tkinter import ttk
import os
from tools.Functions import *
import threading
import pyperclip
from tkinter import messagebox
from tools.StaticJson import *

class ReviewerWindow():
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

    def renderText(self, review, text):
        '''
        按照text中指定的格式从review中提取对应的信息填入.
        params:
        - review: 专案组提供的反馈建议类.
        - text: 需要替换的文本.
        returns:
        - 替换完成的文本.
        '''
        return text  # TODO

    def loadWindow(self):
        '''
        使用tkinter绘制窗口。
        '''
        height = 20
        nowHeight = 20

        window = tk.Toplevel()
        window.title('专案组')
        self.window = window

        result = self.result
        for review in result["review"]["content"]:
            code = str(review["code"])
            if code in self.json:
                std = self.json[code]
                title = std["title"]
                rate = review["rate"]
                rateCent = parseCent(rate)
                status = review["status"]

                frame = tk.Frame(window, width=730, height=100, highlightthickness=1, highlightbackground=self.color)
                frame.place(x=20, y=nowHeight)

                tk.Label(frame, text=title).grid(row=0, column=0)
                tk.Label(frame, text=rateCent).grid(row=0, column=1)

                if "descCondition" in std and status in std["descCondition"]:
                    # 加入描述
                    text = self.renderText(review, std["desc"])
                    ttk.Label(frame, text=text, wraplength=700).grid(row=1, column=0)

                if "addCondition" in std and status in std["addCondition"]:
                    # 加入额外信息
                    text = self.renderText(review, std["add"])
                    ttk.Label(frame, text=text, wraplength=700).grid(row=2, column=0)

                nowHeight += 100
                height += 100

        window.geometry('780x%d' % height)
        window.protocol('WM_DELETE_WINDOW', self.final)

    def preloadJson(self):
        '''
        重新处理review的形式.
        '''
        self.json = {}
        for line in REVIEW_JSON["content"]:
            code = str(line["code"])
            res = {}
            for key in line:
                if key != "code":
                    res[key] = line[key]
            self.json[code] = res

    def __init__(self, result, color):
        '''
        构造方法.
        params:
        - result: 复盘结果dict.
        - color: 主题颜色.
        '''
        self.result = result
        self.color = color
        self.preloadJson()
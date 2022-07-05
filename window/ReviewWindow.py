# Created by moeheart at 07/01/2022
# 专案组模块的窗口文件.

import tkinter as tk
from tkinter import ttk
import os
import re
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

    def renderText(self, review, text, array=0):
        '''
        按照text中指定的格式从review中提取对应的信息填入.
        params:
        - review: 专案组提供的反馈建议类.
        - text: 需要替换的文本.
        returns:
        - 替换完成的文本.
        '''
        resultList = []
        endFlag = 0
        i = 0
        num = 0
        while num < 100:
            result = text
            while num < 100:
                num += 1
                regex = re.search(r"`(.+?)`", result)
                if not regex:
                    break
                key = regex.group(1)
                if key in review:
                    if not array:
                        value = review[key]
                    else:
                        if i < len(review[key]):
                            value = review[key][i]
                        else:
                            endFlag = 1
                            break
                    if type(value) is type(0.0) and value < 1:
                        valueStr = parseCent(value) + '%'
                    else:
                        valueStr = str(value)
                else:
                    valueStr = "[%s]" % key
                result = re.sub(r"`%s`" % key, valueStr, result)
            if endFlag:
                break
            resultList.append(result)
            i += 1
            if not array:
                break

        result = '\n'.join(resultList)
        return result

    def loadWindow(self):
        '''
        使用tkinter绘制窗口。
        '''
        height = 20
        nowHeight = 20

        window = tk.Toplevel()
        window.title('专案组')
        self.window = window

        BAR_STATUS = ["#22b14c", "#0077ff", "#ff7700", "#ff0000"]

        s = ttk.Style()
        s.theme_use('clam')
        for i in range(4):
            s.configure("bar%d.Horizontal.TProgressbar" % i, background=BAR_STATUS[i], lightcolor=BAR_STATUS[i],
                darkcolor=BAR_STATUS[i])

        s.configure('TLabel', background="#f0f0f0")

        result = self.result
        for review in result["review"]["content"]:
            code = str(review["code"])
            if code in self.json:
                std = self.json[code]
                title = std["title"]
                rate = review["rate"]
                rateCent = parseCent(rate) + '%'
                status = review["status"]

                statusColor = BAR_STATUS[status]

                frame = tk.Frame(window, width=730, height=100, highlightthickness=1, highlightbackground=self.color)
                frame.pack()  # place(x=20, y=nowHeight)

                subframe1 = tk.Frame(frame, width=730, height=20)
                subframe1.pack()
                subframe1.propagate(0)

                tk.Label(subframe1, text=title, font=("微软雅黑", 12, 'bold'), fg=statusColor, anchor=tk.W).pack(side='left')
                tk.Label(subframe1, text=rateCent, width=10, anchor=tk.E).pack(side='right')

                progressBar = ttk.Progressbar(subframe1, style="bar%d.Horizontal.TProgressbar" % status, orient="horizontal")
                progressBar['maximum'] = 1
                progressBar['value'] = rate
                progressBar.pack(side='right')

                subframe2 = tk.Frame(frame, width=730)
                subframe2.pack(side='left')

                if "descCondition" in std and status in std["descCondition"]:
                    # 加入描述
                    text = self.renderText(review, std["desc"])
                    ttk.Label(subframe2, text=text, wraplength=700, anchor=tk.W).grid(row=0, column=0, sticky='w')

                if "addCondition" in std and status in std["addCondition"]:
                    # 加入额外信息
                    text = self.renderText(review, std["add"], array=0)
                    ttk.Label(subframe2, text=text, wraplength=700, anchor=tk.W, foreground="#777777").grid(row=1, column=0, sticky='w')

                if "addArrayCondition" in std and status in std["addArrayCondition"]:
                    # 加入数组额外信息
                    text = self.renderText(review, std["addArray"], array=1)
                    ttk.Label(subframe2, text=text, wraplength=700, anchor=tk.W, foreground="#777777").grid(row=2, column=0, sticky='w')

                nowHeight += 100
                height += 85

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
# Created by moeheart at 04/14/2022
# 时间轴窗口类文件.

import tkinter as tk
import os
from PIL import Image
from PIL import ImageTk
from tools.Functions import *
import threading

class TimelineWindow():
    '''
    时间轴窗口的展示类.
    '''

    def final(self):
        '''
        收集分锅结果并关闭窗口。
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
        使用tkinter绘制复盘窗口。
        '''

        singleWidth = 720
        singleHeight = 60
        numRows = int((self.bh.finalTime - self.bh.startTime) / 60000) + 1
        timeRate = singleWidth / 60000

        overallHeight = singleHeight * numRows

        window = tk.Toplevel()
        window.title('时间轴')
        window.geometry('780x%d'%(numRows*60+100))


        frame = tk.Frame(window, width=730, height=overallHeight)
        frame.place(x=20, y=0)

        canvas = tk.Canvas(frame, width=singleWidth+10, height=overallHeight)  # 创建canvas
        canvas.place(x=0, y=0) #放置canvas的位置
        canvas.config()

        # 加载图片列表
        canvas.imDict = {}
        canvas.im = {}
        imFile = os.listdir('icons')
        for line in imFile:
            imID = line.split('.')[0]
            if line.split('.')[1] == "png":
                canvas.imDict[imID] = Image.open("icons/%s.png" % imID).resize((20, 20), Image.ANTIALIAS)
                canvas.im[imID] = ImageTk.PhotoImage(canvas.imDict[imID])

        for i in range(numRows):
            baseY = i * singleHeight
            colorH = getColorHex((0, 255, 255))

            if i != numRows - 1:
                canvas.create_rectangle(0, baseY + 29, singleWidth, baseY + 31, fill=colorH, width=0)
            else:
                # 结束
                row = int((self.bh.finalTime - self.bh.startTime) / 60000)
                baseY = row * singleHeight
                baseX = int((self.bh.finalTime - self.bh.startTime - 60000 * row) * timeRate)
                colorH = getColorHex((0, 255, 255))
                canvas.create_rectangle(0, baseY + 29, baseX, baseY + 31, fill=colorH, width=0)
                canvas.create_rectangle(baseX, baseY+15, baseX+1, baseY+45, fill=colorH, width=0)
                canvas.create_rectangle(baseX+3, baseY+15, baseX+6, baseY+45, fill=colorH, width=0)

        for line in self.bh.log["environment"]:
            row = int((line["start"] - self.bh.startTime) / 60000)
            baseY = row * singleHeight
            baseX = int((line["start"] - self.bh.startTime - 60000*row) * timeRate)

            color = (0, 0, 0)
            if line["type"] == "cast":
                color = (128, 128, 255)
            elif line["type"] == "skill":
                color = (255, 128, 0)
            elif line["type"] == "buff":
                color = (0, 128, 255)
            elif line["type"] == "shout":
                color = (128, 0, 0)
                continue
            elif line["type"] == "npc":
                color = (128, 0, 0)
                continue
            colorH = getColorHex(color)
            text = line["skillname"]
            time = "%.1f" % ((line["start"] - self.bh.startTime) / 1000)
            canvas.create_text(baseX, baseY+15, text=text, fill=colorH)
            canvas.create_text(baseX, baseY+45, text=time, fill=colorH)
            if line["iconid"] in canvas.im:
                canvas.create_image(baseX, baseY+30, image=canvas.im[line["iconid"]])

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def setData(self, bh, boss):
        '''
        导入数据.
        params:
        - bh: 战斗流程信息，与BattleLog中的定义相同.
        - boss: BOSS名称.
        '''
        self.bh = bh
        self.boss = boss

    def __init__(self):
        pass
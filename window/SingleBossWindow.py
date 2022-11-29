# Created by moeheart at 08/08/2022
# 维护单个BOSS复盘结果，这是最重要的窗口类，其显示的是对应BOSS的重伤统计，但是其中还有控制前后翻页的功能。

import threading
import tkinter as tk
from tkinter import messagebox
from tools.Functions import *
import pyperclip

from replayer.boss.General import GeneralWindow

from replayer.boss.ZhangJingchao import ZhangJingchaoWindow
from replayer.boss.LiuZhan import LiuZhanWindow
from replayer.boss.SuFenglou import SuFenglouWindow
from replayer.boss.HanJingqing import HanJingqingWindow
from replayer.boss.TengyuanYouye import TengyuanYouyeWindow
from replayer.boss.LiChongmao import LiChongmaoWindow

from window.PotExtendWindow import PotExtendWindow
from window.Window import Window
from window.ToolTip import ToolTip

class SingleBossWindow(Window):
    '''
    单个BOSS复盘结果类。维护复盘结果的窗体，与简单的信息收集逻辑。
    '''

    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"

    def AddPot(self, pot, score):
        '''
        新增一条锅。暂时的处理方式为添加的锅不会在记录中显示，而是添加到记录中，刷新后才显示。
        params
        - pot 锅
        '''
        self.potList.append(pot)
        self.scoreList.append(score)

    def StartPotExtend(self):
        '''
        开启加锅界面。
        '''
        if self.potExtendRunning == False:
            self.potExtendWindow = PotExtendWindow(self)
            self.potExtendWindow.start()
            self.potExtendRunning = True

    def getPot(self, tmp, num):
        '''
        分锅结果变化的处理函数。
        params
        - tmp 记录编号
        - num 锅数
        '''
        self.scoreList[tmp] += num
        scoreStr = ""
        scoreColor = "#000000"
        if self.scoreList[tmp] > 0:
            scoreStr = "+%d" % self.scoreList[tmp]
            scoreColor = "#007700"
        elif self.scoreList[tmp] < 0:
            scoreStr = "%d" % self.scoreList[tmp]
            scoreColor = "#ff0000"
        self.scoreLabels[tmp].config(text=scoreStr, fg=scoreColor)

        # self.analyser.potListScore[-self.numPot + tmp][-1] = self.scoreList[tmp]

        self.analyser.setSinglePotScore(self.bossNum, tmp, self.scoreList[tmp])

        self.analyser.getPlayerPotList()

        text = self.analyser.getPlayerText(self.nameList[tmp])
        self.toolTips[tmp].remove()
        toopTip = ToolTip(self.toolTips[tmp].widget, text)
        self.toolTips[tmp] = toopTip

    def copyPot(self, tmp):
        '''
        点击复制按钮的处理函数。
        params
        - tmp 记录编号
        '''
        text = self.potList[tmp][4]
        player = self.potList[tmp][0].strip('"')
        copyText = "[%s]：%s" % (player, text)
        pyperclip.copy(copyText)
        messagebox.showinfo(title='提示', message='复制成功！')

    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''

        # print("[Test]SingleBoss")
        # print(self.potWindowActivated)
        # print(self.potList)
        # print(self.scoreList)

        if self.potExtendRunning:
            self.potExtendWindow.final()

        if self.potWindowActivated:
            for i in range(len(self.potList)):
                self.potList[i][6] = self.scoreList[i]
            self.analyser.changeResult(self.potList, self.bossNum)

        # print("[Test]After modified")
        # print(self.potWindowActivated)
        # print(self.potList)
        # print(self.scoreList)

        if self.windowAlive:
            self.window.destroy()
            self.windowAlive = False

    def constructReplayByNum(self, num):
        '''
        根据序号来打开对应的BOSS复盘窗口，要求序号必须合法
        params
        - num 对应的序号，如果序号为-1，表示选择最后一个BOSS
        '''
        if num == -1:
            num = self.analyser.getLastBossNum()
        if num == "None":
            return
        self.bossNum = int(num)
        self.addPotList(self.analyser.potContainer.getBoss(num))
        a, b, c, d, e = self.analyser.potContainer.getDetail(num)
        self.setDetail(a, b, c, d, e)
        # self.start()
        self.specificBossWindow.start()

    def finalPrev(self):
        '''
        收集分锅结果并关闭窗口，尝试打开前一个BOSS的窗口。
        '''
        prevNum = self.bossNum - 1
        if self.analyser.checkBossExists(prevNum):
            self.final()
            self.specificBossWindow.final()
            self.potWindowActivated = False
            self.constructReplayByNum(prevNum)
        else:
            messagebox.showinfo(title='嘶', message='前序BOSS未找到。')

    def finalNext(self):
        '''
        收集分锅结果并关闭窗口，尝试打开后一个BOSS的窗口。
        '''
        nextNum = self.bossNum + 1
        if self.analyser.checkBossExists(nextNum):
            self.final()
            self.specificBossWindow.final()
            self.potWindowActivated = False
            self.constructReplayByNum(nextNum)
        else:
            messagebox.showinfo(title='嘶', message='后继BOSS未找到。')

    def setDetail(self, potList, effectiveDPSList, detail, occResult, analysedBattleData):
        '''
        初始化详细复盘的数据.
        - params
        potList 分锅记录.
        effectiveDPSList DPS详细统计，包括每名玩家在特定算法下的DPS.
        detail 详细复盘记录.
        occResult 心法复盘记录.
        bh 战斗事件记录.
        '''
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.occResult = occResult
        self.analysedBattleData = analysedBattleData
        self.hasDetail = 1
        if "boss" in detail:
            if detail["boss"] == "张景超":
                self.specificBossWindow = ZhangJingchaoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            elif detail["boss"] == "刘展":
                self.specificBossWindow = LiuZhanWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            elif detail["boss"] == "苏凤楼":
                self.specificBossWindow = SuFenglouWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            elif detail["boss"] == "韩敬青":
                self.specificBossWindow = HanJingqingWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            elif detail["boss"] == "藤原佑野":
                self.specificBossWindow = TengyuanYouyeWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            elif detail["boss"] == "李重茂":
                self.specificBossWindow = LiChongmaoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                         analysedBattleData)
            else:
                self.specificBossWindow = GeneralWindow(self.mainWindow.config, effectiveDPSList, detail, occResult,
                                                        analysedBattleData)
            self.specificBossWindow.setPotWindow(self)

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        # window = tk.Tk()
        window.title('战斗复盘')
        window.geometry('650x700')

        numPot = len(self.potList)
        self.numPot = numPot
        self.potWindowActivated = True

        canvas = tk.Canvas(window, width=600, height=500, scrollregion=(0, 0, 580, numPot * 30))  # 创建canvas
        canvas.place(x=25, y=25)  # 放置canvas的位置
        frame = tk.Frame(canvas)  # 把frame放在canvas里
        frame.place(width=580, height=500)  # frame的长宽，和canvas差不多的
        vbar = tk.Scrollbar(canvas, orient=tk.VERTICAL)  # 竖直滚动条
        vbar.place(x=580, width=20, height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置
        canvas.create_window((265, numPot * 15), window=frame)  # create_window

        self.scoreLabels = []
        self.scoreList = []
        self.toolTips = []
        self.nameList = []

        for i in range(len(self.potList)):
            assert len(self.potList[i]) == 7
            self.scoreList.append(self.potList[i][6])

        print("[LiveTest]", self.analyser.checkBossExists(self.bossNum))
        print("[LiveTest]", self.bossNum)

        if not self.analyser.checkBossExists(self.bossNum):
            self.analyser.addResult(self.potList, self.bossNum, self.effectiveDPSList, self.detail, self.occResult,
                                    self.analysedBattleData)

        self.analyser.getPlayerPotList()

        for i in range(numPot):
            line = self.potList[i]
            name = line[0].strip('"')
            occ = line[1]
            color = getColor(occ)
            nameLabel = tk.Label(frame, text=name, width=13, height=1, fg=color)
            nameLabel.grid(row=i, column=0)
            pot = line[4]
            color = self.getPotColor(line[2])
            potLabel = tk.Label(frame, text=pot, height=1, fg=color)
            potLabel.grid(row=i, column=1)

            if len(line) > 5:
                potDetail = '\n'.join(line[5])
                if potDetail != "":
                    ToolTip(potLabel, potDetail)

            scoreLabel = tk.Label(frame, text="", width=5, height=1, font=("Arial", 12, "bold"))
            scoreLabel.grid(row=i, column=2)
            self.scoreLabels.append(scoreLabel)

            tmp = i
            button1 = tk.Button(frame, text='接锅', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, -1),
                                bg='#ffcccc')
            button1.grid(row=i, column=3)
            button2 = tk.Button(frame, text='领赏', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, 1),
                                bg='#ccffcc')
            button2.grid(row=i, column=4)
            button3 = tk.Button(frame, text='复制', width=6, height=1, command=lambda tmp=tmp: self.copyPot(tmp),
                                bg='#ccccff')
            button3.grid(row=i, column=5)

            text = self.analyser.getPlayerText(name)
            toolTip = ToolTip(nameLabel, text)
            self.toolTips.append(toolTip)
            self.nameList.append(name)

        for i in range(len(self.potList)):
            self.getPot(i, 0)

        buttonFinal = tk.Button(window, text='分锅完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=250, y=540)

        # buttonPrev = tk.Button(window, text='<<', width=2, height=1, command=self.finalPrev)
        # buttonPrev.place(x = 220, y = 540)
        #
        # buttonNext = tk.Button(window, text='>>', width=2, height=1, command=self.finalNext)
        # buttonNext.place(x = 340, y = 540)

        buttonDetail = tk.Button(window, text='手动设置', width=10, height=1, command=self.StartPotExtend)
        buttonDetail.place(x=200, y=580)

        # buttonDetail = tk.Button(window, text='数据统计', width=10, height=1, command=self.showDetail)
        # buttonDetail.place(x = 300, y = 570)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        # window.mainloop()

    def openDetailWindow(self):
        '''
        开启详细复盘界面。这是由于在7.0版本更新后，先显示复盘界面，再显示分锅界面。
        '''
        self.potWindowActivated = False
        self.specificBossWindow.start()

    def addPotList(self, potList):
        self.potList = potList

    def __init__(self, analyser, bossNum, mainWindow):
        super().__init__()
        self.analyser = analyser
        self.bossNum = bossNum
        self.mainWindow = mainWindow
        self.effectiveDPSList = []
        self.detail = {}
        self.potExtendRunning = False
        self.potWindowActivated = False
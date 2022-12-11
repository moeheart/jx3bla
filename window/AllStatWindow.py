# Created by moeheart at 08/08/2022
# 全局复盘结果类.

import tkinter as tk
from tools.Functions import *

from window.CommentWindow import CommentWindow
from window.SingleBossWindow import SingleBossWindow

from window.Window import Window
from window.ToolTip import ToolTip

class AllStatWindow(Window):
    '''
    全局复盘结果类。用于展示所有的复盘结果及所有玩家。
    '''

    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"

    def TryComment(self, tmp):
        '''
        准备评论窗口的函数。
        params
        - tmp 玩家编号
        '''
        id = self.playerID[tmp][0].strip('"')
        occ = self.playerID[tmp][1]
        pots = self.analyser.getPlayerText(id)
        server = self.analyser.getServer()
        userid = self.mainWindow.config.items_user["uuid"]
        mapDetail = self.analyser.getMapDetail()
        beginTime = self.analyser.getBeginTime()
        commentWindow = CommentWindow(id, occ, pots, server, userid, mapDetail, beginTime)
        commentWindow.start()

    def openBoss(self, bossID):
        '''
        打开对应BOSS的复盘界面。
        params
        - bossID 需要打开的BOSS的ID。
        '''
        replayWindow = SingleBossWindow(self.analyser, bossID, self.mainWindow)
        replayWindow.constructReplayByNum(bossID)

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('总结')
        window.geometry('600x700')

        frame1 = tk.Frame(window)
        frame1.pack()

        bossDict = self.analyser.getBossName()
        for id in bossDict:
            idNum = int(id)
            button = tk.Button(frame1, text=bossDict[id], width=10, height=1,
                               command=lambda idNum=idNum: self.openBoss(idNum))
            row = (idNum - 1) // 6
            column = (idNum - 1) % 6
            button.grid(row=row, column=column)

        frame2 = tk.Frame(window)
        frame2.pack()

        numPlayer = len(self.playerID)

        i = 0

        self.toolTips = []

        for player in self.playerID:

            if player[0] in self.playerPotList:
                line = self.playerPotList[player[0]]
            else:
                line = {"occ": player[1], "numPositive": 0, "numNegative": 0, "pot": []}

            name = player[0].strip('"')
            occ = line["occ"]
            color = getColor(occ)
            nameLabel = tk.Label(frame2, text=name, width=13, fg=color)
            nameLabel.grid(row=i, column=0)

            posNumText = ""
            if line["numPositive"] > 0:
                posNumText = "+%s" % str(line["numPositive"])
            positiveLabel = tk.Label(frame2, text=posNumText, width=5, fg="#007700", font=("Arial", 12, "bold"))
            positiveLabel.grid(row=i, column=1)

            negNumText = ""
            if line["numNegative"] < 0:
                negNumText = "%s" % str(line["numNegative"])
            negativeLabel = tk.Label(frame2, text=negNumText, width=5, fg="#ff0000", font=("Arial", 12, "bold"))
            negativeLabel.grid(row=i, column=2)

            # tmp = i
            # button1 = tk.Button(frame2, bitmap="warning", text="评价", width=60, height=15, compound=tk.LEFT,
            #                     command=lambda tmp=tmp: self.TryComment(tmp))
            # button1.grid(row=i, column=3)

            for j in range(1, 7):
                rankText = self.playerRank[player[0]][j]
                rankColor = getRankColor(rankText)
                rankLabel = tk.Label(frame2, text=rankText, fg=rankColor)
                rankLabel.grid(row=i, column=2 + j)

            text = self.analyser.getPlayerText(name)
            toopTip = ToolTip(nameLabel, text)
            self.toolTips.append(toopTip)

            i += 1

        buttonFinal = tk.Button(window, text='查看完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=250, y=670)
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        # window.mainloop()

    def addPotList(self):
        self.potListScore = self.analyser.potContainer.getAll()
        self.playerPotList = self.analyser.getPlayerPotList()
        self.playerID = self.analyser.getPlayer()
        self.playerRank = self.analyser.getPlayerRank()

    def __init__(self, analyser, mainWindow):
        super().__init__()
        self.analyser = analyser
        self.mainWindow = mainWindow
        self.addPotList()
# Created by moeheart at 08/07/2022
# BOSS复盘显示窗口的类库，这里实现了一个基类，每个BOSS需要派生一个具体的类，并做对应的统计。

import tkinter as tk

from window.Window import Window
from window.CombatTrackerWindow import CombatTrackerWindow
from window.TimelineWindow import TimelineWindow
from tools.Functions import *

class SpecificBossWindow(Window):
    '''
    BOSS复盘窗口基类.
    '''

    def getMaskName(self, name):
        '''
        获取名称打码的结果。事实上只需要对统计列表中的玩家打码.
        params:
        - name: 打码之前的玩家名.
        '''
        s = name.strip('"')
        if s == "":
            return s
        elif self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def openPrev(self):
        '''
        尝试打开前序BOSS。
        '''
        self.potWindow.finalPrev()

    def openNext(self):
        '''
        尝试打开后序BOSS。
        '''
        self.potWindow.finalNext()

    def openPot(self):
        '''
        打开分锅界面（也即战斗事件记录界面）。
        '''
        self.potWindow.start()

    def setPotWindow(self, potWindow):
        '''
        设置分锅界面对象，为后面通过复盘窗口打开分锅窗口提供连接。
        '''
        self.potWindow = potWindow

    def openTimelineWindow(self):
        '''
        打开时间轴窗口。
        '''
        self.timelineWindow.start()

    def setTimelineWindow(self, data, boss):
        '''
        设置时间轴窗口对象.
        - environment: 环境轴，与BattleLog中的定义相同.
        - boss: BOSS名称.
        '''
        self.timelineWindow = TimelineWindow()
        self.timelineWindow.setData(data, boss)

    def openCombatTrackerWindow(self):
        '''
        打开时间轴窗口。
        '''
        self.combatTrackerWindow.start()

    def setCombatTrackerWindow(self, act):
        '''
        设置统计结果对象.
        - act: 统计结果对象
        '''
        self.combatTrackerWindow = CombatTrackerWindow(act)

    def constructWindow(self, name, size):
        '''
        准备构建窗口.
        这个方法是所有BOSS窗口共享的部分.
        params:
        - name: BOSS的名字
        - size: 窗口的大小
        '''
        self.setTimelineWindow(self.bh, name)
        self.setCombatTrackerWindow(self.act)

        window = tk.Toplevel()
        window.title('%s复盘' % name)
        window.geometry(size)
        window.protocol('WM_DELETE_WINDOW', self.final)
        self.window = window

    def constructCommonHeader(self, tb, stunDescription=""):
        '''
        构建不同BOSS窗口中共享的前几个表头。
        params:
        - tb: 表格创建类.
        - stunDescription: 被控栏的描述.
        '''
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。\n被星号标记的装分表示对应的装备已经获取失败，但服务器可以从最近的战斗记录中读取到缓存。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("强化", "装备强化列表，表示[精炼满级装备数量]/[插8]-[插7]-[插6]/[五彩石等级]/[紫色附魔]-[蓝色附魔]/[大附魔：手腰脚头衣裤]")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。\n%s" % stunDescription)

    def constructCommonLine(self, tb, line):
        '''
        构建不同BOSS窗口中共享的前几个内容。
        params:
        - tb: 表格创建类.
        - line: 对应的数据.
        '''
        name = self.getMaskName(line[0])
        color = getColor(line[1])
        tb.AppendContext(name, color=color, width=13)
        tb.AppendContext(int(line[2]))

        if getOccType(line[1]) != "healer":
            text3 = str(line[3]) + '%'
            color3 = "#000000"
        else:
            text3 = line[3]
            color3 = "#00ff00"
        tb.AppendContext(text3, color=color3)

        text4 = "-"
        if line[4] != -1:
            text4 = str(line[4])
        color4 = "#000000"
        if "大橙武" in line[5]:
            color4 = "#ffcc00"
        tb.AppendContext(text4, color=color4)

        tb.AppendContext(line[5].split('|')[0])
        tb.AppendContext(line[5].split('|')[1])
        tb.AppendContext(int(line[6]))

    def constructNavigator(self):
        '''
        构建不同BOSS窗口中共享的导航栏.
        '''
        window = self.window
        frame2 = tk.Frame(window)
        frame2.pack()
        buttonPrev = tk.Button(frame2, text='<<', width=2, height=1, command=self.openPrev)
        submitButton = tk.Button(frame2, text='战斗事件记录', command=self.openPot)
        actButton = tk.Button(frame2, text='数值统计', command=self.openCombatTrackerWindow, bg='#777777')
        timelineButton = tk.Button(frame2, text='时间轴', command=self.openTimelineWindow)
        buttonNext = tk.Button(frame2, text='>>', width=2, height=1, command=self.openNext)
        buttonPrev.grid(row=0, column=0)
        submitButton.grid(row=0, column=1)
        actButton.grid(row=0, column=2)
        timelineButton.grid(row=0, column=3)
        buttonNext.grid(row=0, column=4)

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        '''
        初始化.
        '''
        super().__init__()
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.occResult = occResult
        self.config = config
        self.mask = config.item["general"]["mask"]
        self.analysedBattleData = analysedBattleData
        self.bh = self.analysedBattleData["bossBh"]
        self.act = self.analysedBattleData["act"]
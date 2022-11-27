# Created by moeheart at 08/08/2022
# DPS复盘窗口展示类。

import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyperclip

from replayer.TableConstructor import TableConstructor
from tools.Functions import *
from window.ReviewWindow import ReviewerWindow
from window.Window import Window
from window.ToolTip import ToolTip
from window.HealerDisplayWindow import SingleSkillDisplayer

def getDirection(key):
    if "delay" in key:
        return -1
    else:
        return 1

def getRankColor(percent):
    '''
    根据排名获取对应的颜色.
    '''
    if percent == 100:
        color = "#e5cc80"
    elif percent == 99:
        color = "#e268a8"
    elif percent >= 95:
        color = "#ff7700"
    elif percent >= 75:
        color = "#330077"
    elif percent >= 50:
        color = "#0000ff"
    elif percent >= 25:
        color = "#007700"
    else:
        color = "#aaaaaa"
    return color

class DpsDisplayWindow(Window):
    '''
    DPS复盘窗口基类，实现部分通用功能.
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

    def exportEquipment(self):
        '''
        导出装备信息到剪贴板.
        '''
        copyText = self.result["equip"]["raw"]
        pyperclip.copy(copyText)
        messagebox.showinfo(title='提示', message='复制成功！')

    def OpenInWeb(self):
        '''
        打开网页版的复盘界面.
        '''
        url = "http://120.48.95.56/%s/%d" % (self.occPinyin, self.result["overall"]["shortID"])
        webbrowser.open(url)

    def renderOverall(self):
        '''
        渲染全局信息(Part 1).
        '''
        window = self.window
        # Part 1: 全局
        frame1 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground=self.themeColor)
        frame1.place(x=10, y=10)
        frame1sub = tk.Frame(frame1)
        frame1sub.place(x=0, y=0)
        tb = TableConstructor(self.config, frame1sub)
        tb.AppendContext("复盘版本：", justify="right")
        tb.AppendContext(self.result["overall"]["edition"])
        tb.EndOfLine()
        tb.AppendContext("玩家ID：", justify="right")
        tb.AppendContext(self.result["overall"]["playerID"], color=self.themeColor)
        tb.EndOfLine()
        tb.AppendContext("服务器：", justify="right")
        tb.AppendContext(self.result["overall"]["server"])
        tb.EndOfLine()
        tb.AppendContext("战斗时间：", justify="right")
        tb.AppendContext(self.result["overall"]["battleTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("生成时间：", justify="right")
        tb.AppendContext(self.result["overall"]["generateTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("地图：", justify="right")
        tb.AppendContext(self.result["overall"]["map"])
        tb.EndOfLine()
        bossPrint = self.result["overall"]["boss"]
        if self.result["overall"].get("win", 1) == 0:
            bossPrint = bossPrint + "(未通关)"
        tb.AppendContext("首领：", justify="right")
        tb.AppendContext(bossPrint, color="#ff0000")
        tb.EndOfLine()
        tb.AppendContext("人数：", justify="right")
        tb.AppendContext("%.2f"%self.result["overall"].get("numPlayer", 0))
        tb.EndOfLine()
        tb.AppendContext("战斗时长：", justify="right")
        tb.AppendContext(self.result["overall"]["sumTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("数据种类：", justify="right")
        tb.AppendContext(self.result["overall"]["dataType"])
        tb.EndOfLine()

    def renderEquipment(self):
        '''
        渲染装备信息(Part 2).
        '''
        window = self.window
        # Part 2: 装备
        frame2 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground=self.themeColor)
        frame2.place(x=220, y=10)
        frame2sub = tk.Frame(frame2)
        frame2sub.place(x=0, y=0)
        if self.result["equip"]["available"] == 0:
            text = "装备信息获取失败。\n在进入战斗后打开团队装分面板即可获取。\n如果是第一视角也可以自动获取。"
            tk.Label(frame2, text=text, justify="left").place(x=0, y=0)
        else:
            tb = TableConstructor(self.config, frame2sub)
            tb.AppendContext("装备分数：", justify="right")
            color4 = "#000000"
            if "大橙武" in self.result["equip"]["sketch"]:
                color4 = "#ffcc00"
            tb.AppendContext("%s"%self.result["equip"]["score"], color=color4)
            tb.EndOfLine()
            tb.AppendContext("详情：", justify="right")
            tb.AppendContext(self.result["equip"]["sketch"])
            tb.EndOfLine()
            tb.AppendContext("强化：", justify="right")
            tb.AppendContext(self.result["equip"].get("forge", ""))
            tb.EndOfLine()
            tb.AppendContext("根骨：", justify="right")
            tb.AppendContext("%d"%self.result["equip"]["spirit"])
            tb.EndOfLine()
            tb.AppendContext("攻击：", justify="right")
            tb.AppendContext("%d(%d)"%(self.result["equip"]["attack"], self.result["equip"]["attackBase"]))
            tb.EndOfLine()
            tb.AppendContext("会心：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critPercent"], self.result["equip"]["crit"]))
            tb.EndOfLine()
            tb.AppendContext("会心效果：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critpowPercent"], self.result["equip"]["critpow"]))
            tb.EndOfLine()
            tb.AppendContext("破防：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["overcomePercent"], self.result["equip"]["overcome"]))
            tb.EndOfLine()
            tb.AppendContext("无双：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["strainPercent"], self.result["equip"]["strain"]))
            tb.EndOfLine()
            tb.AppendContext("破招：", justify="right")
            tb.AppendContext("%d"%self.result["equip"]["surplus"])
            tb.EndOfLine()
            tb.AppendContext("加速：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["hastePercent"], self.result["equip"]["haste"]))
            tb.EndOfLine()
            b2 = tk.Button(frame2, text='导出', height=1, command=self.exportEquipment)
            b2.place(x=140, y=180)

    def renderDps(self):
        '''
        渲染输出信息(Part 3).
        '''
        window = self.window
        # Part 3: 输出
        frame3 = tk.Frame(window, width=310, height=150, highlightthickness=1, highlightbackground=self.themeColor)
        frame3.place(x=430, y=10)
        frame3sub = tk.Frame(frame3)
        frame3sub.place(x=0, y=0)

        tb = TableConstructor(self.config, frame3sub)
        tb.AppendHeader("rDPS", "全称raid DPS，是将伤害值中的增益部分转移给增益来源后得到的值。\nrDPS可以反映各种增益的强度，并且适用于对比不同战斗中的表现。")
        tb.AppendHeader("nDPS", "全称natrual DPS，指自然计算所有伤害的值。\nnDPS会受到各种增益的影响，且不能反映自身对团队的增益，因此只能用来计算全团伤害与BOSS血量的比较。")
        tb.AppendHeader("mrDPS", "全称main-target raid DPS，是只考虑主目标的rDPS。\n如果有些阶段只能转火、打分身、打双目标，则这个阶段没有主目标。\n用于衡量单体与群攻的差别。")
        tb.AppendHeader("mnDPS", "全称main-target natrual DPS，是只考虑主目标的nDPS。\n如果有些阶段只能转火、打分身、打双目标，则这个阶段没有主目标。\n用于衡量单体与群攻的差别。")
        tb.EndOfLine()
        # 当前玩家
        dpsDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        for stat in ["rdps", "ndps", "mrdps", "mndps"]:
            num, percent, color = dpsDisplayer.getSkillPercent("dps", stat)
            if num > 0:
                descText = "排名：%d%%\n数量：%d" % (percent, num)
            else:
                descText = "排名未知"
            tb.AppendHeader(self.result["dps"]["stat"].get(stat, 0), descText, color=color)
        tb.EndOfLine()

    def renderQx(self):
        '''
        渲染奇穴信息(Part 4).
        '''
        window = self.window
        # Part 4: 奇穴
        frame4 = tk.Frame(window, width=310, height=70, highlightthickness=1, highlightbackground=self.themeColor)
        frame4.place(x=430, y=170)
        if self.result["qixue"]["available"] == 0:
            text = "奇穴信息获取失败。\n在进入战斗后查看目标的奇穴即可获取。\n如果是第一视角也可以自动获取。"
            tk.Label(frame4, text=text, justify="left").place(x=0, y=0)
        else:
            text = ""
            for i in range(1, 7):
                text = text + self.result["qixue"][str(i)] + ','
            text = text + '\n'
            for i in range(7, 13):
                text = text + self.result["qixue"][str(i)] + ','
            text = text[:-1]
            tk.Label(frame4, text=text, justify="left").place(x=0, y=0)

    def renderSkill(self):
        '''
        渲染技能信息，需要派生类实现(Part 5).
        '''
        pass

    def renderReplay(self):
        '''
        渲染回放信息，需要派生类实现(Part 6).
        '''
        pass

    def renderTeam(self):
        '''
        渲染团队信息，需要派生类实现(Part 7).
        '''
        pass

    def openReviewerWindow(self):
        '''
        打开专案组窗口.
        '''
        self.reviewerWindow.start()

    def renderRate(self):
        '''
        渲染评分信息，需要派生类实现(Part 8).
        '''
        pass

        # window = self.window
        # # Part 8: 打分
        # frame8 = tk.Frame(window, width=210, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        # frame8.place(x=320, y=620)
        #
        # if "review" in self.result:
        #     # 支持专案组模块
        #     tk.Label(frame8, text="综合评分：").place(x=30, y=20)
        #     score = self.result["review"]["score"]
        #     descText = "排名未知"
        #     color = "#aaaaaa"
        #     if "numReplays" in self.result["overall"]:
        #         numReplays = self.result["overall"]["numReplays"]
        #         scoreRank = self.result["overall"]["scoreRank"]
        #         descText = "排名：%d%%\n数量：%d" % (scoreRank, numReplays)
        #         color = getRankColor(scoreRank)
        #     scoreLabel = tk.Label(frame8, text="%d" % score, fg=color)
        #     scoreLabel.place(x=100, y=20)
        #     ToolTip(scoreLabel, descText)
        #
        #     numReview = self.result["review"]["num"]
        #     tk.Label(frame8, text="共有%d条手法建议。" % numReview).place(x=30, y=50)
        #     b2 = tk.Button(frame8, text='在[专案组]中查看', height=1, command=self.openReviewerWindow)
        #     b2.place(x=60, y=80)
        #     tk.Label(frame8, text="本模块仅可作为提高手法的参考，").place(x=20, y=110)
        #     tk.Label(frame8, text="请勿使用本模块出警！").place(x=20, y=130)
        #     self.reviewerWindow = ReviewerWindow(self.result, self.themeColor)
        # else:
        #     tk.Label(frame8, text="复盘生成时的版本尚不支持此功能。").place(x=10, y=20)

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9).
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="当前心法详细复盘还未实现！").place(x=20, y=20)
        # tk.Label(frame9, text="奶花PVE群：294479046").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb, bg='#777777')
            b2.place(x=40, y=90)

        # tk.Label(frame9, text="广告位招租").place(x=40, y=140)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def initWindow(self):
        '''
        对窗口进行初始化.
        '''
        window = tk.Toplevel()
        self.window = window
        window.geometry('750x900')
        window.title(self.title)
        window.protocol('WM_DELETE_WINDOW', self.final)

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.initWindow()
        self.renderOverall()
        self.renderEquipment()
        self.renderDps()
        self.renderQx()
        # self.renderSkill()
        # self.renderReplay()
        # self.renderTeam()
        # self.renderRate()
        self.renderAdvertise()

    def setThemeColor(self, color):
        '''
        设置主题色，用于界面展示.
        params:
        - color: 主题色
        '''
        self.themeColor = color

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - config: 设置类.
        - result: 复盘逻辑返回的结果.
        '''
        super().__init__()
        self.config = config
        self.mask = self.config.item["general"]["mask"]
        self.result = result["result"]
        self.rank = result["rank"]
        if "mask" in self.result["overall"]:
            self.mask = self.result["overall"]["mask"]  # 使用数据中的mask选项顶掉框架中现场读取的判定
        occ = result["occ"]
        self.themeColor = getColor(occ)
        self.title = '%s复盘' % OCC_NAME_DICT[occ]
        self.occPinyin = OCC_PINYIN_DICT[occ]
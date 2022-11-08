# Created by moeheart at 01/14/2022
# 奶毒复盘，用于奶毒复盘的生成，展示

from replayer.ReplayerBase import ReplayerBase
from replayer.occ.Healer import HealerReplay
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *
from window.HealerDisplayWindow import HealerDisplayWindow, SingleSkillDisplayer

import os
import time
import json
import copy
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import urllib.request
import hashlib
import webbrowser
import pyperclip

class BuTianJueWindow(HealerDisplayWindow):
    '''
    奶毒复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴中从上到下的四个条分别表示：迷仙引梦、仙王蛊鼎、蛊惑众生、醉舞九天。
醉舞九天作为不占gcd的技能，不会在技能轴中显示，而是改为在时间轴内部显示。
战斗效率包含醉舞九天的读条时间，而gcd效率则不包含。'''
        messagebox.showinfo(title='说明', message=text)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，奶歌复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame5.place(x=10, y=250)
        
        bcqsDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        bcqsDisplayer.setImage("2745", "冰蚕牵丝")
        bcqsDisplayer.setDouble("rate", "数量", "bcqs", "num", "numPerSec")
        bcqsDisplayer.setSingle("delay", "延迟", "bcqs", "delay")
        bcqsDisplayer.setSingle("int", "HPS", "bcqs", "HPS")
        bcqsDisplayer.setSingle("percent", "有效比例", "bcqs", "effRate")
        bcqsDisplayer.export_image(frame5, 0)

        zwjtDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        zwjtDisplayer.setImage("2746", "醉舞九天")
        zwjtDisplayer.setDouble("rate", "数量", "zwjt", "num", "numPerSec")
        zwjtDisplayer.setSingle("delay", "延迟", "zwjt", "delay")
        zwjtDisplayer.setSingle("int", "HPS", "zwjt", "HPS")
        zwjtDisplayer.setSingle("percent", "有效比例", "zwjt", "effRate")
        zwjtDisplayer.export_image(frame5, 1)

        ssztDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        ssztDisplayer.setImage("3028", "圣手织天")
        ssztDisplayer.setDouble("rate", "数量", "sszt", "num", "numPerSec")
        ssztDisplayer.setSingle("delay", "延迟", "sszt", "delay")
        ssztDisplayer.setSingle("int", "HPS", "sszt", "HPS")
        ssztDisplayer.setSingle("percent", "有效比例", "sszt", "effRate")
        ssztDisplayer.export_image(frame5, 2)

        qdtrDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        qdtrDisplayer.setImage("2748", "千蝶吐瑞")
        qdtrDisplayer.setDouble("rate", "数量", "qdtr", "num", "numPerSec")
        qdtrDisplayer.setSingle("int", "HPS", "qdtr", "HPS")
        qdtrDisplayer.setSingle("percent", "有效比例", "qdtr", "effRate")
        qdtrDisplayer.export_image(frame5, 3)

        dcDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        dcDisplayer.setImage("9567", "蝶池")
        dcDisplayer.setDouble("rate", "数量", "dc", "num", "numPerSec")
        dcDisplayer.setSingle("int", "HPS", "dc", "HPS")
        dcDisplayer.setSingle("percent", "有效比例", "dc", "effRate")
        dcDisplayer.export_image(frame5, 4)

        mxymDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        mxymDisplayer.setImage("7255", "迷仙引梦")
        mxymDisplayer.setDouble("rate", "数量", "mxym", "num", "numPerSec")
        mxymDisplayer.setSingle("int", "HPS", "mxym", "HPS")
        mxymDisplayer.setSingle("percent", "覆盖率", "mxym", "cover")
        mxymDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "蝶旋HPS", "dx", "HPS")
        info1Displayer.setSingle("int", "蝶旋次数", "dx", "num")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.setSingle("percent", "蛊惑覆盖率", "ghzs", "cover")
        info1Displayer.setSingle("percent", "女娲覆盖率", "nvwa", "cover")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("percent", "绮栊覆盖率", "qilong", "cover")
        info2Displayer.setSingle("int", "蛊惑HPS", "ghzs", "hps")
        info2Displayer.setSingle("percent", "gcd效率", "general", "efficiency")
        info2Displayer.setSingle("percent", "战斗效率", "general", "efficiencyNonGcd")
        info2Displayer.export_text(frame5, 7)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

    def renderReplay(self):
        '''
        渲染回放信息(Part 6)，奶歌复盘特化.
        '''
        window = self.window
        # Part 6: 回放

        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#3f1f9f")
        frame6.place(x=10, y=460)
        battleTime = self.result["overall"]["sumTime"]
        battleTimePixels = int(battleTime / 100)
        startTime = self.result["replay"]["startTime"]
        canvas6 = tk.Canvas(frame6, width=720, height=140, scrollregion=(0, 0, battleTimePixels, 120))  # 创建canvas
        canvas6.place(x=0, y=0) #放置canvas的位置
        frame6sub = tk.Frame(canvas6) #把frame放在canvas里
        frame6sub.place(width=720, height=120) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas6, orient=tk.HORIZONTAL)
        vbar.place(y=120,width=720,height=20)
        vbar.configure(command=canvas6.xview)
        canvas6.config(xscrollcommand=vbar.set)
        canvas6.create_window((360, int(battleTimePixels/2)), window=frame6sub)

        # 加载图片列表
        canvas6.imDict = {}
        canvas6.im = {}
        imFile = os.listdir('icons')
        for line in imFile:
            imID = line.split('.')[0]
            if line.split('.')[1] == "png":
                canvas6.imDict[imID] = Image.open("icons/%s.png" % imID).resize((20, 20), Image.ANTIALIAS)
                canvas6.im[imID] = ImageTk.PhotoImage(canvas6.imDict[imID])

        # 绘制主时间轴及时间
        canvas6.create_rectangle(0, 30, battleTimePixels, 70, fill='white')
        # 迷仙引梦
        for i in range(1, len(self.result["replay"]["mxym"])):
            posStart = int((self.result["replay"]["mxym"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["mxym"][i][0] - startTime) / 100)
            # if posEnd - posStart < 3:
            #     posEnd = posStart + 3
            mxym = self.result["replay"]["mxym"][i-1][1]
            if mxym == 1:
                canvas6.create_rectangle(posStart, 31, posEnd, 40, fill="#cc3385", width=0)
        # 仙王蛊鼎
        for i in range(1, len(self.result["replay"]["xwgd"])):
            posStart = int((self.result["replay"]["xwgd"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["xwgd"][i][0] - startTime) / 100)
            xwgd = self.result["replay"]["xwgd"][i-1][1]
            if xwgd == 1:
                canvas6.create_rectangle(posStart, 41, posEnd, 50, fill="#4419b7", width=0)
        # 蛊惑众生
        for i in range(1, len(self.result["replay"]["ghzs"])):
            posStart = int((self.result["replay"]["ghzs"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["ghzs"][i][0] - startTime) / 100)
            ghzs = self.result["replay"]["ghzs"][i-1][1]
            if ghzs == 1:
                canvas6.create_rectangle(posStart, 51, posEnd, 60, fill="#ff58ee", width=0)
        # 醉舞九天
        for i in range(1, len(self.result["replay"]["zwjt"])):
            posStart = int((self.result["replay"]["zwjt"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["zwjt"][i][0] - startTime) / 100)
            zwjt = self.result["replay"]["zwjt"][i-1][1]
            if zwjt == 1:
                canvas6.create_rectangle(posStart, 61, posEnd, 70, fill="#957ded", width=0)

        if "badPeriodHealer" in self.result["replay"]:
            # 绘制无效时间段
            for i in range(1, len(self.result["replay"]["badPeriodHealer"])):
                posStart = int((self.result["replay"]["badPeriodHealer"][i - 1][0] - startTime) / 100)
                posStart = max(posStart, 1)
                posEnd = int((self.result["replay"]["badPeriodHealer"][i][0] - startTime) / 100)
                zwjt = self.result["replay"]["badPeriodHealer"][i - 1][1]
                if zwjt == 1:
                    canvas6.create_rectangle(posStart, 31, posEnd, 70, fill="#bbbbbb", width=0)

        nowt = 0
        while nowt < battleTime:
            nowt += 10000
            text = parseTime(nowt / 1000)
            pos = int(nowt / 100)
            canvas6.create_text(pos, 50, text=text)
        # 绘制常规技能轴
        j = -1
        lastName = ""
        lastStart = 0
        l = len(self.result["replay"]["normal"])
        for i in range(l + 1):
            if i == l:
                record = {"skillname": "Final", "start": 999999999999}
            else:
                record = self.result["replay"]["normal"][i]
            if record["skillname"] != lastName or record["start"] - lastStart > 3000:
                if j == -1:
                    j = i
                    lastName = record["skillname"]
                    lastStart = record["start"]
                    continue
                # 结算上一个技能
                if self.config.item["butian"]["stack"] != "不堆叠" and i-j >= int(self.config.item["butian"]["stack"]):
                    # 进行堆叠显示
                    record_first = self.result["replay"]["normal"][j]
                    record_last = self.result["replay"]["normal"][i-1]
                    posStart = int((record_first["start"] - startTime) / 100)
                    posEnd = int((record_last["start"] + record_last["duration"] - startTime) / 100)
                    canvas6.create_image(posStart + 10, 80, image=canvas6.im[record_last["iconid"]])
                    # 绘制表示持续的条
                    if posStart + 20 < posEnd:
                        canvas6.create_rectangle(posStart + 20, 70, posEnd, 90, fill="#64fab4")
                    # 绘制重复次数
                    if posStart + 30 < posEnd:
                        canvas6.create_text(posStart + 30, 80, text="*%d" % (i-j))
                else:
                    # 进行独立显示
                    for k in range(j, i):
                        record_single = self.result["replay"]["normal"][k]
                        posStart = int((record_single["start"] - startTime) / 100)
                        posEnd = int((record_single["start"] + record_single["duration"] - startTime) / 100)
                        canvas6.create_image(posStart + 10, 80, image=canvas6.im[record_single["iconid"]])
                        # 绘制表示持续的条
                        if posStart + 20 < posEnd:
                            canvas6.create_rectangle(posStart + 20, 70, posEnd, 90, fill="#64fab4")
                j = i
            lastName = record["skillname"]
            lastStart = record["start"]

        # 绘制特殊技能轴
        for record in self.result["replay"]["special"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 100, image=canvas6.im[record["iconid"]])

        # 绘制点名轴
        for record in self.result["replay"]["call"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 100, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 90, posEnd, 110, fill="#ff7777")
            # 绘制名称
            if posStart + 30 < posEnd:
                text = record["skillname"]
                canvas6.create_text(posStart+20, 100, text=text, anchor=tk.W)

        # 绘制环境轴
        for record in self.result["replay"]["environment"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 20, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 10, posEnd, 30, fill="#ff7777")
            # 绘制名称
            if posStart + 30 < posEnd:
                text = record["skillname"]
                if record["num"] > 1:
                    text += "*%d"%record["num"]
                canvas6.create_text(posStart+20, 20, text=text, anchor=tk.W)

        tk.Label(frame6sub, text="test").place(x=20, y=20)

    def renderTeam(self):
        '''
        渲染团队信息(Part 7)，奶歌复盘特化.
        '''
        window = self.window
        # Part 7: 输出
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame7.place(x=10, y=620)
        numDPS = self.result["dps"]["numDPS"]
        canvas = tk.Canvas(frame7,width=290,height=190,scrollregion=(0,0,270,numDPS*24)) #创建canvas
        canvas.place(x=0, y=0) #放置canvas的位置
        frame7sub = tk.Frame(canvas) #把frame放在canvas里
        frame7sub.place(width=270, height=190) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas,orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x=270,width=20,height=190)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set) #设置
        canvas.create_window((135,numDPS*12), window=frame7sub)  #create_window

        tb = TableConstructor(self.config, frame7sub)
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("DPS", "全程的DPS")
        tb.AppendHeader("吃锅次数", "无效的次数不会计算")
        tb.AppendHeader("绮栊覆盖率", "绮栊的层数对单位时间的积分。上限为300%。")
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.AppendContext(record["xwgdNum"])
            tb.AppendContext(parseCent(record["qilongRate"]) + '%')
            tb.EndOfLine()

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9)，奶歌复盘特化.
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="奶毒PVE群：208732360").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb, bg='#777777')
            b2.place(x=40, y=90)

        # tk.Label(frame9, text="新建文件夹！").place(x=40, y=140)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - result: 奶毒复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#3f1f9f")
        self.title = '奶毒复盘'
        self.occ = "butianjue"

class BuTianJueReplayer(HealerReplay):
    '''
    奶毒复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        self.window.setNotice({"t2": "加载奶毒复盘...", "c2": "#3f1f9f"})

        self.initFirstState()

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
            if self.interrupt != 0:
                continue

            self.eventInFirstState(event)

            if event.dataType == "Skill":
                pass

            elif event.dataType == "Buff":
                pass

        self.completeFirstState()
        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        self.skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],

                     [None, "冰蚕牵丝", ["2526", "27391", "6662"], "2745", True, 24, False, True, 0, 1],
                     [None, "圣手织天", ["13425", "13426"], "3028", True, 0, False, True, 18, 1],
                     [None, "千蝶吐瑞", ["2449"], "2748", True, 8, True, True, 60, 1],
                     [None, "迷仙引梦", ["15132"], "7255", True, 8, False, True, 30, 1],
                     [None, "仙王蛊鼎", ["2234"], "2747", True, 24, False, True, 120, 1],
                     [None, "玄水蛊", ["3702"], "3038", True, 0, False, True, 40, 1],
                     [None, "圣元阵", ["25058"], "13447", True, 0, False, True, 40, 1],
                     [None, "碧蝶引", ["2965"], "3025", True, 0, False, True, 0, 1],

                     # [None, "醉舞九天", ["6252"], "2746", False, 16, True, True, 0, 1],
                     [None, "化蝶", ["2228"], "2830", False, 0, False, True, 30, 1],
                     [None, "蛊虫献祭", ["2226"], "2762", False, 0, False, True, 30, 1],
                     [None, "蝶鸾", ["3054"], "2764", False, 0, False, True, 6, 1],
                     [None, "女娲补天", ["2230"], "2743", False, 0, False, True, 24, 1],
                     [None, "灵蛊", ["18584"], "2777", False, 0, False, True, 20, 3],
                     [None, "迷仙引梦·收", ["21825"], "11310", False, 0, False, True, 0, 1],
                     [None, "蛊惑众生", ["2231"], "2744", False, 0, False, True, 20, 1],
                     [None, "特效腰坠", ["yaozhui"], "3414", False, 0, False, True, 180, 1]
                    ]

        self.initSecondState()

        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计

        xwgdNumDict = {}  # 仙王蛊鼎触发次数
        firstXwgd = 0
        firstXwgdTaketime = 0
        qilongRateDict = {}  # 绮栊覆盖率

        # 技能统计
        dxSkill = SkillHealCounter("3051", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 蝶旋
        dcSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 蝶池
        # bcqsSkill = SkillHealCounter("2232", self.startTime, self.finalTime, self.haste)  # 冰蚕牵丝
        zwjtSkill = SkillHealCounter("6252", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 醉舞九天
        # ssztSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 圣手织天
        # qdtrSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 千蝶吐瑞
        mxymSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 迷仙引梦

        zwjtDict = BuffCounter("?", self.startTime, self.finalTime)  # 用buff类型来记录醉舞九天的具体时间
        mxymDict = BuffCounter("?", self.startTime, self.finalTime)  # 迷仙引梦记录
        xwgdDict = BuffCounter("?", self.startTime, self.finalTime)  # 锅记录
        ghzsDict = BuffCounter("?", self.startTime, self.finalTime)  # 蛊惑记录

        self.cyDict = BuffCounter("2844", self.startTime, self.finalTime)  # 蚕引
        cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        nvwaDict = BuffCounter("2315", self.startTime, self.finalTime)  # 女娲补天
        self.xjDict = BuffCounter("5950", self.startTime, self.finalTime)  # 献祭
        bdDict = BuffCounter("10237", self.startTime, self.finalTime)  # 碧蝶

        for line in self.bld.info.player:
            battleStat[line] = [0]
            xwgdNumDict[line] = 0

        self.qilongCounter = {}
        for key in self.bld.info.player:
            self.qilongCounter[key] = ShieldCounterNew("20831", self.startTime, self.finalTime)

        # 杂项
        wuhuoHeal = 0  # 无惑
        xjmjHeal = 0  # 献祭秘籍
        bdxjHeal = 0  # 碧蝶献祭
        qdtrLast = 0  # 千蝶施放统计cd
        mxymLast = 0  # 迷仙引梦统计cd
        self.instantNum = 0  # 瞬发冰蚕次数
        canyinNum = 0  # 蚕引次数
        diechiNum = 0  # 蝶池施放次数
        diechiCorrect = 0  # 蝶池正确施放次数
        diechiLast = 0  # 蝶池防止重复统计

        zwjtTime = getLength(16, self.haste)

        qdtrWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["2449"]], self.startTime, self.finalTime,
                                             self.haste, exclude=self.bossBh.badPeriodHealerLog)
        mxymWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["15132"]], self.startTime, self.finalTime,
                                             self.haste, exclude=self.bossBh.badPeriodHealerLog)

        self.unimportantSkill += ["3051", "3644", "3473",  # 蝶旋
                               "2957",  # 圣手织天壳
                               "2233", "6252",  # 醉舞 TODO 统计醉舞！
                               "15134",  # 迷仙引梦
                               "2998",  # 无惑
                               "2968",  # 打断成功
                               "18590",  # 打断伤害
                               "26771",  # 献祭少量治疗
                               "3023",  # 献祭解控
                               "3061",  # 碧蝶献祭治疗
                               "18884",  # 蝶池治疗
                               "2235",  # 千蝶壳
                               "2978",  # 招宠物判断技能
                               "2232",  # 冰蚕壳
                               "3052",  # 驱散实际效果
                               "28643",  # 绮栊
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            self.eventInSecondState(event)

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # 所有治疗技能都不计算化解.
                    continue

                if event.caster == self.mykey and event.scheme == 1:
                    if event.id in self.gcdSkillIndex:
                        # 特殊处理千蝶
                        if event.id == "2449":
                            if event.time - qdtrLast > 1000:
                                qdtrWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                            qdtrLast = event.time
                    elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                        desc = ""
                        index = self.nonGcdSkillIndex[event.id]
                        line = self.skillInfo[index]
                        self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                        skillObj = line[0]
                        record = True
                        if skillObj is None:
                            record = False
                        if event.id == "21825" and self.bh.log["special"] != [] and self.bh.log["special"][-1]["skillid"] == "21825" and event.time - self.bh.log["special"][-1]["start"] < 100:
                            record = False
                        if record:
                            skillObj.recordSkill(event.time, event.heal, event.healEff, self.ss.timeEnd, delta=-1)

                    # 统计不计入时间轴的治疗量
                    if event.id in ["3051", "3473"]:  # 蝶旋
                        dxSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                    if event.id in ["15134"]:  # 迷仙引梦
                        mxymSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        if event.time - mxymDict.log[-1][0] > 200:
                            mxymDict.setState(event.time - 2000, 1)
                            mxymDict.setState(event.time, 0)
                            if event.time - mxymLast > 5000:
                                mxymWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                            mxymLast = event.time
                    if event.id in ["18884"]:  # 蝶池
                        dcSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        #print("[Diechi]", event.time, event.heal, event.healEff)
                        if event.time - diechiLast > 5000:
                            diechiNum += 1
                        if event.time - diechiLast > 500:
                            state = bdDict.checkState(event.time - 50)
                            if state:
                                diechiCorrect += 1
                        diechiLast = event.time
                    if event.id in ["2998"]:  # 无惑
                        wuhuoHeal += event.healEff
                    if event.id in ["26771"]:  # 献祭秘籍
                        xjmjHeal += event.healEff
                    if event.id in ["3061"]:  # 碧蝶献祭
                        bdxjHeal += event.healEff
                    if event.id in ["6252"]:  # 醉舞九天
                        zwjtSkill.recordSkill(event.time, event.heal, event.healEff, 0)
                        # 醉舞也计入战斗效率中
                        if event.time - zwjtDict.log[-1][0] > 200:
                            zwjtDict.setState(event.time - zwjtTime, 1)
                            zwjtDict.setState(event.time, 0)
                    if event.id in ["2234"]:  # 仙王蛊鼎
                        if firstXwgd == 0:
                            firstXwgd = 1
                            if firstXwgdTaketime != 0:
                                xwgdDict.setState(self.startTime, 1)
                                xwgdDict.setState(firstXwgdTaketime, 0)
                        xwgdDict.setState(event.time, 1)
                        xwgdDict.setState(event.time + 60000, 0)
                    if event.id in ["23951"] and event.level == 51:
                        xwgdNumDict[event.target] += 1
                        if firstXwgd == 0:
                            firstXwgdTaketime = event.time


                if event.caster == self.mykey and event.scheme == 2:
                    # 统计HOT，然而五毒并没有HOT
                    pass

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.bld.info.player:
                        battleStat[event.caster][0] += event.damageEff

                # 统计蛊惑
                if event.id in ["2231"]:  # 蛊惑众生
                    if ghzsDict.log != [] and ghzsDict.log[-1][0] > event.time:
                        del ghzsDict.log[-1]
                    ghzsDict.setState(event.time, 1)
                    ghzsDict.setState(event.time + 30000, 0)

            elif event.dataType == "Buff":
                if event.id in ["12769"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    self.bh.setSpecialSkill(event.id, "cw特效", "14407",
                                       event.time, 0, "触发cw特效")
                    cwDict.setState(event.time, event.stack)
                if event.id in ["2315"] and event.target == self.mykey:  # 女娲
                    nvwaDict.setState(event.time, event.stack)
                if event.id in ["2316"] and event.caster == self.mykey:  # 蛊惑
                    if ghzsDict.log != [] and ghzsDict.log[-1][0] > event.time:
                        del ghzsDict.log[-1]
                    ghzsDict.setState(event.time, event.stack)
                if event.id in ["2844"] and event.target == self.mykey:  # 蚕引
                    prevStack = self.cyDict.checkState(event.time)
                    self.cyDict.setState(event.time, event.stack)
                    if event.stack > prevStack:
                        canyinNum += event.stack - prevStack
                if event.id in ["20831"] and event.caster == self.mykey:  # buff绮栊
                    self.qilongCounter[event.target].setState(event.time, event.stack)
                if event.id in ["5950"] and event.caster == self.mykey:  # 献祭
                    self.xjDict.setState(event.time, event.stack)
                if event.id in ["10237"] and event.caster == self.mykey:  # 碧蝶
                    bdDict.setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

        self.completeSecondState()

        # 计算DPS列表(Part 7)

        # 计算伤害
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0]

        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        for key in self.bld.info.player:
            liveCount = self.battleDict[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)  # 存活时间比例
            if self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog) - liveCount < 8000:  # 脱战缓冲时间
                liveCount = self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)
            self.battleTimeDict[key] = liveCount
            self.sumPlayer += liveCount / self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)

            time1 = self.qilongCounter[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            timeAll = liveCount
            qilongRateDict[key] = safe_divide(time1, timeAll)

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTimeDpsEff"] * 1000),
                   "xwgdNum": xwgdNumDict[line[0]],
                   "qilongRate": roundCent(qilongRateDict[line[0]]),
                   }
            self.result["dps"]["table"].append(res)

        # 计算绮栊覆盖率
        numRate = 0
        sumRate = 0
        for key in qilongRateDict:
            numRate += self.battleTimeDict[key]
            sumRate += qilongRateDict[key] * self.battleTimeDict[key]
        overallRate = safe_divide(sumRate, numRate)

        mxymDict.shrink(100)
        ghzsDict.shrink(100)
        zwjtDict.shrink(100)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 冰蚕牵丝
        bcqsSkill = self.calculateSkillInfo("bcqs", "2526")
        # 醉舞九天
        self.calculateSkillInfoDirect("zwjt", zwjtSkill)
        # 圣手织天
        ssztSkill = self.calculateSkillInfo("sszt", "13425")
        # 千蝶吐瑞
        qdtrSkill = self.calculateSkillInfo("qdtr", "2449")
        # 蝶池
        self.calculateSkillInfoDirect("dc", dcSkill)
        # 迷仙引梦
        self.calculateSkillInfoDirect("mxym", mxymSkill)
        num = self.battleTimeDict[self.mykey]
        sum = mxymDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        self.result["skill"]["mxym"]["cover"] = roundCent(safe_divide(sum, num))
        # 蝶旋
        self.calculateSkillInfoDirect("dx", dxSkill)
        # 杂项
        self.result["skill"]["nvwa"] = {}
        sum = nvwaDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        self.result["skill"]["nvwa"]["cover"] = roundCent(safe_divide(sum, num))
        self.result["skill"]["ghzs"] = {}
        num = self.battleTimeDict[self.mykey]
        sum = ghzsDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        self.result["skill"]["ghzs"]["cover"] = roundCent(safe_divide(sum, num))
        ghzsHps = 0
        if self.mykey in self.act.hps["player"] and "蛊惑众生" in self.act.hps["player"][self.mykey]["namedSkill"]:
            ghzsHps = int(self.act.hps["player"][self.mykey]["namedSkill"]["蛊惑众生"]["sum"] / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["ghzs"]["hps"] = ghzsHps
        self.result["skill"]["qilong"] = {}
        self.result["skill"]["qilong"]["cover"] = roundCent(overallRate)
        # 整体
        self.result["skill"]["general"] = {}
        # self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()
        self.result["skill"]["general"]["efficiencyNonGcd"] = self.bh.getNormalEfficiency("healer", zwjtDict.log)
        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)
        self.result["replay"]["mxym"] = mxymDict.log
        self.result["replay"]["xwgd"] = xwgdDict.log
        self.result["replay"]["ghzs"] = ghzsDict.log
        self.result["replay"]["zwjt"] = zwjtDict.log

        self.specialKey = {"bcqs-numPerSec": 10, "zwjt-numPerSec": 10, "general-efficiencyNonGcd": 20, "healer-rhps": 20}

        self.markedSkill = ["2226", "2230"]
        self.outstandingSkill = [qdtrWatchSkill]
        self.calculateSkillOverall()

        # 计算专案组的心法部分.
        # code 401 保证`冰蚕牵丝`或`醉舞九天`的触发次数
        bcNum = self.result["skill"]["bcqs"]["numPerSec"]
        bcRank = self.result["rank"]["bcqs"]["numPerSec"]["percent"]
        zwNum = self.result["skill"]["zwjt"]["numPerSec"]
        zwRank = self.result["rank"]["zwjt"]["numPerSec"]["percent"]
        rate = roundCent(max(bcRank, zwRank) / 100)
        res = {"code": 401, "bcNum": bcNum, "bcRank": bcRank, "zwNum": zwNum, "zwRank": zwRank, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 402 使用`蛊惑众生`
        cover = roundCent(self.result["skill"]["ghzs"]["cover"])
        res = {"code": 402, "cover": cover, "rate": cover}
        res["status"] = getRateStatus(res["rate"], 90, 50, 0)
        self.result["review"]["content"].append(res)

        # code 403 保证回蓝技能的使用次数
        scCandidate = []
        for id in ["2234"]:
            if id in self.nonGcdSkillIndex:
                scCandidate.append(self.skillInfo[self.nonGcdSkillIndex[id]][0])
            else:
                scCandidate.append(self.skillInfo[self.gcdSkillIndex[id]][0])
        scCandidate.append(mxymWatchSkill)

        rateSum = 0
        rateNum = 0
        numAll = []
        sumAll = []
        skillAll = []
        for skillObj in scCandidate:
            num = skillObj.getNum()
            sum = skillObj.getMaxPossible()
            skill = skillObj.name
            if skill in ["特效腰坠"] and num == 0:
                continue
            rateNum += 1
            rateSum += min(safe_divide(num, sum), 1)
            numAll.append(num)
            sumAll.append(sum)
            skillAll.append(skill)
        rate = roundCent(safe_divide(rateSum, rateNum), 4)
        res = {"code": 403, "skill": skillAll, "num": numAll, "sum": sumAll, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 80, 60, 40)
        self.result["review"]["content"].append(res)

        # code 404 不要回收`迷仙引梦`
        timeAll = mxymWatchSkill.getNum()
        timeCast = self.skillInfo[self.nonGcdSkillIndex["21825"]][0].getNum()
        rate = roundCent(1 - safe_divide(timeCast, timeAll))
        res = {"code": 404, "timeAll": timeAll, "timeCast": timeCast, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 0, 0)
        self.result["review"]["content"].append(res)

        # code 405 使用`蚕引`层数
        rate = roundCent(safe_divide(self.instantNum, canyinNum))
        res = {"code": 405, "sumAll": canyinNum, "timeCast": self.instantNum, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 50, 0)
        self.result["review"]["content"].append(res)

        # code 406 保留`碧蝶献祭`的会心增益到`蝶池`
        rate = roundCent(safe_divide(diechiCorrect, diechiNum))
        res = {"code": 406, "sumAll": diechiNum, "rightTime": diechiCorrect, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 50, 0)
        self.result["review"]["content"].append(res)

        self.calculateSkillFinal()

        # 横刀断浪更新整理
        # - 鼎的覆盖率、使用次数
        # - 专案组中单独分析鼎的次数，和迷仙引梦拆开
        # - 用rdps替换整体dps统计


    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", actorData={}):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - myname: 需要复盘的奶歌名.
        - actorData: 演员复盘得到的统计记录.
        '''
        super().__init__(config, fileNameInfo, path, bldDict, window, myname, actorData)
        self.haste = config.item["butian"]["speed"]
        self.public = config.item["butian"]["public"]
        self.occ = "butianjue"
        self.occCode = "6h"
        self.occPrint = "奶毒"


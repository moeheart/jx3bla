# Created by moeheart at 01/06/2022
# 奶花复盘，用于奶花复盘的生成，展示

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

class LiJingYiDaoWindow(HealerDisplayWindow):
    '''
    奶花复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴中的颜色深浅表示五个分队的握针剩余时间。注意，1-5队可能并不按顺序对应团队面板的1-5队。
部分技能上有数字标记，表示这个技能是对第几个小队施放的。同样，可能并不与游戏中对应。'''
        messagebox.showinfo(title='说明', message=text)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，奶歌复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#7f1fdf")
        frame5.place(x=10, y=250)

        wozhenDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        wozhenDisplayer.setImage("1519", "握针")
        wozhenDisplayer.setDouble("rate", "数量", "wozhen", "num", "numPerSec")
        wozhenDisplayer.setSingle("delay", "延迟", "wozhen", "delay")
        wozhenDisplayer.setSingle("int", "HPS", "wozhen", "HPS")
        wozhenDisplayer.setSingle("int", "生息HPS", "wozhen", "shengxiHPS")
        wozhenDisplayer.setSingle("percent", "覆盖率", "wozhen", "cover")
        wozhenDisplayer.export_image(frame5, 0)
        
        tizhenDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        tizhenDisplayer.setImage("395", "提针")
        tizhenDisplayer.setDouble("rate", "数量", "tizhen", "num", "numPerSec")
        tizhenDisplayer.setSingle("delay", "延迟", "tizhen", "delay")
        tizhenDisplayer.setSingle("int", "HPS", "tizhen", "HPS")
        tizhenDisplayer.setDouble("plus", "毫针HPS", "tizhen", "hzDirectHPS", "hzPercentHPS")
        tizhenDisplayer.setSingle("percent", "有效比例", "tizhen", "effRate")
        tizhenDisplayer.export_image(frame5, 1)
        
        changzhenDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        changzhenDisplayer.setImage("396", "长针")
        changzhenDisplayer.setDouble("rate", "数量", "changzhen", "num", "numPerSec")
        changzhenDisplayer.setSingle("delay", "延迟", "changzhen", "delay")
        changzhenDisplayer.setSingle("int", "HPS", "changzhen", "HPS")
        changzhenDisplayer.setSingle("int", "月华HPS", "changzhen", "yuehuaHPS")
        changzhenDisplayer.setSingle("percent", "有效比例", "changzhen", "effRate")
        changzhenDisplayer.export_image(frame5, 2)

        bizhenDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        bizhenDisplayer.setImage("1518", "彼针")
        bizhenDisplayer.setDouble("rate", "数量", "bizhen", "num", "numPerSec")
        bizhenDisplayer.setSingle("delay", "延迟", "bizhen", "delay")
        bizhenDisplayer.setSingle("int", "HPS", "bizhen", "HPS")
        bizhenDisplayer.setSingle("percent", "有效比例", "bizhen", "effRate")
        bizhenDisplayer.setSingle("percent", "述怀覆盖", "bizhen", "shCover")
        bizhenDisplayer.export_image(frame5, 3)

        lzwhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        lzwhDisplayer.setImage("17705", "落子无悔")
        lzwhDisplayer.setDouble("rate", "数量", "lzwh", "num", "numPerSec")
        lzwhDisplayer.setSingle("int", "HPS", "lzwh", "HPS")
        lzwhDisplayer.export_image(frame5, 4)

        suiyuDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        suiyuDisplayer.setImage("13441", "碎玉")
        suiyuDisplayer.setDouble("rate", "数量", "suiyu", "num", "numPerSec")
        suiyuDisplayer.setSingle("int", "HPS", "suiyu", "HPS")
        suiyuDisplayer.export_image(frame5, 5)

        # chunniDisplayer.setImage("413", "春泥护花")
        # chunniDisplayer.setDouble("rate", "数量", "chunni", "num", "numPerSec")
        # chunniDisplayer.export_image(frame5, 4)

        # longwuDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        # longwuDisplayer.setImage("16221", "泷雾")
        # longwuDisplayer.setDouble("rate", "数量", "longwu", "num", "numPerSec")
        # longwuDisplayer.setSingle("delay", "延迟", "longwu", "delay")
        # longwuDisplayer.setSingle("int", "HPS", "longwu", "HPS")
        # longwuDisplayer.setSingle("percent", "有效比例", "longwu", "effRate")
        # longwuDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setDouble("int", "春泥次数", "chunni", "num", "numPerSec")
        info1Displayer.setSingle("int", "清疏HPS", "qingshu", "HPS")
        info1Displayer.setSingle("int", "寒清次数", "general", "HanQingNum")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("int", "rDPS", "general", "rdps")
        info2Displayer.setSingle("percent", "秋肃覆盖率", "qiusu", "cover")
        info2Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        # info2Displayer.setSingle("int", "秋肃DPS", "qiusu", "dps")
        info2Displayer.setSingle("percent", "战斗效率", "general", "efficiency")
        info2Displayer.export_text(frame5, 7)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

    def renderReplay(self):
        '''
        渲染回放信息(Part 6)，奶歌复盘特化.
        '''
        window = self.window
        # Part 6: 回放

        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#7f1fdf")
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
        if "heat" in self.result["replay"]:
            yPos = [31, 39, 47, 55, 63, 70]
            for j in range(5):
                nowTimePixel = 0
                for line in self.result["replay"]["heat"]["timeline"][j]:
                    if line == 0:
                        color = "#ff7777"
                    else:
                        color = getColorHex((int(255 - (255 - 127) * line / 100),
                                             int(255 - (255 - 31) * line / 100),
                                             int(255 - (255 - 223) * line / 100)))
                    canvas6.create_rectangle(nowTimePixel, yPos[j], nowTimePixel + 5, yPos[j+1], fill=color, width=0)
                    nowTimePixel += 5

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
                if self.config.item["lijing"]["stack"] != "不堆叠" and i-j >= int(self.config.item["lijing"]["stack"]):
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
                        # 绘制目标分队
                        if "team" in record_single and record_single["team"] != 0:
                            canvas6.create_text(posStart + 7, 80, text="%d" % record_single["team"], font="Arial 12 bold",
                                                fill="#ff0000")
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
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#7f1fdf")
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
        tb.AppendHeader("等效DPS", "全程去除秋肃增益后的DPS，注意包含重伤时间。")
        tb.AppendHeader("寒清次数", "触发寒清的次数。如果被击未触发寒清则不计入。")
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.AppendContext(record["HanQingNum"])
            tb.EndOfLine()

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9)，奶歌复盘特化.
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#7f1fdf")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="奶花PVE群：294479046").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb, bg='#777777')
            b2.place(x=40, y=90)

        tk.Label(frame9, text="广告位招租").place(x=40, y=140)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - config: 设置类
        - result: 奶花复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#7f1fdf")
        self.title = '奶花复盘'
        self.occ = "lijingyidao"

class LiJingYiDaoReplayer(HealerReplay):
    '''
    奶花复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        self.window.setNotice({"t2": "加载奶花复盘...", "c2": "#7f1fdf"})

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

        wozhenSkill = SkillHealCounter("101", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 握针
        # tizhenSkill = SkillHealCounter("138", self.startTime, self.finalTime, self.haste)  # 提针
        # changzhenSkill = SkillHealCounter("142", self.startTime, self.finalTime, self.haste)  # 长针
        # bizhenSkill = SkillHealCounter("140", self.startTime, self.finalTime, self.haste)  # 彼针
        # longwuSkill = SkillHealCounter("28541", self.startTime, self.finalTime, self.haste)  # 泷雾

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        self.skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],

                     [None, "握针", ["101"], "1519", True, 0, False, True, 0, 1],
                     [None, "提针", ["22792", "22886"], "395", True, 24, False, True, 0, 1],
                     [None, "长针", ["3038"], "396", True, 48, False, True, 0, 1],
                     [None, "彼针", ["26666", "26667", "26668"], "1518", True, 24, False, True, 6, 1],
                     [None, "春泥护花", ["132"], "413", True, 0, False, True, 36, 1],
                     [None, "利针", ["2654"], "3004", True, 16, False, True, 0, 1],
                     [None, "清风垂露", ["133"], "1523", True, 0, False, True, 3, 1],
                     [None, "折叶笼花", ["14963"], "16602", True, 0, False, True, 70, 1],
                     [None, "碧水滔天", ["131"], "1525", True, 0, False, True, 95, 1],
                     [None, "大针", ["24911"], "14148", True, 0, False, True, 50, 1],
                     [None, "天工甲士", ["28724"], "16223", True, 80, False, True, 0, 1],
                     [None, "天工", ["28720"], "16224", True, 32, False, False, 0, 1],
                     [None, "泷雾", ["28541"], "16224", True, 16, True, True, 0, 1],
                     [None, "护本", ["28555"], "16222", True, 0, False, True, 10, 1],
                     [None, "脱离机甲", ["28480"], "16225", True, 0, False, True, 0, 1],
                     [None, "商阳指", ["180"], "1514", True, 0, False, True, 0, 1],
                     [None, "阳明指", ["14941"], "1527", True, 24, False, True, 0, 1],

                     [None, "水月无间", ["136"], "1522", False, 0, False, True, 60, 1],
                     [None, "听风吹雪", ["2663"], "2998", False, 0, False, True, 75, 1],
                     [None, "落子无悔", ["32750"], "17705", False, 0, False, True, 70, 1],
                     [None, "特效腰坠", ["yaozhui"], "3414", False, 0, False, True, 180, 1]
                    ]

        self.initSecondState()
        self.initTeamDetect()

        battleStat = {}  # 伤害占比统计，[无秋肃伤害，有秋肃伤害]
        damageDict = {}  # 伤害统计
        hanqingNumDict = {}  # 寒清触发次数
        hanqingLastTime = {}  # 寒清上次触发

        # 技能统计
        wozhenBuff = SkillHealCounter("631", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 握针
        shuhuaiBuff = SkillHealCounter("5693", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 述怀
        lzwhSkill = SkillHealCounter("32750", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 落子无悔
        sySkill = SkillHealCounter("28645", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 碎玉

        self.xqxDict = BuffCounter("6266", self.startTime, self.finalTime)  # 行气血
        self.cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        self.shuiyueDict = BuffCounter("412", self.startTime, self.finalTime)  # 水月

        wozhenDict = {}  # 握针
        shuhuaiDict = {}  # 述怀

        for line in self.bld.info.player:
            hanqingNumDict[line] = 0
            hanqingLastTime[line] = 0
            wozhenDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 握针
            shuhuaiDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 述怀
            battleStat[line] = [0, 0]

        lastSkillTime = self.startTime

        # 秋肃统计
        qiusuTarget = ""
        qiusuTime = 0
        qiusuCounter = BuffCounter("0", self.startTime, self.finalTime)

        # 墨意、黑白子推测（这个实现逻辑非常简单，因为不需要回溯搜索）
        self.moyiInfer = [[self.startTime, 0]]
        self.usedMoyi = 0
        self.wastedMoyi = 0
        self.heiziInfer = [[self.startTime, 0]]
        self.baiziInfer = [[self.startTime, 0]]
        self.sumHeizi = 0
        self.sumBaizi = 0
        self.moyiActiveTime = 0  # 墨意对齐生效的时间，在buff发生变化之后进行检测
        self.moyiBuffNum = 0  # 墨意层数要求，有层数优先级高于0层

        # 落子统计
        self.luoziWhite = 0
        self.luoziBlack = 0
        self.luoziNone = 0

        # 杂项
        qingshuHeal = 0
        wozhenDirectHeal = 0
        changzhenAOEHeal = 0
        haozhenDirectHeal = 0  # 毫针本体
        haozhenPercentHeal = 0  # 毫针贯体
        shuiyueStack = 0
        shuiyueNum = 0
        # xqxStack = 0
        # xqxNum = 0
        self.instantNum = 0
        self.instantChangzhenNum = 0
        self.lastInstant = 0
        weichaoSingleList = []
        weichaoNum = 0
        weichaoSkill = 0
        weichaoEff = 0
        weichaoEffList = []

        # 监控cd用的类
        # lzwhWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["32750"]], self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)

        self.unimportantSkill += ["6112",  # 清疏
                               "6894",  # 握针直接治疗
                               "6103",  # 月华
                               "29748",  # 毫针
                               "598",  # 生聚
                               "6111",  # 清疏叠层数
                               "14660",  # 长针溅射  # TODO 微潮判定
                               "1588",  # 千机判定
                               "142",  # 长针壳技能
                               "138",  # 提针壳技能
                               "140", "14664", "27033", "27034",  # 彼针壳技能
                               "140", "14664", "27033", "27034",  # 彼针壳技能
                               "14665",  # 零落判定  # TODO 微潮判定
                               "27145",  # 束彼壳技能
                               "21308", "23572", "22043", "22047", "21309",  # 大笛子
                               "23405", "23703",   # 大笛子
                               "22077",  # 大笛子治疗壳技能
                               "14434",  # 阵眼
                               "27135",  # 彼针x行气血
                               "23955",  # 大笛子启动
                               "22208",  # 腰带大附魔
                               "25788",  # 奶花cw小特效
                               "23753",  # 大笛子人数检测
                               "1857",  # 春泥，可能是青律
                               "16",  # 判官笔法
                               "28465",  # 天工甲士开始读条
                               "28540",  # 泷雾引导
                               "2872", "2873",  # 利针实际作用
                               "6105",  # 彼针挂握针
                               "100",  # 星楼 TODO 可以加统计
                               "28645",  # 碎玉
                               "32923",  # 微潮新判定
                               "32377",  # 白子触发
                               "32376",  # 黑字触发
                               "27144",  # 彼针范围
                               "32381",  # 落子壳技能
                               "26695",  # 碎玉检索
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            self.eventInTeamDetect(event)
            self.eventInSecondState(event)

            # 墨意推断
            if event.time >= self.moyiActiveTime and self.moyiActiveTime != 0:
                # 修正不合理的墨意值
                lastMoyi = self.moyiInfer[-1][1]
                # print("[MoyiCorrect]", event.time, self.moyiBuffNum, lastMoyi)
                if int(lastMoyi / 20) != self.moyiBuffNum:
                    correctNum = lastMoyi
                    # 尝试向上修复
                    while int(correctNum / 20) > self.moyiBuffNum:
                        correctNum = max(correctNum - 10, 0)
                    # 尝试向下修复
                    while int(correctNum / 20) < self.moyiBuffNum:
                        correctNum = min(correctNum + 10, 100)
                    # print("[MoyiChange]", correctNum)
                    self.moyiInfer.append([event.time, correctNum])
                # 重置
                self.moyiActiveTime = 0
                self.moyiBuffNum = 0

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # 所有治疗技能都不计算化解.
                    continue

                if event.caster == self.mykey and event.scheme == 1:
                    if event.id in self.gcdSkillIndex:
                        pass
                    elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                        desc = ""
                        record = True
                        if event.id in ["136"]:  # 水月
                            # 获得墨意推测
                            lastMoyi = self.moyiInfer[-1][1]
                            maxMoyi = 100
                            nowMoyi = lastMoyi + 60
                            if nowMoyi > maxMoyi:
                                self.wastedMoyi += nowMoyi - maxMoyi
                                nowMoyi = maxMoyi
                            self.moyiInfer.append([event.time, nowMoyi])
                            self.moyiActiveTime = 0  # 取消这附近的墨意判定
                        if event.id in ["32750"]:  # 落子无悔
                            # print("[lijing]Detect lozi")
                            if self.bh.log["special"] != [] and self.bh.log["special"][-1]["skillid"] == "32750" and event.time - self.bh.log["special"][-1]["start"] < 100:
                                record = False
                            else:
                                # lzwhWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                                heiziNum = self.heiziInfer[-1][1]
                                baiziNum = self.baiziInfer[-1][1]
                                if heiziNum > baiziNum:
                                    self.luoziBlack += 1
                                elif baiziNum > heiziNum:
                                    self.luoziWhite += 1
                                else:
                                    self.luoziNone += 1
                        if record:
                            index = self.nonGcdSkillIndex[event.id]
                            line = self.skillInfo[index]
                            self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                            skillObj = line[0]
                            if skillObj is not None:
                                skillObj.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=self.ss.timeEnd, delta=-1)

                    # 统计不计入时间轴的治疗量
                    if event.id in ["6112"]:  # 清疏
                        qingshuHeal += event.healEff
                    if event.id in ["6894"]:  # 握针直接治疗
                        wozhenDirectHeal += event.healEff
                    if event.id in ["6103"]:  # 长针AOE
                        changzhenAOEHeal += event.healEff
                    if event.id in ["29748"]:  # 毫针
                        haozhenDirectHeal += event.healEff
                    if event.id in ["23951"] and event.level == 2:  # 毫针贯体
                        haozhenPercentHeal += event.healEff
                    if event.id in ["14660"]:
                        # 根据微潮统计长针有效目标数
                        timeDiff = event.time - weichaoSkill
                        effFlag = 0
                        if event.target in wozhenDict and wozhenDict[event.target].checkState(event.time) == 0:
                            effFlag = 1
                        if timeDiff > 100:
                            if weichaoNum != 0:
                                weichaoSingleList.append(weichaoNum)
                            if weichaoEff != 0:
                                weichaoEffList.append(weichaoEff)
                            weichaoNum = 1
                            weichaoEff = effFlag
                        else:
                            weichaoNum += 1
                            weichaoEff += effFlag
                        weichaoSkill = event.time
                    if event.id in ["32750"]:  # 落子无悔
                        lzwhSkill.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=event.time)
                    if event.id in ["28645"]:  # 碎玉
                        sySkill.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=event.time)
                    if event.id in ["180"]:  # 商阳指
                        # 秋肃生成
                        qiusuTarget = event.target
                        qiusuTime = event.time
                        if qiusuCounter.log != [] and qiusuCounter.log[-1][1] == 0 and qiusuCounter.log[-1][0] > event.time:
                            del qiusuCounter.log[-1]
                        qiusuCounter.setState(event.time, 1)
                        qiusuCounter.setState(event.time + 40000, 0)

                if event.caster == self.mykey and event.scheme == 2:
                    if event.id in ["631"]:  # 握针
                        wozhenBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=lastSkillTime)
                        # print("[WozhenFlag]", event.time, event.target, self.bld.info.getName(event.target))
                        if event.target in hanqingNumDict and event.time - hanqingLastTime[event.target] < 250:
                            hanqingNumDict[event.target] += 1
                    if event.id in ["5693"]:  # 述怀
                        shuhuaiBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=lastSkillTime)

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    # 秋肃累计
                    if event.target in self.bld.info.npc and event.caster in self.bld.info.player:
                        if event.target == qiusuTarget and event.time - qiusuTime < 40000:
                            battleStat[event.caster][1] += event.damageEff
                        else:
                            battleStat[event.caster][0] += event.damageEff

                # 统计寒清
                if event.id in ["18274"] and event.target in hanqingNumDict:  # and event.caster == self.mykey:
                    # hanqingNumDict[event.target] += 1
                    hanqingLastTime[event.target] = event.time
                    # print("[HanqingFlag]", event.time, event.target, self.bld.info.player[event.target].name)

                # if event.target in self.bld.info.player and event.damageEff > 0:
                #     print("[DamageFlag]", event.time, event.target, self.bld.info.getName(event.target), event.damageEff, self.bld.info.getSkillName(event.full_id))

                # if event.id in ["631"]:
                #     print("[WozhenTest]", parseTime((event.time-self.startTime)/1000), event.target, event.healEff, event.fullResult)

            elif event.dataType == "Buff":

                # if event.id in ["20399"]:
                #     print("[ZikuRecord]", parseTime((event.time-self.startTime)/1000), event.target, event.stack)

                if event.id in ["12770"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    self.bh.setSpecialSkill(event.id, "cw特效", "14404",
                                       event.time, 0, "触发cw特效")
                    self.cwDict.setState(event.time, event.stack)
                if event.id in ["6266"] and event.target == self.mykey:  # 行气血
                    self.xqxDict.setState(event.time, event.stack)
                    if event.time + 500 > self.moyiActiveTime and (self.moyiBuffNum == 0 or event.stack != 0):
                        # 修正墨意推测
                        self.moyiActiveTime = event.time + 500
                        self.moyiBuffNum = event.stack

                if event.id in ["6265"] and event.target == self.mykey and event.stack == 0:  # 行气血回复墨意，这里用0层推测，可能有不准确的地方
                    # 获得墨意推测
                    lastMoyi = self.moyiInfer[-1][1]
                    maxMoyi = 60
                    nowMoyi = lastMoyi + 10
                    sf = self.shuiyueDict.checkState(event.time - 200)
                    if sf:
                        maxMoyi = 100
                    if nowMoyi > maxMoyi:
                        self.wastedMoyi += nowMoyi - maxMoyi
                        nowMoyi = maxMoyi
                    self.moyiInfer.append([event.time, nowMoyi])
                if event.id in ["412"] and event.target == self.mykey:  # 水月无间
                    self.shuiyueDict.setState(event.time, event.stack)
                    # if event.stack > shuiyueStack:
                    #     shuiyueNum += event.stack
                    # shuiyueStack = event.stack
                    if event.time + 500 > self.moyiActiveTime and (self.moyiBuffNum == 0 or event.stack != 0):
                        # 修正墨意推测
                        self.moyiActiveTime = event.time + 500
                        self.moyiBuffNum = event.stack
                if event.id in ["631"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 握针
                    wozhenDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                    # print("[WozhenTest]", event.time, event.id, event.stack, self.bld.info.player[event.target].name, event.end - event.frame)
                if event.id in ["5693"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 述怀
                    shuhuaiDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                if event.id in ["24143", "24144", "24145", "24146", "24147"] and event.target == self.mykey:  # 黑子buff
                    heiziNum = self.heiziInfer[-1][1]
                    if event.stack == 1:
                        heiziNum += 1
                    elif heiziNum > 0:
                        heiziNum -= 1
                    self.heiziInfer.append([event.time, heiziNum])
                if event.id in ["24138", "24139", "24140", "24141", "24142"] and event.target == self.mykey:  # 白子buff
                    baiziNum = self.baiziInfer[-1][1]
                    if event.stack == 1:
                        baiziNum += 1
                    elif baiziNum > 0:
                        baiziNum -= 1
                    self.baiziInfer.append([event.time, baiziNum])
            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

        self.completeSecondState()
        self.completeTeamDetect()

        if weichaoNum != 0:
            weichaoSingleList.append(weichaoNum)
        if weichaoEff != 0:
            weichaoEffList.append(weichaoEff)

        # 记录每次技能的目标队伍
        for i in range(len(self.bh.log["normal"])):
            if "team" in self.bh.log["normal"][i]:
                if self.bh.log["normal"][i]["team"] in self.teamCluster:
                    self.bh.log["normal"][i]["team"] = self.teamCluster[self.bh.log["normal"][i]["team"]]
                else:
                    self.bh.log["normal"][i]["team"] = 0

        # 计算DPS列表(Part 7)

        # 计算伤害
        numdam1 = 0
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0] + line[1] / 1.05
            numdam1 += line[1] / 1.05 * 0.05
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

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTimeDpsEff"] * 1000),
                   "HanQingNum": hanqingNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        # 计算寒清次数
        numHanQing = 0
        for key in hanqingNumDict:
            numHanQing += hanqingNumDict[key]

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 队伍HOT统计初始化
        hotHeat = [[], [], [], [], []]
        # 握针
        self.calculateSkillInfoDirect("wozhen", wozhenBuff)
        # self.result["skill"]["wozhen"] = {}
        # self.result["skill"]["wozhen"]["num"] = wozhenBuff.getNum()
        # self.result["skill"]["wozhen"]["numPerSec"] = roundCent(
        #     self.result["skill"]["wozhen"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        # effHeal = wozhenBuff.getHealEff()
        # self.result["skill"]["wozhen"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["wozhen"]["shengxiHPS"] = int(wozhenDirectHeal / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["wozhen"]["delay"] = int(wozhenSkill.getAverageDelay())
        num = 0
        sum = 0
        for key in wozhenDict:
            singleDict = wozhenDict[key]
            num += self.battleTimeDict[key]
            sum += singleDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            singleHeat = singleDict.getHeatTable()
            if self.teamCluster[key] <= 5:
                if len(hotHeat[self.teamCluster[key] - 1]) == 0:
                    for line in singleHeat["timeline"]:
                        hotHeat[self.teamCluster[key] - 1].append(line)
                else:
                    for i in range(len(singleHeat["timeline"])):
                        hotHeat[self.teamCluster[key] - 1][i] += singleHeat["timeline"][i]
        self.result["skill"]["wozhen"]["cover"] = roundCent(safe_divide(sum, num))
        # 计算HOT统计
        for i in range(len(hotHeat)):
            if i+1 >= len(self.numCluster) or self.numCluster[i+1] == 0:
                continue
            for j in range(len(hotHeat[i])):
                hotHeat[i][j] = int(hotHeat[i][j] / self.numCluster[i+1] * 100)
        # print("[self.teamCluster]", self.teamCluster)
        # print("[HotHeat]", hotHeat)
        # print("[HotHeat0]", hotHeat[0])
        # 提针
        tizhenSkill = self.calculateSkillInfo("tizhen", "22792")
        self.result["skill"]["tizhen"]["hzDirectHPS"] = int(haozhenDirectHeal / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["tizhen"]["hzPercentHPS"] = int(haozhenPercentHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 长针
        changzhenSkill = self.calculateSkillInfo("changzhen", "3038")
        self.result["skill"]["changzhen"]["yuehuaHPS"] = int(changzhenAOEHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 彼针
        bizhenSkill = self.calculateSkillInfo("bizhen", "26666")
        num = 0
        sum = 0
        for key in shuhuaiDict:
            singleDict = shuhuaiDict[key]
            num += self.battleTimeDict[key]
            sum += singleDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        self.result["skill"]["bizhen"]["shCover"] = roundCent(safe_divide(sum, num))

        # 春泥护花
        chunniSkill = self.calculateSkillInfo("chunni", "132")
        # 泷雾
        longwuSkill = self.calculateSkillInfo("longwu", "28541")

        # 秋肃
        self.result["skill"]["qiusu"] = {}
        # num = self.battleTimeDict[self.mykey]
        # 这里改成所有玩家里最长的那个
        num = max(self.battleTimeDict.values())
        sum = qiusuCounter.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        sum2 = qiusuCounter.buffTimeIntegral()

        # print("[qiusuDebug/Num]", num)
        # print("[qiusuDebug/Sum]", sum)
        # # print("[qiusuDebug/Sum2]", sum2)
        # print(self.bh.badPeriodHealerLog)
        # print(self.battleTimeDict)
        # print(qiusuCounter.log)

        self.result["skill"]["qiusu"]["cover"] = roundCent(safe_divide(sum, num))
        self.result["skill"]["qiusu"]["dps"] = int(numdam1 / self.result["overall"]["sumTimeDpsEff"] * 1000)
        # 杂项
        self.result["skill"]["qingshu"] = {}
        self.result["skill"]["qingshu"]["HPS"] = int(qingshuHeal / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["lzwh"] = {}
        self.calculateSkillInfoDirect("lzwh", lzwhSkill)
        self.result["skill"]["suiyu"] = {}
        self.calculateSkillInfoDirect("suiyu", sySkill)

        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["HanQingNum"] = numHanQing
        # self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()
        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)
        self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}
        self.result["replay"]["moyi"] = self.moyiInfer
        self.result["replay"]["heizi"] = self.heiziInfer
        self.result["replay"]["baizi"] = self.baiziInfer
        self.result["replay"]["qiusu"] = qiusuCounter.log
        self.specialKey = {"wozhen-numPerSec": 20, "general-efficiency": 20, "healer-rhps": 20, "qiusu-cover": 20}
        self.markedSkill = ["132", "136", "2663", "14963", "24911", "32750"]
        self.outstandingSkill = []
        self.calculateSkillOverall()
        # 计算专案组的心法部分.

        if self.actorData["boss"] not in ["苏凤楼"]:
            # code 201 保证`秋肃`的覆盖率
            cover = self.result["skill"]["qiusu"]["cover"]
            coverRank = self.result["rank"]["qiusu"]["cover"]["percent"]
            res = {"code": 201, "cover": cover, "rank": coverRank, "rate": roundCent(coverRank / 100)}
            res["status"] = getRateStatus(res["rate"], 75, 50, 25)
            self.result["review"]["content"].append(res)

        # code 202 保证`握针`的覆盖率
        cover = self.result["skill"]["wozhen"]["cover"]
        coverRank = self.result["rank"]["wozhen"]["cover"]["percent"]
        res = {"code": 202, "cover": cover, "rank": coverRank, "rate": roundCent(coverRank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # # code 203 不要浪费瞬发次数
        # rate = roundCent(safe_divide(self.instantNum, shuiyueNum + xqxNum))
        # res = {"code": 203, "timeShuiyue": shuiyueNum, "timeXqx": xqxNum, "timeCast": self.instantNum, "rate": rate}
        # res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        # self.result["review"]["content"].append(res)
        #
        # # code 204 优先瞬发`长针`
        # rate = roundCent(safe_divide(self.instantChangzhenNum, self.instantNum))
        # res = {"code": 204, "timeCast": self.instantNum, "timeChangzhen": self.instantChangzhenNum, "rate": rate}
        # res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        # self.result["review"]["content"].append(res)

        # code 205 选择合适的`长针`目标
        # num = 0
        # sum = 0
        # for i in weichaoSingleList:
        #     sum += 1
        #     if i >= 4:
        #         num += 1
        # coverRate = roundCent(safe_divide(num, sum))
        # res = {"code": 205, "time": sum, "coverTime": num, "rate": coverRate}
        # res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        # self.result["review"]["content"].append(res)

        # code 206 提高握针扩散效率
        num = 0
        sum = 0
        for i in weichaoEffList:
            sum += 1
            num += i
        cover = roundCent(safe_divide(num, sum))
        rate = roundCent(safe_divide(num, sum) / 4)
        res = {"code": 206, "cover": cover, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 50, 0)
        self.result["review"]["content"].append(res)

        # code 207 优先使用`水月无间`瞬发`长针`
        rate = roundCent(safe_divide(self.instantChangzhenNum, self.instantNum))
        res = {"code": 207, "timeCast": self.instantNum, "timeChangzhen": self.instantChangzhenNum, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 70, 50)
        self.result["review"]["content"].append(res)

        # code 208 充分利用墨意
        rate = roundCent(safe_divide(self.usedMoyi, self.usedMoyi + self.wastedMoyi))
        res = {"code": 208, "sumMoyi": self.usedMoyi + self.wastedMoyi, "wastedMoyi": self.wastedMoyi, "usedMoyi": self.usedMoyi, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 50, 0)
        self.result["review"]["content"].append(res)

        # code 209 使用`落子无悔`的buff效果
        rate = roundCent(safe_divide(self.luoziBlack + self.luoziWhite, self.luoziBlack + self.luoziWhite + self.luoziNone))
        if rate < 1e-10:
            rate = 1.0
        res = {"code": 209, "sumBlack": self.luoziBlack, "sumWhite": self.luoziWhite, "sumNone": self.luoziNone, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 50, 0)
        self.result["review"]["content"].append(res)

        self.calculateSkillFinal()

        # print("[LijingTest]")
        # print(self.result["replay"]["moyi"])
        # print(self.result["replay"]["heizi"])
        # print(self.result["replay"]["baizi"])
        # for line in self.result["review"]["content"]:
        #     print(line)


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
        self.haste = config.item["lijing"]["speed"]
        self.public = config.item["lijing"]["public"]
        self.occ = "lijingyidao"
        self.occCode = "2h"
        self.occPrint = "奶花"


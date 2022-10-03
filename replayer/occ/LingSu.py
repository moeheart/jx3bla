# Created by moeheart at 11/14/2021
# 灵素复盘，用于灵素复盘的生成，展示

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *
from window.HealerDisplayWindow import HealerDisplayWindow, SingleSkillDisplayer
from replayer.occ.Healer import HealerReplay

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

class LingSuWindow(HealerDisplayWindow):
    '''
    灵素复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴由上到下分别表示：药性、千枝绽蕊、青川濯莲。'''
        messagebox.showinfo(title='说明', message=text)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，灵素复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#00ac99")
        frame5.place(x=10, y=250)

        lszhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        lszhDisplayer.setImage("16025", "灵素中和")
        lszhDisplayer.setDouble("rate", "数量", "lszh", "num", "numPerSec")
        lszhDisplayer.setSingle("int", "HPS", "lszh", "HPS")
        lszhDisplayer.export_image(frame5, 0)
        
        bzhfDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        bzhfDisplayer.setImage("15411", "白芷含芳")
        bzhfDisplayer.setDouble("rate", "数量", "bzhf", "num", "numPerSec")
        bzhfDisplayer.setSingle("delay", "延迟", "bzhf", "delay")
        bzhfDisplayer.setSingle("int", "HPS", "bzhf", "HPS")
        bzhfDisplayer.setSingle("percent", "有效比例", "bzhf", "effRate")
        bzhfDisplayer.export_image(frame5, 1)
        
        cshxDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        cshxDisplayer.setImage("15414", "赤芍寒香")
        cshxDisplayer.setDouble("rate", "数量", "cshx", "num", "numPerSec")
        cshxDisplayer.setSingle("delay", "延迟", "cshx", "delay")
        cshxDisplayer.setSingle("int", "HOT HPS", "cshx", "HPS")
        cshxDisplayer.setSingle("int", "本体数量", "cshx", "skillNum")
        cshxDisplayer.setSingle("int", "本体HPS", "cshx", "skillHPS")
        cshxDisplayer.export_image(frame5, 2)

        dgsnDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        dgsnDisplayer.setImage("15412", "当归四逆")
        dgsnDisplayer.setDouble("rate", "数量", "dgsn", "num", "numPerSec")
        dgsnDisplayer.setSingle("delay", "延迟", "dgsn", "delay")
        dgsnDisplayer.setSingle("int", "HPS", "dgsn", "HPS")
        dgsnDisplayer.setSingle("percent", "有效比例", "dgsn", "effRate")
        dgsnDisplayer.export_image(frame5, 3)

        qczlDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        qczlDisplayer.setImage("15420", "青川濯莲")
        qczlDisplayer.setDouble("rate", "数量", "qczl", "num", "numPerSec")
        qczlDisplayer.setSingle("int", "HPS", "qczl", "HPS")
        qczlDisplayer.setSingle("percent", "有效比例", "qczl", "effRate")
        qczlDisplayer.export_image(frame5, 4)

        ygzxDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        ygzxDisplayer.setImage("15400", "银光照雪")
        ygzxDisplayer.setDouble("rate", "数量", "ygzx", "num", "numPerSec")
        ygzxDisplayer.setSingle("int", "HPS", "ygzx", "HPS")
        ygzxDisplayer.setSingle("percent", "有效比例", "ygzx", "effRate")
        ygzxDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "七情数量", "qqhh", "num")
        info1Displayer.setSingle("int", "七情HPS", "qqhh", "HPS")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("percent", "配伍比例", "general", "PeiwuRate")
        info2Displayer.setSingle("int", "飘黄数量", "general", "PiaohuangNum")
        info2Displayer.setSingle("int", "配伍DPS", "general", "PeiwuDPS")
        info2Displayer.setSingle("int", "飘黄DPS", "general", "PiaohuangDPS")
        info2Displayer.setSingle("percent", "战斗效率", "general", "efficiency")
        info2Displayer.export_text(frame5, 7)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

    def renderReplay(self):
        '''
        渲染回放信息(Part 6)，灵素复盘特化.
        '''
        window = self.window
        # Part 6: 回放

        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#00ac99")
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
        # 药性
        for i in range(1, len(self.result["replay"]["yaoxing"])):
            posStart = int((self.result["replay"]["yaoxing"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["yaoxing"][i][0] - startTime) / 100)
            yaoxing = self.result["replay"]["yaoxing"][i-1][1]
            color = "#ffffff"
            if yaoxing < 0:
                color = getColorHex((int(255 + (255 - 255) * yaoxing / 5),
                                     int(255 + (255 - 128) * yaoxing / 5),
                                     int(255 + (255 - 128) * yaoxing / 5)))
            elif yaoxing > 0:
                color = getColorHex((int(255 - (255 - 0) * yaoxing / 5),
                                     int(255 - (255 - 192) * yaoxing / 5),
                                     int(255 - (255 - 255) * yaoxing / 5)))
            canvas6.create_rectangle(posStart, 31, posEnd, 50, fill=color, width=0)
        # 千枝
        for i in range(1, len(self.result["replay"]["qianzhi"])):
            posStart = int((self.result["replay"]["qianzhi"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["qianzhi"][i][0] - startTime) / 100)
            if posEnd - posStart < 3:
                posEnd = posStart + 3
            qianzhi = self.result["replay"]["qianzhi"][i-1][1]
            if qianzhi == 1:
                canvas6.create_rectangle(posStart, 51, posEnd, 60, fill="#64afb4", width=0)
        # 青川
        for i in range(1, len(self.result["replay"]["qingchuan"])):
            posStart = int((self.result["replay"]["qingchuan"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["qingchuan"][i][0] - startTime) / 100)
            qingchuan = self.result["replay"]["qingchuan"][i-1][1]
            if qingchuan == 1:
                canvas6.create_rectangle(posStart, 61, posEnd, 70, fill="#00ff77", width=0)

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
                if self.config.item["lingsu"]["stack"] != "不堆叠" and i-j >= int(self.config.item["lingsu"]["stack"]):
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
        渲染团队信息(Part 7)，灵素复盘特化.
        '''
        window = self.window
        # Part 7: 输出
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#00ac99")
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
        tb.AppendHeader("DPS", "全程去除配伍、飘黄增益后的DPS，注意包含重伤时间。")
        tb.AppendHeader("配伍比例", "配伍的层数对时间的积分除以总量。极限情况下可以是500%。")
        tb.AppendHeader("飘黄次数", "触发飘黄的次数。")
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.AppendContext(parseCent(record["PeiwuRate"]) + '%')
            tb.AppendContext(record["PiaohuangNum"])
            tb.EndOfLine()

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9)，灵素复盘特化.
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#00ac99")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="灵素PVE群：710451604").place(x=20, y=40)
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
        - result: 灵素复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#00ac99")
        self.title = '灵素复盘'
        self.occ = "lingsu"

class LingSuReplayer(HealerReplay):
    '''
    灵素复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        self.window.setNotice({"t2": "加载灵素复盘...", "c2": "#00ac99"})

        self.initFirstState()

        self.peiwuCounter = {}
        for key in self.bld.info.player:
            self.peiwuCounter[key] = ShieldCounterNew("20877", self.startTime, self.finalTime)

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
                if event.id in ["20877"] and event.caster == self.mykey and event.target in self.bld.info.player:  # buff配伍
                    self.peiwuCounter[event.target].setState(event.time, event.stack)

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
                     [None, "白芷含芳", ["27622"], "15411", True, 24, False, True, 0, 1],
                     [None, "赤芍寒香", ["27633"], "15414", True, 0, False, True, 0, 1],
                     [None, "当归四逆", ["27624"], "15412", True, 8, True, True, 16, 1],
                     [None, "龙葵自苦", ["27630"], "15413", True, 0, False, True, 25, 1],
                     [None, "七情和合", ["28620"], "15416", True, 0, False, True, 22, 1],
                     [None, "青川濯莲", ["27669"], "15420", True, 24, False, True, 40, 1],
                     [None, "枯木苏息", ["27675"], "15422", True, 80, False, True, 240, 1],
                     [None, "千枝绽蕊", ["27650"], "15417", False, 0, False, True, 0, 1],
                     [None, "凌然天风", ["27642"], "15405", False, 0, False, True, 38, 1],
                     [None, "逐云寒蕊", ["27674"], "15421", False, 0, False, True, 74, 1],
                     [None, "青圃着尘", ["28533"], "15768", False, 0, False, True, 40, 1],
                     [None, "银光照雪", ["27531", "28347"], "15400", False, 0, False, True, 10, 1],
                     [None, "百药宣时", ["28756"], "15718", False, 0, False, True, 60, 1],
                     [None, "特效腰坠", ["yaozhui"], "3414", False, 0, False, True, 180, 1]
                     ]

        self.initSecondState()

        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        peiwuRateDict = {}  # 配伍覆盖率
        piaohuangNumDict = {}  # 飘黄触发次数

        # 技能统计
        lszhSkill = SkillHealCounter("28083", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 灵素中和
        qczlSkill = SkillHealCounter("27669", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 青川濯莲
        ygzxSkill = SkillHealCounter("27531", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 银光照雪
        cshxBuff = SkillHealCounter("20070", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 赤芍寒香  (20819素柯)
        qianzhiDict = BuffCounter("20075", self.startTime, self.finalTime)  # 千枝buff
        qingchuanDict = BuffCounter("20800", self.startTime, self.finalTime)  # 青川buff

        for line in self.bld.info.player:
            piaohuangNumDict[line] = 0

        # 杂项
        qianzhiRemain = 0
        qianzhiLast = 0
        zyhrLast = 0
        zyhrCast = 0
        zyhrList = []
        zyhrNum = []
        qqhhMaxNum = 0
        dgsnLast = 0
        zhongheInQianzhi = 0

        # 药性判断
        yaoxingLog = [[0, 0, 0, 0]]  # 药性记录: (时间，中和次数，变化，技能ID)

        # 监控cd用的类
        qczlWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["27669"]], self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)
        dgsnWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["27624"]], self.startTime, self.finalTime,
                                             self.haste, exclude=self.bossBh.badPeriodHealerLog)

        self.unimportantSkill += ["28083", "28602", "28734", "28733", "28082", "28757",  # 灵素中和
                               "27621",  # 白芷本体
                               "27632",  # 赤芍本体
                               "27528", "27529", "28345",  # 银光本体+伤害
                               "27623",  # 当归本体
                               "28679",  # 飘黄判定
                               "27671",  # 青川濯莲目标点判定
                               "29079",  # 当归区域判定
                               "28114",  # 获得药性
                               "28403",  # 获得药性带目标
                               "27673", "27670", "28003",  # 青川治疗
                               "28640",  # 赤芍添加HOT
                               "28638",  # 素柯判定
                               "28699",  # 同梦龙葵
                               "28929",  # 药宗阵回蓝
                               "27672",  # 青川濯莲寻找主人
                               "27649",  # 千枝伏藏
                               "28974",  # 药宗阵
                               "29995", "27700",  # 凌然天风表现
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if qianzhiRemain != 0 and event.time - qianzhiRemain > 300:
                # 补全由千枝技能推测的千枝buff
                qianzhiDict.setState(qianzhiRemain, 1)
                qianzhiDict.setState(qianzhiRemain + 50, 0)
                qianzhiRemain = 0

            self.eventInSecondState(event)

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # 所有治疗技能都不计算化解.
                    continue

                if event.caster == self.mykey and event.scheme == 1:
                    # 根据技能表进行自动处理
                    if event.id in self.gcdSkillIndex:
                        # 特殊处理当归四逆
                        if event.id == "27624":
                            if event.time - dgsnLast > 1000:
                                dgsnWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                            dgsnLast = event.time

                    # 处理特殊技能
                    elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                        desc = ""
                        if event.id in ["27650"]:
                            if event.time - qianzhiLast > 300:
                                qianzhiRemain = event.time
                        elif event.id in ["27642"]:
                            desc = "开启凌然天风"
                        elif event.id in ["27674"]:
                            desc = "逐云寒蕊"
                            zyhrCast = event.time
                        elif event.id in ["28533"]:
                            desc = "青圃着尘结算"
                        elif event.id in ["28756"]:
                            desc = "开启百药宣时"
                        record = True
                        if event.id == "27650":
                            record = False
                        if event.id == "27531" and self.bh.log["special"] != [] and self.bh.log["special"][-1]["skillid"] == "27531" and event.time - self.bh.log["special"][-1]["start"] < 100:
                            record = False
                        if record:
                            index = self.nonGcdSkillIndex[event.id]
                            line = self.skillInfo[index]
                            self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                            index = self.nonGcdSkillIndex[event.id]
                            line = self.skillInfo[index]
                            skillObj = line[0]
                            if skillObj is not None:
                                skillObj.recordSkill(event.time, event.heal, event.healEff, self.ss.timeEnd, delta=-1)

                    # 记录药性相关
                    if event.id in ["27622", "27633", "27624", "27630", "28620"]:
                        if event.time - yaoxingLog[-1][0] > 100:
                            yaoxingLog.append([event.time, 0, 0, 0])
                        yaoxingLog[-1][3] = event.id

                    # 统计不计入时间轴的治疗量
                    if event.id in ["28083", "28734", "28733", "28757"]:  # 灵素中和
                        lszhSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        # print("[Zhonghe]", event.id, event.heal)
                        if event.time - yaoxingLog[-1][0] > 100 or yaoxingLog[-1][2] != 0:
                            yaoxingLog.append([event.time, 0, 0, 0])
                        yaoxingLog[-1][1] += 1
                        state = qianzhiDict.checkState(event.time - 50)
                        if state:
                            zhongheInQianzhi += 1
                    if event.id in ["27673", "28003"]:  # 青川濯莲
                        qczlSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        # print("[qcvlSkill]", event.time, event.id, event.heal, event.healEff)
                    if event.id in ["27531", "28347"]:  # 银光照雪
                        ygzxSkill.recordSkill(event.time, event.heal, event.healEff, event.time)

                if event.caster == self.mykey and event.scheme == 2:
                    if event.id in ["20070"]:  # 赤芍寒香
                        cshxBuff.recordSkill(event.time, event.heal, event.healEff, self.ss.timeEnd)

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.peiwuCounter:
                        if event.caster not in battleStat:
                            battleStat[event.caster] = [0, 0, 0]  # 正常伤害，配伍伤害，飘黄伤害
                        if int(event.id) >= 29532 and int(event.id) <= 29537:  # 逐云寒蕊
                            battleStat[event.caster][2] += event.damageEff
                            piaohuangNumDict[event.caster] += 1
                        else:
                            numStack = self.peiwuCounter[event.caster].checkState(event.time)
                            battleStat[event.caster][0] += event.damageEff / (1 + 0.0025 * numStack)
                            battleStat[event.caster][1] += event.damageEff / (1 + 0.0025 * numStack) * 0.0025 * numStack

                if event.id in ["28114", "28403"] and event.caster == self.mykey:
                    # 药性特征技能
                    # print("[YaoxingTest]", event.time, event.id, event.level, self.bld.info.player[event.caster].name,
                    #       self.bld.info.player[event.target].name, parseTime((event.time - self.startTime) / 1000))
                    if event.time - yaoxingLog[-1][0] > 100 or yaoxingLog[-1][2] != 0:
                        yaoxingLog.append([event.time, 0, 0, 0])
                    if event.level <= 5:
                        yaoxingLog[-1][2] = - event.level
                    else:
                        yaoxingLog[-1][2] = event.level - 5

            elif event.dataType == "Buff":
                if event.id in ["21803"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    self.bh.setSpecialSkill(event.id, "cw特效", "15888",
                                       event.time, 0, "触发cw特效")
                if event.id in ["20075"] and event.caster == self.mykey:  # 千枝
                    hasQianzhi = qianzhiDict.checkState(event.time)
                    if hasQianzhi == 0 and event.stack == 0:
                        # 补全不准确的千枝记录
                        qianzhiDict.setState(event.time - 50, 1)
                    qianzhiDict.setState(event.time, event.stack)
                    qianzhiLast = event.time
                    qianzhiRemain = 0
                if event.id in ["20800"] and event.target == self.mykey:  # 青川濯莲
                    qingchuanDict.setState(event.time, event.stack)
                    if event.stack == 1:
                        qczlWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                if event.id in ["20854"] and event.time - zyhrCast < 20000:  # 逐云寒蕊判定
                    if event.time - zyhrLast > 20000:  # 保证是新的一次
                        zyhrNum.append(len(zyhrList))
                        zyhrList = []
                        zyhrLast = event.time
                    if event.target not in zyhrList:
                        zyhrList.append(event.target)
                if event.id in ["20811"] and event.target == self.mykey:  # 七情debuff判定
                    if event.stack > qqhhMaxNum:
                        qqhhMaxNum = event.stack

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

        self.completeSecondState()

        zyhrNum.append(len(zyhrList))
        zyhrNum = zyhrNum[1:]

        # 药性推测
        for i in range(1, len(yaoxingLog)):
            if yaoxingLog[i][2] == 0 and yaoxingLog[i][3] != 0:
                if yaoxingLog[i][3] in ["27622", "27624"]:
                    yaoxingLog[i][2] = -1  # 温性为负
                if yaoxingLog[i][3] in ["27633", "27630"]:
                    yaoxingLog[i][2] = 2  # 寒性为正
            # print(yaoxingLog[i])
        maxYaoxing = 0
        maxScore = -9999999
        for baseYaoxing in range(-5, 6):
            score = 0
            nowYaoxing = baseYaoxing
            for i in range(1, len(yaoxingLog)):
                line = yaoxingLog[i]
                zhongheTrigger = 0
                if line[1] > 0:
                    zhongheTrigger = 1
                zhongheInfer = 0
                if nowYaoxing * line[2] < 0:
                    zhongheInfer = 1
                if zhongheTrigger != zhongheInfer:
                    score -= 1
                nowYaoxing += line[2]
                if line[3] == '26820' and nowYaoxing != 0:
                    score -= 5
                if nowYaoxing < -5:
                    nowYaoxing = -5
                if nowYaoxing > 5:
                    nowYaoxing = 5
                if line[3] == '28620':
                    break
            # print("[YaoxingScore]", baseYaoxing, score)
            if score > maxScore:
                maxScore = score
                maxYaoxing = baseYaoxing
        yaoxingInfer = [[self.startTime, maxYaoxing]]
        nowYaoxing = maxYaoxing
        yaoxingSum = 0
        yaoxingWaste = 0
        for i in range(1, len(yaoxingLog)):
            prevYaoxing = nowYaoxing
            nowYaoxing += yaoxingLog[i][2]
            yaoxingSum += abs(yaoxingLog[i][2])
            if nowYaoxing < -5:
                yaoxingWaste += (-5 - nowYaoxing)
                nowYaoxing = -5
            if nowYaoxing > 5:
                yaoxingWaste += (nowYaoxing - 5)
                nowYaoxing = 5
            if line[3] == '26820':
                nowYaoxing = 0
            if nowYaoxing != prevYaoxing:
                yaoxingInfer.append([yaoxingLog[i][0], nowYaoxing])
        # print("[YaoxingInfer]", yaoxingInfer)

        # 计算DPS列表(Part 7)

        # 计算等效伤害
        numdam1 = 0
        numdam2 = 0
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0]
            numdam1 += line[1]
            numdam2 += line[2]

        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        overallShieldHeat = {"interval": 500, "timeline": []}
        for key in self.peiwuCounter:
            liveCount = self.battleDict[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)  # 存活时间比例
            if self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog) - liveCount < 8000:  # 脱战缓冲时间
                liveCount = self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)
            self.battleTimeDict[key] = liveCount
            self.sumPlayer += liveCount / self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)
            # # 过滤老板，T奶，自己
            # if key not in damageDict or damageDict[key] / self.result["overall"]["sumTime"] * 1000 < 10000:
            #     continue
            # if getOccType(occDetailList[key]) == "healer":
            #     continue
            # if getOccType(occDetailList[key]) == "tank" and not self.config.xiangzhiCalTank:
            #     continue
            # if key == self.mykey:
            #     continue
            time1 = self.peiwuCounter[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            timeAll = liveCount
            peiwuRateDict[key] = time1 / (timeAll + 1e-10)

        for line in damageList:
            if line[0] not in peiwuRateDict:
                continue
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTimeDpsEff"] * 1000),
                   "PeiwuRate": roundCent(peiwuRateDict[line[0]]),
                   "PiaohuangNum": piaohuangNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        # 计算配伍覆盖率
        numRate = 0
        sumRate = 0
        for key in peiwuRateDict:
            numRate += self.battleTimeDict[key]
            sumRate += peiwuRateDict[key] * self.battleTimeDict[key]
        overallRate = sumRate / (numRate + 1e-10)

        # 计算飘黄次数
        numPiaoHuang = 0
        for key in piaohuangNumDict:
            numPiaoHuang += piaohuangNumDict[key]

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 灵素中和
        self.calculateSkillInfoDirect("lszh", lszhSkill)
        # 白芷含芳
        bzhfSkill = self.calculateSkillInfo("bzhf", "27622")
        # 赤芍寒香
        cshxSkill = self.skillInfo[self.gcdSkillIndex["27633"]][0]
        self.result["skill"]["cshx"] = {}
        self.result["skill"]["cshx"]["num"] = cshxBuff.getNum()
        self.result["skill"]["cshx"]["numPerSec"] = roundCent(
            self.result["skill"]["cshx"]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
        effHeal = cshxBuff.getHealEff()
        self.result["skill"]["cshx"]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["cshx"]["skillNum"] = cshxSkill.getNum()
        self.result["skill"]["cshx"]["delay"] = int(cshxSkill.getAverageDelay())
        effHeal = cshxSkill.getHealEff()
        self.result["skill"]["cshx"]["skillHPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 当归四逆
        dgsnSkill = self.calculateSkillInfo("dgsn", "27624")
        # 银光照雪
        self.calculateSkillInfoDirect("ygzx", ygzxSkill)
        # 青川濯莲
        self.calculateSkillInfoDirect("qczl", qczlSkill)
        # 杂项
        qqhhSkill = self.calculateSkillInfo("qqhh", "28620")
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["PeiwuRate"] = overallRate
        self.result["skill"]["general"]["PiaohuangNum"] = numPiaoHuang
        self.result["skill"]["general"]["PeiwuDPS"] = int(numdam1 / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["general"]["PiaohuangDPS"] = int(numdam2 / self.result["overall"]["sumTimeEff"] * 1000)
        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)
        self.result["replay"]["qianzhi"] = qianzhiDict.log
        self.result["replay"]["qingchuan"] = qingchuanDict.log
        self.result["replay"]["yaoxing"] = yaoxingInfer

        self.specialKey = {"lszh-numPerSec": 20, "general-efficiency": 20, "healer-healEff": 20}
        self.markedSkill = ["28620", "27531", "28756", "28533"]
        self.outstandingSkill = [qczlWatchSkill, dgsnWatchSkill]
        self.calculateSkillOverall()

        # 计算专案组的心法部分.
        # code 301 保证`灵素中和`的触发次数
        numPerSec = self.result["skill"]["lszh"]["numPerSec"]
        rank = self.result["rank"]["lszh"]["numPerSec"]["percent"]
        res = {"code": 301, "numPerSec": numPerSec, "rank": rank, "rate": roundCent(rank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 302 避免药性溢出
        rate = roundCent(1 - yaoxingWaste / (yaoxingSum + 1e-10))
        res = {"code": 302, "numOver": yaoxingWaste, "numAll": yaoxingSum, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 95, 90, 0)
        self.result["review"]["content"].append(res)

        # code 303 提高`飘黄`的覆盖人数
        num = 0
        sum = 0
        for line in zyhrNum:
            num += 1
            sum += line
        zyhrAverage = roundCent(sum / (num + 1e-10))
        rate = roundCent(zyhrAverage / (self.result["overall"]["numPlayer"] + 1e-10))
        res = {"code": 303, "numCover": zyhrAverage, "numAll": self.result["overall"]["numPlayer"], "rate": rate}
        res["status"] = getRateStatus(res["rate"], 90, 50, 10)
        self.result["review"]["content"].append(res)

        # code 304 注意控制`七情`状态
        maxLayer = qqhhMaxNum
        rate = 1 - maxLayer * 0.1
        res = {"code": 304, "maxLayer": maxLayer, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 30, 0)
        self.result["review"]["content"].append(res)

        # code 305 充分使用`千枝绽蕊`
        time = roundCent(qianzhiDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog) / 1000)
        num = roundCent(zhongheInQianzhi / 5)
        efficiency = min(1, roundCent(num / (time + 1e-10) * 1.75))
        rate = min(100, efficiency)
        res = {"code": 305, "time": time, "num": num, "efficiency": efficiency, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 30, 0)
        self.result["review"]["content"].append(res)

        self.calculateSkillFinal()

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
        self.haste = config.item["lingsu"]["speed"]
        self.public = config.item["lingsu"]["public"]
        self.occ = "lingsu"
        self.occCode = "212h"
        self.occPrint = "灵素"

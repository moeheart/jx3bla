# Created by moeheart at 04/19/2022
# 奶秀复盘，用于奶秀复盘的生成，展示

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *
from replayer.occ.Display import HealerDisplayWindow, SingleSkillDisplayer

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

class YunChangXinJingWindow(HealerDisplayWindow):
    '''
    奶秀复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴中从上到下的三个条分别表示：翔舞比例、上元比例、回雪飘摇。
回雪飘摇作为不占gcd的技能，不会在技能轴中显示，而是改为在时间轴内部显示。
战斗效率包含回雪飘摇的读条时间，而gcd效率则不包含。'''
        messagebox.showinfo(title='说明', message=text)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，奶歌复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#ff77ff")
        frame5.place(x=10, y=250)

        hxpyDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        hxpyDisplayer.setImage("894", "回雪飘摇")
        hxpyDisplayer.setDouble("rate", "数量", "hxpy", "num", "numPerSec")
        hxpyDisplayer.setSingle("delay", "延迟", "hxpy", "delay")
        hxpyDisplayer.setSingle("int", "HPS", "hxpy", "HPS")
        hxpyDisplayer.setSingle("percent", "有效比例", "hxpy", "effRate")
        hxpyDisplayer.export_image(frame5, 0)

        # frame5_1 = tk.Frame(frame5, width=180, height=95)
        # frame5_1.place(x=0, y=0)
        # frame5_1.photo = tk.PhotoImage(file="icons/894.png")
        # label = tk.Label(frame5_1, image=frame5_1.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "回雪飘摇")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["hxpy"]["num"], self.result["skill"]["hxpy"]["numPerSec"])
        # text = text + "延迟：%dms\n" % self.result["skill"]["hxpy"]["delay"]
        # text = text + "HPS：%d\n" % self.result["skill"]["hxpy"]["HPS"]
        # text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["hxpy"]["effRate"])
        # label = tk.Label(frame5_1, text=text, justify="left")
        # label.place(x=60, y=15)

        xlwlDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        xlwlDisplayer.setImage("897", "翔鸾舞柳")
        xlwlDisplayer.setDouble("rate", "数量", "xlwl", "num", "numPerSec")
        xlwlDisplayer.setSingle("delay", "延迟", "xlwl", "delay")
        xlwlDisplayer.setSingle("int", "持续HPS", "xlwl", "HPS")
        xlwlDisplayer.setSingle("int", "首跳HPS", "xlwl", "shuangluanHPS")
        xlwlDisplayer.setSingle("percent", "覆盖率", "xlwl", "cover")
        xlwlDisplayer.export_image(frame5, 1)

        # frame5_2 = tk.Frame(frame5, width=180, height=95)
        # frame5_2.place(x=180, y=0)
        # frame5_2.photo = tk.PhotoImage(file="icons/897.png")
        # label = tk.Label(frame5_2, image=frame5_2.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "翔鸾舞柳")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["xlwl"]["num"], self.result["skill"]["xlwl"]["numPerSec"])
        # text = text + "延迟：%dms\n" % self.result["skill"]["xlwl"]["delay"]
        # text = text + "持续HPS：%d\n" % self.result["skill"]["xlwl"]["HPS"]
        # text = text + "首跳HPS：%d\n" % self.result["skill"]["xlwl"]["shuangluanHPS"]
        # text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["xlwl"]["cover"])
        # label = tk.Label(frame5_2, text=text, justify="left")
        # label.place(x=60, y=10)

        sydhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        sydhDisplayer.setImage("913", "上元点鬟")
        sydhDisplayer.setDouble("rate", "数量", "sydh", "num", "numPerSec")
        sydhDisplayer.setSingle("delay", "延迟", "sydh", "delay")
        sydhDisplayer.setSingle("int", "HPS", "sydh", "HPS")
        sydhDisplayer.setSingle("int", "首跳HPS", "sydh", "shuangluanHPS")
        sydhDisplayer.setSingle("percent", "覆盖率", "sydh", "cover")
        sydhDisplayer.export_image(frame5, 2)

        # frame5_3 = tk.Frame(frame5, width=180, height=95)
        # frame5_3.place(x=360, y=0)
        # frame5_3.photo = tk.PhotoImage(file="icons/913.png")
        # label = tk.Label(frame5_3, image=frame5_3.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "上元点鬟")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["sydh"]["num"], self.result["skill"]["sydh"]["numPerSec"])
        # text = text + "延迟：%dms\n" % self.result["skill"]["sydh"]["delay"]
        # text = text + "HPS：%d\n" % self.result["skill"]["sydh"]["HPS"]
        # text = text + "首跳HPS：%d\n" % self.result["skill"]["sydh"]["shuangluanHPS"]
        # text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["sydh"]["cover"])
        # label = tk.Label(frame5_3, text=text, justify="left")
        # label.place(x=60, y=10)

        wmhmDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        wmhmDisplayer.setImage("900", "王母挥袂")
        wmhmDisplayer.setDouble("rate", "数量", "wmhm", "num", "numPerSec")
        wmhmDisplayer.setSingle("int", "HPS", "wmhm", "HPS")
        wmhmDisplayer.setSingle("int", "辞致HPS", "wmhm", "cizhiHPS")
        wmhmDisplayer.setSingle("percent", "有效比例", "wmhm", "effRate")
        wmhmDisplayer.export_image(frame5, 3)

        # frame5_4 = tk.Frame(frame5, width=180, height=95)
        # frame5_4.place(x=540, y=0)
        # frame5_4.photo = tk.PhotoImage(file="icons/900.png")
        # label = tk.Label(frame5_4, image=frame5_4.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "王母挥袂")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["wmhm"]["num"], self.result["skill"]["wmhm"]["numPerSec"])
        # text = text + "HPS：%d\n" % self.result["skill"]["wmhm"]["HPS"]
        # text = text + "辞致HPS：%d\n" % self.result["skill"]["wmhm"]["cizhiHPS"]
        # text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["wmhm"]["effRate"])
        # label = tk.Label(frame5_4, text=text, justify="left")
        # label.place(x=60, y=20)

        fxdaDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        fxdaDisplayer.setImage("1507", "风袖低昂")
        fxdaDisplayer.setDouble("rate", "数量", "fxda", "num", "numPerSec")
        fxdaDisplayer.setSingle("int", "HPS", "fxda", "HPS")
        fxdaDisplayer.setSingle("int", "晚晴HPS", "fxda", "wanqingHPS")
        fxdaDisplayer.setSingle("percent", "有效比例", "fxda", "effRate")
        fxdaDisplayer.export_image(frame5, 4)

        # frame5_5 = tk.Frame(frame5, width=180, height=95)
        # frame5_5.place(x=0, y=100)
        # frame5_5.photo = tk.PhotoImage(file="icons/1507.png")
        # label = tk.Label(frame5_5, image=frame5_5.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "风袖低昂")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["fxda"]["num"], self.result["skill"]["fxda"]["numPerSec"])
        # text = text + "HPS：%d\n" % self.result["skill"]["fxda"]["HPS"]
        # text = text + "晚晴HPS：%d\n" % self.result["skill"]["fxda"]["wanqingHPS"]
        # text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["fxda"]["effRate"])
        # label = tk.Label(frame5_5, text=text, justify="left")
        # label.place(x=60, y=20)

        jwfhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        jwfhDisplayer.setImage("13417", "九微飞花")
        jwfhDisplayer.setDouble("rate", "数量", "jwfh", "num", "numPerSec")
        jwfhDisplayer.setSingle("int", "HPS", "jwfh", "HPS")
        jwfhDisplayer.setSingle("percent", "有效比例", "jwfh", "effRate")
        jwfhDisplayer.export_image(frame5, 5)

        # frame5_6 = tk.Frame(frame5, width=180, height=95)
        # frame5_6.place(x=180, y=100)
        # frame5_6.photo = tk.PhotoImage(file="icons/13417.png")
        # label = tk.Label(frame5_6, image=frame5_6.photo)
        # label.place(x=5, y=25)
        # ToolTip(label, "九微飞花")
        # text = "数量：%d(%.2f)\n" % (self.result["skill"]["jwfh"]["num"], self.result["skill"]["jwfh"]["numPerSec"])
        # text = text + "HPS：%d\n" % self.result["skill"]["jwfh"]["HPS"]
        # text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["jwfh"]["effRate"])
        # label = tk.Label(frame5_6, text=text, justify="left")
        # label.place(x=60, y=20)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "垂眉HPS", "xlwl", "chuimeiHPS")
        info1Displayer.setDouble("rate", "跳珠数量", "tzhy", "num", "numPerSec")
        info1Displayer.setSingle("int", "跳珠HPS", "tzhy", "HPS")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.export_text(frame5, 6)

        # frame5_7 = tk.Frame(frame5, width=180, height=95)
        # frame5_7.place(x=360, y=100)
        # text = "垂眉HPS：%d\n" % self.result["skill"]["xlwl"]["chuimeiHPS"]
        # text = text + "沐风覆盖率：%s%%\n" % parseCent(self.result["skill"]["mufeng"]["cover"])
        # text = text + "跳珠数量：%d(%.2f)\n" % (self.result["skill"]["tzhy"]["num"], self.result["skill"]["tzhy"]["numPerSec"])
        # text = text + "跳珠HPS：%d\n" % self.result["skill"]["tzhy"]["HPS"]
        # label = tk.Label(frame5_7, text=text, justify="left")
        # label.place(x=20, y=15)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("percent", "gcd效率", "general", "efficiency")
        info2Displayer.setSingle("percent", "战斗效率", "general", "efficiencyNonGcd")
        info2Displayer.export_text(frame5, 7)

        # frame5_8 = tk.Frame(frame5, width=180, height=95)
        # frame5_8.place(x=540, y=100)
        # text = "gcd效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiency"])
        # text = text + "战斗效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiencyNonGcd"])
        # label = tk.Label(frame5_8, text=text, justify="left")
        # label.place(x=20, y=30)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

    def renderReplay(self):
        '''
        渲染回放信息(Part 6)，奶歌复盘特化.
        '''
        window = self.window
        # Part 6: 回放
        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#ff77ff")
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
        # 翔舞
        nowTimePixel = 0
        for line in self.result["replay"]["heat"]["timeline"][0]:
            color = getColorHex((int(255 - (255 - 255) * line / 100),
                                 int(255 - (255 - 0) * line / 100),
                                 int(255 - (255 - 128) * line / 100)))
            canvas6.create_rectangle(nowTimePixel, 31, nowTimePixel + 5, 45, fill=color, width=0)
            nowTimePixel += 5

        # 上元
        nowTimePixel = 0
        for line in self.result["replay"]["heat"]["timeline"][1]:
            color = getColorHex((int(255 - (255 - 0) * line / 100),
                                 int(255 - (255 - 255) * line / 100),
                                 int(255 - (255 - 0) * line / 100)))
            canvas6.create_rectangle(nowTimePixel, 46, nowTimePixel + 5, 60, fill=color, width=0)
            nowTimePixel += 5

        # 回雪飘摇
        for i in range(1, len(self.result["replay"]["hxpy"])):
            posStart = int((self.result["replay"]["hxpy"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["hxpy"][i][0] - startTime) / 100)
            zwjt = self.result["replay"]["hxpy"][i-1][1]
            if zwjt == 1:
                canvas6.create_rectangle(posStart, 61, posEnd, 70, fill="#ff77ff", width=0)

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
                if self.config.item["yunchang"]["stack"] != "不堆叠" and i-j >= int(self.config.item["yunchang"]["stack"]):
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
                    text += "*%d" % record["num"]
                canvas6.create_text(posStart+20, 20, text=text, anchor=tk.W)

        tk.Label(frame6sub, text="test").place(x=20, y=20)

    def renderTeam(self):
        '''
        渲染团队信息(Part 7)，奶歌复盘特化.
        '''
        window = self.window
        # Part 7: 输出
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#ff77ff")
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
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.EndOfLine()

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9)，奶歌复盘特化.
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#ff77ff")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="奶秀PVE群：556065010").place(x=20, y=40)
        tk.Label(frame9, text="").place(x=20, y=40)
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
        - result: 奶秀复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#ff77ff")
        self.title = '奶秀复盘'
        self.occ = "yunchangxinjing"

class YunChangXinJingReplayer(ReplayerBase):
    '''
    奶秀复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        self.window.setNotice({"t2": "加载奶秀复盘...", "c2": "#ff77ff"})

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶秀复盘 v%s"%EDITION
        self.result["overall"]["playerID"] = "未知"
        self.result["overall"]["server"] = self.bld.info.server
        self.result["overall"]["battleTime"] = self.bld.info.battleTime
        self.result["overall"]["battleTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        self.result["overall"]["generateTime"] = int(time.time())
        self.result["overall"]["generateTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["generateTime"]))
        self.result["overall"]["map"] = self.bld.info.map
        self.result["overall"]["boss"] = getNickToBoss(self.bld.info.boss)
        self.result["overall"]["sumTime"] = self.bld.info.sumTime
        self.result["overall"]["sumTimePrint"] = parseTime(self.bld.info.sumTime / 1000)
        self.result["overall"]["dataType"] = self.bld.dataType
        self.result["overall"]["mask"] = self.config.item["general"]["mask"]

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"', '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
                self.npcKey = key
                break

        # 记录盾的存在情况与减疗
        jianLiaoLog = {}

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.
        self.interrupt = 0

        # 不知道有什么用
        self.activeBoss = ""

        # 记录战斗开始时间与结束时间
        if self.startTime == 0:
            self.startTime = self.bld.log[0].time
        if self.finalTime == 0:
            self.finalTime = self.bld.log[-1].time

        # 如果时间被大幅度修剪过，则修正战斗时间
        if abs(self.finalTime - self.startTime - self.result["overall"]["sumTime"]) > 6000:
            actualTime = self.finalTime - self.startTime
            self.result["overall"]["sumTime"] = actualTime
            self.result["overall"]["sumTimePrint"] = parseTime(actualTime / 1000)

        # 记录所有治疗的key，首先尝试直接使用心法列表获取.
        self.healerDict = {}
        XiangZhiList = []

        # 记录具体心法的表.
        occDetailList = {}
        for key in self.bld.info.player:
            occDetailList[key] = self.bld.info.player[key].occ

        # 自动推导奶歌角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            raise Exception("角色名暂时不可自动推导，需要通过前序分析来手动指定")
        else:
            for key in self.bld.info.player:
                if self.bld.info.player[key].name == self.myname:
                    self.mykey = key

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if self.interrupt != 0:
                continue

            if event.dataType == "Skill":
                # 记录治疗心法的出现情况.
                if event.caster not in self.healerDict and event.id in ["565", "554", "555", "2232", "6662", "2233", "6675",
                                                                  "2231", "101", "142", "138", "14231", "14140", "14301", "16852", "18864",
                                                                  "27621", "27623", "28083"]:  # 奶妈的特征技能
                    self.healerDict[event.caster] = 0

                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22', '212']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"宓桃"':
                    self.activeBoss = "宓桃"
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif event.dataType == "Buff":
                if event.id in ["15774", "17200"]:  # buff精神匮乏
                    if event.target not in jianLiaoLog:
                        jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                    jianLiaoLog[event.target].setState(event.time, event.stack)
                if event.caster in occDetailList and occDetailList[event.caster] in ['21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                # 为未来需要统计喊话时备用.
                pass

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        # for key in self.bld.info.player:
        #     self.shieldCountersNew[key].inferFirst()

        self.result["overall"]["playerID"] = self.myname

        self.occDetailList = occDetailList

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        self.result["equip"] = {"available": 0}
        if self.bld.info.player[self.mykey].equip != {} and "beta" not in EDITION:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, "6h")
            self.result["equip"]["score"] = int(self.bld.info.player[self.mykey].equipScore)
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res["根骨"]
            self.result["equip"]["heal"] = res["治疗"]
            self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["critPercent"] = res["会心"]
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = res["会效"]
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["hastePercent"] = res["加速"]
            self.result["equip"]["haste"] = res["加速等级"]
            if not self.config.item["yunchang"]["speedforce"]:
                self.haste = self.result["equip"]["haste"]
            self.result["equip"]["raw"] = strEquip

        self.result["qixue"] = {"available": 0}
        if self.bld.info.player[self.mykey].qx != {}:
            self.result["qixue"]["available"] = 1
            for key in self.bld.info.player[self.mykey].qx:
                qxKey = "1,%s,1" % self.bld.info.player[self.mykey].qx[key]["2"]
                qxKey0 = "1,%s,0" % self.bld.info.player[self.mykey].qx[key]["2"]
                if qxKey in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey]
                elif qxKey0 in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey0]
                elif self.bld.info.player[self.mykey].qx[key]["2"] == "0":
                    self.result["qixue"]["available"] = 0
                    break
                else:
                    self.result["qixue"][key] = self.bld.info.player[self.mykey].qx[key]["2"]

        # print(self.result["overall"])
        # print(self.result["equip"])
        # print(self.result["qixue"])

        # res = {}
        # for line in self.result["qixue"]:
        #     if line != "available":
        #         key = self.result["qixue"][line]
        #         value = SKILL_NAME["1,%s,1"%key]
        #         res[key] = value
        # print(res)

        self.result["overall"]["hasteReal"] = self.haste

        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        occDetailList = self.occDetailList

        num = 0

        # 以承疗者记录的关键治疗
        self.criticalHealCounter = {}
        hpsActive = 0

        # 以治疗者记录的关键治疗
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            numSmall = 0

        npcHealStat = {}
        numPurge = 0  # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        battleTimeDict = {}  # 进战时间
        sumPlayer = 0  # 玩家数量

        xwgdNumDict = {}  # 仙王蛊鼎触发次数

        # 技能统计

        xlwlSkill = SkillHealCounter("554", self.startTime, self.finalTime, self.haste)  # 翔鸾舞柳
        sydhSkill = SkillHealCounter("556", self.startTime, self.finalTime, self.haste)  # 上元点鬟
        tzhySkill = SkillHealCounter("566", self.startTime, self.finalTime, self.haste)  # 跳珠憾玉
        wmhmSkill = SkillHealCounter("2976", self.startTime, self.finalTime, self.haste)  # 王母挥袂
        fxdaSkill = SkillHealCounter("555", self.startTime, self.finalTime, self.haste)  # 王母挥袂
        hxpySkill = SkillHealCounter("6250", self.startTime, self.finalTime, self.haste)  # 回雪飘摇
        jwfhSkill = SkillHealCounter("24990", self.startTime, self.finalTime, self.haste)  # 九微飞花
        xiangwuBuff = SkillHealCounter("680", self.startTime, self.finalTime, self.haste)  # 翔舞
        shangyuanBuff = SkillHealCounter("681", self.startTime, self.finalTime, self.haste)  # 上元

        hxpyDict = BuffCounter("?", self.startTime, self.finalTime)  # 用buff类型来记录回雪飘摇的具体时间

        cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风
        battleDict = self.battleDict

        xiangwuDict = {}  # 翔舞
        shangyuanDict = {}  # 上元

        for line in self.bld.info.player:
            xiangwuDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 翔舞
            shangyuanDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 上元
            battleStat[line] = [0]
            xwgdNumDict[line] = 0

        lastSkillTime = self.startTime

        # 杂项
        cizhiHeal = 0  # 辞致
        chuimeiHeal = 0  # 垂眉
        shuangluanHeal1 = 0  # 双鸾翔舞
        shuangluanHeal3 = 0  # 双鸾上元
        wanqingHeal = 0  # 晚晴
        jwfhLast = 0  # 九微飞花统计cd
        sydhNum = 0  # 上元施放
        sydhWrong = 0  # 上元错误施放

        # 回雪的特殊统计
        hxpyLastSkill = 0
        hxpyCastNum = 0
        hxpyCompleteNum = 0
        hxpyLocalNum = 0
        hxpyCastList = []
        hxpySingleNum = 0
        hxpySingleList = []

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],

                     [xlwlSkill, "翔鸾舞柳", ["554"], "897", True, 0, False, True, 0, 1],
                     [sydhSkill, "上元点鬟", ["556"], "913", True, 0, False, True, 0, 1],
                     [wmhmSkill, "王母挥袂", ["2976", "28771"], "900", True, 0, False, True, 12, 1],
                     [None, "风袖低昂", ["555"], "1507", True, 0, False, True, 33, 1],
                     [None, "九微飞花", ["24990"], "13417", True, 0, False, True, 60, 1],
                     [tzhySkill, "跳珠憾玉", ["566"], "1505", True, 0, False, True, 3, 1],
                     [None, "心鼓弦", ["551"], "898", True, 48, False, True, 660, 1],
                     [None, "天地低昂", ["557"], "1498", True, 0, False, True, 35, 1],

                     # [None, "回雪飘摇", ["6250"], "894", False, 16, True, True],
                     [None, "蝶弄足", ["574"], "915", False, 0, False, True, 75, 2],
                     [None, "鹊踏枝", ["550"], "912", False, 0, False, True, 60, 2],
                     [None, "繁音急节", ["568"], "1502", False, 0, False, True, 54, 1],
                     [None, "余寒映日", ["18221"], "7497", False, 0, False, True, 35, 1],
                    ]

        hxpyTime = getLength(13, self.haste)  # TODO 判断瑰姿

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            if line[0] is None:
                skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste)
            if line[1] == "风袖低昂":
                fxdaSkill = skillInfo[i][0]
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i
        yzInfo = [None, "特效腰坠", ["0"], "3414", False, 0, False, True, 180, 1]
        yzSkill = SkillCounterAdvance(yzInfo, self.startTime, self.finalTime, self.haste)
        yzInfo[0] = yzSkill

        jwfhWatchSkill = SkillCounterAdvance(skillInfo[gcdSkillIndex["24990"]], self.startTime, self.finalTime,
                                             self.haste)

        xiangZhiUnimportant = ["4877",  # 水特效作用
                               "25682", "25683", "25684", "25685", "25686", "24787", "24788", "24789", "24790",  # 破招
                               "22155", "22207", "22211", "22201", "22208",  # 大附魔
                               "3071", "18274", "14646", "604",  # 治疗套装，寒清，书离，春泥
                               "23951",  # 贯体通用
                               "14536", "14537",  # 盾填充, 盾移除
                               "3584", "2448",  # 蛊惑
                               "6800",  # 风特效
                               "25231",  # 桑柔判定
                               "21832",  # 绝唱触发
                               "9007", "9004", "9005", "9006",  # 后跳，小轻功
                               "29532", "29541",  # 飘黄
                               "4697", "13237",  # 明教阵眼
                               "13332",  # 锋凌横绝阵
                               "14427", "14426",  # 浮生清脉阵
                               "26128", "26116", "26129", "26087",  # 龙门飞剑
                               "28982",  # 药宗阵
                               "742",  # T阵
                               "14358",  # 删除羽减伤
                               "30399", "30273",  # 点燃传染
                               ## 奶秀分割线
                               "6633", "6634", "6635",  # 翔舞判定
                               "24987", "3776",  # 上元判定
                               "6651",  # 加疗伤
                               "2341", "3001", "537",  # 添加剑舞
                               "565",  # 回雪飘摇壳
                               "569",  # 王母壳
                               "6250",  # 回雪飘摇实际效果
                               "6209",  # 辞致
                               "21270", "21274", "21275", "21276",  # 垂眉
                               "24991", "24992", "24993",  # 九微飞花
                               "6249",  # 双鸾
                               "3415",  # 丰年
                               "807",  # 重伤保护驱散？？
                               "901",  # 战复实际效果
                               "6210",  # 风袖判定
                               "6211",  # 晚晴治疗
                               "1662",  # 添加风袖debuff
                               "18977",  # cw风袖
                               "505",  # 风袖判定
                               "15207", "15756",  # 繁音判断
                               "25789",  # cw小特效 TODO 统计这个，但是鸽了算了
                               "1556",  # 婆罗门
                               "545",  # 婆罗门
                               "30729",  # 闪避减cd
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # numAbsorb1 += event.healEff
                    pass
                else:
                    # 所有治疗技能都不计算化解.

                    # 统计自身技能使用情况.
                    # if event.caster == self.mykey and event.scheme == 1 and event.id in xiangZhiUnimportant and event.heal != 0:
                    #     print(event.id, event.time)

                    if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey and event.id not in gcdSkillIndex and event.id not in xiangZhiUnimportant:
                        # 打印所有有治疗量的技能，以进行整理
                        # print("[Heal]", event.id, event.heal)
                        pass

                    if event.caster == self.mykey and event.scheme == 1:
                        # 根据技能表进行自动处理
                        if event.id in gcdSkillIndex:
                            ss.initSkill(event)
                            index = gcdSkillIndex[event.id]
                            line = skillInfo[index]
                            castTime = line[5]
                            ss.analyseSkill(event, castTime, line[0], tunnel=line[6], hasteAffected=line[7])
                            targetName = "Unknown"
                            if event.target in self.bld.info.player:
                                targetName = self.bld.info.player[event.target].name
                            elif event.target in self.bld.info.npc:
                                targetName = self.bld.info.npc[event.target].name
                            lastSkillID, lastTime = bh.getLastNormalSkill()
                            if gcdSkillIndex[lastSkillID] == gcdSkillIndex[ss.skill] and ss.timeStart - lastTime < 100:
                                # 相同技能，原地更新
                                bh.updateNormalSkill(ss.skill, line[1], line[3],
                                                     ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                                     ss.healEff, 0, ss.busy, "", "", targetName)
                            else:
                                # 不同技能，新建条目
                                bh.setNormalSkill(ss.skill, line[1], line[3],
                                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                                  ss.healEff, 0, ss.busy, "", "", targetName)
                            ss.reset()
                            # 在gcd技能生效时重置回雪
                            if hxpyLocalNum > 0:
                                hxpyCastNum += 1
                                hxpyCastList.append(hxpyLocalNum)
                            hxpyLocalNum = 0
                            if hxpySingleNum > 0:
                                hxpySingleList.append(hxpySingleNum)
                            hxpySingleNum = 0
                        elif event.id in nonGcdSkillIndex:  # 特殊技能
                            desc = ""
                            index = nonGcdSkillIndex[event.id]
                            line = skillInfo[index]
                            bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                            skillObj = line[0]
                            if skillObj is not None:
                                skillObj.recordSkill(event.time, event.heal, event.healEff, ss.timeEnd, delta=-1)
                        # 无法分析的技能
                        elif event.id not in xiangZhiUnimportant:
                            pass
                            # print("[YunChangNonRec]", event.time, event.id, event.heal, event.healEff)

                        # 统计不计入时间轴的治疗量
                        if event.id in ["6209"]:  # 辞致
                            cizhiHeal += event.healEff
                        if event.id in ["21270", "21274", "21275", "21276"]:  # 垂眉
                            chuimeiHeal += event.healEff
                        if event.id in ["24992", "24993"]:  # 九微飞花
                            jwfhSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                            if event.time - jwfhLast > 5000:
                                # 记录九微飞花
                                jwfhWatchSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                                # bh.setNormalSkill(ss.skill, line[1], line[3],
                                #                   ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                #                   ss.healEff, 0, ss.busy, "", "", targetName)
                            jwfhLast = event.time
                        if event.id in ["6250"]:  # 回雪飘摇
                            hxpySkill.recordSkill(event.time, event.heal, event.healEff, 0)
                            # 回雪也计入战斗效率中
                            if event.time - hxpyDict.log[-1][0] > 200:
                                hxpyDict.setState(event.time - hxpyTime, 1)
                                hxpyDict.setState(event.time, 0)
                        if event.id in ["6249"]:  # 双鸾
                            if event.level == 1:
                                shuangluanHeal1 += event.healEff
                            elif event.level == 3:
                                shuangluanHeal3 += event.healEff
                        if event.id in ["6211"]:  # 晚晴
                            wanqingHeal += event.healEff
                        if event.id in ["556"]:  # 上元主动施放
                            if event.target in self.bld.info.player:
                                status = shangyuanDict[event.target].checkState(event.time - 50)
                                if status:
                                    sydhWrong += 1

                        if event.id in ["6250"]:
                            # 回雪的运算。此处是推测逻辑，较为复杂，有心重构可以大胆尝试。
                            timeDiff = event.time - hxpyLastSkill
                            reset = 0
                            flag = 1
                            if hxpyLocalNum == 3:
                                reset = 1
                            elif timeDiff > 100:
                                hxpyLocalNum += 1
                            else:
                                flag = 0
                            if flag:
                                if hxpySingleNum > 0:
                                    hxpySingleList.append(hxpySingleNum)
                                hxpySingleNum = 0
                            hxpySingleNum += 1
                            if reset:
                                if hxpyLocalNum >= 1:
                                    hxpyCastNum += 1
                                    hxpyCastList.append(hxpyLocalNum)
                                hxpyLocalNum = 0
                            if hxpyLocalNum == 3:
                                hxpyCompleteNum += 1
                            hxpyLastSkill = event.time
                            # print("[HxpySkill]", event.time, event.id, event.heal, event.healEff)

                    if event.caster == self.mykey and event.scheme == 2:
                        # 统计HOT
                        if event.id in ["680"]:  # 翔舞
                            xiangwuBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        if event.id in ["681"]:  # 上元
                            shangyuanBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

                    # 统计对NPC的治疗情况.
                    if event.healEff > 0 and event.target == self.npcKey:
                        if event.caster not in npcHealStat:
                            npcHealStat[event.caster] = 0
                        npcHealStat[event.caster] += event.healEff

                    # 统计以承疗者计算的关键治疗
                    if event.healEff > 0 and self.npcKey != 0:
                        if event.target in self.criticalHealCounter and self.criticalHealCounter[event.target].checkState(event.time):
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = event.healEff
                            else:
                                npcHealStat[event.caster] += event.healEff

                    # 统计以治疗者计算的关键治疗
                    if self.activeBoss in ["宓桃", "哑头陀"]:
                        if event.healEff > 0 and self.npcKey != 0 and hpsActive:
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = 0
                            npcHealStat[event.caster] += event.healEff

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.bld.info.player:
                        battleStat[event.caster][0] += event.damageEff

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                    yzSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                if event.id in ["12768"] and event.stack == 1 and event.target == self.mykey:  # cw特效
                    bh.setSpecialSkill(event.id, "cw特效", "14402",
                                       event.time, 0, "触发cw特效")
                    cwDict.setState(event.time, event.stack)
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)
                if event.id in ["680"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 翔舞
                    xiangwuDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                if event.id in ["681"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 上元
                    shangyuanDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

            elif event.dataType == "Cast":
                if event.caster == self.mykey and event.id == "565":
                    # 回雪飘摇
                    hxpyCastNum += 1
                    if hxpyLocalNum > 0:
                        hxpyCastList.append(hxpyLocalNum)
                    hxpyLocalNum = 0
                    if hxpySingleNum > 0:
                        hxpySingleList.append(hxpySingleNum)
                    hxpySingleNum = 0
                    # print("[HxpyCast]", event.time, event.id)

            num += 1

        # 记录最后一个技能
        if ss.skill != "0":
            index = gcdSkillIndex[ss.skill]
            line = skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")
        hxpyCastList.append(hxpyLocalNum)
        hxpySingleList.append(hxpySingleNum)

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

        # 计算伤害
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0]

        # 关键治疗量统计
        if self.activeBoss in ["宓桃", "哑头陀"]:
            for line in npcHealStat:
                npcHealStat[line] /= (hpsSumTime + 1e-10)

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0}

        myHealStat = {}
        for player in self.act.rhps["player"]:
            if player in self.healerDict:
                self.result["healer"]["numHealer"] += 1
                res = {"rhps": int(self.act.rhps["player"][player]["hps"]),
                       "name": self.act.rhps["player"][player]["name"],
                       "occ": self.bld.info.player[player].occ}
                if player in self.act.hps["player"]:
                    res["hps"] = int(self.act.hps["player"][player]["hps"])
                if player in self.act.ahps["player"]:
                    res["ahps"] = int(self.act.ahps["player"][player]["hps"])
                if player in self.act.ohps["player"]:
                    res["ohps"] = int(self.act.ohps["player"][player]["hps"])
                res["heal"] = res.get("ohps", 0)
                res["healEff"] = res.get("hps", 0)
                if player == self.mykey:
                    myHealStat = res
                self.result["healer"]["table"].append(res)
        self.result["healer"]["table"].sort(key=lambda x: -x["rhps"])
        # print(myHealStat)

        # 计算DPS列表(Part 7)
        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        for key in self.bld.info.player:
            liveCount = battleDict[key].buffTimeIntegral()  # 存活时间比例
            if battleDict[key].sumTime() - liveCount < 8000:  # 脱战缓冲时间
                liveCount = battleDict[key].sumTime()
            battleTimeDict[key] = liveCount
            sumPlayer += liveCount / battleDict[key].sumTime()

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   "xwgdNum": xwgdNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        hxpyDict.shrink(100)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}

        # 回雪飘摇
        self.result["skill"]["hxpy"] = {}
        self.result["skill"]["hxpy"]["num"] = hxpySkill.getNum()
        self.result["skill"]["hxpy"]["numPerSec"] = roundCent(
            self.result["skill"]["hxpy"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["hxpy"]["delay"] = int(hxpySkill.getAverageDelay())
        effHeal = hxpySkill.getHealEff()
        self.result["skill"]["hxpy"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["hxpy"]["effRate"] = effHeal / (hxpySkill.getHeal() + 1e-10)

        # 翔鸾舞柳
        self.result["skill"]["xlwl"] = {}
        self.result["skill"]["xlwl"]["num"] = xiangwuBuff.getNum()
        self.result["skill"]["xlwl"]["numPerSec"] = roundCent(
            self.result["skill"]["xlwl"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = xiangwuBuff.getHealEff()
        self.result["skill"]["xlwl"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xlwl"]["shuangluanHPS"] = int(shuangluanHeal1 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xlwl"]["delay"] = int(xlwlSkill.getAverageDelay())
        num = 0
        sum = 0
        xiangwuHeat = []
        for key in xiangwuDict:
            singleDict = xiangwuDict[key]
            num += battleTimeDict[key]
            sum += singleDict.buffTimeIntegral()
            singleHeat = singleDict.getHeatTable(decay=0)
            if xiangwuHeat == []:
                for line in singleHeat["timeline"]:
                    xiangwuHeat.append(line)
            else:
                for i in range(len(singleHeat["timeline"])):
                    xiangwuHeat[i] += singleHeat["timeline"][i]

        self.result["skill"]["xlwl"]["cover"] = roundCent(sum / (num + 1e-10))
        # 计算HOT统计
        for i in range(len(xiangwuHeat)):
            xiangwuHeat[i] = int(xiangwuHeat[i] * 4)

        # 上元点鬟
        self.result["skill"]["sydh"] = {}
        self.result["skill"]["sydh"]["num"] = shangyuanBuff.getNum()
        self.result["skill"]["sydh"]["numPerSec"] = roundCent(
            self.result["skill"]["sydh"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = shangyuanBuff.getHealEff()
        self.result["skill"]["sydh"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["sydh"]["shuangluanHPS"] = int(shuangluanHeal3 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["sydh"]["delay"] = int(sydhSkill.getAverageDelay())
        num = 0
        sum = 0
        shangyuanHeat = []
        for key in shangyuanDict:
            singleDict = shangyuanDict[key]
            num += battleTimeDict[key]
            sum += singleDict.buffTimeIntegral()
            singleHeat = singleDict.getHeatTable(decay=0)
            if shangyuanHeat == []:
                for line in singleHeat["timeline"]:
                    shangyuanHeat.append(line)
            else:
                for i in range(len(singleHeat["timeline"])):
                    shangyuanHeat[i] += singleHeat["timeline"][i]

        self.result["skill"]["sydh"]["cover"] = roundCent(sum / (num + 1e-10))
        # 计算HOT统计
        for i in range(len(shangyuanHeat)):
            shangyuanHeat[i] = int(shangyuanHeat[i] * 4)

        # 王母
        self.result["skill"]["wmhm"] = {}
        self.result["skill"]["wmhm"]["num"] = wmhmSkill.getNum()
        self.result["skill"]["wmhm"]["numPerSec"] = roundCent(
            self.result["skill"]["wmhm"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["wmhm"]["delay"] = int(wmhmSkill.getAverageDelay())
        effHeal = wmhmSkill.getHealEff()
        self.result["skill"]["wmhm"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["wmhm"]["cizhiHPS"] = int(cizhiHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["wmhm"]["effRate"] = effHeal / (wmhmSkill.getHeal() + 1e-10)

        # 风袖
        self.result["skill"]["fxda"] = {}
        self.result["skill"]["fxda"]["num"] = fxdaSkill.getNum()
        self.result["skill"]["fxda"]["numPerSec"] = roundCent(
            self.result["skill"]["fxda"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["fxda"]["delay"] = int(fxdaSkill.getAverageDelay())
        effHeal = fxdaSkill.getHealEff()
        self.result["skill"]["fxda"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["fxda"]["wanqingHPS"] = int(wanqingHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["fxda"]["effRate"] = effHeal / (fxdaSkill.getHeal() + 1e-10)

        # 九微飞花
        self.result["skill"]["jwfh"] = {}
        self.result["skill"]["jwfh"]["num"] = jwfhSkill.getNum()
        self.result["skill"]["jwfh"]["numPerSec"] = roundCent(
            self.result["skill"]["jwfh"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = jwfhSkill.getHealEff()
        self.result["skill"]["jwfh"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["jwfh"]["effRate"] = effHeal / (jwfhSkill.getHeal() + 1e-10)

        # 杂项
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["xlwl"]["chuimeiHPS"] = int(chuimeiHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["tzhy"] = {}
        self.result["skill"]["tzhy"]["num"] = tzhySkill.getNum()
        self.result["skill"]["tzhy"]["numPerSec"] = roundCent(
            self.result["skill"]["tzhy"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = tzhySkill.getHealEff()
        self.result["skill"]["tzhy"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)

        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        self.result["skill"]["general"]["efficiencyNonGcd"] = bh.getNonGcdEfficiency(hxpyDict.log)
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        self.result["replay"]["hxpy"] = hxpyDict.log
        self.result["replay"]["heat"] = {"interval": 500, "timeline": [xiangwuHeat, shangyuanHeat]}
        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = myHealStat["ohps"]
        self.result["skill"]["healer"]["healEff"] = myHealStat["hps"]
        self.result["skill"]["healer"]["ohps"] = myHealStat["ohps"]
        self.result["skill"]["healer"]["hps"] = myHealStat["hps"]
        self.result["skill"]["healer"]["rhps"] = myHealStat["rhps"]
        self.result["skill"]["healer"]["ahps"] = myHealStat["ahps"]


        self.getRankFromStat("yunchangxinjing")
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        specialKey = {"hxpy-numPerSec": 20, "general-efficiency": 20, "healer-healEff": 20, "xlwl-cover": 10, "sydh-cover": 10}
        for key1 in self.result["rank"]:
            for key2 in self.result["rank"][key1]:
                key = "%s-%s" % (key1, key2)
                weight = 1
                if key in specialKey:
                    weight = specialKey[key]
                    # print(key)
                sumScore += self.result["rank"][key1][key2]["percent"] * weight
                sumWeight += weight
        reviewScore = roundCent((sumScore / sumWeight) ** 0.5 * 10, 2)

        # print(self.result["healer"])
        # print(self.result["dps"])
        # for line in self.result["skill"]:
        #     print(line, self.result["skill"][line])

        # print(xiangwuHeat)
        # print(shangyuanHeat)
        #
        # for line in self.result["replay"]["normal"]:
        #     print(line)
        # print("===")
        # for line in self.result["replay"]["special"]:
        #     print(line)

        # 计算专案组
        self.result["review"] = {"available": 1, "content": []}

        # code 1 不要死
        num = self.deathDict[self.mykey]["num"]
        if num > 0:
            time = roundCent(((self.finalTime - self.startTime) - self.battleDict[self.mykey].buffTimeIntegral()) / 1000, 2)
            self.result["review"]["content"].append({"code": 1, "num": num, "duration": time, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 1, "num": num, "duration": 0, "rate": 1, "status": 0})

        # code 10 不要放生队友
        num = 0
        log = []
        time = []
        id = []
        damage = []
        for key in self.unusualDeathDict:
            if self.unusualDeathDict[key]["num"] > 0:
                for line in self.unusualDeathDict[key]["log"]:
                    num += 1
                    log.append([(int(line[0]) - self.startTime) / 1000, self.bld.info.player[key].name, "%s:%d/%d" % (line[1], line[2], line[6])])
        log.sort(key=lambda x: x[0])
        for line in log:
            time.append(parseTime(line[0]))
            id.append(line[1])
            damage.append(line[2])
        if num > 0:
            self.result["review"]["content"].append({"code": 10, "num": num, "time": time, "id": id, "damage": damage, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 10, "num": num, "time": time, "id": id, "damage": damage, "rate": 1, "status": 0})

        # code 11 保持gcd不要空转
        gcd = self.result["skill"]["general"]["efficiencyNonGcd"]
        gcdRank = self.result["rank"]["general"]["efficiencyNonGcd"]["percent"]
        res = {"code": 11, "cover": gcd, "rank": gcdRank, "rate": roundCent(gcdRank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 12 提高HPS或者虚条HPS
        hps = 0
        ohps = 0
        for record in self.result["healer"]["table"]:
            if record["name"] == self.result["overall"]["playerID"]:
                # 当前玩家
                hps = record["healEff"]
                ohps = record["heal"]
        hpsRank = self.result["rank"]["healer"]["healEff"]["percent"]
        ohpsRank = self.result["rank"]["healer"]["heal"]["percent"]
        rate = max(hpsRank, ohpsRank)
        res = {"code": 12, "hps": hps, "ohps": ohps, "hpsRank": hpsRank, "ohpsRank": ohpsRank, "rate": roundCent(rate / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 13 使用有cd的技能

        scCandidate = []
        for id in ["555", "568", "18221"]:
            if id in nonGcdSkillIndex:
                scCandidate.append(skillInfo[nonGcdSkillIndex[id]][0])
            else:
                scCandidate.append(skillInfo[gcdSkillIndex[id]][0])
        scCandidate.append(yzSkill)
        scCandidate.append(jwfhWatchSkill)

        rateSum = 0
        rateNum = 0
        numAll = []
        sumAll = []
        skillAll = []
        for skillObj in scCandidate:
            num = skillObj.getNum()
            sum = skillObj.getMaxPossible()
            skill = skillObj.name
            if skill in ["余寒映日", "九微飞花", "特效腰坠"] and num == 0:
                continue
            rateNum += 1
            rateSum += min(num / (sum + 1e-10), 1)
            numAll.append(num)
            sumAll.append(sum)
            skillAll.append(skill)
        rate = roundCent(rateSum / (rateNum + 1e-10), 4)
        res = {"code": 13, "skill": skillAll, "num": numAll, "sum": sumAll, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 25, 0)
        self.result["review"]["content"].append(res)

        # code 501 保证`回雪飘摇`的触发次数
        numPerSec = self.result["skill"]["hxpy"]["numPerSec"]
        rank = self.result["rank"]["hxpy"]["numPerSec"]["percent"]
        rate = roundCent(rank / 100)
        res = {"code": 501, "numPerSec": numPerSec, "rank": rank, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 502 保证`上元点鬟`的覆盖率
        cover = self.result["skill"]["sydh"]["cover"]
        rank = self.result["rank"]["sydh"]["cover"]["percent"]
        rate = roundCent(rank / 100)
        res = {"code": 502, "cover": cover, "rank": rank, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 25, 0)
        self.result["review"]["content"].append(res)

        # code 503 中断`回雪飘摇`的倒读条
        num = [0] * 4
        sum = hxpyCastNum
        # print("[hxpyList]", hxpyCastList)
        for i in hxpyCastList:
            num[min(i, 3)] += 1
        perfectTime = num[2]
        earlyTime = num[1]
        perfectRate = roundCent(perfectTime / (sum + 1e-10), 4)
        res = {"code": 503, "time": sum, "perfectTime": perfectTime, "earlyTime": earlyTime, "rate": perfectRate}
        res["status"] = getRateStatus(res["rate"], 85, 50, 0)
        self.result["review"]["content"].append(res)

        # code 504 保证`上元点鬟`的覆盖率
        sum = sydhSkill.getNum()
        wrongTime = sydhWrong
        perfectTime = sum - sydhWrong
        rate = roundCent(perfectTime / (sum + 1e-10))
        res = {"code": 504, "time": time, "wrongTime": wrongTime, "perfectTime": perfectTime, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 95, 90, 0)
        self.result["review"]["content"].append(res)

        # 排序
        self.result["review"]["content"].sort(key=lambda x:-x["status"] * 1000 + x["rate"])
        num = 0
        for line in self.result["review"]["content"]:
            if line["status"] > 0:
                num += 1
                reviewScore -= [0, 1, 3, 10][line["status"]]
        self.result["review"]["num"] = num
        if reviewScore < 0:
            reviewScore = 0
        self.result["review"]["score"] = reviewScore
        self.result["skill"]["general"]["score"] = reviewScore

        # # 测试效果，在UI写好之后注释掉
        # for line in self.result["review"]["content"]:
        #     print(line)

    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        self.result["score"] = {"available": 10, "sum": 0}

    def replay(self):
        '''
        开始奶秀复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()
        self.prepareUpload()

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
        super().__init__(config, fileNameInfo, path, bldDict, window, actorData)

        self.myname = myname
        self.failThreshold = config.item["actor"]["failthreshold"]
        self.mask = config.item["general"]["mask"]
        self.public = config.item["yunchang"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}
        self.haste = config.item["yunchang"]["speed"]
        self.occ = "yunchangxinjing"


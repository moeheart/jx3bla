# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *

import os
import time
import json
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import urllib.request
import hashlib
import webbrowser
import pyperclip

class XiangZhiProWindow():
    '''
    奶歌复盘pro界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def getLvl(self, score):
        '''
        根据清华绩点算法获取等级.
        params:
        - score: 分数
        returns:
        - rate: 等级
        - color: 对应的颜色
        - describe: 对应的评语
        '''
        self.rateScale = [[100, "#ffff00", "A+", "不畏浮云遮望眼，只缘身在最高层。"],
                          [95, "#ff7777", "A", "独有凤凰池上客，阳春一曲和皆难。"],
                          [90, "#ff7777", "A-", "欲把一麾江海去，乐游原上望昭陵。"],
                          [85, "#ff7700", "B+", "敢将十指夸针巧，不把双眉斗画长。"],
                          [80, "#ff7700", "B", "云想衣裳花想容，春风拂槛露华浓。"],
                          [77, "#ff7700", "B-", "疏影横斜水清浅，暗香浮动月黄昏。"],
                          [73, "#0077ff", "C+", "青山隐隐水迢迢，秋尽江南草未凋。"],
                          [70, "#0077ff", "C", "花径不曾缘客扫，蓬门今始为君开。"],
                          [67, "#0077ff", "C-", "上穷碧落下黄泉，两处茫茫皆不见。"],
                          [63, "#77ff00", "D+", "人世几回伤往事，山形依旧枕寒流。"],
                          [60, "#77ff00", "D", "总为浮云能蔽日，长安不见使人愁。"],
                          [0, "#ff0000", "F", "仰天大笑出门去，我辈岂是蓬蒿人。"]]

        for line in self.rateScale:
            if score >= line[0]:
                return line[2], line[1], line[3]

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

    def final(self):
        '''
        关闭窗口。
        '''
        self.windowAlive = False
        self.window.destroy()

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
        url = "http://139.199.102.41:8009/showReplayPro.html?id=%d"%self.result["overall"]["shortID"]
        webbrowser.open(url)

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''如果是盾歌，时间轴中表示梅花三弄的实时全团覆盖率。
如果是血歌，时间轴中表示每个小队的双HOT剩余时间。注意，1-5队可能并不按顺序对应团队面板的1-5队。'''
        messagebox.showinfo(title='说明', message=text)

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        # window = tk.Tk()
        window.title('奶歌复盘pro')
        window.geometry('750x900')

        if "mask" in self.result["overall"]:
            self.mask = self.result["overall"]["mask"]  # 使用数据中的mask选项顶掉框架中现场读取的判定

        # Part 1: 全局
        frame1 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground="#64fab4")
        frame1.place(x=10, y=10)
        frame1sub = tk.Frame(frame1)
        frame1sub.place(x=0, y=0)
        tb = TableConstructor(self.config, frame1sub)
        tb.AppendContext("复盘版本：", justify="right")
        tb.AppendContext(self.result["overall"]["edition"])
        tb.EndOfLine()
        tb.AppendContext("玩家ID：", justify="right")
        tb.AppendContext(self.result["overall"]["playerID"], color="#64fab4")
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
        #tk.Label(frame1, text=text, justify="left").place(x=0, y=0)

        # Part 2: 装备
        frame2 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground="#64fab4")
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
            tb.AppendContext("%d"%self.result["equip"]["score"], color=color4)
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
            tb.AppendContext("治疗量：", justify="right")
            tb.AppendContext("%d(%d)"%(self.result["equip"]["heal"], self.result["equip"]["healBase"]))
            tb.EndOfLine()
            tb.AppendContext("会心：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critPercent"], self.result["equip"]["crit"]))
            tb.EndOfLine()
            tb.AppendContext("会心效果：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critpowPercent"], self.result["equip"]["critpow"]))
            tb.EndOfLine()
            tb.AppendContext("加速：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["hastePercent"], self.result["equip"]["haste"]))
            tb.EndOfLine()

            b2 = tk.Button(frame2, text='导出', height=1, command=self.exportEquipment)
            b2.place(x=140, y=180)

        # Part 3: 治疗
        frame3 = tk.Frame(window, width=310, height=150, highlightthickness=1, highlightbackground="#64fab4")
        frame3.place(x=430, y=10)
        frame3sub = tk.Frame(frame3)
        frame3sub.place(x=0, y=0)

        tb = TableConstructor(self.config, frame3sub)
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效HPS", "最常用语境下的每秒治疗量，注意包含重伤时间。")
        tb.AppendHeader("虚条HPS", "指虚条的最右端，包含溢出治疗量，也即计算所有绿字。")
        tb.EndOfLine()
        for record in self.result["healer"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["healEff"])
            tb.AppendContext(record["heal"])
            tb.EndOfLine()

        # Part 4: 奇穴
        frame4 = tk.Frame(window, width=310, height=70, highlightthickness=1, highlightbackground="#64fab4")
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

        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#64fab4")
        frame5.place(x=10, y=250)

        frame5_1 = tk.Frame(frame5, width=180, height=95)
        frame5_1.place(x=0, y=0)
        frame5_1.photo = tk.PhotoImage(file="icons/7059.png")
        label = tk.Label(frame5_1, image=frame5_1.photo)
        label.place(x=5, y=25)
        ToolTip(label, "梅花三弄")
        text = "数量：%d(%.2f)\n"%(self.result["skill"]["meihua"]["num"], self.result["skill"]["meihua"]["numPerSec"])
        text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["meihua"]["cover"])
        text = text + "延迟：%dms\n" % self.result["skill"]["meihua"]["delay"]
        text = text + "犹香HPS：%d\n" % self.result["skill"]["meihua"].get("youxiangHPS", 0)
        text = text + "平吟HPS：%d\n" % self.result["skill"]["meihua"].get("pingyinHPS", 0)
        label = tk.Label(frame5_1, text=text, justify="left")
        label.place(x=60, y=10)

        frame5_2 = tk.Frame(frame5, width=180, height=95)
        frame5_2.place(x=180, y=0)
        frame5_2.photo = tk.PhotoImage(file="icons/7174.png")
        label = tk.Label(frame5_2, image=frame5_2.photo)
        label.place(x=5, y=25)
        ToolTip(label, "徵")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["zhi"]["num"], self.result["skill"]["zhi"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["zhi"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["zhi"]["HPS"]
        text = text + "古道HPS：%d\n" % self.result["skill"]["zhi"].get("gudaoHPS", 0)
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["zhi"]["effRate"])
        label = tk.Label(frame5_2, text=text, justify="left")
        label.place(x=60, y=10)

        frame5_3 = tk.Frame(frame5, width=180, height=95)
        frame5_3.place(x=360, y=0)
        frame5_3.photo = tk.PhotoImage(file="icons/7176.png")
        label = tk.Label(frame5_3, image=frame5_3.photo)
        label.place(x=5, y=25)
        ToolTip(label, "角")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["jue"]["num"], self.result["skill"]["jue"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["jue"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["jue"]["HPS"]
        text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["jue"]["cover"])
        label = tk.Label(frame5_3, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_4 = tk.Frame(frame5, width=180, height=95)
        frame5_4.place(x=540, y=0)
        frame5_4.photo = tk.PhotoImage(file="icons/7172.png")
        label = tk.Label(frame5_4, image=frame5_4.photo)
        label.place(x=5, y=25)
        ToolTip(label, "商")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["shang"]["num"], self.result["skill"]["shang"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["shang"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["shang"]["HPS"]
        text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["shang"]["cover"])
        label = tk.Label(frame5_4, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_5 = tk.Frame(frame5, width=180, height=95)
        frame5_5.place(x=0, y=100)
        frame5_5.photo = tk.PhotoImage(file="icons/7173.png")
        label = tk.Label(frame5_5, image=frame5_5.photo)
        label.place(x=5, y=25)
        ToolTip(label, "宫")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["gong"]["num"], self.result["skill"]["gong"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["gong"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["gong"]["HPS"]
        text = text + "枕流HPS：%d\n" % self.result["skill"]["meihua"].get("zhenliuHPS", 0)
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["gong"]["effRate"])
        label = tk.Label(frame5_5, text=text, justify="left")
        label.place(x=60, y=10)

        frame5_6 = tk.Frame(frame5, width=180, height=95)
        frame5_6.place(x=180, y=100)
        frame5_6.photo = tk.PhotoImage(file="icons/7175.png")
        label = tk.Label(frame5_6, image=frame5_6.photo)
        label.place(x=5, y=25)
        ToolTip(label, "羽")
        text = "数量：%d\n"%self.result["skill"]["yu"]["num"]
        text = text + "延迟：%dms\n" % self.result["skill"]["yu"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["yu"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["yu"]["effRate"])
        label = tk.Label(frame5_6, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_7 = tk.Frame(frame5, width=180, height=95)
        frame5_7.place(x=360, y=100)
        text = "相依数量：%d\n" % self.result["skill"]["xiangyi"]["num"]
        text = text + "相依HPS：%d\n" % self.result["skill"]["xiangyi"]["HPS"]
        text = text + "沐风覆盖率：%s%%\n" % parseCent(self.result["skill"]["mufeng"]["cover"])
        label = tk.Label(frame5_7, text=text, justify="left")
        label.place(x=20, y=25)

        frame5_8 = tk.Frame(frame5, width=180, height=95)
        frame5_8.place(x=540, y=100)
        text = "APS：%d\n" % self.result["skill"]["general"].get("APS", 0)
        text = text + "桑柔DPS：%d\n" % self.result["skill"]["general"]["SangrouDPS"]
        text = text + "庄周梦DPS：%d\n" % self.result["skill"]["general"]["ZhuangzhouDPS"]
        text = text + "玉简DPS：%d\n" % self.result["skill"]["general"].get("YujianDPS", 0)
        text = text + "战斗效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiency"])
        label = tk.Label(frame5_8, text=text, justify="left")
        label.place(x=20, y=10)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

        # Part 6: 回放

        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#64fab4")
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

        #canvas6 = tk.Canvas(frame6sub, width=battleTimePixels, height=125)
        # 绘制主时间轴及时间
        canvas6.create_rectangle(0, 30, battleTimePixels, 70, fill='white')
        if "heatType" in self.result["replay"]:
            if self.result["replay"]["heatType"] == "meihua":
                nowTimePixel = 0
                for line in self.result["replay"]["heat"]["timeline"]:
                    color = getColorHex((int(255 - (255 - 100) * line / 100),
                                         int(255 - (255 - 250) * line / 100),
                                         int(255 - (255 - 180) * line / 100)))
                    canvas6.create_rectangle(nowTimePixel, 31, nowTimePixel + 5, 70, fill=color, width=0)
                    nowTimePixel += 5
                # canvas6.create_image(10, 40, image=canvas6.im["7059"])
            elif self.result["replay"]["heatType"] == "hot":
                yPos = [31, 39, 47, 55, 63, 70]
                for j in range(5):
                    nowTimePixel = 0
                    for line in self.result["replay"]["heat"]["timeline"][j]:
                        if line == 0:
                            color = "#ff7777"
                        else:
                            color = getColorHex((int(255 - (255 - 100) * line / 100),
                                                 int(255 - (255 - 250) * line / 100),
                                                 int(255 - (255 - 180) * line / 100)))
                        canvas6.create_rectangle(nowTimePixel, yPos[j], nowTimePixel + 5, yPos[j+1], fill=color, width=0)
                        nowTimePixel += 5
                # canvas6.create_image(10, 40, image=canvas6.im["7172"])
                # canvas6.create_image(30, 40, image=canvas6.im["7176"])
        nowt = 0
        while nowt < battleTime:
            nowt += 10000
            text = parseTime(nowt / 1000)
            pos = int(nowt / 100)
            canvas6.create_text(pos, 50, text=text)
        # 绘制常规技能轴
        for record in self.result["replay"]["normal"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 80, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 70, posEnd, 90, fill="#64fab4")
            # 绘制重复次数
            if posStart + 30 < posEnd and record["num"] > 1:
                canvas6.create_text(posStart+30, 80, text="*%d"%record["num"])

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

        # Part 7: 输出
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#64fab4")
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
        tb.AppendHeader("自身DPS", "全程去除庄周梦/玉简增益后的DPS，注意包含重伤时间。")
        tb.AppendHeader("覆盖率", "梅花三弄的覆盖率。")
        tb.AppendHeader("破盾", "破盾次数，包含盾受到伤害消失、未刷新自然消失、及穿透消失。")
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.AppendContext(parseCent(record["shieldRate"]) + '%')
            tb.AppendContext(record["shieldBreak"])
            tb.EndOfLine()

        # Part 8: 打分
        frame8 = tk.Frame(window, width=210, height=200, highlightthickness=1, highlightbackground="#64fab4")
        frame8.place(x=320, y=620)
        frame8sub = tk.Frame(frame8)
        frame8sub.place(x=30, y=30)

        if self.result["score"]["available"] == 0:
            tk.Label(frame8, text="复盘生成时的版本尚不支持打分。").place(x=10, y=150)
        elif self.result["score"]["available"] == 11:
            tk.Label(frame8, text="由于BOSS机制原因，不提供打分结果。").place(x=10, y=150)
        else:
            tb = TableConstructor(self.config, frame8sub)
            tb.AppendHeader("数值分：", "对治疗数值的打分，包括治疗量、各个技能数量。")
            descA = "治疗量评分：%.1f\n盾数量评分：%.1f\n徵数量评分：%.1f\n宫数量评分：%.1f" % (self.result["score"]["scoreA1"], self.result["score"]["scoreA2"],
                                                               self.result["score"]["scoreA3"], self.result["score"]["scoreA4"])
            tb.AppendHeader(self.result["score"]["scoreA"], descA, width=9)
            lvlA, colorA, _ = self.getLvl(self.result["score"]["scoreA"])
            tb.AppendContext(lvlA, color=colorA)
            tb.EndOfLine()
            tb.AppendHeader("统计分：", "对统计结果的打分，包括梅花三弄和HOT的覆盖率。")
            descB = "盾覆盖率评分：%.1f\nHOT覆盖率评分：%.1f" % (self.result["score"]["scoreB1"], self.result["score"]["scoreB2"])
            tb.AppendHeader(self.result["score"]["scoreB"], descB, width=9)
            lvlB, colorB, _ = self.getLvl(self.result["score"]["scoreB"])
            tb.AppendContext(lvlB, color=colorB)
            tb.EndOfLine()
            tb.AppendHeader("操作分：", "对操作表现的打分，包括战斗效率，各个技能延迟。")
            descC = "战斗效率评分：%.1f\n盾延迟评分：%.1f\n徵延迟评分：%.1f\n宫延迟评分：%.1f" % (self.result["score"]["scoreC1"], self.result["score"]["scoreC2"],
                                                               self.result["score"]["scoreC3"], self.result["score"]["scoreC4"])
            tb.AppendHeader(self.result["score"]["scoreC"], descC, width=9)
            lvlC, colorC, _ = self.getLvl(self.result["score"]["scoreC"])
            tb.AppendContext(lvlC, color=colorC)
            tb.EndOfLine()

            tb.AppendHeader("总评：", "综合计算这几项的结果。")
            tb.AppendContext(self.result["score"]["sum"], width=9)
            lvl, color, desc = self.getLvl(self.result["score"]["sum"])
            tb.AppendContext(lvl, color=color)
            tb.EndOfLine()
            tk.Label(frame8, text=desc, fg=color).place(x=10, y=150)

        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#64fab4")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="相知PVE群：538939220").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb)
            b2.place(x=40, y=90)

        tk.Label(frame9, text="广告位招租").place(x=40, y=140)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        '''
        创建并展示窗口.
        '''
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def alive(self):
        '''
        返回窗口是否仍生存.
        returns:
        - res: 布尔类型，窗口是否仍生存.
        '''
        return self.windowAlive

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - result: 奶歌复盘的结果.
        '''
        self.config = config
        self.mask = self.config.item["general"]["mask"]
        self.result = result

class XiangZhiProReplayer(ReplayerBase):
    '''
    奶歌复盘pro类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 大部分全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶歌复盘pro v%s"%EDITION
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
        self.result["overall"]["calTank"] = self.config.item["xiangzhi"]["caltank"]
        self.result["overall"]["mask"] = self.config.item["general"]["mask"]
        self.result["overall"]["win"] = self.win

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"',
                                  '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
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

        self.shieldCountersNew = {}
        for key in self.bld.info.player:
            self.shieldCountersNew[key] = ShieldCounterNew("16911", self.startTime, self.finalTime)

        # 自动推导奶歌角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            raise Exception("奶歌名暂时不可自动推导，需要通过前序分析来手动指定")
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
                # 记录奶歌和治疗心法的出现情况.
                if event.caster not in XiangZhiList and event.id in ["14231", "14140", "14301"]:  # 奶歌的特征技能
                    XiangZhiList.append(event.caster)
                    self.healerDict[event.caster] = 0
                if event.caster not in self.healerDict and event.id in ["565", "554", "555", "2232", "6662", "2233", "6675",
                                                                  "2231", "101", "142", "138", "16852", "18864", "27621", "27623", "28083"]:  # 其它治疗的特征技能
                    self.healerDict[event.caster] = 0

                # 记录主动贴盾，主要是为了防止复盘记录中的数据丢失。
                if event.id == "14231" and event.caster == self.mykey:
                    jianLiaoStack = 0
                    if event.target in jianLiaoLog:
                        jianLiaoStack = jianLiaoLog[event.target].checkState(event.time)
                    if jianLiaoStack < 20:
                        self.shieldCountersNew[event.target].setState(event.time, 1)

                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22', '212']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"宓桃"':
                    self.activeBoss = "宓桃"
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif event.dataType == "Buff":
                if event.id in ["9334", "16911"] and event.caster == self.mykey:  # buff梅花三弄
                    self.shieldCountersNew[event.target].setState(event.time, event.stack)
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

        for key in self.bld.info.player:
            self.shieldCountersNew[key].inferFirst()

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
            res = adr.Display(strEquip, "22h")
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
            if not self.config.item["xiangzhi"]["speedforce"]:
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
                else:
                    self.result["qixue"][key] = self.bld.info.player[self.mykey].qx[key]["2"]

        # print(self.result["overall"])
        # print(self.result["equip"])
        # print(self.result["qixue"])

        self.result["overall"]["hasteReal"] = self.haste

        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        occDetailList = self.occDetailList

        #data = XiangZhiData()

        num = 0
        skillLog = []

        # 以承疗者记录的关键治疗
        self.criticalHealCounter = {}
        hpsActive = 0

        # 以治疗者记录的关键治疗
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            # numSmall = 0

        numHeal = 0
        numEffHeal = 0
        numAbsorb1 = 0  # jx3dat推测的化解
        numAbsorb2 = 0  # 战斗记录推测的化解
        npcHealStat = {}
        numPurge = 0 # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        healStat = {}  # 治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        rateDict = {}  # 盾覆盖率
        breakDict = {}  # 破盾次数
        battleTimeDict = {}  # 进战时间
        sumShield = 0  # 盾数量
        sumPlayer = 0  # 玩家数量
        teamLog = {}  # 小队聚类数量统计
        teamLastTime = {}  # 小队聚类时间

        # 技能统计
        mhsnSkill = SkillHealCounter("14231", self.startTime, self.finalTime, self.haste)  # 梅花三弄
        gongSkill = SkillHealCounter("14137", self.startTime, self.finalTime, self.haste)  # 宫
        zhiSkill = SkillHealCounter("14140", self.startTime, self.finalTime, self.haste)  # 徵
        yuSkill = SkillHealCounter("14141", self.startTime, self.finalTime, self.haste)  # 羽
        shangSkill = SkillHealCounter("14138", self.startTime, self.finalTime, self.haste)  # 商
        jueSkill = SkillHealCounter("14139", self.startTime, self.finalTime, self.haste)  # 角
        shangBuff = SkillHealCounter("9459", self.startTime, self.finalTime, self.haste)  # 商
        jueBuff = SkillHealCounter("9463", self.startTime, self.finalTime, self.haste)  # 角
        xySkill = SkillHealCounter("21321", self.startTime, self.finalTime, self.haste)  # 相依
        shangBuffDict = {}
        jueBuffDict = {}
        nongmeiDict = {}  # 弄梅
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风
        battleDict = {}
        firstHitDict = {}
        for line in self.bld.info.player:
            shangBuffDict[line] = HotCounter("9459", self.startTime, self.finalTime)  # 商，9460=殊曲，9461=洞天
            jueBuffDict[line] = HotCounter("9463", self.startTime, self.finalTime)  # 角，9460=殊曲，9461=洞天
            battleDict[line] = BuffCounter("0", self.startTime, self.finalTime)  # 战斗状态统计
            nongmeiDict[line] = BuffCounter("9584", self.startTime, self.finalTime)
            firstHitDict[line] = 0
            teamLog[line] = {}
            teamLastTime[line] = 0
        lastSkillTime = self.startTime

        # 杂项
        fengleiActiveTime = self.startTime
        youxiangHeal = 0
        pingyinHeal = 0
        gudaoHeal = 0
        zhenliuHeal = 0

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True],
                     [mhsnSkill, "梅花三弄", ["14231"], "7059", True, 0, False, True],
                     [gongSkill, "宫", ["18864", "14360", "16852"], "7173", True, 24, False, True],
                     [zhiSkill, "徵", ["14362", "18865"], "7174", True, 8, True, True],
                     [yuSkill, "羽", ["14141", "14354", "14355", "14356"], "7175", True, 0, False, True],
                     [shangSkill, "商", ["14138"], "7172", True, 0, False, True],
                     [jueSkill, "角", ["14139"], "7176", True, 0, False, True],
                     [None, "一指回鸾", ["14169"], "7045", True, 0, False, True],
                     [None, "孤影化双", ["14081"], "7052", False, 0, False, True],
                     [None, "云生结海", ["14075"], "7048", False, 0, False, True],
                     [None, "高山流水", ["14069"], "7080", False, 0, False, True],
                     [None, "青霄飞羽", ["14076"], "7078", False, 0, False, True],
                     [None, "青霄飞羽·落", ["21324"], "7128", False, 0, False, True],
                     [None, "移形换影", ["15039", "15040", "15041", "15042", "15043", "15044"], "7066", False, 0, False, True],
                     [None, "高山流水·切换", ["18838", "18839"], "7080", False, 0, False, True],
                     [None, "梅花三弄·切换", ["18841", "18842"], "7059", False, 0, False, True],
                     [None, "阳春白雪·切换", ["18845", "18846"], "7077", False, 0, False, True],
                    ]

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i

        xiangZhiUnimportant = ["15181", "15082", "25232",  # 影子宫，桑柔
                               "14082", # 疏影横斜
                               "4877", "15054", "15057",  # 水特效作用，盾奇穴效果
                               "25683", "24787",  # 破招
                               "22155", "22207",  # 大附魔
                               "14535", "14532", # 徵判定
                               "3071", "18274", "14646",  # 治疗套装，寒清，书离
                               "23951", # 贯体通用
                               "15168", "14357", "15169", "15170", "14358", # 羽
                               "14536", "14537", # 盾填充, 盾移除
                               "15138", "15081", "15153", # 影子判定
                               "25237", # 古道
                               "14071", # 盾主动切换技能
                               "26894", # 平吟新效果
                               "3584", "2448",  # 蛊惑
                               "604", # 春泥
                               "4697", "13237", # 队友阵眼
                               "6800", # 风？
                               "14084", # 杯水
                               "14162", # 收孤影
                               "15055", # 盾高血量
                               "13332", # 锋凌横绝阵
                               "25231", # 桑柔判定
                               "14137", "14300", # 宫的壳技能
                               "14140", "14301", # 徵的壳技能
                               "14407", "14408", "14409", "14410", "14411", "14412", "14413", "14414", "14415",  # 寸光阴的智障判定
                               "14395", "14396", "14397", "14398", "14399", "14400", "14401", "14402",  # 估计是寸光阴添加HOT
                               "15090", "14344",  # 阳春白雪主动技能（无尽藏！）
                               "14243",  # 掷杯判定
                               "22211",  # 治疗衣服大附魔
                               "15091",  # 阳春添加状态切换buff
                               "9007",  # 后跳 (TODO) 统计各种后跳
                               "9004", "9005", "9006",  # 左右小轻功
                               "26731",  # 不器
                               "26965",  # 枕流
                               "14150",  # 云生结海平摊
                               "29532", "29541",  # 飘黄
                               "14427", "14426",  # 浮生清脉阵
                               "20763", "20764", "21321",  # 相依
                               "14153",  # 云生结海
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    numAbsorb1 += event.healEff
                else:
                    # 所有治疗技能都不计算化解.
                    # 统计自身治疗
                    if event.caster == self.mykey and event.heal != 0:
                        numHeal += event.heal
                        numEffHeal += event.healEff

                    # 统计团队治疗
                    if event.heal + event.healEff > 0 and event.effect != 7 and event.caster in self.healerDict:
                        if event.caster not in healStat:
                            healStat[event.caster] = [0, 0]
                        healStat[event.caster][0] += event.healEff
                        healStat[event.caster][1] += event.heal

                    # 统计自身技能使用情况.
                    # if event.caster == self.mykey and event.scheme == 1 and event.id in xiangZhiUnimportant and event.heal != 0:
                    #     print(event.id, event.time)

                    if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey:
                        # 打印所有有治疗量的技能，以进行整理
                        # print("[Heal]", event.id, event.heal)
                        pass

                    if event.caster == self.mykey and event.scheme == 1 and event.id not in xiangZhiUnimportant:  # 影子宫、桑柔等需要过滤的技能
                        # skillLog.append([event.time, event.id])

                        # 若技能没有连续，则在战斗回放中记录技能
                        if ((event.id not in gcdSkillIndex or gcdSkillIndex[event.id] != gcdSkillIndex[ss.skill]) and event.id not in nonGcdSkillIndex)\
                          or event.time - ss.timeEnd > 3000:
                            # 记录本次技能
                            # print("[ReplaceSkill]", event.id, ss.skill)
                            # 此处的逻辑完全可以去掉，保留这个逻辑就是为了监控哪些是值得挖掘的隐藏技能

                            if ss.skill != "0":
                                index = gcdSkillIndex[ss.skill]
                                line = skillInfo[index]
                                bh.setNormalSkill(ss.skill, line[1], line[3],
                                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                                  roundCent(ss.healEff / (ss.heal + 1e-10)),
                                                  int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")
                            ss.reset()
                        # 根据技能表进行自动处理
                        if event.id in gcdSkillIndex:
                            if ss.skill == "0":
                                ss.initSkill(event)
                            index = gcdSkillIndex[event.id]
                            line = skillInfo[index]
                            ss.analyseSkill(event, line[5], line[0], tunnel=line[6], hasteAffected=line[7])
                        # 处理特殊技能
                        elif event.id in nonGcdSkillIndex:  # 特殊技能
                            desc = ""
                            if event.id in ["18838", "18839"]:
                                desc = "切换曲风到高山流水"
                            if event.id in ["18841", "18842"]:
                                desc = "切换曲风到梅花三弄"
                            if event.id in ["18845", "18846"]:
                                desc = "切换曲风到阳春白雪"
                            index = nonGcdSkillIndex[event.id]
                            line = skillInfo[index]
                            bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)

                    if event.caster == self.mykey and event.scheme == 1:
                        # 统计不计入时间轴的治疗量
                        if event.id == "15057":  # 犹香
                            youxiangHeal += event.healEff
                        if event.id == "26894":  # 平吟
                            pingyinHeal += event.healEff
                        if event.id == "23951" and event.level == 75:  # 古道
                            gudaoHeal += event.healEff
                        if event.id == "26965":  # 枕流
                            zhenliuHeal += event.healEff
                        if event.id == "21321":  # 相依
                            xySkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

                    if event.caster == self.mykey and event.scheme == 2:
                        if event.id in ["9459", "9460", "9461", "9462"]:  # 商
                            shangBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        elif event.id in ["9463", "9464", "9465", "9466"]:  # 角
                            jueBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

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

                    # 尝试统计化解
                    if event.target in self.bld.info.player:
                        absorb = int(event.fullResult.get("9", 0))
                        if absorb > 0:
                            meihua = self.shieldCountersNew[event.target].checkState(event.time - 100)
                            nongmei = nongmeiDict[event.target].checkState(event.time - 100)
                            if meihua or nongmei:
                                numAbsorb2 += absorb

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.shieldCountersNew:
                        if event.caster not in battleStat:
                            battleStat[event.caster] = [0, 0, 0, 0]  # 无盾伤害，有盾伤害，桑柔伤害，玉简伤害
                        if int(event.id) >= 21827 and int(event.id) <= 21831:  # 玉简
                            battleStat[event.caster][3] += event.damageEff
                        elif event.id == "25232" and event.caster == self.mykey:  # 桑柔伤害
                            battleStat[event.caster][2] += event.damageEff
                        else:
                            hasShield = self.shieldCountersNew[event.caster].checkState(event.time)
                            battleStat[event.caster][hasShield] += event.damageEff

                # 根据战斗信息推测进战状态
                if event.caster in self.bld.info.player and firstHitDict[event.caster] == 0 and (event.damageEff > 0 or event.healEff > 0):
                    firstHitDict[event.caster] = 1
                    if event.scheme == 1:
                        battleDict[event.caster].setState(event.time, 1)

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["9459", "9460", "9461", "9462"] and event.caster == self.mykey:  # 商
                    shangBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                if event.id in ["9463", "9464", "9465", "9466"] and event.caster == self.mykey:  # 角
                    jueBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                if event.id == "10521":  # 风雷标志debuff:
                    if event.stack == 1:
                        fengleiActiveTime = max(event.time, lastSkillTime)
                    else:
                        bh.setNormalSkill("15502", "风雷引", "8625",
                                          fengleiActiveTime, event.time - fengleiActiveTime, 1, 0,
                                          0,
                                          0, 1, "风雷读条，在此不做细节区分，只记录读条时间")
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                if event.id in ["10193"] and event.stack == 1:  # cw特效:
                    bh.setSpecialSkill(event.id, "cw特效", "14416",
                                       event.time, 0, "触发cw特效")
                if event.id in ["9584"] and event.caster == self.mykey:  # 弄梅
                    nongmeiDict[event.target].setState(event.time, event.stack)
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                if event.id in self.bld.info.player:
                    battleDict[event.id].setState(event.time, event.fight)

            num += 1

        # 记录最后一个技能
        if ss.skill != "0":
            index = gcdSkillIndex[ss.skill]
            line = skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]

        # 计算战斗效率等统计数据，TODO 扩写
        # skillCounter = SkillLogCounter(skillLog, self.startTime, self.finalTime, self.haste, ss.skillLog)
        # skillCounter.analysisSkillData()
        # sumBusyTime = skillCounter.sumBusyTime
        # sumSpareTime = skillCounter.sumSpareTime
        # spareRate = sumSpareTime / (sumBusyTime + sumSpareTime + 1e-10)

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

        # 计算组队聚类信息
        teamCluster, numCluster = finalCluster(teamLog)

        # 计算等效伤害
        numdam1 = 0
        numdam3 = 0
        for key in battleStat:
            line = battleStat[key]
            # damageDict[key] = line[0] + line[1] / 1.117 # 100赛季数值
            # numdam1 += line[1] / 1.117 * 0.117# + line[2]
            damageDict[key] = line[0] + line[1] / 1.0554  # 110赛季数值
            numdam1 += line[1] / 1.0554 * 0.0554
            numdam3 += line[3]
        if self.mykey in battleStat:
            numdam2 = battleStat[self.mykey][2]
        else:
            numdam2 = 0
        # numdam = numdam1 + numdam2

        # 关键治疗量统计
        if self.activeBoss in ["宓桃", "哑头陀"]:
            for line in npcHealStat:
                npcHealStat[line] /= (hpsSumTime + 1e-10)

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0}
        healList = dictToPairs(healStat)
        healList.sort(key=lambda x: -x[1][0])

        sumHeal = 0
        numid = 0
        topHeal = 0
        for line in healList:
            if numid == 0:
                topHeal = line[1][0]
            sumHeal += line[1][0]
            numid += 1
            if line[0] == self.mykey and myHealRank == 0:
                myHealRank = numid
            # 当前逻辑为治疗量大于第一的20%才被记为治疗，否则为老板
            if line[1][0] > topHeal * 0.2:
                numHealer += 1
        if myHealRank > numHealer:
            numHealer = myHealRank
        self.result["healer"]["numHealer"] = numHealer
        for line in healList:
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "healEff": int(line[1][0] / self.result["overall"]["sumTime"] * 1000),
                   "heal": int(line[1][1] / self.result["overall"]["sumTime"] * 1000)}
            self.result["healer"]["table"].append(res)

        # 计算DPS列表(Part 7)
        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # for line in occDetailList:
        #     print(line, occDetailList[line], self.bld.info.player[line].name)

        # 计算DPS的盾指标
        overallShieldHeat = {"interval": 500, "timeline": []}
        for key in self.shieldCountersNew:
            sumShield += self.shieldCountersNew[key].countCast()
            liveCount = battleDict[key].buffTimeIntegral()  # 存活时间比例
            # print(self.bld.info.player[key].name, liveCount, battleDict[key].sumTime())
            # print(battleDict[key].log)
            if battleDict[key].sumTime() - liveCount < 8000:  # 脱战缓冲时间
                liveCount = battleDict[key].sumTime()
            battleTimeDict[key] = liveCount
            sumPlayer += liveCount / battleDict[key].sumTime()
            # 过滤老板，T奶，自己
            if key not in damageDict or damageDict[key] / self.result["overall"]["sumTime"] * 1000 < 10000:
                continue
            if getOccType(occDetailList[key]) == "healer":
                continue
            if getOccType(occDetailList[key]) == "tank" and not self.config.item["xiangzhi"]["caltank"]:
                continue
            if key == self.mykey:
                continue
            time1 = self.shieldCountersNew[key].buffTimeIntegral()
            timeAll = liveCount
            rateDict[key] = time1 / (timeAll + 1e-10)
            breakDict[key] = self.shieldCountersNew[key].countBreak()

            shieldHeat = self.shieldCountersNew[key].getHeatTable(500)
            if overallShieldHeat["timeline"] == []:
                for i in shieldHeat["timeline"]:
                    overallShieldHeat["timeline"].append(i * 4)  # 按25人构造热力图
            else:
                for i in range(len(shieldHeat["timeline"])):
                    overallShieldHeat["timeline"][i] += shieldHeat["timeline"][i] * 4

        for line in damageList:
            if line[0] not in rateDict:
                continue
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   "shieldRate": roundCent(rateDict[line[0]]),
                   "shieldBreak": breakDict[line[0]]}
            self.result["dps"]["table"].append(res)

        # 计算覆盖率
        numRate = 0
        sumRate = 0
        for key in rateDict:
            numRate += battleTimeDict[key]
            sumRate += rateDict[key] * battleTimeDict[key]
        overallRate = sumRate / (numRate + 1e-10)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 梅花三弄
        self.result["skill"]["meihua"] = {}
        self.result["skill"]["meihua"]["num"] = mhsnSkill.getNum()
        self.result["skill"]["meihua"]["numPerSec"] = roundCent(self.result["skill"]["meihua"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["meihua"]["delay"] = int(mhsnSkill.getAverageDelay())
        self.result["skill"]["meihua"]["cover"] = roundCent(overallRate)
        self.result["skill"]["meihua"]["youxiangHPS"] = int(youxiangHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["meihua"]["pingyinHPS"] = int(pingyinHeal / self.result["overall"]["sumTime"] * 1000)
        # 宫
        self.result["skill"]["gong"] = {}
        self.result["skill"]["gong"]["num"] = gongSkill.getNum()
        self.result["skill"]["gong"]["numPerSec"] = roundCent(self.result["skill"]["gong"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["gong"]["delay"] = int(gongSkill.getAverageDelay())
        effHeal = gongSkill.getHealEff()
        self.result["skill"]["gong"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["gong"]["effRate"] = effHeal / (gongSkill.getHeal() + 1e-10)
        self.result["skill"]["gong"]["zhenliuHPS"] = int(zhenliuHeal / self.result["overall"]["sumTime"] * 1000)
        # 徵
        self.result["skill"]["zhi"] = {}
        self.result["skill"]["zhi"]["num"] = zhiSkill.getNum()
        self.result["skill"]["zhi"]["numPerSec"] = roundCent(self.result["skill"]["zhi"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["zhi"]["delay"] = int(zhiSkill.getAverageDelay())
        effHeal = zhiSkill.getHealEff()
        self.result["skill"]["zhi"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["zhi"]["effRate"] = roundCent(effHeal / (zhiSkill.getHeal() + 1e-10))
        self.result["skill"]["zhi"]["gudaoHPS"] = int(gudaoHeal / self.result["overall"]["sumTime"] * 1000)
        # 羽
        self.result["skill"]["yu"] = {}
        self.result["skill"]["yu"]["num"] = yuSkill.getNum()
        self.result["skill"]["yu"]["delay"] = int(yuSkill.getAverageDelay())
        effHeal = yuSkill.getHealEff()
        self.result["skill"]["yu"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["yu"]["effRate"] = roundCent(effHeal / (yuSkill.getHeal() + 1e-10))
        # 队伍HOT统计初始化
        hotHeat = [[], [], [], [], []]
        # 商，注意Buff与Skill统计不同
        self.result["skill"]["shang"] = {}
        self.result["skill"]["shang"]["num"] = shangBuff.getNum()
        self.result["skill"]["shang"]["numPerSec"] = roundCent(
            self.result["skill"]["shang"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["shang"]["delay"] = int(shangSkill.getAverageDelay())
        effHeal = shangBuff.getHealEff()
        self.result["skill"]["shang"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        num = 0
        sum = 0
        for key in shangBuffDict:
            singleDict = shangBuffDict[key]
            num += battleTimeDict[key]
            sum += singleDict.buffTimeIntegral()
            singleHeat = singleDict.getHeatTable()
            if teamCluster[key] <= 5:
                if len(hotHeat[teamCluster[key] - 1]) == 0:
                    for line in singleHeat["timeline"]:
                        hotHeat[teamCluster[key] - 1].append(line)
                else:
                    for i in range(len(singleHeat["timeline"])):
                        hotHeat[teamCluster[key] - 1][i] += singleHeat["timeline"][i]
        self.result["skill"]["shang"]["cover"] = roundCent(sum / (num + 1e-10))
        # 角
        self.result["skill"]["jue"] = {}
        self.result["skill"]["jue"]["num"] = jueBuff.getNum()
        self.result["skill"]["jue"]["numPerSec"] = roundCent(
            self.result["skill"]["jue"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["jue"]["delay"] = int(jueSkill.getAverageDelay())
        effHeal = jueBuff.getHealEff()
        self.result["skill"]["jue"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        num = 0
        sum = 0
        for key in jueBuffDict:
            singleDict = jueBuffDict[key]
            num += battleTimeDict[key]
            sum += singleDict.buffTimeIntegral()
            singleHeat = singleDict.getHeatTable()
            if teamCluster[key] <= 5:
                if len(hotHeat[teamCluster[key] - 1]) == 0:
                    for line in singleHeat["timeline"]:
                        hotHeat[teamCluster[key] - 1].append(line)
                else:
                    for i in range(len(singleHeat["timeline"])):
                        hotHeat[teamCluster[key] - 1][i] += singleHeat["timeline"][i]
        self.result["skill"]["jue"]["cover"] = roundCent(sum / (num + 1e-10))
        # 计算HOT统计
        for i in range(len(hotHeat)):
            if i+1 >= len(numCluster) or numCluster[i+1] == 0:
                continue
            for j in range(len(hotHeat[i])):
                hotHeat[i][j] = int(hotHeat[i][j] / numCluster[i+1] * 50)
        # print("[teamCluster]", teamCluster)
        # print("[HotHeat]", hotHeat)
        # print("[HotHeat0]", hotHeat[0])
        # 杂项
        self.result["skill"]["xiangyi"] = {}
        self.result["skill"]["xiangyi"]["num"] = xySkill.getNum()
        effHeal = xySkill.getHealEff()
        self.result["skill"]["xiangyi"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xiangyi"]["effRate"] = roundCent(effHeal / (xySkill.getHeal() + 1e-10))
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["APS"] = int(numAbsorb2 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["SangrouDPS"] = int(numdam2 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["ZhuangzhouDPS"] = int(numdam1 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["YujianDPS"] = int(numdam3 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()

        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        if self.result["skill"]["shang"]["cover"] > 0.1:  # HOT覆盖率大于10%，判定为血鸽
            self.result["replay"]["heatType"] = "hot"
            self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}
        else:  # 默认为盾鸽
            self.result["replay"]["heatType"] = "meihua"
            self.result["replay"]["heat"] = overallShieldHeat

        # print(self.result["healer"])
        # print(self.result["dps"])
        # print(self.result["skill"])
        # for line in self.result["replay"]["normal"]:
        #     print(line)
        # print("===")
        # for line in self.result["replay"]["special"]:
        #     print(line)
        #
        # f1 = open("xiangzhiTest.txt", "w")
        # for line in self.result["replay"]["normal"]:
        #     f1.write(str(line))
        # f1.write("===")
        # for line in self.result["replay"]["special"]:
        #     f1.write(str(line))
        # f1.close()

    def scaleScore(self, x, scale):
        N = len(scale)
        assert N >= 1
        if N == 1:
            return scale[0][1]
        score = 0
        if scale[0][0] > scale[1][0]:
            x = -x
            for i in range(N):
                scale[i][0] = -scale[i][0]
        for i in range(0, N - 1):
            assert scale[i][0] < scale[i + 1][0]

        if x < scale[0][0]:
            score = scale[0][1]
        else:
            for i in range(0, N - 1):
                if x >= scale[i][0] and x < scale[i + 1][0]:
                    score = scale[i][1] + (x - scale[i][0]) / (scale[i + 1][0] - scale[i][0] + 1e-10) * (scale[i + 1][1] - scale[i][1])
                    break
            else:
                score = scale[N - 1][1]
        return score

    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''

        self.result["score"] = {"available": 0, "sum": 0}

        map = self.result["overall"]["map"]
        boss = self.result["overall"]["boss"]
        if map not in ["25人普通雷域大泽", "25人英雄雷域大泽"]:
            return
        if boss not in ["巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]:
            return

        if boss == "巨型尖吻凤":
            self.result["score"]["available"] = 11  # BOSS机制原因不提供评分
            return

        self.result["score"]["available"] = 1
        # 数值分A
        # 治疗量A1
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0], [2072, 3], [4129, 6], [5294, 10]],
                                  '桑乔': [[0, 0], [1520, 3], [3150, 6], [4302, 10]],
                                  '悉达罗摩': [[0, 0], [4712, 3], [8983, 6], [11416, 10]],
                                  '尤珈罗摩': [[0, 0], [43743, 3], [57848, 6], [72406, 10]],
                                  '月泉淮': [[0, 0], [5180, 3], [14029, 6], [21187, 10]],
                                  '乌蒙贵': [[0, 0], [5490, 3], [14115, 6], [17161, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0], [2259, 3], [4488, 6], [5358, 10]],
                                  '桑乔': [[0, 0], [1984, 3], [3562, 6], [4563, 10]],
                                  '悉达罗摩': [[0, 0], [4433, 3], [7054, 6], [8911, 10]],
                                  '尤珈罗摩': [[0, 0], [67502, 3], [75771, 6], [87567, 10]],
                                  '月泉淮': [[0, 0], [8170, 3], [14506, 6], [16076, 10]],
                                  '乌蒙贵': [[0, 0], [3476, 3], [8271, 6], [11394, 10]]}}
        std = stdTable[map][boss]
        heal = 0
        for record in self.result["healer"]["table"]:
            name = record["name"]
            if name == self.result["overall"]["playerID"]:
                heal = record["healEff"]
                break
        scoreA1 = self.scaleScore(heal, std)
        self.result["score"]["scoreA1"] = scoreA1
        # 盾数量A2
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0], [44, 3], [54, 6], [71, 10]],
                                  '桑乔': [[0, 0], [56, 3], [64, 6], [74, 10]],
                                  '悉达罗摩': [[0, 0], [84, 3], [109, 6], [138, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [45, 3], [92, 6], [141, 10]],
                                  '乌蒙贵': [[0, 0], [47, 3], [81, 6], [113, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0], [72, 3], [80, 6], [104, 10]],
                                  '桑乔': [[0, 0], [62, 3], [72, 6], [88, 10]],
                                  '悉达罗摩': [[0, 0], [105, 3], [145, 6], [199, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [46, 3], [115, 6], [168, 10]],
                                  '乌蒙贵': [[0, 0], [100, 3], [121, 6], [139, 10]]}}
        std = stdTable[map][boss]
        numShield = self.result["skill"]["meihua"]["num"]
        scoreA2 = self.scaleScore(numShield, std)
        self.result["score"]["scoreA2"] = scoreA2
        # 徵数量A3
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0], [10, 3], [152, 6], [212, 10]],
                                  '桑乔': [[0, 0], [80, 3], [307, 6], [464, 10]],
                                  '悉达罗摩': [[0, 0], [173, 3], [349, 6], [472, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [65, 3], [560, 6], [889, 10]],
                                  '乌蒙贵': [[0, 0], [93, 3], [490, 6], [771, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0], [44, 3], [252, 6], [400, 10]],
                                  '桑乔': [[0, 0], [258, 3], [667, 6], [987, 10]],
                                  '悉达罗摩': [[0, 0], [104, 3], [498, 6], [708, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [234, 3], [863, 6], [1171, 10]],
                                  '乌蒙贵': [[0, 0], [288, 3], [1040, 6], [1465, 10]]}}
        std = stdTable[map][boss]
        numZhi = self.result["skill"]["zhi"]["num"]
        scoreA3 = self.scaleScore(numZhi, std)
        self.result["score"]["scoreA3"] = scoreA3
        # 宫数量A4
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0]],
                                  '桑乔': [[0, 0]],
                                  '悉达罗摩': [[0, 0]],
                                  '尤珈罗摩': [[0, 0], [150, 3], [345, 6], [570, 10]],
                                  '月泉淮': [[0, 0]],
                                  '乌蒙贵': [[0, 0]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0]],
                                  '桑乔': [[0, 0]],
                                  '悉达罗摩': [[0, 0]],
                                  '尤珈罗摩': [[0, 0], [221, 3], [658, 6], [1084, 10]],
                                  '月泉淮': [[0, 0]],
                                  '乌蒙贵': [[0, 0]]}}
        std = stdTable[map][boss]
        numGong = self.result["skill"]["gong"]["num"]
        scoreA4 = self.scaleScore(numGong, std)
        self.result["score"]["scoreA4"] = scoreA4
        # A类总计

        scoreAT1 = scoreA1 * 10
        scoreAT2 = (scoreA2 + scoreA3) * 5
        scoreAT3 = (scoreA1 * 2 + scoreA2 + scoreA3) * 3
        scoreAT4 = (scoreA1 + scoreA4) * 6
        scoreA = max(scoreAT1, scoreAT2, scoreAT3, scoreAT4)
        scoreA = min(scoreA, 100)
        scoreA = roundCent(scoreA, 1)
        self.result["score"]["scoreA"] = scoreA

        # 统计分B
        # 盾覆盖率B1
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0], [0.42, 3], [0.45, 6], [0.6, 10]],
                                  '桑乔': [[0, 0], [0.7, 3], [0.71, 6], [0.83, 10]],
                                  '悉达罗摩': [[0, 0], [0.35, 3], [0.45, 6], [0.53, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [0.1, 3], [0.36, 6], [0.59, 10]],
                                  '乌蒙贵': [[0, 0], [0.27, 3], [0.36, 6], [0.49, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0], [0.47, 3], [0.56, 6], [0.71, 10]],
                                  '桑乔': [[0, 0], [0.74, 3], [0.77, 6], [0.88, 10]],
                                  '悉达罗摩': [[0, 0], [0.49, 3], [0.54, 6], [0.65, 10]],
                                  '尤珈罗摩': [[0, 0]],
                                  '月泉淮': [[0, 0], [0.19, 3], [0.32, 6], [0.45, 10]],
                                  '乌蒙贵': [[0, 0], [0.44, 3], [0.5, 6], [0.6, 10]]}}
        std = stdTable[map][boss]
        coverShield = self.result["skill"]["meihua"]["cover"]
        scoreB1 = self.scaleScore(coverShield, std)
        self.result["score"]["scoreB1"] = scoreB1
        # HOT覆盖率B2
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0]],
                                  '桑乔': [[0, 0]],
                                  '悉达罗摩': [[0, 0]],
                                  '尤珈罗摩': [[0, 0], [0.31, 3], [0.42, 6], [0.53, 10]],
                                  '月泉淮': [[0, 0]],
                                  '乌蒙贵': [[0, 0]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0]],
                                  '桑乔': [[0, 0]],
                                  '悉达罗摩': [[0, 0]],
                                  '尤珈罗摩': [[0, 0], [0.58, 3], [0.63, 6], [0.7, 10]],
                                  '月泉淮': [[0, 0]],
                                  '乌蒙贵': [[0, 0]]}}
        std = stdTable[map][boss]
        coverHot = (self.result["skill"]["shang"]["cover"] + self.result["skill"]["jue"]["cover"]) / 2
        scoreB2 = self.scaleScore(coverHot, std)
        self.result["score"]["scoreB2"] = scoreB2
        # B类总计
        scoreBT1 = scoreB1 * 10
        scoreBT2 = scoreB2 * 10
        scoreB = max(scoreBT1, scoreBT2)
        scoreB = min(scoreB, 100)
        scoreB = roundCent(scoreB, 1)
        self.result["score"]["scoreB"] = scoreB

        # 操作分C
        # 战斗效率C1
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[0, 0], [0.52, 3], [0.58, 6], [0.73, 10]],
                                  '桑乔': [[0, 0], [0.46, 3], [0.57, 6], [0.71, 10]],
                                  '悉达罗摩': [[0, 0], [0.59, 3], [0.64, 6], [0.68, 10]],
                                  '尤珈罗摩': [[0, 0], [0.53, 3], [0.62, 6], [0.72, 10]],
                                  '月泉淮': [[0, 0], [0.56, 3], [0.63, 6], [0.75, 10]],
                                  '乌蒙贵': [[0, 0], [0.47, 3], [0.55, 6], [0.66, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[0, 0], [0.57, 3], [0.63, 6], [0.76, 10]],
                                  '桑乔': [[0, 0], [0.4, 3], [0.5, 6], [0.61, 10]],
                                  '悉达罗摩': [[0, 0], [0.55, 3], [0.63, 6], [0.72, 10]],
                                  '尤珈罗摩': [[0, 0], [0.68, 3], [0.72, 6], [0.79, 10]],
                                  '月泉淮': [[0, 0], [0.54, 3], [0.58, 6], [0.71, 10]],
                                  '乌蒙贵': [[0, 0], [0.39, 3], [0.5, 6], [0.65, 10]]}}
        std = stdTable[map][boss]
        efficiency = self.result["skill"]["general"]["efficiency"]
        scoreC1 = self.scaleScore(efficiency, std)
        self.result["score"]["scoreC1"] = scoreC1
        # 盾延迟C2
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[500, 0], [368, 3], [261, 6], [174, 10]],
                                  '桑乔': [[500, 0], [462, 3], [346, 6], [236, 10]],
                                  '悉达罗摩': [[500, 0], [424, 3], [329, 6], [235, 10]],
                                  '尤珈罗摩': [[500, 0]],
                                  '月泉淮': [[500, 0], [352, 3], [226, 6], [215, 10]],
                                  '乌蒙贵': [[700, 0], [499, 3], [347, 6], [227, 10]]},
                     '25人英雄雷域大泽': {'巨型尖吻凤': [[500, 0], [343, 3], [302, 6], [201, 10]],
                                  '桑乔': [[500, 0], [376, 3], [319, 6], [270, 10]],
                                  '悉达罗摩': [[500, 0], [353, 3], [307, 6], [246, 10]],
                                  '尤珈罗摩': [[500, 0]],
                                  '月泉淮': [[500, 0], [356, 3], [285, 6], [168, 10]],
                                  '乌蒙贵': [[500, 0], [445, 3], [374, 6], [301, 10]]}}
        std = stdTable[map][boss]
        delayShield = self.result["skill"]["meihua"]["delay"]
        scoreC2 = self.scaleScore(delayShield, std)
        self.result["score"]["scoreC2"] = scoreC2
        # 徵延迟C3
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[300, 0], [123, 3], [110, 6], [27, 10]],
                                  '桑乔': [[300, 0], [177, 3], [132, 6], [11, 10]],
                                  '悉达罗摩': [[300, 0], [118, 3], [109, 6], [55, 10]],
                                  '尤珈罗摩': [[300, 0], [95, 3], [73, 6], [30, 10]],
                                  '月泉淮': [[300, 0], [108, 3], [96, 6], [24, 10]],
                                  '乌蒙贵': [[300, 0], [152, 3], [132, 6], [76, 10]]},
                    '25人英雄雷域大泽': {'巨型尖吻凤': [[300, 0], [155, 3], [112, 6], [37, 10]],
                                  '桑乔': [[300, 0], [135, 3], [102, 6], [65, 10]],
                                  '悉达罗摩': [[300, 0], [128, 3], [98, 6], [55, 10]],
                                  '尤珈罗摩': [[300, 0]],
                                  '月泉淮': [[300, 0], [109, 3], [75, 6], [39, 10]],
                                  '乌蒙贵': [[300, 0], [135, 3], [127, 6], [61, 10]]}}
        std = stdTable[map][boss]
        delayZhi = self.result["skill"]["zhi"]["delay"]
        scoreC3 = self.scaleScore(delayZhi, std)
        self.result["score"]["scoreC3"] = scoreC3
        # 宫延迟C4
        stdTable = {'25人普通雷域大泽': {'巨型尖吻凤': [[1, 0]],
                                  '桑乔': [[1, 0]],
                                  '悉达罗摩': [[1, 0]],
                                  '尤珈罗摩': [[500, 0], [344, 3], [279, 6], [217, 10]],
                                  '月泉淮': [[1, 0]],
                                  '乌蒙贵': [[1, 0]]},
                                  '25人英雄雷域大泽': {'巨型尖吻凤': [[1, 0]],
                                  '桑乔': [[1, 0]],
                                  '悉达罗摩': [[1, 0]],
                                  '尤珈罗摩': [[500, 0], [284, 3], [247, 6], [202, 10]],
                                  '月泉淮': [[1, 0]],
                                  '乌蒙贵': [[1, 0]]}}
        std = stdTable[map][boss]
        delayGong = self.result["skill"]["gong"]["delay"]
        scoreC4 = self.scaleScore(delayGong, std)
        self.result["score"]["scoreC4"] = scoreC4
        # C类总计
        scoreCT1 = scoreC1 * 10
        scoreCT2 = (scoreC2 + scoreC3) * 5
        scoreCT3 = (scoreC1 * 2 + scoreC2 + scoreC3) * 3
        scoreCT4 = (scoreC1 + scoreC4) * 6
        scoreC = max(scoreCT1, scoreCT2, scoreCT3, scoreCT4)
        scoreC = min(scoreC, 100)
        scoreC = roundCent(scoreC, 1)
        self.result["score"]["scoreC"] = scoreC

        # 总分
        scoreT1 = scoreA * 0.1 + (scoreA + scoreB + scoreC) * 0.3
        scoreT2 = scoreB * 0.1 + (scoreA + scoreB + scoreC) * 0.3
        scoreT3 = scoreC * 0.1 + (scoreA + scoreB + scoreC) * 0.3
        score = max(scoreT1, scoreT2, scoreT3)
        score = roundCent(score, 1)
        self.result["score"]["sum"] = score

    def getHash(self):
        '''
        获取战斗结果的哈希值.
        '''
        hashStr = ""
        nameList = []
        for key in self.bld.info.player:
            nameList.append(self.bld.info.player[key].name)
        nameList.sort()
        battleMinute = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        hashStr = battleMinute + self.result["overall"]["map"] + "".join(nameList)
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        '''
        准备上传复盘结果，并向服务器上传.
        '''
        if "beta" in EDITION:
            return
        upload = {}
        upload["server"] = self.result["overall"]["server"]
        upload["id"] = self.result["overall"]["playerID"]
        upload["occ"] = "xiangzhi"
        upload["score"] = self.result["score"]["sum"]
        upload["battledate"] = time.strftime("%Y-%m-%d", time.localtime(self.result["overall"]["battleTime"]))
        upload["mapdetail"] = self.result["overall"]["map"]
        upload["boss"] = self.result["overall"]["boss"]
        upload["statistics"] = self.result
        upload["public"] = self.public
        upload["edition"] = EDITION
        upload["editionfull"] = parseEdition(EDITION)
        upload["replayedition"] = self.result["overall"]["edition"]
        upload["userid"] = self.config.item["user"]["uuid"]
        upload["battletime"] = self.result["overall"]["battleTime"]
        upload["submittime"] = int(time.time())
        upload["hash"] = self.getHash()

        Jdata = json.dumps(upload)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        # print(jparse)
        resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadReplayPro', data=jparse)
        res = json.load(resp)
        # print(res)
        if res["result"] != "fail":
            self.result["overall"]["shortID"] = res["shortID"]
        else:
            self.result["overall"]["shortID"] = "数据保存出错"
        return res

    def replay(self):
        '''
        开始奶歌复盘pro分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()
        self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", bossBh=None, startTime=0, finalTime=0, win=0):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - myname: 需要复盘的奶歌名.
        - bossBh: BOSS施放的技能列表类，用于生成时间轴.
        - startTime: 演员复盘推断得到的战斗开始时间.
        - finalTime: 演员复盘推断得到的战斗结束时间.
        '''
        self.win = win
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.myname = myname
        self.bossBh = bossBh
        self.failThreshold = config.item["actor"]["failthreshold"]
        self.mask = config.item["general"]["mask"]
        self.public = config.item["xiangzhi"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.startTime = startTime
        self.finalTime = finalTime

        self.result = {}
        self.haste = config.item["xiangzhi"]["speed"]


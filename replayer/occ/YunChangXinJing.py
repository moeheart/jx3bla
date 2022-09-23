# Created by moeheart at 04/19/2022
# 奶秀复盘，用于奶秀复盘的生成，展示

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

        xlwlDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        xlwlDisplayer.setImage("897", "翔鸾舞柳")
        xlwlDisplayer.setDouble("rate", "数量", "xlwl", "num", "numPerSec")
        xlwlDisplayer.setSingle("delay", "延迟", "xlwl", "delay")
        xlwlDisplayer.setSingle("int", "持续HPS", "xlwl", "HPS")
        xlwlDisplayer.setSingle("int", "首跳HPS", "xlwl", "shuangluanHPS")
        xlwlDisplayer.setSingle("percent", "覆盖率", "xlwl", "cover")
        xlwlDisplayer.export_image(frame5, 1)

        sydhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        sydhDisplayer.setImage("913", "上元点鬟")
        sydhDisplayer.setDouble("rate", "数量", "sydh", "num", "numPerSec")
        sydhDisplayer.setSingle("delay", "延迟", "sydh", "delay")
        sydhDisplayer.setSingle("int", "HPS", "sydh", "HPS")
        sydhDisplayer.setSingle("int", "首跳HPS", "sydh", "shuangluanHPS")
        sydhDisplayer.setSingle("percent", "覆盖率", "sydh", "cover")
        sydhDisplayer.export_image(frame5, 2)

        wmhmDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        wmhmDisplayer.setImage("900", "王母挥袂")
        wmhmDisplayer.setDouble("rate", "数量", "wmhm", "num", "numPerSec")
        wmhmDisplayer.setSingle("int", "HPS", "wmhm", "HPS")
        wmhmDisplayer.setSingle("int", "辞致HPS", "wmhm", "cizhiHPS")
        wmhmDisplayer.setSingle("percent", "有效比例", "wmhm", "effRate")
        wmhmDisplayer.export_image(frame5, 3)

        fxdaDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        fxdaDisplayer.setImage("1507", "风袖低昂")
        fxdaDisplayer.setDouble("rate", "数量", "fxda", "num", "numPerSec")
        fxdaDisplayer.setSingle("int", "HPS", "fxda", "HPS")
        fxdaDisplayer.setSingle("int", "晚晴HPS", "fxda", "wanqingHPS")
        fxdaDisplayer.setSingle("percent", "有效比例", "fxda", "effRate")
        fxdaDisplayer.export_image(frame5, 4)

        jwfhDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        jwfhDisplayer.setImage("13417", "九微飞花")
        jwfhDisplayer.setDouble("rate", "数量", "jwfh", "num", "numPerSec")
        jwfhDisplayer.setSingle("int", "HPS", "jwfh", "HPS")
        jwfhDisplayer.setSingle("percent", "有效比例", "jwfh", "effRate")
        jwfhDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "垂眉HPS", "xlwl", "chuimeiHPS")
        info1Displayer.setSingle("int", "双鸾次数", "xlwl", "shuangluanNum")
        info1Displayer.setDouble("rate", "跳珠数量", "tzhy", "num", "numPerSec")
        info1Displayer.setSingle("int", "跳珠HPS", "tzhy", "HPS")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
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

class YunChangXinJingReplayer(HealerReplay):
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

        xlwlSkill = SkillHealCounter("554", self.startTime, self.finalTime, self.haste)  # 翔鸾舞柳
        sydhSkill = SkillHealCounter("556", self.startTime, self.finalTime, self.haste)  # 上元点鬟
        tzhySkill = SkillHealCounter("566", self.startTime, self.finalTime, self.haste)  # 跳珠憾玉
        wmhmSkill = SkillHealCounter("2976", self.startTime, self.finalTime, self.haste)  # 王母挥袂

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        self.skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
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
                     [None, "特效腰坠", ["yaozhui"], "3414", False, 0, False, True, 180, 1]
                     ]

        self.initSecondState()

        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计

        # 技能统计

        # fxdaSkill = SkillHealCounter("555", self.startTime, self.finalTime, self.haste)  # 风袖低昂
        hxpySkill = SkillHealCounter("6250", self.startTime, self.finalTime, self.haste)  # 回雪飘摇
        jwfhSkill = SkillHealCounter("24990", self.startTime, self.finalTime, self.haste)  # 九微飞花
        xiangwuBuff = SkillHealCounter("680", self.startTime, self.finalTime, self.haste)  # 翔舞
        shangyuanBuff = SkillHealCounter("681", self.startTime, self.finalTime, self.haste)  # 上元
        hxpyDict = BuffCounter("?", self.startTime, self.finalTime)  # 用buff类型来记录回雪飘摇的具体时间
        xiangwuDict = {}  # 翔舞
        shangyuanDict = {}  # 上元

        for line in self.bld.info.player:
            xiangwuDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 翔舞
            shangyuanDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 上元
            battleStat[line] = [0]

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

        hxpyTime = getLength(13, self.haste)  # TODO 判断瑰姿

        jwfhWatchSkill = SkillCounterAdvance(self.skillInfo[self.gcdSkillIndex["24990"]], self.startTime, self.finalTime,
                                             self.haste)

        self.unimportantSkill += ["6633", "6634", "6635",  # 翔舞判定
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

            self.eventInSecondState(event)

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # 所有治疗技能都不计算化解.
                    continue

                    # 统计自身技能使用情况.
                    # if event.caster == self.mykey and event.scheme == 1 and event.id in xiangZhiUnimportant and event.heal != 0:
                    #     print(event.id, event.time)

                if event.caster == self.mykey and event.scheme == 1:
                    # 根据技能表进行自动处理
                    if event.id in self.gcdSkillIndex:
                        # 在gcd技能生效时重置回雪
                        if hxpyLocalNum > 0:
                            hxpyCastNum += 1
                            hxpyCastList.append(hxpyLocalNum)
                        hxpyLocalNum = 0
                        if hxpySingleNum > 0:
                            hxpySingleList.append(hxpySingleNum)
                        hxpySingleNum = 0
                    elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                        desc = ""
                        index = self.nonGcdSkillIndex[event.id]
                        line = self.skillInfo[index]
                        self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                        skillObj = line[0]
                        if skillObj is not None:
                            skillObj.recordSkill(event.time, event.heal, event.healEff, self.ss.timeEnd, delta=-1)

                    # 统计不计入时间轴的治疗量
                    if event.id in ["6209"]:  # 辞致
                        cizhiHeal += event.healEff
                    if event.id in ["21270", "21274", "21275", "21276"]:  # 垂眉
                        chuimeiHeal += event.healEff
                    if event.id in ["24992", "24993"]:  # 九微飞花
                        jwfhSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        if event.time - jwfhLast > 5000:
                            # 记录九微飞花
                            jwfhWatchSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
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
                        xiangwuBuff.recordSkill(event.time, event.heal, event.healEff)
                    if event.id in ["681"]:  # 上元
                        shangyuanBuff.recordSkill(event.time, event.heal, event.healEff)

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.bld.info.player:
                        battleStat[event.caster][0] += event.damageEff

            elif event.dataType == "Buff":
                if event.id in ["12768"] and event.stack == 1 and event.target == self.mykey:  # cw特效
                    self.bh.setSpecialSkill(event.id, "cw特效", "14402",
                                       event.time, 0, "触发cw特效")
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
                    if hxpyLocalNum > 0:
                        hxpyCastNum += 1
                        hxpyCastList.append(hxpyLocalNum)
                    hxpyLocalNum = 0
                    if hxpySingleNum > 0:
                        hxpySingleList.append(hxpySingleNum)
                    hxpySingleNum = 0
                    # print("[HxpyCast]", event.time, event.id)

        # 记录最后一个技能
        self.completeSecondState()
        
        hxpyCastList.append(hxpyLocalNum)
        hxpySingleList.append(hxpySingleNum)

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
            liveCount = self.battleDict[key].buffTimeIntegral()  # 存活时间比例
            if self.battleDict[key].sumTime() - liveCount < 8000:  # 脱战缓冲时间
                liveCount = self.battleDict[key].sumTime()
            self.battleTimeDict[key] = liveCount
            self.sumPlayer += liveCount / self.battleDict[key].sumTime()

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   }
            self.result["dps"]["table"].append(res)

        hxpyDict.shrink(100)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100

        self.result["skill"] = {}

        # 回雪飘摇
        self.calculateSkillInfoDirect("hxpy", hxpySkill)

        # 翔鸾舞柳
        self.calculateSkillInfoDirect("xlwl", xiangwuBuff)
        xlwlSkill = self.skillInfo[self.gcdSkillIndex["554"]][0]
        self.result["skill"]["xlwl"]["shuangluanHPS"] = int(shuangluanHeal1 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xlwl"]["delay"] = int(xlwlSkill.getAverageDelay())
        num = 0
        sum = 0
        xiangwuHeat = []
        for key in xiangwuDict:
            singleDict = xiangwuDict[key]
            num += self.battleTimeDict[key]
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
        self.calculateSkillInfoDirect("sydh", shangyuanBuff)
        sydhSkill = self.skillInfo[self.gcdSkillIndex["556"]][0]
        self.result["skill"]["sydh"]["shuangluanHPS"] = int(shuangluanHeal3 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["sydh"]["delay"] = int(sydhSkill.getAverageDelay())
        num = 0
        sum = 0
        shangyuanHeat = []
        for key in shangyuanDict:
            singleDict = shangyuanDict[key]
            num += self.battleTimeDict[key]
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
        wmhmSkill = self.calculateSkillInfo("wmhm", "2976")
        self.result["skill"]["wmhm"]["cizhiHPS"] = int(cizhiHeal / self.result["overall"]["sumTime"] * 1000)

        # 风袖
        fxdaSkill = self.calculateSkillInfo("fxda", "555")
        self.result["skill"]["fxda"]["wanqingHPS"] = int(wanqingHeal / self.result["overall"]["sumTime"] * 1000)
        # 九微飞花
        jwfhSkill = self.calculateSkillInfo("jwfh", "24990")
        # 杂项
        self.result["skill"]["xlwl"]["chuimeiHPS"] = int(chuimeiHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xlwl"]["shuangluanNum"] = xlwlSkill.getNum() + sydhSkill.getNum()  # 注意这两个放在翔舞底下，但是实际上是翔舞+上元的数据
        self.result["skill"]["tzhy"] = {}
        self.result["skill"]["tzhy"]["num"] = tzhySkill.getNum()
        self.result["skill"]["tzhy"]["numPerSec"] = roundCent(
            self.result["skill"]["tzhy"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = tzhySkill.getHealEff()
        self.result["skill"]["tzhy"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)

        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["efficiencyNonGcd"] = self.bh.getNormalEfficiency("healer", hxpyDict.log)
        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)
        self.result["replay"]["hxpy"] = hxpyDict.log
        self.result["replay"]["heat"] = {"interval": 500, "timeline": [xiangwuHeat, shangyuanHeat]}

        self.specialKey = {"hxpy-numPerSec": 20, "general-efficiency": 20, "healer-healEff": 20, "xlwl-cover": 10, "sydh-cover": 10}
        self.markedSkill = ["555", "568", "18221"]
        self.outstandingSkill = [jwfhWatchSkill]
        self.calculateSkillOverall()

        # 计算专案组的心法部分.
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
        self.haste = config.item["yunchang"]["speed"]
        self.public = config.item["yunchang"]["public"]
        self.occ = "yunchangxinjing"
        self.occCode = "5h"
        self.occPrint = "奶秀"


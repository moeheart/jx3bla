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

class LingSuReplayer(ReplayerBase):
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

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "灵素复盘 v%s"%EDITION
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
        self.result["overall"]["win"] = self.win

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

        self.peiwuCounter = {}
        for key in self.bld.info.player:
            self.peiwuCounter[key] = ShieldCounterNew("20877", self.startTime, self.finalTime)

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
                if event.id in ["20877"] and event.caster == self.mykey and event.target in self.bld.info.player:  # buff配伍
                    self.peiwuCounter[event.target].setState(event.time, event.stack)
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
        # TODO 实现
        self.result["equip"] = {"available": 0}
        if self.bld.info.player[self.mykey].equip != {} and "beta" not in EDITION:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, "212h")
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
            if not self.config.item["lingsu"]["speedforce"]:
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
        skillLog = []

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
        peiwuRateDict = {}  # 配伍覆盖率
        piaohuangNumDict = {}  # 飘黄触发次数
        battleTimeDict = {}  # 进战时间
        sumPlayer = 0  # 玩家数量

        # 技能统计
        lszhSkill = SkillHealCounter("28083", self.startTime, self.finalTime, self.haste)  # 灵素中和
        bzhfSkill = SkillHealCounter("27622", self.startTime, self.finalTime, self.haste)  # 白芷含芳
        cshxSkill = SkillHealCounter("27633", self.startTime, self.finalTime, self.haste)  # 赤芍寒香
        # dgsnSkill = SkillCounterAdvance("27624", self.startTime, self.finalTime, self.haste)  # 当归四逆
        # qqhhSkill = SkillCounterAdvance("28620", self.startTime, self.finalTime, self.haste)  # 七情和合
        qczlSkill = SkillHealCounter("27669", self.startTime, self.finalTime, self.haste)  # 青川濯莲
        ygzxSkill = SkillHealCounter("27531", self.startTime, self.finalTime, self.haste)  # 银光照雪
        cshxBuff = SkillHealCounter("20070", self.startTime, self.finalTime, self.haste)  # 赤芍寒香  (20819素柯)

        qianzhiDict = BuffCounter("20075", self.startTime, self.finalTime)  # 千枝buff
        qingchuanDict = BuffCounter("20800", self.startTime, self.finalTime)  # 青川buff
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风

        battleDict = self.battleDict
        for line in self.bld.info.player:
            piaohuangNumDict[line] = 0

        lastSkillTime = self.startTime

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

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)
        ss2 = SingleSkill(self.startTime, self.haste)  # 存一个技能, 在只有两个技能相同时不合并.

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],
                     [bzhfSkill, "白芷含芳", ["27622"], "15411", True, 24, False, True, 0, 1],
                     [cshxSkill, "赤芍寒香", ["27633"], "15414", True, 0, False, True, 0, 1],
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
                    ]

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            if line[0] is None:
                skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste)
            if line[1] == "当归四逆":
                dgsnSkill = skillInfo[i][0]
            elif line[1] == "七情和合":
                qqhhSkill = skillInfo[i][0]
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i
        yzInfo = [None, "特效腰坠", ["0"], "3414", False, 0, False, True, 180, 1]
        yzSkill = SkillCounterAdvance(yzInfo, self.startTime, self.finalTime, self.haste)
        yzInfo[0] = yzSkill

        # 监控cd用的类
        qczlWatchSkill = SkillCounterAdvance(skillInfo[gcdSkillIndex["27669"]], self.startTime, self.finalTime, self.haste)
        dgsnWatchSkill = SkillCounterAdvance(skillInfo[gcdSkillIndex["27624"]], self.startTime, self.finalTime,
                                             self.haste)

        xiangZhiUnimportant = ["4877",  # 水特效作用
                               "25682", "25683", "25684", "25685", "25686", "24787", "24788", "24789", "24790", # 破招
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
                               ## 灵素分割线
                               "28083", "28602", "28734", "28733", "28082", "28757",  # 灵素中和
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

                    if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey:
                        # 打印所有有治疗量的技能，以进行整理
                        # print("[Heal]", event.id, event.heal)
                        pass

                    if event.caster == self.mykey and event.scheme == 1:
                        # 根据技能表进行自动处理
                        if event.id in gcdSkillIndex:
                            ss.initSkill(event)
                            index = gcdSkillIndex[event.id]
                            line = skillInfo[index]
                            ss.analyseSkill(event, line[5], line[0], tunnel=line[6], hasteAffected=line[7])
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
                            # 特殊处理当归四逆
                            if event.id == "27624":
                                if event.time - dgsnLast > 1000:
                                    dgsnWatchSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                                dgsnLast = event.time

                        # 处理特殊技能
                        elif event.id in nonGcdSkillIndex:  # 特殊技能
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
                            if event.id == "27531" and bh.log["special"] != [] and bh.log["special"][-1]["skillid"] == "27531" and event.time - bh.log["special"][-1]["start"] < 100:
                                record = False
                            if record:
                                index = nonGcdSkillIndex[event.id]
                                line = skillInfo[index]
                                bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                                index = nonGcdSkillIndex[event.id]
                                line = skillInfo[index]
                                skillObj = line[0]
                                if skillObj is not None:
                                    skillObj.recordSkill(event.time, event.heal, event.healEff, ss.timeEnd, delta=-1)
                        # 无法分析的技能
                        elif event.id not in xiangZhiUnimportant:
                            pass
                            # print("[LingSuNonRec]", event.time, event.id, event.heal, event.healEff)

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
                            cshxBuff.recordSkill(event.time, event.heal, event.healEff, ss.timeEnd)

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

                    # # 尝试统计化解
                    # if event.target in self.bld.info.player:
                    #     absorb = int(event.fullResult.get("9", 0))
                    #     if absorb > 0:
                    #         meihua = self.peiwuCounter[event.target].checkState(event.time - 100)
                    #         nongmei = nongmeiDict[event.target].checkState(event.time - 100)
                    #         if meihua or nongmei:
                    #             numAbsorb2 += absorb

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
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                    yzSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                if event.id in ["21803"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    bh.setSpecialSkill(event.id, "cw特效", "15888",
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
                        qczlWatchSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
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

                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

            num += 1

        # 记录最后一个技能
        if ss.skill != "0":
            index = gcdSkillIndex[ss.skill]
            line = skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")

        zyhrNum.append(len(zyhrList))
        zyhrNum = zyhrNum[1:]

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]

        # 计算战斗效率等统计数据，TODO 扩写
        # skillCounter = SkillLogCounter(skillLog, self.startTime, self.finalTime, self.haste)
        # skillCounter.analysisSkillData()
        # sumBusyTime = skillCounter.sumBusyTime
        # sumSpareTime = skillCounter.sumSpareTime
        # spareRate = sumSpareTime / (sumBusyTime + sumSpareTime + 1e-10)

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

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

        # 计算等效伤害
        numdam1 = 0
        numdam2 = 0
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0]
            numdam1 += line[1]
            numdam2 += line[2]

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
                else:
                    res["hps"] = 0
                if player in self.act.ahps["player"]:
                    res["ahps"] = int(self.act.ahps["player"][player]["hps"])
                else:
                    res["ahps"] = 0
                if player in self.act.ohps["player"]:
                    res["ohps"] = int(self.act.ohps["player"][player]["hps"])
                else:
                    res["ohps"] = 0
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
        overallShieldHeat = {"interval": 500, "timeline": []}
        for key in self.peiwuCounter:
            liveCount = battleDict[key].buffTimeIntegral()  # 存活时间比例
            if battleDict[key].sumTime() - liveCount < 8000:  # 脱战缓冲时间
                liveCount = battleDict[key].sumTime()
            battleTimeDict[key] = liveCount
            sumPlayer += liveCount / battleDict[key].sumTime()
            # # 过滤老板，T奶，自己
            # if key not in damageDict or damageDict[key] / self.result["overall"]["sumTime"] * 1000 < 10000:
            #     continue
            # if getOccType(occDetailList[key]) == "healer":
            #     continue
            # if getOccType(occDetailList[key]) == "tank" and not self.config.xiangzhiCalTank:
            #     continue
            # if key == self.mykey:
            #     continue
            time1 = self.peiwuCounter[key].buffTimeIntegral()
            timeAll = liveCount
            peiwuRateDict[key] = time1 / (timeAll + 1e-10)

        for line in damageList:
            if line[0] not in peiwuRateDict:
                continue
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   "PeiwuRate": roundCent(peiwuRateDict[line[0]]),
                   "PiaohuangNum": piaohuangNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        # 计算配伍覆盖率
        numRate = 0
        sumRate = 0
        for key in peiwuRateDict:
            numRate += battleTimeDict[key]
            sumRate += peiwuRateDict[key] * battleTimeDict[key]
        overallRate = sumRate / (numRate + 1e-10)

        # 计算飘黄次数
        numPiaoHuang = 0
        for key in piaohuangNumDict:
            numPiaoHuang += piaohuangNumDict[key]

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 灵素中和
        self.result["skill"]["lszh"] = {}
        self.result["skill"]["lszh"]["num"] = lszhSkill.getNum()
        self.result["skill"]["lszh"]["numPerSec"] = roundCent(
            self.result["skill"]["lszh"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = lszhSkill.getHealEff()
        self.result["skill"]["lszh"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        # 白芷含芳
        self.result["skill"]["bzhf"] = {}
        self.result["skill"]["bzhf"]["num"] = bzhfSkill.getNum()
        self.result["skill"]["bzhf"]["numPerSec"] = roundCent(
            self.result["skill"]["bzhf"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["bzhf"]["delay"] = int(bzhfSkill.getAverageDelay())
        effHeal = bzhfSkill.getHealEff()
        self.result["skill"]["bzhf"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["bzhf"]["effRate"] = effHeal / (bzhfSkill.getHeal() + 1e-10)
        # 赤芍寒香
        self.result["skill"]["cshx"] = {}
        self.result["skill"]["cshx"]["num"] = cshxBuff.getNum()
        self.result["skill"]["cshx"]["numPerSec"] = roundCent(
            self.result["skill"]["cshx"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = cshxBuff.getHealEff()
        self.result["skill"]["cshx"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["cshx"]["skillNum"] = cshxSkill.getNum()
        self.result["skill"]["cshx"]["delay"] = int(cshxSkill.getAverageDelay())
        effHeal = cshxSkill.getHealEff()
        self.result["skill"]["cshx"]["skillHPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        # 当归四逆
        self.result["skill"]["dgsn"] = {}
        self.result["skill"]["dgsn"]["num"] = dgsnSkill.getNum()
        self.result["skill"]["dgsn"]["numPerSec"] = roundCent(
            self.result["skill"]["dgsn"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["dgsn"]["delay"] = int(dgsnSkill.getAverageDelay())
        effHeal = dgsnSkill.getHealEff()
        self.result["skill"]["dgsn"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["dgsn"]["effRate"] = roundCent(effHeal / (dgsnSkill.getHeal() + 1e-10))
        # 银光照雪
        self.result["skill"]["ygzx"] = {}
        self.result["skill"]["ygzx"]["num"] = ygzxSkill.getNum()
        self.result["skill"]["ygzx"]["numPerSec"] = roundCent(
            self.result["skill"]["ygzx"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = ygzxSkill.getHealEff()
        self.result["skill"]["ygzx"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["ygzx"]["effRate"] = roundCent(effHeal / (ygzxSkill.getHeal() + 1e-10))
        # 青川濯莲
        self.result["skill"]["qczl"] = {}
        self.result["skill"]["qczl"]["num"] = qczlSkill.getNum()
        self.result["skill"]["qczl"]["numPerSec"] = roundCent(
            self.result["skill"]["qczl"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = qczlSkill.getHealEff()
        self.result["skill"]["qczl"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["qczl"]["effRate"] = roundCent(effHeal / (qczlSkill.getHeal() + 1e-10))
        # 杂项
        self.result["skill"]["qqhh"] = {}
        self.result["skill"]["qqhh"]["num"] = qqhhSkill.getNum()
        effHeal = qqhhSkill.getHealEff()
        self.result["skill"]["qqhh"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["qqhh"]["effRate"] = roundCent(effHeal / (qqhhSkill.getHeal() + 1e-10))
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["PeiwuRate"] = overallRate
        self.result["skill"]["general"]["PiaohuangNum"] = numPiaoHuang
        self.result["skill"]["general"]["PeiwuDPS"] = int(numdam1 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["PiaohuangDPS"] = int(numdam2 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        self.result["replay"]["qianzhi"] = qianzhiDict.log
        self.result["replay"]["qingchuan"] = qingchuanDict.log
        self.result["replay"]["yaoxing"] = yaoxingInfer
        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["healEff"] = myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["ohps"] = myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = myHealStat.get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = myHealStat.get("ahps", 0)

        self.getRankFromStat("lingsu")
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        specialKey = {"lszh-numPerSec": 20, "general-efficiency": 20, "healer-healEff": 20}
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
        gcd = self.result["skill"]["general"]["efficiency"]
        gcdRank = self.result["rank"]["general"]["efficiency"]["percent"]
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
        for id in ["28620", "27531", "28756", "28533"]:
            if id in nonGcdSkillIndex:
                scCandidate.append(skillInfo[nonGcdSkillIndex[id]][0])
            else:
                scCandidate.append(skillInfo[gcdSkillIndex[id]][0])
        scCandidate.append(yzSkill)
        scCandidate.append(qczlWatchSkill)
        scCandidate.append(dgsnWatchSkill)

        rateSum = 0
        rateNum = 0
        numAll = []
        sumAll = []
        skillAll = []
        for skillObj in scCandidate:
            num = skillObj.getNum()
            sum = skillObj.getMaxPossible()
            # if sum < num:
            #     sum = num
            skill = skillObj.name
            if skill in ["特效腰坠", "百药宣时", "青圃着尘"] and num == 0:
                continue
            # TODO 通过奇穴和装备辅助判断
            # TODO 修改春泥这类既统计治疗又统计cd的技能
            rateNum += 1
            rateSum += min(num / (sum + 1e-10), 1)
            numAll.append(num)
            sumAll.append(sum)
            skillAll.append(skill)
        rate = roundCent(rateSum / (rateNum + 1e-10), 4)
        res = {"code": 13, "skill": skillAll, "num": numAll, "sum": sumAll, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 25, 0)
        self.result["review"]["content"].append(res)

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
        time = roundCent(qianzhiDict.buffTimeIntegral() / 1000)
        num = roundCent(zhongheInQianzhi / 5)
        efficiency = min(1, roundCent(num / (time + 1e-10) * 1.75))
        rate = min(100, efficiency)
        res = {"code": 305, "time": time, "num": num, "efficiency": efficiency, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 30, 0)
        self.result["review"]["content"].append(res)

        # # 敬请期待
        # res = {"code": 90, "rate": 0, "status": 1}
        # self.result["review"]["content"].append(res)

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
        开始灵素复盘分析.
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
        self.public = config.item["lingsu"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}
        self.haste = config.item["lingsu"]["speed"]
        self.occ = "lingsu"



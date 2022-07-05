# Created by moeheart at 01/14/2022
# 奶毒复盘，用于奶毒复盘的生成，展示

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
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb)
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

class BuTianJueReplayer(ReplayerBase):
    '''
    奶毒复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶毒复盘 v%s"%EDITION
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
            if not self.config.item["butian"]["speedforce"]:
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

        numHeal = 0
        numEffHeal = 0
        npcHealStat = {}
        numPurge = 0  # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        healStat = {}  # 治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        battleTimeDict = {}  # 进战时间
        sumPlayer = 0  # 玩家数量

        xwgdNumDict = {}  # 仙王蛊鼎触发次数
        firstXwgd = 0
        firstXwgdTaketime = 0
        qilongRateDict = {}  # 绮栊覆盖率

        # 技能统计
        dxSkill = SkillHealCounter("3051", self.startTime, self.finalTime, self.haste)  # 蝶旋
        dcSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 蝶池
        bcqsSkill = SkillHealCounter("2232", self.startTime, self.finalTime, self.haste)  # 冰蚕牵丝
        zwjtSkill = SkillHealCounter("6252", self.startTime, self.finalTime, self.haste)  # 醉舞九天
        ssztSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 圣手织天
        qdtrSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 千蝶吐瑞
        mxymSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 迷仙引梦

        zwjtDict = BuffCounter("?", self.startTime, self.finalTime)  # 用buff类型来记录醉舞九天的具体时间
        mxymDict = BuffCounter("?", self.startTime, self.finalTime)  # 迷仙引梦记录
        xwgdDict = BuffCounter("?", self.startTime, self.finalTime)  # 锅记录
        ghzsDict = BuffCounter("?", self.startTime, self.finalTime)  # 蛊惑记录

        cyDict = BuffCounter("2844", self.startTime, self.finalTime)  # 蚕引
        cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风
        nvwaDict = BuffCounter("2315", self.startTime, self.finalTime)  # 女娲补天

        battleDict = {}
        firstHitDict = {}

        for line in self.bld.info.player:
            battleDict[line] = BuffCounter("0", self.startTime, self.finalTime)  # 战斗状态统计
            firstHitDict[line] = 0
            battleStat[line] = [0]
            xwgdNumDict[line] = 0

        self.qilongCounter = {}
        for key in self.bld.info.player:
            self.qilongCounter[key] = ShieldCounterNew("20831", self.startTime, self.finalTime)

        lastSkillTime = self.startTime

        # 杂项
        wuhuoHeal = 0  # 无惑
        xjmjHeal = 0  # 献祭秘籍
        bdxjHeal = 0  # 碧蝶献祭

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True],

                     [bcqsSkill, "冰蚕牵丝", ["2526", "27391", "6662"], "2745", True, 24, False, True],
                     [ssztSkill, "圣手织天", ["13425", "13426"], "3028", True, 0, False, True],
                     [qdtrSkill, "千蝶吐瑞", ["2449"], "2748", True, 8, True, True],
                     [None, "迷仙引梦", ["15132"], "7255", True, 8, False, True],
                     [None, "仙王蛊鼎", ["2234"], "2747", True, 24, False, True],
                     [None, "玄水蛊", ["3702"], "3038", True, 0, False, True],
                     [None, "圣元阵", ["25058"], "13447", True, 0, False, True],
                     [None, "蛊惑众生", ["2231"], "2744", True, 0, False, True],
                     [None, "碧蝶引", ["2965"], "3025", True, 0, False, True],

                     # [None, "醉舞九天", ["6252"], "2746", False, 16, True, True],
                     [None, "化蝶", ["2228"], "2830", False, 0, False, True],
                     [None, "蛊虫献祭", ["2226"], "2762", False, 0, False, True],
                     [None, "蝶鸾", ["3054"], "2764", False, 0, False, True],
                     [None, "女娲补天", ["2230"], "2743", False, 0, False, True],
                     [None, "灵蛊", ["18584"], "2777", False, 0, False, True],
                    ]

        zwjtTime = getLength(16, self.haste)

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i

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
                               ## 奶毒分割线
                               "3051", "3644", "3473",  # 蝶旋
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

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # numAbsorb1 += event.healEff
                    pass
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
                            if event.id in ["2526", "27391", "6662"]:
                                # 检查冰蚕诀
                                sf = cyDict.checkState(event.time - 200)
                                if sf:
                                    castTime = 0
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
                        elif event.id in nonGcdSkillIndex:  # 特殊技能
                            desc = ""
                            index = nonGcdSkillIndex[event.id]
                            line = skillInfo[index]
                            bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                            # 无法分析的技能
                        elif event.id not in xiangZhiUnimportant:
                            pass
                            # print("[ButianNonRec]", event.time, event.id, event.heal, event.healEff)

                        # 统计不计入时间轴的治疗量
                        if event.id in ["3051", "3473"]:  # 蝶旋
                            dxSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        if event.id in ["15134"]:  # 迷仙引梦
                            mxymSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                            if event.time - mxymDict.log[-1][0] > 200:
                                mxymDict.setState(event.time - 2000, 1)
                                mxymDict.setState(event.time, 0)
                        if event.id in ["18884"]:  # 蝶池
                            dcSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
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
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                if event.id in ["12769"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    bh.setSpecialSkill(event.id, "cw特效", "14407",
                                       event.time, 0, "触发cw特效")
                    cwDict.setState(event.time, event.stack)
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)
                if event.id in ["2315"] and event.target == self.mykey:  # 沐风
                    nvwaDict.setState(event.time, event.stack)
                if event.id in ["2316"] and event.caster == self.mykey:  # 蛊惑
                    ghzsDict.setState(event.time, event.stack)
                if event.id in ["2844"] and event.target == self.mykey:  # 蚕引
                    cyDict.setState(event.time, event.stack)
                if event.id in ["20831"] and event.caster == self.mykey:  # buff绮栊
                    self.qilongCounter[event.target].setState(event.time, event.stack)

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
        healList = dictToPairs(healStat)
        healList.sort(key=lambda x: -x[1][0])

        sumHeal = 0
        numid = 0
        topHeal = 0
        myHealStat = {"hps": 0, "ohps": 0}
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
            if line[0] == self.mykey:
                myHealStat["hps"] = res["healEff"]
                myHealStat["ohps"] = res["heal"]

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

            time1 = self.qilongCounter[key].buffTimeIntegral()
            timeAll = liveCount
            qilongRateDict[key] = time1 / (timeAll + 1e-10)

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   "xwgdNum": xwgdNumDict[line[0]],
                   "qilongRate": roundCent(qilongRateDict[line[0]]),
                   }
            self.result["dps"]["table"].append(res)

        # 计算绮栊覆盖率
        numRate = 0
        sumRate = 0
        for key in qilongRateDict:
            numRate += battleTimeDict[key]
            sumRate += qilongRateDict[key] * battleTimeDict[key]
        overallRate = sumRate / (numRate + 1e-10)

        mxymDict.shrink(100)
        ghzsDict.shrink(100)
        zwjtDict.shrink(100)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 冰蚕牵丝
        self.result["skill"]["bcqs"] = {}
        self.result["skill"]["bcqs"]["num"] = bcqsSkill.getNum()
        self.result["skill"]["bcqs"]["numPerSec"] = roundCent(
            self.result["skill"]["bcqs"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["bcqs"]["delay"] = int(bcqsSkill.getAverageDelay())
        effHeal = bcqsSkill.getHealEff()
        self.result["skill"]["bcqs"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["bcqs"]["effRate"] = effHeal / (bcqsSkill.getHeal() + 1e-10)
        # 醉舞九天
        self.result["skill"]["zwjt"] = {}
        self.result["skill"]["zwjt"]["num"] = zwjtSkill.getNum()
        self.result["skill"]["zwjt"]["numPerSec"] = roundCent(
            self.result["skill"]["zwjt"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["zwjt"]["delay"] = int(zwjtSkill.getAverageDelay())
        effHeal = zwjtSkill.getHealEff()
        self.result["skill"]["zwjt"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["zwjt"]["effRate"] = effHeal / (zwjtSkill.getHeal() + 1e-10)
        # 圣手织天
        self.result["skill"]["sszt"] = {}
        self.result["skill"]["sszt"]["num"] = ssztSkill.getNum()
        self.result["skill"]["sszt"]["numPerSec"] = roundCent(
            self.result["skill"]["sszt"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["sszt"]["delay"] = int(ssztSkill.getAverageDelay())
        effHeal = ssztSkill.getHealEff()
        self.result["skill"]["sszt"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["sszt"]["effRate"] = effHeal / (ssztSkill.getHeal() + 1e-10)
        # 千蝶吐瑞
        self.result["skill"]["qdtr"] = {}
        self.result["skill"]["qdtr"]["num"] = qdtrSkill.getNum()
        self.result["skill"]["qdtr"]["numPerSec"] = roundCent(
            self.result["skill"]["qdtr"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["qdtr"]["delay"] = int(qdtrSkill.getAverageDelay())
        effHeal = qdtrSkill.getHealEff()
        self.result["skill"]["qdtr"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["qdtr"]["effRate"] = effHeal / (qdtrSkill.getHeal() + 1e-10)
        # 蝶池
        self.result["skill"]["dc"] = {}
        self.result["skill"]["dc"]["num"] = dcSkill.getNum()
        self.result["skill"]["dc"]["numPerSec"] = roundCent(
            self.result["skill"]["dc"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = dcSkill.getHealEff()
        self.result["skill"]["dc"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["dc"]["effRate"] = effHeal / (dcSkill.getHeal() + 1e-10)
        # 迷仙引梦
        self.result["skill"]["mxym"] = {}
        self.result["skill"]["mxym"]["num"] = mxymSkill.getNum()
        self.result["skill"]["mxym"]["numPerSec"] = roundCent(
            self.result["skill"]["mxym"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = mxymSkill.getHealEff()
        self.result["skill"]["mxym"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["mxym"]["effRate"] = effHeal / (mxymSkill.getHeal() + 1e-10)
        num = battleTimeDict[self.mykey]
        sum = mxymDict.buffTimeIntegral()
        self.result["skill"]["mxym"]["cover"] = roundCent(sum / (num + 1e-10))
        # 蝶旋
        self.result["skill"]["dx"] = {}
        self.result["skill"]["dx"]["num"] = dxSkill.getNum()
        self.result["skill"]["dx"]["numPerSec"] = roundCent(
            self.result["skill"]["dx"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = dxSkill.getHealEff()
        self.result["skill"]["dx"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["dx"]["effRate"] = effHeal / (dxSkill.getHeal() + 1e-10)
        # 杂项
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["nvwa"] = {}
        sum = nvwaDict.buffTimeIntegral()
        self.result["skill"]["nvwa"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["ghzs"] = {}
        num = battleTimeDict[self.mykey]
        sum = ghzsDict.buffTimeIntegral()
        self.result["skill"]["ghzs"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["qilong"] = {}
        self.result["skill"]["qilong"]["cover"] = roundCent(overallRate)
        # 整体
        self.result["skill"]["general"] = {}
        # self.result["skill"]["general"]["HanQingNum"] = numHanQing
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        self.result["skill"]["general"]["efficiencyNonGcd"] = bh.getNonGcdEfficiency(zwjtDict.log)
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        self.result["replay"]["mxym"] = mxymDict.log
        self.result["replay"]["xwgd"] = xwgdDict.log
        self.result["replay"]["ghzs"] = ghzsDict.log
        self.result["replay"]["zwjt"] = zwjtDict.log
        # 统计治疗相关
        # TODO 改为整体统计
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = myHealStat["ohps"]
        self.result["skill"]["healer"]["healEff"] = myHealStat["hps"]

        self.getRankFromStat("butianjue")
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        specialKey = {"bcqs-numPerSec": 10, "zwjt-numPerSec": 10, "general-efficiency": 20, "healer-healEff": 20}
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

        # self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}

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

        # 敬请期待
        res = {"code": 90, "rate": 0, "status": 1}
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
        hashStr = battleMinute + self.result["overall"]["map"] + "".join(nameList) + self.result["overall"]["edition"]
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
        upload["occ"] = "butianjue"
        upload["score"] = 0
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
        开始奶毒复盘分析.
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
        self.public = config.item["butian"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}
        self.haste = config.item["butian"]["speed"]



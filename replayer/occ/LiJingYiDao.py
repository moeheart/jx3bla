# Created by moeheart at 01/06/2022
# 奶花复盘，用于奶花复盘的生成，展示

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

        chunniDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        chunniDisplayer.setImage("413", "春泥护花")
        chunniDisplayer.setDouble("rate", "数量", "chunni", "num", "numPerSec")
        chunniDisplayer.export_image(frame5, 4)

        longwuDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        longwuDisplayer.setImage("16221", "泷雾")
        longwuDisplayer.setDouble("rate", "数量", "longwu", "num", "numPerSec")
        longwuDisplayer.setSingle("delay", "延迟", "longwu", "delay")
        longwuDisplayer.setSingle("int", "HPS", "longwu", "HPS")
        longwuDisplayer.setSingle("percent", "有效比例", "longwu", "effRate")
        longwuDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "清疏HPS", "qingshu", "HPS")
        info1Displayer.setSingle("int", "寒清次数", "general", "HanQingNum")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("percent", "秋肃覆盖率", "qiusu", "cover")
        info2Displayer.setSingle("int", "秋肃DPS", "qiusu", "dps")
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
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb)
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

class LiJingYiDaoReplayer(ReplayerBase):
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

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶花复盘 v%s"%EDITION
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
            res = adr.Display(strEquip, "2h")
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
            if not self.config.item["lijing"]["speedforce"]:
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

        battleDict = self.battleDict

        numHeal = 0
        numEffHeal = 0
        npcHealStat = {}
        numPurge = 0  # 驱散次数
        battleStat = {}  # 伤害占比统计，[无秋肃伤害，有秋肃伤害]
        damageDict = {}  # 伤害统计
        healStat = {}  # 治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        hanqingNumDict = {}  # 寒清触发次数
        battleTimeDict = {}  # 进战时间
        sumPlayer = 0  # 玩家数量
        teamLog = {}  # 小队聚类数量统计
        teamLastTime = {}  # 小队聚类时间

        # 技能统计
        wozhenSkill = SkillHealCounter("101", self.startTime, self.finalTime, self.haste)  # 握针
        tizhenSkill = SkillHealCounter("138", self.startTime, self.finalTime, self.haste)  # 提针
        changzhenSkill = SkillHealCounter("142", self.startTime, self.finalTime, self.haste)  # 长针
        bizhenSkill = SkillHealCounter("140", self.startTime, self.finalTime, self.haste)  # 彼针
        # chunniSkill = SkillHealCounter("132", self.startTime, self.finalTime, self.haste)  # 春泥护花
        longwuSkill = SkillHealCounter("28541", self.startTime, self.finalTime, self.haste)  # 泷雾
        wozhenBuff = SkillHealCounter("631", self.startTime, self.finalTime, self.haste)  # 握针
        shuhuaiBuff = SkillHealCounter("5693", self.startTime, self.finalTime, self.haste)  # 述怀

        xqxDict = BuffCounter("6266", self.startTime, self.finalTime)  # 行气血
        cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        shuiyueDict = BuffCounter("412", self.startTime, self.finalTime)  # 水月
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风

        firstHitDict = {}
        wozhenDict = {}  # 握针
        shuhuaiDict = {}  # 述怀

        for line in self.bld.info.player:
            firstHitDict[line] = 0
            hanqingNumDict[line] = 0
            wozhenDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 握针
            shuhuaiDict[line] = HotCounter("20070", self.startTime, self.finalTime)  # 述怀
            teamLog[line] = {}
            teamLastTime[line] = 0
            battleStat[line] = [0, 0]

        lastSkillTime = self.startTime

        # 秋肃统计
        qiusuTarget = ""
        qiusuTime = 0
        qiusuCounter = BuffCounter("0", self.startTime, self.finalTime)

        # 杂项
        qingshuHeal = 0
        wozhenDirectHeal = 0
        changzhenAOEHeal = 0
        haozhenDirectHeal = 0  # 毫针本体
        haozhenPercentHeal = 0  # 毫针贯体
        shuiyueStack = 0
        shuiyueNum = 0
        xqxStack = 0
        xqxNum = 0
        instantNum = 0
        instantChangzhenNum = 0
        lastInstant = 0
        weichaoSingleList = []
        weichaoNum = 0
        weichaoSkill = 0
        weichaoEff = 0
        weichaoEffList = []

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],

                     [wozhenSkill, "握针", ["101"], "1519", True, 0, False, True, 0, 1],
                     [tizhenSkill, "提针", ["22792", "22886"], "395", True, 24, False, True, 0, 1],
                     [changzhenSkill, "长针", ["3038"], "396", True, 48, False, True, 0, 1],
                     [bizhenSkill, "彼针", ["26666", "26667", "26668"], "1518", True, 24, False, True, 6, 1],
                     [None, "春泥护花", ["132"], "413", True, 0, False, True, 36, 1],
                     [None, "利针", ["2654"], "3004", True, 16, False, True, 0, 1],
                     [None, "清风垂露", ["133"], "1523", True, 0, False, True, 3, 1],
                     [None, "折叶笼花", ["14963"], "16602", True, 0, False, True, 70, 1],
                     [None, "碧水滔天", ["131"], "1525", True, 0, False, True, 95, 1],
                     [None, "大针", ["24911"], "14148", True, 0, False, True, 50, 1],
                     [None, "天工甲士", ["28724"], "16223", True, 80, False, True, 0, 1],
                     [None, "天工", ["28720"], "16224", True, 32, False, False, 0, 1],
                     [longwuSkill, "泷雾", ["28541"], "16224", True, 16, True, True, 0, 1],
                     [None, "护本", ["28555"], "16222", True, 0, False, True, 10, 1],
                     [None, "脱离机甲", ["28480"], "16225", True, 0, False, True, 0, 1],
                     [None, "商阳指", ["180"], "1514", True, 0, False, True, 0, 1],

                     [None, "水月无间", ["136"], "1522", False, 0, False, True, 60, 1],
                     [None, "听风吹雪", ["2663"], "2998", False, 0, False, True, 75, 1],
                    ]

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            if line[0] is None:
                skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste)
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i
        yzInfo = [None, "特效腰坠", ["0"], "3414", False, 0, False, True, 180, 1]
        yzSkill = SkillCounterAdvance(yzInfo, self.startTime, self.finalTime, self.haste)
        yzInfo[0] = yzSkill

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
                               ## 奶花分割线
                               "6112",  # 清疏
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
                            sfFlag = 0
                            if event.id in ["22792", "22886", "3038", "26666", "26667", "26668"]:
                                # 检查水月
                                sf = shuiyueDict.checkState(event.time - 200)
                                if sf:
                                    sfFlag = 1
                            if not sfFlag and event.id in ["3038", "26666", "26667", "26668"]:
                                # 检查行气血、cw
                                sf2 = xqxDict.checkState(event.time - 200)
                                sf3 = cwDict.checkState(event.time - 200)
                                if sf2 or sf3:
                                    sfFlag = 1
                            if sfFlag:
                                castTime = 0
                                if event.time - lastInstant > 100:
                                    instantNum += 1
                                lastInstant = event.time
                                if event.id in ["3038"]:
                                    instantChangzhenNum += 1
                            ss.analyseSkill(event, castTime, line[0], tunnel=line[6], hasteAffected=line[7])
                            target = ""
                            if event.id in ["101", "3038", "26666", "26667", "26668"]:
                                target = event.target
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
                                                     ss.healEff, 0, ss.busy, "", target, targetName)
                            else:
                                # 不同技能，新建条目
                                bh.setNormalSkill(ss.skill, line[1], line[3],
                                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                                  ss.healEff, 0, ss.busy, "", target, targetName)
                                if sfFlag:
                                    bh.log["normal"][-1]["instant"] = 1
                            ss.reset()
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
                            # print("[LijingNonRec]", event.time, event.id, event.heal, event.healEff)
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
                        if event.id in ["14660", "14665"]:  # 微潮/零落
                            teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                        if event.id in ["14660"]:
                            # 根据微潮统计长针有效目标数
                            timeDiff = event.time - weichaoSkill
                            effFlag = 0
                            if wozhenDict[event.target].checkState(event.time) == 0:
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
                        if event.id in ["180"]:  # 商阳指
                            # 秋肃生成
                            qiusuTarget = event.target
                            qiusuTime = event.time
                            if qiusuCounter.log != [] and qiusuCounter.log[-1][1] == 0 and qiusuCounter.log[-1][0] > event.time:
                                del qiusuCounter.log[-1]
                            qiusuCounter.setState(event.time, 1)
                            qiusuCounter.setState(event.time + 18000, 0)

                    if event.caster == self.mykey and event.scheme == 2:
                        if event.id in ["631"]:  # 握针
                            wozhenBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        if event.id in ["5693"]:  # 述怀
                            shuhuaiBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

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
                    # 秋肃累计
                    if event.target in self.bld.info.npc and event.caster in self.bld.info.player:
                        if event.target == qiusuTarget and event.time - qiusuTime < 18000:
                            battleStat[event.caster][1] += event.damageEff
                        else:
                            battleStat[event.caster][0] += event.damageEff

                # 统计寒清
                if event.id in ["18274"] and event.target in hanqingNumDict: # and event.caster == self.mykey:
                    hanqingNumDict[event.target] += 1

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                    yzSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                if event.id in ["12770"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    bh.setSpecialSkill(event.id, "cw特效", "14404",
                                       event.time, 0, "触发cw特效")
                    cwDict.setState(event.time, event.stack)
                if event.id in ["6266"] and event.target == self.mykey:  # 行气血
                    xqxDict.setState(event.time, event.stack)
                    if event.stack > xqxStack:
                        xqxNum += event.stack
                    xqxStack = event.stack
                if event.id in ["412"] and event.target == self.mykey:  # 水月无间
                    shuiyueDict.setState(event.time, event.stack)
                    if event.stack > shuiyueStack:
                        shuiyueNum += event.stack
                    shuiyueStack = event.stack
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)
                if event.id in ["631"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 握针
                    wozhenDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                    # print("[WozhenTest]", event.time, event.id, event.stack)
                if event.id in ["5693"] and event.caster == self.mykey and event.target in self.bld.info.player:  # 述怀
                    shuhuaiDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)

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
        if weichaoNum != 0:
            weichaoSingleList.append(weichaoNum)
        if weichaoEff != 0:
            weichaoEffList.append(weichaoEff)

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

        # 计算组队聚类信息
        teamCluster, numCluster = finalCluster(teamLog)

        # 记录每次技能的目标队伍
        for i in range(len(bh.log["normal"])):
            if "team" in bh.log["normal"][i]:
                if bh.log["normal"][i]["team"] in teamCluster:
                    bh.log["normal"][i]["team"] = teamCluster[bh.log["normal"][i]["team"]]
                else:
                    bh.log["normal"][i]["team"] = 0

        # 计算伤害
        numdam1 = 0
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0] + line[1] / 1.05
            numdam1 += line[1] / 1.05 * 0.05

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
        for key in self.peiwuCounter:
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
                   "HanQingNum": hanqingNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        # 计算寒清次数
        numHanQing = 0
        for key in hanqingNumDict:
            numHanQing += hanqingNumDict[key]

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 队伍HOT统计初始化
        hotHeat = [[], [], [], [], []]
        # 握针
        self.result["skill"]["wozhen"] = {}
        self.result["skill"]["wozhen"]["num"] = wozhenBuff.getNum()
        self.result["skill"]["wozhen"]["numPerSec"] = roundCent(
            self.result["skill"]["wozhen"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = wozhenBuff.getHealEff()
        self.result["skill"]["wozhen"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["wozhen"]["shengxiHPS"] = int(wozhenDirectHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["wozhen"]["delay"] = int(wozhenSkill.getAverageDelay())
        num = 0
        sum = 0
        for key in wozhenDict:
            singleDict = wozhenDict[key]
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
        self.result["skill"]["wozhen"]["cover"] = roundCent(sum / (num + 1e-10))
        # 计算HOT统计
        for i in range(len(hotHeat)):
            if i+1 >= len(numCluster) or numCluster[i+1] == 0:
                continue
            for j in range(len(hotHeat[i])):
                hotHeat[i][j] = int(hotHeat[i][j] / numCluster[i+1] * 100)
        # print("[teamCluster]", teamCluster)
        # print("[HotHeat]", hotHeat)
        # print("[HotHeat0]", hotHeat[0])
        # 提针
        self.result["skill"]["tizhen"] = {}
        self.result["skill"]["tizhen"]["num"] = tizhenSkill.getNum()
        self.result["skill"]["tizhen"]["numPerSec"] = roundCent(
            self.result["skill"]["tizhen"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["tizhen"]["delay"] = int(tizhenSkill.getAverageDelay())
        effHeal = tizhenSkill.getHealEff()
        self.result["skill"]["tizhen"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["tizhen"]["hzDirectHPS"] = int(haozhenDirectHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["tizhen"]["hzPercentHPS"] = int(haozhenPercentHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["tizhen"]["effRate"] = effHeal / (tizhenSkill.getHeal() + 1e-10)
        # 长针
        self.result["skill"]["changzhen"] = {}
        self.result["skill"]["changzhen"]["num"] = changzhenSkill.getNum()
        self.result["skill"]["changzhen"]["numPerSec"] = roundCent(
            self.result["skill"]["changzhen"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["changzhen"]["delay"] = int(changzhenSkill.getAverageDelay())
        effHeal = changzhenSkill.getHealEff()
        self.result["skill"]["changzhen"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["changzhen"]["yuehuaHPS"] = int(changzhenAOEHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["changzhen"]["effRate"] = effHeal / (changzhenSkill.getHeal() + 1e-10)
        # 彼针
        self.result["skill"]["bizhen"] = {}
        self.result["skill"]["bizhen"]["num"] = bizhenSkill.getNum()
        self.result["skill"]["bizhen"]["numPerSec"] = roundCent(
            self.result["skill"]["bizhen"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["bizhen"]["delay"] = int(bizhenSkill.getAverageDelay())
        effHeal = bizhenSkill.getHealEff()
        self.result["skill"]["bizhen"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["bizhen"]["effRate"] = effHeal / (bizhenSkill.getHeal() + 1e-10)
        num = 0
        sum = 0
        for key in shuhuaiDict:
            singleDict = shuhuaiDict[key]
            num += battleTimeDict[key]
            sum += singleDict.buffTimeIntegral()
        self.result["skill"]["bizhen"]["shCover"] = roundCent(sum / (num + 1e-10))
        # 春泥护花
        self.result["skill"]["chunni"] = {}
        self.result["skill"]["chunni"]["num"] = skillInfo[gcdSkillIndex["132"]][0].getNum()
        self.result["skill"]["chunni"]["numPerSec"] = roundCent(
            self.result["skill"]["chunni"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        # 泷雾
        self.result["skill"]["longwu"] = {}
        self.result["skill"]["longwu"]["num"] = longwuSkill.getNum()
        self.result["skill"]["longwu"]["numPerSec"] = roundCent(
            self.result["skill"]["longwu"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["longwu"]["delay"] = int(longwuSkill.getAverageDelay())
        effHeal = longwuSkill.getHealEff()
        self.result["skill"]["longwu"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["longwu"]["effRate"] = roundCent(effHeal / (longwuSkill.getHeal() + 1e-10))
        # 秋肃
        self.result["skill"]["qiusu"] = {}
        num = battleTimeDict[self.mykey]
        sum = qiusuCounter.buffTimeIntegral()
        self.result["skill"]["qiusu"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["qiusu"]["dps"] = int(numdam1 / self.result["overall"]["sumTime"] * 1000)
        # 杂项
        self.result["skill"]["qingshu"] = {}
        self.result["skill"]["qingshu"]["HPS"] = int(qingshuHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["HanQingNum"] = numHanQing
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}
        # 统计治疗相关
        # TODO 改为整体统计
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = myHealStat["ohps"]
        self.result["skill"]["healer"]["healEff"] = myHealStat["hps"]

        self.getRankFromStat("lijingyidao")
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        specialKey = {"wozhen-numPerSec": 20, "general-efficiency": 20, "healer-healEff": 20, "qiusu-cover": 20}
        for key1 in self.result["rank"]:
            for key2 in self.result["rank"][key1]:
                key = "%s-%s" % (key1, key2)
                weight = 1
                if key in specialKey:
                    weight = specialKey[key]
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
        for id in ["132", "136", "2663", "14963", "24911"]:
            if id in nonGcdSkillIndex:
                scCandidate.append(skillInfo[nonGcdSkillIndex[id]][0])
            else:
                scCandidate.append(skillInfo[gcdSkillIndex[id]][0])
        scCandidate.append(yzSkill)

        rateSum = 0
        rateNum = 0
        numAll = []
        sumAll = []
        skillAll = []
        for skillObj in scCandidate:
            num = skillObj.getNum()
            sum = skillObj.getMaxPossible()
            skill = skillObj.name
            if skill in ["折叶笼花", "大针", "特效腰坠"] and num == 0:
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

        # code 203 不要浪费瞬发次数
        rate = roundCent(instantNum / (shuiyueNum + xqxNum + 1e-10))
        res = {"code": 203, "timeShuiyue": shuiyueNum, "timeXqx": xqxNum, "timeCast": instantNum, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # code 204 优先瞬发`长针`
        rate = roundCent(instantChangzhenNum / (instantNum + 1e-10))
        res = {"code": 204, "timeCast": instantNum, "timeChangzhen": instantChangzhenNum, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # code 205 选择合适的`长针`目标
        num = 0
        sum = 0
        for i in weichaoSingleList:
            sum += 1
            if i >= 4:
                num += 1
        coverRate = roundCent(num / (sum + 1e-10))
        res = {"code": 205, "time": sum, "coverTime": num, "rate": coverRate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # code 206 提高握针扩散效率
        num = 0
        sum = 0
        for i in weichaoEffList:
            sum += 1
            num += i
        cover = roundCent(num / (sum + 1e-10))
        rate = roundCent(num / (sum + 1e-10) / 4)
        res = {"code": 206, "cover": cover, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
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
        开始奶花复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()
        self.prepareUpload()
        pass

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
        self.public = config.item["lijing"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}
        self.haste = config.item["lijing"]["speed"]
        self.occ = "lijingyidao"


# Created by moeheart at 01/22/2023
# 花间游的复盘方法。

from replayer.occ.Dps import DpsReplayer

from replayer.BattleHistory import BattleHistory, SingleSkill
from tools.Names import *
from tools.Functions import *
from replayer.Name import *
from window.DpsDisplayWindow import DpsDisplayWindow, SingleSkillDisplayer

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk

import webbrowser

import time

class HuaJianYouWindow(DpsDisplayWindow):
    '''
    花间复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴中由上到下分别表示：商阳、钟林、兰摧、快雪这四个DoT。颜色深浅表示剩余时间。
注意，对于多目标的情况这里会尝试合并所有目标的状况，因此不一定准确。'''
        messagebox.showinfo(title='说明', message=text)

    def openHelp(self):
        '''
        打开心法的介绍网页.
        '''
        url = "https://www.jx3box.com/bps/56562"
        webbrowser.open(url)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，奶歌复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        frame5.place(x=10, y=250)

        ymzDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        ymzDisplayer.setImage("1527", "阳明指")
        ymzDisplayer.setDouble("rate", "数量", "ymz", "num", "numPerSec")
        ymzDisplayer.setDouble("rate", "rDPS", "ymz", "rdps", "rdpsRate")
        ymzDisplayer.setSingle("delay", "延迟", "ymz", "delay")
        ymzDisplayer.setSingle("int", "吞海次数", "ymz", "tunhai")
        ymzDisplayer.export_image(frame5, 0)

        syzDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        syzDisplayer.setImage("1514", "商阳指")
        syzDisplayer.setDouble("rate", "数量", "syz", "num", "numPerSec")
        syzDisplayer.setDouble("rate", "rDPS", "syz", "rdps", "rdpsRate")
        syzDisplayer.setSingle("percent", "覆盖率", "syz", "cover")
        syzDisplayer.export_image(frame5, 1)

        zlyxDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        zlyxDisplayer.setImage("404", "钟林毓秀")
        zlyxDisplayer.setDouble("rate", "数量", "zlyx", "num", "numPerSec")
        zlyxDisplayer.setDouble("rate", "rDPS", "zlyx", "rdps", "rdpsRate")
        zlyxDisplayer.setSingle("percent", "覆盖率", "zlyx", "cover")
        zlyxDisplayer.export_image(frame5, 2)

        lcyzDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        lcyzDisplayer.setImage("390", "兰摧玉折")
        lcyzDisplayer.setDouble("rate", "数量", "lcyz", "num", "numPerSec")
        lcyzDisplayer.setDouble("rate", "rDPS", "lcyz", "rdps", "rdpsRate")
        lcyzDisplayer.setSingle("percent", "覆盖率", "lcyz", "cover")
        lcyzDisplayer.export_image(frame5, 3)

        kxsqDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        kxsqDisplayer.setImage("2999", "快雪时晴")
        kxsqDisplayer.setDouble("rate", "数量", "kxsq", "num", "numPerSec")
        kxsqDisplayer.setDouble("rate", "rDPS", "kxsq", "rdps", "rdpsRate")
        kxsqDisplayer.setDouble("rate", "DOT数量", "kxsqdot", "num", "numPerSec")
        kxsqDisplayer.setDouble("rate", "DOTrDPS", "kxsqdot", "rdps", "rdpsRate")
        kxsqDisplayer.setSingle("delay", "延迟", "kxsq", "delay")
        kxsqDisplayer.export_image(frame5, 4)

        ysjfDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        ysjfDisplayer.setImage("411", "玉石俱焚")
        ysjfDisplayer.setDouble("rate", "数量", "ysjf", "num", "numPerSec")
        ysjfDisplayer.setDouble("rate", "rDPS", "ysjf", "rdps", "rdpsRate")
        ysjfDisplayer.setSingle("delay", "延迟", "ysjf", "delay")
        ysjfDisplayer.export_image(frame5, 5)

        frbdDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        frbdDisplayer.setImage("398", "芙蓉并蒂")
        frbdDisplayer.setDouble("rate", "数量", "frbd", "num", "numPerSec")
        frbdDisplayer.setDouble("rate", "rDPS", "frbd", "rdps", "rdpsRate")
        frbdDisplayer.setSingle("delay", "延迟", "frbd", "delay")
        frbdDisplayer.export_image(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("int", "rDPS", "general", "rdps")
        info2Displayer.setSingle("int", "mrDPS", "general", "mrdps")
        info2Displayer.setSingle("int", "nDPS", "general", "ndps")
        info2Displayer.setSingle("int", "mnDPS", "general", "mndps")
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
        dotName = ["shangyang", "zhonglin", "lancui", "kuaixue"]
        if "heat" in self.result["replay"]:
            yPos = [31, 41, 51, 61, 70]
            for j in range(4):
                dot = dotName[j]
                nowTimePixel = 0
                for line in self.result["replay"]["heat"][dot]["timeline"]:
                    if line == 0:
                        color = "#ff7777"
                    else:
                        color = getColorHex((int(255 - (255 - 127) * line / 100),
                                             int(255 - (255 - 31) * line / 100),
                                             int(255 - (255 - 223) * line / 100)))
                    canvas6.create_rectangle(nowTimePixel, yPos[j], nowTimePixel + 5, yPos[j+1], fill=color, width=0)
                    nowTimePixel += 5

        if "badPeriodDps" in self.result["replay"]:
            # 绘制无效时间段
            for i in range(1, len(self.result["replay"]["badPeriodDps"])):
                posStart = int((self.result["replay"]["badPeriodDps"][i - 1][0] - startTime) / 100)
                posStart = max(posStart, 1)
                posEnd = int((self.result["replay"]["badPeriodDps"][i][0] - startTime) / 100)
                zwjt = self.result["replay"]["badPeriodDps"][i - 1][1]
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
                            canvas6.create_rectangle(posStart, 70, posStart + 20, 90, fill="#64fab4")
                        if "tunhai" in record_single:
                            canvas6.create_rectangle(posStart, 70, posStart + 20, 90, outline="#ff0000", width=2)
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

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - config: 设置类
        - result: 花间复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#7f1fdf")
        self.title = '花间复盘'
        self.occ = "huajianyou"

class HuaJianYouReplayer(DpsReplayer):
    '''
    花间复盘类。
    '''


    # def calculateSkillInfoDirect(self, name, skillObj):
    #     '''
    #     根据技能名和对象统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - skillObj: skillInfo中定义的技能对象.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))
    #
    # def calculateSkillInfo(self, name, id):
    #     '''
    #     根据技能名和ID统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - id: 技能的ID，用于在skillInfo中查找.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     skillObj = self.skillInfo[self.gcdSkillIndex[id]][0]
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))

    def calculateSkillFinal(self):
        '''
        第二阶段结束时最后计算评分的部分.
        '''

        # 排序
        self.result["review"]["content"].sort(key=lambda x: -x["status"] * 1000 + x["rate"])
        num = 0
        for line in self.result["review"]["content"]:
            if line["status"] > 0:
                num += 1
                self.reviewScore -= [0, 1, 3, 10][line["status"]] * 100
        self.result["review"]["num"] = num

        self.result["review"]["score"] = self.reviewScore
        self.result["skill"]["general"]["score"] = self.reviewScore

    def calculateSkillOverall(self):
        '''
        第二阶段结束时共有的技能统计部分.
        '''

        # self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()
        self.result["skill"]["general"]["rdps"] = self.result["dps"]["stat"].get("rdps", 0)
        self.result["skill"]["general"]["ndps"] = self.result["dps"]["stat"].get("ndps", 0)
        self.result["skill"]["general"]["mrdps"] = self.result["dps"]["stat"].get("mrdps", 0)
        self.result["skill"]["general"]["mndps"] = self.result["dps"]["stat"].get("mndps", 0)

        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["ohps"] = self.result["dps"]["stat"].get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = self.result["dps"]["stat"].get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = self.result["dps"]["stat"].get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = self.result["dps"]["stat"].get("ahps", 0)

        self.getRankFromStat(self.occ)
        self.result["rank"] = self.rank
        # sumWeight = 0
        # sumScore = 0
        # for key1 in self.result["rank"]:
        #     for key2 in self.result["rank"][key1]:
        #         key = "%s-%s" % (key1, key2)
        #         weight = 1
        #         if key in self.specialKey:
        #             weight = self.specialKey[key]
        #         sumScore += self.result["rank"][key1][key2]["percent"] * weight
        #         sumWeight += weight

        self.reviewScore = 0

        # 计算专案组的公有部分.

        self.result["review"] = {"available": 1, "content": []}

    def completeSecondState(self):
        '''
        第二阶段扫描完成后的公共流程.
        '''
        bh = self.bh
        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]
            bh.badPeriodDpsLog = self.bossBh.badPeriodDpsLog
            bh.badPeriodHealerLog = self.bossBh.badPeriodHealerLog

        # 计算团队伤害区(Part 3)
        self.result["dps"] = {"stat": {}}

        player = self.mykey
        res = {"rhps": int(self.act.getRhps(player)),
               "hps": int(self.act.getRhps(player, "hps")),
               "ahps": int(self.act.getRhps(player, "ahps")),
               "phps": int(self.act.getRhps(player, "ohps")),
               "rdps": int(self.act.getRdps(player)),
               "ndps": int(self.act.getRdps(player, "ndps")),
               "mrdps": int(self.act.getRdps(player, "mrdps")),
               "mndps": int(self.act.getRdps(player, "mndps"))}
        self.result["dps"]["stat"] = res

        self.myDpsStat = res

    def getOverallInfo(self):
        '''
        获取全局信息.
        '''
        # 大部分全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "%s复盘pro v%s" % (self.occPrint, EDITION)
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
        self.result["overall"]["sumTimeEff"] = self.bossBh.sumTime("healer")
        self.result["overall"]["sumTimeEffPrint"] = parseTime(self.result["overall"]["sumTimeEff"] / 1000)
        self.result["overall"]["sumTimeDpsEff"] = self.bossBh.sumTime("dps")
        self.result["overall"]["dataType"] = self.bld.dataType
        self.result["overall"]["mask"] = self.config.item["general"]["mask"]
        self.result["overall"]["win"] = self.win

    def completeFirstState(self):
        '''
        第一阶段扫描完成后的公共流程.
        '''

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        self.result["overall"]["playerID"] = self.myname

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        self.result["equip"] = {"available": 0}

        if self.mykey in self.equip and self.equip[self.mykey] is not None:
            # TODO 验证
            self.result["equip"]["available"] = 1
            # ea = EquipmentAnalyser()
            # jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            # eee = ExcelExportEquipment()
            # strEquip = eee.export(jsonEquip)
            jsonEquip = self.jsonEquip[self.mykey]
            strEquip = self.strEquip[self.mykey]
            res = self.equip[self.mykey]
            # print("[Equip2]", jsonEquip)
            self.result["equip"]["score"] = str(jsonEquip.get("score", 0))  # int(self.bld.info.player[self.mykey].equipScore)
            if jsonEquip.get("cached", 0) == 1:
                self.result["equip"]["score"] += "*"
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res.get("根骨", 0)
            self.result["equip"]["strength"] = res.get("力道", 0)
            self.result["equip"]["agility"] = res.get("身法", 0)
            self.result["equip"]["spunk"] = res.get("元气", 0)
            # self.result["equip"]["heal"] = res["治疗"]
            # self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["attack"] = res.get("攻击", 0)
            self.result["equip"]["attackBase"] = res.get("基础攻击", 0)
            self.result["equip"]["critPercent"] = parseCent(res.get("会心", 0)) + "%"
            self.result["equip"]["crit"] = res.get("会心等级", 0)
            self.result["equip"]["critpowPercent"] = parseCent(res.get("会效", 0)) + "%"
            self.result["equip"]["critpow"] = res.get("会效等级", 0)
            self.result["equip"]["overcomePercent"] = parseCent(res.get("破防", 0)) + "%"
            self.result["equip"]["overcome"] = res.get("破防等级", 0)
            self.result["equip"]["strainPercent"] = parseCent(res.get("无双", 0)) + "%"
            self.result["equip"]["strain"] = res.get("无双等级", 0)
            self.result["equip"]["surplus"] = res.get("破招", 0)
            self.result["equip"]["hastePercent"] = parseCent(res.get("加速", 0)) + "%"
            self.result["equip"]["haste"] = res.get("加速等级", 0)
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

        # self.result["overall"]["hasteReal"] = self.haste

    def eventInFirstState(self, event):
        '''
        第一阶段处理事件的公共流程.
        params:
        - event: 处理的事件.
        '''

        if event.dataType == "Skill":
            # 记录治疗心法的出现情况.
            pass

        elif event.dataType == "Buff":
            pass

        elif event.dataType == "Shout":
            # 为未来需要统计喊话时备用.
            pass

    def initFirstState(self):
        '''
        第一阶段初始化.
        '''

        self.getOverallInfo()

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.  TODO 用无效时间修复这个逻辑
        self.interrupt = 0

        # 记录战斗开始时间与结束时间
        if self.startTime == 0:
            self.startTime = self.bld.log[0].time
        if self.finalTime == 0:
            self.finalTime = self.bld.log[-1].time

        # 如果时间被大幅度修剪过，则修正战斗时间  TODO 用无效时间修复这个逻辑
        if abs(self.finalTime - self.startTime - self.result["overall"]["sumTime"]) > 6000:
            actualTime = self.finalTime - self.startTime
            self.result["overall"]["sumTime"] = actualTime
            self.result["overall"]["sumTimePrint"] = parseTime(actualTime / 1000)

        # 记录具体心法的表.
        self.occDetailList = {}
        for key in self.bld.info.player:
            self.occDetailList[key] = self.bld.info.player[key].occ

        # 推导自身id
        for key in self.bld.info.player:
            if self.bld.info.player[key].name == self.myname:
                self.mykey = key

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        '''

        self.window.setNotice({"t2": "加载%s复盘..." % self.occPrint, "c2": self.occColor})

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
                     [None, "碧水滔天", ["131"], "1525", True, 0, False, True, 95, 1],
                     [None, "春泥护花", ["132"], "413", True, 0, False, True, 36, 1],
                     [None, "太阴指", ["228", "497"], "1515", True, 0, False, True, 22, 1],
                     [None, "商阳指", ["180"], "1514", True, 0, False, True, 0, 1],
                     [None, "阳明指", ["14941"], "1527", True, 24, False, True, 0, 1],
                     [None, "钟林毓秀", ["189"], "404", True, 24, False, True, 0, 1],
                     [None, "兰摧玉折", ["190"], "390", True, 24, False, True, 0, 1],
                     [None, "快雪时晴", ["2636"], "2999", True, 10, True, True, 0, 1],
                     [None, "芙蓉并蒂", ["186"], "398", True, 0, False, True, 25, 1],
                     [None, "玉石俱焚", ["182"], "411", True, 0, False, True, 11, 1],

                     [None, "星楼月影", ["100"], "1520", False, 0, False, True, 21, 1],
                     [None, "水月无间", ["136"], "1522", False, 0, False, True, 60, 1],
                     [None, "乱洒青荷", ["2645"], "3001", False, 0, False, True, 75, 1],
                    ]

        self.initSecondState()

        # buff统计
        self.xqxDict = BuffCounter("6266", self.startTime, self.finalTime)  # 行气血
        self.cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        self.shuiyueDict = BuffCounter("412", self.startTime, self.finalTime)  # 水月
        self.luansaDict = BuffCounter("2719", self.startTime, self.finalTime)  # 乱洒
        self.busanDict = BuffCounter("1487", self.startTime, self.finalTime)  # 布散
        self.fengxueDict = BuffCounter("24205", self.startTime, self.finalTime)  # 逢雪
        self.jianyuDict = BuffCounter("24599", self.startTime, self.finalTime)  # 溅玉

        # 技能统计
        syzBuff = SkillHealCounter("180", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodDpsLog)  # 商阳
        zlyxBuff = SkillHealCounter("189", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodDpsLog)  # 钟林
        lcyzBuff = SkillHealCounter("190", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodDpsLog)  # 兰摧
        kxsqBuff = SkillHealCounter("2636", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodDpsLog)  # 快雪
        self.numTunhai = 0

        # 墨意推测
        self.moyiInfer = [[self.startTime, 0]]
        self.moyiActiveTime = 0  # 墨意对齐生效的时间，在buff发生变化之后进行检测
        self.moyiBuffNum = 0  # 墨意层数要求，有层数优先级高于0层

        # Dot统计, 注意这里使用敌对目标.
        self.dotSY = {}
        self.dotZL = {}
        self.dotLC = {}
        self.dotKX = {}

        # 阳明状态
        self.tunhaiTime = 0

        # 手法警察统计
        self.lcWrongNum = 0  # 兰摧：错误次数
        self.lcWrong = []
        self.lcSum = 0  # 兰摧：技能总数
        self.lastLcSkill = 0  # 上一次施放的除兰摧以外的技能
        self.lastYushi = 0  # 上一次施放玉石的时间
        self.luansaLastTime = 0  # 用隐藏技能标记的可能的乱洒时机
        self.ysWrongNum = 0  # 玉石：错误次数
        self.ysWrong = []
        self.ysSum = 0  # 玉石总数
        self.frWrongNum = 0  # 芙蓉：错误次数
        self.frWrong = []
        self.frSum = 0  # 芙蓉总数
        self.frLastTime = 0  # 上次芙蓉时间
        self.frMidNum = -1  # 芙蓉间隔技能数
        self.frBusan = 0  # 上次芙蓉是否有布散
        self.ysfrWrong = []
        self.ysfrWrongNum = 0  # 玉石之前是否没有打芙蓉的计数
        self.ymSum = 0  # 阳明总数
        self.ymtgWrong = []
        self.ymtgWrongNum = 0  # 阳明：踏歌错误的次数
        self.ymfxWrong = []
        self.ymfxWrongNum = 0  # 阳明：逢雪错误的次数
        self.kxSum = 0  # 快雪首跳总数
        self.kxLastTime = 0  # 上一次快雪时间（用于判断快雪是不是同一组）
        self.kxCurrentNum = 0  # 当前的快雪引导了多少跳
        self.kxCurrentNumAll = 0  # 当前的快雪累计命中了多少个目标（和上一项只在群攻场景有区别）
        self.kxfxWrong = []
        self.kxfxWrongNum = 0  # 快雪：逢雪错误的次数
        self.kxloWrong = []
        self.kxloWrongNum = 0  # 快雪：数量太少的次数
        self.kxhiWrong = []
        self.kxhiWrongNum = 0  # 快雪：数量太多的次数
        self.dotSum = 0  # 三毒总数
        self.dotWrongNum = 0
        self.dotWrong = []  # 三毒重复的次数
        self.dot2Sum = 0  # 商阳/钟林总数
        self.dot2WrongNum = 0
        self.dot2Wrong = []  # 商阳/钟林可以延后的次数
        self.syLast = 0  # 没有溅玉时施展的商阳和钟林先暂存时间
        self.zlLast = 0

        self.unimportantSkill += ["32467",  # 花间破招
                                  "32501",  # 踏歌伤害
                                  "33091",  # 踏歌
                                  "601",  # 吞海（阳明触发）
                                  "6693",  # 商阳指的壳
                                  "18730",  # 兰摧的壳
                                  "18722",  # 兰摧检测
                                  "285",  # 钟林的壳
                                  "13848", "13847",  # 乱洒附带毒
                                  "6126", "6129", "6128",  # 玉石辅助判断
                                  "14644",  # 涓流判断
                                  "33222",  # 快雪（带雪弃）
                                  "33231",  # 快雪（不带雪弃）
                                  "179",  # 阳明指（壳）
                                  "32481",  # 快雪上dot
                                  "6134", "6135", "6136", "32409",  # 芙蓉刷新
                                  "32410",  # 吞快雪dot
                                  "14652",  # 玉石减调息
                                  "1320",  # 套装效果
                                  "16",  # 判官笔法
                                  "1856",  # cw加buff
                                  "13849",  # 乱洒带商阳（cwbuff用了以前的壳）
                                  "3086",  # cw实际处理
                                  "25768",  # cw小特效

                                # 记录所有的特殊技能11
                                # 改善重复计数的问题11
                                # 对齐花间的各种瞬发1?
                                # 用dot跳数补充记录
                                # 复盘dot状况
                                # - 上毒 11
                                # - 玉石 11
                                # - 芙蓉 11
                                # - 乱洒/cw 11
                                # - 阳明(601辅助判断)11
                                # 显示时间轴
                                # - 检查cw玉石11
                                # - 检查阳明瞬发11
                                # - 吞海阳明显示一个提示11
                                # 检查墨意复盘是否正确11
                                # 技能统计
                                # - 设计内容
                                  # gcd效率11
                                  # 增益覆盖（队友、自身）11
                                  # 技能数量（阳明：次数11、吞海、dps11、rdps11、比例11；dot：跳数11、覆盖率11、dps11；快雪：数量11、dot11、dps11；芙蓉/玉石：数量11、dps11）；补充
                                # - 统计
                                # - 展示
                                # 手法警察
                                # - 设计内容
                                # - 统计
                                # - 展示
                                # 重新设计UI
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            self.sf = 0

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

                # 跳过纯吸血记录
                if int(event.fullResult.get("7", 0)) > 0 and event.damageEff == 0:
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
                            maxMoyi = 60
                            nowMoyi = lastMoyi + 20
                            if nowMoyi > maxMoyi:
                                nowMoyi = maxMoyi
                            self.moyiInfer.append([event.time, nowMoyi])
                            self.moyiActiveTime = 0  # 取消这附近的墨意判定
                        if event.id in ["100"]:  # 星楼
                            # 获得墨意推测
                            lastMoyi = self.moyiInfer[-1][1]
                            maxMoyi = 60
                            nowMoyi = lastMoyi + 10
                            if nowMoyi > maxMoyi:
                                nowMoyi = maxMoyi
                            self.moyiInfer.append([event.time, nowMoyi])
                            self.moyiActiveTime = 0  # 取消这附近的墨意判定
                        if record:
                            index = self.nonGcdSkillIndex[event.id]
                            line = self.skillInfo[index]
                            self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                            skillObj = line[0]
                            if skillObj is not None:
                                skillObj.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=self.ss.timeEnd, delta=-1)

                    if event.id in ["180", "189", "190", "32481", "182", "6134", "6135", "6136", "32409", "13849", "13847", "13848", "601", "14941", "186"]:  # 可能涉及目标dot的都计入统计
                        if event.target not in self.dotSY:
                            self.dotSY[event.target] = DotCounter("180", self.startTime, self.finalTime, 7, 1, getLength(48, self.haste))
                        if event.target not in self.dotZL:
                            self.dotZL[event.target] = DotCounter("189", self.startTime, self.finalTime, 7, 1, getLength(48, self.haste))
                        if event.target not in self.dotLC:
                            self.dotLC[event.target] = DotCounter("190", self.startTime, self.finalTime, 7, 1, getLength(48, self.haste))
                        if event.target not in self.dotKX:
                            self.dotKX[event.target] = DotCounter("32481", self.startTime, self.finalTime, 10, 6, getLength(48, self.haste))
                    if event.id in ["180", "13849"]:  # 商阳指
                        self.dotSY[event.target].addDot(event.time, 1)
                    if event.id in ["189", "13847"]:  # 钟林
                        self.dotZL[event.target].addDot(event.time, 1)
                    if event.id in ["190", "13848"]:  # 兰摧
                        self.dotLC[event.target].addDot(event.time, 1)
                    if event.id in ["32481"]:  # 快雪上Dot
                        self.dotKX[event.target].addDot(event.time, 1)
                    if event.id in ["182"]:  # 玉石
                        self.lastYushi = event.time
                        numDot = 0
                        numDot += self.dotSY[event.target].checkState(event.time)
                        numDot += self.dotZL[event.target].checkState(event.time)
                        numDot += self.dotLC[event.target].checkState(event.time)
                        numDot += self.dotKX[event.target].checkState(event.time)
                        self.dotSY[event.target].clearDot(event.time)
                        self.dotZL[event.target].clearDot(event.time)
                        self.dotLC[event.target].clearDot(event.time)
                        self.dotKX[event.target].clearDot(event.time)
                        # 是否有cw?
                        cw = self.cwDict.checkState(event.time)
                        if cw:
                            self.dotSY[event.target].addDot(event.time, 1)
                            self.dotZL[event.target].addDot(event.time, 1)
                        if numDot < 4 and not cw:
                            prevCw = self.cwDict.checkState(event.time - 3000)
                            if numDot < 3 or not prevCw:
                                self.ysWrongNum += 1
                                self.ysWrong.append(parseTime((event.time - self.startTime) / 1000))
                        self.ysSum += 1
                        # 芙蓉判定
                        fr = 0
                        if self.frMidNum <= 2:
                            self.frSum += 1
                            self.frMidNum = -1
                            fr = 1  # 玉石之前是否打了芙蓉
                        if not fr and event.time - self.frLastTime > 26000:  # 芙蓉cd转好了
                            self.ysfrWrongNum += 1
                            self.ysfrWrong.append(parseTime((event.time - self.startTime) / 1000))
                        if not fr:
                            if self.syLast != 0:
                                self.dot2WrongNum += 1
                                self.dot2Wrong.append(parseTime((self.syLast - self.startTime) / 1000))
                            if self.zlLast != 0:
                                self.dot2WrongNum += 1
                                self.dot2Wrong.append(parseTime((self.zlLast - self.startTime) / 1000))
                        self.syLast = 0
                        self.zlLast = 0
                    if event.id in ["6134"]:  # 芙蓉刷新商阳
                        self.dotSY[event.target].addDot(event.time, 0)
                    if event.id in ["6135"]:  # 芙蓉刷新钟林
                        self.dotZL[event.target].addDot(event.time, 0)
                    if event.id in ["6136"]:  # 芙蓉刷新兰摧
                        self.dotLC[event.target].addDot(event.time, 0)
                    if event.id in ["32409"]:  # 芙蓉刷新快雪
                        self.dotKX[event.target].addDot(event.time, 0)
                    if event.id in ["601"]:  # 阳明指吞噬事件
                        if event.level == 9:  # 钟林
                            self.dotZL[event.target].clearDot(event.time)
                        elif event.level == 10:  # 商阳
                            self.dotSY[event.target].clearDot(event.time)
                        elif event.level == 11:  # 兰摧
                            self.dotLC[event.target].clearDot(event.time)
                        else:
                            # print("[Tunhai]", event.full_id, event.time, self.bld.info.getSkillName(event.full_id),
                            #       event.damageEff,
                            #       self.bld.info.getName(event.caster), self.bld.info.getName(event.target))
                            pass
                        if self.bh.log["normal"][-1]["skillid"] == "14941" and event.time - self.tunhaiTime < 100:
                            self.bh.log["normal"][-1]["tunhai"] = 1
                            self.numTunhai += 1
                    if event.id in ["14941"]:  # 阳明
                        self.tunhaiTime = event.time
                        self.ymSum += 1
                        numDot = 0
                        numDot += self.dotSY[event.target].checkState(event.time - 10)
                        numDot += self.dotZL[event.target].checkState(event.time - 10)
                        numDot += self.dotLC[event.target].checkState(event.time - 10)
                        numDot += self.dotKX[event.target].checkState(event.time - 10)

                        lsCheck = 0
                        luansa = self.luansaDict.checkState(event.time - 30)
                        if luansa or event.time - self.luansaLastTime < 30:
                            lsCheck = 1

                        if (not self.sf or (numDot == 0 and not lsCheck)) and event.time - self.startTime > 2500:
                            self.ymtgWrongNum += 1
                            self.ymtgWrong.append(parseTime((event.time - self.startTime) / 1000))
                        fx = self.fengxueDict.checkState(event.time - 500)
                        if fx == 2:
                            self.ymfxWrongNum += 1
                            self.ymfxWrong.append(parseTime((event.time - self.startTime) / 1000))
                    if event.id in ["180", "189", "2636", "14941"]:  # 是否有兰摧的判定
                        lc = 0
                        if event.target in self.dotLC:
                            lc = self.dotLC[event.target].checkState(event.time - 30) + self.dotLC[event.target].checkState(event.time)  # 前后都判定防止秒吞
                        if self.lastLcSkill == "2636" and event.id == "2636":  # 前一个技能和这个技能都是快雪，跳过判定
                            pass
                        else:
                            self.lcSum += 1
                            if not lc:
                                # 如果是快雪，任意目标有兰摧，也可以
                                anylc = 0
                                if event.id == "2636":
                                    for key in self.dotLC:
                                        if self.dotLC[key].checkState(event.time - 30):
                                            anylc = 1
                                # 是否缺墨意？如果缺墨意并且在打完玉石或者起手之后，那么就可以打商阳和阳明
                                lowmy = 0
                                nowMoyi = self.moyiInfer[-1][1]
                                if event.id in ["180", "14941"] and nowMoyi < 40 and (event.time - self.lastYushi < 5000 or event.time - self.startTime < 5000):
                                    lowmy = 1
                                # 是否在用快雪和商阳卡布散？如果布散合适的话，也可以没有兰摧就打
                                busanTrick = 0
                                gap = 0
                                if event.id == "180":
                                    gap = 1500
                                elif event.id == "2636":
                                    gap = 4300
                                if gap != 0:
                                    beforeStack = self.busanDict.checkState(event.time)
                                    afterStack = self.busanDict.checkState(event.time + gap)
                                    if beforeStack and not afterStack:
                                        busanTrick = 1
                                # 阳明带乱洒
                                luansa = self.luansaDict.checkState(event.time - 30)
                                if not anylc and not lowmy and not busanTrick and not luansa and event.time - self.luansaLastTime > 30:
                                    self.lcWrongNum += 1
                                    self.lcWrong.append(parseTime((event.time - self.startTime) / 1000))
                        self.lastLcSkill = event.id
                    if event.id in ["180", "189", "2636", "14941", "190"]:  # 芙蓉之后是否打了技能的判定
                        if self.frMidNum != -1:
                            bs = self.busanDict.checkState(event.time - 100)
                            if self.frMidNum <= 1 and self.frBusan and not bs:
                                self.frMidNum += 1
                            else:  # 打错判定
                                self.frSum += 1
                                self.frMidNum = -1
                                self.frWrongNum += 1
                                self.frWrong.append(parseTime((event.time - self.startTime) / 1000))
                    if event.id in ["180", "189", "14941", "190", "186", "182"]:  # 快雪以外的技能
                        if self.kxCurrentNumAll > 0:
                            if self.kxCurrentNum < 5:
                                numKxDot = self.dotKX[event.target].checkState(event.time)
                                bs = self.busanDict.checkState(event.time)
                                if bs and event.time - self.busanDict.log[-1][0] > 8000:  # 卡布散判定
                                    numKxDot = 6
                                if numKxDot < 6:
                                    self.kxloWrongNum += 1
                                    self.kxloWrong.append(parseTime((self.kxLastTime - self.startTime) / 1000))
                            if self.kxCurrentNum > 5:
                                # 如果这个技能打的是芙蓉，就可以多打3跳快雪；如果还能吃到布散，多打几跳都行
                                frSkip = 0
                                if event.id == "186":
                                    bsStack = self.busanDict.checkState(event.time)
                                    if self.kxCurrentNum <= 8 or bsStack:
                                        frSkip = 1
                                if not frSkip and self.kxCurrentNum * 2.5 > self.kxCurrentNumAll:
                                    self.kxhiWrongNum += 1
                                    self.kxhiWrong.append(parseTime((self.kxLastTime - self.startTime) / 1000))
                            self.kxCurrentNumAll = 0
                            self.kxCurrentNum = 0
                    if event.id in ["180"]:  # 商阳
                        self.dotSum += 1
                        self.dot2Sum += 1
                        if self.dotSY[event.target].checkState(event.time - 100):
                            self.dotWrongNum += 1
                            self.dotWrong.append(parseTime((event.time - self.startTime) / 1000))
                        jy = self.jianyuDict.checkState(event.time - 100)
                        if not jy:
                            self.syLast = event.time
                    if event.id in ["189"]:  # 钟林
                        self.dotSum += 1
                        self.dot2Sum += 1
                        if self.dotZL[event.target].checkState(event.time - 100):
                            self.dotWrongNum += 1
                            self.dotWrong.append(parseTime((event.time - self.startTime) / 1000))
                        jy = self.jianyuDict.checkState(event.time - 100)
                        if not jy:
                            self.zlLast = event.time
                    if event.id in ["190"]:  # 兰摧
                        self.dotSum += 1
                        if self.dotLC[event.target].checkState(event.time - 100):
                            self.dotWrongNum += 1
                            self.dotWrong.append(parseTime((event.time - self.startTime) / 1000))
                    if event.id in ["2636"]:  # 快雪
                        if event.time - self.kxLastTime > 10:
                            self.kxCurrentNum += 1
                        if self.kxCurrentNumAll == 0:
                            self.kxSum += 1
                            fx = self.fengxueDict.checkState(event.time - 700)
                            jy = self.jianyuDict.checkState(event.time - 700)
                            if fx != 2 and jy == 0:
                                self.kxfxWrongNum += 1
                                self.kxfxWrong.append(parseTime((event.time - self.startTime) / 1000))
                        self.kxCurrentNumAll += 1
                        self.kxLastTime = event.time
                    if event.id == "186":  # 芙蓉
                        self.frLastTime = event.time
                        self.frMidNum = 0
                        self.frBusan = self.busanDict.checkState(event.time - 100)
                    if event.id in ["13848", "13847"]:  # 乱洒隐藏技能
                        self.luansaLastTime = event.time

                if event.caster == self.mykey and event.scheme == 2:
                    if event.id in ["666"]:
                        syzBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff)
                    elif event.id in ["714"]:
                        zlyxBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff)
                    elif event.id in ["711"]:
                        lcyzBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff)
                    elif event.id in ["24158"]:
                        kxsqBuff.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff)

            elif event.dataType == "Buff":
                if event.id in ["6266"] and event.target == self.mykey:  # 行气血（其实是墨意的瞬发buff，用了以前行气血的逻辑）
                    self.xqxDict.setState(event.time, event.stack)
                    if event.time + 500 > self.moyiActiveTime and (self.moyiBuffNum == 0 or event.stack != 0):
                        # 修正墨意推测
                        self.moyiActiveTime = event.time + 500
                        self.moyiBuffNum = event.stack
                if event.id in ["412"] and event.target == self.mykey:  # 水月无间
                    self.shuiyueDict.setState(event.time, event.stack)
                    # if event.stack > shuiyueStack:
                    #     shuiyueNum += event.stack
                    # shuiyueStack = event.stack
                    if event.time + 500 > self.moyiActiveTime and (self.moyiBuffNum == 0 or event.stack != 0):
                        # 修正墨意推测
                        self.moyiActiveTime = event.time + 500
                        self.moyiBuffNum = event.stack
                if event.id in ["1913"] and event.target == self.mykey:  # cw特效:
                    if event.stack == 1:
                        self.bh.setSpecialSkill(event.id, "cw特效", "17817", event.time, 0, "触发cw特效")
                    self.cwDict.setState(event.time, event.stack)
                if event.id == "2719" and event.target == self.mykey:  # 乱洒
                    self.luansaDict.setState(event.time, event.stack)
                if event.id == "1487" and event.target == self.mykey:  # 布散
                    self.busanDict.setState(event.time, event.stack)
                if event.id == "24205" and event.target == self.mykey:  # 逢雪
                    self.fengxueDict.setState(event.time, event.stack)
                if event.id == "24599" and event.target == self.mykey:  # 溅玉
                    self.jianyuDict.setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

        self.sumPlayer = 0
        for key in self.bld.info.player:
            liveCount = self.battleDict[key].buffTimeIntegral(exclude=self.bh.badPeriodDpsLog)  # 存活时间比例
            if self.battleDict[key].sumTime(exclude=self.bh.badPeriodDpsLog) - liveCount < 8000:  # 脱战缓冲时间
                liveCount = self.battleDict[key].sumTime(exclude=self.bh.badPeriodDpsLog)
            self.battleTimeDict[key] = liveCount
            self.sumPlayer += liveCount / self.battleDict[key].sumTime(exclude=self.bh.badPeriodDpsLog)

        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100

        self.completeSecondState()

        # 计算DPS列表(Part 7)

        pass

        # 整体
        self.result["skill"] = {}
        self.result["skill"]["general"] = {}

        self.calculateSkillOverall()

        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)

        self.result["replay"]["heat"] = {}

        # self.result["replay"]["heat"][dot]["timeline"]

        # 实现一个展示增益覆盖率的逻辑
        self.myRdpsSource = {}
        for player in self.act.rdps["player"]:
            if player == self.mykey:
                self.myRdpsSource = self.act.rdps["player"][player]["namedSource"]
                self.myRdpsSkill = self.act.rdps["player"][player]["namedSkill"]
                self.myAdjustedTime = self.act.rdps["player"][player]["adjustedTime"]
        self.result["boost"] = self.myRdpsSource
        self.result["fraction"] = {"table": self.myRdpsSkill, "time": self.myAdjustedTime}

        # print("[self.myRdpsSkill]", self.myRdpsSkill)

        # 阳明
        ymskill = self.calculateSkillInfo("ymz", "14941")
        self.result["skill"]["ymz"]["tunhai"] = self.numTunhai
        self.result["skill"]["ymz"]["rdps"] = 0
        if "阳明指" in self.myRdpsSkill:
            self.result["skill"]["ymz"]["rdps"] = int(self.myRdpsSkill["阳明指"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["ymz"]["rdpsRate"] = roundCent(self.result["skill"]["ymz"]["rdps"] / self.result["skill"]["general"]["rdps"])

        # 商阳
        self.calculateSkillInfoDirect("syz", syzBuff)
        self.result["skill"]["syz"]["rdps"] = 0
        if "商阳指(持续)" in self.myRdpsSkill:
            self.result["skill"]["syz"]["rdps"] = int(self.myRdpsSkill["商阳指(持续)"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["syz"]["rdpsRate"] = roundCent(self.result["skill"]["syz"]["rdps"] / self.result["skill"]["general"]["rdps"])
        overallHeat = []
        for target in self.dotSY:
            singleHeat = self.dotSY[target].getHeatTable(500, 1)["timeline"]
            if overallHeat == []:
                overallHeat = singleHeat
            else:  # 合并
                for i in range(len(singleHeat)):
                    overallHeat[i] = max(overallHeat[i], singleHeat[i])
        for i in range(len(overallHeat)):
            overallHeat[i] = int(overallHeat[i] * 100)
        self.result["replay"]["heat"]["shangyang"] = {"interval": 500, "timeline": overallHeat}

        ic = IntervalCounter(self.startTime, self.finalTime)
        for target in self.dotSY:
            ic.recordLog(self.dotSY[target].log)
        dotCombine = BuffCounter("?", self.startTime, self.finalTime)
        dotCombine.log = ic.export()
        num = self.battleTimeDict[self.mykey]
        sum = dotCombine.buffTimeIntegral(exclude=self.bh.badPeriodDpsLog)
        self.result["skill"]["syz"]["cover"] = roundCent(safe_divide(sum, num))

        # 钟林
        self.calculateSkillInfoDirect("zlyx", zlyxBuff)
        self.result["skill"]["zlyx"]["rdps"] = 0
        if "钟林毓秀(持续)" in self.myRdpsSkill:
            self.result["skill"]["zlyx"]["rdps"] = int(self.myRdpsSkill["钟林毓秀(持续)"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["zlyx"]["rdpsRate"] = roundCent(self.result["skill"]["zlyx"]["rdps"] / self.result["skill"]["general"]["rdps"])
        overallHeat = []
        for target in self.dotZL:
            singleHeat = self.dotZL[target].getHeatTable(500, 1)["timeline"]
            if overallHeat == []:
                overallHeat = singleHeat
            else:  # 合并
                for i in range(len(singleHeat)):
                    overallHeat[i] = max(overallHeat[i], singleHeat[i])
        for i in range(len(overallHeat)):
            overallHeat[i] = int(overallHeat[i] * 100)
        self.result["replay"]["heat"]["zhonglin"] = {"interval": 500, "timeline": overallHeat}

        ic = IntervalCounter(self.startTime, self.finalTime)
        for target in self.dotZL:
            ic.recordLog(self.dotZL[target].log)
        dotCombine = BuffCounter("?", self.startTime, self.finalTime)
        dotCombine.log = ic.export()
        num = self.battleTimeDict[self.mykey]
        sum = dotCombine.buffTimeIntegral(exclude=self.bh.badPeriodDpsLog)
        self.result["skill"]["zlyx"]["cover"] = roundCent(safe_divide(sum, num))

        # 兰摧
        self.calculateSkillInfoDirect("lcyz", lcyzBuff)
        self.result["skill"]["lcyz"]["rdps"] = 0
        if "兰摧玉折(持续)" in self.myRdpsSkill:
            self.result["skill"]["lcyz"]["rdps"] = int(self.myRdpsSkill["兰摧玉折(持续)"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["lcyz"]["rdpsRate"] = roundCent(self.result["skill"]["lcyz"]["rdps"] / self.result["skill"]["general"]["rdps"])
        overallHeat = []
        for target in self.dotLC:
            singleHeat = self.dotLC[target].getHeatTable(500, 1)["timeline"]
            if overallHeat == []:
                overallHeat = singleHeat
            else:  # 合并
                for i in range(len(singleHeat)):
                    overallHeat[i] = max(overallHeat[i], singleHeat[i])
        for i in range(len(overallHeat)):
            overallHeat[i] = int(overallHeat[i] * 100)
        self.result["replay"]["heat"]["lancui"] = {"interval": 500, "timeline": overallHeat}

        ic = IntervalCounter(self.startTime, self.finalTime)
        for target in self.dotLC:
            ic.recordLog(self.dotLC[target].log)
        dotCombine = BuffCounter("?", self.startTime, self.finalTime)
        dotCombine.log = ic.export()
        num = self.battleTimeDict[self.mykey]
        sum = dotCombine.buffTimeIntegral(exclude=self.bh.badPeriodDpsLog)
        self.result["skill"]["lcyz"]["cover"] = roundCent(safe_divide(sum, num))

        # 快雪
        kxskill = self.calculateSkillInfo("kxsq", "2636")
        self.result["skill"]["kxsq"]["rdps"] = 0
        if "快雪时晴" in self.myRdpsSkill:
            self.result["skill"]["kxsq"]["rdps"] = int(self.myRdpsSkill["快雪时晴"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["kxsq"]["rdpsRate"] = roundCent(self.result["skill"]["kxsq"]["rdps"] / self.result["skill"]["general"]["rdps"])

        self.calculateSkillInfoDirect("kxsqdot", kxsqBuff)
        self.result["skill"]["kxsqdot"]["rdps"] = 0
        if "快雪时晴(持续)" in self.myRdpsSkill:
            self.result["skill"]["kxsqdot"]["rdps"] = int(self.myRdpsSkill["快雪时晴(持续)"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["kxsqdot"]["rdpsRate"] = roundCent(self.result["skill"]["kxsqdot"]["rdps"] / self.result["skill"]["general"]["rdps"])
        overallHeat = []
        for target in self.dotKX:
            singleHeat = self.dotKX[target].getHeatTable(500, 1)["timeline"]
            if overallHeat == []:
                overallHeat = singleHeat
            else:  # 合并
                for i in range(len(singleHeat)):
                    overallHeat[i] = max(overallHeat[i], singleHeat[i])
        for i in range(len(overallHeat)):
            overallHeat[i] = int(overallHeat[i] * 100)
        self.result["replay"]["heat"]["kuaixue"] = {"interval": 500, "timeline": overallHeat}

        ic = IntervalCounter(self.startTime, self.finalTime)
        for target in self.dotKX:
            ic.recordLog(self.dotKX[target].log)
        dotCombine = BuffCounter("?", self.startTime, self.finalTime)
        dotCombine.log = ic.export()
        num = self.battleTimeDict[self.mykey]
        sum = dotCombine.buffTimeIntegral(exclude=self.bh.badPeriodDpsLog)
        self.result["skill"]["kxsqdot"]["cover"] = roundCent(safe_divide(sum, num))

        # 玉石
        ysjfSkill = self.calculateSkillInfo("ysjf", "182")
        self.result["skill"]["ysjf"]["rdps"] = 0
        if "玉石俱焚" in self.myRdpsSkill:
            self.result["skill"]["ysjf"]["rdps"] = int(self.myRdpsSkill["玉石俱焚"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["ysjf"]["rdpsRate"] = roundCent(self.result["skill"]["ysjf"]["rdps"] / self.result["skill"]["general"]["rdps"])

        # 芙蓉
        frbdSkill = self.calculateSkillInfo("frbd", "186")
        self.result["skill"]["frbd"]["rdps"] = 0
        if "芙蓉并蒂" in self.myRdpsSkill:
            self.result["skill"]["frbd"]["rdps"] = int(self.myRdpsSkill["芙蓉并蒂"]["sum"] / self.myAdjustedTime * 1000)
        self.result["skill"]["frbd"]["rdpsRate"] = roundCent(self.result["skill"]["frbd"]["rdps"] / self.result["skill"]["general"]["rdps"])

        # 一部分公有逻辑可以在其它心法实现后提到外面
        self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency(base="dps")

        # print("[Efficiency]", self.result["skill"]["general"]["efficiency"])
        # print("[Boost]", self.result["boost"])
        # print("[Skill]")
        # for line in self.result["skill"]:
        #     print(line)
        #     print(self.result["skill"][line])

        # code 21 保持gcd不要空转
        gcd = self.result["skill"]["general"]["efficiency"]
        res = {"code": 21, "cover": gcd, "rate": roundCent(gcd)}
        res["status"] = getRateStatus(res["rate"], 95, 90, 85)
        self.result["review"]["content"].append(res)

        # code 1001 优先使用`兰摧玉折`
        res = {"code": 1001, "failTime": self.lcWrong, "num": self.lcWrongNum, "sum": self.lcSum, "rate": roundCent(1 - safe_divide(self.lcWrongNum, self.lcSum))}
        res["status"] = getRateStatus(res["rate"], 100, 0, 0)
        self.result["review"]["content"].append(res)

        # code 1002 使`玉石俱焚`覆盖到全部的持续伤害效果
        res = {"code": 1002, "failTime": self.ysWrong, "num": self.ysWrongNum, "sum": self.ysSum, "rate": roundCent(1 - safe_divide(self.ysWrongNum, self.ysSum))}
        res["status"] = getRateStatus(res["rate"], 100, 98, 95)
        self.result["review"]["content"].append(res)

        # code 1003 在`芙蓉并蒂`后立刻结算持续伤害
        res = {"code": 1003, "failTime": self.frWrong, "num": self.frWrongNum, "sum": self.frSum, "rate": roundCent(1 - safe_divide(self.frWrongNum, self.frSum))}
        res["status"] = getRateStatus(res["rate"], 100, 0, 0)
        self.result["review"]["content"].append(res)

        # code 1004 尽可能使用`芙蓉并蒂`
        res = {"code": 1004, "failTime": self.ysfrWrong, "num": self.ysfrWrongNum, "sum": self.ysSum, "rate": roundCent(1 - safe_divide(self.ysfrWrongNum, self.ysSum))}
        res["status"] = getRateStatus(res["rate"], 100, 98, 95)
        self.result["review"]["content"].append(res)

        # code 1005 使用瞬发`阳明指`尝试触发`踏歌`
        res = {"code": 1005, "failTime": self.ymtgWrong, "num": self.ymtgWrongNum, "sum": self.ymSum, "rate": roundCent(1 - safe_divide(self.ymtgWrongNum, self.ymSum))}
        res["status"] = getRateStatus(res["rate"], 100, 98, 95)
        self.result["review"]["content"].append(res)

        # code 1006 使用瞬发`阳明指`尝试触发`雪中行`
        res = {"code": 1006, "failTime": self.ymfxWrong, "num": self.ymfxWrongNum, "sum": self.ymSum, "rate": roundCent(1 - safe_divide(self.ymfxWrongNum, self.ymSum))}
        res["status"] = getRateStatus(res["rate"], 100, 95, 0)
        self.result["review"]["content"].append(res)

        # code 1007 在`逢雪`气劲层数最大时使用`快雪时晴`
        res = {"code": 1007, "failTime": self.kxfxWrong, "num": self.kxfxWrongNum, "sum": self.kxSum, "rate": roundCent(1 - safe_divide(self.kxfxWrongNum, self.kxSum))}
        res["status"] = getRateStatus(res["rate"], 100, 98, 95)
        self.result["review"]["content"].append(res)

        # code 1008 打满`快雪时晴`的跳数
        res = {"code": 1008, "failTime": self.kxloWrong, "num": self.kxloWrongNum, "sum": self.kxSum, "rate": roundCent(1 - safe_divide(self.kxloWrongNum, self.kxSum))}
        res["status"] = getRateStatus(res["rate"], 100, 0, 0)
        self.result["review"]["content"].append(res)

        # code 1009 避免重复施展`快雪时晴`
        res = {"code": 1009, "failTime": self.kxhiWrong, "num": self.kxhiWrongNum, "sum": self.kxSum, "rate": roundCent(1 - safe_divide(self.kxhiWrongNum, self.kxSum))}
        res["status"] = getRateStatus(res["rate"], 100, 0, 0)
        self.result["review"]["content"].append(res)

        # code 1010 避免重复施展持续伤害效果
        res = {"code": 1010, "failTime": self.dotWrong, "num": self.dotWrongNum, "sum": self.dotSum, "rate": roundCent(1 - safe_divide(self.dotWrongNum, self.dotSum))}
        res["status"] = getRateStatus(res["rate"], 100, 98, 95)
        self.result["review"]["content"].append(res)

        # code 1011 将持续伤害技能延后到`溅玉`期间
        res = {"code": 1011, "failTime": self.dot2Wrong, "num": self.dot2WrongNum, "sum": self.dot2Sum, "rate": roundCent(1 - safe_divide(self.dot2WrongNum, self.dot2Sum))}
        res["status"] = getRateStatus(res["rate"], 100, 95, 0)
        self.result["review"]["content"].append(res)

        self.result["review"]["intro"] = {"code": 1000}

        self.calculateSkillFinal()

        # print("[Review]")
        # for line in self.result["review"]["content"]:
        #     print(line)

        # print("[HuajianTest]")
        # # print(self.result["replay"]["moyi"])
        # for line in self.result["replay"]["normal"]:
        #     print(line)
        # for line in self.result["replay"]["special"]:
        #     print(line)
        # print("[Shangyang]")
        # for target in self.dotSY:
        #     print(target, self.bld.info.getName(target))
        #     for line in self.dotSY[target].log:
        #         print(line)
        # print("[Zhonglin]")
        # for target in self.dotZL:
        #     print(target, self.bld.info.getName(target))
        #     for line in self.dotZL[target].log:
        #         print(line)
        # print("[Lancui]")
        # for target in self.dotLC:
        #     print(target, self.bld.info.getName(target))
        #     for line in self.dotLC[target].log:
        #         print(line)
        # print("[Kuaixue]")
        # for target in self.dotKX:
        #     print(target, self.bld.info.getName(target))
        #     for line in self.dotKX[target].log:
        #         print(line)


    def replay(self):
        '''
        开始复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
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
        super().__init__(config, fileNameInfo, path, bldDict, window, myname, actorData)
        self.public = 1  # 暂时强制公开，反正没什么东西  TODO 更改设置中的选项，简化内容
        self.myname = myname
        self.occ = "huajianyou"
        self.occCode = "2d"
        self.occPrint = "花间"
        self.occColor = getColor(self.occCode)
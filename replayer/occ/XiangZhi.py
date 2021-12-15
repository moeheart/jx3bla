# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment

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

XIANGZHI_QIXUE = {
    '14237':'雪海',
    '14247':'太和',
    '23313':'枕流',
    '24020':'流音',
    '14405':'谪仙',
    '14384':'自赏',
    '14406':'寸光阴',
    '26728':'诗上',
    '14244':'凝绝',
    '14359':'棋宫',
    '14242':'掷杯',
    '19308':'思议',
    '14238':'红隙',
    '14373':'秋鸿',
    '17521':'争簇',
    '14439':'织心',
    '14164':'超然',
    '14361':'引芳',
    '14313':'井仪',
    '22029':'绝唱',
    '14163':'相依',
    '14557':'贯珠',
    '18718':'凝眉',
    '22030':'无尽藏',
    '14464':'蔚风',
    '18382':'风入松',
    '14286':'流霜',
    '14285':'殊曲',
    '14248':'寒酒',
    '14253':'犹香',
    '14251':'笙簧',
    '22797':'蒹葭',
    '14461':'鸣鸾',
    '14167':'寿生',
    '14155':'剡注',
    '14442':'桑柔',
    '14256':'石间意',
    '14169':'一指回鸾',
    '14254':'温语',
    '14249':'平吟',
    '23678':'乐情',
    '14874':'捣衣',
    '14470':'天音知脉',
    '18819':'庄周梦',
    '22808':'大韶',
    '15068':'琴音共鸣',
    '26772':'行云',
    '25234':'绕梁',
    '25235':'不器',
    '25236':'古道',
    '25229':'游太清',
    '28131':'祭子期',
    '29069':'游羽',
    '28248':'潋滟',
    '29003':'敛意',
    '28210':'江永',
}

def getXiangZhiQixue(id):
    '''
    根据ID获取奶歌奇穴名.
    '''
    if id in XIANGZHI_QIXUE:
        return XIANGZHI_QIXUE[id]
    else:
        # return "未知"
        return id  # 方便在技改附近批量更新

class ShieldCounterNew(BuffCounter):
    '''
    盾的统计类.
    继承buff的统计类，加入获得次数、破盾次数等指标.
    '''

    def inferFirst(self):
        '''
        根据记录尝试推导战斗开始前是否存在盾，若存在则强制修改最开始的情形为有盾.
        '''
        if len(self.log) > 1 and self.log[1][1] == 0:
            self.log[0][1] = 1

    def countCast(self):
        '''
        计算盾施放的次数.
        根据buff做推断，消失间隔小于500ms的视为没有消失.
        returns:
        - num 盾施放的次数.
        '''
        num = 0
        lastTime = 0
        lastStack = 0
        for line in self.log:
            if line[1] == 1 and lastStack == 0 and line[0] - lastTime > 500:
                num += 1
            lastTime = line[0]
            lastStack = line[1]
        return num

    def countBreak(self):
        '''
        计算破盾的次数.
        直接通过施放的次数推导.
        returns:
        - num 破盾的次数.
        '''
        num = self.countCast()
        if self.checkState(self.finalTime) == 1:
            num -= 1
        return num

    def getHeatTable(self, interval=500):
        '''
        获取单个玩家的覆盖率热力表.
        params:
        - interval: 间隔
        returns:
        - 结果对象
        '''
        time = 0
        nowi = 0
        result = {"interval": interval, "timeline": []}
        for nowTime in range(self.startTime, self.finalTime, interval):
            single = 0
            while nowi < len(self.log) and self.log[nowi][0] < nowTime:
                nowi += 1
            if len(self.log) > 0 and nowi > 0:
                single = self.log[nowi-1][1]
            result["timeline"].append(single)
        return result

    def __init__(self, shieldLog, startTime, finalTime):
        '''
        初始化.
        '''
        super().__init__(shieldLog, startTime, finalTime)

class HotCounter(BuffCounter):
    '''
    HOT的统计类.
    继承buff的统计类，考虑HOT的持续时间等指标。
    '''

    def getHeatTable(self, interval=500):
        '''
        获取单个玩家的覆盖率热力表.
        params:
        - interval: 间隔
        returns:
        - 结果对象
        '''
        nowi = 0
        result = {"interval": interval, "timeline": []}
        for nowTime in range(self.startTime, self.finalTime, interval):
            single = 0
            while nowi < len(self.log) and self.log[nowi][0] < nowTime:
                nowi += 1
            if len(self.log) > 0 and nowi > 0 and self.log[nowi-1][1] > 0:
                single = (self.log[nowi-1][2] + self.log[nowi-1][0] - nowTime) / self.log[nowi-1][2]
            # single = int(single * 100)
            result["timeline"].append(single)
        return result

    def setState(self, time, stack, duration):
        '''
        设置特定时间点buff的层数.
        无论是获得还是消亡均可用这个方法。对应的层数的有效时间即是这个时刻到下一个时刻中间的部分。
        params:
        - time: 获得buff的时刻.
        - stack: buff层数，可以为0.
        - duration: 预计的持续时间.
        '''
        self.log.append([int(time), int(stack), int(duration)])

    def __init__(self, shieldLog, startTime, finalTime):
        '''
        初始化.
        '''
        super().__init__(shieldLog, startTime, finalTime)

class SkillLogCounter():
    '''
    技能统计类.
    TODO: 扩展这个类的功能，支持更多统计.
    '''
    skillLog = []
    actLog = []
    startTime = 0
    finalTime = 0
    speed = 3770
    sumBusyTime = 0
    sumSpareTime = 0

    def getLength(self, length):
        flames = calculFramesAfterHaste(self.speed, length)
        return flames * 0.0625 * 1000

    def analysisSkillData(self):
        for line in self.skillLog:
            if line[1] in [15181, 15082, 25232]:  #奶歌常见的自动施放技能：影子宫，影子宫，桑柔
                continue
            elif line[1] in [14137, 14300]:  # 宫，变宫
                self.actLog.append([line[0] - self.getLength(24), self.getLength(24)])
            elif line[1] in [14140, 14301]:  # 徵，变徵
                self.actLog.append([line[0] - self.getLength(16), self.getLength(16)])
            else:
                self.actLog.append([line[0], self.getLength(24)])

        self.actLog.sort(key=lambda x: x[0])

        nowTime = self.startTime
        self.sumBusyTime = 0
        self.sumSpareTime = 0
        for line in self.actLog:
            if line[0] > nowTime:
                self.sumSpareTime += line[0] - nowTime
                self.sumBusyTime += line[1]
                nowTime = line[0] + line[1]
            elif line[0] + line[1] > nowTime:
                self.sumBusyTime += line[0] + line[1] - nowTime
                nowTime = line[0] + line[1]

    def __init__(self, skillLog, startTime, finalTime, speed=3770):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed

def countCluster(teamLog, teamLastTime, event):
    '''
    根据HOT的获取事件提取组队聚类信息.
    params:
    - teamLog: 玩家两两配对的事件.
    - teamLastTime: 玩家上次获取HOT的时间.
    - event: HOT事件.
    '''
    if event.target in teamLastTime:
        teamLastTime[event.target] = event.time
    else:
        return teamLog, teamLastTime
    # print("[teamLastTime]", event.time, teamLastTime)
    for player in teamLastTime:
        if event.time - teamLastTime[player] < 100:
            if player not in teamLog[event.target]:
                teamLog[event.target][player] = 0
            teamLog[event.target][player] += 1
            if event.target != player:
                if event.target not in teamLog[player]:
                    teamLog[player][event.target] = 0
                teamLog[player][event.target] += 1
    return teamLog, teamLastTime

def finalCluster(teamLog):
    '''
    根据组队聚类信息计算聚类结果.
    params:
    - teamLog: 玩家两两配对的事件.
    returns:
    - teamCluster: 聚类结果.
    - numCluster: 聚类结果中每个类别的数量.
    '''
    teamCluster = {}
    for player in teamLog:
        teamCluster[player] = 0
    nTeam = 0
    numCluster = [0]

    # 从前五名开始按一定阈值聚类
    for player in teamLog:
        if teamCluster[player] != 0:
            continue
        singleRes = []
        for playerT in teamLog[player]:
            singleRes.append([playerT, teamLog[player][playerT]])
        singleRes.sort(key=lambda x: -x[1])
        j = 5
        while len(singleRes) <= j or (j >= 1 and singleRes[j-1][1] / (singleRes[j][1] + 1e-10) >= 3):
            j -= 1
        # print(singleRes)
        # print(j)
        if j >= 1:
            nTeam += 1
            numCluster.append(0)
            for i in range(0, j+1):
                teamCluster[singleRes[i][0]] = nTeam
                numCluster[nTeam] += 1

    # 为剩余角色聚类
    hasRemain = 0
    for player in teamCluster:
        if teamCluster[player] == 0:
            if not hasRemain:
                hasRemain = 1
                nTeam += 1
                numCluster.append(0)
            teamCluster[player] = nTeam
            numCluster[nTeam] += 1

    return teamCluster, numCluster

class XiangZhiProWindow():
    '''
    奶歌复盘pro界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

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
        tb.AppendContext("首领：", justify="right")
        tb.AppendContext(self.result["overall"]["boss"], color="#ff0000")
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

            b2 = tk.Button(frame2, text='导出', height=1, command=self.exportEquipment)  # TODO: 实现
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
        frame4.place(x = 430, y = 170)
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
        text = "数量：%d\n"%self.result["skill"]["meihua"]["num"]
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
        text = "数量：%d\n"%self.result["skill"]["zhi"]["num"]
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
        text = "数量：%d\n"%self.result["skill"]["jue"]["num"]
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
        text = "数量：%d\n"%self.result["skill"]["shang"]["num"]
        text = text + "延迟：%dms\n" % self.result["skill"]["shang"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["shang"]["HPS"]
        text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["shang"]["cover"])
        label = tk.Label(frame5_4, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_5 = tk.Frame(frame5, width=180, height=95)
        frame5_5.place(x=0, y=100)
        frame5_5.photo = tk.PhotoImage(file="icons/7168.png")
        label = tk.Label(frame5_5, image=frame5_5.photo)
        label.place(x=5, y=25)
        ToolTip(label, "相依")
        text = "数量：%d\n"%self.result["skill"]["xiangyi"]["num"]
        text = text + "HPS：%d\n" % self.result["skill"]["xiangyi"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["xiangyi"]["effRate"])
        label = tk.Label(frame5_5, text=text, justify="left")
        label.place(x=60, y=25)

        frame5_6 = tk.Frame(frame5, width=180, height=95)
        frame5_6.place(x=180, y=100)
        frame5_6.photo = tk.PhotoImage(file="icons/7173.png")
        label = tk.Label(frame5_6, image=frame5_6.photo)
        label.place(x=5, y=25)
        ToolTip(label, "宫")
        text = "数量：%d\n"%self.result["skill"]["gong"]["num"]
        text = text + "延迟：%dms\n" % self.result["skill"]["gong"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["gong"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["gong"]["effRate"])
        label = tk.Label(frame5_6, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_7 = tk.Frame(frame5, width=180, height=95)
        frame5_7.place(x=360, y=100)
        frame5_7.photo = tk.PhotoImage(file="icons/7175.png")
        label = tk.Label(frame5_7, image=frame5_7.photo)
        label.place(x=5, y=25)
        ToolTip(label, "羽")
        text = "数量：%d\n"%self.result["skill"]["yu"]["num"]
        text = text + "延迟：%dms\n" % self.result["skill"]["yu"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["yu"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["yu"]["effRate"])
        label = tk.Label(frame5_7, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_8 = tk.Frame(frame5, width=180, height=95)
        frame5_8.place(x=540, y=100)
        text = "桑柔DPS：%d\n"%self.result["skill"]["general"]["SangrouDPS"]
        text = text + "庄周梦DPS：%d\n" % self.result["skill"]["general"]["ZhuangzhouDPS"]
        text = text + "玉简DPS：%d\n" % self.result["skill"]["general"].get("YujianDPS", 0)
        text = text + "战斗效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiency"])
        label = tk.Label(frame5_8, text=text, justify="left")
        label.place(x=20, y=20)

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
                canvas6.create_image(10, 40, image=canvas6.im["7059"])
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
                canvas6.create_image(10, 40, image=canvas6.im["7172"])
                canvas6.create_image(30, 40, image=canvas6.im["7176"])
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
        tb.AppendHeader("DPS", "全程去除庄周梦增益后的DPS，注意包含重伤时间。")
        tb.AppendHeader("覆盖率", "梅花三弄的覆盖率。")
        tb.AppendHeader("破盾次数", "破盾次数，包含盾受到伤害消失、未刷新自然消失、及穿透消失。")
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
        # TODO 实现
        tb = TableConstructor(self.config, frame8sub)
        tb.AppendHeader("数值分：", "对治疗数值的打分，包括治疗量、各个技能数量。")
        tb.AppendContext("0", width=9)
        tb.AppendContext("F")
        tb.EndOfLine()
        tb.AppendHeader("统计分：", "对统计结果的打分，包括梅花三弄和HOT的覆盖率。")
        tb.AppendContext("0", width=9)
        tb.AppendContext("F")
        tb.EndOfLine()
        tb.AppendHeader("操作分：", "对操作表现的打分，包括战斗效率，各个技能延迟。")
        tb.AppendContext("0", width=9)
        tb.AppendContext("F")
        tb.EndOfLine()
        tb.AppendHeader("总评：", "综合计算这几项的结果。")
        tb.AppendContext("0", width=9)
        tb.AppendContext("F")
        tb.EndOfLine()
        tk.Label(frame8, text="分数统计在收集一定量的数据后生效。").place(x=10, y=150)

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
        self.mask = config.mask
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
        self.result["overall"]["calTank"] = self.config.xiangzhiCalTank
        self.result["overall"]["mask"] = self.config.mask

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"', '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
                self.npcKey = key
                break

        # 记录盾的存在情况与减疗
        shieldLogDict = {}
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
            # if len(XiangZhiList) >= 2:
            #     nameList = []
            #     for line in XiangZhiList:
            #         nameList.append(namedict[line][0])
            #     s = str(nameList)
            #     raise Exception('奶歌的数量不止一个，请手动指示ID。可能的ID为：%s' % s)
            # elif len(XiangZhiList) == 0:
            #     raise Exception('没有找到奶歌，请确认数据是否正确')
            # else:
            #     self.mykey = XiangZhiList[0]
            #     self.myname = self.bld.info.player[self.mykey].name
            #     print("自动推断奶歌角色名为：%s"%self.myname)
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
                        if event.target not in shieldLogDict:
                            shieldLogDict[event.target] = []
                        shieldLogDict[event.target].append([event.time, 1])
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
                    if event.target not in shieldLogDict:
                        shieldLogDict[event.target] = []
                    shieldLogDict[event.target].append([event.time, event.stack])
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
        # TODO 实现
        self.result["equip"] = {"available": 0}
        if self.bld.info.player[self.mykey].equip != {}:
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
            if not self.config.xiangzhiSpeedForce:
                self.haste = self.result["equip"]["haste"]
            self.result["equip"]["raw"] = strEquip

        self.result["qixue"] = {"available": 0}
        if self.bld.info.player[self.mykey].qx != {}:
            self.result["qixue"]["available"] = 1
            for key in self.bld.info.player[self.mykey].qx:
                self.result["qixue"][key] = getXiangZhiQixue(self.bld.info.player[self.mykey].qx[key]["2"])

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
            numSmall = 0

        numHeal = 0
        numEffHeal = 0
        numAbsorb = 0
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
        mhsnSkill = SkillCounter("14231", self.startTime, self.finalTime, self.haste)  # 梅花三弄
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
        battleDict = {}
        firstHitDict = {}
        for line in self.bld.info.player:
            shangBuffDict[line] = HotCounter("9459", self.startTime, self.finalTime)  # 商，9460=殊曲，9461=洞天
            jueBuffDict[line] = HotCounter("9463", self.startTime, self.finalTime)  # 角，9460=殊曲，9461=洞天
            battleDict[line] = BuffCounter("0", self.startTime, self.finalTime)  # 战斗状态统计
            firstHitDict[line] = 0
            teamLog[line] = {}
            teamLastTime[line] = 0
        lastSkillTime = self.startTime

        # 杂项
        fengleiActiveTime = self.startTime
        youxiangHeal = 0
        pingyinHeal = 0
        gudaoHeal = 0

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        bhSkill = "0"
        bhTimeStart = 0
        bhTimeEnd = 0
        bhNum = 0
        bhHeal = 0
        bhHealEff = 0
        bhDelay = 0
        bhDelayNum = 0
        bhBusy = 0
        skillNameDict = {"0": "未知",
                         "14231": "梅花三弄",
                         "18864": "宫",
                         "14360": "宫",
                         "16852": "宫",
                         # "14140": "徵",
                         "14362": "徵",
                         # "14301": "徵",
                         "18865": "徵",
                         "14141": "羽",
                         "14354": "羽",
                         "14355": "羽",
                         "14356": "羽",
                         "14138": "商",
                         "14139": "角",
                         "9002": "扶摇直上",
                         "9003": "蹑云逐月",
                         "14169": "一指回鸾", }
        specialNameDict = {"14081": "孤影化双",
                           "14075": "云生结海",
                           "14069": "高山流水",
                           "14076": "青霄飞羽",
                           "21324": "青霄飞羽·落",
                           "15039": "移形换影",
                           "15040": "移形换影",
                           "15041": "移形换影",
                           "15042": "移形换影",
                           "15043": "移形换影",
                           "15044": "移形换影",
                           "18838": "高山流水·切换",
                           "18839": "高山流水·切换",
                           "18841": "梅花三弄·切换",
                           "18842": "梅花三弄·切换",
                           "18845": "阳春白雪·切换",
                           "18846": "阳春白雪·切换",
                           }
        skillIconDict = {"0": "未知",
                         "14231": "7059",
                         "18864": "7173",
                         "14360": "7173",
                         "16852": "7173",
                         # "14140": "7174",
                         "14362": "7174",
                         # "14301": "7174",
                         "18865": "7174",
                         "14141": "7175",
                         "14354": "7175",
                         "14355": "7175",
                         "14356": "7175",
                         "14138": "7172",
                         "14139": "7176",
                         "14081": "7052",
                         "14075": "7048",
                         "14069": "7080",
                         "14076": "7078",
                         "21324": "7128",
                         "15039": "7066",
                         "15040": "7066",
                         "15041": "7066",
                         "15042": "7066",
                         "15043": "7066",
                         "15044": "7066",
                         "18838": "7080",
                         "18839": "7080",
                         "18841": "7059",
                         "18842": "7059",
                         "18845": "7077",
                         "18846": "7077",
                         "9002": "1485",
                         "9003": "1490",
                         "14169": "7045",
                         }
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
                               # "16852", # 群体宫
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
                               ]
        xiangZhiSpecial = ["20763", "20764", "21321",  # 相依
                           "15039", # 传影子
                           "14150", "14153", # 云生结海
                           "14075", # 云生结海主动
                           "18838", # 梅花切高山
                           "18841", # 高山切梅花
                           "14069", # 高山
                           "14076", # 青霄飞羽
                           "21324", # 青霄飞羽·落
                           "14081", # 孤影施放
                           ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    numAbsorb += event.healEff
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

                    if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey and event.id not in skillNameDict:
                        # 打印所有有治疗量的技能，以进行整理
                        # print("[Heal]", event.id, event.heal)
                        pass

                    if event.caster == self.mykey and event.scheme == 1 and event.id not in xiangZhiUnimportant: # 影子宫、桑柔等需要过滤的技能
                        skillLog.append([event.time, event.id])

                        # 若技能没有连续，则在战斗回放中记录技能
                        if ((event.id not in skillNameDict or skillNameDict[event.id] != skillNameDict[bhSkill]) and event.id not in xiangZhiSpecial)\
                            or event.time - lastSkillTime > 3000:
                            # 记录本次技能
                            # print("[ReplaceSkill]", event.id, bhSkill)
                            # 此处的逻辑完全可以去掉，保留这个逻辑就是为了监控哪些是值得挖掘的隐藏技能
                            if bhSkill != "0":
                                bh.setNormalSkill(bhSkill, skillNameDict[bhSkill], skillIconDict[bhSkill],
                                                  bhTimeStart, bhTimeEnd - bhTimeStart, bhNum, bhHeal,
                                                  roundCent(bhHealEff / (bhHeal + 1e-10)),
                                                  int(bhDelay / (bhDelayNum + 1e-10)), bhBusy, "")
                            bhSkill = "0"
                            bhTimeStart = 0
                            bhNum = 0
                            bhHeal = 0
                            bhHealEff = 0
                            bhDelay = 0
                            bhDelayNum = 0
                            bhBusy = 0
                        if bhSkill == "0" and event.id in skillNameDict:
                            bhSkill = event.id
                            bhTimeStart = event.time  # 并非最终结果，对于读条技能可能会修正
                        # 分技能进行处理
                        if event.id in ["14231"]:  # 梅花三弄
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            lastSkillTime = mhsnSkill.recordSkill(event.time, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        elif event.id in ["18864", "14360", "16852"]:  # 宫实际效果
                            if bhNum == 0:
                                bhTimeStart -= getLength(24, self.haste)
                            if event.time - lastSkillTime > 100 or bhNum == 0:
                                bhNum += 1
                                bhDelayNum += 1
                                bhDelay += max(event.time - lastSkillTime - getLength(24, self.haste), 0)
                                bhBusy += getLength(24, self.haste)
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            gongSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                            lastSkillTime = event.time
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14362", "18865"]:  # 徵实际效果
                            if bhNum == 0:
                                bhTimeStart -= getLength(8, self.haste)
                            if event.time - lastSkillTime > 100 or bhNum == 0:
                                bhNum += 1
                                bhDelayNum += 1
                                bhDelay += max(event.time - lastSkillTime - getLength(8, self.haste), 0)
                                bhBusy += getLength(8, self.haste)
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            zhiSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                            lastSkillTime = event.time
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14354", "14355"]:  # 羽
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = yuSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        elif event.id in ["21321"]:  # 相依
                            # TODO 实现特殊技能处理
                            xySkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        elif event.id in ["14138"]:  # 商
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = shangSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        elif event.id in ["14139"]:  # 角
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = jueSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        elif event.id in ["9002", "9003"]:  # 扶摇、蹑云
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            lastSkillTime = event.time + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        elif event.id in ["14169"]:  # 一指回鸾
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            lastSkillTime = event.time + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                            bhBusy += getLength(24, self.haste)
                        # 处理特殊技能
                        elif event.id in specialNameDict:  # 特殊技能
                            desc = ""
                            if event.id in ["18838", "18839"]:
                                desc = "切换曲风到高山流水"
                            if event.id in ["18841", "18842"]:
                                desc = "切换曲风到梅花三弄"
                            if event.id in ["18845", "18846"]:
                                desc = "切换曲风到阳春白雪"
                            bh.setSpecialSkill(event.id, specialNameDict[event.id], skillIconDict[event.id],
                                               event.time, 0, desc)
                        else:
                            pass
                            # 对于其它的技能暂时不做记录
                            # lastSkillTime = event.time

                    if event.caster == self.mykey and event.scheme == 1:
                        # 统计不计入时间轴的治疗量
                        if event.id == "15057":  # 犹香
                            youxiangHeal += event.healEff
                        if event.id == "26894":  # 平吟
                            pingyinHeal += event.healEff
                        if event.id == "23951" and event.level == 75:  # 古道
                            gudaoHeal += event.healEff

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

                    if event.id == "14169":  # 一指回鸾
                        numPurge += 1

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
                    shangBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame) * 62.5))
                    teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                if event.id in ["9463", "9464", "9465", "9466"] and event.caster == self.mykey:  # 角
                    jueBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame) * 62.5))
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

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                if event.id in self.bld.info.player:
                    battleDict[event.id].setState(event.time, event.fight)

            num += 1

        # 记录最后一个技能
        if bhSkill != "0":
            bh.setNormalSkill(bhSkill, skillNameDict[bhSkill], skillIconDict[bhSkill],
                              bhTimeStart, bhTimeEnd - bhTimeStart, bhNum, bhHeal,
                              roundCent(bhHealEff / (bhHeal + 1e-10)),
                              int(bhDelay / (bhDelayNum + 1e-10)), bhBusy, "")

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]

        # 计算战斗效率等统计数据，TODO 扩写
        skillCounter = SkillLogCounter(skillLog, self.startTime, self.finalTime, self.haste)
        skillCounter.analysisSkillData()
        sumBusyTime = skillCounter.sumBusyTime
        sumSpareTime = skillCounter.sumSpareTime
        spareRate = sumSpareTime / (sumBusyTime + sumSpareTime + 1e-10)

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
            if getOccType(occDetailList[key]) == "tank" and not self.config.xiangzhiCalTank:
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
        self.result["skill"]["meihua"]["delay"] = int(mhsnSkill.getAverageDelay())
        self.result["skill"]["meihua"]["cover"] = roundCent(overallRate)
        self.result["skill"]["meihua"]["youxiangHPS"] = int(youxiangHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["meihua"]["pingyinHPS"] = int(pingyinHeal / self.result["overall"]["sumTime"] * 1000)
        # 宫
        self.result["skill"]["gong"] = {}
        self.result["skill"]["gong"]["num"] = gongSkill.getNum()
        self.result["skill"]["gong"]["delay"] = int(gongSkill.getAverageDelay())
        effHeal = gongSkill.getHealEff()
        self.result["skill"]["gong"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["gong"]["effRate"] = effHeal / (gongSkill.getHeal() + 1e-10)
        # 徵
        self.result["skill"]["zhi"] = {}
        self.result["skill"]["zhi"]["num"] = zhiSkill.getNum()
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
        # 相依
        self.result["skill"]["xiangyi"] = {}
        self.result["skill"]["xiangyi"]["num"] = xySkill.getNum()
        effHeal = xySkill.getHealEff()
        self.result["skill"]["xiangyi"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xiangyi"]["effRate"] = roundCent(effHeal / (xySkill.getHeal() + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
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

    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        self.result["score"] = {"sum": 0}

        # 数值分A
        # 治疗量A1
        stdTable = {"25人普通雷域大泽": {"巨型尖吻凤": [[0, 0], [1000, 10]],
                                  "桑乔": [[0, 0], [1000, 10]],
                                  "悉达罗摩": [[0, 0], [1000, 10]],
                                  "尤珈罗摩": [[0, 0], [1000, 10]],
                                  "月泉淮": [[0, 0], [1000, 10]],
                                  "乌蒙贵": [[0, 0], [1000, 10]],
                                }
                    }



        # tb.AppendHeader("数值分：", "对治疗数值的打分，包括治疗量、各个技能数量。")
        # tb.AppendContext("0", width=9)
        # tb.AppendContext("F")
        # tb.EndOfLine()
        # tb.AppendHeader("统计分：", "对统计结果的打分，包括梅花三弄和HOT的覆盖率。")
        # tb.AppendContext("0", width=9)
        # tb.AppendContext("F")
        # tb.EndOfLine()
        # tb.AppendHeader("操作分：", "对操作表现的打分，包括战斗效率，各个技能延迟。")
        # tb.AppendContext("0", width=9)
        # tb.AppendContext("F")
        # tb.EndOfLine()
        # tb.AppendHeader("总评：", "综合计算这几项的结果。")
        # tb.AppendContext("0", width=9)
        # tb.AppendContext("F")
        # tb.EndOfLine()
        # tk.Label(frame8, text="分数统计在收集一定量的数据后生效。").place(x=10, y=150)


        pass

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

        upload = {}
        upload["server"] = self.result["overall"]["server"]
        upload["id"] = self.result["overall"]["playerID"]
        upload["occ"] = "xiangzhi"
        upload["score"] = self.result["score"]["sum"]
        upload["battledate"] = time.strftime("%Y-%m-%d", time.localtime(self.result["overall"]["battleTime"]))
        upload["mapdetail"] = self.result["overall"]["map"]
        upload["boss"] = self.result["overall"]["boss"]
        upload["statistics"] = self.result
        upload["public"] = self.xiangzhiPublic
        upload["edition"] = EDITION
        upload["editionfull"] = parseEdition(EDITION)
        upload["replayedition"] = self.result["overall"]["edition"]
        upload["userid"] = self.config.items_user["uuid"]
        upload["battletime"] = self.result["overall"]["battleTime"]
        upload["submittime"] = int(time.time())
        upload["hash"] = self.getHash()

        Jdata = json.dumps(upload)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        # print(jparse)
        resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadReplayPro', data=jparse)
        res = json.load(resp)
        print(res)
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

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", bossBh=None, startTime=0, finalTime=0):
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
        #self.win = 0
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.myname = myname
        self.bossBh = bossBh
        self.failThreshold = config.failThreshold
        self.mask = config.mask
        self.xiangzhiPublic = config.xiangzhiPublic
        self.config = config
        #self.filePath = path + '\\' + fileNameInfo[0]
        self.bld = bldDict[fileNameInfo[0]]
        self.startTime = startTime
        self.finalTime = finalTime

        self.result = {}
        self.haste = config.speed

        #if self.numTry == 0:
        #    self.bossNamePrint = self.bossname
        #else:
        #    self.bossNamePrint = "%s.%d" % (self.bossname, self.numTry)

        #print("奶歌复盘pro类创建成功...")


# Created by moeheart at 06/08/2022
# 展示界面，用于复盘结果展示窗口中部分共有功能的实现。

import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import json
import webbrowser
import pyperclip

from replayer.TableConstructor import TableConstructor, ToolTip
from replayer.Percent import *
from tools.Functions import *
from tools.Names import getIDFromMap
from tools.StaticJson import *
from window.ReviewWindow import ReviewerWindow

def getDirection(key):
    if "delay" in key:
        return -1
    else:
        return 1

class SingleSkillDisplayer():
    '''
    单个技能展示类，用于整理并显示单独的技能。
    '''

    def getSkillPercent(self, name, key):
        '''
        获取对应统计数据的百分数.
        params:
        - name: results中的分类，用于计算百分位数.
        - key: results中的键，用于计算百分位数.
        returns:
        - num: 记录总数量.
        - percent: 排名百分位.
        - color: 排名颜色.
        '''
        if name in self.rank and key in self.rank[name]:
            # 查找成功
            num = self.rank[name][key]["num"]
            percent = self.rank[name][key]["percent"]
            if percent == 100:
                color = "#e5cc80"
            elif percent == 99:
                color = "#e268a8"
            elif percent >= 95:
                color = "#ff7700"
            elif percent >= 75:
                color = "#330077"
            elif percent >= 50:
                color = "#0000ff"
            elif percent >= 25:
                color = "#007700"
            else:
                color = "#aaaaaa"
            return num, percent, color
        else:
            # 查找失败
            return 0, 0, "#000000"

    def export_image(self, frame, pos):
        '''
        导出为带图片类型的tk.Label，并显示在frame的对应位置.
        params:
        - frame: Tkinter定义的窗口类，当前复盘的展示窗口.
        - pos: 1-8的数字，对应显示的位置.
        '''
        assert pos >= 0 and pos <= 7
        y = 0
        if pos >= 4:
            y = 100
            x = (pos - 4) * 180
        else:
            x = pos * 180

        subFrame = tk.Frame(frame, width=180, height=95)
        subFrame.place(x=x, y=y)
        subFrame.photo = tk.PhotoImage(file="icons/%s.png" % self.iconID)
        label = tk.Label(subFrame, image=subFrame.photo)
        label.place(x=5, y=25)
        ToolTip(label, self.skillName)

        labelY = 45 - 9 * len(self.attrib)
        for line in self.attrib:
            text1 = "%s：" % line[1]
            label1 = tk.Label(subFrame, text=text1, justify="left")
            label1.place(x=60, y=labelY)
            text = ""
            if line[0] == "int":
                text = "%d\n" % line[2]
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "percent":
                text = "%s%%\n" % parseCent(line[2])
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "delay":
                text = "%dms\n" % line[2]
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "plus":
                text = "%d+%d\n" % (line[2], line[5])
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "rate":
                text = "%d(%.2f)\n" % (line[2], line[5])
                num, percent, color = self.getSkillPercent(line[6], line[7])
            else:
                num, percent, color = 0, 0, "#000000"
            if num > 0:
                descText = "排名：%d%%\n数量：%d" % (percent, num)
            else:
                descText = "排名未知"
            label2 = tk.Label(subFrame, text=text, justify="left", fg=color)
            label2.place(x=120, y=labelY)
            ToolTip(label2, descText)
            labelY += 18

    def export_text(self, frame, pos):
        '''
        导出为纯文本类型的tk.Label，并显示在window的对应位置.
        params:
        - frame: Tkinter定义的窗口类，当前复盘的展示窗口.
        - pos: 1-8的数字，对应显示的位置.
        '''
        assert pos >= 0 and pos <= 7
        y = 0
        if pos >= 4:
            y = 100
            x = (pos - 4) * 180
        else:
            x = pos * 180

        subFrame = tk.Frame(frame, width=180, height=95)
        subFrame.place(x=x, y=y)

        labelY = 45 - 9 * len(self.attrib)
        for line in self.attrib:
            text1 = "%s：" % line[1]
            label1 = tk.Label(subFrame, text=text1, justify="left")
            label1.place(x=10, y=labelY)
            text = ""
            if line[0] == "int":
                text = "%d\n" % line[2]
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "percent":
                text = "%s%%\n" % parseCent(line[2])
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "delay":
                text = "%dms\n" % line[2]
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "plus":
                text = "%d+%d\n" % (line[2], line[5])
                num, percent, color = self.getSkillPercent(line[3], line[4])
            elif line[0] == "rate":
                text = "%d(%.2f)\n" % (line[2], line[5])
                num, percent, color = self.getSkillPercent(line[6], line[7])
            else:
                num, percent, color = 0, 0, "#000000"
            if num > 0:
                descText = "排名：%d%%\n数量：%d" % (percent, num)
            else:
                descText = "排名未知"
            label2 = tk.Label(subFrame, text=text, justify="left", fg=color)
            label2.place(x=80, y=labelY)
            ToolTip(label2, descText)
            labelY += 18

    def setDoubleRaw(self, style, desc, value1, name1, key1, value2, name2, key2):
        '''
        设置两项式的统计结果.
        - style: 显示风格, "plus"表示A+B, "rate"表示A(B).
        - desc: 统计结果的描述.
        - value1: 第一项统计结果的值.
        - name1: 第一项在results中的分类，用于计算百分位数.
        - key1: 第一项在results中的键，用于计算百分位数.
        - value2: 第二项统计结果的值.
        - name2: 第二项在results中的分类，用于计算百分位数.
        - key2: 第二项在results中的键，用于计算百分位数.
        '''
        self.attrib.append([style, desc, value1, name1, key1, value2, name2, key2])

    def setDouble(self, style, desc, name, key1, key2):
        '''
        设置两项式的统计结果, 并从results中直接获取.
        - style: 显示风格, "plus"表示A+B, "rate"表示A(B).
        - desc: 统计结果的描述.
        - name: 第一项在results中的分类，用于计算百分位数.
        - key1: 第一项在results中的键，用于计算百分位数.
        - key2: 第二项在results中的键，用于计算百分位数.
        '''
        self.setDoubleRaw(style, desc, self.skill[name].get(key1, 0), name, key1, self.skill[name].get(key2, 0), name, key2)

    def setSingleRaw(self, style, desc, value, name, key):
        '''
        设置一条统计结果.
        - style: 显示风格, "int"表示整数, "percent"表示百分数.
        - desc: 统计结果的描述.
        - value: 统计结果的值.
        - name: 在results中的分类，用于计算百分位数.
        - key: 在results中的键，用于计算百分位数.
        '''
        self.attrib.append([style, desc, value, name, key])

    def setSingle(self, style, desc, name, key):
        '''
        设置一条统计结果, 并从results中直接获取.
        - style: 显示风格, "int"表示整数, "percent"表示百分数.
        - desc: 统计结果的描述.
        - name: 在results中的分类，用于计算百分位数.
        - key: 在results中的键，用于计算百分位数.
        '''
        self.setSingleRaw(style, desc, self.skill[name].get(key, 0), name, key)

    def setImage(self, iconID, skillName):
        '''
        设置技能图标.
        params:
        - iconID: 图标ID.
        - skillName: 技能名，用于鼠标滑过时显示对应的技能.
        '''
        self.withImage = True
        self.iconID = iconID
        self.skillName = skillName

    def __init__(self, skill, rank):
        '''
        初始化.
        params:
        - skill: 技能统计的结果.
        - rank: 排名列表.
        '''
        self.withImage = False
        self.attrib = []
        self.skill = skill
        self.rank = rank


class HealerDisplayWindow():
    '''
    治疗复盘窗口基类，实现部分通用功能.
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
        url = "http://120.48.95.56/%s/%d" % (self.occ, self.result["overall"]["shortID"])
        webbrowser.open(url)

    def renderOverall(self):
        '''
        渲染全局信息(Part 1).
        '''
        window = self.window
        # Part 1: 全局
        frame1 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground=self.themeColor)
        frame1.place(x=10, y=10)
        frame1sub = tk.Frame(frame1)
        frame1sub.place(x=0, y=0)
        tb = TableConstructor(self.config, frame1sub)
        tb.AppendContext("复盘版本：", justify="right")
        tb.AppendContext(self.result["overall"]["edition"])
        tb.EndOfLine()
        tb.AppendContext("玩家ID：", justify="right")
        tb.AppendContext(self.result["overall"]["playerID"], color=self.themeColor)
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

    def renderEquipment(self):
        '''
        渲染装备信息(Part 2).
        '''
        window = self.window
        # Part 2: 装备
        frame2 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground=self.themeColor)
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

    def renderHeal(self):
        '''
        渲染治疗信息(Part 3).
        '''
        window = self.window
        # Part 3: 治疗
        frame3 = tk.Frame(window, width=310, height=150, highlightthickness=1, highlightbackground=self.themeColor)
        frame3.place(x=430, y=10)
        frame3sub = tk.Frame(frame3)
        frame3sub.place(x=0, y=0)

        tb = TableConstructor(self.config, frame3sub)
        tb.AppendHeader("玩家名", "", width=13)
        # tb.AppendHeader("有效HPS", "最常用语境下的每秒治疗量，注意包含重伤时间。")
        # tb.AppendHeader("虚条HPS", "指虚条的最右端，包含溢出治疗量，也即计算所有绿字。")
        tb.AppendHeader("rHPS", "全称raid HPS，是综合考虑有效治疗量、化解、减伤、以及安全范围内的溢出治疗量后得到的值。\nrHPS与对团血的贡献程度完全成正比。在承伤与配置不变的情况下，使rHPS更高的手法就能使团血更稳。")
        tb.AppendHeader("HPS", "与游戏中[有效HPS]接近的值。相比于插件的统计，其考虑了吸血、蛊惑等隐藏数值，因此与游戏中会有细微的不同。")
        tb.AppendHeader("aHPS", "全称absorb HPS，包括化解、减伤、响应式治疗。游戏中的APS漏洞百出，而aHPS可以更准确地反应这些被抵消的伤害。")
        tb.AppendHeader("oHPS", "全称over HPS，指包含溢出的治疗量，也即游戏中的虚条。oHPS与aHPS之和决定了承伤的上限。")
        tb.EndOfLine()
        for record in self.result["healer"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            if name != self.result["overall"]["playerID"]:
                # 非当前玩家
                tb.AppendContext(record.get("rhps", 0))
                tb.AppendContext(record.get("hps", record.get("healEff", 0)))
                tb.AppendContext(record.get("ahps", 0))
                tb.AppendContext(record.get("ohps", record.get("heal", 0)))
                # tb.AppendContext(record["healEff"])
                # tb.AppendContext(record["heal"])
            else:
                # 当前玩家
                hpsDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
                # rHPS
                tb.AppendContext(record.get("rhps", 0))
                # HPS
                num, percent, color = hpsDisplayer.getSkillPercent("healer", "healEff")
                if num > 0:
                    descText = "排名：%d%%\n数量：%d" % (percent, num)
                else:
                    descText = "排名未知"
                tb.AppendHeader(record.get("hps", record.get("healEff", 0)), descText, color=color)
                # aHPS
                tb.AppendContext(record.get("ahps", 0))
                # oHPS
                num, percent, color = hpsDisplayer.getSkillPercent("healer", "heal")
                if num > 0:
                    descText = "排名：%d%%\n数量：%d" % (percent, num)
                else:
                    descText = "排名未知"
                tb.AppendHeader(record.get("ohps", record.get("heal", 0)), descText, color=color)
            tb.EndOfLine()

    def renderQx(self):
        '''
        渲染奇穴信息(Part 4).
        '''
        window = self.window
        # Part 4: 奇穴
        frame4 = tk.Frame(window, width=310, height=70, highlightthickness=1, highlightbackground=self.themeColor)
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

    def renderSkill(self):
        '''
        渲染技能信息，需要派生类实现(Part 5).
        '''
        pass

    def renderReplay(self):
        '''
        渲染回放信息，需要派生类实现(Part 6).
        '''
        pass

    def renderTeam(self):
        '''
        渲染团队信息，需要派生类实现(Part 7).
        '''
        pass

    def openReviewerWindow(self):
        '''
        打开专案组窗口.
        '''
        self.reviewerWindow.start()

    def renderRate(self):
        '''
        渲染评分信息，需要派生类实现(Part 8).
        '''
        window = self.window
        # Part 8: 打分
        frame8 = tk.Frame(window, width=210, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        frame8.place(x=320, y=620)

        if "review" in self.result:
            # 支持专案组模块
            tk.Label(frame8, text="AI评分：").place(x=30, y=20)
            score = self.result["review"]["score"]
            tk.Label(frame8, text="%.2f" % score).place(x=100, y=20)
            numReview = self.result["review"]["num"]
            tk.Label(frame8, text="共有%d条手法建议。" % numReview).place(x=30, y=50)
            b2 = tk.Button(frame8, text='在[专案组]中查看', height=1, command=self.openReviewerWindow)
            b2.place(x=60, y=80)
            tk.Label(frame8, text="本模块仅可作为提高手法的参考，").place(x=20, y=110)
            tk.Label(frame8, text="请勿使用本模块出警！").place(x=20, y=130)
            self.reviewerWindow = ReviewerWindow(self.result, self.themeColor)
        else:
            tk.Label(frame8, text="复盘生成时的版本尚不支持此功能。").place(x=10, y=20)

    def renderAdvertise(self):
        '''
        渲染广告信息，需要派生类实现(Part 9).
        '''
        pass

    def initWindow(self):
        '''
        对窗口进行初始化.
        '''
        window = tk.Toplevel()
        self.window = window
        window.geometry('750x900')
        window.title(self.title)
        window.protocol('WM_DELETE_WINDOW', self.final)

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.initWindow()
        self.renderOverall()
        self.renderEquipment()
        self.renderHeal()
        self.renderQx()
        self.renderSkill()
        self.renderReplay()
        self.renderTeam()
        self.renderRate()
        self.renderAdvertise()

    def setThemeColor(self, color):
        '''
        设置主题色，用于界面展示.
        params:
        - color: 主题色
        '''
        self.themeColor = color

    def final(self):
        '''
        关闭窗口。
        '''
        self.windowAlive = False
        self.window.destroy()

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
        - config: 设置类.
        - result: 复盘逻辑返回的结果.
        '''
        self.config = config
        self.mask = self.config.item["general"]["mask"]
        self.result = result["result"]
        self.rank = result["rank"]
        if "mask" in self.result["overall"]:
            self.mask = self.result["overall"]["mask"]  # 使用数据中的mask选项顶掉框架中现场读取的判定
        self.themeColor = "#000000"  # 默认为黑色



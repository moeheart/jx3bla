# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *
from replayer.occ.Healer import HealerReplay
from window.HealerDisplayWindow import HealerDisplayWindow, SingleSkillDisplayer

import os
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk

class XiangZhiProWindow(HealerDisplayWindow):
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

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''如果是盾歌，时间轴中表示梅花三弄的实时全团覆盖率。
如果是血歌，时间轴中表示每个小队的双HOT剩余时间。注意，1-5队可能并不按顺序对应团队面板的1-5队。
由于底层机制问题，APS统计在有两个或以上化解同时作用时无法准确计算，仅为推测值。'''
        messagebox.showinfo(title='说明', message=text)

    def renderSkill(self):
        '''
        渲染技能信息(Part 5)，奶歌复盘特化.
        '''
        window = self.window
        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        frame5.place(x=10, y=250)

        mhsnDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        mhsnDisplayer.setImage("7059", "梅花三弄")
        mhsnDisplayer.setDouble("rate", "数量", "meihua", "num", "numPerSec")
        mhsnDisplayer.setSingle("percent", "覆盖率", "meihua", "cover")
        mhsnDisplayer.setSingle("delay", "延迟", "meihua", "delay")
        mhsnDisplayer.setSingle("int", "犹香HPS", "meihua", "youxiangHPS")
        mhsnDisplayer.setSingle("int", "平吟HPS", "meihua", "pingyinHPS")
        mhsnDisplayer.export_image(frame5, 0)

        zhiDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        zhiDisplayer.setImage("7174", "徵")
        zhiDisplayer.setDouble("rate", "数量", "zhi", "num", "numPerSec")
        zhiDisplayer.setSingle("delay", "延迟", "zhi", "delay")
        zhiDisplayer.setSingle("int", "HPS", "zhi", "HPS")
        zhiDisplayer.setSingle("int", "古道HPS", "zhi", "gudaoHPS")
        zhiDisplayer.setSingle("percent", "有效比例", "zhi", "effRate")
        zhiDisplayer.export_image(frame5, 1)

        jueDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        jueDisplayer.setImage("7176", "角")
        jueDisplayer.setDouble("rate", "数量", "jue", "num", "numPerSec")
        jueDisplayer.setSingle("delay", "延迟", "jue", "delay")
        jueDisplayer.setSingle("int", "HPS", "jue", "HPS")
        jueDisplayer.setSingle("percent", "覆盖率", "jue", "cover")
        jueDisplayer.export_image(frame5, 2)

        shangDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        shangDisplayer.setImage("7172", "商")
        shangDisplayer.setDouble("rate", "数量", "shang", "num", "numPerSec")
        shangDisplayer.setSingle("delay", "延迟", "shang", "delay")
        shangDisplayer.setSingle("int", "HPS", "shang", "HPS")
        shangDisplayer.setSingle("percent", "覆盖率", "shang", "cover")
        shangDisplayer.export_image(frame5, 3)

        gongDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        gongDisplayer.setImage("7173", "宫")
        gongDisplayer.setDouble("rate", "数量", "gong", "num", "numPerSec")
        gongDisplayer.setSingle("delay", "延迟", "gong", "delay")
        gongDisplayer.setSingle("int", "HPS", "gong", "HPS")
        gongDisplayer.setSingle("int", "枕流HPS", "gong", "zhenliuHPS")
        gongDisplayer.setSingle("percent", "有效比例", "gong", "effRate")
        gongDisplayer.export_image(frame5, 4)

        yuDisplayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        yuDisplayer.setImage("7175", "羽")
        yuDisplayer.setDouble("rate", "数量", "yu", "num", "numPerSec")
        yuDisplayer.setSingle("delay", "延迟", "yu", "delay")
        yuDisplayer.setSingle("int", "HPS", "yu", "HPS")
        yuDisplayer.setSingle("percent", "有效比例", "yu", "effRate")
        yuDisplayer.export_image(frame5, 5)

        info1Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info1Displayer.setSingle("int", "相依数量", "xiangyi", "num")
        info1Displayer.setSingle("int", "相依HPS", "xiangyi", "HPS")
        info1Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        # info2Displayer.setSingle("int", "APS估算", "general", "APS")
        info2Displayer.setSingle("int", "桑柔DPS", "general", "SangrouDPS")
        info2Displayer.setSingle("int", "庄周梦DPS", "general", "ZhuangzhouDPS")
        info2Displayer.setSingle("int", "玉简DPS", "general", "YujianDPS")
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
        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground=self.themeColor)
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
                if self.config.item["xiangzhi"]["stack"] != "不堆叠" and i-j >= int(self.config.item["xiangzhi"]["stack"]):
                    # 进行堆叠显示
                    record_first = self.result["replay"]["normal"][j]
                    record_last = self.result["replay"]["normal"][i-1]
                    posStart = int((record_first["start"] - startTime) / 100)
                    posEnd = int((record_last["start"] + record_last["duration"] - startTime) / 100)
                    canvas6.create_image(posStart + 10, 80, image=canvas6.im[record_last["iconid"]])
                    # 绘制表示持续的条
                    if posStart + 20 < posEnd:
                        canvas6.create_rectangle(posStart + 20, 70, posEnd, 90, fill=self.themeColor)
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
                            canvas6.create_rectangle(posStart + 20, 70, posEnd, 90, fill=self.themeColor)
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
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground=self.themeColor)
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

    def renderAdvertise(self):
        '''
        渲染广告信息(Part 9)，奶歌复盘特化.
        '''
        window = self.window
        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground=self.themeColor)
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="相知PVE群：538939220").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb, bg='#777777')
            b2.place(x=40, y=90)

        tk.Label(frame9, text="广告位招租").place(x=40, y=140)

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - config: 设置类
        - result: 奶歌复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#64fab4")
        self.title = '奶歌复盘pro'
        self.occ = "xiangzhi"

class XiangZhiProReplayer(HealerReplay):
    '''
    奶歌复盘pro类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        self.window.setNotice({"t2": "加载奶歌复盘...", "c2": "#64fab4"})

        self.initFirstState()

        self.result["overall"]["calTank"] = self.config.item["xiangzhi"]["caltank"]
        self.shieldCountersNew = {}
        for key in self.bld.info.player:
            self.shieldCountersNew[key] = ShieldCounterNew("16911", self.startTime, self.finalTime)

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
            if self.interrupt != 0:
                continue

            self.eventInFirstState(event)
            if event.dataType == "Skill":

                # 记录主动贴盾，主要是为了防止复盘记录中的数据丢失。
                if event.id == "14231" and event.caster == self.mykey:
                    jianLiaoStack = 0
                    if event.target in self.jianLiaoLog:
                        jianLiaoStack = self.jianLiaoLog[event.target].checkState(event.time)
                    if jianLiaoStack < 20:
                        self.shieldCountersNew[event.target].setState(event.time, 1)

            elif event.dataType == "Buff":
                if event.id in ["9334", "16911"] and event.caster == self.mykey:  # buff梅花三弄
                    self.shieldCountersNew[event.target].setState(event.time, event.stack)

        for key in self.bld.info.player:
            self.shieldCountersNew[key].inferFirst()

        self.completeFirstState()
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

        numPurge = 0 # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
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
        firstHitDict = {}
        longkuiDict = {}
        jueOverallCounter = BuffCounter("9463", self.startTime, self.finalTime)  # 角的全局覆盖
        for line in self.bld.info.player:
            shangBuffDict[line] = HotCounter("9459", self.startTime, self.finalTime)  # 商，9460=殊曲，9461=洞天
            jueBuffDict[line] = HotCounter("9463", self.startTime, self.finalTime)  # 角，9460=殊曲，9461=洞天
            nongmeiDict[line] = BuffCounter("9584", self.startTime, self.finalTime)
            firstHitDict[line] = 0
            teamLog[line] = {}
            teamLastTime[line] = 0
            longkuiDict[line] = BuffCounter("20398", self.startTime, self.finalTime)
        lastSkillTime = self.startTime
        battleDict = self.battleDict

        # 杂项
        fengleiActiveTime = self.startTime
        youxiangHeal = 0
        pingyinHeal = 0
        gudaoHeal = 0
        zhenliuHeal = 0

        # 徵的特殊统计
        zhiLastCast = 0
        zhiLastSkill = 0
        zhiZheXian = 0
        zhiCastNum = 0
        zhiCompleteNum = 0
        zhiLocalNum = 0
        zhiCastList = []
        zhiSingleNum = 0
        zhiSingleList = []

        # 影子的推断统计
        shadowBuffDict = {}
        for i in range(6):
            shadowBuffDict[str(i+9993)] = BuffCounter(str(i+9993), self.startTime, self.finalTime)

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],
                     [mhsnSkill, "梅花三弄", ["14231"], "7059", True, 0, False, True, 0, 1],
                     [gongSkill, "宫", ["18864", "14360", "16852"], "7173", True, 24, False, True, 0, 1],
                     [zhiSkill, "徵", ["14362", "18865"], "7174", True, 8, True, True, 0, 1],
                     [yuSkill, "羽", ["14141", "14354", "14355", "14356"], "7175", True, 0, False, True, 6, 3],
                     [shangSkill, "商", ["14138"], "7172", True, 0, False, True, 0, 1],
                     [jueSkill, "角", ["14139"], "7176", True, 0, False, True, 0, 1],
                     [None, "风雷引", ["15502"], "13", True, 0, False, False, 180, 1],
                     [None, "一指回鸾", ["14169"], "7045", True, 0, False, True, 0, 1],
                     [None, "孤影化双", ["14081"], "7052", False, 0, False, True, 180, 1],
                     [None, "云生结海", ["14075"], "7048", False, 0, False, True, 80, 1],
                     [None, "高山流水", ["14069"], "7080", False, 0, False, True, 0, 1],
                     [None, "青霄飞羽", ["14076"], "7078", False, 0, False, True, 35, 1],
                     [None, "青霄飞羽·落", ["21324"], "7128", False, 0, False, True, 0, 1],
                     [None, "疏影横斜", ["14082"], "7066", False, 0, False, True, 20, 3],
                     [None, "移形换影", ["15039", "15040", "15041", "15042", "15043", "15044"], "7066", False, 0, False, True, 0, 1],
                     [None, "高山流水·切换", ["18838", "18839"], "7080", False, 0, False, True, 0, 1],
                     [None, "梅花三弄·切换", ["18841", "18842"], "7059", False, 0, False, True, 0, 1],
                     [None, "阳春白雪·切换", ["18845", "18846"], "7077", False, 0, False, True, 0, 1],
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
                               # 奶歌分割线
                               "15054", "15057",  # 盾奇穴效果
                               "15181", "15082", "25232",  # 影子宫，桑柔
                               "14535", "14532",  # 徵判定
                               "14082",  # 疏影横斜
                               "26731",  # 不器
                               "15168", "14357", "15169", "15170", "14358",  # 羽
                               "15138", "15081", "15153",  # 影子判定
                               "25237",  # 古道
                               "14071",  # 盾主动切换技能
                               "26894",  # 平吟新效果
                               "26965",  # 枕流
                               "14150",  # 云生结海平摊
                               "20763", "20764", "21321",  # 相依
                               "14153",  # 云生结海
                               "14084",  # 杯水
                               "14162",  # 收孤影
                               "15055",  # 盾高血量
                               "14137", "14300",  # 宫的壳技能
                               "14140", "14301",  # 徵的壳技能
                               "14407", "14408", "14409", "14410", "14411", "14412", "14413", "14414", "14415",  # 寸光阴的智障判定
                               "14395", "14396", "14397", "14398", "14399", "14400", "14401", "14402",  # 估计是寸光阴添加HOT
                               "15090", "14344", "14070",  # 阳春白雪主动技能（无尽藏！）
                               "14243",  # 掷杯判定
                               "15091",  # 阳春添加状态切换buff
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    pass
                    # numAbsorb1 += event.healEff
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
                            skillObj = line[0]
                            if skillObj is not None and event.id != "14082":  # 防止第一视角的影子重复计算
                                skillObj.recordSkill(event.time, event.heal, event.healEff, ss.timeEnd, delta=-1)
                        # 无法分析的技能
                        elif event.id not in xiangZhiUnimportant:
                            pass
                            # print("[XiangzhiNonRec]", event.time, event.id, event.heal, event.healEff)

                        # 统计不计入时间轴的治疗量
                        if event.id == "15057":  # 犹香
                            youxiangHeal += event.healEff
                        elif event.id == "26894":  # 平吟
                            pingyinHeal += event.healEff
                        elif event.id == "23951" and event.level == 75:  # 古道
                            gudaoHeal += event.healEff
                        elif event.id == "26965":  # 枕流
                            zhenliuHeal += event.healEff
                        elif event.id == "21321":  # 相依
                            xySkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

                        if event.id in ["14362", "18865"]:
                            # 徵的运算。此处是推测逻辑，较为复杂，有心重构可以大胆尝试。
                            timeDiff = event.time - zhiLastSkill
                            timeDiff2 = event.time - zhiLastCast
                            reset = 0
                            flag = 1
                            if timeDiff > 100 and (timeDiff2 < 100 or timeDiff < 200):
                                zhiZheXian = 1
                                bh.log["normal"][-1]["instant"] = 1
                                bh.log["normal"][-1]["start"] = event.time
                                bh.log["normal"][-1]["duration"] = 0
                                reset = 1
                            elif zhiZheXian and timeDiff > 1100:
                                bh.log["normal"][-1]["instant"] = 1
                                bh.log["normal"][-1]["start"] = event.time
                                bh.log["normal"][-1]["duration"] = 0
                                reset = 1
                            elif timeDiff > 1100:
                                reset = 2
                            elif zhiLocalNum == 6:
                                reset = 1
                                # zhiZheXian = 1
                            elif timeDiff > 100:
                                zhiLocalNum += 1
                            else:
                                flag = 0
                            if flag:
                                if zhiSingleNum > 0:
                                    zhiSingleList.append(zhiSingleNum)
                                zhiSingleNum = 0
                            zhiSingleNum += 1
                            if reset:
                                if zhiLocalNum >= 1:
                                    zhiCastNum += 1
                                    zhiCastList.append(zhiLocalNum)
                                    # print("[ZhiZheXian]", zhiZheXian)
                                zhiLocalNum = reset - 1
                            if zhiLocalNum == 6:
                                zhiCompleteNum += 1
                            zhiLastSkill = event.time

                            # print("[XiangzhiZhiSkill]", event.time, event.id, event.heal, event.healEff)

                    if event.caster == self.mykey and event.scheme == 2:
                        if event.id in ["9459", "9460", "9461", "9462"]:  # 商
                            shangBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        elif event.id in ["9463", "9464", "9465", "9466"]:  # 角
                            jueBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

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
                    pass

                if event.caster == self.mykey and event.id in ["15039", "15040", "15041", "15042", "15043", "15044"]:
                    # print("[xzTransport]", event.time, event.id)
                    state = shadowBuffDict[str(int(event.id)-15039+9993)].checkState(event.time - 50)
                    if state == 0:
                        skillObj = skillInfo[nonGcdSkillIndex["14082"]][0]
                        skillObj.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)

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
                    if event.stack == 1:
                        jueOverallCounter.setStateSafe(event.time, 1)
                        jueOverallCounter.setState(event.time + int((event.end - event.frame) * 62.5), 0)
                if event.id == "10521":  # 风雷标志debuff:
                    if event.stack == 1:
                        fengleiActiveTime = max(event.time, lastSkillTime)
                    else:
                        bh.setNormalSkill("15502", "风雷引", "8625",
                                          fengleiActiveTime, event.time - fengleiActiveTime, 1, 0,
                                          0,
                                          0, 1, "风雷读条，在此不做细节区分，只记录读条时间")
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                    yzSkill.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                if event.id in ["10193"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    bh.setSpecialSkill(event.id, "cw特效", "14416",
                                       event.time, 0, "触发cw特效")
                if event.id in ["9584"] and event.caster == self.mykey:  # 弄梅
                    nongmeiDict[event.target].setState(event.time, event.stack)
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)
                if event.id in ["20398"]:  # 龙葵
                    longkuiDict[event.target].setState(event.time, event.stack)

                if event.id in ["9993", "9994", "9995", "9996", "9997", "9998"] and event.target == self.mykey:
                    # 记录影子事件
                    skillObj = skillInfo[nonGcdSkillIndex["14082"]][0]
                    if skillObj is not None and event.stack == 1:
                        skillObj.recordSkill(event.time, 0, 0, ss.timeEnd, delta=-1)
                        # print("[xzRecord]", skillObj.getNum())
                    # print("[xzShadow]", event.time, event.id, event.stack)
                    shadowBuffDict[event.id].setState(event.time, event.stack)


            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

            elif event.dataType == "Cast":
                if event.caster == self.mykey and event.id == "14140":
                    # 徵
                    zhiLastCast = event.time
                    zhiCastNum += 1
                    if zhiLocalNum > 0:
                        zhiCastList.append(zhiLocalNum)
                    zhiLocalNum = 0
                    if zhiSingleNum > 0:
                        zhiSingleList.append(zhiSingleNum)
                    zhiSingleNum = 0
                    # print(event.time, event.id)

            num += 1

        # 记录最后一个技能
        if ss.skill != "0":
            index = gcdSkillIndex[ss.skill]
            line = skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")

        zhiCastList.append(zhiLocalNum)
        zhiSingleList.append(zhiSingleNum)

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

        # for line in occDetailList:
        #     print(line, occDetailList[line], self.bld.info.player[line].name)

        # 计算DPS的盾指标
        overallShieldHeat = {"interval": 500, "timeline": []}
        for key in self.shieldCountersNew:
            sumShield += self.shieldCountersNew[key].countCast()
            liveCount = battleDict[key].buffTimeIntegral()  # 存活时间比例
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
        self.result["skill"]["yu"]["numPerSec"] = roundCent(self.result["skill"]["yu"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
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
        self.result["skill"]["general"]["APS"] = myHealStat["ahps"]
        self.result["skill"]["general"]["SangrouDPS"] = int(numdam2 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["ZhuangzhouDPS"] = int(numdam1 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["YujianDPS"] = int(numdam3 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        xuegeFlag = 0
        if self.result["skill"]["shang"]["cover"] > 0.1:  # HOT覆盖率大于10%，判定为血鸽
            self.result["replay"]["heatType"] = "hot"
            self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}
            xuegeFlag = 1
        else:  # 默认为盾鸽
            self.result["replay"]["heatType"] = "meihua"
            self.result["replay"]["heat"] = overallShieldHeat
        # 统计治疗相关
        # TODO 改为整体统计
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["healEff"] = myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["ohps"] = myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = myHealStat.get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = myHealStat.get("ahps", 0)

        self.getRankFromStat("xiangzhi")
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        specialKey = {"meihua-num": 20, "general-efficiency": 20, "zhi-numPerSec": 10, "general-APS": 10, "healer-healEff": 10}
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
        # print(self.result["skill"])
        # for line in self.result["replay"]["normal"]:
        #     print(line)
        # print("===")
        # for line in self.result["replay"]["special"]:
        #     print(line)
        #
        # f1 = open("xiangzhiTest.txt", "w")
        # for line in self.result["replay"]["normal"]:
        #     f1.write(str(line) + '\n')
        # f1.write("===")
        # for line in self.result["replay"]["special"]:
        #     f1.write(str(line) + '\n')
        # f1.close()

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
        for id in ["14082"]:
            scCandidate.append(skillInfo[nonGcdSkillIndex[id]][0])
        scCandidate.append(yzSkill)

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
            if skill in ["特效腰坠"] and num == 0:
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

        # code 101 不要玩血歌
        if xuegeFlag:
            self.result["review"]["content"].append({"code": 101, "num": 1, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 101, "num": 0, "rate": 1, "status": 0})

        # code 102 保证`梅花三弄`的覆盖率
        cover = self.result["skill"]["meihua"]["cover"]
        coverRank = self.result["rank"]["meihua"]["cover"]["percent"]
        res = {"code": 102, "cover": cover, "rank": coverRank, "rate": roundCent(coverRank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 103 中断`徵`的倒读条
        num = [0] * 7
        sum = zhiCastNum
        # print(zhiCastList)
        for i in zhiCastList:
            num[min(i, 6)] += 1
        if num[3] >= num[2]:
            # 争簇
            perfectTime = num[3]
            fullTime = num[6]
        else:
            # 非争簇（真的会有人不点争簇？）
            perfectTime = num[2]
            fullTime = num[3]
        perfectRate= roundCent(perfectTime / (sum + 1e-10), 4)
        res = {"code": 103, "time": sum, "perfectTime": perfectTime, "fullTime": fullTime, "rate": perfectRate}
        res["status"] = getRateStatus(res["rate"], 50, 0, 0)
        self.result["review"]["content"].append(res)

        # code 104 选择合适的`徵`目标
        num = 0
        sum = 0
        for i in zhiSingleList:
            sum += 1
            if i >= 4:
                num += 1
        coverRate = roundCent(num / (sum + 1e-10))
        res = {"code": 104, "time": sum, "coverTime": num, "rate": coverRate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # code 105 使用`移形换影`
        sum = skillInfo[nonGcdSkillIndex["14082"]][0].getNum()
        num = skillInfo[nonGcdSkillIndex["15039"]][0].getNum()
        rate = roundCent(num / (sum + 1e-10))
        res = {"code": 105, "time": sum, "coverTime": num, "wasteTime": sum - num, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # # code 106 使用`角`
        # sum = battleTimeDict[self.mykey]
        # num = jueOverallCounter.buffTimeIntegral()
        # cover = roundCent(num / (sum + 1e-10))
        # res = {"code": 106, "cover": cover, "rate": cover}
        # res["status"] = getRateStatus(res["rate"], 50, 0, 0)
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

        # 测试效果，在UI写好之后注释掉
        # for line in self.result["review"]["content"]:
        #     print(line)


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

    def replay(self):
        '''
        开始奶歌复盘pro分析.
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
        super().__init__(config, fileNameInfo, path, bldDict, window, myname, actorData)
        self.haste = config.item["xiangzhi"]["speed"]
        self.public = config.item["xiangzhi"]["public"]
        self.occ = "xiangzhi"
        self.occCode = "22h"
        self.occPrint = "奶歌"


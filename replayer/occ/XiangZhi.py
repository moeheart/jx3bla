# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.TableConstructor import TableConstructor
from tools.Functions import *
from replayer.occ.Healer import HealerReplay
from window.HealerDisplayWindow import HealerDisplayWindow, SingleSkillDisplayer

import os
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
        text = '''时间轴由上到下分别表示：盾实时覆盖，HOT实时覆盖。'''
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
        info1Displayer.setDouble("rate", "暗香次数", "meihua", "anxiangNum", "anxiangNumPerSec")
        info1Displayer.export_text(frame5, 6)

        info2Displayer = SingleSkillDisplayer(self.result["skill"], self.rank)
        info2Displayer.setSingle("int", "rDPS", "general", "rdps")
        info2Displayer.setSingle("percent", "沐风覆盖率", "mufeng", "cover")
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
            else:
                # 新的展示方式
                # 盾
                nowTimePixel = 0
                for line in self.result["replay"]["heat"]["timeline"][0]:
                    color = getColorHex((int(255 - (255 - 100) * line / 100),
                                         int(255 - (255 - 250) * line / 100),
                                         int(255 - (255 - 180) * line / 100)))
                    canvas6.create_rectangle(nowTimePixel, 31, nowTimePixel + 5, 50, fill=color, width=0)
                    nowTimePixel += 5

                # 双HOT
                nowTimePixel = 0
                for line in self.result["replay"]["heat"]["timeline"][1]:
                    color = getColorHex((int(255 - (255 - 128) * line / 100),
                                         int(255 - (255 - 128) * line / 100),
                                         int(255 - (255 - 255) * line / 100)))
                    canvas6.create_rectangle(nowTimePixel, 51, nowTimePixel + 5, 70, fill=color, width=0)
                    nowTimePixel += 5
                    # canvas6.create_image(10, 40, image=canvas6.im["7172"])
                    # canvas6.create_image(30, 40, image=canvas6.im["7176"])

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
            # print("[XiangzhiTest]", record)
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
        self.anxiangTimeDict = {}
        self.anxiangTimeIndex = {}
        for key in self.bld.info.player:
            self.shieldCountersNew[key] = ShieldCounterNew("16911", self.startTime, self.finalTime)
            self.anxiangTimeDict[key] = [0]
            self.anxiangTimeIndex[key] = 0
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
                # 记录暗香，用于判断后面贴盾的来源
                if event.id == "32684" and event.target in self.bld.info.player:
                    self.anxiangTimeDict[event.target].append(event.time)

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

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        self.skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1],
                     [None, "梅花三弄", ["14231"], "7059", True, 0, False, True, 0, 1],
                     [None, "宫", ["18864", "14360", "16852"], "7173", True, 24, False, True, 0, 1],
                     [None, "徵", ["14362", "18865"], "7174", True, 8, True, True, 0, 1],
                     [None, "羽", ["14141", "14354", "14355", "14356"], "7175", True, 0, False, True, 6, 3],
                     [None, "商", ["14138"], "7172", True, 0, False, True, 0, 1],
                     [None, "角", ["14139"], "7176", True, 0, False, True, 0, 1],
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
                     [None, "特效腰坠", ["yaozhui"], "3414", False, 0, False, True, 180, 1]
                    ]

        self.initSecondState()
        self.initTeamDetect()

        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        rateDict = {}  # 盾覆盖率
        breakDict = {}  # 破盾次数

        # 技能统计
        shangBuff = SkillHealCounter("9459", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 商
        jueBuff = SkillHealCounter("9463", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 角
        shangBuffDict = {}
        jueBuffDict = {}
        xySkill = SkillHealCounter("21321", self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)  # 相依
        jueOverallCounter = BuffCounter("9463", self.startTime, self.finalTime)  # 角的全局覆盖
        for line in self.bld.info.player:
            shangBuffDict[line] = HotCounter("9459", self.startTime, self.finalTime)  # 商，9460=殊曲，9461=洞天
            jueBuffDict[line] = HotCounter("9463", self.startTime, self.finalTime)  # 角，9460=殊曲，9461=洞天

        # 杂项
        fengleiActiveTime = self.startTime
        youxiangHeal = 0
        pingyinHeal = 0
        gudaoHeal = 0
        zhenliuHeal = 0
        gcsActive = 0  # 共潮生
        numAnxiang = 0  # 暗香
        numShield = 0  # 主动贴盾

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

        self.unimportantSkill += ["15054", "15057",  # 盾奇穴效果
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
                               "32684",  # 暗香判定
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            self.eventInTeamDetect(event)
            self.eventInSecondState(event)

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # 所有治疗技能都不计算化解.
                    continue

                if event.caster == self.mykey and event.scheme == 1:

                    # print("[XiangzhiMeihua]", event.time, event.id, self.bld.info.getSkillName(event.full_id), event.target, self.bld.info.getName(event.target), event.heal, event.healEff)

                    if event.id in self.nonGcdSkillIndex:  # 特殊技能
                        desc = ""
                        if event.id in ["18838", "18839"]:
                            desc = "切换曲风到高山流水"
                        if event.id in ["18841", "18842"]:
                            desc = "切换曲风到梅花三弄"
                        if event.id in ["18845", "18846"]:
                            desc = "切换曲风到阳春白雪"
                        index = self.nonGcdSkillIndex[event.id]
                        line = self.skillInfo[index]
                        self.bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                        skillObj = line[0]
                        if skillObj is not None and event.id != "14082":  # 防止第一视角的影子重复计算
                            skillObj.recordSkill(event.time, event.heal, event.healEff, self.ss.timeEnd, delta=-1)

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
                        xySkill.recordSkill(event.time, event.heal, event.healEff)

                    if event.id in ["14362", "18865"]:
                        # 徵的运算。此处是推测逻辑，较为复杂，有心重构可以大胆尝试。
                        timeDiff = event.time - zhiLastSkill
                        timeDiff2 = event.time - zhiLastCast
                        reset = 0
                        flag = 1
                        if timeDiff > 100 and (timeDiff2 < 100 or timeDiff < 200):
                            zhiZheXian = 1
                            self.bh.log["normal"][-1]["instant"] = 1
                            self.bh.log["normal"][-1]["start"] = event.time
                            self.bh.log["normal"][-1]["duration"] = 0
                            reset = 1
                        elif zhiZheXian and timeDiff > 1100:
                            self.bh.log["normal"][-1]["instant"] = 1
                            self.bh.log["normal"][-1]["start"] = event.time
                            self.bh.log["normal"][-1]["duration"] = 0
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
                        shangBuff.recordSkill(event.time, event.heal, event.healEff)
                    elif event.id in ["9463", "9464", "9465", "9466"]:  # 角
                        jueBuff.recordSkill(event.time, event.heal, event.healEff)

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

                if event.caster == self.mykey and event.id in ["15039", "15040", "15041", "15042", "15043", "15044"]:
                    # print("[xzTransport]", event.time, event.id)
                    state = shadowBuffDict[str(int(event.id)-15039+9993)].checkState(event.time - 50)
                    if state == 0:
                        skillObj = self.skillInfo[self.nonGcdSkillIndex["14082"]][0]
                        skillObj.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)

                if event.caster == self.mykey and event.id in ["32684"] and event.target in self.bld.info.player:
                    numAnxiang += 1
                    #print("[xzAnXiang]", parseTime((event.time - self.startTime)/1000), self.bld.info.getName(event.caster), self.bld.info.getName(event.target) )


            elif event.dataType == "Buff":
                if event.id in ["9459", "9460", "9461", "9462"] and event.caster == self.mykey and event.target in shangBuffDict:  # 商
                    shangBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                if event.id in ["9463", "9464", "9465", "9466"] and event.caster == self.mykey and event.target in jueBuffDict:  # 角
                    jueBuffDict[event.target].setState(event.time, event.stack, int((event.end - event.frame + 3) * 62.5))
                    # teamLog, teamLastTime = countCluster(teamLog, teamLastTime, event)
                    if event.stack == 1:
                        jueOverallCounter.setStateSafe(event.time, 1)
                        jueOverallCounter.setState(event.time + int((event.end - event.frame) * 62.5), 0)
                if event.id == "10521":  # 风雷标志debuff:
                    if event.stack == 1:
                        fengleiActiveTime = max(event.time, self.startTime)
                    else:
                        self.bh.setNormalSkill("15502", "风雷引", "8625",
                                          fengleiActiveTime, event.time - fengleiActiveTime, 1, 0,
                                          0,
                                          0, 1, "风雷读条，在此不做细节区分，只记录读条时间")
                if event.id in ["10193"] and event.stack == 1 and event.target == self.mykey:  # cw特效:
                    self.bh.setSpecialSkill(event.id, "cw特效", "14416",
                                       event.time, 0, "触发cw特效")
                if event.id in ["9993", "9994", "9995", "9996", "9997", "9998"] and event.target == self.mykey:
                    # 记录影子事件
                    skillObj = self.skillInfo[self.nonGcdSkillIndex["14082"]][0]
                    if skillObj is not None and event.stack == 1:
                        skillObj.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
                        # print("[xzRecord]", skillObj.getNum())
                    # print("[xzShadow]", event.time, event.id, event.stack)
                    shadowBuffDict[event.id].setState(event.time, event.stack)

                if event.id in ["24153"] and event.target == self.mykey:
                    # 共潮生激活
                    gcsActive = 1

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

        self.completeSecondState()
        self.completeTeamDetect()

        zhiCastList.append(zhiLocalNum)
        zhiSingleList.append(zhiSingleNum)

        # 计算DPS列表(Part 7)

        # 计算等效伤害
        numdam1 = 0
        numdam3 = 0
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0] + line[1] / 1.0554  # 110赛季数值
            numdam1 += line[1] / 1.0554 * 0.0554
            numdam3 += line[3]
        if self.mykey in battleStat:
            numdam2 = battleStat[self.mykey][2]
        else:
            numdam2 = 0

        self.result["dps"] = {"table": [], "numDPS": 0}
        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        badPeriod = self.bh

        overallShieldHeat = {"interval": 500, "timeline": []}
        for key in self.shieldCountersNew:
            liveCount = self.battleDict[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)  # 存活时间比例
            if self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog) - liveCount < 8000:  # 脱战缓冲时间
                liveCount = self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)
            self.battleTimeDict[key] = liveCount
            self.sumPlayer += liveCount / self.battleDict[key].sumTime(exclude=self.bh.badPeriodHealerLog)
            # 过滤老板，T奶，自己
            if key not in damageDict or damageDict[key] / self.result["overall"]["sumTimeEff"] * 1000 < 10000:
                continue
            if getOccType(self.occDetailList[key]) == "healer":
                continue
            if getOccType(self.occDetailList[key]) == "tank" and not self.config.item["xiangzhi"]["caltank"]:
                continue
            if key == self.mykey:
                continue
            time1 = self.shieldCountersNew[key].buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            timeAll = liveCount
            rateDict[key] = safe_divide(time1, timeAll)
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
                   "damage": int(line[1] / self.result["overall"]["sumTimeDpsEff"] * 1000),
                   "shieldRate": roundCent(rateDict[line[0]]),
                   "shieldBreak": breakDict[line[0]]}
            self.result["dps"]["table"].append(res)

        # 计算覆盖率
        numRate = 0
        sumRate = 0
        for key in rateDict:
            numRate += self.battleTimeDict[key]
            sumRate += rateDict[key] * self.battleTimeDict[key]
        overallRate = safe_divide(sumRate, numRate)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(self.sumPlayer * 100) / 100
        self.result["skill"] = {}

        # 梅花三弄
        mhsnSkill = self.calculateSkillInfo("meihua", "14231")
        self.result["skill"]["meihua"]["cover"] = roundCent(overallRate)
        self.result["skill"]["meihua"]["anxiangNum"] = numAnxiang
        self.result["skill"]["meihua"]["anxiangNumPerSec"] = roundCent(safe_divide(numAnxiang, self.result["overall"]["sumTimeEff"] / 1000), 2)
        self.result["skill"]["meihua"]["youxiangHPS"] = int(youxiangHeal / self.result["overall"]["sumTimeEff"] * 1000)
        self.result["skill"]["meihua"]["pingyinHPS"] = int(pingyinHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 宫
        gongSkill = self.calculateSkillInfo("gong", "18864")
        self.result["skill"]["gong"]["zhenliuHPS"] = int(zhenliuHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 徵
        zhiSkill = self.calculateSkillInfo("zhi", "14362")
        self.result["skill"]["zhi"]["gudaoHPS"] = int(gudaoHeal / self.result["overall"]["sumTimeEff"] * 1000)
        # 羽
        yuSkill = self.calculateSkillInfo("yu", "14141")

        # 队伍HOT统计初始化
        hotHeat = []
        # 商，注意Buff与Skill统计不同
        self.calculateSkillInfoDirect("shang", shangBuff)
        shangSkill = self.skillInfo[self.gcdSkillIndex["14138"]][0]
        self.result["skill"]["shang"]["delay"] = int(shangSkill.getAverageDelay())
        num = 0
        sum = 0
        for key in shangBuffDict:
            singleDict = shangBuffDict[key]
            num += self.battleTimeDict[key]
            sum += singleDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            singleHeat = singleDict.getHeatTable()
            if self.teamCluster[key] <= 5:
                if len(hotHeat) == 0:
                    for line in singleHeat["timeline"]:
                        hotHeat.append(line)
                else:
                    for i in range(len(singleHeat["timeline"])):
                        hotHeat[i] += singleHeat["timeline"][i]
        self.result["skill"]["shang"]["cover"] = roundCent(safe_divide(sum, num))

        # 角
        self.calculateSkillInfoDirect("jue", jueBuff)
        jueSkill = self.skillInfo[self.gcdSkillIndex["14139"]][0]
        self.result["skill"]["jue"]["delay"] = int(jueSkill.getAverageDelay())
        num = 0
        sum = 0
        for key in jueBuffDict:
            singleDict = jueBuffDict[key]
            num += self.battleTimeDict[key]
            sum += singleDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
            singleHeat = singleDict.getHeatTable()
            if self.teamCluster[key] <= 5:
                if len(hotHeat) == 0:
                    for line in singleHeat["timeline"]:
                        hotHeat.append(line)
                else:
                    for i in range(len(singleHeat["timeline"])):
                        hotHeat[i] += singleHeat["timeline"][i]
        self.result["skill"]["jue"]["cover"] = roundCent(safe_divide(sum, num))
        # 计算HOT统计
        for j in range(len(hotHeat)):
            hotHeat[j] = int(hotHeat[j] * 2)
        # print("[self.teamCluster]", self.teamCluster)
        # print("[HotHeat]", hotHeat)
        # print("[HotHeat0]", hotHeat[0])
        # 杂项
        self.calculateSkillInfoDirect("xiangyi", xySkill)
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["SangrouDPS"] = int(numdam2 / self.result["overall"]["sumTimeDpsEff"] * 1000)
        self.result["skill"]["general"]["ZhuangzhouDPS"] = int(numdam1 / self.result["overall"]["sumTimeDpsEff"] * 1000)
        self.result["skill"]["general"]["YujianDPS"] = int(numdam3 / self.result["overall"]["sumTimeDpsEff"] * 1000)

        # 计算战斗回放
        self.result["replay"] = self.bh.getJsonReplay(self.mykey)
        # xuegeFlag = 0
        # if self.result["skill"]["shang"]["cover"] > 0.1:  # HOT覆盖率大于10%，判定为血鸽
        #     self.result["replay"]["heatType"] = "hot"
        #     self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}
        #     xuegeFlag = 1
        # else:  # 默认为盾鸽
        #     self.result["replay"]["heatType"] = "meihua"
        #     self.result["replay"]["heat"] = overallShieldHeat

        self.result["replay"]["heatType"] = "combined"
        self.result["replay"]["heat"] = {"interval": 500, "timeline": [overallShieldHeat["timeline"], hotHeat]}

        self.specialKey = {"meihua-cover": 20, "general-efficiency": 20, "zhi-numPerSec": 10, "healer-rhps": 20}
        self.markedSkill = ["14082"]
        self.outstandingSkill = []
        self.calculateSkillOverall()

        # 计算专案组的心法部分.
        # code 101 不要玩血歌
        if gcsActive:
            self.result["review"]["content"].append({"code": 101, "num": 1, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 101, "num": 0, "rate": 1, "status": 0})

        # code 102 保证`梅花三弄`的覆盖率
        cover = self.result["skill"]["meihua"]["cover"]
        coverRank = self.result["rank"]["meihua"]["cover"]["percent"]
        res = {"code": 102, "cover": cover, "rank": coverRank, "rate": roundCent(coverRank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # # code 103 中断`徵`的倒读条（因为有暗香，这个手法作废）
        # num = [0] * 7
        # sum = zhiCastNum
        # # print(zhiCastList)
        # for i in zhiCastList:
        #     num[min(i, 6)] += 1
        # if num[3] >= num[2]:
        #     # 争簇
        #     perfectTime = num[3]
        #     fullTime = num[6]
        # else:
        #     # 非争簇（真的会有人不点争簇？）
        #     perfectTime = num[2]
        #     fullTime = num[3]
        # perfectRate = roundCent(safe_divide(perfectTime, sum), 4)
        # if self.result["qixue"]["available"] == 1 and self.result["qixue"]["5"] != "谪仙":
        #     perfectRate = 1
        # res = {"code": 103, "time": sum, "perfectTime": perfectTime, "fullTime": fullTime, "rate": perfectRate}
        # res["status"] = getRateStatus(res["rate"], 50, 0, 0)
        # self.result["review"]["content"].append(res)

        # code 104 选择合适的`徵`目标
        num = 0
        sum = 0
        for i in zhiSingleList:
            sum += 1
            if i >= 4:
                num += 1
        coverRate = roundCent(safe_divide(num, sum))
        res = {"code": 104, "time": sum, "coverTime": num, "rate": coverRate}
        res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        self.result["review"]["content"].append(res)

        # # code 105 使用`移形换影` (现在放影子就会立刻回蓝)
        # sum = self.skillInfo[self.nonGcdSkillIndex["14082"]][0].getNum()
        # num = self.skillInfo[self.nonGcdSkillIndex["15039"]][0].getNum()
        # rate = roundCent(safe_divide(num, sum))
        # res = {"code": 105, "time": sum, "coverTime": num, "wasteTime": sum - num, "rate": rate}
        # res["status"] = getRateStatus(res["rate"], 75, 0, 0)
        # self.result["review"]["content"].append(res)

        # # code 106 使用`角`  (移除这个统计)
        # sum = self.battleTimeDict[self.mykey]
        # num = jueOverallCounter.buffTimeIntegral()
        # cover = roundCent(safe_divide(num, sum))
        # res = {"code": 106, "cover": cover, "rate": cover}
        # res["status"] = getRateStatus(res["rate"], 50, 0, 0)
        # self.result["review"]["content"].append(res)

        # code 107 使用`暗香`提高刷盾的效率
        timeMhsn = self.result["skill"]["meihua"]["num"]
        timeAnxiang = self.result["skill"]["meihua"]["anxiangNum"]
        timeAll = timeMhsn + timeAnxiang
        rate = roundCent(safe_divide(timeAnxiang, timeAll))
        res = {"code": 107, "timeMhsn": timeMhsn, "timeAnxiang": timeAnxiang, "timeAll": timeAll, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 10, 0)
        self.result["review"]["content"].append(res)

        self.calculateSkillFinal()

        # 横刀断浪更新整理
        # - 分队HOT的判定移除，改为整体覆盖的HOT（显示方式也改为双排）11
        # - 专案组增加一个暗香下限判定11
        # - 用rdps替换整体dps统计11

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


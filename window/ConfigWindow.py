# Created by moeheart at 08/08/2022
# 设置窗口类，其中包含了大量人工维护的设置选项.

import threading
import json
import tkinter as tk
import urllib.request

from tkinter import ttk
from tkinter import messagebox
import webbrowser

from FileLookUp import FileLookUp
from Constants import *
from replayer.occ.XiangZhi import XiangZhiProWindow
from window.Window import Window
from window.ToolTip import ToolTip

from ConfigTools import Config

class ConfigWindow(Window):
    '''
    设置窗口类，将各种设置选项可视化，并维护交互的接口。
    '''

    def show_xiangzhiTianti(self):
        webbrowser.open("http://%s:8009/XiangZhiTable.html" % IP)

    def show_replay(self):
        '''
        尝试远程读取数据并显示.
        '''
        pass
        id = self.entry2_8.get()
        resp = urllib.request.urlopen('http://%s:8009/getReplayPro?id=%s' % (IP, id))
        res = json.load(resp)
        if res["text"] == "结果未找到.":
            messagebox.showinfo(title='嘶', message='找不到该ID对应的数据！')
        elif res["text"] == "数据未公开.":
            messagebox.showinfo(title='嘶', message='该ID对应的数据没有公开。')
        else:
            t = res["text"]
            t = t.replace("'", '"').replace("\t", "\\t").replace("\n", "\\n")
            result = json.loads(t)
            window = XiangZhiProWindow(self.config, result)
            window.start()

    def final(self):

        for frameKey in self.frameInfo:
            for itemKey in self.frameInfo[frameKey]:
                if itemKey == "num":
                    continue
                res = self.frameInfo[frameKey][itemKey]
                if res["type"] == "Entry":
                    self.config.item[res["configGroup"]][res["configKey"]] = res["entry"].get()
                elif res["type"] == "Check":
                    self.config.item[res["configGroup"]][res["configKey"]] = res["var"].get()
                elif res["type"] == "Radio":
                    self.config.item[res["configGroup"]][res["configKey"]] = res["var"].get()

        self.config.item["user"]["id"] = self.userId

        self.config.printSettings()
        self.window.destroy()

    def register(self):
        uuid = self.config.userUuid
        id = self.entry4_2.get()
        jpost = {'uuid': uuid, 'id': id}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://%s:8009/setUserId' % IP, data=jparse)
        res = json.load(resp)

        if res["result"] == "dupid":
            self.entry4_2.delete(0, tk.END)
            self.entry4_2.insert(0, "用户名已存在")
        elif res["result"] == "hasuuid":
            self.entry4_2.delete(0, tk.END)
            self.entry4_2.insert(0, "唯一标识已使用")
        elif res["result"] == "nouuid":
            self.entry4_2.delete(0, tk.END)
            self.entry4_2.insert(0, "唯一标识出错")
        else:
            messagebox.showinfo(title='提示', message='注册成功！')
            self.userId = id

    def clear_basepath(self, event):
        self.frameInfo["Frame1"]["basepath"]["entry"].delete(0, tk.END)

    def get_path(self):
        self.config.item["general"]["playername"] = self.frameInfo["Frame1"]["playername"]["entry"].get()
        self.config.item["general"]["jx3path"] = self.frameInfo["Frame1"]["jx3path"]["entry"].get()
        self.config.item["general"]["basepath"] = ""
        self.config.item["general"]["datatype"] = self.frameInfo["Frame1"]["datatype"]["var"].get()
        fileLookUp = FileLookUp()
        res = fileLookUp.initFromConfig(self.config)
        if res != "":
            self.frameInfo["Frame1"]["basepath"]["entry"].delete(0, tk.END)
            self.frameInfo["Frame1"]["basepath"]["entry"].insert(0, res)

    def init_checkbox(self, box, value):
        if value == 0:
            box.deselect()
        else:
            box.select()

    def init_radio(self, radio, value, valueStd):
        if value == valueStd:
            radio.select()

    def lvlup(self):
        jpost = {'uuid': self.config.userUuid}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://%s:8009/userLvlup' % IP, data=jparse)
        res = json.load(resp)
        if res["result"] == "fail":
            messagebox.showinfo(title='错误', message='升级失败！')
        elif res["result"] == "success":
            messagebox.showinfo(title='成功', message='升级成功！\n%s' % res["info"])

    def constructEntry(self, frame, f, description, detail, configGroup, configKey):
        '''
        建立输入类别的设置.
        params:
        - frame: 所在面板的名字.
        - f: 所在面板的tkinter类.
        - description: 文字描述的键名.
        - detail: 键名的展开说明.
        - configGroup: 在Config中的类别.
        - configKey: 在Config中的键.
        '''
        num = self.frameInfo[frame]["num"]
        res = {}
        label = tk.Label(f, text=description)
        entry = tk.Entry(f, show=None)
        label.grid(row=num, column=0)
        entry.grid(row=num, column=1)
        ToolTip(label, detail)
        entry.insert(0, self.config.item[configGroup][configKey])
        res["type"] = "Entry"
        res["label"] = label
        res["entry"] = entry
        res["configGroup"] = configGroup
        res["configKey"] = configKey
        self.frameInfo[frame][configKey] = res
        self.frameInfo[frame]["num"] += 1

    def constructCheck(self, frame, f, description, detail, configGroup, configKey, forcePos=None):
        '''
        建立多选类别的设置.
        params:
        - frame: 所在面板的名字.
        - f: 所在面板的tkinter类.
        - description: 文字描述的键名.
        - detail: 键名的展开说明.
        - configGroup: 在Config中的类别.
        - configKey: 在Config中的键.
        '''
        num = self.frameInfo[frame]["num"]
        res = {}
        var = tk.IntVar(f)
        cb = tk.Checkbutton(f, text=description, variable=var, onvalue=1, offvalue=0)
        if forcePos is None:
            cb.grid(row=num, column=0)
        else:
            cb.grid(row=forcePos[0], column=forcePos[1])
        ToolTip(cb, detail)
        self.init_checkbox(cb, self.config.item[configGroup][configKey])
        res["type"] = "Check"
        res["var"] = var
        res["cb"] = cb
        res["configGroup"] = configGroup
        res["configKey"] = configKey
        self.frameInfo[frame][configKey] = res
        if forcePos is None:
            self.frameInfo[frame]["num"] += 1

    def constructRadio(self, frame, f, description, detail, configGroup, configKey, itemList, descList):
        '''
        建立单选类别的设置.
        params:
        - frame: 所在面板的名字.
        - f: 所在面板的tkinter类.
        - description: 文字描述的键名.
        - detail: 键名的展开说明.
        - configGroup: 在Config中的类别.
        - configKey: 在Config中的键.
        - itemList: 选项列表.
        - descList: 选项描述列表.
        '''
        num = self.frameInfo[frame]["num"]
        res = {}
        res["rb"] = []

        label = tk.Label(f, text=description)
        var = tk.StringVar(f)
        frame_inner = tk.Frame(f)
        label.grid(row=num, column=0)
        frame_inner.grid(row=num, column=1)
        for i in range(len(itemList)):
            rb = tk.Radiobutton(frame_inner, text=itemList[i], variable=var, value=itemList[i])
            rb.grid(row=0, column=i)
            ToolTip(rb, descList[i])
            self.init_radio(rb, self.config.item[configGroup][configKey], itemList[i])
            res["rb"].append(rb)
        ToolTip(label, detail)

        res["type"] = "Radio"
        res["var"] = var
        res["label"] = label
        res["configGroup"] = configGroup
        res["configKey"] = configKey
        self.frameInfo[frame][configKey] = res
        self.frameInfo[frame]["num"] += 1

    def loadWindow(self):
        '''
        使用tkinter绘制设置窗口，同时读取config.ini。
        '''

        self.config = Config("config.ini", skipUser=0)
        config = self.config

        window = tk.Toplevel(self.mainWindow)
        # window = tk.Tk()
        window.title('设置')
        window.geometry('400x300')

        notebook = ttk.Notebook(window)

        self.frameInfo = {}

        # 全局页面
        self.frameInfo["Frame1"] = {"num": 0}
        frame1 = tk.Frame(notebook)
        self.constructEntry("Frame1", frame1, "玩家ID",
                            "在当前电脑上线的角色的ID，同时也是记录者。\n通常情况下，只需要指定此项。\n如果指定了基准路径，则无需指定此项。",
                            "general", "playername")
        self.constructEntry("Frame1", frame1, "剑三路径",
                            "剑三路径，一般是名为JX3的文件夹，一般可以右键剑三的快捷方式找到，例如C:\\JX3。\n有时客户端并非标准安装方式（如体服），这时也可以使用MY#DATA的任意上层文件夹代替，例如C:\\SeasunGame\\Game\\JX3_EXP\\bin\\zhcn_exp。\n此项会尝试自动从注册表获取，如果获取失败，才需要手动指定。\n指定此项时，必须指定角色名。\n如果指定了基准路径，则无需指定此项。",
                            "general", "jx3path")
        self.constructEntry("Frame1", frame1, "基准路径",
                            "基准路径，一般为Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA\\一串数字@zhcn\\userdata\\fight_stat\n必备选项，可以点击右侧的自动获取来从角色名自动推导。\n如果留空，则会在运行时自动推导。推导失败时将以当前目录作为基准目录。",
                            "general", "basepath")
        self.constructCheck("Frame1", frame1, "名称打码",
                            "是否在生成的图片中将ID打码。\n这一选项同样会影响上传的数据，如果开启，则上传的数据也会打码。",
                            "general", "mask")
        self.constructCheck("Frame1", frame1, "门派染色",
                            "是否在生成的图片开启门派染色。",
                            "general", "color")
        self.constructCheck("Frame1", frame1, "生成txt格式",
                            "是否将生成的图片中的信息以txt格式保存，方便再次传播。",
                            "general", "text")
        self.constructRadio("Frame1", frame1, "数据格式",
                            "复盘数据的格式，由剑三茗伊插件集的对应功能生成。\n对于指定的格式，必须正确设置，才能进行复盘。",
                            "general", "datatype",
                            ["jcl", "jx3dat"],
                            [
                                "jcl格式，是茗伊团队工具的结果记录。这种记录结构轻巧，且拥有更全面的数据，但没有技能名等固定的信息。\n开启步骤：\n1. 在茗伊插件集-团队-团队工具中，勾选[xxx]\n2. 点击旁边的小齿轮，勾选[xxx]",
                                "jx3dat格式，是茗伊战斗统计的结果记录。这种记录无需依赖全局信息，但没有部分数据种类。\n开启步骤：\n1. 在茗伊战斗统计的小齿轮中，勾选[记录所有复盘数据]。\n2. 按Shift点开历史页面，勾选[退出游戏时保存复盘][脱离战斗时保存复盘]，并取消[不保存历史复盘数据]。\n3. 再次按Shift点开历史页面，点击[仅在秘境中启用复盘]2-3次，使其取消。"])

        self.frameInfo["Frame1"]["playername"]["entry"].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["jx3path"]["entry"].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["datatype"]["rb"][0].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["datatype"]["rb"][1].bind('<Button-1>', self.clear_basepath)

        tk.Button(frame1, text='自动获取', command=self.get_path).grid(row=2, column=2)

        # 演员复盘页面
        frame3 = tk.Frame(notebook)
        self.frameInfo["Frame2"] = {"num": 0}
        self.constructCheck("Frame2", frame3, "启用演员复盘",
                            "演员复盘的总开关。如果关闭，则将跳过整个演员复盘。",
                            "actor", "active")
        self.constructCheck("Frame2", frame3, "处理拉脱的数据",
                            "如果开启，在复盘模式下会尝试复盘所有的数据；\n反之，则复盘每个BOSS的最后一次战斗。",
                            "actor", "checkall")
        self.constructEntry("Frame2", frame3, "拉脱末尾的无效时间(s)",
                            "设置拉脱保护时间，在拉脱的数据中，最后若干秒的犯错记录将不再统计。",
                            "actor", "failthreshold")
        self.constructEntry("Frame2", frame3, "DPS及格线",
                            "团队-心法DPS的及格线。\n如果全程低于这个值，一般代表没有工资，或者需要转老板。\n以1为单位。",
                            "actor", "qualifiedrate")
        self.constructEntry("Frame2", frame3, "DPS预警线",
                            "团队-心法DPS的预警线。\n如果有BOSS低于这个值，一般代表后续需要重点关注。\n以1为单位。",
                            "actor", "alertrate")
        self.constructEntry("Frame2", frame3, "DPS补贴线",
                            "团队-心法DPS的补贴线。\n如果全程高于这个值，一般代表可以发DPS补贴。\n以1为单位。",
                            "actor", "bonusrate")
        self.constructEntry("Frame2", frame3, "过滤监控列表",
                            "在展示时间轴时人工指定需要过滤的技能或buff，由玩家指定，用逗号隔开，例如：\ns6746,b17933,b6131",
                            "actor", "filter")

        # 用户信息界面 TODO 以后维护
        frame4 = tk.Frame(notebook)
        self.frameInfo["Frame3"] = {"num": 0}
        self.label4_1 = tk.Label(frame4, text='用户唯一标识')
        self.label4_1_1 = tk.Label(frame4, text=config.userUuid)
        self.label4_2 = tk.Label(frame4, text='用户名')
        self.entry4_2 = tk.Entry(frame4, show=None)
        self.button4_2 = tk.Button(frame4, text='注册', command=self.register)
        self.label4_3 = tk.Label(frame4, text='积分')
        self.label4_3_1 = tk.Label(frame4, text=config.score)
        self.label4_4 = tk.Label(frame4, text='经验值')
        self.frame4_4 = tk.Frame(frame4)
        rankNow = config.rankNow
        rankNext = config.rankNext
        rankBar = config.rankBar
        rankPercent = config.rankPercent
        self.label4_4_1 = tk.Label(self.frame4_4, text=rankNow)
        self.label4_4_2 = ttk.Progressbar(self.frame4_4)
        self.label4_4_2['maximum'] = 1
        self.label4_4_2['value'] = rankPercent
        ToolTip(self.label4_4_2, rankBar)
        self.label4_4_4 = tk.Label(self.frame4_4, text=rankNext)
        self.button4_4_5 = tk.Button(frame4, text='升级', command=self.lvlup)
        self.label4_4_1.grid(row=0, column=0)
        self.label4_4_2.grid(row=0, column=1)
        self.label4_4_4.grid(row=0, column=2)
        self.frame4_5 = tk.Frame(frame4)
        self.label4_5_1 = tk.Label(frame4, text="道具数量")
        self.label4_5_1a = tk.Label(self.frame4_5, text="中级点赞卡")
        self.label4_5_1b = tk.Label(self.frame4_5, text=config.userItems[0])
        self.label4_5_2a = tk.Label(self.frame4_5, text="高级点赞卡")
        self.label4_5_2b = tk.Label(self.frame4_5, text=config.userItems[1])
        self.label4_5_3a = tk.Label(self.frame4_5, text="中级吐槽卡")
        self.label4_5_3b = tk.Label(self.frame4_5, text=config.userItems[2])
        self.label4_5_4a = tk.Label(self.frame4_5, text="高级吐槽卡")
        self.label4_5_4b = tk.Label(self.frame4_5, text=config.userItems[3])
        self.label4_5_1a.grid(row=0, column=0)
        self.label4_5_1b.grid(row=0, column=1)
        self.label4_5_2a.grid(row=1, column=0)
        self.label4_5_2b.grid(row=1, column=1)
        self.label4_5_3a.grid(row=2, column=0)
        self.label4_5_3b.grid(row=2, column=1)
        self.label4_5_4a.grid(row=3, column=0)
        self.label4_5_4b.grid(row=3, column=1)
        self.label4_1.grid(row=0, column=0)
        self.label4_1_1.grid(row=0, column=1)
        self.label4_2.grid(row=1, column=0)
        self.entry4_2.grid(row=1, column=1)
        self.button4_2.grid(row=1, column=2)
        self.label4_3.grid(row=2, column=0)
        self.label4_3_1.grid(row=2, column=1)
        self.label4_4.grid(row=3, column=0)
        self.frame4_4.grid(row=3, column=1)
        if rankPercent >= 1:
            self.button4_4_5.grid(row=3, column=2)
        self.label4_5_1.grid(row=4, column=0)
        self.frame4_5.grid(row=4, column=1)
        self.entry4_2.insert(0, self.config.item["user"]["id"])
        ToolTip(self.label4_1, "用来验证用户唯一性的字符串。")
        ToolTip(self.label4_2, "代表玩家ID的用户名，用于在社区中展示。\n第一次使用时，需要点击右方的注册，之后则不可修改。")
        ToolTip(self.label4_3, "玩家的积分。积分可用于中级、高级评价的消耗，或是在活动中兑换实物奖品。")
        ToolTip(self.label4_4, "玩家的经验值。当经验值满足升级条件时即可升级，升级后会获得一些道具奖励，并且解锁部分额外功能。")
        ToolTip(self.label4_5_1, "玩家的道具数量。")

        # 治疗设置（包括奶歌/奶花/奶毒/奶秀/奶药)
        frame2 = tk.Frame(notebook)
        frame5 = tk.Frame(notebook)
        frame6 = tk.Frame(notebook)
        frame7 = tk.Frame(notebook)
        frame8 = tk.Frame(notebook)

        healerSettings = [[frame2, "Frame4-1", "xiangzhi"],
                          [frame5, "Frame4-2", "lingsu"],
                          [frame6, "Frame4-3", "lijing"],
                          [frame7, "Frame4-4", "butian"],
                          [frame8, "Frame4-5", "yunchang"]]

        for line in healerSettings:
            frameID = line[1]
            frameTK = line[0]
            configClass = line[2]
            self.frameInfo[frameID] = {"num": 0}
            self.constructCheck(frameID, frameTK, "启用",
                                "对应治疗心法复盘的总开关。如果关闭，则将跳过整个心法复盘。",
                                configClass, "active")
            self.constructEntry(frameID, frameTK, "加速",
                                "对应治疗心法的加速等级。用于在复盘中的装备信息获取失败的情况下手动指定加速。",
                                configClass, "speed")
            self.constructCheck(frameID, frameTK, "分享结果",
                                "是否将复盘数据设置为公开。\n在之后的版本中，可以通过网站浏览所有公开的数据。",
                                configClass, "public")
            self.constructCheck(frameID, frameTK, "强制指定",
                                "是否强制指定加速为设置的值。\n这是用来处理配装信息不准的情况，例如小药、家园酒的增益。",
                                configClass, "speedforce", forcePos=[1, 2])
            self.constructRadio(frameID, frameTK, "时间轴堆叠阈值",
                                "复盘结果的战斗回放中，将相同技能堆叠显示的阈值。低于这个阈值则不会堆叠。",
                                configClass, "stack",
                                ["2", "3", "不堆叠"],
                                ["堆叠全部重复的技能。", "只堆叠3个以上的技能。", "从不堆叠技能。"])
            if configClass == "xiangzhi":
                self.constructCheck(frameID, frameTK, "统计T的覆盖率",
                                    "是否统计T心法的覆盖率。\n多数情况下，统计T心法的覆盖率会使数据略微变差。",
                                    configClass, "caltank")

        # tk.Button(frame2, text='查看天梯', height=1, command=self.show_xiangzhiTianti).grid(row=5, column=0)  # TODO 移除此功能
        tk.Button(frame2, text='根据ID查看复盘', height=1, command=self.show_replay).grid(row=6, column=0)
        self.entry2_8 = tk.Entry(frame2, show=None)
        self.entry2_8.grid(row=6, column=1)

        notebook.add(frame1, text='全局')
        notebook.add(frame3, text='演员')
        notebook.add(frame4, text='用户')
        notebook.add(frame2, text='奶歌')
        notebook.add(frame5, text='灵素')
        notebook.add(frame6, text='奶花')
        notebook.add(frame7, text='奶毒')
        notebook.add(frame8, text='奶秀')
        notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.userId = self.config.item["user"]["id"]

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def __init__(self, window):
        super().__init__()
        self.mainWindow = window
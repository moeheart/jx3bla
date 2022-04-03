# Created by moeheart at 10/10/2020
# 处理config.ini，包括所有选项的解析与导出。
# 目前还加入了一些其它的子窗口，例如公告栏。

import threading
import os
import configparser
import time
import re
import uuid
import json
import tkinter as tk
import urllib.request
import pyperclip

from tkinter import ttk
from tkinter import messagebox
import webbrowser

from LiveBase import ToolTip
from FileLookUp import FileLookUp
from equip.EquipmentExport import HuajianExportEquipment, ExcelExportEquipment, EquipmentAnalyser
from Constants import *
from tools.Functions import *
from replayer.occ.XiangZhi import XiangZhiProWindow

class Config():
    '''
    设置类，负责读取与写入config.ini，并且维护各种设置选项。
    '''
    
    def getUserInfo(self):
        '''
        与服务器通信，获取当前uuid的用户信息并保存在config中。
        '''
        if parseEdition(EDITION) == 0:  # 非联机版本跳过加载步骤
            res = {"item1": 0, "item2": 0, "item3": 0, "item4": 0, "exp": 0, "score": 0, "lvl": 0, "exist": 1}
        else:
            jpost = {'uuid': self.userUuid}
            jparse = urllib.parse.urlencode(jpost).encode('utf-8')
            resp = urllib.request.urlopen('http://139.199.102.41:8009/getUserInfo', data=jparse)
            res = json.load(resp)
        
        if res['exist'] == 0:
            messagebox.showinfo(title='错误', message='用户唯一标识出错，将重新生成并清除用户数据。如果遇到问题，请联系作者。')
            uuid = self.getNewUuid()
            self.userUuid = uuid
            self.userItems = [0, 0, 0, 0]
            self.exp = 0
            self.score = 0
            self.lvl = 0
        
        else:
            self.userItems = [res["item1"], res["item2"], res["item3"], res["item4"]]
            self.exp = res["exp"]
            self.score = res["score"]
            self.lvl = res["lvl"]
            
        self.rankNow = LVLNAME[self.lvl]
        self.rankNext = LVLNAME[self.lvl+1]
        self.rankBar = "%d/%d"%(self.exp, LVLTABLE[self.lvl+1])
        
        if self.exp >= LVLTABLE[self.lvl+1]:
            self.rankPercent = 1
        else:
            self.rankPercent = (self.exp - LVLTABLE[self.lvl]) / (LVLTABLE[self.lvl+1] - LVLTABLE[self.lvl])

    def getNewUuid(self):
        '''
        与服务器通信，取得一个新的uuid。
        '''
        mac = "-".join(re.findall(r".{2}",uuid.uuid1().hex[-12:].upper()))
        jpost = {'mac': mac}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://139.199.102.41:8009/getUuid', data=jparse)
        res = json.load(resp)
        return res["uuid"]

    def initHealerItems(self, items_target, occ):
        '''
        初始化治疗相关的设置.
        params:
        - items_target: 治疗相关的选项列表.
        - occ: 职业描述.
        '''

        items_target["active"] = int(items_target.get("active", 1))
        items_target["speed"] = int(items_target.get("speed", 8780))
        items_target["public"] = int(items_target.get("public", 1))
        items_target["speedforce"] = int(items_target.get("speedforce", 0))
        if occ in ["xiangzhi", "butian", "yunchang"]:
            items_target["stack"] = items_target.get("stack", "2")
        elif occ in ["lingsu"]:
            items_target["stack"] = items_target.get("stack", "3")
        elif occ in ["lijing"]:
            items_target["stack"] = items_target.get("stack", "不堆叠")
        if occ == "xiangzhi":
            items_target["caltank"] = int(items_target.get("caltank", 0))
        
    def checkItems(self):
        '''
        检查config.ini是否符合规范，并设置默认选项。
        '''
        try:
            self.item["general"]["playername"] = self.item["general"].get("playername", "")
            self.item["general"]["basepath"] = self.item["general"].get("basepath", "")
            self.item["general"]["jx3path"] = self.item["general"].get("jx3path", "")
            self.item["general"]["mask"] = int(self.item["general"].get("mask", 0))
            self.item["general"]["color"] = int(self.item["general"].get("color", 1))
            self.item["general"]["text"] = int(self.item["general"].get("text", 0))
            self.item["general"]["datatype"] = self.item["general"].get("datatype", "jcl")
            self.item["general"]["edition"] = self.item["general"].get("edition", EDITION)

            self.item["actor"]["active"] = int(self.item["actor"].get("active", 1))
            self.item["actor"]["checkall"] = int(self.item["actor"].get("checkall", 0))
            self.item["actor"]["failthreshold"] = int(self.item["actor"].get("failthreshold", 10))
            self.item["actor"]["qualifiedrate"] = float(self.item["actor"].get("qualifiedrate", 0.75))
            self.item["actor"]["alertrate"] = float(self.item["actor"].get("alertrate", 0.85))
            self.item["actor"]["bonusrate"] = float(self.item["actor"].get("bonusrate", 1.20))

            self.item["user"]["uuid"] = self.item["user"].get("uuid", "")
            self.item["user"]["id"] = self.item["user"].get("id", "")
            if self.item["user"]["uuid"] == "" and "beta" not in EDITION:
                uuid = self.getNewUuid()
                self.item["user"]["uuid"] = uuid

            self.initHealerItems(self.item["xiangzhi"], "xiangzhi")
            self.initHealerItems(self.item["lingsu"], "lingsu")
            self.initHealerItems(self.item["lijing"], "lijing")
            self.initHealerItems(self.item["butian"], "butian")
            self.initHealerItems(self.item["yunchang"], "yunchang")

            # self.playername = self.item["general"].get("playername", "")
            # self.basepath = self.item["general"].get("basepath", "")
            # self.jx3path = self.item["general"].get("jx3path", "")
            # self.mask = int(self.item["general"].get("mask", 0))
            # self.color = int(self.item["general"].get("color", 1))
            # self.text = int(self.item["general"].get("text", 0))
            # self.datatype = self.item["general"].get("datatype", "jcl")
            # self.edition = self.item["general"].get("edition", EDITION)

            # self.actorActive = int(self.item["actor"].get("active", 1))
            # self.checkAll = int(self.item["actor"].get("checkall", 0))
            # self.failThreshold = int(self.item["actor"].get("failthreshold", 10))
            # self.qualifiedRate = float(self.item["actor"].get("qualifiedrate", 0.75))
            # self.alertRate = float(self.item["actor"].get("alertrate", 0.85))
            # self.bonusRate = float(self.item["actor"].get("bonusrate", 1.20))

            self.userUuid = self.item["user"].get("uuid", "")
            self.userId = self.item["user"].get("id", "")
            if self.userUuid == "" and "beta" not in EDITION:
                uuid = self.getNewUuid()
                self.userUuid = uuid

            # self.xiangzhiActive = int(self.item["xiangzhi"].get("active", 1))
            # self.speed = int(self.item["xiangzhi"].get("speed", 8780))
            # self.xiangzhiPublic = int(self.item["xiangzhi"].get("public", 1))
            # self.xiangzhiSpeedForce = int(self.item["xiangzhi"].get("speedforce", 0))
            # self.xiangzhiCalTank = int(self.item["xiangzhi"].get("caltank", 0))
            # self.xiangzhiStack = int(self.item["xiangzhi"].get("stack", 3))
            #
            # self.lingsuActive = int(self.item["lingsu"].get("active", 1))
            # self.lingsuSpeed = int(self.item["lingsu"].get("speed", 8780))
            # self.lingsuPublic = int(self.item["lingsu"].get("public", 1))
            # self.lingsuSpeedForce = int(self.item["lingsu"].get("speedforce", 0))
            # self.lingsuStack = int(self.item["lingsu"].get("stack", 3))
            #
            # self.lijingActive = int(self.item["lijing"].get("active", 1))
            # self.lijingSpeed = int(self.item["lijing"].get("speed", 8780))
            # self.lijingPublic = int(self.item["lijing"].get("public", 1))
            # self.lijingSpeedForce = int(self.item["lijing"].get("speedforce", 0))
            # self.lijingStack = int(self.item["lijing"].get("stack", 3))
            #
            # self.butianActive = int(self.item["butian"].get("active", 1))
            # self.butianSpeed = int(self.item["butian"].get("speed", 8780))
            # self.butianPublic = int(self.item["butian"].get("public", 1))
            # self.butianSpeedForce = int(self.item["butian"].get("speedforce", 0))
            # self.butianStack = int(self.item["butian"].get("stack", 3))
            #
            # self.yunchangActive = int(self.item["yunchang"].get("active", 1))
            # self.yunchangSpeed = int(self.item["yunchang"].get("speed", 8780))
            # self.yunchangPublic = int(self.item["yunchang"].get("public", 1))
            # self.yunchangSpeedForce = int(self.item["yunchang"].get("speedforce", 0))
            # self.yunchangStack = int(self.item["yunchang"].get("stack", 3))

            self.getUserInfo()
                
            # assert self.mask in [0, 1]
            # assert self.color in [0, 1]
            # assert self.text in [0, 1]
            # assert self.xiangzhiActive in [0, 1]
            # assert self.actorActive in [0, 1]
            # assert self.checkAll in [0, 1]
            # assert self.qualifiedRate <= self.alertRate
            # assert self.alertRate <= self.bonusRate
        except:
            raise Exception("配置文件格式不正确，请确认。如无法定位问题，请删除config.ini，在生成的配置文件的基础上进行修改。")

    def printDefault(self):
        '''
        产生默认的config.ini.
        '''
        g = open("config.ini", "w", encoding="utf-8")
        g.close()
        
    def printSettings(self):
        '''
        将当前设置输出到config.ini。
        '''
        g = open("config.ini", "w", encoding="utf-8")
        text = ""
        for itemClass in self.item:
            nameInFile = self.item[itemClass]["nameInFile"]
            text += "[%s]\n" % nameInFile
            for key in self.item[itemClass]:
                if key != "nameInFile":
                    if type(self.item[itemClass][key]).__name__ == "int":
                        text += "%s=%d\n" % (key, self.item[itemClass][key])
                    else:
                        text += "%s=%s\n" % (key, self.item[itemClass][key])
            text += '\n'
        g.write(text)
        g.close()
        pass

    def loadSettings(self, cf, nameInFile, nameInConfig):
        '''
        从ConfigParser中读取设置内容并转化为pythondict形式.
        params:
        - cf: 用来读取的ConfigParser
        - nameInFile: ConfigParser中的名字.
        - nameInConfig: 本类中保存的名字.
        '''
        if nameInFile in cf.sections():
            self.item[nameInConfig] = dict(cf.items(nameInFile))
        else:
            self.item[nameInConfig] = {}
        self.item[nameInConfig]["nameInFile"] = nameInFile

    def __init__(self, filename, build=0):
        '''
        构造方法。
        params
        - filename: 配置文件名，通常为config.ini。
        '''
        self.item = {}
        if not os.path.isfile(filename):
            if build:
                self.printDefault()
            else:
                print("config.ini不存在，请检查使用方法，或删除重试。")
        else:
            try:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="utf-8")
                self.loadSettings(cf, "General", "general")
                self.loadSettings(cf, "ActorAnalysis", "actor")
                self.loadSettings(cf, "UserAnalysis", "user")
                self.loadSettings(cf, "XiangZhiAnalysis", "xiangzhi")
                self.loadSettings(cf, "LingSuAnalysis", "lingsu")
                self.loadSettings(cf, "LiJingAnalysis", "lijing")
                self.loadSettings(cf, "BuTianAnalysis", "butian")
                self.loadSettings(cf, "YunChangAnalysis", "yunchang")
                self.checkItems()
            except:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="gbk")
                self.loadSettings(cf, "General", "general")
                self.loadSettings(cf, "ActorAnalysis", "actor")
                self.loadSettings(cf, "UserAnalysis", "user")
                self.loadSettings(cf, "XiangZhiAnalysis", "xiangzhi")
                self.loadSettings(cf, "LingSuAnalysis", "lingsu")
                self.loadSettings(cf, "LiJingAnalysis", "lijing")
                self.loadSettings(cf, "BuTianAnalysis", "butian")
                self.loadSettings(cf, "YunChangAnalysis", "yunchang")
                self.checkItems()
                
class LicenseWindow():
    """
    用户协议窗口类，用于展示用户协议与交互。
    """

    license_fake = """
************************************************************
|                     剑三警长 使用协议                      |
************************************************************
    剑三警长是一款剑网三战斗日志分析工具，在使用本工具之前，我
们需要部分授权，需要您的同意：
    1. 您授权将游戏账号下的所有不绑定道具，包括但不限于：金币、
五行石、不绑定装备、外观礼盒，全部邮寄给开发者作为开发报酬。
    2. 您知晓并同意，本协议只用于测试您是否认真阅读了条款，请
点击下方复选框10次以获取真实的协议。
    3. 为了数据对比，您授权将自己及情缘的所有信息向作者公开，
并对之后可能引发的818放弃所有保留的权利。
    4. 本协议仅对jx3bla主仓库的主分支有效，开发者如果需要修改
代码，需要同时维护此协议，否则视为本协议无效。
************************************************************
"""
    license_true = """
************************************************************
|                     剑三警长 使用协议                      |
************************************************************
    剑三警长是一款剑网三战斗日志分析工具，在使用本工具之前，我
们需要部分授权，需要您的同意：
    1. 本工具会读取茗伊插件集生成的战斗复盘日志，其中的信息包
括但不限于：全部技能与buff的时间与数值、玩家ID与门派、区服、
重伤记录。这些读取的内容只会在本地进行运算。
    2. 本工具会上传战斗复盘结果图中的所有信息到作者的服务器，
包括但不限于：DPS/HPS统计，区服，玩家ID与门派，打分，犯错记录。
收集这些信息是为了进行进一步研究，对之后的的开发提供数据支持。
由于上传的数据只有全局信息，因此您无需担心打法被泄漏。
    3. 对于上传的数据，可能会以HPS天梯/评分百分比的形式，进行
数据公开。作者在公开数据时，有对玩家个人信息进行保密的义务，
包括玩家ID与团队构建等信息，应在去特征化后再发布。但演员不在此
列，对于表现明显低于正常水平的玩家，可能会有其它安排。
    4. 即使没有显式同意本协议，使用本工具依然需要协议的内容经
过授权。尝试绕过本协议并不能免除您的义务。
    5. 本协议仅对jx3bla主仓库的主分支有效，开发者如果需要修改
代码，需要同时维护此协议，否则视为本协议无效。
************************************************************
"""

    def final(self):
        messagebox.showinfo(title='杯具了', message='本工具依赖于用户协议中的部分项目，必须同意才可以运行。')
        self.window.destroy()
        self.mainWindow.destroy()
    
    def init_checkbox(self, box, value):
        if value == 0:
            box.deselect()
        else:
            box.select()
            
    def hit_ok(self):
        if not self.genius:
            messagebox.showinfo(title='你是认真的吗', message='请认真阅读用户协议。')
            self.window.destroy()
            self.mainWindow.destroy()
        elif not self.var.get():
            self.final()
        else:
            Config("config.ini", 1)
            self.lock.Unlock()
            self.window.destroy()
        
    def hit_cancel(self):
        self.final()
        
    def hit_box(self, dummy):
        self.numBox += 1
        if self.numBox >= 10 and not self.genius:
            self.genius = 1
            self.cb.deselect()
            self.label.configure(text=self.license_true)
    
    def loadWindow(self):
        '''
        弹出用户协议界面。
        '''
        self.numBox = 0
        self.genius = 0
        window = tk.Toplevel()
        window.title('用户协议')
        window.geometry('500x400')
        
        l = tk.Label(window, text=self.license_fake, font=('宋体', 10), width=60, bg='#ffffff', anchor='nw', justify=tk.LEFT)
        l.pack()
        self.label = l
        
        self.var = tk.IntVar(window)
        self.cb = tk.Checkbutton(window, text = "同意上述协议", variable = self.var, onvalue = 1, offvalue = 0)
        self.cb.bind("<Button-1>", self.hit_box)
        self.cb.pack()
        
        b1 = tk.Button(window, text='完成', height=1, command=self.hit_ok)
        b1.place(x = 200, y = 350)
        
        b2 = tk.Button(window, text='关闭', height=1, command=self.hit_cancel)
        b2.place(x = 250, y = 350)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
    
    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()

    def __init__(self, mainWindow, lock):
        self.mainWindow = mainWindow
        self.lock = lock
        
class AnnounceWindow():
    '''
    公告窗口类，提供公告窗口的展示。
    现有的公告窗口拼凑了较多的功能，之后可能会改名。
    '''

    def final(self):
        self.window.destroy()
        
    def show_tutorial(self):
        webbrowser.open("https://www.jx3box.com/bps/31349")
        
    def show_help(self):
        webbrowser.open("https://wwe.lanzouy.com/iKY8Ayggt4j")
        
    def show_update(self):
        webbrowser.open("https://github.com/moeheart/jx3bla/blob/master/update.md")
        
    def show_export_equip(self):
        if self.mainWindow.playerEquipment == []:
            messagebox.showinfo(title='提示', message='还未读取记录，请至少读取一条记录再试。')
            return
        self.exportEquip = ExportEquipmentWindow(self.mainWindow.playerEquipment)
        self.exportEquip.start()
    
    def loadWindow(self):
        '''
        使用tkinter绘制公告窗口。
        '''
        window = tk.Toplevel()
        window.title('公告')
        window.geometry('400x200')

        self.window = window
        
        l = tk.Message(window, text=self.announcement, font=('宋体', 10), width=380, anchor='nw', justify=tk.LEFT)
        l.pack()
        self.label = l
        
        l2 = tk.Message(window, text="反馈QQ群：418483739", font=('宋体', 10), width=380, anchor='nw', justify=tk.LEFT)
        l2.place(x = 30, y = 140)
        
        b3 = tk.Button(window, text='复盘指南', height=1, command=self.show_tutorial)
        b3.place(x = 50, y = 160)
        
        b4 = tk.Button(window, text='帮助文档', height=1, command=self.show_help)
        b4.place(x = 123, y = 160)
        
        b5 = tk.Button(window, text='更新内容', height=1, command=self.show_update)
        b5.place(x = 196, y = 160)
        
        b5 = tk.Button(window, text='导出配装', height=1, command=self.show_export_equip)
        b5.place(x = 270, y = 160)
        
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()

    def __init__(self, announcement, mainWindow):
        self.announcement = announcement
        self.mainWindow = mainWindow
        
class ExportEquipmentWindow():
    '''
    配装导出窗口类，用于支持配装计算器的一站式导入。
    '''
    
    def final(self):
        self.window.destroy()
        
    def export_huajian(self):
        l = os.listdir('.')
        if "花间DPS配装计算器—奉天证道beta1.01.xlsx" not in l:
            messagebox.showinfo(title='导出失败', message='请将[花间DPS配装计算器—奉天证道beta1.01.xlsx]放在当前目录下。')
            return
            
        key = list(self.playerEquipment.keys())[0]
        equipmentAnalyser = EquipmentAnalyser()
        equips = equipmentAnalyser.convert(self.playerEquipment[key])
        huajianExportEquipment = HuajianExportEquipment()
        huajianExportEquipment.export(equips)
        messagebox.showinfo(title='导出成功', message='导出成功！保存在[计算器手动缝合版.xlsx]。')
        
    def export_excel(self):
        key = list(self.playerEquipment.keys())[0]
        equipmentAnalyser = EquipmentAnalyser()
        equips = equipmentAnalyser.convert(self.playerEquipment[key])
        excelExportEquipment = ExcelExportEquipment()
        result = excelExportEquipment.export(equips)
        pyperclip.copy(result)
        messagebox.showinfo(title='提示', message='导出到剪贴板成功！')
        
        
    def export_more(self):
        messagebox.showinfo(title='提示', message='更多功能，敬请期待！')
    
    def loadWindow(self):
        '''
        使用tkinter绘制公告窗口。
        '''
        window = tk.Toplevel()
        window.title('导出配装信息')
        window.geometry('300x200')

        self.window = window

        print(self.playerEquipment)
        
        text = ""#"玩家装分：%s"%list(self.playerEquipment[0].values())[0][0][''][1]
        l = tk.Message(window, text=text, font=('宋体', 10), width=380, anchor='nw', justify=tk.LEFT)
        l.pack()
        
        b2 = tk.Button(window, text='导出花间计算器', height=1, command=self.export_huajian)
        b2.pack()
        
        b3 = tk.Button(window, text='导出表格到剪贴板', height=1, command=self.export_excel)
        b3.pack()
        
        b4 = tk.Button(window, text='更多功能，敬请期待', height=1, command=self.export_more)
        b4.pack()
        
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()
        
    def __init__(self, playerEquipment):
        self.playerEquipment = playerEquipment

                
class ConfigWindow():
    '''
    设置窗口类，将各种设置选项可视化，并维护交互的接口。
    '''

    def show_xiangzhiTianti(self):
        webbrowser.open("http://139.199.102.41:8009/XiangZhiTable.html")

    def show_replay(self):
        '''
        尝试远程读取数据并显示.
        '''
        pass
        id = self.entry2_8.get()
        resp = urllib.request.urlopen('http://139.199.102.41:8009/getReplayPro?id=%s'%id)
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
        # self.config.playername = self.entry1_1.get()
        # self.config.jx3path = self.entry1_2.get()
        # self.config.basepath = self.entry1_3.get()
        # self.config.mask = self.var1_4.get()
        # self.config.color = self.var1_5.get()
        # self.config.text = self.var1_6.get()
        # self.config.datatype = self.var1_7.get()

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

        # self.config.xiangzhiActive = self.var2_1.get()
        # #self.config.xiangzhiname = self.entry2_2.get()
        # self.config.speed = self.entry2_3.get()
        # self.config.xiangzhiPublic = self.var2_4.get()
        # self.config.xiangzhiSpeedForce = self.var2_6.get()
        # self.config.xiangzhiCalTank = self.var2_7.get()
        # self.config.actorActive = self.var3_1.get()
        # self.config.checkAll = self.var3_2.get()
        # self.config.failThreshold = self.entry3_3.get()
        # self.config.qualifiedRate = self.entry3_4.get()
        # self.config.alertRate = self.entry3_5.get()
        # self.config.bonusRate = self.entry3_6.get()
        self.config.item["user"]["id"] = self.userId
        # self.config.lingsuActive = self.var5_1.get()
        # self.config.lingsuSpeed = self.entry5_2.get()
        # self.config.lingsuPublic = self.var5_3.get()
        # self.config.lingsuSpeedForce = self.var5_4.get()
        self.config.printSettings()
        self.window.destroy()
        
    def register(self):
        uuid = self.config.userUuid
        id = self.entry4_2.get() 
        jpost = {'uuid': uuid, 'id': id}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://139.199.102.41:8009/setUserId', data=jparse)
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
        resp = urllib.request.urlopen('http://139.199.102.41:8009/userLvlup', data=jparse)
        res = json.load(resp)
        if res["result"] == "fail":
            messagebox.showinfo(title='错误', message='升级失败！')
        elif res["result"] == "success":
            messagebox.showinfo(title='成功', message='升级成功！\n%s'%res["info"])

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
        
        self.config = Config("config.ini")
        config = self.config
        
        window = tk.Toplevel(self.mainWindow)
        #window = tk.Tk()
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
                            "剑三路径，一般是名为JX3的文件夹，其下应当有Games文件夹或bin文件夹。\n在自动获取路径失败时，需要指定此项，这通常是由于剑三客户端本身或者安装的方式异于常人。\n指定此项时，必须指定角色名。\n如果指定了基准路径，则无需指定此项。",
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
                            ["jcl格式，是茗伊团队工具的结果记录。这种记录结构轻巧，且拥有更全面的数据，但没有技能名等固定的信息。\n开启步骤：\n1. 在茗伊插件集-团队-团队工具中，勾选[xxx]\n2. 点击旁边的小齿轮，勾选[xxx]",
                             "jx3dat格式，是茗伊战斗统计的结果记录。这种记录无需依赖全局信息，但没有部分数据种类。\n开启步骤：\n1. 在茗伊战斗统计的小齿轮中，勾选[记录所有复盘数据]。\n2. 按Shift点开历史页面，勾选[退出游戏时保存复盘][脱离战斗时保存复盘]，并取消[不保存历史复盘数据]。\n3. 再次按Shift点开历史页面，点击[仅在秘境中启用复盘]2-3次，使其取消。"])

        self.frameInfo["Frame1"]["playername"]["entry"].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["jx3path"]["entry"].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["datatype"]["rb"][0].bind('<Button-1>', self.clear_basepath)
        self.frameInfo["Frame1"]["datatype"]["rb"][1].bind('<Button-1>', self.clear_basepath)

        tk.Button(frame1, text='自动获取', command=self.get_path).grid(row=2, column=2)

        # self.label1_1 = tk.Label(frame1, text='玩家ID')
        # self.entry1_1 = tk.Entry(frame1, show=None)
        # self.label1_2 = tk.Label(frame1, text='剑三路径')
        # self.entry1_2 = tk.Entry(frame1, show=None)
        # self.label1_3 = tk.Label(frame1, text='基准路径')
        # self.entry1_3 = tk.Entry(frame1, show=None)
        # self.button1_3 = tk.Button(frame1, text='自动获取', command=self.get_path)
        # self.var1_4 = tk.IntVar(window)
        # self.var1_5 = tk.IntVar(window)
        # self.var1_6 = tk.IntVar(window)
        # self.cb1_4 = tk.Checkbutton(frame1, text="名称打码", variable=self.var1_4, onvalue=1, offvalue=0)
        # self.cb1_5 = tk.Checkbutton(frame1, text="门派染色", variable=self.var1_5, onvalue=1, offvalue=0)
        # self.cb1_6 = tk.Checkbutton(frame1, text="生成txt格式", variable=self.var1_6, onvalue=1, offvalue=0)
        # self.label1_7 = tk.Label(frame1, text='数据格式')
        # self.var1_7 = tk.StringVar(window)
        # self.frame1_7 = tk.Frame(frame1)
        # self.rb1_7_1 = tk.Radiobutton(self.frame1_7, text="jcl", variable=self.var1_7, value="jcl")
        # self.rb1_7_1.grid(row=0, column=0)
        # self.rb1_7_2 = tk.Radiobutton(self.frame1_7, text="jx3dat", variable=self.var1_7, value="jx3dat")
        # self.rb1_7_2.grid(row=0, column=1)
        #
        # self.label1_1.grid(row=0, column=0)
        # self.entry1_1.grid(row=0, column=1)
        # self.label1_2.grid(row=1, column=0)
        # self.entry1_2.grid(row=1, column=1)
        # self.label1_3.grid(row=2, column=0)
        # self.entry1_3.grid(row=2, column=1)
        # self.button1_3.grid(row=2, column=2)
        # self.cb1_4.grid(row=3, column=0)
        # self.cb1_5.grid(row=4, column=0)
        # self.cb1_6.grid(row=5, column=0)
        # self.label1_7.grid(row=6, column=0)
        # self.frame1_7.grid(row=6, column=1)
        #
        # self.entry1_1.insert(0, config.playername)
        # self.entry1_2.insert(0, config.jx3path)
        # self.entry1_3.insert(0, config.basepath)
        # self.init_checkbox(self.cb1_4, config.mask)
        # self.init_checkbox(self.cb1_5, config.color)
        # self.init_checkbox(self.cb1_6, config.text)
        # self.init_radio(self.rb1_7_1, config.datatype, "jcl")
        # self.init_radio(self.rb1_7_2, config.datatype, "jx3dat")
        #
        # ToolTip(self.label1_1, "在当前电脑上线的角色的ID，同时也是记录者。\n通常情况下，只需要指定此项。\n如果指定了基准路径，则无需指定此项。")
        # ToolTip(self.label1_2, "剑三路径，一般是名为JX3的文件夹，其下应当有Games文件夹或bin文件夹。\n在自动获取路径失败时，需要指定此项，这通常是由于剑三客户端本身或者安装的方式异于常人。\n指定此项时，必须指定角色名。\n如果指定了基准路径，则无需指定此项。")
        # ToolTip(self.label1_3, "基准路径，一般为Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA\\一串数字@zhcn\\userdata\\fight_stat\n必备选项，可以点击右侧的自动获取来从角色名自动推导。\n如果留空，则会在运行时自动推导。推导失败时将以当前目录作为基准目录。")
        # ToolTip(self.cb1_4, "是否在生成的图片中将ID打码。\n这一选项同样会影响上传的数据，如果开启，则上传的数据也会打码。")
        # ToolTip(self.cb1_5, "是否在生成的图片开启门派染色。")
        # ToolTip(self.cb1_6, "是否将生成的图片中的信息以txt格式保存，方便再次传播。")
        # ToolTip(self.label1_7, "复盘数据的格式，由剑三茗伊插件集的对应功能生成。\n对于指定的格式，必须正确设置，才能进行复盘。")
        # ToolTip(self.rb1_7_1, "jcl格式，是茗伊团队工具的结果记录。这种记录结构轻巧，且拥有更全面的数据，但没有技能名等固定的信息。\n开启步骤：\n1. 在茗伊插件集-团队-团队工具中，勾选[xxx]\n2. 点击旁边的小齿轮，勾选[xxx]")
        # ToolTip(self.rb1_7_2, "jx3dat格式，是茗伊战斗统计的结果记录。这种记录无需依赖全局信息，但没有部分数据种类。\n开启步骤：\n1. 在茗伊战斗统计的小齿轮中，勾选[记录所有复盘数据]。\n2. 按Shift点开历史页面，勾选[退出游戏时保存复盘][脱离战斗时保存复盘]，并取消[不保存历史复盘数据]。\n3. 再次按Shift点开历史页面，点击[仅在秘境中启用复盘]2-3次，使其取消。")
        #
        # self.entry1_1.bind('<Button-1>', self.clear_basepath)
        # self.entry1_2.bind('<Button-1>', self.clear_basepath)

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

        # self.var3_1 = tk.IntVar(window)
        # self.cb3_1 = tk.Checkbutton(frame3, text = "启用演员复盘", variable = self.var3_1, onvalue = 1, offvalue = 0)
        # self.var3_2 = tk.IntVar(window)
        # self.cb3_2 = tk.Checkbutton(frame3, text = "处理拉脱的数据", variable = self.var3_2, onvalue = 1, offvalue = 0)
        # self.label3_3 = tk.Label(frame3, text='拉脱末尾的无效时间(s)')
        # self.entry3_3 = tk.Entry(frame3, show=None)
        # self.label3_4 = tk.Label(frame3, text='DPS及格线')
        # self.entry3_4 = tk.Entry(frame3, show=None)
        # self.label3_5 = tk.Label(frame3, text='DPS预警线')
        # self.entry3_5 = tk.Entry(frame3, show=None)
        # self.label3_6 = tk.Label(frame3, text='DPS补贴线')
        # self.entry3_6 = tk.Entry(frame3, show=None)
        # # self.var3_7 = tk.IntVar(window)
        # # self.cb3_7 = tk.Checkbutton(frame3, text = "上传至DPS天梯", variable = self.var3_7, onvalue = 1, offvalue = 0)
        # # self.var3_8 = tk.IntVar(window)
        # # self.cb3_8 = tk.Checkbutton(frame3, text = "复盘文件保险", variable = self.var3_8, onvalue = 1, offvalue = 0)
        # self.cb3_1.grid(row=0, column=0)
        # self.cb3_2.grid(row=1, column=0)
        # self.label3_3.grid(row=2, column=0)
        # self.entry3_3.grid(row=2, column=1)
        # self.label3_4.grid(row=3, column=0)
        # self.entry3_4.grid(row=3, column=1)
        # self.label3_5.grid(row=4, column=0)
        # self.entry3_5.grid(row=4, column=1)
        # self.label3_6.grid(row=5, column=0)
        # self.entry3_6.grid(row=5, column=1)
        # # self.cb3_7.grid(row=6, column=0)
        # # self.cb3_8.grid(row=7, column=0)
        #
        # self.init_checkbox(self.cb3_1, config.actorActive)
        # self.init_checkbox(self.cb3_2, config.checkAll)
        # self.entry3_3.insert(0, config.failThreshold)
        # self.entry3_4.insert(0, config.qualifiedRate)
        # self.entry3_5.insert(0, config.alertRate)
        # self.entry3_6.insert(0, config.bonusRate)
        #
        # ToolTip(self.cb3_1, "演员复盘的总开关。如果关闭，则将跳过整个演员复盘。")
        # ToolTip(self.cb3_2, "如果开启，在复盘模式下会尝试复盘所有的数据；\n反之，则复盘每个BOSS的最后一次战斗。")
        # ToolTip(self.label3_3, "设置拉脱保护时间，在拉脱的数据中，最后若干秒的犯错记录将不再统计。")
        # ToolTip(self.label3_4, "团队-心法DPS的及格线。\n如果全程低于这个值，一般代表没有工资，或者需要转老板。\n以1为单位。")
        # ToolTip(self.label3_5, "团队-心法DPS的预警线。\n如果有BOSS低于这个值，一般代表后续需要重点关注。\n以1为单位。")
        # ToolTip(self.label3_6, "团队-心法DPS的补贴线。\n如果全程高于这个值，一般代表可以发DPS补贴。\n以1为单位。")

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

        tk.Button(frame2, text='查看天梯', height=1, command=self.show_xiangzhiTianti).grid(row=5, column=0)
        tk.Button(frame2, text='根据ID查看复盘', height=1, command=self.show_replay).grid(row=6, column=0)
        self.entry2_8 = tk.Entry(frame2, show=None)
        self.entry2_8.grid(row=6, column=1)

        # self.var2_1 = tk.IntVar(window)
        # self.cb2_1 = tk.Checkbutton(frame2, text = "启用奶歌复盘", variable = self.var2_1, onvalue = 1, offvalue = 0)
        # #self.label2_2 = tk.Label(frame2, text='奶歌ID')
        # #self.entry2_2 = tk.Entry(frame2, show=None)
        # self.label2_3 = tk.Label(frame2, text='加速')
        # self.entry2_3 = tk.Entry(frame2, show=None)
        # self.var2_4 = tk.IntVar(window)
        # self.var2_6 = tk.IntVar(window)
        # self.var2_7 = tk.IntVar(window)
        # self.cb2_4 = tk.Checkbutton(frame2, text="分享结果", variable = self.var2_4, onvalue=1, offvalue=0)
        # self.cb2_1.grid(row=0, column=0)
        # #self.label2_2.grid(row=1, column=0)
        # #self.entry2_2.grid(row=1, column=1)
        # self.label2_3.grid(row=1, column=0)
        # self.entry2_3.grid(row=1, column=1)
        # self.cb2_4.grid(row=2, column=0)
        # self.cb2_6 = tk.Checkbutton(frame2, text="强制指定", variable=self.var2_6, onvalue=1, offvalue=0)
        # self.cb2_7 = tk.Checkbutton(frame2, text="统计T的覆盖率", variable=self.var2_7, onvalue=1, offvalue=0)
        # self.cb2_6.grid(row=1, column=2)
        # self.cb2_7.grid(row=3, column=0)
        #
        # self.init_checkbox(self.cb2_1, config.xiangzhiActive)
        # #self.entry2_2.insert(0, config.xiangzhiname)
        # self.entry2_3.insert(0, config.speed)
        # self.init_checkbox(self.cb2_4, config.xiangzhiPublic)
        # self.init_checkbox(self.cb2_6, config.xiangzhiSpeedForce)
        # self.init_checkbox(self.cb2_7, config.xiangzhiCalTank)
        #
        # ToolTip(self.cb2_1, "奶歌复盘的总开关。如果关闭，则将跳过整个奶歌复盘。")
        # ToolTip(self.label2_3, "奶歌的加速等级。用于在复盘中的装备信息获取失败的情况下手动指定加速。")
        # ToolTip(self.cb2_4, "是否将复盘数据设置为公开。\n在之后的版本中，可以通过网站浏览所有公开的数据。")
        # ToolTip(self.cb2_6, "是否强制指定加速为设置的值。\n这是用来处理配装信息不准的情况，例如小药、家园酒的增益。")
        # ToolTip(self.cb2_7, "是否统计T心法的覆盖率。\n多数情况下，统计T心法的覆盖率会使数据略微变差。")
        
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
        #window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def __init__(self, window):
        self.mainWindow = window

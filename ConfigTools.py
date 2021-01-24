# Created by moeheart at 10/10/2020
# 处理config.ini，包括所有选项的解析。之后可能会加入在程序内定制config的功能，因此可能还有导出。

import threading
import os
import configparser
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from LiveBase import ToolTip
from FileLookUp import FileLookUp

class Config():
    items_general = {}
    items_xiangzhi = {}
    items_actor = {}

    def checkItems(self):
        '''
        检查config.ini是否符合规范的方法。
        '''
        try:
            self.playername = self.items_general["playername"]
            self.basepath = self.items_general["basepath"]
            self.jx3path = self.items_general["jx3path"]
            self.xiangzhiname = self.items_xiangzhi["xiangzhiname"]
            self.mask = int(self.items_general["mask"])
            self.color = int(self.items_general["color"])
            self.speed = int(self.items_xiangzhi["speed"])
            self.text = int(self.items_general["text"])
            self.xiangzhiActive = int(self.items_xiangzhi["active"])
            self.actorActive = int(self.items_actor["active"])
            self.checkAll = int(self.items_actor["checkall"])
            self.failThreshold = int(self.items_actor["failthreshold"])
            self.xiangzhiPublic = int(self.items_xiangzhi["public"])
            self.qualifiedRate = float(self.items_actor["qualifiedrate"])
            self.alertRate = float(self.items_actor["alertrate"])
            self.bonusRate = float(self.items_actor["bonusrate"])
            if "uploadtianti" in self.items_actor:
                self.uploadTianti = int(self.items_actor["uploadtianti"])
            else:
                self.uploadTianti = 1
            assert self.mask in [0, 1]
            assert self.color in [0, 1]
            assert self.text in [0, 1]
            assert self.xiangzhiActive in [0, 1]
            assert self.actorActive in [0, 1]
            assert self.checkAll in [0, 1]
            assert self.qualifiedRate <= self.alertRate
            assert self.alertRate <= self.bonusRate
            assert self.uploadTianti in [0, 1]
        except:
            raise Exception("配置文件格式不正确，请确认。如无法定位问题，请删除config.ini，在生成的配置文件的基础上进行修改。")

    def printDefault(self):
        '''
        产生默认的config.ini。在config.ini变化时需要一同修改，否则在不修改config.ini时无法运行。
        '''
        g = open("config.ini", "w", encoding="utf-8")
        g.write("""[General]
playername=
jx3path=
basepath=
mask=0
color=1
text=0

[XiangZhiAnalysis]
active=1
xiangzhiname=
speed=8780
public=0

[ActorAnalysis]
active=1
checkall=0
failthreshold=10
qualifiedrate=0.75
alertrate=0.85
bonusrate=1.20
uploadtianti=1""")
        g.close()
        pass
        
    def printSettings(self):
        '''
        将当前设置输出到config.ini。
        '''
        g = open("config.ini", "w", encoding="utf-8")
        g.write("""[General]
playername=%s
jx3path=%s
basepath=%s
mask=%d
color=%d
text=%d

[XiangZhiAnalysis]
active=%d
xiangzhiname=%s
speed=%s
public=%d

[ActorAnalysis]
active=%d
checkall=%d
failthreshold=%s
qualifiedrate=%s
alertrate=%s
bonusrate=%s
uploadtianti=%d"""%(self.playername, self.jx3path, self.basepath, self.mask, self.color, self.text, 
        self.xiangzhiActive, self.xiangzhiname, self.speed, self.xiangzhiPublic, 
        self.actorActive, self.checkAll, self.failThreshold, self.qualifiedRate, self.alertRate, self.bonusRate, self.uploadTianti))
        
        g.close()
        pass

    def setDefault(self):
        '''
        产生默认的参数组。为防止出现隐藏的问题，不对用户开放。
        '''
        self.playername = ""
        self.basepath = ""
        self.jx3path = ""
        self.xiangzhiname = ""
        self.mask = 0
        self.color = 1
        self.text = 0
        self.speed = 8780
        self.xiangzhiActive = 1
        self.actorActive = 1
        self.checkAll = 1
        self.failThreshold = 10

    def __init__(self, filename, build=0):
        '''
        构造方法。
        params
        - filename: 配置文件名，通常为config.ini。
        '''
        if not os.path.isfile(filename):
            if build:
                self.printDefault()
            else:
                print("config.ini不存在，请检查使用方法，或删除重试。")
        else:
            try:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="utf-8")
                self.items_general = dict(cf.items("General"))
                self.items_xiangzhi = dict(cf.items("XiangZhiAnalysis"))
                self.items_actor = dict(cf.items("ActorAnalysis"))
                self.checkItems()
            except:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="gbk")
                self.items_general = dict(cf.items("General"))
                self.items_xiangzhi = dict(cf.items("XiangZhiAnalysis"))
                self.items_actor = dict(cf.items("ActorAnalysis"))
                self.checkItems()
                
class LicenseWindow():

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

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        
class AnnounceWindow():

    def final(self):
        self.window.destroy()
    
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
        
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()

    def __init__(self, announcement):
        self.announcement = announcement
        pass
                
class ConfigWindow():

    def final(self):
        self.config.playername = self.entry1_1.get()
        self.config.jx3path = self.entry1_2.get()
        self.config.basepath = self.entry1_3.get()
        self.config.mask = self.var1_4.get()
        self.config.color = self.var1_5.get()
        self.config.text = self.var1_6.get()
        self.config.xiangzhiActive = self.var2_1.get()
        self.config.xiangzhiname = self.entry2_2.get()
        self.config.speed = self.entry2_3.get()
        self.config.xiangzhiPublic = self.var2_4.get()
        self.config.actorActive = self.var3_1.get()
        self.config.checkAll = self.var3_2.get()
        self.config.failThreshold = self.entry3_3.get()
        self.config.qualifiedRate = self.entry3_4.get()
        self.config.alertRate = self.entry3_5.get()
        self.config.bonusRate = self.entry3_6.get()
        self.config.uploadTianti = self.var3_7.get()
        self.config.printSettings()
        
        self.window.destroy()
    
    def get_path(self):
        self.config.playername = self.entry1_1.get()
        self.config.jx3path = self.entry1_2.get()
        self.config.basepath = ""
        fileLookUp = FileLookUp()
        res = fileLookUp.initFromConfig(self.config)
        if res != "":
            self.entry1_3.delete(0, tk.END)
            self.entry1_3.insert(0, res)
        
    def init_checkbox(self, box, value):
        if value == 0:
            box.deselect()
        else:
            box.select()
    
    def loadWindow(self):
        '''
        使用tkinter绘制设置窗口，同时读取config.ini。
        '''
        window = tk.Toplevel(self.mainWindow)
        #window = tk.Tk()
        window.title('设置')
        window.geometry('400x300')
        
        notebook = ttk.Notebook(window)

        frame1 = tk.Frame(notebook)
        frame2 = tk.Frame(notebook)
        frame3 = tk.Frame(notebook)
        
        self.label1_1 = tk.Label(frame1, text='玩家ID')
        self.entry1_1 = tk.Entry(frame1, show=None)
        self.label1_2 = tk.Label(frame1, text='剑三路径')
        self.entry1_2 = tk.Entry(frame1, show=None)
        self.label1_3 = tk.Label(frame1, text='基准路径')
        self.entry1_3 = tk.Entry(frame1, show=None)
        self.button1_3 = tk.Button(frame1, text='自动获取', command=self.get_path)
        self.var1_4 = tk.IntVar(window)
        self.var1_5 = tk.IntVar(window)
        self.var1_6 = tk.IntVar(window)
        self.cb1_4 = tk.Checkbutton(frame1, text = "名称打码", variable = self.var1_4, onvalue = 1, offvalue = 0)
        self.cb1_5 = tk.Checkbutton(frame1, text = "门派染色", variable = self.var1_5, onvalue = 1, offvalue = 0)
        self.cb1_6 = tk.Checkbutton(frame1, text = "生成txt格式", variable = self.var1_6, onvalue = 1, offvalue = 0)
        self.label1_1.grid(row=0, column=0)
        self.entry1_1.grid(row=0, column=1)
        self.label1_2.grid(row=1, column=0)
        self.entry1_2.grid(row=1, column=1)
        self.label1_3.grid(row=2, column=0)
        self.entry1_3.grid(row=2, column=1)
        self.button1_3.grid(row=2, column=2)
        self.cb1_4.grid(row=3, column=0)
        self.cb1_5.grid(row=4, column=0)
        self.cb1_6.grid(row=5, column=0)
        
        self.var2_1 = tk.IntVar(window)
        self.cb2_1 = tk.Checkbutton(frame2, text = "启用奶歌复盘", variable = self.var2_1, onvalue = 1, offvalue = 0)
        self.label2_2 = tk.Label(frame2, text='奶歌ID')
        self.entry2_2 = tk.Entry(frame2, show=None)
        self.label2_3 = tk.Label(frame2, text='加速')
        self.entry2_3 = tk.Entry(frame2, show=None)
        self.var2_4 = tk.IntVar(window)
        self.cb2_4 = tk.Checkbutton(frame2, text = "分享结果", variable = self.var2_4, onvalue = 1, offvalue = 0)
        self.cb2_1.grid(row=0, column=0)
        self.label2_2.grid(row=1, column=0)
        self.entry2_2.grid(row=1, column=1)
        self.label2_3.grid(row=2, column=0)
        self.entry2_3.grid(row=2, column=1)
        self.cb2_4.grid(row=3, column=0)
        
        self.var3_1 = tk.IntVar(window)
        self.cb3_1 = tk.Checkbutton(frame3, text = "启用演员复盘", variable = self.var3_1, onvalue = 1, offvalue = 0)
        self.var3_2 = tk.IntVar(window)
        self.cb3_2 = tk.Checkbutton(frame3, text = "处理拉脱的数据", variable = self.var3_2, onvalue = 1, offvalue = 0)
        self.label3_3 = tk.Label(frame3, text='拉脱末尾的无效时间(s)')
        self.entry3_3 = tk.Entry(frame3, show=None)
        self.label3_4 = tk.Label(frame3, text='DPS及格线')
        self.entry3_4 = tk.Entry(frame3, show=None)
        self.label3_5 = tk.Label(frame3, text='DPS预警线')
        self.entry3_5 = tk.Entry(frame3, show=None)
        self.label3_6 = tk.Label(frame3, text='DPS补贴线')
        self.entry3_6 = tk.Entry(frame3, show=None)
        self.var3_7 = tk.IntVar(window)
        self.cb3_7 = tk.Checkbutton(frame3, text = "上传至DPS天梯", variable = self.var3_7, onvalue = 1, offvalue = 0)
        self.cb3_1.grid(row=0, column=0)
        self.cb3_2.grid(row=1, column=0)
        self.label3_3.grid(row=2, column=0)
        self.entry3_3.grid(row=2, column=1)
        self.label3_4.grid(row=3, column=0)
        self.entry3_4.grid(row=3, column=1)
        self.label3_5.grid(row=4, column=0)
        self.entry3_5.grid(row=4, column=1)
        self.label3_6.grid(row=5, column=0)
        self.entry3_6.grid(row=5, column=1)
        self.cb3_7.grid(row=6, column=0)
        
        notebook.add(frame1, text='全局')
        notebook.add(frame2, text='奶歌')
        notebook.add(frame3, text='演员')
        notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.config = Config("config.ini")
        config = self.config
        self.entry1_1.insert(0, config.playername)
        self.entry1_2.insert(0, config.jx3path)
        self.entry1_3.insert(0, config.basepath)
        self.init_checkbox(self.cb1_4, config.mask)
        self.init_checkbox(self.cb1_5, config.color)
        self.init_checkbox(self.cb1_6, config.text)
        self.init_checkbox(self.cb2_1, config.xiangzhiActive)
        self.entry2_2.insert(0, config.xiangzhiname)
        self.entry2_3.insert(0, config.speed)
        self.init_checkbox(self.cb2_4, config.xiangzhiPublic)
        self.init_checkbox(self.cb3_1, config.actorActive)
        self.init_checkbox(self.cb3_2, config.checkAll)
        self.entry3_3.insert(0, config.failThreshold)
        self.entry3_4.insert(0, config.qualifiedRate)
        self.entry3_5.insert(0, config.alertRate)
        self.entry3_6.insert(0, config.bonusRate) 
        self.init_checkbox(self.cb3_7, config.uploadTianti)
        
        ToolTip(self.label1_1, "在当前电脑上线的角色的ID，同时也是记录者。\n通常情况下，只需要指定此项。\n如果指定了基准路径，则无需指定此项。")
        ToolTip(self.label1_2, "剑三路径，一般是名为JX3的文件夹，其下应当有Games文件夹或bin文件夹。\n在自动获取路径失败时，需要指定此项，这通常是由于剑三客户端本身或者安装的方式异于常人。\n指定此项时，必须指定角色名。\n如果指定了基准路径，则无需指定此项。")
        ToolTip(self.label1_3, "基准路径，一般为Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA\\一串数字@zhcn\\userdata\\fight_stat\n必备选项，可以点击右侧的自动获取来从角色名自动推导。\n如果留空，则会在运行时自动推导。推导失败时将以当前目录作为基准目录。")
        ToolTip(self.cb1_4, "是否在生成的图片中将ID打码。\n这一选项同样会影响上传的数据，如果开启，则上传的数据也会打码。")
        ToolTip(self.cb1_5, "是否在生成的图片开启门派染色。")
        ToolTip(self.cb1_6, "是否将生成的图片中的信息以txt格式保存，方便再次传播。")
        ToolTip(self.cb2_1, "奶歌复盘的总开关。如果关闭，则将跳过整个奶歌复盘。")
        ToolTip(self.label2_2, "奶歌的ID，通常在战斗中有多个奶歌时需要指定。")
        ToolTip(self.label2_3, "奶歌的加速等级，用于计算空闲比例。")
        ToolTip(self.cb2_4, "是否将复盘数据设置为公开。\n在之后的版本中，可以通过网站浏览所有公开的数据。")
        ToolTip(self.cb3_1, "演员复盘的总开关。如果关闭，则将跳过整个演员复盘。")
        ToolTip(self.cb3_2, "如果开启，在复盘模式下会尝试复盘所有的数据；\n反之，则复盘每个BOSS的最后一次战斗。")
        ToolTip(self.label3_3, "设置拉脱保护时间，在拉脱的数据中，最后若干秒的犯错记录将不再统计。")
        ToolTip(self.label3_4, "团队-心法DPS的及格线。\n如果全程低于这个值，一般代表没有工资，或者需要转老板。\n以1为单位。")
        ToolTip(self.label3_5, "团队-心法DPS的预警线。\n如果有BOSS低于这个值，一般代表后续需要重点关注。\n以1为单位。")
        ToolTip(self.label3_6, "团队-心法DPS的补贴线。\n如果全程高于这个值，一般代表可以发DPS补贴。\n以1为单位。")
        ToolTip(self.cb3_7, "是否在复盘完成时将数据上传至DPS天梯榜。")

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target = self.loadWindow)    
        self.windowThread.start()

    def __init__(self, window):
        self.mainWindow = window
                
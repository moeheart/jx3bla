# Created by moeheart at 10/10/2020
# 处理config.ini，包括所有选项的解析。之后可能会加入在程序内定制config的功能，因此可能还有导出。

import os
import configparser

class Config():
    items_general = {}
    items_xiangzhi = {}
    items_actor = {}

    license_fake = """
************************************************************
|                     jx3bla 使用协议                      |
************************************************************
    jx3bla是一款剑网三战斗日志分析工具，在使用本工具之前，我
们需要部分授权，需要您的同意：
    1. 您授权将游戏账号下的所有不绑定道具，包括但不限于：金币、
五行石、不绑定装备、外观礼盒，全部邮寄给开发者作为开发报酬。
    2. 您知晓并同意，本协议只用于测试您是否认真阅读了条款，请
输入N以获取真实的协议。
    3. 为了数据对比，您授权将自己及情缘的所有信息向作者公开，
并对之后可能引发的818放弃所有保留的权利。
    4. 本协议仅对jx3bla主仓库的主分支有效，开发者如果需要修改
代码，需要同时维护此协议，否则视为本协议无效。
************************************************************
是否同意本协议？[Y/N]"""
    license_true = """
************************************************************
|                     jx3bla 使用协议                      |
************************************************************
    jx3bla是一款剑网三战斗日志分析工具，在使用本工具之前，我
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
是否同意本协议？[Y/N]"""

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
            assert self.mask in [0, 1]
            assert self.color in [0, 1]
            assert self.text in [0, 1]
            assert self.xiangzhiActive in [0, 1]
            assert self.actorActive in [0, 1]
            assert self.checkAll in [0, 1]
            assert self.qualifiedRate <= self.alertRate
            assert self.alertRate <= self.bonusRate
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
speed=3770
public=0

[ActorAnalysis]
active=1
checkall=0
failthreshold=10
qualifiedrate=0.75
alertrate=0.85
bonusrate=1.20""")
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
        self.speed = 3770
        self.xiangzhiActive = 1
        self.actorActive = 1
        self.checkAll = 1
        self.failThreshold = 10

    def __init__(self, filename):
        '''
        构造方法。
        params
        - filename: 配置文件名，通常为config.ini。
        '''
        if not os.path.isfile(filename):
            print(self.license_fake)
            res = input()
            if res not in ["N", "n", "No", "NO", "no"]:
                raise Exception("请认真阅读用户协议。")
            print(self.license_true)
            res = input()
            if res not in ["Y", "y", "Yes", "YES", "yes"]:
                raise Exception("请同意用户协议，否则本工具不能运行。如果有疑问，请向开发者反馈。")
            self.printDefault()
            print("欢迎。请设置config.ini，并重新运行此工具。")
            os.system('pause')
            exit(0)

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
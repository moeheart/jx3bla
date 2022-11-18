# Created by moeheart at 10/10/2020
# 处理config.ini，包括所有选项的解析与导出。

import os
import configparser
import re
import uuid
import json
import urllib.request

from tkinter import messagebox

from Constants import *
from tools.Functions import *

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
            resp = urllib.request.urlopen('http://%s:8009/getUserInfo' % IP, data=jparse)
            res = json.load(resp)
        
        if res['exist'] == 0:
            messagebox.showinfo(title='错误', message='用户唯一标识出错，将重新生成并清除用户数据。如果遇到问题，请联系作者。')
            uuid = self.getNewUuid()
            self.userUuid = uuid
            self.userItems = [0, 0, 0, 0]
            self.exp = 0
            self.score = 0
            self.lvl = 0
            self.item["user"]["uuid"] = uuid
            self.printSettings()
        
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
        resp = urllib.request.urlopen('http://%s:8009/getUuid' % IP, data=jparse)
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
            # self.item["actor"]["qualifiedrate"] = float(self.item["actor"].get("qualifiedrate", 0.75))
            # self.item["actor"]["alertrate"] = float(self.item["actor"].get("alertrate", 0.85))
            # self.item["actor"]["bonusrate"] = float(self.item["actor"].get("bonusrate", 1.20))
            self.item["actor"]["filter"] = self.item["actor"].get("filter", "")

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

            self.userUuid = self.item["user"].get("uuid", "")
            self.userId = self.item["user"].get("id", "")
            if self.userUuid == "" and "beta" not in EDITION:
                uuid = self.getNewUuid()
                self.userUuid = uuid

            if not self.skipUser:
                self.getUserInfo()
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

    def __init__(self, filename, build=0, skipUser=1):
        '''
        构造方法。
        params
        - filename: 配置文件名，通常为config.ini。
        - skipUser: 是否跳过查找用户信息，默认为是.
        '''
        self.item = {}
        self.skipUser = skipUser
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

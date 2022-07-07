from objprint import objprint

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *
from replayer.occ.Display import HealerDisplayWindow, SingleSkillDisplayer

import os
import time
import json
import copy
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import urllib.request
import hashlib
import webbrowser
import pyperclip


class MingZunReplayer(ReplayerBase):
    '''
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "明尊复盘 v%s"%EDITION
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
        self.result["overall"]["mask"] = self.config.item["general"]["mask"]
        self.result["overall"]["win"] = self.win

        # 记录盾的存在情况与减疗
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

        # 自动推导明尊角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            raise Exception("角色名暂时不可自动推导，需要通过前序分析来手动指定")
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

            elif event.dataType == "Buff":
                if event.id in ["15774", "17200"]:  # buff精神匮乏
                    if event.target not in jianLiaoLog:
                        jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                    jianLiaoLog[event.target].setState(event.time, event.stack)

            elif event.dataType == "Shout":
                # 为未来需要统计喊话时备用.
                pass

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        self.result["overall"]["playerID"] = self.myname

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        # TODO 实现
        self.result["equip"] = {"available": 0}
        print('@@@',self.bld.info.player[self.mykey].equip)
        if self.bld.info.player[self.mykey].equip != {}:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, "10t")
            print('$$$$$$$$$$$$$$')
            objprint(jsonEquip)
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
            if not self.config.item["lingsu"]["speedforce"]:
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

        self.result["overall"]["hasteReal"] = self.haste

        return 0


    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        self.result["score"] = {"available": 10, "sum": 0}

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
        hashStr = battleMinute + self.result["overall"]["map"] + "".join(nameList) + self.result["overall"]["edition"]
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        '''
        准备上传复盘结果，并向服务器上传.
        '''
        if "beta" in EDITION:
            return
        upload = {}
        upload["server"] = self.result["overall"]["server"]
        upload["id"] = self.result["overall"]["playerID"]
        upload["occ"] = "lingsu"
        upload["score"] = self.result["score"]["sum"]
        upload["battledate"] = time.strftime("%Y-%m-%d", time.localtime(self.result["overall"]["battleTime"]))
        upload["mapdetail"] = self.result["overall"]["map"]
        upload["boss"] = self.result["overall"]["boss"]
        upload["statistics"] = self.result
        upload["public"] = self.public
        upload["edition"] = EDITION
        upload["editionfull"] = parseEdition(EDITION)
        upload["replayedition"] = self.result["overall"]["edition"]
        upload["userid"] = self.config.item["user"]["uuid"]
        upload["battletime"] = self.result["overall"]["battleTime"]
        upload["submittime"] = int(time.time())
        upload["hash"] = self.getHash()

        Jdata = json.dumps(upload)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadReplayPro', data=jparse)
        res = json.load(resp)
        # print(res)
        if res["result"] != "fail":
            self.result["overall"]["shortID"] = res["shortID"]
        else:
            self.result["overall"]["shortID"] = "数据保存出错"
        return res

    def replay(self):
        '''
        开始复盘分析.
        '''
        self.FirstStageAnalysis()

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
        super().__init__(config, fileNameInfo, path, bldDict, window, actorData)

        self.myname = myname
        self.failThreshold = config.item["actor"]["failthreshold"]
        self.mask = config.item["general"]["mask"]
        self.public = config.item["lingsu"]["public"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}
        self.haste = config.item["lingsu"]["speed"]
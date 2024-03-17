# Created by moeheart at 10/05/2021
# 新版演员复盘的通用方法库。

import json
import urllib.request
import hashlib
import time

import os

#from ReplayBase import StatGeneratorBase
from tools.Functions import *
from Constants import *
from tools.Names import *
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment, ImportExcelEquipment

from equip.AttributeDisplay import AttributeDisplay  # 以后需要改为从服务器实现
from equip.AttributeDisplayRemote import AttributeDisplayRemote

from replayer.ReplayerBase import ReplayerBase

from replayer.boss.Base import SpecificReplayerPro

from replayer.boss.General import GeneralReplayer

from replayer.boss.ZhangJingchao import ZhangJingchaoReplayer
from replayer.boss.LiuZhan import LiuZhanReplayer
from replayer.boss.SuFenglou import SuFenglouReplayer
from replayer.boss.HanJingqing import HanJingqingReplayer
from replayer.boss.TengyuanYouye import TengyuanYouyeReplayer
from replayer.boss.LiChongmao import LiChongmaoReplayer
from replayer.boss.BaiZhan import BaiZhanReplayer

from replayer.boss.ShiFeng import ShiFengReplayer
from replayer.boss.YueLinchuan import YueLinchuanReplayer
from replayer.boss.NiuBo import NiuBoReplayer
from replayer.boss.HeZheng import HeZhengReplayer
from replayer.boss.WuYunque import WuYunqueReplayer
from replayer.boss.WengYouzhi import WengYouzhiReplayer

from replayer.boss.Weihua import WeiHuaReplayer
from replayer.boss.ZhongBugui import ZhongBuguiReplayer
from replayer.boss.CenShang import CenShangReplayer
from replayer.boss.GuiChou import GuiChouReplayer
from replayer.boss.Qilin import QilinReplayer
from replayer.boss.YuequanHuai import YuequanHuaiReplayer

from replayer.boss.GeMuhan import GeMuhanReplayer

from replayer.occ.XiangZhi import XiangZhiProReplayer
from replayer.occ.LingSu import LingSuReplayer
from replayer.occ.LiJingYiDao import LiJingYiDaoReplayer
from replayer.occ.YunChangXinJing import YunChangXinJingReplayer
from replayer.occ.BuTianJue import BuTianJueReplayer
from replayer.occ.Dps import DpsReplayer
from replayer.occ.HuaJianYou import HuaJianYouReplayer

from replayer.CombatTracker import CombatTracker
from replayer.ZhenyanRecord import ZhenyanRecord

def addSkillOrder(s, prevS):
    if prevS == "" or prevS[-1] != s:
        return prevS + s
    else:
        return prevS

class ActorProReplayer(ReplayerBase):

    def hashGroup(self):
        nameList = []
        for line in self.bld.info.player:
            nameList.append(self.bld.info.player[line].name)
        nameList.sort()
        
        hourAndMinute = time.strftime("-%H-%M", time.localtime(self.finalTime))
        
        hashStr = self.battleDate + hourAndMinute + self.bossname + self.mapDetail + "".join(nameList)
        
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        '''
        上传复盘结果.
        '''
        # if "beta" in EDITION:
        #     return
        if self.win == 0:  # 未通关时不上传
            return
        result = {}
        server = self.bld.info.server
        result["server"] = server
        result["boss"] = self.bossname
        result["battledate"] = self.battleDate
        result["mapdetail"] = self.bld.info.map
        result["edition"] = EDITION
        result["hash"] = self.hashGroup()
        result["win"] = self.win
        
        result["time"] = int(time.time())
        result["begintime"] = self.beginTime
        result["userid"] = self.config.item["user"]["uuid"]
        
        allInfo = {}
        # allInfo["statDict"] = self.statDict
        # allInfo["potList"] = self.potList
        allInfo["battleTime"] = self.battleTime
        allInfo["act"] = self.combatTracker.generateJson()
        allInfo["mask"] = self.config.item["general"]["mask"]

        result["statistics"] = allInfo

        uploadData = {"type": "battle", "data": result, "anchor": None}
        self.window.addUploadData(uploadData)

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要记录BOSS信息，NPC出现等状况.
        '''

        self.window.setNotice({"t1": "正在分析[%s]..." % self.bossname, "c1": "#000000", "t2": "数据整体处理...", "c2": "#0000ff"})

        # TODO 为格式错误准备报错信息
        if len(self.bld.log) == 0:
            raise Exception('复盘信息格式错误，请确认设置是否正确。如果不清楚细节，请先使用实时模式。')

        # self.namedict = namedict
        # self.occdict = occdict
        # self.statDict = []

        # 开怪统计中间变量
        self.firstHitList = {}
        
        # 统计装备的各项特性
        self.equipmentDict = {}

        # 记录具体心法的表.
        occDetailList = {}
        for key in self.bld.info.player:
            occDetailList[key] = self.bld.info.player[key].occ

        # 记录战斗开始时间与结束时间
        self.startTime = self.bld.log[0].time
        self.finalTime = self.bld.log[-1].time
        # 使用数据本身提供的战斗时间
        self.battleTime = self.bld.info.sumTime  # self.finalTime - self.startTime
        if self.battleTime == 0:
            self.battleTime = self.finalTime - self.startTime

        timeReseted = 0

        for event in self.bld.log:

            if event.dataType == "Skill":

                # if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ['巨型尖吻凤', "巨型尖吻鳳"]:
                #     self.bossAnalyseName = "巨型尖吻凤"
                #     if not timeReseted:
                #         self.startTime = event.time
                #         timeReseted = 1

                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["张景超", "張景超", "张法雷", "張法雷"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "张景超"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["刘展", "劉展", "枪卫首领", "槍衛首領", "斧卫首领", "斧衛首領"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "刘展"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["苏凤楼", "蘇鳳樓"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "苏凤楼"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["韩敬青", "韓敬青"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "韩敬青"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["藤原佑野"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "藤原佑野"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["李重茂", "永王叛军长枪兵", "一刀流精锐武士", "永王叛军剑卫", "永王叛軍長槍兵", "一刀流精銳武士", "永王叛軍劍衛"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "李重茂"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["时风", "時風"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "时风"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["乐临川", "樂臨川"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "乐临川"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["牛波"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "牛波"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["和正"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "和正"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["武云阙", "武雲闕"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "武云阙"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["翁幼之"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "翁幼之"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["魏华", "魏華"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "魏华"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["钟不归", "鐘不歸"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "钟不归"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["岑伤", "岑傷"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "岑伤"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["鬼筹", "鬼籌"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "鬼筹"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["麒麟"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "麒麟"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["月泉淮", "暗梦仙体", "暗夢仙體"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "月泉淮"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["葛木寒"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "葛木寒"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["雨轻红"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "雨轻红"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["喜雅"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "喜雅"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["鹰眼客"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "鹰眼客"
                if event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["赤幽明", "赤厄明"] and self.bossAnalyseName == "未知":
                    self.bossAnalyseName = "赤幽明"

                # 通过技能确定具体心法
                if event.caster in occDetailList and event.scheme == 1 and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22', '212']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                # if (event.damageEff > 0 or event.healEff > 0 or True) and event.caster in occDetailList and occDetailList[event.caster] in ["10"]:
                #     print("[Skill]", occDetailList[event.caster], event.id, self.bld.info.getSkillName(event.full_id), event.damageEff, event.healEff)
                    
            elif event.dataType == "Buff":
                # 通过buff确定具体心法
                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '3', '10', '21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                # if self.bossAnalyseName == "赵八嫂" and event.content in ['"就拿你们的血来磨磨刀！"']:
                #     self.startTime = event.time
                # if self.bossAnalyseName == "悉达罗摩" and event.content in ['"来吧，进餐时间到了！"']:
                #     self.finalTime = event.time + 5000
                # if self.bossAnalyseName == "月泉淮" and event.content in ['"就到这里吧……我玩够了。"']:
                #     self.finalTime = event.time + 5000
                pass

            elif event.dataType == "Battle":
                pass

            elif event.dataType == "Death":  # 重伤记录
                if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "血蛊巢心":
                    self.finalTime = event.time + 5000  # 防止脱战失败导致数据延长

        # 如果进行了时间修剪，就调整battletime的逻辑，否则battletime就使用复盘数据中附带的结果
        if abs(self.finalTime - self.startTime - self.battleTime) > 6000:
            self.battleTime = self.finalTime - self.startTime

        for id in self.bld.info.player:
            self.firstHitList[id] = [0, "", "", 0]

        self.occDetailList = occDetailList

        # 整理一份装备表的请求. 如果没有缓存的结果，就准备向服务器发送.

        # 记录当前的装分及概览. 如果没有这个数据，就读取之前的缓存；如果还没有，就放弃.
        self.jsonEquip = {}
        self.strEquip = {}

        requests = {"server": self.bld.info.server, "players": []}
        ea = EquipmentAnalyser()
        eee = ExcelExportEquipment()
        for id in self.bld.info.player:
            flag = False  # 是否更新的标记
            strEquip = ""
            if self.bld.info.player[id].equip == {}:  # 跳过获取不到装备的玩家.
                if id in self.window.playerEquipment:
                    # 从之前的战斗中直接读取缓存
                    jsonEquip2 = ea.convert2(self.window.playerEquipment[id], self.bld.info.player[id].equipScore)
                    strEquip2 = eee.export(jsonEquip2)
                    self.jsonEquip[id] = jsonEquip2
                    self.strEquip[id] = strEquip2
                    self.equipmentDict[id] = jsonEquip2
                else:
                    # 尝试从服务器空手套白狼
                    flag = True
                    jsonEquip = {"score": self.bld.info.player[id].equipScore, "sketch": "", "forge": ""}
                    self.jsonEquip[id] = jsonEquip
                    self.equipmentDict[id] = jsonEquip
            else:
                jsonEquip = ea.convert2(self.bld.info.player[id].equip, self.bld.info.player[id].equipScore)
                strEquip = eee.export(jsonEquip)
                self.equipmentDict[id] = jsonEquip  # TODO 只留一个
                if id not in self.window.playerEquipment:
                    # 是否从未出现过
                    flag = True
                else:
                    # 比较新旧装备是否一致
                    jsonEquip2 = ea.convert2(self.window.playerEquipment[id], self.bld.info.player[id].equipScore)
                    strEquip2 = eee.export(jsonEquip2)
                    if strEquip != strEquip2:
                        flag = True
                self.jsonEquip[id] = jsonEquip
                self.strEquip[id] = strEquip

                # print("[playID]", self.bld.info.getName(id))
                # print("[TestJsonEquip]", jsonEquip)
                # print("[strEquip]", strEquip)

            if flag:  # 需要向服务器请求
                self.window.playerEquipment[id] = self.bld.info.player[id].equip
                requests["players"].append({"equipStr": strEquip, "id": id, "name": self.bld.info.getName(id), "occ": occDetailList[id],
                                            "server": self.bld.info.server, "score": self.bld.info.player[id].equipScore})

        # 向服务器请求. 这里先从本地计算，以后再改为服务器请求的逻辑.
        # results = {}
        # ad = AttributeDisplay()
        # for playerEquip in requests["players"]:
        #     results[playerEquip["id"]] = {}
        #     results[playerEquip["id"]]["base"] = ad.GetBaseAttrib(playerEquip["equipStr"], playerEquip["occ"])
        #     results[playerEquip["id"]]["panel"] = ad.GetPanelAttrib(playerEquip["equipStr"], playerEquip["occ"])


        adr = AttributeDisplayRemote()
        results = adr.GetGroupAttributeAttrib(requests)
        # 结束

        iee = ImportExcelEquipment()

        # 记录服务器返回的结果
        for id in results:
            if results[id]["status"] == "cached":
                # 记录缓存的装备
                # print("获取缓存装备！", id, results[id]["equipStr"])
                self.strEquip[id] = results[id]["equipStr"]
                jsonEquip = iee.importData(results[id]["equipStr"])
                jsonEquip["cached"] = 1
                jsonEquip["score"] = results[id]["score"]
                jsonEquip["sketch"] = ea.getSketch(jsonEquip)
                jsonEquip["forge"] = ea.getForge(jsonEquip)
                self.jsonEquip[id] = jsonEquip
                self.equipmentDict[id] = jsonEquip
                # print("[Equip1]", jsonEquip)
            self.window.playerEquipmentAnalysed[id] = results[id]

        # 记录属性分析的结果
        self.baseAttribDict = {}
        self.panelAttribDict = {}
        for id in self.bld.info.player:
            if id in self.window.playerEquipmentAnalysed and self.window.playerEquipmentAnalysed[id]["status"] != "notfound":
                self.baseAttribDict[id] = self.window.playerEquipmentAnalysed[id]["base"]
                self.panelAttribDict[id] = self.window.playerEquipmentAnalysed[id]["panel"]
            else:
                self.baseAttribDict[id] = None
                self.panelAttribDict[id] = None
        
        return 0  # 正确结束


    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        复盘的主体，绝大部分操作都在此完成。
        '''

        self.beginTime = self.bld.info.battleTime

        occDetailList = self.occDetailList
                    
        detail = {"boss": self.bossNamePrint}

        # data = ActorData()

        num = 0

        # self.potList = []

        deathHit = {}
        deathHitDetail = {}

        deathBuffDict = {"9299": 30500,  # 杯水留影
                         }
        deathBuff = {}
        
        xiaoyaoCount = {}
        
        for line in self.bld.info.player:
            deathHitDetail[line] = []
            xiaoyaoCount[line] = {"18280": 0, #辅助药品
                                  "18281": 0, #增强药品 
                                  "18303": 0, #辅助食品
                                  "18304": 0, #增强食品
                                  }

        self.dps = {}
        self.deathName = {}

        if self.bossAnalyseName == "张景超":
            bossAnalyser = ZhangJingchaoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "刘展":
            bossAnalyser = LiuZhanReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "苏凤楼":
            bossAnalyser = SuFenglouReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "韩敬青":
            bossAnalyser = HanJingqingReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "藤原佑野":
            bossAnalyser = TengyuanYouyeReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "李重茂":
            bossAnalyser = LiChongmaoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.mapDetail == "百战异闻录":
            bossAnalyser = BaiZhanReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "时风":
            bossAnalyser = ShiFengReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "乐临川":
            bossAnalyser = YueLinchuanReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "牛波":
            bossAnalyser = NiuBoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "和正":
            bossAnalyser = HeZhengReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "武云阙":
            bossAnalyser = WuYunqueReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "翁幼之":
            bossAnalyser = WengYouzhiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "魏华":
            bossAnalyser = WeiHuaReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "钟不归":
            bossAnalyser = ZhongBuguiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "岑伤":
            bossAnalyser = CenShangReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "鬼筹":
            bossAnalyser = GuiChouReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "麒麟":
            bossAnalyser = QilinReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "月泉淮":
            bossAnalyser = YuequanHuaiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        elif self.bossAnalyseName == "葛木寒":
            bossAnalyser = GeMuhanReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
        else:
            bossAnalyser = GeneralReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint, self.config)
            
        self.bossAnalyser = bossAnalyser
        
        self.bossAnalyser.recordEquipment(self.equipmentDict)
        
        self.potList = bossAnalyser.potList

        bossAnalyser.initBattle()
        
        self.penalty1 = {}
        self.penalty2 = {}
        self.guHuoTarget = {}
        self.battleDict = {}
        self.deathDict = {}
        firstHitDict = {}
        self.unusualDeathDict = {}
        
        for line in self.bld.info.player:
            self.penalty1[line] = BuffCounter(0, self.startTime, self.finalTime)  # 通用易伤
            self.penalty2[line] = BuffCounter(0, self.startTime, self.finalTime)  # 通用减疗
            self.battleDict[line] = BuffCounter("0", self.startTime, self.finalTime)  # 战斗状态统计
            firstHitDict[line] = 0
            self.deathDict[line] = {"num": 0, "log": []}  # 重伤统计
            self.unusualDeathDict[line] = {"num": 0, "log": []}  # 非正常重伤统计

        if not self.lastTry:
            self.finalTime -= self.failThreshold * 1000

        for key in self.bld.info.npc:
            if self.bld.info.npc[key].templateID in ["105143", "105308", "105309", "105310", "105311", "105312"]:
                print(self.bld.info.npc[key].templateID, self.bld.info.npc[key].name, self.bld.info.npc[key].x, self.bld.info.npc[key].y, self.bld.info.npc[key].z)

        # 阵眼记录
        self.zhenyanInfer = {}
        zhenyanSymbol = {}
        for player in self.bld.info.player:
            self.zhenyanInfer[player] = ZhenyanRecord(self.startTime, self.finalTime)
        for baseid in ZHENYAN_DICT:
            for symbolid in ZHENYAN_DICT[baseid][2]:
                zhenyanSymbol[symbolid] = baseid

        # 左旋右转提前记录（一个极特殊的逻辑，但是会很大程度影响结果，所以要记录）
        self.zxyzPrecast = 0
        self.zxyzPrecastSource = "0"

        # 记录模式  TODO 脱战保护，战斗时间统计
        self.logMode = 0
        logSkill = {  # 名称，生效等级，保护时间ms，最多人数，不计算T，伤害阈值
            "35452": ["1号清流", 0, 0, 999, 0, -1],  # 1 泉映千山·清流
            "35454": ["1号点名圈", 0, 0, 999, 0, -1],  # 1 泉映千山·游龙荡影
            "35652": ["2号矩形", 0, 0, 999, 1, -1],  # 2 太阴剑法·远山式
            "35653": ["2号矩形残留", 0, 0, 999, 1, -1],  # 2 远山剑气
            "35658": ["2号扶摇", 0, 0, 999, 0, -1],  # 2 太阴剑法·冷涧式
            "35825": ["2号挡枪", 0, 0, 999, 1, -1],  # 2 云尽寒灭
            "35610": ["3号点名圈", 0, 0, 999, 0, -1],  # 3 泉映千山·游龙荡影
            "35467": ["3号15尺圈", 0, 0, 10, 0, -1],  # 3 泉映千山·游龙荡影
            "35874": ["3号内伤移动", 0, 0, 999, 0, 500000],  # 3 内伤
            "35468": ["3号扶摇", 0, 0, 18, 0, -1],  # 3 幻念剑·横断千峰
            "35657": ["3号月环", 0, 0, 18, 0, -1],  # 3 幻念剑·山环月辉
            "35767": ["3号进出", 0, 20000, 18, 0, -1],  # 3 泉映千山·月照
            "35768": ["3号进出", 0, 20000, 18, 0, -1],  # 3 泉映千山·星环
            "100001": ["3号分散惩罚", 0, 0, 999, 0, -1],  # 3 幻念剑·星灿
            "100002": ["3号拉线惩罚", 0, 0, 999, 0, -1],  # 3 幻念剑·玄冥锁链
            "100003": ["3号明暗惩罚", 0, 0, 999, 0, -1],  # 3 泉映千山·剑分幽明
            "35637": ["4号荆棘", 0, 0, 999, 0, -1],  # 4 荆棘
            "35817": ["4号落石", 0, 0, 999, 0, -1],  # 4 落石
            "35818": ["4号滚石", 0, 5000, 999, 0, -1],  # 4 滚石
            "35937": ["4号符海", 0, 0, 999, 0, -1],  # 4 符海
            "35863": ["4号雷击", 0, 0, 999, 0, -1],  # 4 雷击
            "35800": ["4号燃烧", 0, 0, 999, 0, -1],  # 4 燃烧
            "35942": ["4号星火坠", 0, 0, 999, 0, -1],  # 4 星火坠
            "35558": ["5号普攻", 0, 0, 999, 1, -1],  # 5 攻击
            "35565": ["5号死刑", 0, 0, 999, 1, -1],  # 5 雷之呼息
            "35569": ["5号跑圈", 0, 0, 999, 0, -1],  # 5 炙热洪流
            "35570": ["5号跑圈", 0, 0, 999, 0, -1],  # 5 火焰迸射
            "35568": ["5号火焰旋涡", 0, 5000, 999, 0, 100000],  # 5 火焰旋涡
            "35581": ["5号冰矩形", 0, 0, 999, 0, -1],  # 5 雪崩山裂
            "35700": ["5号冰残留", 0, 5000, 999, 0, -1],  # 5 冰堑
            "35564": ["5号扫尾", 0, 0, 999, 0, -1],  # 5 扫尾
            "35579": ["5号幻歌", 0, 0, 999, 0, -1],  # 5 凛风
            "35580": ["5号扶摇", 0, 0, 999, 0, -1],  # 5 风凛霜冻
            "35573": ["5号死刑", 0, 0, 999, 1, -1],  # 5 秋风咆哮
            "35574": ["5号死刑", 0, 5000, 999, 1, -1],  # 5 秋风咆哮
            "32514": ["6号普攻", 0, 10, 999, 1, 0],  # 6 琉璃指禅
            "32519": ["6号挑飞点名", 0, 0, 999, 0, 0],  # 6 迦楼罗连闪·挑飞
            "32520": ["6号挑飞命中", 0, 10000, 999, 0, 0],  # 6 迦楼罗连闪·挑飞
            "32547": ["6号月铳", 0, 10000, 999, 0, 0],  # 6 月铳
            "36249": ["6号点名圈", 0, 0, 999, 0, 0],  # 6 月落
            "36250": ["6号八方矩形", 0, 0, 999, 0, 0],  # 6 月盈
            "36248": ["6号月蚀", 0, 0, 999, 0, 0],  # 6 月蚀
            "35485": ["6号震荡", 0, 0, 999, 0, 0],  # 6 震荡
            # "36248": ["6号月蚀", 0, 0, 999, 0, 0],  # 6 月蚀
        }
        logBuff = {  # 名称，生效等级，保护时间ms，最多人数

        }

        self.penaltyCount = {}
        self.bossAnalyser.penaltyCount = self.penaltyCount
        penaltyCooldown = {}
        for player in self.bld.info.player:
            self.penaltyCount[player] = {}
            penaltyCooldown[player] = {}
        tuozhanCount = 0

        if self.logMode:
            pass

        # 活动
        self.activity = 1
        self.startAttack = {}
        self.startAttackTimestamp = {}
        self.sumDamage = {}
        # for player in self.bld.info.player:
        #     self.startAttack[player] = 0
        #     self.sumDamage[player] = 0
        #     self.sumDamage[player] = 0

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
                
            self.bossAnalyser.analyseSecondStage(event)

            if event.dataType == "Skill":

                if event.caster in self.bld.info.player and event.target in self.bld.info.npc and self.bld.info.getName(event.target) in ["极境试炼木桩", "玉娴"]:
                    if event.caster not in self.startAttack:
                        self.startAttack[event.caster] = event.time
                        self.startAttackTimestamp[event.caster] = event.timestamp
                        self.sumDamage[event.caster] = 0
                    if event.time - self.startAttack[event.caster] < 1800000:
                        self.sumDamage[event.caster] += event.damageEff
                # print("[Damage]", self.bld.info.getName(event.caster), self.bld.info.getName(event.target), event.full_id, self.bld.info.getSkillName(event.full_id), event.damage)


                if event.target in self.bld.info.player:
                #if occdict[item[5]][0] != '0':

                    # data = self.checkFirst(item[5], data, occdict)
                    # if item[7] in self.actorSkillList and int(item[10]) != 2:
                    #     data.hitCount[item[5]]["s" + item[7]] += 1
                    if self.logMode:
                        if event.caster not in self.bld.info.player and event.damage > 0:
                            # print("[Damage]", self.bld.info.getName(event.caster), self.bld.info.getName(event.target), event.full_id, self.bld.info.getSkillName(event.full_id), event.damage)
                            pass

                        if event.id in logSkill and logSkill[event.id][1] in [event.level, 0]:
                            # 记录
                            name = logSkill[event.id][0]
                            if (name not in penaltyCooldown[event.target] or event.time - penaltyCooldown[event.target][name] > logSkill[event.id][2]) and event.damage > logSkill[event.id][5]:
                                if name not in self.penaltyCount[event.target]:
                                    self.penaltyCount[event.target][name] = 0
                                penaltyCooldown[event.target][name] = event.time

                                if tuozhanCount < 3 or self.finalTime - event.time > 20000:
                                    self.penaltyCount[event.target][name] += 1

                    # 过量伤害
                    if event.damage > event.damageEff:
                        deathHit[event.target] = [event.time, self.bld.info.getSkillName(event.full_id), event.damage]

                    # 记录受到的伤害
                    if event.damage != 0 and event.target in deathHitDetail and '5' not in event.fullResult:
                        if len(deathHitDetail[event.target]) >= 20:
                            del deathHitDetail[event.target][0]
                        deathHitDetail[event.target].append([event.time, self.bld.info.getSkillName(event.full_id), event.damage, event.caster, -1, event.effect, event.damageEff])

                    # 普通治疗
                    if event.heal != 0:
                        if event.heal > event.healEff and self.bossAnalyseName not in ["宫傲", "李重茂"]:
                            if event.target in deathHitDetail:
                                deathHitDetail[event.target] = []
                        else:
                            if event.target in deathHitDetail:
                                if len(deathHitDetail[event.target]) >= 20:
                                    del deathHitDetail[event.target][0]
                                deathHitDetail[event.target].append([event.time, self.bld.info.getSkillName(event.full_id), event.healEff, event.caster, 1, event.effect, 0])
                        # 计算蛊惑
                        if event.caster in self.guHuoTarget and self.guHuoTarget[event.caster] != "0" and int(int(event.healEff) / 2) > 2000:
                            guHuo = self.guHuoTarget[event.caster]
                            if guHuo in deathHitDetail:
                                if len(deathHitDetail[guHuo]) >= 20:
                                    del deathHitDetail[guHuo][0]
                                deathHitDetail[guHuo].append([event.time, self.bld.info.getSkillName(event.full_id)+"(蛊惑)", int(int(event.healEff) / 2), event.caster, 1, event.effect, 0])

                elif event.target in self.bld.info.npc:
                    # 检查反弹
                    if event.damage != 0 and event.damageEff == 0:
                        deathHit[event.caster] = [event.time, self.bld.info.getSkillName(event.full_id), event.damage]
                        if event.caster in deathHitDetail:
                            if len(deathHitDetail[event.caster]) >= 20:
                                del deathHitDetail[event.caster][0]
                            deathHitDetail[event.caster].append([event.time, self.bld.info.getSkillName(event.full_id), event.damage, event.caster, -1, event.effect, event.damageEff])

                    # 开怪统计，判断对本体的伤害
                    if event.caster in self.bld.info.player and event.heal == 0 and self.bld.info.getName(event.target) in BOSS_RAW[self.bossAnalyseName][2]:
                        if event.id in ["2516"]:
                            pass
                        elif self.firstHitList[event.caster][1] == "":
                            #print(event.full_id)
                            #print(self.bld.info.skill[event.full_id])
                            self.firstHitList[event.caster] = [event.time, self.bld.info.getSkillName(event.full_id), "", 0]
                        elif self.firstHitList[event.caster][1][0] == '#' and self.firstHitList[event.caster][2] == "":
                            if self.bld.info.getSkillName(event.full_id)[0] not in ["#", "1", "2"]:
                                self.firstHitList[event.caster][2] = self.bld.info.getSkillName(event.full_id)
                                self.firstHitList[event.caster][3] = event.time

                    if event.caster in self.bld.info.player:
                        if event.caster not in self.dps:
                            self.dps[event.caster] = [0]
                        self.dps[event.caster][0] += event.damageEff

                    # if self.bld.info.getName(event.target) == "修罗僧" and event.damageEff < event.damage:
                    #     s = "%s: %d/%d, %s, %s" % (parseTime((event.time - self.startTime) / 1000), event.damageEff, event.damage,
                    #                                self.bld.info.getName(event.caster), self.bld.info.getSkillName(event.full_id))
                    #     if P3active:
                    #         immuneLog.append(s)

                    # if self.bld.info.getName(event.target) == "萧沙":
                    #     print("[XiaoshaTest]", parseTime((event.time - self.startTime) / 1000), event.caster, event.target, event.damageEff, self.bld.info.getName(event.caster), event.full_id, self.bld.info.getSkillName(event.full_id))

                if event.damageEff < event.damage:
                    s = "%s: %d/%d, %s, %s" % (parseTime((event.time - self.startTime) / 1000), event.damageEff, event.damage,
                                               self.bld.info.getName(event.target), self.bld.info.getSkillName(event.full_id))

                # for i in ["5", "8", "9", "10", "11", "12", "15", "16"]:
                #     if i in event.fullResult:
                #         print(self.bld.info.getSkillName(event.full_id), self.bld.info.getName(event.caster), self.bld.info.getName(event.target), parseTime((event.time - self.startTime) / 1000), event.fullResult)

                # 根据战斗信息推测进战状态
                if event.caster in self.bld.info.player and event.scheme == 1 and firstHitDict[event.caster] == 0 and (event.damageEff > 0 or event.healEff > 0):
                    firstHitDict[event.caster] = 1
                    self.battleDict[event.caster].setState(event.time, 1)

                if event.id == "6251":  # 记录左旋右转的施放者
                    self.zxyzPrecastSource = event.caster

            elif event.dataType == "Buff":

                if event.target not in self.bld.info.player:
                    continue

                if self.logMode:
                    # if event.caster not in self.bld.info.player:
                    #     print("[Buff]", self.bld.info.getName(event.caster), self.bld.info.getName(event.target), event.full_id, self.bld.info.getSkillName(event.full_id), event.stack)

                    if event.id == "2685":
                        if event.stack == 0:
                            tuozhanCount -= 1
                        else:
                            tuozhanCount += 1

                if event.id == "16877":
                    print(parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.target), event.level)

                if event.id in deathBuffDict:
                    if event.target not in deathBuff:
                        deathBuff[event.target] = {}
                    deathBuff[event.target][event.id] = [event.time, self.bld.info.getSkillName(event.full_id), deathBuffDict[event.id]]

                # 统计小药
                if event.id in ["18280", "18281", "18303", "18304"] and event.stack == 1:
                    xiaoyaoCount[event.target][event.id] = 1
                    
                if event.id in ["15775", "17201"] and event.target in self.penalty1:  # buff耐力损耗
                    self.penalty1[event.target].setState(event.time, event.stack)

                if event.id in ["15774", "17200"] and event.target in self.penalty2:  # buff精神匮乏
                    self.penalty2[event.target].setState(event.time, event.stack)
                    
                if event.id in ["2316"]:  # 蛊惑众生
                    if event.stack == 1:
                        self.guHuoTarget[event.caster] = event.target
                    else:
                        self.guHuoTarget[event.caster] = "0"
                    
                if event.id in ["6214"] and event.stack == 0 and event.target in deathHitDetail:  # 断禅语
                    if len(deathHitDetail[event.target]) >= 20:
                        del deathHitDetail[event.target][0]
                    deathHitDetail[event.target].append([event.time, "禅语消失", 0, event.caster, -1, 0, 0])

                # 推测阵眼。
                if event.target in self.zhenyanInfer:
                    if event.id in zhenyanSymbol and event.stack == 1:
                        # 获取到小队阵眼记录. 推测这里附近都是这个阵眼.
                        self.zhenyanInfer[event.target].recordPresent(event.time, zhenyanSymbol[event.id])
                        # print("[GetZhenyan1]", self.bld.info.getName(event.target), event.id, parseTime((event.time - self.startTime) / 1000))
                    if event.id in ZHENYAN_DICT and event.id != "0":
                        # 阵眼本身的获得与消失.
                        if event.stack == 1:
                            self.zhenyanInfer[event.target].recordPost(event.time, event.id)
                        else:
                            self.zhenyanInfer[event.target].recordPrev(event.time, event.id)
                        # print("[GetZhenyan2]", self.bld.info.getName(event.target), event.id, parseTime((event.time - self.startTime) / 1000), event.stack)

                if event.id in ["20938"] and event.target in self.bld.info.player:  # 左旋右转
                    if event.time - self.startTime < 60000:  # 假设起始时有这个buff
                        self.zxyzPrecast = 1

                if event.id in ["24941"] and event.stack > 0 and event.target in deathHitDetail:  # 李重茂业障复盘
                    deathSourceDetail = ["血量变化记录："]
                    deathTime = parseTime((event.time - self.startTime) / 1000)
                    for line in deathHitDetail[event.target]:
                        name = self.bld.info.getName(line[3])
                        resultStr = ""
                        if line[5] > 0 and line[5] <= 7:
                            resultStr = ["", "(招架)", "(免疫)", "(偏离)", "(闪避)", "(会心)", "(识破)", "(化解)"][line[5]]
                        if line[4] == -1:
                            deathSourceDetail.append("-%s, %s:%s%s(%d)" % (
                            parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))
                        elif line[4] == 1:
                            deathSourceDetail.append("+%s, %s:%s%s(%d)" % (
                            parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))

                    self.bossAnalyser.addPot([self.bld.info.player[event.target].name,
                                              occDetailList[event.target],
                                              0,
                                              self.bossNamePrint,
                                              "%s叠加业障debuff到%d层" % (deathTime, event.stack),
                                              deathSourceDetail,
                                              0])

                # if event.id in ["25603", "25604", "25605", "25606", "25607", "25608", "25609", "25603", "25603", "25501", "25602"] and event.stack == 1:
                #     print("[Dianming]", parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.target), event.id, self.bld.info.getSkillName(event.full_id),
                #           parseTime((event.end - event.frame) * 62.5 / 1000))

            elif event.dataType == "Death":  # 重伤记录
                
                # if item[4] not in occdict or occdict[item[4]][0] == '0':
                #     continue

                if event.id not in self.bld.info.player:
                    continue

                severe = 1

                self.deathName[self.bld.info.player[event.id].name] = 1

                deathTime = parseTime((event.time - self.startTime) / 1000)

                deathSource = "未知"
                if event.id in deathHit and abs(deathHit[event.id][0] - event.time) < 1000:
                    deathSource = "%s(%d)" % (deathHit[event.id][1], deathHit[event.id][2])
                elif event.id in deathBuff:
                    for line in deathBuff[event.id]:
                        if deathBuff[event.id][line][0] + deathBuff[event.id][line][2] > event.time:
                            deathSource = deathBuff[event.id][line][1]
                        if deathSource == "杯水留影":
                            severe = 0
                            if deathBuff[event.id][line][0] + 29500 > event.time:  # 杯水的精确时间特殊处理
                                deathSource = "未知"
                                severe = 1

                if "邪水之握" in deathSource:
                    severe = 0
                if "能量爆裂" in deathSource:
                    severe = 0

                damageSum1 = 0
                damageSum5 = 0
                lastFatal = 0
                lastLine = [event.time, "未知", 0, "0", -1, 0, 0]

                fromWushi = 0

                if event.id in deathHitDetail:
                    deathSourceDetail = ["血量变化记录："]
                    for line in deathHitDetail[event.id]:
                        name = self.bld.info.getName(line[3])
                        resultStr = ""
                        if line[5] > 0 and line[5] <= 7:
                            resultStr = ["", "(招架)", "(免疫)", "(偏离)", "(闪避)", "(会心)", "(识破)", "(化解)"][line[5]]
                        if line[4] == -1:
                            deathSourceDetail.append("-%s, %s:%s%s(%d)"%(parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))
                        elif line[4] == 1:
                            deathSourceDetail.append("+%s, %s:%s%s(%d)"%(parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))
                        if line[2] > line[6] and line[4] == -1 and line[1] not in ['一刀流·烈日', '一刀流·落日', '一刀流·旭日', '怯战', '逃避'] and event.time - self.startTime > 10000:
                            lastFatal = 1
                        else:
                            lastFatal = 0
                        lastLine = line
                        if event.time - line[0] < 1000:
                            damageSum1 += line[2]
                        if event.time - line[0] < 5000:
                            damageSum5 += line[2]
                        if name == "一刀流武士" and line[2] > 3000000:
                            fromWushi = 1

                    state1 = self.penalty1[event.id].checkState(event.time - 500)
                    state2 = self.penalty2[event.id].checkState(event.time - 500)
                    if state1 > 0:
                        deathSourceDetail.append("重伤时debuff耐力损耗：%d层"%state1)
                    if state2 > 0:
                        deathSourceDetail.append("重伤时debuff精神匮乏：%d层"%state2)

                    if (self.bossAnalyseName != "月泉淮" or deathSource != "未知") and not fromWushi:  # 排除月泉淮的自绝统计
                        self.bossAnalyser.addPot([self.bld.info.player[event.id].name,
                                                  occDetailList[event.id],
                                                  severe,
                                                  self.bossNamePrint,
                                                  "%s重伤，来源：%s" % (deathTime, deathSource),
                                                  deathSourceDetail,
                                                  0])

                    self.deathDict[event.id]["num"] += 1
                    self.deathDict[event.id]["log"].append(lastLine)

                    if damageSum1 < 350000 and damageSum5 < 550000 and lastFatal:
                        # 非正常死亡界限值，需要随版本更新
                        self.unusualDeathDict[event.id]["num"] += 1
                        self.unusualDeathDict[event.id]["log"].append(lastLine)


            elif event.dataType == "Shout":  # 喊话
                pass
                # print("[Shout]", event.time, event.content)

            elif event.dataType == "Battle":  # 战斗状态变化
                if event.id in self.bld.info.player:
                    self.battleDict[event.id].setState(event.time, event.fight)

            elif event.dataType == "Scene":  # 进入、离开场景
                pass

            elif event.dataType == "Cast":  # 施放技能事件，jcl专属
                pass
                # if event.caster in self.bld.info.npc:
                #     print("[Cast]", event.time, event.id, self.bld.info.getSkillName(event.full_id))

            num += 1

        # 活动
        if self.activity:
            # print(self.sumDamage)
            # print(self.startAttack)
            # print(self.startAttackTimestamp)
            for player in self.sumDamage:
                print("[uid]", player)
                print("[玩家名]", self.bld.info.getName(player))
                print("[开始时刻]", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.startAttackTimestamp[player])))
                print("[首次攻击]", parseTime((self.startAttack[player] - self.startTime) / 1000))
                print("[总伤害]", self.sumDamage[player])
                print("[DPS]", self.sumDamage[player] / 180)

        # 检验阵眼判断
        for player in self.zhenyanInfer:
            res = self.zhenyanInfer[player].getSummary()
            # print("[Zhenyan]", player, self.bld.info.getName(player), res)

        # 左旋右转最终调整
        if self.zxyzPrecast == 0:
            self.zxyzPrecastSource = "0"

        # 调整战斗时间
        self.startTime, self.finalTime, self.battleTime = self.bossAnalyser.trimTime()
        self.battleTime += 1e-10  # 防止0战斗时间导致错误

        statDict, potList, detail, stunCounter = self.bossAnalyser.getResult()
        self.potList = potList
        self.win = self.bossAnalyser.win
        self.stunCounter = stunCounter

        # recordGORate = 1
        # sumDPS = 0
        # numDPS = 0
        # for line in statDict:
        #     sumDPS += line[2]
        #     numDPS += 1
        #
        # averageDPS = safe_divide(sumDPS, numDPS)
        #
        # # 在DPS过于离谱的BOSS跳过DPS统计
        # skipDPS = 0
        #
        # if True:
        #     if parseEdition(EDITION) == 0:  # 非联机版本跳过加载步骤
        #         result = None
        #     else:
        #         result = {"mapdetail": self.mapDetail, "boss": self.bossname}
        #         Jdata = json.dumps(result)
        #         jpost = {'jdata': Jdata}
        #         jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        #         resp = urllib.request.urlopen('http://%s:8009/getDpsStat' % IP, data=jparse)
        #         res = json.load(resp)
        #     if result is None:
        #         print("连接服务器失败！")
        #     elif res['result'] == 'success':
        #         resultDict = json.loads(res['statistics'].replace("'", '"'))
        #         sumStandardDPS = 0
        #
        #         for i in range(len(statDict) - 1, -1, -1):
        #             line = statDict[i]
        #             occ = str(line[1])
        #             if occ not in resultDict:
        #                 resultDict[occ] = ["xx", "xx", 50000]
        #             #if occ[-1] in ["d", "h", "t", "p", "m"]:
        #             #    occ = occ[:-1]
        #             sumStandardDPS += resultDict[occ][2]
        #
        #         for i in range(len(statDict) - 1, -1, -1):
        #             line = statDict[i]
        #             occ = str(line[1])
        #             if occ not in resultDict:
        #                 resultDict[occ] = ["xx", "xx", 50000]
        #             GORate = safe_divide(line[2], sumDPS) * safe_divide(sumStandardDPS, resultDict[occ][2])
        #
        #             occDPS = resultDict[occ][2]
        #             GODPS = safe_divide(sumDPS, sumStandardDPS) * occDPS
        #             DPSDetail = ["实际DPS：%d"%line[2], "心法平均DPS：%d"%occDPS, "团队-心法平均DPS：%d"%GODPS]
        #
        #             if GORate < self.qualifiedRate:
        #                 sumDPS -= line[2]
        #                 numDPS -= 1
        #                 sumStandardDPS -= resultDict[occ][2]
        #                 if GORate > 0.1 and not skipDPS:
        #                     self.bossAnalyser.addPot([line[0],
        #                                          line[1],
        #                                          1,
        #                                          self.bossNamePrint,
        #                                          "团队-心法DPS未到及格线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.qualifiedRate, 0)),
        #                                          DPSDetail,
        #                                          0])
        #             elif GORate < self.alertRate and not skipDPS:
        #                 self.bossAnalyser.addPot([line[0],
        #                                      line[1],
        #                                      0,
        #                                      self.bossNamePrint,
        #                                      "团队-心法DPS低于预警线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.alertRate, 0)),
        #                                      DPSDetail,
        #                                      0])
        #
        #             elif GORate > self.bonusRate and not skipDPS:
        #                 self.bossAnalyser.addPot([line[0],
        #                                      line[1],
        #                                      3,
        #                                      self.bossNamePrint,
        #                                      "团队-心法DPS达到补贴线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.bonusRate, 0)),
        #                                      DPSDetail,
        #                                      0])
        #
        #             if recordGORate and getOccType(line[1]) != "healer":
        #                 statDict[i][3] = int(GORate * 100)

        # 开怪统计
        if self.firstHitList != {}:
            earliestHit = 0
            earliestTankHit = 0
            for name in self.firstHitList:
                # print("[EarliestHit]", self.bld.info.getName(name), self.firstHitList[name][0], self.firstHitList[name][1])
                if self.firstHitList[name][1] == "":
                    continue
                if self.firstHitList[name][1][0] in ["#", "1", "2"] and self.firstHitList[name][2] == "":
                    continue
                if earliestHit == 0 or self.firstHitList[name][0] < self.firstHitList[earliestHit][0]:
                    earliestHit = name
                if occDetailList[name] in ["1t", "3t", "10t", "21t"]:
                    if earliestTankHit == 0 or self.firstHitList[name][0] < self.firstHitList[earliestTankHit][0]:
                        earliestTankHit = name

            # print(earliestHit, self.firstHitList[earliestHit])
            # if earliestTankHit != 0:
            #    print(earliestTankHit, self.firstHitList[earliestTankHit])

            if earliestHit != 0 and (earliestTankHit == 0 or self.firstHitList[earliestTankHit][0] - 500 > self.firstHitList[earliestHit][0]):
                if self.firstHitList[earliestHit][2] == "":
                    hitName = self.firstHitList[earliestHit][1]
                else:
                    hitName = self.firstHitList[earliestHit][2] + "(推测)"
                self.potList = [[self.bld.info.player[earliestHit].name,
                                 occDetailList[earliestHit],
                                 0,
                                 self.bossNamePrint,
                                 "提前开怪：%s" % hitName,
                                 ["如果带有[推测]，表示复盘中是壳技能，可能与实际情况不一致，仅供参考"],
                                 0]] + self.potList

        # 战斗补药统计
        checkXiaoYao = 0
        for line in xiaoyaoCount:
            if sum(list(xiaoyaoCount[line].values())) == 4:
                checkXiaoYao += 1
        
        if checkXiaoYao >= 3:
            for line in xiaoyaoCount:
                if sum(list(xiaoyaoCount[line].values())) < 4 and occDetailList[line] not in ["1t", "3t", "10t", "21t", "2h", "5h", "6h", "22h", "212h"]:
                    self.potList = [[self.bld.info.player[line].name,
                                     occDetailList[line],
                                     0,
                                     self.bossNamePrint,
                                     "小药数量错误：%d" % sum(list(xiaoyaoCount[line].values())),
                                     [],
                                     0]] + self.potList
                                     
        for line in self.potList:
            if len(line) == 5:
                line.append([])
                
        detail["win"] = self.win
        if "boss" not in detail:
            detail["boss"] = ""
        if self.bossAnalyseName not in ["", "未知"]:
            detail["boss"] = self.bossAnalyseName
        elif detail["boss"] == "":
            detail["boss"] = self.bossname

        # self.data = data
        self.statDict = statDict
        self.detail = detail
        
        self.server = self.bld.info.server
        
        ids = {}
        for line in self.bld.info.player:
            ids[self.bld.info.player[line].name] = 0
        self.ids = ids

        if self.win:
            self.upload = 1

        print("[Win]", self.win)

        if self.bossAnalyser.hasBh:
            self.bh = self.bossAnalyser.bh

        else:
            self.bh = None

        # BOSS名称回流
        if self.bossAnalyseName not in ["", "未知"] and self.bld.info.boss != self.bossAnalyseName:
            self.bld.info.boss = self.bossAnalyseName

        # # 月泉淮中间分片
        # if self.detail["boss"] == "月泉淮":
        #     if self.bossAnalyser.yqhInterrupt:
        #         self.available = False  # 进行分片

        if self.logMode:
            # 统计总数，如果中的人数超过了一定数值，就排除
            numLog = {}
            for key in logSkill:
                numLog[logSkill[key][0]] = 0
            for player in self.penaltyCount:
                for key in self.penaltyCount[player]:
                    if self.penaltyCount[player][key] != 0:
                        numLog[key] += 1
            for key in logSkill:
                if numLog[logSkill[key][0]] > logSkill[key][3]:
                    numLog[logSkill[key][0]] = -1
            for player in self.penaltyCount:
                for key in self.penaltyCount[player]:
                    if numLog[key] == -1:
                        self.penaltyCount[player][key] = 0

            # 不计算T心法中的一些技能
            exemptDict = {}
            for key in logSkill:
                if logSkill[key][4] == 1:
                    exemptDict[logSkill[key][0]] = 1
            for player in self.penaltyCount:
                if getOccType(self.occDetailList[player]) == "tank":
                    for key in self.penaltyCount[player]:
                        if key in exemptDict:
                            self.penaltyCount[player][key] = 0

            num = 0
            BOSS_NAME = {"魏华": 1, "钟不归": 2, "岑伤": 3, "鬼筹": 4, "麒麟": 5, "月泉淮": 6, "葛木寒": 1, "雨轻红": 2, "喜雅": 3, "鹰眼客": 4, "赤幽明": 5}
            if self.bossAnalyseName in BOSS_NAME:
                num = BOSS_NAME[self.bossAnalyseName]

            # 计算战斗时间
            for player in self.penaltyCount:
                t = self.battleDict[player].buffTimeIntegral()
                if num != 0:
                    self.penaltyCount[player]["%d号时间" % num] = int(t / 1000)

            # 转玩家名
            self.penaltyCountWithName = {}
            for key in self.penaltyCount:
                self.penaltyCountWithName[self.bld.info.getName(key)] = self.penaltyCount[key]


    def ThirdStageAnalysis(self):
        '''
        第三阶段复盘.
        目前实现了战斗的数值统计.
        '''

        combatTracker = CombatTracker(self.bld.info, self.bh, self.occDetailList, self.zhenyanInfer, self.stunCounter, self.zxyzPrecastSource, self.baseAttribDict)

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
            if event.dataType == "Skill":
                combatTracker.recordSkill(event)
            elif event.dataType == "Buff":
                combatTracker.recordBuff(event)
            elif event.dataType == "Shout":
                combatTracker.recordShout(event)

        combatTracker.export(self.battleTime, self.bh.sumTime("dps"), self.bh.sumTime("healer"), self.stunCounter)
        self.combatTracker = combatTracker

        # for key in self.bld.info.player:
        #     print("[Player]", key, self.bld.info.getName(key))
        #
        # for key in self.bld.info.npc:
        #     print("[NPC]", key, self.bld.info.getName(key))

        # 保存log
        if self.logMode:
            num = 0
            BOSS_NAME = {"魏华": 1, "钟不归": 2, "岑伤": 3, "鬼筹": 4, "麒麟": 5, "月泉淮": 6}
            if self.bossAnalyseName in BOSS_NAME:
                num = BOSS_NAME[self.bossAnalyseName]

            for key in self.penaltyCount:
                name = self.bld.info.getName(key)
                rdps = 0
                if key in self.combatTracker.rdps["player"]:
                    rdps = self.combatTracker.rdps["player"][key]["dps"]
                    occ = self.combatTracker.rdps["player"][key]["occ"]
                    if getOccType(occ) != "dps":
                        rdps = 0
                self.penaltyCountWithName[name]["%d号rDPS" % num] = int(rdps)

            with open("jldCount/%s.txt" % self.startTime, "w", encoding="utf-8") as f:
                f.write(str(self.penaltyCountWithName))

    def OccAnalysis(self):
        '''
        心法复盘实现.
        每个心法都会再独立扫一次战斗记录.
        '''
        self.occResult = {}
        actorData = {}
        self.actorData = actorData
        actorData["startTime"] = self.startTime  # 这个是毫秒级的抽象时间
        actorData["finalTime"] = self.finalTime
        actorData["beginTime"] = self.beginTime  # 这个是具体的时间戳
        actorData["mapid"] = getIDFromMap(self.mapDetail)
        actorData["win"] = self.win
        actorData["bossBh"] = self.bh
        actorData["battleDict"] = self.battleDict
        actorData["deathDict"] = self.deathDict
        actorData["unusualDeathDict"] = self.unusualDeathDict
        actorData["act"] = self.combatTracker
        actorData["occDetailList"] = self.occDetailList
        actorData["hash"] = self.hashGroup()
        actorData["boss"] = self.bossAnalyseName
        actorData["equip"] = self.panelAttribDict
        actorData["jsonEquip"] = self.jsonEquip
        actorData["strEquip"] = self.strEquip
        # actorData["zhenyanInfer"] = self.zhenyanInfer  # TODO 在dps统计中可能会用到
        for id in self.bld.info.player:
            name = self.bld.info.player[id].name
            replayer = None
            rdps = self.combatTracker.getRdps(id)
            if self.config.item["xiangzhi"]["active"] and self.occDetailList[id] == "22h":  # 奶歌
                replayer = XiangZhiProReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.config.item["lingsu"]["active"] and self.occDetailList[id] == "212h":  # 灵素
                replayer = LingSuReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.config.item["lijing"]["active"] and self.occDetailList[id] == "2h":  # 奶花
                replayer = LiJingYiDaoReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.config.item["yunchang"]["active"] and self.occDetailList[id] == "5h":  # 奶秀
                replayer = YunChangXinJingReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.config.item["butian"]["active"] and self.occDetailList[id] == "6h":  # 奶毒
                replayer = BuTianJueReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.occDetailList[id] == "2d":  # 花间
                replayer = HuaJianYouReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData)
            if self.occDetailList[id] in ["1d", "1t", "3d", "3t", "4p", "4m", "5d", "6d", "7p", "7m", "8", "9", "10d", "10t",
                                          "21d", "21t", "22d", "23", "24", "25", "211", "212d", "213", "214"] and rdps != 0:
                replayer = DpsReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, actorData, self.occDetailList[id])
            if replayer is not None:
                replayer.replay()
                self.occResult[name] = {"occ": self.occDetailList[id], "result": replayer.result, "rank": replayer.rank}
                # print("[Skill]", replayer.result["skill"]["general"])
                # 尝试从心法复盘中回流排名
                rdps = replayer.result["skill"]["general"].get("rdps", 0)
                ndps = replayer.result["skill"]["general"].get("ndps", 0)
                score = replayer.result["skill"]["general"]["score"]
                rdpsRank = replayer.result["rank"]["general"]["rdps"]
                scoreRank = replayer.result["rank"]["general"].get("score", {"num": 0, "percent": -1})
                for i in range(len(self.statDict)):
                    if self.statDict[i]["name"] == self.bld.info.getName(id):
                        self.statDict[i]["rdps"] = rdps
                        self.statDict[i]["ndps"] = ndps
                        self.statDict[i]["score"] = score
                        self.statDict[i]["rdpsRank"] = rdpsRank["percent"]
                        self.statDict[i]["scoreRank"] = scoreRank["percent"]
        self.statDict.sort(key=lambda x:-x["rdps"])

    def replay(self):
        '''
        开始演员复盘pro分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.ThirdStageAnalysis()
        self.OccAnalysis()
        if self.upload:
            self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名组合，格式为[文件名, 尝试次数, 是否为最后一次]
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        '''
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.config = config
        self.failThreshold = config.item["actor"]["failthreshold"]  # BOSS失败时倒推的秒数
        self.win = 0
        self.mask = config.item["general"]["mask"]
        self.bldDict = bldDict
        self.fileNameInfo = fileNameInfo
        self.path = path
        self.bld = bldDict[fileNameInfo[0]]
        self.bossname = getNickToBoss(self.bld.info.boss)
        self.mapDetail = self.bld.info.map
        self.battleDate = time.strftime("%Y-%m-%d", time.localtime(self.bld.info.battleTime))
        self.numTry = 0  # TODO 修改为战斗次数
        if self.numTry == 0:
            self.bossNamePrint = self.bossname
        else:
            self.bossNamePrint = "%s.%d" % (self.bossname, self.numTry)

        # 复盘结果信息
        self.potList = []
        self.detail = {"boss": "未知"}
        self.statDict = []
        self.equipmentDict = {}
        self.available = True  # 暂时用来判定月泉淮中间分片
        self.bossAnalyseName = "未知"
        self.occDetailList = {}
        self.upload = 0



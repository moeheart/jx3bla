# Created by moeheart at 10/05/2021
# 新版演员复盘的通用方法库。

import json
import threading
import urllib.request
import requests
import hashlib
import time
import os
from PIL import Image, ImageFont, ImageDraw

#from ReplayBase import StatGeneratorBase
from tools.Functions import *
from Constants import *
from tools.Names import *
from equip.EquipmentExport import EquipmentAnalyser

from replayer.ReplayerBase import ReplayerBase

from replayer.boss.Base import SpecificReplayerPro

from replayer.boss.General import GeneralReplayer
from replayer.boss.HuTangLuoFen import HuTangLuoFenReplayer
from replayer.boss.ZhaoBasao import ZhaoBasaoReplayer
from replayer.boss.HaiTu import HaiTuReplayer
from replayer.boss.JiangJiku import JiangJikuReplayer
from replayer.boss.YuwenMie import YuwenMieReplayer
from replayer.boss.GongWei import GongWeiReplayer
from replayer.boss.GongAo import GongAoReplayer

from replayer.boss.JuxingJianwenfeng import JuxingJianwenfengReplayer
from replayer.boss.SangQiao import SangQiaoReplayer
from replayer.boss.XidaLuomo import XidaLuomoReplayer
from replayer.boss.YoujiaLuomo import YoujiaLuomoReplayer
from replayer.boss.YuequanHuai import YuequanHuaiReplayer
from replayer.boss.WuMenggui import WuMengguiReplayer

from replayer.occ.XiangZhi import XiangZhiProReplayer
from replayer.occ.LingSu import LingSuReplayer
from replayer.occ.LiJingYiDao import LiJingYiDaoReplayer
from replayer.occ.YunChangXinJing import YunChangXinJingReplayer
from replayer.occ.BuTianJue import BuTianJueReplayer

class ActorProReplayer(ReplayerBase):

    occDetailList = {}
    upload = 0
    bossAnalyseName = "未知"

    actorSkillList = [
                      ]

    actorBuffList = [
                     ]

    bossNameDict = {"胡汤&罗芬": 1,
                    "胡汤": 1,
                    "罗芬": 1,
                    "赵八嫂": 2, 
                    "海荼": 3,
                    "天怒惊霆戟": 3,
                    "姜集苦": 4, 
                    "宇文灭": 5, 
                    "宫威": 6, 
                    "宫傲": 7,
                    "巨型尖吻凤": 1,
                    "桑乔": 2,
                    "悉达罗摩": 3,
                    "赐恩血瘤": 4,
                    "血蛊巢心": 4,
                    "月泉淮": 5,
                    "乌蒙贵": 6}

    # def makeEmptyHitList(self):
    #     res = {}
    #     for i in self.actorSkillList:
    #         res["s" + i] = 0
    #     for i in self.actorBuffList:
    #         res["b" + i] = 0
    #     return res
    #
    # def checkFirst(self, key, data, occdict):
    #     if occdict[key][0] != '0' and key not in data.hitCount:
    #         data.hitCount[key] = self.makeEmptyHitList()
    #         data.hitCountP2[key] = self.makeEmptyHitList()
    #     return data

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
        if "beta" in EDITION:
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
        result["userid"] = self.config.items_user["uuid"]
        #result["instancecd"] = self.instanceCD
        
        #print(result["begintime"])
        #print(result["time"])
        #print(result["userid"])
        #print(result["instancecd"])
        
        allInfo = {}
        allInfo["effectiveDPSList"] = self.effectiveDPSList
        allInfo["potList"] = self.potList
        allInfo["battleTime"] = self.battleTime
        # for i in range(len(allInfo["effectiveDPSList"])):
        #     allInfo["effectiveDPSList"][i][0] = allInfo["effectiveDPSList"][i][0]
        # for i in range(len(allInfo["potList"])):
        #     allInfo["potList"][i][0] = allInfo["potList"][i][0]
        allInfo["mask"] = self.config.mask

        result["statistics"] = allInfo

        Jdata = json.dumps(result)

        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadActorData', data=jparse)
        
        res = json.load(resp)
        
        #print(res)
        
        if self.window is not None:
            if res["scoreStatus"] == "illegal":
                self.window.setNotice({"t2": "未增加荣誉值，原因：非指定地图", "c2": "#ff0000"})
            elif res["scoreStatus"] == "notwin":
                self.window.setNotice({"t2": "未增加荣誉值，原因：未击败BOSS", "c2": "#ff0000"})
            elif res["scoreStatus"] == "expire":
                self.window.setNotice({"t2": "未增加荣誉值，原因：数据已被他人上传", "c2": "#ff0000"})
            elif res["scoreStatus"] == "dupid":
                self.window.setNotice({"t2": "未增加荣誉值，原因：数据已被自己上传", "c2": "#ff0000"})
            elif res["scoreStatus"] == "nologin":
                self.window.setNotice({"t2": "未增加荣誉值，原因：未注册用户名", "c2": "#ff0000"})
            elif res["scoreStatus"] == "success":
                self.window.setNotice({"t2": "数据上传成功，荣誉值增加：%d"%res["scoreAdd"], "c2": "#00ff00"})

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要记录BOSS信息，NPC出现等状况.
        '''

        # 向窗口类中存储装备信息，作为不同boss之间的缓存
        for id in self.bld.info.player:
            self.window.playerEquipment[id] = self.bld.info.player[id].equip

        # TODO 为格式错误准备报错信息
        if len(self.bld.log) == 0:
            raise Exception('复盘信息格式错误，请确认设置是否正确。如果不清楚细节，请先使用实时模式。')
            return 1  # 格式错误

        # self.namedict = namedict
        # self.occdict = occdict
        # self.effectiveDPSList = []

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

        # skillList50 = {}

        for event in self.bld.log:
            
            # if len(item) > 5 and item[5] not in occdict:
            #     occdict[item[5]] = ['0']

            #if item[3] == "1":
            if event.dataType == "Skill":

                # if item[5] not in namedict:
                #     continue
                # if occdict[item[5]][0] != '0':
                #     self.playerIDList[item[5]] = 0
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '罗芬':
                    self.bossAnalyseName = "胡汤&罗芬"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '赵八嫂':
                    self.bossAnalyseName = "赵八嫂"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '海荼':
                    self.bossAnalyseName = "海荼"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '姜集苦':
                    self.bossAnalyseName = "姜集苦"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '宇文灭':
                    self.bossAnalyseName = "宇文灭"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '宫威':
                    self.bossAnalyseName = "宫威"
                    
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '宫傲':
                    self.bossAnalyseName = "宫傲"

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name in ['巨型尖吻凤', "巨型尖吻鳳"]:
                    self.bossAnalyseName = "巨型尖吻凤"
                    if not timeReseted:
                        self.startTime = event.time
                        timeReseted = 1

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name in ['桑乔', "桑喬"]:
                    self.bossAnalyseName = "桑乔"

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name in ['悉达罗摩', "悉達羅摩"]:
                    self.bossAnalyseName = "悉达罗摩"

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name in ['赐恩血瘤', "賜恩血瘤"]:
                    self.bossAnalyseName = "尤珈罗摩"

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '月泉淮':
                    self.bossAnalyseName = "月泉淮"

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name in ['乌蒙贵', "烏蒙貴"]:
                    self.bossAnalyseName = "乌蒙贵"

                # 通过技能确定具体心法
                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22', '212']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                # if event.caster == "15697871" and event.id not in skillList50:
                #     skillList50[event.id] = 1
                #     print(event.time, event.id, self.bld.info.getSkillName(event.full_id))

                    
            elif event.dataType == "Buff":
                # 通过buff确定具体心法
                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '3', '10', '21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                if self.bossAnalyseName == "赵八嫂" and event.content in ['"就拿你们的血来磨磨刀！"']:
                    self.startTime = event.time
                if self.bossAnalyseName == "悉达罗摩" and event.content in ['"来吧，进餐时间到了！"']:
                    self.finalTime = event.time + 5000
                if self.bossAnalyseName == "月泉淮" and event.content in ['"就到这里吧……我玩够了。"']:
                    self.finalTime = event.time + 5000

            elif event.dataType == "Battle":
                pass

            elif event.dataType == "Death":  # 重伤记录
                if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "血蛊巢心":
                    self.finalTime = event.time + 5000  # 防止脱战失败导致数据延长

        # 如果进行了时间修剪，就调整battletime的逻辑，否则battletime就使用复盘数据中附带的结果
        if abs(self.finalTime - self.startTime - self.battleTime) > 6000:
            self.battleTime = self.finalTime - self.startTime

        for id in self.bld.info.player:
            self.firstHitList[id] = 0
            
        equipmentAnalyser = EquipmentAnalyser()
        for id in self.bld.info.player:
            if id in self.window.playerEquipment and self.window.playerEquipment[id] != {}:
                equips = equipmentAnalyser.convert2(self.window.playerEquipment[id], self.bld.info.player[id].equipScore)
                self.equipmentDict[id] = equips
            
        self.occDetailList = occDetailList
        
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

        if self.bossAnalyseName == "胡汤&罗芬":
            bossAnalyser = HuTangLuoFenReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "赵八嫂":
            bossAnalyser = ZhaoBasaoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "海荼":
            bossAnalyser = HaiTuReplayer(self.bld, occDetailList, self.startTime,
                                         self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "姜集苦":
            bossAnalyser = JiangJikuReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "宇文灭":
            bossAnalyser = YuwenMieReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "宫威":
            bossAnalyser = GongWeiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "宫傲":
            bossAnalyser = GongAoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "巨型尖吻凤":
            bossAnalyser = JuxingJianwenfengReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "桑乔":
            bossAnalyser = SangQiaoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "悉达罗摩":
            bossAnalyser = XidaLuomoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "尤珈罗摩":
            bossAnalyser = YoujiaLuomoReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "月泉淮":
            bossAnalyser = YuequanHuaiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        elif self.bossAnalyseName == "乌蒙贵":
            bossAnalyser = WuMengguiReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
        else:
            bossAnalyser = GeneralReplayer(self.bld, occDetailList, self.startTime,
                                           self.finalTime, self.battleTime, self.bossNamePrint)
            
        self.bossAnalyser = bossAnalyser
        
        self.bossAnalyser.recordEquipment(self.equipmentDict)
        
        self.potList = bossAnalyser.potList

        bossAnalyser.initBattle()
        
        self.penalty1 = {}
        self.penalty2 = {}
        self.guHuoTarget = {}
        
        for line in self.bld.info.player:
            self.penalty1[line] = BuffCounter(0, self.startTime, self.finalTime)  # 通用易伤
            self.penalty2[line] = BuffCounter(0, self.startTime, self.finalTime)  # 通用减疗

        if not self.lastTry:
            self.finalTime -= self.failThreshold * 1000
        
        #for line in sk:
        for event in self.bld.log:

            # item = line[""]
            # if int(item[2]) > self.finalTime:
            #     break
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
                
            self.bossAnalyser.analyseSecondStage(event)

            if event.dataType == "Skill":

                if event.target in self.bld.info.player:
                #if occdict[item[5]][0] != '0':

                    # data = self.checkFirst(item[5], data, occdict)
                    # if item[7] in self.actorSkillList and int(item[10]) != 2:
                    #     data.hitCount[item[5]]["s" + item[7]] += 1

                    # 过量伤害
                    if event.damage > event.damageEff:
                        deathHit[event.target] = [event.time, self.bld.info.getSkillName(event.full_id), event.damage]

                    # 记录受到的伤害
                    if event.damage != 0 and event.target in deathHitDetail and '5' not in event.fullResult:
                        if len(deathHitDetail[event.target]) >= 20:
                            del deathHitDetail[event.target][0]
                        deathHitDetail[event.target].append([event.time, self.bld.info.getSkillName(event.full_id), event.damage, event.caster, -1, event.effect])

                    # 普通治疗
                    if event.heal != 0:
                        if event.heal > event.healEff:
                            if event.target in deathHitDetail:
                                deathHitDetail[event.target] = []
                        else:
                            if event.target in deathHitDetail:
                                if len(deathHitDetail[event.target]) >= 20:
                                    del deathHitDetail[event.target][0]
                                deathHitDetail[event.target].append([event.time, self.bld.info.getSkillName(event.full_id), event.healEff, event.caster, 1, event.effect])
                        # 计算蛊惑
                        if event.caster in self.guHuoTarget and self.guHuoTarget[event.caster] != "0" and int(int(event.healEff) / 2) > 2000:
                            guHuo = self.guHuoTarget[event.caster]
                            if guHuo in deathHitDetail:
                                if len(deathHitDetail[guHuo]) >= 20:
                                    del deathHitDetail[guHuo][0]
                                deathHitDetail[guHuo].append([event.time, self.bld.info.getSkillName(event.full_id)+"(蛊惑)", int(int(event.healEff) / 2), event.caster, 1, event.effect])

                elif event.target in self.bld.info.npc:

                    # 检查反弹
                    if event.damage != 0 and event.damageEff == 0:
                        deathHit[event.caster] = [event.time, self.bld.info.getSkillName(event.full_id), event.damage]
                        if event.caster in deathHitDetail:
                            if len(deathHitDetail[event.caster]) >= 20:
                                del deathHitDetail[event.caster][0]
                            deathHitDetail[event.caster].append([event.time, self.bld.info.getSkillName(event.full_id), event.damage, event.caster, -1, event.effect])

                    # 开怪统计，判断对本体的伤害
                    if event.caster in self.bld.info.player and event.heal == 0 and self.bld.info.npc[event.target].name in self.bossNameDict:
                        if event.id in ["2516"]:
                            pass
                        elif self.firstHitList[event.caster] == 0:
                            #print(event.full_id)
                            #print(self.bld.info.skill[event.full_id])
                            self.firstHitList[event.caster] = [event.time, self.bld.info.getSkillName(event.full_id), "", 0]
                        elif self.firstHitList[event.caster][1][0] == '#' and self.firstHitList[event.caster][2] == "":
                            if self.bld.info.getSkillName(event.full_id)[0] not in ["#", "1", "2"]:
                                self.firstHitList[event.caster][2] = self.bld.info.getSkillName(event.full_id)
                                self.firstHitList[event.caster][3] = event.time
                    
                    # if calculDPS:
                    if event.caster in self.bld.info.player:
                        if event.caster not in self.dps:
                            self.dps[event.caster] = [0]
                        self.dps[event.caster][0] += event.damageEff
                            
            elif event.dataType == "Buff":
                # if occdict[item[5]][0] == '0':
                #     continue
                if event.target not in self.bld.info.player:
                    continue

                # data = self.checkFirst(item[5], data, occdict)
                # if item[6] in self.actorBuffList and int(item[10]) == 1:
                #     if item[5] not in data.hitCount:
                #         data.hitCount[item[5]] = self.makeEmptyHitList()
                #     data.hitCount[item[5]]["b" + item[6]] += 1

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
                    deathHitDetail[event.target].append([event.time, "禅语消失", 0, event.caster, -1, 0])

            elif event.dataType == "Death":  # 重伤记录
                
                # if item[4] not in occdict or occdict[item[4]][0] == '0':
                #     continue

                if event.id not in self.bld.info.player:
                    continue

                # data = self.checkFirst(item[4], data, occdict)
                # if item[4] in occdict and int(occdict[item[4]][0]) != 0:
                severe = 1
                # if self.bossname in self.bossNameDict:
                #     data.deathCount[item[4]][self.bossNameDict[self.bossname]] += 1

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

                if event.id in deathHitDetail:
                    deathSourceDetail = ["血量变化记录："]
                    for line in deathHitDetail[event.id]:
                        name = "未知"
                        if line[3] in self.bld.info.player:
                            name = self.bld.info.player[line[3]].name
                        elif line[3] in self.bld.info.npc:
                            name = self.bld.info.npc[line[3]].name
                        # if line[3] in namedict:
                        #     name = namedict[line[3]][0].strip('"')
                        resultStr = ""
                        if line[5] > 0 and line[5] <= 7:
                            resultStr = ["", "(招架)", "(免疫)", "(偏离)", "(闪避)", "(会心)", "(识破)", "(化解)"][line[5]]
                        if line[4] == -1:
                            deathSourceDetail.append("-%s, %s:%s%s(%d)"%(parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))
                        elif line[4] == 1:
                            deathSourceDetail.append("+%s, %s:%s%s(%d)"%(parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], resultStr, line[2]))

                    state1 = self.penalty1[event.id].checkState(event.time - 500)
                    state2 = self.penalty2[event.id].checkState(event.time - 500)
                    if state1 > 0:
                        deathSourceDetail.append("重伤时debuff耐力损耗：%d层"%state1)
                    if state2 > 0:
                        deathSourceDetail.append("重伤时debuff精神匮乏：%d层"%state2)

                    if self.bossAnalyseName != "月泉淮" or deathSource != "未知":  # 排除月泉淮的自绝统计
                        self.bossAnalyser.addPot([self.bld.info.player[event.id].name,
                                                  occDetailList[event.id],
                                                  severe,
                                                  self.bossNamePrint,
                                                  "%s重伤，来源：%s" % (deathTime, deathSource),
                                                  deathSourceDetail,
                                                  0])

                    # 对有重伤统计的BOSS进行记录
                    if self.bossAnalyser.activeBoss in []:
                        self.bossAnalyser.recordDeath(item, deathSource)

            elif event.dataType == "Shout":  # 喊话
                pass
                    
            elif event.dataType == "Battle":  # 战斗状态变化
                pass

            num += 1

        # 调整战斗时间
        self.startTime, self.finalTime, self.battleTime = self.bossAnalyser.trimTime()
        self.battleTime += 1e-10  # 防止0战斗时间导致错误

        recordGORate = 0

        effectiveDPSList, potList, detail = self.bossAnalyser.getResult()
        self.potList = potList
        self.win = self.bossAnalyser.win
        recordGORate = 1

        sumDPS = 0
        numDPS = 0
        for line in effectiveDPSList:
            sumDPS += line[2]
            numDPS += 1

        averageDPS = sumDPS / (numDPS + 1e-10)

        # 在DPS过于离谱的BOSS跳过DPS统计
        skipDPS = 0
        
        if True: # self.playerIDList != {}:
            result = {"mapdetail": self.mapDetail, "boss": self.bossname}
            Jdata = json.dumps(result)
            jpost = {'jdata': Jdata}
            jparse = urllib.parse.urlencode(jpost).encode('utf-8')
            resp = urllib.request.urlopen('http://139.199.102.41:8009/getDpsStat', data=jparse)
            res = json.load(resp)
            if result is None:
                print("连接服务器失败！")
            elif res['result'] == 'success':
                resultDict = json.loads(res['statistics'].replace("'", '"'))
                sumStandardDPS = 0
                
                for i in range(len(effectiveDPSList) - 1, -1, -1):
                    line = effectiveDPSList[i]
                    occ = str(line[1])
                    if occ not in resultDict:
                        resultDict[occ] = ["xx", "xx", 50000]
                    #if occ[-1] in ["d", "h", "t", "p", "m"]:
                    #    occ = occ[:-1]
                    sumStandardDPS += resultDict[occ][2]
                    
                for i in range(len(effectiveDPSList) - 1, -1, -1):  
                    line = effectiveDPSList[i]
                    occ = str(line[1])
                    if occ not in resultDict:
                        resultDict[occ] = ["xx", "xx", 50000]
                    GORate = line[2] / (sumDPS + 1e-10) * sumStandardDPS / (resultDict[occ][2] + 1e-10)
                    
                    occDPS = resultDict[occ][2]
                    GODPS = sumDPS / (sumStandardDPS + 1e-10) * occDPS
                    DPSDetail = ["实际DPS：%d"%line[2], "心法平均DPS：%d"%occDPS, "团队-心法平均DPS：%d"%GODPS]
                
                    if GORate < self.qualifiedRate:
                        sumDPS -= line[2]
                        numDPS -= 1
                        sumStandardDPS -= resultDict[occ][2]
                        if GORate > 0.1 and not skipDPS:
                            self.bossAnalyser.addPot([line[0],
                                                 line[1],
                                                 1,
                                                 self.bossNamePrint,
                                                 "团队-心法DPS未到及格线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.qualifiedRate, 0)),
                                                 DPSDetail,
                                                 0])
                    elif GORate < self.alertRate and not skipDPS:
                        self.bossAnalyser.addPot([line[0],
                                             line[1],
                                             0,
                                             self.bossNamePrint,
                                             "团队-心法DPS低于预警线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.alertRate, 0)),
                                             DPSDetail,
                                             0])
                                             
                    elif GORate > self.bonusRate and not skipDPS:
                        self.bossAnalyser.addPot([line[0],
                                             line[1],
                                             3,
                                             self.bossNamePrint,
                                             "团队-心法DPS达到补贴线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.bonusRate, 0)),
                                             DPSDetail,
                                             0])
                                             
                    if recordGORate and getOccType(line[1]) != "healer":
                        effectiveDPSList[i][3] = int(GORate * 100)
                            
        # 开怪统计
        # print(self.firstHitList)

        if self.firstHitList != {}:
            earliestHit = 0
            earliestTankHit = 0
            for name in self.firstHitList:
                if self.firstHitList[name] == 0:
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
                                 [],
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
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        
        self.server = self.bld.info.server
        
        ids = {}
        for line in self.bld.info.player:
            ids[self.bld.info.player[line].name] = 0
        self.ids = ids

        if self.win:
            self.upload = 1
        if self.mapDetail in ["25人英雄雷域大泽"]:
            self.upload = 1

        # print("[Win]", self.win)

        if self.bossAnalyser.hasBh:
            self.bh = self.bossAnalyser.bh
        else:
            self.bh = None

        # BOSS名称回流
        if self.bossAnalyseName not in ["", "未知"] and self.bld.info.boss != self.bossAnalyseName:
            self.bld.info.boss = self.bossAnalyseName

        # 月泉淮中间分片
        if self.detail["boss"] == "月泉淮":
            if self.bossAnalyser.yqhInterrupt:
                self.available = False  # 进行分片

    def ThirdStageAnalysis(self):
        '''
        第三阶段复盘.
        主要是心法复盘的实现.
        '''
        self.occResult = {}
        for id in self.bld.info.player:
            if self.config.xiangzhiActive and self.occDetailList[id] == "22h":  # 奶歌
                name = self.bld.info.player[id].name
                xiangzhiRep = XiangZhiProReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, self.bh, self.startTime, self.finalTime, self.win)
                xiangzhiRep.replay()
                self.occResult[name] = {"occ": "22h", "result": xiangzhiRep.result}
            if self.config.lingsuActive and self.occDetailList[id] == "212h":  # 灵素
                name = self.bld.info.player[id].name
                lingsuRep = LingSuReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, self.bh, self.startTime, self.finalTime, self.win)
                lingsuRep.replay()
                self.occResult[name] = {"occ": "212h", "result": lingsuRep.result}
            if self.config.lingsuActive and self.occDetailList[id] == "2h":  # 奶花
                name = self.bld.info.player[id].name
                lijingyidaoRep = LiJingYiDaoReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, self.bh, self.startTime, self.finalTime, self.win)
                lijingyidaoRep.replay()
                self.occResult[name] = {"occ": "2h", "result": lijingyidaoRep.result}
            # if self.config.lingsuActive and self.occDetailList[id] == "5h":  # 奶秀
            #     name = self.bld.info.player[id].name
            #     yunchangxinjingRep = YunChangXinJingReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, self.bh, self.startTime, self.finalTime)
            #     yunchangxinjingRep.replay()
            #     self.occResult[name] = {"occ": "5h", "result": yunchangxinjingRep.result}
            if self.config.lingsuActive and self.occDetailList[id] == "6h":  # 奶毒
                name = self.bld.info.player[id].name
                butianjueRep = BuTianJueReplayer(self.config, self.fileNameInfo, self.path, self.bldDict, self.window, name, self.bh, self.startTime, self.finalTime, self.win)
                butianjueRep.replay()
                self.occResult[name] = {"occ": "6h", "result": butianjueRep.result}

    def replay(self):
        '''
        开始演员复盘pro分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.ThirdStageAnalysis()
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
        self.failThreshold = config.failThreshold  # BOSS失败时倒推的秒数
        self.win = 0
        self.mask = config.mask
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

        self.qualifiedRate = config.qualifiedRate
        self.alertRate = config.alertRate
        self.bonusRate = config.bonusRate

        # self.getMap()
        # self.lastTimeStamp = 0

        # 复盘结果信息
        self.potList = []
        self.detail = {"boss": "未知"}
        self.effectiveDPSList = []
        self.equipmentDict = {}
        self.available = True  # 暂时用来判定月泉淮中间分片


#TODO 重构，想办法移除
# class ActorAnalysis():
#
#     def analysis(self):
#         self.potList = []
#         for line in self.generator:
#             self.potList += line.potList
#
#     def loadData(self, fileList, path, raw):
#         for filename in fileList:
#             res = ActorStatGenerator(filename, path, rawdata=raw[filename[0]], failThreshold=self.failThreshold,
#                 battleDate=self.battledate, mask=self.mask, dpsThreshold=self.dpsThreshold, uploadTiantiFlag=self.uploadTiantiFlag)
#
#             analysisExitCode = res.firstStageAnalysis()
#             if analysisExitCode == 1:
#                 continue
#             res.secondStageAnalysis()
#             if res.upload:
#                 res.prepareUpload()
#             self.generator.append(res)
#
#     def __init__(self, filelist, map, path, config, raw):
#         self.myname = config.xiangzhiname
#         self.mask = config.mask
#         self.color = config.color
#         self.text = config.text
#         self.speed = config.speed
#         self.failThreshold = config.failThreshold
#         self.uploadTiantiFlag = config.uploadTianti
#         self.map = map
#         self.battledate = '-'.join(filelist[0][0].split('-')[0:3])
#         self.dpsThreshold = {"qualifiedRate": config.qualifiedRate,
#                              "alertRate": config.alertRate,
#                              "bonusRate": config.bonusRate}
#         self.loadData(filelist, path, raw)

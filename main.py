import os
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import time
import traceback
import sys
import argparse
import hashlib
import json
import urllib.request
import functools

from FileLookUp import FileLookUp
from painter import XiangZhiPainter
from ConfigTools import Config
from ActorReplay import ActorStatGenerator, ActorData, ActorAnalysis
from ReplayBase import StatGeneratorBase
from Functions import *
from Constants import *
from BossNameUtils import *

edition = EDITION

class ShieldCounter():
    shieldLog = []
    breakCount = 0
    shieldCount = 0
    shieldDuration = [0, 0]
    startTime = 0
    finalTime = 0
    nowi = 0
    timeCount = 0

    def checkTime(self, time):
        while self.nowi + 1 < len(self.shieldLog) and self.shieldLog[self.nowi + 1][0] < time:
            self.nowi += 1
        return self.shieldLog[self.nowi][1]

    def analysisShieldData(self):

        s = self.shieldLog

        newList = []
        for i in range(len(s)):
            if i > 0 and i + 1 < len(s) and s[i][1] == 0 and s[i + 1][1] == 1 and s[i + 1][0] - s[i][0] < 500:
                s[i][1] = 2
                s[i + 1][1] = 2
            if i < len(s) and len(newList) > 0 and s[i][1] == newList[-1][1]:
                s[i][1] = 2
            if s[i][1] != 2:
                newList.append(s[i])

        if newList == []:
            newList = [[self.startTime, 0]]
        else:
            if newList[0][1] == 0:
                newList = [[self.startTime, 1]] + newList
            else:
                newList = [[self.startTime, 0]] + newList

        self.shieldLog = newList

        n = len(newList)
        self.shieldDuration = [0, 0]
        self.breakCount = 0
        self.shieldCount = 0
        for i in range(1, n):
            assert newList[i][1] != newList[i - 1][1]
            self.shieldDuration[newList[i - 1][1]] += newList[i][0] - newList[i - 1][0]
            if newList[i][1] == 0:
                self.breakCount += 1
            if newList[i - 1][1] == 1:
                self.shieldCount += 1

        if newList[-1][1] == 1:
            self.shieldCount += 1

        self.shieldDuration[newList[n - 1][1]] += self.finalTime - newList[n - 1][0]

    def __init__(self, shieldLog, startTime, finalTime):
        self.shieldLog = shieldLog
        self.startTime = startTime
        self.finalTime = finalTime


class SkillCounter():
    skillLog = []
    actLog = []
    startTime = 0
    finalTime = 0
    speed = 3770
    sumBusyTime = 0
    sumSpareTime = 0

    def getLength(self, length):
        flames = calculSpeed(self.speed, length)
        return flames * 0.0625 * 1000

    def analysisSkillData(self):
        for line in self.skillLog:
            if line[1] in [15181, 15082, 25232]:  #奶歌常见的自动施放技能：影子宫，影子宫，桑柔
                continue
            elif line[1] in [14137, 14300]:  # 宫，变宫
                self.actLog.append([line[0] - self.getLength(24), self.getLength(24)])
            elif line[1] in [14140, 14301]:  # 徵，变徵
                self.actLog.append([line[0] - self.getLength(16), self.getLength(16)])
            else:
                self.actLog.append([line[0], self.getLength(24)])

        self.actLog.sort(key=lambda x: x[0])

        nowTime = self.startTime
        self.sumBusyTime = 0
        self.sumSpareTime = 0
        for line in self.actLog:
            if line[0] > nowTime:
                self.sumSpareTime += line[0] - nowTime
                self.sumBusyTime += line[1]
                nowTime = line[0] + line[1]
            elif line[0] + line[1] > nowTime:
                self.sumBusyTime += line[0] + line[1] - nowTime
                nowTime = line[0] + line[1]

    def __init__(self, skillLog, startTime, finalTime, speed=3770):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed

def add1(d, s):
    if s in d:
        d[s] += 1
    else:
        d[s] = 1
    return d


class DpsGeneralStatGenerator(StatGeneratorBase):

    def makeEmptyStat(self, name, occ):
        res = {"name": name,
               "occ": occ,
               "damage": 0,
               "numskill": 0,
               "log": []}
        return res

    def SecondStageAnalysis(self):

        res = self.rawdata

        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]

        num = 0

        result = {"player": {},
                  "bossname": self.bossname,
                  "battleTime": self.battleTime}

        for line in sk:
            item = line[""]

            if item[3] == "1":
                if item[14] != "0" and item[4] in namedict:
                    if item[4] not in result["player"]:
                        result["player"][item[4]] = self.makeEmptyStat(namedict[item[4]][0], occdict[item[4]][0])
                    result["player"][item[4]]["damage"] += int(item[14])
                    result["player"][item[4]]["numskill"] += 1
                    result["player"][item[4]]["log"].append([item[2], item[7], item[14]])

            num += 1

        return result

    def __init__(self, filename, path="", rawdata={}, myname=""):
        self.myname = myname
        super().__init__(filename, path, rawdata)


class XiangZhiStatGenerator(StatGeneratorBase):
    myname = ""
    mykey = ""
    npckey = ""
    startTime = 0
    finalTime = 0
    speed = 3770
    shieldCounters = {}
    rumo = {}
    occDetailList = {}
    
    def getMap(self):
        mapid = self.rawdata['20'][0]
        if mapid == "428":
            self.mapDetail = "25人英雄敖龙岛"
        elif mapid == "427":
            self.mapDetail = "25人普通敖龙岛"
        elif mapid == "426":
            self.mapDetail = "10人普通敖龙岛"
        elif mapid == "454":
            self.mapDetail = "25人英雄范阳夜变"
        elif mapid == "453":
            self.mapDetail = "25人普通范阳夜变"
        elif mapid == "452":
            self.mapDetail = "10人普通范阳夜变"
        elif mapid == "484":
            self.mapDetail = "25人英雄达摩洞"
        elif mapid == "483":
            self.mapDetail = "25人普通达摩洞"
        elif mapid == "482":
            self.mapDetail = "10人普通达摩洞"
        else:
            self.mapDetail = "未知"

    def secondStageAnalysis(self):
        res = self.rawdata

        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        occDetailList = self.occDetailList

        data = XiangZhiData()

        data.mykey = self.mykey

        num = 0
        skillLog = []

        self.rumo = {}
        
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            numSmall = 0

        for line in sk:
            item = line[""]

            if int(item[2]) > self.finalTime:
                break

            if item[3] == "1":

                if item[4] == self.mykey and item[11] != '0':
                    if item[10] != '7':
                        data.numheal += int(item[11])
                        data.numeffheal += int(item[12])
                    else:
                        data.numabsorb += int(item[12])

                if int(item[12]) > 0 and item[10] != "7" and item[4] in self.healerDict:
                    if item[4] not in data.healStat:
                        data.healStat[item[4]] = int(item[12])
                    else:
                        data.healStat[item[4]] += int(item[12])

                if item[4] == self.mykey and item[6] == "1":
                    skillLog.append([int(item[2]), int(item[7])])

                if item[12] != '0' and item[5] == self.npckey:
                    if item[4] not in data.npchealstat:
                        data.npchealstat[item[4]] = int(item[12])
                    else:
                        data.npchealstat[item[4]] += int(item[12])

                if item[12] != '0' and self.npckey != 0:
                    if item[5] in self.rumo and self.rumo[item[5]].checkState(int(item[2])):
                        if item[4] not in data.npchealstat:
                            data.npchealstat[item[4]] = int(item[12])
                        else:
                            data.npchealstat[item[4]] += int(item[12])
                            
                if self.activeBoss in ["宓桃", "哑头陀"]:     
                    if item[12] != '0' and self.npckey != 0 and hpsActive:
                        if item[4] not in data.npchealstat:
                            data.npchealstat[item[4]] = int(item[12])
                        else:
                            data.npchealstat[item[4]] += int(item[12])

                # if item[7] == "14231": #梅花三弄
                #    data.numshield += 1

                if item[7] == "14169":  # 一指回鸾
                    data.numpurge += 1

                if int(item[14]) > 0:
                    if item[4] in self.shieldCounters:
                        if item[4] not in data.battlestat:
                            data.battlestat[item[4]] = [0, 0, 0]
                        if int(item[7]) >= 21827 and int(item[7]) <= 21831:  # 桑柔
                            data.battlestat[item[4]][2] += int(item[14])
                        elif int(item[7]) == 25232 and item[4] == self.mykey:
                            data.battlestat[item[4]][2] += int(item[14])
                        else:
                            hasShield = self.shieldCounters[item[4]].checkTime(int(item[2]))
                            data.battlestat[item[4]][hasShield] += int(item[14])

            elif item[3] == "5":
                if item[6] == "16796" and int(item[7]) >= 9:  # 走火入魔
                    # print(item)
                    if item[5] not in self.rumo:
                        self.rumo[item[5]] = BuffCounter("16796", self.startTime, self.finalTime)
                    self.rumo[item[5]].setState(int(item[2]), int(item[10]))
                if item[6] == "17798" and item[10] == "1" and self.activeBoss == "哑头陀" and hpsTime == 0:
                    hpsActive = 1
                    hpsTime = item[2]
                    numSmall = 2

            elif item[3] == "8":
                if len(item) <= 4:
                    continue
                if self.activeBoss == "宓桃":
                    if item[4] == '"人多的时候更有乐趣，大家一起来嘛~"':
                        hpsActive = 1
                        hpsTime = item[2]
                        numSmall = 1
                        if self.mapDetail == "25人英雄达摩洞":
                            numSmall = 2
                            
            elif item[3] == '3':  # 重伤记录
                if self.activeBoss == "宓桃":
                    if item[4] in namedict and namedict[item[4]][0] in ['"天欲宫弟子"', '"天欲宫男宠"'] and (item[4] not in occdict or occdict[item[4]][0] == '0'):
                        numSmall -= 1
                        if numSmall == 0:
                            hpsSumTime += (int(item[2]) - int(hpsTime)) / 1000
                            hpsActive = 0
                if self.activeBoss == "哑头陀":
                    if item[4] in namedict and namedict[item[4]][0] in ['"充能核心"'] and (item[4] not in occdict or occdict[item[4]][0] == '0'):
                        numSmall -= 1
                        if numSmall == 0:
                            hpsSumTime += (int(item[2]) - int(hpsTime)) / 1000
                            hpsActive = 0

            num += 1

        skillCounter = SkillCounter(skillLog, self.startTime, self.finalTime, self.speed)
        skillCounter.analysisSkillData()
        data.sumBusyTime = skillCounter.sumBusyTime
        data.sumSpareTime = skillCounter.sumSpareTime
        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)

        numdam1 = 0
        for key in data.battlestat:
            if int(occdict[key][0]) == 0:
                continue
            line = data.battlestat[key]
            #data.damageDict[key] = line[0] + line[1] / 1.117 # 100赛季数值
            #numdam1 += line[1] / 1.117 * 0.117# + line[2]
            data.damageDict[key] = line[0] + line[1] / 1.0554 # 110赛季数值
            numdam1 += line[1] / 1.0554 * 0.0554# + line[2]
        if self.mykey in data.battlestat:
            numdam2 = data.battlestat[self.mykey][2]
        else:
            numdam2 = 0
        #print(numdam1, numdam2)
        numdam = numdam1 + numdam2

        if self.mykey not in data.damageDict:
            data.damageDict[self.mykey] = numdam
        else:
            data.damageDict[self.mykey] += numdam

        data.damageList = dictToPairs(data.damageDict)
        data.damageList.sort(key=lambda x: -x[1])

        for i in range(len(data.damageList)):
            data.damageList[i].append(namedict[data.damageList[i][0]][0])
            data.damageList[i].append(occDetailList[data.damageList[i][0]])

        sumdamage = 0
        numid = 0
        for line in data.damageList:
            line[1] /= self.battleTime
            sumdamage += line[1]
            numid += 1
            if line[0] == self.mykey and data.myrank == 0:
                data.myrank = numid
                data.mydamage = line[1]
                sumdamage -= line[1]

        data.healList = dictToPairs(data.healStat)
        data.healList.sort(key=lambda x: -x[1])

        sumHeal = 0
        numid = 0
        topHeal = 0
        for line in data.healList:
            if numid == 0:
                topHeal = line[1]
            sumHeal += line[1]
            numid += 1
            if line[0] == self.mykey and data.myHealRank == 0:
                data.myHealRank = numid
            if line[1] > topHeal * 0.2:
                data.numHealer += 1

        if data.myHealRank > data.numHealer:
            data.numHealer = data.myHealRank

        data.healRate = data.numeffheal / sumHeal

        sumShield = 0
        for key in self.shieldCounters:
            sumShield += self.shieldCounters[key].shieldCount
            if int(occdict[key][0]) in [0, ]:
                continue
            if key not in data.damageDict or data.damageDict[key] / self.battleTime < 10000:
                continue
            if occDetailList[key] in ["1t", "2h", "3t", "5h", "10t", "6h", "21t", "22h"]:
                continue
            if key == self.mykey:
                continue

            rate = self.shieldCounters[key].shieldDuration[1] / \
                   (self.shieldCounters[key].shieldDuration[0] + self.shieldCounters[key].shieldDuration[1] + 1e-10)
            data.rateDict[key] = rate
            data.durationDict[key] = self.shieldCounters[key].shieldDuration[1]
            data.breakDict[key] = self.shieldCounters[key].breakCount

        data.numshield = sumShield

        data.equalDPS = data.mydamage / (sumdamage + 1e-10) * (len(data.durationDict) - 1)

        numrate = 0
        sumrate = 0
        
        if self.activeBoss in ["宓桃", "哑头陀"]:  
            for line in data.npchealstat:
                data.npchealstat[line] /= hpsSumTime

        for key in data.rateDict:
            numrate += 1
            sumrate += data.rateDict[key]

        data.overallrate = sumrate / (numrate + 1e-10)

        self.data = data

    def firstStageAnalysis(self):

        res = self.rawdata

        if '9' not in res:
            raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")

        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        occDetailList = {}
        
        for line in occdict:
            if occdict[line][0] != '0':
                occDetailList[line] = occdict[line][0]

        for key in namedict:
            if namedict[key][0] == '"尹青羲"':
                self.npckey = key
                break
            if namedict[key][0] == '"安小逢"':
                self.npckey = key
                break
            if namedict[key][0] in ['"宓桃"', '"毗留博叉"']:
                self.npckey = key
                break

        MoWenList = []
        XiangZhiList = []

        self.healerDict = {}

        shieldLogDict = {}
        jingshenkuifa = {}

        self.interrupt = 0
        
        self.activeBoss = ""

        for line in sk:
            item = line[""]
            if self.startTime == 0:
                self.startTime = int(item[2])
            self.finalTime = int(item[2])

            if self.interrupt != 0:
                continue

            if item[3] == "1":
                if item[4] not in MoWenList and item[7] in ["14067", "14298", "14302"]:
                    MoWenList.append(item[4])
                if item[4] not in XiangZhiList and item[7] in ["14231", "14140", "14301"]:
                    XiangZhiList.append(item[4])
                    self.healerDict[item[4]] = 0
                if item[4] not in self.healerDict and item[7] in ["565", "554", "555", "2232", "6662", "2233", "6675", "2231", "101", "142", "138"]:
                    self.healerDict[item[4]] = 0
                if item[7] == "14231":
                    jingshenkuifaStack = 0
                    if item[5] in jingshenkuifa:
                        jingshenkuifaStack = jingshenkuifa[item[5]].checkState(int(item[2]))
                    if jingshenkuifaStack < 20:
                        if item[5] not in shieldLogDict:
                            shieldLogDict[item[5]] = [[int(item[2]), 1]]
                        else:
                            shieldLogDict[item[5]].append([int(item[2]), 1])
                            
                if item[4] in occDetailList and occDetailList[item[4]] in ['1', '2', '3', '4', '5', '6', '7', '10', '21', '22']:
                    occDetailList[item[4]] = checkOccDetailBySkill(occDetailList[item[4]], item[7], item[12])
                    
                if item[5] in namedict and namedict[item[5]][0] == '"宓桃"':
                    self.activeBoss = "宓桃"
                if item[5] in namedict and namedict[item[5]][0] == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif item[3] == "5":
                if item[6] in ["9334", "16911"]:  # buff梅花三弄
                    if item[5] not in shieldLogDict:
                        shieldLogDict[item[5]] = [[int(item[2]), int(item[10])]]
                    else:
                        shieldLogDict[item[5]].append([int(item[2]), int(item[10])])
                if item[6] in ["15774", "17200"]:  # buff精神匮乏
                    if item[5] not in jingshenkuifa:
                        jingshenkuifa[item[5]] = BuffCounter("17200", self.startTime, self.finalTime)
                    jingshenkuifa[item[5]].setState(int(item[2]), int(item[10]))
                if item[4] in occDetailList and occDetailList[item[4]] in ['21']:
                    occDetailList[item[4]] = checkOccDetailByBuff(occDetailList[item[4]], item[6])

            elif item[3] == "8":
                if len(item) < 5:
                    continue
                if item[4] in ['"嘶...这帮贼人竟如此厉害。余下将士，快随我冲出去！"'] and item[6] == '"周贽"':
                    self.interrupt = int(item[2])

        if self.interrupt != 0:
            self.battleTime -= (self.finalTime - self.interrupt) / 1000
            self.finalTime = self.interrupt

        if self.myname == "":
            if len(XiangZhiList) >= 2:
                nameList = []
                for line in XiangZhiList:
                    nameList.append(namedict[line][0])
                s = str(nameList)
                raise Exception('奶歌的数量不止一个，请手动指示ID。可能的ID为：%s' % s)
            elif len(XiangZhiList) == 0:
                raise Exception('没有找到奶歌，请确认数据是否正确')
            else:
                self.mykey = XiangZhiList[0]
                self.myname = namedict[self.mykey][0]
        else:
            for key in namedict:
                if namedict[key][0].strip('"') == self.myname.strip('"'):
                    self.mykey = key

        self.shieldCounters = {}
        for key in shieldLogDict:
            self.shieldCounters[key] = ShieldCounter(shieldLogDict[key], self.startTime, self.finalTime)
            self.shieldCounters[key].analysisShieldData()

        for key in occdict:
            if occdict[key] != 0 and key not in self.shieldCounters:
                self.shieldCounters[key] = ShieldCounter([], self.startTime, self.finalTime)
                self.shieldCounters[key].analysisShieldData()
                
        self.occDetailList = occDetailList

    def __init__(self, filename, myname, path="", rawdata={}):
        self.myname = myname
        super().__init__(filename[0], path, rawdata)
        self.getMap()
        # self.filename = filename
        # self.parseFile(path)

class XiangZhiData():

    def __init__(self):
        self.numheal = 0
        self.numeffheal = 0
        self.numabsorb = 0
        self.healRate = 0
        self.numHealer = 0
        self.myHealRank = 0
        self.numshield = 0
        self.numpurge = 0
        self.mydamage = 0
        self.myrank = 0
        self.battlestat = {}
        self.npchealstat = {}
        self.healStat = {}
        self.damageDict = {}
        self.damageList = []
        self.equalDPS = 0
        self.rateDict = {}
        self.durationDict = {}
        self.breakDict = {}
        self.overallrate = 0
        self.sumSpareTime = 0
        self.sumBusyTime = 0
        self.spareRate = 0
        self.mykey = ""


class XiangZhiOverallData(XiangZhiData):

    def __init__(self):
        XiangZhiData.__init__(self)
        self.healTable = []
        self.dpsTable = []
        self.maxDpsTable = []
        self.maxDpsName = ""
        self.maxDps = 0
        self.maxDpsRank = 999
        self.maxEqualDPS = 0

        self.rateTable = []
        self.maxRateName = ""
        self.maxRate = 0

        self.rateList = []
        self.breakList = []

        self.bossRateDict = {}
        self.bossBreakDict = {}

        self.maxSingleRate = 0
        self.maxSingleRateName = ""
        self.maxSingleBreak = 0
        self.maxSingleBreakName = ""

        self.npcHealDict = {}
        self.npcHealList = []
        self.npcRank = 0
        self.npcHeal = 0
        self.npcSumHeal = 0
        self.npcHealRate = 0
        self.npcHealNum = 0

        self.mykey = ""

        self.spareRateList = []


class XiangZhiScore():
    map = "敖龙岛"
    
    def getRateScale(self, mapdetail):
        if mapdetail == "25人普通达摩洞":
            self.rateScale = [[100, 11, "天道", "天间璀璨，无上荣光。"],
                         [90, 12, "人道", "纷繁乱世，不忘初心。"],
                         [80, 13, "阿修罗道", "心存善念，莫问前程。"],
                         [70, 14, "畜生道", "入此道者，受截图发群，团长点名之业报。"],
                         [60, 15, "饿鬼道", "入此道者，受团队出警，团员避雷之业报。"],
                         [0, 16, "地狱道", "入此道者，受踢出团队，贴吧818之业报。"]]
        else:
            self.rateScale = [[100, 0, "A+", "不畏浮云遮望眼，只缘身在最高层。"],
                         [95, 1, "A", "独有凤凰池上客，阳春一曲和皆难。"],
                         [90, 1, "A-", "欲把一麾江海去，乐游原上望昭陵。"],
                         [85, 2, "B+", "敢将十指夸针巧，不把双眉斗画长。"],
                         [80, 2, "B", "云想衣裳花想容，春风拂槛露华浓。"],
                         [77, 2, "B-", "疏影横斜水清浅，暗香浮动月黄昏。"],
                         [73, 3, "C+", "青山隐隐水迢迢，秋尽江南草未凋。"],
                         [70, 3, "C", "花径不曾缘客扫，蓬门今始为君开。"],
                         [67, 3, "C-", "上穷碧落下黄泉，两处茫茫皆不见。"],
                         [63, 4, "D+", "人世几回伤往事，山形依旧枕寒流。"],
                         [60, 4, "D", "总为浮云能蔽日，长安不见使人愁。"],
                         [0, 6, "F", "仰天大笑出门去，我辈岂是蓬蒿人。"]]

    def scaleScore(self, x, scale):
        N = len(scale)
        assert N >= 2
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

    def analysisHPS(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                HPSList = [[2000, 0], [12000, 5]]
            elif id == 2:
                HPSList = [[2000, 0], [10000, 5]]
            elif id == 3:
                return 0
            elif id == 4:
                HPSList = [[1000, 0], [5000, 3], [8000, 5]]
            elif id == 5:
                HPSList = [[500, 0], [1500, 2], [2500, 3], [5000, 5]]
            elif id == 6:
                HPSList = [[500, 0], [1500, 4], [3000, 7]]
            hps = self.data.healTable[id - 1][1]
        elif self.map == "范阳夜变":
            if id == 1:
                HPSList = [[2000, 0], [6000, 2], [10000, 5]]
            elif id == 2:
                HPSList = [[2000, 0], [6000, 2], [10000, 5]]
            elif id == 3:
                HPSList = [[3000, 0], [8000, 2], [15000, 7]]
            elif id == 4:
                HPSList = [[3000, 0], [8000, 2], [15000, 7]]
            elif id == 5:
                HPSList = [[2000, 0], [5000, 4], [10000, 12]]
            hps = self.data.healTable[id - 1][1] + self.data.healTable[id - 1][5]
        elif self.mapdetail == "25人普通达摩洞":
            if id == 1:
                HPSList = [[1000, 0], [5000, 3], [10000, 5]]
            elif id == 2:
                HPSList = [[3000, 0], [16000, 3], [30000, 5]]
            elif id == 3:
                HPSList = [[2000, 0], [6000, 3], [12000, 5]]
            elif id == 4:
                HPSList = [[1000, 0], [4000, 3], [8000, 5]]
            elif id == 5:
                HPSList = [[2000, 0], [8000, 2], [15000, 4]]
            elif id == 6:
                HPSList = [[2000, 0], [9000, 3], [18000, 7]]
            hps = self.data.healTable[id - 1][1] + self.data.healTable[id - 1][5]
        score = self.scaleScore(hps, HPSList)
        return score

    def analysisShield(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                ShieldList = [[10, 0], [16, 3], [24, 5]]
            elif id == 2:
                ShieldList = [[12, 0], [18, 3], [28, 5]]
            elif id == 3:
                return 0
            elif id == 4:
                ShieldList = [[6, 0], [10, 3], [16, 5]]
            elif id == 5:
                ShieldList = [[3, 0], [10, 1], [25, 5]]
            elif id == 6:
                ShieldList = [[1, 0], [5, 1], [13, 4], [20, 7]]
        elif self.map == "范阳夜变":
            if id == 1:
                ShieldList = [[7, 0], [15, 2], [30, 5]]
            elif id == 2:
                ShieldList = [[7, 0], [13, 2], [20, 5]]
            elif id == 3:
                ShieldList = [[7, 0], [15, 2], [30, 7]]
            elif id == 4:
                ShieldList = [[7, 0], [15, 2], [25, 7]]
            elif id == 5:
                ShieldList = [[5, 0], [10, 2], [20, 12]]
        elif self.mapdetail == "25人普通达摩洞":
            if id == 1:
                ShieldList = [[3, 0], [9, 3], [15, 5]]
            elif id == 2:
                ShieldList = [[5, 0], [16, 3], [22, 5]]
            elif id == 3:
                ShieldList = [[4, 0], [14, 3], [20, 5]]
            elif id == 4:
                ShieldList = [[3, 0], [12, 3], [18, 5]]
            elif id == 5:
                ShieldList = [[3, 0], [12, 2], [18, 4]]
            elif id == 6:
                ShieldList = [[5, 0], [12, 3], [21, 7]]
        score = self.scaleScore(self.data.healTable[id - 1][8], ShieldList)
        return score

    def analysisDPS(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                DPSList = [[0.65, 0], [1.15, 5]]
            elif id == 2:
                DPSList = [[0.4, 0], [1.0, 5]]
            elif id == 3:
                DPSList = [[0.41, 0], [1.65, 10]]
            elif id == 4:
                DPSList = [[0.25, 0], [0.83, 5]]
            elif id == 5:
                DPSList = [[0.25, 0], [0.65, 2], [1.05, 5]]
            elif id == 6:
                DPSList = [[0.25, 0], [0.65, 2], [1.15, 7]]
        elif self.map == "范阳夜变":
            if id == 1:
                DPSList = [[0.65, 0], [1.0, 2], [1.65, 5]]
            elif id == 2:
                DPSList = [[0.65, 0], [1.05, 2], [1.65, 5]]
            elif id == 3:
                DPSList = [[0.4, 0], [0.65, 2], [1.05, 7]]
            elif id == 4:
                DPSList = [[0.5, 0], [0.75, 2], [1.2, 7]]
            elif id == 5:
                DPSList = [[0.3, 0], [0.55, 4], [1.45, 12]]
        elif self.mapdetail == "25人普通达摩洞":
            if id == 1:
                DPSList = [[0.8, 0], [2.0, 5]]
            elif id == 2:
                DPSList = [[0.3, 0], [1.3, 5]]
            elif id == 3:
                DPSList = [[0.5, 0], [1.8, 5]]
            elif id == 4:
                DPSList = [[0.5, 0], [1.8, 5]]
            elif id == 5:
                DPSList = [[0.5, 0], [1.8, 4]]
            elif id == 6:
                DPSList = [[0.3, 0], [1.4, 7]]
        score = self.scaleScore(self.data.dpsTable[id - 1][3], DPSList)
        return score

    def analysisRate(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                RateList = [[0.1, 0], [0.3, 1], [0.5, 5]]
            elif id == 2:
                RateList = [[0.1, 0], [0.25, 1], [0.45, 5]]
            elif id == 3:
                RateList = [[0.1, 0], [0.5, 1], [0.8, 10]]
            elif id == 4:
                RateList = [[0.1, 0], [0.2, 1], [0.5, 5]]
            elif id == 5:
                RateList = [[0.1, 0], [0.2, 1], [0.6, 5]]
            elif id == 6:
                RateList = [[0.1, 0], [0.2, 1], [0.6, 7]]
        elif self.map == "范阳夜变":
            if id == 1:
                RateList = [[0.1, 0], [0.7, 3], [0.95, 5]]
            elif id == 2:
                RateList = [[0.1, 0], [0.7, 3], [0.95, 5]]
            elif id == 3:
                RateList = [[0.1, 0], [0.25, 2], [0.6, 7]]
            elif id == 4:
                RateList = [[0.1, 0], [0.3, 2], [0.7, 7]]
            elif id == 5:
                RateList = [[0.1, 0], [0.2, 1], [0.7, 12]]
        elif self.mapdetail == "25人普通达摩洞":
            if id == 1:
                RateList = [[0.1, 0], [0.7, 1], [0.9, 5]]
            elif id == 2:
                RateList = [[0.1, 0], [0.15, 1], [0.55, 5]]
            elif id == 3:
                RateList = [[0.1, 0], [0.5, 1], [0.85, 5]]
            elif id == 4:
                RateList = [[0.1, 0], [0.5, 1], [0.8, 5]]
            elif id == 5:
                RateList = [[0.1, 0], [0.5, 1], [0.8, 4]]
            elif id == 6:
                RateList = [[0.1, 0], [0.3, 1], [0.75, 7]]
        score = self.scaleScore(self.data.rateTable[id - 1][1], RateList)
        return score

    def analysisSpare(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 2:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 3:
                RateList = [[0.5, 0], [0.1, 5]]
            elif id == 4:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 5:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 6:
                RateList = [[0.5, 0], [0.1, 7]]
        elif self.map == "范阳夜变":
            if id == 1:
                RateList = [[0.5, 0], [0.3, 1], [0.1, 5]]
            elif id == 2:
                RateList = [[0.5, 0], [0.3, 1], [0.1, 5]]
            elif id == 3:
                RateList = [[0.3, 0], [0.1, 6]]
            elif id == 4:
                RateList = [[0.3, 0], [0.1, 6]]
            elif id == 5:
                RateList = [[0.3, 0], [0.1, 6]]
        elif self.mapdetail == "25人普通达摩洞":
            if id == 1:
                RateList = [[0.5, 0], [0.1, 5]]
            elif id == 2:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 3:
                RateList = [[0.35, 0], [0.15, 5]]
            elif id == 4:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 5:
                RateList = [[0.3, 0], [0.1, 5]]
            elif id == 6:
                RateList = [[0.35, 0], [0.15, 6]]
        score = self.scaleScore(self.data.spareRateList[id - 1][1], RateList)
        return score

    def analysisPurge(self, id):
        if self.map == "敖龙岛" or self.map == "范阳夜变":
            PurgeList = [[0, 0], [3, 3], [10, 5]]
        elif self.mapdetail == "25人普通达摩洞":
            PurgeList = [[0, 0], [5, 3], [20, 5]]
        score = self.scaleScore(self.generator[id - 1].data.numpurge, PurgeList)
        return score

    def analysisNPC(self, id):
        if self.map == "敖龙岛":
            NPCList = [[0.15, 0], [0.3, 5]]
            compareRate = self.data.npcHealRate
        elif self.map == "范阳夜变":
            NPCList = [[0.1, 0], [0.2, 5]]
            compareRate = self.data.npcHealRate
        elif self.mapdetail == "25人普通达摩洞":
            if id == 2:
                NPCList = [[0.1, 0], [0.3, 5]]
                compareRate = self.data.npcHealRate[0]
            elif id == 5:
                NPCList = [[0.05, 0], [0.3, 2]]
                compareRate = self.data.npcHealRate[1]
        score = self.scaleScore(compareRate, NPCList)
        return score

    def analysisInner(self, id):
        InnerList = [[0, 0], [1, 3], [2, 5]]
        score = self.scaleScore(sum(self.generator2[id - 1].data.innerPlace[self.mykey]), InnerList)
        return score

    def analysisDrawer(self, id):
        InnerList = [[0, 0], [4, 4]]
        score = self.scaleScore(self.generator2[id - 1].data.drawer[self.mykey], InnerList)
        return score

    def analysisBOSSald(self, id):
        cutOff1 = [0, 5, 5, 0, 5, 5, 7]
        cutOff2 = [0, 5, 5, 10, 5, 5, 7]
        cutOff4 = [0, 0, 0, 0, 5, 0, 5]
        cutOff0 = [0, 15, 15, 15, 20, 15, 20]
        self.printTable.append([0, "%s 打分表" % self.bossDictR[id], ""])
        c1 = 0
        c5 = 0
        
        
        
        
        if id != 3:
            s1 = self.analysisHPS(id)
            self.printTable.append([1, "治疗量", "%.1f" % s1])
            s2 = self.analysisShield(id)
            self.printTable.append([1, "盾数", "%.1f" % s2])
            c1 = s1 + s2
            if c1 > cutOff1[id]:
                c1 = cutOff1[id]
                c5 += (s1 + s2 - cutOff1[id]) / 2
        s3 = self.analysisDPS(id)
        self.printTable.append([1, "等效DPS", "%.1f" % s3])
        s4 = self.analysisRate(id)
        self.printTable.append([1, "覆盖率", "%.1f" % s4])
        c2 = s3 + s4
        if c2 > cutOff2[id]:
            c2 = cutOff2[id]
            c5 += (s3 + s4 - cutOff2[id]) / 2
        s5 = self.analysisSpare(id)
        self.printTable.append([1, "空闲比例", "%.1f" % s5])
        c3 = s5

        c4 = 0
        if id == 4:
            s6 = self.analysisPurge(id)
            self.printTable.append([1, "驱散次数", "%.1f" % s6])
            s7 = self.analysisNPC(id)
            self.printTable.append([1, "NPC承疗", "%.1f" % s7])
            c4 = s6 + s7
            if c4 > cutOff4[id]:
                c4 = cutOff4[id]
                c5 += (s6 + s7) / 2
        elif id == 5:
            s6 = self.analysisDrawer(id)
            self.printTable.append([1, "连线", "%.1f" % s6])
            c4 = s6
        elif id == 6:
            s6 = self.analysisInner(id)
            self.printTable.append([1, "内场", "%.1f" % s6])
            c4 = s6

        numDPS = self.data.dpsTable[id - 1][4]
        if numDPS < 16:
            s8 = 16 - numDPS
            self.printTable.append([1, "人数修正", "%.1f" % s8])
            c5 += s8

        c6 = c1 + c2 + c3 + c4 + c5
        if c6 > cutOff0[id]:
            c6 = cutOff0[id]

        c7 = 0
        c8 = 0

        num1 = sum(self.generator2[id - 1].data.hitCount[self.mykey].values())
        num2 = sum(self.generator2[id - 1].data.deathCount[self.mykey])
        if num1 > 0:
            c7 = -num1
            self.printTable.append([2, "犯错", "%.1f" % c7])
        if num2 > 0:
            c8 = -num2 * 2
            self.printTable.append([2, "重伤", "%.1f" % c8])

        c9 = c6 + c7 + c8
        if c9 < 0:
            c9 = 0

        self.printTable.append([3, "小计", "%.1f" % c9])
        return c9

    def analysisBOSSyd(self, id):
        cutOff1 = [0, 5, 5, 7, 7, 12]
        cutOff2 = [0, 5, 5, 7, 7, 12]
        cutOff4 = [0, 0, 0, 0, 0, 0, 0]
        cutOff0 = [0, 15, 15, 20, 20, 30]
        self.printTable.append([0, "%s 打分表" % self.bossDictR[id], ""])
        c1 = 0
        c5 = 0

        s1 = self.analysisHPS(id)
        self.printTable.append([1, "治疗量", "%.1f" % s1])
        s2 = self.analysisShield(id)
        self.printTable.append([1, "盾数", "%.1f" % s2])
        c1 = s1 + s2
        if c1 > cutOff1[id]:
            c1 = cutOff1[id]
            c5 += (s1 + s2 - cutOff1[id]) / 2

        s3 = self.analysisDPS(id)
        self.printTable.append([1, "等效DPS", "%.1f" % s3])
        s4 = self.analysisRate(id)
        self.printTable.append([1, "覆盖率", "%.1f" % s4])
        c2 = s3 + s4
        if c2 > cutOff2[id]:
            c2 = cutOff2[id]
            c5 += (s3 + s4 - cutOff2[id]) / 2

        s5 = self.analysisSpare(id)
        self.printTable.append([1, "空闲比例", "%.1f" % s5])
        c3 = s5

        c4 = 0

        numDPS = self.data.dpsTable[id - 1][4]
        if numDPS < 16:
            s8 = 16 - numDPS
            self.printTable.append([1, "人数修正", "%.1f" % s8])
            c5 += s8

        c6 = c1 + c2 + c3 + c4 + c5
        if c6 > cutOff0[id]:
            c6 = cutOff0[id]

        c7 = 0
        c8 = 0

        num1 = sum(self.generator2[id - 1].data.hitCount[self.mykey].values())
        num2 = sum(self.generator2[id - 1].data.deathCount[self.mykey])
        if num1 > 0:
            c7 = -num1
            self.printTable.append([2, "犯错", "%.1f" % c7])
        if num2 > 0:
            c8 = -num2 * 2
            self.printTable.append([2, "重伤", "%.1f" % c8])

        c9 = c6 + c7 + c8
        if c9 < 0:
            c9 = 0

        self.printTable.append([3, "小计", "%.1f" % c9])
        return c9
        
    def analysisBOSSptdmd(self, id):
        cutOff1 = [0, 5, 5, 5, 5, 4, 7]
        cutOff2 = [0, 5, 5, 5, 5, 4, 7]
        cutOff4 = [0, 5, 0, 0, 0, 2, 0]
        cutOff0 = [0, 15, 20, 15, 15, 15, 20]
        self.printTable.append([0, "%s 打分表" % self.bossDictR[id], ""])
        c1 = 0
        c5 = 0
        
        s1 = self.analysisHPS(id)
        self.printTable.append([1, "治疗量", "%.1f" % s1])
        s2 = self.analysisShield(id)
        self.printTable.append([1, "盾数", "%.1f" % s2])
        c1 = s1 + s2
        if c1 > cutOff1[id]:
            c1 = cutOff1[id]
            c5 += (s1 + s2 - cutOff1[id]) / 2
            
        s3 = self.analysisDPS(id)
        self.printTable.append([1, "等效DPS", "%.1f" % s3])
        s4 = self.analysisRate(id)
        self.printTable.append([1, "覆盖率", "%.1f" % s4])
        c2 = s3 + s4
        if c2 > cutOff2[id]:
            c2 = cutOff2[id]
            c5 += (s3 + s4 - cutOff2[id]) / 2

        s5 = self.analysisSpare(id)
        self.printTable.append([1, "空闲比例", "%.1f" % s5])
        c3 = s5

        c4 = 0
        if id == 2:
            s6 = self.analysisPurge(id)
            self.printTable.append([1, "驱散次数", "%.1f" % s6])
            s7 = self.analysisNPC(id)
            self.printTable.append([1, "AOE治疗", "%.1f" % s7])
            c4 = s6 + s7
            if c4 > cutOff4[id]:
                c4 = cutOff4[id]
                c5 += (s6 + s7) / 2
        elif id == 5:
            s7 = self.analysisNPC(id)
            self.printTable.append([1, "AOE治疗", "%.1f" % s7])
            c4 = s7

        numDPS = self.data.dpsTable[id - 1][4]
        if numDPS < 16:
            s8 = 16 - numDPS
            self.printTable.append([1, "人数修正", "%.1f" % s8])
            c5 += s8

        c6 = c1 + c2 + c3 + c4 + c5
        if c6 > cutOff0[id]:
            c6 = cutOff0[id]

        c7 = 0
        c8 = 0

        num1 = sum(self.generator2[id - 1].data.hitCount[self.mykey].values())
        num2 = sum(self.generator2[id - 1].data.deathCount[self.mykey])
        if num1 > 0:
            c7 = -num1
            self.printTable.append([2, "犯错", "%.1f" % c7])
        if num2 > 0:
            c8 = -num2 * 2
            self.printTable.append([2, "重伤", "%.1f" % c8])

        c9 = c6 + c7 + c8
        if c9 < 0:
            c9 = 0

        self.printTable.append([3, "小计", "%.1f" % c9])
        return c9

    def finalRate(self):
        for line in self.rateScale:
            if self.score >= line[0]:
                self.color = line[1]
                self.rate = line[2]
                self.describe = line[3]
                break

    def analysisAll(self):
        if len(self.generator) == 6 and self.map == "敖龙岛":
            self.available = 1
            sumScore = 0
            for i in range(1, 7):
                score = self.analysisBOSSald(i)
                sumScore += score
            self.printTable.append([0, "总分", "%.1f" % sumScore])
            self.score = sumScore
            self.finalRate()
        elif len(self.generator) == 5 and self.map == "范阳夜变":
            self.available = 1
            sumScore = 0
            for i in range(1, len(self.generator) + 1):
                score = self.analysisBOSSyd(i)
                sumScore += score
            self.printTable.append([0, "总分", "%.1f" % sumScore])
            self.score = sumScore
            self.finalRate()
        elif len(self.generator) == 6 and self.mapdetail == "25人普通达摩洞":
            self.available = 1
            sumScore = 0
            for i in range(1, 7):
                score = self.analysisBOSSptdmd(i)
                sumScore += score
            self.printTable.append([0, "总分", "%.1f" % sumScore])
            self.score = sumScore
            self.finalRate()
        else:
            self.available = 0
            print("战斗记录不全，无法进行打分。")

    def __init__(self, data, generator, generator2, mykey, map, mapdetail):
        self.data = data
        self.mykey = mykey
        self.generator = generator
        self.generator2 = generator2
        self.map = map
        self.mapdetail = mapdetail + map
        self.printTable = []
        self.score = 0
        self.bossDict, self.bossDictR = getBossDictFromMap(self.map)
        self.getRateScale(self.mapdetail)

class RawDataParser():

    def parseFile(self, path, filename):
        if path == "":
            name = filename
        else:
            name = "%s\\%s" % (path, filename)
        print("读取文件：%s" % name)
        f = open(name, "r")
        s = f.read()
        res, _ = parseLuatable(s, 8, len(s))

        if '9' not in res:
            if len(res['']) == 17:
                for i in range(1, 17):
                    res[str(i)] = [res[''][i - 1]]
            else:
                raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")

        return res

    def __init__(self, filelist, path):
        self.rawdata = {}
        for filename in filelist:
            self.rawdata[filename[0]] = self.parseFile(path, filename[0])


class XiangZhiAnalysis():
    map = "敖龙岛"
    mapdetail = "未知"
    myname = ""
    generator = []
    generator2 = []
    battledate = ""
    mask = 0
    color = 1
    text = 0
    speed = 3770
    pastH = 0

    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def hashGroup(self):
        nameList = []
        for line in self.namedict:
            if line in self.occdict and self.occdict[line][0].strip('"') != "0":
                nameList.append(self.namedict[line][0].strip('"'))
        nameList.sort()
        hashStr = self.battledate + self.mapdetail + self.map + edition + "".join(nameList)
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self, upload=0):
        result = {}
        server = self.generator[0].rawdata["19"][0].strip('"')
        result["server"] = server
        result["id"] = self.myname.strip('"')
        result["score"] = self.score.score
        result["battledate"] = self.battledate
        result["mapdetail"] = self.mapdetail + self.map
        result["edition"] = edition
        result["hash"] = self.hashGroup()
        result["public"] = self.public
        allInfo = {}
        data = self.data
        allInfo["speed"] = self.speed
        
        allInfo["healTable"] = data.healTable
        allInfo["dpsTable"] = data.dpsTable
        allInfo["rateTable"] = data.rateTable
        allInfo["overallrate"] = data.overallrate
        allInfo["bossRateDict"] = data.bossRateDict
        allInfo["bossBreakDict"] = data.bossBreakDict
        allInfo["maxDpsName"] = data.maxDpsName
        allInfo["maxDpsTable"] = data.maxDpsTable
        allInfo["npcHealList"] = data.npcHealList
        allInfo["spareRateList"] = data.spareRateList
        allInfo["spareRate"] = data.spareRate
        allInfo["healList"] = data.healList
        allInfo["printTable"] = self.score.printTable

        allInfo["rateList"] = data.rateList
        allInfo["breakList"] = data.breakList

        allInfo["numheal"] = data.numheal
        allInfo["numeffheal"] = data.numeffheal
        allInfo["numshield"] = data.numshield
        allInfo["maxDps"] = data.maxDps
        allInfo["maxEqualDPS"] = data.maxEqualDPS
        allInfo["maxDpsRank"] = data.maxDpsRank
        allInfo["maxSingleRateName"] = self.getMaskName(data.maxSingleRateName)
        allInfo["maxSingleRate"] = data.maxSingleRate
        allInfo["maxSingleBreakName"] = self.getMaskName(data.maxSingleBreakName)
        allInfo["maxSingleBreak"] = data.maxSingleBreak
        allInfo["hardBOSS"] = self.hardBOSS
        allInfo["numpurge"] = data.numpurge
        allInfo["hardNPC"] = self.hardNPC
        allInfo["npcHeal"] = data.npcHeal
        allInfo["npcRank"] = data.npcRank
        allInfo["npcNum"] = data.npcHealNum
        allInfo["npcHealRate"] = data.npcHealRate
        allInfo["sumHit"] = self.sumHit
        allInfo["sumDeath"] = self.sumDeath
        allInfo["hitCount"] = self.actorData.hitCount[data.mykey]
        if self.map == "敖龙岛":
            allInfo["sumDrawer"] = self.sumDrawer
            allInfo["sumInner"] = self.sumInner

        for i in range(len(allInfo["rateList"])):
            allInfo["rateList"][i][2] = self.getMaskName(allInfo["rateList"][i][2])
        for i in range(len(allInfo["breakList"])):
            allInfo["breakList"][i][2] = self.getMaskName(allInfo["breakList"][i][2])
        for i in range(len(allInfo["maxDpsTable"])):
            allInfo["maxDpsTable"][i][2] = self.getMaskName(allInfo["maxDpsTable"][i][2])
        if type(data.numpurge) == type(0):
            for i in range(len(allInfo["npcHealList"])):
                allInfo["npcHealList"][i][2] = self.getMaskName(allInfo["npcHealList"][i][2])
        else:
            for j in range(len(data.numpurge)):
                for i in range(len(allInfo["npcHealList"][j])):
                    #print(allInfo["npcHealList"])
                    allInfo["npcHealList"][j][i][2] = self.getMaskName(allInfo["npcHealList"][j][i][2])
        result["statistics"] = allInfo

        result["id"] = self.getMaskName(result["id"])

        if upload:
            Jdata = json.dumps(result)
            jpost = {'jdata': Jdata}
            jparse = urllib.parse.urlencode(jpost).encode('utf-8')
            resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadXiangZhiData', data=jparse)
            res = json.load(resp)
            return result, res
        else:
            return result, None

    def paint(self, filename):
        painter = XiangZhiPainter()
        painter.text = self.text
        painter.speed = self.speed
        painter.mask = self.mask
        painter.color = self.color
        painter.paint(self.info, "result.png")

    def loadData(self, fileList, path, raw):

        for filename in fileList:
            res = XiangZhiStatGenerator(filename, self.myname, rawdata=raw[filename[0]])
            res.speed = self.speed
            res.firstStageAnalysis()
            res.secondStageAnalysis()
            self.generator.append(res)
            if self.myname == "":
                self.myname = res.myname
            elif self.myname != res.myname:
                raise Exception("全程奶歌名称不一致，请手动指定ID")

            res2 = ActorStatGenerator(filename, path, res.rawdata, self.myname)
            res2.startTime = res.startTime
            res2.finalTime = res.finalTime
            res2.secondStageAnalysis()
            self.generator2.append(res2)

    def analysis(self):

        generator = self.generator

        self.hardBOSS = "源思弦"
        self.hardNPC = "[尹青羲]"

        if self.map == "敖龙岛":
            mapid = generator[0].rawdata['20'][0]
            if mapid == "428":
                self.mapdetail = "25人英雄"
            elif mapid == "427":
                self.mapdetail = "25人普通"
            elif mapid == "426":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知   "

        if self.map == "范阳夜变":
            self.hardBOSS = "安小逢"
            self.hardNPC = "走火入魔玩家"
            self.hitDict = {"s23621": "隐雷鞭",
                            "s23700": "短歌式",
                            "b16842": "符咒禁锢",
                            "s24029": "赤镰乱舞·矩形",
                            "s24030": "赤镰乱舞·扇形",
                            "s24031": "赤镰乱舞·圆形",
                            "b17110": "绞首链",
                            "b17301": "不听话的小孩子",
                            }

            mapid = generator[0].rawdata['20'][0]
            if mapid == "454":
                self.mapdetail = "25人英雄"
            elif mapid == "453":
                self.mapdetail = "25人普通"
            elif mapid == "452":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知   "
                
        if self.map == "达摩洞":
            mapid = generator[0].rawdata['20'][0]
            self.hardBOSS = ["宓桃", "哑头陀"]
            self.hardNPC = ["蛊心魅智阶段", "充能阶段"]
            self.hitDict = {}
            if mapid == "484":
                self.mapdetail = "25人英雄"
            elif mapid == "483":
                self.mapdetail = "25人普通"
            elif mapid == "482":
                self.mapdetail = "10人普通"

        data = XiangZhiOverallData()

        for line in generator:
            data.numheal += line.data.numheal
            data.numeffheal += line.data.numeffheal
            data.numshield += line.data.numshield
            data.healTable.append([line.bossname.strip('"'), int(line.data.numeffheal / line.battleTime),
                                   line.data.healRate, line.data.myHealRank, line.data.numHealer,
                                   int(line.data.numabsorb / line.battleTime),
                                   line.data.numshield, line.battleTime, line.data.numshield / line.battleTime * 60])
            if data.mykey == "":
                data.mykey = line.data.mykey

        for line in generator:
            data.dpsTable.append([line.bossname.strip('"'), line.data.mydamage, line.data.myrank, line.data.equalDPS, len(line.data.durationDict)])
            if line.data.myrank < data.maxDpsRank or (line.data.myrank == data.maxDpsRank and line.data.mydamage > data.maxDps):
                data.maxDpsName = line.bossname.strip('"')
                data.maxDps = line.data.mydamage
                data.maxDpsRank = line.data.myrank
                data.maxDpsTable = line.data.damageList
                data.maxEqualDPS = line.data.equalDPS

        for line in generator:
            data.rateTable.append([line.bossname.strip('"'), line.data.overallrate])
            if line.data.overallrate > data.maxRate:
                data.maxRate = line.data.overallrate
                data.maxRateName = line.bossname.strip('"')
            data.overallrate += line.data.overallrate
        data.overallrate /= len(data.rateTable)

        sumTime = 0
        for line in generator:
            data.durationDict = plusDict(data.durationDict, line.data.durationDict)
            data.breakDict = plusDict(data.breakDict, line.data.breakDict)
            sumTime += line.battleTime

        data.rateList = dictToPairs(data.durationDict)
        data.breakList = dictToPairs(data.breakDict)

        namedict = {}
        occdict = {}
        for i in range(len(self.generator)):
            namedict = concatDict(namedict, self.generator[i].rawdata['9'][0])
            occdict = concatDict(occdict, self.generator[i].rawdata['10'][0])

        for i in range(len(data.rateList)):
            data.rateList[i].append(namedict[data.rateList[i][0]][0])
            data.rateList[i].append(occdict[data.rateList[i][0]][0])
            data.rateList[i][1] /= sumTime * 1000

        for i in range(len(data.breakList)):
            data.breakList[i].append(namedict[data.breakList[i][0]][0])
            data.breakList[i].append(occdict[data.breakList[i][0]][0])

        self.namedict = namedict
        self.occdict = occdict

        data.rateList.sort(key=lambda x: -x[1])
        data.breakList.sort(key=lambda x: -x[1])

        for line in data.rateList:
            data.bossRateDict[line[0]] = [0, 0, 0]

        for line in data.breakList:
            data.bossBreakDict[line[0]] = [0, 0, 0]

        for line in generator:
            if self.map == "范阳夜变":
                bossNameList = ["迟驻", "白某", "安小逢"]
            elif self.map == "敖龙岛":
                bossNameList = ["铁黎", "陈徽", "藤原武裔"]
            elif self.map == "达摩洞":
                bossNameList = ["宓桃", "哑头陀", "岳琳&岳琅"]
            else:
                bossNameList = ["宓桃", "哑头陀", "岳琳&岳琅"]
            for i in range(len(bossNameList)):
                if line.bossname == bossNameList[i]:
                    for line2 in line.data.durationDict:
                        data.bossRateDict[line2][i] = line.data.durationDict[line2] / (line.battleTime * 1000)
                    for line2 in line.data.breakDict:
                        data.bossBreakDict[line2][i] = line.data.breakDict[line2]

        data.maxSingleRate = data.rateList[0][1]
        data.maxSingleRateName = data.rateList[0][2].strip("")
        data.maxSingleBreak = data.breakList[0][1]
        data.maxSingleBreakName = data.breakList[0][2].strip("")
        
        if type(self.hardBOSS) != type("0"):
            num = len(self.hardBOSS)
            data.numpurge = [0] * num
            data.npchealstat = [{}] * num
            data.npcHealList = [[]] * num

        for line in generator:
            if line.bossname in ["源思弦", "安小逢", "宓桃", "哑头陀"]:
                if line.bossname == self.hardBOSS:
                    data.numpurge = line.data.numpurge
                    data.npchealstat = line.data.npchealstat
                    data.npcHealList = dictToPairs(data.npchealstat)
                    data.npcHealList.sort(key=lambda x: -x[1])
                    for i in range(len(data.npcHealList)):
                        data.npcHealList[i].append(namedict[data.npcHealList[i][0]][0])
                        data.npcHealList[i].append(occdict[data.npcHealList[i][0]][0])
                elif type(self.hardBOSS) != type("0"):
                    num = len(self.hardBOSS)
                    for i in range(num):
                        if line.bossname == self.hardBOSS[i]:
                            data.numpurge[i] = line.data.numpurge
                            data.npchealstat[i] = line.data.npchealstat
                            data.npcHealList[i] = dictToPairs(data.npchealstat[i])
                            data.npcHealList[i].sort(key=lambda x: -x[1])
                            for j in range(len(data.npcHealList[i])):
                                data.npcHealList[i][j].append(namedict[data.npcHealList[i][j][0]][0])
                                data.npcHealList[i][j].append(occdict[data.npcHealList[i][j][0]][0])
                                
        if type(data.numpurge) == type(int):
            findSelf = 0
            for line in data.npcHealList:
                if not findSelf:
                    data.npcRank += 1
                if line[0] == data.mykey and not findSelf:
                    data.npcHeal = line[1]
                    findSelf = 1
                data.npcSumHeal += line[1]
            data.npcHealRate = data.npcHeal / (data.npcSumHeal + 1e-10)
            data.npcHealNum = len(data.npcHealList)
        else:
            num = len(self.hardBOSS)
            data.npcRank = [0] * num
            data.npcHeal = [0] * num
            data.npcSumHeal = [0] * num
            data.npcHealRate = [0] * num
            data.npcHealNum = [0] * num
            for i in range(num):
                findSelf = 0
                for line in data.npcHealList[i]:
                    if not findSelf:
                        data.npcRank[i] += 1
                    if line[0] == data.mykey and not findSelf:
                        data.npcHeal[i] = line[1]
                        findSelf = 1
                    data.npcSumHeal[i] += line[1]
                data.npcHealRate[i] = data.npcHeal[i] / (data.npcSumHeal[i] + 1e-10)
                data.npcHealNum[i] = len(data.npcHealList[i])

        data.healDict = {}
        data.healList = []
        data.allBoss = []
        for i in range(len(generator)):
            line = generator[i]
            for name in line.data.healStat:
                if name not in data.healDict:
                    data.healDict[name] = [0] * len(generator)
                data.healDict[name][i] = int(line.data.healStat[name] / line.battleTime)
            data.allBoss.append(line.bossname)

        for id in data.healDict:
            line = [namedict[id][0].strip('"'), occdict[id][0]] + data.healDict[id]
            data.healList.append(line)

        for line in generator:
            data.sumBusyTime += line.data.sumBusyTime
            data.sumSpareTime += line.data.sumSpareTime
            data.spareRateList.append([line.bossname.strip('"'), line.data.spareRate])

        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)

        actorData = ActorData()
        for line in self.generator2:
            actorData.addActorData(line.data)

        self.data = data
        self.actorData = actorData
        self.sumHit = sum(self.actorData.hitCount[data.mykey].values())
        self.sumDeath = sum(self.actorData.deathCount[data.mykey])
        self.sumInner = sum(self.actorData.innerPlace[data.mykey])
        self.sumDrawer = self.actorData.drawer[data.mykey]

        self.score = XiangZhiScore(self.data, self.generator, self.generator2, data.mykey, self.map, self.mapdetail)
        self.score.analysisAll()

        self.scoreRate = None
        if self.score.available or self.map == "达摩洞":
            info, res = self.prepareUpload(upload=1)
            if res["num"] != 0:
                self.scoreRate = res["numOver"] / res["num"]
                info["scoreRate"] = self.scoreRate
            info["uploaded"] = 1
        else:
            info, res = self.prepareUpload(upload=0)
            info["uploaded"] = 0
        self.info = info

    def __init__(self, filelist, map, path, config, raw):
        self.myname = config.xiangzhiname
        self.mask = config.mask
        self.color = config.color
        self.text = config.text
        self.speed = config.speed
        self.public = config.xiangzhiPublic
        self.loadData(filelist, path, raw)
        self.map = map
        self.battledate = '-'.join(filelist[0][0].split('-')[0:3])


# Add by KEQX
def parseCmdArgs(argv):
    parser = argparse.ArgumentParser()

    # pause=0代表不暂停，pause=1代表结束后暂停，pause=2代表程序出错后暂停
    parser.add_argument('--pause', type=int, help='Should end up with system("pause").', default=1)
    parser.add_argument('--basepath', type=str, help='Set which file to analyse, separated by semicolon.', default='')
    parser.add_argument('--files', type=str, help='Set which file to analyse, separated by semicolon.', default='')
    return parser.parse_args(argv)
    
def replay_by_window():

    # Add by KEQX
    cmdArgs = parseCmdArgs(sys.argv[1:])
    exitCode = 0

    try:
        config = Config("config.ini")
        #resp = urllib.request.urlopen('http://139.199.102.41:8009/getAnnouncement')
        #res = json.load(resp)
        #print(res["announcement"])

        fileLookUp = FileLookUp()

        # Edit by KEQX
        # 优先级递降：
        if cmdArgs.basepath != "":
            print("指定基准目录，使用：%s" % cmdArgs.basepath)
            fileLookUp.basepath = cmdArgs.basepath
        else:
            fileLookUp.initFromConfig(config)

        # Add by KEQX
        if cmdArgs.files != '':
            if "/" in cmdArgs.files or "\\" in cmdArgs.files:
                raise Exception('--files参数是文件名而非路径，不应包含"/"或"\\"')
            fileLookUp.specifyFiles(cmdArgs.files.split(";"))

        filelist, allFilelist, map = fileLookUp.getLocalFile()
        print("开始分析。分析耗时可能较长，请耐心等待……")

        if config.actorActive and config.checkAll:
            raw = RawDataParser(allFilelist, fileLookUp.basepath).rawdata
        else:
            raw = RawDataParser(filelist, fileLookUp.basepath).rawdata

        print("分析数据完毕，开始制图。咕叽咕叽咕叽￣ω￣=")
        if config.xiangzhiActive:
            b = XiangZhiAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            b.analysis()
            b.paint("result.png")
            print("奶歌战斗复盘分析完成！结果保存在result.png中")
            if b.info["uploaded"]:
                print("可以通过以下链接来查看与分享：http://139.199.102.41:8009/XiangZhiData/png?key=%s" % b.info["hash"])
            exitCode |= 2  # 第2位设为1

        if config.actorActive:
            if config.checkAll:
                c = ActorAnalysis(allFilelist, map, fileLookUp.basepath, config, raw)
            else:
                c = ActorAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            c.analysis()
            c.paint("actor.png")
            print("演员战斗复盘分析完成！结果保存在actor.png中")
            exitCode |= 4  # 第3位设为1

    except Exception as e:
        traceback.print_exc()
        exitCode |= 1  # 错误的退出点

def replay():

    # Add by KEQX
    cmdArgs = parseCmdArgs(sys.argv[1:])
    exitCode = 0

    try:
        config = Config("config.ini")

        resp = urllib.request.urlopen('http://139.199.102.41:8009/getAnnouncement')
        res = json.load(resp)
        print(res["announcement"])

        fileLookUp = FileLookUp()

        # Edit by KEQX
        # 优先级递降：
        if cmdArgs.basepath != "":
            print("指定基准目录，使用：%s" % cmdArgs.basepath)
            fileLookUp.basepath = cmdArgs.basepath
        else:
            fileLookUp.initFromConfig(config)

        # Add by KEQX
        if cmdArgs.files != '':
            if "/" in cmdArgs.files or "\\" in cmdArgs.files:
                raise Exception('--files参数是文件名而非路径，不应包含"/"或"\\"')
            fileLookUp.specifyFiles(cmdArgs.files.split(";"))

        filelist, allFilelist, map = fileLookUp.getLocalFile()
        print("开始分析。分析耗时可能较长，请耐心等待……")

        if config.actorActive and config.checkAll:
            raw = RawDataParser(allFilelist, fileLookUp.basepath).rawdata
        else:
            raw = RawDataParser(filelist, fileLookUp.basepath).rawdata

        print("分析数据完毕，开始制图。咕叽咕叽咕叽￣ω￣=")
        if config.xiangzhiActive:
            b = XiangZhiAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            b.analysis()
            b.paint("result.png")
            print("奶歌战斗复盘分析完成！结果保存在result.png中")
            if b.info["uploaded"]:
                print("可以通过以下链接来查看与分享：http://139.199.102.41:8009/XiangZhiData/png?key=%s" % b.info["hash"])
            exitCode |= 2  # 第2位设为1

        if config.actorActive:
            if config.checkAll:
                c = ActorAnalysis(allFilelist, map, fileLookUp.basepath, config, raw)
            else:
                c = ActorAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            c.analysis()
            c.paint("actor.png")
            print("演员战斗复盘分析完成！结果保存在actor.png中")
            exitCode |= 4  # 第3位设为1

    except Exception as e:
        traceback.print_exc()
        exitCode |= 1  # 错误的退出点

    if cmdArgs.pause == 1 or (cmdArgs.pause == 2 and exitCode & 1):
        os.system('pause')

    sys.exit(exitCode)  # 程序返回值，用于外部调取
    
if __name__ == "__main__":
    replay()

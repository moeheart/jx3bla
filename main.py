import os
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import time
import winreg
import configparser
import traceback

edition = "3.2.0"

def parseLuatable(s, n, maxn):
    numLeft = 0
    nowi = n
    nowobj = {}
    nowkey = ""
    keystart = 0
    nowitem = ""
    nowitems = []
    nowquote = 0
    while True:
        #print(nowobj)
        c = s[nowi]
        if c == "[":
            if nowitems != []:
                nowobj[nowkey] = nowitems
                nowkey = ""
                nowitem = ""
                nowitems = []
            keystart = 1
        elif c == "{":
            #print(nowi)
            jdata, pn = parseLuatable(s, nowi + 1, maxn)
            nowitems.append(jdata)
            nowi = pn
        elif keystart == 1:
            if c == "]":
                keystart = 0
            else:
                nowkey += c
        elif keystart == 0:
            if c == '"':
                nowquote = (nowquote + 1) % 2
            if c == "," and nowquote != 1:
                if nowitem != "":
                    nowitems.append(nowitem)
                nowitem = ""
            elif c == "}":
                if nowitem != "":
                    nowitems.append(nowitem)
                nowobj[nowkey] = nowitems
                return nowobj, nowi
            elif c != '=':
                nowitem += c
        if c == "}":
            if nowitem != "":
                nowitems.append(nowitem)
            nowobj[nowkey] = nowitems
            return nowobj, nowi
        nowi += 1
        if nowi >= maxn:
            break
    nowobj[nowkey] = nowitems
    return nowobj, nowi


def dictToPairs(dict):
    pairs = []
    for key in dict:
        pairs.append([key, dict[key]])
    return pairs
    
def calculSpeed(speed, origin):
    tmp = int(speed / 188.309 * 10.24);
    y = int(origin*1024/(tmp+1024));
    return y
    
def parseTime(time):
    if time < 60:
        return "%ds"%time
    else:
        if time % 60 == 0:
            return "%dm"%(time/60)
        else:
            return "%dm%ds"%(time/60, time%60)
            
def parseCent(num, digit = 2):
    n = int(num * 10000)
    n1 = str(n // 100)
    n2 = str(n % 100)
    if len(n2) == 1:
        n2 = '0' + n2
    if digit == 2:
        return "%s.%s"%(n1, n2)
    else:
        return "%s"%n1
            
class BuffCounter():
    startTime = 0
    finalTime = 0
    buffid = 0
    log = []
    
    def setState(self, time, stack):
        self.log.append([int(time), int(stack)])
    
    def checkState(self, time):
        res = 0
        for i in range(1, len(self.log)):
            if int(time) < self.log[i][0]:
                res = self.log[i-1][1]
                break
        else:
            res = self.log[-1][1]
        return res
        
    def sumTime(self):
        time = 0
        for i in range(len(self.log)-1):
            time += self.log[i][1] * (self.log[i+1][0] - self.log[i][0])
        return time
    
    def __init__(self, buffid, startTime, finalTime):
        self.buffid = buffid
        self.startTime = startTime
        self.finalTime = finalTime
        self.log = [[startTime, 0]]
        

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
        while self.nowi + 1 < len(self.shieldLog) and self.shieldLog[self.nowi+1][0] < time:
            self.nowi += 1
        return self.shieldLog[self.nowi][1]
    
    def analysisShieldData(self):
        
        s = self.shieldLog
        
        newList = []
        for i in range(len(s)):
            if i > 0 and i + 1 < len(s) and s[i][1] == 0 and s[i+1][1] == 1 and s[i+1][0] - s[i][0] < 500:
                s[i][1] = 2
                s[i+1][1] = 2
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
            assert newList[i][1] != newList[i-1][1]
            self.shieldDuration[newList[i-1][1]] += newList[i][0] - newList[i-1][0]
            if newList[i][1] == 0:
                self.breakCount += 1
            if newList[i-1][1] == 1:
                self.shieldCount += 1
                
        if newList[-1][1] == 1:
            self.shieldCount += 1

        self.shieldDuration[newList[n-1][1]] += self.finalTime - newList[n-1][0]
        
    
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
            if line[1] in [14137, 14300]: #宫，变宫
                self.actLog.append([line[0] - self.getLength(24), self.getLength(24)])
            elif line[1] in [14140, 14301]: #徵，变徵
                self.actLog.append([line[0] - self.getLength(16), self.getLength(16)])
            else:
                self.actLog.append([line[0], self.getLength(24)])
                
        self.actLog.sort(key = lambda x: x[0])
        
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
                
    
    def __init__(self, skillLog, startTime, finalTime, speed = 3770):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed

class StatGeneratorBase():
    
    filename = ""
    rawdata = {}
    bossname = ""
    battleTime = 0
    
    def parseFile(self, path):
        if path == "":
            name = self.filename
        else:
            name = "%s\\%s"%(path, self.filename)
        print("读取文件：%s"%name)
        f = open(name, "r")
        s = f.read()
        res, _ = parseLuatable(s, 8, len(s))
        self.rawdata = res
        
        if '9' not in self.rawdata:
            if len(self.rawdata['']) == 17:
                for i in range(1, 17):
                    self.rawdata[str(i)] = [self.rawdata[''][i-1]]
            else:
                raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")
        
        self.bossname = self.filename.split('_')[1]
        self.battleTime = int(self.filename.split('_')[2].split('.')[0])
    
    def __init__(self, filename, path = "", rawdata = {}):
        if rawdata == {}:
            self.filename = filename
            self.parseFile(path)
        else:
            self.filename = filename
            self.rawdata = rawdata
            self.bossname = self.filename.split('_')[1]
            self.battleTime = int(self.filename.split('_')[2].split('.')[0])
            
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


    def __init__(self, filename, path = "", rawdata = {}, myname = ""):
        self.myname = myname
        super().__init__(filename, path, rawdata)
        
class ActorStatGenerator(StatGeneratorBase):
    yanyeID = {}
    yanyeThreshold = 0.04
    yanyeActive = 0
    wumianguiID = {}
    chizhuActive = 0
    chizhuID = ""
    baimouActive = 0
    baimouID = ""
    anxiaofengActive = 0
    anxiaofengID = 0
    fulingID = {}
    sideTargetID = {}
    guishouID = {}
    
    startTime = 0
    finalTime = 0
    playerIDList = {}
    
    actorSkillList = ["22520", #锈铁钩锁
                  "22521", #火轮重锤
                  "22203", #气吞八方
                  "22388", #岚吟
                  "22367", #禊祓·绀凌
                  "22356", #禊祓·绛岚
                  "22374", #零域
                  "22776", #双环掌击
                  "22246", #劈山尾鞭
                  "22272", #追魂扫尾
                  "22111", #巨力爪击
                  "23621", #隐雷鞭
                  "23700", #短歌式
                  ]
                  
    actorBuffList = ["16316", #离群之狐成就buff
                     "16842", #符咒禁锢buff
                  ]
                  
    bossNameDict = {"铁黎": 1,
                    "陈徽": 2,
                    "藤原武裔": 3,
                    "源思弦": 4,
                    "驺吾": 5,
                    "方有崖": 6
                    }
    
    def makeEmptyHitList(self):
        res = {}
        for i in self.actorSkillList:
            res["s" + i] = 0
        for i in self.actorBuffList:
            res["b" + i] = 0
        return res
        
    def checkFirst(self, key, data, occdict):
        if occdict[key][0] != '0' and key not in data.hitCount:
            data.hitCount[key] = self.makeEmptyHitList()
            data.hitCountP2[key] = self.makeEmptyHitList()
            data.deathCount[key] = [0, 0, 0, 0, 0, 0, 0]
            data.innerPlace[key] = [0, 0, 0, 0]
            data.drawer[key] = 0
        return data
        
    def firstStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        for line in sk:
            item = line[""]
            if item[3] == "1":
                if item[5] not in namedict:
                    continue
                    
                if occdict[item[5]][0] != '0':
                    self.playerIDList[item[5]] = 0
                    
                if namedict[item[5]][0] == '"厌夜"' and occdict[item[5]][0] == '0':
                    if item[5] not in self.yanyeID:
                        self.yanyeID[item[5]] = 0
                    if int(item[13]) > 0: 
                        self.yanyeActive = 1
                if item[4] in self.yanyeID:
                    if item[7] == "23635":
                        self.yanyeID[item[4]] = 1
                    elif item[7] == "23637":
                        self.yanyeID[item[4]] = 2
                        
                if namedict[item[5]][0] == '"无面鬼"' and occdict[item[5]][0] == '0':
                    self.wumianguiID[item[5]] = 0
                    
                if namedict[item[5]][0] == '"迟驻"' and occdict[item[5]][0] == '0':
                    self.chizhuActive = 1
                    self.chizhuID = item[5]
                    
                if namedict[item[5]][0] == '"白某"' and occdict[item[5]][0] == '0':
                    self.baimouActive = 1
                    self.baimouID = item[5]
                    
                if namedict[item[5]][0] == '"安小逢"' and occdict[item[5]][0] == '0':
                    self.anxiaofengActive = 1
                    self.anxiaofengID = item[5]
                
                if namedict[item[5]][0] in ['"少阴符灵"', '"少阳符灵"'] and occdict[item[5]][0] == '0':
                    self.fulingID[item[5]] = 1
                    
                if namedict[item[5]][0] in ['"狼牙斧卫"', '"水鬼"'] and occdict[item[5]][0] == '0':
                    self.sideTargetID[item[5]] = 1
                    
                if namedict[item[5]][0] in ['"鬼首"'] and occdict[item[5]][0] == '0':
                    self.guishouID[item[5]] = 1
                    

    def secondStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        skilldict = res['11'][0]
        sk = res['16'][0][""]
        
        data = ActorData()

        num = 0
        skillLog = []
        
        no5P2 = 0
        
        lastHit = {}
        
        self.potList = []
        
        deathHit = {}

        deathBuffDict = {"9299": 30000, #杯水留影
                         "16981": 30000, #翩然
                         "17128": 5000, #阴阳逆乱}
                         "16892": 36000, #应援
                         "17301": 16000, #不听话的小孩子
                         }
        deathBuff = {}
        
        rateStandard = {"0": 0,
                        "1": 0.85,
                        "2": 0.9,
                        "3": 0.85,
                        "4": 0.85,
                        "5": 0.8,
                        "6": 0.85,
                        "7": 0.95,
                        "8": 0.9,
                        "9": 0.95,
                        "10": 0.9,
                        "21": 0.95,
                        "22": 0.9,
                        "23": 0.9,
                        "24": 0.85,
                        "25": 0.95}
        
        yanyeActive = self.yanyeActive
        if yanyeActive:
            yanyeHP = [0, 261440000, 261440000]
            yanyeMaxHP = 261440000
            yanyeDPS = {}
            rushDPS = {}
            rushTmpDPS = {}
            paneltyDPS = {}
            wasteDPS = {}
            yanyeResult = {}
            rush = 1
            wumianguiLabel = 0
            
        chizhuActive = self.chizhuActive
        if chizhuActive:
            chizhuBuff = ["16909", "16807", "16824", "17075"]
            self.buffCount = {}
            self.dps = {}
            for line in self.playerIDList:
                self.buffCount[line] = {}
                for id in chizhuBuff:
                    self.buffCount[line][id] = BuffCounter(id, self.startTime, self.finalTime)
                self.dps[line] = [0, 0]
                
        baimouActive = self.baimouActive
        if baimouActive:
            self.breakBoatCount = {}
            self.dps = {}
            for line in self.playerIDList:
                self.breakBoatCount[line] = {}
                self.breakBoatCount[line] = BuffCounter("16841", self.startTime, self.finalTime)
                self.dps[line] = [0, 0, 0]
            mingFuHistory = {}
            
        anxiaofengActive = self.anxiaofengActive
        if anxiaofengActive:
            self.dps = {}
            self.catchCount = {}
            self.rumo = {}
            self.xuelian = {}
            for line in self.playerIDList:
                self.dps[line] = [0, 0, 0, 0, 0, 0]
                self.catchCount[line] = 0
                self.rumo[line] = BuffCounter("16796", self.startTime, self.finalTime)
                self.xuelian[line] = []
            P3 = 0
            P3TimeStamp = 0
            sideTime = 0
            guishouTime = 0
            xuelianStamp = 0
            xuelianTime = 0
            xuelianCount = 0
        
        #print(self.yanyeID)
        #print(self.wumianguiID)
        #print(yanyeActive)

        for line in sk:
            item = line[""]
            if self.startTime == 0:
                self.startTime = int(item[2])
            self.finalTime = int(item[2])
            
            if item[3] == '1': #技能
                    
                #群24105 单24144
            
                if occdict[item[5]][0] != '0':
                    data = self.checkFirst(item[5], data, occdict)
                    if item[7] in self.actorSkillList and int(item[10]) != 2:
                        if item[7] == "22520": #锈铁钩锁
                            if item[5] not in lastHit or int(item[2]) - lastHit[item[5]] > 10000: #10秒缓冲时间
                                lastHit[item[5]] = int(item[2])
                            else:
                                continue
                        data.hitCount[item[5]]["s" + item[7]] += 1
                        if no5P2:
                            data.hitCountP2[item[5]]["s" + item[7]] += 1
                            
                    if item[7] == "23092": #震怒咆哮
                        no5P2 = 1
                        
                    if item[13] != item[14]:
                        deathHit[item[5]] = [int(item[2]), skilldict[item[9]][0][""][0].strip('"'), int(item[13])]
                    
                    if anxiaofengActive:
                        hasRumo = self.rumo[item[5]].checkState(int(item[2]))
                        if hasRumo and occdict[item[4]][0] != '0':
                            self.dps[item[4]][5] += int(item[12])
                        
                        if item[7] in ["24105", "24144"]:
                            if int(item[2]) - xuelianStamp > 10000:
                                if xuelianTime > 0:
                                    for line in self.xuelian:
                                        while len(self.xuelian[line]) < xuelianTime:
                                            self.xuelian[line].append(0)
                                xuelianTime += 1
                                xuelianCount = 1
                            elif int(item[2]) - xuelianStamp > 500:
                                xuelianCount += 1
                            if len(self.xuelian[item[5]]) == xuelianTime - 1:
                                if item[7] == "24105":
                                    self.xuelian[item[5]].append(xuelianCount)
                                else:
                                    self.xuelian[item[5]].append(-1)
                            xuelianStamp = int(item[2])
                        
                        
                else:
                    
                    if yanyeActive:
                        if item[5] in self.yanyeID:
                            yanyeLabel = self.yanyeID[item[5]]
                            yanyeHP[yanyeLabel] -= int(item[14])
                            if rush == 2:
                                if item[4] not in rushTmpDPS:
                                    rushTmpDPS[item[4]] = [0, 0, 0]
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                rushTmpDPS[item[4]][yanyeLabel] += int(item[14])
                            elif rush == 1:
                                if item[4] not in rushDPS:
                                    rushDPS[item[4]] = 0
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                rushDPS[item[4]] += int(item[14])
                            else:
                                if item[4] not in yanyeDPS:
                                    yanyeDPS[item[4]] = [0, 0, 0]
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                yanyeDPS[item[4]][yanyeLabel] += int(item[14])
                                if yanyeHP[yanyeLabel] < yanyeHP[3-yanyeLabel] - 0.04 * yanyeMaxHP:
                                    if item[4] not in paneltyDPS:
                                        paneltyDPS[item[4]] = 0
                                        yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                    paneltyDPS[item[4]] += int(item[14])
                        if item[5] in self.wumianguiID:
                            if item[4] not in rushDPS:
                                rushDPS[item[4]] = 0
                                yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                            rushDPS[item[4]] += int(item[14])
                            yanyeHP[wumianguiLabel] -= int(item[14])
                    
                    if chizhuActive:
                        if item[5] == self.chizhuID and item[4] in self.buffCount:
                            self.dps[item[4]][0] += int(item[14])
                            self.dps[item[4]][1] += int(item[14])
                            #kanpo = self.buffCount[item[4]]["17075"].checkState(int(item[2]))
                            #if kanpo < 6:
                            #    self.dps[item[4]][1] += int(item[14]) / (1 - 0.15 * kanpo)
                                
                    if baimouActive:
                        if item[5] == self.baimouID and item[4] in self.breakBoatCount:
                            self.dps[item[4]][0] += int(item[14])
                        if item[5] in self.fulingID and item[4] in self.breakBoatCount:
                            self.dps[item[4]][1] += int(item[14])
                        if item[5] in namedict and item[4] in self.breakBoatCount and namedict[item[5]][0] == '"水牢"':
                            self.dps[item[4]][2] += int(item[14])
                            
                    if anxiaofengActive:
                        if item[4] in self.playerIDList:
                            self.dps[item[4]][0] += int(item[14])
                        if item[5] == self.anxiaofengID and item[4] in self.playerIDList:
                            self.dps[item[4]][1] += int(item[14])
                        if item[5] in self.sideTargetID and item[4] in self.playerIDList:
                            self.dps[item[4]][2] += int(item[14])
                        if item[5] in self.guishouID and item[4] in self.playerIDList:
                            self.dps[item[4]][3] += int(item[14])
                        if P3 and item[4] in self.playerIDList:
                            self.dps[item[4]][4] += int(item[14])
                              
            elif item[3] == '5': #气劲
            
                if occdict[item[5]][0] == '0':
                    continue
                data = self.checkFirst(item[5], data, occdict)
                if item[6] == "15868": #老六内场buff
                    data.innerPlace[item[5]][int(item[7])-1] = 1
                if item[6] == "15419": #老五吃球buff
                    if item[9] == "false" and item[10] == '1':
                        data.drawer[item[5]] += 1
                if item[6] in self.actorBuffList and int(item[10]) == 1:
                    if item[5] not in data.hitCount:
                        data.hitCount[item[5]] = self.makeEmptyHitList()
                    data.hitCount[item[5]]["b" + item[6]] += 1
                    
                if item[6] in deathBuffDict:
                    if item[5] not in deathBuff:
                        deathBuff[item[5]] = {}
                    deathBuff[item[5]][item[6]] = [int(item[2]), skilldict[item[8]][0][""][0].strip('"'), deathBuffDict[item[6]]]
                
                if yanyeActive:
                    if item[6] == "16913": #厌夜威压buff     
                        halfHP = (yanyeHP[1] + yanyeHP[2]) / 2
                        yanyeHP[1] = halfHP
                        yanyeHP[2] = halfHP
                        rush = 0
                        wumianguiLabel = 0
                        
                if chizhuActive:
                    if item[6] in chizhuBuff:
                        self.buffCount[item[5]][item[6]].setState(int(item[2]), int(item[10]))
                        
                if baimouActive:
                    if item[6] == "16841":
                        self.breakBoatCount[item[5]].setState(int(item[2]), int(item[10]))
                    if item[6] in ["16818", "16819", "16816", "16817"]:
                        mingFuHistory[item[5]] = item[6]
                    if item[6] == "16842" and item[10] == '1':
                        if item[5] in mingFuHistory:
                            lockReason = ["命符·生", "命符·死", "命符·阴", "命符·阳"][int(mingFuHistory[item[5]]) - 16816] + "站错"
                        else:
                            lockReason = "未知原因"
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occdict[item[5]][0],
                                             self.bossname,
                                             "%s由于 %s 被锁"%(lockTime, lockReason)])
                                             
                if anxiaofengActive: 
                    if item[6] == "16796": #走火入魔
                        #print(item)
                        self.rumo[item[5]].setState(int(item[2]), int(item[10]))
                    if item[6] == "16892" and item[10] == '1': #应援
                        self.catchCount[item[5]] += 34.9
                    if item[6] == "16795" and item[10] == '1': #安小逢的凝视
                        self.catchCount[item[5]] += 19.9
                    if item[6] == "17110" and item[10] == '1':
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occdict[item[5]][0],
                                             self.bossname,
                                             "%s触发P1惩罚"%lockTime])
                    if item[6] == "17301" and item[10] == '1':
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occdict[item[5]][0],
                                             self.bossname,
                                             "%s触发P2惩罚"%lockTime])
                        
            elif item[3] == '3': #重伤记录
                if item[4] not in occdict or occdict[item[4]][0] == '0':
                    continue
                    
                #if item[4] in namedict and namedict[item[4]][0] == '"一叶修罗一"':
                #    print(item)
                    
                data = self.checkFirst(item[4], data, occdict)
                if item[4] in occdict and int(occdict[item[4]][0]) != 0:
                    if self.bossname in self.bossNameDict:
                        data.deathCount[item[4]][self.bossNameDict[self.bossname]] += 1
                    
                    deathTime = parseTime((int(item[2]) - self.startTime) / 1000)
                    
                    deathSource = "未知"
                    if item[4] in deathHit and abs(deathHit[item[4]][0] - int(item[2])) < 1000:
                        deathSource = "%s(%d)"%(deathHit[item[4]][1], deathHit[item[4]][2])
                    elif item[4] in deathBuff:
                        for line in deathBuff[item[4]]:
                            if deathBuff[item[4]][line][0] + deathBuff[item[4]][line][2] > int(item[2]):
                                deathSource = deathBuff[item[4]][line][1]
                    
                    if deathSource == "翩然":
                        deathSource = "推测为摔死"
                
                    self.potList.append([namedict[item[4]][0],
                                         occdict[item[4]][0],
                                         self.bossname,
                                         "%s重伤，来源：%s"%(deathTime, deathSource)])
                                         
                                     
                        
            elif item[3] == '8': #喊话
                #print(item)
                if len(item) < 5:
                    continue
                if yanyeActive:
                    if item[4] in ['"吱吱叽！！！"', '"咯咯咕！！！"', "……锋刃可弃身。"]:
                        rush = 2
                        rushTmpDPS = {}
                    if item[4] in ['"呜啊……！"']:
                        if rush == 2:
                            if yanyeHP[1] < yanyeHP[2]:
                                wumianguiLabel = 1
                            else:
                                wumianguiLabel = 2
                            for line in rushTmpDPS:
                                if line not in rushDPS:
                                    rushDPS[line] = 0
                                    yanyeResult[line] = [0, 0, 0, 0, 0, 0]
                                if line not in wasteDPS:
                                    wasteDPS[line] = 0
                                    yanyeResult[line] = [0, 0, 0, 0, 0, 0]
                                rushDPS[line] += rushTmpDPS[line][wumianguiLabel]
                                wasteDPS[line] += rushTmpDPS[line][3 - wumianguiLabel]
                            rushTmpDPS = {}
                        rush = 1
                if anxiaofengActive:
                    if item[4] in ['"你们全都要死！"']:
                        P3 = 1
                        P3TimeStamp = int(item[2])
                        
                    if item[4] in ['"永远忠诚的部下们到达了！"']:
                        sideTime += 35
                    if '"来陪人家玩儿嘛~"' in item[4]:
                        sideTime += 20
                    if item[4] in ['"哼哼哼哼……"']:
                        sideTime += 20
                        guishouTime += 20
                    pass

            num += 1
            
        yanyeResultList = []
        
        effectiveDPSList = []
        
        if yanyeActive:
            for line in yanyeDPS:
                yanyeResult[line][0] = int(yanyeDPS[line][1] / self.battleTime)
                yanyeResult[line][1] = int(yanyeDPS[line][2] / self.battleTime)
            for line in rushDPS:
                yanyeResult[line][2] = int(rushDPS[line] / self.battleTime)
            for line in wasteDPS:
                yanyeResult[line][3] = int(wasteDPS[line] / self.battleTime)
            for line in paneltyDPS:
                yanyeResult[line][4] = int(paneltyDPS[line] / self.battleTime)
            for line in yanyeResult:
                if yanyeResult[line][0] + yanyeResult[line][1] + yanyeResult[line][2] - yanyeResult[line][4] > 10000:
                    yanyeResultList.append([namedict[line][0]] + [occdict[line][0]] + [yanyeResult[line][0] + yanyeResult[line][1] + yanyeResult[line][2] - yanyeResult[line][4]] + yanyeResult[line])
            
            yanyeResultList.sort(key = lambda x:-x[2])
            
            sumDPS = 0
            for line in yanyeResultList:
                sumDPS += line[2]
            averageDPS = sumDPS / len(yanyeResultList)
            
            effectiveDPSList = yanyeResultList
            
            self.yanyeResult = yanyeResultList
            
            #print(yanyeResultList)
            
        if chizhuActive:
            chizhuResult = []
            for line in self.buffCount:
                disableTime = 0
                for id in ["16909", "16807", "16824"]:
                    res = self.buffCount[line][id].sumTime()
                    disableTime += res
                wushiTime = self.buffCount[line]["17075"].sumTime()
                baseTime = self.battleTime - disableTime / 1000
                if self.dps[line][1] / baseTime > 10000:
                    chizhuResult.append([namedict[line][0], 
                                         occdict[line][0],
                                         self.dps[line][1] / baseTime,
                                         disableTime / 1000,
                                         wushiTime / 1000,
                                         self.dps[line][0] / self.battleTime])
                                     
            chizhuResult.sort(key = lambda x:-x[2])                   
            #print(chizhuResult)
            
            sumDPS = 0
            for line in chizhuResult:
                sumDPS += line[2]
            averageDPS = sumDPS / len(chizhuResult)
            
            effectiveDPSList = chizhuResult
            
            self.chizhuResult = chizhuResult
            
        if baimouActive:
            baimouResult = []
            for line in self.breakBoatCount:
                disableTime = self.breakBoatCount[line].sumTime()
                baseTime = self.battleTime - disableTime / 1000
                effectiveDPS = (self.dps[line][0] + self.dps[line][1]) / baseTime
                originDPS = (self.dps[line][0] + self.dps[line][1] + self.dps[line][2]) / self.battleTime
                if effectiveDPS > 10000:
                    baimouResult.append([namedict[line][0],
                                         occdict[line][0],
                                         effectiveDPS,
                                         self.dps[line][0] / (baseTime - 170.5),
                                         self.dps[line][1] / 170.5,
                                         self.dps[line][2] / self.battleTime,
                                         originDPS,
                                         disableTime / 1000])
                                         
            baimouResult.sort(key = lambda x:-x[2]) 
            #print(baimouResult)
            
            sumDPS = 0
            for line in baimouResult:
                sumDPS += line[2]
            averageDPS = sumDPS / len(baimouResult)
            
            effectiveDPSList = baimouResult
            
            self.baimouResult = baimouResult
            
        if anxiaofengActive:
            for line in self.xuelian:
                while len(self.xuelian[line]) < xuelianTime:
                    self.xuelian[line].append(0)
            anxiaofengResult = []
            for line in self.playerIDList:
                disableTime = self.catchCount[line]
                P3Time = (self.finalTime - P3TimeStamp) / 1000
                originDPS = self.dps[line][0] / self.battleTime
                bossDPS = self.dps[line][1] / self.battleTime
                sideDPS = self.dps[line][2] / (sideTime - disableTime)
                guishouDPS = self.dps[line][3] / guishouTime
                P3DPS = self.dps[line][4] / P3Time
                rumoHeal = self.dps[line][5]
                xuelianStr = ""
                for ch in self.xuelian[line]:
                    if ch == -1:
                        xuelianStr += 'X'
                    else:
                        xuelianStr += str(ch)
                anxiaofengResult.append([namedict[line][0],
                                         occdict[line][0],
                                         originDPS,
                                         bossDPS,
                                         sideDPS,
                                         guishouDPS,
                                         P3DPS,
                                         rumoHeal,
                                         xuelianStr
                                         ])
                                         
            #print(anxiaofengResult)   
            anxiaofengResult.sort(key = lambda x:-x[2]) 
            self.anxiaofengResult = anxiaofengResult
            
        
        for line in effectiveDPSList:
            occ = str(line[1])
            rate = rateStandard[occ]
            lineRate = line[2] / averageDPS
            if lineRate < rate:
                self.potList.append([line[0],
                                     line[1],
                                     self.bossname,
                                     "有效DPS未到及格线(%s%%/%s%%)"%(parseCent(lineRate, 0), parseCent(rate, 0))])
                                     
        self.data = data
        
    def __init__(self, filename, path = "", rawdata = {}, myname = ""):
        self.myname = myname
        super().__init__(filename, path, rawdata)
        self.no1Hit = {}
        

class XiangZhiStatGenerator(StatGeneratorBase):
    
    myname = ""
    mykey = ""
    npckey = ""
    startTime = 0
    finalTime = 0
    speed = 3770
    shieldCounters = {}
    rumo = {}
    
    def secondStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        data = XiangZhiData()
        
        data.mykey = self.mykey

        num = 0
        skillLog = []

        for line in sk:
            item = line[""]
            
            if item[3] == "1":
                
                if item[4] == self.mykey and item[11] != '0':
                    if item[10] != '7':
                        data.numheal += int(item[11])
                        data.numeffheal += int(item[12])
                    else:
                        data.numabsorb += int(item[12])
                    
                if int(item[12]) > 0 and item[10] != "7":
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
                
                        
                
                if self.npckey != 0 and item[12] != '0':
                    if item[5] in self.rumo and self.rumo[item[5]].checkState(int(item[2])):
                        print(item)
                        if item[4] not in data.npchealstat:
                            data.npchealstat[item[4]] = int(item[12])
                        else:
                            data.npchealstat[item[4]] += int(item[12])
                            
                #if item[7] == "14231": #梅花三弄
                #    data.numshield += 1

                if item[7] == "14169": #一指回鸾
                    data.numpurge += 1

                if int(item[14]) > 0:
                    if item[4] in self.shieldCounters:
                        if item[4] not in data.battlestat:
                            data.battlestat[item[4]] = [0, 0, 0]
                        if int(item[7]) >= 21827 and int(item[7]) <= 21831: #桑柔
                            data.battlestat[item[4]][2] += int(item[14])
                        else:
                            hasShield = self.shieldCounters[item[4]].checkTime(int(item[2]))
                            data.battlestat[item[4]][hasShield] += int(item[14])
                            
            if item[3] == "5":
                if item[6] == "16796":
                    if item[5] not in self.rumo:
                        self.rumo[item[5]] = BuffCounter("16796", self.startTime, self.finalTime)
                    self.rumo[item[5]].setState(int(item[2]), int(item[10]))

            num += 1
        
        skillCounter = SkillCounter(skillLog, self.startTime, self.finalTime, self.speed)
        skillCounter.analysisSkillData()
        data.sumBusyTime = skillCounter.sumBusyTime
        data.sumSpareTime = skillCounter.sumSpareTime
        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)

            
        numdam = 0
        for key in data.battlestat:
            if int(occdict[key][0]) == 0:
                continue
            line = data.battlestat[key]
            data.damageDict[key] = line[0] + line[1] / 1.139
            numdam += line[1] / 1.139 * 0.139 + line[2]
        
        if self.mykey not in data.damageDict:
            data.damageDict[self.mykey] = numdam
        else:
            data.damageDict[self.mykey] += numdam
            
        data.damageList = dictToPairs(data.damageDict)
        data.damageList.sort(key = lambda x: -x[1])
        
        for i in range(len(data.damageList)):
            data.damageList[i].append(namedict[data.damageList[i][0]][0])
            data.damageList[i].append(occdict[data.damageList[i][0]][0])

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
        data.healList.sort(key = lambda x: -x[1])
        
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
        
        for key in namedict:
            if namedict[key][0] == '"尹青羲"':
                self.npckey = key
                break
            if namedict[key][0] == '"安小逢"':
                self.npckey = key
                break

        MoWenList = []
        XiangZhiList = []
        
        shieldLogDict = {}
                    
        for line in sk:
            item = line[""]
            if self.startTime == 0:
                self.startTime = int(item[2])
            self.finalTime = int(item[2])
                
            if item[3] == "1":
                if item[4] not in MoWenList and item[7] in ["14067", "14298", "14302"]:
                    MoWenList.append(item[4])
                if item[4] not in XiangZhiList and item[7] in ["14231", "14140", "14301"]:
                    XiangZhiList.append(item[4])
                if item[7] == "14231":
                    if item[5] not in shieldLogDict:
                        shieldLogDict[item[5]] = [[int(item[2]), 1]]
                    else:
                        shieldLogDict[item[5]].append([int(item[2]), 1])
                    
            if item[3] == "5":
                if item[6] in ["9334", "16911"]: #buff梅花三弄
                    if item[5] not in shieldLogDict:
                        shieldLogDict[item[5]] = [[int(item[2]), int(item[10])]]
                    else:
                        shieldLogDict[item[5]].append([int(item[2]), int(item[10])])
        
        if self.myname == "":
            if len(XiangZhiList) >= 2:
                nameList = []
                for line in XiangZhiList:
                    nameList.append(namedict[line][0])
                s = str(nameList)
                raise Exception('奶歌的数量不止一个，请手动指示ID。可能的ID为：%s'%s)
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
            
    def __init__(self, filename, myname, path = "", rawdata = {}):
        self.myname = myname
        super().__init__(filename, path, rawdata)
        #self.filename = filename
        #self.parseFile(path)
            
def plusList(a1, a2):
    a = []
    assert len(a1) == len(a2)
    for i in range(len(a1)):
        a.append(a1[i] + a2[i])
    return a

def plusDict(d1, d2):
    d = {}
    for key in d1:
        d[key] = d1[key]
    for key in d2:
        if key in d1:
            d[key] += d2[key]
        else:
            d[key] = d2[key]
    return d
    
def concatDict(d1, d2):
    d = {}
    for key in d1:
        d[key] = d1[key]
    for key in d2:
        if key not in d:
            d[key] = d2[key]
    return d
    
class ActorData():

    def addActorData(self, a2):
        for line in a2.deathCount:
            if line not in self.deathCount:
                self.deathCount[line] = a2.deathCount[line]
            else:
                self.deathCount[line] = plusList(self.deathCount[line], a2.deathCount[line])
        
        for line in a2.hitCount:
            if line not in self.hitCount:
                self.hitCount[line] = a2.hitCount[line]
            else:
                self.hitCount[line] = plusDict(self.hitCount[line], a2.hitCount[line])
        
        for line in a2.hitCountP2:
            if line not in self.hitCountP2:
                self.hitCountP2[line] = a2.hitCountP2[line]
            else:
                self.hitCountP2[line] = plusDict(self.hitCountP2[line], a2.hitCountP2[line])
                
        for line in a2.innerPlace:
            if line not in self.innerPlace:
                self.innerPlace[line] = a2.innerPlace[line]
            else:
                self.innerPlace[line] = plusList(self.innerPlace[line], a2.innerPlace[line])
                
        for line in a2.drawer:
            if line not in self.drawer:
                self.drawer[line] = a2.drawer[line]
            else:
                self.drawer[line] += a2.drawer[line]
                
    def __init__(self):
        self.deathCount = {}
        self.hitCount = {}
        self.hitCountP2 = {}
        self.innerPlace = {}
        self.drawer = {}

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

    bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
    bossDictR = ["", "铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
    rateScale = [[100, 0, "A+", "不畏浮云遮望眼，只缘身在最高层。"],
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
    map = "敖龙岛"

    def scaleScore(self, x, scale):
        N = len(scale)
        assert N >= 2
        score = 0
        if scale[0][0] > scale[1][0]:
            x = -x
            for i in range(N):
                scale[i][0] = -scale[i][0]
        for i in range(0, N-1):
            assert scale[i][0] < scale[i+1][0]
        
        if x < scale[0][0]:
            score = scale[0][1]
        else:
            for i in range(0, N-1):
                if x >= scale[i][0] and x < scale[i+1][0]:
                    score = scale[i][1] + (x - scale[i][0]) / (scale[i+1][0] - scale[i][0] + 1e-10) * (scale[i+1][1] - scale[i][1])
                    break
            else:
                score = scale[N-1][1]
        return score
    
    def analysisHPS(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                HPSList = [[2000,0], [12000,5]]
            elif id == 2:
                HPSList = [[2000,0], [10000,5]]
            elif id == 3:
                return 0
            elif id == 4:
                HPSList = [[1000,0], [5000,3], [8000,5]]
            elif id == 5:
                HPSList = [[500,0], [1500,2], [2500,3], [5000,5]]
            elif id == 6:
                HPSList = [[500,0], [1500,4], [3000,7]]
        elif self.map == "范阳夜变":
            if id == 1:
                return 0
            elif id == 2:
                return 0
            elif id == 3:
                HPSList = [[500,0], [1000,2], [2500,5]]
            elif id == 4:
                HPSList = [[500,0], [1000,2], [3000,5]]
            elif id == 5:
                HPSList = [[500,0], [1000,1], [3000,5]]
        score = self.scaleScore(self.data.healTable[id-1][1], HPSList)
        return score
        
    def analysisShield(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                ShieldList = [[10,0], [16,3], [24,5]]
            elif id == 2:
                ShieldList = [[12,0], [18,3], [28,5]]
            elif id == 3:
                return 0
            elif id == 4:
                ShieldList = [[6,0], [10,3], [16,5]]
            elif id == 5:
                ShieldList = [[3,0], [10,1], [25,5]]
            elif id == 6:
                ShieldList = [[1,0], [5,1], [13,4], [20,7]]
        elif self.map == "范阳夜变":
            if id == 1:
                return 0
            elif id == 2:
                return 0
            elif id == 3:
                ShieldList = [[10,0], [18,2], [25,5]]
            elif id == 4:
                ShieldList = [[10,0], [15,2], [22,5]]
            elif id == 5:
                ShieldList = [[5,0], [10,2], [15,5]]
        score = self.scaleScore(self.data.healTable[id-1][8], ShieldList)
        return score
        
    def analysisDPS(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                DPSList = [[0.8,0], [1.4,5]]
            elif id == 2:
                DPSList = [[0.5,0], [1.2,5]]
            elif id == 3:
                DPSList = [[0.5,0], [2,10]]
            elif id == 4:
                DPSList = [[0.3,0], [1,5]]
            elif id == 5:
                DPSList = [[0.3,0], [0.8,2], [1.3,5]]
            elif id == 6:
                DPSList = [[0.3,0], [0.8,2], [1.4,7]]
        elif self.map == "范阳夜变":
            if id == 1:
                DPSList = [[1.0,0], [1.6,5], [2.3,15]]
            elif id == 2:
                DPSList = [[1.0,0], [1.65,5], [2.35,15]]
            elif id == 3:
                DPSList = [[0.5,0], [0.8,2], [1.5,10]]
            elif id == 4:
                DPSList = [[0.7,0], [1.0,2], [1.7,10]]
            elif id == 5:
                DPSList = [[0.5,0], [0.8,1], [1.5,5]]
        score = self.scaleScore(self.data.dpsTable[id-1][3], DPSList)
        return score
        
        
    def analysisRate(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                RateList = [[0.1,0], [0.3,1], [0.5,5]]
            elif id == 2:
                RateList = [[0.1,0], [0.25,1], [0.45,5]]
            elif id == 3:
                RateList = [[0.1,0], [0.5,1], [0.8,10]]
            elif id == 4:
                RateList = [[0.1,0], [0.2,1], [0.5,5]]
            elif id == 5:
                RateList = [[0.1,0], [0.2,1], [0.6,5]]
            elif id == 6:
                RateList = [[0.1,0], [0.2,1], [0.6,7]]
        elif self.map == "范阳夜变":
            if id == 1:
                RateList = [[0.1,0], [0.7,3], [0.95,15]]
            elif id == 2:
                RateList = [[0.1,0], [0.7,3], [0.95,15]]
            elif id == 3:
                RateList = [[0.1,0], [0.25,2], [0.55,10]]
            elif id == 4:
                RateList = [[0.1,0], [0.3,2], [0.6,10]]
            elif id == 5:
                RateList = [[0.1,0], [0.2,1], [0.5,5]]
        score = self.scaleScore(self.data.rateTable[id-1][1], RateList)
        return score
    
    def analysisSpare(self, id):
        if self.map == "敖龙岛":
            if id == 1:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 2:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 3:
                RateList = [[0.5,0], [0.1,5]]
            elif id == 4:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 5:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 6:
                RateList = [[0.5,0], [0.1,7]]
        elif self.map == "范阳夜变":
            if id == 1:
                RateList = [[0.5,0], [0.3,3], [0.2,5]]
            elif id == 2:
                RateList = [[0.5,0], [0.2,3], [0.1,5]]
            elif id == 3:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 4:
                RateList = [[0.3,0], [0.1,5]]
            elif id == 5:
                RateList = [[0.5,0], [0.1,5]]
        score = self.scaleScore(self.data.spareRateList[id-1][1], RateList)
        return score
        
    def analysisPurge(self, id):
        PurgeList = [[0,0], [3,3], [10,5]]
        score = self.scaleScore(self.generator[id-1].data.numpurge, PurgeList)
        return score
    
    def analysisNPC(self, id):
        if self.map == "敖龙岛":
            NPCList = [[0.15,0], [0.3,5]]
        elif self.map == "范阳夜变":
            NPCList = [[0.1,0], [0.2,5]]
        score = self.scaleScore(self.data.npcHealRate, NPCList)
        return score
        
    def analysisInner(self, id):
        InnerList = [[0,0], [1,3], [2,5]]
        score = self.scaleScore(sum(self.generator2[id-1].data.innerPlace[self.mykey]), InnerList)
        return score
        
    def analysisDrawer(self, id):
        InnerList = [[0,0], [4,4]]
        score = self.scaleScore(self.generator2[id-1].data.drawer[self.mykey], InnerList)
        return score
    
    def analysisBOSSald(self, id):
        cutOff1 = [0, 5, 5, 0, 5, 5, 7]
        cutOff2 = [0, 5, 5, 10, 5, 5, 7]
        cutOff4 = [0, 0, 0, 0, 5, 0, 5]
        cutOff0 = [0, 15, 15, 15, 20, 15, 20]
        self.printTable.append([0, "%s 打分表"%self.bossDictR[id], ""])
        c1 = 0
        c5 = 0
        if id != 3:
            s1 = self.analysisHPS(id)
            self.printTable.append([1, "治疗量", "%.1f"%s1])
            s2 = self.analysisShield(id)
            self.printTable.append([1, "盾数", "%.1f"%s2])
            c1 = s1 + s2
            if c1 > cutOff1[id]:
                c1 = cutOff1[id]
                c5 += (s1 + s2 - cutOff1[id]) / 2
        s3 = self.analysisDPS(id)
        self.printTable.append([1, "等效DPS", "%.1f"%s3])
        s4 = self.analysisRate(id)
        self.printTable.append([1, "覆盖率", "%.1f"%s4])
        c2 = s3 + s4
        if c2 > cutOff2[id]:
            c2 = cutOff2[id]
            c5 += (s3 + s4 - cutOff2[id]) / 2
        s5 = self.analysisSpare(id)
        self.printTable.append([1, "空闲比例", "%.1f"%s5])
        c3 = s5
        
        c4 = 0
        if id == 4:
            s6 = self.analysisPurge(id)
            self.printTable.append([1, "驱散次数", "%.1f"%s6])
            s7 = self.analysisNPC(id)
            self.printTable.append([1, "NPC承疗", "%.1f"%s7])
            c4 = s6 + s7
            if c4 > cutOff4[id]:
                c4 = cutOff4[id]
                c5 += (s6 + s7) / 2
        elif id == 5:
            s6 = self.analysisDrawer(id)
            self.printTable.append([1, "连线", "%.1f"%s6])
            c4 = s6
        elif id == 6:
            s6 = self.analysisInner(id)
            self.printTable.append([1, "内场", "%.1f"%s6])
            c4 = s6
            
        numDPS = self.data.dpsTable[id-1][4]
        if numDPS < 16:
            s8 = 16 - numDPS
            self.printTable.append([1, "人数修正", "%.1f"%s8])
            c5 += s8
        
        c6 = c1 + c2 + c3 + c4 + c5
        if c6 > cutOff0[id]:
            c6 = cutOff0[id]
        
        c7 = 0
        c8 = 0
        
        num1 = sum(self.generator2[id-1].data.hitCount[self.mykey].values())
        num2 = sum(self.generator2[id-1].data.deathCount[self.mykey])
        if num1 > 0:
            c7 = -num1
            self.printTable.append([2, "犯错", "%.1f"%c7])
        if num2 > 0:
            c8 = -num2 * 2
            self.printTable.append([2, "重伤", "%.1f"%c8])
        
        c9 = c6 + c7 + c8
        if c9 < 0:
            c9 = 0
        
        self.printTable.append([3, "小计", "%.1f"%c9])
        return c9
        
    def analysisBOSSyd(self, id):
        cutOff1 = [0, 0, 0, 5, 5, 5]
        cutOff2 = [0, 15, 15, 10, 10, 5]
        cutOff4 = [0, 0, 0, 0, 0, 0, 5]
        cutOff0 = [0, 20, 20, 20, 20, 20]
        self.printTable.append([0, "%s 打分表"%self.bossDictR[id], ""])
        c1 = 0
        c5 = 0
        if id in [3,4,5]:
            s1 = self.analysisHPS(id)
            self.printTable.append([1, "治疗量", "%.1f"%s1])
            s2 = self.analysisShield(id)
            self.printTable.append([1, "盾数", "%.1f"%s2])
            c1 = s1 + s2
            if c1 > cutOff1[id]:
                c1 = cutOff1[id]
                c5 += (s1 + s2 - cutOff1[id]) / 2
        s3 = self.analysisDPS(id)
        self.printTable.append([1, "等效DPS", "%.1f"%s3])
        s4 = self.analysisRate(id)
        self.printTable.append([1, "覆盖率", "%.1f"%s4])
        c2 = s3 + s4
        if c2 > cutOff2[id]:
            c2 = cutOff2[id]
            c5 += (s3 + s4 - cutOff2[id]) / 2
        s5 = self.analysisSpare(id)
        self.printTable.append([1, "空闲比例", "%.1f"%s5])
        c3 = s5
        
        c4 = 0
        if id == 5:
            s7 = self.analysisNPC(id)
            self.printTable.append([1, "入魔承疗", "%.1f"%s7])
            c4 = s7
            
        numDPS = self.data.dpsTable[id-1][4]
        if numDPS < 16:
            s8 = 16 - numDPS
            self.printTable.append([1, "人数修正", "%.1f"%s8])
            c5 += s8
        
        c6 = c1 + c2 + c3 + c4 + c5
        if c6 > cutOff0[id]:
            c6 = cutOff0[id]
        
        c7 = 0
        c8 = 0
        
        num1 = sum(self.generator2[id-1].data.hitCount[self.mykey].values())
        num2 = sum(self.generator2[id-1].data.deathCount[self.mykey])
        if num1 > 0:
            c7 = -num1
            self.printTable.append([2, "犯错", "%.1f"%c7])
        if num2 > 0:
            c8 = -num2 * 2
            self.printTable.append([2, "重伤", "%.1f"%c8])
        
        c9 = c6 + c7 + c8
        if c9 < 0:
            c9 = 0
            
        self.printTable.append([3, "小计", "%.1f"%c9])
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
            self.printTable.append([0, "总分", "%.1f"%sumScore])
            self.score = sumScore
            self.finalRate()
        elif len(self.generator) in [4,5] and self.map == "范阳夜变":
            self.available = 1
            sumScore = 0
            for i in range(1, len(self.generator) + 1):
                score = self.analysisBOSSyd(i)
                sumScore += score
            self.printTable.append([0, "总分", "%.1f"%sumScore])
            self.score = sumScore
            self.finalRate()
        else:
            self.available = 0
            print("战斗记录不全，无法进行打分。")
        
    def __init__(self, data, generator, generator2, mykey, map):
        self.data = data
        self.mykey = mykey
        self.generator = generator
        self.generator2 = generator2
        self.map = map
        self.printTable = []
        self.score = 0
        if self.map == "敖龙岛":
            bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
            bossDictR = ["", "铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
        elif self.map == "范阳夜变":
            bossDict = {"周贽": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5}
            bossDictR = ["", "周贽", "厌夜", "迟驻", "白某", "安小逢"]

class RawDataParser():

    def parseFile(self, path, filename):
        if path == "":
            name = filename
        else:
            name = "%s\\%s"%(path, filename)
        print("读取文件：%s"%name)
        f = open(name, "r")
        s = f.read()
        res, _ = parseLuatable(s, 8, len(s))
        
        if '9' not in res:
            if len(res['']) == 17:
                for i in range(1, 17):
                    res[str(i)] = [res[''][i-1]]
            else:
                raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")
                
        return res
    
    def __init__(self, filelist, path):
        self.rawdata = {}
        for filename in filelist:
            self.rawdata[filename] = self.parseFile(path, filename)
            
class ActorAnalysis():
    
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
    yanyeTable = {}
    yanyeActive = 0
    chizhuActive = 0
    baimouActive = 0
    anxiaofengActive = 0
    
    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s)-1)
            
    def getColor(self, occ):
        if self.color == 0:
            return (0, 0, 0)
        colorDict = {"0": (0, 0, 0), 
                     "1": (210, 180, 0),#少林
                     "2": (127, 31, 223),#万花
                     "4": (56, 175, 255),#纯阳
                     "5": (255, 127, 255),#七秀
                     "3": (160, 0, 0),#天策
                     "8": (255, 255, 0),#藏剑
                     "9": (205, 133, 63),#丐帮
                     "10": (253, 84, 0),#明教
                     "6": (63, 31, 159),#五毒
                     "7": (0, 133, 144),#唐门
                     "21": (180, 60, 0),#苍云
                     "22": (100, 250, 180),#长歌
                     "23": (71, 73, 166),#霸刀
                     "24": (195, 171, 227),#蓬莱
                     "25": (161, 9, 34)#凌雪
                    }
        if occ not in colorDict:
            occ = "0"
        return colorDict[occ]
        
    def paint(self, filename):
    
        #data = self.data
    
        battleDate = self.battledate
        generateDate = time.strftime("%Y-%m-%d", time.localtime())

        width = 800
        height = 1200

        def paint(draw, content, posx, posy, font, fill):
            draw.text(
                (posx, posy),
                text = content,
                font = font,
                fill = fill
            )
            if self.text == 1:
                if posy != self.pastH:
                    self.f.write('\n')
                    self.pastH = posy
                else:
                    self.f.write('    ')
                self.f.write(content)
                
        def write(content):
            if self.text == 1:
                self.f.write(content)

        fontPath = 'C:\\Windows\\Fonts\\msyh.ttc'
        if not os.path.isfile(fontPath):
            print("系统中未找到字体文件，将在当前目录下查找msyh.ttc")
            fontPath = 'msyh.ttc'
            if not os.path.isfile(fontPath):
                print("当前目录下也没有，请尝试从群文件或Github上获取")
                raise Exception("找不到字体文件：msyh.ttc")

        fontTitle = ImageFont.truetype(font=fontPath, encoding="unic", size=24)
        fontText = ImageFont.truetype(font=fontPath, encoding="unic", size=14)
        fontSmall = ImageFont.truetype(font=fontPath, encoding="unic", size=8)
        fontBig = ImageFont.truetype(font=fontPath, encoding="unic", size=48)

        image = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
        fillcyan = (0, 255, 255)
        fillblack = (0, 0, 0)
        fillred = (255, 0, 0)
        draw = ImageDraw.Draw(image)
        
        if self.text == 1:
            self.f = open("result.txt", "w")

        paint(draw, "%s战斗记录-演员"%self.map, 290, 10, fontTitle, fillcyan)
        
        if self.yanyeActive:
            paint(draw, "[厌夜]的战斗时间为%s。"%parseTime(self.yanyeTime), 10, 60, fontText, fillblack)
            paint(draw, "“平血”表示未识别时对白云和小剑的伤害。", 20, 90, fontSmall, fillblack)
            paint(draw, "“RUSH”表示识别成功时对假厌夜和无面鬼的伤害。", 20, 100, fontSmall, fillblack)
            paint(draw, "“无效DPS”表示识别成功时对真厌夜的伤害。", 20, 110, fontSmall, fillblack)
            paint(draw, "“惩罚DPS”表示平血阶段血量差超过4%时的伤害。", 20, 120, fontSmall, fillblack)
            paint(draw, "“有效DPS”表示扣除无效与惩罚DPS的总伤害。", 20, 130, fontSmall, fillblack)
            write('\n')

            paint(draw, "厌夜战斗统计", 230, 75, fontSmall, fillblack)
            paint(draw, "有效DPS", 300, 75, fontSmall, fillblack)
            paint(draw, "平血-白云", 340, 75, fontSmall, fillblack)
            paint(draw, "平血-小剑", 380, 75, fontSmall, fillblack)
            paint(draw, "RUSH", 420, 75, fontSmall, fillblack)
            paint(draw, "无效DPS", 460, 75, fontSmall, fillblack)
            paint(draw, "惩罚DPS", 500, 75, fontSmall, fillblack)
            h = 75
            for line in self.yanyeTable:
                h += 10
                paint(draw, "%s"%self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1])) 
                paint(draw, "%d"%line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d"%line[3], 343, h, fontSmall, fillblack)
                paint(draw, "%d"%line[4], 383, h, fontSmall, fillblack)
                paint(draw, "%d"%line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d"%line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d"%line[7], 500, h, fontSmall, fillblack)
                
        if self.chizhuActive:
            paint(draw, "[迟驻]的战斗时间为%s。"%parseTime(self.chizhuTime), 10, 300, fontText, fillblack)
            paint(draw, "“点名时间”表示扶桑、月落、一觞的点名总时间。", 20, 330, fontSmall, fillblack)
            paint(draw, "“无视debuff”表示[无视]的层数对时间取积分。", 20, 340, fontSmall, fillblack)
            paint(draw, "“原始DPS”表示实际的DPS。", 20, 350, fontSmall, fillblack)
            paint(draw, "“等效DPS”表示考虑上面两项后，折算的DPS。", 20, 360, fontSmall, fillblack)
            write('\n')
            
            paint(draw, "迟驻战斗统计", 230, 300, fontSmall, fillblack)
            paint(draw, "等效DPS", 300, 300, fontSmall, fillblack)
            paint(draw, "点名时间", 340, 300, fontSmall, fillblack)
            paint(draw, "无视debuff", 380, 300, fontSmall, fillblack)
            paint(draw, "原始DPS", 420, 300, fontSmall, fillblack)
            write('\n')
            
            h = 300
            for line in self.chizhuTable:
                h += 10
                paint(draw, "%s"%self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1])) 
                paint(draw, "%d"%line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d"%line[3], 343, h, fontSmall, fillblack)
                paint(draw, "%d"%line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d"%line[5], 420, h, fontSmall, fillblack)
                
        if self.baimouActive:
            paint(draw, "[白某]的战斗时间为%s。"%parseTime(self.baimouTime), 10, 540, fontText, fillblack)
            paint(draw, "“单体DPS”表示在常规阶段，对BOSS的DPS。", 20, 570, fontSmall, fillblack)
            paint(draw, "“符灵DPS”表示在推命阶段，对符灵的DPS。", 20, 580, fontSmall, fillblack)
            paint(draw, "“水牢DPS”表示对水牢的DPS", 20, 590, fontSmall, fillblack)
            paint(draw, "“原始DPS”表示实际的DPS。", 20, 600, fontSmall, fillblack)
            paint(draw, "“点名时间”表示受[覆舟]影响的时间。", 20, 610, fontSmall, fillblack)
            paint(draw, "“有效DPS”表示排除点名及群攻之后的DPS。", 20, 620, fontSmall, fillblack)
            write('\n')
            
            paint(draw, "白某战斗统计", 230, 540, fontSmall, fillblack)
            paint(draw, "有效DPS", 300, 540, fontSmall, fillblack)
            paint(draw, "单体DPS", 340, 540, fontSmall, fillblack)
            paint(draw, "符灵DPS", 380, 540, fontSmall, fillblack)
            paint(draw, "水牢DPS", 420, 540, fontSmall, fillblack)
            paint(draw, "原始DPS", 460, 540, fontSmall, fillblack)
            paint(draw, "点名时间", 500, 540, fontSmall, fillblack)
            h = 540
            for line in self.baimouTable:
                h += 10
                paint(draw, "%s"%self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1])) 
                paint(draw, "%d"%line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d"%line[3], 340, h, fontSmall, fillblack)
                paint(draw, "%d"%line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d"%line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d"%line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d"%line[7], 500, h, fontSmall, fillblack)
                
        if self.anxiaofengActive:
            paint(draw, "[安小逢]的战斗时间为%s。"%parseTime(self.anxiaofengTime), 10, 780, fontText, fillblack)
            paint(draw, "“原始DPS”表示游戏中插件统计的实际DPS。", 20, 810, fontSmall, fillblack)
            paint(draw, "“安小逢DPS”表示原始DPS中属于安小逢的部分。", 20, 820, fontSmall, fillblack)
            paint(draw, "“小怪DPS”表示对狼牙斧卫和水鬼的DPS，", 20, 830, fontSmall, fillblack)
            paint(draw, "其中，每个DPS被点名的时间段都不计算。", 20, 840, fontSmall, fillblack)
            paint(draw, "“鬼首DPS”表示对鬼首的DPS。", 20, 850, fontSmall, fillblack)
            paint(draw, "注意，小怪和鬼首的DPS中，时间为估算。", 20, 860, fontSmall, fillblack)
            paint(draw, "“P3DPS”表示在P3对安小逢的DPS。", 20, 870, fontSmall, fillblack)
            paint(draw, "“入魔治疗量”表示对[走火入魔]状态队友的治疗量。", 20, 880, fontSmall, fillblack)
            paint(draw, "“承伤记录”表示对[暗月血镰]技能的承伤在第几组。", 20, 890, fontSmall, fillblack)
            paint(draw, "“0”表示本次未承伤，“X”表示本次被[盯]点名。", 20, 900, fontSmall, fillblack)
            write('\n')
            
            
            paint(draw, "安小逢战斗统计", 230, 780, fontSmall, fillblack)
            paint(draw, "原始DPS", 300, 780, fontSmall, fillblack)
            paint(draw, "安小逢DPS", 340, 780, fontSmall, fillblack)
            paint(draw, "小怪DPS", 380, 780, fontSmall, fillblack)
            paint(draw, "鬼首DPS", 420, 780, fontSmall, fillblack)
            paint(draw, "P3DPS", 460, 780, fontSmall, fillblack)
            paint(draw, "入魔治疗量", 500, 780, fontSmall, fillblack)
            paint(draw, "承伤记录", 540, 780, fontSmall, fillblack)
            h = 780
            for line in self.anxiaofengTable:
                h += 10
                paint(draw, "%s"%self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1])) 
                paint(draw, "%d"%line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d"%line[3], 340, h, fontSmall, fillblack)
                paint(draw, "%d"%line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d"%line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d"%line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d"%line[7], 500, h, fontSmall, fillblack)
                paint(draw, "%s"%line[8], 540, h, fontSmall, fillblack)
                
        write('\n')
        paint(draw, "犯错记录", 550, 70, fontSmall, fillblack)
        h = 70
        for line in self.potList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[0]), 560, h, fontSmall, self.getColor(line[1])) 
            paint(draw, "%s"%line[2], 610, h, fontSmall, fillblack)
            paint(draw, "%s"%line[3], 640, h, fontSmall, fillblack)


        write('\n')
        paint(draw, "进本时间：%s"%battleDate, 700, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s"%generateDate, 700, 50, fontSmall, fillblack)
        paint(draw, "难度：%s"%self.mapdetail, 700, 60, fontSmall, fillblack)
        paint(draw, "版本号：%s"%edition, 30, 1180, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 1180, fontSmall, fillblack)

        image.save(filename)
        
        if self.text == 1:
            self.f.close()
        
    
    def analysis(self):
        if self.map == "敖龙岛":
            mapid = self.generator[0].rawdata['20'][0]
            if mapid == "428":
                self.mapdetail = "25人英雄"
            elif mapid == "427":
                self.mapdetail = "25人普通"
            elif mapid == "426":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"

        if self.map == "范阳夜变":    
            mapid = self.generator[0].rawdata['20'][0]
            if mapid == "454":
                self.mapdetail = "25人英雄"
            elif mapid == "453":
                self.mapdetail = "25人普通"
            elif mapid == "452":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"
            
        self.potList = []
        for line in self.generator:
            if line.bossname == "厌夜" and line.yanyeActive:
                self.yanyeActive = 1
                self.yanyeTable = line.yanyeResult
                self.yanyeTime = line.battleTime
            if line.bossname == "迟驻" and line.chizhuActive:
                self.chizhuActive = 1
                self.chizhuTable = line.chizhuResult
                self.chizhuTime = line.battleTime
            if line.bossname == "白某" and line.baimouActive:
                self.baimouActive = 1
                self.baimouTable = line.baimouResult
                self.baimouTime = line.battleTime
            if line.bossname == "安小逢" and line.anxiaofengActive:
                self.anxiaofengActive = 1
                self.anxiaofengTable = line.anxiaofengResult
                self.anxiaofengTime = line.battleTime
            self.potList += line.potList
            
    
    def loadData(self, fileList, path, raw):
        for filename in fileList:
            res = ActorStatGenerator(filename, path, rawdata = raw[filename])
            res.firstStageAnalysis()
            res.secondStageAnalysis()
            self.generator.append(res)
            
    
    def __init__(self, filelist, map, path, config, raw):
        self.myname = config.xiangzhiname
        self.mask = config.mask
        self.color = config.color
        self.text = config.text
        self.speed = config.speed
        self.loadData(filelist, path, raw)
        self.map = map
        self.battledate = '-'.join(filelist[0].split('-')[0:3])
    

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
    
    hitDict = {"s22520": "锈铁钩锁", 
               "s22521": "火轮重锤",
               "s22203": "气吞八方",
               "s22388": "岚吟",
               "s22367": "禊祓·绀凌",
               "s22356": "禊祓·绛岚",
               "s22374": "零域",
               "s22776": "双环掌击",
               "s22246": "劈山尾鞭",
               "s22272": "追魂扫尾",
               "s22111": "巨力爪击",
               "b16316": "心狐炸人",
              }
    
    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s)-1)
            
    def getColor(self, occ):
        if self.color == 0:
            return (0, 0, 0)
        colorDict = {"0": (0, 0, 0), 
                     "1": (160, 0, 0),#天策
                     "2": (127, 31, 223),#万花
                     "4": (56, 175, 255),#纯阳
                     "5": (255, 127, 255),#七秀
                     "3": (210, 180, 0),#少林
                     "8": (255, 255, 0),#藏剑
                     "9": (205, 133, 63),#丐帮
                     "10": (253, 84, 0),#明教
                     "6": (63, 31, 159),#五毒
                     "7": (0, 133, 144),#唐门
                     "21": (180, 60, 0),#苍云
                     "22": (100, 250, 180),#长歌
                     "23": (71, 73, 166),#霸刀
                     "24": (195, 171, 227),#蓬莱
                     "25": (161, 9, 34)#凌雪
                    }
        if occ not in colorDict:
            occ = "0"
        return colorDict[occ]
    
    def paint(self, filename):
    
        data = self.data
        actorData = self.actorData
    
        battleDate = self.battledate
        generateDate = time.strftime("%Y-%m-%d", time.localtime())

        width = 800
        height = 800

        def paint(draw, content, posx, posy, font, fill):
            draw.text(
                (posx, posy),
                text = content,
                font = font,
                fill = fill
            )
            if self.text == 1:
                if posy != self.pastH:
                    self.f.write('\n')
                    self.pastH = posy
                else:
                    self.f.write('    ')
                self.f.write(content)
                
        def write(content):
            if self.text == 1:
                self.f.write(content)

        fontPath = 'C:\\Windows\\Fonts\\msyh.ttc'
        if not os.path.isfile(fontPath):
            print("系统中未找到字体文件，将在当前目录下查找msyh.ttc")
            fontPath = 'msyh.ttc'
            if not os.path.isfile(fontPath):
                print("当前目录下也没有，请尝试从群文件或Github上获取")
                raise Exception("找不到字体文件：msyh.ttc")

        fontTitle = ImageFont.truetype(font=fontPath, encoding="unic", size=24)
        fontText = ImageFont.truetype(font=fontPath, encoding="unic", size=14)
        fontSmall = ImageFont.truetype(font=fontPath, encoding="unic", size=8)
        fontBig = ImageFont.truetype(font=fontPath, encoding="unic", size=48)

        image = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
        fillcyan = (0, 255, 255)
        fillblack = (0, 0, 0)
        fillred = (255, 0, 0)
        draw = ImageDraw.Draw(image)
        
        if self.text == 1:
            self.f = open("result.txt", "w")

        paint(draw, "%s战斗记录-奶歌"%self.map, 290, 10, fontTitle, fillcyan)
        paint(draw, "可爱的奶歌[%s]："%self.myname.strip('"'), 10, 50, fontText, fillblack)
        write('\n')

        base = 75
        paint(draw, "在这次%s之旅中，"%self.map, 30, base, fontText, fillblack)
        paint(draw, "你一共产生了%d点治疗量，"%data.numheal, 30, base+15, fontText, fillblack)
        paint(draw, "其中有%d点是有效治疗，"%data.numeffheal, 30, base+30, fontText, fillblack)
        paint(draw, "你一共使用了%d次[梅花三弄]，"%data.numshield, 30, base+45, fontText, fillblack)
        paint(draw, "它们是不是也可以算成治疗量的一部分呢。", 30, base+60, fontText, fillblack)
        write('\n')

        base = base + 90
        paint(draw, "每个奶歌都有一个DPS的心，", 30, base, fontText, fillblack)
        paint(draw, "你的高光时刻是在与[%s]的战斗中，"%data.maxDpsName, 30, base+15, fontText, fillblack)
        paint(draw, "如果将[庄周梦]和[桑柔]改为计算在你身上，", 30, base+30, fontText, fillblack)
        paint(draw, "相当于你打了%d点DPS，"%data.maxDps, 30, base+45, fontText, fillblack)
        paint(draw, "是平均数的%.2f倍，"%data.maxEqualDPS, 30, base+60, fontText, fillblack)
        paint(draw, "在所有DPS中排在第%d位，"%data.maxDpsRank, 30, base+75, fontText, fillblack)
        paint(draw, "是不是又觉得自己的门票稳了一些！", 30, base+90, fontText, fillblack)
        write('\n')

        base = base + 120
        paint(draw, "并非每时每刻都能感受到梅花三弄的体贴，", 30, base, fontText, fillblack)
        paint(draw, "整个战斗中，梅花三弄的平均覆盖率是%s%%，"%parseCent(data.overallrate), 30, base+15, fontText, fillblack)
        paint(draw, "其中最高的BOSS是[%s]，覆盖率为%s%%"%(data.maxRateName, parseCent(data.maxRate)), 30, base+30, fontText, fillblack)
        paint(draw, "和你想象中的一样吗？", 30, base+45, fontText, fillblack)
        write('\n')

        base = base + 75
        paint(draw, "DPS们并不都知道奶歌的人间冷暖，", 30, base, fontText, fillblack)
        paint(draw, "盾平均覆盖率最高的是[%s]，达到了%s%%，"%(self.getMaskName(data.maxSingleRateName), parseCent(data.maxSingleRate)), 30, base+15, fontText, fillblack)
        paint(draw, "是因为好好保了盾，还是你更关注他一些?", 30, base+30, fontText, fillblack)
        paint(draw, "而破盾次数最多的是[%s]，有%d次,"%(self.getMaskName(data.maxSingleBreakName), data.maxSingleBreak), 30, base+45, fontText, fillblack)
        paint(draw, "下次知道该把谁放在最后了吧！", 30, base+60, fontText, fillblack)
        write('\n')

        base = base + 90
        paint(draw, "[%s]可以说是整个副本最难的BOSS，"%self.hardBOSS, 30, base, fontText, fillblack)
        paint(draw, "你在其中使用了%d次[一指回鸾]，"%data.numpurge, 30, base+15, fontText, fillblack)
        paint(draw, "你对%s的治疗量是%d点，占比%s%%，"%(self.hardNPC, data.npcHeal, parseCent(data.npcHealRate)), 30, base+30, fontText, fillblack)
        paint(draw, "在所有奶妈中排名第%d/%d位，"%(data.npcRank, data.npcHealNum), 30, base+45, fontText, fillblack)
        paint(draw, "是不是觉得自己能打能奶，文武双全！", 30, base+60, fontText, fillblack)
        write('\n')
        
        base = base + 90
        paint(draw, "治疗职业在副本中一点也不比DPS轻松，", 30, base, fontText, fillblack)
        paint(draw, "按照%d加速计算，"%self.speed, 30, base+15, fontText, fillblack)
        paint(draw, "你在副本中的空闲时间比例为%s%%，"%parseCent(data.spareRate), 30, base+30, fontText, fillblack)
        paint(draw, "快和别的小伙伴比一比，看是谁更划水呀。", 30, base+45, fontText, fillblack)
        write('\n')
        
        base = base + 75
        paint(draw, "当然，大家都要面对相同的副本机制，", 30, base, fontText, fillblack)
        paint(draw, "你中了%d次惩罚技能，重伤了%d次，"%(self.sumHit, self.sumDeath), 30, base+15, fontText, fillblack)
        if self.map == "敖龙岛":
            paint(draw, "在老五连了%d次线，在老六进了%d次内场，"%(self.sumDrawer, self.sumInner), 30, base+30, fontText, fillblack)
            paint(draw, "下次是不是可以说，自己是合格的演员啦！", 30, base+45, fontText, fillblack)
        else:
            paint(draw, "下次是不是可以说，自己是合格的演员啦！", 30, base+30, fontText, fillblack)
        write('\n')

        paint(draw, "整体治疗量表", 300, 75, fontSmall, fillblack)
        paint(draw, "HPS", 355, 75, fontSmall, fillblack)
        paint(draw, "占比", 390, 75, fontSmall, fillblack)
        paint(draw, "排名", 430, 75, fontSmall, fillblack)
        paint(draw, "APS", 460, 75, fontSmall, fillblack)
        paint(draw, "盾数", 490, 75, fontSmall, fillblack)
        paint(draw, "战斗时间", 520, 75, fontSmall, fillblack)
        paint(draw, "盾每分", 570, 75, fontSmall, fillblack)
        h = 75
        for line in data.healTable:
            h += 10
            paint(draw, "%s"%line[0], 310, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 355, h, fontSmall, fillblack)
            paint(draw, "%s%%"%parseCent(line[2]), 390, h, fontSmall, fillblack)
            paint(draw, "%d/%d"%(line[3], line[4]), 430, h, fontSmall, fillblack)
            paint(draw, "%d"%line[5], 460, h, fontSmall, fillblack)
            paint(draw, "%d"%line[6], 490, h, fontSmall, fillblack)
            paint(draw, "%s"%parseTime(line[7]), 520, h, fontSmall, fillblack)
            paint(draw, "%.1f"%line[8], 570, h, fontSmall, fillblack)

        write('\n')
        paint(draw, "等效DPS表", 320, 165, fontSmall, fillblack)
        paint(draw, "DPS", 375, 165, fontSmall, fillblack)
        paint(draw, "排名", 410, 165, fontSmall, fillblack)
        paint(draw, "强度", 440, 165, fontSmall, fillblack)
        paint(draw, "人数", 470, 165, fontSmall, fillblack)
        h = 165
        for line in data.dpsTable:
            h += 10
            paint(draw, "%s"%line[0], 330, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 370, h, fontSmall, fillblack)
            paint(draw, "%d"%line[2], 410, h, fontSmall, fillblack)
            paint(draw, "%.2f"%line[3], 440, h, fontSmall, fillblack)
            paint(draw, "%d"%line[4], 470, h, fontSmall, fillblack)

        write('\n')
        paint(draw, "[%s]的等效DPS统计"%data.maxDpsName, 520, 165, fontSmall, fillblack)  
        h = 165
        for line in data.maxDpsTable:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 520, h, fontSmall, self.getColor(line[3]))
            paint(draw, "%d DPS"%int(line[1]), 595, h, fontSmall, fillblack) 
            if h > 330:
                break

        write('\n')
        paint(draw, "平均覆盖率表", 350, 280, fontSmall, fillblack)
        h = 280
        for line in data.rateTable:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 410, h, fontSmall, fillblack) 
            
        if self.map == "范阳夜变":
            bossNameList = ["迟驻", "白某", "安小逢"]
        else:
            bossNameList = ["铁黎", "陈徽", "藤原武裔"]

        write('\n')
        paint(draw, "DPS覆盖率统计", 350, 375, fontSmall, fillblack)
        paint(draw, "全程", 420, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[0], 465, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[1], 490, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[2], 515, 375, fontSmall, fillblack)
        h = 375
        
        #print(data.rateList)
        for line in data.rateList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 360, h, fontSmall, self.getColor(line[3])) 
            paint(draw, "%s%%"%parseCent(line[1]), 420, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][0], 0), 465, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][1], 0), 490, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][2], 0), 515, h, fontSmall, fillblack)
            if h > 550:
                break

        write('\n')
        paint(draw, "DPS破盾次数", 550, 375, fontSmall, fillblack)
        paint(draw, "全程", 620, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[0], 650, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[1], 675, 375, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[2], 700, 375, fontSmall, fillblack)
        h = 375
        for line in data.breakList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 560, h, fontSmall, self.getColor(line[3])) 
            paint(draw, "%d"%line[1], 620, h, fontSmall, fillblack)
            paint(draw, "%d"%data.bossBreakDict[line[0]][0], 650, h, fontSmall, fillblack) 
            paint(draw, "%d"%data.bossBreakDict[line[0]][1], 675, h, fontSmall, fillblack) 
            paint(draw, "%d"%data.bossBreakDict[line[0]][2], 700, h, fontSmall, fillblack)
            if h > 550:
                break

        write('\n')
        paint(draw, "%s治疗量统计"%self.hardNPC, 345, 580, fontSmall, fillblack)
        h = 580
        for line in data.npcHealList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 360, h, fontSmall, self.getColor(line[3]))
            paint(draw, "%d"%line[1], 440, h, fontSmall, fillblack)
            if h > 630:
                break
             
        write('\n')
        paint(draw, "空闲比例表", 500, 580, fontSmall, fillblack)
        h = 580
        for line in data.spareRateList:
            h += 10
            paint(draw, "%s"%line[0], 510, h, fontSmall, fillblack)
            paint(draw, "%s%%"%parseCent(line[1]), 560, h, fontSmall, fillblack)
            
        write('\n')
        paint(draw, "犯错记录", 620, 580, fontSmall, fillblack)
        h = 580
        for line in actorData.hitCount[data.mykey]:
            if line not in self.hitDict:
                continue
            h += 10
            paint(draw, "%s"%self.hitDict[line], 630, h, fontSmall, fillblack)
            paint(draw, "%d"%actorData.hitCount[data.mykey][line], 690, h, fontSmall, fillblack)
            
        write('\n')
        paint(draw, "评分记录", 730, 70, fontSmall, fillblack)
        h = 70
        for line in self.score.printTable:
            h += 10
            if line[0] == 0:
                paint(draw, line[1], 730, h, fontSmall, fillblack)
                paint(draw, line[2], 770, h, fontSmall, fillblack)
            elif line[0] == 1:
                paint(draw, line[1], 740, h, fontSmall, fillblack)
                paint(draw, line[2], 780, h, fontSmall, fillblack)
            elif line[0] == 2:
                paint(draw, line[1], 740, h, fontSmall, fillred)
                paint(draw, line[2], 780, h, fontSmall, fillred)
            elif line[0] == 3:
                paint(draw, line[1], 740, h, fontSmall, fillblack)
                paint(draw, line[2], 780, h, fontSmall, fillblack)
        
        write('\n')
        if self.score.available == 0:
            paint(draw, "由于1-6的战斗数据不完整，无法生成评分。", 30, 690, fontText, fillblack)
        else:
            fillRate = (0, 0, 0)
            if self.score.color == 0: 
                fillRate = (255, 255, 0)
            elif self.score.color == 1:
                fillRate = (255, 128, 128)
            elif self.score.color == 2:
                fillRate = (255, 128, 0)
            elif self.score.color == 3:
                fillRate = (0, 128, 255)
            elif self.score.color == 4:
                fillRate = (128, 255, 0)
            else:
                fillRate = (255, 0, 0)
            paint(draw, "基于以上数据，你的评分为：", 30, 690, fontText, fillblack)
            paint(draw, self.score.rate, 220, 680, fontBig, fillRate)
            paint(draw, "（以实际表现为准，评分仅供参考）", 30, 715, fontSmall, fillblack)
            paint(draw, self.score.describe, 320, 735, fontTitle, fillRate)
            
        write('\n')
        paint(draw, "进本时间：%s"%battleDate, 700, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s"%generateDate, 700, 50, fontSmall, fillblack)
        paint(draw, "难度：%s"%self.mapdetail, 700, 60, fontSmall, fillblack)
        paint(draw, "版本号：%s"%edition, 30, 780, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 780, fontSmall, fillblack)

        image.save(filename)
        
        if self.text == 1:
            self.f.close()
    
    def loadData(self, fileList, path, raw):
        
        for filename in fileList:
            res = XiangZhiStatGenerator(filename, self.myname, rawdata = raw[filename])
            res.speed = self.speed
            res.firstStageAnalysis()
            res.secondStageAnalysis()
            self.generator.append(res)
            if self.myname == "":
                self.myname = res.myname
            elif self.myname != res.myname:
                raise Exception("全程奶歌名称不一致，请手动指定ID")
            
            res2 = ActorStatGenerator(filename, path, res.rawdata, self.myname)
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
                self.mapdetail = "未知"
                
        if self.map == "范阳夜变":
            self.hardBOSS = "安小逢"
            self.hardNPC = "走火入魔玩家"
            self.hitDict = {"s23621": "隐雷鞭", 
                       "s23700": "短歌式",
                       "b16842": "符咒禁锢",
                      }
                      
            mapid = generator[0].rawdata['20'][0]
            if mapid == "454":
                self.mapdetail = "25人英雄"
            elif mapid == "453":
                self.mapdetail = "25人普通"
            elif mapid == "452":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"
        
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

        data.rateList.sort(key=lambda x:-x[1])
        data.breakList.sort(key=lambda x:-x[1])
        
        for line in data.rateList:
            data.bossRateDict[line[0]] = [0, 0, 0]
        
        for line in data.breakList:
            data.bossBreakDict[line[0]] = [0, 0, 0]
        
        for line in generator:
            if self.map == "范阳夜变":
                bossNameList = ["迟驻", "白某", "安小逢"]
            else:
                bossNameList = ["铁黎", "陈徽", "藤原武裔"]
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
        
        for line in generator:
            if line.bossname == "源思弦":
                data.numpurge = line.data.numpurge
                data.npchealstat = line.data.npchealstat
                data.npcHealList = dictToPairs(data.npchealstat)
            if line.bossname == "安小逢":
                data.numpurge = line.data.numpurge
                data.npchealstat = line.data.npchealstat
                data.npcHealList = dictToPairs(data.npchealstat)
                
        data.npcHealList.sort(key=lambda x:-x[1])
        
        for i in range(len(data.npcHealList)):
            data.npcHealList[i].append(namedict[data.npcHealList[i][0]][0])
            data.npcHealList[i].append(occdict[data.npcHealList[i][0]][0])
        
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
        
        for line in generator:
            data.sumBusyTime += line.data.sumBusyTime
            data.sumSpareTime += line.data.sumSpareTime
            data.spareRateList.append([line.bossname.strip('"'), line.data.spareRate])
            
        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)
        #print(data.spareRate)
        
        actorData = ActorData()
        for line in self.generator2:
            #namedict = line.rawdata['9'][0]
            actorData.addActorData(line.data)
        
        self.data = data
        self.actorData = actorData
        self.sumHit = sum(self.actorData.hitCount[data.mykey].values())
        self.sumDeath = sum(self.actorData.deathCount[data.mykey])
        self.sumInner = sum(self.actorData.innerPlace[data.mykey])
        self.sumDrawer = self.actorData.drawer[data.mykey]
        
        self.score = XiangZhiScore(self.data, self.generator, self.generator2, data.mykey, self.map)
        self.score.analysisAll()
        
    
    def __init__(self, filelist, map, path, config, raw):
        self.myname = config.xiangzhiname
        self.mask = config.mask
        self.color = config.color
        self.text = config.text
        self.speed = config.speed
        self.loadData(filelist, path, raw)
        self.map = map
        self.battledate = '-'.join(filelist[0].split('-')[0:3])
        
        
class FileLookUp():

    jx3path = ""
    basepath = "."
    
    def getPathFromWinreg(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\JX3Installer',)
            pathres = winreg.QueryValueEx(key, "InstPath")[0]
        except:
            print("自动获取目录失败，请手动指定目录")
            pathres = ""
        self.jx3path = pathres
        
    def getBasePath(self, playerName):
        datapath = "%s\\Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA"%self.jx3path
        resDir = ""
        l = os.listdir(datapath)
        for name in l:
            path2 = "%s\\%s"%(datapath, name)
            if os.path.isdir(path2):
                l2 = os.listdir(path2)
                if playerName in l2:
                    resDir = "%s\\userdata\\fight_stat"%path2
                    break
                    
        self.basepath = resDir
        if resDir == "":
            print("剑三目录有误，请检查记录者角色名是否正确")
        
    def getLocalFile(self):
        filelist = os.listdir(self.basepath)

        selectFileList = []
        for line in filelist:
            if line[-6:] == "jx3dat":
                selectFileList.append(line)

        bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6,
                    "周贽": 1, "狼牙精锐": 1, "狼牙刀盾兵": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5}
        mapDict = {"铁黎": 1, "陈徽": 1, "藤原武裔": 1, "源思弦": 1, "驺吾": 1, "方有崖": 1,
                   "周贽": 2, "狼牙精锐": 2, "狼牙刀盾兵": 2, "厌夜": 2, "迟驻": 2, "白某": 2, "安小逢": 2}
        mapNameList = ["未知地图", "敖龙岛", "范阳夜变"]
        
        nowBoss = 6
        bossPos = [-1] * 8
        bossPos[7] = 999
        bossList = [0] * len(selectFileList)
        for i in range(len(selectFileList)-1, -1, -1):
            if selectFileList[i][-13:] == "config.jx3dat":
                continue
            bossname = selectFileList[i].split('_')[-2]
            if bossname in bossDict:
                if bossDict[bossname] <= nowBoss:
                    bossPos[bossDict[bossname]] = i
                    bossList[i] = bossDict[bossname]
                    nowBoss = bossDict[bossname] - 1
            battletime = int(selectFileList[i].split('_')[2].split('.')[0])
            if battletime > 120 and bossList[i] == 0:
                bossList[i] = 999

        #for i in range(1, 7):
        #    if bossPos[i] == -1:
        #        for j in range(len(selectFileList)):
        #            if j > bossPos[i-1] and j < bossPos[i+1] and bossList[j] == 999:
        #                bossList[j] = i
        #                bossPos[i] = j

        finalList = []
        for i in range(1, 7):
            if bossPos[i] != -1:
                finalList.append(selectFileList[bossPos[i]])
                
        if finalList == []:
            print("没有合适的战斗记录，请确认目录设置或角色是否正确。")
            
        finalFileName = finalList[-1]
        finalBossName = finalFileName.split('_')[-2]
        finalMap = mapNameList[mapDict[finalBossName]]

        return finalList, finalMap
    
    def __init__(self):
        pass
        
class Config():

    items_general = {}
    items_xiangzhi = {}
    items_actor = {}
    
    def checkItems(self):
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
            assert self.mask in [0, 1]
            assert self.color in [0, 1]
            assert self.text in [0, 1]
            assert self.xiangzhiActive in [0, 1]
            assert self.actorActive in [0, 1]
        except:
            raise Exception("配置文件格式不正确，请确认。如无法定位问题，请删除config.ini，在生成的配置文件的基础上进行修改。")
    
    def printDefault(self):
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

[ActorAnalysis]
active=1""")
        g.close()
        pass
    
    def setDefault(self):
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
    
    def __init__(self, filename):
        if not os.path.isfile(filename):
            print("配置文件不存在，使用默认配置并自动生成到config.ini")
            self.setDefault()
            self.printDefault()
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
    
if __name__ == "__main__":

    try:
        config = Config("config.ini")
        
        fileLookUp = FileLookUp()
        if config.basepath != "":
            print("指定基准目录，使用：%s"%config.basepath)
            fileLookUp.basepath = config.basepath
        elif config.playername == "":
            print("没有指定记录者角色名，将查找当前目录下的文件……")
        else:
            if config.jx3path != "":
                print("指定剑三目录，使用：%s"%config.jx3path)
                fileLookUp.jx3path = config.jx3path
                fileLookUp.getBasePath(config.playername)
            else:
                print("无指定目录，自动查找目录……")
                fileLookUp.getPathFromWinreg()
                fileLookUp.getBasePath(config.playername)

        filelist, map = fileLookUp.getLocalFile()
        print("开始分析。分析耗时可能较长，请耐心等待……")
        
        raw = RawDataParser(filelist, fileLookUp.basepath).rawdata
        
        if config.xiangzhiActive:
            b = XiangZhiAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            b.analysis()
            b.paint("result.png")
            print("奶歌战斗复盘分析完成！结果保存在result.png中")
        
        if config.actorActive:
            c = ActorAnalysis(filelist, map, fileLookUp.basepath, config, raw)
            c.analysis()
            c.paint("actor.png")
            print("演员战斗复盘分析完成！结果保存在actor.png中")
        
        
    except Exception as e:
        traceback.print_exc()
        
    os.system('pause')
    
    
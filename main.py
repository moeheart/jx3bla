import os
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import time
import winreg
import configparser
import traceback

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

class ShieldCounter():
    
    shieldLog = []
    breakCount = 0
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
            if i + 1 < len(s) and s[i][1] == 0 and s[i+1][1] == 1 and s[i+1][0] - s[i][0] < 500:
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
        for i in range(1, n):
            assert newList[i][1] != newList[i-1][1]
            self.shieldDuration[newList[i-1][1]] += newList[i][0] - newList[i-1][0]
            if newList[i][1] == 0:
                self.breakCount += 1

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
        
class ActorStatGenerator(StatGeneratorBase):

    def secondStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        data = ActorData()

        num = 0
        skillLog = []
        
        no5P2 = 0
        
        lastHit = {}

        for line in sk:
            item = line[""]
            
            if len(item) == 16:
                if item[7] == "22520" and item[10] == "0": #锈铁钩锁
                    if item[5] not in lastHit or int(item[2]) - lastHit[item[5]] > 10000: #10秒缓冲时间
                        lastHit[item[5]] = int(item[2])
                        data.no1Lock = add1(data.no1Lock, item[5])
                if item[7] == "22521" and item[10] == "0": #火轮重锤
                    data.no1Face = add1(data.no1Face, item[5])
                if item[7] == "22203" and item[10] == "0": #气吞八方
                    data.no2Hit = add1(data.no2Hit, item[5])
                if item[7] in ["22388", "22367", "22356"] and item[10] == "0": #岚吟, 禊祓·绀凌, 禊祓·绛岚
                    data.no4Hit = add1(data.no4Hit, item[5]) 
                if item[7] in ["22776", "22402", "22246", "22272", "22111"] and item[10] == "0": #双环掌击, 掌击, 劈山尾鞭, 追魂扫尾, 巨力爪击
                    data.no5Hit = add1(data.no5Hit, item[5])
                    if no5P2:
                        data.no5P2Hit = add1(data.no5P2Hit, item[5])
                if item[7] == "23092": #震怒咆哮
                    no5P2 = 1
                              
            elif len(item) == 13:
                if item[6] == "15868": #内场buff
                    if item[5] not in data.innerPlace:
                        data.innerPlace[item[5]] = [0, 0, 0, 0]
                    data.innerPlace[item[5]][int(item[7])-1] = 1
                if item[6] == "16316": #离群之狐成就buff
                    data.no6Circle = add1(data.no6Circle, item[5]) 

            num += 1
        
        self.data = data
        
    def __init__(self, filename, path = "", rawdata = {}, myname = ""):
        self.myname = myname
        super().__init__(filename, path, rawdata)
        #self.filename = filename
        #self.parseFile(path)
        self.no1Hit = {}
    
    pass
        

class XiangZhiStatGenerator(StatGeneratorBase):
    
    myname = ""
    mykey = ""
    npckey = ""
    startTime = 0
    finalTime = 0
    speed = 3770
    shieldCounters = {}
    
    def secondStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        data = XiangZhiData()

        num = 0
        skillLog = []

        for line in sk:
            item = line[""]
            
            if len(item) == 16:
                
                if item[4] == self.mykey and item[11] != '0':
                    data.numheal += int(item[11])
                    data.numeffheal += int(item[12])
                    
                if item[4] == self.mykey and item[6] == "1":
                    skillLog.append([int(item[2]), int(item[7])])
                    
                if item[12] != '0' and item[5] == self.npckey:
                    if namedict[item[4]][0] not in data.npchealstat:
                        data.npchealstat[namedict[item[4]][0]] = int(item[12])
                    else:
                        data.npchealstat[namedict[item[4]][0]] += int(item[12])
                            
                if item[7] == "14231": #梅花三弄
                    data.numshield += 1

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

            num += 1
        
        skillCounter = SkillCounter(skillLog, self.startTime, self.finalTime, self.speed)
        skillCounter.analysisSkillData()
        data.sumBusyTime = skillCounter.sumBusyTime
        data.sumSpareTime = skillCounter.sumSpareTime
        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)
        #print(data.spareRate)
        #print(data.sumBusyTime, data.sumSpareTime, data.spareRate)
            
        numdam = 0
        for key in data.battlestat:
            if int(occdict[key][0]) == 0:
                continue
            line = data.battlestat[key]
            data.damageDict[namedict[key][0]] = line[0] + line[1] / 1.139
            numdam += line[1] / 1.139 * 0.139 + line[2]
        
        if self.myname not in data.damageDict:
            data.damageDict[self.myname] = numdam
        else:
            data.damageDict[self.myname] += numdam
            
        data.damageList = dictToPairs(data.damageDict)
        data.damageList.sort(key = lambda x: -x[1])

        sumdamage = 0
        numid = 0
        for line in data.damageList:
            line[1] /= self.battleTime
            sumdamage += line[1]
            numid += 1
            if line[0] == self.myname and data.myrank == 0:
                data.myrank = numid
                data.mydamage = line[1]
                sumdamage -= line[1]
                
        for key in self.shieldCounters:
            if int(occdict[key][0]) in [0, ]:
                continue
            if namedict[key][0] not in data.damageDict or data.damageDict[namedict[key][0]] / self.battleTime < 10000:
                continue
            if key == self.mykey:
                continue

            rate = self.shieldCounters[key].shieldDuration[1] / \
                (self.shieldCounters[key].shieldDuration[0] + self.shieldCounters[key].shieldDuration[1] + 1e-10)
            data.rateDict[namedict[key][0]] = rate
            data.durationDict[namedict[key][0]] = self.shieldCounters[key].shieldDuration[1]
            data.breakDict[namedict[key][0]] = self.shieldCounters[key].breakCount
            
        data.equalDPS = data.mydamage / (sumdamage + 1e-10) * (len(data.durationDict) - 1)
        #print(data.equalDPS)
        
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

        MoWenList = []
        XiangZhiList = []
        
        shieldLogDict = {}
                    
        for line in sk:
            item = line[""]
            if self.startTime == 0:
                self.startTime = int(item[2])
            self.finalTime = int(item[2])
                
            if len(item) == 16:
                if item[4] not in MoWenList and item[7] in ["14067", "14298", "14302"]:
                    MoWenList.append(item[4])
                if item[4] not in XiangZhiList and item[7] in ["14231", "14140", "14301"]:
                    XiangZhiList.append(item[4])
                if item[7] == "14231":
                    if item[5] not in shieldLogDict:
                        shieldLogDict[item[5]] = [[int(item[2]), 1]]
                    else:
                        shieldLogDict[item[5]].append([int(item[2]), 1])
                    
            if len(item) == 13:
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
            
    def __init__(self, filename, path, myname):
        self.myname = myname
        super().__init__(filename, path)
        #self.filename = filename
        #self.parseFile(path)
            
            
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
    
class ActorData():
    def __init__(self):
        self.no1Lock = {}
        self.no1Face = {}
        self.no2Hit = {}
        self.no4Hit = {}
        self.no5Hit = {}
        self.no5P2Hit = {}
        self.no6Sword = {}
        self.no6Circle = {}
        self.innerPlace = {}

class XiangZhiData():
    
    def __init__(self):
        self.numheal = 0
        self.numeffheal = 0
        self.numshield = 0
        self.numpurge = 0
        self.mydamage = 0
        self.myrank = 0
        self.battlestat = {}
        self.npchealstat = {}
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
        
        self.spareRateList = []

class XiangZhiAnalysis():
    
    myname = ""
    generator = []
    generator2 = []
    battledate = ""
    mask = 0
    speed = 3770
    
    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s)-1)
    
    def paint(self, filename):
    
        data = self.data
    
        battleDate = self.battledate
        generateDate = time.strftime("%Y-%m-%d", time.localtime())

        width = 750
        height = 750

        def paint(draw, content, posx, posy, font, fill):
            draw.text(
                (posx, posy),
                text = content,
                font = font,
                fill = fill
            )

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
        draw = ImageDraw.Draw(image)

        paint(draw, "敖龙岛战斗记录-奶歌", 265, 10, fontTitle, fillcyan)
        paint(draw, "可爱的奶歌[%s]："%self.myname.strip('"'), 10, 50, fontText, fillblack)

        base = 75
        paint(draw, "在这次敖龙岛之旅中，", 30, base, fontText, fillblack)
        paint(draw, "你一共产生了%d点治疗量，"%data.numheal, 30, base+15, fontText, fillblack)
        paint(draw, "其中有%d点是有效治疗，"%data.numeffheal, 30, base+30, fontText, fillblack)
        paint(draw, "你一共使用了%d次[梅花三弄]，"%data.numshield, 30, base+45, fontText, fillblack)
        paint(draw, "它们是不是也可以算成治疗量的一部分呢。", 30, base+60, fontText, fillblack)

        base = 165
        paint(draw, "每个奶歌都有一个DPS的心，", 30, base, fontText, fillblack)
        paint(draw, "你的高光时刻是在与[%s]的战斗中，"%data.maxDpsName, 30, base+15, fontText, fillblack)
        paint(draw, "如果将[庄周梦]和[桑柔]改为计算在你身上，", 30, base+30, fontText, fillblack)
        paint(draw, "相当于你打了%d点DPS，"%data.maxDps, 30, base+45, fontText, fillblack)
        paint(draw, "是平均数的%.2f倍，"%data.maxEqualDPS, 30, base+60, fontText, fillblack)
        paint(draw, "在所有DPS中排在第%d位，"%data.maxDpsRank, 30, base+75, fontText, fillblack)
        paint(draw, "是不是又觉得自己的门票稳了一些！", 30, base+90, fontText, fillblack)

        base = 285
        paint(draw, "并非每时每刻都能感受到梅花三弄的体贴，", 30, base, fontText, fillblack)
        paint(draw, "整个战斗中，梅花三弄的平均覆盖率是%s%%，"%parseCent(data.overallrate), 30, base+15, fontText, fillblack)
        paint(draw, "其中最高的BOSS是[%s]，覆盖率为%s%%"%(data.maxRateName, parseCent(data.maxRate)), 30, base+30, fontText, fillblack)
        paint(draw, "和你想象中的一样吗？", 30, base+45, fontText, fillblack)

        base = 360
        paint(draw, "DPS们并不都知道奶歌的人间冷暖，", 30, base, fontText, fillblack)
        paint(draw, "盾平均覆盖率最高的是[%s]，达到了%s%%，"%(self.getMaskName(data.maxSingleRateName), parseCent(data.maxSingleRate)), 30, base+15, fontText, fillblack)
        paint(draw, "是因为好好保了盾，还是你更关注他一些?", 30, base+30, fontText, fillblack)
        paint(draw, "而破盾次数最多的是[%s]，整个战斗中有%d次,"%(self.getMaskName(data.maxSingleBreakName), data.maxSingleBreak), 30, base+45, fontText, fillblack)
        paint(draw, "下次知道该把谁放在最后了吧！", 30, base+60, fontText, fillblack)

        base = 450
        paint(draw, "[源思弦]可以说是整个副本最难的BOSS，", 30, base, fontText, fillblack)
        paint(draw, "你在其中使用了%d次[一指回鸾]，"%data.numpurge, 30, base+15, fontText, fillblack)
        paint(draw, "你对[尹青羲]的治疗量是%d点，占比%s%%，"%(data.npcHeal, parseCent(data.npcHealRate)), 30, base+30, fontText, fillblack)
        paint(draw, "在所有奶妈中排名第%d位，"%data.npcRank, 30, base+45, fontText, fillblack)
        paint(draw, "是不是觉得自己能打能奶，文武双全！", 30, base+60, fontText, fillblack)
        
        base = 540
        paint(draw, "治疗职业在副本中一点也不比DPS轻松，", 30, base, fontText, fillblack)
        paint(draw, "按照%d加速计算，"%self.speed, 30, base+15, fontText, fillblack)
        paint(draw, "你在副本中的空闲时间比例为%s%%，"%parseCent(data.spareRate), 30, base+30, fontText, fillblack)
        paint(draw, "快和别的小伙伴比一比，看是谁更划水呀。", 30, base+45, fontText, fillblack)

        paint(draw, "基于以上数据，你的评分为：", 30, 615, fontText, fillblack)
        paint(draw, "GG", 220, 605, fontBig, (255, 255, 0))
        paint(draw, "（此处未实现，待收集数据）", 30, 630, fontText, fillblack)

        paint(draw, "整体治疗量表", 350, 75, fontSmall, fillblack)
        paint(draw, "HPS", 425, 75, fontSmall, fillblack)
        paint(draw, "盾数", 460, 75, fontSmall, fillblack)
        paint(draw, "战斗时间", 500, 75, fontSmall, fillblack)
        h = 75
        for line in data.healTable:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 425, h, fontSmall, fillblack)
            paint(draw, "%d"%line[2], 461, h, fontSmall, fillblack)
            paint(draw, "%s"%parseTime(line[3]), 505, h, fontSmall, fillblack)

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

        paint(draw, "[%s]的等效DPS统计"%data.maxDpsName, 520, 165, fontSmall, fillblack)  
        h = 165
        for line in data.maxDpsTable:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[0]), 520, h, fontSmall, fillblack)
            paint(draw, "%d DPS"%int(line[1]), 595, h, fontSmall, fillblack) 
            if h > 330:
                break

        paint(draw, "平均覆盖率表", 350, 280, fontSmall, fillblack)
        h = 280
        for line in data.rateTable:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 410, h, fontSmall, fillblack) 

        paint(draw, "DPS覆盖率统计", 350, 375, fontSmall, fillblack)
        paint(draw, "全程", 420, 375, fontSmall, fillblack)
        paint(draw, "铁黎", 470, 375, fontSmall, fillblack)
        paint(draw, "陈徽", 495, 375, fontSmall, fillblack)
        paint(draw, "藤原武裔", 520, 375, fontSmall, fillblack)
        h = 375
        for line in data.rateList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[0]), 360, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 420, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][0], 0), 470, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][1], 0), 495, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(data.bossRateDict[line[0]][2], 0), 520, h, fontSmall, fillblack)
            if h > 550:
                break

        paint(draw, "DPS破盾次数", 550, 375, fontSmall, fillblack)
        paint(draw, "全程", 620, 375, fontSmall, fillblack)
        paint(draw, "铁黎", 650, 375, fontSmall, fillblack)
        paint(draw, "陈徽", 675, 375, fontSmall, fillblack)
        paint(draw, "藤原武裔", 700, 375, fontSmall, fillblack)
        h = 375
        for line in data.breakList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[0]), 560, h, fontSmall, fillblack) 
            paint(draw, "%d"%line[1], 620, h, fontSmall, fillblack)
            paint(draw, "%d"%data.bossBreakDict[line[0]][0], 650, h, fontSmall, fillblack) 
            paint(draw, "%d"%data.bossBreakDict[line[0]][1], 675, h, fontSmall, fillblack) 
            paint(draw, "%d"%data.bossBreakDict[line[0]][2], 700, h, fontSmall, fillblack)
            if h > 550:
                break

        paint(draw, "NPC治疗量统计", 345, 580, fontSmall, fillblack)
        h = 580
        for line in data.npcHealList:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[0]), 360, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 440, h, fontSmall, fillblack)
            if h > 630:
                break
                
        paint(draw, "空闲比例表", 500, 580, fontSmall, fillblack)
        h = 580
        for line in data.spareRateList:
            h += 10
            paint(draw, "%s"%line[0], 510, h, fontSmall, fillblack)
            paint(draw, "%s%%"%parseCent(line[1]), 560, h, fontSmall, fillblack)

        paint(draw, "进本时间：%s"%battleDate, 650, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s"%generateDate, 650, 50, fontSmall, fillblack)
        paint(draw, "版本号：1.7.0", 30, 690, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 690, fontSmall, fillblack)

        image.save(filename)
    
    def loadData(self, fileList, path):
        
        for filename in fileList:
            res = XiangZhiStatGenerator(filename, path, self.myname)
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
        
        data = XiangZhiOverallData()

        for line in generator:
            data.numheal += line.data.numheal
            data.numeffheal += line.data.numeffheal
            data.numshield += line.data.numshield
            data.healTable.append([line.bossname.strip('"'), int(line.data.numeffheal / line.battleTime), 
                                   line.data.numshield, line.battleTime])


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
        
        for i in range(len(data.rateList)):
            data.rateList[i][1] /= sumTime * 1000

        data.rateList.sort(key=lambda x:-x[1])
        data.breakList.sort(key=lambda x:-x[1])
        
        for line in data.rateList:
            data.bossRateDict[line[0]] = [0, 0, 0]
        
        for line in data.breakList:
            data.bossBreakDict[line[0]] = [0, 0, 0]
        
        for line in generator:
            bossNameList = ["铁黎", "陈徽", "藤原武裔"]
            for i in range(len(bossNameList)):
                if line.bossname == bossNameList[i]:
                    for line2 in line.data.durationDict:
                        data.bossRateDict[line2][i] = line.data.durationDict[line2] / (line.battleTime * 1000)
                    for line2 in line.data.breakDict:
                        data.bossBreakDict[line2][i] = line.data.breakDict[line2]
        
        #print(data.bossRateDict)
        #print(data.bossBreakDict)
        
        #print(len(data.rateList))
        
        data.maxSingleRate = data.rateList[0][1]
        data.maxSingleRateName = data.rateList[0][0].strip("")
        data.maxSingleBreak = data.breakList[0][1]
        data.maxSingleBreakName = data.breakList[0][0].strip("")
        
        for line in generator:
            if line.bossname == "源思弦":
                data.numpurge = line.data.numpurge
                data.npchealstat = line.data.npchealstat
                data.npcHealList = dictToPairs(data.npchealstat)
                
        data.npcHealList.sort(key=lambda x:-x[1])
        
        findSelf = 0
        for line in data.npcHealList:
            if not findSelf:
                data.npcRank += 1
            if line[0].strip('"') == self.myname.strip('"') and not findSelf:
                data.npcHeal = line[1]
                findSelf = 1
            data.npcSumHeal += line[1]
        data.npcHealRate = data.npcHeal / (data.npcSumHeal + 1e-10)
        
        for line in generator:
            data.sumBusyTime += line.data.sumBusyTime
            data.sumSpareTime += line.data.sumSpareTime
            data.spareRateList.append([line.bossname.strip('"'), line.data.spareRate])
            
        data.spareRate = data.sumSpareTime / (data.sumBusyTime + data.sumSpareTime + 1e-10)
        #print(data.spareRate)
        
        for line in self.generator2:
            namedict = line.rawdata['9'][0]
            if line.bossname == "铁黎":
                print("老一被锁次数：")
                for line2 in line.data.no1Lock:
                    print(namedict[line2][0], line.data.no1Lock[line2])
                print("老一中面向次数：")
                for line2 in line.data.no1Face:
                    print(namedict[line2][0], line.data.no1Face[line2])
            if line.bossname == "陈徽":
                print("老二中面向次数：")
                for line2 in line.data.no2Hit:
                    print(namedict[line2][0], line.data.no2Hit[line2])
            if line.bossname == "源思弦":
                print("老四中技能次数：")
                for line2 in line.data.no4Hit:
                    print(namedict[line2][0], line.data.no4Hit[line2])
            if line.bossname == "驺吾":
                print("老五中技能次数：")
                for line2 in line.data.no5Hit:
                    print(namedict[line2][0], line.data.no5Hit[line2])
                print("老五下阶段中技能次数：")
                for line2 in line.data.no5P2Hit:
                    print(namedict[line2][0], line.data.no5P2Hit[line2])
            if line.bossname == "方有崖":
                print("老六心狐炸人次数：")
                for line2 in line.data.no6Circle:
                    print(namedict[line2][0], line.data.no6Circle[line2])
                print("老六进内场情况：")
                for line2 in line.data.innerPlace:
                    print(namedict[line2][0], line.data.innerPlace[line2])
        
        
        self.data = data
    
    def __init__(self, filelist, path, config):
        self.myname = config.xiangzhiname
        self.mask = config.mask
        self.speed = config.speed
        self.loadData(filelist, path)
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

        bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
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

        for i in range(1, 7):
            if bossPos[i] == -1:
                for j in range(len(selectFileList)):
                    if j > bossPos[i-1] and j < bossPos[i+1] and bossList[j] == 999:
                        bossList[j] = i
                        bossPos[i] = j

        finalList = []
        for i in range(1, 7):
            if bossPos[i] != -1:
                finalList.append(selectFileList[bossPos[i]])
                
        if finalList == "":
            print("没有合适的战斗记录，请确认目录设置或角色是否正确。")

        return finalList
    
    def __init__(self):
        pass
        
class Config():

    items = {}
    
    def checkItems(self):
        try:
            self.playername = self.items["playername"]
            self.basepath = self.items["basepath"]
            self.jx3path = self.items["jx3path"]
            self.xiangzhiname = self.items["xiangzhiname"]
            self.mask = int(self.items["mask"])
            self.speed = int(self.items["speed"])
            assert self.mask in [0, 1]
        except:
            raise Exception("配置文件格式不正确，请确认。如无法定位问题，请删除config.ini，在生成的配置文件的基础上进行修改。")
    
    def printDefault(self):
        g = open("config.ini", "w", encoding="utf-8")
        g.write("""[XiangZhiAnalysis]
playername=
jx3path=
basepath=
xiangzhiname=
mask=0
speed=3770""")
        g.close()
        pass
    
    def setDefault(self):
        self.playername = ""
        self.basepath = ""
        self.jx3path = ""
        self.xiangzhiname = ""
        self.mask = 0
        self.speed = 3770
    
    def __init__(self, filename):
        if not os.path.isfile(filename):
            print("配置文件不存在，使用默认配置并自动生成到config.ini")
            self.setDefault()
            self.printDefault()
        else:
            try:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="utf-8")
                self.items = dict(cf.items("XiangZhiAnalysis"))
                self.checkItems()
            except:
                cf = configparser.ConfigParser()
                cf.read("config.ini", encoding="gbk")
                self.items = dict(cf.items("XiangZhiAnalysis"))
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

        filelist = fileLookUp.getLocalFile()
        print("开始分析。分析耗时可能较长，请耐心等待……")
        
        b = XiangZhiAnalysis(filelist, fileLookUp.basepath, config)
        b.analysis()
        b.paint("result.png")
        
        print("分析完成！结果保存在result.png中")
        
    except Exception as e:
        traceback.print_exc()
        
    os.system('pause')
    
    
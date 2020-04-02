import os
from PIL import Image, ImageFont, ImageDraw
from matplotlib.pyplot import imshow
import numpy as np
import time

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

class ShieldCounter():
    
    shieldLog = []
    breakCount = 0
    shieldDuration = [0, 0]
    startTime = 0
    finalTime = 0
    nowi = 1
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
        


class StatGeneratorBase():
    
    filename = ""
    rawdata = {}
    bossname = ""
    battleTime = 0
    
    def parseFile(self):
        f = open(self.filename, "r")
        s = f.read()
        res, _ = parseLuatable(s, 8, len(s))
        self.rawdata = res
        self.bossname = self.filename.split('_')[1]
        self.battleTime = int(self.filename.split('_')[2].split('.')[0])
    
    def __init__(self, filename):
        self.filename = filename
        self.parseFile()
        pass

class XiangZhiStatGenerator(StatGeneratorBase):
    
    myname = ""
    mykey = ""
    npckey = ""
    startTime = 0
    finalTime = 0
    shieldCounters = {}
    
    def secondStageAnalysis(self):
        res = self.rawdata
        
        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]
        
        data = XiangZhiData()

        num = 0

        for line in sk:
            item = line[""]
            
            if len(item) == 16:
                
                if item[4] == self.mykey and item[11] != '0':
                    data.numheal += int(item[11])
                    data.numeffheal += int(item[12])
                    
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

        numdam = 0
        for key in data.battlestat.keys():
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

        numid = 0
        for line in data.damageList:
            line[1] /= self.battleTime
            numid += 1
            if line[0] == self.myname and data.myrank == 0:
                data.myrank = numid
                data.mydamage = line[1]
                
        for key in self.shieldCounters:
            if int(occdict[key][0]) in [0, ]:
                continue
            if namedict[key][0] not in data.damageDict or data.damageDict[namedict[key][0]] < 10000:
                continue

            rate = self.shieldCounters[key].shieldDuration[1] / \
                (self.shieldCounters[key].shieldDuration[0] + self.shieldCounters[key].shieldDuration[1] + 1e-10)
            data.rateDict[namedict[key][0]] = rate
            data.durationDict[namedict[key][0]] = self.shieldCounters[key].shieldDuration[1]
            data.breakDict[namedict[key][0]] = self.shieldCounters[key].breakCount

        numrate = 0
        sumrate = 0

        for key in data.rateDict:
            numrate += 1
            sumrate += data.rateDict[key]

        data.overallrate = sumrate / (numrate + 1e-10)
        
        self.data = data
    
    def firstStageAnalysis(self):
        
        res = self.rawdata
        
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
                    
            if len(item) == 13:
                if item[6] == "9334": #buff梅花三弄
                    if item[5] not in shieldLogDict:
                        shieldLogDict[item[5]] = [[int(item[2]), int(item[10])]]
                    else:
                        shieldLogDict[item[5]].append([int(item[2]), int(item[10])])
        
        if self.myname == "":
            if len(XiangZhiList) >= 2:
                raise Exception('奶歌的数量不止一个，请手动指示ID')
            elif len(XiangZhiList) == 0:
                raise Exception('没有找到奶歌，请确认数据是否正确')
            else:
                self.mykey = XiangZhiList[0]
                self.myname = namedict[self.mykey][0]
        
        self.shieldCounters = {}
        for key in shieldLogDict:
            self.shieldCounters[key] = ShieldCounter(shieldLogDict[key], self.startTime, self.finalTime)
            self.shieldCounters[key].analysisShieldData()
            
def parseCent(num):
    n = int(num * 10000)
    n1 = str(n // 100)
    n2 = str(n % 100)
    if len(n2) == 1:
        n2 = '0' + n2
    return "%s.%s"%(n1, n2)

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
        self.rateDict = {}
        self.durationDict = {}
        self.breakDict = {}
        self.overallrate = 0
        
class XiangZhiOverallData(XiangZhiData):
    
    def __init__(self):
        XiangZhiData.__init__(self)
        self.healTable = []
        self.dpsTable = []
        self.maxDpsTable = []
        self.maxDpsName = ""
        self.maxDps = 0
        self.maxDpsRank = 999
        
        self.rateTable = []
        self.maxRateName = ""
        self.maxRate = 0
        
        self.rateList = []
        self.breakList = []
        
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

class XiangZhiAnalysis():
    
    myname = ""
    generator = []
    battledate = ""
    
    def paint(self, filename):
        battleDate = self.battledate
        generateDate = time.strftime("%Y-%m-%d", time.localtime())

        width = 600
        height = 600

        def paint(draw, content, posx, posy, font, fill):
            draw.text(
                (posx, posy),
                text = content,
                font = font,
                fill = fill
            )

        image = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
        fontTitle = ImageFont.truetype(font='C:\\Windows\\Fonts\\msyh.ttc', encoding="unic", size=24)
        fontText = ImageFont.truetype(font='C:\\Windows\\Fonts\\msyh.ttc', encoding="unic", size=14)
        fontSmall = ImageFont.truetype(font='C:\\Windows\\Fonts\\msyh.ttc', encoding="unic", size=8)
        fontBig = ImageFont.truetype(font='C:\\Windows\\Fonts\\msyh.ttc', encoding="unic", size=48)
        fillcyan = (0, 255, 255)
        fillblack = (0, 0, 0)
        draw = ImageDraw.Draw(image)

        paint(draw, "敖龙岛战斗记录-奶歌", 190, 10, fontTitle, fillcyan)
        paint(draw, "可爱的奶歌[%s]："%self.myname.strip('"'), 10, 50, fontText, fillblack)

        data = self.data

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
        paint(draw, "在所有DPS中排在第%d位，"%data.maxDpsRank, 30, base+60, fontText, fillblack)
        paint(draw, "是不是又觉得自己的门票稳了一些！", 30, base+75, fontText, fillblack)

        base = 270
        paint(draw, "并非每时每刻都能感受到梅花三弄的体贴，", 30, base, fontText, fillblack)
        paint(draw, "整个战斗中，梅花三弄的平均覆盖率是%s%%，"%parseCent(data.overallrate), 30, base+15, fontText, fillblack)
        paint(draw, "其中最高的BOSS是[%s]，覆盖率为%s%%"%(data.maxRateName, parseCent(data.maxRate)), 30, base+30, fontText, fillblack)
        paint(draw, "和你想象中的一样吗？", 30, base+45, fontText, fillblack)

        base = 345
        paint(draw, "DPS们并不都知道奶歌的人间冷暖，", 30, base, fontText, fillblack)
        paint(draw, "盾平均覆盖率最高的是[%s]，达到了%s%%，"%(data.maxSingleRateName.strip('"'), parseCent(data.maxSingleRate)), 30, base+15, fontText, fillblack)
        paint(draw, "是因为好好保了盾，还是你更关注他一些?", 30, base+30, fontText, fillblack)
        paint(draw, "而破盾次数最多的是[%s]，整个战斗中有%d次,"%(data.maxSingleBreakName.strip('"'), data.maxSingleBreak), 30, base+45, fontText, fillblack)
        paint(draw, "下次知道该把谁放在最后了吧！", 30, base+60, fontText, fillblack)

        base = 435
        paint(draw, "[源思弦]可以说是整个副本最难的BOSS，", 30, base, fontText, fillblack)
        paint(draw, "你在其中使用了%d次[一指回鸾]，"%data.numpurge, 30, base+15, fontText, fillblack)
        paint(draw, "你对[尹青羲]的治疗量是%d点，占比%s%%，"%(data.npcHeal, parseCent(data.npcHealRate)), 30, base+30, fontText, fillblack)
        paint(draw, "在所有奶妈中排名第%d位，"%data.npcRank, 30, base+45, fontText, fillblack)
        paint(draw, "是不是觉得自己能打能奶，文武双全！", 30, base+60, fontText, fillblack)

        paint(draw, "基于以上数据，你的评分为：", 30, 535, fontText, fillblack)
        paint(draw, "GG", 220, 525, fontBig, (255, 255, 0))
        paint(draw, "（此处未实现，待收集数据）", 30, 550, fontText, fillblack)

        paint(draw, "整体治疗量表", 350, 75, fontSmall, fillblack)
        h = 75
        for line in data.healTable:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack)
            paint(draw, "%d HPS"%line[1], 400, h, fontSmall, fillblack)
            paint(draw, "盾数：%d"%line[2], 460, h, fontSmall, fillblack)
            paint(draw, "战斗时间：%d秒"%line[3], 520, h, fontSmall, fillblack)

        paint(draw, "等效DPS表", 320, 165, fontSmall, fillblack)  
        h = 165
        for line in data.dpsTable:
            h += 10
            paint(draw, "%s"%line[0], 330, h, fontSmall, fillblack)
            paint(draw, "%d DPS"%line[1], 370, h, fontSmall, fillblack)
            paint(draw, "排名：%d"%line[2], 420, h, fontSmall, fillblack)

        paint(draw, "[%s]的等效DPS统计"%data.maxDpsName, 470, 165, fontSmall, fillblack)  
        h = 165
        for line in data.maxDpsTable:
            h += 10
            paint(draw, "%s"%line[0].strip('"'), 480, h, fontSmall, fillblack)
            paint(draw, "%d DPS"%int(line[1]), 535, h, fontSmall, fillblack) 
            if h > 290:
                break

        paint(draw, "平均覆盖率表", 350, 250, fontSmall, fillblack)
        h = 250
        for line in data.rateTable:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 410, h, fontSmall, fillblack) 

        paint(draw, "DPS覆盖率统计", 350, 345, fontSmall, fillblack)
        h = 345
        for line in data.rateList:
            h += 10
            paint(draw, "%s"%line[0].strip('"'), 370, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 420, h, fontSmall, fillblack) 
            if h > 500:
                break

        paint(draw, "DPS破盾次数", 480, 345, fontSmall, fillblack)
        h = 345
        for line in data.breakList:
            h += 10
            paint(draw, "%s"%line[0].strip('"'), 490, h, fontSmall, fillblack) 
            paint(draw, "%d"%line[1], 550, h, fontSmall, fillblack)
            if h > 520:
                break

        paint(draw, "NPC治疗量统计", 345, 530, fontSmall, fillblack)
        h = 530
        for line in data.npcHealList:
            h += 10
            paint(draw, "%s"%line[0].strip('"'), 360, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 440, h, fontSmall, fillblack)
            if h > 580:
                break

        paint(draw, "进本时间：%s"%battleDate, 500, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s"%generateDate, 500, 50, fontSmall, fillblack)
        paint(draw, "版本号：1.2.2", 30, 590, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 590, fontSmall, fillblack)

        image.save(filename)
    
    def loadData(self, fileList):
        
        for filename in fileList:
            res = XiangZhiStatGenerator(filename)
            res.firstStageAnalysis()
            res.secondStageAnalysis()
            self.generator.append(res)
            if self.myname == "":
                self.myname = res.myname
            elif self.myname != res.myname:
                raise Exception("全程奶歌名称不一致，请手动指定ID")
                
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
            data.dpsTable.append([line.bossname.strip('"'), line.data.mydamage, line.data.myrank])
            if line.data.myrank < data.maxDpsRank or (line.data.myrank == data.maxDpsRank and line.data.mydamage > data.maxDps):
                data.maxDpsName = line.bossname.strip('"')
                data.maxDps = line.data.mydamage
                data.maxDpsRank = line.data.myrank
                data.maxDpsTable = line.data.damageList

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
        
        
        
        self.data = data
    
    def __init__(self, filelist):
        self.loadData(filelist)
        self.battledate = '-'.join(filelist[0].split('-')[0:3])
        
        
class FileLookUp():
    
    def getLocalFile(self):
        
        filelist = os.listdir()

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
            bossname = selectFileList[i].split('_')[1]
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

        return finalList
    
    def __init__(self):
        pass
    
if __name__ == "__main__":
    filelist = FileLookUp().getLocalFile()
    b = XiangZhiAnalysis(filelist)
    b.analysis()
    b.paint("result.png")
    
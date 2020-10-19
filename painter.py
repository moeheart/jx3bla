from PIL import Image, ImageFont, ImageDraw
import numpy as np
import time
import os
from Constants import *

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

class XiangZhiPainter():
    
    text = 0
    speed = 3770
    mask = 0
    color = 1
    edition = "3.6.3"
    printint = 1
    
    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s)-1)
        
    def getHitDict(self):
        if self.map == "敖龙岛":
            self.hitDict = {"s22520": "锈铁钩锁", 
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
            self.allBoss = ["铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
        elif self.map == "范阳夜变":
            self.hitDict = {"s23621": "隐雷鞭", 
                       "s23700": "短歌式",
                       "b16842": "符咒禁锢",
                       "s24029": "赤镰乱舞·矩形",
                       "s24030": "赤镰乱舞·扇形",
                       "s24031": "赤镰乱舞·圆形",
                       "b17110": "绞首链",
                       "b17301": "不听话的小孩子",
                      }
            self.allBoss = ["周贽", "厌夜", "迟驻", "白某", "安小逢"]
        elif self.map == "达摩洞":
            self.hitDict = {}
            self.allBoss = ["余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳"]
            
    def getScoreInfo(self, score):
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
        for line in rateScale:
            if score >= line[0]:
                self.scoreColor = line[1]
                self.scoreLevel = line[2]
                self.scoreDescribe = line[3]
                break
                
    def getColor(self, occ):
        if self.color == 0:
            return (0, 0, 0)
        if occ[-1] in ['d', 't', 'h', 'p', 'm']:
            occ = occ[:-1]
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
    
    def paint(self, info, saveFile):
    
        self.edition = info["edition"]
    
        battleDate = info["battledate"]
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
            # print("系统中未找到字体文件，将在当前目录下查找msyh.ttc")
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
            self.f = open("%s.txt"%saveFile.split('.')[0], "w")
            
        stat = info["statistics"]

        mapDetail = info["mapdetail"]
        difficulty = mapDetail[:5]
        self.map = mapDetail[5:]
        
        print(info["mapdetail"])
        
        self.speed = 3770
        
        self.getHitDict()
        
        maxRate = 0
        maxRateName = ""
        sumRate = 0
        numRate = 0
        overallrate = 0
        for line in stat["rateTable"]:
            if line[1] > maxRate:
                maxRate = line[1]
                maxRateName = line[0]
            sumRate += line[1]
            numRate += 1
        overallrate = sumRate / (numRate + 1e-10)
        
        sumDrawer = 0
        sumInner = 0
        if "sumDrawer" in stat:
            sumDrawer = stat["sumDrawer"]
        if "sumInner" in stat:
            sumInner = stat["sumInner"]
            
        npcRank = 0
        npcNum = 0
        for i in range(len(stat["npcHealList"])):
            if info["id"] == stat["npcHealList"][i][2]:
                npcRank = i + 1
            npcNum += 1
            
        spareRate = 0
        sumSpare = 0
        numSpare = 0
        for line in stat["spareRateList"]:
            sumSpare += line[1]
            numSpare += 1
        spareRate = sumSpare / (numSpare + 1e-10)
        
        self.getScoreInfo(info["score"])
        
        paint(draw, "%s战斗记录-奶歌"%self.map, 290, 10, fontTitle, fillcyan)
        paint(draw, "可爱的奶歌[%s]："%info["id"], 10, 50, fontText, fillblack)
        write('\n')

        base = 75
        paint(draw, "在这次%s之旅中，"%self.map, 30, base, fontText, fillblack)
        paint(draw, "你一共产生了%d点治疗量，"%stat["numheal"], 30, base+15, fontText, fillblack)
        paint(draw, "其中有%d点是有效治疗，"%stat["numeffheal"], 30, base+30, fontText, fillblack)
        paint(draw, "你一共使用了%d次[梅花三弄]，"%stat["numshield"], 30, base+45, fontText, fillblack)
        paint(draw, "它们是不是也可以算成治疗量的一部分呢。", 30, base+60, fontText, fillblack)
        write('\n')

        base = base + 90
        paint(draw, "每个奶歌都有一个DPS的心，", 30, base, fontText, fillblack)
        paint(draw, "你的高光时刻是在与[%s]的战斗中，"%stat["maxDpsName"], 30, base+15, fontText, fillblack)
        paint(draw, "如果将[庄周梦]和[桑柔]改为计算在你身上，", 30, base+30, fontText, fillblack)
        paint(draw, "相当于你打了%d点DPS，"%stat["maxDps"], 30, base+45, fontText, fillblack)
        paint(draw, "是平均数的%.2f倍，"%stat["maxEqualDPS"], 30, base+60, fontText, fillblack)
        paint(draw, "在所有DPS中排在第%d位，"%stat["maxDpsRank"], 30, base+75, fontText, fillblack)
        paint(draw, "是不是又觉得自己的门票稳了一些！", 30, base+90, fontText, fillblack)
        write('\n')

        base = base + 120
        paint(draw, "并非每时每刻都能感受到梅花三弄的体贴，", 30, base, fontText, fillblack)
        paint(draw, "整个战斗中，梅花三弄的平均覆盖率是%s%%，"%parseCent(overallrate), 30, base+15, fontText, fillblack)
        paint(draw, "其中最高的BOSS是[%s]，覆盖率为%s%%"%(maxRateName, parseCent(maxRate)), 30, base+30, fontText, fillblack)
        paint(draw, "和你想象中的一样吗？", 30, base+45, fontText, fillblack)
        write('\n')

        base = base + 75
        paint(draw, "DPS们并不都知道奶歌的人间冷暖，", 30, base, fontText, fillblack)
        paint(draw, "盾平均覆盖率最高的是[%s]，达到了%s%%，"%(self.getMaskName(stat["maxSingleRateName"]), parseCent(stat["maxSingleRate"])), 30, base+15, fontText, fillblack)
        paint(draw, "是因为好好保了盾，还是你更关注他一些?", 30, base+30, fontText, fillblack)
        paint(draw, "而破盾次数最多的是[%s]，有%d次,"%(self.getMaskName(stat["maxSingleBreakName"]), stat["maxSingleBreak"]), 30, base+45, fontText, fillblack)
        paint(draw, "下次知道该把谁放在最后了吧！", 30, base+60, fontText, fillblack)
        write('\n')

        base = base + 90
        paint(draw, "[%s]可以说是整个副本最难的BOSS，"%stat["hardBOSS"], 30, base, fontText, fillblack)
        paint(draw, "你在其中使用了%d次[一指回鸾]，"%stat["numpurge"], 30, base+15, fontText, fillblack)
        paint(draw, "你对%s的治疗量是%d点，占比%s%%，"%(stat["hardNPC"], stat["npcHeal"], parseCent(stat["npcHealRate"])), 30, base+30, fontText, fillblack)
        paint(draw, "在所有奶妈中排名第%d/%d位，"%(npcRank, npcNum), 30, base+45, fontText, fillblack)
        paint(draw, "是不是觉得自己能打能奶，文武双全！", 30, base+60, fontText, fillblack)
        write('\n')
        
        base = base + 90
        paint(draw, "治疗职业在副本中一点也不比DPS轻松，", 30, base, fontText, fillblack)
        paint(draw, "按照%d加速计算，"%self.speed, 30, base+15, fontText, fillblack)
        paint(draw, "你在副本中的空闲时间比例为%s%%，"%parseCent(spareRate), 30, base+30, fontText, fillblack)
        paint(draw, "快和别的小伙伴比一比，看是谁更划水呀。", 30, base+45, fontText, fillblack)
        write('\n')
        
        base = base + 75
        paint(draw, "当然，大家都要面对相同的副本机制，", 30, base, fontText, fillblack)
        if self.printint:
            paint(draw, "你中了%d次惩罚技能，重伤了%d次，"%(stat["sumHit"], stat["sumDeath"]), 30, base+15, fontText, fillblack)
        else:
            paint(draw, "你中了%.1f次惩罚技能，重伤了%.1f次，"%(stat["sumHit"], stat["sumDeath"]), 30, base+15, fontText, fillblack)
        if self.map == "敖龙岛":
            paint(draw, "在老五连了%d次线，在老六进了%d次内场，"%(stat["sumDrawer"], stat["sumInner"]), 30, base+30, fontText, fillblack)
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
        for line in stat["healTable"]:
            h += 10
            paint(draw, "%s"%line[0], 310, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 355, h, fontSmall, fillblack)
            paint(draw, "%s%%"%parseCent(line[2]), 390, h, fontSmall, fillblack)
            if self.printint:
                paint(draw, "%d/%d"%(line[3], line[4]), 430, h, fontSmall, fillblack)
            else:
                paint(draw, "%.1f/%.1f"%(line[3], line[4]), 430, h, fontSmall, fillblack)
            paint(draw, "%d"%line[5], 460, h, fontSmall, fillblack)
            if self.printint:
                paint(draw, "%d"%line[6], 490, h, fontSmall, fillblack)
            else:
                paint(draw, "%.1f"%line[6], 490, h, fontSmall, fillblack)
            paint(draw, "%s"%parseTime(line[7]), 520, h, fontSmall, fillblack)
            paint(draw, "%.1f"%line[8], 570, h, fontSmall, fillblack)

        write('\n')
        paint(draw, "等效DPS表", 320, 165, fontSmall, fillblack)
        paint(draw, "DPS", 375, 165, fontSmall, fillblack)
        paint(draw, "排名", 410, 165, fontSmall, fillblack)
        paint(draw, "强度", 440, 165, fontSmall, fillblack)
        paint(draw, "人数", 470, 165, fontSmall, fillblack)
        h = 165
        for line in stat["dpsTable"]:
            h += 10
            paint(draw, "%s"%line[0], 330, h, fontSmall, fillblack)
            paint(draw, "%d"%line[1], 370, h, fontSmall, fillblack)
            if self.printint:
                paint(draw, "%d"%line[2], 410, h, fontSmall, fillblack)
                paint(draw, "%.2f"%line[3], 440, h, fontSmall, fillblack)
                paint(draw, "%d"%line[4], 470, h, fontSmall, fillblack)
            else:
                paint(draw, "%.1f"%line[2], 410, h, fontSmall, fillblack)
                paint(draw, "%.2f"%line[3], 440, h, fontSmall, fillblack)
                paint(draw, "%.1f"%line[4], 470, h, fontSmall, fillblack)

        write('\n')
        paint(draw, "[%s]的等效DPS统计"%stat["maxDpsName"], 520, 165, fontSmall, fillblack)  
        h = 165
        for line in stat["maxDpsTable"]:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 520, h, fontSmall, self.getColor(line[3]))
            paint(draw, "%d DPS"%int(line[1]), 595, h, fontSmall, fillblack) 
            if h > 330:
                break

        write('\n')
        h = 250
        paint(draw, "平均覆盖率表", 350, h, fontSmall, fillblack)
        for line in stat["rateTable"]:
            h += 10
            paint(draw, "%s"%line[0], 360, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(line[1]), 410, h, fontSmall, fillblack) 
            
        if self.map == "范阳夜变":
            bossNameList = ["迟驻", "白某", "安小逢"]
        else:
            bossNameList = ["铁黎", "陈徽", "藤原武裔"]

        write('\n')
        h = 345
        paint(draw, "DPS覆盖率统计", 350, 345, fontSmall, fillblack)
        paint(draw, "全程", 420, 345, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[0], 465, 345, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[1], 490, 345, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[2], 515, 345, fontSmall, fillblack)
        
        #print(data.rateList)
        for line in stat["rateList"]:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 360, h, fontSmall, self.getColor(line[3])) 
            paint(draw, "%s%%"%parseCent(line[1]), 420, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(stat["bossRateDict"][line[0]][0], 0), 465, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(stat["bossRateDict"][line[0]][1], 0), 490, h, fontSmall, fillblack) 
            paint(draw, "%s%%"%parseCent(stat["bossRateDict"][line[0]][2], 0), 515, h, fontSmall, fillblack)
            if h > 550:
                break

        write('\n')
        h = 345
        paint(draw, "DPS破盾次数", 550, h, fontSmall, fillblack)
        paint(draw, "全程", 620, h, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[0], 650, h, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[1], 675, h, fontSmall, fillblack)
        paint(draw, "%s"%bossNameList[2], 700, h, fontSmall, fillblack)
        for line in stat["breakList"]:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 560, h, fontSmall, self.getColor(line[3])) 
            if self.printint:
                paint(draw, "%d"%line[1], 620, h, fontSmall, fillblack)
                paint(draw, "%d"%stat["bossBreakDict"][line[0]][0], 650, h, fontSmall, fillblack) 
                paint(draw, "%d"%stat["bossBreakDict"][line[0]][1], 675, h, fontSmall, fillblack) 
                paint(draw, "%d"%stat["bossBreakDict"][line[0]][2], 700, h, fontSmall, fillblack)
            else:
                paint(draw, "%.1f"%line[1], 620, h, fontSmall, fillblack)
                paint(draw, "%.1f"%stat["bossBreakDict"][line[0]][0], 650, h, fontSmall, fillblack) 
                paint(draw, "%.1f"%stat["bossBreakDict"][line[0]][1], 675, h, fontSmall, fillblack) 
                paint(draw, "%.1f"%stat["bossBreakDict"][line[0]][2], 700, h, fontSmall, fillblack)
            if h > 550:
                break

        write('\n')
        h = 550
        paint(draw, "%s治疗量统计"%stat["hardNPC"], 345, h, fontSmall, fillblack)
        for line in stat["npcHealList"]:
            h += 10
            paint(draw, "%s"%self.getMaskName(line[2]), 360, h, fontSmall, self.getColor(line[3]))
            paint(draw, "%d"%line[1], 440, h, fontSmall, fillblack)
            if h > 610:
                break
             
        write('\n')
        h = 550
        paint(draw, "空闲比例表", 500, h, fontSmall, fillblack)
        for line in stat["spareRateList"]:
            h += 10
            paint(draw, "%s"%line[0], 510, h, fontSmall, fillblack)
            paint(draw, "%s%%"%parseCent(line[1]), 560, h, fontSmall, fillblack)
            
        write('\n')
        h = 550
        paint(draw, "犯错记录", 620, h, fontSmall, fillblack)
        for line in stat["hitCount"]:
            if line not in self.hitDict:
                continue
            h += 10
            paint(draw, "%s"%self.hitDict[line], 630, h, fontSmall, fillblack)
            if self.printint:
                paint(draw, "%d"%stat["hitCount"][line], 690, h, fontSmall, fillblack)
            else:
                paint(draw, "%.1f"%stat["hitCount"][line], 690, h, fontSmall, fillblack)
            
        write('\n')
        paint(draw, "面板治疗统计", 345, 620, fontSmall, fillblack)
        h = 620
        w = 420
        for line in self.allBoss:
            paint(draw, "%s"%line, w, h, fontSmall, fillblack)
            w += 30
        h += 10
        for line in stat["healList"]:
            paint(draw, "%s"%self.getMaskName(line[0]), 360, h, fontSmall, self.getColor(line[1]))
            w = 420
            for i in range(2, len(line)):
                paint(draw, "%d"%line[i], w, h, fontSmall, fillblack)
                w += 30
            h += 10
            
        write('\n')
        paint(draw, "评分记录", 730, 70, fontSmall, fillblack)
        h = 70
        for line in stat["printTable"]:
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
        if stat["printTable"] == []:
            paint(draw, "由于全程战斗数据不完整，无法生成评分。", 30, 690, fontText, fillblack)
        else:
            fillRate = (0, 0, 0)
            if self.scoreColor == 0: 
                fillRate = (255, 255, 0)
            elif self.scoreColor == 1:
                fillRate = (255, 128, 128)
            elif self.scoreColor == 2:
                fillRate = (255, 128, 0)
            elif self.scoreColor == 3:
                fillRate = (0, 128, 255)
            elif self.scoreColor == 4:
                fillRate = (128, 255, 0)
            else:
                fillRate = (255, 0, 0)
            paint(draw, "基于以上数据，你的评分为：", 30, 690, fontText, fillblack)
            paint(draw, self.scoreLevel, 220, 680, fontBig, fillRate)
            if "scoreRate" in info:
                paint(draw, "超过了%s%%的奶歌玩家！"%parseCent(info["scoreRate"]), 30, 715, fontText, fillblack)
            paint(draw, self.scoreDescribe, 320, 735, fontTitle, fillRate)
            paint(draw, "（以实际表现为准，评分仅供参考）", 30, 730, fontSmall, fillblack)
            
        write('\n')
        paint(draw, "进本时间：%s"%battleDate, 700, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s"%generateDate, 700, 50, fontSmall, fillblack)
        paint(draw, "难度：%s"%difficulty, 700, 60, fontSmall, fillblack)
        paint(draw, "版本号：%s"%self.edition, 30, 780, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 780, fontSmall, fillblack)

        image.save(saveFile)
        
        if self.text == 1:
            self.f.close()
    
    def __init__(self, printint = 1):
        self.scoreRate = None
        self.printint = printint
        self.edition = EDITION
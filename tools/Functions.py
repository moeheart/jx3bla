# Created by moeheart at 10/11/2020
# 部分简单python对象操作的方法库。

def calculFramesAfterHaste(haste, origin):
    '''
    计算加速过后的帧数.
    params:
    - haste: 加速数值
    - origin: 原始的帧数
    returns:
    - res: 加速过后的帧数
    '''
    #tmp = int(haste / 188.309 * 10.24)   # 100赛季数值
    tmp = int(haste / 438.5625 * 10.24)   # 110赛季数值
    res = int(origin * 1024 / (tmp + 1024))
    return res

def getLength(length, haste):
    '''
    计算固定帧数在计算加速后的毫秒数.
    params:
    - length: 帧数
    - haste: 加速数值
    returns:
    - res: 毫秒数
    '''
    flames = calculFramesAfterHaste(haste, length)
    return flames * 0.0625 * 1000

class SkillCounter():
    '''
    通用的技能统计类，记录技能的施放位置，并给出技能平均延时、数量等数据.
    '''

    def recordSkill(self, time, lastTime=0, delta=-1):
        '''
        记录技能施放的事件.
        params:
        - time: 技能施放的时间点.
        - lastTime: 上一个技能施放的时间点. 如果未提供则自动推断. 技能的施放以开始读条的时间为准。
        - delta: 所记录技能的读条时间.
        returns:
        - res: 推测的减去读条时间的技能位置.
        '''
        if delta == -1:
            delta = self.delta
        if lastTime == 0:
            if len(self.log) != 0:
                lastTime = self.log[-1][1]
            else:
                lastTime = self.startTime
        self.log.append([time, lastTime, delta])
        return time - delta

    def getDelta(self):
        '''
        根据技能id判断技能是否是读条技能，计算出其偏移量.
        '''
        if self.skillid in ["14137", "14300"]:  # 宫，变宫
            self.delta = getLength(24, self.haste)
        if self.skillid in ["14140", "14301"]:  # 徵，变徵
            self.delta = getLength(8, self.haste)

    def getAverageDelay(self):
        '''
        获取技能平均延时.
        returns:
        - res: 平均延时毫秒数.
        '''
        # 在处理时，首先过滤同一技能命中多人的情况，只保留第一次.
        logClear = []
        skillTime = 0
        for line in self.log:
            if line[0] - skillTime > 100:
                logClear.append(line)
                skillTime = line[0]
        num = 0
        sumDelay = 0
        for line in logClear:
            if line[0] - line[1] - line[2] > 3000:  # 不计算>3秒的延迟
                continue
            num += 1
            sumDelay += line[0] - line[1] - line[2]
        #print(self.log)
        #print(logClear)
        return sumDelay / (num + 1e-10)

    def getNum(self):
        '''
        获取技能施放数量.
        '''
        return len(self.log)

    def __init__(self, skillid, startTime, finalTime, haste, delta=-1):
        '''
        构造函数.
        params:
        - skillid: 统计的技能id.
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        - haste: 加速.
        - delta: 指定的技能读条时间.
        '''
        self.skillid = skillid
        self.startTime = startTime
        self.finalTime = finalTime
        self.log = []
        self.haste = haste
        if delta == -1:
            self.delta = 0
            self.getDelta()
        else:
            self.delta = delta

class SkillHealCounter(SkillCounter):
    '''
    治疗技能的统计类，在基类的基础上支持统计治疗量、有效治疗量等数据.
    '''

    def getHeal(self):
        '''
        获取这个技能的总治疗量.
        '''
        sum = 0
        for line in self.log:
            sum += line[3]
        return sum

    def getHealEff(self):
        '''
        获取这个技能的总有效治疗量.
        '''
        sum = 0
        for line in self.log:
            sum += line[4]
        return sum

    def recordSkill(self, time, heal, healEff, lastTime=0, delta=-1):
        '''
        记录技能施放的事件.
        params:
        - time: 技能施放的时间点.
        - heal: 治疗量.
        - healEff: 有效治疗量.
        - lastTime: 上一个技能施放的时间点. 如果未提供则自动推断. 技能的施放以开始读条的时间为准。
        - delta: 所记录技能的读条时间.
        returns:
        - res: 推测的减去读条时间的技能位置.
        '''
        if delta == -1:
            delta = self.delta
        if lastTime == 0:
            if len(self.log) != 0:
                lastTime = self.log[-1][1]
            else:
                lastTime = self.startTime
        self.log.append([time, lastTime, delta, heal, healEff])
        return time - delta


    def __init__(self, skillid, startTime, finalTime, haste, delta=-1):
        '''
        构造函数.
        params:
        - skillid: 统计的技能id.
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        - haste: 加速.
        - delta: 指定的技能读条时间.
        '''
        super().__init__(skillid, startTime, finalTime, haste, delta=-1)

class BuffCounter():
    '''
    通用的buff统计类，记录buff的获取、消亡、层数，并给出覆盖率、存在时间等指标.
    '''

    def setState(self, time, stack):
        '''
        设置特定时间点buff的层数.
        无论是获得还是消亡均可用这个方法。对应的层数的有效时间即是这个时刻到下一个时刻中间的部分。
        params:
        - time: 获得buff的时刻.
        - stack: buff层数，可以为0.
        '''
        self.log.append([int(time), int(stack)])

    def checkState(self, time):
        '''
        查询特定时刻buff的层数.
        params:
        - time: 要查询的时刻.
        returns:
        - res: 层数结果.
        '''
        res = 0
        if len(self.log) == 0:
            return 0
        for i in range(1, len(self.log)):
            if int(time) < self.log[i][0]:
                res = self.log[i - 1][1]
                break
        else:
            res = self.log[-1][1]
        return res

    def buffTimeIntegral(self):
        '''
        获取全程buff层数对时间的积分.
        这个方法可以用于计算覆盖率、平均层数等.
        returns:
        - time: 积分结果.
        '''
        time = 0
        for i in range(len(self.log) - 1):
            time += self.log[i][1] * (self.log[i+1][0] - self.log[i][0])
        if len(self.log) > 0:
            time += self.log[-1][1] * (self.finalTime - self.log[-1][0])
        return time

    def sumTime(self):
        '''
        获取战斗总时间.
        returns:
        - res: 战斗总时间.
        '''
        return self.finalTime - self.startTime

    def __init__(self, buffid, startTime, finalTime):
        '''
        构造函数.
        params:
        - buffid: 统计的buffid，暂时没有实际作用，仅供记录用.
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        '''
        self.buffid = buffid
        self.startTime = startTime
        self.finalTime = finalTime
        self.log = [[startTime, 0]]
        
def parseEdition(e):
    '''
    封装版本号，得到对应的代表数。
    '''
    s = e.split('.')
    if "beta" in s[2]:
        return 0
    if len(s) == 3:
        return int(s[0]) * 1000000 + int(s[1]) * 1000 + int(s[2])
    elif len(s) == 2:
        return int(s[0]) * 1000000 + int(s[1]) * 1000
    else:
        return int(s[0]) * 1000000
        
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
    
def DestroyRaw(raw):
    '''
    销毁一个raw数据以释放内存。
    '''
    raw['16'] = []

def getOccType(occ):
    '''
    根据门派获取团队定位(dps/T/奶)
    params
    - occ 门派代码。
    return
    - 字符串，为tank/dps/healer之一。
    '''
    if occ in ['1t', '3t', '10t', '21t']:
        return "tank"
    elif occ in ['2h', '5h', '6h', '22h', '212h']:
        return "healer"
    else:
        return "dps"
        
def ConvertRgbToStr(res):
    '''
    将数组形式的RGB代码转换为字符串形式
    params
    - res 数组形式的RGB代码
    '''
    return "#%s%s%s"%(str(hex(res[0]))[-2:].replace('x', '0'), 
        str(hex(res[1]))[-2:].replace('x', '0'),
        str(hex(res[2]))[-2:].replace('x', '0'))
    
def getColor(occ):
    '''
    根据门派获取颜色。
    params
    - occ 门派代码。
    return
    - 颜色RGB代码。
    '''
    if occ[-1] in ['d', 't', 'h', 'p', 'm']:
        occ = occ[:-1]
    colorDict = {"0": (0, 0, 0), 
                 "1": (210, 180, 0),#少林
                 "2": (127, 31, 223),#万花
                 "4": (56, 175, 255),#纯阳
                 "5": (255, 127, 255),#七秀
                 "3": (160, 0, 0),#天策
                 "8": (220, 220, 0),#藏剑
                 "9": (205, 133, 63),#丐帮
                 "10": (253, 84, 0),#明教
                 "6": (63, 31, 159),#五毒
                 "7": (0, 133, 144),#唐门
                 "21": (180, 60, 0),#苍云
                 "22": (100, 250, 180),#长歌
                 "23": (71, 73, 166),#霸刀
                 "24": (195, 171, 227),#蓬莱
                 "25": (161, 9, 34),#凌雪
                 "211": (166, 83, 251),#衍天
                 "212": (0, 0, 0),#药宗
                }
    res = (0, 0, 0)
    if occ in colorDict:
        res = colorDict[occ]
    return "#%s%s%s"%(str(hex(res[0]))[-2:].replace('x', '0'), 
                      str(hex(res[1]))[-2:].replace('x', '0'),
                      str(hex(res[2]))[-2:].replace('x', '0'))

def getPotColor(level):
    '''
    在分锅记录中，根据锅的等级获取颜色。
    params
    - occ 等级。
    return
    - 颜色RGB代码。
    '''
    if level == 0:
        return "#777777"
    elif level == 1:
        return "#000000"
    else:
        return "#0000ff"

def dictToPairs(dict):
    pairs = []
    for key in dict:
        pairs.append([key, dict[key]])
    return pairs

def parseTime(time):
    if time < 60:
        return "%ds" % time
    else:
        if time % 60 == 0:
            return "%dm" % (time / 60)
        else:
            return "%dm%ds" % (time / 60, time % 60)

def roundCent(num, digit=4):
    '''
    保留特定的小数位数，并仍保持浮点数形式.
    '''
    return int(num * (10 ** digit)) / (10 ** digit)

def parseCent(num, digit=2):
    n = int(num * 10000)
    n1 = str(n // 100)
    n2 = str(n % 100)
    if len(n2) == 1:
        n2 = '0' + n2
    if digit == 2:
        return "%s.%s" % (n1, n2)
    else:
        return "%s" % n1
        
        
def checkOccDetailBySkill(default, skillID, damage):
    '''
    根据特征技能判定双心法门派的具体心法.
    '''
    #if skillID in ["18207", "18773"] and int(damage) > 10000:
    #    return '3d'
    #elif skillID in ["18207", "18773"] and int(damage) < 3000:
    #    return '3t'
    if skillID in ["2636"]:
        return '2d'
    elif skillID in ["101", "138", "14664"]:
        return '2h'
    elif skillID in ["444"]:
        return '3d'
    elif skillID in ["15115"]:
        return '3t'
    elif skillID in ["365", "2699"]:
        return '4p'
    elif skillID in ["301", "367"]:
        return '4m'
    elif skillID in ["2707", "2716"]:
        return '5d'
    elif skillID in ["565", "554", "555"]:
        return '5h'
    elif skillID in ["2572"]:
        return '1d'
    elif skillID in ["2589", "246", "15195"]:
        return '1t'
    elif skillID in ["3979"]:
        return '10d'
    elif skillID in ["3980", "3982", "3985"]:
        return '10t'
    elif skillID in ["2210", "2211", "2227"]:
        return '6d'
    elif skillID in ["2232", "2233", "2957"]:
        return '6h'
    elif skillID in ["3098", "3096", "18672"]:
        return '7p'
    elif skillID in ["3357", "3111", "3109"]:
        return '7m'
    elif skillID in ["13391", "15072"]:
        return '21t'
    elif skillID in ["14067", "14298", "14302"]:
        return '22d'
    elif skillID in ["14231", "14140", "14301"]:
        return '22h'
    elif skillID in ["27551", "27554", "28081"]:
        return '212d'
    elif skillID in ["27621", "27623", "28083"]:
        return '212h'
    else:
        return default
        
def checkOccDetailByBuff(default, buffID):
    if buffID in ["17885"]:
        return default + 't'
    elif buffID in ["7671"]:
        return '3d'
    elif buffID in ["14309"]:
        return '21d'
    else:
        return default
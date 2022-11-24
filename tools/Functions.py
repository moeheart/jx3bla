# Created by moeheart at 10/11/2020
# 部分简单python对象操作的方法库。

from Constants import *
from tools.Attribute import *

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
    #tmp = int(haste / 438.5625 * 10.24)   # 110赛季数值
    tmp = int(haste / getCoefficient("加速") * 1024)
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

def safe_divide(x, y):
    '''
    计算x/y的值，并防止出现0/0的错误.
    如果x=y=0, 返回0; 如果x!=0, y=0, 返回1e+10或-1e+10.
    '''
    if y != 0:
        return x / y
    elif x == 0:
        return 0
    elif x > 0:
        return 1e+10
    else:
        return -1e+10

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
        if self.skillid in ["27622"]:  # 白芷含芳
            self.delta = getLength(24, self.haste)
        if self.skillid in ["27624"]:  # 当归四逆
            self.delta = getLength(8, self.haste)
        if self.skillid in ["138", "140"]:  # 提针，彼针
            self.delta = getLength(24, self.haste)
        if self.skillid in ["142"]:  # 长针
            self.delta = getLength(48, self.haste)
        if self.skillid in ["28541"]:  # 泷雾
            self.delta = getLength(8, self.haste)
        if self.skillid in ["2232"]:  # 冰蚕牵丝
            self.delta = getLength(24, self.haste)
        if self.skillid in ["6252"]:  # 醉舞九天
            self.delta = getLength(16, self.haste)

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
            sumDelay += max(line[0] - line[1] - line[2], 0)
            # print("[Delay]", line[0] - line[1] - line[2])
        # print("=======")
        return safe_divide(sumDelay, num)

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
            if not line[5]:
                sum += line[3]
        return sum

    def getHealEff(self):
        '''
        获取这个技能的总有效治疗量.
        '''
        sum = 0
        for line in self.log:
            if not line[5]:
                sum += line[4]
        return sum

    def getNum(self):
        '''
        获取技能施放数量.
        '''
        sum = 0
        for line in self.log:
            if not line[5]:
                sum += 1
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
        while self.excludePos < len(self.exclude) and time > self.exclude[self.excludePos][0]:
            self.excludeStatus = self.exclude[self.excludePos][1]
            self.excludePos += 1

        if delta == -1:
            delta = self.delta
        if lastTime == 0:
            if len(self.log) != 0:
                lastTime = self.log[-1][0]
            else:
                lastTime = self.startTime
        self.log.append([time, lastTime, delta, heal, healEff, self.excludeStatus])
        return time - delta

    def __init__(self, skillid, startTime, finalTime, haste, delta=-1, exclude=[]):
        '''
        构造函数.
        params:
        - skillid: 统计的技能id.
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        - haste: 加速.
        - delta: 指定的技能读条时间.
        - exclude: 不占统计的时间段，以log格式表示.
        '''
        super().__init__(skillid, startTime, finalTime, haste, delta=-1)
        self.exclude = exclude
        self.excludePos = 0
        self.excludeStatus = 0

class SkillCounterAdvance(SkillHealCounter):
    '''
    扩展技能统计类，在基类的基础上支持最大可能数量统计.
    '''

    def getHeal(self):
        '''
        获取这个技能的总治疗量.
        '''
        sum = 0
        for line in self.log:
            if not line[5]:
                sum += line[3]
        return sum

    def getHealEff(self):
        '''
        获取这个技能的总有效治疗量.
        '''
        sum = 0
        for line in self.log:
            if not line[5]:
                sum += line[4]
        return sum

    def getNum(self):
        '''
        获取技能施放数量.
        '''
        sum = 0
        for line in self.log:
            if not line[5]:
                sum += 1
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
        while self.excludePos < len(self.exclude) and time > self.exclude[self.excludePos][0]:
            self.excludeStatus = self.exclude[self.excludePos][1]
            self.excludePos += 1

        if delta == -1:
            delta = self.delta
        if lastTime == 0:
            if len(self.log) != 0:
                lastTime = self.log[-1][0]
            else:
                lastTime = self.startTime
        self.log.append([time, lastTime, delta, heal, healEff, self.excludeStatus])
        return time - delta

    def getMaxPossible(self):
        '''
        获取技能最大可能的施放次数.
        '''
        if self.cd == 0:
            return 99999
        else:
            return int((self.finalTime - self.startTime) / self.cd) + self.stack

    def __init__(self, skillInfoSingle, startTime, finalTime, haste, delta=-1, exclude=[]):
        '''
        构造函数.
        params:
        - skillInfoSingle: 技能信息数组.
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        - haste: 加速.
        - delta: 指定的技能读条时间.
        - exclude: 不占统计的时间段，以log格式表示.
        '''
        self.skillid = skillInfoSingle[2][0]
        self.startTime = startTime
        self.finalTime = finalTime
        self.log = []
        self.haste = haste
        if delta == -1:
            self.delta = 0
            self.getDelta()
        else:
            self.delta = delta
        self.cd = skillInfoSingle[8] * 1000
        self.stack = skillInfoSingle[9]
        self.name = skillInfoSingle[1]
        self.exclude = exclude
        self.excludePos = 0
        self.excludeStatus = 0

class IntervalCounter():
    '''
    区间统计类，用于在时间先后顺序可能错乱的情况下取代BuffCounter，其在结束时可以安全转化为log格式.
    '''

    def recordInterval(self, start, end, exclude=0):
        '''
        记录一个区间.
        - start: 区间开始时间.
        - end: 区间结束时间.
        - exclude: 是否为排除的区间.
        '''
        if start >= end:
            return
        if start < self.startTime:
            start = self.startTime
        if end > self.finalTime:
            end = self.finalTime
        self.intervals.append([start, end, exclude])

    def export(self):
        '''
        导出为log格式.
        returns
        - res: logs格式的结果，按覆盖为1，未覆盖为0判定.
        '''
        self.intervals.sort(key=lambda x: x[0])
        effIntervals = []
        excludeTime = 0
        for line in self.intervals:
            if line[2] == 0:
                if effIntervals == [] or line[0] > effIntervals[-1][1]:
                    if line[0] > excludeTime:
                        effIntervals.append([line[0], line[1]])
                    elif line[1] > excludeTime:
                        effIntervals.append([excludeTime, line[1]])
                    else:
                        pass  # 被删除部分完全覆盖，不记录
                elif line[1] > effIntervals[-1][1]:
                    effIntervals[-1][1] = line[1]
            else:
                # 是排除形式的区间
                if effIntervals != []:
                    if effIntervals[-1][1] < line[0]:
                        excludeTime = max(excludeTime, line[1])
                    elif effIntervals[-1][1] < line[1]:
                        effIntervals[-1][1] = line[0]
                        excludeTime = max(excludeTime, line[1])
                    else:
                        prevEnd = effIntervals[-1][1]
                        effIntervals[-1][1] = line[0]
                        effIntervals.append([line[1], prevEnd])
                        excludeTime = 0
                else:
                    excludeTime = max(excludeTime, line[1])

        res = [[self.startTime, 0]]
        if effIntervals != []:
            if effIntervals[0][0] == self.startTime:
                del res[0]
            for line in effIntervals:
                res.append([line[0], 1])
                res.append([line[1], 0])
                assert line[0] <= line[1]
                assert line[1] >= self.startTime
                assert line[1] <= self.finalTime
        if res[-1][1] == 1:
            res.append([self.finalTime, 0])
        if res[-1][0] != self.finalTime:
            res.append([self.finalTime, 0])
        return res

    def __init__(self, startTime, finalTime):
        '''
        构造函数.
        params:
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        '''
        self.startTime = startTime
        self.finalTime = finalTime
        self.intervals = []

class BuffCounter():
    '''
    通用的buff统计类，记录buff的获取、消亡、层数，并给出覆盖率、存在时间等指标.
    '''

    def setStateSafe(self, time, stack):
        '''
        设置特定时间点buff的层数.
        如果类中buff有晚于这个时间点的记录，则将其覆盖.
        params:
        - time: 获得buff的时刻.
        - stack: buff层数，可以为0.
        '''
        if self.log != [] and self.log[-1][0] > time:
            del self.log[-1]
        if time < self.startTime:
            time = self.startTime
        if time > self.finalTime:
            time = self.finalTime
        self.log.append([int(time), int(stack)])

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

    def buffTimeIntegral(self, exclude=[]):
        '''
        获取全程buff层数对时间的积分.
        这个方法可以用于计算覆盖率、平均层数等.
        params:
        - exclude: 不参与记录的时间段，同样用log形式表示.
        returns:
        - time: 积分结果.
        '''

        lastTime = self.startTime
        lastStack = 0
        excluding = 0
        sumTime = 0
        i = 0
        j = 0
        while i < len(self.log) or j < len(exclude):
            if i < len(self.log):
                timeX = self.log[i][0]
                valueX = self.log[i][1]
            else:
                timeX = self.finalTime + 999999999
                valueX = 0
            if j < len(exclude):
                timeY = exclude[j][0]
                valueY = exclude[j][1]
            else:
                timeY = self.finalTime + 999999999
                valueY = 0
            if timeX < timeY:
                if not excluding:
                    sumTime += lastStack * (timeX - lastTime)
                lastTime = timeX
                lastStack = valueX
                i += 1
            else:
                if not excluding:
                    sumTime += lastStack * (timeY - lastTime)
                lastTime = timeY
                excluding = valueY
                j += 1
        if lastTime < self.finalTime:
            if not excluding:
                sumTime += lastStack * (self.finalTime - lastTime)
        return sumTime

        # sumTime = 0
        # for i in range(len(self.log) - 1):
        #     sumTime += self.log[i][1] * (self.log[i+1][0] - self.log[i][0])
        # if len(self.log) > 0:
        #     sumTime += self.log[-1][1] * (self.finalTime - self.log[-1][0])
        # return sumTime

    def shrink(self, threshold=100):
        '''
        对记录进行收缩，减少大小的同时优化在界面显示时的效果.
        params:
        - threshold: 融合的最小间隔
        '''
        i = 1
        while i < len(self.log):
            if i+1 < len(self.log) and self.log[i+1][0] - self.log[i][0] < threshold:
                del self.log[i]
            if self.log[i][1] == self.log[i-1][1]:
                del self.log[i]
                i -= 1
            i += 1

    def sumTime(self, exclude=[]):
        '''
        获取战斗总时间.
        returns:
        - res: 战斗总时间.
        '''

        lastTime = self.startTime
        lastStack = 1
        sumTime = 0
        for line in exclude:
            sumTime += lastStack * (line[0] - lastTime)
            lastTime = line[0]
            lastStack = 1 - line[1]
        sumTime += lastStack * (self.finalTime - lastTime)
        return sumTime

        # return self.finalTime - self.startTime

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

class HotCounter(BuffCounter):
    '''
    HOT的统计类.
    继承buff的统计类，考虑HOT的持续时间等指标。
    '''

    def getHeatTable(self, interval=500, decay=1):
        '''
        获取单个玩家的覆盖率热力表.
        params:
        - interval: 间隔.
        - decay: 是否衰减.
        returns:
        - 结果对象
        '''
        nowi = 0
        result = {"interval": interval, "timeline": []}
        for nowTime in range(self.startTime, self.finalTime, interval):
            single = 0
            while nowi < len(self.log) and self.log[nowi][0] < nowTime:
                nowi += 1
            if len(self.log) > 0 and nowi > 0 and self.log[nowi-1][1] > 0:
                if decay:
                    single = max(safe_divide(self.log[nowi-1][2] + self.log[nowi-1][0] - nowTime, self.log[nowi-1][2]), 0)
                else:
                    single = self.log[nowi - 1][1]
            result["timeline"].append(single)
        return result

    def setState(self, time, stack, duration):
        '''
        设置特定时间点buff的层数.
        无论是获得还是消亡均可用这个方法。对应的层数的有效时间即是这个时刻到下一个时刻中间的部分。
        params:
        - time: 获得buff的时刻.
        - stack: buff层数，可以为0.
        - duration: 预计的持续时间.
        '''
        self.log.append([int(time), int(stack), int(duration)])

    def __init__(self, shieldLog, startTime, finalTime):
        '''
        初始化.
        '''
        super().__init__(shieldLog, startTime, finalTime)

class SkillLogCounter():
    '''
    技能统计类.
    TODO: 扩展这个类的功能，支持更多统计.
    '''
    skillLog = []
    actLog = []
    startTime = 0
    finalTime = 0
    speed = 3770
    sumBusyTime = 0
    sumSpareTime = 0

    def getLength(self, length):
        flames = calculFramesAfterHaste(self.speed, length)
        return flames * 0.0625 * 1000

    def analysisSkillData(self):
        if self.actLog != []:
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

    def __init__(self, skillLog, startTime, finalTime, speed=3770, actLog=[]):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed
        self.actLog = actLog

class ShieldCounterNew(BuffCounter):
    '''
    盾的统计类.
    继承buff的统计类，加入获得次数、破盾次数等指标.
    '''

    def inferFirst(self):
        '''
        根据记录尝试推导战斗开始前是否存在盾，若存在则强制修改最开始的情形为有盾.
        '''
        if len(self.log) > 1 and self.log[1][1] == 0:
            self.log[0][1] = 1

    def countCast(self):
        '''
        计算盾施放的次数.
        根据buff做推断，消失间隔小于500ms的视为没有消失.
        returns:
        - num 盾施放的次数.
        '''
        num = 0
        lastTime = 0
        lastStack = 0
        for line in self.log:
            if line[1] == 1 and lastStack == 0 and line[0] - lastTime > 500:
                num += 1
            lastTime = line[0]
            lastStack = line[1]
        return num

    def countBreak(self):
        '''
        计算破盾的次数.
        直接通过施放的次数推导.
        returns:
        - num 破盾的次数.
        '''
        num = self.countCast()
        if self.checkState(self.finalTime) == 1:
            num -= 1
        return num

    def getHeatTable(self, interval=500):
        '''
        获取单个玩家的覆盖率热力表.
        params:
        - interval: 间隔
        returns:
        - 结果对象
        '''
        nowi = 0
        result = {"interval": interval, "timeline": []}
        for nowTime in range(self.startTime, self.finalTime, interval):
            single = 0
            while nowi < len(self.log) and self.log[nowi][0] < nowTime:
                nowi += 1
            if len(self.log) > 0 and nowi > 0:
                single = self.log[nowi-1][1]
            result["timeline"].append(single)
        return result

    def __init__(self, shieldLog, startTime, finalTime):
        '''
        初始化.
        '''
        super().__init__(shieldLog, startTime, finalTime)
        
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
        
# def ConvertRgbToStr(res):
#     '''
#     将数组形式的RGB代码转换为字符串形式
#     params
#     - res 数组形式的RGB代码
#     '''
#     return "#%s%s%s" % (str(hex(res[0]))[-2:].replace('x', '0'),
#                         str(hex(res[1]))[-2:].replace('x', '0'),
#                         str(hex(res[2]))[-2:].replace('x', '0'))

def getColorHex(color):
    '''
    根据数组形式的颜色获取16进制颜色代码.
    '''
    return "#%s%s%s"%(str(hex(color[0]))[-2:].replace('x', '0'),
                      str(hex(color[1]))[-2:].replace('x', '0'),
                      str(hex(color[2]))[-2:].replace('x', '0'))

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
    res = (0, 0, 0)
    if occ in COLOR_DICT:
        res = COLOR_DICT[occ]
    return getColorHex(res)

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
    if time - int(time) == 0:
        if time < 60:
            return "%ds" % time
        else:
            if time % 60 == 0:
                return "%dm" % (time / 60)
            else:
                return "%dm%ds" % (time / 60, time % 60)
    else:
        if time < 60:
            return "%.1fs" % time
        else:
            return "%dm%.1fs" % (time / 60, time % 60)

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

def countCluster(teamLog, teamLastTime, event):
    '''
    根据HOT的获取事件提取组队聚类信息.
    params:
    - teamLog: 玩家两两配对的事件.
    - teamLastTime: 玩家上次获取HOT的时间.
    - event: HOT事件.
    '''
    if event.target in teamLastTime:
        teamLastTime[event.target] = event.time
    else:
        return teamLog, teamLastTime
    # print("[teamLastTime]", event.time, teamLastTime)
    for player in teamLastTime:
        if event.time - teamLastTime[player] < 100:
            if player not in teamLog[event.target]:
                teamLog[event.target][player] = 0
            teamLog[event.target][player] += 1
            if event.target != player:
                if event.target not in teamLog[player]:
                    teamLog[player][event.target] = 0
                teamLog[player][event.target] += 1
    return teamLog, teamLastTime

def getRateStatus(rate, thres0, thres1, thres2):
    '''
    根据阈值来给出打分结果.
    params:
    - rate: 打分参数.
    - thres0: 为0时的阈值，大于等于这个数时返回0.
    - thres1: 为1时的阈值，大于等于这个数但小于thres0时返回1.
    - thres2: 为2时的阈值，大于等于这个数但小于thres1时返回2.
    returns:
    - status: 结果.
    '''
    if rate >= thres0 / 100:
        return 0
    elif rate >= thres1 / 100:
        return 1
    elif rate >= thres2 / 100:
        return 2
    else:
        return 3

def finalCluster(teamLog):
    '''
    根据组队聚类信息计算聚类结果.
    params:
    - teamLog: 玩家两两配对的事件.
    returns:
    - teamCluster: 聚类结果.
    - numCluster: 聚类结果中每个类别的数量.
    '''
    teamCluster = {}
    for player in teamLog:
        teamCluster[player] = 0
    nTeam = 0
    numCluster = [0]

    # 聚类5次
    for _ in range(5):
        maxValue = 0
        maxPlayer = ""
        for player in teamLog:
            if teamCluster[player] == 0:
                value = teamLog[player].get(player, 0)
                if value > maxValue:
                    maxValue = value
                    maxPlayer = player
        if maxPlayer == "":
            break
        player = maxPlayer
        singleRes = []
        for playerT in teamLog[player]:
            singleRes.append([playerT, teamLog[player][playerT]])
        singleRes.sort(key=lambda x: -x[1])
        j = 4  # 最多选5人
        while len(singleRes) <= j or (j >= 1 and safe_divide(singleRes[j-1][1], singleRes[j][1]) >= 3):
            j -= 1
        # print(singleRes)
        # print(j)
        if j >= 1:
            nTeam += 1
            numCluster.append(0)
            for i in range(0, j+1):
                teamCluster[singleRes[i][0]] = nTeam
                numCluster[nTeam] += 1
        else:
            teamCluster[player] = -1

    # print(nTeam)

    # 为剩余角色聚类
    hasRemain = 0
    for player in teamCluster:
        if teamCluster[player] <= 0:
            if not hasRemain:
                hasRemain = 1
                nTeam += 1
                numCluster.append(0)
            teamCluster[player] = nTeam
            numCluster[nTeam] += 1

    # print(teamCluster)
    # print(numCluster)

    return teamCluster, numCluster

def getCoefficient(coeff):
    '''
    获取对应变量的等级系数.
    '''
    if CHAPTER == 110:
        if coeff in COEFF110:
            return COEFF110[coeff]
        else:
            return 1
    elif CHAPTER == 120:
        if coeff in COEFF120:
            return COEFF120[coeff]
        else:
            return 1
        
def checkOccDetailBySkill(default, skillID, damage):
    '''
    根据特征技能判定双心法门派的具体心法.
    '''
    #if skillID in ["18207", "18773"] and int(damage) > 10000:
    #    return '3d'
    #elif skillID in ["18207", "18773"] and int(damage) < 3000:
    #    return '3t'
    if skillID in ["25587"]:
        return default + 't'
    elif skillID in ["2636"]:
        return '2d'
    elif skillID in ["101", "138", "14664", "28541"]:
        return '2h'
    elif skillID in ["18740"]:
        return '3d'
    elif skillID in ["15115", "4094"]:
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
    elif skillID in ["2210", "2211", "2227", "13472", "29573", "25019"]:
        return '6d'
    elif skillID in ["2232", "2233", "2957"]:
        return '6h'
    elif skillID in ["3098", "3096", "18672", "3227"]:
        return '7p'
    elif skillID in ["3357", "3111", "3109", "3401", "3228", "3105"]:
        return '7m'
    elif skillID in ["13391", "15072"]:
        return '21t'
    elif skillID in ["14067", "14298", "14302"]:
        return '22d'
    elif skillID in ["14231", "14140", "14301", "14137", "14300"]:
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
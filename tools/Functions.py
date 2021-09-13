# Created by moeheart at 10/11/2020
# 部分简单python对象操作的方法库。

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
                res = self.log[i - 1][1]
                break
        else:
            res = self.log[-1][1]
        return res

    def sumTime(self):
        time = 0
        for i in range(len(self.log) - 1):
            time += self.log[i][1] * (self.log[i + 1][0] - self.log[i][0])
        return time

    def __init__(self, buffid, startTime, finalTime):
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
    elif occ in ['2h', '5h', '6h', '22h']:
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


def calculSpeed(speed, origin):
    #tmp = int(speed / 188.309 * 10.24)   # 100赛季数值
    tmp = int(speed / 438.5625 * 10.24)   # 110赛季数值
    y = int(origin * 1024 / (tmp + 1024))
    return y


def parseTime(time):
    if time < 60:
        return "%ds" % time
    else:
        if time % 60 == 0:
            return "%dm" % (time / 60)
        else:
            return "%dm%ds" % (time / 60, time % 60)


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
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
        # print(nowobj)
        c = s[nowi]
        if c == "[":
            if nowitems != []:
                nowobj[nowkey] = nowitems
                nowkey = ""
                nowitem = ""
                nowitems = []
            keystart = 1
        elif c == "{":
            # print(nowi)
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
    #if skillID in ["18207", "18773"] and int(damage) > 10000:
    #    return '3d'
    #elif skillID in ["18207", "18773"] and int(damage) < 3000:
    #    return '3t'
    if skillID in ["2636"]:
        return '2d'
    elif skillID in ["101", "138", "14664"]:
        return '2h'
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
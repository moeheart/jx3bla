# Created by moeheart at 09/06/2021
# 读取数据的方法库，维护从jx3dat, jcl读取数据的方法。

# class FormattedBattleLog():
#     '''
#     格式化的战斗记录类，可以从jx3dat或jcl文件生成。
#     '''
#
#     def generate_from_jx3dat(self, raw):
#         '''
#         根据处理过的jx3dat格式的战斗复盘，生成对应的格式化复盘。
#         params:
#         - raw raw格式的复盘
#         returns:
#         - 格式化的复盘，由一个对象维护。
#         '''
#         return {}
#
#     def __init__(self):
#         pass

class LuaTableAnalyser():
    '''
    Lua Table到json形式的python dict的解析类，中间维护一个显示百分比的算法。
    json形式更易于存储、处理和理解，但对于数组标签与自然情形混合的情况无法正确推导, 很多时候""实际上代表"1"。
    '''

    def parseLuatable(self, n, maxn):

        numLeft = 0
        nowi = n
        nowobj = {}
        nowkey = ""
        keystart = 0
        nowitem = ""
        nowitems = []
        nowquote = 0

        while True:

            if nowi > self.nextI:
                self.lastPercent += 1
                if self.hasWindow:
                    self.window.setNotice({"t2": "已完成：%d%%" % self.lastPercent, "c2": "#0000ff"})
                self.nextI = int((self.lastPercent + 1) * self.maxn / 100)

            c = self.s[nowi]
            if c == "[":
                if nowitems != []:
                    nowobj[nowkey] = nowitems
                    nowkey = ""
                    nowitem = ""
                    nowitems = []
                keystart = 1
            elif c == "{":
                # print(nowi)
                jdata, pn = self.parseLuatable(nowi + 1, maxn)
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

    def analyse(self, s):
        self.s = s
        self.lastPercent = 0
        self.maxn = len(self.s)
        self.nextI = int((self.lastPercent + 1) * self.maxn / 100)
        res, _ = self.parseLuatable(8, self.maxn)
        return res

    def __init__(self, window=None):
        self.hasWindow = False
        if window is not None:
            self.hasWindow = True
            self.window = window

class LuaTableAnalyserToDict():
    '''
    LuaTable到dict形式的python dict的解析类，中间维护一个显示百分比的算法。
    dict形式更能还原LuaTable原本的结构，只使用字典，不再有数组形式.
    '''

    def parseLuatable(self, n, maxn):
        '''
        递归地将Luatable转为dict.
        注意字符串存储在类本身的self.s中，在递归中复用，为了节省空间
        params:
        - n: 起始位置.
        - maxn: 字符串长度.
        returns:
        - nowDict: 结果dict.
        - nowi: 当前递归的结束位置.
        '''

        nowi = n
        nowDict = {}
        nowKey = ""
        nowItem = ""
        nowLabel = 1
        keyStart = 0
        keyQuote = 0

        while True:
            if nowi > self.nextI:
                self.lastPercent += 1
                if self.hasWindow:
                    self.window.setNotice({"t2": "已完成：%d%%" % self.lastPercent, "c2": "#0000ff"})
                self.nextI = int((self.lastPercent + 1) * self.maxn / 100)

            c = self.s[nowi]
            if c == "[":
                keyStart = 1
            elif c == "{":
                jdata, pn = self.parseLuatable(nowi + 1, maxn)
                nowi = pn
                nowItem = jdata
            elif keyStart == 1:
                if c == "]":
                    keyStart = 0
                else:
                    nowKey += c
            elif keyStart == 0:
                if c == '"':
                    keyQuote = (keyQuote + 1) % 2
                if c == "," and keyQuote != 1:
                    if nowKey != "":
                        nowDict[nowKey] = nowItem
                    else:
                        nowDict[str(nowLabel)] = nowItem
                    nowItem = ""
                    nowKey = ""
                    nowLabel += 1
                elif c == "}":
                    if nowItem != "":
                        if nowKey != "":
                            nowDict[nowKey] = nowItem
                        else:
                            nowDict[str(nowLabel)] = nowItem
                    return nowDict, nowi
                elif c != '=':
                    nowItem += c
            nowi += 1
            if nowi >= maxn:
                break
        return nowDict, nowi

    def analyse(self, s, delta=8):
        '''
        进行转换.
        params:
        - s: 需要转换的字符串形式的luatable
        - delta: 偏移量，表示起始位置（自然读取时会用return 开始）
        returns:
        - res: 转换后的dict
        '''
        self.s = s
        self.lastPercent = 0
        self.maxn = len(self.s)
        self.nextI = int((self.lastPercent + 1) * self.maxn / 100)
        res, _ = self.parseLuatable(delta, self.maxn)
        self.s = ""
        return res

    def __init__(self, window=None):
        self.hasWindow = False
        if window is not None:
            self.hasWindow = True
            self.window = window


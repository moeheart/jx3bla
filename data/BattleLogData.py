# Created by moeheart at 09/03/2021
# 复盘日志内容集合，主要包含复盘的全局数据与单条数据的通用形式，兼容jx3dat与jcl。

from data.DataContent import *
from tools.LoadData import *
from tools.Names import *
from tools.Functions import *

class RawDataLoader():
    '''
    直接读取数据文件的类。
    '''

    def parseFile(self, path, filename):
        '''
        读取文件。
        params:
        - path: 文件路径
        - filename: 文件名
        returns:
        - bld: 战斗复盘数据.
        '''

        if path == "":
            name = filename
        else:
            name = "%s\\%s" % (path, filename)

        bld = BattleLogData(self.window)

        if self.window is not None:
            if self.config.item["general"]["datatype"] == "jx3dat":
                bossname = getNickToBoss(filename.split('/')[-1].split('\\')[-1].split('_')[1])
            else:
                bossname = getNickToBoss(filename.split('/')[-1].split('\\')[-1].split('-')[-1].split('.')[0])
            self.window.setNotice({"t1": "正在读取[%s]..." % bossname, "c1": "#000000"})

        if self.config.item["general"]["datatype"] == "jcl":
            bld.loadFromJcl(name)
        elif self.config.item["general"]["datatype"] == "jx3dat":
            bld.loadFromJx3dat(name)
        else:
            raise Exception("未知的数据类型")

        if self.window.lastBld is not None:
            bld.merge(self.window.lastBld)  # 融合上次的记录
            self.window.lastBld = None

        return bld

    def __init__(self, config, filelist, path, window=None, bldDict={}):
        '''
        初始化.
        params:
        - config: 设置类.
        - bldDict: 复盘数据存储类，key为文件名，value为BattleLogData形式的数据。
        - filelist: 需要读取的文件列表。
        - path: 路径。
        - window: 主窗体，用于显示进度。
        - bldDict: 已有的复盘数据，用于缓存从而节省读取时间。
        '''
        self.config = config
        self.bldDict = bldDict
        self.window = window
        for filename in filelist:
            if filename[0] not in self.bldDict:
                self.bldDict[filename[0]] = self.parseFile(path, filename[0])

class BattleLogData():
    '''
    复盘日志维护类.
    '''

    def loadFromJcl(self, filePath):
        '''
        由jcl文件读取复盘信息并转化.
        params:
        - filePath: jcl文件的路径.
        '''
        self.dataType = "jcl"
        ltaDict = LuaTableAnalyserToDict()
        firstBattleInfo = True

        print("读取文件：%s" % filePath)
        try:
            f = open(filePath, "r")
            s = f.read()
        except:
            f = open(filePath, "r", encoding='utf-8')
            s = f.read()
        jclRaw = s.strip('\n').split('\n')

        maxN = len(jclRaw)
        nowN = 0
        nowI = 0

        playerNameDict = {}
        summonDict = {}

        for line in jclRaw:
            # 维护进度条
            nowN += 1
            if nowN > maxN * nowI / 100:
                nowI += 1
                if self.window is not None:
                    self.window.setNotice({"t2": "已完成：%d%%" % nowI, "c2": "#0000ff"})

            jclItem = line.split('\t')
            jclItem[5] = ltaDict.analyse(jclItem[5], delta=1)
            # 读取单条数据
            if jclItem[4] == "13":
                singleData = SingleDataBuff()
            elif jclItem[4] == "21":
                singleData = SingleDataSkill()
                # 召唤物修正
                if jclItem[5]["1"] in summonDict:
                    jclItem[5]["1"] = summonDict[jclItem[5]["1"]]
            elif jclItem[4] == "28":
                singleData = SingleDataDeath()
            elif jclItem[4] == "14":
                singleData = SingleDataShout()
            elif jclItem[4] in ["5", "9"]:
                singleData = SingleDataBattle()
            elif jclItem[4] in ["2", "3", "6", "7"]:
                singleData = SingleDataScene()
            elif jclItem[4] in ["19"]:
                singleData = SingleDataCast()
            else:
                # 读取全局数据
                if jclItem[4] == "1":
                    if firstBattleInfo:
                        self.info.server = jclItem[5]["2"].split(':')[2].split('_')[1]  # 分隔符为两个冒号
                        self.info.battleTime = int(jclItem[5]["2"].split(':')[4])
                        firstBattleInfo = False
                        self.info.sumTime = 0
                    else:
                        self.info.sumTime = int(jclItem[5]["3"])
                elif jclItem[4] == "4":
                    flag = self.info.addPlayer(jclItem[5]["1"], jclItem[5]["2"], jclItem[5]["3"])
                    if flag:
                        self.info.player[jclItem[5]["1"]].xf = jclItem[5]["4"]
                        self.info.player[jclItem[5]["1"]].equipScore = jclItem[5]["5"]
                        self.info.player[jclItem[5]["1"]].equip = jclItem[5]["6"]
                        if "7" in jclItem[5]:
                            self.info.player[jclItem[5]["1"]].qx = jclItem[5]["7"]
                    playerNameDict[self.info.player[jclItem[5]["1"]].name] = jclItem[5]["1"]
                elif jclItem[4] == "8":
                    self.info.addNPC(jclItem[5]["1"], jclItem[5]["2"])
                    self.info.npc[jclItem[5]["1"]].templateID = jclItem[5]["3"]
                    self.info.npc[jclItem[5]["1"]].x = int(jclItem[5]["5"])
                    self.info.npc[jclItem[5]["1"]].y = int(jclItem[5]["6"])
                    self.info.npc[jclItem[5]["1"]].z = int(jclItem[5]["7"])
                    # 判断召唤物
                    if '的' in jclItem[5]["2"]:
                        possiblePlayerName = '的'.join(jclItem[5]["2"].strip('"').split('的')[:-1])
                        if possiblePlayerName in playerNameDict:
                            summonDict[jclItem[5]["1"]] = playerNameDict[possiblePlayerName]
                elif jclItem[4] == "12":
                    self.info.addDoodad(jclItem[5]["1"], jclItem[5]["2"])
                    self.info.doodad[jclItem[5]["1"]].x = int(jclItem[5]["3"])
                    self.info.doodad[jclItem[5]["1"]].y = int(jclItem[5]["4"])
                    self.info.doodad[jclItem[5]["1"]].z = int(jclItem[5]["5"])

                # TODO: 完整的player信息
                continue
            singleData.setByJcl(jclItem)
            self.log.append(singleData)

        # print(playerNameDict)
        # print(summonDict)

        #读取全局数据
        self.info.skill = {}
        self.info.map = filePath.split('/')[-1].split('\\')[-1].split('-')[6]
        if self.info.map == "25人普通雷域大澤":
            self.info.map = "25人普通雷域大泽"
        elif self.info.map == "25人英雄雷域大澤":
            self.info.map = "25人英雄雷域大泽"
        self.info.boss = filePath.split('/')[-1].split('\\')[-1].split('-')[7].split('.')[0]


    def loadFromJx3dat(self, filePath):
        '''
        由jx3dat文件读取复盘信息并转化.
        params:
        - filePath: jx3dat文件的路径.
        '''
        self.dataType = "jx3dat"
        print("读取文件：%s" % filePath)
        f = open(filePath, "r")
        s = f.read()
        ltaDict = LuaTableAnalyserToDict(self.window)
        result = ltaDict.analyse(s)

        # 读取全局数据
        # TODO: 完整的player信息
        self.info.skill = result["11"]
        self.info.server = result["19"].strip('"')
        self.info.map = getMapFromID(result["20"])
        self.info.boss = filePath.split('/')[-1].split('\\')[-1].split('_')[1]
        self.info.battleTime = int(result["4"])
        self.info.sumTime = int(result["7"])

        for line in result["9"]:
            if result["10"][line] == "0":
                self.info.addNPC(line, result["9"][line])
            else:
                self.info.addPlayer(line, result["9"][line], result["10"][line])
                if line in result["18"]:
                    self.info.player[line].xf = result["18"][line]["1"]
                    self.info.player[line].equipScore = result["18"][line]["2"]
                    self.info.player[line].equip = result["18"][line]["3"]

        # 读取单条数据
        for key in result["16"]:
            value = result["16"][key]
            if value["4"] == "5":
                singleData = SingleDataBuff()
            elif value["4"] == "1":
                singleData = SingleDataSkill()
            elif value["4"] == "3":
                singleData = SingleDataDeath()
            elif value["4"] == "8":
                singleData = SingleDataShout()
            elif value["4"] == "10":
                singleData = SingleDataBattle()
                if value["6"] in self.info.npc:
                    self.info.npc[value["6"]].templateID = value["9"]
            elif value["4"] == "6":
                singleData = SingleDataScene()
            else:
                continue
            singleData.setByJx3dat(value)
            self.log.append(singleData)

    def merge(self, bld2):
        '''
        将另一条战斗复盘记录合并到自身的前方.
        params:
        - bld2: 需要融合的战斗记录
        returns:
        - 融合结果, 0代表成功
        '''
        if self.dataType != bld2.dataType:
            return 1
        if self.info.server != bld2.info.server:
            return 1
        if self.info.map != bld2.info.map:
            return 1
        if self.info.boss != bld2.info.boss:
            return 1

        self.info.battleTime = bld2.info.battleTime
        self.info.sumTime += bld2.info.sumTime
        self.info.skill = concatDict(self.info.skill, bld2.info.skill)
        self.info.player = concatDict(self.info.player, bld2.info.player)
        self.info.npc = concatDict(self.info.npc, bld2.info.npc)
        self.log = bld2.log + self.log
        return 0

    def __init__(self, window=None):
        self.log = []
        self.window = window
        self.info = OverallData()
        self.dataType = "unknown"

if __name__ == "__main__":
    bld = BattleLogData()
    bld.loadFromJx3dat("2021-09-06-22-44-32_极境试炼木桩_4.fstt.jx3dat")
    #print(bld.log)
    #for line in bld.log:
    #    print(line.dataType)
    print(bld.info.map)
    print(bld.info.boss)
    for line in bld.info.player:
        print(bld.info.player[line].xf)
        print(bld.info.player[line].name)
        print(bld.info.player[line].equip)
    bld.loadFromJcl("2021-09-06-22-44-32-帮会领地-极境试炼木桩.jcl")
    #print(bld.log)
    #for line in bld.log:
    #    print(line.dataType)
    print(bld.info.map)
    print(bld.info.boss)
    for line in bld.info.player:
        print(bld.info.player[line].xf)
        print(bld.info.player[line].name)
        print(bld.info.player[line].equip)
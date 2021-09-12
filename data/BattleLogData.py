# Created by moeheart at 09/03/2021
# 复盘日志内容集合，主要包含复盘的全局数据与单条数据的通用形式，兼容jx3dat与jcl。

from data.DataContent import *
from tools.LoadData import *
from tools.Names import *

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
        ltaDict = LuaTableAnalyserToDict()
        firstBattleInfo = True

        print("读取文件：%s" % filePath)
        f = open(filePath, "r")
        s = f.read()
        jclRaw = s.strip('\n').split('\n')
        for line in jclRaw:
            jclItem = line.split('\t')
            jclItem[5] = ltaDict.analyse(jclItem[5], delta=1)
            # 读取单条数据
            if jclItem[4] == "13":
                singleData = SingleDataBuff()
            elif jclItem[4] == "21":
                singleData = SingleDataSkill()
            elif jclItem[4] == "28":
                singleData = SingleDataDeath()
            elif jclItem[4] == "14":
                singleData = SingleDataShout()
            elif jclItem[4] in ["5", "9"]:
                singleData = SingleDataBattle()
            else:
                # 读取全局数据
                if jclItem[4] == "1" and firstBattleInfo:
                    self.info.server = jclItem[5]["2"].split(':')[2]  # 分隔符为两个冒号
                    self.info.battleTime = int(jclItem[5]["2"].split(':')[4])
                    self.info.sumTime = int(jclItem[5]["3"])
                    firstBattleInfo = False
                elif jclItem[4] == "4":
                    flag = self.info.addPlayer(jclItem[5]["1"], jclItem[5]["2"], jclItem[5]["3"])
                    if flag:
                        self.info.player[jclItem[5]["1"]].xf = jclItem[5]["4"]
                        self.info.player[jclItem[5]["1"]].equipScore = jclItem[5]["5"]
                        self.info.player[jclItem[5]["1"]].equip = jclItem[5]["6"]
                        self.info.player[jclItem[5]["1"]].qx = jclItem[5]["7"]
                elif jclItem[4] == "8":
                    self.info.addNPC(jclItem[5]["1"], jclItem[5]["2"])

                # TODO: 完整的player信息
                continue
            singleData.setByJcl(jclItem)
            self.log.append(singleData)
        #读取全局数据
        self.info.skill = {}
        self.info.map = filePath.split('-')[6]
        self.info.boss = filePath.split('-')[7].split('.')[0]


    def loadFromJx3dat(self, filePath):
        '''
        由jx3dat文件读取复盘信息并转化.
        params:
        - filePath: jx3dat文件的路径.
        '''
        print("读取文件：%s" % filePath)
        f = open(filePath, "r")
        s = f.read()
        ltaDict = LuaTableAnalyserToDict(self.window)
        result = ltaDict.analyse(s)

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
            else:
                continue
            singleData.setByJx3dat(value)
            self.log.append(singleData)

        # 读取全局数据
        # TODO: 完整的player信息
        self.info.skill = result["11"]
        self.info.server = result["19"]
        self.info.map = getMapFromID(result["20"])
        self.info.boss = filePath.split('_')[1]
        self.info.battleTime = int(result["4"])
        self.info.sumTime = int(result["7"])

        print("Info:")
        print(result["9"])
        print(result["10"])
        for line in result["9"]:
            if result["10"][line] == "0":
                self.info.addNPC(line, result["9"][line])
            else:
                self.info.addPlayer(line, result["9"][line], result["10"][line])
                if line in result["18"]:
                    self.info.player[line].xf = result["18"][line]["1"]
                    self.info.player[line].equipScore = result["18"][line]["2"]
                    self.info.player[line].equip = result["18"][line]["3"]

    def __init__(self, window=None):
        self.log = []
        self.window = window
        self.info = OverallData()

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
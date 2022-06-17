# Created by moeheart at 09/12/2021
# 复盘相关方法的基类库，此处进行过修改，读取文件的逻辑实际由DataController完成.

from tools.Functions import *
from tools.LoadData import *
from tools.Names import *
from data.BattleLogData import RawDataLoader
from replayer.Percent import *

import json

def getDirection(key):
    if "delay" in key:
        return -1
    else:
        return 1

class RankCalculator():
    '''
    排名计算类.
    实现由统计数据到排名的计算方法，在本体复盘和服务器处理排名时调用.
    '''

    def getSkillPercent(self, occ, map, boss, name, key, value):
        '''
        获取对应统计数据的百分数.
        params:
        - occ: 对应的心法.
        - map: 地图编号.
        - boss: BOSS名称.
        - name: results中的分类，用于计算百分位数.
        - key: results中的键，用于计算百分位数.
        - value: 对应的值.
        returns:
        - num: 记录总数量.
        - percent: 排名百分位.
        '''
        value = getDirection(key) * value
        percent_key = "%s-%s-%s-%s-%s" % (occ, map, boss, name, key)
        if percent_key in STAT_PERCENT:
            # 计算百分位数流程
            result = STAT_PERCENT[percent_key]
            num = result["num"]
            table = json.loads(result["value"])
            l = 0
            r = 100
            while r > l + 1:
                m = (l + r + 1) // 2
                if value >= table[m]:
                    l = m
                else:
                    r = m
            percent = m
            return num, percent
        else:
            # 缺省值流程
            return 0, 0

    def getRankFromStat(self, occ):
        '''
        通过统计数据从self.result中获取百分比排名.
        params:
        - occ: 复盘心法.
        returns:
        - rank: 排名，dict形式
        '''
        self.rank = {}
        map = getIDFromMap(self.result["overall"]["map"])
        boss = self.result["overall"]["boss"]
        # 枚举skill中的所有结果.
        for name in self.result["skill"]:
            self.rank[name] = {}
            for key in self.result["skill"][name]:
                value = self.result["skill"][name][key]
                num, percent = self.getSkillPercent(occ, map, boss, name, key, value)
                self.rank[name][key] = {"num": num, "percent": percent}
        # 记录HPS
        self.rank["healer"] = {}
        for record in self.result["healer"]["table"]:
            if record["name"] == self.result["overall"]["playerID"]:
                # 当前玩家
                num, percent = self.getSkillPercent(occ, map, boss, "healer", "healEff", record["healEff"])
                self.rank["healer"]["healEff"] = {"num": num, "percent": percent}
                num, percent = self.getSkillPercent(occ, map, boss, "healer", "heal", record["heal"])
                self.rank["healer"]["heal"] = {"num": num, "percent": percent}
        return self.rank

    def __init__(self, result):
        '''
        初始化.
        params:
        - result: 复盘类中的result.
        '''
        self.result = result


class ReplayerBase():
    '''
    复盘方法基类.
    '''

    def getRankFromStat(self, occ):
        '''
        通过统计数据从self.result中获取百分比排名, 并保存在self.rank中.
        params:
        - occ: 复盘心法.
        '''
        rc = RankCalculator(self.result)
        self.rank = rc.getRankFromStat(occ)

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名组合，格式为[文件名, 尝试次数, 是否为最后一次]
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        '''
        self.numTry = fileNameInfo[1]
        self.lastTry = fileNameInfo[2]
        self.bldDict = {}
        self.config = config
        self.window = window
        self.fileNameInfo = fileNameInfo[0]
        if fileNameInfo[0] not in bldDict:
            # self.parseFile(path)
            self.bldDict = RawDataLoader(config, [fileNameInfo], path, window).bldDict
            bldDict[fileNameInfo[0]] = self.bldDict[fileNameInfo[0]]
        else:
            self.bldDict = bldDict

# Created by moeheart at 09/12/2021
# 复盘相关方法的基类库，此处进行过修改，读取文件的逻辑实际由DataController完成.

from tools.Functions import *
from tools.LoadData import *
from tools.Names import *
from data.BattleLogData import RawDataLoader
# from replayer.Percent import *
from Constants import *

import time
import json
import hashlib
import urllib.request

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
        if percent_key in self.percent_data:
            # 计算百分位数流程
            result = self.percent_data[percent_key]
            num = result["num"]
            table = json.loads(result["value"])
            l = 0
            r = 101
            while r > l + 1:
                m = (l + r + 1) // 2
                if value >= table[m]:
                    l = m
                else:
                    r = m
            percent = l
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
        if "healer" in self.result:
            self.rank["healer"] = {}
            for record in self.result["healer"]["table"]:
                if record["name"] == self.result["overall"]["playerID"]:
                    # 当前玩家
                    num, percent = self.getSkillPercent(occ, map, boss, "healer", "healEff", record["healEff"])
                    self.rank["healer"]["healEff"] = {"num": num, "percent": percent}
                    num, percent = self.getSkillPercent(occ, map, boss, "healer", "heal", record["heal"])
                    self.rank["healer"]["heal"] = {"num": num, "percent": percent}
                    for stat in ["hps", "rhps", "ahps", "ohps"]:
                        num, percent = self.getSkillPercent(occ, map, boss, "healer", stat, record.get(stat, 0))
                        self.rank["healer"][stat] = {"num": num, "percent": percent}
        # print("[Rank]", self.rank)
        return self.rank

    def __init__(self, result, percent_data):
        '''
        初始化.
        params:
        - result: 复盘类中的result.
        - percent_data: 百分位排名数据.
        '''
        self.result = result
        self.percent_data = percent_data


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
        rc = RankCalculator(self.result, self.window.stat_percent)
        self.rank = rc.getRankFromStat(occ)

    def getHash(self):
        '''
        获取战斗结果的哈希值.
        '''
        hashStr = ""
        nameList = []
        for key in self.bld.info.player:
            nameList.append(self.bld.info.player[key].name)
        nameList.sort()
        battleMinute = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        hashStr = battleMinute + self.result["overall"]["map"] + "".join(nameList) + self.mykey
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        '''
        准备上传复盘结果，并向服务器上传.
        '''
        # if "beta" in EDITION:
        #     return
        if self.win == 0:  # 未通关时不上传
            return
        upload = {}
        upload["server"] = self.result["overall"]["server"]
        upload["id"] = self.result["overall"]["playerID"]
        upload["occ"] = self.occ
        upload["score"] = self.result["review"]["score"]
        upload["battledate"] = time.strftime("%Y-%m-%d", time.localtime(self.result["overall"]["battleTime"]))
        upload["mapdetail"] = self.result["overall"]["map"]
        upload["boss"] = self.result["overall"]["boss"]
        upload["statistics"] = self.result
        upload["public"] = self.public
        upload["edition"] = EDITION
        upload["editionfull"] = parseEdition(EDITION)
        upload["replayedition"] = self.result["overall"]["edition"]
        upload["userid"] = self.config.item["user"]["uuid"]
        upload["battletime"] = self.result["overall"]["battleTime"]
        upload["submittime"] = int(time.time())
        upload["hash"] = self.getHash()
        upload["battleID"] = self.battleID

        uploadData = {"type": "replay", "data": upload, "anchor": self.result}
        self.window.addUploadData(uploadData)

        # Jdata = json.dumps(upload)
        # jpost = {'jdata': Jdata}
        # jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        # # print(jparse)
        # resp = urllib.request.urlopen('http://%s:8009/uploadReplayPro' % IP, data=jparse)
        # res = json.load(resp)
        # # print(res)
        # if res["result"] != "fail":
        #     self.result["overall"]["shortID"] = res["shortID"]
        # else:
        #     self.result["overall"]["shortID"] = "数据保存出错"
        # return res

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, actorData={}):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名组合，格式为[文件名, 尝试次数, 是否为最后一次]
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - actorData: 演员复盘得到的统计记录.
        '''
        self.numTry = fileNameInfo[1]
        self.lastTry = fileNameInfo[2]
        self.bldDict = {}
        self.config = config
        self.window = window
        self.fileNameInfo = fileNameInfo[0]
        self.equip = {}
        if fileNameInfo[0] not in bldDict:
            # self.parseFile(path)
            self.bldDict = RawDataLoader(config, [fileNameInfo], path, window).bldDict
            bldDict[fileNameInfo[0]] = self.bldDict[fileNameInfo[0]]
        else:
            self.bldDict = bldDict
        if actorData != {}:
            self.actorData = actorData
            self.startTime = actorData["startTime"]
            self.finalTime = actorData["finalTime"]
            self.win = actorData["win"]
            self.bossBh = actorData["bossBh"]
            self.battleDict = actorData["battleDict"]
            self.unusualDeathDict = actorData["unusualDeathDict"]
            self.deathDict = actorData["deathDict"]
            self.act = actorData["act"]
            self.battleID = actorData["hash"]
            self.equip = actorData["equip"]
        # self.myname = myname
        self.failThreshold = config.item["actor"]["failthreshold"]
        self.mask = config.item["general"]["mask"]
        self.config = config
        self.bld = bldDict[fileNameInfo[0]]
        self.result = {}


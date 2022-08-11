# Created by moeheart at 1/8/2021
# 定制化复盘的基类库。

from replayer.BattleHistory import BattleHistory
from tools.Functions import *

class SpecificReplayerPro():
    '''
    BOSS复盘通用类.
    '''

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        pass

    def recordEquipment(self, equipmentDict):
        '''
        记录装备信息流程，只在白帝江关之后的副本中会用到。
        params
        - equipmentDict 经过处理的装备信息。
        '''
        self.equipmentDict = equipmentDict

    def getBaseList(self, id):
        '''
        根据单个角色的复盘信息返回复盘结果. 属于共享流程.
        params
        - id: 角色id
        returns
        - res: 生成的复盘结果（前7项）
        '''
        line = self.stat[id]
        if id in self.equipmentDict:
            line[4] = self.equipmentDict[id]["score"]
            line[5] = "%s|%s" % (self.equipmentDict[id]["sketch"], self.equipmentDict[id]["forge"])
        else:
            line[5] = "|"

        line[6] = self.stunCounter[id].buffTimeIntegral() / 1000

        if getOccType(self.occDetailList[id]) == "healer":
            line[3] = int(self.hps[id] / self.battleTime * 1000)

        dps = int(line[2] / self.battleTime * 1000)
        res = [line[0],
               line[1],
               dps,
               line[3],
               line[4],
               line[5],
               line[6],
               ]
        return res

    def analyseSecondStage(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def analyseFirstStage(self, item):
        '''
        处理单条复盘数据时的流程，在第一阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        '''
        pass

    def addPot(self, pot):
        '''
        在分锅记录中加入一条单独的锅。
        params
        - pot 分锅记录
        '''
        self.potList.append(pot)

    def mergeBlackList(self, blackList, config):
        '''
        将BOSS复盘中附带的列表和设置中的过滤监控词条列表合并.
        params:
        - blackList: 合并之前的列表.
        - config: 设置类.
        returns:
        - blackList: 合并之后的列表
        '''
        configList = config.item["actor"]["filter"].split(',')
        blackList.extend(configList)
        return blackList

    def trimTime(self):
        '''
        根据战斗记录的结果修剪时间。
        '''
        if self.trimmedStartTime != 0:
            self.startTime = self.trimmedStartTime
        if self.trimmedFinalTime != 0:
            self.finalTime = self.trimmedFinalTime
        if self.trimmedStartTime != 0 or self.trimmedFinalTime != 0:
            # 如果进行了时间修剪，就调整battletime的逻辑，否则battletime就使用复盘数据中附带的结果
            self.battleTime = self.finalTime - self.startTime
        return self.startTime, self.finalTime, self.battleTime

    def initBattleBase(self):
        '''
        初始化流程的通用部分.
        '''
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.stunCounter = {}

        self.bhTime = {}

        # 通用的复盘黑名单
        self.bhBlackList = ["b17200", "c15076", "c15082", "b20854", "b3447", "b14637", "s15082", "b789", "c3365",
                            "s15181", "s20763", "s28",
                            "n108263", "n108426", "n108754", "n108736", "n108217", "n108216", "b15775", "b17201",
                            "s6746", "b17933", "b6131", "b20128", "b1242", "b2685", "s20764", "s3051"]

        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                              []
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

        # 对DPS和治疗分别给出无效区间
        self.badPeriodDps = IntervalCounter(self.startTime, self.finalTime)
        self.badPeriodHealer = IntervalCounter(self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        self.activeBoss = "None"
        self.bld = bld
        # self.mapDetail = mapDetail  # TODO 需要时更换为从bld获取
        self.occDetailList = occDetailList
        self.startTime = startTime
        self.finalTime = finalTime
        self.battleTime = battleTime
        self.bossNamePrint = bossNamePrint

        self.trimmedStartTime = 0
        self.trimmedFinalTime = 0

        self.detail = {}
        self.potList = []
        self.effectiveDPSList = []
        self.hasBh = False

# Created by moeheart at 1/8/2021
# 定制化复盘的基类库。

from tools.Functions import *

import threading
import tkinter as tk
from replayer.TableConstructor import TableConstructor, ToolTip
from window.TimelineWindow import TimelineWindow

class SpecificBossWindow():

    def getMaskName(self, name):
        '''
        获取名称打码的结果。事实上只需要对统计列表中的玩家打码.
        params:
        - name: 打码之前的玩家名.
        '''
        s = name.strip('"')
        if s == "":
            return s
        elif self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def openPrev(self):
        '''
        尝试打开前序BOSS。
        '''
        self.potWindow.finalPrev()

    def openNext(self):
        '''
        尝试打开后序BOSS。
        '''
        self.potWindow.finalNext()

    def openPot(self):
        '''
        打开分锅界面（也即战斗事件记录界面）。
        '''
        self.potWindow.start()

    def setPotWindow(self, potWindow):
        '''
        设置分锅界面对象，为后面通过复盘窗口打开分锅窗口提供连接。
        '''
        self.potWindow = potWindow

    def openTimelineWindow(self):
        '''
        打开时间轴窗口。
        '''
        self.timelineWindow.start()

    def setTimelineWindow(self, data, boss):
        '''
        设置时间轴窗口对象.
        - environment: 环境轴，与BattleLog中的定义相同.
        - boss: BOSS名称.
        '''
        self.timelineWindow = TimelineWindow()
        self.timelineWindow.setData(data, boss)

    def final(self):
        '''
        关闭窗口.
        '''
        self.windowAlive = False
        self.window.destroy()

    def start(self):
        '''
        显示窗口.
        '''
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def alive(self):
        '''
        判断窗口是否存活.
        '''
        return self.windowAlive

    def __init__(self, config, effectiveDPSList, detail, occResult):
        '''
        初始化.
        '''
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.occResult = occResult
        self.config = config
        self.mask = config.item["general"]["mask"]


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

        # 通用的复盘黑名单
        self.bhBlackList = ["b17200", "c15076", "c15082", "b20854", "b3447", "b14637", "s15082", "b789", "c3365",
                            "s15181", "s20763",
                            "n108263", "n108426", "n108754", "n108736", "n108217", "n108216", "b15775", "b17201",
                            "s6746", "b17933", "b6131", "b20128", "b1242", "b2685"]

class SpecificReplayer():
    # TODO 移除

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

    def __init__(self, playerIDList, mapDetail, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        self.activeBoss = "None"
        self.playerIDList = playerIDList
        self.mapDetail = mapDetail
        self.bld = bld
        self.occDetailList = occDetailList
        self.startTime = startTime
        self.finalTime = finalTime
        self.battleTime = battleTime
        self.bossNamePrint = bossNamePrint
        
        self.detail = {}
        self.potList = []
        self.effectiveDPSList = []


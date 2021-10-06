# Created by moeheart at 1/8/2021
# 定制化复盘的基类库。

from tools.Functions import *

import threading
import tkinter as tk
from replayer.TableConstructor import TableConstructor, ToolTip

class SpecificBossWindow():

    def __init__(self):
        pass


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

        self.detail = {}
        self.potList = []
        self.effectiveDPSList = []

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

    def __init__(self, playerIDList, mapDetail, res, occDetailList, startTime, finalTime, battleTime, bossNamePrint):
        '''
        对类本身进行初始化。
        '''
        self.activeBoss = "None"
        self.playerIDList = playerIDList
        self.mapDetail = mapDetail
        self.namedict = res['9'][0]
        self.occdict = res['10'][0]
        self.skilldict = res['11'][0]
        self.occDetailList = occDetailList
        self.startTime = startTime
        self.finalTime = finalTime
        self.battleTime = battleTime
        self.bossNamePrint = bossNamePrint
        
        self.detail = {}
        self.potList = []
        self.effectiveDPSList = []


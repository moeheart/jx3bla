# Created by moeheart at 1/8/2021
# 定制化复盘的基类库。

from tools.Functions import *

import threading
import tkinter as tk
from replayer.TableConstructor import TableConstructor, ToolTip

class SpecificBossWindow():

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

    # def loadWindow(self):
    #     '''
    #     默认的BOSS复盘窗口.
    #     '''
    #     window = tk.Toplevel()
    #     # window = tk.Tk()
    #     window.title('通用BOSS详细复盘')
    #     window.geometry('1200x800')
    #
    #     frame1 = tk.Frame(window)
    #     frame1.pack()
    #
    #     # 通用格式：
    #     # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
    #
    #     tb = TableConstructor(frame1)
    #
    #     tb.AppendHeader("玩家名", "", width=13)
    #     tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
    #     tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
    #     tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
    #     tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
    #     tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。")
    #     tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
    #     tb.EndOfLine()
    #
    #     for i in range(len(self.effectiveDPSList)):
    #         name = self.effectiveDPSList[i][0]
    #         color = getColor(self.effectiveDPSList[i][1])
    #         tb.AppendContext(name, color=color, width=13)
    #         tb.AppendContext(int(self.effectiveDPSList[i][2]))
    #
    #         if getOccType(self.effectiveDPSList[i][1]) != "healer":
    #             text3 = str(self.effectiveDPSList[i][3]) + '%'
    #             color3 = "#000000"
    #         else:
    #             text3 = self.effectiveDPSList[i][3]
    #             color3 = "#00ff00"
    #         tb.AppendContext(text3, color=color3)
    #
    #         text4 = "-"
    #         if self.effectiveDPSList[i][4] != -1:
    #             text4 = int(self.effectiveDPSList[i][4])
    #         tb.AppendContext(text4)
    #
    #         tb.AppendContext(self.effectiveDPSList[i][5])
    #         tb.AppendContext(int(self.effectiveDPSList[i][6]))
    #         tb.AppendContext("")
    #         tb.EndOfLine()
    #
    #     self.window = window
    #     window.protocol('WM_DELETE_WINDOW', self.final)

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

    def __init__(self, effectiveDPSList, detail, occResult):
        '''
        初始化.
        '''
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.occResult = occResult


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
        self.hasBh = False

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


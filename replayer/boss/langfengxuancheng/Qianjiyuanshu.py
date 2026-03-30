import tkinter as tk

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.General import GeneralReplayer
from replayer.TableConstructorMeta import TableConstructorMeta


class QianjiyuanshuWindow(SpecificBossWindow):
    '''
    千机源枢的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用 tkinter 绘制详细复盘窗口。
        '''
        self.constructWindow("千机源枢", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for line in self.effectiveDPSList:
            self.constructCommonLine(tb, line)

            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class QianjiyuanshuReplayer(GeneralReplayer):
    '''
    千机源枢的定制复盘类。
    '''

    def initBattle(self):
        self.initBattleBase()
        self.initPhase(1, 1)

        self.activeBoss = "千机源枢"
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)
        self.bhInfo = {}

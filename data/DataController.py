# Created by moeheart at 09/12/2021
# 数据控制类。实现数据的读取、传递的各种类，也可以直接连接数据处理。

from data.BattleLogData import BattleLogData, RawDataLoader
import traceback
from FileLookUp import FileLookUp
from tools.Names import getNickToBoss
from replayer.ActorReplayPro import ActorProReplayer
from replayer.occ.XiangZhi import XiangZhiProWindow, XiangZhiProReplayer

class DataController():
    '''
    数据维护类，控制数据的与读取传递。
    '''

    def getMultiData(self, window, fileList):
        '''
        获取多个文件中的数据. 用于复盘模式中一次性读入的场景.
        params:
        - window: 主程序窗口对象.
        - fileList: 新增的文件名.
        '''
        try:
            config = self.config
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            if self.cached:
                bldDict = RawDataLoader(config, fileList, fileLookUp.basepath, window, self.bldDict).bldDict
            else:
                bldDict = RawDataLoader(config, fileList, fileLookUp.basepath, window).bldDict
            window.setBattleLogData(bldDict)

        except Exception as e:
            traceback.print_exc()

    def getSingleData(self, window, fileName):
        '''
        获取单个文件中的数据. 用于实时模式中一条一条读取的场景.
        params:
        - window: 主程序窗口对象.
        - fileName: 新增的文件名.
        '''
        try:
            config = self.config
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            if self.cached:
                bldDict = RawDataLoader(config, [[fileName, 0, 1]], fileLookUp.basepath, window, self.bldDict).bldDict
            else:
                bldDict = RawDataLoader(config, [[fileName, 0, 1]], fileLookUp.basepath, window).bldDict
            window.setBattleLogData(bldDict)

        except Exception as e:
            traceback.print_exc()

    def setRawData(self, bldDict):
        '''
        直接指定战斗复盘的缓存，从而节省从文件读取的时间。
        params:
        - bldDict: 数据，dict形式
        '''
        self.cached = True
        self.bldDict = bldDict

    def __init__(self, config):
        '''
        初始化。
        params:
        - config: 设置类。
        '''
        self.cached = False
        self.config = config


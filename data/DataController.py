# Created by moeheart at 09/12/2021
# 数据控制类。实现数据的读取、传递的各种类，也可以直接连接数据处理。

from data.BattleLogData import BattleLogData, RawDataLoader
import traceback
from FileLookUp import FileLookUp
from BossNameUtils import getNickToBoss
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

    def replay(self, window):
        '''
        在现有的条件下识别需要复盘的文件，并执行复盘流程。
        params:
        - window: 主程序窗口对象。
        '''
        try:
            config = self.config
            fileLookUp = FileLookUp()
            fileLookUp.initFromConfig(config)
            filelist, allFilelist, map = fileLookUp.getLocalFile()
            print("开始分析。分析耗时可能较长，请耐心等待……")

            # 加载与补充加载，保证raw中包含了所有可能用到的数据。
            if self.cached:
                bldDict = RawDataLoader(config, filelist, fileLookUp.basepath, window, self.bldDict).bldDict
            elif config.checkAll:
                bldDict = RawDataLoader(config, allFilelist, fileLookUp.basepath, window).bldDict
            else:
                bldDict = RawDataLoader(config, filelist, fileLookUp.basepath, window).bldDict

            # TODO 在线展示链接重构
            '''
            if config.xiangzhiActive:
                b = XiangZhiAnalysis(filelist, map, fileLookUp.basepath, config, raw)
                b.analysis()
                b.paint("result.png")
                print("奶歌战斗复盘分析完成！结果保存在result.png中")
                if b.info["uploaded"]:
                    print("可以通过以下链接来查看与分享：http://139.199.102.41:8009/XiangZhiData/png?key=%s" % b.info["hash"])
            '''
            for fileName in bldDict:
                fileNameInfo = [fileName, 0, 1]

                # 演员复盘部分
                actorRep = ActorProReplayer(config, fileNameInfo, fileLookUp.basepath, bldDict, window)
                actorRep.replay()
                actorWindow = actorRep.generateWindow()
                actorWindow.start()

                # 奶歌复盘部分
                # xiangzhiRep = XiangZhiProReplayer(config, fileNameInfo, fileLookUp.basepath, bldDict, window)
                # xiangzhiRep.replay()
                # xiangzhiWindow = XiangZhiProWindow(xiangzhiRep.result)
                # xiangzhiWindow.start()

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


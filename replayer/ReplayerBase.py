# Created by moeheart at 09/12/2021
# 复盘相关方法的基类库，此处进行过修改，读取文件的逻辑实际由DataController完成.

from tools.Functions import *
from tools.LoadData import *
from tools.Names import *
from data.BattleLogData import RawDataLoader

class ReplayerBase():
    '''
    复盘方法基类.
    '''

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

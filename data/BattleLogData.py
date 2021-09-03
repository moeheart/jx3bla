# Created by moeheart at 09/03/2021
# 复盘日志维护，主要包含复盘的全局数据与单条数据的通用形式，兼容jx3dat与jcl。


class SingleData():
    '''
    单条日志，包含全部形式。
    具体形式均继承自此类。
    '''

    def getType(self):
        return self.dataType

    def __init__(self):
        self.dataType = "Empty"

class SingleDataBuff(SingleData):
    '''
    Buff事件。
    '''

    def set(self):
        pass


    def __init__(self):
        self.dataType = "Buff"

class BattleLogData():
    '''
    复盘日志维护类.
    '''

    def getSingleFromJcl(self, item):
        pass

    def getSingleFromJx3dat(self, item):
        pass

    def getFromJcl(self, raw):
        pass

    def getFromJx3dat(self, raw):
        pass

    def __init__(self):
        self.log = []
        pass


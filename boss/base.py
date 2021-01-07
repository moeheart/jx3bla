# Created by moeheart at 1/8/2021
# 定制化复盘的基类库。

class SpecificReplayer():

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        子类需要继承并实现此方法。
        '''
        pass

    def analyseSingle(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        子类需要继承并实现此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        子类需要继承并实现此方法。
        '''
        pass

    def __init__(self):
        '''
        对类本身进行初始化。
        '''
        pass


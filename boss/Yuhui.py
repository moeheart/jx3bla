# Created by moeheart at 1/11/2021
# 余晖的定制复盘方法库。
# 余晖是达摩洞1号首领，复盘主要集中在以下几个方面：
# 1. 狂热崇拜值的层数。
# 2. 引导情况。
# 3. 寒刃绞杀承伤情况。
# 余晖的各种处理较为简单，可以作为例程来参考。

class YuhuiReplayer(SpecificReplayer):

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''
        pass

    def analyseSingle(self, item):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        '''
        pass

    def __init__(self):
        '''
        对类本身进行初始化。
        '''
        pass


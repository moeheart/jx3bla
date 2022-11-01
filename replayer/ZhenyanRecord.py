# Created by moeheart at 11/01/2021
# 推测阵眼的方法.

from tools.Attribute import *
from tools.Functions import safe_divide

class ZhenyanRecord():
    '''
    阵眼推测类. 对每个玩家，根据其获得过的buff进行阵眼推测，这个类维护了推测功能.
    '''

    def scan(self, time):
        '''
        按时序进行扫描，并得到在这个时间点上阵眼buff的变化情况. 保证在调用initScan后，这些scan都是按时间顺序进行的.
        params:
        - time: 当前的时间
        returns:
        - minus: 需要移除的阵眼增益，若无则为"0"
        - plus: 需要添加的阵眼增益，若无则为"0"
        '''
        if self.step >= self.sum or self.log[self.step][0] > time:
            return "0", "0"
        minus = self.current
        plus = self.log[self.step][1]
        self.current = plus
        self.step += 1
        return minus, plus

    def initScan(self):
        '''
        在扫描前初始化.
        '''
        self.step = 0
        self.sum = len(self.log)
        self.current = "0"

    def getSummary(self):
        '''
        得到整个战斗中阵眼比例的结果.
        returns:
        - res: dict形式的结果. 暂时直接使用文字来表示.
        '''
        resRaw = {}
        prevTime = self.startTime
        prevValue = "0"
        for line in self.log:
            if line[0] - prevTime > 0:
                resRaw[prevValue] = resRaw.get(prevValue, 0) + line[0] - prevTime
            prevTime = line[0]
            prevValue = line[1]
        if self.finalTime - prevTime > 0:
            resRaw[prevValue] = resRaw.get(prevValue, 0) + self.finalTime - prevTime
        res = {}
        for key in resRaw:
            res[ZHENYAN_DICT[key][0]] = safe_divide(resRaw[key], self.finalTime - self.startTime)
        return res

    def recordPrev(self, time, zhenfa):
        '''
        在这一个时刻及之前记录阵眼.
        params:
        - time: 时间
        - zhenfa: 阵法，用阵法效果对应的那个buffID记录.
        '''
        pass
        # 由于复盘中阵眼丢失大量的信息，暂时不判定这个事件
        # if self.log == []:
        #     self.log.append([self.startTime, zhenfa])
        # if "0" != self.log[-1][1]:
        #     self.log.append([time, "0"])

    def recordPost(self, time, zhenfa):
        '''
        在这一个时刻及之后记录阵眼.
        params:
        - time: 时间
        - zhenfa: 阵法，用阵法效果对应的那个buffID记录.
        '''
        # 由于复盘中阵眼丢失大量的信息，改用另一种逻辑判定这个事件
        # if self.log == []:
        #     self.log.append([self.startTime, "0"])
        # if zhenfa != self.log[-1][1]:
        #     self.log.append([time, zhenfa])
        if self.log == []:
            self.log.append([self.startTime, zhenfa])
        elif zhenfa != self.log[-1][1]:
            self.log.append([time, zhenfa])

    def recordPresent(self, time, zhenfa):
        '''
        在这一个时刻记录阵眼.
        params:
        - time: 时间
        - zhenfa: 阵法，用阵法效果对应的那个buffID记录.
        '''
        if self.log == []:
            self.log.append([self.startTime, zhenfa])
        elif time - self.log[-1][0] > 10000 and zhenfa != self.log[-1][1]:
            self.log.append([time, zhenfa])

    def __init__(self, startTime, finalTime):
        '''
        构造方法. 需要传入战斗的开始和结束时间.
        '''
        self.log = []
        self.startTime = startTime
        self.finalTime = finalTime
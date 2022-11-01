# Created by moeheart at 11/01/2021
# 推测阵眼的方法.

class ZhenyanRecord():
    '''
    阵眼推测类. 对每个玩家，根据其获得过的buff进行阵眼推测，这个类维护了推测功能.
    '''


    def recordPrev(self, time, zhenfa):
        '''
        在这一个时刻及之前记录阵眼.
        params:
        - time: 时间
        - zhenfa: 阵法，用阵法效果对应的那个buffID记录.
        '''
        if self.log == []:
            self.log.append([self.startTime, zhenfa])
        self.log.append([time, "0"])

    def recordPost(self, time, zhenfa):
        '''
        在这一个时刻及之后记录阵眼.
        params:
        - time: 时间
        - zhenfa: 阵法，用阵法效果对应的那个buffID记录.
        '''
        if self.log == []:
            self.log.append([self.startTime, "0"])
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
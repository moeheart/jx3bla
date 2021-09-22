# Created by moeheart at 09/22/2021
# 技能回放，用于记录与提取技能回放信息。

class BattleHistory():
    '''
    技能回放类，维护3个轴：场地轴，常规技能轴，特殊技能轴
    技能回放以json的形式存储.
    '''

    def getJsonReplay(self):
        '''
        获取json格式的数据.
        '''
        self.log["startTime"] = self.startTime
        self.log["finalTime"] = self.finalTime
        return self.log

    def setEnvironment(self, skillid, skillname, iconid, start, duration, num, healeff, effrate, delay, description):
        '''
        添加场地.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - healeff: 治疗量.
        - effrate: 有效比例.
        - delay: 平均延时.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "description": description}
        self.log["environment"].append(res)

    def setSpecialSkill(self, skillid, skillname, iconid, start, duration, num, healeff, effrate, delay, description):
        '''
        添加特殊技能.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - healeff: 治疗量.
        - effrate: 有效比例.
        - delay: 平均延时.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "description": description}
        self.log["special"].append(res)

    def setNormalSkill(self, skillid, skillname, iconid, start, duration, num, healeff, effrate, delay, description):
        '''
        添加常规技能.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - healeff: 治疗量.
        - effrate: 有效比例.
        - delay: 平均延时.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "num": num,
               "healeff": healeff,
               "effrate": effrate,
               "delay": delay,
               "description": description}
        self.log["normal"].append(res)

    def __init__(self, startTime, finalTime):
        '''
        构造函数.
        params:
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        '''
        self.log = {"environment": [], "normal": [], "special": []}
        self.startTime = startTime
        self.finalTime = finalTime
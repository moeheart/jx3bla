# Created by moeheart at 09/22/2021
# 技能回放，用于记录与提取技能回放信息。

from tools.Functions import *

class BattleHistory():
    '''
    技能回放类，维护3个轴：场地轴，常规技能轴，特殊技能轴
    技能回放以json的形式存储.
    '''

    def getJsonReplay(self, key=""):
        '''
        获取json格式的数据.
        params:
        - key: 玩家ID，用于在点名数据中区分玩家所属的记录.
        '''
        res = {}
        res["startTime"] = self.startTime
        res["finalTime"] = self.finalTime
        res["environment"] = self.log["environment"]
        res["normal"] = self.log["normal"]
        res["special"] = self.log["special"]
        if key in self.log["call"]:
            res["call"] = self.log["call"][key]
        else:
            res["call"] = []
        return res

    def setEnvironment(self, skillid, skillname, iconid, start, duration, num, description):
        '''
        添加场地.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "num": num,
               "description": description}
        self.log["environment"].append(res)

    def setCall(self, skillid, skillname, iconid, start, duration, player, description):
        '''
        添加点名.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - player: 被点名的玩家id.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "player": player,
               "description": description}
        if player not in self.log["call"]:
            self.log["call"][player] = []
        self.log["call"][player].append(res)

    def setSpecialSkill(self, skillid, skillname, iconid, start, duration, description):
        '''
        添加特殊技能.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - description: 描述.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "description": description}
        self.log["special"].append(res)

    def setNormalSkill(self, skillid, skillname, iconid, start, duration, num, healeff, effrate, delay, busyTime, description, target=""):
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
        - busyTime: 实际所用时间.
        - description: 描述.
        - target: 目标ID，用于奶花复盘指示分队
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
               "busyTime": busyTime,
               "description": description}
        if target != "":
            res["team"] = target
        self.log["normal"].append(res)

    def getNormalEfficiency(self):
        '''
        计算常规技能的战斗效率.
        returns:
        - res: 战斗效率.
        '''
        spare = 0
        busy = 0
        lastTime = self.startTime
        for record in self.log["normal"]:
            if record["start"] > lastTime:
                spare += record["start"] - lastTime
                busy += record["busyTime"]
                lastTime = record["start"] + record["busyTime"]  # 这里暂存了spare的时间
            elif record["start"] + record["duration"] > lastTime:
                spare -= lastTime - record["start"]
                busy += record["start"] + record["busyTime"] - lastTime
                lastTime = record["start"] + record["busyTime"]
            else:
                spare -= record["busyTime"]
                busy += record["busyTime"]
            # print(spare, busy, lastTime, record["start"], record["busyTime"])
        spare += self.finalTime - lastTime
        return busy / (spare + busy + 1e-10)

    def __init__(self, startTime, finalTime):
        '''
        构造函数.
        params:
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        '''
        self.log = {"environment": [], "normal": [], "special": [], "call": {}}
        self.startTime = startTime
        self.finalTime = finalTime


class SingleSkill():
    '''
    单个技能信息类，存储连续的同名技能的相关信息.
    '''

    def initSkill(self, event):
        '''
        对新的技能进行分析.
        - event: 技能事件.
        '''
        self.skill = event.id
        self.timeStart = event.time

    def analyseSkill(self, event, castLength, skillObj=None, tunnel=False, hasteAffected=True):
        '''
        对已有的技能进行分析.
        - event: 技能事件.
        - castLength: 运功时长，按帧数计.
        - skillObj: 技能记录对象.
        - tunnel: 是否为倒读条技能.
        - hasteAffected: 读条时间是否被加速影响.
        '''
        tunnelD = 0
        if tunnel:
            tunnelD = 1
        hasteActual = self.haste
        if not hasteAffected:
            hasteActual = 0
        if skillObj is not None:
            skillObj.recordSkill(event.time, event.heal, event.healEff, self.timeEnd, delta=getLength(castLength, hasteActual))
        if self.num == 0:
            self.timeStart -= getLength(castLength, hasteActual)
        if event.time - self.timeEnd > 100 or self.num == 0:
            self.num += 1
            self.delayNum += 1
            self.delay += max(event.time - self.timeEnd - getLength(castLength, hasteActual), 0)
            singleBusy = max(getLength(self.gcd, self.haste), getLength(castLength, hasteActual))
            singleEnd = event.time + max(getLength(self.gcd, self.haste) - getLength(castLength, hasteActual), 0) * (1 - tunnelD)
            self.busy += singleBusy
            self.skillLog.append([singleBusy, singleEnd])
        self.heal += event.heal
        self.healEff += event.healEff
        self.timeEnd = event.time + max(getLength(self.gcd, self.haste) - getLength(castLength, hasteActual), 0) * (1 - tunnelD)

    def reset(self):
        '''
        重置技能信息为初始情形.
        '''
        self.skill = "0"
        self.timeStart = 0
        self.num = 0
        self.heal = 0
        self.healEff = 0
        self.delay = 0
        self.delayNum = 0
        self.busy = 0

    def __init__(self, timeEnd, haste):
        '''
        构造函数.
        params:
        - timeEnd: 上个技能gcd转完的时间. 初始情形一般为第一次进入战斗的时间.
        - haste: 加速
        '''
        self.skill = "0"
        self.timeStart = 0
        self.timeEnd = timeEnd
        self.num = 0
        self.heal = 0
        self.healEff = 0
        self.delay = 0
        self.delayNum = 0
        self.busy = 0
        self.haste = haste
        self.gcd = 24  # 一般心法的gcd都是24帧，注意加速是之后再计算
        self.skillLog = []  # 用于战斗效率计算

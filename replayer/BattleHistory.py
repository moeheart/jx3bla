# Created by moeheart at 09/22/2021
# 技能回放，用于记录与提取技能回放信息。

from tools.Functions import *

class BattleHistory():
    '''
    技能回放类，维护3个轴：场地轴，常规技能轴，特殊技能轴
    技能回放以json的形式存储.
    '''

    def setMainTarget(self, target):
        '''
        记录主目标.
        params:
        - target: 目标的key
        '''
        self.mainTargets[target] = 0

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
        res["badPeriodDps"] = self.badPeriodDpsLog
        res["badPeriodHealer"] = self.badPeriodHealerLog
        return res

    def calBadPeriod(self):
        '''
        在战斗结束时结算所有的无效时间段.
        '''
        self.badPeriodDpsLog = self.badPeriodDps.export()
        self.badPeriodHealerLog = self.badPeriodHealer.export()

    def setBadPeriod(self, start, end, affectDps=True, affectHealer=True):
        '''
        设置战斗中的无效时间段.
        params:
        - start: 开始时间点.
        - end: 结束时间点.
        - affectDps: 这个时间段是否影响dps.
        - affectHealer: 这个时间段是否影响治疗.
        '''
        if affectDps:
            self.badPeriodDps.recordInterval(start, end)
        if affectHealer:
            self.badPeriodHealer.recordInterval(start, end)

    def printEnvironmentInfo(self):
        '''
        打印所有的bldinfo. 用于调试.
        '''
        for i in range(len(self.log["environment"])):
            line = self.log["environment"][i]
            time = line["start"]
            formattedTime = parseTime((time - self.startTime) / 1000)
            id = line["skillid"]
            name = line["skillname"]
            t = line["type"]
            if line["iconid"] == "341":
                print("[Unsolved]", formattedTime, t, id, name)
            else:
                pass
                # print("[Env]", formattedTime, t, id, name)

    def setEnvironmentInfo(self, infoDict):
        '''
        通过对应表对场地轴的图片和颜色进行修正.
        params:
        - infoDict: 字典类型，从对应的事件映射到[图片ID,颜色]的数组.
        '''
        for i in range(len(self.log["environment"])):
            name = ""
            if self.log["environment"][i]["type"] == "cast":
                name = "c" + self.log["environment"][i]["skillid"]
            elif self.log["environment"][i]["type"] == "buff":
                name = "b" + self.log["environment"][i]["skillid"]
            elif self.log["environment"][i]["type"] == "skill":
                name = "s" + self.log["environment"][i]["skillid"]
            if name in infoDict:
                self.log["environment"][i]["iconid"] = infoDict[name][0]
                self.log["environment"][i]["color"] = infoDict[name][1]

    def setEnvironment(self, skillid, skillname, iconid, start, duration, num, description, type="unknown", color="#ffffff"):
        '''
        添加场地事件.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - description: 描述.
        - type: 种类，一般为cast, skill, buff, shout等
        - color: 颜色，用于显示
        '''
        res = {"skillid": skillid,
               "skillname": skillname.strip('"'),
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "num": num,
               "description": description,
               "type": type,
               "color": color}
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

    def getLastNormalSkill(self):
        '''
        获取上一次施放的常规技能.
        returns:
        - skillid: 技能ID.
        - start: 技能开始施放时间.
        '''
        if len(self.log["normal"]) == 0:
            return "0", 0
        else:
            return self.log["normal"][-1]["skillid"], self.log["normal"][-1]["start"]

    def updateNormalSkill(self, skillid, skillname, iconid, start, duration, num, heal, healeff, damage, damageEff, delay=0, busyTime=0, description="", target="", targetName=""):
        '''
        在常规技能的末尾与当前技能相同时进行更新.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - heal: 治疗量.
        - healeff: 有效治疗量.
        - damage: 伤害.
        - damageEff: 有效伤害.
        - delay: 平均延时.
        - busyTime: 实际所用时间.
        - description: 描述.
        - target: 目标ID，用于奶花复盘指示分队.
        - targetName: 目标角色名，用于复盘中进行精确显示.
        '''
        assert self.log["normal"][-1]["skillname"] == skillname
        self.log["normal"][-1]["num"] += num
        self.log["normal"][-1]["healeff"] += healeff
        self.log["normal"][-1]["heal"] += heal
        self.log["normal"][-1]["damageeff"] += damageEff
        self.log["normal"][-1]["damage"] += damage
        self.log["normal"][-1]["targetName"] += '+' + targetName

    def setNormalSkill(self, skillid, skillname, iconid, start, duration, num, heal, healeff, damage, damageEff, delay=0, busyTime=0, description="", target="", targetName=""):
        '''
        添加常规技能.
        params:
        - skillid: 技能ID.
        - skillname: 技能名，用于显示.
        - iconid: 图标ID，用于显示.
        - start: 技能开始时刻，以毫秒计.
        - duration: 技能持续时间.
        - num: 技能次数.
        - heal: 治疗量.
        - healeff: 有效治疗量.
        - damage: 伤害.
        - damageEff: 有效伤害.
        - delay: 平均延时.
        - busyTime: 实际所用时间.
        - description: 描述.
        - target: 目标ID，用于奶花复盘指示分队.
        - targetName: 目标角色名，用于复盘中进行精确显示.
        '''
        res = {"skillid": skillid,
               "skillname": skillname,
               "iconid": iconid,
               "start": start,
               "duration": duration,
               "targetName": targetName,
               "num": num,
               "heal": heal,
               "healeff": healeff,
               "damage": damage,
               "damageeff": damageEff,
               }
        if description != "":
            res["description"] = description
        if target != "":
            res["team"] = target
        self.log["normal"].append(res)

    def getNormalEfficiency(self, base="healer", nonGcdLog=[]):
        '''
        计算常规技能的战斗效率.
        returns:
        - res: 战斗效率.
        - base: 所属的心法. 会影响所使用的无效时间段.
        - nonGcd: 非gcd技能统计. 会以log的形式加入最后的统计中.
        '''

        intervals = IntervalCounter(self.startTime, self.finalTime)
        for record in self.log["normal"]:
            intervals.recordInterval(record["start"], record["start"] + record["duration"])
        for i in range(len(nonGcdLog)):
            if nonGcdLog[i][1] == 1 and i != len(nonGcdLog) - 1:
                intervals.recordInterval(nonGcdLog[i][0], nonGcdLog[i+1][0])
        targetLog = []
        if base == "healer":
            targetLog = self.badPeriodHealerLog
        elif base == "dps":
            targetLog = self.badPeriodDpsLog
        sum = 0
        for i in range(len(targetLog)):  # 反转被排除的区间
            if targetLog[i][1] == 1 and i != len(targetLog) - 1:
                intervals.recordInterval(targetLog[i][0], targetLog[i+1][0], 1)
            if targetLog[i][1] == 0 and i != len(targetLog) - 1:
                sum += targetLog[i+1][0] - targetLog[i][0]
        intervalResult = intervals.export()
        busy = 0
        lastStack = 0
        lastTime = self.startTime
        for line in intervalResult:
            if lastStack == 1:
                busy += line[0] - lastTime
            # sum += line[0] - lastTime
            lastStack = line[1]
            lastTime = line[0]
            # print("[busy]", busy, lastStack, lastTime, line)
        efficiency = safe_divide(busy, sum)

        # print("[BH-efficiency]", busy, sum)
        # print(targetLog)

        return efficiency

    def sumTime(self, exclude="none"):
        '''
        获取战斗总时间（考虑排除时间）.
        '''
        target = []
        if exclude == "healer":
            target = self.badPeriodHealerLog
        elif exclude == "dps":
            target = self.badPeriodDpsLog
        lastTime = self.startTime
        lastStack = 1
        sumTime = 0
        for line in target:
            sumTime += lastStack * (line[0] - lastTime)
            lastTime = line[0]
            lastStack = 1 - line[1]
        sumTime += lastStack * (self.finalTime - lastTime)
        return sumTime

    def __init__(self, startTime, finalTime):
        '''
        构造函数.
        params:
        - startTime: 战斗开始时间.
        - finalTime: 战斗结束时间.
        '''
        self.log = {"environment": [], "normal": [], "special": [], "call": {}, "nongcd": []}
        self.startTime = startTime
        self.finalTime = finalTime
        # 对DPS和治疗分别给出无效区间
        self.badPeriodDps = IntervalCounter(self.startTime, self.finalTime)
        self.badPeriodHealer = IntervalCounter(self.startTime, self.finalTime)
        self.badPeriodDpsLog = []
        self.badPeriodHealerLog = []
        # 记录主目标
        self.mainTargets = {}

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
            skillObj.recordSkill(event.time, event.heal, event.healEff, event.damage, event.damageEff, lastTime=self.timeEnd, delta=getLength(castLength, hasteActual))
        if self.num == 0:
            self.timeStart -= getLength(castLength, hasteActual)
        if event.time - self.timeEnd > 100 or self.num == 0:
            self.num += 1
            self.delayNum += 1
            self.delay += max(event.time - self.timeEnd - getLength(castLength, hasteActual), 0)
            singleBusy = getLength(castLength, hasteActual)
            if not tunnel:
                singleBusy = max(getLength(self.gcd, self.haste), singleBusy)
            singleEnd = event.time + max(getLength(self.gcd, self.haste) - getLength(castLength, hasteActual), 0) * (1 - tunnelD)
            self.busy += singleBusy
            self.skillLog.append([singleBusy, singleEnd])
        self.heal += event.heal
        self.healEff += event.healEff
        self.damage += event.damage
        self.damageEff += event.damageEff
        self.timeEnd = event.time + max(getLength(self.gcd, self.haste) - getLength(castLength, hasteActual), 0) * (1 - tunnelD)
        self.target = event.target

    def reset(self):
        '''
        重置技能信息为初始情形.
        '''
        self.skill = "0"
        self.timeStart = 0
        self.num = 0
        self.heal = 0
        self.healEff = 0
        self.damage = 0
        self.damageEff = 0
        self.delay = 0
        self.delayNum = 0
        self.busy = 0
        self.target = ""

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
        self.damage = 0
        self.damageEff = 0
        self.delay = 0
        self.delayNum = 0
        self.busy = 0
        self.haste = haste
        self.gcd = 24  # 一般心法的gcd都是24帧，注意加速是之后再计算
        self.skillLog = []  # 用于战斗效率计算
        self.target = ""

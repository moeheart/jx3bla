# Created by moeheart at 07/10/2022
# 战斗数据统计，维护伤害、治疗的统计及展示。

from tools.Functions import *
from replayer.Name import *

class HealCastRecorder():
    '''
    治疗量统计类.
    记录为"A用B技能治疗C，值为D效果为E"，按A-(此类)-B-C的顺序逐层封装.
    '''

    def specificName(self, id, full_id):
        '''
        根据full_id做大量特殊判定，从而实现类似于合并的效果。
        params:
        - id: 技能或buff的ID.
        - full_id: 三名ID表示法.
        '''
        res = ""
        if id == "6209":
            res = "王母挥袂(辞致)"
        elif id == "6211":
            res = "风袖低昂(晚晴)"
        elif full_id == '"1,6249,3"':
            res = "上元点鬟(双鸾)"
        elif full_id == '"1,6249,1"':
            res = "翔鸾舞柳(双鸾)"
        elif full_id == '"1,6249,1"':
            res = "翔鸾舞柳(双鸾)"
        elif id == "15181":
            res = "宫(疏影横斜)"
        elif id == "8571":
            res = "心法减伤"
        elif id == "21112":
            res = "凌然天风"
        elif id == "3307":
            res = "田螺阵"
        elif id == "15914":
            res = "斩无常"
        return res

    def getSkillName(self, full_id, info):
        '''
        根据full_id做大量特殊判定，从而实现类似于合并的效果。
        '''
        l = len(full_id.split(','))
        if l == 3:
            id = full_id.split(',')[1]
            res = info.getSkillName(full_id)
            resNew = self.specificName(id, full_id)
            if resNew != "":
                res = resNew
        elif l == 4:
            real_id = ','.join(full_id.split(',')[1:])
            area = full_id.split(',')[0]
            id = real_id.split(',')[1]
            res = info.getSkillName(real_id)
            resNew = self.specificName(id, real_id)
            if resNew != "":
                res = resNew
            nameArray = ["未知", "化解", "减伤", "吸血", "蛊惑", "响应"]
            res = "%s(%s)" % (res, nameArray[int(area)])
            if area == "3":
                res = "吸血"
            if area == "4":
                res = "蛊惑众生"
        return res


    def export(self, time, info):
        '''
        统计结束时的后处理.
        params:
        - time: 战斗时间.
        - info: bld的info类
        '''
        self.sum = 0
        for skill in self.skill:
            self.sum += self.skill[skill]["sum"]
        for skill in self.skill:
            self.skill[skill]["percent"] = self.skill[skill]["sum"] / (self.sum + 1e-10)
            self.skill[skill]["name"] = self.getSkillName(skill, info)
        self.hps = self.sum / time * 1000
        for skill in self.skill:
            if self.skill[skill]["name"] not in self.namedSkill:
                self.namedSkill[self.skill[skill]["name"]] = {"sum": self.skill[skill]["sum"],
                                                              "num": self.skill[skill]["num"],
                                                              "percent": self.skill[skill]["percent"]}
            else:
                for key in ["sum", "num", "percent"]:
                    self.namedSkill[self.skill[skill]["name"]][key] += self.skill[skill][key]


    def record(self, target, skill, value):
        '''
        记录一次治疗事件.
        params:
        - target: 目标ID(可以是数字或文字).
        - skill: 技能ID(可以是数字或文字).
        - value: 数值.
        '''
        if skill not in self.skill:
            self.skill[skill] = {"sum": 0, "num": 0}  # , "targets": {}}，暂时不记录目标
        # if target not in self.skill[skill]["targets"]:
        #     self.skill[skill]["targets"][target] = 0
        # self.skill[skill]["targets"][target] += value
        self.skill[skill]["sum"] += value
        self.skill[skill]["num"] += 1

    def __init__(self, allied):
        '''
        构造方法.
        params:
        - allied: 是否为友方.
        '''
        self.skill = {}
        self.namedSkill = {}
        self.sum = 0
        self.hps = 0

class CombatTracker():
    '''
    战斗数据统计类.
    '''

    def export(self, time):
        '''
        统计结束时的后处理.
        params:
        - time: 战斗时间.
        '''

        # hps
        hps = {"sumHps": 0, "player": {}}
        for player in self.hpsCast:
            self.hpsCast[player].export(time, self.info)
            if self.hpsCast[player].hps > 0:
                hps["player"][player] = {"sum": self.hpsCast[player].sum,
                                         "hps": self.hpsCast[player].hps,
                                         "skill": self.hpsCast[player].skill,
                                         "namedSkill": self.hpsCast[player].namedSkill}
                hps["sumHps"] += hps["player"][player]["hps"]

        # ohps
        ohps = {"sumHps": 0, "player": {}}
        for player in self.ohpsCast:
            self.ohpsCast[player].export(time, self.info)
            if self.ohpsCast[player].hps > 0:
                ohps["player"][player] = {"sum": self.ohpsCast[player].sum,
                                          "hps": self.ohpsCast[player].hps,
                                          "skill": self.ohpsCast[player].skill,
                                          "namedSkill": self.ohpsCast[player].namedSkill}
                ohps["sumHps"] += ohps["player"][player]["hps"]

        # ahps
        ahps = {"sumHps": 0, "player": {}}
        for player in self.ahpsCast:
            self.ahpsCast[player].export(time, self.info)
            if self.ahpsCast[player].hps > 0:
                ahps["player"][player] = {"sum": self.ahpsCast[player].sum,
                                          "hps": self.ahpsCast[player].hps,
                                          "skill": self.ahpsCast[player].skill,
                                          "namedSkill": self.ahpsCast[player].namedSkill}
                ahps["sumHps"] += ahps["player"][player]["hps"]

        # 简单展示类
        print("[HPS]", hps["sumHps"])
        for player in hps["player"]:
            print("[Player]", player, self.info.getName(player), hps["player"][player]["hps"], hps["player"][player]["sum"])
            for skill in hps["player"][player]["namedSkill"]:
                print("--[Skill]", skill, hps["player"][player]["namedSkill"][skill]["sum"],
                      hps["player"][player]["namedSkill"][skill]["num"], parseCent(hps["player"][player]["namedSkill"][skill]["percent"]))

        print("=================")

        print("[oHPS]", ohps["sumHps"])
        for player in ohps["player"]:
            print("[Player]", player, self.info.getName(player), ohps["player"][player]["hps"], ohps["player"][player]["sum"])
            for skill in ohps["player"][player]["namedSkill"]:
                print("--[Skill]", skill, ohps["player"][player]["namedSkill"][skill]["sum"],
                      ohps["player"][player]["namedSkill"][skill]["num"], parseCent(ohps["player"][player]["namedSkill"][skill]["percent"]))

        print("=================")

        print("[aHPS]", ahps["sumHps"])
        for player in ahps["player"]:
            print("[Player]", player, self.info.getName(player), ahps["player"][player]["hps"], ahps["player"][player]["sum"])
            for skill in ahps["player"][player]["namedSkill"]:
                print("--[Skill]", skill, ahps["player"][player]["namedSkill"][skill]["sum"],
                      ahps["player"][player]["namedSkill"][skill]["num"], parseCent(ahps["player"][player]["namedSkill"][skill]["percent"]))

    def recordBuff(self, event):
        '''
        记录buff事件.
        '''
        # if "龙葵" in self.info.getSkillName(event.full_id):
        #     print("[NameBuff]", event.time, event.id, event.caster, event.target, event.full_id)

        full_id = event.full_id.strip('"')
        lvl0_id = ','.join(full_id.split(',')[0:2])+',0'

        # 记录化解buff
        if (full_id in ABSORB_DICT or lvl0_id in ABSORB_DICT or event.id == "9334") and event.target in self.absorbBuff:
            if event.stack != 0:
                self.absorbBuff[event.target][full_id] = [event.caster, event.time]
                if full_id in self.buffRemove[event.target]:
                    del self.buffRemove[event.target][full_id]
                if event.id == "9334":  # 记录梅花三弄的来源
                    self.shieldDict[event.target] = event.caster
                # print("[GetAbsorbBuff]", event.id, event.time, event.target, event.caster)
            elif full_id in self.absorbBuff[event.target]:
                # 进行延迟移除
                if event.id != "9334":
                    self.buffRemove[event.target][full_id] = {"time": event.time + 50}
                else:  # 盾有更长的黏着时间
                    self.buffRemove[event.target][full_id] = {"time": event.time + 500}
                # del self.absorbBuff[event.target][full_id]
                # print("[DelAbsorbBuff]", event.id, event.time, event.target, event.caster)

        # 记录减伤buff
        if (full_id in RESIST_DICT or lvl0_id in RESIST_DICT) and event.target in self.resistBuff:
            if full_id in RESIST_DICT:
                resistValue = RESIST_DICT[full_id]
            else:
                resistValue = RESIST_DICT[lvl0_id]
            if event.stack != 0:
                if event.id == "9336" or event.id == "9337":
                    event.caster = self.shieldDict[event.target]
                if event.id == "8424":
                    event.caster = event.target
                self.resistBuff[event.target][full_id] = [event.caster, event.time, resistValue]
                if full_id in self.buffRemove[event.target]:
                    del self.buffRemove[event.target][full_id]
            elif full_id in self.resistBuff[event.target]:
                # 进行延迟移除
                self.buffRemove[event.target][full_id] = {"time": event.time + 50}
            # if event.id == "9336":
            #     print("[Buff9336]", event.time, event.id, event.stack)

        # 记录蛊惑
        if event.id in ["2316"]:  # 蛊惑众生
            if event.stack == 1:
                self.guHuoTarget[event.caster] = event.target
            else:
                self.guHuoTarget[event.caster] = "0"

    def checkRemoveBuff(self, time, target):
        '''
        在事件开始前将待移除列表的buff尝试移除的方法.
        params:
        - time: 本次事件的时间.
        - target: 目标玩家.
        '''

        if target in self.buffRemove:
            toRemove = []
            for id in self.buffRemove[target]:
                if self.buffRemove[target][id]["time"] <= time:
                    # 执行移除
                    toRemove.append(id)
            for id in toRemove:
                if id in self.absorbBuff[target]:
                    del self.absorbBuff[target][id]
                if id in self.resistBuff[target]:
                    del self.resistBuff[target][id]
                del self.buffRemove[target][id]


    def recordSkill(self, event):
        '''
        记录技能事件.
        '''

        # 先检验是否有需要移除的buff
        self.checkRemoveBuff(event.time, event.target)

        # 治疗事件
        if event.heal > 0 and event.effect != 7 and event.caster in self.hpsCast:
            hanQingFlag = 0
            if event.full_id == '"2,631,29"':  # 特殊处理寒清
                if event.target in self.hanQingTime and event.time - self.hanQingTime[event.target] < 500:
                    hanQingFlag = 1
                    self.hanQingTime[event.target] = 0
            if event.full_id == '"1,23951,40"':  # 特殊处理寂灭
                if self.cbyCaster in self.hpsCast:
                    self.hpsCast[self.cbyCaster].record(event.target, event.full_id, event.healEff)
                    self.ohpsCast[self.cbyCaster].record(event.target, event.full_id, event.heal)
            elif event.full_id in ['"1,23951,70"']:  # 特殊处理大针
                pass
            elif hanQingFlag:  # 寒清的响应式统计
                self.ahpsCast[event.caster].record(event.target, "5," + event.full_id, event.healEff)
            elif event.full_id in ['"1,29748,1"', '"1,23951,2"']:  # 其它响应式处理
                self.ahpsCast[event.caster].record(event.target, "5," + event.full_id, event.healEff)
            else:
                self.hpsCast[event.caster].record(event.target, event.full_id, event.healEff)
                self.ohpsCast[event.caster].record(event.target, event.full_id, event.heal)
                # 推算蛊惑产生的治疗量
                if event.caster in self.guHuoTarget and self.guHuoTarget[event.caster] != "0" and event.healEff > 0:
                    target = self.guHuoTarget[event.caster]
                    self.ohpsCast[event.caster].record(event.caster, "4," + event.full_id, event.healEff * 0.5)
                    if self.hpStatus[event.caster]["damage"] > self.hpStatus[event.caster]["healFull"] or \
                            self.hpStatus[event.caster]["healNotFull"] > self.hpStatus[event.caster]["healFull"]:
                        self.hpsCast[event.caster].record(target, "4," + event.full_id, event.healEff * 0.5)

        # elif event.heal > 0 and event.effect == 7:
        #     # 插件统计的APS
        #     print("[面板APS]", self.info.getSkillName(event.full_id), event.time, event.target, event.heal, event.id)

        # 根据治疗事件更新血量状态
        if event.heal > 0 and event.target in self.hpStatus:
            if event.heal == event.healEff:
                self.hpStatus[event.target]["healNotFull"] = event.time
            else:
                self.hpStatus[event.target]["healFull"] = event.time
            self.hpStatus[event.target]["estimateHP"] += event.heal
            if self.hpStatus[event.target]["estimateHP"] > 0:
                self.hpStatus[event.target]["estimateHP"] = 0
                self.hpStatus[event.target]["healFull"] = event.time

        # 根据伤害事件更新血量状态
        if event.damage > 0 and event.target in self.hpStatus:
            self.hpStatus[event.target]["damage"] = event.time
            self.hpStatus[event.target]["estimateHP"] -= event.damage

        # 记录一些公有技能的状态
        if event.id == "3982":
            self.cbyCaster = event.caster
        if event.id == "18274" and event.target in self.hanQingTime:
            self.hanQingTime[event.target] = event.time

        # 来源于化解的aps
        absorb = int(event.fullResult.get("9", 0))
        if absorb > 0 and event.target in self.absorbBuff:
            # print("[RawAbsorb]", event.time, event.target, absorb)
            # 目前只记录一个化解的buff，如果单次击破了某个化解盾导致有两个buff都参与了化解，那么其实无法统计到具体的化解量
            calcBuff = ["0", "0", 0]
            for key in self.absorbBuff[event.target]:
                res = self.absorbBuff[event.target][key]
                if calcBuff[1] == "0" or "9334" in calcBuff[0] or ("9334" not in key and res[1] > calcBuff[2]):
                    calcBuff = [key, res[0], res[1]]
            if calcBuff[0] != "0":
                # 记录化解
                self.ahpsCast[calcBuff[1]].record(event.target, "1," + calcBuff[0], absorb)
                # print("[复盘aHPS]", self.info.getSkillName(calcBuff[0]), event.time, event.target, absorb, calcBuff[0])

        # 来自于减伤的aps
        sumDamage = event.damage + absorb
        if sumDamage > 0 and event.target in self.resistBuff:
            # print("[Damage]", event.time, event.target, sumDamage)
            # 考虑所有减伤，如果减伤之和大于100%，则不做统计，这种情况一般不可能发生.
            resistSum = 0
            for key in self.resistBuff[event.target]:
                resistSum += self.resistBuff[event.target][key][2]
            if resistSum > 0 and resistSum < 1024:
                damageOrigin = sumDamage / (1 - resistSum / 1024)
                for key in self.resistBuff[event.target]:
                    res = self.resistBuff[event.target][key]
                    damageResist = int(damageOrigin * (res[2] / 1024))
                    # print("[ResistRes]", key, sumDamage, resistSum, damageOrigin, damageResist, res)
                    if res[0] in self.ahpsCast and damageResist < 1000000:
                        self.ahpsCast[res[0]].record(event.target, "2," + key, damageResist)

        # 从吸血推测HPS
        xixue = int(event.fullResult.get("7", 0))
        if xixue > 0 and event.caster in self.hpStatus:
            # print("[Xixue]", event.time, event.caster, xixue)
            self.ohpsCast[event.caster].record(event.caster, "3," + event.full_id, xixue)
            if self.hpStatus[event.caster]["damage"] > self.hpStatus[event.caster]["healFull"] or \
              self.hpStatus[event.caster]["healNotFull"] > self.hpStatus[event.caster]["healFull"]:
                self.hpsCast[event.caster].record(event.caster, "3," + event.full_id, xixue)

            self.hpStatus[event.caster]["estimateHP"] += xixue
            if self.hpStatus[event.caster]["estimateHP"] > 0:
                self.hpStatus[event.caster]["estimateHP"] = 0
                self.hpStatus[event.caster]["healFull"] = event.time

    def __init__(self, info):
        '''
        构造方法，需要读取角色或玩家信息。
        params:
        - info: bld读取的玩家信息.
        '''
        self.hpsCast = {}
        self.ohpsCast = {}
        self.ahpsCast = {}
        self.info = info

        self.absorbBuff = {}
        self.resistBuff = {}
        self.shieldDict = {}
        self.buffRemove = {}  # buff延迟删除

        self.hpStatus = {}

        self.cbyCaster = "0"  # 记录慈悲愿
        self.guHuoTarget = {}  # 记录蛊惑
        self.hanQingTime = {}  # 记录寒清时间

        for player in info.player:
            self.hpsCast[player] = HealCastRecorder(1)
            self.ohpsCast[player] = HealCastRecorder(1)
            self.ahpsCast[player] = HealCastRecorder(1)
            self.absorbBuff[player] = {}
            self.resistBuff[player] = {}
            self.buffRemove[player] = {}
            self.shieldDict[player] = "0"
            self.hpStatus[player] = {"damage": 0, "healNotFull": 0, "healFull": 0, "estimateHP": 0}
            self.guHuoTarget[player] = "0"
            self.hanQingTime[player] = 0
        for player in info.npc:
            self.hpsCast[player] = HealCastRecorder(0)
            self.ohpsCast[player] = HealCastRecorder(0)
            self.ahpsCast[player] = HealCastRecorder(0)

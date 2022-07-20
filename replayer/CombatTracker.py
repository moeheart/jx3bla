# Created by moeheart at 07/10/2022
# 战斗数据统计，维护伤害、治疗的统计及展示。

from tools.Functions import *
from replayer.Name import *

class HealCastRecorder():
    '''
    治疗量统计类.
    记录为"A用B技能治疗C，值为D效果为E"，按A-(此类)-B-C的顺序逐层封装.
    '''

    def getSkillName(self, full_id, info):
        '''
        根据full_id做大量特殊判定，从而实现类似于合并的效果。
        '''
        l = len(full_id.split(','))
        if l == 3:
            id = full_id.split(',')[1]
            res = info.getSkillName(full_id)
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
        elif l == 4:
            real_id = ','.join(full_id.split(',')[1:])
            area = full_id.split(',')[0]
            res = info.getSkillName(real_id)
            nameArray = ["未知", "化解"]
            res = "%s(%s)" % (res, nameArray[int(area)])

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

        print("[aHPS]", ahps["sumHps"])
        for player in ahps["player"]:
            print("[Player]", player, self.info.getName(player), ahps["player"][player]["hps"], ahps["player"][player]["sum"])
            for skill in ahps["player"][player]["namedSkill"]:
                print("--[Skill]", skill, ahps["player"][player]["namedSkill"][skill]["sum"],
                      ahps["player"][player]["namedSkill"][skill]["num"], parseCent(ahps["player"][player]["namedSkill"][skill]["percent"]))

        # print("[oHPS]", ohps["sumHps"])
        # for player in ohps["player"]:
        #     print("[Player]", ohps["player"][player]["hps"], ohps["player"][player]["sum"])
        #     for skill in ohps["player"][player]["skill"]:
        #         print("--[Skill]", skill, hps["player"][player]["skill"][skill]["name"], ohps["player"][player]["skill"][skill]["sum"], parseCent(ohps["player"][player]["skill"][skill]["percent"]))

    def recordBuff(self, event):
        '''
        记录buff事件.
        '''
        # if "龙葵" in self.info.getSkillName(event.full_id):
        #     print("[NameBuff]", event.time, event.id, event.caster, event.target, event.full_id)

        # 记录化解buff
        full_id = event.full_id.strip('"')
        lvl0_id = ','.join(full_id.split(',')[0:2])+',0'
        if (full_id in ABSORB_DICT or lvl0_id in ABSORB_DICT or event.id == "9334") and event.target in self.absorbBuff:
            if event.stack != 0:
                self.absorbBuff[event.target][full_id] = [event.caster, event.time]
                # print("[GetAbsorbBuff]", event.id, event.time, event.target, event.caster)
            elif full_id in self.absorbBuff[event.target]:
                del self.absorbBuff[event.target][full_id]
                # print("[DelAbsorbBuff]", event.id, event.time, event.target, event.caster)


    def recordSkill(self, event):
        '''
        记录技能事件.
        '''
        # 治疗事件
        if event.heal > 0 and event.effect != 7:
            self.hpsCast[event.caster].record(event.target, event.full_id, event.healEff)
            self.ohpsCast[event.caster].record(event.target, event.full_id, event.heal)
        elif event.heal > 0 and event.effect == 7:
            # 插件统计的APS
            print("[面板APS]", self.info.getSkillName(event.full_id), event.time, event.target, event.heal, event.id)

        # 来源于化解的aps
        absorb = int(event.fullResult.get("9", 0))
        if absorb > 0 and event.target in self.absorbBuff:
            print("[RawAbsorb]", event.time, event.target, absorb)
            # 目前只记录一个化解的buff，如果单次击破了某个化解盾导致有两个buff都参与了化解，那么其实无法统计到具体的化解量
            calcBuff = ["0", "0", 0]
            for key in self.absorbBuff[event.target]:
                res = self.absorbBuff[event.target][key]
                if calcBuff[1] == "0" or "9334" in calcBuff[0] or ("9334" not in key and res[1] > calcBuff[2]):
                    calcBuff = [key, res[0], res[1]]
            if calcBuff[0] != "0":
                # 记录化解
                self.ahpsCast[calcBuff[1]].record(event.target, "1," + calcBuff[0], absorb)
                print("[复盘aHPS]", self.info.getSkillName(calcBuff[0]), event.time, event.target, absorb, calcBuff[0])

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

        for player in info.player:
            self.hpsCast[player] = HealCastRecorder(1)
            self.ohpsCast[player] = HealCastRecorder(1)
            self.ahpsCast[player] = HealCastRecorder(1)
            self.absorbBuff[player] = {}
        for player in info.npc:
            self.hpsCast[player] = HealCastRecorder(0)
            self.ohpsCast[player] = HealCastRecorder(0)
            self.ahpsCast[player] = HealCastRecorder(0)

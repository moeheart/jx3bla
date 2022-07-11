# Created by moeheart at 07/10/2022
# 战斗数据统计，维护伤害、治疗的统计及展示。

from tools.Functions import *

class HealCastRecorder():
    '''
    治疗量统计类.
    记录为"A用B技能治疗C，值为D效果为E"，按A-(此类)-B-C的顺序逐层封装.
    '''

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
            self.skill[skill]["name"] = info.getSkillName(skill)
        self.hps = self.sum / time * 1000

    def record(self, target, skill, value):
        '''
        记录一次治疗事件.
        params:
        - target: 目标ID(可以是数字或文字).
        - skill: 技能ID(可以是数字或文字).
        - value: 数值.
        '''
        if skill not in self.skill:
            self.skill[skill] = {"sum": 0, "targets": {}}
        if target not in self.skill[skill]["targets"]:
            self.skill[skill]["targets"][target] = 0
        self.skill[skill]["targets"][target] += value
        self.skill[skill]["sum"] += value

    def __init__(self, allied):
        '''
        构造方法.
        params:
        - allied: 是否为友方.
        '''
        self.skill = {}
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
                                         "skill": self.hpsCast[player].skill}
                hps["sumHps"] += hps["player"][player]["hps"]

        # ohps
        ohps = {"sumHps": 0, "player": {}}
        for player in self.hpsCast:
            self.ohpsCast[player].export(time, self.info)
            if self.ohpsCast[player].hps > 0:
                ohps["player"][player] = {"sum": self.hpsCast[player].sum,
                                          "hps": self.hpsCast[player].hps,
                                          "skill": self.hpsCast[player].skill}
                ohps["sumHps"] += ohps["player"][player]["hps"]

        # 简单展示类
        print("[HPS]", hps["sumHps"])
        for player in hps["player"]:
            print("[Player]", player, self.info.getName(player), hps["player"][player]["hps"], hps["player"][player]["sum"])
            for skill in hps["player"][player]["skill"]:
                print("--[Skill]", skill, hps["player"][player]["skill"][skill]["name"], hps["player"][player]["skill"][skill]["sum"], parseCent(hps["player"][player]["skill"][skill]["percent"]))

        # print("[oHPS]", ohps["sumHps"])
        # for player in ohps["player"]:
        #     print("[Player]", ohps["player"][player]["hps"], ohps["player"][player]["sum"])
        #     for skill in ohps["player"][player]["skill"]:
        #         print("--[Skill]", skill, hps["player"][player]["skill"][skill]["name"], ohps["player"][player]["skill"][skill]["sum"], parseCent(ohps["player"][player]["skill"][skill]["percent"]))

    def recordEvent(self, event):
        '''
        记录一个事件.
        '''
        # 治疗事件
        if event.heal > 0:
            self.hpsCast[event.caster].record(event.target, event.full_id, event.healEff)
            self.ohpsCast[event.caster].record(event.target, event.full_id, event.heal)

    def __init__(self, info):
        '''
        构造方法，需要读取角色或玩家信息。
        params:
        - info: bld读取的玩家信息.
        '''
        self.hpsCast = {}
        self.ohpsCast = {}
        self.info = info

        for player in info.player:
            self.hpsCast[player] = HealCastRecorder(1)
            self.ohpsCast[player] = HealCastRecorder(1)
        for player in info.npc:
            self.hpsCast[player] = HealCastRecorder(0)
            self.ohpsCast[player] = HealCastRecorder(0)

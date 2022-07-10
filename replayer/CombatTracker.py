# Created by moeheart at 07/10/2022
# 战斗数据统计，维护伤害、治疗的统计及展示。

class HealCastRecorder():
    '''
    治疗量统计类.
    '''

    def record(self, target, skill, value):
        '''
        记录一次治疗事件.
        params:
        - target: 目标ID(可以是数字或文字).
        - skill: 技能ID(可以是数字或文字).
        - value: 数值.
        '''
        pass

    def __init__(self, allied):
        '''
        构造方法.
        params:
        - allied: 是否为友方.
        '''
        self.skill = {}

class CombatTracker():
    '''
    战斗数据统计类.
    '''

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

        for player in info.player:
            self.hpsCast[player] = HealCastRecorder(1)
            self.ohpsCast[player] = HealCastRecorder(1)
        for player in info.npc:
            self.hpsCast[player] = HealCastRecorder(0)
            self.ohpsCast[player] = HealCastRecorder(0)

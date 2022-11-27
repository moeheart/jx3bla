# Created by moeheart at 09/03/2021
# 复盘日志内容集合，主要包含复盘的全局数据与单条数据的通用形式，兼容jx3dat与jcl。

from replayer.Name import *

class SingleData():
    '''
    单条日志，包含全部形式。
    具体形式均继承自此类。
    在子类的文档中会说明具体内容的意义，来源参考：
    https://github.com/tinymins/MY/wiki/MY-Combat-Log-DS
    https://github.com/tinymins/MY/wiki/MY-Recount-Data-Structure
    https://www.jx3box.com/bbs/27776
    注意：来源均为luaTable转写的dict，下标从1开始.
    '''

    def setByJcl(self, jclItem):
        pass

    def setByJx3dat(self, jx3datItem):
        pass

    def getType(self):
        return self.dataType

    def __init__(self):
        self.dataType = "Empty"

class SingleDataBuff(SingleData):
    '''
    Buff事件，对应jx3dat-5, jcl-13
    buff事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      frame: 逻辑帧，对应jx3dat[x], jcl[2]
      caster: 来源ID，对应jx3dat[5], jcl[6][10]
      target: 目标ID，对应jx3dat[6], jcl[6][1]
      id: buffID，对应jx3dat[7], jcl[6][5]
      level: buff等级，对应jx3dat[8], jcl[6][9]
      delete: 是否为消亡，对应jx3dat[10], jcl[6][2]
      stack: buff层数，对应jx3dat[11], jcl[6][6]
      end: 消亡预计的逻辑帧，对应jx3dat[12], jcl[6][7]
      cancel: 是否可以点掉，对应jx3dat[13], jcl[6][4]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.frame = int(item[1])
        self.caster = item[5]["10"]
        self.target = item[5]["1"]
        self.id = item[5]["5"]
        self.level = int(item[5]["9"])
        self.full_id = "2,%s,%d" % (self.id, self.level)
        self.delete = item[5]["2"]
        self.stack = int(item[5]["6"])
        self.end = int(item[5]["7"])
        self.cancel = item[5]["4"]

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        self.time = int(item["3"])
        self.frame = int(item["1"])
        self.caster = item["5"]
        self.target = item["6"]
        self.id = item["7"]
        self.level = int(item["8"])
        self.full_id = item["9"]
        self.delete = item["10"]
        self.stack = int(item["11"])
        self.end = int(item["12"])
        self.cancel = item["13"]

    def __init__(self):
        self.dataType = "Buff"

class SingleDataSkill(SingleData):
    '''
    技能事件，对应jx3dat-1, jcl-21
    技能事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      caster: 来源ID，对应jx3dat[5], jcl[6][1]
      target: 目标ID，对应jx3dat[6], jcl[6][2]
      scheme: 种类, 对应jx3dat[7], jcl[6][4]
      id: 技能ID，对应jx3dat[8], jcl[6][5]
      level: 技能等级，对应jx3dat[9], jcl[6][6]
      full_id: 完整ID，对应jx3dat[10, jcl[6][4-6]（推导）
      effect: 结果，对应jx3dat[11], jcl无内容（需要修复jx3dat逻辑）
      heal: 治疗, 对应jx3dat[12], jcl[6][9][6]
      healEff: 有效治疗, 对应jx3dat[13], jcl[6][9][14]
      damage: 伤害, 对应jx3dat[14], jcl[6][9][0-4]（推导）
      damageEff: 有效伤害, 对应jx3dat[15], jcl[6][9][13]
      fullResult: 完整结果, 对应jx3dat[16], jcl[6][9]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.caster = item[5]["1"]
        self.target = item[5]["2"]
        self.scheme = int(item[5]["4"])
        self.id = item[5]["5"]
        self.level = int(item[5]["6"])
        self.full_id = '"%d,%s,%d"'%(self.scheme, self.id, self.level)
        self.effect = 0
        self.heal = int(item[5]["9"].get("6", 0))
        self.healEff = int(item[5]["9"].get("14", 0))
        self.damage = int(item[5]["9"].get("0", 0)) + int(item[5]["9"].get("1", 0)) + \
                      int(item[5]["9"].get("2", 0)) + int(item[5]["9"].get("3", 0)) + \
                      int(item[5]["9"].get("4", 0))
        self.damageEff = int(item[5]["9"].get("13", 0))
        self.fullResult = item[5]["9"]

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        self.time = int(item["3"])
        self.caster = item["5"]
        self.target = item["6"]
        self.scheme = int(item["7"])
        self.id = item["8"]
        self.level = int(item["9"])
        self.full_id = item["10"]
        self.effect = int(item["11"])
        self.heal = int(item["12"])
        self.healEff = int(item["13"])
        self.damage = int(item["14"])
        self.damageEff = int(item["15"])
        self.fullResult = item["16"]

    def __init__(self):
        self.dataType = "Skill"

class SingleDataDeath(SingleData):
    '''
    重伤事件，对应jx3dat-3, jcl-28
    重伤事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      id: 重伤者ID，对应jx3dat[5], jcl[6][1]
      killer: 击杀者ID，对应jx3dat[6], jcl[6][2]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.id = item[5]["1"]
        if "2" in item[5]:
            self.killer = item[5]["2"]
        else:
            self.killer = "0"

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        self.time = int(item["3"])
        self.id = item["5"]
        self.killer = item["6"]

    def __init__(self):
        self.dataType = "Death"

class SingleDataShout(SingleData):
    '''
    喊话事件，对应jx3dat-8, jcl-14
    喊话事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      content: 喊话内容, 对应jx3dat[5], jcl[6][1]
      id: 喊话者ID, 对应jx3dat[6], jcl[6][2]
      name: 喊话者名字, 对应jx3dat[7], jcl[6][4]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        # print("[JclDebug]", item)
        self.time = int(item[3])
        if "1" in item[5]:
            self.content = item[5]["1"]
        else:
            self.content = ""
        self.id = item[5]["2"]
        self.name = item[5]["4"]

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        # print("[DataShout]", item)
        self.time = int(item["3"])
        self.content = item["5"]
        self.id = item["6"]
        self.name = item["7"]

    def __init__(self):
        self.dataType = "Shout"

class SingleDataBattle(SingleData):
    '''
    战斗状态变化事件，对应jx3dat-10, jcl-5/9
    战斗状态变化事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      id: ID, 对应jx3dat[6], jcl[6][1]
      fight: 是否为进战, 对应jx3dat[7], jcl[6][2]
      hp: 当前气血, 对应jx3dat[10], jcl[6][3]
      hpMax: 气血上限, 对应jx3dat[11], jcl[6][4]
      mp: 当前内力, 对应jx3dat[12], jcl[6][5]
      mpMax: 内力上限, 对应jx3dat[13], jcl[6][6]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.id = item[5]["1"]
        self.fight = item[5]["2"]
        if self.fight == "true":
            self.fight = 1
        elif self.fight == "false":
            self.fight = 0
        self.hp = int(item[5]["3"])
        self.hpMax = int(item[5]["4"])
        self.mp = int(item[5]["5"])
        self.mpMax = int(item[5]["6"])

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        self.time = int(item["3"])
        self.id = item["6"]
        self.fight = item["7"]
        if self.fight == "true":
            self.fight = 1
        elif self.fight == "false":
            self.fight = 0
        self.hp = int(item["10"])
        self.hpMax = int(item["11"])
        self.mp = int(item["12"])
        self.mpMax = int(item["13"])

    def __init__(self):
        self.dataType = "Battle"

class SingleDataScene(SingleData):
    '''
    进入或离开场景事件，对应jx3dat-6, jcl-2/3/6/7/10/11
    战斗状态变化事件包括：
      time: 毫秒数，对应jx3dat[3], jcl[4]
      id: ID, 对应jx3dat[7], jcl[6][1]
      enter: 是否为进入场景，1为是，0为否，对应jx3dat[5], jcl[5]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.id = item[5]["1"]
        if item[4] in ["2", "6", "10"]:
            self.enter = 1
        else:
            self.enter = 0

    def setByJx3dat(self, item):
        '''
        从jx3dat形式的item获取事件信息并记录.
        params:
        - item: jx3dat形式的事件信息.
        '''
        self.time = int(item["3"])
        self.id = item["7"]
        self.enter = int(item["5"])

    def __init__(self):
        self.dataType = "Scene"

class SingleDataCast(SingleData):
    '''
    施放技能事件，对应jx3dat-NaN, jcl-19
    施放技能事件：
      time: 毫秒数，对应jcl[4]
      caster: 施放者ID，对应jcl[6][1]
      id: 技能ID, 对应jcl[6][2]
      level: 技能等级，对应jcl[6][3]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.caster = item[5]["1"]
        self.id = item[5]["2"]
        self.level = int(item[5]["3"])
        self.full_id = "1,%s,%d" % (self.id, self.level)

    def setByJx3dat(self, item):
        '''
        jx3dat暂无此记录.
        '''
        pass

    def __init__(self):
        self.dataType = "Cast"

class SingleDataAlert(SingleData):
    '''
    系统警告事件，对应jx3dat-NaN, jcl-19
    系统警告事件：
      time: 毫秒数，对应jcl[4]
      type: 信息类型（MSG_NOTICE_GREEN，MSG_NOTICE_YELLOW，MSG_NOTICE_RED中的一个），对应jcl[6][1]
      content: 信息内容, 对应jcl[6][2]
    '''

    def setByJcl(self, item):
        '''
        从jcl形式的item获取事件信息并记录.
        params:
        - item: jcl形式的事件信息.
        '''
        self.time = int(item[3])
        self.type = item[5]["1"]
        if "2" in item[5]:
            self.content = item[5]["2"]
        else:
            self.content = ""

    def setByJx3dat(self, item):
        '''
        jx3dat有，但是回头再确认吧.
        '''
        pass

    def __init__(self):
        self.dataType = "Alert"

class NPCdata():
    '''
    单条NPC数据。玩家也属于特殊的NPC。
    '''

    def __init__(self):
        self.name = "未知"
        self.occ = "0"
        self.xf = "0"  # 心法
        self.equipScore = 0
        self.equip = {}
        self.qx = {}

class OverallData():
    '''
    全局数据.
    全局数据包括以下信息，会根据用途更新.
      player: 角色信息，dict格式
        [key]: 角色ID，对应jx3dat多处，jcl-4[1].
        name: 角色名字符串，对应jx3dat-9, jcl-4[2].
        occ: 心法代码，对应jx3dat-10, jcl-4[4]，注意需要经过一步转换.
        equip: 装备，对应jx3dat-18, jcl-4[6].
        qx: 奇穴，jx3dat暂无，jcl-4[7].
        equipScore: 装分.
        xf: 心法.
      npc: NPC信息，dict格式.
        [key], NPCID，对应jx3dat多处，jcl-7[1].
        name: 名字字符串.
        templateID: 模板ID.
      skill: 技能名缓存，对应jx3dat-11, jcl暂无此数据（需要从解包中手动读，暂时不做实现，何必呢）
      server: 服务器，对应jx3dat-19, jcl-1[2][2].
      map: 地图（记录名称而非ID），对应jx3dat-20, jcl-文件名.
      boss: BOSS名称，对应jx3dat-文件名，jcl-文件名.
      battleTime: 战斗开始时间戳，对应jx3dat-4, jcl-1[2][3].
      sumTime: 战斗时长毫秒数，对应jx3dat-7, jcl-1[3].
    '''

    def getSkillName(self, full_id):
        '''
        根据技能ID获取技能名.
        '''
        full_id = full_id.strip('"')
        lvl0_id = ','.join(full_id.split(',')[0:2])+',0'
        if full_id in self.skill:
            return self.skill[full_id]["1"].strip('"')
        elif full_id in SKILL_NAME:
            return SKILL_NAME[full_id]
        elif lvl0_id in SKILL_NAME:
            return SKILL_NAME[lvl0_id]
        else:
            return full_id

    def getOcc(self, key):
        '''
        根据玩家或NPC的ID获取心法，防止player和npc类中不存在的问题.
        '''
        if key in self.player:
            return self.player[key].occ
        else:
            return "0"

    def getName(self, key):
        '''
        根据玩家或NPC的ID获取名字，防止player和npc类中不存在的问题.
        '''
        if key in self.player:
            return self.player[key].name
        elif key in self.npc:
            return self.npc[key].name
        else:
            return key

    def addPlayer(self, key, name, occ):
        '''
        添加一个玩家信息. 如果有装备和奇穴信息，需要手动增补.
        parmas:
        - key: 玩家ID。
        - name: 玩家的名字.
        - occ: 心法代码.
        returns:
        - flag: 如果是第一次添加玩家信息为True, 否则为False
        '''
        if key not in self.player:
            self.player[key] = NPCdata()
            self.player[key].name = name.strip('"')
            self.player[key].occ = occ
            self.player[key].equip = {}
            return True
        elif self.player[key].name == "" or self.player[key].occ == "":
            self.player[key].name = name.strip('"')
            self.player[key].occ = occ
            self.player[key].equip = {}
            return True
        elif self.player[key].equip == {}:
            return True
        else:
            return False

    def addNPC(self, key, name):
        '''
        添加一个NPC.
        parmas:
        - key: NPC的ID。
        - name: NPC的名字.
        '''
        if key not in self.npc:
            self.npc[key] = NPCdata()
            self.npc[key].name = name.strip('"')
            self.npc[key].templateID = "0"

    def addDoodad(self, key, templateID):
        '''
        添加一个交互物件.
        parmas:
        - key: NPC的ID。
        - templateID: 交互物件模板ID.
        '''
        if key not in self.npc:
            self.doodad[key] = NPCdata()
            self.doodad[key].templateID = templateID

    def __init__(self):
        self.player = {}
        self.npc = {}
        self.doodad = {}


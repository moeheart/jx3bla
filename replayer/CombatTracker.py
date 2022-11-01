# Created by moeheart at 07/10/2022
# 战斗数据统计，维护伤害、治疗的统计及展示。

from tools.Functions import *
from replayer.Name import *
from equip.AttributeData import *
import time

SUM_TIME = 0
SUM1 = 0
SUM2 = 0
SUM3 = 0
SUM4 = 0
SUM5 = 0

def getDamageCoeff(occ, attrib, targetBoosts, lvl=114, isPoZhao=0):
    '''
    根据最终面板属性和目标增益获取伤害系数.
    params:
    - occ: 心法.
    - attrib: 最终面板属性.
    - targetBoosts: 目标增益.
    - lvl: 目标等级. 会决定目标的防御，从而影响无视防御的结果.
    - isPoZhao: 是否是破招伤害.
    '''

    global SUM1
    startTime = time.time()

    base = attrib.get("攻击", 0)
    if isPoZhao:
        base = attrib.get("破招", 0)
    crit = 1 + min(attrib.get("会心", 0), 1) * min(attrib.get("会心效果", 0), 3)
    over = 1 + attrib.get("破防", 0)
    strain = 1 + attrib.get("无双", 0)
    damageAdd1 = 1 + attrib.get("伤害变化", 0) / 1024
    targetBoostsDict = {}
    for boost in targetBoosts:
        for key in boost:
            targetBoostsDict[key] = targetBoostsDict.get(key, 0) + boost[key]
    shieldParam = {"120": 42000.75, "121": 44291.7, "122": 46582.65, "123": 48873.6, "124": 51164.55,
                   "110": 19091.25, "111": 20132.6, "112": 21173.95, "113": 22215.3, "114": 23256.6}[str(lvl)]
    shieldBase = {"110": 7060, "111": 7060, "112": 7060, "113": 11966, "114": 12528,
                  "120": 15528, "121": 15528, "122": 15528, "123": 26317, "124": 26317}[str(lvl)]

    availableBoostDict = {}
    playerType = attrib["类型"]
    for boost in targetBoostsDict:
        if boost in ATTRIB_TYPE:
            desc = ATTRIB_TYPE[boost]
            if desc[playerType+1] == 1:
                availableBoostDict[desc[0]] = availableBoostDict.get(desc[0], 0) + targetBoostsDict[boost]

    damageAdd2 = 1 + availableBoostDict.get("受伤增加", 0) / 1024
    shieldBase += availableBoostDict.get("防御", 0)
    shieldBase += shieldBase * availableBoostDict.get("防御%", 0) / 1024
    shieldBase = max(shieldBase, 0)
    shieldBase -= shieldBase * attrib.get("无视防御A", 0) / 1024
    shieldRate = 1 - min(shieldBase / (shieldBase + shieldParam), 0.75)

    endTime = time.time()
    SUM1 += endTime - startTime

    # print("[Calculate]", base, crit, over, strain, damageAdd1, damageAdd2, shieldRate)
    return base * crit * over * strain * damageAdd1 * damageAdd2 * shieldRate

class BoostCounter():
    '''
    统计增益，计算增益的来源的贡献占比.
    '''

    def calculateCoeff(self, target, skill):
        '''
        重新计算所有的增益系数. 一般在buff变动的时候进行计算.
        params:
        - target: 需要计算的目标.
        - skill: 需要计算的技能.
        '''

        isPoZhao = 0
        if skill == "破招":
            isPoZhao = 1

        if target not in self.rdpsRate:
            self.rdpsRate[target] = {}
        self.rdpsRate[target][skill] = {}
        rdpsSeparateRate = {}

        # 计算仅自身增益的伤害
        boosts = []
        for boost in self.boost:
            if self.boost[boost]["source"] == self.playerid:
                boosts.append(self.boost[boost]["effect"])
        self.attributeData.setBoosts(boosts)
        finalAttrib = self.attributeData.getFinalAttrib()
        targetBoosts = []
        for boost in self.targetBoost[target]:
            if self.targetBoost[target][boost]["source"] == self.playerid:
                targetBoosts.append(self.targetBoost[target][boost]["effect"])
        coeffSelf = getDamageCoeff(self.occ, finalAttrib, targetBoosts, isPoZhao=isPoZhao)

        sumCoeff = 0

        # 计算全增益的伤害
        boosts = []
        for boost in self.boost:
            boosts.append(self.boost[boost]["effect"])
        self.attributeData.setBoosts(boosts)
        # print("[Boosts]", boosts)
        finalAttrib = self.attributeData.getFinalAttrib()
        targetBoosts = []
        for boost in self.targetBoost[target]:
            targetBoosts.append(self.targetBoost[target][boost]["effect"])
        coeffAll = getDamageCoeff(self.occ, finalAttrib, targetBoosts, isPoZhao=isPoZhao)

        self.attributeData2.setBoosts(boosts)
        self.attributeData2.getFinalAttrib()

        # 计算特殊情况，转移全部来源.
        if skill == "相知玉简" and self.mhsn != "0":
            coeffSelf = 0
            baseBoost = "1,21827,1"
            rdpsSeparateRate[baseBoost] = {"source": self.mhsn,
                                           "amount": coeffAll}
            sumCoeff += rdpsSeparateRate[baseBoost]["amount"]
        if skill == "逐云寒蕊" and self.zyhr != "0":
            coeffSelf = 0
            baseBoost = "1,29532,1"
            rdpsSeparateRate[baseBoost] = {"source": self.zyhr,
                                           "amount": coeffAll}
            sumCoeff += rdpsSeparateRate[baseBoost]["amount"]

        # 计算排除某个增益的伤害，并记录
        targetBoosts = []
        for boost in self.targetBoost[target]:
            targetBoosts.append(self.targetBoost[target][boost]["effect"])
        for baseBoost in self.boost:
            if self.boost[baseBoost]["source"] == self.playerid:
                continue
            boosts = []
            for boost in self.boost:
                if boost != baseBoost:
                    boosts.append(self.boost[boost]["effect"])
            self.attributeData.setBoosts(boosts)
            finalAttrib = self.attributeData.getFinalAttrib()
            coeffSpecific = getDamageCoeff(self.occ, finalAttrib, targetBoosts, isPoZhao=isPoZhao)

            finalAttrib2 = self.attributeData2.removeBoostAndGetAttrib(self.boost[baseBoost]["effect"])
            self.attributeData2.addBoostAndGetAttrib(self.boost[baseBoost]["effect"])
            coeffSpecific2 = getDamageCoeff(self.occ, finalAttrib2, targetBoosts, isPoZhao=isPoZhao)

            # print("[Test]", self.boost[baseBoost])

            diff = coeffSpecific - coeffSpecific2
            if abs(diff) > 1e-5:
                print("[DifferentA]", coeffSpecific, coeffSpecific2)
                print(finalAttrib)
                print(finalAttrib2)

            rdpsSeparateRate[baseBoost] = {"source": self.boost[baseBoost]["source"],
                                           "amount": coeffAll - coeffSpecific}
            sumCoeff += rdpsSeparateRate[baseBoost]["amount"]

        # 计算排除某个目标增益的伤害，并记录
        boosts = []
        for boost in self.boost:
            boosts.append(self.boost[boost]["effect"])
        self.attributeData.setBoosts(boosts)
        finalAttrib = self.attributeData.getFinalAttrib()
        for baseBoost in self.targetBoost[target]:
            if self.targetBoost[target][baseBoost]["source"] == self.playerid:
                continue
            targetBoosts = []
            for boost in self.targetBoost[target]:
                if boost != baseBoost:
                    targetBoosts.append(self.targetBoost[target][boost]["effect"])
            coeffSpecific = getDamageCoeff(self.occ, finalAttrib, targetBoosts, isPoZhao=isPoZhao)

            rdpsSeparateRate[baseBoost] = {"source": self.targetBoost[target][baseBoost]["source"],
                                           "amount": coeffAll - coeffSpecific}
            sumCoeff += rdpsSeparateRate[baseBoost]["amount"]

        # 计算结果
        for boost in rdpsSeparateRate:
            rate = safe_divide(rdpsSeparateRate[boost]["amount"], sumCoeff) * safe_divide(coeffAll - coeffSelf, coeffAll)
            if rate > 0:
                self.rdpsRate[target][skill][boost] = {"source": rdpsSeparateRate[boost]["source"],
                                                       "rate": rate}
        self.rdpsRate[target][skill]["self"] = {"source": self.playerid,
                                                "rate": safe_divide(coeffSelf, coeffAll)}


    def getRate(self, target, skill, skillName):
        '''
        获取rDPS比例.
        params:
        - target: 目标ID.
        - skill: 技能ID.
        - skillName: 技能名.
        '''

        if target not in self.targetBoost:
            target = "all"
        if skillName in ["逐云寒蕊"]:
            skill = "逐云寒蕊"
        elif skillName in ["相知·玉简"]:
            skill = "相知玉简"
        elif skillName in ["破", "破·虚空"]:
            skill = "破招"
        else:
            skill = "all"

        reCalFlag = False
        if target not in self.rdpsRate or skill not in self.rdpsRate[target]:
            reCalFlag = True
        if target not in self.needUpdate or skill not in self.needUpdate[target] or self.needUpdate[target][skill]:
            reCalFlag = True
        if reCalFlag:
            self.calculateCoeff(target, skill)
            if target not in self.needUpdate:
                self.needUpdate[target] = {}
            self.needUpdate[target][skill] = False

        return self.rdpsRate[target][skill]

    def SetUpdateFlag(self, target="all"):
        '''
        设定所有数值为需要更新的状态. 通常在增益变化时调用.
        params:
        - target: 增益变化的目标. 为"all"时影响所有目标.
        '''

        if target == "all":
            for targetid in self.rdpsRate:
                for skill in self.rdpsRate[targetid]:
                    self.needUpdate[targetid][skill] = True
        else:
            if target in self.rdpsRate:
                for skill in self.rdpsRate[target]:
                    self.needUpdate[target][skill] = True

    def removeTargetBoost(self, targetid, id):
        '''
        移除一个目标增益.
        params:
        - targetid: 目标ID.
        - id: 增益的id，一般是buffID.
        '''
        if targetid not in self.targetBoost:
            self.targetBoost[targetid] = {}
        elif id in self.targetBoost[targetid]:
            del self.targetBoost[targetid][id]
            if self.targetBoost[targetid] == {}:
                del self.targetBoost[targetid]
            self.SetUpdateFlag(targetid)

    def addTargetBoost(self, targetid, id, effect, source, stack):
        '''
        添加一个目标增益.
        params:
        - targetid: 目标ID.
        - id: 增益的id，一般是buffID.
        - effect: 增益效果，用一个dict控制.
        - source: 增益来源.
        - stack: buff层数.
        '''
        if source == "0":
            source = self.playerid
        if targetid not in self.targetBoost:
            self.targetBoost[targetid] = {}
        effectCopy = effect.copy()
        tmp = {"effect": effectCopy, "source": source}
        for key in tmp["effect"]:
            tmp["effect"][key] *= stack
        if id not in self.targetBoost[targetid] or tmp != self.targetBoost[targetid][id]:
            self.targetBoost[targetid][id] = tmp
            self.SetUpdateFlag(targetid)

    def removeBoost(self, id):
        '''
        移除一个自身增益.
        params:
        - id: 增益的id，一般是buffID.
        '''
        if id in self.boost:
            del self.boost[id]
            self.SetUpdateFlag()

    def addBoost(self, id, effect, source, stack):
        '''
        添加一个自身增益.
        params:
        - id: 增益的id，一般是buffID.
        - effect: 增益效果，用一个dict控制.
        - source: 增益来源.
        - stack: buff层数.
        '''
        effectCopy = effect.copy()
        tmp = {"effect": effectCopy, "source": source}
        for key in tmp["effect"]:
            tmp["effect"][key] *= stack
        if id not in self.boost or tmp != self.boost[id]:
            self.boost[id] = tmp
            self.SetUpdateFlag()

    def setSpecificSkill(self, name, source):
        '''
        设置特殊技能的来源. 主要是梅花三弄和逐云寒蕊.
        params:
        - name: 技能名.
        - source: 来源ID.
        '''
        if name == "mhsn":
            self.mhsn = source
        if name == "zyhr":
            self.zyhr = source

    def __init__(self, playerid, occ, baseAttribute=None):
        '''
        构造方法.
        params:
        - playerid: 玩家自身的ID.
        - occ: 玩家的心法.
        - baseAttribute: 玩家的基本属性. 留空时会按照默认属性进行计算.
        '''
        self.playerid = playerid
        self.occ = occ
        self.boost = {}
        self.targetBoost = {"all": {}}
        # rdps伤害系数. 第一级是目标（all表示全目标），第二级是技能ID（all表示通用技能）
        # 其中source表示来源玩家ID，rate表示倍率，boost表示增益ID
        self.rdpsRate = {}
        self.basicAttribute = {}
        self.attributeData = AttributeData(occ)
        self.attributeData2 = AttributeData(occ)
        self.mhsn = "0"  # 梅花三弄
        self.zyhr = "0"  # 逐云寒蕊
        self.needUpdate = {}


class StatRecorder():
    '''
    统计类的基类，实现分类统计、获取名称相关的方法.
    '''
    SPECIAL_NAME_DICT = {
        "6209": "王母挥袂(辞致)",
        "6211": "风袖低昂(晚晴)",
        '"1,6249,3"': "上元点鬟·双鸾",
        '"1,6249,1"': "翔鸾舞柳·双鸾",
        "15181": "宫(疏影横斜)",
        "8571": "心法减伤",
        "21112": "凌然天风", 
        "3307": "田螺阵",
        "15914": "斩无常",
        '2,23543,1': "庄周梦",
    }
    
    def specificName(self, id, full_id):
        '''
        根据full_id做大量特殊判定，从而实现类似于合并的效果。
        params:
        - id: 技能或buff的ID.
        - full_id: 三名ID表示法.
        '''
        if id in self.SPECIAL_NAME_DICT:
            return self.SPECIAL_NAME_DICT[id]
        elif full_id in self.SPECIAL_NAME_DICT:
            return self.SPECIAL_NAME_DICT[full_id]
        else:
            return ""

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
            area = full_id.split(',')[0]
            if area == '"2':
                res = res + "(持续)"
        elif l == 4:
            real_id = ','.join(full_id.split(',')[1:])
            area = full_id.split(',')[0]
            id = real_id.split(',')[1]
            res = info.getSkillName(real_id)
            resNew = self.specificName(id, real_id)
            if resNew != "":
                res = resNew
            nameArray = ["未知", "化解", "减伤", "吸血", "蛊惑", "响应", "增益"]
            res = "%s(%s)" % (res, nameArray[int(area)])
            if area == "3":
                res = "吸血"
            if area == "4":
                res = "蛊惑众生"
        return res

class HealCastRecorder(StatRecorder):
    '''
    治疗量统计类.
    记录为"A用B技能治疗C，值为D效果为E"，按A-(此类)-B-D的顺序逐层封装.
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
            self.skill[skill]["percent"] = safe_divide(self.skill[skill]["sum"], self.sum)
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

class RHpsRecorder():
    '''
    rHPS统计类.
    记录为"A用B技能治疗C，值为D效果为E"，按(此类)-C-A-B-D的顺序暂存每条信息，并统计累计的治疗量.
    将所有涉及治疗量的部分暂存，并提供结算方法.
    '''

    def popTarget(self, target, recorder):
        '''
        结算对应目标暂存的数据到统计类中.
        params:
        - target: 需要结算的目标.
        - recorder: HealCastRecorder类的数组.
        '''
        if target in self.records:
            rate = safe_divide(self.effHps[target], self.sumHps[target])
            for line in self.records[target]:
                if line["caster"] in recorder:
                    recorder[line["caster"]].record(target, line["full_id"], line["heal"] * rate)

        self.records[target] = []
        self.effHps[target] = 0
        self.sumHps[target] = 0

    def record(self, caster, target, heal, healEff, full_id, status):
        '''
        暂存一条信息.
        params:
        - caster: 事件的施放者
        - target: 事件的目标
        - heal: 治疗量/化解量
        - healEff: 有效治疗量/化解量
        - full_id: 事件的完整id
        - status: 目标的血量状态
        '''
        if target in self.records and status != 0:
            self.records[target].append({"caster": caster, "heal": heal, "healEff": healEff, "full_id": full_id})
            self.effHps[target] += healEff
            self.sumHps[target] += heal

    def __init__(self, info):
        self.records = {}
        self.effHps = {}
        self.sumHps = {}
        for player in info.player:
            self.records[player] = []
            self.effHps[player] = 0
            self.sumHps[player] = 0
            
class DpsCastRecorder(StatRecorder):
    '''
    伤害统计类.
    记录为"A用B技能攻击C，值为D效果为E"，按A-(此类)-B-D的顺序逐层封装.
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
            self.skill[skill]["percent"] = safe_divide(self.skill[skill]["sum"], self.sum)
            self.skill[skill]["name"] = self.getSkillName(skill, info)
        self.dps = self.sum / time * 1000
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
        记录一次伤害事件.
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
        self.dps = 0
    

class CombatTracker():
    '''
    战斗数据统计类.
    '''

    def generateJson(self):
        '''
        将结果导出为json.
        '''
        res = {}
        res["hps"] = self.hps
        res["ahps"] = self.ahps
        res["ohps"] = self.ohps
        res["rhps"] = self.rhps
        res["ndps"] = self.ndps
        res["rdps"] = self.rdps
        res["mndps"] = self.mndps
        res["mndps"] = self.mrdps

        # 精简技能表，不再记录ID。
        for t in res:
            for p in res[t]["player"]:
                del res[t]["player"][p]["skill"]
        return res
        
    def getStatInHps(self, objSource, objTarget):
        '''
        以dict的形式整理统计治疗结果.
        '''
        for player in objSource:
            objSource[player].export(self.timeHealer, self.info)
            if objSource[player].hps > 0:
                objTarget["player"][player] = {"sum": objSource[player].sum,
                                         "hps": objSource[player].hps,
                                         "skill": objSource[player].skill,
                                         "namedSkill": objSource[player].namedSkill,
                                         "name": self.info.getName(player),
                                         "occ": self.info.getOcc(player)}
                objTarget["sum"] += objTarget["player"][player]["hps"]
                
    def getStatInDps(self, objSource, objTarget):
        '''
        以dict的形式整理统计伤害结果.
        '''
        for player in objSource:
            objSource[player].export(self.timeDps, self.info)
            if objSource[player].dps > 0:
                objTarget["player"][player] = {"sum": objSource[player].sum,
                                         "dps": objSource[player].dps,
                                         "skill": objSource[player].skill,
                                         "namedSkill": objSource[player].namedSkill,
                                         "name": self.info.getName(player),
                                         "occ": self.info.getOcc(player)}
                objTarget["sum"] += objTarget["player"][player]["dps"]

    def export(self, time, timeDps, timeHealer):
        '''
        统计结束时的后处理.
        params:
        - time: 战斗时间.
        - timeDps: dps的有效战斗时间.
        - timeHealer: 治疗的有效战斗时间.
        '''

        self.time = time
        self.timeDps = timeDps
        self.timeHealer = timeHealer

        # 脱战时对缓冲区的结算.
        for player in self.hpStatus:
            self.rhpsRecorder.popTarget(player, self.rhpsCast)

        # hps
        hps = {"sum": 0, "player": {}}
        self.getStatInHps(self.hpsCast, hps)
        self.hps = hps

        # ohps
        ohps = {"sum": 0, "player": {}}
        self.getStatInHps(self.ohpsCast, ohps)
        self.ohps = ohps

        # ahps
        ahps = {"sum": 0, "player": {}}
        self.getStatInHps(self.ahpsCast, ahps)
        self.ahps = ahps

        # rhps
        rhps = {"sum": 0, "player": {}}
        self.getStatInHps(self.rhpsCast, rhps)
        self.rhps = rhps
        
        # ndps
        ndps = {"sum": 0, "player": {}}
        self.getStatInDps(self.ndpsCast, ndps)
        self.ndps = ndps
        
        # mndps
        mndps = {"sum": 0, "player": {}}
        self.getStatInDps(self.mndpsCast, mndps)
        self.mndps = mndps
        
        # rdps
        rdps = {"sum": 0, "player": {}}
        self.getStatInDps(self.rdpsCast, rdps)
        self.rdps = rdps
        
        # mrdps
        mrdps = {"sum": 0, "player": {}}
        self.getStatInDps(self.mrdpsCast, mrdps)
        self.mrdps = mrdps

    def recordBuff(self, event):
        '''
        记录buff事件.
        '''
        # if "左旋右转" in self.info.getSkillName(event.full_id):
        # if event.id == "23543":
        #     print("[NameBuff]", event.time, event.id, event.caster, event.target, event.full_id, event.stack)

        full_id = event.full_id.strip('"')
        lvl0_id = ','.join(full_id.split(',')[0:2])+',0'

        # 记录一些单独的buff
        if event.id == "9334":  # 记录梅花三弄的来源
            self.shieldDict[event.target] = event.caster
            self.boostCounter[event.target].setSpecificSkill("mhsn", event.caster)
            # 检查庄周梦效果，用独立的方式判定
            # 这里是因为笙簧刷新会有盾的真空期，但是庄周梦在游戏里做了特殊判定，因此这里也要做特殊判定
            if event.level in [2, 4]:
                effect_id = "2,23543,1"
                boostValue = BOOST_DICT[effect_id]
                source = event.caster
                self.boostCounter[event.target].addBoost(effect_id, boostValue, source, event.stack)
                # print("[AddShield]", self.boostCounter[event.target].boost)

        # if event.id == "20854":
        #     self.zyhrDict[event.target] = event.caster
        #     self.boostCounter[event.target].setSpecificSkill("zyhr", event.caster)

        # 记录化解buff
        if (full_id in ABSORB_DICT or lvl0_id in ABSORB_DICT or event.id == "9334") and event.target in self.absorbBuff:
            if event.stack != 0:
                self.absorbBuff[event.target][full_id] = [event.caster, event.time]
                if full_id in self.buffRemove[event.target]:
                    del self.buffRemove[event.target][full_id]
                    self.updateRemoveTime()

                # print("[GetAbsorbBuff]", event.id, event.time, event.target, event.caster)
            elif full_id in self.absorbBuff[event.target]:
                # 进行延迟移除
                if event.id != "9334":
                    self.buffRemove[event.target][full_id] = {"time": event.time + 50}
                    self.updateRemoveTime()
                else:  # 盾有更长的黏着时间
                    self.buffRemove[event.target][full_id] = {"time": event.time + 500}
                    self.updateRemoveTime()
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
                self.updateRemoveTime()
            # if event.id == "9336":
            #     print("[Buff9336]", event.time, event.id, event.stack)

        # 记录蛊惑
        if event.id in ["2316"]:  # 蛊惑众生
            if event.stack == 1:
                self.guHuoTarget[event.caster] = event.target
            else:
                self.guHuoTarget[event.caster] = "0"

        # 记录增益buff
        if (full_id in BOOST_DICT or lvl0_id in BOOST_DICT) and event.target in self.boostCounter:
            effect_id = full_id
            if full_id not in BOOST_DICT:
                effect_id = lvl0_id
            boostValue = BOOST_DICT[effect_id]
            source = event.caster
            if event.caster not in self.rdpsCast:
                source = event.target
            if effect_id == "2,20938,1":  # 左旋右转的特殊逻辑 (TODO)改成通用逻辑
                source = self.zxyzCaster
            if event.stack != 0:
                self.boostCounter[event.target].addBoost(effect_id, boostValue, source, event.stack)
            else:
                self.boostCounter[event.target].removeBoost(effect_id)

    def updateRemoveTime(self):
        '''
        更新最近的移除时间，一般在移除事项变化时调用.
        '''
        earliestTime = 9999999999
        for target in self.buffRemove:
            for id in self.buffRemove[target]:
                if self.buffRemove[target][id]["time"] < earliestTime:
                    earliestTime = self.buffRemove[target][id]["time"]
        for boost in self.boostRemove:
            if self.boostRemove[boost]["time"] < earliestTime:
                earliestTime = self.boostRemove[boost]["time"]
        self.removeTime = earliestTime
        # print("[Update111]Update", self.removeTime)

    def checkRemoveBuff(self, time):
        '''
        在事件开始前将待移除列表的buff尝试移除的方法.
        params:
        - time: 本次事件的时间.
        '''
        if time < self.removeTime:
            return

        # print("[Remove]Try removing...", self.removeTime, time)
        # print("[Before]")
        # print(self.buffRemove)
        # print(self.boostRemove)

        for target in self.buffRemove:
            toRemove = []
            for id in self.buffRemove[target]:
                if self.buffRemove[target][id]["time"] <= time:
                    # 执行移除
                    toRemove.append(id)
            #         print("[id]", id)
            # print("[toRemove]", toRemove)
            for id in toRemove:
                if id in self.absorbBuff[target]:
                    del self.absorbBuff[target][id]
                    if id in ["2,9334,2", "2,9334,4"]:
                        self.boostCounter[target].removeBoost("2,23543,1")
                if id in self.resistBuff[target]:
                    del self.resistBuff[target][id]
                del self.buffRemove[target][id]

        toRemove = []
        for boost in self.boostRemove:
            if self.boostRemove[boost]["time"] <= time:
                # 执行移除
                for player in self.boostCounter:
                    self.boostCounter[player].removeTargetBoost(self.boostRemove[boost]["target"], boost)
                toRemove.append(boost)
        for boost in toRemove:
            del self.boostRemove[boost]

        self.updateRemoveTime()

        # print("[After]")
        # print(self.buffRemove)
        # print(self.boostRemove)

    def recordSkill(self, event):
        '''
        记录技能事件.
        '''

        # 一些全局事件
        if event.id == "27674":
            self.zyhrCaster = event.caster
            for player in self.zyhrDict:
                self.zyhrDict[player] = event.caster
                self.boostCounter[player].setSpecificSkill("zyhr", event.caster)

        if event.id == "6251":
            self.zxyzCaster = event.caster

        # 先判断是否进入了无效区间
        while self.excludePosDps < len(self.badPeriodDpsLog) and event.time > self.badPeriodDpsLog[self.excludePosDps][0]:
            self.excludeStatusDps = self.badPeriodDpsLog[self.excludePosDps][1]
            self.excludePosDps += 1
        while self.excludePosHealer < len(self.badPeriodHealerLog) and event.time > self.badPeriodHealerLog[self.excludePosHealer][0]:
            self.excludeStatusHealer = self.badPeriodHealerLog[self.excludePosHealer][1]
            self.excludePosHealer += 1

        if event.target not in self.hpStatus:
            self.hpStatus[event.target] = {"damage": 0, "healNotFull": 0, "healFull": 0, "estimateHP": 0, "status": 0,
                                           "fullTime": 0}

        # 先检验是否有需要移除的buff
        self.checkRemoveBuff(event.time)

        # 治疗事件
        if event.heal > 0 and event.effect != 7 and event.caster in self.hpsCast and not self.excludeStatusHealer:
            hanQingFlag = 0
            if event.full_id == '"2,631,29"':  # 特殊处理寒清
                if event.target in self.hanQingTime and event.time - self.hanQingTime[event.target] < 500:
                    hanQingFlag = 1
                    self.hanQingTime[event.target] = 0
            if event.full_id == '"1,23951,40"':  # 特殊处理寂灭
                if self.cbyCaster in self.hpsCast:
                    self.hpsCast[self.cbyCaster].record(event.target, event.full_id, event.healEff)
                    self.ohpsCast[self.cbyCaster].record(event.target, event.full_id, event.heal)
                    self.rhpsRecorder.record(self.cbyCaster, event.target, event.heal, event.healEff, event.full_id, self.hpStatus[event.target]["status"])
            elif event.full_id in ['"1,23951,70"']:  # 特殊处理大针
                pass
            elif hanQingFlag:  # 寒清的响应式统计
                self.ahpsCast[event.caster].record(event.target, "5," + event.full_id, event.healEff)
                self.rhpsRecorder.record(event.caster, event.target, event.heal, event.healEff, "5," + event.full_id, self.hpStatus[event.target]["status"])
            elif event.full_id in ['"1,29748,1"', '"1,23951,2"']:  # 其它响应式处理
                self.ahpsCast[event.caster].record(event.target, "5," + event.full_id, event.healEff)
                self.rhpsRecorder.record(event.caster, event.target, event.heal, event.healEff, "5," + event.full_id, self.hpStatus[event.target]["status"])
            else:
                self.hpsCast[event.caster].record(event.target, event.full_id, event.healEff)
                self.ohpsCast[event.caster].record(event.target, event.full_id, event.heal)
                self.rhpsRecorder.record(event.caster, event.target, event.heal, event.healEff, event.full_id, self.hpStatus[event.target]["status"])
                # 推算蛊惑产生的治疗量
                if event.caster in self.guHuoTarget and self.guHuoTarget[event.caster] != "0" and event.healEff > 0:
                    target = self.guHuoTarget[event.caster]
                    self.ohpsCast[event.caster].record(target, "4," + event.full_id, event.healEff * 0.5)
                    # if self.hpStatus[event.caster]["damage"] > self.hpStatus[event.caster]["healFull"] or \
                    #         self.hpStatus[event.caster]["healNotFull"] > self.hpStatus[event.caster]["healFull"]:
                    if self.hpStatus[target]["status"] in [1, 2]:
                        self.hpsCast[event.caster].record(target, "4," + event.full_id, event.healEff * 0.5)
                    self.rhpsRecorder.record(event.caster, target, event.healEff * 0.5, event.healEff * 0.5, "4," + event.full_id,
                                             self.hpStatus[target]["status"])

        # elif event.heal > 0 and event.effect == 7:
        #     # 插件统计的APS
        #     print("[面板APS]", self.info.getSkillName(event.full_id), event.time, event.target, event.heal, event.id)

        # 根据治疗事件更新血量状态
        if event.heal > 0 and event.target in self.hpStatus:
            if event.heal == event.healEff:
                self.hpStatus[event.target]["healNotFull"] = event.time
                if self.hpStatus[event.target]["status"] != 1:
                    self.hpStatus[event.target]["status"] = 2  # 非伤害导致的不满血
            else:
                self.hpStatus[event.target]["healFull"] = event.time
                if self.hpStatus[event.target]["status"] in [1, 2]:
                    self.hpStatus[event.target]["status"] = 3  # 满血后的缓冲期
                    self.hpStatus[event.target]["fullTime"] = event.time

            if self.hpStatus[event.target]["status"] == 3 and event.time - self.hpStatus[event.target]["fullTime"] > 5000:  # 缓冲期阈值
                self.hpStatus[event.target]["fullTime"] = 0
                self.hpStatus[event.target]["status"] = 0  # 满血期
                self.rhpsRecorder.popTarget(event.target, self.rhpsCast)  # rHPS结算
                # if event.target in self.info.player:
                #     print("[PopTarget]", event.time, event.target, self.info.player[event.target].name)

            self.hpStatus[event.target]["estimateHP"] += event.heal
            if self.hpStatus[event.target]["estimateHP"] > 0:
                self.hpStatus[event.target]["estimateHP"] = 0
                self.hpStatus[event.target]["healFull"] = event.time

        # 根据伤害事件更新血量状态
        if event.damage > 0 and event.target in self.hpStatus:
            self.hpStatus[event.target]["damage"] = event.time
            self.hpStatus[event.target]["estimateHP"] -= event.damage
            self.hpStatus[event.target]["status"] = 1  # 已受伤

        # 记录一些公有技能的状态
        if event.id == "3982":
            self.cbyCaster = event.caster
        if event.id == "18274" and event.target in self.hanQingTime:
            self.hanQingTime[event.target] = event.time

        # 来源于化解的aps
        absorb = int(event.fullResult.get("9", 0))
        if absorb > 0 and event.target in self.absorbBuff:
            # print("[RawAbsorb]", event.time, event.target, absorb)

            # 根据化解更新血量状态
            if self.hpStatus[event.target]["status"] == 0:  # 满血状态产生化解
                self.hpStatus[event.target]["status"] = 3
                self.hpStatus[event.target]["fullTime"] = event.time
                self.hpStatus[event.target]["healFull"] = event.time

            # 目前只记录一个化解的buff，如果单次击破了某个化解盾导致有两个buff都参与了化解，那么其实无法统计到具体的化解量
            if not self.excludeStatusHealer:
                calcBuff = ["0", "0", 0]
                for key in self.absorbBuff[event.target]:
                    res = self.absorbBuff[event.target][key]
                    if calcBuff[1] == "0" or "9334" in calcBuff[0] or ("9334" not in key and res[1] > calcBuff[2]):
                        calcBuff = [key, res[0], res[1]]
                # TODO 2,2542,1 这种npc来源的buff也可以统计一下，但是现在占比不高先无限期延期吧
                if calcBuff[1] != "0":
                    # 记录化解
                    self.ahpsCast[calcBuff[1]].record(event.target, "1," + calcBuff[0], absorb)
                    # print("[复盘aHPS]", self.info.getSkillName(calcBuff[0]), event.time, event.target, absorb, calcBuff[0])
                    self.rhpsRecorder.record(calcBuff[1], event.target, absorb, absorb, "1," + calcBuff[0],
                                             self.hpStatus[event.target]["status"])

        # 来自于减伤的aps
        sumDamage = event.damage + absorb
        if sumDamage > 0 and event.target in self.resistBuff and not self.excludeStatusHealer:
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
                        self.rhpsRecorder.record(res[0], event.target, damageResist, damageResist, "2," + key,
                                                 self.hpStatus[event.target]["status"])

        # 从吸血推测HPS
        xixue = int(event.fullResult.get("7", 0))
        if xixue > 0 and event.caster in self.hpStatus and not self.excludeStatusHealer:
            # print("[Xixue]", event.time, event.caster, xixue)
            self.ohpsCast[event.caster].record(event.caster, "3," + event.full_id, xixue)
            # if self.hpStatus[event.caster]["damage"] > self.hpStatus[event.caster]["healFull"] or \
            #   self.hpStatus[event.caster]["healNotFull"] > self.hpStatus[event.caster]["healFull"]:
            if self.hpStatus[event.caster]["status"] in [1, 2]:
                self.hpsCast[event.caster].record(event.caster, "3," + event.full_id, xixue)
                self.rhpsRecorder.record(event.caster, event.caster, xixue, xixue, "3," + event.full_id,
                                         self.hpStatus[event.caster]["status"])

            self.hpStatus[event.caster]["estimateHP"] += xixue
            if self.hpStatus[event.caster]["estimateHP"] > 0:
                self.hpStatus[event.caster]["estimateHP"] = 0
                self.hpStatus[event.caster]["healFull"] = event.time

        # 记录蛊惑
        if event.id in ["2231"]:  # 蛊惑众生
            self.guHuoTarget[event.caster] = event.target

        # if self.info.getSkillName(event.full_id) == "盾飞":
        #     print("[Dunfei]", event.full_id, event.caster, self.info.getName(event.caster), event.time, event.damageEff)

        # 记录主动增益技能
        if event.id in ["3980"]:  # 戒火斩
            # print("[YishangDetect]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                if event.target in self.boostCounter[player].targetBoost and "2,23305,1" in self.boostCounter[player].targetBoost[event.target]:
                    continue  # 在有秋肃时跳过结算
                effect_id = "2,4058,1"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 15000, "target": event.target}
                self.updateRemoveTime()
        elif event.id in ["180"] and self.occDetailList.get(event.caster, "") == "2h":  # 秋肃
            # print("[YishangDetect]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                if event.target in self.boostCounter[player].targetBoost and "2,4058,1" in self.boostCounter[player].targetBoost[event.target]:
                    self.boostCounter[player].removeTargetBoost(event.target, "2,4058,1")  # 在有戒火斩时移除
                effect_id = "2,23305,1"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 40000, "target": event.target}
                self.updateRemoveTime()
        elif event.id in ["403"] and self.occDetailList.get(event.caster, "") == "3d":  # 傲血破风
            #print("[YishangDetect1]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                if event.target in self.boostCounter[player].targetBoost and "2,12717,30" in self.boostCounter[player].targetBoost[event.target]:
                    continue  # 在有高等级时跳过结算
                effect_id = "2,661,30"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 14000, "target": event.target}
                self.updateRemoveTime()
        elif event.id in ["403"] and self.occDetailList.get(event.caster, "") == "3t":  # 铁牢破风
            #print("[YishangDetect2]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                if event.target in self.boostCounter[player].targetBoost and "2,661,30" in self.boostCounter[player].targetBoost[event.target]:
                    self.boostCounter[player].removeTargetBoost(event.target, "2,661,30")  # 在有低等级时移除
                effect_id = "2,12717,30"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 14000, "target": event.target}
                self.updateRemoveTime()
        elif event.id in ["211", "212", "213"]:  # 立地成佛
            # global SUM_TIME, SUM1, SUM2, SUM3, SUM4, SUM5
            # print("[SUM_TIME]", SUM_TIME, SUM1, SUM2, SUM3, SUM4, SUM5)
            lvl = int(event.id) - 210
            postLvl = lvl
            postStack = 1
            change = 1
            if event.target in self.lidiInfo and event.time - self.lidiInfo[event.target]["time"] < 20000:
                preLvl = self.lidiInfo[event.target]["level"]
                if preLvl > lvl:
                    postLvl = preLvl
                    postStack = self.lidiInfo[event.target]["stack"]
                    change = 0
                elif preLvl == lvl:
                    postStack = min(self.lidiInfo[event.target]["stack"] + 1, 5)  # 最高5层
            if change:
                self.lidiInfo[event.target] = {"time": event.time, "stack": postStack, "level": postLvl}
                for player in self.boostCounter:
                    for i in range(postLvl):  # 移除低等级
                        id = "2,%d,1" % (563 + i)
                        if event.target in self.boostCounter[player].targetBoost and id in self.boostCounter[player].targetBoost[event.target]:
                            self.boostCounter[player].removeTargetBoost(event.target, id)  # 在有低等级时移除
                    effect_id = "2,%d,1" % (563 + postLvl)
                    boostValue = BOOST_DICT[effect_id]
                    self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, postStack)  # 注意层数判定
                    self.boostRemove[effect_id] = {"time": event.time + 20000, "target": event.target}
                    self.updateRemoveTime()
        elif event.id in ["13050"]:  # 盾飞
            # print("[YishangDetect]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                effect_id = "2,8248,1"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 25000, "target": event.target}
                self.updateRemoveTime()
        elif event.id in ["3963"]:  # 烈日斩
            # print("[YishangDetect]", event.time, event.id, event.caster, self.info.getName(event.caster))
            for player in self.boostCounter:
                effect_id = "2,4418,1"
                boostValue = BOOST_DICT[effect_id]
                self.boostCounter[player].addTargetBoost(event.target, effect_id, boostValue, event.caster, 1)
                self.boostRemove[effect_id] = {"time": event.time + 12000, "target": event.target}
                self.updateRemoveTime()
            
        # 记录DPS
        if event.damageEff > 0 and event.caster in self.ndpsCast and not self.excludeStatusDps:
            self.ndpsCast[event.caster].record(event.target, event.full_id, event.damageEff)
            # print("[DpsRecord]", event.time, event.damageEff)
            # rDPS
            if event.caster in self.boostCounter:
                rdpsRate = self.boostCounter[event.caster].getRate(event.target, event.full_id, self.info.getSkillName(event.full_id))

                # if self.info.getSkillName(event.full_id) == "破" and '2,20938,1' in rdpsRate:
                #     print("[PoZyhr]", rdpsRate, event.caster, self.info.getName(event.caster), event.damageEff)

                for key in rdpsRate:
                    if key == "self":
                        self.rdpsCast[event.caster].record(event.target, event.full_id, event.damageEff * rdpsRate[key]["rate"])
                    elif rdpsRate[key]["source"] in self.rdpsCast:
                        keyName = "6,%s" % key
                        self.rdpsCast[rdpsRate[key]["source"]].record(event.target, keyName, event.damageEff * rdpsRate[key]["rate"])

            if event.target in self.mainTargets and event.caster in self.mndpsCast:
                self.mndpsCast[event.caster].record(event.target, event.full_id, event.damageEff)
                # mrDPS
                if event.caster in self.boostCounter:
                    for key in rdpsRate:
                        if key == "self":
                            self.mrdpsCast[event.caster].record(event.target, event.full_id, event.damageEff * rdpsRate[key]["rate"])
                        elif rdpsRate[key]["source"] in self.mrdpsCast:
                            keyName = "6,%s" % key
                            self.mrdpsCast[rdpsRate[key]["source"]].record(event.target, keyName, event.damageEff * rdpsRate[key]["rate"])

    def __init__(self, info, bh, occDetailList):
        '''
        构造方法，需要读取角色或玩家信息。
        params:
        - info: bld读取的玩家信息.
        - bh: BOSS复盘得到的战斗记录基本信息，用于计算无效时间.
        - occDetailList: 具体心法信息.
        - TODO 还要扩充装备表，之后应该会整理成一个全的
        '''
        self.info = info
        self.occDetailList = occDetailList

        self.hpsCast = {}
        self.ohpsCast = {}
        self.ahpsCast = {}
        self.rhpsCast = {}
        self.absorbBuff = {}
        self.resistBuff = {}
        self.buffRemove = {}  # buff延迟删除
        self.rhpsRecorder = RHpsRecorder(info)
        self.hpStatus = {}
        self.boostRemove = {}
        self.removeTime = 9999999999  # 下一次移除事件的时间
        
        self.ndpsCast = {}
        self.rdpsCast = {}
        self.mndpsCast = {}
        self.mrdpsCast = {}
        self.boostCounter = {}

        self.shieldDict = {}  # 梅花三弄记录
        self.zyhrDict = {}  # 逐云寒蕊记录
        self.zyhrCaster = "0"
        self.zxyzCaster = "0"  # 左旋右转
        self.lidiInfo = {}  # 立地记录
        # TODO 这里直接做一个通用逻辑

        # 无效时间相关
        self.badPeriodDpsLog = bh.badPeriodDpsLog
        self.badPeriodHealerLog = bh.badPeriodHealerLog
        self.excludePosDps = 0
        self.excludeStatusDps = 0
        self.excludePosHealer = 0
        self.excludeStatusHealer = 0

        # 等效治疗相关
        self.cbyCaster = "0"  # 记录慈悲愿
        self.guHuoTarget = {}  # 记录蛊惑
        self.hanQingTime = {}  # 记录寒清时间

        # dps相关
        self.mainTargets = bh.mainTargets

        for player in info.player:
            # 治疗
            self.hpsCast[player] = HealCastRecorder(1)
            self.ohpsCast[player] = HealCastRecorder(1)
            self.ahpsCast[player] = HealCastRecorder(1)
            self.rhpsCast[player] = HealCastRecorder(1)
            self.absorbBuff[player] = {}
            self.resistBuff[player] = {}
            self.buffRemove[player] = {}
            self.hpStatus[player] = {"damage": 0, "healNotFull": 0, "healFull": 0, "estimateHP": 0, "status": 0, "fullTime": 0}
            self.guHuoTarget[player] = "0"
            self.hanQingTime[player] = 0
            # 输出
            self.ndpsCast[player] = DpsCastRecorder(1)
            self.mndpsCast[player] = DpsCastRecorder(1)
            self.rdpsCast[player] = DpsCastRecorder(1)
            self.mrdpsCast[player] = DpsCastRecorder(1)
            # 增益统计
            self.boostCounter[player] = BoostCounter(player, self.occDetailList[player])
            self.shieldDict[player] = "0"
            self.zyhrDict[player] = "0"
            
        for player in info.npc:
            self.hpsCast[player] = HealCastRecorder(0)
            self.ohpsCast[player] = HealCastRecorder(0)
            self.ahpsCast[player] = HealCastRecorder(0)
            self.hpStatus[player] = {"damage": 0, "healNotFull": 0, "healFull": 0, "estimateHP": 0, "status": 0,
                                     "fullTime": 0}
            # 输出
            self.ndpsCast[player] = DpsCastRecorder(0)


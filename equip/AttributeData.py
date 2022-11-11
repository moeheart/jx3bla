# Created by moeheart at 10/22/2022
# 属性数据类.

from tools.Functions import *
import time

OCC_ATTRIB = {
    '1d': {'类型': 2, '主属性': '元气', '攻击': 1.85, '会心': 0.38},  # 易筋
    '1t': {'类型': 2, '主属性': '体质', '气血': 2.5, '防御': 0.1, '攻击': 0.05},  # 洗髓   0.1攻击0.05破防
    '2d': {'类型': 4, '主属性': '元气', '攻击': 1.95, '破防': 0.19},  # 花间
    '2h': {'类型': 4, '主属性': '根骨', '治疗': 1.65, '会心': 0.41},  # 奶花
    '3d': {'类型': 1, '主属性': '力道', '攻击': 1.6, '破防': 0.25},  # 傲血
    '3t': {'类型': 1, '主属性': '体质', '气血': 1.5, '防御': 0.1, '招架': 0.1, '攻击': 0.04},  # 铁牢   0.1攻击0.05破防
    '4p': {'类型': 1, '主属性': '身法', '攻击': 1.45, '会心': 0.58},  # 剑纯
    '4m': {'类型': 4, '主属性': '根骨', '攻击': 1.75, '会心': 0.56},  # 气纯
    '5d': {'类型': 3, '主属性': '根骨', '攻击': 1.9, '会心': 0.28},  # 冰心
    '5h': {'类型': 3, '主属性': '根骨', '治疗': 1.75, '会心': 0.21},  # 奶秀
    '6d': {'类型': 5, '主属性': '根骨', '攻击': 1.95, '破防': 0.19},  # 毒经
    '6h': {'类型': 5, '主属性': '根骨', '治疗': 1.85},  # 奶毒
    '7p': {'类型': 1, '主属性': '力道', '攻击': 1.45, '会心': 0.59},  # 惊羽
    '7m': {'类型': 5, '主属性': '元气', '攻击': 1.75, '会心': 0.57},  # 田螺
    '8': {'类型': 1, '主属性': '身法', '攻击': 1.6, '破防': 0.25},  # 藏剑
    '9': {'类型': 1, '主属性': '力道', '攻击': 1.5, '破防': 0.47},  # 丐帮
    '10d': {'类型': 2, '主属性': '元气', '攻击': 1.9, '会心': 0.29},  # 焚影
    '10t': {'类型': 1, '主属性': '体质', '气血': 1.25, '闪避': 0.225, '攻击': 0.05},  # 明尊   0.11攻击0.06破防
    '21d': {'类型': 1, '主属性': '身法', '攻击': 1.71, '招架': 0.1, '拆招': 1},  # 分山
    '21t': {'类型': 1, '主属性': '体质', '气血': 2.2, '招架': 0.15, '拆招': 0.5, '攻击': 0.04},  # 铁骨 0.04攻击0.02破防
    '22d': {'类型': 3, '主属性': '根骨', '攻击': 1.85, '会心': 0.38},  # 莫问
    '22h': {'类型': 3, '主属性': '根骨', '治疗': 1.7, '会心': 0.31},  # 奶歌
    '23': {'类型': 1, '主属性': '力道', '攻击': 1.55, '破防': 0.36},  # 霸刀
    '24': {'类型': 1, '主属性': '身法', '攻击': 1.55, '会心': 0.36},  # 蓬莱
    '25': {'类型': 1, '主属性': '身法', '攻击': 1.5, '破防': 0.47},  # 凌雪
    '211':  {'类型': 4, '主属性': '元气', '攻击': 1.8, '会心': 0.47},  # 衍天
    '212d': {'类型': 5, '主属性': '根骨', '攻击': 1.8, '破防': 0.47},  # 无方
    '212h': {'类型': 5, '主属性': '根骨', '治疗': 1.8, '会心': 0.11},  # 奶药
    '213': {'类型': 1, '主属性': '力道', '攻击': 1.6, '会心': 0.25},  # 刀宗
    # TODO Tbuff
}

OCC_BASE = {  # 心法自带的基础值
    '1d': {'atSolarAttackPowerBase': 4139},  # 易筋
    '1t': {},  # 洗髓
    '2d': {'atNeutralAttackPowerBase': 4139},  # 花间
    '2h': {'atTherapyPowerBase': 5901},  # 奶花
    '3d': {'atPhysicsAttackPowerBase': 3794},  # 傲血
    '3t': {'atParryBase': 1207, 'atParryValueBase': 4651},  # 铁牢
    '4p': {'atPhysicsAttackPowerBase': 3277, 'atPhysicsCriticalStrike': 2929},  # 剑纯
    '4m': {'atNeutralAttackPowerBase': 3725, 'atNeutralCriticalStrike': 1788},  # 气纯
    '5d': {'atLunarAttackPowerBase': 4222},  # 冰心
    '5h': {'atTherapyPowerBase': 6323},  # 奶秀
    '6d': {'atPoisonAttackPowerBase': 4139},  # 毒经
    '6h': {'atTherapyPowerBase': 6112},  # 奶毒
    '7p': {'atPhysicsAttackPowerBase': 3277, 'atPhysicsOvercomeBase': 2929},  # 惊羽
    '7m': {'atPoisonAttackPowerBase': 3725, 'atPhysicsCriticalStrike': 1279},  # 田螺
    '8': {'atPhysicsAttackPowerBase': 3449, 'atPhysicsCriticalStrike': 2544},  # 藏剑
    '9': {'atPhysicsAttackPowerBase': 3621},  # 丐帮
    '10d': {'atSolarAttackPowerBase': 4346, 'atLunarAttackPowerBase': 4346},  # 焚影
    '10t': {},  # 明尊
    '21d': {'atPhysicsAttackPowerBase': 3449, 'atPhysicsOvercomeBase': 1526, 'atParryBase': 1220},  # 分山
    '21t': {'atParryBase': 2011, 'atParryValueBase': 4651},  # 铁骨
    '22d': {'atLunarAttackPowerBase': 3725, 'atLunarCriticalStrike': 1279},  # 莫问
    '22h': {'atTherapyPowerBase': 6535},  # 奶歌
    '23': {'atPhysicsAttackPowerBase': 3725},  # 霸刀
    '24': {'atPhysicsAttackPowerBase': 3621, 'atPhysicsCriticalStrike': 2158},  # 蓬莱
    '25': {'atPhysicsAttackPowerBase': 3656, 'atPhysicsOvercomeBase': 2081},  # 凌雪
    '211': {'atNeutralAttackPowerBase': 4222, 'atNeutralCriticalStrike': 2390},  # 衍天
    '212d': {'atPoisonAttackPowerBase': 3808, 'atPoisonOvercomeBase': 1788},  # 无方
    '212h': {'atTherapyPowerBase': 6533},  # 奶药
    '213': {'atPhysicsAttackPowerBase': 3346, 'atPhysicsCriticalStrike': 2775},  # 刀宗
}

OVERALL_OCC_BASE = {'atStrengthBase': 38, 'atAgilityBase': 38, 'atSpunkBase': 38, 'atSpiritBase': 38, 'atVitalityBase': 38}

def getExtraAttrib(occ, attrib):
    '''
    根据心法和主属性获取额外增益的数值.
    params:
    - occ: 心法代码.
    - attrib: 属性列表.
    returns:
    - res: 计算结果.
    '''
    attribDict = {'类型': 1, '主属性': '元气', '攻击': 1.95, '破防': 0.19}
    if occ in OCC_ATTRIB:
        attribDict = OCC_ATTRIB[occ]
    else:
        print("[Not in dict]", occ)
    res = {}
    mainAttrib = attribDict["主属性"]
    value = attrib[mainAttrib]
    for attrib in attribDict:
        if attrib not in ["类型", "主属性"]:
            res[attrib] = attribDict[attrib] * value
    return res

def getBoostAttrib(res, baseResult, attrib, playerType):
    '''
    根据属性列表获取其中的百分比类增益值，并累加到结果中（只包含百分比部分）.
    params:
    - res: 当前结果.
    - baseResult: 基础值的计算结果.
    - attrib: 属性列表.
    - playerType: 玩家所属类型.
    returns:
    - newRes: 计算结果.
    '''
    newRes = res.copy()
    for key in attrib:
        if key not in ATTRIB_TYPE:
            continue
        boostDetail = ATTRIB_TYPE[key]
        if boostDetail[playerType + 1] == 0:
            continue
        if boostDetail[1] == 1:
            continue
        affectedAttrib = boostDetail[0]
        if affectedAttrib not in newRes:
            newRes[affectedAttrib] = 0
        # print("[Extra]", key, boost, res.get(affectedAttrib, 0), affectedAttrib)
        newRes[affectedAttrib] += attrib[key] * boostDetail[7] * baseResult.get(affectedAttrib, 0)
    return newRes

def getBaseAttrib(res, attrib, playerType, attribDict):
    '''
    根据属性列表获取其中的基础值，并累加到结果中（只包含基础值部分）.
    params:
    - res: 当前结果.
    - attrib: 属性列表.
    - playerType: 玩家所属类型.
    - attribDict: 心法的系数表.
    returns:
    - newRes: 计算结果.
    '''
    newRes = res.copy()
    for key in attrib:
        if key not in ATTRIB_TYPE:
            continue
        boostDetail = ATTRIB_TYPE[key]
        if boostDetail[playerType + 1] == 0:
            continue
        if boostDetail[1] == 0:
            continue
        affectedAttrib = boostDetail[0]
        if affectedAttrib == "全属性":
            affectedAttrib = attribDict["主属性"]
        if affectedAttrib not in newRes:
            newRes[affectedAttrib] = 0
        if boostDetail[7] == 0:
            newRes[affectedAttrib] += attrib[key] / getCoefficient(affectedAttrib)
        else:
            newRes[affectedAttrib] += attrib[key] * boostDetail[7]
    return newRes

class AttributeData():
    '''
    属性数据类. 用于统计所有可能出现的属性（和增益的结果）, 并计算对于各个职业的特有方法.
    '''

    def getFinalAttrib(self):
        '''
        根据增益列表，从零开始计算最终属性.
        returns:
        - res: 最终属性列表.
        '''

        # print("[AllBoosts]", self.boosts)

        res = {}
        for attrib in self.baseAttrib:
            res[attrib] = self.baseAttrib[attrib]
        attribDict = {'类型': 1, '主属性': '元气', '攻击': 1.95, '破防': 0.19}
        if self.occ in OCC_ATTRIB:
            attribDict = OCC_ATTRIB[self.occ]
        else:
            print("[Not in dict]", self.occ)
        # 计算增益
        playerType = attribDict["类型"]
        res["类型"] = playerType
        # 第一次扫描基础值
        for boost in self.boosts:
            res = getBaseAttrib(res, boost, playerType, attribDict)
            # for key in boost:
            #     boostDetail = ATTRIB_TYPE[key]
            #     if boostDetail[playerType+1] == 0:
            #         continue
            #     if boostDetail[1] == 0:
            #         continue
            #     affectedAttrib = boostDetail[0]
            #     if affectedAttrib == "全属性":
            #         affectedAttrib = attribDict["主属性"]
            #     if affectedAttrib not in res:
            #         res[affectedAttrib] = 0
            #     if boostDetail[7] == 0:
            #         res[affectedAttrib] += boost[key] / getCoefficient(affectedAttrib)
            #     else:
            #         res[affectedAttrib] += boost[key] * boostDetail[7]
        self.baseAttribute = res.copy()
        # 第二次扫描非基础值
        extra = {}
        for boost in self.boosts:
            extra = getBoostAttrib(extra, res, boost, playerType)
            # for key in boost:
            #     boostDetail = ATTRIB_TYPE[key]
            #     if boostDetail[playerType+1] == 0:
            #         continue
            #     if boostDetail[1] == 1:
            #         continue
            #     affectedAttrib = boostDetail[0]
            #     if affectedAttrib not in extra:
            #         extra[affectedAttrib] = 0
            #     # print("[Extra]", key, boost, res.get(affectedAttrib, 0), affectedAttrib)
            #     extra[affectedAttrib] += boost[key] * boostDetail[7] * res.get(affectedAttrib, 0)
        self.extraAttribute = extra.copy()
        for key in extra:
            res[key] = res.get(key, 0) + extra[key]
        # 计算主属性加成
        mainAttribExtra = getExtraAttrib(self.occ, res)
        for attrib in mainAttribExtra:
            res[attrib] += mainAttribExtra[attrib] / getCoefficient(attrib)
        return res

    def addBoostAndGetAttrib(self, boost):
        '''
        根据当前暂存的属性结果, 计算添加某个增益之后的属性.
        这个流程主要用来提高效率, 用了一些复杂的计算，尽量避免对其做优化.
        params:
        - boost: 待添加的增益.
        '''
        attribDict = {'类型': 1, '主属性': '元气', '攻击': 1.95, '破防': 0.19}
        if self.occ in OCC_ATTRIB:
            attribDict = OCC_ATTRIB[self.occ]
        # 计算增益
        playerType = attribDict["类型"]

        # 第一次扫描基础值
        for key in boost:
            boostDetail = ATTRIB_TYPE[key]
            if boostDetail[playerType + 1] == 0:
                continue
            if boostDetail[1] == 0:
                continue
            affectedAttrib = boostDetail[0]
            if affectedAttrib not in self.baseAttribute:
                self.baseAttribute[affectedAttrib] = 0
            if affectedAttrib not in self.extraAttribute:
                self.extraAttribute[affectedAttrib] = 0
            prev = self.baseAttribute[affectedAttrib]
            if boostDetail[7] == 0:
                self.baseAttribute[affectedAttrib] += boost[key] / getCoefficient(affectedAttrib)
            else:
                self.baseAttribute[affectedAttrib] += boost[key] * boostDetail[7]
            self.extraAttribute[affectedAttrib] = safe_divide(self.extraAttribute[affectedAttrib] * self.baseAttribute[affectedAttrib], prev)
        # 第二次扫描非基础值
        for key in boost:
            boostDetail = ATTRIB_TYPE[key]
            if boostDetail[playerType+1] == 0:
                continue
            if boostDetail[1] == 1:
                continue
            affectedAttrib = boostDetail[0]
            if affectedAttrib not in self.baseAttribute:
                self.baseAttribute[affectedAttrib] = 0
            if affectedAttrib not in self.extraAttribute:
                self.extraAttribute[affectedAttrib] = 0
            self.extraAttribute[affectedAttrib] += boost[key] * boostDetail[7] * self.baseAttribute.get(affectedAttrib, 0)
        # 计算最终结果
        res = self.baseAttribute.copy()
        for key in self.extraAttribute:
            res[key] = res.get(key, 0) + self.extraAttribute[key]
        # 计算主属性加成
        mainAttribExtra = getExtraAttrib(self.occ, res)
        for attrib in mainAttribExtra:
            res[attrib] += mainAttribExtra[attrib] / getCoefficient(attrib)
        return res

    def removeBoostAndGetAttrib(self, boost):
        '''
        根据当前暂存的属性结果, 计算移除某个增益之后的属性.
        这个流程主要用来提高效率, 用了一些复杂的计算，尽量避免对其做优化.
        params:
        - boost: 待添加的增益.
        '''
        attribDict = {'类型': 1, '主属性': '元气', '攻击': 1.95, '破防': 0.19}
        if self.occ in OCC_ATTRIB:
            attribDict = OCC_ATTRIB[self.occ]
        # 计算增益
        playerType = attribDict["类型"]

        # 第二次扫描非基础值
        for key in boost:
            boostDetail = ATTRIB_TYPE[key]
            if boostDetail[playerType+1] == 0:
                continue
            if boostDetail[1] == 1:
                continue
            affectedAttrib = boostDetail[0]
            if affectedAttrib not in self.baseAttribute:
                self.baseAttribute[affectedAttrib] = 0
            if affectedAttrib not in self.extraAttribute:
                self.extraAttribute[affectedAttrib] = 0
            self.extraAttribute[affectedAttrib] -= boost[key] * boostDetail[7] * self.baseAttribute.get(affectedAttrib, 0)
        # 第一次扫描基础值
        for key in boost:
            boostDetail = ATTRIB_TYPE[key]
            if boostDetail[playerType + 1] == 0:
                continue
            if boostDetail[1] == 0:
                continue
            affectedAttrib = boostDetail[0]
            if affectedAttrib not in self.baseAttribute:
                self.baseAttribute[affectedAttrib] = 0
            if affectedAttrib not in self.extraAttribute:
                self.extraAttribute[affectedAttrib] = 0
            prev = self.baseAttribute[affectedAttrib]
            #self.baseAttribute[affectedAttrib] -= boost[key] / getCoefficient(affectedAttrib)
            if boostDetail[7] == 0:
                self.baseAttribute[affectedAttrib] -= boost[key] / getCoefficient(affectedAttrib)
            else:
                self.baseAttribute[affectedAttrib] -= boost[key] * boostDetail[7]
            self.extraAttribute[affectedAttrib] = safe_divide(self.extraAttribute[affectedAttrib] * self.baseAttribute[affectedAttrib], prev)
        # 计算最终结果
        res = self.baseAttribute.copy()
        for key in self.extraAttribute:
            res[key] = res.get(key, 0) + self.extraAttribute[key]
        # 计算主属性加成
        mainAttribExtra = getExtraAttrib(self.occ, res)
        for attrib in mainAttribExtra:
            res[attrib] += mainAttribExtra[attrib] / getCoefficient(attrib)
        return res

    def setBoosts(self, boosts):
        '''
        设置增益.
        params:
        - boosts: 数组形式的增益列表.
        '''
        self.boosts = boosts

    def copy(self):
        '''
        建立一个副本.
        '''
        pass

    def __init__(self, occ='2d'):
        '''
        构造方法.
        params:
        - occ: 心法代码
        '''
        self.baseAttrib = {
            '气血': 500000,
            '体质': 2249,
            '元气': 2249,
            '力道': 2249,
            '身法': 2249,
            '根骨': 2249,
            '攻击': 23388,
            '治疗': 21464,
            '会心': 0.1556,
            '会心效果': 1.9543,
            '破防': 0.2147,
            '加速': 4864,
            '无双': 0.1713,
            '破招': 1332,
            '防御': 0.0444,
            '招架': 0.03,
            '拆招': 0,
            '闪避': 0,
            '御劲': 0,
            '御劲减会伤': 0,
            '化劲': 0.015,
            '伤害变化': 0,
            '无视防御A': 0,
        }
        self.occ = occ

        self.baseAttribute = {}  # 基础属性
        self.extraAttribute = {}  # 额外属性

if __name__ == "__main__":
    pass
# Created by moeheart at 10/22/2022
# 属性数据类.

from tools.Functions import *
import time

OCC_ATTRIB = {
    '2h': {'类型': 4, '主属性': '根骨', '治疗': 1.65, '会心': 0.41},  # 奶花
    '5h': {'类型': 3, '主属性': '根骨', '治疗': 1.75, '会心': 0.21},  # 奶秀
    '6h': {'类型': 5, '主属性': '根骨', '治疗': 1.85},  # 奶毒
    '22h': {'类型': 3, '主属性': '根骨', '治疗': 1.7, '会心': 0.31},  # 奶歌
    '212h': {'类型': 5, '主属性': '根骨', '治疗': 1.8, '会心': 0.11},  # 奶药
    # TODO 回头再加
}

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
    res = {}
    mainAttrib = attribDict["主属性"]
    value = attrib[mainAttrib]
    for attrib in attribDict:
        if attrib not in ["类型", "主属性"]:
            res[attrib] = attribDict[attrib] * value
    return res


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
        # 计算增益
        playerType = attribDict["类型"]
        res["类型"] = playerType
        # 第一次扫描基础值
        for boost in self.boosts:
            for key in boost:
                boostDetail = ATTRIB_TYPE[key]
                if boostDetail[playerType+1] == 0:
                    continue
                if boostDetail[1] == 0:
                    continue
                affectedAttrib = boostDetail[0]
                if affectedAttrib not in res:
                    res[affectedAttrib] = 0
                if boostDetail[7] == 0:
                    res[affectedAttrib] += boost[key] / getCoefficient(affectedAttrib)
                else:
                    res[affectedAttrib] += boost[key] * boostDetail[7]
        self.baseAttribute = res.copy()
        # 第二次扫描非基础值
        extra = {}
        for boost in self.boosts:
            for key in boost:
                boostDetail = ATTRIB_TYPE[key]
                if boostDetail[playerType+1] == 0:
                    continue
                if boostDetail[1] == 1:
                    continue
                affectedAttrib = boostDetail[0]
                if affectedAttrib not in extra:
                    extra[affectedAttrib] = 0
                # print("[Extra]", key, boost, res.get(affectedAttrib, 0), affectedAttrib)
                extra[affectedAttrib] += boost[key] * boostDetail[7] * res.get(affectedAttrib, 0)
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
            #self.baseAttribute[affectedAttrib] += boost[key] / getCoefficient(affectedAttrib)
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
# Created by moeheart at 08/31/2021
# 维护属性计算类.
# 这个属性计算只计算装备提供的属性，需要与AttributeDisplay配合计算心法的属性得到最终结果。这个命名逻辑以后再调整。

from equip.EquipmentInfo import EquipmentInfo
from equip.EquipmentExport import ImportExcelEquipment
from tools.Attribute import CURRENT_GAME_EDITION

class AttributeCal():
    '''
    属性计算类，通过装备构成来推断出最终属性.
    '''

    def attribMerge(self, attribA, attribB):
        '''
        将两个属性相加.
        params:
        - attribA, attribB: 需要相加的属性
        returns:
        - res: 相加后的属性
        '''
        res = {}
        for line in attribA:
            if "at" in line:
                if line in res:
                    res[line] += attribA[line]
                else:
                    res[line] = attribA[line]
        for line in attribB:
            if "at" in line:
                if line in res:
                    res[line] += attribB[line]
                else:
                    res[line] = attribB[line]
        return res

    def CalculateAll(self, attrStr):
        '''
        通过字符串形式的装备信息计算属性.
        格式由这一标准定义：https://www.jx3box.com/bbs/22011
        '''
        self.equipmentInfo.unsupportedEffects.clear()
        self.equipmentInfo.effects.clear()
        self.lastWarnings = []
        self.lastEffects = []
        if not attrStr.strip():
            return {}
        equips = self.im.importData(attrStr.rstrip('\r\n'))
        sumAttrib = {}
        sumPlug = 0
        sumPlugLvl = 0
        setCount = {}  # 套装统计
        for line in equips:
            if equips[line].get('id', '').strip() in ('', '0'):
                continue
            #计算基础属性
            refineLvl = int(equips[line].get("star", 0))
            if not 0 <= refineLvl <= 8:
                raise ValueError("装备精炼等级超出0至8: %s" % refineLvl)
            feature = self.equipmentInfo.getFeature(
                equips[line]["id_full"], refineLvl)
            if feature == 0:
                continue

            if feature["set"] not in ["", "0"]:
                if feature["set"] not in setCount:
                    setCount[feature["set"]] = 1
                else:
                    setCount[feature["set"]] += 1
            singleAttrib = {}
            singleAttrib = self.attribMerge(singleAttrib, feature)

            #计算镶嵌
            for i in range(1, 4):
                plugLvl = equips[line].get("plug%d"%i, 0)
                if plugLvl in ['', ' ']:
                    plugLvl = 0
                else:
                    plugLvl = int(plugLvl)
                plugID = feature['DiamondAttributeID%d' % i]
                if plugID in ('', '0', 0) or plugLvl == 0:
                    continue
                sumPlug += 1
                sumPlugLvl += plugLvl
                plugAttrib = self.equipmentInfo.getGemAttribute(plugID, plugLvl)
                singleAttrib = self.attribMerge(singleAttrib, plugAttrib)

            #计算附魔
            for i in range(1, 3):
                magicID = equips[line].get("magic%d"%i, '0')
                if magicID in ['', ' ', '0']:
                    continue
                if magicID in self.equipmentInfo.enchantAttributes:
                    magicAttrib = {}
                    for name, value, value2 in self.equipmentInfo.enchantAttributes[magicID]:
                        magicAttrib = self.attribMerge(magicAttrib, self.equipmentInfo.staticAttribute(
                            name, value, "附魔%s" % magicID, value2))
                else:
                    raise KeyError("附魔未收录于当前正式服底表: %s" % magicID)
                singleAttrib = self.attribMerge(singleAttrib, magicAttrib)
            sumAttrib = self.attribMerge(singleAttrib, sumAttrib)

        #计算五彩石
        if "0" in equips:
            colorID = equips["0"].get("plug0", "0")
            if colorID in self.equipmentInfo.color:
                colorAttrib = self.equipmentInfo.color[colorID]
                for i in range(3):  # 按属性个数排序
                    if colorAttrib[i*4+2] == "" or colorAttrib[i*4+1] == "":
                        continue
                    if sumPlug >= int(colorAttrib[i*4+2]) and sumPlugLvl >= int(colorAttrib[i*4+3]):
                        colorSingleAttrib = self.equipmentInfo.staticAttribute(
                            colorAttrib[i*4], colorAttrib[i*4+1], "五彩石%s" % colorID)
                        sumAttrib = self.attribMerge(colorSingleAttrib, sumAttrib)
            elif colorID.strip() not in ('', '0'):
                raise KeyError("五彩石未收录于当前正式服底表: %s" % colorID)

        #计算套装
        for line in setCount:
            if line not in self.equipmentInfo.set:
                continue
            setInfo = self.equipmentInfo.set[line]
            for setN, setAttribID in setInfo:
                if setCount[line] >= setN:  # 满足套装数量条件
                    if setAttribID in ['', "0", 0]:
                        continue
                    setAttribRes = self.equipmentInfo.attrib[setAttribID]
                    setAttrib = self.equipmentInfo.staticAttribute(
                        setAttribRes[0], setAttribRes[1], "套装%s/%s件" % (line, setN),
                        self.equipmentInfo.attribParameters.get(setAttribID, {}).get('value2', ''))
                    sumAttrib = self.attribMerge(setAttrib, sumAttrib)

        self.lastWarnings = sorted(self.equipmentInfo.unsupportedEffects)
        self.lastEffects = list(self.equipmentInfo.effects)
        return sumAttrib

    def __init__(self, gameEdition=CURRENT_GAME_EDITION):
        self.gameEdition = CURRENT_GAME_EDITION
        self.equipmentInfo = EquipmentInfo()
        self.equipmentInfo.LoadFromStaticData()
        self.im = ImportExcelEquipment()
        self.lastWarnings = []
        self.lastEffects = []

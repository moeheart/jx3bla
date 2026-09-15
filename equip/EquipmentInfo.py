# Created by moeheart at 08/30/2021
# 维护装备信息类.

import csv
import re

from tools.ResourcePath import get_resource_path

class EquipmentInfo():
    '''
    装备信息类，包括属性的读取与获得。
    '''

    def openTextFile(self, path):
        '''
        兼容读取不同编码的静态资源文件。
        目前优先尝试 utf-8 / utf-8-sig，失败后回退到 gbk。
        '''
        path = get_resource_path(path)
        last_error = None
        for encoding in ["utf-8", "utf-8-sig", "gbk"]:
            try:
                f = open(path, 'r', encoding=encoding)
                f.readline()
                f.seek(0)
                return f
            except UnicodeDecodeError as e:
                last_error = e
                try:
                    f.close()
                except:
                    pass
            except LookupError as e:
                last_error = e
        if last_error is not None:
            raise last_error
        return open(path, 'r')

    def getAttribute(self, full_id, attribute):
        '''
        通过带标签的ID获取装备特定的属性。
        params:
        - full_id: 装备带标签的编号，例如6,12345.
        - attribute: 要查找的属性，必须是表头中的一项.
        returns:
        - 属性值
        '''
        if full_id not in self.data:
            return 0
        header_key = "%s,%s"%(full_id.split(',')[0], attribute)
        if header_key not in self.headerID:
            return 0
        return self.data[full_id][self.headerID[header_key]]

    def getFeature(self, full_id, refineLevel=0):
        '''
        通过装备ID获取关心的所有属性.

        params:
        - full_id: 装备带标签的编号，例如6,12345.
        returns:
        - 字典，为对应的装备属性列表.
        '''

        result = {}
        result["name"] = self.getAttribute(full_id, "Name")
        result["set"] = self.getAttribute(full_id, "SetID")
        if self.gameEdition >= 160 and full_id not in self.data:
            raise KeyError("装备未收录于当前体服底表: %s" % full_id)
        for i in range(1, 17):
            attribName = "Magic%dType"%i
            attribID = self.getAttribute(full_id, attribName)
            if attribID in ["", "0", 0, "atInvalid"]:
                continue
            attribRes = self.attrib[attribID]
            attributes = self.staticAttribute(attribRes[0], attribRes[1], "装备%s词条%s" % (full_id, attribID))
            for name, value in attributes.items():
                # 当前客户端只精炼 Magic 词条；白字武器伤害、攻速、基础防御不参与。
                if self.gameEdition >= 160 and name in self.strengthable:
                    rate = self.REFINE_PERMILLE[refineLevel]
                    value = (value * (1000 + rate) + 500) // 1000
                result[name] = result.get(name, 0) + value

        for i in range(1, 11):
            attribName = "Base%dType"%i
            attribType = self.getAttribute(full_id, attribName)
            attribVName = "Base%dMax"%i
            attribValue = self.getAttribute(full_id, attribVName)
            if attribValue in ["", "0", 0, "atInvalid"]:
                continue
            if attribType not in result:
                result[attribType] = int(attribValue)
            else:
                result[attribType] += int(attribValue)

        for i in range(1, 4):
            name = "DiamondAttributeID%d"%i
            result[name] = self.getAttribute(full_id, name)

        return result

    REFINE_PERMILLE = (0, 5, 13, 24, 38, 55, 75, 98, 124)

    def getGemAttribute(self, attribID, level):
        """返回已激活孔的属性；50级使用当前客户端 GetSlotAttrib 的数值流程。"""
        if not 1 <= level <= 8:
            raise ValueError("五行石等级超出1至8: %s" % level)
        name, value = self.attrib[attribID]
        attributes = self.staticAttribute(name, value, "镶嵌词条%s" % attribID)
        result = {}
        for name, value in attributes.items():
            if self.gameEdition >= 160:
                # SO3ItemHouseX64.dll 1.6.0.9503 RVA 216C0：仅缩放 Value1Strable。
                # 原生依次做 double 乘法/除法，最后 cvttsd2si 向零截断，不能提前取整。
                if name in self.strengthable:
                    factor = level * 0.195 if level <= 6 else (level * 0.65 - 3.2) * 1.3
                    scaled = float(value) * factor
                    scaled *= 1355.0
                    scaled /= 27800.0
                    value = int(scaled)
            else:
                rate = (0, 190, 390, 585, 780, 975, 1170, 1750, 2600)[level]
                value = value * rate // 1000
            result[name] = value
        return result

    def staticAttribute(self, name, value, source):
        """只返回可直接相加的数值；脚本/技能效果 ID 不能充当面板数值。"""
        if not name or name == "atInvalid":
            return {}
        if name in {"atExecuteScript", "atSetEquipmentRecipe", "atSkillEventHandler", "atSetEquipmentSkill"}:
            self.unsupportedEffects.add("%s: %s" % (source, name))
            return {}
        try:
            return {name: int(value or 0)}
        except (ValueError, TypeError):
            self.unsupportedEffects.add("%s: %s" % (source, name))
            return {}

    def readRows(self, path):
        with self.openTextFile(path) as source:
            yield from csv.DictReader(source, delimiter="\t")


    def loadSingleFile(self, path, scene):
        '''
        从文件中读取装备，并打上对应的标签保存在data中.
        params:
        - path: 文件路径
        - scene: 表的编号，可能是6,7,8
        '''
        header = []
        first = True
        with self.openTextFile(path) as f:
            for line in f:
                if first:
                    header = line.strip('\n').split('\t')
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    new_id = "%d,%s"%(scene, content[0])
                    self.data[new_id] = content

        for i in range(len(header)):
            header_key = "%d,%s"%(scene, header[i])
            self.headerID[header_key] = i

    def LoadFromStaticData(self):
        '''
        从解包中读取所有装备的属性。
        '''
        TRINKET_PATH = self.resourceRoot + '/Custom_Trinket.tab'
        ARMOR_PATH = self.resourceRoot + '/Custom_Armor.tab'
        WEAPON_PATH = self.resourceRoot + '/Custom_Weapon.tab'
        self.loadSingleFile(TRINKET_PATH, 6)
        self.loadSingleFile(ARMOR_PATH, 7)
        self.loadSingleFile(WEAPON_PATH, 8)

        ATTRIB_PATH = self.resourceRoot + '/attrib.tab'
        first = True
        with self.openTextFile(ATTRIB_PATH) as f:
            for line in f:
                if first:
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    self.attrib[content[0]] = [content[2], content[3]]  # 只记录最简单的形式

        ENCHANT_PATH = self.resourceRoot + '/enchant.tab'
        # 以列名读取全部四条附魔效果；五彩石条件与普通附魔共用同一源表。
        for row in self.readRows(ENCHANT_PATH):
            self.enchantAttributes[row['ID']] = [
                (row.get('Attribute%dID' % i, ''), row.get('Attribute%dValue1' % i, ''))
                for i in range(1, 5)
            ]
            self.enchant[row['ID']] = [
                row.get(column % i, '')
                for i in range(1, 4)
                for column in ('Attribute%dID', 'Attribute%dValue1', 'DiamondCount%d', 'DiamondIntensity%d')
            ]

        ITEM_PATH = self.resourceRoot + '/item.txt'
        first = True
        with self.openTextFile(ITEM_PATH) as f:
            for line in f:
                if first:
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    id = content[0]
                    text = content[5]
                    res = re.search("SpiStone ([0-9]+)", text)
                    if res:
                        number = res.group(1)
                        self.itemColor[id] = number

        OTHER_PATH = self.resourceRoot + '/other.tab'
        first = True
        with self.openTextFile(OTHER_PATH) as f:
            for line in f:
                if first:
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    if content[3] in self.itemColor:
                        self.color[content[0]] = self.enchant[self.itemColor[content[3]]]  # 记录五彩石

        SET_PATH = self.resourceRoot + '/Set.tab'
        for row in self.readRows(SET_PATH):
            self.set[row['ID']] = [
                (int(column.split('_')[0]), value)
                for column, value in row.items()
                if re.fullmatch(r'\d+_\d+', column) and value not in ('', '0', None)
            ]

        if self.gameEdition >= 160:
            for row in self.readRows(self.resourceRoot + '/StrengthableAttrib.tab'):
                if row['Value1Strable'] == '1':
                    self.strengthable.add(row['AttribType'])

    def __init__(self, gameEdition=0):
        self.gameEdition = int(gameEdition or 0)
        self.resourceRoot = 'equip/resources/cangshengtf' if self.gameEdition >= 160 else 'equip/resources'
        self.data = {}
        self.attrib = {}
        self.enchant = {}
        self.enchantAttributes = {}
        self.color = {}
        self.set = {}
        self.itemColor = {}  # 存储可能的五彩石物品id与对应的enchantID
        self.headerID = {}
        self.strengthable = set()
        self.unsupportedEffects = set()

if __name__ == "__main__":
    t = EquipmentInfo()
    print("准备读取")
    t.LoadFromStaticData()
    print("读取完成")
    print(t.getFeature("7,50953"))



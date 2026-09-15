# Created by moeheart at 08/31/2021
# 维护属性计算类.
# 这个属性计算只计算装备提供的属性，需要与AttributeDisplay配合计算心法的属性得到最终结果。这个命名逻辑以后再调整。

from equip.EquipmentInfo import EquipmentInfo
from equip.EquipmentExport import ImportExcelEquipment

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
        self.lastWarnings = []
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
                equips[line]["id_full"], refineLvl if self.gameEdition >= 160 else 0)
            if feature == 0:
                continue

            if feature["set"] not in ["", "0"]:
                if feature["set"] not in setCount:
                    setCount[feature["set"]] = 1
                else:
                    setCount[feature["set"]] += 1
            singleAttrib = {}
            singleAttrib = self.attribMerge(singleAttrib, feature)

            #计算精炼
            refineRate = [0, 0.005, 0.013, 0.024, 0.038, 0.055, 0.075, 0.098, 0.124][refineLvl]
            if self.gameEdition < 160:
                for attrib in singleAttrib:
                    singleAttrib[attrib] = int(singleAttrib[attrib] * (1 + refineRate) + 0.5)

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
                if magicID in ["11272"] and self.gameEdition < 160:  # 旧版本治疗鞋大附魔
                    magicAttrib = {'atTherapyPowerBase': 241}  #TODO 记得改
                elif magicID in self.equipmentInfo.enchantAttributes:
                    magicAttrib = {}
                    for name, value in self.equipmentInfo.enchantAttributes[magicID]:
                        magicAttrib = self.attribMerge(magicAttrib, self.equipmentInfo.staticAttribute(
                            name, value, "附魔%s" % magicID))
                else:
                    if self.gameEdition >= 160:
                        raise KeyError("附魔未收录于当前体服底表: %s" % magicID)
                    magicAttrib = {}
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
            elif self.gameEdition >= 160 and colorID.strip() not in ('', '0'):
                raise KeyError("五彩石未收录于当前体服底表: %s" % colorID)

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
                        setAttribRes[0], setAttribRes[1], "套装%s/%s件" % (line, setN))
                    sumAttrib = self.attribMerge(setAttrib, sumAttrib)

        self.lastWarnings = sorted(self.equipmentInfo.unsupportedEffects)
        return sumAttrib

    def __init__(self, gameEdition=0):
        self.gameEdition = int(gameEdition or 0)
        self.equipmentInfo = EquipmentInfo(gameEdition=gameEdition)
        self.equipmentInfo.LoadFromStaticData()
        self.im = ImportExcelEquipment()
        self.lastWarnings = []

if __name__ == "__main__":
    str = """25441	6	11163	0	6	 	 	 
50953	6	11189	11145	6	6	 	 
50927	6	11051	11146	6	6	 	 
29491	6	11148	0	6	 	 	 
29509	6	11156	0	 	 	 	 
29399	6	11156	0	 	 	 	 
50875	6	11191	11142	6	6	 	 
29423	4	11149	0	6	 	 	 
51071	4	11022	0	6	6	 	 
50901	6	11083	0	6	6	 	 
51057	4	11077	11144	6	6	 	 
25481	4	11011	0	6	6	6	13686"""
    str = """27106	0	0	0	4			
51011	0	0	0	4	4		
54043	0	0	0	4	4		
30907	0	0	0	4			
29330	0	0	0				
29330	0	0	0				
54025	0	0	0	4	4		
29396	0	0	0	4			
53509	0	0	0	4	4		
51029	0	0	0	4	4		
50981	0	0	0	4	4		
26782	0	0	0	4	4	4	25692"""
    str = "27891\t0\t0\t0\t4\t\t\t\n50103\t0\t0\t0\t\t\t\t\n50169\t0\t0\t0\t\t\t\t\n31668\t0\t0\t0\t4\t\t\t\n31680\t0\t0\t0\t\t\t\t\n31680\t0\t0\t0\t\t\t\t\n50079\t0\t0\t0\t\t\t\t\n31674\t0\t0\t0\t4\t\t\t\n55389\t0\t0\t0\t4\t4\t\t\n50157\t0\t0\t0\t\t\t\t\n55371\t0\t0\t0\t4\t4\t\t\n24995\t0\t0\t0\t\t\t\t"

#     str = """好鱼 32774	0	11664	0
# 90563	0	0	0
# 90835	0	11531	11684
# 34407	0	0	0
# 36130	0	11662	0
# 34443	0	11657	0
# 90611	0	0	0
# 34413	0	0	0
# 90383	0	11547	0
# 90545	0	11613	0
# 90918	0	11579	11682
# 32569	0	11568	0				12095"""

    str = """38888	6	12357	0	8			25469
100876	6	12285	0	8	8		25469
100834	6	12227	0	8	8		25469
41221	6	12346	0	8			25469
41197	6	12350	0				25469
41197	6	12350	0				25469
100816	6	12230	0	8	8		25469
41209	6	12348	0	8			25469
100900	6	12219	0	8	8		25469
100858	6	12282	0	8	8		25469
100810	6	12274	0	8	8		25469
38855	6	12213	0	8	8	8	25469"""

    ac = AttributeCal()
    res = ac.CalculateAll(str)
    print(res)
    # im = ImportExcelEquipment()
    # equips = im.importData(str)
    # print(equips)

# [colorID] 73408
# [colorAttrib] ['atHasteBase', '1463']

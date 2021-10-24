# Created by moeheart at 08/31/2021
# 维护属性计算类.

from equip.EquipmentInfo import EquipmentInfo
from equip.EquipmentExport import ImportExcelEquipment, getPlug

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
        equips = self.im.importData(attrStr)
        sumAttrib = {}
        sumPlug = 0
        sumPlugLvl = 0
        setCount = {}  # 套装统计
        for line in equips:
            #计算基础属性
            feature = self.equipmentInfo.getFeature(equips[line]["id_full"])
            if feature["set"] not in ["", "0"]:
                if feature["set"] not in setCount:
                    setCount[feature["set"]] = 1
                else:
                    setCount[feature["set"]] += 1
            singleAttrib = {}
            singleAttrib = self.attribMerge(singleAttrib, feature)

            #计算精炼
            refineLvl = int(equips[line]["star"])
            refineRate = [0, 0.005, 0.013, 0.024, 0.038, 0.055, 0.075, 0.098, 0.124][refineLvl]
            for attrib in singleAttrib:
                singleAttrib[attrib] = int(singleAttrib[attrib] * (1 + refineRate) + 0.5)

            #计算镶嵌
            for i in range(1, 4):
                plugLvl = equips[line]["plug%d"%i]
                if plugLvl in ['', ' ']:
                    plugLvl = 0
                else:
                    plugLvl = int(plugLvl)
                if plugLvl != 0:
                    sumPlug += 1
                    sumPlugLvl += plugLvl
                plugRate = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.2, 1.55][plugLvl]
                plugID = feature['DiamondAttributeID%d'%i]
                if plugID == 0 or plugLvl == 0:
                    continue
                plugAttribInfo = self.equipmentInfo.attrib[plugID]
                plugAttrib = {plugAttribInfo[0]: int(int(plugAttribInfo[1]) * plugRate)}
                singleAttrib = self.attribMerge(singleAttrib, plugAttrib)

            #计算附魔
            for i in range(1, 3):
                magicID = equips[line]["magic%d"%i]
                if magicID in ['', ' ', '0']:
                    continue
                if magicID in ["11272"]:  # 鞋子大附魔
                    magicAttrib = {'atTherapyPowerBase': 241}
                elif magicID in self.equipmentInfo.enchant:
                    magicAttribInfo = self.equipmentInfo.enchant[magicID]
                    if magicAttribInfo[0] in ["atExecuteScript"]:
                        continue
                    magicAttrib = {magicAttribInfo[0]: int(magicAttribInfo[1])}
                else:
                    magicAttrib = {}
                singleAttrib = self.attribMerge(singleAttrib, magicAttrib)
            sumAttrib = self.attribMerge(singleAttrib, sumAttrib)

        #计算五彩石
        colorID = equips["0"]["plug0"]
        colorAttrib = self.equipmentInfo.color[colorID]
        for i in range(3):  # 按属性个数排序
            if colorAttrib[i*4+2] == "" or colorAttrib[i*4+1] == "":
                continue
            if sumPlug >= int(colorAttrib[i*4+2]) and sumPlugLvl >= int(colorAttrib[i*4+3]):
                colorSingleAttrib = {colorAttrib[i*4]: int(colorAttrib[i*4+1])}
                sumAttrib = self.attribMerge(colorSingleAttrib, sumAttrib)

        #计算套装
        for line in setCount:
            if line not in self.equipmentInfo:
                continue
            setInfo = self.equipmentInfo.set[line]
            for i in range(10):
                setN = int(2 + i / 2)
                if setCount[line] >= setN:  # 满足套装数量条件
                    setAttribID = setInfo[i]
                    if setAttribID in ['', "0", 0]:
                        continue
                    setAttribRes = self.equipmentInfo.attrib[setAttribID]
                    setAttrib = {setAttribRes[0]: int(setAttribRes[1])}
                    sumAttrib = self.attribMerge(setAttrib, sumAttrib)

        return sumAttrib

    def __init__(self):
        self.equipmentInfo = EquipmentInfo()
        self.equipmentInfo.LoadFromStaticData()
        self.im = ImportExcelEquipment()

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
    ac = AttributeCal()
    ac.CalculateAll(str)
    # im = ImportExcelEquipment()
    # equips = im.importData(str)
    # print(equips)


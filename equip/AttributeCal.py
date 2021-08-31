# Created by moeheart at 08/31/2021
# 维护属性计算类.

from EquipmentInfo import EquipmentInfo
from EquipmentExport import ImportExcelEquipment

class AttributeCal():
    '''
    属性计算类，通过装备构成来推断出最终属性.
    '''

    def CalculateAll(self, attrStr):
        '''
        通过字符串形式的装备信息计算属性.
        格式由这一标准定义：https://www.jx3box.com/bbs/22011
        '''
        equips = self.im.importData(str)
        for line in equips:
            print(equips[line]["id_full"])
            singleAttrib = self.equipmentInfo.getFeature(equips[line]["id_full"])
            print(singleAttrib)

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
    ac = AttributeCal()
    ac.CalculateAll(str)
    # im = ImportExcelEquipment()
    # equips = im.importData(str)
    # print(equips)


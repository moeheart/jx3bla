# Created by moeheart at 08/31/2021
# 维护属性展示类.

from equip.AttributeCal import AttributeCal
from equip.AttributeData import *

class AttributeDisplay():

    def GetBaseAttrib(self, str, occ):
        '''
        根据心法和装备列表，计算所属心法的基础属性.
        这里计算了角色基础、心法基础、装备基础三种。如果要获取最终属性，需要用另外的方法.
        这些输入用游戏中at开头的字段名表示，而输出用中文表示，以示区分.
        params:
        - str: 配装标准表示法.
        - occ: 心法代码.
        returns:
        - res: 整理得到的基础属性.
        '''

        attrib = self.ac.CalculateAll(str)

        # 全心法的基础属性
        generalAttribute = OVERALL_OCC_BASE
        attrib1 = self.ac.attribMerge(attrib, generalAttribute)

        # 添加对应心法的基础属性
        occAttribute = {}
        if occ in OCC_BASE:
            occAttribute = OCC_BASE[occ]
        attrib2 = self.ac.attribMerge(attrib1, occAttribute)

        # 转换为中文名称
        attribDict = {'类型': 1, '主属性': '元气', '攻击': 1.95, '破防': 0.19}
        if occ in OCC_ATTRIB:
            attribDict = OCC_ATTRIB[occ]
        else:
            print("心法判断失败2", occ)

        # 计算属性
        playerType = attribDict["类型"]
        attrib3 = {"类型": playerType}

        attrib3 = getBaseAttrib(attrib3, attrib2, playerType, attribDict)

        # 基础值到真实值的转化
        attrib3["招架"] = attrib3.get("招架", 0) + 0.03
        attrib3["会心效果"] = attrib3.get("会心效果", 0) + 1.75
        return attrib3

    def GetPanelAttrib(self, str, occ):
        '''
        根据装备信息与心法，生成字典形式的面板属性结果.
        不同心法的结果列表也应当不同.
        params:
        - str 字符串形式的装备信息.
        - occ 心法.
        returns:
        - res 属性结果
        '''

        # 根据装备计算属性
        baseAttrib = self.GetBaseAttrib(str, occ)
        finalAttrib = baseAttrib.copy()
        mainAttribExtra = getExtraAttrib(occ, finalAttrib)
        for attrib in mainAttribExtra:
            finalAttrib[attrib] = finalAttrib.get(attrib, 0) + mainAttribExtra.get(attrib, 0) / getCoefficient(attrib)

        # 进行翻译
        result = finalAttrib.copy()
        result["会效"] = finalAttrib.get("会心效果", 0)
        result["基础攻击"] = baseAttrib.get("攻击", 0)
        result["基础治疗"] = baseAttrib.get("治疗", 0)
        result["会心等级"] = int(finalAttrib.get("会心", 0) * getCoefficient("会心"))
        result["会效等级"] = int((finalAttrib.get("会心效果", 0) - 1.75) * getCoefficient("会心效果"))
        result["加速等级"] = int(finalAttrib.get("加速", 0) * getCoefficient("加速"))
        result["破防等级"] = int(finalAttrib.get("破防", 0) * getCoefficient("破防"))
        result["无双等级"] = int(finalAttrib.get("无双", 0) * getCoefficient("无双"))

        return result


    def Display(self, str, occ):
        '''
        （即将废弃，被GetPanelAttrib取代）根据装备信息与心法，生成字典形式的属性结果.
        不同心法关注的结果也不同.
        params:
        - str 字符串形式的装备信息.
        - occ 心法.
        returns:
        属性结果
        '''

        result = {}

        # 根据装备计算属性
        attribute = self.ac.CalculateAll(str)

        standardAttribute = {'atSpiritBase': 38}  # 初始属性，目前只计算根骨
        attribute = self.ac.attribMerge(attribute, standardAttribute)

        c1 = ''
        c2 = ''
        c3 = 'atAllTypeCriticalStrike'
        ct1 = ''
        ct2 = ''
        ct3 = 'atCriticalDamagePowerBase'
        hRate = 0
        cRate = 0
        baseAttribute = {}
        if occ == '22h':  # 奶歌
            c1 = 'atLunarCriticalStrike'
            c2 = 'atMagicCriticalStrike'
            ct1 = 'atLunarCriticalDamagePowerBase'
            ct2 = 'atMagicCriticalDamagePowerBase'
            baseAttribute = {'atTherapyPowerBase': 3078}  # 为简洁性只写这一个
            hRate = 1.7
            cRate = 0.31
        if occ == '212h':  # 灵素
            c1 = 'atPoisonCriticalStrike'
            c2 = 'atMagicCriticalStrike'
            ct1 = 'atPoisonCriticalDamagePowerBase'
            ct2 = 'atMagicCriticalDamagePowerBase'
            baseAttribute = {'atTherapyPowerBase': 2768}  # 为简洁性只写这一个
            hRate = 1.8
            cRate = 0.11
        if occ == '2h':  # 奶花
            c1 = 'atNeutralCriticalStrike'
            c2 = 'atMagicCriticalStrike'
            ct1 = 'atNeutralCriticalDamagePowerBase'
            ct2 = 'atMagicCriticalDamagePowerBase'
            baseAttribute = {'atTherapyPowerBase': 2780}  # 为简洁性只写这一个
            hRate = 1.65
            cRate = 0.41
        if occ == '5h':  # 奶秀
            c1 = 'atLunarCriticalStrike'
            c2 = 'atMagicCriticalStrike'
            ct1 = 'atLunarCriticalDamagePowerBase'
            ct2 = 'atMagicCriticalDamagePowerBase'
            baseAttribute = {'atTherapyPowerBase': 2979}  # 为简洁性只写这一个
            hRate = 1.75
            cRate = 0.21
        if occ == '6h':  # 奶毒
            c1 = 'atPoisonCriticalStrike'
            c2 = 'atMagicCriticalStrike'
            ct1 = 'atPoisonCriticalDamagePowerBase'
            ct2 = 'atMagicCriticalDamagePowerBase'
            baseAttribute = {'atTherapyPowerBase': 2880}  # 为简洁性只写这一个
            hRate = 1.85
            cRate = 0

        attribute = self.ac.attribMerge(attribute, baseAttribute)

        spirit = attribute.get('atSpiritBase', 0)
        if occ in ['22h', '212h', '2h', '5h', '6h']:  # 根骨
            result['根骨'] = spirit

        # 由根骨得到的额外属性
        extraAttributeSpirit = {'atTherapyPower': int(hRate * spirit),
                                'atMagicCriticalStrike': int((cRate + 0.64) * spirit)}
        attribute = self.ac.attribMerge(attribute, extraAttributeSpirit)

        if occ in ['22h', '212h', '2h', '5h', '6h']:  # 治疗通用
            result['基础治疗'] = attribute.get('atTherapyPowerBase', 0)
            result['治疗'] = attribute.get('atTherapyPowerBase', 0) + attribute.get('atTherapyPower', 0)
            result['会心等级'] = attribute.get(c1, 0) + attribute.get(c2, 0) + attribute.get(c3, 0)
            result['会心'] = "%.2f%%"%(result['会心等级']/35737.5*100)
            result['会效等级'] = attribute.get(ct1, 0) + attribute.get(ct2, 0) + attribute.get(ct3, 0)
            result['会效'] = "%.2f%%"%(min(1.75+result['会效等级']/12506.25, 3)*100)
            result['加速等级'] = attribute.get('atHasteBase', 0)
            result['加速'] = "%.2f%%"%(min(result['加速等级']/43856.25, 0.25)*100)

        return result

    def __init__(self):
        self.ac = AttributeCal()

if __name__ == "__main__":
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
    str = "27221\t6\t11265\t0\t6\t\t\t\n54315\t6\t11189\t11274\t6\t6\t\t\n54150\t6\t11213\t11275\t6\t6\t\t\n31097\t6\t11248\t0\t6\t\t\t\n30999\t6\t11257\t0\t\t\t\t\n30981\t6\t11257\t0\t\t\t\t\n54098\t6\t11191\t11271\t6\t6\t\t\n31005\t4\t11250\t0\t6\t\t\t\n54303\t6\t11209\t0\t6\t6\t\t\n54124\t6\t11236\t11272\t6\t6\t\t\n54072\t6\t11232\t11273\t6\t6\t\t\n27278\t4\t11199\t0\t6\t6\t6\t15192"
    str = """32774	0	11664	0				
90563	0	0	0				
90835	0	11531	11684				
34407	0	0	0				
36130	0	11662	0				
34443	0	11657	0				
90611	0	0	0				
34413	0	0	0				
90383	0	11547	0				
90545	0	11613	0				
90918	0	11579	11682				
32569	0	11568	0				12095"""

    ad = AttributeDisplay()
    res = ad.Display(str, '7p')
    res = ad.GetPanelAttrib(str, '7p')
    for line in res:
        print(line, res[line])
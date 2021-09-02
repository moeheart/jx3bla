# Created by moeheart at 08/31/2021
# 维护属性展示类.

from AttributeCal import AttributeCal

class AttributeDisplay():

    def Display(self, str, occ):
        '''
        根据装备信息与心法，生成字典形式的属性结果.
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
        c3 = 'atCriticalStrike'
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

        attribute = self.ac.attribMerge(attribute, baseAttribute)

        spirit = attribute.get('atSpiritBase', 0)
        if occ in ['22h']:  # 根骨
            result['根骨'] = spirit

        # 由根骨得到的额外属性
        extraAttributeSpirit = {'atTherapyPower': int(hRate * spirit),
                                'atMagicCriticalStrike': int((cRate + 0.64) * spirit)}
        attribute = self.ac.attribMerge(attribute, extraAttributeSpirit)

        if occ in ['22h']:  # 治疗通用
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
    ad = AttributeDisplay()
    res = ad.Display(str, '22h')
    for line in res:
        print(line, res[line])
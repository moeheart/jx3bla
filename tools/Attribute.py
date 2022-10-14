# Created by moeheart at 10/14/2020
# 整理属性相关的常量与方法.

# 110级系数
COEFF110 = {
    '会心': 35737.5,
    '会心效果': 12506.25,
    '破防': 35737.5,
    '加速': 43856.25,
    '无双': 34458.75,
    '防御': 19091.25,
    '招架': 16293.75,
    '闪避': 17355,
    '御劲': 35737.5,
    '御劲减会伤': 9588.75,
    '化劲': 5175
}

# 120级系数
COEFF120 = {
    '会心': 78622.5,
    '会心效果': 27513.75,
    '破防': 78622.5,
    '加速': 96483.75,
    '无双': 75809.25,
    '防御': 42000.75,
    '招架': 35846.25,
    '闪避': 30549.75,
    '御劲': 78622.5,
    '御劲减会伤': 21095.25,
    '化劲': 11385
}

# 各种属性词条的实际作用方式，尽量记录全
# 内容为：属性意义、是否为“基础值”、影响外功、影响阳性内功、影响阴性内功、影响混元内功、影响毒性内功、直接提升最终值的系数
ATTRIB_TYPE = {
    # 会心
    "atAllTypeCriticalStrike": ["会心", 0, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalStrike": ["会心", 0, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalStrike": ["会心", 0, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalStrike": ["会心", 0, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalStrike": ["会心", 0, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalStrike": ["会心", 0, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalStrike": ["会心", 0, 0, 0, 0, 0, 1, 0],
    "atPhysicsCriticalStrikeBaseRate": ["会心", 0, 1, 0, 0, 0, 0, 0.0001],
    "atSolarCriticalStrikeBaseRate": ["会心", 0, 0, 1, 0, 0, 0, 0.0001],
    "atLunarCriticalStrikeBaseRate": ["会心", 0, 0, 0, 1, 0, 0, 0.0001],
    "atNeutralCriticalStrikeBaseRate": ["会心", 0, 0, 0, 0, 1, 0, 0.0001],
    "atPoisonCriticalStrikeBaseRate": ["会心", 0, 0, 0, 0, 0, 1, 0.0001],
    # 会心效果
    "atCriticalDamagePowerBase": ["会心效果", 1, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalDamagePowerBase": ["会心效果", 1, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 0, 1, 0],
    "atPhysicsCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 1, 0, 0, 0, 0, 1/1024],
    "atMagicCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 0, 1, 1, 1, 1, 1/1024],
    "atSolarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonCriticalDamagePowerBaseKiloNumRate": ["会心效果", 0, 0, 0, 0, 0, 1, 1/1024],
    # 破防
    "atPhysicsOvercomeBase": ["破防", 1, 1, 0, 0, 0, 0, 0],
    "atMagicOvercome": ["破防", 1, 0, 1, 1, 1, 1, 0],
    "atSolarOvercomeBase": ["破防", 1, 0, 1, 0, 0, 0, 0],
    "atLunarOvercomeBase": ["破防", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralOvercomeBase": ["破防", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonOvercomeBase": ["破防", 1, 0, 0, 0, 0, 1, 0],
    "atSolarAndLunarOvercomeBase": ["破防", 1, 0, 1, 1, 0, 0, 0],
    "atPhysicsOvercomePercent": ["破防", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarOvercomePercent": ["破防", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarOvercomePercent": ["破防", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralOvercomePercent": ["破防", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonOvercomePercent": ["破防", 0, 0, 0, 0, 0, 1, 1/1024],
    # 加速
    "atHasteBase": ["加速", 1, 1, 1, 1, 1, 1, 0],
    "atHasteBasePercentAdd": ["加速", 0, 1, 1, 1, 1, 1, 1/1024],
    "atUnlimitHasteBasePercentAdd": ["加速", 0, 1, 1, 1, 1, 1, 1/1024],
    # 治疗
    "atTherapyPowerBase": ["治疗", 1, 1, 1, 1, 1, 1, 0],
    "atTherapyPowerPercent": ["治疗", 0, 1, 1, 1, 1, 1, 1/1024],
    # 主属性
    "atVitalityBase": ["体质", 1, 1, 1, 1, 1, 1, 0],
    "atStrengthBase": ["力道", 1, 1, 1, 1, 1, 1, 0],
    "atAgilityBase": ["身法", 1, 1, 1, 1, 1, 1, 0],
    "atSpunkBase": ["元气", 1, 1, 1, 1, 1, 1, 0],
    "atSpiritBase": ["根骨", 1, 1, 1, 1, 1, 1, 0],
    "atVitalityBasePercentAdd": ["体质", 0, 1, 1, 1, 1, 1, 1/1024],
    "atStrengthBasePercentAdd": ["力道", 0, 1, 1, 1, 1, 1, 1/1024],
    "atAgilityBasePercentAdd": ["身法", 0, 1, 1, 1, 1, 1, 1/1024],
    "atSpunkBasePercentAdd": ["元气", 0, 1, 1, 1, 1, 1, 1/1024],
    "atSpiritBasePercentAdd": ["根骨", 0, 1, 1, 1, 1, 1, 1/1024],
    # 攻击
    "atPhysicsAttackPowerBase": ["攻击", 1, 1, 0, 0, 0, 0, 0],
    "atMagicAttackPowerBase": ["攻击", 1, 0, 1, 1, 1, 1, 0],
    "atSolarAttackPowerBase": ["攻击", 1, 0, 1, 0, 0, 0, 0],
    "atLunarAttackPowerBase": ["攻击", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralAttackPowerBase": ["攻击", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonAttackPowerBase": ["攻击", 1, 0, 0, 0, 0, 1, 0],
    "atPhysicsAttackPowerPercent": ["攻击", 0, 1, 0, 0, 0, 0, 1/1024],
    "atMagicAttackPowerPercent": ["攻击", 0, 0, 1, 1, 1, 1, 1/1024],
    "atSolarAttackPowerPercent": ["攻击", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarAttackPowerPercent": ["攻击", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralAttackPowerPercent": ["攻击", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonAttackPowerPercent": ["攻击", 0, 0, 0, 0, 0, 1, 1/1024],
    # 无双
    "atStrainBase": ["无双", 1, 1, 1, 1, 1, 1, 0],
    "atStrainPercent": ["无双", 0, 1, 1, 1, 1, 1, 1/1024],
    # 破招
    "atSurplusValueBase": ["破招", 1, 1, 1, 1, 1, 1, 0],
    # 防御
    "atPhysicsShieldBase": ["防御", 1, 1, 0, 0, 0, 0, 0],
    "atSolarShieldBase": ["防御", 1, 0, 1, 0, 0, 0, 0],
    "atLunarShieldBase": ["防御", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralShieldBase": ["防御", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonShieldBase": ["防御", 1, 0, 0, 0, 0, 1, 0],
    "atPhysicsShieldAdditional": ["防御", 0, 1, 0, 0, 0, 0, 0],
    "atMagicShield": ["防御", 0, 0, 1, 1, 1, 1, 0],
    "atPhysicsShieldPercent": ["防御", 0, 1, 0, 0, 0, 0, 0],
    "atSolarMagicShieldPercent": ["防御", 0, 0, 1, 0, 0, 0, 0],
    "atLunarMagicShieldPercent": ["防御", 0, 0, 0, 1, 0, 0, 0],
    "atNeutralMagicShieldPercent": ["防御", 0, 0, 0, 0, 1, 0, 0],
    "atPoisonMagicShieldPercent": ["防御", 0, 0, 0, 0, 0, 1, 0],
    # 招架
    "atParryBase": ["招架", 1, 1, 1, 1, 1, 1, 0],
    "atParryBaseRate": ["招架", 0, 1, 1, 1, 1, 1, 0.0001],
    # 拆招
    "atParryValueBase": ["拆招", 1, 1, 1, 1, 1, 1, 0],
    "atParryValuePercent": ["拆招", 0, 1, 1, 1, 1, 1, 1/1024],
    # 闪避
    "atDodge": ["闪避", 1, 1, 1, 1, 1, 1, 0],
    "atDodgeBaseRate": ["闪避", 0, 1, 1, 1, 1, 1, 0.0001],
    # 御劲
    "atToughnessBase": ["御劲", 1, 1, 1, 1, 1, 1, 0],
    "atToughnessBaseRate": ["御劲", 0, 1, 1, 1, 1, 1, 0.0001],
    # 化劲
    "atDecriticalDamagePowerBase": ["化劲", 1, 1, 1, 1, 1, 1, 0],
    "atDecriticalDamagePowerPercent": ["化劲", 0, 1, 1, 1, 1, 1, 1/1024],
}


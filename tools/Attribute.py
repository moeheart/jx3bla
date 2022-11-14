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
    '化劲': 5175,
    '气血': 1,
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
    '化劲': 11385,
    '气血': 1,
}

# 各种属性词条的实际作用方式，尽量记录全
# 内容为：属性意义、是否为“基础值”、影响外功、影响阳性内功、影响阴性内功、影响混元内功、影响毒性内功、直接提升最终值的系数
ATTRIB_TYPE = {
    # 会心
    "atAllTypeCriticalStrike": ["会心", 1, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalStrike": ["会心", 1, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalStrike": ["会心", 1, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalStrike": ["会心", 1, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalStrike": ["会心", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalStrike": ["会心", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalStrike": ["会心", 1, 0, 0, 0, 0, 1, 0],
    "atPhysicsCriticalStrikeBaseRate": ["会心", 1, 1, 0, 0, 0, 0, 0.0001],
    "atSolarCriticalStrikeBaseRate": ["会心", 1, 0, 1, 0, 0, 0, 0.0001],
    "atLunarCriticalStrikeBaseRate": ["会心", 1, 0, 0, 1, 0, 0, 0.0001],
    "atNeutralCriticalStrikeBaseRate": ["会心", 1, 0, 0, 0, 1, 0, 0.0001],
    "atPoisonCriticalStrikeBaseRate": ["会心", 1, 0, 0, 0, 0, 1, 0.0001],
    # 会心效果
    "atCriticalDamagePowerBase": ["会心效果", 1, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalDamagePowerBase": ["会心效果", 1, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 0, 1, 0],
    "atPhysicsCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 1, 0, 0, 0, 0, 1/1024],
    "atMagicCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 1, 1, 1, 1, 1/1024],
    "atSolarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 1, 0, 0, 0, 1/1024],
    "atLunarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 0, 0, 1, 1/1024],
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
    "atBasePotentialAdd": ["全属性", 1, 1, 1, 1, 1, 1, 0],
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
    "atSolarShieldBase": ["防御", 1, 1, 1, 0, 0, 0, 0],
    "atLunarShieldBase": ["防御", 1, 1, 0, 1, 0, 0, 0],
    "atNeutralShieldBase": ["防御", 1, 1, 0, 0, 1, 0, 0],
    "atPoisonShieldBase": ["防御", 1, 1, 0, 0, 0, 1, 0],
    "atPhysicsShieldAdditional": ["防御", 0, 1, 0, 0, 0, 0, 0],
    "atMagicShield": ["防御", 0, 0, 1, 1, 1, 1, 0],
    "atPhysicsShieldPercent": ["防御%", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarMagicShieldPercent": ["防御%", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarMagicShieldPercent": ["防御%", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralMagicShieldPercent": ["防御%", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonMagicShieldPercent": ["防御%", 0, 0, 0, 0, 0, 1, 1/1024],
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

    #### 不属于属性的增益
    "atAllDamageAddPercent": ["伤害变化", 1, 1, 1, 1, 1, 1, 0],
    "atAllPhysicsDamageAddPercent": ["伤害变化", 1, 1, 0, 0, 0, 0, 0],
    "atAllMagicDamageAddPercent": ["伤害变化", 1, 0, 1, 1, 1, 1, 0],
    "atPhysicsDamageCoefficient": ["受伤增加", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarDamageCoefficient": ["受伤增加", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarDamageCoefficient": ["受伤增加", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralDamageCoefficient": ["受伤增加", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonDamageCoefficient": ["受伤增加", 0, 0, 0, 0, 0, 1, 1/1024],
    "atAllShieldIgnorePercent": ["无视防御A", 1, 1, 1, 1, 1, 1, 0],
}

# 阵眼相关的ID记录.
# 前三重buffID 心法名 阵法名 队友buff 自身buff 团队buff 最高等级
ZHENYAN_DICT = {"0": ["未知", "未知", [], [], [], 0],
                "914": ["洗髓", "金刚伏魔阵", ["13891"], ["916"], [], 6],
                "919": ["易筋", "天鼓雷音阵", ["920"], ["940"], [], 6],
                "923": ["铁牢", "九襄地玄阵", ["926"], ["925"], [], 6],
                "924": ["离经", "落星惊鸿阵", ["928"], ["927"], [], 6],
                "930": ["傲血", "卫公折冲阵", ["936"], ["935", "940"], [], 6],
                "934": ["花间", "七绝逍遥阵", ["939"], ["937"], [], 6],
                "938": ["气纯", "九宫八卦阵", ["943"], ["949"], [], 6],
                "942": ["奶秀", "花月凌风阵", [], ["944", "948"], ["945"], 6],
                "947": ["剑纯", "北斗七星阵", ["950"], ["953"], [], 6],
                "952": ["冰心", "九音惊弦阵", ["955"], ["954", "956"], [], 6],
                "1924": ["藏剑", "依山观澜阵", ["1925"], ["1926"], [], 6],
                "2506": ["奶毒", "妙手织天阵", [], ["2507", "2510"], ["2508"], 6],
                "2512": ["毒经", "万蛊噬心阵", ["2514"], ["2513", "2510"], [], 6],
                "3306": ["惊羽", "流星赶月阵", ["3308"], ["3309"], [], 6],
                "3307": ["田螺", "千机百变阵", ["3310"], ["3311"], [], 6],
                "4579": ["焚影", "炎威破魔阵", [], ["4584"], ["4586"], 6],
                "4580": ["明尊", "无量光明阵", [], ["4587"], [], 6],
                "6342": ["丐帮", "降龙伏虎阵", ["6345"], ["6343", "6362"], [], 6],
                "8402": ["分山", "锋凌横绝阵", ["8403"], ["8404", "8484"], [], 1],
                "8338": ["铁骨", "临川列山阵", ["8341"], ["8339"], [], 1],
                "9485": ["莫问", "万籁金弦阵", ["9492"], ["9486", "9489"], [], 1],
                "9476": ["奶歌", "浮声清脉阵", [], ["9477", "9479", "9483"], [], 1],
                "10954": ["霸刀", "霜岚洗锋阵", ["11158"], ["11159"], [], 6],
                "14074": ["蓬莱", "墟海引归阵", ["14093"], ["14092", "14095"], [], 6],
                "15957": ["凌雪", "龙皇雪风阵", ["15961"], ["15960", "15963"], [], 6],
                "21035": ["无方", "乱暮浊茵阵", [], ["21059"], [], 6],
                "21065": ["灵素", "潜光藏象阵", ["21069"], ["21071"], [], 6],
                "24578": ["刀宗", "横云破锋阵", ["24582"], ["24581"], [], 6],
                }




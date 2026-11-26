"""Normalize attribute calls shared by the historical and formal xinfa generators."""

BASE_ATTRIBUTE_NAMES = {
    'MAGIC_ATTACK_POWER_BASE': 'atMagicAttackPowerBase',
    'PHYSICS_ATTACK_POWER_BASE': 'atPhysicsAttackPowerBase',
    'SOLAR_ATTACK_POWER_BASE': 'atSolarAttackPowerBase',
    'LUNAR_ATTACK_POWER_BASE': 'atLunarAttackPowerBase',
    'NEUTRAL_ATTACK_POWER_BASE': 'atNeutralAttackPowerBase',
    'POISON_ATTACK_POWER_BASE': 'atPoisonAttackPowerBase',
    'THERAPY_POWER_BASE': 'atTherapyPowerBase',
    'MAGIC_SHIELD': 'atMagicShield',
    'PHYSICS_SHIELD_BASE': 'atPhysicsShieldBase',
    'PHYSICS_CRITICAL_STRIKE': 'atPhysicsCriticalStrike',
    'SOLAR_CRITICAL_STRIKE': 'atSolarCriticalStrike',
    'LUNAR_CRITICAL_STRIKE': 'atLunarCriticalStrike',
    'NEUTRAL_CRITICAL_STRIKE': 'atNeutralCriticalStrike',
    'POISON_CRITICAL_STRIKE': 'atPoisonCriticalStrike',
    'PHYSICS_OVERCOME_BASE': 'atPhysicsOvercomeBase',
    'POISON_OVERCOME_BASE': 'atPoisonOvercomeBase',
    'PARRY_BASE': 'atParryBase', 'PARRYVALUE_BASE': 'atParryValueBase',
    'DODGE': 'atDodge', 'MAX_LIFE_PERCENT_ADD': 'atMaxLifePercentAdd',
    'DST_NPC_DAMAGE_COEFFICIENT': 'atDstNpcDamageCoefficient',
    'DECRITICAL_DAMAGE_POWER_BASE_KILONUM_RATE': 'atDecriticalDamagePowerBaseKiloNumRate',
    'LIFE_REPLENISH_EXT': 'atLifeReplenishExt',
}
MAIN_ATTRIBUTES = {'STRENGTH': '力道', 'AGILITY': '身法', 'SPIRIT': '根骨',
                   'SPUNK': '元气', 'VITALITY': '体质'}
DERIVED_ATTRIBUTES = {'ATTACK_POWER': '攻击', 'CRITICAL_STRIKE': '会心', 'OVERCOME': '破防',
                      'THERAPY_POWER': '治疗', 'MAX_LIFE': '气血', 'MAX_MANA': '内力',
                      'SHIELD': '防御', 'PARRY': '招架', 'PARRY_VALUE': '拆招', 'DODGE': '闪避'}


def normalize_attributes(calls):
    base, conversions = {}, []
    for call in calls:
        name, value = call['attribute'], call['value_a']
        if name in BASE_ATTRIBUTE_NAMES:
            target = BASE_ATTRIBUTE_NAMES[name]
            base[target] = base.get(target, 0) + value
        if '_TO_' not in name or not name.endswith('_COF'):
            continue
        source, destination = name[:-4].split('_TO_', 1)
        if source not in MAIN_ATTRIBUTES:
            continue
        school = 'All'
        for prefix in ('SOLAR_AND_LUNAR', 'PHYSICS', 'SOLAR', 'NEUTRAL', 'LUNAR', 'POISON', 'MAGIC'):
            if destination.startswith(prefix + '_'):
                school, destination = prefix, destination[len(prefix) + 1:]
                break
        if destination not in DERIVED_ATTRIBUTES:
            raise ValueError(('Unknown conversion', name))
        conversions.append(dict(source=MAIN_ATTRIBUTES[source], target=DERIVED_ATTRIBUTES[destination],
            school=school, raw=value, denominator=1024, coefficient=value / 1024, enum=name,
            denominator_basis='Original client role_attribute.lua: R44 lijing 686/1024 and 82/1024, yunshang 727/1024 and 41/1024; current skill Lua controls the numerator'))
    return base, conversions

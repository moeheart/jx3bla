"""Current formal-server 50-level attribute calculations.

The input remains the game's raw at* attributes. This keeps percentage boosts
and temporary main-stat conversions correct when a base value is zero.
"""
from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path
import re

from tools.Attribute import ATTRIB_TYPE, COEFF50, CURRENT_GAME_EDITION
from tools.Functions import getOccType

RESOURCE_ROOT = Path(__file__).parent / 'resources' / 'cangshengtf'
SCHOOLS = {1: 'Physics', 2: 'Solar', 3: 'Lunar', 4: 'Neutral', 5: 'Poison'}
PRIMARY = {'Vitality': '体质', 'Strength': '力道', 'Agility': '身法', 'Spunk': '元气', 'Spirit': '根骨'}
ATTACK_SOURCES = {'混元攻击': 'Neutral', '阴性攻击': 'Lunar', '毒性攻击': 'Poison'}

# Ordinary kungfu evidence predates the explicit school field. Keep only this
# classification here; no old-level attribute values enter the runtime.
OCC_SCHOOLS = {
    '1d': 'Solar', '1t': 'Solar', '2d': 'Neutral', '2h': 'Neutral',
    '3d': 'Physics', '3t': 'Physics', '4p': 'Physics', '4m': 'Neutral',
    '5d': 'Lunar', '5h': 'Lunar', '6d': 'Poison', '6h': 'Poison',
    '7p': 'Physics', '7m': 'Poison', '8': 'Physics', '9': 'Physics',
    '10d': 'Solar', '10t': 'Solar', '21d': 'Physics', '21t': 'Physics',
    '22d': 'Lunar', '22h': 'Lunar', '23': 'Physics', '24': 'Physics',
    '25': 'Physics', '211': 'Neutral', '212d': 'Poison', '212h': 'Poison',
    '213': 'Physics', '214': 'Physics', '215': 'Neutral',
}


@lru_cache(maxsize=1)
def kungfu_data():
    return json.loads((RESOURCE_ROOT / 'xinfa50.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def formal_parameters():
    return json.loads((RESOURCE_ROOT / 'global_parameters.json').read_text(encoding='utf-8'))['values']


def get_profile(occ):
    profiles = kungfu_data()['occupations']
    if occ not in profiles:
        raise ValueError('尚无当前客户端心法属性证据：' + occ)
    return profiles[occ]


@lru_cache(maxsize=1)
def npc_data():
    return json.loads((RESOURCE_ROOT / 'luoyang_npc_defense.json').read_text(encoding='utf-8'))


def get_target_profiles(info):
    if info.map != npc_data()['map']:
        return {}
    rows = npc_data()['profiles']

    def complete(profile):
        level = profile.get('level')
        shields = profile.get('shieldBase')
        if not isinstance(level, int) or isinstance(level, bool) or level <= 0 or not isinstance(shields, dict):
            return False
        # Missing client defense is unresolved evidence, never a zero defense.
        return all(isinstance(shields.get(school), (int, float))
                   and not isinstance(shields[school], bool)
                   and 0 <= shields[school] < float('inf') for school in SCHOOLS.values())

    return {npc_id: rows[str(npc.templateID)] for npc_id, npc in info.npc.items()
            if str(npc.templateID) in rows and complete(rows[str(npc.templateID)])}


def merge_attributes(*groups):
    result = defaultdict(float)
    for group in groups:
        for key, value in group.items():
            if key.startswith('at') and isinstance(value, (int, float)):
                result[key] += value
    return dict(result)


def conversion_spec(attribute):
    """Map runtime conversion attribute names to a source and a target school."""
    match = re.fullmatch(r'at(.+?)To(.+?)Cof', attribute)
    if not match:
        return None
    source, target = match.groups()
    source_key = PRIMARY.get(source, {'TherapyPower': '治疗', 'MaxLife': '气血',
        'ParryValue': '拆招', 'NeutralAttackPower': '混元攻击', 'LunarAttackPower': '阴性攻击',
        'PoisonAttackPower': '毒性攻击'}.get(source))
    if source_key is None:
        return None
    school = ''
    for prefix in ('SolarAndLunar', 'Physics', 'Solar', 'Lunar', 'Neutral', 'Poison', 'Magic'):
        if target.startswith(prefix):
            school, target = prefix, target[len(prefix):]
            break
    target_key = {'AttackPower': '攻击', 'TherapyPower': '治疗', 'CriticalStrike': '会心等级',
        'OverCome': '破防等级', 'Overcome': '破防等级', 'Shield': '防御等级',
        'Parry': '招架等级', 'ParryValue': '拆招', 'Dodge': '闪避等级', 'MaxLife': '气血'}.get(target)
    return (source_key, target_key, school) if target_key else None


class CangshengAttributeData:
    """BoostCounter-compatible calculator using a complete raw attribute sum."""
    def __init__(self, occ, gameEdition=CURRENT_GAME_EDITION):
        self.occ = occ
        self.gameEdition = CURRENT_GAME_EDITION
        self.baseAttrib = None
        self.boosts = []
        self.combined = {}
        self.school = None

    def setBoosts(self, boosts):
        self.boosts = list(boosts)

    def getFinalAttrib(self):
        if not self.baseAttrib or '_raw' not in self.baseAttrib:
            raise ValueError('50级属性计算缺少真实装备和心法输入：' + self.occ)
        self.combined = merge_attributes(self.baseAttrib['_raw'], *self.boosts)
        return calculate_attributes(self.combined, self.occ, school=self.school)

    def removeBoostAndGetAttrib(self, boost):
        for key, value in boost.items():
            if key.startswith('at'):
                self.combined[key] = self.combined.get(key, 0) - value
        return calculate_attributes(self.combined, self.occ, school=self.school)

    def addBoostAndGetAttrib(self, boost):
        for key, value in boost.items():
            if key.startswith('at'):
                self.combined[key] = self.combined.get(key, 0) + value
        return calculate_attributes(self.combined, self.occ, school=self.school)


def profile_school(occ):
    profile = get_profile(occ)
    return profile.get('school') or OCC_SCHOOLS[occ]


def school_matches(required, actual):
    return not required or required == actual or (required == 'Magic' and actual != 'Physics') or (required == 'SolarAndLunar' and actual in ('Solar', 'Lunar'))


def enum_attribute(enum):
    # The game uses both OverCome (conversion) and Overcome (rating) spellings.
    name = 'at' + ''.join(part.title() for part in enum.split('_'))
    return name.replace('Parryvalue', 'ParryValue').replace('Kilonum', 'KiloNum')


def static_attributes(occ):
    result = defaultdict(float)
    for row in get_profile(occ)['raw_attributes']:
        name = enum_attribute(row['attribute'])
        if (name in ATTRIB_TYPE or conversion_spec(name) or name in (
                'atMaxLifeBase', 'atMaxLifePercentAdd', 'atDecriticalDamagePowerBaseKiloNumRate',
                'atDstNpcDamageCoefficient', 'atAdaptAttributeType')):
            if isinstance(row['value_a'], (int, float)):
                result[name] += row['value_a']
    return dict(result)


def adapt_youluo_equipment(equipment):
    """Client panel child21 adapts equipment before adding naked attributes."""
    result = equipment.copy()
    sources = ('atStrengthBase', 'atSpunkBase', 'atAgilityBase')
    result['atSpiritBase'] = result.get('atSpiritBase', 0) + max(
        0, *(result.pop(key, 0) for key in sources))
    return result


def adapt_youluo_ratings(raw):
    """Client panel child31 takes the largest alternate-school contribution.

    Both Youluo kungfus enable ADAPT_ATTRIBUTE_TYPE=1. Preserve raw input so
    boost removal recalculates the winning source rather than subtracting a
    previously adapted number. See docs/160/evidence/wujie_evidence/youluo_panel_evidence.json.
    """
    result = raw.copy()
    for suffix in ('AttackPowerBase', 'CriticalStrike', 'CriticalDamagePowerBase', 'OvercomeBase'):
        sources = tuple('at' + school + suffix for school in ('Solar', 'Neutral', 'Poison', 'Physics'))
        candidate = max(0, *(result.get(key, 0) for key in sources if key != 'atPhysicsAttackPowerBase'))
        if suffix == 'AttackPowerBase':
            candidate = max(candidate, result.get('atPhysicsAttackPowerBase', 0) + 6 * (
                result.get('atMeleeWeaponDamageBase', 0) + result.get('atMeleeWeaponDamageRand', 0) / 2))
        for key in sources:
            result.pop(key, None)
        target = 'atLunar' + suffix
        result[target] = result.get(target, 0) + candidate
    return result


def make_base_attributes(equipment, occ):
    # Current role_attribute.lua R54 provides the default base attributes.
    general = {'atVitalityBase': 18, 'atStrengthBase': 17, 'atAgilityBase': 18,
               'atSpiritBase': 18, 'atSpunkBase': 17, 'atMaxLifeBase': 3956}
    static = static_attributes(occ)
    if static.get('atAdaptAttributeType') == 1:
        equipment = adapt_youluo_equipment(equipment)
    raw = merge_attributes(equipment, general, static)
    result = calculate_attributes(raw, occ, include_conversions=False)
    result['_raw'] = raw
    result['_baseSource'] = 'formal client 1.6.0.10009 role_attribute.lua R54; JCL body type unavailable'
    return result


def calculate_attributes(raw, occ, include_conversions=True, school=None, include_secondary=True):
    """Apply flat values, base multipliers, then main-stat conversions."""
    school = school or profile_school(occ)
    if raw.get('atAdaptAttributeType') == 1:
        raw = adapt_youluo_ratings(raw)
    player_type = next(key for key, value in SCHOOLS.items() if value == school)
    result = defaultdict(float)
    ratings, rates, multipliers = defaultdict(float), defaultdict(float), defaultdict(float)
    for prefix, name in PRIMARY.items():
        value = raw.get('at' + prefix + 'Base', 0) + raw.get('atBasePotentialAdd', 0)
        result[name] = value * (1 + raw.get('at' + prefix + 'BasePercentAdd', 0) / 1024)

    nonlinear = {'防御', '闪避', '招架', '化劲'}
    rating_names = {'会心', '会心效果', '破防', '加速', '无双', '防御', '闪避', '招架', '御劲', '化劲'}
    for key, value in raw.items():
        direct_rates = {'atParryBaseRate': '招架', 'atDodgeBaseRate': '闪避', 'atToughnessBaseRate': '御劲'}
        if key in direct_rates:
            rates[direct_rates[key]] += value / 10000
            continue
        if key == 'atMagicShield' and school != 'Physics':
            ratings['防御'] += value
            continue
        if key == 'atPhysicsShieldAdditional' and school == 'Physics':
            ratings['防御'] += value
            continue
        desc = ATTRIB_TYPE.get(key)
        if not desc or not desc[player_type + 1] or desc[0] in set(PRIMARY.values()) | {'全属性', '受伤增加'}:
            continue
        name, flat, factor = desc[0], desc[1], desc[7]
        if name.endswith('%'):
            multipliers[name[:-1]] += value * factor
        elif not flat:
            # Percentage boosts affect the base rating/AP, before main-stat AP.
            multipliers[name] += value * factor
        elif name in rating_names:
            if factor == 0:
                ratings[name] += value
            else:
                rates[name] += value * factor
        else:
            result[name] += value * (factor or 1)

    result['全能'] = raw.get('atPVXAllRound', 0)
    result['非侠士伤害系数'] = 1 + raw.get('atDstNpcDamageCoefficient', 0) / 1024
    result['气血'] = raw.get('atMaxLifeBase', 0)
    if include_conversions:
        # Read the formal 10009 parameters directly; no test-server fallback.
        parameters = formal_parameters()
        result['气血'] += result['体质'] * (parameters['nVitalityToMaxLifeCof'] / 1000)
        if school == 'Physics':
            result['攻击'] += result['力道'] * (parameters['nStrengthToPhysicsAPCof'] / 1000)
            ratings['破防'] += result['力道'] * (parameters['nStrengthToPhysicsOvercomeCof'] / 1000)
            ratings['会心'] += result['身法'] * (parameters['nAgilityToPhysicsCriticalCof'] / 1000)
        else:
            result['攻击'] += result['元气'] * (parameters['nSpunkToMagicAPCof'] / 1000)
            ratings['破防'] += result['元气'] * (parameters['nSpunkToMagicOvercomeCof'] / 1000)
            ratings['会心'] += result['根骨'] * (parameters['nSpiritToMagicCriticalCof'] / 1000)
        # The all-round treatment toggle is controlled by the healer kungfu.
        if getOccType(occ) == 'healer':
            result['治疗'] += result['全能'] * (parameters['nPVXAllRoundToTherapyPowerCof'] / 1000)
        else:
            ratings['无双'] += result['全能'] * (parameters['nPVXAllRoundToStrainCof'] / 1000)
        ratings['化劲'] += result['全能'] * (parameters['nPVXAllRoundToDecriticalDamagePowerCof'] / 1000)

    # Retain the AP/therapy basis used by percentage buffs. The global innate
    # conversion above is included in base AP, unlike the kungfu extra AP.
    result['基础攻击'] = result['攻击']
    result['基础治疗'] = result['治疗']
    for name, multiplier in multipliers.items():
        if name in rating_names:
            ratings[name] *= 1 + multiplier
        else:
            result[name] *= 1 + multiplier

    if include_conversions:
        converted = defaultdict(float)
        for key, value in raw.items():
            spec = conversion_spec(key)
            if spec is None or spec[0] not in PRIMARY.values() or not school_matches(spec[2], school):
                continue
            source, target, _ = spec
            converted[target] += result[source] * value / 1024
        for name, value in converted.items():
            if name.endswith('等级'):
                ratings[name[:-2]] += value
            else:
                result[name] += value

    result['气血'] *= 1 + raw.get('atMaxLifePercentAdd', 0) / 1024
    if include_conversions and include_secondary:
        # Follow the dependency direction: primary stats -> AP/therapy/life ->
        # secondary conversions. Read AP-to-therapy before therapy-to-AP, so a
        # bidirectional pair never recursively amplifies itself.
        attack_sources = {}
        for key in raw:
            spec = conversion_spec(key)
            if spec is not None and spec[0] in ATTACK_SOURCES:
                source_school = ATTACK_SOURCES[spec[0]]
                attack_sources[spec[0]] = (result['攻击'] if source_school == school else
                    calculate_attributes(raw, occ, school=source_school, include_secondary=False)['攻击'])
        for sources in (set(ATTACK_SOURCES), {'治疗', '气血', '拆招'}):
            secondary = defaultdict(float)
            for key, value in raw.items():
                spec = conversion_spec(key)
                if spec is None or spec[0] not in sources or not school_matches(spec[2], school):
                    continue
                source_value = attack_sources[spec[0]] if spec[0] in ATTACK_SOURCES else result[spec[0]]
                secondary[spec[1]] += source_value * value / 1024
            for name, value in secondary.items():
                if name.endswith('等级'):
                    ratings[name[:-2]] += value
                else:
                    result[name] += value
    for name in rating_names:
        rating = max(0, ratings[name])
        result[name + '等级'] = rating
        if name in nonlinear:
            result[name] = rating / (rating + COEFF50[name]) + rates[name]
        else:
            result[name] = rating / COEFF50[name] + rates[name]
    result['招架'] += 0.03
    result['会心效果'] += 1.75
    result['额外会心效果'] = raw.get('atUnlimitCriticalDamagePowerKiloNumRate', 0) / 1024
    result['化劲'] += raw.get('atDecriticalDamagePowerBaseKiloNumRate', 0) / 1024
    result['会效'] = result['会心效果']
    result['会效等级'] = result['会心效果等级']
    result['类型'] = player_type
    return dict(result)

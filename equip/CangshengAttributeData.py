"""50-level attribute calculations isolated from the legacy CHAPTER profile.

The input remains the game's raw at* attributes. This keeps percentage boosts
and temporary main-stat conversions correct when a base value is zero.
"""
from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path
import re

from tools.Attribute import ATTRIB_TYPE, COEFF50

RESOURCE_ROOT = Path(__file__).parent / 'resources' / 'cangshengtf'
SCHOOLS = {1: 'Physics', 2: 'Solar', 3: 'Lunar', 4: 'Neutral', 5: 'Poison'}
PRIMARY = {'Vitality': '体质', 'Strength': '力道', 'Agility': '身法', 'Spunk': '元气', 'Spirit': '根骨'}
ATTACK_SOURCES = {'混元攻击': 'Neutral', '阴性攻击': 'Lunar', '毒性攻击': 'Poison'}


@lru_cache(maxsize=1)
def kungfu_data():
    return json.loads((RESOURCE_ROOT / 'xinfa50.json').read_text(encoding='utf-8'))


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
    return {npc_id: rows[str(npc.templateID)] for npc_id, npc in info.npc.items()
            if str(npc.templateID) in rows}


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
    def __init__(self, occ):
        self.occ = occ
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
    # Select only the attack school from the legacy lookup, never its numbers.
    from equip.AttributeData import OCC_ATTRIB
    return SCHOOLS[2 if occ == '10t' else OCC_ATTRIB[occ]['类型']]


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
                'atDstNpcDamageCoefficient')):
            if isinstance(row['value_a'], (int, float)):
                result[name] += row['value_a']
    return dict(result)


def make_base_attributes(equipment, occ):
    # Current role_attribute.lua R54 provides the default base attributes.
    general = {'atVitalityBase': 18, 'atStrengthBase': 17, 'atAgilityBase': 18,
               'atSpiritBase': 18, 'atSpunkBase': 17, 'atMaxLifeBase': 3956}
    raw = merge_attributes(equipment, general, static_attributes(occ))
    result = calculate_attributes(raw, occ, include_conversions=False)
    result['_raw'] = raw
    result['_baseSource'] = 'current role_attribute.lua R54; JCL body type unavailable'
    return result


def calculate_attributes(raw, occ, include_conversions=True, school=None, include_secondary=True):
    """Apply flat values, base multipliers, then main-stat conversions."""
    school = school or profile_school(occ)
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
        # GlobalParam stores these general conversions in thousandths.
        result['气血'] += result['体质'] * 10
        if school == 'Physics':
            result['攻击'] += result['力道'] * 0.195
            ratings['破防'] += result['力道'] * 0.061
            ratings['会心'] += result['身法'] * 0.25
        else:
            result['攻击'] += result['元气'] * 0.195
            ratings['破防'] += result['元气'] * 0.061
            ratings['会心'] += result['根骨'] * 0.25
        # The all-round treatment toggle is controlled by the healer kungfu.
        if occ.endswith('h'):
            result['治疗'] += result['全能'] * 0.15
        else:
            ratings['无双'] += result['全能'] * 1.22
        ratings['化劲'] += result['全能']

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

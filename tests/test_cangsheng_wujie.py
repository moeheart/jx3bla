"""Current-client Wujie kungfu profiles, conversion branches and whole-log replay."""
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from equip.AttributeDisplay import AttributeDisplay
from equip.CangshengAttributeData import (
    CangshengAttributeData, calculate_attributes, get_profile, kungfu_data, make_base_attributes,
    profile_school, static_attributes,
)
from replayer.CombatTracker import BoostCounter
from tests.test_cangsheng_equipment import equipment_text


ROOT = Path(__file__).resolve().parents[1]
JCL = ROOT / '2026-10-06-22-24-47-25人普通洛阳之战(835)-史朝义(139312).jcl'
WUJIE = (
    '1dw', '1tw', '2dw', '2hw', '3dw', '3tw', '4pw', '4mw', '5dw', '5hw',
    '6dw', '6hw', '7pw', '7mw', '8w', '9w', '10dw', '10tw', '21dw', '21tw',
    '22dw', '22hw', '23w', '24w', '25w', '211w', '212dw', '212hw', '213w',
    '214w', '215w', '34w',
)
HEALERS = ('2hw', '5hw', '6hw', '22hw', '212hw')
TARGET = {'level': 53, 'shieldBase': {school: 6399 for school in
          ('Physics', 'Solar', 'Neutral', 'Lunar', 'Poison')}}


class WujieAttributeTests(unittest.TestCase):
    def test_all_current_wujie_profiles_have_their_own_skill_evidence(self):
        profiles = kungfu_data()['occupations']
        self.assertEqual({occ for occ in profiles if occ.endswith('w')}, set(WUJIE))
        self.assertEqual(len(profiles), 64)
        for occ in WUJIE:
            with self.subTest(occ=occ):
                wujie = get_profile(occ)
                normal = get_profile(occ[:-1])
                self.assertNotEqual(wujie['skill_id'], normal['skill_id'])
                self.assertGreater(wujie['skill_id'], 100000)
                self.assertEqual(wujie['skill_level'], 5)
                self.assertIn('悟', wujie['name'])
                self.assertTrue(wujie['raw_attributes'])
                self.assertTrue(static_attributes(occ))
                self.assertEqual(wujie['source']['evidence_root'], 'wujie_evidence')
                evidence = ROOT / 'equip/resources/cangshengtf/wujie_evidence/unpack_result'
                source = (evidence / wujie['source']['origin']).read_bytes()
                self.assertEqual(hashlib.sha256(source).hexdigest(), wujie['source']['sha256'])

    def test_portable_wujie_originals_match_their_manifest(self):
        evidence = ROOT / 'equip/resources/cangshengtf/wujie_evidence'
        manifest = json.loads((evidence / 'source_manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(manifest['files'])
        for row in manifest['files']:
            with self.subTest(origin=row['origin']):
                raw = (evidence / 'unpack_result' / row['origin']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
                self.assertEqual(len(raw), row['bytes'])

    def test_penglais_wujie_uses_its_actual_skill_and_unique_damage_bonuses(self):
        self.assertEqual(get_profile('24w')['skill_id'], 101090)
        raw = static_attributes('24w')
        for attribute, value in {'atPhysicsAttackPowerBase': 2662,
                                 'atPhysicsCriticalStrike': 147,
                                 'atAgilityToPhysicsAttackPowerCof': 707,
                                 'atAgilityToPhysicsCriticalStrikeCof': 61,
                                 'atDstNpcDamageCoefficient': 860,
                                 'atAllShieldIgnorePercent': 614}.items():
            self.assertEqual(raw[attribute], value, attribute)
        self.assertNotEqual(raw['atDstNpcDamageCoefficient'], static_attributes('24')['atDstNpcDamageCoefficient'])
        self.assertNotEqual(raw['atAllShieldIgnorePercent'], static_attributes('24').get('atAllShieldIgnorePercent', 0))

    def test_every_wujie_base_merges_real_kungfu_and_equipment_attributes(self):
        equipment = {'atVitalityBase': 100, 'atSpiritBase': 200,
                     'atSpunkBase': 300, 'atPhysicsAttackPowerBase': 400,
                     'atMagicAttackPowerBase': 500, 'atPVXAllRound': 600}
        general = {'atVitalityBase': 18, 'atStrengthBase': 17, 'atAgilityBase': 18,
                   'atSpiritBase': 18, 'atSpunkBase': 17, 'atMaxLifeBase': 3956}
        for occ in WUJIE:
            with self.subTest(occ=occ):
                static = static_attributes(occ)
                base = make_base_attributes(equipment, occ)
                for attribute in set(equipment) | set(general) | set(static):
                    if occ == '34w' and attribute in ('atStrengthBase', 'atAgilityBase', 'atSpunkBase', 'atSpiritBase'):
                        # Equipment contributes 200 spirit plus its winning 300
                        # spunk; the role's naked stats are added afterwards.
                        expected = {'atStrengthBase': 17, 'atAgilityBase': 18,
                                    'atSpunkBase': 17, 'atSpiritBase': 518}[attribute]
                    else:
                        expected = equipment.get(attribute, 0) + general.get(attribute, 0) + static.get(attribute, 0)
                    self.assertEqual(base['_raw'][attribute], expected)
                panel = calculate_attributes(base['_raw'], occ)
                self.assertTrue(all(math.isfinite(value) for value in panel.values()
                                    if isinstance(value, (int, float))))
                self.assertGreater(panel['攻击'] + panel['治疗'], 0)

    def test_current_wujie_healer_original_values(self):
        for occ, therapy, spirit, critical in (
                ('2hw', 6367, 686, 82), ('5hw', 6822, 727, 41),
                ('6hw', 6595, 768, 0), ('22hw', 7049, 707, 61),
                ('212hw', 7049, 748, 20)):
            with self.subTest(occ=occ):
                raw = static_attributes(occ)
                self.assertEqual(raw['atTherapyPowerBase'], therapy)
                self.assertEqual(raw['atSpiritToTherapyPowerCof'], spirit)
                panel = calculate_attributes(dict(raw, atSpiritBase=1024), occ)
                self.assertEqual(panel['治疗'], therapy + spirit)
                self.assertEqual(panel['会心等级'], 256 + critical)

    def test_wujie_healers_convert_allround_to_therapy(self):
        for occ in HEALERS:
            with self.subTest(occ=occ):
                panel = calculate_attributes({'atPVXAllRound': 1000}, occ)
                self.assertEqual(panel['治疗'], 150)
                self.assertEqual(panel['无双等级'], 0)
        panel = calculate_attributes({'atPVXAllRound': 1000}, '24w')
        self.assertEqual(panel['治疗'], 0)
        self.assertEqual(panel['无双等级'], 1220)

    def test_mingzun_wujie_defaults_to_solar_and_keeps_lunar_conversion(self):
        self.assertEqual(profile_school('10tw'), 'Solar')
        raw = static_attributes('10tw')
        self.assertEqual(raw['atVitalityToSolarAttackPowerCof'], 163)
        self.assertEqual(raw['atVitalityToLunarAttackPowerCof'], 163)
        attributes = dict(raw, atVitalityBase=1024,
                          atSolarAttackPowerBase=100, atLunarAttackPowerBase=200)
        self.assertEqual(calculate_attributes(attributes, '10tw')['攻击'], 263)
        self.assertEqual(calculate_attributes(attributes, '10tw', school='Lunar')['攻击'], 363)

    def test_mingzun_wujie_attributes_lunar_events_to_lunar_boost(self):
        base = {'_raw': {'atSolarAttackPowerBase': 1000, 'atLunarAttackPowerBase': 1000}}
        counter = BoostCounter('self', '10tw', 0, 10000, base,
                               gameEdition=160, targetProfiles={'boss': TARGET})
        counter.addBoost('lunar', {'atLunarAttackPowerPercent': 1024}, 'other', 1, 0)
        event = SimpleNamespace(target='boss', full_id='1,1,1', fullResult={'3': 100})
        rate = counter.getRateForEvent(event, 'damage')
        self.assertAlmostEqual(rate['lunar']['rate'], .5)
        self.assertAlmostEqual(rate['self']['rate'], .5)
        self.assertAlmostEqual(sum(value['rate'] for value in rate.values()), 1)
        solar = counter.getRate('boss', '1,1,1', 'damage', 'Solar')
        self.assertEqual(solar, {'self': {'source': 'self', 'rate': 1}})

    def test_wuxiang_wujie_lunar_panel_uses_its_own_profile(self):
        self.assertEqual(profile_school('34w'), 'Lunar')
        raw = static_attributes('34w')
        self.assertEqual(raw['atMagicAttackPowerBase'], 2611)
        self.assertEqual(raw['atMagicShield'], 444)
        self.assertEqual(raw['atSpiritToLunarAttackPowerCof'], 717)
        self.assertEqual(raw['atSpiritToLunarCriticalStrikeCof'], 51)
        self.assertEqual(raw['atDstNpcDamageCoefficient'], 860)
        self.assertEqual(raw['atAllShieldIgnorePercent'], 614)
        self.assertEqual(static_attributes('34')['atDstNpcDamageCoefficient'], 471)
        panel = calculate_attributes(dict(raw, atSpiritBase=1024), '34w')
        self.assertEqual(panel['攻击'], 2611 + 717)
        self.assertEqual(panel['会心等级'], 34 + 256 + 51)
        gear = equipment_text({'12': [111692, 0, 0, 0, 0, 0, 0, 0]})
        displayed = AttributeDisplay(160).GetPanelAttrib(gear, '34w')
        self.assertIsNotNone(displayed)
        self.assertEqual(displayed['类型'], 3)
        self.assertGreater(displayed['攻击'], 2611)

    def test_unknown_wujie_profile_is_not_silently_replaced(self):
        with self.assertRaises(ValueError):
            get_profile('unknown-w')

    def test_youluo_converts_equipment_primary_only_before_naked_stats(self):
        gear = {'atStrengthBase': 100, 'atSpunkBase': 300,
                'atAgilityBase': 200, 'atSpiritBase': 70}
        for occ in ('34', '34w'):
            with self.subTest(occ=occ):
                base = make_base_attributes(gear, occ)
                self.assertEqual(base['_raw']['atSpiritBase'], 388)
                self.assertEqual(base['_raw']['atStrengthBase'], 17)
                self.assertEqual(base['_raw']['atSpunkBase'], 17)
                self.assertEqual(base['_raw']['atAgilityBase'], 18)
                naked = calculate_attributes(dict(gear, atAdaptAttributeType=1), occ)
                self.assertEqual(naked['根骨'], 70)
                self.assertEqual(naked['力道'], 100)
                self.assertEqual(naked['元气'], 300)
                self.assertEqual(naked['身法'], 200)
        self.assertEqual(gear['atSpunkBase'], 300)

    def test_youluo_chooses_the_largest_attack_source_with_weapon_damage(self):
        raw = {'atAdaptAttributeType': 1, 'atLunarAttackPowerBase': 100,
               'atSolarAttackPowerBase': 200, 'atNeutralAttackPowerBase': 300,
               'atPoisonAttackPowerBase': 400, 'atPhysicsAttackPowerBase': 500,
               'atMeleeWeaponDamageBase': 10, 'atMeleeWeaponDamageRand': 4}
        original = raw.copy()
        self.assertEqual(calculate_attributes(raw, '34w')['攻击'], 672)
        self.assertEqual(raw, original)
        raw['atPhysicsAttackPowerBase'] = 100
        self.assertEqual(calculate_attributes(raw, '34w')['攻击'], 500)

    def test_youluo_chooses_each_rating_source_independently(self):
        raw = {'atAdaptAttributeType': 1, 'atLunarCriticalStrike': 10,
               'atSolarCriticalStrike': 20, 'atNeutralCriticalStrike': 40,
               'atPoisonCriticalStrike': 30, 'atPhysicsCriticalStrike': 60,
               'atLunarOvercomeBase': 7, 'atSolarOvercomeBase': 11,
               'atNeutralOvercomeBase': 30, 'atPoisonOvercomeBase': 20,
               'atPhysicsOvercomeBase': 5, 'atLunarCriticalDamagePowerBase': 13,
               'atSolarCriticalDamagePowerBase': 31, 'atNeutralCriticalDamagePowerBase': 21,
               'atPoisonCriticalDamagePowerBase': 51, 'atPhysicsCriticalDamagePowerBase': 61}
        panel = calculate_attributes(raw, '34w')
        self.assertEqual(panel['会心等级'], 70)
        self.assertEqual(panel['破防等级'], 37)
        self.assertEqual(panel['会心效果等级'], 74)

    def test_youluo_boost_removal_reselects_the_original_winning_source(self):
        raw = {'atAdaptAttributeType': 1, 'atLunarAttackPowerBase': 100,
               'atSolarAttackPowerBase': 200, 'atPoisonAttackPowerBase': 300}
        calculator = CangshengAttributeData('34w')
        calculator.baseAttrib = {'_raw': raw.copy()}
        solar = {'atSolarAttackPowerBase': 200}
        poison = {'atPoisonAttackPowerBase': 200}
        calculator.setBoosts([solar])
        self.assertEqual(calculator.getFinalAttrib()['攻击'], 500)
        self.assertEqual(calculator.addBoostAndGetAttrib(poison)['攻击'], 600)
        self.assertEqual(calculator.removeBoostAndGetAttrib(poison)['攻击'], 500)
        self.assertEqual(calculator.removeBoostAndGetAttrib(solar)['攻击'], 400)
        self.assertEqual(calculator.baseAttrib['_raw'], raw)

    def test_youluo_attribution_tracks_the_winning_external_source(self):
        base = {'_raw': {'atAdaptAttributeType': 1, 'atLunarAttackPowerBase': 100,
                        'atSolarAttackPowerBase': 200, 'atPoisonAttackPowerBase': 300}}
        counter = BoostCounter('self', '34w', 0, 10000, base,
                               gameEdition=160, targetProfiles={'boss': TARGET})
        counter.addBoost('solar', {'atSolarAttackPowerBase': 200}, 'a', 1, 0)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Lunar')
        self.assertAlmostEqual(rates['solar']['rate'], .2)
        counter.addBoost('poison', {'atPoisonAttackPowerBase': 200}, 'b', 1, 100)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Lunar')
        self.assertNotIn('solar', rates)
        self.assertAlmostEqual(rates['poison']['rate'], 1 / 3)
        counter.removeBoost('poison', 200)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Lunar')
        self.assertNotIn('poison', rates)
        self.assertAlmostEqual(rates['solar']['rate'], .2)
        counter.removeBoost('solar', 300)
        self.assertEqual(counter.getRate('boss', '1,1,1', 'damage', 'Lunar'),
                         {'self': {'source': 'self', 'rate': 1}})


class FakeWidget(dict):
    def configure(self, **values):
        self.update(values)

    def bind(self, *args):
        pass


class WujieCombatWindowTests(unittest.TestCase):
    def test_wujie_bars_select_existing_school_color_styles(self):
        from window.CombatTrackerWindow import CombatTrackerWindow
        for occ, school in (('24w', '24'), ('2hw', '2'), ('34w', '34')):
            with self.subTest(occ=occ):
                window = CombatTrackerWindow.__new__(CombatTrackerWindow)
                window.act = SimpleNamespace(ndps={'player': {'p': dict(name='测试', occ=occ,
                                                                       sumPerSec=100, dps=100)}})
                window.rightTitle = FakeWidget()
                window.bars = [[FakeWidget(), FakeWidget(), FakeWidget(), ''] for _ in range(30)]
                window.highlightPlayer = ''
                window.setPlayer = lambda *args: None
                window.setStat('ndps')
                self.assertEqual(window.bars[0][1]['style'], 'bar%s.Horizontal.TProgressbar' % school)


@unittest.skipUnless(JCL.exists(), 'Optional original user JCL is absent')
class WujieWholeLogTests(unittest.TestCase):
    def test_user_log_finishes_and_retains_wujie_damage(self):
        from tools.ValidateLuoyang import replay
        with patch('socket.socket.connect', side_effect=AssertionError('Network disabled in validation')):
            with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'):
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(JCL, healers=True)
        self.assertEqual(actor.occDetailList['2994'], '24w')
        self.assertEqual(actor.bld.info.player['2994'].xinfaCode, '101090')
        self.assertIsNotNone(actor.baseAttribDict['2994'])
        self.assertFalse(actor.baseAttribDict['2994'].get('_warnings'))
        self.assertFalse(actor.panelAttribDict['2994'].get('_warnings'))
        self.assertIn('2994', actor.combatTracker.boostCounter)
        self.assertIn(actor.bld.info.player['2994'].name, actor.occResult)
        names = {player.name for player in actor.bld.info.player.values()}
        self.assertEqual(len(names), 25)
        self.assertEqual(len(actor.statDict), 25)
        self.assertEqual({row['name'] for row in actor.statDict}, names)
        self.assertEqual(set(actor.occResult), names)
        self.assertTrue(all(base is not None for base in actor.baseAttribDict.values()))
        unresolved = {target for counter in actor.combatTracker.boostCounter.values()
                      for target in counter.unresolvedTargets}
        self.assertFalse(unresolved)
        warnings = {player: base['_warnings'] for player, base in actor.baseAttribDict.items()
                    if base.get('_warnings')}
        if warnings:
            # This original log has one independently unsupported ordinary
            # Cangjian weapon recipe; never hide it to declare rDPS supported.
            self.assertEqual(warnings, {'2836': ['装备8,23766词条17121: atSetEquipmentRecipe']})
            self.assertEqual(actor.occDetailList['2836'], '8')
            self.assertEqual(actor.combatTracker.rdpsStatus['status'], 'incomplete')
            self.assertEqual(actor.combatTracker.rdpsStatus['reason'],
                             '部分玩家装备或当前地图首领属性缺少验证数据。')
        else:
            self.assertEqual(actor.combatTracker.rdpsStatus['status'], 'supported')
        raw_damage = 0
        for event in actor.bld.log:
            if event.dataType != 'Skill' or event.caster != '2994' or not actor.startTime <= event.time <= actor.finalTime:
                continue
            if event.damageEff <= 0 or event.target not in actor.bld.info.npc or event.id in ('35990', '36026', '36735', '36734'):
                continue
            excluded = next((state for time, state in reversed(actor.bh.badPeriodDpsLog) if event.time > time), 0)
            if not excluded:
                raw_damage += event.damageEff
        self.assertGreater(raw_damage, 0)
        self.assertEqual(raw_damage, 17753129)
        self.assertEqual(actor.combatTracker.ndpsCast['2994'].sum, raw_damage)
        self.assertGreater(actor.combatTracker.getRdps('2994'), 0)


if __name__ == '__main__':
    unittest.main()

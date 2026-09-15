"""Formula and attribution regressions for current raw client attributes."""
import unittest
from types import SimpleNamespace

from equip.CangshengAttributeData import (
    CangshengAttributeData, calculate_attributes, make_base_attributes, static_attributes,
)
from replayer.CombatTracker import BoostCounter, getDamageCoeff
from tools.Attribute import COEFF50
from equip.AttributeDisplay import AttributeDisplay


PROFILE = {'level': 53, 'shieldBase': {school: 6399 for school in
           ('Physics', 'Solar', 'Neutral', 'Lunar', 'Poison')}}


class CangshengAttributeTests(unittest.TestCase):
    def test_base_rate_adds_six_percentage_points_at_zero_parry(self):
        panel = calculate_attributes({'atParryBaseRate': 600}, '21t')
        self.assertAlmostEqual(panel['招架'], .09)
        self.assertEqual(panel['招架等级'], 0)

    def test_dodge_and_toughness_base_rates_are_direct(self):
        panel = calculate_attributes({'atDodgeBaseRate': 3000, 'atToughnessBaseRate': 500}, '10t')
        self.assertAlmostEqual(panel['闪避'], .3)
        self.assertAlmostEqual(panel['御劲'], .05)

    def test_lijing_level_five_uses_original_lua(self):
        raw = static_attributes('2h')
        self.assertEqual(raw['atTherapyPowerBase'], 6367)
        panel = calculate_attributes(dict(raw, atSpiritBase=1024), '2h')
        self.assertEqual(panel['治疗'], 6367 + 686)
        self.assertEqual(panel['会心等级'], 256 + 82)

    def test_therapy_conversion_reads_completed_primary_conversion(self):
        raw = {'atTherapyPowerBase': 1000, 'atSpiritBase': 200,
               'atSpiritToTherapyPowerCof': 512, 'atTherapyPowerToPoisonAttackPowerCof': 1024}
        panel = calculate_attributes(raw, '212h')
        self.assertEqual(panel['治疗'], 1100)
        self.assertEqual(panel['攻击'], 1100)

    def test_secondary_conversion_does_not_recursively_amplify(self):
        raw = {'atNeutralAttackPowerBase': 100, 'atTherapyPowerBase': 200,
               'atNeutralAttackPowerToTherapyPowerCof': 1024,
               'atTherapyPowerToNeutralAttackPowerCof': 1024}
        panel = calculate_attributes(raw, '2h')
        self.assertEqual(panel['治疗'], 300)
        self.assertEqual(panel['攻击'], 400)

    def test_attack_to_therapy_uses_named_source_school(self):
        raw = {'atPhysicsAttackPowerBase': 100, 'atPoisonAttackPowerBase': 1000,
               'atNeutralAttackPowerBase': 500, 'atPoisonAttackPowerToTherapyPowerCof': 1024,
               'atNeutralAttackPowerToTherapyPowerCof': 512}
        for school in ('Physics', 'Poison', 'Neutral'):
            self.assertEqual(calculate_attributes(raw, '212h', school=school)['治疗'], 1250)

    def test_empty_equipment_rows_do_not_create_guessed_panel(self):
        text = '\n'.join('\t'.join(['0'] * 8) for _ in range(13))
        self.assertIsNone(AttributeDisplay(160).GetPanelAttrib(text, '6h'))

    def test_unknown_equipment_script_is_visible_and_marks_incomplete(self):
        from tests.test_cangsheng_equipment import equipment_text
        display = AttributeDisplay(160)
        panel = display.GetPanelAttrib(equipment_text({'12': [111692, 0, 11272, 0, 0, 0, 0, 0]}), '6h')
        self.assertEqual(display.status['status'], 'incomplete')
        self.assertEqual(panel['_warnings'], ['附魔11272: atExecuteScript'])

    def test_same_kungfu_can_calculate_both_logged_damage_schools(self):
        raw = {'atSolarAttackPowerBase': 100, 'atLunarAttackPowerBase': 200,
               'atVitalityBase': 1024, 'atVitalityToSolarAttackPowerCof': 300}
        self.assertEqual(calculate_attributes(raw, '10t', school='Solar')['攻击'], 400)
        self.assertEqual(calculate_attributes(raw, '10t', school='Lunar')['攻击'], 200)

    def test_percentage_is_applied_to_base_before_kungfu_extra(self):
        raw = {'atPhysicsAttackPowerBase': 1000, 'atStrengthBase': 1000,
               'atPhysicsAttackPowerPercent': 1024, 'atStrengthToPhysicsAttackPowerCof': 512}
        self.assertEqual(calculate_attributes(raw, '3d')['攻击'], (1000 + 195) * 2 + 500)

    def test_allround_uses_healer_and_damage_branches(self):
        raw = {'atPVXAllRound': 1000}
        healer = calculate_attributes(raw, '2h')
        damage = calculate_attributes(raw, '2d')
        self.assertEqual(healer['治疗'], 150)
        self.assertEqual(healer['无双'], 0)
        self.assertAlmostEqual(damage['无双'], 1220 / COEFF50['无双'])

    def test_boost_recalculation_retains_percent_when_base_was_zero(self):
        calculator = CangshengAttributeData('3d')
        calculator.baseAttrib = {'_raw': {'atPhysicsAttackPowerPercent': 1024}}
        calculator.setBoosts([{'atPhysicsAttackPowerBase': 100}])
        self.assertEqual(calculator.getFinalAttrib()['攻击'], 200)
        self.assertEqual(calculator.removeBoostAndGetAttrib({'atPhysicsAttackPowerBase': 100})['攻击'], 0)
        self.assertEqual(calculator.addBoostAndGetAttrib({'atPhysicsAttackPowerBase': 100})['攻击'], 200)

    def test_npc_coefficient_and_unlimited_critical_are_independent(self):
        raw = {'atPhysicsAttackPowerBase': 100, 'atPhysicsCriticalStrikeBaseRate': 10000,
               'atCriticalDamagePowerBase': COEFF50['会心效果'] * 5}
        plain = calculate_attributes(raw, '3d')
        boosted = calculate_attributes(dict(raw, atDstNpcDamageCoefficient=1024,
                                           atUnlimitCriticalDamagePowerKiloNumRate=512), '3d')
        a = getDamageCoeff('3d', plain, [], isSangRou=0, gameEdition=160, targetProfile=PROFILE)
        b = getDamageCoeff('3d', boosted, [], isSangRou=0, gameEdition=160, targetProfile=PROFILE)
        self.assertAlmostEqual(b / a, 2 * 3.5 / 3)

    def counter(self):
        base = {'_raw': {'atSolarAttackPowerBase': 1000, 'atLunarAttackPowerBase': 1000}}
        return BoostCounter('self', '10t', 0, 10000, base, gameEdition=160, targetProfiles={'boss': PROFILE})

    def test_mixed_school_attribution_matches_weighted_results(self):
        counter = self.counter()
        counter.addBoost('buff', {'atSolarAttackPowerPercent': 1024}, 'healer', 1, 0)
        event = SimpleNamespace(target='boss', full_id='1,1,1', fullResult={'1': 25, '3': 75})
        mixed = counter.getRateForEvent(event, 'damage')
        self.assertAlmostEqual(mixed['buff']['rate'], .125)
        self.assertAlmostEqual(mixed['self']['rate'], .875)
        self.assertEqual(len(counter.rdpsRate['boss']), 2)

    def test_negative_boost_does_not_receive_positive_credit(self):
        counter = self.counter()
        counter.addBoost('bad', {'atSolarAttackPowerPercent': -512}, 'other', 1, 0)
        result = counter.getRate('boss', '1,1,1', 'damage', 'Solar')
        self.assertEqual(result, {'self': {'source': 'self', 'rate': 1}})

    def test_missing_npc_is_recorded_instead_of_assuming_main_boss(self):
        counter = self.counter()
        counter.getRate('unknown', '1,1,1', 'damage')
        self.assertEqual(counter.unresolvedTargets, {'unknown'})

    def test_missing_equipment_does_not_mislabel_known_npc(self):
        counter = self.counter()
        counter.attributeData.baseAttrib = None
        counter.getRate('boss', '1,1,1', 'damage')
        self.assertEqual(counter.unresolvedTargets, set())

    def test_same_buff_two_sources_keep_separate_credit_and_canonical_name(self):
        counter = self.counter()
        a, b = ('2,1,1', 'slot', '1'), ('2,1,1', 'slot', '2')
        counter.addBoost('2,1,1', {'atSolarAttackPowerPercent': 512}, 'a', 1, 0, instance=a)
        counter.addBoost('2,1,1', {'atSolarAttackPowerPercent': 512}, 'b', 1, 0, instance=b)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Solar')
        self.assertEqual((rates[a]['source'], rates[b]['source']), ('a', 'b'))
        self.assertEqual(rates[a]['id'], '2,1,1')
        self.assertAlmostEqual(sum(value['rate'] for value in rates.values()), 1)
        counter.removeBoost('2,1,1', 1000, instance=a)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Solar')
        self.assertNotIn(a, rates)
        self.assertAlmostEqual(rates[b]['rate'], 1 / 3)

    def test_observed_instance_replaces_inferred_pre_pull_copy(self):
        counter = self.counter()
        effect = {'atSolarAttackPowerPercent': 1024}
        counter.addBoost('2,1,1', effect, 'healer', 1, 0)
        counter.addBoost('2,1,1', effect, 'healer', 1, 100, instance=('2,1,1', 'slot', '1'))
        self.assertEqual(len(counter.boost), 1)
        rates = counter.getRate('boss', '1,1,1', 'damage', 'Solar')
        self.assertAlmostEqual(rates['self']['rate'], .5)

    def test_changed_zyhr_provider_invalidates_cached_attribution(self):
        counter = self.counter()
        counter.setSpecificSkill('zyhr', 'a')
        rate = counter.getRate('boss', '1,29532,1', '逐云寒蕊', 'Solar')
        self.assertEqual(rate['1,29532,1']['source'], 'a')
        counter.setSpecificSkill('zyhr', 'b')
        rate = counter.getRate('boss', '1,29532,1', '逐云寒蕊', 'Solar')
        self.assertEqual(rate['1,29532,1']['source'], 'b')


if __name__ == '__main__':
    unittest.main()

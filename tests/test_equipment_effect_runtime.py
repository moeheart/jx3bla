"""Analytical rDPS checks for personal equipment attributes and external buffs.

These fixtures test the attribution algebra independently of any particular
equipment script. An actual script/recipe must still establish which raw
attribute, skill, level and lifetime it supplies before using this mechanism.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from replayer.CombatTracker import BoostCounter
from equip.EquipmentEffects import resolve_equipment_effects
from replayer import Name
from release.NameGenerator import parse_buff
from data.DataContent import SingleDataSkill, SingleDataBuff
from tests import test_target_boost_sources as source_fixtures


PROFILE = {"level": 53, "shieldBase": {school: 6399 for school in
           ("Physics", "Solar", "Lunar", "Neutral", "Poison")}}
EVIDENCE = Path(__file__).resolve().parents[1] / 'docs/160/evidence/equipment_effects'


class EquipmentEffectAttributionTests(unittest.TestCase):
    def counter(self, raw=None):
        base = {"_raw": raw or {"atPhysicsAttackPowerBase": 1000}}
        return BoostCounter("owner", "3d", 0, 10000, baseAttribute=base,
                            targetProfiles={"boss": PROFILE})

    def rates(self, counter):
        return counter.getRate("boss", "1,999,1", "测试伤害", "Physics")

    def test_personal_flat_attack_stays_with_owner_and_changes_external_share(self):
        counter = self.counter()
        original = deepcopy(counter.attributeData.baseAttrib)
        counter.addBoost("equipment", {"atPhysicsAttackPowerBase": 100}, "owner", 1, 0)
        counter.addBoost("external", {"atPhysicsAttackPowerBase": 200}, "provider", 1, 0)
        rates = self.rates(counter)
        # Damage is proportional to 1100 AP alone, 1300 AP with the provider.
        self.assertAlmostEqual(rates["self"]["rate"], 1100/1300)
        self.assertAlmostEqual(rates["external"]["rate"], 200/1300)
        self.assertNotIn("equipment", rates)
        self.assertEqual(counter.attributeData.baseAttrib, original)
        self.assertAlmostEqual(sum(row["rate"] for row in rates.values()), 1)

    def test_personal_critical_chance_can_saturate_external_critical_uplift(self):
        counter = self.counter({"atPhysicsAttackPowerBase": 1000,
                                "atPhysicsCriticalStrikeBaseRate": 9000})
        counter.addBoost("equipment", {"atPhysicsCriticalStrikeBaseRate": 1000}, "owner", 1, 0)
        counter.addBoost("external", {"atPhysicsCriticalStrikeBaseRate": 1000}, "provider", 1, 0)
        self.assertEqual(self.rates(counter), {"self": {"source": "owner", "rate": 1.0}})
        counter.removeBoost("equipment", 1000)
        rates = self.rates(counter)
        # Default critical damage is 1.75: expectation rises from 1.675 to 1.75.
        self.assertAlmostEqual(rates["self"]["rate"], 1.675/1.75)
        self.assertAlmostEqual(rates["external"]["rate"], 0.075/1.75)

    def test_personal_damage_attribute_uses_its_shared_additive_pool(self):
        counter = self.counter()
        counter.addBoost("equipment", {"atAllPhysicsDamageAddPercent": 512}, "owner", 1, 0)
        counter.addBoost("external", {"atAllPhysicsDamageAddPercent": 256}, "provider", 1, 0)
        rates = self.rates(counter)
        self.assertAlmostEqual(rates["self"]["rate"], 1.5/1.75)
        self.assertAlmostEqual(rates["external"]["rate"], 0.25/1.75)
        # Incorrectly treating the equipment effect as a separate multiplier
        # would leave the external share at 0.25/1.25 instead.
        self.assertNotAlmostEqual(rates["external"]["rate"], 0.25/1.25)

    def test_personal_buff_removal_invalidates_cached_attribution(self):
        counter = self.counter()
        counter.addBoost("equipment", {"atPhysicsAttackPowerBase": 100}, "owner", 1, 0,
                         instance=("equipment", "slot", "7"))
        counter.addBoost("external", {"atPhysicsAttackPowerBase": 200}, "provider", 1, 0)
        self.assertAlmostEqual(self.rates(counter)["self"]["rate"], 1100/1300)
        counter.removeBoost("equipment", 1000, instance=("equipment", "slot", "7"))
        self.assertAlmostEqual(self.rates(counter)["self"]["rate"], 1000/1200)

    def script(self, filename, value2='0'):
        return {'type': 'atExecuteScript', 'value1': 'skill/装备/' + filename,
                'value2': value2, 'source': 'enchant', 'warning': 'unmodeled enchant'}

    def test_exact_clothing_passive_dilutes_external_attack_without_double_damage(self):
        effect = self.script('苍生铸世赛季输出衣服附魔_1110.lua')
        resolved, warnings, raw = resolve_equipment_effects([effect], '3d')
        self.assertFalse(warnings)
        self.assertEqual(resolved[0]['handling'], 'static_attributes')
        self.assertEqual(raw, {'atAllTypeAttackPowerBase': 81, 'atBeTherapyCoefficient': -102})
        counter = self.counter(dict(raw, atPhysicsAttackPowerBase=1000))
        counter.addBoost('external', {'atPhysicsAttackPowerBase': 200}, 'provider', 1, 0)
        rates = self.rates(counter)
        self.assertAlmostEqual(rates['self']['rate'], 1081/1281)
        self.assertAlmostEqual(rates['external']['rate'], 200/1281)

    def test_damage_hat_uses_logged_overcome_and_healer_hat_has_no_panel_bonus(self):
        for filename, handling in (
                ('苍生铸世赛季输出帽子附魔_1110.lua', 'logged_event'),
                ('帽子_新附魔_治疗非战斗附魔减读条.lua', 'non_combat')):
            with self.subTest(filename=filename):
                resolved, warnings, raw = resolve_equipment_effects([self.script(filename)], '3d')
                self.assertFalse(warnings)
                self.assertEqual(raw, {})
                self.assertEqual(resolved[0]['handling'], handling)
        self.assertEqual(Name.BOOST_DICT['2,15436,18'], {'atAllTypeOvercomeBase': 81})

    def test_unverified_script_parameter_and_platform_preserve_warning(self):
        known = self.script('苍生铸世赛季输出衣服附魔_1110.lua')
        for effect, occ in ((dict(known, value2='18'), '3d'),
                            (self.script('unknown.lua'), '3d'), (known, '3dw')):
            with self.subTest(effect=effect, occ=occ):
                self.assertEqual(resolve_equipment_effects([effect], occ),
                                 ([], {effect['warning']}, {}))

    def test_portable_script_sources_keep_version_and_exact_hashes(self):
        manifest = json.loads((EVIDENCE/'script-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['clientVersion'], '1.6.0.10072')
        self.assertEqual(manifest['archivedTableReference'], '1.6.0.10009')
        self.assertEqual(len(manifest['files']), 6)
        for entry in manifest['files']:
            self.assertEqual(entry['clientVersion'], '1.6.0.10072')
            for key, digest in (('rawPath', 'sha256'), ('readablePath', 'readableSha256')):
                path = EVIDENCE / entry[key]
                self.assertFalse(Path(entry[key]).is_absolute())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry[digest])

    def event_rates(self, counter, full_id='1,37561,1', school='0'):
        event = SimpleNamespace(full_id=full_id, target='boss', fullResult={school: '10000'})
        return counter.getRateForEvent(event, '附魔伤害')

    def test_fixed_proc_does_not_export_ordinary_attack_or_target_boosts(self):
        for identifier in ('1,37561,1', '1,37562,1'):
            for school in ('0', '1', '2', '3', '4'):
                with self.subTest(identifier=identifier, school=school):
                    counter = self.counter()
                    counter.addBoost('external', {'atAllTypeAttackPowerBase': 200,
                        'atAllTypeCriticalStrike': 3000, 'atAllTypeOvercomeBase': 3000,
                        'atStrainRate': 256, 'atAllDamageAddPercent': 256,
                        'atDstNpcDamageCoefficient': 256}, 'provider', 1, 0)
                    counter.addTargetBoost('boss', 'vulnerable',
                        {'atPhysicsDamageCoefficient': 256, 'atPhysicsShieldAdditional': -1000},
                        'provider', 1, 0)
                    rates = self.event_rates(counter, identifier, school)
                    self.assertEqual(set(rates), {'self'})
                    self.assertEqual(rates['self']['rate'], 1)

    def test_fixed_proc_respects_exact_scheme_id_level_and_separate_cache(self):
        counter = self.counter()
        counter.addBoost('attack', {'atPhysicsAttackPowerBase': 200}, 'provider', 1, 0)
        for identifier in ('1,37560,1', '1,37563,1', '2,37561,1', '1,37561,2',
                           '1,37562,2', '1,999,1'):
            with self.subTest(identifier=identifier):
                self.assertAlmostEqual(self.event_rates(counter, identifier)['attack']['rate'], 1/6)
                self.assertEqual(self.event_rates(counter)['self']['rate'], 1)
        counter.removeBoost('attack', 100)
        self.assertEqual(self.event_rates(counter)['self']['rate'], 1)

    def test_real_jcl_skill_identity_reaches_fixed_path_and_malformed_ids_do_not(self):
        counter = self.counter()
        counter.addBoost('attack', {'atPhysicsAttackPowerBase': 200}, 'provider', 1, 0)
        for identifier in ('37561', '37562'):
            event = SingleDataSkill()
            event.setByJcl(['', '16', '1793577600', '1000', '21',
                {'1': 'owner', '2': 'boss', '4': '1', '5': identifier,
                 '6': '1', '9': {'0': '10000', '13': '9999'}}])
            self.assertEqual(event.full_id, '"1,%s,1"' % identifier)
            rates = counter.getRateForEvent(event, '附魔伤害')
            self.assertEqual(set(rates), {'self'})
            self.assertEqual(rates['self']['rate'], 1)
        for bad in ('"1,37561,1', '1,37561,1"', '""1,37561,1""', '"1,37561,2"'):
            self.assertAlmostEqual(self.event_rates(counter, bad)['attack']['rate'], 1/6)

    def test_fixed_proc_harmful_and_zero_final_pools_do_not_create_positive_credit(self):
        for base, external, expected in ((-512, 256, 2/3), (0, -256, 1),
                                         (0, -1024, 1), (-1024, 256, 0)):
            with self.subTest(base=base, external=external):
                counter = self.counter({'atPhysicsAttackPowerBase': 1000,
                                        'atActivityDamageFinalCof': base})
                counter.addBoost('external', {'atActivityDamageFinalCof': external}, 'provider', 1, 0)
                rates = self.event_rates(counter)
                self.assertAlmostEqual(rates['self']['rate'], expected)
                self.assertAlmostEqual(sum(row['rate'] for row in rates.values()), 1)
                self.assertTrue(all(row['rate'] >= 0 for row in rates.values()))

    def test_fixed_proc_keeps_both_final_pools_and_personal_dilution(self):
        counter = self.counter({'atPhysicsAttackPowerBase': 1000, 'atGamePlayDamageFinalCof': 256})
        counter.addBoost('equipment', {'atActivityDamageFinalCof': 512}, 'owner', 1, 0)
        counter.addBoost('game', {'atGamePlayDamageFinalCof': 256}, 'provider', 1, 0)
        counter.addBoost('activity', {'atActivityDamageFinalCof': 256}, 'provider2', 1, 0)
        rates = self.event_rates(counter)
        # Self 1.25*1.5; all 1.5*1.75. Marginal uplifts are .25*1.75
        # and 1.5*.25; the existing attribution normalization conserves damage.
        self.assertAlmostEqual(rates['self']['rate'], 1.875/2.625)
        self.assertAlmostEqual(rates['game']['rate'], (.4375/.8125)*(1-1.875/2.625))
        self.assertAlmostEqual(rates['activity']['rate'], (.375/.8125)*(1-1.875/2.625))
        self.assertAlmostEqual(sum(row['rate']*10000 for row in rates.values()), 10000)
        self.assertNotIn('equipment', rates)
        counter.removeBoost('game', 100)
        counter.removeBoost('activity', 100)
        self.assertEqual(self.event_rates(counter)['self']['rate'], 1)

    def test_final_pools_are_generated_from_buff_source_and_apply_to_normal_damage(self):
        row = {'ID': '1', 'Level': '1', 'BeginAttrib1': 'atGamePlayDamageFinalCof',
               'BeginValue1A': '256', 'BeginAttrib2': 'atActivityDamageFinalCof', 'BeginValue2A': '512'}
        self.assertEqual(parse_buff(row)[1], {'atGamePlayDamageFinalCof': 256,
                                            'atActivityDamageFinalCof': 512})
        self.assertEqual(Name.BOOST_DICT['2,3220,10']['atActivityDamageFinalCof'], 51)
        counter = self.counter()
        unchanged = deepcopy(self.rates(counter))
        counter.addBoost('zero', {'atGamePlayDamageFinalCof': 0, 'atActivityDamageFinalCof': 0}, 'provider', 1, 0)
        self.assertEqual(self.rates(counter), unchanged)
        counter.addBoost('final', {'atGamePlayDamageFinalCof': 256, 'atActivityDamageFinalCof': 512}, 'provider', 1, 0)
        self.assertAlmostEqual(self.rates(counter)['self']['rate'], 1/1.875)
        self.assertAlmostEqual(self.event_rates(counter)['self']['rate'], 1/1.875)

    def test_real_buff_and_skill_pipeline_conserves_damage_and_expires_final_credit(self):
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        buff = SingleDataBuff()
        buff.setByJcl(['', '16', '1793577600', '1000', '13',
            {'1': 'self', '2': 'false', '3': '5', '4': 'true', '5': '3220',
             '6': '1', '7': '32', '9': '10', '10': 'fs', '11': 'true'}])
        tracker.recordBuff(buff)
        tracker.boostCounter['self'].addBoost('ap', {'atPhysicsAttackPowerBase': 1000}, 'tg', 1, 1000)
        for time in (1000, 2000):
            skill = SingleDataSkill()
            skill.setByJcl(['', '16', '1793577600', str(time), '21',
                {'1': 'self', '2': 'boss', '4': '1', '5': '37561', '6': '1',
                 '9': {'0': '10750', '13': '10750'}}])
            tracker.recordSkill(skill)
        self.assertEqual(tracker.rdpsCast['tg'].skill, {})
        self.assertAlmostEqual(sum(row['sum'] for row in tracker.rdpsCast['fs'].skill.values()), 510)
        for recorders in (tracker.rdpsCast, tracker.mrdpsCast):
            self.assertAlmostEqual(sum(row['sum'] for recorder in recorders.values()
                                       for row in recorder.skill.values()), 21500)
        self.assertEqual(tracker.ndpsCast['self'].skill[skill.full_id]['sum'], 21500)

    def test_fixed_helper_is_exact_archived_bytecode_with_two_final_pools(self):
        manifest = json.loads((EVIDENCE/'fixed-damage-helper-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['clientVersion'], '1.6.0.10072')
        self.assertTrue(manifest['bytecodeRoundTrip'])
        for kind in ('raw', 'readable'):
            self.assertEqual(hashlib.sha256((EVIDENCE/manifest[kind+'Path']).read_bytes()).hexdigest(),
                             manifest[kind+'Sha256'])
        constants = manifest['constants']
        self.assertIn('nGamePlayDamageFinalCof', constants)
        self.assertIn('nActivityDamageFinalCof', constants)
        self.assertIn('SuperCustomDamage', constants)


if __name__ == "__main__":
    unittest.main()

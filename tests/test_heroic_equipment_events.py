"""Heroic exact-event chains and scoped Wujie fixed-proc attribution."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from data.DataContent import SingleDataBuff, SingleDataSkill
from replayer.CombatTracker import BoostCounter
from replayer import Name
from release.NameGenerator import parse_buff
from tests import test_target_boost_sources as source_fixtures

EVIDENCE = Path(__file__).resolve().parents[1] / 'docs/160/evidence/heroic_equipment10082'
PROFILE = {'level': 53, 'shieldBase': {school: 6399 for school in
           ('Physics', 'Solar', 'Lunar', 'Neutral', 'Poison')}}


class HeroicEquipmentEventTests(unittest.TestCase):
    def counter(self, occ='4pw', raw=None):
        return BoostCounter('owner', occ, 0, 10000,
                            baseAttribute={'_raw': raw or {'atPhysicsAttackPowerBase': 1000}},
                            targetProfiles={'boss': PROFILE})

    def rates(self, counter, identifier='"1,37561,1"'):
        return counter.getRateForEvent(SimpleNamespace(target='boss', full_id=identifier,
                                                        fullResult={'0': '10000'}), '附魔伤害')

    def test_wujie_fixed_children_retain_two_final_pools_and_reject_ordinary_boosts(self):
        for identifier in ('"1,37561,1"', '"1,37562,1"'):
            counter = self.counter(raw={'atPhysicsAttackPowerBase': 1000,
                                        'atGamePlayDamageFinalCof': 256})
            counter.addBoost('own', {'atActivityDamageFinalCof': 512}, 'owner', 1, 0)
            counter.addBoost('ap', {'atAllTypeAttackPowerBase': 200,
                'atAllTypeCriticalStrike': 3000, 'atAllTypeOvercomeBase': 3000,
                'atStrainRate': 256, 'atAllDamageAddPercent': 256,
                'atDstNpcDamageCoefficient': 256}, 'ordinary-provider', 1, 0)
            counter.addTargetBoost('boss', 'vulnerable',
                {'atPhysicsDamageCoefficient': 256, 'atPhysicsShieldAdditional': -1000},
                'ordinary-provider', 1, 0)
            counter.addBoost('game', {'atGamePlayDamageFinalCof': 256}, 'game-provider', 1, 0)
            counter.addBoost('activity', {'atActivityDamageFinalCof': 256}, 'activity-provider', 1, 0)
            rates = self.rates(counter, identifier)
            # Own coefficient1.25*1.5; all1.5*1.75; normalize two marginal gains.
            self.assertEqual(set(rates), {'self', 'game', 'activity'})
            self.assertAlmostEqual(rates['self']['rate'], 1.875 / 2.625)
            self.assertAlmostEqual(rates['game']['rate'], .4375 / .8125 * (1 - 1.875 / 2.625))
            self.assertAlmostEqual(rates['activity']['rate'], .375 / .8125 * (1 - 1.875 / 2.625))
            self.assertEqual(rates['game']['source'], 'game-provider')
            counter.removeBoost('game', 100)
            counter.removeBoost('activity', 100)
            self.assertEqual(set(self.rates(counter, identifier)), {'self'})
            self.assertEqual(self.rates(counter, identifier)['self']['rate'], 1)

    def test_exact_identity_and_wujie_scope_do_not_expand_to_neighbors(self):
        for occ in ('4pw', '3d', '4p', '4mw', '3dw'):
            counter = self.counter(occ)
            counter.addBoost('ap', {'atPhysicsAttackPowerBase': 200}, 'provider', 1, 0)
            if occ in ('4pw', '3d', '4p'):
                self.assertEqual(self.rates(counter)['self']['rate'], 1)
            else:
                self.assertAlmostEqual(self.rates(counter)['ap']['rate'], 1/6)
            for identifier in ('1,37560,1', '1,37563,1', '2,37561,1', '1,37561,2',
                               '1,37562,2', '"1,37561,1', '1,37561,1"'):
                self.assertAlmostEqual(self.rates(counter, identifier)['ap']['rate'], 1/6)

    def test_real_buff_pipeline_allocates_only_final_provider_and_expires_it(self):
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        tracker.boostCounter['self'] = BoostCounter('self', '4pw', 0, 10000,
            baseAttribute={'_raw': {'atPhysicsAttackPowerBase': 1000}},
            targetProfiles={'boss': PROFILE})
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
        self.assertAlmostEqual(sum(r['sum'] for r in tracker.rdpsCast['fs'].skill.values()), 510)
        self.assertAlmostEqual(sum(r['sum'] for r in tracker.rdpsCast['self'].skill.values()), 20990)
        self.assertEqual(tracker.ndpsCast['self'].skill[skill.full_id]['sum'], 21500)

    def test_exact_team_attack_and_waist_pool_preserve_source_and_lifetime(self):
        counter = self.counter()
        base = deepcopy(counter.attributeData.baseAttrib)
        counter.addBoost('own-waist', Name.BOOST_DICT['2,15455,2'], 'owner', 1, 0)
        counter.addBoost('tank-enchant', Name.BOOST_DICT['2,15413,19'], 'tank', 1, 0)
        rates = self.rates(counter, '1,999,1')
        self.assertAlmostEqual(rates['tank-enchant']['rate'], 90/1090)
        self.assertEqual(rates['tank-enchant']['source'], 'tank')
        self.assertNotIn('own-waist', rates)
        counter.removeBoost('tank-enchant', 100)
        self.assertEqual(set(self.rates(counter, '1,999,1')), {'self'})
        self.assertEqual(self.rates(counter, '1,999,1')['self']['rate'], 1)
        self.assertEqual(counter.attributeData.baseAttrib, base)

    def test_exact_native_rows_match_runtime_dynamic_attributes(self):
        evidence = json.loads((EVIDENCE/'event-evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(evidence['rowDiffs'], [])
        self.assertEqual(len(evidence['events']), 21)
        for event in evidence['events']:
            for buff in event['buffs']:
                self.assertTrue(buff['sameAs10082'])
                key = '2,%s,%s' % (buff['id'], buff['level'])
                expected = parse_buff(buff['row'])[1]
                if expected:
                    self.assertEqual(Name.BOOST_DICT[key], expected)
        chains = {row['id']: row for row in evidence['events']}
        self.assertEqual(chains['2753']['effectiveSkillID'], '1852')
        self.assertEqual(chains['2753']['buffs'][0]['id'], '1915')
        derived = {row['row']['RecipeID']: row for row in evidence['derivedRecipes']}
        self.assertEqual(derived['5758']['row']['SkillID'], '2699')
        self.assertEqual(derived['5758']['row']['DamageAddPercent'], '461')
        self.assertEqual(derived['6228']['row']['DamageAddPercent'], '0')
        self.assertTrue(all(not row['archived10082Available'] for row in derived.values()))

    def test_portable_fresh_sources_and_scoped_models(self):
        manifest = json.loads((EVIDENCE/'event-source-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['clientVersion'], '1.6.0.10086')
        self.assertEqual(manifest['archivedTableReference'], '1.6.0.10082')
        for stage in manifest['stages']:
            self.assertTrue(stage['protectedUnchanged'])
            self.assertEqual(stage['protectedBefore'], stage['protectedAfter'])
        for source in manifest['files']:
            for path, digest in (('rawPath', 'rawSha256'), ('readablePath', 'readableSha256'),
                                 ('disassemblyPath', 'disassemblySha256')):
                if path in source:
                    self.assertEqual(hashlib.sha256((EVIDENCE/source[path]).read_bytes()).hexdigest(), source[digest])
        models = json.loads((EVIDENCE/'event-models.json').read_text(encoding='utf-8'))
        scoped = [row for row in models if 'wujieHandling' in row]
        self.assertEqual({r['value1'] for r in scoped}, {'1932','2753','3149','3203','3204','3205'})
        self.assertTrue(all(row['wujieOccupations'] == ['4pw'] for row in scoped))

    def reflection(self, time=1000, caster='boss', target='self', result_type='1', amount=12520,
                   extra=None):
        event = SingleDataSkill()
        result = {'5': str(amount), '13': '0', '14': '0'}
        result.update(extra or {})
        event.setByJcl(['', '16', '1793577600', str(time), '21',
            {'1': caster, '2': target, '3': result_type, '4': '1', '5': '45532',
             '6': '3', '9': result}])
        return event

    def test_reflection_parser_keeps_original_hit_and_credits_owner_once(self):
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        tracker.boostCounter['self'].addBoost('ap', {'atPhysicsAttackPowerBase': 1000,
            'atGamePlayDamageFinalCof': 512}, 'tg', 1, 0)
        tracker.boostCounter['self'].addTargetBoost('boss', 'vulnerable',
            {'atPhysicsDamageCoefficient': 256}, 'fs', 1, 0)
        event = self.reflection()
        before = deepcopy(vars(event))
        tracker.recordSkill(event)
        tracker.recordSkill(event)  # Re-delivery of this result does not consume twice.
        self.assertEqual(vars(event), before)
        self.assertEqual((event.caster, event.target, event.damageEff), ('boss', 'self', 0))
        key = '7,1,45532,3'
        for counters in (tracker.ndpsCast, tracker.rdpsCast, tracker.mndpsCast, tracker.mrdpsCast):
            self.assertEqual(counters['self'].skill[key], {'sum': 12520, 'num': 1})
            self.assertEqual(counters['tg'].skill, {})
            self.assertEqual(counters['fs'].skill, {})
        self.assertEqual(tracker.ndpsCast['self'].target['boss']['sum'], 12520)
        self.assertEqual(tracker.rdpsCast['self'].source['自身伤害']['sum'], 12520)
        self.assertIn('反弹', tracker.ndpsCast['self'].getSkillName(key, tracker.info))
        # The ordinary paired hit has its own resultType=0 and no returned amount.
        incoming = self.reflection(result_type='0', amount=0, extra={'0': '30849', '13': '30849'})
        tracker.recordSkill(incoming)
        self.assertEqual(tracker.rdpsCast['self'].skill[key]['sum'], 12520)

    def test_distinct_same_frame_reflections_sum_once_per_native_result_not_school(self):
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        for _ in range(2):
            event = self.reflection(amount=300, extra={'0': '0', '1': '0', '13': '0'})
            tracker.recordSkill(event)
        self.assertEqual(tracker.rdpsCast['self'].skill['7,1,45532,3'], {'sum': 600, 'num': 2})
        # An add's reflected damage belongs to all-target DPS but not main-target DPS.
        tracker.recordSkill(self.reflection(time=1001, caster='other', amount=400))
        self.assertEqual(tracker.ndpsCast['self'].skill['7,1,45532,3']['sum'], 1000)
        self.assertEqual(tracker.mndpsCast['self'].skill['7,1,45532,3']['sum'], 600)

    def test_reflection_requires_verified_native_direction_result_and_time(self):
        invalid = [self.reflection(result_type='0'), self.reflection(result_type='2'),
                   self.reflection(amount=0), self.reflection(amount=-1),
                   self.reflection(caster='unknown'), self.reflection(caster='fs'),
                   self.reflection(target='other'), self.reflection(time=-1),
                   self.reflection(time=9000001),
                   self.reflection(extra={'0': '100', '1': '200', '13': '0'}),
                   self.reflection(extra={'13': '300'}), self.reflection(extra={'6': '10'})]
        missing = self.reflection()
        del missing.fullResult['5']
        mismatch = self.reflection()
        mismatch.fullResult['5'] = '1'
        invalid.extend((missing, mismatch))
        for event in invalid:
            tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
            tracker.recordSkill(event)
            self.assertFalse(any('7,1,45532,3' in c.skill for c in tracker.ndpsCast.values()))
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        tracker.badPeriodDpsLog = [[1000, 1], [2000, 0]]
        tracker.recordSkill(self.reflection(time=1001))
        tracker.recordSkill(self.reflection(time=1500))
        tracker.recordSkill(self.reflection(time=2001, amount=50))
        self.assertEqual(tracker.rdpsCast['self'].skill['7,1,45532,3']['sum'], 50)

    def test_legacy_result_five_is_not_assumed_to_be_jcl_reflection(self):
        event = SingleDataSkill()
        event.setByJx3dat({'2': '1793577600', '3': '1000', '5': 'boss', '6': 'self',
            '7': '1', '8': '45532', '9': '3', '10': '1,45532,3', '11': '0',
            '12': '0', '13': '0', '14': '0', '15': '0', '16': {'5': '12520'}})
        self.assertIsNone(event.resultType)
        self.assertEqual(event.reflectionDamage, 0)
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        tracker.recordSkill(event)
        self.assertEqual(tracker.ndpsCast['self'].skill, {})


if __name__ == '__main__':
    unittest.main()

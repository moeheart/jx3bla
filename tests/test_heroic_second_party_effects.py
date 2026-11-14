"""November14 exact equipment identities and newly audited Wujie contexts.

All fixtures are synthetic: no player's equipment, name or identifier is used.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from data.DataContent import SingleDataBuff
from equip.EquipmentEffects import effect_catalogue, effect_key, resolve_equipment_effects
from release.EquipmentEffectGenerator import build_catalogue, OUTPUT, EVIDENCE
from replayer import Name
from replayer.CombatTracker import BoostCounter
from tests import test_target_boost_sources as source_fixtures
from tools.Attribute import COEFF50


AUDIT = Path(__file__).resolve().parents[1] / 'docs/160/evidence/heroic_equipment20261114'
PROFILE = {'level': 53, 'shieldBase': {school: 6399 for school in
           ('Physics', 'Solar', 'Lunar', 'Neutral', 'Poison')}}
CLOTHES = 'skill/装备/苍生铸世赛季输出衣服附魔_1110.lua'
HAT = 'skill/装备/苍生铸世赛季输出帽子附魔_1110.lua'

# Exact affected contexts observed in this party; not a blanket Wujie allowlist.
ACTUAL_CONTEXTS = {
    **{('atSetEquipmentRecipe', identifier, '1'): ('25',) for identifier in ('5037', '5038')},
    **{('atSetEquipmentRecipe', identifier, '1'): ('10t',) for identifier in
       ('1544', '1545', '17333', '17246', '17337', '17343')},
    **{('atSetEquipmentRecipe', identifier, '1'): ('5dw',) for identifier in
       ('1524', '1525', '17380', '17239', '17384', '17383', '1547')},
    ('atSetEquipmentRecipe', '17250', '1'): ('5dw', '23w'),
    **{('atSetEquipmentRecipe', identifier, '1'): ('23w',) for identifier in ('4290', '4291')},
    ('atExecuteScript', CLOTHES, '0'): ('7pw', '5dw', '23w'),
    ('atExecuteScript', HAT, '0'): ('7pw', '5dw'),
    ('atSkillEventHandler', '1194', '0'): ('7p', '7pw'),
    ('atSkillEventHandler', '3240', '0'): ('3d',),
    ('atSkillEventHandler', '3261', '0'): ('10t',),
    ('atSkillEventHandler', '1952', '0'): ('10t',),
    ('atSkillEventHandler', '3203', '0'): ('7pw', '5dw'),
    ('atSkillEventHandler', '3204', '0'): ('7pw', '5dw', '23w'),
    ('atSkillEventHandler', '3205', '0'): ('5dw', '23w'),
    **{('atSkillEventHandler', identifier, '0'): ('5dw',) for identifier in
       ('3215', '3217', '2719', '1930', '3149')},
}


class HeroicSecondPartyEffectsTests(unittest.TestCase):
    def effect(self, kind, identifier, level):
        return {'type': kind, 'value1': identifier, 'value2': level,
                'source': 'synthetic equipment', 'warning': 'unverified exact effect'}

    def counter(self, occ, raw=None):
        school = 'Lunar' if occ == '5dw' else 'Physics'
        base = {'at%sAttackPowerBase' % school: 1000}
        base.update(raw or {})
        return BoostCounter('self', occ, 0, 10000, baseAttribute={'_raw': base},
                            targetProfiles={'boss': PROFILE})

    def rate(self, counter):
        school = 'Lunar' if counter.occ == '5dw' else 'Physics'
        return counter.getRate('boss', '1,999,1', 'synthetic damage', school)

    def tracker(self, occ):
        tracker = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        tracker.boostCounter['self'] = self.counter(occ)
        return tracker

    def buff(self, identifier, level, *, stack=1, caster='self', time=1000):
        buff = SingleDataBuff()
        buff.setByJcl(['', '16', '1793577600', str(time), '13', {
            '1': 'self', '2': 'false' if stack else 'true', '3': '5', '4': 'true',
            '5': str(identifier), '6': str(stack), '7': '32', '9': str(level),
            '10': caster, '11': 'true'}])
        return buff

    def test_all_32_exact_effects_resolve_in_actual_audited_contexts(self):
        self.assertEqual(len(ACTUAL_CONTEXTS), 32)
        model_keys = set()
        for prefix in ('recipe', 'script', 'event'):
            models = json.loads((AUDIT / (prefix + '-models.json')).read_text(encoding='utf-8'))
            model_keys.update(effect_key(model) for model in models)
        self.assertEqual(model_keys, set(ACTUAL_CONTEXTS))
        for key, occupations in ACTUAL_CONTEXTS.items():
            for occ in occupations:
                with self.subTest(effect=key, occupation=occ):
                    resolved, pending, _ = resolve_equipment_effects([self.effect(*key)], occ)
                    self.assertEqual(len(resolved), 1)
                    self.assertFalse(pending)

    def test_unknown_identity_level_and_unreviewed_wujie_remain_restricted(self):
        for key, occupations in ACTUAL_CONTEXTS.items():
            effect = self.effect(*key)
            with self.subTest(effect=key):
                for changed in (dict(effect, value1='999999-unverified'), dict(effect, value2='999')):
                    self.assertEqual(resolve_equipment_effects([changed], occupations[0]),
                                     ([], {changed['warning']}, {}))
                for occ in ('4mw', '10tw', '25w'):
                    self.assertEqual(resolve_equipment_effects([effect], occ),
                                     ([], {effect['warning']}, {}))
        with self.assertRaises(ValueError):
            resolve_equipment_effects([self.effect('atSkillEventHandler', '1194', '0')], 'unknown-profile')

    def test_catalogue_matches_generator_and_portable_evidence_hashes(self):
        generated = build_catalogue()
        self.assertEqual(len(generated['effects']), 205)
        self.assertEqual(json.loads(OUTPUT.read_text(encoding='utf-8')), generated)
        for model in generated['effects']:
            self.assertTrue((EVIDENCE / model['evidence'].split('#', 1)[0]).is_file())
        for source in generated['evidenceSources']:
            self.assertEqual(hashlib.sha256((EVIDENCE / source['file']).read_bytes()).hexdigest(),
                             source['sha256'])
        for prefix in ('recipe', 'script'):
            manifest = json.loads((AUDIT / (prefix + '-manifest.json')).read_text(encoding='utf-8'))
            self.assertEqual(manifest['clientVersion'], '1.6.0.10086')
            for source in manifest['files']:
                for path, digest in (('rawPath', 'sha256'), ('readablePath', 'readableSha256')):
                    self.assertFalse(Path(source[path]).is_absolute())
                    self.assertEqual(hashlib.sha256((AUDIT / source[path]).read_bytes()).hexdigest(),
                                     source[digest])

    def test_supplement_requires_explicit_wujie_handling_and_preserves_prior_scope(self):
        # Exercise generator input validation without changing audited files.
        original = {'type': 'atSetEquipmentRecipe', 'value1': '1524', 'value2': '1',
            'name': 'synthetic recipe', 'evidence': 'synthetic.json#1524/1',
            'ordinaryHandling': 'skill_coefficient', 'wujieHandling': 'inactive_ordinary',
            'wujieOccupations': ['5dw']}
        with TemporaryDirectory() as temporary:
            base, extra = Path(temporary) / 'base', Path(temporary) / 'extra'
            for directory in (base, extra):
                directory.mkdir()
                for name in ('script-models.json', 'event-models.json'):
                    (directory / name).write_text('[]', encoding='utf-8')
            def write(directory, row):
                (directory / 'recipe-models.json').write_text(json.dumps([row]), encoding='utf-8')
            write(base, original)
            write(extra, dict(original, wujieOccupations=['7pw']))
            generated = build_catalogue(base, extra)
            self.assertEqual(generated['effects'][0]['wujieOccupations'], ['5dw', '7pw'])
            self.assertEqual(generated['effects'][0]['wujieHandling'], 'inactive_ordinary')
            write(extra, dict(original, wujieHandling='logged_event', wujieOccupations=['7pw']))
            with self.assertRaises(ValueError):
                build_catalogue(base, extra)
            incomplete = dict(original, wujieOccupations=['4mw'])
            incomplete.pop('wujieHandling')
            write(extra, incomplete)
            with self.assertRaises(ValueError):
                build_catalogue(base, extra)

    def test_1110_clothing_adds_81_once_for_each_new_wujie_context(self):
        effect = self.effect('atExecuteScript', CLOTHES, '0')
        for occ in ('7pw', '5dw', '23w'):
            with self.subTest(occupation=occ):
                resolved, pending, raw = resolve_equipment_effects(
                    [effect, dict(effect, source='second synthetic source')], occ)
                self.assertEqual(len(resolved), 2)
                self.assertFalse(pending)
                self.assertEqual(raw, {'atAllTypeAttackPowerBase': 81, 'atBeTherapyCoefficient': -102})
                counter = self.counter(occ, raw)
                counter.addBoost('external', {'atAllTypeAttackPowerBase': 200}, 'provider', 1, 0)
                rates = self.rate(counter)
                self.assertAlmostEqual(rates['self']['rate'], 1081 / 1281)
                self.assertAlmostEqual(rates['external']['rate'], 200 / 1281)
                self.assertEqual(rates['external']['source'], 'provider')

    def test_hat_overcome_81_is_personal_only_during_native_buff_lifetime(self):
        effect = self.effect('atExecuteScript', HAT, '0')
        self.assertEqual(Name.BOOST_DICT['2,15436,18'], {'atAllTypeOvercomeBase': 81})
        denominator = COEFF50['破防']
        for occ in ('7pw', '5dw'):
            with self.subTest(occupation=occ):
                resolved, pending, raw = resolve_equipment_effects([effect], occ)
                self.assertEqual((resolved[0]['handling'], pending, raw), ('logged_event', set(), {}))
                tracker = self.tracker(occ)
                counter = tracker.boostCounter['self']
                base = deepcopy(counter.attributeData.baseAttrib)
                counter.addBoost('external', {'atAllTypeOvercomeBase': 200}, 'provider', 1, 0)
                initial = self.rate(counter)
                self.assertAlmostEqual(initial['self']['rate'], denominator / (denominator + 200))
                tracker.recordBuff(self.buff('15436', 18))
                active = self.rate(counter)
                self.assertEqual(set(active), {'self', 'external'})
                self.assertAlmostEqual(active['self']['rate'], (denominator + 81) / (denominator + 281))
                self.assertAlmostEqual(active['external']['rate'], 200 / (denominator + 281))
                tracker.checkRemoveBuff(2001)
                expired = self.rate(counter)
                self.assertAlmostEqual(expired['self']['rate'], initial['self']['rate'])
                self.assertEqual(counter.attributeData.baseAttrib, base)

    def test_mingzun_1544_and_1545_change_threat_only(self):
        rows = json.loads((AUDIT / 'recipe-evidence.json').read_text(encoding='utf-8'))['recipes']
        by_id = {row['id']: row for row in rows}
        text = (AUDIT / 'recipe-sources/readable/scripts/skill/秘笈/增加威胁20分.lua').read_text(encoding='utf-8')
        self.assertIn('ThreatPecent = 205', text)
        self.assertIn('ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT', text)
        for identifier in ('1544', '1545'):
            with self.subTest(recipe=identifier):
                effect = self.effect('atSetEquipmentRecipe', identifier, '1')
                resolved, pending, raw = resolve_equipment_effects([effect], '10t')
                self.assertEqual((resolved[0]['handling'], pending, raw), ('non_combat', set(), {}))
                self.assertEqual(by_id[identifier + '/1']['recipe'].get('DamageAddPercent', ''), '')
                self.assertEqual(by_id[identifier + '/1']['matchedSkills']['skill_mobile'], [])

    def test_water_4761_level87_adds_22_attack_with_owner_and_expiry(self):
        self.assertEqual(Name.BOOST_DICT['2,4761,87'], {'atAllTypeAttackPowerBase': 22})
        for occ in ('7p', '7pw'):
            with self.subTest(occupation=occ):
                tracker = self.tracker(occ)
                counter = tracker.boostCounter['self']
                base = deepcopy(counter.attributeData.baseAttrib)
                counter.addBoost('external', {'atAllTypeAttackPowerBase': 200}, 'provider', 1, 0)
                self.assertAlmostEqual(self.rate(counter)['self']['rate'], 1000 / 1200)
                tracker.recordBuff(self.buff('4761', 87))
                rates = self.rate(counter)
                self.assertEqual(set(rates), {'self', 'external'})
                self.assertAlmostEqual(rates['self']['rate'], 1022 / 1222)
                self.assertAlmostEqual(rates['external']['rate'], 200 / 1222)
                tracker.checkRemoveBuff(2001)
                self.assertAlmostEqual(self.rate(counter)['self']['rate'], 1000 / 1200)
                self.assertEqual(counter.attributeData.baseAttrib, base)


if __name__ == '__main__':
    unittest.main()

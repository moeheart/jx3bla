"""Exact heroic equipment effects, platform boundaries and attribution algebra."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from equip.EquipmentEffects import effect_key, resolve_equipment_effects
from replayer import Name
from replayer.CombatTracker import BoostCounter


EVIDENCE = Path(__file__).resolve().parents[1] / 'docs/160/evidence/heroic_equipment10082'
PROFILE = {'level': 53, 'shieldBase': {s: 6399 for s in
           ('Physics', 'Solar', 'Lunar', 'Neutral', 'Poison')}}


def read(name):
    return json.loads((EVIDENCE / name).read_text(encoding='utf-8'))


class HeroicRecipeScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipes = read('recipe-models.json')
        cls.scripts = read('script-models.json')
        cls.catalogue = {effect_key(r): r for r in cls.recipes + cls.scripts}

    def effect(self, model):
        return dict(model, source='synthetic equipment', warning='unverified effect')

    def resolve(self, models, occ):
        with patch('equip.EquipmentEffects.effect_catalogue', return_value=self.catalogue):
            return resolve_equipment_effects([self.effect(m) for m in models], occ)

    def counter(self, raw=None, occ='4pw'):
        return BoostCounter('owner', occ, 0, 10000,
                            baseAttribute={'_raw': dict(raw or {}, atPhysicsAttackPowerBase=1000)},
                            targetProfiles={'boss': PROFILE})

    def rate(self, counter):
        return counter.getRate('boss', '1,100001,1', '合成伤害', 'Physics')

    def test_fresh_script_bytes_and_readable_sources_have_explicit_version(self):
        for prefix in ('recipe', 'script'):
            manifest = read(prefix + '-manifest.json')
            self.assertEqual(manifest['clientVersion'], '1.6.0.10086')
            self.assertEqual(manifest['archivedTableReference'], '1.6.0.10082')
            self.assertTrue(manifest['protectedUnchanged'])
            for item in manifest['files']:
                for path_key, digest_key in (('rawPath', 'sha256'), ('readablePath', 'readableSha256')):
                    self.assertFalse(Path(item[path_key]).is_absolute())
                    self.assertEqual(hashlib.sha256((EVIDENCE / item[path_key]).read_bytes()).hexdigest(),
                                     item[digest_key])

    def test_coefficients_are_exact_rows_and_never_added_to_panel_twice(self):
        evidence = read('recipe-evidence.json')
        rows = {r['id']: r for r in evidence['recipes']}
        self.assertEqual(len(rows), 41)
        self.assertEqual(sum(m['ordinaryHandling'] == 'skill_coefficient' for m in self.recipes), 29)
        for model in self.recipes:
            with self.subTest(key=effect_key(model)):
                record = rows[model['value1'] + '/' + model['value2']]
                self.assertTrue(record['equalPrior10072RecipeRow'])
                self.assertTrue(record['matchedSkillsEqual10082Rows'])
                self.assertEqual((record['recipe']['RecipeID'], record['recipe']['RecipeLevel']),
                                 (model['value1'], model['value2']))
                _, warnings, raw = self.resolve([model], '4p')
                self.assertEqual((warnings, raw), (set(), {}))
        self.assertEqual(rows['818/7']['recipe']['DamageAddPercent'], '204')
        self.assertEqual(rows['17250/1']['recipe']['DamageAddPercent'], '55')
        # These exact ordinary recipes have no matching mobile skill scope.
        for identifier in ('1522/1', '1523/1', '818/1'):
            self.assertFalse(rows[identifier]['matchedSkills']['skill_mobile'])
        for row in rows.values():
            if row['recipeTable'] == 'skill_mobile':
                self.assertFalse(row['matchedSkills']['skill'])

    def test_only_observed_wujie_specialization_and_exact_parameters_are_supported(self):
        certified = [m for m in self.recipes + self.scripts if m.get('wujieHandling')]
        self.assertEqual(len(certified), 10)
        for model in self.recipes + self.scripts:
            with self.subTest(key=effect_key(model)):
                resolved, pending, _ = self.resolve([model], '4pw')
                self.assertEqual(bool(resolved), bool(model.get('wujieHandling')))
                self.assertEqual(bool(pending), not bool(model.get('wujieHandling')))
                self.assertTrue(self.resolve([model], '4mw')[1])
                changed = dict(model, value2='999')
                self.assertEqual(self.resolve([changed], '4p'), ([], {'unverified effect'}, {}))
                self.assertEqual(self.resolve([changed], '4pw'), ([], {'unverified effect'}, {}))

    def test_clothing_passive_adds_exact_attack_once_and_dilutes_external_share(self):
        for suffix, attack in (('1110', 81), ('1280', 90)):
            model = next(m for m in self.scripts if m['value1'].endswith('输出衣服附魔_' + suffix + '.lua'))
            for occ in (('4p', '4pw') if suffix == '1110' else ('4p',)):
                with self.subTest(suffix=suffix, occ=occ):
                    resolved, pending, raw = self.resolve([model, model], occ)
                    self.assertEqual(len(resolved), 2)
                    self.assertFalse(pending)
                    self.assertEqual(raw, {'atAllTypeAttackPowerBase': attack, 'atBeTherapyCoefficient': -102})
                    counter = self.counter(raw, occ)
                    counter.addBoost('external', {'atPhysicsAttackPowerBase': 200}, 'provider', 1, 0)
                    rates = self.rate(counter)
                    self.assertAlmostEqual(rates['self']['rate'], (1000 + attack) / (1200 + attack))
                    self.assertAlmostEqual(rates['external']['rate'], 200 / (1200 + attack))
                    self.assertAlmostEqual(sum(r['rate'] for r in rates.values()), 1)

    def test_hat_is_logged_overcome_with_no_permanent_static_bonus(self):
        for suffix, level, overcome in (('1110', '18', 81), ('1280', '19', 90)):
            model = next(m for m in self.scripts if m['value1'].endswith('输出帽子附魔_' + suffix + '.lua'))
            resolved, pending, raw = self.resolve([model], '4p')
            self.assertEqual((resolved[0]['handling'], pending, raw), ('logged_event', set(), {}))
            self.assertEqual(Name.BOOST_DICT['2,15436,' + level], {'atAllTypeOvercomeBase': overcome})

    def test_wujie_orange_proc_uses_personal_additive_pool_and_logged_removal(self):
        model = next(m for m in self.recipes if m['value1'] == '17305')
        resolved, pending, raw = self.resolve([model], '4pw')
        self.assertEqual((resolved[0]['handling'], pending, raw), ('logged_event', set(), {}))
        boost = Name.BOOST_DICT['2,70161,15']
        self.assertEqual(boost, {'atAllPhysicsDamageAddPercent': 154, 'atAllMagicDamageAddPercent': 154})
        counter = self.counter()
        counter.addBoost('equipment', boost, 'owner', 1, 0,
                         instance=('70161', 'slot', '106'))
        counter.addBoost('external', {'atAllPhysicsDamageAddPercent': 256}, 'provider', 1, 0)
        rates = self.rate(counter)
        self.assertNotIn('equipment', rates)
        self.assertAlmostEqual(rates['self']['rate'], (1024 + 154) / (1024 + 154 + 256))
        self.assertAlmostEqual(sum(r['rate'] * 10000 for r in rates.values()), 10000)
        counter.removeBoost('equipment', 1000, instance=('70161', 'slot', '106'))
        self.assertAlmostEqual(self.rate(counter)['self']['rate'], 1024 / 1280)
        cooldown = next(m for m in self.recipes if m['value1'] == '17341')
        self.assertEqual(self.resolve([cooldown], '4pw')[1:], (set(), {}))


if __name__ == '__main__':
    unittest.main()

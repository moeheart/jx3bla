"""Evidence-scoped equipment support and conservative unknown-effect handling."""
import json
import hashlib
import unittest

from equip.AttributeDisplay import AttributeDisplay
from equip.EquipmentEffects import resolve_equipment_effects
from release.EquipmentEffectGenerator import build_catalogue, OUTPUT, EVIDENCE
from tests.test_cangsheng_equipment import equipment_text


class EquipmentEffectCatalogueTests(unittest.TestCase):
    def test_runtime_catalogue_is_reproducible_from_reviewed_evidence(self):
        catalogue = build_catalogue()
        self.assertEqual(json.loads(OUTPUT.read_text(encoding='utf-8')), catalogue)
        self.assertEqual(len(catalogue['effects']), 193)
        self.assertEqual(sum(row['ordinaryHandling'] == 'inactive_mobile'
                             for row in catalogue['effects']), 63)
        for row in catalogue['effects']:
            self.assertTrue((EVIDENCE / row['evidence'].split('#', 1)[0]).is_file(), row)
        for source in catalogue['evidenceSources']:
            self.assertEqual(hashlib.sha256((EVIDENCE / source['file']).read_bytes()).hexdigest(),
                             source['sha256'])

    def effect(self, name='atSetEquipmentRecipe', value='1516', level='1', source='test'):
        return {'type': name, 'value1': value, 'value2': level, 'source': source,
                'warning': source + ': ' + name}

    def test_recipe_identity_and_level_are_both_required(self):
        known = self.effect()
        modeled, pending, raw = resolve_equipment_effects([known], '2d')
        self.assertEqual(modeled[0]['handling'], 'skill_coefficient')
        self.assertEqual((pending, raw), (set(), {}))
        for unknown in (self.effect(level='2'), self.effect(value='999999'),
                        self.effect(name='atSetEquipmentSkill')):
            with self.subTest(unknown=unknown):
                self.assertEqual(resolve_equipment_effects([unknown], '2d'),
                                 ([], {unknown['warning']}, {}))

    def test_mobile_recipes_are_inactive_only_for_ordinary_specializations(self):
        effect = self.effect(value='17239')
        self.assertEqual(resolve_equipment_effects([effect], '2d')[0][0]['handling'], 'inactive_mobile')
        self.assertEqual(resolve_equipment_effects([effect], '2dw'), ([], {effect['warning']}, {}))
        with self.assertRaises(ValueError):
            resolve_equipment_effects([effect], 'unknown-specialization')

    def test_weapon_preserves_recipe_level_and_resolves_all_its_real_effects(self):
        display = AttributeDisplay()
        text = equipment_text({'0': [45303, 0, 0, 0, 0, 0, 0, 0]})
        base = display.GetBaseAttrib(text, '2d')
        self.assertEqual(display.status['status'], 'supported')
        self.assertNotIn('_warnings', base)
        self.assertEqual(len(base['_modeledEffects']), 9)
        self.assertEqual({row['value2'] for row in display.ac.lastEffects
                          if row['type'] == 'atSetEquipmentRecipe'}, {'1'})
        mobile = AttributeDisplay()
        self.assertTrue(mobile.GetBaseAttrib(text, '2dw')['_warnings'])
        self.assertEqual(mobile.status['status'], 'incomplete')

    def test_unknown_script_remains_explicit_and_prevents_precision(self):
        display = AttributeDisplay()
        base = display.GetBaseAttrib(equipment_text({'12': [111692, 0, 11272, 0, 0, 0, 0, 0]}), '6h')
        self.assertEqual(base['_warnings'], ['附魔11272: atExecuteScript'])
        self.assertEqual(display.status['status'], 'incomplete')

    def test_shared_warning_text_cannot_hide_an_unknown_effect(self):
        known = self.effect(source='same source')
        unknown = self.effect(value='999999', source='same source')
        modeled, pending, _ = resolve_equipment_effects([known, unknown], '2d')
        self.assertEqual(len(modeled), 1)
        self.assertEqual(pending, {unknown['warning']})

    def test_passive_learned_skill_is_not_added_twice_from_duplicate_entries(self):
        effect = self.effect('atExecuteScript', 'skill/装备/苍生铸世赛季输出衣服附魔_1110.lua', '0')
        second = dict(effect, source='second source')
        modeled, pending, raw = resolve_equipment_effects([effect, second], '3d')
        self.assertEqual(len(modeled), 2)
        self.assertFalse(pending)
        self.assertEqual(raw, {'atAllTypeAttackPowerBase': 81, 'atBeTherapyCoefficient': -102})


if __name__ == '__main__':
    unittest.main()

"""Supplemental audits cannot silently relax platform or existing semantics."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from release.EquipmentEffectGenerator import build_catalogue
from equip.EquipmentEffects import resolve_equipment_effects


class HeroicCatalogueBoundaryTests(unittest.TestCase):
    def model(self, **changes):
        row = dict(type='atSetEquipmentRecipe', value1='123', value2='1',
                   name='Audited recipe', ordinaryHandling='skill_coefficient',
                   evidence='recipe-evidence.json#123/1')
        row.update(changes)
        return row

    def build(self, original, supplemental):
        with tempfile.TemporaryDirectory() as folder:
            roots = [Path(folder)/name for name in ('original', 'supplemental')]
            for root, rows in zip(roots, (original, supplemental)):
                root.mkdir()
                for kind in ('recipe', 'script', 'event'):
                    (root/(kind+'-models.json')).write_text(
                        json.dumps(rows if kind == 'recipe' else []), encoding='utf-8')
            return build_catalogue(*roots)

    def test_reviewed_platform_extension_preserves_ordinary_semantics(self):
        result = self.build([self.model()], [self.model(
            wujieHandling='inactive_ordinary', wujieOccupations=['4pw'])])
        self.assertEqual(len(result['effects']), 1)
        row = result['effects'][0]
        self.assertEqual(row['ordinaryHandling'], 'skill_coefficient')
        self.assertEqual(row['wujieOccupations'], ['4pw'])
        self.assertEqual(row['evidence'], '../supplemental/recipe-evidence.json#123/1')

    def test_wujie_requires_explicit_valid_specialization_scope(self):
        for values in ({}, {'wujieOccupations': []}, {'wujieOccupations': ['4p']},
                       {'wujieOccupations': [None]}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.build([], [self.model(wujieHandling='logged_event', **values)])

    def test_new_audit_cannot_silently_change_existing_calculation(self):
        for changes in ({'ordinaryHandling': 'non_combat'},
                        {'staticAttributes': {'atAllTypeAttackPowerBase': 90}}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.build([self.model()], [self.model(**changes)])

    def test_duplicate_within_one_audit_is_rejected(self):
        with self.assertRaises(ValueError):
            self.build([], [self.model(), self.model()])

    def test_missing_evidence_is_not_hidden_by_supplemental_path_prefix(self):
        with self.assertRaises(ValueError):
            self.build([], [self.model(evidence='')])

    def test_inactive_wujie_path_does_not_inherit_ordinary_passive_attributes(self):
        model = self.model(ordinaryHandling='static_attributes',
                           staticAttributes={'atAllTypeAttackPowerBase': 90},
                           wujieHandling='inactive_ordinary', wujieOccupations=['4pw'])
        key = (model['type'], model['value1'], model['value2'])
        effect = dict(model, source='synthetic', warning='unknown')
        with patch('equip.EquipmentEffects.effect_catalogue', return_value={key: model}):
            self.assertEqual(resolve_equipment_effects([effect], '4p')[2], {'atAllTypeAttackPowerBase': 90})
            self.assertEqual(resolve_equipment_effects([effect], '4pw')[2], {})
            self.assertTrue(resolve_equipment_effects([effect], '4mw')[1])


if __name__ == '__main__':
    unittest.main()

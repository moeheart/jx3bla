"""Formal 10009 attribute regression and retained 160 replay compatibility."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import copy
import unittest

from equip.AttributeDisplay import AttributeDisplay
from equip.CangshengAttributeData import (
    CangshengAttributeData, calculate_attributes, kungfu_data, make_base_attributes,
    static_attributes, npc_data, get_target_profiles,
)
from release.GenerateFormalXinfa50 import verify_evidence
from replayer.CombatTracker import BoostCounter
from tools.check_cangsheng_role_panel import literal_tables
from release.Lua51Evidence import Chunk

ROOT = Path(__file__).resolve().parents[1] / 'equip/resources/cangshengtf'


class FormalAttributeTests(unittest.TestCase):
    def test_original_sources_and_complete_profile_selection(self):
        manifest, selected = verify_evidence(ROOT / 'xinfa10009_evidence')
        self.assertEqual(len(manifest['files']), 114)
        self.assertEqual(len(selected), 65)
        formal, old = kungfu_data(161), kungfu_data(160)
        self.assertEqual(formal['client_version'], '1.6.0.10009')
        self.assertEqual(set(formal['occupations']), set(old['occupations']))
        sources = {row['origin']: row['sha256'] for row in manifest['files']}
        for profile in list(formal['occupations'].values()) + list(formal['alternate_xinfa'].values()):
            self.assertEqual(profile['source']['sha256'], sources[profile['source']['origin']])
            self.assertEqual(profile['learning_source']['sha256'], sources[profile['learning_source']['origin']])
            self.assertEqual(profile['skill_level'], 5)
            self.assertEqual(profile['learning_source']['row']['RequirePlayerLevel'], '50')
        self.assertEqual(kungfu_data(162), formal)

    def test_npc_coefficients_use_formal_shared_constants_and_keep_old(self):
        for occ, old_value, formal_value in (
                ('1d', 287, 174), ('2d', 543, 604), ('7p', 195, 317),
                ('22d', 61, 31), ('24w', 860, 922), ('34', 471, 532)):
            self.assertEqual(static_attributes(occ, 160)['atDstNpcDamageCoefficient'], old_value)
            self.assertEqual(static_attributes(occ, 161)['atDstNpcDamageCoefficient'], formal_value)
        # All five normal healer permanent level-50 attributes remain unchanged.
        for occ in ('2h', '5h', '6h', '22h', '212h'):
            self.assertEqual(static_attributes(occ, 160), static_attributes(occ, 161))

    def test_base_primary_conversion_is_versioned_before_multipliers(self):
        for occ, primary, attack in (('3d', 'atStrengthBase', 'atPhysicsAttackPowerBase'),
                                     ('2d', 'atSpunkBase', 'atNeutralAttackPowerBase')):
            raw = {primary: 1000, attack: 1000}
            old = calculate_attributes(raw, occ, gameEdition=160)
            formal = calculate_attributes(raw, occ, gameEdition=161)
            self.assertEqual(old['攻击'], 1195)
            self.assertEqual(old['破防等级'], 61)
            self.assertEqual(formal['攻击'], 1190)
            self.assertEqual(formal['破防等级'], 60)
        raw = dict(atStrengthBase=1000, atPhysicsAttackPowerBase=1000, atPhysicsAttackPowerPercent=1024)
        self.assertEqual(calculate_attributes(raw, '3d', gameEdition=161)['攻击'], 2380)

    def test_boost_counter_and_equipment_display_propagate_game_edition(self):
        raw = dict(atStrengthBase=1000, atPhysicsAttackPowerBase=1000)
        calculator = CangshengAttributeData('3d', gameEdition=161)
        calculator.baseAttrib = {'_raw': raw}
        calculator.setBoosts([])
        self.assertEqual(calculator.getFinalAttrib()['攻击'], 1190)
        self.assertEqual(calculator.addBoostAndGetAttrib({'atStrengthBase': 100})['攻击'], 1209)
        self.assertEqual(calculator.removeBoostAndGetAttrib({'atStrengthBase': 100})['攻击'], 1190)
        display = object.__new__(AttributeDisplay)
        display.gameEdition = 161
        display.status = {}
        display.ac = SimpleNamespace(CalculateAll=lambda _: raw, lastWarnings=[])
        base = display.GetBaseAttrib('equipment', '3d')
        panel = display.GetPanelAttrib('equipment', '3d')
        self.assertEqual(base, make_base_attributes(raw, '3d', gameEdition=161))
        self.assertEqual(panel['攻击'], calculate_attributes(base['_raw'], '3d', gameEdition=161)['攻击'])
        self.assertEqual(base['_raw']['atDstNpcDamageCoefficient'], 451)

    def test_new_npc_templates_only_apply_to_formal_logs(self):
        old, formal = npc_data(160)['profiles'], npc_data(161)['profiles']
        self.assertEqual(len(old), 90)
        self.assertEqual(len(formal), 102)
        for template, profile in old.items():
            self.assertEqual(formal[template]['level'], profile['level'])
            self.assertEqual(formal[template]['shieldBase'], profile['shieldBase'])
        info = SimpleNamespace(map='25人普通洛阳之战', npc={'new': SimpleNamespace(templateID='141688')})
        self.assertEqual(get_target_profiles(info, 160), {})
        self.assertEqual(get_target_profiles(info, 161)['new'], formal['141688'])

    def test_missing_formal_npc_defense_preserves_damage_and_marks_unresolved(self):
        raw = npc_data(161)['profiles']['140665']
        self.assertTrue(all(value is None for value in raw['shieldBase'].values()))
        info = SimpleNamespace(map='25人普通洛阳之战', npc={
            'unknown': SimpleNamespace(templateID='140665'),
            'boss': SimpleNamespace(templateID='139323')})
        profiles = get_target_profiles(info, 161)
        self.assertNotIn('unknown', profiles)
        self.assertIn('boss', profiles)
        counter = BoostCounter('player', '3d', 0, 10000,
                               baseAttribute=make_base_attributes({}, '3d', 161),
                               gameEdition=161, targetProfiles=profiles)
        self.assertEqual(counter.getRate('unknown', '999', '普通伤害'),
                         {'self': {'source': 'player', 'rate': 1.0}})
        self.assertEqual(counter.unresolvedTargets, {'unknown'})
        self.assertNotIn('unknown', counter.rdpsRate)
        self.assertTrue(all(value is None for value in raw['shieldBase'].values()))

    def test_target_selection_requires_valid_level_and_all_five_defenses(self):
        valid = npc_data(161)['profiles']['139323']
        invalid = []
        for level in (None, 0, -1, True, 53.5):
            invalid.append(dict(valid, level=level))
        for value in (None, -1, True, float('nan'), float('inf')):
            profile = copy.deepcopy(valid)
            profile['shieldBase']['Lunar'] = value
            invalid.append(profile)
        profile = copy.deepcopy(valid)
        del profile['shieldBase']['Poison']
        invalid.append(profile)
        data = {'map': 'test-map', 'profiles': {str(index): row for index, row in enumerate(invalid)}}
        data['profiles']['valid'] = valid
        info = SimpleNamespace(map='test-map', npc={key: SimpleNamespace(templateID=key)
                                                  for key in data['profiles']})
        with patch('equip.CangshengAttributeData.npc_data', return_value=data):
            self.assertEqual(get_target_profiles(info, 161), {'valid': valid})
        # The six retained 160 boss templates keep identical values and routing.
        old = npc_data(160)
        info = SimpleNamespace(map=old['map'], npc={key: SimpleNamespace(templateID=key)
                                                  for key in old['mainTemplates']})
        self.assertEqual(get_target_profiles(info, 160),
                         {key: old['profiles'][key] for key in old['mainTemplates']})

    def test_formal_defaults_refinement_and_defense_parameters_remain_compatible(self):
        evidence = ROOT / 'xinfa10009_evidence/unpack_result'
        registers, _, _ = literal_tables(Chunk((evidence / 'ui/Script/common/role_attribute.lua').read_bytes()))
        self.assertEqual(registers[54], dict(atVitalityBase=18, atStrengthBase=17, atSpunkBase=17,
                                            atSpiritBase=18, atAgilityBase=18, atLifeAdditional=3956))
        self.assertEqual(registers[57]['YouluoPhysicsAPToMagicAPCof'], 1)
        self.assertEqual(registers[57]['YouluoWeaponToMagicAPCof'], 6)
        self.assertEqual((ROOT / 'StrengthableAttrib.tab').read_text(encoding='utf-8'),
                         (evidence / 'settings/item/StrengthableAttrib.tab').read_text(encoding='gb18030'))
        parameters = json.loads((ROOT / 'global_parameters_hd.json').read_text(encoding='utf-8'))
        for name, value in (('fPhysicsShieldParam', 10.912), ('fMagicShieldParam', 10.912),
                            ('fInsightParam', 7.117), ('fHasteRate', 10.21)):
            self.assertEqual(parameters['values'][name], value)
        self.assertEqual(parameters['level_factors']['50'], 990)
        self.assertEqual(parameters['level_factors']['53'], 1089)


if __name__ == '__main__':
    unittest.main()

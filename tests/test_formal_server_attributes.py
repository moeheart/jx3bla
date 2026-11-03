"""Formal 10009 attribute and original-source regressions."""
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
from release.FormalXinfa50Generator import verify_evidence
from replayer.CombatTracker import BoostCounter
from tools.ValidateCangshengRolePanel import literal_tables
from release.Lua51Evidence import Chunk

ROOT = Path(__file__).resolve().parents[1] / 'equip/resources/cangshengtf'
EVIDENCE = Path(__file__).resolve().parents[1] / 'docs/160/evidence/xinfa10009_evidence'


class FormalAttributeTests(unittest.TestCase):
    def test_original_sources_and_complete_profile_selection(self):
        manifest, selected = verify_evidence(EVIDENCE)
        self.assertEqual(len(manifest['files']), 114)
        self.assertEqual(len(selected), 65)
        formal = kungfu_data()
        self.assertEqual(formal['client_version'], '1.6.0.10009')
        self.assertEqual(len(formal['occupations']), 64)
        sources = {row['origin']: row['sha256'] for row in manifest['files']}
        for profile in list(formal['occupations'].values()) + list(formal['alternate_xinfa'].values()):
            self.assertEqual(profile['source']['sha256'], sources[profile['source']['origin']])
            self.assertEqual(profile['learning_source']['sha256'], sources[profile['learning_source']['origin']])
            self.assertEqual(profile['skill_level'], 5)
            self.assertEqual(profile['learning_source']['row']['RequirePlayerLevel'], '50')

    def test_npc_coefficients_use_formal_shared_constants(self):
        for occ, value in (('1d', 174), ('2d', 604), ('7p', 317),
                           ('22d', 31), ('24w', 922), ('34', 532)):
            self.assertEqual(static_attributes(occ)['atDstNpcDamageCoefficient'], value)

    def test_formal_primary_conversion_precedes_multipliers(self):
        for occ, primary, attack in (('3d', 'atStrengthBase', 'atPhysicsAttackPowerBase'),
                                     ('2d', 'atSpunkBase', 'atNeutralAttackPowerBase')):
            raw = {primary: 1000, attack: 1000}
            formal = calculate_attributes(raw, occ)
            self.assertEqual(formal['攻击'], 1190)
            self.assertEqual(formal['破防等级'], 60)
        raw = dict(atStrengthBase=1000, atPhysicsAttackPowerBase=1000, atPhysicsAttackPowerPercent=1024)
        self.assertEqual(calculate_attributes(raw, '3d')['攻击'], 2380)

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
        self.assertEqual(base, make_base_attributes(raw, '3d'))
        self.assertEqual(panel['攻击'], calculate_attributes(base['_raw'], '3d')['攻击'])
        self.assertEqual(base['_raw']['atDstNpcDamageCoefficient'], 451)

    def test_formal_npc_templates_are_available(self):
        formal = npc_data()['profiles']
        self.assertEqual(len(formal), 102)
        info = SimpleNamespace(map='25人普通洛阳之战', npc={'new': SimpleNamespace(templateID='141688')})
        self.assertEqual(get_target_profiles(info)['new'], formal['141688'])

    def test_missing_formal_npc_defense_preserves_damage_and_marks_unresolved(self):
        raw = npc_data()['profiles']['140665']
        self.assertTrue(all(value is None for value in raw['shieldBase'].values()))
        info = SimpleNamespace(map='25人普通洛阳之战', npc={
            'unknown': SimpleNamespace(templateID='140665'),
            'boss': SimpleNamespace(templateID='139323')})
        profiles = get_target_profiles(info)
        self.assertNotIn('unknown', profiles)
        self.assertIn('boss', profiles)
        counter = BoostCounter('player', '3d', 0, 10000,
                               baseAttribute=make_base_attributes({}, '3d'),
                               gameEdition=161, targetProfiles=profiles)
        self.assertEqual(counter.getRate('unknown', '999', '普通伤害'),
                         {'self': {'source': 'player', 'rate': 1.0}})
        self.assertEqual(counter.unresolvedTargets, {'unknown'})
        self.assertNotIn('unknown', counter.rdpsRate)
        self.assertTrue(all(value is None for value in raw['shieldBase'].values()))

    def test_target_selection_requires_valid_level_and_all_five_defenses(self):
        valid = npc_data()['profiles']['139323']
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
            self.assertEqual(get_target_profiles(info), {'valid': valid})
        formal = npc_data()
        info = SimpleNamespace(map=formal['map'], npc={key: SimpleNamespace(templateID=key)
                                                     for key in formal['mainTemplates']})
        self.assertEqual(get_target_profiles(info),
                         {key: formal['profiles'][key] for key in formal['mainTemplates']})

    def test_formal_defaults_refinement_and_defense_parameters_remain_compatible(self):
        evidence = EVIDENCE / 'unpack_result'
        registers, _, _ = literal_tables(Chunk((evidence / 'ui/Script/common/role_attribute.lua').read_bytes()))
        self.assertEqual(registers[54], dict(atVitalityBase=18, atStrengthBase=17, atSpunkBase=17,
                                            atSpiritBase=18, atAgilityBase=18, atLifeAdditional=3956))
        self.assertEqual(registers[57]['YouluoPhysicsAPToMagicAPCof'], 1)
        self.assertEqual(registers[57]['YouluoWeaponToMagicAPCof'], 6)
        self.assertEqual((ROOT / 'StrengthableAttrib.tab').read_text(encoding='utf-8'),
                         (evidence / 'settings/item/StrengthableAttrib.tab').read_text(encoding='gb18030'))
        parameters = json.loads((ROOT / 'global_parameters.json').read_text(encoding='utf-8'))
        for name, value in (('fPhysicsShieldParam', 10.912), ('fMagicShieldParam', 10.912),
                            ('fInsightParam', 7.117), ('fHasteRate', 10.21)):
            self.assertEqual(parameters['values'][name], value)
        self.assertEqual(parameters['level_factors']['50'], 990)
        self.assertEqual(parameters['level_factors']['53'], 1089)


if __name__ == '__main__':
    unittest.main()

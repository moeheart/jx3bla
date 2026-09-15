"""50 级装备源表与导入链路回归；不把推算值冒充游戏面板实测值。"""
import unittest
from unittest.mock import patch

from equip.AttributeCal import AttributeCal
from equip.EquipmentExport import ImportExcelEquipment


def equipment_text(items):
    """按现有配装标准生成 13 个槽位；items 的键使用游戏槽位。"""
    order = ImportExcelEquipment().orderTable
    return '\n'.join('\t'.join(map(str, items.get(pos, [0, 0, 0, 0, 0, 0, 0, 0]))) for pos in order)


class CangshengEquipmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ac = AttributeCal(160)

    def test_gem_import_accepts_exported_levels_and_legacy_item_ids(self):
        importer = ImportExcelEquipment()
        for level in range(1, 9):
            self.assertEqual(importer.getPlug(str(level)), level)
            self.assertEqual(importer.getPlug(str(24422 + level)), level)
            self.assertEqual(importer.getPlug(str(24441 + level)), level)
        self.assertEqual(importer.getPlug(' '), 0)
        self.assertEqual(importer.getPlug('999999999'), 0)

    def test_current_values_are_already_compressed(self):
        result = self.ac.CalculateAll(equipment_text({'12': [111692, 0, 0, 0, 0, 0, 0, 0]}))
        self.assertEqual(result['atVitalityBase'], 348)
        self.assertEqual(result['atSpiritBase'], 165)
        self.assertEqual(result['atMagicAttackPowerBase'], 228)

    def test_refine_changes_magic_but_not_white_weapon_or_base_shield(self):
        result = self.ac.CalculateAll(equipment_text({'0': [46253, 6, 0, 0, 0, 0, 0, 0]}))
        self.assertEqual(result['atNeutralAttackPowerBase'], 925)
        self.assertEqual(result['atMeleeWeaponDamageBase'], 43)
        self.assertEqual(result['atMeleeWeaponDamageRand'], 28)
        self.assertEqual(result['atMeleeWeaponAttackSpeedBase'], 16)
        armor = self.ac.CalculateAll(equipment_text({'12': [111692, 6, 0, 0, 0, 0, 0, 0]}))
        self.assertEqual(armor['atSpiritBase'], 177)
        self.assertEqual(armor['atPhysicsShieldBase'], 22)
        self.assertEqual(armor['atMagicShield'], 28)

    def test_gems_survive_import_and_are_not_refined(self):
        result = self.ac.CalculateAll(equipment_text({'12': [111692, 6, 0, 0, 8, 6, 0, 0]}))
        self.assertEqual(result['atMagicOvercome'], 28)
        self.assertEqual(result['atSpiritBase'], 177 + 12)
        old_ids = self.ac.CalculateAll(equipment_text({'12': [111692, 6, 0, 0, 24449, 24447, 0, 0]}))
        self.assertEqual(result, old_ids)

    def test_native_gem_levels_and_scaling_flags(self):
        info = self.ac.equipmentInfo
        self.assertEqual([info.getGemAttribute('8145', level)['atSpiritBase'] for level in range(1, 9)],
                         [2, 4, 6, 8, 10, 12, 19, 28])
        with patch.dict(info.attrib, {'negative': ['atSpiritBase', '-225'],
                                    'threat': ['atActiveThreatCoefficient', '500']}):
            self.assertEqual(info.getGemAttribute('negative', 1)['atSpiritBase'], -2)
            # Value1Strable=0, Value2Strable=1：Param0 保持原值。
            self.assertEqual(info.getGemAttribute('threat', 8)['atActiveThreatCoefficient'], 500)

    def test_all_ordinary_enchant_attributes_are_read(self):
        text = equipment_text({'12': [111692, 0, 35, 16543, 0, 0, 0, 0]})
        result = self.ac.CalculateAll(text)
        self.assertEqual(result['atMaxLifeBase'], 2)
        self.assertEqual(result['atPhysicsShieldBase'], 23)
        self.assertEqual(result['atSpiritBase'], 165 + 72)

    def test_old_script_enchant_does_not_invent_241_healing(self):
        result = self.ac.CalculateAll(equipment_text({'12': [111692, 0, 11272, 0, 0, 0, 0, 0]}))
        self.assertNotIn('atTherapyPowerBase', result)
        self.assertTrue(any('11272' in warning for warning in self.ac.lastWarnings))

    def test_set_columns_retain_actual_piece_thresholds(self):
        self.assertEqual(self.ac.equipmentInfo.set['633'], [(2, '115508'), (4, '111190'), (6, '26521')])
        self.assertEqual([count for count, _ in self.ac.equipmentInfo.set['650']], [2, 2, 4])
        feature = {'set': '633', 'DiamondAttributeID1': '', 'DiamondAttributeID2': '', 'DiamondAttributeID3': ''}
        with patch.object(self.ac.equipmentInfo, 'getFeature', return_value=feature):
            for count, expected_toughness, expected_decrit in [(2, 8, 0), (3, 8, 0), (4, 8, 10)]:
                slots = ImportExcelEquipment().orderTable[:count]
                result = self.ac.CalculateAll(equipment_text({pos: [1, 0, 0, 0, 0, 0, 0, 0] for pos in slots}))
                self.assertEqual(result.get('atToughnessBase', 0), expected_toughness)
                self.assertEqual(result.get('atDecriticalDamagePowerBase', 0), expected_decrit)

    def test_five_color_needs_both_count_and_intensity_and_applies_once(self):
        info = self.ac.equipmentInfo
        self.assertEqual(info.color['25469'][:8], ['atSpiritBase', '104', '16', '90', 'atTherapyCoefficient', '102', '18', '108'])
        feature = {'set': '', 'DiamondAttributeID1': '8145', 'DiamondAttributeID2': '8145', 'DiamondAttributeID3': '8145'}
        slots = ['0', '2', '3', '4', '5', '6']
        with patch.object(info, 'getFeature', return_value=feature):
            for level, bonus, coefficient in [(4, 0, 0), (5, 104, 0), (6, 104, 102)]:
                text = equipment_text({pos: [1, 0, 0, 0, level, level, level, 25469] for pos in slots})
                result = self.ac.CalculateAll(text)
                gem = {4: 8, 5: 10, 6: 12}[level]
                self.assertEqual(result['atSpiritBase'], 18 * gem + bonus)
                self.assertEqual(result.get('atTherapyCoefficient', 0), coefficient)

    def test_invalid_sockets_cannot_activate_five_color(self):
        feature = {'set': '', 'DiamondAttributeID1': '8145', 'DiamondAttributeID2': '0', 'DiamondAttributeID3': '0'}
        slots = ['0', '2', '3', '4', '5', '6']
        with patch.object(self.ac.equipmentInfo, 'getFeature', return_value=feature):
            result = self.ac.CalculateAll(equipment_text({pos: [1, 0, 0, 0, 8, 8, 8, 25469] for pos in slots}))
        self.assertEqual(result['atSpiritBase'], 6 * 28)
        self.assertNotIn('atTherapyCoefficient', result)

    def test_empty_slots_are_valid_but_unknown_current_items_are_errors(self):
        self.assertEqual(self.ac.CalculateAll(''), {})
        self.assertEqual(self.ac.CalculateAll(equipment_text({}) + '\n'), {})
        with self.assertRaises(KeyError):
            self.ac.CalculateAll(equipment_text({'0': [999999999, 0, 0, 0, 0, 0, 0, 0]}))


if __name__ == '__main__':
    unittest.main()

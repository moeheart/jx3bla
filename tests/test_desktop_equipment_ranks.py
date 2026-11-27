import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from data.DisplayRanks import desktop_percentiles
from equip.EquipmentExport import EquipmentAnalyser, forge_tooltip
from tools.ValidateCleanupReplays import baseline_differences, digest


class EquipmentSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.equipment = EquipmentAnalyser()

    @staticmethod
    def item(category, number, stars=6):
        return {'id_cat': str(category), 'id': str(number), 'star': stars, 'magic1': '', 'magic2': ''}

    def test_formal_items_use_set_ids_and_actual_simple_marker(self):
        # 112444 is 迟舟护腰·尊 (精简, maximum six); 49922 and 47942 belong
        # to other item tables. Slot 24 is horse gear and cannot add a fourth piece.
        gear = {'8': self.item(7, 112444), '6': self.item(8, 49922),
                '2': self.item(6, 47942, 3), '24': self.item(7, 112444),
                '11': self.item(7, 112035), '7': self.item(8, 50323)}
        sketch = self.equipment.getSketch(gear)
        self.assertEqual(sketch, '无套装，3白字，0黄字')
        self.assertTrue(self.equipment.getForge(gear).startswith('4/'))

    def test_effective_set_tier_weapon_and_yellow_effects(self):
        item = self.item
        gear = {'11': item(7, 112035), '4': item(7, 112305), '8': item(7, 112003),
                '5': item(8, 51490), '9': item(8, 49916), '0': item(6, 46720)}
        self.assertEqual(self.equipment.getSketch(gear), '2件套，0白字，2黄字，水特效')
        gear.update({'3': item(7, 112099), '0': item(6, 47732)})
        self.assertEqual(self.equipment.getSketch(gear), '4件套，0白字，2黄字，大橙武')

    def test_all_twelve_enchant_slots_quality_roles_and_major_count(self):
        ids = {'0': '16488', '2': '16626', '3': '16565', '4': '16517', '5': '16633',
               '6': '16621', '7': '16375', '8': '16501', '9': '16638', '10': '16493',
               '11': '16577', '12': '16540'}
        gear = {slot: {**self.item(7, 112035), 'magic1': enchant, 'magic2': '16670'}
                for slot, enchant in ids.items()}
        gear['1'] = gear['5']
        self.assertEqual(self.equipment.getForge(gear, '2h').split('/')[3:], ['2-3-3-2', '5'])
        self.assertEqual(self.equipment.getForge(gear, '3tw').split('/')[3:], ['2-4-4-2', '5'])
        self.assertIn('挑战 / 精品 / 紫色 / 蓝色及以下附魔　2 / 3 / 3 / 2',
                      forge_tooltip(self.equipment.getForge(gear, '2d')))
        self.assertIn('旧版', forge_tooltip('11/0-0-18/6/3-2/001020'))


class DisplayPercentileTests(unittest.TestCase):
    def setUp(self):
        self.actor = SimpleNamespace(
            timestamp=1795673277, mapDetail='25人普通洛阳之战', bossAnalyseName='突利和顺',
            attributeStatus={'staticAttributes': 'available', 'unmodeledEffects': ['特效']},
            statDict=[{'name': '甲', 'occ': '2h'}, {'name': '乙', 'occ': '2d'}],
            combatTracker={'rdps': {'player': {'42': {'name': '甲', 'dps': 25.9}}},
                           'rhps': {'player': {'42': {'name': '甲', 'hps': 89}}}})
        self.key = 'lijingyidao-835-突利和顺-stat-rdps-161'
        self.sample = {'num': 23, 'value': json.dumps([i + 0.5 for i in range(101)])}

    def test_logs_uses_full_fight_integer_rdps_for_healers(self):
        ranks = desktop_percentiles(self.actor, {self.key: self.sample})
        self.assertEqual(ranks['甲'], {'scope': 'logs', 'metric': 'rdps', 'edition': '161',
                                     'percent': 24, 'num': 23, 'reference': True,
                                     'basis': 'unmodeled_effects'})
        self.assertNotIn('乙', ranks)

    def test_no_other_season_difficulty_metric_or_party_fallback(self):
        rates = {self.key.replace('stat-rdps', 'general-rdps'): self.sample,
                 self.key.replace('835', '836'): self.sample,
                 self.key.replace('rdps', 'rhps'): self.sample,
                 self.key.replace('161', '160'): self.sample}
        self.assertEqual(desktop_percentiles(self.actor, rates), {})
        self.actor.timestamp = 1791000000
        self.actor.attributeStatus = {}
        self.assertEqual(desktop_percentiles(self.actor, rates)['甲']['edition'], '160')

    def test_quality_and_missing_measurements_do_not_fabricate_zero_percent(self):
        self.actor.attributeStatus['targetProfileUnavailable'] = True
        rates = {self.key: self.sample, self.key.replace('lijingyidao', 'huajianyou'): self.sample}
        ranks = desktop_percentiles(self.actor, rates)
        for name in ('甲', '乙'):
            self.assertEqual(ranks[name]['basis'], 'unavailable')
            self.assertNotIn('percent', ranks[name])

    def test_partial_equipment_requires_evidence_of_attribution(self):
        self.actor.attributeStatus.update(missingEquipmentPlayers={'42': {'hasReference': False}})
        rates = {self.key: self.sample}
        self.assertNotIn('percent', desktop_percentiles(self.actor, rates)['甲'])
        self.actor.combatTracker['ndps'] = {'player': {'42': {'dps': 14}}}
        self.assertEqual(desktop_percentiles(self.actor, rates)['甲']['basis'], 'partial_attribution')

    def test_repeated_thresholds_use_online_tie_rule_and_allow_real_p0(self):
        sample = {'num': 1, 'value': [25] * 101}
        self.assertEqual(desktop_percentiles(self.actor, {self.key: sample})['甲']['percent'], 100)
        self.actor.combatTracker['rdps']['player']['42']['dps'] = 24
        self.assertEqual(desktop_percentiles(self.actor, {self.key: sample})['甲']['percent'], 0)


class MigrationEvidenceTests(unittest.TestCase):
    def test_original_and_new_hashes_accept_only_the_approved_display_fields(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'9.0').mkdir()
            path = root/'160'/'baseline.json'
            actor = SimpleNamespace(statDict=[{'name':'甲', 'occ':'2h', 'rdps':42, 'equip':{'sketch':'新'}}])
            expected = {'teamTableSha256':'old'}
            actual = {'teamTableSha256':digest(actor.statDict)}
            record = {'source':'known', 'originalTeam':'old', 'updatedTeam':actual['teamTableSha256'],
                      'excludingPresentation':digest([{'name':'甲', 'occ':'2h', 'rdps':42, 'equip':{}}])}
            (root/'9.0'/'装备摘要回归.json').write_text(json.dumps({'cases':[record]}), encoding='utf8')
            self.assertEqual(baseline_differences(actor, actual, expected, 'known', path), [])
            self.assertEqual(baseline_differences(actor, actual, expected, 'other', path), ['teamTableSha256'])
            actor.statDict[0]['rdps'] = 43
            self.assertEqual(baseline_differences(actor, actual, expected, 'known', path), ['teamTableSha256'])

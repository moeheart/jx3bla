import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from data.DisplayRanks import desktop_percentiles
from equip.EquipmentExport import EquipmentAnalyser
from tools.Attribute import CURRENT_GAME_EDITION
from tools.RecordQuality import is_metric_rank_eligible
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
        self.assertIn('3精简', sketch)
        self.assertIn('元元·素芷×1', sketch)
        self.assertIn('独镇乾坤·逆川×1', sketch)
        self.assertTrue(self.equipment.getForge(gear).startswith('4/'))


class DisplayPercentileTests(unittest.TestCase):
    def actor(self, rates=None):
        def table(field, rows):
            return {'player': {i: {'name': name, field: value} for i, (name, value) in enumerate(rows)}}
        members = [('甲', '2d'), ('乙', '2d'), ('丙', '2d'), ('丁', '2h'), ('戊', '5h'), ('己', '1t')]
        return SimpleNamespace(
            attributeStatus={'status': 'incomplete', 'staticAttributes': 'available', 'unmodeledEffects': ['特效']},
            mapDetail='25人普通洛阳之战', bossAnalyseName='突利和顺',
            window=SimpleNamespace(stat_percent=rates or {}),
            statDict=[{'name': n, 'occ': o} for n, o in members],
            combatTracker=SimpleNamespace(rdps=table('dps', [('甲', 25), ('乙', 75), ('丙', 75), ('己', 99)]),
                                          rhps=table('hps', [('丁', 2), ('戊', 3)])))

    def test_historical_reference_preserves_official_sample_ineligibility(self):
        key = f'huajianyou-835-突利和顺-general-rdps-{CURRENT_GAME_EDITION}'
        actor = self.actor({key: {'num': 222, 'value': json.dumps(list(range(101)))}})
        rank = desktop_percentiles(actor)['甲']
        self.assertEqual(rank, {'scope': 'historical', 'metric': 'rdps', 'percent': 25,
                                'num': 222, 'cohort': '同心法', 'reference': True})
        self.assertFalse(is_metric_rank_eligible(actor.attributeStatus, 'rdps'))
        self.assertTrue(all('displayRanks' not in row for row in actor.statDict))

    def test_local_fallback_excludes_self_and_other_roles_and_credits_ties(self):
        ranks = desktop_percentiles(self.actor())
        self.assertEqual((ranks['乙']['percent'], ranks['乙']['num'], ranks['乙']['scope']), (75, 2, 'team'))
        self.assertEqual((ranks['戊']['metric'], ranks['戊']['percent'], ranks['戊']['num']), ('rhps', 100, 1))
        self.assertNotIn('己', ranks)

    def test_unusable_attribution_has_no_damage_percentile(self):
        actor = self.actor()
        actor.attributeStatus.update(targetProfileUnavailable=True)
        ranks = desktop_percentiles(actor)
        self.assertNotIn('甲', ranks)
        self.assertIn('丁', ranks)


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

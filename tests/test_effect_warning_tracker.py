"""Tracker quality retains effect-only reference results and real data gaps."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from data.DataContent import SingleDataSkill
from replayer.CombatTracker import CombatTracker
from tests import test_target_boost_sources as source_fixtures
from tools.RecordQuality import get_record_quality, is_effect_warning_only, is_metric_rank_eligible


EFFECT = 'synthetic equipment: atSkillEventHandler'


class EffectWarningTrackerTests(unittest.TestCase):
    def tracker(self, gap=None):
        fixture = source_fixtures.TargetBoostSourceTests().tracker('25人普通洛阳之战')
        info = fixture.info
        history = SimpleNamespace(badPeriodDpsLog=[], badPeriodHealerLog=[],
            critPeriodHealerLog=[], critPeriodSum=0, mainTargets=['boss'],
            startTime=0, finalTime=10000)
        base = {player: {'_raw': {'atPhysicsAttackPowerBase': 1000,
                                'atSolarAttackPowerBase': 1000}} for player in info.player}
        base['fs'].update(_warnings=[EFFECT], _unmodeledEffects=[EFFECT])
        if gap == 'missing':
            base['self'] = None
        elif gap == 'unparsed':
            base['self']['_warnings'] = ['synthetic invalid static field']
        elif gap == 'estimated':
            base['self']['_estimated'] = {'source': 'synthetic same-kungfu average'}
        arguments = (info, history, fixture.occDetailList, {}, {},
            {key: {'id': '0', 'stack': 0} for key in ('zxyz', 'qs', 'zzm')}, base)
        if gap == 'target_profiles':
            with patch('replayer.CombatTracker.get_target_profiles', return_value={}):
                tracker = CombatTracker(*arguments)
        else:
            tracker = CombatTracker(*arguments)
        for counter in tracker.boostCounter.values():
            counter.boost.clear()
        return tracker

    def damage(self, tracker, target='boss', amount=1200):
        event = SingleDataSkill()
        event.setByJcl(['', '16', '1793577600', '1000', '21', {
            '1': 'self', '2': target, '3': '0', '4': '1', '5': '999', '6': '1',
            '9': {'0': str(amount), '13': str(amount)}}])
        tracker.recordSkill(event)

    def export(self, tracker):
        tracker.export(10000, 10000, 10000, {})
        return tracker.generateJson()

    def assert_quality(self, value, reference):
        # Repeat normalization because server caches/exported summaries are
        # fed back into the same helper; no blocker may disappear in transit.
        values = [value, get_record_quality(value)]
        values.append(get_record_quality(values[-1]))
        for data in values:
            self.assertEqual(is_effect_warning_only(data), reference)
            self.assertFalse(get_record_quality(data)['precise'])
            for metric in ('score', 'rdps', 'mrdps'):
                self.assertFalse(is_metric_rank_eligible(data, metric))
            for metric in ('ndps', 'mndps', 'hps'):
                self.assertTrue(is_metric_rank_eligible(data, metric))

    def test_effect_only_status_and_export_preserve_calculated_reference_rdps(self):
        tracker = self.tracker()
        self.assertEqual(tracker.rdpsStatus['staticAttributes'], 'available')
        self.assertEqual(tracker.rdpsStatus['unmodeledEffects'], [EFFECT])
        self.assert_quality(tracker.rdpsStatus, True)
        tracker.boostCounter['self'].addBoost('2,15413,18',
            {'atPhysicsAttackPowerBase': 200}, 'fs', 1, 0)
        self.damage(tracker)
        result = self.export(tracker)
        self.assertAlmostEqual(result['ndps']['player']['self']['sum'], 1200)
        self.assertAlmostEqual(result['rdps']['player']['self']['sum'], 1000)
        self.assertAlmostEqual(result['rdps']['player']['fs']['sum'], 200)
        for data in (result['rdpsStatus'], result['rdps'], result['mrdps'], {'act': result}):
            self.assert_quality(data, True)

    def test_static_data_gaps_are_not_reclassified_as_only_effect_warnings(self):
        for gap in ('missing', 'unparsed', 'estimated', 'target_profiles'):
            with self.subTest(gap=gap):
                tracker = self.tracker(gap)
                self.assertIn(EFFECT, tracker.rdpsStatus['unmodeledEffects'])
                self.assert_quality(tracker.rdpsStatus, False)
                result = self.export(tracker)
                for data in (result['rdpsStatus'], result['rdps'], {'act': result}):
                    self.assert_quality(data, False)
                if gap in ('missing', 'unparsed'):
                    self.assertEqual(result['rdpsStatus']['staticAttributes'], 'partial')
                elif gap == 'estimated':
                    self.assertIn('self', result['rdpsStatus']['estimatedPlayers'])
                    self.assertTrue(get_record_quality(result)['estimated'])
                else:
                    self.assertTrue(result['rdpsStatus']['targetProfileUnavailable'])

    def test_unknown_target_found_during_damage_survives_export_normalization(self):
        tracker = self.tracker()
        self.assert_quality(tracker.rdpsStatus, True)
        tracker.boostCounter['self'].targetProfiles.pop('other')
        self.damage(tracker, target='other')
        self.assertIn('other', tracker.boostCounter['self'].unresolvedTargets)
        result = self.export(tracker)
        self.assertEqual(result['rdpsStatus']['unresolvedTargets'], ['other'])
        for data in (result['rdpsStatus'], result['rdps'], {'act': result}):
            self.assert_quality(data, False)


if __name__ == '__main__':
    unittest.main()

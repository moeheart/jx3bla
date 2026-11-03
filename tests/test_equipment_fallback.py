"""Missing gear uses a marked, source-backed average without official ranking."""
from copy import deepcopy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import json
import hashlib
import math

from data.DataContent import OverallData
from equip.CangshengAttributeData import make_base_attributes, static_attributes
from equip.EquipmentFallback import (
    EQUIPMENT_FALLBACK_WARNING, REQUIRED_EQUIPMENT_SLOTS, average_equipment_data,
    make_average_base_attributes, missing_equipment_slots,
)
from equip.EquipmentExport import ImportExcelEquipment
from replayer.ActorReplayPro import ActorProReplayer
from replayer.CombatTracker import CombatTracker
from replayer.ReplayerBase import RankCalculator, ReplayerBase
from release.AverageEquipmentGenerator import (
    build_average_equipment, read_player_equipment, main as generate_average_equipment,
)
from tools.ValidateLuoyang import ValidationWindow


ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP = ROOT / '.tmp/average-equipment-fallback/test-temp'


class AverageEquipmentResourceTests(unittest.TestCase):
    def test_shipped_current_profiles_apply_each_kungfus_native_attributes(self):
        data = average_equipment_data()
        self.assertEqual((data['gameEdition'], data['profile'], data['level']), (161, 'cangsheng50', 50))
        self.assertGreater(data['sourceFileCount'], 0)
        self.assertEqual(data['clientVersion'], '1.6.0.10009')
        self.assertTrue(all(row['clientMode'] == 'zhcn_hd' for row in data['sourceFiles']))
        self.assertTrue(all(date >= '2026-10-29' for date in data['sourceDates']))
        for occ in set(data['occupations']) | set(data['aliases']):
            with self.subTest(occ=occ):
                sample_occ = data['aliases'].get(occ, occ)
                sample = data['occupations'][sample_occ]
                expected = make_base_attributes(sample['equipment'], occ)
                actual = make_average_base_attributes(occ)
                self.assertEqual(actual['_raw'], expected['_raw'])
                self.assertEqual(actual['_estimated']['occ'], occ)
                self.assertEqual(actual['_estimated']['sampleOcc'], sample_occ)
                self.assertEqual(actual['_estimated']['sampleCount'], sample['sampleCount'])
                self.assertEqual(actual['_estimated']['warning'], EQUIPMENT_FALLBACK_WARNING)
                self.assertTrue(all(math.isfinite(value) for value in actual['_raw'].values()))
        for occ in ('10t', '22d', '22h', '24', '6d'):
            self.assertIsNotNone(make_average_base_attributes(occ))

    def test_mobile_alias_shares_only_equipment_and_keeps_own_kungfu(self):
        data = average_equipment_data()
        self.assertEqual(data['aliases']['6dw'], '6d')
        self.assertNotEqual(static_attributes('6dw'), static_attributes('6d'))
        normal = make_average_base_attributes('6d')
        mobile = make_average_base_attributes('6dw')
        self.assertNotEqual(normal['_raw'], mobile['_raw'])
        self.assertEqual(mobile['_raw'], make_base_attributes(data['occupations']['6d']['equipment'], '6dw')['_raw'])

    def test_returned_reference_cannot_pollute_other_players_or_resource_cache(self):
        data_before = deepcopy(average_equipment_data())
        initial = make_average_base_attributes('6d')
        altered = make_average_base_attributes('6d')
        altered['_raw']['atSpiritBase'] = -999999
        altered['_estimated']['sourceDates'].append('2099-01-01')
        self.assertEqual(make_average_base_attributes('6d'), initial)
        self.assertEqual(average_equipment_data(), data_before)

    def test_no_unrelated_kungfu_is_used_when_family_has_no_sample(self):
        for occ in (*average_equipment_data()['unavailableOccupations'], 'unknown'):
            with self.subTest(occ=occ):
                self.assertIsNone(make_average_base_attributes(occ))

    def test_corrupted_raw_average_is_rejected(self):
        examples = ({'atSpiritBase': float('nan')}, {'atSpiritBase': float('inf')},
                    {'atSpiritBase': True}, {'atSpiritBase': '1000'}, {'根骨': 1000}, {})
        for equipment in examples:
            with self.subTest(equipment=equipment):
                data = {'gameEdition': 161, 'level': 50,
                        'occupations': {'6d': {'equipment': equipment, 'sampleCount': 1}}}
                with patch('equip.EquipmentFallback.average_equipment_data', return_value=data):
                    with self.assertRaises(ValueError):
                        make_average_base_attributes('6d')
        with patch('equip.EquipmentFallback.average_equipment_data', return_value={
                'gameEdition': 161, 'level': 50,
                'occupations': {'6d': {'equipment': {'atSpiritBase': 1000}, 'sampleCount': 0}}}):
            with self.assertRaises(ValueError):
                make_average_base_attributes('6d')

    def test_old_season_average_is_rejected_before_calculation(self):
        for game_edition, level in ((130, 130), (161, 130), (130, 50), (160, 50)):
            data = {'gameEdition': game_edition, 'level': level, 'occupations': {}}
            with patch('equip.EquipmentFallback.average_equipment_data', return_value=data):
                with self.assertRaises(ValueError):
                    make_average_base_attributes('6d')

    def test_complete_gear_may_omit_only_the_optional_secondary_weapon(self):
        equipment = {slot: {'id': '100'} for slot in REQUIRED_EQUIPMENT_SLOTS}
        self.assertEqual(missing_equipment_slots(equipment), [])
        equipment['1'] = {'id': '0'}
        self.assertEqual(missing_equipment_slots(equipment), [])
        equipment['12']['id'] = '0'
        self.assertEqual(missing_equipment_slots(equipment), ['12'])
        equipment.pop('0')
        self.assertEqual(missing_equipment_slots(equipment), ['0', '12'])
        self.assertEqual(set(missing_equipment_slots({})), REQUIRED_EQUIPMENT_SLOTS)


def player_record(player_id, name, xinfa=10026, item=10, slots=None, has_equipment=True):
    if slots is None:
        slots = [*range(2, 13), 0]
    equipment = '{' + ','.join('{%d,7,%d,0,{},0,0}' % (pos, item) for pos in slots) + '}' if has_equipment else '{}'
    return '{%d,"%s",3,%d,18000,%s}' % (player_id, name, xinfa, equipment)


class AverageEquipmentSamplingTests(unittest.TestCase):
    def test_canonical_generation_refreshes_provenance_but_custom_output_is_isolated(self):
        result = {'clientVersion': '1.6.0.10009', 'clientMode': 'zhcn_hd',
                  'sourceDates': ['2026-11-02'], 'sourceFileCount': 1, 'sampleCount': 2,
                  'method': 'selected formal snapshots', 'sourceFiles': [{'file': 'sample.jcl'}],
                  'occupations': {}, 'aliases': {}, 'unavailableOccupations': [], 'exclusionCounts': {}}
        with self.temporary_directory() as directory:
            output = Path(directory) / 'average_equipment.json'
            manifest_path = output.parent / 'source_manifest.json'
            unrelated = {'name': 'other.tab', 'sha256': 'keep this source unchanged'}
            manifest_path.write_text(json.dumps({'files': [unrelated,
                {'name': output.name, 'sha256': 'stale', 'supported_samples': 1}]}), encoding='utf-8')
            with patch('release.AverageEquipmentGenerator.DEFAULT_OUTPUT', output), \
                    patch('release.AverageEquipmentGenerator.collect_paths', return_value=[]), \
                    patch('release.AverageEquipmentGenerator.build_average_equipment', return_value=(result, {})):
                with patch('sys.argv', ['AverageEquipmentGenerator', 'sample.jcl']):
                    generate_average_equipment()
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                self.assertEqual(manifest['files'][0], unrelated)
                self.assertEqual(len(manifest['files']), 2)
                entry = manifest['files'][1]
                self.assertEqual(entry['sha256'], hashlib.sha256(output.read_bytes()).hexdigest())
                self.assertEqual(entry['bytes'], output.stat().st_size)
                self.assertEqual(entry['supported_samples'], 2)
                self.assertEqual(entry['source_dates'], ['2026-11-02'])
                before = manifest_path.read_bytes()
                custom_output = output.parent / 'preview.json'
                with patch('sys.argv', ['AverageEquipmentGenerator', 'sample.jcl', '--output', str(custom_output)]):
                    generate_average_equipment()
                self.assertTrue(custom_output.is_file())
                self.assertEqual(manifest_path.read_bytes(), before)

    def write_log(self, directory, suffix, records):
        path = Path(directory) / ('2026-11-02-21-%s-25人普通洛阳之战(835)-田承嗣(139329).jcl' % suffix)
        header = '0\t0\t0\t0\t1\t{1,"zhcn_hd::formal_test::1793620894",0}'
        lines = [header] + ['%d\t%d\t0\t%d\t4\t%s' % (index, index, index, record)
                            for index, record in enumerate(records, 1)]
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return path

    def temporary_directory(self):
        TEST_TEMP.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=TEST_TEMP)

    def test_metadata_name_arriving_after_equipment_does_not_lose_equipment(self):
        with self.temporary_directory() as directory:
            path = self.write_log(directory, '00-00', [player_record(1, ''),
                                  player_record(1, 'Alpha', has_equipment=False)])
            source, players = read_player_equipment(path)
        self.assertEqual(players['1']['name'], 'Alpha')
        self.assertEqual(players['1']['server'], 'formal_test')
        self.assertEqual(len(players['1']['equipment']), 12)
        self.assertEqual(len(source['sha256']), 64)

    def test_nonformal_or_unknown_client_cannot_be_relabelled_as_formal_average(self):
        with self.temporary_directory() as directory:
            for mode in ('zhcn_exp', 'zhcn_classic', ''):
                with self.subTest(mode=mode):
                    path = self.write_log(directory, '00-00', [player_record(1, 'Alpha')])
                    path.write_text(path.read_text(encoding='utf-8').replace('zhcn_hd', mode), encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, 'formal-server'):
                        build_average_equipment([path])

    def test_latest_supported_character_snapshot_has_one_vote_and_missing_fields_are_zero(self):
        class FakeCal:
            def __init__(self, edition):
                self.lastWarnings = []

            def CalculateAll(self, equipment):
                item = int(equipment.split('\t', 1)[0])
                self.lastWarnings = ['unsupported script'] if item == 99 else []
                if item == 999:
                    return {}
                raw = {'atPhysicsAttackPowerBase': item}
                if item == 50:
                    raw['atPhysicsCriticalStrike'] = 100
                return raw

        with self.temporary_directory() as directory:
            older = self.write_log(directory, '00-00', [player_record(1, 'Alpha', item=10)])
            newer = self.write_log(directory, '01-00', [player_record(999, 'Alpha', item=30),
                                   player_record(1, 'Beta', item=50),
                                   player_record(10, 'Mobile', xinfa=100406, item=200)])
            last = self.write_log(directory, '02-00', [player_record(999, 'Alpha', item=99),
                                  player_record(20, 'Partial', slots=[2]),
                                  player_record(21, 'Absent', has_equipment=False),
                                  player_record(22, 'NoAttributes', item=999)])
            with patch('release.AverageEquipmentGenerator.AttributeCal', FakeCal):
                data, audit = build_average_equipment([older, newer, last])
        normal = data['occupations']['3d']
        self.assertEqual(normal['sampleCount'], 2)
        self.assertEqual(normal['equipment'], {'atPhysicsAttackPowerBase': 40, 'atPhysicsCriticalStrike': 50})
        self.assertEqual(data['occupations']['3dw']['sampleCount'], 1)
        self.assertEqual(data['occupations']['3dw']['equipment']['atPhysicsAttackPowerBase'], 200)
        self.assertEqual(data['sampleCount'], 3)
        self.assertEqual(len({(row['characterKeySHA256'], row['occ']) for row in audit['selectedSamples']}), 3)
        self.assertEqual(data['exclusionCounts'], {'unsupported_effects': 1, 'missing_slots': 1,
                                                 'missing_equipment': 1, 'missing_attributes': 1})


class EstimatedReplayTests(unittest.TestCase):
    def make_actor(self, scripted_gear=False):
        info = OverallData()
        info.map = '25人普通洛阳之战'
        info.server = 'test'
        info.battleTime = 1793620894
        info.sumTime = 10000
        info.addPlayer('missing', 'Missing', '6', '10175')
        if scripted_gear:
            info.addPlayer('scripted', 'Scripted', '22', '10448')
            importer = ImportExcelEquipment()
            full_gear = {}
            for index, (position, category) in enumerate(zip(importer.orderTable, importer.scemeTable), 1):
                if position == '1':
                    continue
                full_gear[str(index)] = {'1': position, '2': category,
                    '3': {'7': '111692', '8': '46253', '6': '18'}[category], '4': '0',
                    '5': {}, '6': '11272' if position == '12' else '0', '7': '0'}
            info.player['scripted'].equip = full_gear
        info.npc = {'boss': SimpleNamespace(name='田承嗣', templateID='139329')}
        actor = ActorProReplayer.__new__(ActorProReplayer)
        actor.window = ValidationWindow()
        actor.bld = SimpleNamespace(info=info, log=[SimpleNamespace(dataType='Battle', time=time) for time in (0, 10000)])
        actor.mapDetail = info.map
        actor.gameEdition = 161
        actor.bossname = actor.bossAnalyseName = '田承嗣'
        actor.win = 1
        return actor

    def tracker(self, actor, extra_unresolved=False):
        info = actor.bld.info
        bases = dict(actor.baseAttribDict)
        occupations = dict(actor.occDetailList)
        if extra_unresolved:
            info.addPlayer('unresolved', 'No family sample', '9', '10268')
            bases['unresolved'] = None
            occupations['unresolved'] = '9'
        history = SimpleNamespace(badPeriodDpsLog=[], badPeriodHealerLog=[], critPeriodHealerLog=[],
                                  critPeriodSum=0, mainTargets=['boss'], startTime=0, finalTime=10000)
        return CombatTracker(info, history, occupations, {}, {},
                             {key: {'id': '0', 'stack': 0} for key in ('zxyz', 'qs', 'zzm')}, bases)

    def test_missing_gear_gets_estimate_without_creating_real_panel_or_cache(self):
        actor = self.make_actor()
        actor.FirstStageAnalysis()
        self.assertEqual(actor.attributeStatus['status'], 'estimated')
        self.assertEqual(set(actor.attributeStatus['estimatedPlayers']), {'missing'})
        self.assertIn('_estimated', actor.baseAttribDict['missing'])
        self.assertIsNone(actor.panelAttribDict['missing'])
        self.assertEqual(actor.bld.info.player['missing'].equip, {})
        self.assertNotIn('missing', actor.window.playerEquipment)
        self.assertEqual(actor.window.playerEquipmentAnalysed['missing']['status'], 'notfound')
        tracker = self.tracker(actor)
        self.assertEqual(tracker.rdpsStatus['status'], 'estimated')
        self.assertEqual(tracker.rdpsStatus['warning'], EQUIPMENT_FALLBACK_WARNING)

    def test_estimated_metadata_survives_additional_incomplete_equipment(self):
        actor = self.make_actor(scripted_gear=True)
        actor.FirstStageAnalysis()
        self.assertEqual(actor.attributeStatus['status'], 'incomplete')
        self.assertEqual(set(actor.attributeStatus['estimatedPlayers']), {'missing'})
        self.assertNotIn('_estimated', actor.baseAttribDict['scripted'])
        self.assertEqual(actor.baseAttribDict['scripted']['_warnings'], ['附魔11272: atExecuteScript'])
        tracker = self.tracker(actor, extra_unresolved=True)
        self.assertEqual(tracker.rdpsStatus['status'], 'incomplete')
        self.assertEqual(set(tracker.rdpsStatus['estimatedPlayers']), {'missing'})
        self.assertEqual(tracker.rdpsStatus['warning'], EQUIPMENT_FALLBACK_WARNING)

    def test_nonempty_partial_gear_also_gets_marked_estimate(self):
        actor = self.make_actor(scripted_gear=True)
        raw = actor.bld.info.player['scripted'].equip
        missing_entry = next(key for key, row in raw.items() if row['1'] == '12')
        raw.pop(missing_entry)
        original = deepcopy(raw)
        actor.FirstStageAnalysis()
        self.assertEqual(actor.attributeStatus['status'], 'estimated')
        self.assertEqual(actor.baseAttribDict['scripted']['_estimated']['missingSlots'], ['12'])
        self.assertIsNone(actor.panelAttribDict['scripted'])
        self.assertEqual(actor.bld.info.player['scripted'].equip, original)
        self.assertEqual(actor.window.playerEquipment['scripted'], original)
        self.assertNotIn('12', actor.jsonEquip['scripted'])

    def actor_with_complete_gear(self):
        actor = self.make_actor(scripted_gear=True)
        actor.bld.info.player['missing'].equip = deepcopy(actor.bld.info.player['scripted'].equip)
        for row in actor.bld.info.player['missing'].equip.values():
            row['6'] = '0'
        del actor.bld.info.player['scripted']
        actor.FirstStageAnalysis()
        self.assertEqual(actor.attributeStatus['status'], 'supported')
        self.assertIsNotNone(actor.panelAttribDict['missing'])
        return actor

    def test_same_character_can_reuse_real_gear_between_bosses(self):
        previous = self.actor_with_complete_gear()
        actor = self.make_actor()
        actor.window = previous.window
        actor.FirstStageAnalysis()
        self.assertEqual(actor.attributeStatus['status'], 'supported')
        self.assertNotIn('_estimated', actor.baseAttribDict['missing'])
        self.assertEqual(actor.baseAttribDict['missing'], previous.baseAttribDict['missing'])
        self.assertIsNotNone(actor.panelAttribDict['missing'])

    def test_reused_actor_id_or_unowned_cache_cannot_supply_someone_elses_gear(self):
        for changed in ('name', 'server', 'unowned'):
            with self.subTest(changed=changed):
                previous = self.actor_with_complete_gear()
                actor = self.make_actor()
                actor.window = previous.window
                if changed == 'name':
                    actor.bld.info.player['missing'].name = 'Different character'
                elif changed == 'server':
                    actor.bld.info.server = 'different server'
                else:
                    del actor.window.playerEquipmentOwners
                actor.FirstStageAnalysis()
                self.assertEqual(actor.attributeStatus['status'], 'estimated')
                self.assertIn('_estimated', actor.baseAttribDict['missing'])
                self.assertIsNone(actor.panelAttribDict['missing'])
                self.assertEqual(actor.bld.info.player['missing'].equip, {})

    def test_no_family_sample_keeps_missing_gear_unresolved_without_fake_panel(self):
        actor = self.make_actor()
        actor.bld.info.player['missing'].occ = '9'
        actor.bld.info.player['missing'].xinfaCode = '10268'
        actor.FirstStageAnalysis()
        self.assertIsNone(actor.baseAttribDict['missing'])
        self.assertIsNone(actor.panelAttribDict['missing'])
        tracker = self.tracker(actor)
        self.assertEqual(tracker.rdpsStatus['status'], 'incomplete')
        self.assertNotIn('estimatedPlayers', tracker.rdpsStatus)
        self.assertEqual(tracker.boostCounter['missing'].getRate('boss', 'all', '攻击'),
                         {'self': {'source': 'missing', 'rate': 1.0}})

    def test_partial_gear_without_family_sample_is_not_a_complete_panel(self):
        actor = self.make_actor(scripted_gear=True)
        player = actor.bld.info.player['scripted']
        player.occ, player.xinfaCode = '9', '10268'
        player.equip.pop(next(key for key, row in player.equip.items() if row['1'] == '12'))
        actor.FirstStageAnalysis()
        self.assertNotIn('_estimated', actor.baseAttribDict['scripted'])
        self.assertIn(EQUIPMENT_FALLBACK_WARNING, actor.baseAttribDict['scripted']['_warnings'])
        self.assertIsNone(actor.panelAttribDict['scripted'])
        self.assertEqual(self.tracker(actor).rdpsStatus['status'], 'incomplete')

    def test_estimated_group_and_player_replays_never_enqueue_official_uploads(self):
        for status in ({'status': 'estimated', 'estimatedPlayers': {'missing': {}}},
                       {'status': 'incomplete'},
                       {'status': 'supported', 'estimatedPlayers': {'missing': {}}}):
            with self.subTest(status=status):
                actor = ActorProReplayer.__new__(ActorProReplayer)
                actor.win, actor.attributeStatus = 1, status
                actor.window = SimpleNamespace(addUploadData=Mock())
                actor.prepareUpload()
                actor.window.addUploadData.assert_not_called()
                replay = ReplayerBase.__new__(ReplayerBase)
                replay.win, replay.actorData = 1, {'attributeStatus': actor.attributeStatus}
                replay.window = actor.window
                replay.prepareUpload()
                replay.window.addUploadData.assert_not_called()

    def test_estimate_hides_attribute_rank_but_direct_damage_percentile_remains(self):
        percent_data = {'6d-835-田承嗣-stat-%s-161' % key: {'num': 100, 'value': json.dumps(list(range(102)))}
                        for key in ('rdps', 'mrdps', 'score', 'ndps', 'mndps', 'hps', 'rhps')}
        for status in ({'status': 'estimated'}, {'status': 'incomplete'},
                       {'status': 'incomplete', 'estimatedPlayers': {'missing': {}}}):
            with self.subTest(status=status):
                rank = RankCalculator({'overall': {'attributeStatus': status}}, percent_data, 161)
                for key in ('rdps', 'mrdps', 'score'):
                    self.assertEqual(rank.getSkillPercent('6d', '835', '田承嗣', 'stat', key, 70), (0, -1))
                for key in ('ndps', 'mndps', 'hps', 'rhps'):
                    self.assertEqual(rank.getSkillPercent('6d', '835', '田承嗣', 'stat', key, 70), (100, 70))
        rank = RankCalculator({'overall': {}}, percent_data, 161)
        self.assertEqual(rank.getSkillPercent('6d', '835', '田承嗣', 'stat', 'rdps', 70), (100, 70))

    def test_unresolved_status_reaches_personal_ranks_even_without_any_estimate(self):
        replay = ReplayerBase.__new__(ReplayerBase)
        status = {'status': 'incomplete', 'reason': 'No sample for this kungfu'}
        replay.actorData = {'attributeStatus': status}
        replay.result = {'overall': {'map': '25人普通洛阳之战', 'boss': '田承嗣'},
                         'skill': {'stat': {'rdps': 70, 'ndps': 70}}, 'review': {'score': 70}}
        replay.gameEdition = 161
        replay.window = SimpleNamespace(stat_percent={
            '6d-835-田承嗣-stat-%s-161' % key: {'num': 100, 'value': json.dumps(list(range(102)))}
            for key in ('rdps', 'ndps', 'score')})
        replay.getRankFromStat('6d')
        self.assertEqual(replay.result['overall']['attributeStatus'], status)
        self.assertEqual(replay.rank['stat']['rdps'], {'num': 0, 'percent': -1})
        self.assertEqual(replay.rank['stat']['ndps'], {'num': 100, 'percent': 70})
        self.assertEqual(replay.getScoreRankFromStat('6d')['score'], {'num': 0, 'percent': -1})


if __name__ == '__main__':
    unittest.main()

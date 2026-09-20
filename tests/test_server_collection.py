"""Server collection regressions: no real DB, network, or replay-file writes."""
import contextlib
import copy
import csv
from datetime import datetime, timedelta, timezone
import importlib
import io
import json
import re
import unittest
from unittest.mock import MagicMock, mock_open, patch


MAPS = {'828': '10人普通洛阳之战', '835': '25人普通洛阳之战', '836': '25人英雄洛阳之战'}
INITIAL = 1793228400
FIRST_NERF = 1797807600
BOUNDARIES = ((INITIAL - 1, '160'), (INITIAL, '161'), (INITIAL + 1, '161'),
              (FIRST_NERF - 1, '161'), (FIRST_NERF, '162'), (FIRST_NERF + 1, '162'))


class RecordingCursor:
    def __init__(self, fail_on=None):
        self.queries = []
        self.last = ''
        self.fail_on = fail_on

    def execute(self, sql, *args):
        self.last = sql
        self.queries.append(sql)
        if self.fail_on and self.fail_on in sql:
            raise RuntimeError('simulated database failure')

    def fetchall(self):
        if 'FROM PreloadInfo' in self.last:
            return [('version', '8.16.0'), ('announcement', 'collection enabled'),
                    ('updateurl', 'https://example.invalid/j3jz.exe'), ('rateEdition', '0')]
        if 'from ReplayProInfo' in self.last:
            return [('num', '', 100)]
        if 'from UserInfo' in self.last:
            return [('uuid', '测试用户', '', '', '', 10, 20)]
        return []

    def inserted(self, table):
        query = next(q for q in reversed(self.queries) if q.startswith('INSERT INTO ' + table + ' '))
        values = re.search(r'VALUES\s*\((.*)\)\s*;?\s*$', query, re.S).group(1)
        return next(csv.reader([values.replace('\n', ' ')], skipinitialspace=True))


class ServerCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ServerAddress
        # Importing server must not initialize its remote cache or large local
        # attribute reader. The real route functions and Flask app remain intact.
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(ServerAddress, '_address_cache', copy.deepcopy(ServerAddress.FALLBACK_ADDRESS)))
            stack.enter_context(patch('socket.socket.connect', side_effect=AssertionError('network forbidden')))
            stack.enter_context(patch('urllib.request.urlopen', side_effect=AssertionError('HTTP forbidden')))
            stack.enter_context(patch('pymysql.connect', side_effect=AssertionError('database forbidden')))
            stack.enter_context(patch('equip.AttributeDisplay.AttributeDisplay'))
            cls.server = importlib.import_module('server')
            cls.rank = importlib.import_module('serverFunc.UpdateReplayRank')

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.stack.enter_context(patch('socket.socket.connect', side_effect=AssertionError('network forbidden')))
        self.stack.enter_context(patch('urllib.request.urlopen', side_effect=AssertionError('HTTP forbidden')))
        self.writer = self.stack.enter_context(patch.object(self.server, 'open', mock_open(), create=True))
        self.stack.enter_context(patch.object(self.server.app, 'dbname', 'mock-user', create=True))
        self.stack.enter_context(patch.object(self.server.app, 'dbpwd', 'mock-password', create=True))
        self.stack.enter_context(patch.object(self.server.app, 'percent_data', {}, create=True))
        self.cursor = RecordingCursor()
        self.db = MagicMock()
        self.db.cursor.return_value = self.cursor
        self.connect = self.stack.enter_context(patch.object(self.server.pymysql, 'connect', return_value=self.db))
        self.client = self.server.app.test_client()

    def battle(self, map_name=MAPS['835'], when=INITIAL - 1):
        return {'server': '测试服', 'boss': '史朝义', 'battledate': '2026-09-20',
                'mapdetail': map_name, 'edition': '8.16.0', 'hash': 'battle-test-hash',
                'team': '测试团队', 'length': 600, 'statistics': {'win': 1},
                'win': 1, 'time': when + 1000, 'begintime': when, 'userid': 'uuid'}

    def replay(self, map_name=MAPS['835'], when=INITIAL - 1):
        return {'server': '测试服', 'id': '测试侠士', 'occ': 'lingsu', 'score': 95,
                'battledate': '2026-09-20', 'mapdetail': map_name, 'boss': '史朝义',
                'edition': '8.16.0', 'hash': 'replay-test-hash', 'public': 1,
                'submittime': when + 1000, 'battletime': when, 'userid': 'uuid',
                'editionfull': self.server.parseEdition('8.16.0'), 'replayedition': '8.16.0',
                'battleID': 'battle-test-hash', 'statistics': {
                    'overall': {'playerID': '测试侠士'},
                    'skill': {'healer': {'rhps': 1200, 'hps': 1500},
                              'general': {'rdps': 2200, 'ndps': 2000, 'mrdps': 1800, 'mndps': 1600}}}}

    def test_boundaries_are_explicit_utc_plus_eight(self):
        local = timezone(timedelta(hours=8))
        self.assertEqual(datetime.fromtimestamp(INITIAL, local).isoformat(), '2026-10-29T07:00:00+08:00')
        self.assertEqual(datetime.fromtimestamp(FIRST_NERF, local).isoformat(), '2026-12-21T07:00:00+08:00')
        for map_id in MAPS:
            for when, expected in BOUNDARIES:
                with self.subTest(map_id=map_id, when=when):
                    self.assertEqual(self.server.getGameEditionFromTime(map_id, when), expected)

    def test_battle_persists_map_id_version_and_all_boundary_cases(self):
        for map_id, map_name in MAPS.items():
            for when, expected in BOUNDARIES:
                with self.subTest(map_id=map_id, when=when):
                    response = self.server.receiveBattle(self.battle(map_name, when), self.cursor)
                    self.assertEqual(response['result'], 'success')
                    row = self.cursor.inserted('ActorStat')
                    self.assertEqual((row[3], row[4], row[9], row[12]),
                                     (map_id, '8.16.0', str(when), expected))
        self.writer.assert_any_call('database/ActorStat/battle-test-hash', 'w')
        self.assertTrue(self.writer().write.called)

    def test_old_battle_without_begin_time_uses_default(self):
        payload = self.battle()
        del payload['begintime']
        response = self.server.receiveBattle(payload, self.cursor)
        self.assertEqual(response['result'], 'success')
        row = self.cursor.inserted('ActorStat')
        self.assertEqual((row[9], row[12]), ('0', '160'))

    def test_replay_persists_map_name_version_and_all_boundary_cases(self):
        for map_id, map_name in MAPS.items():
            for when, expected in BOUNDARIES:
                with self.subTest(map_id=map_id, when=when):
                    response = self.server.receiveReplay(self.replay(map_name, when), self.cursor)
                    self.assertEqual(response['result'], 'success')
                    row = self.cursor.inserted('ReplayProStat')
                    self.assertEqual((row[5], row[10], row[14], row[31]),
                                     (map_name, '8.16.0', str(when), expected))
                    self.assertEqual(int(row[11]), self.server.parseEdition('8.16.0'))
        self.writer.assert_any_call('database/ReplayProStat/101', 'w')

    def test_all_three_upload_routes_commit_and_close(self):
        payloads = [('/uploadActorData', self.battle(), 'result'),
                    ('/uploadReplayPro', self.replay(), 'result'),
                    ('/uploadCombinedData', {'data': [
                        {'type': 'battle', 'id': 0, 'data': self.battle()},
                        {'type': 'replay', 'id': 1, 'data': self.replay()}]}, 'status')]
        for route, payload, status in payloads:
            with self.subTest(route=route):
                self.db.reset_mock()
                response = self.client.post(route, data={'jdata': json.dumps(payload)})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json()[status], 'success')
                self.db.commit.assert_called_once_with()
                self.db.rollback.assert_not_called()
                self.db.close.assert_called_once_with()

    def test_all_three_upload_routes_rollback_and_close_on_sql_failure(self):
        cases = [('/uploadActorData', self.battle(), 'INSERT INTO ActorStat', 'result'),
                 ('/uploadReplayPro', self.replay(), 'INSERT INTO ReplayProStat', 'result'),
                 ('/uploadCombinedData', {'data': [
                     {'type': 'battle', 'id': 0, 'data': self.battle()},
                     {'type': 'replay', 'id': 1, 'data': self.replay()}]}, 'INSERT INTO ReplayProStat', 'status')]
        for route, payload, failure, status in cases:
            with self.subTest(route=route):
                self.db.reset_mock()
                self.cursor.fail_on = failure
                with patch.object(self.server.traceback, 'print_exc'):
                    response = self.client.post(route, data={'jdata': json.dumps(payload)})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json()[status], 'fail')
                self.db.commit.assert_not_called()
                self.db.rollback.assert_called_once_with()
                self.db.close.assert_called_once_with()

    def test_combined_success_keeps_response_ids_and_both_insertions(self):
        response = self.client.post('/uploadCombinedData', data={'jdata': json.dumps({'data': [
            {'type': 'battle', 'id': 41, 'data': self.battle()},
            {'type': 'replay', 'id': 42, 'data': self.replay()}]})}).get_json()
        self.assertEqual(response['status'], 'success')
        self.assertEqual([row['id'] for row in response['data']], [41, 42])
        self.assertEqual(self.cursor.inserted('ActorStat')[3], '835')
        self.assertEqual(self.cursor.inserted('ReplayProStat')[5], MAPS['835'])
        self.db.commit.assert_called_once_with()

    def test_map_and_edition_endpoints_expose_collection_periods(self):
        maps = self.client.get('/getMaps').get_json()['result']
        for map_id, map_name in MAPS.items():
            self.assertEqual(maps[map_id]['name'], map_name)
            for when, expected in BOUNDARIES:
                with self.subTest(map_id=map_id, when=when), patch.object(self.server.time, 'time', return_value=when):
                    data = self.client.get('/getGameEditionFromMap', query_string={'map': map_name}).get_json()
                    self.assertEqual(data['available'], 1)
                    self.assertEqual(set(data['result']), {'160', '161', '162'})
                    self.assertEqual(str(data['current']), expected)
                    self.assertEqual(data['ranges']['160'], [[0, INITIAL]])
                    self.assertEqual(data['ranges']['161'], [[INITIAL, FIRST_NERF]])
                    self.assertEqual(data['ranges']['162'][0][0], FIRST_NERF)
                    self.assertEqual(data['timezone'], 'UTC+08:00')

    def test_announcement_returns_current_release_metadata(self):
        self.assertEqual(self.server.EDITION, '8.16.0')
        response = self.client.get('/getAnnouncement', query_string={'edition': '8.16.0'}).get_json()
        self.assertEqual(response['version'], '8.16.0')
        self.assertEqual(response['url'], 'https://example.invalid/j3jz.exe')
        self.db.close.assert_called_once_with()

    def test_rank_aggregation_keeps_game_editions_and_difficulties_separate(self):
        data = self.replay()['statistics']
        records = []
        for map_id in ('835', '836'):
            for edition in ('160', '161', '162'):
                row = [0] * 32
                row[0:4] = ['测试服', '测试侠士', 'lingsu', 95]
                row[5:9] = [MAPS[map_id], '史朝义', 'rank-hash', 101]
                row[10:12] = ['8.16.0', self.server.parseEdition('8.16.0')]
                row[31] = edition
                records.append(row)
        with patch.object(self.rank, 'open', mock_open(read_data=json.dumps(data)), create=True):
            ranks = self.rank.getAllStat(records)
        for map_id in ('835', '836'):
            for edition in ('160', '161', '162'):
                self.assertEqual(ranks['lingsu-%s-史朝义-general-rdps-%s' % (map_id, edition)], [2200])
        # Existing rules collect ten-player runs but do not rank them with 25-player runs.
        row = list(records[0])
        row[5] = MAPS['828']
        with patch.object(self.rank, 'open', mock_open(read_data=json.dumps(data)), create=True):
            self.assertEqual(self.rank.getSingleStat(row), {})

    def test_cangsheng_rank_list_excludes_pre_816_client(self):
        records = []
        for index, edition in enumerate(('8.15.5', '8.16.0')):
            row = [0] * 32
            row[0:4] = ['测试服', '旧版侠士' if index == 0 else '新版侠士', 'lingsu', 100 - index]
            row[5:9] = [MAPS['835'], '史朝义', 'rank-%d' % index, 101 + index]
            row[10:12] = [edition, self.server.parseEdition(edition)]
            row[16] = 'battle-test-hash'
            row[30:32] = [1, '160']
            records.append(row)
        with patch.object(self.cursor, 'fetchall', return_value=records):
            response = self.client.get('/getRank', query_string={
                'map': MAPS['835'], 'boss': '史朝义', 'occ': 'lingsu', 'gameEdition': '160'}).get_json()
        self.assertEqual(response['available'], 1)
        self.assertEqual([row['edition'] for row in response['result']['table']], ['8.16.0'])
        self.assertEqual(response['result']['table'][0]['id'], '新版侠士')
        self.db.close.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()

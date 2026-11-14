"""Optional original missed clears through Actor, rank quality and real upload form.

Set JX3BLA_HEROIC_LOG_DIR. Database/files/HTTP are isolated test doubles;
original player logs and payloads never leave this machine.
"""
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import Mock

import test_luoyang_heroic_upload as receipts


LOG_DIR = Path(os.environ.get('JX3BLA_HEROIC_LOG_DIR', Path(__file__).resolve().parents[1]))
LOGS = (
    ('2026-11-14-19-53-35-25人英雄洛阳之战(836)-田承嗣(139382).jcl', '田承嗣',
     '2fda230b75e5ee5d68f5d4e45d788f88fd79c1855f710e59d6bbefa5e8644b0d', 2024157, 2024205, 2024664),
    ('2026-11-14-21-51-56-25人英雄洛阳之战(836)-阿史那承庆(139378).jcl', '阿史那承庆',
     '585cde9c9d8d8d1ba9a5782a251f09a79b6983831814eb691908f85aefc032de', 9197920, 9198045, 9198550),
    ('2026-11-14-22-54-07-25人英雄洛阳之战(836)-史朝义(139365).jcl', '史朝义',
     '321a4ce21bc00c4d6778a225286333436b7835f8605adfa40ffe779f8d505c36', 13069172, 13069269, 13069589),
)


class LatestHeroicVictoryTests(unittest.TestCase):
    setUpClass = classmethod(receipts.HeroicUploadTests.setUpClass.__func__)
    setUp = receipts.HeroicUploadTests.setUp
    _upload = receipts.HeroicUploadTests._upload
    _assert_readback = receipts.HeroicUploadTests._assert_readback
    _check_actor_boundaries = receipts.HeroicUploadTests._check_actor_boundaries
    validation_results = []

    @unittest.skipUnless(all((LOG_DIR / row[0]).is_file() for row in LOGS),
                         'Set JX3BLA_HEROIC_LOG_DIR to the local 2026-11-14 JCL directory')
    def test_three_missed_clears_generate_precise_replays_and_stable_server_receipts(self):
        from MainWindow import MainWindow
        from release.SmokeTest import check_damage_conservation, check_upload_payloads
        from tools.ValidateLuoyang import replay, check_windows

        window = MainWindow.__new__(MainWindow)
        window.playerEquipment = {}
        window.playerEquipmentAnalysed = {}
        window.lastBld = None
        window.stat_percent = {}
        window.uploadData = []
        window.setNotice = Mock()
        reports = []
        type(self).validation_results = reports
        for filename, boss, sha, last_damage, credit_time, exit_time in LOGS:
            with self.subTest(boss=boss):
                path = LOG_DIR / filename
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), sha)
                actor = replay(path, window, healers=True)
                self.assertEqual((actor.bossAnalyseName, actor.win, actor.finalTime), (boss, 1, exit_time))
                self.assertEqual(actor.detail['winReason'], 'seasonal_boss_credit_and_combat_exit')
                evidence = next(row for row in actor.detail['winEvidence']
                                if row['rule'] == actor.detail['winReason'])
                self.assertEqual((evidence['lastMainDamage'], evidence['honorTime']), (last_damage, credit_time))
                quality = self.server.get_record_quality(actor.detail)
                self.assertTrue(quality['precise'], quality)
                self.assertEqual(actor.combatTracker.rdpsStatus['status'], 'supported')
                periods = self._check_actor_boundaries(actor)
                damage = check_damage_conservation(actor.combatTracker)
                names = {actor.bld.info.getName(pid): pid for pid in actor.bld.info.player}
                order = [actor.combatTracker.getRdps(names[row['name']]) for row in actor.statDict]
                self.assertEqual(order, sorted(order, reverse=True))
                for row, value in zip(actor.statDict, order):
                    self.assertEqual(row['rdps'], int(value))
                ui = check_windows(actor)
                summary, _ = check_upload_payloads(window, actor)
                self.assertEqual((summary['battle'], summary['replay']), (1, 25))
                battle = next(row['data'] for row in window.uploadData if row['type'] == 'battle')
                personal = [copy.deepcopy(row['data']) for row in window.uploadData if row['type'] == 'replay']
                self.assertTrue(all(self.server.get_record_quality(row['statistics'])['precise'] for row in personal))
                pending = list(window.uploadData)
                response, size = self._upload(window)
                ids = [row['shortID'] for row in response['data'] if 'shortID' in row]
                self.assertEqual(len(set(ids)), 25)
                for record in personal:
                    persisted = json.loads(self.files['database/ReplayProStat/%d' % self.cursor.replays[record['hash']][8]])
                    self.assertTrue(self.server.get_record_quality(persisted)['precise'])
                self._assert_readback(battle, personal[0])
                before = dict(self.files)
                window.uploadData = pending
                repeat, _ = self._upload(window)
                self.assertEqual([row['shortID'] for row in repeat['data'] if 'shortID' in row], ids)
                self.assertTrue(all(row['result'] == 'dupid' for row in repeat['data']))
                self.assertEqual(self.files, before)
                public_evidence = {key: value for key, value in evidence.items() if key != 'npcID'}
                reports.append({'file': filename, 'sha256': sha, 'boss': boss, 'win': actor.win,
                    'status': 'passed', 'winEvidence': public_evidence, 'finalTime': actor.finalTime,
                    'battleMs': actor.battleTime, 'dpsMs': actor.bh.sumTime('dps'),
                    'healerMs': actor.bh.sumTime('healer'), 'personalReplays': 25,
                    'preciseReplays': 25, 'quality': quality, 'damage': damage, 'phasePeriods': periods,
                    'battleValuesAndSort': 'passed', 'ui': ui, 'requestBytes': size,
                    'readback': 'passed', 'duplicateIDs': 'stable', 'productionUploaded': False})
                del actor
                gc.collect()
        self.assertEqual((len(self.cursor.battles), len(self.cursor.replays)), (3, 75))


if __name__ == '__main__':
    unittest.main()

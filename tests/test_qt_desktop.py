import os
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtWidgets import QApplication

from data.ReplaySession import AnalysisCancelled, ReplaySession
from window.QtDesktop import DesktopWindow, StableLogs, configure_application
from window.QtSettings import load_desktop_config


class ReplaySessionTests(unittest.TestCase):
    def test_failed_analysis_rolls_back_equipment_and_only_its_uploads(self):
        session = ReplaySession()
        session.playerEquipment['a'] = '上一场'
        session.uploadData.append({'id': 0})
        actor = Mock(available=True, upload=True)
        actor.FirstStageAnalysis.return_value = 0
        def fail():
            session.playerEquipment['a'] = '失败场'
            session.playerEquipmentOwners['b'] = '新角色'
            session.uploadData.append({'id': 1})
            raise ValueError('读取中断')
        actor.OccAnalysis.side_effect = fail
        with patch('data.BattleLogData.BattleLogData', return_value=Mock(log=[1])), \
                patch('replayer.ActorReplayPro.ActorProReplayer', return_value=actor):
            with self.assertRaisesRegex(ValueError, '读取中断'):
                session.analyse(Path('first.jcl'), {})
        self.assertEqual(session.playerEquipment, {'a': '上一场'})
        self.assertEqual(session.playerEquipmentOwners, {})
        self.assertEqual(session.uploadData, [{'id': 0}])
        self.assertIsNone(session.lastBld)

    def test_partial_encounter_is_joined_to_next_completed_file(self):
        session = ReplaySession()
        first, second = Mock(log=[1]), Mock(log=[2])
        partial, complete = Mock(available=False), Mock(available=True, upload=False)
        partial.FirstStageAnalysis.return_value = complete.FirstStageAnalysis.return_value = 0
        with patch('data.BattleLogData.BattleLogData', side_effect=[first, second]), \
                patch('replayer.ActorReplayPro.ActorProReplayer', side_effect=[partial, complete]):
            self.assertIsNone(session.analyse(Path('a.jcl'), {}))
            self.assertIs(session.lastBld, first)
            partial.OccAnalysis.assert_not_called()
            self.assertIs(session.analyse(Path('b.jcl'), {}), complete)
        second.merge.assert_called_once_with(first)
        self.assertIsNone(session.lastBld)


class WatchTests(unittest.TestCase):
    def test_all_new_and_changed_files_are_delivered_once_after_stable_poll(self):
        with TemporaryDirectory() as temp:
            folder = Path(temp)
            old = folder / '00.jcl'
            old.write_bytes(b'old')
            watcher = StableLogs(folder, '.jcl')
            self.assertEqual(watcher.ready(), [])
            older, newer = folder/'01.jcl', folder/'02.JCL'
            newer.write_bytes(b'new')
            older.write_bytes(b'start')
            self.assertEqual(watcher.ready(), [])
            older.write_bytes(b'finished')
            self.assertEqual(watcher.ready(), [newer])
            self.assertEqual(watcher.ready(), [older])
            self.assertEqual(watcher.ready(), [])
            old.write_bytes(b'replaced')
            self.assertEqual(watcher.ready(), [])
            self.assertEqual(watcher.ready(), [old])


class ShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        configure_application(cls.app)

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.session = ReplaySession()
        self.window = DesktopWindow(load_desktop_config(Path(self.folder.name)/'config.ini'),
                                    services=False, session=self.session)
        self.window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        self.window.show()
        self.addCleanup(self.window.close)

    def wait_for_batch(self):
        loop = QEventLoop()
        self.window.batchFinished.connect(loop.quit)
        QTimer.singleShot(5000, loop, loop.quit)
        loop.exec()
        self.assertFalse(self.window.busy)

    @staticmethod
    def result(name):
        return SimpleNamespace(bossAnalyseName=name, statDict=[{'name':'队员'}],
               potList=[['队员','2d',1,name,'失误',[],-1]], server='测试服', mapDetail='测试地图',
               timestamp=100, battleTime=42000, win=1, mask=True)

    def test_sequential_results_use_one_worker_and_recover_after_bad_file(self):
        calls = []
        def analyse(path, config):
            self.assertNotEqual(threading.current_thread(), threading.main_thread())
            calls.append(path.stem)
            if path.stem=='b':
                raise ValueError('格式错误')
            return self.result(path.stem)
        with patch.object(self.session, 'analyse', side_effect=analyse), \
                patch('window.QtDesktop.display_result',side_effect=lambda actor:actor):
            self.window.enqueue_files(['c.jcl','b.jcl','a.jcl'])
            self.wait_for_batch()
        self.assertEqual(calls, ['a','b','c'])
        self.assertEqual(self.window.history.rowCount(), 2)
        self.assertEqual(len(self.window.failures), 1)
        self.window.nav[1].click()
        self.assertEqual(self.window.summary.item(0,0).text(), '队员01')
        self.assertEqual(self.window.summary.item(0,3).text(), '-2')

    def test_cancel_interrupts_safe_checkpoint_and_does_not_drain_future_jobs(self):
        started = threading.Event()
        proceed = threading.Event()
        calls = []
        def analyse(path, config):
            calls.append(path.name)
            started.set()
            self.assertTrue(proceed.wait(3))
            self.session.checkpoint()
        with patch.object(self.session, 'analyse', side_effect=analyse):
            self.window.enqueue_files(['a.jcl','b.jcl'])
            self.assertTrue(started.wait(3))
            self.window.enqueue_files(['c.jcl'])
            self.window.cancel_batch()
            self.window.enqueue_files(['d.jcl'])
            proceed.set()
            self.wait_for_batch()
        self.assertEqual(calls, ['a.jcl'])
        self.assertEqual(self.window.pending, [])
        self.assertEqual(self.window.failures, [])
        self.session.checkpoint()

    def test_reanalysis_preserves_scores_and_manual_notes_only_for_same_encounter(self):
        path = Path('same.jcl')
        old = self.result('首领')
        self.window._result(path, old)
        old.potList[0][6] = 3
        old.potList.append(['队员', '2d', 0, '首领', '[手动] 补救', [], 1])
        self.window._result(path, self.result('首领'))
        self.assertEqual([p[6] for p in self.window.results[0].potList], [3, 1])
        self.window._result(path, self.result('新首领'))
        self.assertEqual([p[6] for p in self.window.results[0].potList], [-1])
        self.assertEqual(self.window.history.rowCount(), 1)

    def test_stale_live_signals_do_not_start_new_work(self):
        with patch.object(self.window, 'enqueue_files') as queue:
            self.window._watch_files(0,['stale.jcl'])
            self.window.watch_stop=threading.Event()
            self.window._stop_watch()
            self.window._watch_files(0,['stale.jcl'])
            queue.assert_not_called()

"""Regression coverage for Qt navigation, quality eligibility, privacy, and editable battle records."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    from PySide6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QTableView
except ImportError:
    QApplication = None
else:
    from window.QtResults import BattleView


def cells(table):
    model = table.model()
    return [[model.data(model.index(r, c)) for c in range(model.columnCount())]
            for r in range(model.rowCount())]


def fixture(mask=False):
    player = '花间甲'
    healer = '云裳乙'
    skill = {'general': {'rdps': 102}, 'hxpy': {'num': 5, 'delay': 0}}
    team = [{'name': player, 'occ': '2d', 'damage': 900}]
    percent = {'percent': 0, 'num': 3}
    result = {'overall': {'playerID': healer, 'mask': 0}, 'skill': skill,
              'dps': {'table': team}, 'qixue': {'available': 1, '1': '甲穴', '3': '丙穴'},
              'equip': {'available': 1, 'score': 42000, 'raw': '1,2,3'},
              'review': {'score': 90, 'content': [
                  {'code': 1, 'status': 3, 'rate': 0, 'num': 1, 'duration': 6}]}}
    players = {healer: {'occ': '5h', 'result': result, 'rank': {'general': {'rdps': percent}}},
               player: {'occ': '2d', 'result': {'skill': {'general': {'rdps': 900}}}}}
    row = {'name': healer, 'occ': '5h', 'score': 90, 'scoreRank': 0, 'scoreRankNum': 3,
           'rdps': 102, 'ndps': 50, 'hps': 300, 'battle': {'swordActivations': 2}}
    tracker = {'rhps': {'player': {'123': {'name': healer, 'occ': '5h', 'hps': 300, 'sum': 3000,
                'namedSkill': {'回雪': {'num': 4, 'sum': 3000, 'percent': 1}},
                'namedTarget': {player: {'num': 4, 'sum': 3000, 'percent': 1}}}}}}
    return SimpleNamespace(statDict=[row, {'name': player, 'occ': '2d', 'rdps': 900}],
                           occResult=players, detail={'boss': '史朝义', 'map': '洛阳之战', 'win': 1,
                           'mechanicEvents': [{'time': 10500, 'player': player, 'mechanic': '拾取碎片'}]},
                           startTime=10000, finalTime=20000, potList=[[player, '2d', 1, '史朝义',
                           '机制失误', [f'{healer}观察'], 0]], combatTracker=tracker, mask=mask)


@unittest.skipUnless(QApplication, 'PySide6 is required for Qt desktop tests')
class BattleViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        cls.app = QApplication.instance() or QApplication([])

    def view(self, actor):
        view = BattleView(actor)
        self.addCleanup(view.deleteLater)
        return view

    def test_team_to_personal_rank_zero_equipment_and_talent(self):
        view = self.view(fixture())
        self.assertIn('0%', cells(view.team_table)[0])
        self.assertTrue(view.open_player('云裳乙'))
        self.assertEqual(view.tabs.currentWidget(), view.personal_tabs.parentWidget())
        self.assertFalse(view.open_player('未知'))
        self.assertIn('回雪飘摇', str(cells(view.personal_tabs.widget(0).findChild(QTableView))))
        self.assertIn('0%', str(cells(view.personal_tabs.widget(0).findChild(QTableView))))
        view.personal_tabs.setCurrentIndex(1)
        self.assertTrue(any('甲穴,丙穴' in label.text() for label in view.personal_tabs.widget(1).findChildren(QLabel)))
        view.personal_tabs.setCurrentIndex(3)
        self.assertIn('重伤了1次', view.personal_tabs.widget(3).findChild(QPlainTextEdit).toPlainText())
        self.assertTrue(view.open_player('花间甲'))
        self.assertTrue(any('没有评分建议' in label.text() for label in view.personal_tabs.widget(3).findChildren(QLabel)))

    def test_cannot_display_precise_rank_for_missing_gear(self):
        actor = fixture()
        actor.attributeStatus = {'status': 'incomplete', 'targetProfileUnavailable': True}
        view = self.view(actor)
        row = cells(view.team_table)[0]
        self.assertEqual(row[2:8], ['—', '50', '300', '300', '—', '待校准'])
        view.open_player('云裳乙')
        rows = cells(view.personal_tabs.widget(0).findChild(QTableView))
        self.assertEqual(next(r for r in rows if r[1] == 'rDPS')[3], '—')

    def test_mechanics_and_all_tracker_details_obey_mask(self):
        actor = fixture(mask=True)
        view = self.view(actor)
        self.assertNotIn('云裳乙', str(cells(view.team_table)))
        view.tabs.setCurrentIndex(1)
        self.assertIn('0:00.500', str(cells(view.mechanic_table)))
        self.assertNotIn('花间甲', str(cells(view.mechanic_table)))
        view.tabs.setCurrentIndex(3)
        view.combat_selector.setCurrentIndex(view.combat_selector.findData('rhps'))
        self.assertIn('300', str(cells(view.combat_table)))
        self.assertIn('回雪', str(cells(view.combat_skill)))
        self.assertIn('100.0%', str(cells(view.combat_targets)))
        self.assertNotIn('花间甲', str(cells(view.combat_targets)))
        view.open_player('云裳乙')
        view.personal_tabs.setCurrentIndex(2)
        self.assertNotIn('花间甲', str(cells(view.personal_tabs.widget(2).findChild(QTableView))))

    def test_manual_records_share_scores_with_battle_and_copy_masked_text(self):
        actor = fixture(mask=True)
        view = self.view(actor)
        view.tabs.setCurrentIndex(2)
        self.assertNotIn('云裳乙', view.pot_details.toPlainText())
        view.adjust_pot(-1)
        self.assertEqual(actor.potList[0][6], -1)
        self.assertTrue(view.add_pot('云裳乙', '帮助花间甲', 3, 2))
        view.adjust_pot(1)
        self.assertEqual(actor.potList[-1][6], 3)
        with patch.object(QApplication, 'clipboard') as clipboard:
            view.copy_pot()
            set_text = clipboard.return_value.setText
            set_text.assert_called_once()
            text = set_text.call_args.args[0]
        self.assertIn('[手动]', text)
        self.assertNotIn('花间甲', text)
        self.assertNotIn('云裳乙', text)
        self.assertFalse(view.add_pot('云裳乙', ' '))
        self.assertFalse(view.add_pot('未知', '描述'))

    def test_web_replay_and_link_copy_use_uploaded_id_and_current_host(self):
        actor = fixture()
        view = self.view(actor)
        view.logs_url = 'https://example.test/'
        view.open_player('云裳乙')
        self.assertIsNone(view.personal_url())
        self.assertTrue(view.web_button.isHidden())
        actor.occResult['云裳乙']['result']['overall']['shortID'] = 127
        view.refresh_links()
        self.assertFalse(view.web_button.isHidden())
        url = 'https://example.test/yunchangxinjing/127'
        self.assertEqual(view.personal_url().toString(), url)
        with patch('window.QtResults.QDesktopServices.openUrl') as launch:
            view.web_button.click()
            self.assertEqual(launch.call_args.args[0].toString(), url)
        with patch.object(QApplication, 'clipboard') as clipboard:
            view.copy_link.click()
            clipboard.return_value.setText.assert_called_once_with(url)
        actor.occResult['云裳乙']['result']['overall']['shortID'] = '数据保存出错'
        view.tabs.setCurrentIndex(0)
        view.tabs.setCurrentIndex(5)
        self.assertTrue(view.web_button.isHidden())

    def test_replacing_player_pages_releases_previous_models(self):
        import gc
        import weakref
        from PySide6.QtCore import QCoreApplication, QEvent
        view = self.view(fixture())
        view.open_player('云裳乙')
        old_page = weakref.ref(view.personal_tabs.widget(0))
        old_model = weakref.ref(old_page().findChild(QTableView).model())
        view.open_player('花间甲')
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        gc.collect()
        self.assertIsNone(old_page())
        self.assertIsNone(old_model())

    def test_empty_and_legacy_snapshots(self):
        view = self.view({'statDict': [['旧角色', '2d', 999]], 'occResult': {}, 'detail': {}, 'potList': []})
        self.assertIn('999', cells(view.team_table)[0])
        self.assertEqual(cells(view.team_table)[0][2], '—')
        for n in range(view.tabs.count()):
            view.tabs.setCurrentIndex(n)
        self.assertIsNone(view.current_player)
        self.assertFalse(view.pot_actions[0].isEnabled())


if __name__ == '__main__':
    unittest.main()

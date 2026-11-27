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
    players = {healer: {'occ': '5h', 'result': result, 'rank': {'general': {'rdps': percent},'healer': {'rhps': percent}}},
               player: {'occ': '2d', 'result': {'skill': {'general': {'rdps': 900}}}}}
    row = {'name': healer, 'occ': '5h', 'score': 90, 'scoreRank': 0, 'scoreRankNum': 3,
           'rdps': 102, 'ndps': 50, 'hps': 300, 'battle': {'swordActivations': 2}}
    tracker = {'rhps': {'player': {'123': {'name': healer, 'occ': '5h', 'hps': 300, 'sum': 3000,
                'namedSkill': {'回雪': {'num': 4, 'sum': 3000, 'percent': 1}},
                'namedTarget': {player: {'num': 4, 'sum': 3000, 'percent': 1}}}}}}
    return SimpleNamespace(statDict=[row, {'name': player, 'occ': '2d', 'rdps': 900}],
                           displayRanks={healer: {'scope': 'logs', 'metric': 'rdps', 'basis': 'verified',
                                                  'percent': 0, 'num': 3}},
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

    def test_team_to_dense_personal_view_with_rank_talents_and_search(self):
        view = self.view(fixture())
        from PySide6.QtCore import Qt
        self.assertIn('0%', cells(view.team_table)[1])
        self.assertIn('样本 3 人', view.team_table.model().index(1, 6).data(Qt.ItemDataRole.ToolTipRole))
        self.assertTrue(view.open_player('云裳乙'))
        self.assertFalse(view.open_player('未知'))
        self.assertIn('回雪飘摇', str(cells(view.skill_table)))
        labels = [label.text() for label in view.personal_dashboard.findChildren(QLabel)]
        self.assertTrue(any('甲穴,丙穴' in text for text in labels))
        self.assertFalse(any('评分' in text for text in labels))
        self.assertIn('42000', view.equipment_summary.text())
        self.assertEqual(view.player_selector.completer().filterMode(), Qt.MatchFlag.MatchContains)
        self.assertTrue(view.player_selector.isEditable())
        self.assertTrue(view.open_player('花间甲'))
        self.assertIn('装备', view.equipment_summary.text())

    def test_legacy_team_rank_ignored_and_unavailable_gear_explained(self):
        actor = fixture()
        actor.playerNames = {'123': '云裳乙', '234': '花间甲'}
        actor.attributeStatus = {'status': 'estimated',
            'estimatedPlayers': {'234': {}},
            'missingEquipmentPlayers': {'234': {'hasEquipment': False, 'reason': 'missing_slots'}}}
        actor.displayRanks = {'云裳乙': {'metric': 'rhps', 'scope':'team', 'reference':True,
                                      'percent':25, 'num':4, 'cohort':'治疗'}}
        view = self.view(actor)
        self.assertIn('暂无线上样本', cells(view.team_table)[1])
        self.assertTrue(any('1/2 人资料齐全' in label.text() for label in view.findChildren(QLabel)))
        view.open_player('云裳乙')
        self.assertNotIn('估算', view.equipment_summary.text())
        view.open_player('花间甲')
        self.assertIn('本次未记录该玩家装备，属性采用估算',view.equipment_summary.text())
        incomplete = fixture()
        incomplete.attributeStatus = {'status':'incomplete', 'targetProfileUnavailable':True}
        incomplete.displayRanks = {'花间甲': {'scope': 'logs', 'metric': 'rdps', 'basis': 'unavailable'}}
        other = self.view(incomplete)
        self.assertEqual(cells(other.team_table)[0][2], '—')
        self.assertIn('无法归因', cells(other.team_table)[0])

    def test_bars_and_live_rank_refresh_preserve_player_and_selection(self):
        from PySide6.QtCore import Qt
        from window.QtResults import BAR_ROLE, _rank_color
        view = self.view(fixture())
        table = view.team_table
        model = table.model()
        self.assertEqual(model.index(0, 0).data(BAR_ROLE), 1)
        self.assertAlmostEqual(model.index(1, 0).data(BAR_ROLE), 102 / 900)
        self.assertTrue(model.headerData(9, Qt.Orientation.Horizontal, Qt.ItemDataRole.ToolTipRole))
        table.selectRow(1)
        view.open_player('云裳乙')
        self.assertEqual(view.personal_rank.text(), '0%')
        view.refresh_display_ranks({'云裳乙': {'scope': 'logs', 'metric': 'rdps', 'basis': 'estimated_equipment',
                                              'percent': 98, 'num': 27}})
        self.assertIs(model, table.model())
        self.assertEqual(table.currentIndex().row(), 1)
        self.assertEqual(view.current_player, '云裳乙')
        self.assertEqual(view.personal_rank.text(), '98%')
        self.assertIn('装备属性含估算', view.personal_rank.toolTip())
        self.assertIn('98%', cells(table)[1])
        self.assertEqual(model.index(1, 6).data(Qt.ItemDataRole.ForegroundRole).color(), _rank_color(99))
        self.assertNotEqual(_rank_color(97), _rank_color(98))
        self.assertEqual(len({_rank_color(n).name() for n in (0, 25, 50, 75, 95, 98, 100)}), 7)
        view.refresh_display_ranks({})
        self.assertEqual(view.personal_rank.text(), '暂无线上样本')
        self.assertIsNone(model.index(1, 6).data(Qt.ItemDataRole.ForegroundRole))

    def test_fractional_rates_match_logs_integer_in_all_views_and_keep_raw_bars(self):
        from window.QtResults import BAR_ROLE
        actor = fixture()
        actor.combatTracker['rdps'] = {'player': {
            '2': {'name': '花间甲', 'occ': '2d', 'dps': 900.9},
            '1': {'name': '云裳乙', 'occ': '5h', 'dps': 102.9, 'sumPerSec': 0}}}
        # Historical reports can omit individual rDPS and record zero for a buff-only healer.
        del actor.statDict[0]['rdps']
        actor.occResult['云裳乙']['result']['skill']['general']['rdps'] = 0
        actor.combatTracker['rhps']['player']['123']['hps'] = 300.9
        actor.occResult['云裳乙']['result']['skill']['healer'] = {'rhps': 300}
        view = self.view(actor)
        self.assertEqual(cells(view.team_table)[1][2], '102')
        self.assertEqual(cells(view.team_table)[1][4], '300')
        self.assertAlmostEqual(view.team_table.model().index(1, 0).data(BAR_ROLE), 102.9/900.9)
        view.tabs.setCurrentIndex(2)
        self.assertEqual(cells(view.combat_table)[1][2], '102')
        self.assertAlmostEqual(view.combat_table.model().index(1, 2).data(BAR_ROLE), 102.9/900.9)
        view.combat_selector.setCurrentIndex(view.combat_selector.findData('rhps'))
        self.assertEqual(cells(view.combat_table)[0][2], '300')
        self.assertTrue(view.open_player('云裳乙'))
        self.assertIn('300', [label.text() for label in view.personal_dashboard.findChildren(QLabel)])
        self.assertEqual(view.personal_rdps.text(), '102')

    def test_team_and_tracker_details_obey_mask_and_show_occupation_roles(self):
        from PySide6.QtCore import Qt
        from window.QtOccupation import ICON_IDS, occupation_icon
        actor = fixture(mask=True)
        actor.detail['phaseTimes'] = {'常规阶段': 10}
        view = self.view(actor)
        self.assertNotIn('云裳乙', str(cells(view.team_table)))
        self.assertNotIn('阶段与机制', [view.tabs.tabText(i) for i in range(view.tabs.count())])
        self.assertTrue(any('常规阶段' in label.text() for label in view.findChildren(QLabel)))
        index = view.team_table.model().index(0, 0)
        self.assertTrue(index.data(Qt.ItemDataRole.ForegroundRole).color().isValid())
        self.assertFalse(index.data(Qt.ItemDataRole.DecorationRole).pixmap(18).isNull())
        self.assertTrue(all(not occupation_icon(occ).pixmap(18).isNull() for occ in ICON_IDS))
        view.tabs.setCurrentIndex(2)
        view.combat_selector.setCurrentIndex(view.combat_selector.findData('rhps'))
        self.assertIn('300', str(cells(view.combat_table)))
        self.assertIn('回雪', str(cells(view.combat_skill)))
        self.assertIn('100%', str(cells(view.combat_targets)))
        self.assertNotIn('花间甲', str(cells(view.combat_targets)))
        view.open_player('云裳乙')
        self.assertNotIn('花间甲', str(cells(view.support_table)))

    def test_manual_records_share_scores_with_battle_and_copy_masked_text(self):
        actor = fixture(mask=True)
        view = self.view(actor)
        view.tabs.setCurrentIndex(1)
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
        view.tabs.setCurrentIndex(4)
        self.assertTrue(view.web_button.isHidden())

    def test_replacing_player_pages_releases_previous_models(self):
        import gc
        import weakref
        from PySide6.QtCore import QCoreApplication, QEvent
        view = self.view(fixture())
        view.open_player('云裳乙')
        old_page = weakref.ref(view.personal_dashboard)
        old_model = weakref.ref(view.skill_table.model())
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

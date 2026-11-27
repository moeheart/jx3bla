"""Keep battle row values, sort order and percentiles tied to the same metric."""
from copy import deepcopy
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from replayer.ActorReplayPro import ActorProReplayer


EFFECT_ONLY = {'status': 'incomplete', 'staticAttributes': 'available',
               'unmodeledEffects': ['附魔99999: atExecuteScript']}


class BattleMetricTests(unittest.TestCase):
    def actor(self, status):
        actor = ActorProReplayer.__new__(ActorProReplayer)
        names = {'first': 'A', 'second': 'B', 'healer': 'H'}
        values = {'first': {'rdps': 100.25, 'ndps': 900},
                  'second': {'rdps': 200.75, 'ndps': 300},
                  'healer': {'rdps': 50.5, 'ndps': 50}}
        tracker = NS(rdpsStatus=deepcopy(status), export=lambda *args: None,
                     getRdps=lambda player, kind='rdps': values[player][kind],
                     getRhps=lambda player, kind='rhps': 321)
        actor.bld = NS(log=[], info=NS(player={key: NS(name=name) for key, name in names.items()},
                                      getName=names.__getitem__))
        actor.bh = NS(sumTime=lambda kind: 10000)
        actor.startTime, actor.finalTime, actor.battleTime = 0, 10000, 10000
        actor.occDetailList = {'first': '4p', 'second': '7p', 'healer': '5h'}
        actor.zhenyanInfer = actor.stunCounter = actor.boostPredict = actor.baseAttribDict = {}
        actor.attributeStatus = deepcopy(status)
        actor.detail = {'attributeStatus': actor.attributeStatus}
        actor.statDict = [dict(name=names[key], occ=occ, rdps=9999, ndps=9999,
                               score=0, rdpsRank=99, scoreRank=99)
                          for key, occ in actor.occDetailList.items()]
        actor.logMode = False
        with patch('replayer.ActorReplayPro.CombatTracker', return_value=tracker):
            actor.ThirdStageAnalysis()
        actor.beginTime = 0
        actor.mapDetail = '25人英雄洛阳之战'
        actor.bossAnalyseName = '突利和顺'
        actor.win = 1
        actor.battleDict = actor.deathDict = actor.unusualDeathDict = {}
        actor.panelAttribDict = actor.jsonEquip = actor.strEquip = {}
        actor.hashGroup = lambda: 'synthetic-battle'
        actor.config = NS(item={key: {'active': int(key == 'yunchang')}
                               for key in ('xiangzhi', 'lingsu', 'lijing', 'butian', 'yunchang')})
        actor.fileNameInfo, actor.path, actor.bldDict, actor.window = [], '', {}, None
        return actor, values

    def run_personal(self, actor):
        metric_values = {'A': ('first', 0, 41, 91),
                         'B': ('second', 0, 79, 13),
                         'H': ('healer', 88, 23, 97)}

        def personal(*args):
            name = args[5]
            player, score, rdps_percent, ndps_percent = metric_values[name]
            rdps = int(actor.combatTracker.getRdps(player))
            ndps = int(actor.combatTracker.getRdps(player, 'ndps'))
            rank = {'general': {'rdps': {'num': 20, 'percent': rdps_percent},
                                'ndps': {'num': 20, 'percent': ndps_percent},
                                'score': {'num': 30, 'percent': 67}}}
            result = {'skill': {'general': {'rdps': rdps, 'ndps': ndps, 'score': score}},
                      'rank': rank}
            return NS(replay=lambda: None, result=result, rank=rank)

        with patch('replayer.ActorReplayPro.DpsReplayer', side_effect=personal), \
                patch('replayer.ActorReplayPro.YunChangXinJingReplayer', side_effect=personal):
            actor.OccAnalysis()

    def test_rows_receive_attributed_values_even_before_personal_replays(self):
        actor, _ = self.actor(EFFECT_ONLY)
        self.assertEqual([(row['rdps'], row['ndps']) for row in actor.statDict],
                         [(100, 900), (200, 300), (50, 50)])
        self.assertTrue(all(row['rdpsRank'] == -1 and row['scoreRank'] == -1
                            and row['rdpsRankNum'] == 0 for row in actor.statDict))

    def test_effect_only_uses_rdps_order_not_opposite_direct_damage_order(self):
        actor, _ = self.actor(EFFECT_ONLY)
        self.run_personal(actor)
        self.assertEqual([row['name'] for row in actor.statDict], ['B', 'A', 'H'])
        self.assertEqual([row['rdps'] for row in actor.statDict], [200, 100, 50])

    def test_sort_uses_unrounded_tracker_values(self):
        actor, values = self.actor(EFFECT_ONLY)
        values['first']['rdps'], values['second']['rdps'] = 200.1, 200.9
        self.run_personal(actor)
        self.assertEqual([row['name'] for row in actor.statDict], ['B', 'A', 'H'])
        self.assertEqual([row['rdps'] for row in actor.statDict[:2]], [200, 200])

    def test_qualified_percentiles_use_rdps_and_healer_score_is_retired(self):
        actor, _ = self.actor({'status': 'supported', 'staticAttributes': 'available'})
        self.run_personal(actor)
        rows = {row['name']: row for row in actor.statDict}
        self.assertEqual((rows['A']['rdpsRank'], rows['B']['rdpsRank']), (41, 79))
        self.assertFalse({'score', 'scoreRank', 'scoreRankNum'} & rows['H'].keys())
        self.assertEqual(rows['H']['rdpsRankNum'], 20)

    def test_unknown_targets_keep_measured_order_even_with_effect_warning(self):
        actor, _ = self.actor(dict(EFFECT_ONLY, unresolvedTargets=['unknown-target']))
        self.run_personal(actor)
        self.assertEqual([row['name'] for row in actor.statDict], ['A', 'B', 'H'])


if __name__ == '__main__':
    unittest.main()

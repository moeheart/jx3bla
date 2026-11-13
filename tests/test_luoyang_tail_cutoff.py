"""Late completion/reset cutoffs keep first-three tables and timelines aligned."""
import unittest

from tests.test_luoyang_heroic_first_three import encounter, event, finish
from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer as Tuli
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer as Tian
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer as Yiman


class TailCutoffTests(unittest.TestCase):
    def test_late_cutoff_clips_damage_calls_hits_and_repeated_finalization(self):
        cases = [(Tuli, '139360', '34238', 'stingCalls', '45494', 'waveHits', 'bossDamage'),
                 (Tian, '139382', '34866', 'swordCalls', '45972', 'slashHits', 'bossDamage'),
                 (Yiman, '139373', '34270', 'prisonCalls', '45899', 'chainHits', 'nightDamage')]
        for cls, template, buff, call_key, hit, hit_key, damage_key in cases:
            with self.subTest(boss=cls.__name__):
                r = encounter(cls, {'boss': (template, '本体')})
                r.analyseSecondStage(event('Skill', 2000, caster='p', target='boss', damageEff=1000))
                r.analyseSecondStage(event('Buff', 2500, caster='boss', target='p', id=buff, stack=1))
                r.analyseSecondStage(event('Skill', 6000, caster='p', target='boss', damageEff=9000))
                r.analyseSecondStage(event('Skill', 6000, caster='boss', target='p', id=hit, damage=100))
                for time, stack in [(7000, 0), (8000, 1), (9000, 0)]:
                    r.analyseSecondStage(event('Buff', time, caster='boss', target='p', id=buff, stack=stack))
                r.trimmedFinalTime = 5000
                finish(r)
                self.assertEqual(r.statDict['p'][damage_key], 1000)
                self.assertEqual(r.statDict['p'][call_key], 1)
                self.assertEqual(r.statDict['p'][hit_key], 0)
                self.assertEqual(r.detail['mechanicHits'], [])
                self.assertEqual(r.potList, [])
                self.assertEqual([(c['start'], c['duration']) for c in r.bh.log['call']['p']], [(2500, 2500)])
                self.assertEqual(r.detail['mechanics'][0]['end'], 5000)
                self.assertTrue(r.detail['mechanics'][0]['truncated'])
                r.getResult()
                self.assertEqual(r.statDict['p'][damage_key], 1000)
                self.assertEqual(r.statDict['p'][call_key], 1)
                self.assertEqual(sum(r.phaseTime), 4000)

    def test_tuli_completion_fallback_removes_closed_post_exit_call(self):
        r = encounter(Tuli, {'boss': ('139360', '突利和顺')})
        for e in [event('Skill', 2000, caster='p', target='boss', damageEff=1000),
                  event('Battle', 5000, id='boss', fight=0),
                  event('System', 5500, channel='MSG_SYS',
                        content='[全胜！25人英雄洛阳之战]：1/5，击败突利和顺！25人英雄(完成)'),
                  event('Buff', 6000, caster='boss', target='p', id='34238', stack=1),
                  event('Buff', 7000, caster='boss', target='p', id='34238', stack=0)]:
            r.analyseSecondStage(e)
        finish(r)
        self.assertEqual((r.win, r.finalTime), (1, 5000))
        self.assertEqual(r.statDict['p']['stingCalls'], 0)
        self.assertEqual(r.bh.log['call']['p'], [])
        self.assertEqual(r.detail['mechanics'], [])

    def test_tian_reset_is_not_overwritten_by_a_later_chest(self):
        r = encounter(Tian, {'boss': ('139382', '田承嗣'), 'box': ('140091', '宝箱')})
        for time in (2000, 12000):
            r.analyseSecondStage(event('Shout', time, id='boss', content='来战！正好让本将看看唐廷的斤两！'))
        r.analyseSecondStage(event('Scene', 16000, id='box', enter=1))
        finish(r)
        self.assertEqual((r.win, r.finalTime), (0, 12000))

    def test_chain_rows_and_bars_are_not_duplicated_by_get_result(self):
        r = encounter(Yiman, {'boss': ('139373', '寂夜'), 'chain': ('139716', '锁链')})
        r.analyseSecondStage(event('Scene', 2000, id='chain', enter=1))
        r.analyseSecondStage(event('Scene', 4000, id='chain', enter=0))
        finish(r)
        r.getResult()
        self.assertEqual(len(r.detail['chains']), 1)
        self.assertEqual(sum(e['skillid'] == '139716' for e in r.bh.log['environment']), 1)


if __name__ == '__main__':
    unittest.main()

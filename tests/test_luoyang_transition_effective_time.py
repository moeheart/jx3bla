"""Confirmed transition downtime preserves targets, damage, and healing pressure."""
import unittest

from tools.ValidateLuoyangLastTwo import replayer, event, damage
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina


def encounter(heroic=True):
    r = replayer(Shi, [('boss', '139365' if heroic else '139312', Shi.BOSS),
                       ('sha', '139363' if heroic else '139308', '煞将'),
                       ('sword', '138287', '玄天剑符'), ('fly', '139918', '飞行狼牙兵'),
                       ('lifu', '139388' if heroic else '139332', '李复'),
                       ('clone', '139399', Shi.BOSS), ('unknown', '999999', '其他可攻击物')])
    r.bld.info.map = '25人英雄洛阳之战' if heroic else '25人普通洛阳之战'
    return r


def begin(r, source='boss'):
    r.analyseSecondStage(event('Scene', 2000, id='sha', enter=1))
    r.analyseSecondStage(event('Scene', 2200, id='sword', enter=1))
    r.analyseSecondStage(event('Shout', 4000, id=source, content=Shi.TRANSITION_START))


def depart(r):
    r.analyseSecondStage(event('Scene', 4500, id='sha', enter=0))
    r.analyseSecondStage(event('Scene', 5000, id='sword', enter=0))


def finish(r, source='boss', time=10000):
    r.analyseSecondStage(event('Shout', time, id=source, content=Shi.TRANSITION_END))
    r.countFinal()


class TransitionEffectiveTimeTests(unittest.TestCase):
    def test_targets_remain_valid_then_only_dps_loses_confirmed_interval(self):
        for heroic in (False, True):
            with self.subTest(heroic=heroic):
                r = encounter(heroic)
                r.analyseSecondStage(damage(1500))
                begin(r)
                r.analyseSecondStage(damage(4200, target='sha'))
                depart(r)
                r.analyseSecondStage(event('Skill', 6000, caster='boss', target='p',
                                          id='45517', damage=900, damageEff=900))
                r.analyseSecondStage(event('Skill', 6500, caster='p', target='p', heal=800, healEff=800))
                finish(r)
                decision = r.detail['transitionPeriods'][0]['dpsExclusion']
                self.assertEqual((decision['start'], decision['end']), (5000, 10000))
                self.assertEqual((r.bh.sumTime('dps'), r.bh.sumTime('healer')), (15000, 20000))
                self.assertEqual(r.detail['effectiveTime'], 15000)
                self.assertEqual(r.detail['effectiveTimeDps'], 15000)
                self.assertEqual(r.detail['effectiveTimeHealer'], 20000)
                self.assertEqual(r.statDict['p']['battle']['mainDps'], 6)
                self.assertEqual(r.statDict['p']['battle']['shaDamage'], 100)
                self.assertEqual(r.hps['p'], 800)
                self.assertEqual(sum(r.phaseTime), 20000)
                before = (list(r.bh.badPeriodDpsLog), r.detail['effectiveTime'])
                r.countFinal()
                self.assertEqual(before, (r.bh.badPeriodDpsLog, r.detail['effectiveTime']))

    def test_silence_without_departure_or_owned_complete_dialogue_is_not_excluded(self):
        for kind in ('no_objects', 'no_end', 'wrong_begin', 'wrong_end', 'still_present'):
            with self.subTest(kind=kind):
                r = encounter()
                if kind == 'no_objects':
                    r.analyseSecondStage(event('Shout', 4000, id='boss', content=Shi.TRANSITION_START))
                else:
                    begin(r, 'clone' if kind == 'wrong_begin' else 'boss')
                    if kind != 'still_present': depart(r)
                if kind == 'no_end': r.countFinal()
                else: finish(r, 'clone' if kind == 'wrong_end' else 'boss')
                self.assertEqual(r.bh.sumTime('dps'), 20000)

    def test_any_observed_effective_target_damage_including_reflection_vetoes_exclusion(self):
        for target in ('boss', 'unknown', 'reflection'):
            with self.subTest(target=target):
                r = encounter(); begin(r); depart(r)
                if target == 'reflection':
                    hit = event('Skill', 7000, caster='boss', target='p', resultType=1,
                                reflectionDamage=900, fullResult={'5': '900', '13': '0'})
                else:
                    hit = damage(7000, target=target)
                r.analyseSecondStage(hit)
                finish(r)
                self.assertEqual(r.bh.sumTime('dps'), 20000)
                self.assertEqual(r.detail['transitionPeriods'][0]['dpsExclusion']['reason'],
                                 'effective_damage_inside_candidate')

    def test_a_new_flying_add_inside_transition_preserves_its_entire_lifetime(self):
        r = encounter(); begin(r); depart(r)
        r.analyseSecondStage(event('Scene', 6000, id='fly', enter=1))
        r.analyseSecondStage(damage(6500, target='fly'))
        r.analyseSecondStage(event('Death', 8000, id='fly'))
        r.analyseSecondStage(event('Shout', 10000, id='boss', content=Shi.TRANSITION_END))
        r.analyseSecondStage(event('Scene', 11000, id='fly', enter=0))
        r.countFinal()
        self.assertEqual(r.detail['transitionPeriods'][0]['dpsExclusion']['start'], 8000)
        self.assertEqual(r.bh.sumTime('dps'), 18000)

    def test_late_end_outside_failure_cutoff_cannot_create_transition_downtime(self):
        r = encounter(); begin(r); depart(r)
        r.trimmedFinalTime = 8000
        finish(r)
        self.assertEqual((r.finalTime, r.bh.sumTime('dps'), r.bh.sumTime('healer')), (8000, 7000, 7000))
        self.assertEqual(r.detail['transitionPeriods'][0]['dpsExclusion']['reason'],
                         'missing_in_bounds_transition_end')

    def test_completed_transition_and_late_tail_use_union_before_table_denominator(self):
        r = encounter()
        r.analyseSecondStage(damage(1500))
        begin(r); depart(r)
        r.trimmedFinalTime = 12000
        finish(r)
        self.assertEqual((r.bh.sumTime('dps'), r.bh.sumTime('healer')), (6000, 11000))
        self.assertEqual(r.detail['effectiveTimeDps'], 6000)
        self.assertEqual(r.statDict['p']['battle']['mainDps'], 16)
        self.assertEqual(sum(r.phaseTime), 11000)

    def test_normal_damage_gap_and_reforge_shout_are_not_transition_boundaries(self):
        r = encounter()
        r.analyseSecondStage(damage(2000))
        r.analyseSecondStage(event('Shout', 6000, id='lifu',
                                  content='速将散落的“残刃”聚拢于我，我要以内力重铸此剑！'))
        r.analyseSecondStage(damage(19000)); r.countFinal()
        self.assertEqual(r.bh.sumTime('dps'), 20000)

    def test_ashina_mechanic_dialogue_and_soul_keep_both_denominators(self):
        r = replayer(Ashina)
        r.analyseSecondStage(event('Shout', 3000, id='boss', content='什么！？废物！'))
        r.analyseSecondStage(event('Cast', 4000, id='45916'))
        r.analyseSecondStage(event('Buff', 4500, id='34251', stack=1))
        r.analyseSecondStage(damage(5000))
        r.analyseSecondStage(event('Buff', 6000, id='34251', stack=0))
        r.countFinal()
        self.assertEqual((r.detail['effectiveTimeDps'], r.detail['effectiveTimeHealer']), (20000, 20000))


if __name__ == '__main__':
    unittest.main()

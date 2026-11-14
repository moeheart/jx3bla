"""Paired transition evidence excludes output time without erasing real hits."""
import unittest

from tests.test_luoyang_heroic_first_three import encounter, event, finish
from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer


def buff(time, identifier, player='p', caster='boss', stack=1, **kwargs):
    return event('Buff', time, id=identifier, caster=caster, target=player,
                 stack=stack, delete='false' if stack else 'true', isValid=bool(stack), **kwargs)


def excluded(history, time):
    # Match the existing CombatTracker/SkillCounter (start, end] contract.
    return next((state for boundary, state in reversed(history.badPeriodDpsLog)
                 if time > boundary), 0)


class FirstThreeDowntimeTests(unittest.TestCase):
    def tuli(self):
        return encounter(TuliHeshunReplayer, {'boss': ('139360', '突利和顺'),
                         'fake': ('139405', '突利和顺'), 'add': ('139716', '锁链')})

    def tian(self):
        return encounter(TianChengsiReplayer, {'boss': ('139382', '田承嗣'),
                         'sword': ('140386', '天陨巨剑'), 'second': ('141799', '天陨巨剑'),
                         'soldier': ('139396', '骨朵兵')})

    def test_tuli_field_end_preserves_early_resume_hit_and_healing(self):
        replay = self.tuli()
        for row in (buff(2000, '35857'), buff(2050, '35857', 'q'),
                    buff(3000, '34490'), buff(3100, '34490', 'q'),
                    event('Skill', 4000, caster='boss', target='p', damageEff=100, damage=100),
                    buff(5000, '34490', stack=0), buff(6000, '34490', 'q', stack=0),
                    event('Skill', 6000, caster='p', target='boss', damageEff=283),
                    buff(6069, '35858'), buff(6100, '35858', 'q')):
            replay.analyseSecondStage(row)
        finish(replay)
        evidence = replay.detail['downtimeEvidence']
        self.assertEqual(len(evidence), 1)
        self.assertEqual((evidence[0]['start'], evidence[0]['boundaryEnd'], evidence[0]['end']),
                         (2000, 6000, 5999))
        self.assertTrue(evidence[0]['affectDps'])
        self.assertFalse(evidence[0]['affectHealer'])
        self.assertEqual(excluded(replay.bh, 5999), 1)
        self.assertEqual(excluded(replay.bh, 6000), 0)
        self.assertEqual(replay.statDict['p']['bossDamage'], 283)
        self.assertEqual(replay.detail['effectiveTimeDps'], 26001)
        self.assertEqual(replay.detail['effectiveTimeHealer'], 30000)
        finish(replay)
        self.assertEqual(len(replay.detail['downtimeEvidence']), 1)

    def test_tuli_requires_both_owned_valid_signals(self):
        for missing in ('start', 'end', 'foreign_end', 'inactive_start'):
            with self.subTest(missing=missing):
                replay = self.tuli()
                if missing != 'start':
                    start = buff(2000, '35857')
                    if missing == 'inactive_start':
                        start.isValid = False
                    replay.analyseSecondStage(start)
                if missing != 'end':
                    replay.analyseSecondStage(buff(5000, '35858',
                        caster='fake' if missing == 'foreign_end' else 'boss'))
                finish(replay)
                self.assertEqual(replay.bh.sumTime('dps'), 30000)
                self.assertEqual(replay.bh.sumTime('healer'), 30000)

    def test_tuli_keeps_pause_with_interior_damage_to_another_objective(self):
        replay = self.tuli()
        for row in (buff(2000, '35857'),
                    event('Skill', 4000, caster='p', target='add', damageEff=1200),
                    buff(8000, '35858')):
            replay.analyseSecondStage(row)
        finish(replay)
        self.assertEqual(replay.detail['downtimeEvidence'][0]['reason'], 'effective_damage_inside_candidate')
        self.assertEqual(replay.bh.sumTime('dps'), 30000)

    def test_tian_excludes_only_preparation_and_keeps_sword_boundary_damage(self):
        replay = self.tian()
        for row in (event('Shout', 2000, id='boss', content='抬头看好了——这一剑，送你们上路！'),
                    event('Scene', 6000, id='sword', enter=1),
                    event('Skill', 6000, caster='p', target='sword', damageEff=1000),
                    event('Skill', 7000, caster='p', target='sword', damageEff=500),
                    event('Death', 10000, id='sword')):
            replay.analyseSecondStage(row)
        finish(replay)
        self.assertEqual(replay.bh.sumTime('dps'), 26001)
        self.assertEqual(replay.bh.sumTime('healer'), 30000)
        self.assertEqual(replay.statDict['p']['swordDamage'], 1500)
        self.assertEqual([excluded(replay.bh, time) for time in (5999, 6000, 7000)], [1, 0, 0])

    def test_tian_preserves_existing_sword_or_any_reflected_damage(self):
        for existing in (True, False):
            with self.subTest(existing=existing):
                replay = self.tian()
                if existing:
                    replay.analyseSecondStage(event('Scene', 1500, id='sword', enter=1))
                replay.analyseSecondStage(event('Shout', 2000, id='boss', content='哼哼！不错，那么第二剑呢？'))
                if not existing:
                    replay.analyseSecondStage(event('Skill', 3000, caster='soldier', target='p',
                        damage=0, damageEff=0, heal=0, healEff=0, resultType=1,
                        reflectionDamage=12520, fullResult={'5': '12520', '13': '0'}))
                replay.analyseSecondStage(event('Scene', 6000, id='second', enter=1))
                finish(replay)
                self.assertEqual(replay.bh.sumTime('dps'), 30000)
                self.assertEqual(replay.detail['downtimeEvidence'][0]['reason'],
                    'sword_already_present' if existing else 'effective_damage_inside_candidate')

    def test_missing_sword_entry_or_resume_after_cutoff_does_not_fill_to_end(self):
        replay = self.tian()
        replay.analyseSecondStage(event('Shout', 2000, id='boss', content='抬头看好了——这一剑，送你们上路！'))
        finish(replay)
        self.assertEqual(replay.bh.sumTime('dps'), 30000)
        replay = self.tuli()
        replay.analyseSecondStage(buff(2000, '35857'))
        replay.analyseSecondStage(buff(6000, '35858'))
        replay.trimmedFinalTime = 5000
        finish(replay)
        self.assertFalse(replay.detail['downtimeEvidence'][0]['affectDps'])

    def test_twins_ring_and_single_boss_remain_active(self):
        replay = encounter(YimanTwinsReplayer, {'night': ('139373', '伊曼·寂夜'),
            'fire': ('139376', '伊曼·逐焰'), 'ring': ('139717', ''), 'chain': ('139716', '锁链')})
        for row in (event('Scene', 2000, id='ring', enter=1),
                    event('Skill', 3000, caster='p', target='night', damageEff=1000),
                    event('Skill', 4000, caster='p', target='chain', damageEff=500),
                    event('Shout', 10000, id='fire', content='姐姐！！—炸碎你们,统统炸碎！！！'),
                    event('Skill', 11000, caster='p', target='fire', damageEff=2000)):
            replay.analyseSecondStage(row)
        finish(replay)
        self.assertEqual(replay.bh.sumTime('dps'), 30000)
        self.assertEqual(replay.bh.sumTime('healer'), 30000)
        self.assertEqual(replay.statDict['p']['chainDamage'], 500)


if __name__ == '__main__':
    unittest.main()

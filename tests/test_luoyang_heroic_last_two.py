"""Heroic mechanics observed on 2026-11-13, without personal log fixtures."""
import unittest

from tools.ValidateLuoyangLastTwo import damage, event, replayer
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi


class HeroicLastTwoTests(unittest.TestCase):
    def test_fuyan_is_construct_and_has_separate_damage(self):
        r = replayer(Ashina, [("boss", "139378", Ashina.BOSS), ("add", "139394", "伏焰")])
        r.analyseSecondStage(event("Scene", 2000, id="add", enter=1))
        r.analyseSecondStage(damage(3000, "add"))
        r.analyseSecondStage(event("Cast", 4000, id="46676", caster="add"))
        r.analyseSecondStage(event("Death", 5000, id="add"))
        r.countFinal()
        stats = r.statDict['p']['battle']
        self.assertEqual((stats['constructDamage'], stats['fuyanDamage'], stats['mainDps']), (100, 100, 0))
        self.assertEqual(r.detail['constructPeriods'][0]['duration'], 3)
        self.assertEqual(r.win, 0)
        casts = [e for e in r.bh.log['environment'] if e['skillid'] == '46676']
        self.assertEqual([(e['skillname'], e['type']) for e in casts], [('伏焰突破', 'cast')])

    def test_heroic_constructs_and_clones_stay_separate(self):
        r = replayer(Ashina, [("boss", "139378", Ashina.BOSS), ("bird", "139404", "玄隼"),
                             ("tiger", "139398", "炽虎"), ("clone", "139377", Ashina.BOSS)])
        for target in ('bird', 'tiger', 'clone'):
            r.analyseSecondStage(damage(3000, target))
        r.countFinal()
        self.assertEqual(r.statDict['p']['battle']['constructDamage'], 200)
        self.assertEqual(r.statDict['p']['battle']['mainDps'], 0)

    def test_lock_and_remnant_refreshes_are_not_extra_calls(self):
        r = replayer(Ashina)
        for buff, key in [('34394', 'fuyanCalls'), ('34357', 'remnantCalls')]:
            for time, stack in [(2000, 1), (2500, 1), (3000, 0), (4000, 1)]:
                r.analyseSecondStage(event('Buff', time, id=buff, stack=stack))
            self.assertEqual(r.statDict['p']['battle'][key], 2)
        r.countFinal()
        self.assertEqual(len(r.bh.log['call']['p']), 4)

    def test_heroic_damage_observations_do_not_assign_blame(self):
        r = replayer(Ashina)
        for skill, key in [('46134', 'remnantHits'), ('46176', 'fireTrackHits'), ('46751', 'fuyanHeatHits')]:
            for time in (2000, 2050):
                r.analyseSecondStage(event('Skill', time, id=skill, damage=100))
            self.assertEqual(r.statDict['p']['battle'][key], 1)
        r.countFinal()
        self.assertTrue(all(pot[2] == 0 for pot in r.potList))

    def test_heroic_shouts_require_main_speaker(self):
        r = replayer(Ashina, [("boss", "139378", Ashina.BOSS), ("clone", "139377", Ashina.BOSS)])
        content = '伏焰，起——！给本帅碾过去！'
        r.analyseSecondStage(event('Shout', 2000, id='clone', content=content))
        r.analyseSecondStage(event('Shout', 3000, id='boss', content=content))
        self.assertEqual([(e['name'], e['time']) for e in r.detail['shouts']], [('伏焰出击', 3000)])

    def test_flying_add_damage_is_separate_and_clipped(self):
        r = replayer(Shi, [("boss", "139365", Shi.BOSS), ("flying", "139918", '飞行狼牙兵')])
        r.analyseSecondStage(damage(2000, 'boss'))
        r.analyseSecondStage(damage(3000, 'flying'))
        r.analyseSecondStage(damage(6000, 'flying'))
        r.trimmedFinalTime = 5000
        r.countFinal()
        self.assertEqual(r.statDict['p']['battle']['flyingDamage'], 100)
        self.assertEqual(r.statDict['p']['battle']['mainDamage'], 100)
        self.assertEqual(set(r.bh.mainTargets), {'boss'})

    def test_fragment_counter_uses_stack_increases_and_one_buff(self):
        r = replayer(Shi)
        for time, stack in [(2000, 1), (2500, 1), (3000, 2), (4000, 0), (5000, 2)]:
            for buff in ('34278', '34725'):
                r.analyseSecondStage(event('Buff', time, id=buff, stack=stack, caster='p'))
        r.countFinal()
        self.assertEqual(r.statDict['p']['battle']['fragmentPickups'], 4)
        self.assertEqual(len(r.bh.log['call']['p']), 2)
        self.assertNotIn('fragmentDeliveries', r.statDict['p']['battle'])

    def test_wings_are_new_applications_and_flight_is_on_call_timeline(self):
        r = replayer(Shi)
        for time, stack in [(2000, 1), (3000, 1), (4000, 0), (5000, 1)]:
            r.analyseSecondStage(event('Buff', time, id='34324', stack=stack))
        r.countFinal()
        self.assertEqual(r.statDict['p']['battle']['wingCalls'], 2)
        calls = r.bh.log['call']['p']
        self.assertEqual([e['duration'] for e in calls], [2000, 16000])

    def test_third_phase_shouts_and_lifu_prompt_do_not_invent_phase(self):
        r = replayer(Shi, [("boss", "139365", Shi.BOSS), ("lifu", "139388", '李复'),
                          ("clone", "139397", Shi.BOSS)])
        prompt = '速将散落的“残刃”聚拢于我，我要以内力重铸此剑！'
        r.analyseSecondStage(event('Shout', 2000, id='p', content=prompt))
        r.analyseSecondStage(event('Shout', 3000, id='lifu', content=prompt))
        r.analyseSecondStage(event('Shout', 4000, id='clone', content='分光化影！'))
        self.assertEqual(r.phase, 1)
        r.analyseSecondStage(event('Cast', 5000, id='45746'))
        r.analyseSecondStage(event('Shout', 5030, id='boss', content='分光化影！'))
        r.countFinal()
        self.assertEqual(r.detail['P3Time'], 16)
        self.assertEqual([e['name'] for e in r.detail['shouts']], ['重铸残刃', '戾月崩斩'])

    def test_maximum_stacks_and_mechanic_counters_obey_late_cutoff(self):
        for cls, buff, key, call, call_key in [(Ashina, '34376', 'abyssMax', '34394', 'fuyanCalls'),
                                              (Shi, '34619', 'invasionMax', '34324', 'wingCalls')]:
            r = replayer(cls)
            r.analyseSecondStage(event('Buff', 2000, id=buff, stack=1))
            r.analyseSecondStage(event('Buff', 3000, id=call, stack=1))
            r.analyseSecondStage(event('Buff', 4000, id=call, stack=0))
            r.analyseSecondStage(event('Buff', 6000, id=buff, stack=2))
            r.analyseSecondStage(event('Buff', 6000, id=call, stack=1))
            r.trimmedFinalTime = 5000
            r.countFinal()
            self.assertEqual(r.statDict['p']['battle'][key], 1)
            self.assertEqual(r.statDict['p']['battle'][call_key], 1)

    def test_tail_failures_and_hits_are_removed_with_the_cutoff(self):
        for cls, buff in [(Ashina, '34376'), (Shi, '34619')]:
            r = replayer(cls)
            r.analyseSecondStage(event('Buff', 6000, id=buff, stack=5))
            if cls == Ashina:
                r.analyseSecondStage(event('Skill', 6000, id='46134', damage=10))
            else:
                r.analyseSecondStage(event('Skill', 6000, id='46077', damage=10))
            self.assertTrue(r.potList)
            r.trimmedFinalTime = 5000
            r.countFinal()
            self.assertEqual(r.potList, [])
            self.assertEqual(r.detail['mechanicEvents'], [])


if __name__ == '__main__':
    unittest.main()

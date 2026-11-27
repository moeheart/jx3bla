"""Native seasonal boss credit needs same-entity terminal combat evidence."""
import contextlib
import io
from types import SimpleNamespace as NS
import unittest
from unittest.mock import mock_open, patch

from data.BattleLogData import BattleLogData
from data.DataContent import SingleDataSystem
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer as Tian
from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer as Tuli
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi
from replayer.boss.luoyangzhizhan.WinEvidence import LuoyangWinEvidence
from tools.LoadData import LuaTableAnalyserToDict
from tools.ValidateLuoyangLastTwo import event, damage


CASES = ((Tian, '田承嗣', '139329', '139382'),
         (Ashina, '阿史那承庆', '139323', '139378'),
         (Shi, '史朝义', '139312', '139365'))
DIFFICULTIES = ('25人普通', '25人英雄')


def honor(difficulty, time=19500, tier='入门', progress=7, target=15,
          channel='MSG_SYS', content=None):
    if content is None:
        content = '赛季荣誉[%s首领击伤·%s]：%s/%s\\n' % (difficulty, tier, progress, target)
    # Exercise exactly the native type18 payload interpretation, including
    # the outer Lua quotes and literal backslash-n used by JCL messages.
    payload = '{"%s","%s"}' % (content, channel)
    row = ['1', '1', '1794690000', str(time), '18',
           LuaTableAnalyserToDict().analyse(payload, delta=1)]
    result = SingleDataSystem()
    result.setByJcl(row)
    return result


def exit_event(time=20000, **fields):
    values = dict(id='boss', fight=0, hp=100, hpMax=100)
    values.update(fields)
    return event('Battle', time, **values)


def replayer(case, difficulty, bld=None):
    cls, boss, normal, heroic = case
    if bld is None:
        bld = BattleLogData()
        bld.info.map = difficulty + '洛阳之战'
        bld.info.skill = {}
        bld.info.addPlayer('p', '匿名', '2', '0')
        for key, template in (('boss', heroic if difficulty == '25人英雄' else normal),
                              ('other', heroic if difficulty == '25人英雄' else normal),
                              ('clone', '0')):
            bld.info.addNPC(key, boss)
            bld.info.npc[key].templateID = template
        start, end = 1000, 31000
    else:
        start, end = bld.log[0].time, bld.log[-1].time
    r = cls(bld, {key: value.occ for key, value in bld.info.player.items()},
            start, end, end-start, boss, NS(item={'actor': {'filter': ''}}))
    r.initBattle()
    r.recordEquipment({})
    return r


def finish(r, events):
    for item in sorted(events, key=lambda item: item.time):
        r.analyseSecondStage(item)
    r.trimTime()
    r.getResult()
    return r


class SeasonalVictoryTests(unittest.TestCase):
    def test_three_bosses_two_difficulties_both_native_tiers(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                for tier, target in (('入门', 15), ('精通', 25)):
                    for progress in (1, target):
                        with self.subTest(boss=case[1], difficulty=difficulty, tier=tier, progress=progress):
                            message = honor(difficulty, tier=tier, target=target, progress=progress)
                            r = finish(replayer(case, difficulty), [damage(19000), message, exit_event()])
                            self.assertEqual((r.win, r.finalTime), (1, 20000))
                            self.assertEqual(r.detail['winReason'], 'seasonal_boss_credit_and_combat_exit')
                            evidence = r.detail['winEvidence'][-1]
                            self.assertEqual((evidence['npcID'], evidence['honorTier'], evidence['honorProgress'],
                                              evidence['honorTarget']), ('boss', tier, progress, target))
                            self.assertEqual(r.bh.sumTime('dps'), 19000)

    def test_parser_retains_native_honor_outside_combat_list_and_all_bosses_use_it(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                with self.subTest(boss=case[1], difficulty=difficulty):
                    template = case[3] if difficulty == '25人英雄' else case[2]
                    rows = [
                        '1\t1\t1794690000\t1000\t4\t{10,"匿名",2,0,0,{}}',
                        '2\t2\t1794690000\t1000\t8\t{20,"%s",%s,0,0,0,0,0}' % (case[1], template),
                        '3\t3\t1794690000\t1000\t9\t{20,true,100,100,0,0}',
                        '4\t4\t1794690000\t19000\t21\t{10,20,0,1,2477,1,0,0,{[0]=100,[13]=100}}',
                        '5\t5\t1794690000\t20000\t9\t{20,false,100,100,0,0}',
                        '6\t6\t1794690000\t20500\t18\t{"赛季荣誉[%s首领击伤·入门]：7/15\\n","MSG_SYS"}' % difficulty,
                    ]
                    filename = '2026-11-14-19-53-35-%s洛阳之战(%s)-%s(%s).jcl' % (
                        difficulty, '836' if difficulty == '25人英雄' else '835', case[1], template)
                    bld = BattleLogData()
                    with patch('builtins.open', mock_open(read_data=('\n'.join(rows)+'\n').encode('utf-8'))):
                        with contextlib.redirect_stdout(io.StringIO()):
                            bld.loadFromJcl(filename)
                    self.assertEqual([x.dataType for x in bld.log], ['Battle', 'Skill', 'Battle'])
                    self.assertEqual(len(bld.systemMessages), 1)
                    self.assertEqual(bld.systemMessages[0].channel, 'MSG_SYS')
                    r = finish(replayer(case, difficulty, bld), bld.log)
                    self.assertEqual((r.win, r.finalTime), (1, 20000))

    def test_exact_message_channel_difficulty_and_progress_bounds(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                text = honor(difficulty).content
                noises = [
                    honor(difficulty, channel='MSG_OTHER'),
                    honor(difficulty, channel='MSG_NOTICE_GREEN'),
                    honor('25人英雄' if difficulty == '25人普通' else '25人普通'),
                    honor(difficulty, content='转发：'+text),
                    honor(difficulty, content=text+'其他文字'),
                    honor(difficulty, content=text.replace('首领击伤', '首领击杀')),
                    honor(difficulty, content=text.replace('赛季荣誉', '赛季任务')),
                    honor(difficulty, content=text.replace('：', ':')),
                    honor(difficulty, content=text.replace('·入门', '·大师')),
                    honor(difficulty, progress=0), honor(difficulty, progress=-1),
                    honor(difficulty, progress=16), honor(difficulty, progress='07'),
                    honor(difficulty, progress='7.0'), honor(difficulty, target=25),
                    honor(difficulty, target='015'), honor(difficulty, target=0),
                    honor(difficulty, tier='精通', target=15),
                    honor(difficulty, tier='精通', target=25, progress=26),
                ]
                noises += [event('Shout', 19500, id=sender, content=text) for sender in ('boss', 'p', '0')]
                for noise in noises:
                    with self.subTest(boss=case[1], difficulty=difficulty, noise=vars(noise)):
                        self.assertEqual(finish(replayer(case, difficulty),
                                                [damage(19000), noise, exit_event()]).win, 0)

    def test_requires_recent_positive_player_damage_and_same_real_entity_exit(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                h = honor(difficulty)
                variants = {
                    'honor_alone': [h],
                    'no_damage': [h, exit_event()],
                    'no_exit': [damage(19000), h],
                    'different_main_entity': [damage(19000), h, exit_event(id='other')],
                    'same_name_clone_exit': [damage(19000), h, exit_event(id='clone')],
                    'same_name_clone_damage': [damage(19000, target='clone'), h, exit_event()],
                    'npc_damage': [event('Skill', 19000, caster='clone', target='boss', damageEff=100), h, exit_event()],
                    'zero_damage': [event('Skill', 19000, caster='p', target='boss', damageEff=0), h, exit_event()],
                    'stale_damage': [damage(14000), h, exit_event()],
                    'honor_before_damage': [honor(difficulty, time=18999), damage(19000), exit_event()],
                    'honor_after_window': [damage(19000), exit_event(), honor(difficulty, time=24001)],
                    'stale_exit': [damage(19000), h, exit_event(24001)],
                }
                for label, rows in variants.items():
                    with self.subTest(boss=case[1], difficulty=difficulty, boundary=label):
                        self.assertEqual(finish(replayer(case, difficulty), rows).win, 0)

    def test_timing_window_includes_exact_boundary_and_message_after_exit(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                for last, message, end in ((15000, 20000, 20000), (19000, 24000, 20000),
                                           (19000, 19000, 24000), (19000, 20500, 20000)):
                    with self.subTest(boss=case[1], difficulty=difficulty, times=(last, message, end)):
                        r = finish(replayer(case, difficulty),
                                   [damage(last), honor(difficulty, time=message), exit_event(end)])
                        self.assertEqual((r.win, r.finalTime), (1, end))

    def test_resumed_damage_combat_or_scene_entry_invalidates_candidate(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                valid = [damage(19000), honor(difficulty), exit_event()]
                for later in (damage(21000), exit_event(21000, fight=1),
                              event('Scene', 21000, id='boss', enter=1)):
                    with self.subTest(boss=case[1], difficulty=difficulty, kind=later.dataType):
                        self.assertEqual(finish(replayer(case, difficulty), valid+[later]).win, 0)
                # A fresh exit after a resumed attempt cannot reuse old credit.
                rows = valid+[exit_event(21000, fight=1), damage(22000), exit_event(23000)]
                self.assertEqual(finish(replayer(case, difficulty), rows).win, 0)
                # Another NPC's entrance does not invalidate the real boss.
                rows = valid+[event('Scene', 21000, id='clone', enter=1)]
                self.assertEqual(finish(replayer(case, difficulty), rows).win, 1)

    def test_early_cutoff_and_changed_map_reject_later_credit(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                rows = [damage(19000), honor(difficulty), exit_event()]
                r = replayer(case, difficulty)
                r.trimmedFinalTime = 18000
                self.assertEqual((finish(r, rows).win, r.finalTime), (0, 18000))
                for map_name in ('25人普通其他副本', '10人普通洛阳之战', '其他地图'):
                    with self.subTest(boss=case[1], difficulty=difficulty, map=map_name):
                        r = replayer(case, difficulty)
                        r.bld.info.map = map_name
                        self.assertEqual(finish(r, rows).win, 0)

    def test_honor_after_explicit_failure_cutoff_cannot_promote_an_earlier_exit(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                with self.subTest(boss=case[1], difficulty=difficulty):
                    r = replayer(case, difficulty)
                    r.trimmedFinalTime = 20200
                    finish(r, [damage(19000), exit_event(), honor(difficulty, time=20500)])
                    self.assertEqual(r.win, 0)
                    self.assertLessEqual(r.finalTime, 20200)

    def test_low_hp_raid_exit_and_generic_rewards_are_not_victory(self):
        for case in CASES:
            for difficulty in DIFFICULTIES:
                for content in ('获得了150点历练值。', '获得了150点祈愿值。',
                                '[茗伊插件]成功分享：击败%s！%s' % (case[1], difficulty),
                                '赛季荣誉[参与团队秘境·入门]：7/15'):
                    for hp in (0, 1, 100):
                        with self.subTest(boss=case[1], difficulty=difficulty, content=content, hp=hp):
                            rows = [damage(19000), honor(difficulty, content=content),
                                    exit_event(hp=hp), exit_event(20001, id='p')]
                            self.assertEqual(finish(replayer(case, difficulty), rows).win, 0)

    def test_battle_exit_and_honor_alone_do_not_confirm_first_or_third_boss(self):
        for difficulty in DIFFICULTIES:
            for boss, template in (('突利和顺', '139360'), ('伊曼·寂夜', '139373')):
                with self.subTest(difficulty=difficulty, boss=boss):
                    r = NS(bld=NS(info=NS(map=difficulty+'洛阳之战', npc={'boss':NS(templateID=template)}),
                                  systemMessages=[]), statDict={'p':{}}, startTime=1000,
                           finalTime=31000, trimmedFinalTime=None)
                    tracker = LuoyangWinEvidence(r, boss, (template,))
                    for item in (damage(19000), honor(difficulty), exit_event()):
                        tracker.observe(item)
                    self.assertIsNone(tracker.resolve())

    def test_tuli_corpse_or_credit_with_delayed_departure(self):
        case = (Tuli, '突利和顺', '139306', '139360')
        for difficulty in DIFFICULTIES:
            for has_corpse, has_credit in ((True, True), (True, False), (False, True)):
                with self.subTest(difficulty=difficulty, corpse=has_corpse, credit=has_credit):
                    r = replayer(case, difficulty)
                    events = [damage(19000)]
                    if has_corpse:
                        r.bld.tuliCorpseSpawns = [(19211, 'boss', '299')]
                    if has_credit:
                        events += [honor(difficulty, 19023, tier='大师', progress=27, target=50),
                                   event('Scene', 25123, id='boss', enter=0)]
                    finish(r, events)
                    self.assertEqual((r.win, r.finalTime), (1, 19023 if has_credit else 19211))
                    self.assertEqual(r.detail['winEvidence'][-1]['npcID'], 'boss')
                    if has_corpse:
                        self.assertEqual(r.detail['winEvidence'][-1]['corpseTime'], 19211)

    def test_tuli_rejects_stale_corpse_or_unrelated_credit(self):
        case = (Tuli, '突利和顺', '139306', '139360')
        normal = '25人普通'
        exit_boss = event('Scene', 25123, id='boss', enter=0)
        variants = (
            ([(18999, 'boss', '299')], [], None),
            ([(19211, 'other', '299')], [], None),
            ([(19211, 'boss', '299')], [damage(21000)], None),
            ([(19211, 'boss', '299')], [], 19100),
            ([], [honor('25人英雄', 19023), exit_boss], None),
            ([], [honor(normal, 19023), event('Scene', 25123, id='clone', enter=0)], None),
            ([], [honor(normal, 19023), exit_boss, event('Scene', 26000, id='boss', enter=1)], None),
            ([], [honor(normal, 19023), exit_boss], 20000),
        )
        for corpses, events, cutoff in variants:
            with self.subTest(corpses=corpses, events=events, cutoff=cutoff):
                r = replayer(case, normal)
                r.bld.tuliCorpseSpawns = corpses
                if cutoff is not None:
                    r.trimmedFinalTime = cutoff
                self.assertEqual(finish(r, [damage(19000), *events]).win, 0)


if __name__ == '__main__':
    unittest.main()

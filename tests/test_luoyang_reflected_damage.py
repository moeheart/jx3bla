"""Returned JCL damage affects boss tables without synthesizing boss events."""
from copy import deepcopy
import unittest

from data.DataContent import SingleDataSkill
from tests.test_luoyang_heroic_first_three import encounter, event, finish
from tools.ValidateLuoyangLastTwo import replayer
from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunReplayer as Tuli
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer as Tian
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer as Yiman
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi


CASES = (
    (Tuli, {'boss': ('139360', '突利和顺'), 'clone': ('139412', '突利和顺')},
     {'boss': ('bossDamage',), 'clone': ()}),
    (Tian, {'boss': ('139382', '田承嗣'), 'sword': ('140386', '天陨巨剑')},
     {'boss': ('bossDamage',), 'sword': ('swordDamage',)}),
    (Yiman, {'boss': ('139373', '伊曼·寂夜'), 'fire': ('139376', '伊曼·逐焰'),
             'chain': ('139716', '锁链'), 'inert': ('139374', '机关')},
     {'boss': ('nightDamage',), 'fire': ('fireDamage',), 'chain': ('chainDamage',), 'inert': ('inertDamage',)}),
    (Ashina, {'boss': ('139378', '阿史那承庆'), 'fuyan': ('139394', '伏焰'),
              'bird': ('139404', '玄隼'), 'clone': ('139377', '阿史那承庆')},
     {'boss': ('mainDamage',), 'fuyan': ('constructDamage', 'fuyanDamage'),
      'bird': ('constructDamage',), 'clone': ()}),
    (Shi, {'boss': ('139365', '史朝义'), 'sha': ('139363', '煞将'),
           'flying': ('139918', '飞行狼牙兵'), 'clone': ('139397', '史朝义')},
     {'boss': ('mainDamage',), 'sha': ('shaDamage',), 'flying': ('flyingDamage',), 'clone': ()}),
)


def make(cls, templates):
    if cls in (Tuli, Tian, Yiman):
        return encounter(cls, templates)
    result = replayer(cls, [(key, template, name) for key, (template, name) in templates.items()])
    result.bld.info.map = '25人英雄洛阳之战'
    return result


def reflected(time=2000, npc='boss', amount=100):
    result = SingleDataSkill()
    result.setByJcl(['', '16', '1793577600', str(time), '21',
                    {'1': npc, '2': 'p', '3': '1', '4': '1', '5': '1', '6': '1',
                     '9': {'5': str(amount), '13': '0'}}])
    return result


def stats(result):
    row = result.statDict['p']
    return row['battle'] if isinstance(result, (Ashina, Shi)) else row


class LuoyangReflectionTests(unittest.TestCase):
    def test_five_encounters_classify_each_returned_component_once(self):
        for cls, templates, categories in CASES:
            with self.subTest(boss=cls.__name__):
                result = make(cls, templates)
                expected = {}
                for index, (npc, keys) in enumerate(categories.items()):
                    record = reflected(2000 + index * 100, npc, 100 + index)
                    # Use encounter hit IDs so a fake outgoing Skill would
                    # alter the existing axis/hit paths and fail this check.
                    record.id = {Tuli: '45494', Tian: '45972', Yiman: '45899',
                                 Ashina: '45954', Shi: '45527'}[cls]
                    record.full_id = '"1,%s,1"' % record.id
                    before = deepcopy(record.__dict__)
                    result.analyseSecondStage(record)
                    self.assertEqual(record.__dict__, before)
                    for key in keys:
                        expected[key] = expected.get(key, 0) + 100 + index
                for key, amount in expected.items():
                    self.assertEqual(stats(result)[key], amount)
                self.assertEqual(result.win, 0)
                self.assertIsNone(getattr(result, 'lastMainDamage', None))
                self.assertEqual(result.bh.log['environment'], [])
                self.assertEqual(result.detail.get('mechanicHits', []), [])
                self.assertEqual(result.detail.get('mechanicEvents', []), [])
                self.assertEqual(set(result.bh.mainTargets),
                                 {'boss', 'fire'} if cls is Yiman else {'boss'})

    def test_reflection_tail_is_reversible_and_finalization_is_idempotent(self):
        for cls, templates, categories in CASES:
            with self.subTest(boss=cls.__name__):
                result = make(cls, templates)
                main_key = categories['boss'][0]
                result.analyseSecondStage(reflected(2000, amount=100))
                result.analyseSecondStage(reflected(6000, amount=900))
                result.trimmedFinalTime = 5000
                finish(result)
                self.assertEqual(stats(result)[main_key], 100)
                result.getResult()
                self.assertEqual(stats(result)[main_key], 100)
                self.assertEqual(result.win, 0)

    def test_normal_damage_and_returned_component_do_not_count_each_other(self):
        for cls, templates, categories in CASES:
            with self.subTest(boss=cls.__name__):
                result = make(cls, templates)
                outgoing = reflected(2000)
                outgoing.caster, outgoing.target = 'p', 'boss'
                outgoing.resultType, outgoing.reflectionDamage = 0, 0
                outgoing.damage = outgoing.damageEff = 200
                outgoing.fullResult = {'0': '200', '13': '200'}
                result.analyseSecondStage(outgoing)
                result.analyseSecondStage(reflected(3000, amount=50))
                self.assertEqual(stats(result)[categories['boss'][0]], 250)
                self.assertEqual(getattr(result, 'lastMainDamage', 2000), 2000)

    def test_unproven_reaction_shapes_do_not_add_table_damage_or_fake_victory(self):
        changes = ({'resultType': 0}, {'reflectionDamage': 0}, {'damage': 1},
                   {'damageEff': 1}, {'caster': 'p', 'target': 'boss'},
                   {'caster': 'unknown'}, {'target': 'unknown'},
                   {'fullResult': {'5': '100', '13': '1'}},
                   {'fullResult': {'13': '0'}},
                   {'fullResult': {'5': '101', '13': '0'}},
                   {'time': 999}, {'time': 1000000})
        for cls, templates, categories in CASES:
            for fields in changes:
                with self.subTest(boss=cls.__name__, fields=fields):
                    result = make(cls, templates)
                    record = reflected()
                    record.__dict__.update(fields)
                    result.analyseSecondStage(record)
                    self.assertEqual(stats(result).get(categories['boss'][0], 0), 0)
                    self.assertIsNone(getattr(result, 'lastMainDamage', None))
                    self.assertEqual(result.win, 0)


if __name__ == '__main__':
    unittest.main()

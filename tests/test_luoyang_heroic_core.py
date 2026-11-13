"""Heroic completion corroboration and raw NPC defense provenance."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

from equip.CangshengAttributeData import get_target_profiles, heroic_npc_data, npc_data
from replayer.boss.luoyangzhizhan.WinEvidence import LuoyangWinEvidence
from tools.ValidateLuoyangNpcDefense import verify
from tools.Names import getJclEncounter
from FileLookUp import FileLookUp
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def event(kind, time, **kwargs):
    return NS(dataType=kind, time=time, **kwargs)


def evidence(boss="突利和顺", template="139360", difficulty="25人英雄"):
    r = NS(bld=NS(info=NS(map=difficulty+"洛阳之战", npc={
        "boss": NS(templateID=template), "clone": NS(templateID="0")}), systemMessages=[]),
        statDict={"p": {}}, startTime=1000, finalTime=40000, trimmedFinalTime=None)
    return LuoyangWinEvidence(r, boss, (template,))


def damage(time=19000):
    return event("Skill", time, caster="p", target="boss", damageEff=100)


def completion(boss="突利和顺", time=19500, difficulty="25人英雄"):
    return event("System", time, channel="MSG_SYS", content=
                 "[全胜！%s洛阳之战]：1/5，击败%s！%s(完成)\\n" % (difficulty, boss, difficulty))


def resolve(e, events):
    for row in sorted(events, key=lambda row: row.time):
        e.observe(row)
    return e.resolve()


class HeroicCompletionTests(unittest.TestCase):
    def test_tuli_delayed_scene_exit_ends_at_exact_completion(self):
        row = resolve(evidence(), [damage(), completion(), event("Scene", 25406, id="boss", enter=0)])
        self.assertEqual((row["time"], row["departureTime"]), (19500, 25406))
        self.assertEqual(row["rule"], "boss_completion_and_scene_exit")

    def test_tuli_scene_exit_needs_same_boss_recent_damage_and_completion(self):
        valid = [damage(), completion(), event("Scene", 25406, id="boss", enter=0)]
        variants = [valid[1:], valid[:1]+valid[2:], valid[:2],
                    [damage(10000)]+valid[1:],
                    valid[:2]+[event("Scene", 30000, id="boss", enter=0)],
                    valid[:2]+[event("Scene", 25406, id="clone", enter=0)],
                    [damage(), completion(difficulty="25人普通"), valid[-1]]]
        for rows in variants:
            with self.subTest(rows=rows):
                self.assertIsNone(resolve(evidence(), rows))
        for resumed in (damage(26000), event("Scene", 26000, id="boss", enter=1),
                        event("Battle", 26000, id="boss", fight=1)):
            self.assertIsNone(resolve(evidence(), valid+[resumed]))
        e = evidence(); e.replayer.trimmedFinalTime = 18000
        self.assertIsNone(resolve(e, valid))

    def test_heroic_pressure_requires_exact_completion(self):
        boss = "阿史那承庆"
        pressure = event("Buff", 19500, id="35875", caster="boss", target="p", stack=1,
                         isValid=True, delete="false", frame=1000, end=2087)
        valid = [damage(), pressure, completion(boss, 19923)]
        row = resolve(evidence(boss, "139378"), valid)
        self.assertEqual(row["time"], 19500)
        self.assertEqual(row["remainingFrames"], 1087)
        for rows in (valid[:2], valid[1:], [damage(), pressure, completion(boss, 25000)],
                     [damage(), pressure, completion(boss, difficulty="25人普通")],
                     valid+[damage(21000)], valid+[event("Battle", 21000, id="boss", fight=1)]):
            self.assertIsNone(resolve(evidence(boss, "139378"), rows))
        for field, value in (("end", 1960), ("isValid", False), ("delete", "true"),
                             ("caster", "clone"), ("stack", 0)):
            invalid = NS(**vars(pressure)); setattr(invalid, field, value)
            self.assertIsNone(resolve(evidence(boss, "139378"), [damage(), invalid, valid[-1]]))

    def test_heroic_battle_exit_preserves_difficulty_boundary(self):
        boss = "史朝义"
        for difficulty, expected in (("25人英雄", 20000), ("25人普通", None)):
            row = resolve(evidence(boss, "139365"), [damage(), completion(boss, difficulty=difficulty),
                           event("Battle", 20000, id="boss", fight=0)])
            self.assertEqual(row["time"] if row else None, expected)


class HeroicDefenseTests(unittest.TestCase):
    def test_original_table_and_all_profiles_are_reproducible(self):
        source = ROOT / 'docs/160/evidence/heroic10082/sNpcTemplate.tab'
        data = heroic_npc_data()
        self.assertEqual(verify(data, source)['allProfiles'], 107)
        self.assertEqual(data['source']['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        runtime = ROOT / 'equip/resources/cangshengtf/luoyang_heroic_npc_defense.json'
        manifest = json.loads((runtime.parent/'source_manifest.json').read_text(encoding='utf-8'))
        row = next(row for row in manifest['files'] if row['name'] == runtime.name)
        self.assertEqual(row['sha256'], hashlib.sha256(runtime.read_bytes()).hexdigest())

    def test_heroic_normal_and_unknown_target_profiles_are_isolated(self):
        npcs = {k: NS(templateID=k) for k in ('139360', '139306', '140386', '141799', '139716', '139918', 'unknown')}
        heroic = get_target_profiles(NS(map='25人英雄洛阳之战', npc=npcs))
        normal = get_target_profiles(NS(map='25人普通洛阳之战', npc=npcs))
        self.assertEqual(set(heroic), {'139360', '140386', '141799', '139716', '139918'})
        self.assertEqual(normal, {'139306': npc_data()['profiles']['139306']})
        self.assertEqual(heroic['139360']['level'], 54)
        self.assertEqual(heroic['139360']['shieldBase']['Physics'], 6592)
        self.assertEqual(get_target_profiles(NS(map='10人普通洛阳之战', npc=npcs)), {})


class HeroicSelectionTests(unittest.TestCase):
    def test_anonymous_fifth_boss_attempt_stays_in_heroic_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            bosses = ('突利和顺(139360)', '田承嗣(139382)', '伊曼·寂夜(139373)',
                      '阿史那承庆(139378)', '煞将(139363)', '李复(139388)', '(139381)', '史朝义(139365)')
            names = ['2026-11-13-20-%02d-00-25人英雄洛阳之战(836)-%s.jcl' % (i, boss)
                     for i, boss in enumerate(bosses)]
            for name in names:
                (Path(directory)/name).touch()
            lookup = FileLookUp(); lookup.basepath = directory; lookup.dataType = 'jcl'
            latest, all_attempts, _ = lookup.getLocalFile()
            self.assertEqual([row[0] for row in all_attempts], names)
            self.assertEqual(len(latest), 5)
            self.assertEqual(getJclEncounter(names[-2])[1], '史朝义')


if __name__ == '__main__':
    unittest.main()

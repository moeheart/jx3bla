"""Map, file grouping and dispatch contracts for the Cangsheng beta."""
import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from FileLookUp import FileLookUp
from tools.Functions import parseEdition
from tools.Names import getAllMapInfoFromID, getGameEditionFromTime, getIDFromMap, getJclEncounter, getNickToBoss, getBossesForMap


def filename(boss, index=0, map_name="25人普通洛阳之战(835)"):
    return "2026-09-15-20-%02d-00-%s-%s.jcl" % (index, map_name, boss)


class EncounterTests(unittest.TestCase):
    def test_generic_dps_skips_events_but_a_first_stage_hook_keeps_combat_bounds(self):
        from replayer.occ.Dps import DpsReplayer

        class Specialization(DpsReplayer):
            def eventInFirstState(self, event):
                self.observed.append(event.time)

        for cls, instance_hook in ((DpsReplayer, False), (Specialization, False), (DpsReplayer, True)):
            replay = cls.__new__(cls)
            replay.window = Mock()
            replay.occPrint, replay.occColor = '测试', '#000'
            replay.initFirstState, replay.completeFirstState = Mock(), Mock()
            replay.startTime, replay.finalTime, replay.interrupt = 100, 200, 0
            replay.observed = []
            if instance_hook:
                replay.eventInFirstState = lambda event: replay.observed.append(event.time)
            has_hook = cls is Specialization or instance_hook
            events = [SimpleNamespace(time=time) for time in (90, 100, 200, 210)]
            replay.bld = SimpleNamespace(log=events if has_hook else None)
            replay.FirstStageAnalysis()
            replay.initFirstState.assert_called_once_with()
            replay.completeFirstState.assert_called_once_with()
            self.assertEqual(replay.observed, [100, 200] if has_hook else [])

    def test_hit_target_aliases_are_only_consulted_until_the_boss_is_known(self):
        from data.BattleLogData import BattleLogData
        from replayer.ActorReplayPro import ActorProReplayer
        from tools.ValidateLuoyang import make_config, ValidationWindow

        for map_name, recorded, expected, lookups in (
                ('25人普通洛阳之战', '史朝义', '史朝义', 0),
                ('25人普通阆风悬城', '未知', '张景超', 2)):
            with self.subTest(recorded=recorded):
                bld = BattleLogData()
                bld.info.map, bld.info.boss, bld.info.server = map_name, recorded, '测试'
                bld.info.battleTime, bld.info.sumTime = 1794576000, 3000
                for time, name in enumerate(('无关目标', '張法雷', '李倓'), start=1):
                    target = str(time)
                    bld.info.addNPC(target, name)
                    bld.log.append(SimpleNamespace(dataType='Skill', time=time * 1000,
                                                   target=target, caster='player'))
                actor = ActorProReplayer(make_config(), ['log', 0, 1], '',
                                         {'log': bld}, ValidationWindow())
                with patch.object(bld.info, 'getName', wraps=bld.info.getName) as get_name:
                    actor.FirstStageAnalysis()
                self.assertEqual(actor.bossAnalyseName, expected)
                self.assertEqual(get_name.call_count, lookups)

    def test_server_boss_listing_includes_same_name_in_both_raids(self):
        # Exercise the real endpoint body without starting the server or a DB.
        tree = ast.parse(Path("server.py").read_text(encoding="utf-8"))
        endpoint = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "getBossesFromMapfunc")
        endpoint.decorator_list = []
        namespace = {"getIDFromMap": getIDFromMap, "getBossesForMap": getBossesForMap, "jsonify": lambda data: data}
        exec(compile(ast.Module(body=[endpoint], type_ignores=[]), "server.py", "exec"), namespace)
        for map_name in ("828", "835", "836", "10人普通洛阳之战", "25人普通洛阳之战", "25人英雄洛阳之战", "25人普通阆风悬城"):
            namespace["request"] = SimpleNamespace(args={"map": map_name})
            result = namespace[endpoint.name]()
            self.assertEqual(result["available"], 1)
            self.assertEqual(result["result"]["阿史那承庆"], 4)
            if "洛阳" in map_name or map_name in ("828", "835", "836"):
                self.assertEqual(len(result["result"]), 5)
        for map_name in ("829", "不存在的地图", None):
            namespace["request"] = SimpleNamespace(args={"map": map_name})
            self.assertEqual(namespace[endpoint.name]()["available"], 0)

    def test_nonconsecutive_map_ids(self):
        for map_id, name in (("828", "10人普通洛阳之战"), ("835", "25人普通洛阳之战"), ("836", "25人英雄洛阳之战")):
            self.assertEqual(getAllMapInfoFromID(map_id)["name"], name)
            self.assertEqual(getIDFromMap(name), map_id)
            self.assertEqual(getGameEditionFromTime(map_id, 1789470000), "160")
        self.assertEqual(getAllMapInfoFromID("829")["name"], "未知地图")
        self.assertEqual(getIDFromMap("25人普通阆风悬城"), "794")

    def test_aliases_are_scoped_to_map(self):
        for boss in ("史朝义(139312)", "煞将(139308)", "李复(139332)", "(139324)"):
            self.assertEqual(getJclEncounter(filename(boss))[1], "史朝义")
        self.assertEqual(getNickToBoss("李复", "其它地图"), "李复")
        self.assertEqual(getJclEncounter(filename("伊曼·寂夜(139319)"))[1], "伊曼双子")
        self.assertEqual(getJclEncounter(filename("阿史那承庆(137017)", map_name="25人普通阆风悬城(794)"))[1], "阿史那承庆")

    def test_latest_five_and_all_attempts_survive_aliases(self):
        bosses = ("突利和顺(139306)", "田承嗣(139329)", "伊曼·寂夜(139319)", "阿史那承庆(139323)", "煞将(139308)", "李复(139332)", "(139324)", "史朝义(139312)")
        lookup = FileLookUp()
        lookup.dataType = "jcl"
        lookup.specifyFiles([filename(boss, i) for i, boss in reversed(list(enumerate(bosses)))])
        latest, attempts, map_name = lookup.getLocalFile()
        self.assertEqual(map_name, "洛阳之战")
        self.assertEqual(len(latest), 5)
        self.assertEqual(len(attempts), 8)
        self.assertEqual([row[1] for row in attempts[4:]], [0, 1, 2, 3])
        self.assertEqual([row[2] for row in attempts[4:]], [0, 0, 0, 1])

    def test_beta_version_uses_offline_path(self):
        self.assertEqual(parseEdition("8.16.0-beta.1"), 0)
        self.assertEqual(parseEdition("8.15.5"), 8015005)


if __name__ == "__main__":
    unittest.main()

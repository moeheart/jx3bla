"""Phase intervals must survive repeated cycles and encounter cutoff."""
import unittest
from types import SimpleNamespace as NS
from replayer.BattleHistory import BattleHistory
from replayer.boss.luoyangzhizhan.LuoyangEvidence import finalize_phase_periods, record_shout


class PhasePeriodTests(unittest.TestCase):
    def test_repeated_phases_and_post_end_events(self):
        bh = BattleHistory(1000, 21000)
        for time in (4000, 8000, 12000, 19000):
            bh.setEnvironment("0", "阶段", "340", time, 0, 1, "", "phase")
        replay = NS(startTime=1000, finalTime=16000, bh=bh, phaseTime=[0, 0, 0], detail={
            "phaseTransitions": [{"time": 1000, "phase": 1}, {"time": 4000, "phase": 2},
                                 {"time": 8000, "phase": 1}, {"time": 12000, "phase": 2},
                                 {"time": 19000, "phase": 1}]})
        finalize_phase_periods(replay, {1: "常规", 2: "机制"})
        self.assertEqual([x["duration"] for x in replay.detail["phasePeriods"]], [3, 4, 4, 4])
        self.assertEqual(sum(x["duration"] for x in replay.detail["phasePeriods"]), 15)
        self.assertEqual(replay.phaseTime, [0, 7000, 8000])
        self.assertEqual([x["duration"] for x in bh.log["environment"]], [4000, 4000, 4000])
        self.assertTrue(all(x["time"] <= 16000 for x in replay.detail["phaseTransitions"]))

    def test_shout_refresh_is_coalesced_without_losing_repeat_cycle(self):
        replay = NS(detail={}, bh=BattleHistory(1000, 21000),
                    bld=NS(info=NS(npc={"boss": NS(templateID="139306")})))
        for time in (2000, 2200, 9000):
            record_shout(replay, NS(id="boss", time=time, content='"转阶段"'), "死水微澜")
        self.assertEqual(len(replay.detail["shouts"]), 2)
        self.assertEqual(replay.detail["shouts"][0]["sourceTemplate"], "139306")
        self.assertEqual([x["start"] for x in replay.bh.log["environment"]], [2000, 9000])


if __name__ == "__main__":
    unittest.main()

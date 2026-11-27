import unittest
from types import SimpleNamespace

from replayer.occ.LingSu import BaiZhiTiming, LingSuReplayer


def buff(time, skill, stack, frame, end, target="healer"):
    return SimpleNamespace(dataType="Buff", time=time, id=skill, stack=stack,
                           frame=frame, end=end, level=1, target=target)


def cast(time):
    return SimpleNamespace(dataType="Cast", id="27621", time=time, caster="healer")


class BaiZhiTimingTest(unittest.TestCase):
    def test_proc_removal_can_precede_or_follow_the_heal(self):
        for offset in (-90, 90):
            with self.subTest(offset=offset):
                timing = BaiZhiTiming()
                timing.observe(buff(1000, "31763", 1, 16, 176), "healer")
                timing.observe(buff(2500 + offset, "31763", 0, 40, 176), "healer")
                self.assertEqual(timing.resolve(2500, 1300), (2500, "月见瞬发"))
                self.assertEqual(timing.resolve(5250, 1300), (3950, ""))

    def test_missing_removal_grants_only_one_instant_and_expiry_is_not_a_proc(self):
        timing = BaiZhiTiming()
        timing.observe(buff(1000, "31763", 1, 16, 176), "healer")
        timing.observe(buff(7000, "31763", 1, 112, 272), "healer")
        timing.observe(buff(17100, "31763", 0, 274, 272), "healer")
        timing.observe(buff(18000, "31763", 1, 288, 448, target="other"), "healer")
        self.assertEqual(timing.resolve(2500, 1300), (2500, "月见瞬发"))
        self.assertEqual(timing.resolve(4500, 1300), (3200, ""))
        self.assertEqual(timing.resolve(17120, 1300), (15820, ""))
        self.assertEqual(timing.resolve(19000, 1300), (17700, ""))

    def test_queued_start_and_airborne_recipe(self):
        timing = BaiZhiTiming()
        timing.observe(buff(1000, "20072", 1, 16, 128), "healer")
        timing.observe(buff(8200, "20072", 0, 131, 128), "healer")
        timing.observe(cast(1100), "healer")
        timing.observe(cast(2300), "healer")
        self.assertEqual(timing.resolve(2320, 1300), (1100, ""))
        self.assertEqual(timing.resolve(3570, 1300), (2300, ""))
        self.assertEqual(timing.resolve(4900, 1300), (4900, "凌然天风瞬发"))
        self.assertEqual(timing.resolve(8100, 1300), (8100, "凌然天风瞬发"))
        self.assertEqual(timing.resolve(9500, 1300), (8200, ""))
        legacy = BaiZhiTiming()
        legacy.observe(buff(1000, "20072", 1, 16, 128), "healer")
        self.assertEqual(legacy.resolve(3000, 1300), (1700, ""))

    def test_native_qingchuan_and_kumu_do_not_cut_the_preceding_baizhi(self):
        bai = dict(skillid="27622", start=7990996, duration=1273)
        qing = dict(skillid="27669", start=7991937.5, duration=1312.5)
        history = [bai, qing]
        replay = LingSuReplayer.__new__(LingSuReplayer)
        replay.nativeStarts = {"27669": [7992442], "27675": [8005186, 8010551]}
        replay.kumuEnds = [8014964]
        replay.observedStarts = {id(bai)}
        replay.observedEnds = {id(bai): 7992269}
        replay.ss = SimpleNamespace(timeEnd=0)
        replay.bh = SimpleNamespace(log={"normal": history})
        replay.haste = 0
        replay.startTime, replay.finalTime = 7900000, 8100000
        replay.gcdSkillIndex = {"27669": 0, "27675": 1}
        replay.skillInfo = [[SimpleNamespace(log=[[0, 0, 0]])] for _ in range(2)]
        replay.anchorAdjacentCast(SimpleNamespace(id="27669", time=7993250))
        replay.alignBaiZhi(history, replay.observedStarts, replay.observedEnds)
        self.assertEqual((bai["start"], bai["duration"], qing["start"]), (7990996, 1273, 7992442))
        for start, duration in ((8005186, 0), (8010551, 4413)):
            kumu = dict(skillid="27675", start=start - 4400, duration=4400)
            history.append(kumu)
            replay.anchorAdjacentCast(SimpleNamespace(id="27675", time=start))
            self.assertEqual((kumu["start"], kumu["duration"]), (start, duration))

        inferred = dict(skillid="27669", start=7991937.5, duration=1312.5)
        replay.alignBaiZhi([bai, inferred], replay.observedStarts, replay.observedEnds)
        self.assertEqual(bai["start"] + bai["duration"], 7992269)
        self.assertEqual(inferred["start"], 7992269)
        self.assertEqual(inferred["start"] + inferred["duration"], 7993250)


if __name__ == "__main__":
    unittest.main()

"""Invalid phases and player control must be excluded exactly once."""
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

from replayer.BattleHistory import BattleHistory
from replayer.CombatTracker import CombatTracker, DpsCastRecorder, HealCastRecorder
from replayer.occ.Dps import DpsReplayer
from replayer.occ.HuaJianYou import HuaJianYouReplayer
from replayer.occ.Healer import HealerReplay
from tools.Functions import BuffCounter


class EffectiveTimeTests(unittest.TestCase):
    def test_record_with_no_effective_dps_time_has_finite_skill_rates(self):
        replay=DpsReplayer.__new__(DpsReplayer)
        replay.result={'overall':{'sumTimeEff':0},'skill':{}}
        skill=NS(getNum=lambda:1,getAverageDelay=lambda:0,getDamageEff=lambda:100)
        replay.skillInfo=[[skill]]
        replay.gcdSkillIndex={'skill':0}
        replay.calculateSkillInfoDirect('direct',skill)
        replay.calculateSkillInfo('indexed','skill')
        for row in replay.result['skill'].values():
            self.assertEqual((row['numPerSec'],row['ndps']),(0,0))

    def test_real_recorders_preserve_amounts_without_rates_when_fully_controlled(self):
        for amount in (0,1000):
            for cls,kind in ((DpsCastRecorder,'Dps'),(HealCastRecorder,'Hps')):
                with self.subTest(amount=amount,kind=kind):
                    tracker=self.tracker(0,10000)
                    tracker.info.getSkillName=lambda _: '测试技能'
                    record=cls(1)
                    record.record('target','1,1,1',amount)
                    output={'player':{},'sum':0}
                    getattr(tracker,'getStatIn'+kind)({'player':record},output)
                    self.assertEqual(record.sum,amount)
                    self.assertEqual(getattr(record,kind.lower()),0)
                    self.assertEqual(output['sum'],0)

    def tracker(self, stun_start, stun_end):
        bh=BattleHistory(0,10000)
        bh.setBadPeriod(2000,6000,True,True)
        bh.calBadPeriod()
        stun=BuffCounter('test',0,10000)
        stun.setState(stun_start,1)
        stun.setState(stun_end,0)
        tracker=CombatTracker.__new__(CombatTracker)
        tracker.startTime,tracker.finalTime,tracker.time=0,10000,10000
        tracker.timeDps,tracker.timeHealer=bh.sumTime('dps'),bh.sumTime('healer')
        tracker.badPeriodDpsLog,tracker.badPeriodHealerLog=bh.badPeriodDpsLog,bh.badPeriodHealerLog
        tracker.stunTime={'player':stun}
        tracker.info=NS(getOcc=lambda _: '2d',getName=lambda _: '匿名')
        tracker.occDetailList={}
        return tracker

    def test_control_overlap_does_not_double_subtract_invalid_time(self):
        for start,end,expected in ((4000,8000,4000),(3000,5000,6000),(6000,8000,4000)):
            for kind in ('Dps','Hps'):
                with self.subTest(control=(start,end),kind=kind):
                    tracker=self.tracker(start,end)
                    record=NS(export=Mock(),dps=1,hps=1,sum=1000,skill={},namedSkill={},
                              namedTarget={},namedSource={})
                    output={'player':{},'sum':0}
                    getattr(tracker,'getStatIn'+kind)({'player':record},output)
                    self.assertEqual(record.export.call_args.args[0],expected)
                    self.assertEqual(output['player']['player']['adjustedTime'],expected)

    def test_personal_effective_time_uses_the_specializations_own_clock(self):
        bh=BattleHistory(1000,11000)
        bh.setBadPeriod(3000,7000,True,False)
        bh.calBadPeriod()
        for cls,expected in ((DpsReplayer,6000),(HuaJianYouReplayer,6000),(HealerReplay,10000)):
            with self.subTest(occupation=cls.__name__):
                replay=cls.__new__(cls)
                replay.result={}
                replay.occPrint='验证'
                replay.bld=NS(info=NS(server='测试',battleTime=1794576000,
                    map='25人英雄洛阳之战',boss='史朝义',sumTime=10000),dataType='jcl')
                replay.bossBh=bh
                replay.config=NS(item={'general':{'mask':1},'xiangzhi':{'caltank':0}})
                replay.win=1
                replay.getOverallInfo()
                self.assertEqual(replay.result['overall']['sumTimeEff'],expected)
                self.assertEqual(replay.result['overall']['sumTimeDpsEff'],6000)


if __name__=='__main__':
    unittest.main()

"""Qt rendering, filtering, sharing formats and legacy profession representations."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from data.PersonalTimeline import ACTION_ICONS, Observation, build_personal_timelines
from window.QtTimeline import (CALLS, MECHANICS, NORMAL, PHASES, SPECIAL, TimelineView,
                              bands, export_text, timeline_data)


def env(name, start, icon="340", duration=0, **extra):
    return dict(skillname=name, start=start, duration=duration, iconid=icon, **extra)


def sample(mask=0):
    start = 800000
    environment = [env("开场", start, type="phase"),
                   env("尚未标注", start+1000, icon="341"),
                   env("机制", start+2000, duration=7000), env("重合机制", start+2000)]
    replay = dict(startTime=start, finalTime=start+90000, environment=environment,
                  normal=[env("读条", start+i*1500, duration=1250, targetName="测试玩家")
                          for i in range(4)], special=[env("特殊", start+7000)],
                  call=[env("点名", start+3600, description="测试玩家中了点名")],
                  yaoxing=[[start, -3], [start+3000, 2]])
    result = dict(overall={"mask": mask, "sumTime": 90000}, replay=replay)
    return NS(startTime=start, finalTime=start+90000, mask=mask,
              playerNames={"1234": "测试玩家"}, statDict=[{"name":"测试玩家"}],
              detail={"phaseTransitions":[{"time":start, "name":"开场"},
                                          {"time":start+60000, "name":"终阶段"}]},
              bh=NS(startTime=start, finalTime=start+90000,
                    log={"environment":environment, "call":{"1234":[env("点名",start+3000)]}},
                    badPeriodDpsLog=[[start+30000,1],[start+32000,0]]),
              occResult={"测试玩家":{"occ":"212h", "result":result}})


class TimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def show(self, actor, player=None):
        view=TimelineView.from_actor(actor,player)
        self.addCleanup(view.close)
        view.resize(720,360)
        view.show()
        self.app.processEvents()
        return view

    def test_team_filter_offset_copy_and_simultaneous_clickable_hits(self):
        actor=sample()
        view=self.show(actor)
        self.assertEqual(view.scope.currentText(), "全部记录")
        view.scope.setCurrentIndex(0)
        self.app.processEvents()
        marked=view.canvas.marks
        self.assertIn("终阶段", [m.name for m in marked if m.track == PHASES])
        self.assertNotIn("尚未标注", [m.name for m in marked])
        self.assertEqual(len([m for m in marked if m.track==CALLS]),1)
        overlapping = [g for g in view.canvas.rows[0].groups if g.name in ("机制", "重合机制")]
        self.assertEqual(len({g.axis_y for g in overlapping}), 2)
        rect,mark=next((r,m) for r,m in view.canvas.hits if m.name=="机制")
        QTest.mouseClick(view.canvas.viewport(), Qt.LeftButton, pos=rect.center())
        self.assertIn("0:02.0 – 0:09.0",view.detail.text())
        view.scope.setCurrentIndex(1)
        self.assertIn("尚未标注", [m.name for m in view.canvas.marks])
        view.offset.setValue(1)
        with patch('window.QtTimeline.QApplication.clipboard') as clipboard:
            view.copy_axis(False)
            clipboard.return_value.setText.assert_called_with("1.0,机制;\n1.0,重合机制;\n")
            view.copy_axis(True)
            clipboard.return_value.setText.assert_called_with("1.0,机制;\n1.0,重合机制;\n")
            view.offset.setValue(-2)
            view.copy_axis(False)
            self.assertTrue(clipboard.return_value.setText.call_args.args[0].startswith("2.0,开场;"))
        self.assertEqual(export_text([(5000,"甲",True),(6500,"乙",True),(8000,"丙",True)],2,True),
                         "3.0,甲;6.0,丙;\n4.5,乙;\n")

    def test_personal_focus_details_full_record_and_anonymous_export(self):
        actor=sample(1)
        before=deepcopy(actor.occResult)
        view=self.show(actor,"测试玩家")
        casts = [g for row in view.canvas.rows for g in row.groups if g.track == NORMAL]
        self.assertEqual(len(casts),1)
        self.assertEqual(casts[0].label, "读条 ×4")
        self.assertEqual(len(casts[0].records), 4)
        self.assertTrue(any(m.track==SPECIAL for m in view.canvas.marks))
        view.scope.setCurrentIndex(1)
        self.assertEqual(len([m for m in view.canvas.marks if m.track==NORMAL]),4)
        self.assertTrue(all("测试玩家" not in view.canvas.describe(m) for m in view.canvas.marks))
        self.assertTrue(any(m.track=="药性" and m.name=="-3" for m in view.canvas.marks))
        self.assertEqual(actor.occResult,before)
        team=timeline_data(actor,None)[1]
        self.assertTrue(all("测试玩家" not in m.detail for m in team))
        actor.mask=0
        team=timeline_data(actor,None)[1]
        self.assertTrue(any("测试玩家" in m.detail for m in team if m.track==CALLS))

    def test_reflow_reaches_last_event_without_horizontal_scroll_at_all_widths(self):
        actor=sample()
        actor.bh.log["environment"].append(env("末段", actor.finalTime-1000))
        view=self.show(actor)
        for width in (360, 720, 1220):
            view.resize(width, 250)
            for zoom in range(view.zoom.count()):
                view.zoom.setCurrentIndex(zoom)
                self.app.processEvents()
                self.assertEqual(view.canvas.horizontalScrollBar().maximum(), 0)
                for row in view.canvas.rows:
                    for g in row.groups:
                        self.assertGreaterEqual(g.rect.left(), 0)
                        self.assertLess(g.rect.right(), view.canvas.viewport().width())
                    for i,g in enumerate(row.groups):
                        self.assertFalse(any(g.rect.intersects(h.rect) for h in row.groups[i+1:]))
                bar = view.canvas.verticalScrollBar()
                last = next(g for row in view.canvas.rows for g in row.groups if g.name == "末段")
                bar.setValue(last.axis_y - view.canvas.viewport().height()//2)
                self.app.processEvents()
                self.assertIn("末段",[m.name for _,m in view.canvas.hits])
        blank=self.show(NS())
        self.assertFalse(blank.canvas.rows)
        self.assertFalse(blank.grab().isNull())
        self.assertFalse(TimelineView.from_actor(actor,player="无记录").canvas.rows)

    def test_all_five_healers_and_damage_heat_are_time_aligned(self):
        cases = [
            ("6h", {"mxym":[[1000,1]],"xwgd":[[1000,1]],"ghzs":[[1000,1]],
                    "zwjt":[[1000,1]]},{"迷仙引梦","仙王蛊鼎","蛊惑众生","醉舞九天"}),
            ("212h", {"yaoxing":[[1000,-5]],"qianzhi":[[1000,1]],"qingchuan":[[1000,1]]},
             {"药性","千枝","青川"}),
            ("2h", {"moyi":[[1000,20]],"heat":{"timeline":[[0,0,80]]*5}},
             {"墨意","小队 5 覆盖"}),
            ("5h", {"hxpy":[[1000,1]], "heat":{"timeline":[[10,10],[60,100]]}},
             {"回雪飘摇","翔舞","上元"}),
            ("22h", {"heatType":"combined","heat":{"timeline":[[20],[40]]}}, {"梅花盾","双持续治疗"}),
            ("22h", {"heatType":"meihua","heat":{"timeline":[20,30]}},{"梅花盾"}),
            ("2d", {"heat":{"shangyang":{"timeline":[10,20],"interval":250}}},{"商阳指"}),
        ]
        for occ, replay, labels in cases:
            with self.subTest(occ=occ):
                tracks=list(bands(replay,1000,5000,occ))
                self.assertTrue(labels.issubset({m.track for m in tracks}))
                self.assertTrue(all(0<=m.start<m.end<=5000 for m in tracks))
        heat=list(bands({"heat":{"timeline":[[20,20,40],[80]]},"heatType":"combined"},1000,2000,"22h"))
        self.assertEqual([(m.start,m.end) for m in heat if m.track=="梅花盾"],[(0,1000),(1000,1500)])

    def test_generic_projection_keeps_casts_and_groups_results_without_guessing_casts(self):
        actor=sample()
        actor.occResult["坦克"]={"occ":"3t", "result":{"overall":{}}}
        actor.occResult["无技能"]={"occ":"1d", "result":{}}
        before=deepcopy(actor.occResult)
        roster={"a":NS(name="坦克"),"b":NS(name="测试玩家"),"c":NS(name="无技能")}
        actor.playerNames.update({key: person.name for key,person in roster.items()})
        def entry(kind, skill, offset=5, caster="a", **extra):
            defaults=dict(caster=caster, dataType=kind, id=skill, level=1, full_id=f'1,{skill},1',
                          target="t1", damage=150, damageEff=100, heal=0, healEff=0, scheme=1,
                          resultType=0, time=actor.startTime+offset)
            return NS(**{**defaults,**extra})
        active=next(iter(ACTION_ICONS))
        another=list(ACTION_ICONS)[1]
        events=[entry("Cast",active),entry("Skill",active),entry("Skill",active,target="t2"),
                entry("Skill",active,target="t1"),entry("Skill",another),
                entry("Skill","999999"),entry("Skill",another,caster="b"),
                entry("Skill",another,scheme=2),entry("Skill",another,resultType=1),
                entry("Skill",another,offset=-1),entry("Skill",another,offset=95000),
                entry("Skill",another,damage=0,damageEff=0),entry("Skill",another,caster="NPC")]
        class Log:
            passes=0
            def __iter__(self):
                self.passes+=1
                return iter(events)
        log=Log()
        actor.bld=NS(info=NS(player=roster,getSkillName=lambda key: key),log=log)
        actor.personalTimelines=build_personal_timelines(actor)
        self.assertEqual(log.passes,1)
        self.assertEqual(set(actor.personalTimelines),{"坦克","无技能"})
        self.assertEqual(actor.personalTimelines["无技能"],[])
        seen=actor.personalTimelines["坦克"]
        self.assertEqual([o.kind for o in seen],["施放","招式命中","招式命中","技能效果"])
        self.assertEqual((seen[1].events,seen[1].targets),(3,2))
        self.assertEqual(actor.occResult,before)
        view=self.show(actor,"坦克")
        self.assertEqual([m.track for m in view.canvas.marks].count("招式命中"),1)
        view.scope.setCurrentIndex(1)
        self.assertEqual([m.track for m in view.canvas.marks].count("招式命中"),2)
        self.assertTrue(any("2 个目标 · 3 条" in m.detail for m in view.canvas.marks))
        self.assertIn("施放",view.hint)
        self.assertEqual(log.passes,1)

    def test_effect_only_focus_retains_observations_without_inventing_any_cast(self):
        actor=sample()
        actor.occResult["只有结算"]={"occ":"24","result":{}}
        actor.personalTimelines={"只有结算":[
            Observation(actor.startTime+i*500,str(i%4),str(i%4),"技能效果",1,1)
            for i in range(11)]}
        view=self.show(actor,"只有结算")
        self.assertIn("仅有可归属的技能效果",view.hint)
        visible=[mark for mark in view.canvas.marks if mark.track=="技能效果"]
        self.assertEqual({m.name for m in visible},{"0","1","2"})
        self.assertFalse(any(mark.track=="施放" for mark in view.marks))
        view.scope.setCurrentIndex(1)
        self.assertEqual(sum(m.track=="技能效果" for m in view.canvas.marks),11)

    def test_json_array_and_named_observations_match_native_and_skip_incomplete_rows(self):
        actor=sample()
        actor.occResult["坦克"]={"occ":"3t","result":{}}
        first=Observation(actor.startTime+200,"101","握针","施放",1,0)
        second=Observation(actor.startTime+300,"101","握针","招式命中",2,2)
        actor.personalTimelines={"坦克":[first,second]}
        expected=timeline_data(actor,"坦克")
        loaded=json.loads(json.dumps(actor,default=vars))
        loaded["personalTimelines"]["坦克"][1]=second._asdict()
        loaded["personalTimelines"]["坦克"].extend([{},["incomplete"],["bad","1",None,"施放",1,0]])
        self.assertEqual(timeline_data(loaded,"坦克"),expected)
        self.assertEqual(timeline_data(loaded,None),timeline_data(actor,None))
        view=self.show(loaded,"坦克")
        view.scope.setCurrentIndex(1)
        self.assertEqual([m.track for m in view.canvas.marks].count("招式命中"),1)

    def test_team_focus_groups_calls_while_full_retains_the_players(self):
        actor=sample()
        actor.bh.log["call"]["other"]=[env("点名",actor.startTime+3015)]
        actor.bh.log["environment"].append(env("点名",actor.startTime+2670))
        view=self.show(actor)
        calls=[g for row in view.canvas.rows for g in row.groups if g.name=="点名"]
        self.assertEqual(len(calls),1)
        self.assertEqual(len(calls[0].records),3)
        self.assertEqual(calls[0].times,(2670,))
        self.assertTrue(any('测试玩家' in m.detail for m in calls[0].records))
        view.scope.setCurrentIndex(1)
        self.assertEqual(sum(m.track==CALLS for m in view.canvas.marks),2)

    def test_team_and_generic_stop_at_actor_end_but_specialists_keep_their_own_boundary(self):
        actor=sample()
        actor.bh.startTime=actor.startTime-500
        actor.bh.finalTime=actor.finalTime+11000
        actor.bh.log["environment"].extend([
            env("跨越开场",actor.startTime-100,duration=600),
            env("最后机制",actor.finalTime-500,duration=3000),
            env("胜利后的喊话",actor.finalTime+200)])
        actor.occResult["坦克"]={"result":{}}
        actor.personalTimelines={"坦克":[Observation(actor.finalTime-5,"35","有效施放","施放",1,0),
                                       Observation(actor.finalTime+1,"35","超时施放","施放",1,0)]}
        for player in (None,"坦克"):
            duration,marks,exported=timeline_data(actor,player)
            self.assertEqual(duration,actor.finalTime-actor.startTime)
            visible={m.name:m for m in marks}
            self.assertEqual((visible["跨越开场"].start,visible["跨越开场"].end),(0,500))
            self.assertEqual(visible["最后机制"].end,duration)
            self.assertNotIn("胜利后的喊话",visible)
            self.assertNotIn("超时施放",visible)
            self.assertTrue(all(0<=m.start<=m.end<=duration for m in marks))
            text=export_text(exported,-10)
            self.assertIn("最后机制",text)
            self.assertNotIn("胜利后的喊话",text)
            self.assertNotIn("跨越开场",text)
        personal=actor.occResult["测试玩家"]["result"]["replay"]
        personal["finalTime"]=actor.finalTime+800
        self.assertEqual(timeline_data(actor,"测试玩家")[0],90800)
        del actor.startTime, actor.finalTime
        self.assertEqual(timeline_data(actor,None)[0],101500)

    def test_many_events_only_paint_visible_slice(self):
        actor=sample()
        actor.finalTime=actor.bh.finalTime=actor.startTime+10000000
        actor.bh.log["environment"]=[env("事件",actor.startTime+i*1000) for i in range(10000)]
        view=self.show(actor)
        self.assertEqual(len(view.exports),10000)
        self.assertLess(len(view.canvas.hits),600)
        bar=view.canvas.verticalScrollBar()
        bar.setValue(bar.maximum())
        self.app.processEvents()
        self.assertLess(len(view.canvas.hits),600)
        self.assertGreater(max(g.times[-1] for _,g in view.canvas.hits),9900000)

    def test_compact_skill_rows_and_full_image_include_every_minute_and_occurrence(self):
        actor = sample()
        replay = actor.occResult['测试玩家']['result']['replay']
        replay['normal'][1]['num'] = 5
        replay['normal'].append(env('读条', actor.startTime+71000))
        view = TimelineView.from_actor(actor, '测试玩家', compact=True)
        self.addCleanup(view.close)
        view.resize(720,180)
        view.show()
        self.app.processEvents()
        self.assertEqual(len(view.canvas.rows),1)
        group = next(g for g in view.canvas.rows[0].groups if g.track==NORMAL)
        self.assertEqual(group.label,'读条 ×5')
        self.assertEqual(group.times[-1],71000)
        self.assertIn('读条 ×5', [m.name for m in group.records])
        self.assertEqual(view.canvas.horizontalScrollBar().maximum(),0)
        view.zoom.setCurrentIndex(2)
        self.app.processEvents()
        self.assertGreater(len(view.canvas.rows),1)
        self.assertGreater(view.canvas.content_height,view.canvas.viewport().height())
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'sheet.png'
            view.canvas.save_png(path)
            image=QImage(str(path))
            self.assertFalse(image.isNull())
            self.assertEqual(image.width(), view.canvas.viewport().width())
            self.assertEqual(image.height(), view.canvas.content_height)


if __name__=="__main__":
    unittest.main()

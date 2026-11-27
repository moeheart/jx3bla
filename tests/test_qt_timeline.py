"""Qt rendering, filtering, sharing formats and legacy profession representations."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from data.PersonalTimeline import ACTION_ICONS, Observation, build_personal_timelines
from window.QtTimeline import (CALLS, MECHANICS, NORMAL, PHASES, SPECIAL, TimelineView,
                              action_icon, bands, cooldown_intervals, export_text, timeline_data)


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
        self.assertEqual(len({g.axis_y for g in overlapping}), 1)
        self.assertFalse(overlapping[0].rect.intersects(overlapping[1].rect))
        self.assertEqual(len({row.bottom-row.top for row in view.canvas.rows}), 1)
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
        casts = next(items for kind, name, items in view.canvas.lanes if name == NORMAL)
        self.assertEqual([g.name for g in casts], ["读条"] * 4)
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

    def test_default_phase_and_autoattacks_do_not_enter_either_boss_axis_or_exports(self):
        actor = sample()
        log = actor.bh.log
        log["environment"].extend([
            env("常规技能", actor.startTime + 1000, type="phase"),
            env("普通攻击·顺劈", actor.startTime + 1500, type="skill"),
            env("普攻", actor.startTime + 2500, type="cast"),
            env("反击姿态", actor.startTime + 3500, type="cast")])
        log["normal"] = [env("普通循环", actor.startTime)]
        actor.detail["phaseTransitions"].append({"time":actor.startTime + 20000, "name":"常规技能"})
        for player in (None, "测试玩家"):
            _, marks, exports = timeline_data(actor, player)
            for names in ({m.name for m in marks}, {name for _, name, _ in exports}):
                self.assertIn("反击姿态", names)
                self.assertTrue(names.isdisjoint({"常规技能", "普通攻击·顺劈", "普攻", "普通循环"}))

    def test_healing_indicators_follow_actions_and_only_healing_resources_get_cooldown_rows(self):
        actor = sample()
        actor.timestamp = 1795673277
        entry = actor.occResult["测试玩家"]
        entry["occ"] = "5h"
        replay = entry["result"]["replay"]
        replay.pop("yaoxing")
        replay.update(hxpy=[[actor.startTime, 1]], heat={"timeline":[[65], [80]]},
                      special=[env("繁音急节", actor.startTime)], normal=[
                          env("扶摇直上", actor.startTime), env("蹑云逐月", actor.startTime+3000),
                          env("蝶弄足", actor.startTime+6000), env("王母挥袂", actor.startTime+9000)])
        view = self.show(actor, "测试玩家")
        lanes = [(kind, label) for kind, label, _ in view.canvas.lanes]
        self.assertEqual(lanes[:4], [('event', CALLS), ('event', MECHANICS), ('event', NORMAL), ('event', SPECIAL)])
        self.assertEqual(lanes[4:7], [('band', '上元'), ('band', '翔舞'), ('band', '回雪飘摇')])
        self.assertEqual({name for kind, name in lanes if kind == 'cd'}, {'王母挥袂', '繁音急节'})
        self.assertTrue({'扶摇直上', '蹑云逐月', '蝶弄足'} <= {m.name for m in view.canvas.marks})

    def test_jiguang_and_zuiwu_channel_casts_keep_one_icon_per_use_in_the_correct_lane(self):
        for occ, name, skill, talents, explicit, expected in (
                ('5h', '回雪飄搖', '40236', {}, True, NORMAL),
                ('5h', '回雪飘摇', '565', {'1':'吉光'}, None, NORMAL),
                ('5h', '回雪飘摇', '40237', {}, False, '引导起手'),
                ('6h', '醉舞九天', '6675', {}, None, '引导起手')):
            with self.subTest(occ=occ, talents=talents, explicit=explicit):
                actor = sample()
                actor.timestamp = 1795673277
                entry = actor.occResult["测试玩家"]
                entry["occ"] = occ
                entry["result"]["qixue"] = talents
                replay = entry["result"]["replay"]
                if explicit is not None:
                    replay["hxpyTriggersGcd"] = explicit
                replay["normal"] = [env(name, actor.startTime + 1400, skillid=skill)]
                replay["special"] = [env(name, actor.startTime + 1440, skillid=skill),
                                     env(name, actor.startTime + 3200, skillid=skill),
                                     env(name, actor.startTime + 3280, skillid=skill)]
                starts = [(m.start, m.lane) for m in timeline_data(actor, "测试玩家")[1] if m.name == name]
                self.assertEqual(starts, [(1400, expected), (3200, expected), (3280, expected)])

    def test_new_channel_band_has_one_interval_per_cast_including_immediate_interrupts(self):
        actor = sample()
        entry = actor.occResult["测试玩家"]
        entry["occ"] = '6h'
        start = actor.startTime
        entry["result"]["replay"].update(
            special=[env("醉舞九天", start + 100), env("醉舞九天", start + 800)],
            zwjt=[[start + 100, 1], [start + 900, 0]],
            zwjtCasts=[dict(start=start + 100, end=start + 600, ticks=2),
                       dict(start=start + 800, end=start + 800, ticks=0)])
        view = self.show(actor, "测试玩家")
        rows = [row for row in view.canvas.lanes if row[1] == "醉舞九天"]
        self.assertEqual(len(rows), 1)
        self.assertEqual([(m.start, m.end, m.ticks) for m in rows[0][2]], [(100, 600, 2), (800, 800, 0)])
        self.assertNotIn(SPECIAL, [name for _, name, _ in view.canvas.lanes])

    def test_adjacent_actions_keep_separate_icons_and_wrapped_mechanics_keep_their_name(self):
        actor = sample()
        start = actor.startTime
        actor.occResult["测试玩家"]["result"]["replay"]["normal"] = [
            env("同招", start + time, ticks=4) for time in (1100, 1200, 1200)]
        view = self.show(actor, "测试玩家")
        casts = next(items for _, label, items in view.canvas.lanes if label == NORMAL)
        self.assertEqual([(len(item.records), item.records[0].ticks) for item in casts], [(1, 4)] * 3)
        actor.bh.log["environment"] = [env("长机制", start, duration=80000)]
        view = self.show(actor)
        labels = [g.label for row in view.canvas.rows for g in row.groups if g.name == '长机制']
        self.assertGreater(len(labels), 1)
        self.assertEqual(set(labels), {'长机制'})

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

    def test_personal_icon_rows_drag_zoom_and_full_image_include_the_last_cast(self):
        actor = sample()
        replay = actor.occResult['测试玩家']['result']['replay']
        replay['normal'][1]['num'] = 5
        replay['normal'].append(env('读条', actor.startTime+71000))
        view = TimelineView.from_actor(actor, '测试玩家', compact=True)
        self.addCleanup(view.close)
        view.resize(720,180)
        view.show()
        self.app.processEvents()
        casts = next(items for kind, name, items in view.canvas.lanes if name == NORMAL)
        self.assertEqual(casts[-1].start,71000)
        self.assertTrue(any(m.name == '读条' and '原记录计数 5' in m.detail for g in casts for m in g.records))
        h = view.canvas.horizontalScrollBar()
        self.assertGreater(h.maximum(),0)
        viewport = view.canvas.viewport()
        QTest.mousePress(viewport, Qt.LeftButton, pos=QPoint(300,50))
        QTest.mouseMove(viewport, QPoint(150,50))
        QTest.mouseRelease(viewport, Qt.LeftButton, pos=QPoint(150,50))
        self.assertEqual(h.value(),150)
        old_max = h.maximum()
        view.zoom.setCurrentIndex(2)
        self.app.processEvents()
        self.assertGreater(h.maximum(),old_max)
        h.setValue(round(70 * view.canvas.seconds))
        self.app.processEvents()
        self.assertIn(71000, [m.start for _,m in view.canvas.hits])
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'sheet.png'
            view.canvas.save_png(path)
            image=QImage(str(path))
            self.assertFalse(image.isNull())
            self.assertEqual(image.width(), view.canvas.viewport().width())
            self.assertEqual(image.height(), view.canvas.export_height(image.width()))
            self.assertGreater(image.height(),view.canvas.content_height)

    def test_current_talents_and_observed_charge_recovery(self):
        actor = sample()
        actor.timestamp = 1795673277
        result = actor.occResult['测试玩家']
        result['occ'] = '2h'
        result['result']['qixue'] = {'1':'遥归','2':'流迟'}
        replay = result['result']['replay']
        replay['special'] = [env('水月无间',actor.startTime + t, icon='1522') for t in (0,10000,70000)]
        replay['normal'] = [env('彼针',actor.startTime, icon='1518', num=25)]
        _, marks, _ = timeline_data(actor,'测试玩家')
        self.assertEqual([(m.start,m.end,m.name) for m in marks if m.track=='水月无间'],
                         [(0,10000,'1/2'),(10000,60000,'0/2'),(60000,70000,'1/2'),(70000,90000,'0/2')])
        self.assertEqual([(m.start,m.end) for m in marks if m.track=='彼针'],[(0,60000)])
        self.assertEqual({m.icon for m in marks if m.lane == '调息'}, {'1518', '1522'})
        self.assertEqual([(m.start,m.end) for m in cooldown_intervals({'甲':(20,1,[0,3000,24000])},35000)],
                         [(0,3000),(3000,23000),(24000,35000)])
        self.assertFalse(action_icon("1522").isNull())
        self.assertFalse(action_icon(ACTION_ICONS["35"]).isNull())

    def test_wu_native_cast_keeps_classification_and_art_and_only_healer_casts_show_resource_cd(self):
        actor = sample()
        actor.timestamp = 1795673277
        actor.occResult["悟心法"] = {"occ":"7pw","result":{}}
        actor.personalTimelines = {"悟心法":[
            Observation(actor.startTime+1000,"101723","追命箭·悟","施放",1,0),
            Observation(actor.startTime+2000,"101723","追命箭·悟","招式命中",1,1)]}
        _,marks,_ = timeline_data(actor,"悟心法")
        cast,hit = [m for m in marks if m.name=="追命箭·悟"]
        self.assertEqual((cast.lane, hit.lane), (NORMAL, "招式命中"))
        self.assertFalse(action_icon(cast.icon).isNull())
        self.assertFalse(any(m.lane == "调息" for m in marks))
        actor.occResult["悟心法"]["occ"] = "5hw"
        actor.personalTimelines["悟心法"] = [Observation(actor.startTime+1000,"100460","左旋右转·悟","施放",1,0)]
        _, marks, _ = timeline_data(actor, "悟心法")
        self.assertEqual([(m.start,m.end) for m in marks if m.lane=="调息"],[(1000,41000)])


if __name__=="__main__":
    unittest.main()

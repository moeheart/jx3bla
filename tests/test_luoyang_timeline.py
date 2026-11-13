"""Mechanism-specific de-duplication and real Tk timeline lane geometry."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS
import tkinter as tk
import unittest
from unittest.mock import patch

from replayer.boss.luoyangzhizhan.Timeline import STYLES, finalize_timeline
from replayer.boss.luoyangzhizhan.LuoyangEvidence import record_environment
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsReplayer
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiReplayer
from tests import test_luoyang_heroic_first_three as fixtures
from tools.ValidateLuoyangLastTwo import replayer, event
from tools.TimelineLayout import layout_timeline_records
from window.TimelineWindow import TimelineWindow


def row(time, label='潜渊之刺', kind='cast', source='boss'):
    icon, color = STYLES.get(label, ('2031', '#b91c1c'))
    return dict(start=time, skillname=label, skillid='45485', iconid=icon,
                color=color, type=kind, source=source, duration=0, num=1, description='')


class LuoyangTimelineTests(unittest.TestCase):
    def test_no_tail_candidate_can_remove_an_in_bounds_fallback(self):
        shout, cast = row(4000, kind='shout'), row(6000)
        r = NS(startTime=0, finalTime=5000, bh=NS(log={'environment': [shout, cast]}),
               bld=NS(info=NS(map='25人英雄洛阳之战')))
        finalize_timeline(r)
        self.assertEqual(r.bh.log['environment'], [shout])

    def test_shout_cast_representation_merges_but_parallel_caster_and_casts_survive(self):
        records = [row(1000), row(1500), row(2000, kind='shout'), row(2000, kind='shout', source='other')]
        r = NS(startTime=0, finalTime=10000, bh=NS(log={'environment': records}),
               bld=NS(info=NS(map='25人英雄洛阳之战')))
        finalize_timeline(r)
        self.assertEqual([(e['start'], e['source']) for e in r.bh.log['environment']],
                         [(1000, 'boss'), (1500, 'boss'), (2000, 'other')])

    def test_casts_are_not_debounced_and_multitarget_hits_keep_distinct_casters(self):
        r = replayer(ShiChaoyiReplayer, [('boss', '139365', '史朝义')])
        mapping = {('Cast', '45726'): ('连斩·一式', *STYLES['连斩·一式']),
                   ('Skill', '46439'): ('千钧锤落', *STYLES['千钧锤落'])}
        for time in (2000, 2500):
            record_environment(r, event('Cast', time, id='45726'), mapping)
        for source in ('first', 'second'):
            for target in ('p', 'q'):
                r.statDict.setdefault(target, {})
                record_environment(r, event('Skill', 3000, id='46439', caster=source,
                                            target=target, damage=10), mapping)
        self.assertEqual(len(r.bh.log['environment']), 4)

    def test_fire_ring_children_form_one_heroic_wave_with_missing_scene_fallback(self):
        r = fixtures.encounter(YimanTwinsReplayer, {'boss': ('139373', '伊曼·寂夜')})
        for source, time in (('ring1', 2000), ('ring2', 4500), ('ring3', 7000), ('ring4', 20000)):
            record_environment(r, event('Cast', time, id='45912', caster=source), r.ENVIRONMENT)
        self.assertEqual([e['start'] for e in r.bh.log['environment']], [2000, 20000])
        r.bh.log['environment'].insert(0, row(1000, '链舞火环', 'phase', ''))
        finalize_timeline(r)
        self.assertEqual([(e['type'], e['start']) for e in r.bh.log['environment']],
                         [('phase', 1000), ('cast', 20000)])
        normal = fixtures.encounter(YimanTwinsReplayer, {'boss': ('139319', '伊曼·寂夜')})
        normal.bld.info.map = '25人普通洛阳之战'
        for time in (2000, 4500):
            record_environment(normal, event('Cast', time, id='45912'), normal.ENVIRONMENT)
        self.assertEqual(len(normal.bh.log['environment']), 2)

    def test_heavy_slash_is_absent_but_other_sha_mechanic_and_raw_event_survive(self):
        r = replayer(ShiChaoyiReplayer, [('boss', '139365', '史朝义'), ('sha', '139363', '煞将')])
        heavy = event('Cast', 2000, id='45539', caster='sha')
        before = deepcopy(vars(heavy))
        r.analyseSecondStage(heavy)
        r.analyseSecondStage(event('Cast', 2500, id='45535', caster='sha'))
        r.getResult()
        self.assertEqual(vars(heavy), before)
        self.assertEqual([e['skillname'] for e in r.bh.log['environment']], ['煞骸崩陨'])

    def test_phase_cast_priority_is_one_direction_including_near_simultaneous_ring(self):
        for label, expected_type in (('链舞火环', 'phase'), ('潜渊之刺', 'cast')):
            with self.subTest(label=label):
                records = [row(4000, label, 'phase', ''), row(4500, label)]
                r = NS(startTime=0, finalTime=10000, bh=NS(log={'environment': records}),
                       bld=NS(info=NS(map='25人英雄洛阳之战')))
                finalize_timeline(r)
                self.assertEqual([e['type'] for e in r.bh.log['environment']], [expected_type])

    def test_measured_phase_has_priority_over_cast_in_both_difficulties_and_input_orders(self):
        for map_name in ('25人普通洛阳之战', '25人英雄洛阳之战'):
            for reverse in (False, True):
                with self.subTest(map=map_name, reverse=reverse):
                    phase = dict(row(4000, '聚邪阶段', 'phase', ''), duration=3000)
                    records = [phase, row(4500, '聚邪凝渊')]
                    if reverse:
                        records.reverse()
                    r = NS(startTime=0, finalTime=10000, bh=NS(log={'environment': records}),
                           bld=NS(info=NS(map=map_name)))
                    finalize_timeline(r)
                    self.assertEqual(r.bh.log['environment'], [phase])
                    self.assertEqual(phase['duration'], 3000)

    def test_styles_use_packaged_icons_and_no_generic_placeholder(self):
        for label, (icon, color) in STYLES.items():
            self.assertNotIn(icon, ('0', '340', '341'), label)
            self.assertTrue((Path('icons')/(icon+'.png')).is_file(), label)
            self.assertRegex(color, r'^#[0-9a-fA-F]{6}$')

    def test_layout_preserves_order_positions_and_long_label_extents(self):
        records = [row(100, '长标签'*15), row(0), row(100, source='other')]
        before = deepcopy(records)
        result = layout_timeline_records(records, lambda t: t/10, lambda text: len(text)*8)
        self.assertEqual(records, before)
        self.assertEqual([i['x'] for i in result['items']], [10, 0, 10])
        self.assertEqual(result['laneCount'], 3)
        self.assertLess(result['minX'], 0)

    def test_real_tk_labels_never_collide_and_export_stays_in_original_order(self):
        root = tk.Tk(); root.withdraw()
        records = [row(59999, '同一时刻很长的机制名称甲'), row(59999, '同一时刻很长的机制名称乙'),
                   row(0, '左边界长标签'), row(60000, '下一分钟独立事件')]
        records[0]['color'] = 'invalid-color'
        before = deepcopy(records)
        window = TimelineWindow(); window.setData(NS(startTime=0, finalTime=120000,
                                                    log={'environment': records}), '史朝义')
        try:
            with patch('window.TimelineWindow.Image.open', side_effect=OSError('broken icon')):
                window.loadWindow()
            window.window.withdraw(); root.update_idletasks()
            canvas = window.canvas
            labels = canvas.find_withtag('timeline-label')
            self.assertEqual(len(labels), len(records))
            boxes = [canvas.bbox(item) for item in labels]
            for index, a in enumerate(boxes):
                for b in boxes[index+1:]:
                    self.assertFalse(a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3])
            region = tuple(map(float, canvas.cget('scrollregion').split()))
            self.assertTrue(all(region[0] <= b[0] and region[2] >= b[2] for b in boxes))
            self.assertEqual(records, before)
            with patch('window.TimelineWindow.pyperclip.copy') as copy, patch('window.TimelineWindow.messagebox.showinfo'):
                window.generateLinear()
            expected = ''.join('%.1f,%s;\n' % (r['start']/1000, r['skillname']) for r in records)
            self.assertEqual(copy.call_args.args[0], expected)
        finally:
            if hasattr(window, 'window'):window.window.destroy()
            root.destroy()


if __name__ == '__main__':
    unittest.main()

"""Shared personal timeline keeps concurrent mechanics and skills accessible."""
from copy import deepcopy
from types import SimpleNamespace as NS
import tkinter as tk
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image
from tools.ResourcePath import get_icon_path
from window.ReplayTimeline import TimelineIcons

from replayer.occ.BuTianJue import BuTianJueWindow
from replayer.occ.LingSu import LingSuWindow
from replayer.occ.YunChangXinJing import YunChangXinJingWindow
from replayer.occ.LiJingYiDao import LiJingYiDaoWindow
from replayer.occ.XiangZhi import XiangZhiProWindow
from replayer.occ.HuaJianYou import HuaJianYouWindow


WINDOWS = (BuTianJueWindow, LingSuWindow, YunChangXinJingWindow,
           LiJingYiDaoWindow, XiangZhiProWindow, HuaJianYouWindow)


class PersonalTimelineTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)

    def test_bundled_icon_loads_with_current_and_pillow_9_0_api(self):
        path = get_icon_path('340')
        self.assertTrue(Path(path).is_file())
        # Pillow9.0 supplies Image.LANCZOS without the later Resampling enum.
        legacy = NS(open=Image.open, LANCZOS=Image.LANCZOS)
        for api in (Image, legacy):
            with self.subTest(legacy=api is legacy), patch('window.ReplayTimeline.Image', api):
                icon = TimelineIcons(self.root)['340']
                self.assertEqual((icon.width(), icon.height()), (20, 20))

    def make(self, cls, screen=(1920, 1080)):
        window = cls.__new__(cls)
        window.window = tk.Toplevel(self.root)
        window.window.withdraw()
        window.window.attributes('-alpha', 0)
        window.window.geometry('750x900')
        window.themeColor = '#64fab4'
        window.config = NS(item={name: {'stack': '不堆叠'} for name in
                                 ('butian', 'lingsu', 'yunchang', 'lijing', 'xiangzhi')})
        records = [dict(skillname='并发机制%d' % i, start=1000, duration=1500,
                        iconid='missing-test-icon', color='#1122aa', num=1) for i in range(8)]
        # Different point-event colors must remain visible without a duration bar.
        records.append(dict(skillname='点事件', start=10000, duration=0,
                            iconid='missing-test-icon', color='#aa2244', num=2))
        skill = dict(skillname='个人技能', start=2000, duration=500,
                     iconid='missing-test-icon', num=1)
        replay = {'startTime': 1000, 'environment': records, 'normal': [skill],
                  'special': [skill], 'call': [skill],
                  'heat': {'timeline': [[0, 100] for _ in range(5)]}}
        for name in ('shangyang', 'zhonglin', 'lancui', 'kuaixue'):
            replay['heat'][name] = {'timeline': [0, 100]}
        for name in ('mxym', 'xwgd', 'ghzs', 'zwjt', 'yaoxing', 'qianzhi', 'qingchuan', 'hxpy'):
            replay[name] = [[1000, 0], [2000, 1]]
        window.result = {'overall': {'sumTime': 20000}, 'replay': replay}
        before = deepcopy(window.result)
        with patch.object(tk.Misc, 'winfo_screenwidth', return_value=screen[0]), \
                patch.object(tk.Misc, 'winfo_screenheight', return_value=screen[1]):
            window.renderReplay()
            window.bottom = tk.Frame(window.window, width=730, height=200)
            window.bottom.place(x=10, y=620)
            window.window.deiconify()
            self.root.update()
        self.assertEqual(window.result, before)
        return window

    def test_six_renderers_keep_skill_band_colors_icons_and_shared_time_position(self):
        for cls in WINDOWS:
            with self.subTest(occupation=cls.__name__):
                window = self.make(cls)
                timeline = window.replayTimeline
                self.assertEqual(timeline.canvas.winfo_height(), 80)
                self.assertEqual(timeline.environment.winfo_height(), 72)
                self.assertGreaterEqual(timeline.layout['laneCount'], 8)
                self.assertEqual(window.bottom.winfo_y(), 662)
                self.assertTrue(timeline.canvas.im['missing-test-icon'])
                rectangles = [item for item in timeline.environment.find_all()
                              if timeline.environment.type(item) == 'rectangle']
                self.assertIn('#1122aa', [timeline.environment.itemcget(item, 'fill') for item in rectangles])
                self.assertIn('#aa2244', [timeline.environment.itemcget(item, 'outline') for item in rectangles])
                timeline.scroll_x('moveto', .5)
                self.root.update()
                self.assertEqual(timeline.canvas.xview(), timeline.environment.xview())
                window.window.destroy()

    def test_small_screen_preserves_skill_band_and_can_scroll_to_bottom_panels(self):
        window = self.make(LingSuWindow, (1024, 768))
        timeline = window.replayTimeline
        self.assertLessEqual(window.window.winfo_height(), 688)
        self.assertTrue(hasattr(timeline, 'outer'))
        self.assertGreaterEqual(timeline.canvas.winfo_rooty(), timeline.outer.winfo_rooty())
        self.assertLessEqual(timeline.canvas.winfo_rooty()+80,
                             timeline.outer.winfo_rooty()+timeline.outer.winfo_height())
        timeline.environment.yview_moveto(1)
        timeline.outer.yview_moveto(1)
        self.root.update()
        self.assertEqual(timeline.environment.yview()[1], 1.0)
        self.assertLessEqual(window.bottom.winfo_rooty()+window.bottom.winfo_height(),
                             timeline.outer.winfo_rooty()+timeline.outer.winfo_height())


if __name__ == '__main__':
    unittest.main()

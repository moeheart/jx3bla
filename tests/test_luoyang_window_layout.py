"""Measure real hidden Tk geometry, including every player's replay button."""
from types import SimpleNamespace as NS
import tkinter as tk
import unittest
from unittest.mock import patch

from replayer.boss.luoyangzhizhan.TuliHeshun import TuliHeshunWindow
from replayer.boss.luoyangzhizhan.TianChengsi import TianChengsiWindow
from replayer.boss.luoyangzhizhan.YimanTwins import YimanTwinsWindow
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingWindow
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiWindow


WINDOWS = (TuliHeshunWindow, TianChengsiWindow, YimanTwinsWindow,
           LuoyangAshinaChengqingWindow, ShiChaoyiWindow)


class LuoyangWindowLayoutTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        original = tk.Toplevel

        def hidden(*args, **kwargs):
            top = original(*args, **kwargs)
            top.withdraw()
            top.attributes('-alpha', 0)
            return top

        self.hidden = patch('tkinter.Toplevel', side_effect=hidden)
        self.hidden.start()
        self.addCleanup(self.hidden.stop)

    def make(self, cls, screen):
        rows = [dict(name='玩家%02d' % index, occ='4p', rdps=123456, rdpsRank=99,
                     equip={'score': 123456, 'sketch': '套装', 'forge': '15/0-0-0/6/0-0/6'})
                for index in range(25)]
        detail = {'win': 1, 'phaseTimes': {'常规技能': 150, '玄溟之火': 24},
                  'phasePeriods': [dict(name='玄溟之火', start=index*10000,
                                        end=(index+1)*10000, duration=10) for index in range(12)],
                  'mechanicNote': '命中为观察记录，不能据此判定玩家承担机制责任。'}
        occ = {row['name']: {'occ': '4p', 'result': {'overall': {}}, 'rank': {}} for row in rows}
        window = cls(NS(item={'general': {'mask': 0}}), rows, detail, occ,
                     {'bossBh': NS(), 'act': NS()})
        with patch.object(tk.Misc, 'winfo_screenwidth', return_value=screen[0]), \
                patch.object(tk.Misc, 'winfo_screenheight', return_value=screen[1]):
            window.loadWindow()
        window.window.deiconify()
        self.root.update()
        return window

    def assert_centered(self, window):
        canvas = window.statsCanvas
        left, _, right, _ = canvas.bbox('all')
        self.assertLessEqual(abs(left-(canvas.winfo_width()-right)), 1)
        table = canvas.winfo_children()[0]
        self.assertEqual(table.grid_size()[1], 26)  # Header plus all 25 players.
        for label in table.winfo_children():
            if isinstance(label, tk.Label):
                self.assertEqual(str(label.cget('anchor')), 'center')
                self.assertEqual(str(label.grid_info()['sticky']), '')

    def test_five_bosses_center_and_show_all_25_rows_on_1080_screen(self):
        for cls in WINDOWS:
            with self.subTest(boss=cls.__name__):
                window = self.make(cls, (1920, 1080))
                canvas = window.statsCanvas
                self.assert_centered(window)
                self.assertGreaterEqual(canvas.winfo_height(), canvas.winfo_children()[0].winfo_reqheight())
                self.assertEqual(canvas.yview(), (0.0, 1.0))
                self.assertLessEqual(window.window.winfo_height(), 1000)
                window.window.destroy()

    def test_small_screen_scrolls_to_last_cell_and_recenters_after_resize(self):
        window = self.make(ShiChaoyiWindow, (1024, 768))
        top, canvas = window.window, window.statsCanvas
        self.assertLessEqual(top.winfo_width(), 984)
        self.assertLessEqual(top.winfo_height(), 688)
        self.assertLess(canvas.yview()[1], 1)
        table = canvas.winfo_children()[0]
        last = max(table.winfo_children(), key=lambda child:
                   (int(child.grid_info()['row']), int(child.grid_info()['column'])))
        canvas.xview_moveto(1)
        canvas.yview_moveto(1)
        self.root.update()
        self.assertGreaterEqual(last.winfo_rootx(), canvas.winfo_rootx())
        self.assertLessEqual(last.winfo_rootx()+last.winfo_width(), canvas.winfo_rootx()+canvas.winfo_width())
        self.assertGreaterEqual(last.winfo_rooty(), canvas.winfo_rooty())
        self.assertLessEqual(last.winfo_rooty()+last.winfo_height(), canvas.winfo_rooty()+canvas.winfo_height())
        top.geometry('1600x1050')
        self.root.update()
        self.assert_centered(window)
        self.assertEqual(canvas.xview(), (0.0, 1.0))
        self.assertEqual(canvas.yview(), (0.0, 1.0))


if __name__ == '__main__':
    unittest.main()

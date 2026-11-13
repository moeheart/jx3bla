"""Variable talent snapshots must never stop the personal replay window."""
import tkinter as tk
import unittest
from unittest.mock import patch

from window.QixueDisplay import format_qixue, UNAVAILABLE_TEXT
from window.HealerDisplayWindow import HealerDisplayWindow
from window.DpsDisplayWindow import DpsDisplayWindow


def snapshot(count):
    # Deliberately reverse insertion order, as object order is not slot order.
    return {'available': 1, **{str(i): '奇穴%d' % i for i in range(count, 0, -1)}}


class QixueFormatTests(unittest.TestCase):
    def test_observed_nine_four_and_ten_slots_and_legacy_twelve(self):
        for count in (9, 4, 10, 12, 6):
            with self.subTest(count=count):
                text = format_qixue(snapshot(count))
                self.assertEqual(text.replace('\n', ',').split(','),
                                 ['奇穴%d' % i for i in range(1, count + 1)])
                self.assertNotIn('undefined', text)
                self.assertNotIn('未记录', text)
                self.assertTrue(all(len(line.split(',')) <= 6 for line in text.splitlines()))

    def test_missing_slots_and_metadata_do_not_invent_tail_talents(self):
        data = {'available': 1, '9': '末项', '1': '首项', '2': None,
                '0': '忽略', '01': '忽略', '²': '忽略', 'note': '说明', '10': {}}
        self.assertEqual(format_qixue(data), '首项,末项')
        self.assertEqual(data['2'], None)

    def test_unavailable_or_empty_snapshot_keeps_the_hint(self):
        for value in (None, {}, [], {'available': 1}, {'available': 0, '1': '部分信息'},
                      {'available': 2, '1': '不应放行'}, {'available': 1, '1': '  '}):
            with self.subTest(value=value):
                self.assertEqual(format_qixue(value), UNAVAILABLE_TEXT)


class QixueWindowTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        original = tk.Toplevel

        def hidden_window(*args, **kwargs):
            window = original(*args, **kwargs)
            window.withdraw()
            return window

        self.patch = patch('tkinter.Toplevel', side_effect=hidden_window)
        self.patch.start()
        self.addCleanup(self.root.destroy)
        self.addCleanup(self.patch.stop)

    def test_missing_tenth_slot_does_not_interrupt_later_window_sections(self):
        for cls in (HealerDisplayWindow, DpsDisplayWindow):
            for talents in (snapshot(9), snapshot(4), {}, None):
                with self.subTest(window=cls.__name__, talents=talents):
                    window = cls.__new__(cls)
                    window.result = {'qixue': talents}
                    window.themeColor = '#006699'
                    window.title = '奇穴回归'
                    steps = []
                    for name in ('renderOverall', 'renderEquipment', 'renderHeal', 'renderDps',
                                 'renderSkill', 'renderReplay', 'renderTeam', 'renderRate', 'renderAdvertise'):
                        setattr(window, name, lambda name=name: steps.append(name))
                    window.loadWindow()
                    self.root.update_idletasks()
                    self.assertIn('renderReplay', steps)
                    self.assertIn('renderSkill', steps)
                    self.assertIn('renderRate', steps)
                    self.assertEqual(steps[-1], 'renderAdvertise')
                    frames = window.window.winfo_children()
                    self.assertEqual(len(frames), 1)
                    text = frames[0].winfo_children()[0].cget('text')
                    self.assertEqual(text, format_qixue(talents))
                    window.window.destroy()


if __name__ == '__main__':
    unittest.main()

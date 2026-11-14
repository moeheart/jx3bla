"""Exercise Window.start through a real Tk mainloop, including worker requests."""
import threading
import tkinter as tk
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from replayer.occ.XiangZhi import XiangZhiProWindow
from window.PotExtendWindow import PotExtendWindow
from window.SingleBossWindow import SingleBossWindow
from window.Window import Window


class ProbeWindow(Window):
    def __init__(self, root, on_load=None):
        super().__init__()
        self.root = root
        self.on_load = on_load
        self.loads = []
        self.finished = 0

    def loadWindow(self):
        self.loads.append(threading.get_ident())
        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.attributes('-alpha', 0)
        self.window.protocol('WM_DELETE_WINDOW', self.final)
        canvas = tk.Canvas(self.window)
        canvas.pack()
        if self.on_load:
            self.on_load(self, canvas)
        canvas.create_rectangle(0, 0, 20, 20)
        self.finished += 1


class SyntheticXiangZhiWindow(XiangZhiProWindow):
    """Use the actual replay renderer without committing a player's result."""
    def __init__(self, root):
        Window.__init__(self)
        self.root = root
        self.themeColor = '#64fab4'
        self.config = SimpleNamespace(item={'xiangzhi': {'stack': '不堆叠'}})
        skill = dict(skillname='梅花三弄', start=2000, duration=500,
                     iconid='7059', num=1)
        self.result = {'overall': {'sumTime': 12000}, 'replay': {
            'startTime': 1000, 'environment': [dict(skillname='测试并行机制',
                start=2000, duration=1000, iconid='340', color='#334499', num=1)],
            'normal': [skill], 'special': [skill], 'call': [skill]}}
        self.loads = []
        self.finished = 0

    def loadWindow(self):
        self.loads.append(threading.get_ident())
        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.attributes('-alpha', 0)
        self.window.protocol('WM_DELETE_WINDOW', self.final)
        # This executes the actual create_image path that failed in production.
        self.renderReplay()
        self.finished += 1


class WindowLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui_thread = threading.get_ident()
        self.errors = []
        self.worker_errors = []
        self.root.report_callback_exception = lambda typ, value, tb: self.errors.append((typ, value))
        self.dispatcher = Window.install_ui(self.root)
        self.workers = []

    def tearDown(self):
        for worker in self.workers:
            worker.join(1)
            self.assertFalse(worker.is_alive(), 'window request blocked its worker')
        if Window._exists(self.root):
            self.root.destroy()
        self.assertEqual(self.worker_errors, [])

    def worker(self, callback):
        def run():
            try:
                callback()
            except Exception as error:
                self.worker_errors.append(error)
        thread = threading.Thread(target=run, daemon=True)
        self.workers.append(thread)
        thread.start()
        return thread

    def business_window(self, cls):
        """Real overridden final(), with anonymous data and a minimal Tk body."""
        window = cls.__new__(cls)
        Window.__init__(window)
        window.root = self.root
        window.loads = []
        window.finished = 0
        window.on_load = None
        window.loadWindow = MethodType(ProbeWindow.loadWindow, window)
        if cls is SingleBossWindow:
            window.potExtendRunning = False
            window.potWindowActivated = True
            window.potList = [['anonymous', '22h', 0, 'synthetic', 'test', [], 99]]
            window.scoreList = [-2]
            window.bossNum = 5
            window.analyser = SimpleNamespace(changeResult=Mock())
        else:
            window.singleBossWindow = SimpleNamespace(potExtendRunning=True)
        return window

    def assert_business_close(self, window):
        if isinstance(window, SingleBossWindow):
            self.assertEqual(window.potList[0][6], -2)
            window.analyser.changeResult.assert_called_once_with(window.potList, 5)
        else:
            self.assertFalse(window.singleBossWindow.potExtendRunning)

    def run_until(self, predicate, timeout=2500):
        """Pump the actual event loop, not a serial series of root.update()."""
        timed_out = []
        poll_token = [None]
        def poll():
            if predicate():
                self.root.quit()
            else:
                poll_token[0] = self.root.after(5, poll)
        def expired():
            timed_out.append(True)
            self.root.quit()
        watchdog = self.root.after(timeout, expired)
        poll_token[0] = self.root.after(0, poll)
        self.root.mainloop()
        if Window._exists(self.root):
            self.root.after_cancel(watchdog)
            self.root.after_cancel(poll_token[0])
        self.assertFalse(timed_out, 'mainloop lifecycle operation timed out')
        self.assertTrue(predicate())

    def test_start_mainloop_and_actual_xiangzhi_images_run_on_ui_thread(self):
        window = SyntheticXiangZhiWindow(self.root)
        image_threads = []
        original = tk.Canvas.create_image
        def image(canvas, *args, **kwargs):
            image_threads.append(threading.get_ident())
            return original(canvas, *args, **kwargs)
        with patch.object(tk.Canvas, 'create_image', image):
            self.root.after(0, window.start)
            self.run_until(lambda: window.finished == 1)
        self.assertEqual(window.loads, [self.ui_thread])
        self.assertGreaterEqual(len(image_threads), 4)
        self.assertEqual(set(image_threads), {self.ui_thread})
        self.assertTrue(window.alive())
        self.assertEqual(self.errors, [])

    def test_worker_and_concurrent_duplicate_start_create_only_one_window(self):
        window = ProbeWindow(self.root)
        release = threading.Event()
        for _ in range(8):
            self.worker(lambda: (release.wait(1), window.start(), window.start()))
        release.set()
        self.run_until(lambda: window.finished == 1 and all(not worker.is_alive() for worker in self.workers))
        original = window.window
        # Flush a barrier behind all pending starts before counting windows.
        drained = []
        self.dispatcher.post(lambda: drained.append(True))
        self.run_until(lambda: bool(drained))
        self.assertEqual(window.loads, [self.ui_thread])
        self.assertEqual(self.root.winfo_children(), [original])
        with patch.object(original, 'lift', wraps=original.lift) as lifted:
            window.start()
            self.run_until(lambda: lifted.called)
        self.assertIs(window.window, original)
        self.assertEqual(self.errors, [])

    def test_pending_cancel_and_repeated_final_do_not_construct_a_window(self):
        window = ProbeWindow(self.root)
        done = []
        def requests():
            window.start()
            window.final()
            window.final()
            self.dispatcher.post(lambda: done.append(True))
        self.worker(requests)
        self.run_until(lambda: bool(done))
        self.assertEqual(window.loads, [])
        self.assertFalse(window.alive())
        self.assertFalse(Window._exists(window.window))
        self.assertEqual(self.root.winfo_children(), [])
        window.start()
        self.run_until(lambda: window.finished == 1)
        self.assertEqual(self.errors, [])

    def test_business_final_overrides_cancel_pending_opens_and_keep_saved_scores(self):
        for cls in (SingleBossWindow, PotExtendWindow):
            with self.subTest(window=cls.__name__):
                window = self.business_window(cls)
                child = None
                if cls is SingleBossWindow:
                    # Closing the pot editor must also cancel an add-pot child
                    # that was requested but has not been constructed yet.
                    child = self.business_window(PotExtendWindow)
                    child.singleBossWindow = window
                    window.potExtendRunning = True
                    window.potExtendWindow = child
                    child.start()
                window.start()
                window.final()
                drained = []
                self.dispatcher.post(lambda: drained.append(True))
                self.run_until(lambda: bool(drained))
                self.assertEqual(window.loads, [])
                self.assertFalse(window.alive())
                self.assertFalse(Window._exists(window.window))
                self.assert_business_close(window)
                if child:
                    self.assertEqual(child.loads, [])
                    self.assertFalse(window.potExtendRunning)
                self.assertEqual(self.root.winfo_children(), [])
                self.assertEqual(self.errors, [])

    def test_business_worker_final_destroys_on_ui_thread_and_keeps_saved_scores(self):
        for cls in (SingleBossWindow, PotExtendWindow):
            with self.subTest(window=cls.__name__):
                window = self.business_window(cls)
                window.start()
                self.run_until(lambda: window.finished == 1)
                top = window.window
                destroyed_on = []
                original = top.destroy
                def destroy():
                    destroyed_on.append(threading.get_ident())
                    return original()
                with patch.object(top, 'destroy', destroy):
                    self.worker(window.final)
                    self.run_until(lambda: not Window._exists(top))
                self.assertEqual(destroyed_on, [self.ui_thread])
                self.assertFalse(window.alive())
                self.assert_business_close(window)
                self.assertEqual(self.errors, [])

    def test_queued_close_during_real_image_render_waits_for_render_completion(self):
        window = SyntheticXiangZhiWindow(self.root)
        sequence = []
        original = tk.Canvas.create_image
        def close():
            sequence.append(('close', window.finished))
            window.final()
        def image(canvas, *args, **kwargs):
            if not sequence:
                sequence.append(('image', window.finished))
                self.root.after(0, close)
            return original(canvas, *args, **kwargs)
        with patch.object(tk.Canvas, 'create_image', image):
            window.start()
            self.run_until(lambda: len(sequence) == 2 and not window.alive())
        self.assertEqual(sequence, [('image', 0), ('close', 1)])
        self.assertFalse(window.alive())
        self.assertEqual(self.errors, [])

    def test_nested_idle_close_cancels_in_progress_canvas_without_error(self):
        for direct_destroy in (False, True):
            with self.subTest(direct_destroy=direct_destroy):
                def close_during_load(window, canvas):
                    self.root.after_idle(window.window.destroy if direct_destroy else window.final)
                    self.root.update_idletasks()
                    # The canvas command is now absent. The lifecycle must
                    # recognize this particular TclError as cancellation.
                    canvas.create_image(0, 0)
                window = ProbeWindow(self.root, close_during_load)
                done = []
                window.start()
                self.dispatcher.post(lambda: done.append(True))
                self.run_until(lambda: bool(done))
                self.assertFalse(window.alive())
                self.assertFalse(Window._exists(window.window))
                self.assertEqual(self.errors, [])

    def test_reopen_ignores_stale_close_and_destroy_callbacks(self):
        window = ProbeWindow(self.root)
        window.start()
        self.run_until(lambda: window.finished == 1)
        old = window.window
        # The callback may already be queued when its original Toplevel exits.
        stale_close = lambda: window._close_current(old)
        stale_destroy = lambda: window._destroy_window(old)
        self.worker(window.final)
        self.run_until(lambda: not Window._exists(old))
        window.start()
        self.run_until(lambda: window.finished == 2)
        current = window.window
        stale_close()
        stale_destroy()
        window._window_destroyed(SimpleNamespace(widget=old), old)
        self.assertIs(window.window, current)
        self.assertTrue(current.winfo_exists())
        self.assertTrue(window.alive())
        # Exercise the actual installed WM callback for the current instance.
        current.tk.call(current.protocol('WM_DELETE_WINDOW'))
        self.assertFalse(window.alive())
        self.assertFalse(Window._exists(window.window))
        # A stale close arriving before a queued reopen must not invalidate
        # that new generation, even while self.window retains the old widget.
        window.start()
        window._close_current(current)
        self.run_until(lambda: window.finished == 3)
        self.assertTrue(window.alive())
        self.assertEqual(self.errors, [])

    def test_external_destroy_updates_liveness_and_allows_reopen(self):
        window = ProbeWindow(self.root)
        window.start()
        self.run_until(lambda: window.finished == 1)
        window.window.destroy()
        self.assertFalse(window.alive())
        self.assertFalse(Window._exists(window.window))
        window.start()
        self.run_until(lambda: window.finished == 2)
        self.assertTrue(window.alive())
        self.assertEqual(self.errors, [])

    def test_root_shutdown_discards_pending_open_and_accepts_late_requests(self):
        window = ProbeWindow(self.root)
        # This starts the request inside mainloop but destroys Tk before its
        # dispatcher runs; root's Destroy callback must clear the queue.
        def shutdown():
            window.start()
            self.root.destroy()
        self.root.after(0, shutdown)
        self.root.mainloop()
        self.assertTrue(self.dispatcher.closed)
        self.assertTrue(self.dispatcher.requests.empty())
        self.assertEqual(window.loads, [])
        self.worker(lambda: (window.start(), window.final()))
        self.assertEqual(self.errors, [])

    def test_root_shutdown_during_nested_layout_cancels_render(self):
        def close_root(window, canvas):
            self.root.after_idle(self.root.destroy)
            self.root.update_idletasks()
            canvas.create_image(0, 0)
        window = ProbeWindow(self.root, close_root)
        self.root.after(0, window.start)
        self.root.mainloop()
        self.assertTrue(self.dispatcher.closed)
        self.assertFalse(window.alive())
        self.assertFalse(Window._exists(window.window))
        self.assertEqual(self.errors, [])

    def test_worker_close_request_does_not_hide_error_on_still_live_canvas(self):
        error = tk.TclError('invalid data before queued close ran')
        def fail_during_close(window, canvas):
            worker = self.worker(window.final)
            worker.join(1)
            # Worker final has posted close, but Tk has not destroyed anything.
            # A mere generation change cannot classify this as cancellation.
            self.assertTrue(window.window.winfo_exists())
            raise error
        window = ProbeWindow(self.root, fail_during_close)
        window.start()
        self.run_until(lambda: bool(self.errors))
        self.assertEqual(self.errors, [(tk.TclError, error)])
        self.assertFalse(window.alive())
        self.assertFalse(Window._exists(window.window))

    def test_unrelated_render_errors_are_reported_cleaned_and_recoverable(self):
        for error in (ValueError('bad replay data'), tk.TclError('invalid color on live canvas')):
            with self.subTest(error=type(error).__name__):
                def fail(window, canvas):
                    raise error
                window = ProbeWindow(self.root, fail)
                self.errors.clear()
                window.start()
                self.run_until(lambda: bool(self.errors))
                self.assertEqual(self.errors, [(type(error), error)])
                self.assertFalse(Window._exists(window.window))
                self.assertFalse(window.alive())
                self.assertEqual(self.root.winfo_children(), [])
                window.on_load = None
                window.start()
                self.run_until(lambda: window.finished == 1)
                self.assertTrue(window.alive())
                window.final()


if __name__ == '__main__':
    unittest.main()

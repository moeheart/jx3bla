# Created by moeheart at 08/07/2022
# 所有“子窗口”(tk.Toplevel)的基类。实现了子窗口的基本功能。所有窗口类都应该由此派生.

import queue
import sys
import threading
import tkinter as tk


class _WindowDispatcher:
    """Workers submit Python callables; only the Tk owner drains the queue."""

    def __init__(self, root):
        self.root = root
        self.thread_id = threading.get_ident()
        self.requests = queue.SimpleQueue()
        self.closed = False
        self.timer = root.after(20, self._drain)
        root.bind('<Destroy>', self._destroyed, add='+')

    def post(self, callback):
        if not self.closed:
            self.requests.put(callback)

    def _drain(self):
        self.timer = None
        # No timer is installed while callbacks run, including nested idle
        # processing during layout. A second render cannot enter this drain.
        # Return to Tk between windows so close/input events are not delayed
        # behind an entire batch of requested replays.
        try:
            if self.closed:
                return
            try:
                callback = self.requests.get_nowait()
            except queue.Empty:
                return
            try:
                callback()
            except Exception:
                self.root.report_callback_exception(*sys.exc_info())
        finally:
            if not self.closed:
                self.timer = self.root.after(20, self._drain)

    def _destroyed(self, event):
        if event.widget is not self.root:
            return
        self.closed = True
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        while not self.requests.empty():
            self.requests.get_nowait()


class Window():
    '''
    窗口基类.
    '''

    def final(self):
        '''
        关闭窗口.
        '''
        # Invalidate opens that were queued before this close, even when no
        # Toplevel has been constructed yet. Capture the particular window so
        # a delayed close never destroys a subsequently reopened instance.
        self._generation += 1
        window = self.window
        dispatcher = self._dispatcher
        if dispatcher is not None and threading.get_ident() != dispatcher.thread_id:
            dispatcher.post(lambda: self._destroy_window(window))
        else:
            self._destroy_window(window)

    def start(self):
        '''
        显示窗口.
        '''
        root = tk._default_root
        if root is None:
            return
        dispatcher = getattr(root, '_jx3bla_window_dispatcher', None)
        if dispatcher is None:
            # The application installs this immediately after creating Tk.
            # Also support standalone windows/tests started on the main thread.
            if threading.current_thread() is not threading.main_thread():
                raise RuntimeError('Window.install_ui(root) must run on the Tk thread before starting windows')
            dispatcher = self.install_ui(root)
        self._dispatcher = dispatcher
        generation = self._generation
        dispatcher.post(lambda: self._open(generation))

    @staticmethod
    def install_ui(root):
        """Call once on the thread that created the application's Tk root."""
        dispatcher = getattr(root, '_jx3bla_window_dispatcher', None)
        if dispatcher is None:
            dispatcher = _WindowDispatcher(root)
            root._jx3bla_window_dispatcher = dispatcher
        return dispatcher

    @staticmethod
    def _exists(window):
        if window is None:
            return False
        try:
            return bool(window.winfo_exists())
        except tk.TclError:
            return False  # The root's interpreter may already be destroyed.

    def _destroy_window(self, window):
        if window is None:
            return
        if self.window is window:
            self.windowAlive = False
        if self._exists(window):
            window.destroy()

    def _window_destroyed(self, event, window):
        if event.widget is window and self.window is window:
            self.windowAlive = False

    def _close_current(self, window):
        if self.window is window and self._exists(window):
            self.final()

    def _open(self, generation):
        if generation != self._generation or self._dispatcher.closed:
            return
        if self._exists(self.window):
            self.window.deiconify()
            self.window.lift()
            return
        self.window = None
        self.windowAlive = True
        try:
            self.loadWindow()
        except tk.TclError:
            # A close/root shutdown processed by nested idle layout is a
            # cancellation. Invalid data or other errors on a live window must
            # still reach Tk's normal error reporter instead of being hidden.
            cancelled = (self._dispatcher.closed or
                         (self.window is not None and not self._exists(self.window)))
            self.windowAlive = False
            self._destroy_window(self.window)
            if not cancelled:
                raise
            return
        except Exception:
            self.windowAlive = False
            self._destroy_window(self.window)
            raise
        if generation != self._generation or not self._exists(self.window):
            self.windowAlive = False
            self._destroy_window(self.window)
            return
        window = self.window
        window.bind('<Destroy>', lambda event: self._window_destroyed(event, window), add='+')
        window.protocol('WM_DELETE_WINDOW', lambda: self._close_current(window))

    def alive(self):
        '''
        判断窗口是否存活.
        '''
        return self.windowAlive

    def __init__(self):
        '''
        初始化.
        '''
        self.windowAlive = False
        self.window = None
        self._generation = 0
        self._dispatcher = None

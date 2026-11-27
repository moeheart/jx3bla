"""Qt desktop shell. All widget changes happen on the QApplication thread."""
import json
import threading
import time
import urllib.request
from collections import defaultdict, deque
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QDialog, QFileDialog, QHBoxLayout,
    QGridLayout, QHeaderView, QLabel, QMainWindow, QMessageBox, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from Constants import ANNOUNCEMENT, EDITION, get_api_url, get_logs_url
from data.ReplaySession import AnalysisCancelled, ReplaySession, display_result
from tools.ResourcePath import get_resource_path, get_writable_path


STYLE = """
QMainWindow, QDialog, QWidget#workspace { background: #f4f7f7; color: #21343b; }
QLabel { color: #21343b; }
QWidget#rail { background: #193538; }
QLabel#brand { color: white; font-size: 22px; font-weight: 650; }
QLabel#version { color: #b4ceca; font-size: 12px; }
QPushButton { min-height: 26px; padding: 3px 12px; border: 1px solid #bdcecb;
              background: white; color: #243d40; border-radius: 5px; }
QPushButton:hover { border-color: #48948a; background: #edf7f3; }
QPushButton:disabled { color: #657573; background: #ecf0ef; border-color: #d7dfdc; }
QPushButton#primary { background: #14695f; color: white; border-color: #14695f; font-weight: 600; }
QPushButton#primary:hover { background: #12594f; }
QPushButton#nav { text-align: left; padding: 7px 12px; background: transparent; color: #d4e2df; border: 0; }
QPushButton#nav:hover, QPushButton#nav:checked { background: #30544f; color: white; }
QLabel#heading { font-size: 25px; font-weight: 650; }
QLabel#muted { color: #4c6666; }
QTableWidget, QTableView, QTreeView { background: white; alternate-background-color: #f6f9f8;
   selection-background-color: #d0eae2; selection-color: #153c33; gridline-color: #e3eae6; }
QHeaderView::section { background: #eaf1ee; color: #3d5753; border: 0;
   border-bottom: 1px solid #cbdad4; padding: 5px; }
QToolTip { background: #fffef8; color: #1c3332; }
"""


class _WindowPlacement(QObject):
    """Keep initial top-level windows inside the current monitor's work area."""
    def eventFilter(self, window, event):
        if (event.type() == QEvent.Type.Show and isinstance(window, (QDialog, QMainWindow))
                and not window.isMaximized() and not window.isFullScreen()):
            screen = window.parentWidget().screen() if window.parentWidget() else window.screen()
            if screen:
                available = screen.availableGeometry()
                window.resize(min(window.width(), max(240, available.width() - 20)),
                              min(window.height(), max(200, available.height() - 54)))
        return False


def configure_application(app):
    if app.findChild(_WindowPlacement) is None:
        app.installEventFilter(_WindowPlacement(app))
    app.setStyle('Fusion')
    palette = app.style().standardPalette()
    for role, color in ((QPalette.ColorRole.Window, '#f4f7f7'), (QPalette.ColorRole.Base, '#ffffff'),
                        (QPalette.ColorRole.Text, '#21343b'), (QPalette.ColorRole.WindowText, '#21343b'),
                        (QPalette.ColorRole.ButtonText, '#21343b')):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    font = QFont('Microsoft YaHei UI')
    font.setPointSize(10)
    app.setFont(font)
    app.setStyleSheet(STYLE)
    icon = QIcon(get_resource_path('jx3bla.ico'))
    if not icon.isNull():
        app.setWindowIcon(icon)


def table(headers):
    widget = QTableWidget(0, len(headers))
    widget.setHorizontalHeaderLabels(headers)
    widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    widget.setAlternatingRowColors(True)
    widget.setShowGrid(False)
    widget.verticalHeader().hide()
    widget.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    widget.horizontalHeader().setStretchLastSection(True)
    return widget


def set_row(widget, index, values):
    if index >= widget.rowCount():
        widget.insertRow(index)
    for col, value in enumerate(values):
        widget.setItem(index, col, QTableWidgetItem(str(value)))


def log_folder(config):
    from FileLookUp import FileLookUp
    lookup = FileLookUp()
    lookup.initFromConfig(config)
    if not lookup.basepath or not Path(lookup.basepath).is_dir():
        raise ValueError('找不到日志目录。请在设置中选择记录者或日志文件夹。')
    return lookup


class StableLogs:
    """Report every changed file once, after its size and timestamp settle."""
    def __init__(self, folder, suffix):
        self.folder, self.suffix = Path(folder), suffix
        self.previous = self.scan()
        self.delivered = self.previous.copy()

    def scan(self):
        entries = {}
        for path in self.folder.iterdir():
            if path.name.lower().endswith(self.suffix) and path.is_file():
                try:
                    st = path.stat()
                except FileNotFoundError:
                    continue
                entries[path] = (st.st_size, st.st_mtime_ns)
        return entries

    def ready(self):
        current = self.scan()
        ready = [p for p, stamp in current.items() if stamp[0] and
                 self.previous.get(p) == stamp and self.delivered.get(p) != stamp]
        self.delivered = {p: v for p, v in self.delivered.items() if p in current}
        self.delivered.update((p, current[p]) for p in ready)
        self.previous = current
        return sorted(ready, key=lambda p: p.name)


class DesktopSignals(QObject):
    notice = Signal(dict)
    result = Signal(object, object)
    error = Signal(str, str)
    finished = Signal()
    readyFiles = Signal(int, object)
    watchError = Signal(int, str)
    service = Signal(object)
    step = Signal(str)


class DesktopWindow(QMainWindow):
    batchFinished = Signal()

    def __init__(self, config, parent=None, *, services=True, session=None):
        super().__init__(parent)
        self.config = config
        self.services = services
        self.signals = DesktopSignals()
        self.session = session or ReplaySession()
        self.session.notice = self.signals.notice.emit
        self.results = []
        self.paths = []
        self.dialogs = {}
        self.failures = []
        self.pending = []
        self.busy = False
        self.cancel = threading.Event()
        self.session.cancel_requested = lambda: False
        self.watch_stop = None
        self.watch_generation = 0
        self.closing = False
        self.announcement = ANNOUNCEMENT
        self.update_url = ''
        self.logs_url = None
        self.rates = None
        self._build()
        for signal, slot in ((self.signals.notice, self._notice),
                             (self.signals.result, self._result),
                             (self.signals.error, self._error),
                             (self.signals.finished, self._finished),
                             (self.signals.readyFiles, self._watch_files),
                             (self.signals.watchError, self._watch_error),
                             (self.signals.service, self._service),
                             (self.signals.step, self.status_label.setText)):
            signal.connect(slot, Qt.ConnectionType.QueuedConnection)
        if services:
            QTimer.singleShot(0, self._start_services)

    def _button(self, label, action, role=''):
        button = QPushButton(label)
        button.setObjectName(role)
        button.clicked.connect(action)
        return button

    def _build(self):
        self.setWindowTitle('剑三警长 · 战斗复盘')
        self.resize(1080, 700)
        body = QWidget()
        body.setObjectName('workspace')
        self.setCentralWidget(body)
        columns = QHBoxLayout(body)
        columns.setContentsMargins(0, 0, 0, 0)
        columns.setSpacing(0)
        rail = QWidget()
        rail.setObjectName('rail')
        self.rail = rail
        rail.setMinimumWidth(136)
        sidebar = QVBoxLayout(rail)
        sidebar.setContentsMargins(14, 28, 14, 16)
        brand = QLabel('剑三警长')
        brand.setObjectName('brand')
        sidebar.addWidget(brand)
        version = QLabel('9.0 界面预览')
        version.setObjectName('version')
        sidebar.addWidget(version)
        sidebar.addSpacing(25)
        self.nav = []
        for index, name in enumerate(('战斗记录', '团队总结')):
            btn = self._button(name, lambda checked=False, i=index: self._page(i), 'nav')
            btn.setCheckable(True)
            sidebar.addWidget(btn)
            self.nav.append(btn)
        sidebar.addStretch()
        self.settings_btn = self._button('设置', self.settings, 'nav')
        sidebar.addWidget(self.settings_btn)
        sidebar.addWidget(self._button('公告与更新', self.announce, 'nav'))
        sidebar.addWidget(self._button('在线排行榜 ↗', self.open_logs, 'nav'))
        columns.addWidget(rail)
        content = QVBoxLayout()
        content.setContentsMargins(22, 18, 22, 14)
        content.setSpacing(12)
        columns.addLayout(content, 1)
        self.title = QLabel()
        self.title.setObjectName('heading')
        content.addWidget(self.title)
        self.pages = QStackedWidget()
        content.addWidget(self.pages, 1)
        history = QWidget()
        hist = QVBoxLayout(history)
        hist.setContentsMargins(0, 0, 0, 0)
        self.toolbar = QGridLayout()
        self.import_btn = self._button('导入日志…', self.choose_files, 'primary')
        self.auto_btn = self._button('分析最近副本', self.latest)
        self.watch_btn = self._button('开始监听', self.toggle_watch)
        self.cancel_btn = self._button('停止分析', self.cancel_batch)
        self.cancel_btn.setEnabled(False)
        self.compact = None
        self._arrange_toolbar()
        hist.addLayout(self.toolbar)
        self.record_stack = QStackedWidget()
        self.empty = QLabel('尚无战斗记录\n\n导入已有日志，或开启监听以分析新战斗。')
        self.empty.setObjectName('muted')
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.record_stack.addWidget(self.empty)
        self.history = table(('开战时间（本机）', '首领', '地图', '结果', '时长', '人数'))
        self.history.horizontalHeader().setStretchLastSection(False)
        self.history.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.history.cellDoubleClicked.connect(lambda row, col: self.open_result(row))
        self.record_stack.addWidget(self.history)
        hist.addWidget(self.record_stack, 1)
        actions = QHBoxLayout()
        self.detail_btn = self._button('打开选中战斗', self.open_selected)
        self.detail_btn.setEnabled(False)
        actions.addWidget(self.detail_btn)
        actions.addStretch()
        self.upload_btn = self._button('上传待传记录', self.upload)
        actions.addWidget(self.upload_btn)
        hist.addLayout(actions)
        self.pages.addWidget(history)
        summary = QWidget()
        layout = QVBoxLayout(summary)
        layout.setContentsMargins(0, 0, 0, 0)
        self.summary = table(('角色', '参与场次', '正分', '负分', '战斗记录'))
        self.summary.cellDoubleClicked.connect(self.summary_detail)
        layout.addWidget(self.summary)
        self.pages.addWidget(summary)
        self.status_label = QLabel('就绪')
        self.status_label.setWordWrap(True)
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        content.addWidget(self.status_label)
        bottom = QHBoxLayout()
        self.online_label = QLabel()
        self.online_label.setObjectName('muted')
        bottom.addWidget(self.online_label)
        bottom.addStretch()
        self.error_btn = self._button('查看错误', self.show_errors)
        self.error_btn.hide()
        bottom.addWidget(self.error_btn)
        content.addLayout(bottom)
        self._page(0)
        self._upload_state()
        shortcut = QAction('导入日志', self)
        shortcut.setShortcut('Ctrl+O')
        shortcut.triggered.connect(self.choose_files)
        self.addAction(shortcut)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'cancel_btn'):
            self._arrange_toolbar()

    def _arrange_toolbar(self):
        compact = self.width() < 805
        if self.compact == compact:
            return
        self.compact = compact
        buttons = (self.import_btn, self.auto_btn, self.watch_btn, self.cancel_btn)
        for button in buttons:
            self.toolbar.removeWidget(button)
        columns = 2 if compact else 4
        for i, button in enumerate(buttons):
            self.toolbar.addWidget(button, i // columns, i % columns)
        self.toolbar.setColumnStretch(4, 0 if compact else 1)

    def _page(self, index):
        self.pages.setCurrentIndex(index)
        self.title.setText(('战斗记录', '团队总结')[index])
        for i, btn in enumerate(self.nav):
            btn.setChecked(i == index)
        if index == 1:
            self.refresh_summary()

    def choose_files(self):
        folder = self.config.item['general'].get('basepath', '')
        files, _ = QFileDialog.getOpenFileNames(self, '导入战斗记录', folder,
                    '战斗记录 (*.jcl *.fstt.jx3dat);;所有文件 (*)')
        if files:
            self.enqueue_files(files)

    def latest(self):
        def discover():
            lookup = log_folder(self.config)
            final, attempts, _ = lookup.getLocalFile()
            files = attempts if self.config.item['actor'].get('checkall') else final
            self._analyse([Path(lookup.basepath) / item[0] for item in files])
        self._start(discover)

    def enqueue_files(self, files):
        paths = sorted(dict.fromkeys(Path(p).resolve() for p in files), key=lambda p: (p.name, str(p)))
        if not paths:
            return
        if self.busy:
            if not self.cancel.is_set():
                self.pending.extend(p for p in paths if p not in self.pending)
            return
        self._start(lambda: self._analyse(paths))

    def _start(self, work):
        if self.busy or self.closing:
            return
        self.cancel.clear()
        self.busy = True
        self.failures_at_start = len(self.failures)
        rates = self.rates
        self.auto_btn.setEnabled(False)
        self.settings_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.upload_btn.setEnabled(False)
        self.status_label.setText('准备中…')
        def run_work():
            try:
                if self.services and rates is None:
                    from tools.Preload import read_rate_cache
                    self.session.stat_percent = read_rate_cache()[1]
                else:
                    self.session.stat_percent = rates or {}
                work()
            except Exception as exc:
                self.signals.error.emit('任务', str(exc))
            finally:
                self.signals.finished.emit()
        threading.Thread(target=run_work, name='replay-analysis', daemon=True).start()

    def _analyse(self, paths):
        for number, path in enumerate(paths, 1):
            if self.cancel.is_set():
                break
            self.signals.step.emit(f'正在分析 {number} / {len(paths)} · {path.name}')
            try:
                self.session.cancel_requested = self.cancel.is_set
                try:
                    actor = self.session.analyse(path, self.config)
                finally:
                    self.session.cancel_requested = lambda: False
                if actor is None:
                    self.signals.step.emit('已保留分段，等待后续战斗记录。')
                    continue
                snapshot = display_result(actor)
                del actor
                if self.services and self.config.item['general'].get('autoupload', 1):
                    try:
                        self._upload()
                    except Exception as exc:
                        self.signals.error.emit('上传', str(exc))
                self.signals.result.emit(path, snapshot)
            except AnalysisCancelled:
                break
            except Exception as exc:
                self.signals.error.emit(path.name, str(exc))

    def _upload(self):
        if not self.session.uploadData:
            return
        from ConfigTools import ensure_user_uuid
        uuid = ensure_user_uuid(self.config)
        for item in self.session.uploadData:
            if not item['data'].get('userid'):
                item['data']['userid'] = uuid
        self.session.executeUploadData()
        if self.session.uploadData:
            raise RuntimeError("待上传记录已保留，可在网络恢复后重试。")

    def upload(self):
        if self.services:
            self._start(self._upload)

    def _upload_state(self):
        enabled = self.services and bool(self.config.item['general'].get('autoupload', 1))
        count = len(self.session.uploadData)
        self.online_label.setText(f'自动上传{"已开启" if enabled else "已关闭"}   ·   {count} 份待传记录')
        self.upload_btn.setEnabled(self.services and not self.busy and count > 0)

    def _notice(self, update):
        parts = [str(update[k]) for k in ('t1', 't2') if update.get(k)]
        if parts:
            self.status_label.setText('  '.join(parts))

    def _result(self, path, result):
        if path in self.paths:
            index = self.paths.index(path)
            previous = self.results[index]
            if index in self.dialogs:
                self.dialogs[index].close()
            if (previous.timestamp, previous.server, previous.bossAnalyseName) == (
                    result.timestamp, result.server, result.bossAnalyseName):
                scores = defaultdict(deque)
                manual = []
                for pot in previous.potList:
                    if str(pot[4]).startswith('[手动] '):
                        manual.append(list(pot))
                    elif len(pot) >= 7:
                        scores[json.dumps(pot[:6], ensure_ascii=False, sort_keys=True)].append(pot[6])
                for pot in result.potList:
                    key = json.dumps(pot[:6], ensure_ascii=False, sort_keys=True)
                    if scores[key]:
                        pot[6] = scores[key].popleft()
                result.potList.extend(manual)
            self.results[index] = result
        else:
            index = len(self.results)
            self.paths.append(path)
            self.results.append(result)
        seconds = int(round(result.battleTime)) // 1000
        set_row(self.history, index, (time.strftime('%m-%d %H:%M', time.localtime(result.timestamp)),
                result.bossAnalyseName, result.mapDetail, '通关' if result.win else '未通关',
                f'{seconds//60}:{seconds%60:02}', len(result.statDict)))
        self.record_stack.setCurrentWidget(self.history)
        self.history.selectRow(index)
        self.detail_btn.setEnabled(True)
        if self.pages.currentIndex() == 1:
            self.refresh_summary()

    def _error(self, source, message):
        self.failures.append((source, message))
        self.error_btn.setText(f'查看错误（{len(self.failures)}）')
        self.error_btn.show()
        self.status_label.setText(f'{source} · {message}')

    def show_errors(self):
        box = QMessageBox(self)
        box.setWindowTitle('任务错误')
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.setText('\n\n'.join(f'{source}\n{message}' for source, message in self.failures[-15:]))
        box.exec()

    def _finished(self):
        self.busy = False
        self.auto_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._upload_state()
        for dialog in self.dialogs.values():
            from window.QtResults import BattleView
            view = dialog.findChild(BattleView)
            if view is not None:
                view.refresh_links()
        if self.closing:
            self.close()
            return
        if self.pending and not self.cancel.is_set():
            paths, self.pending = self.pending, []
            self.enqueue_files(paths)
            return
        errors = len(self.failures) - self.failures_at_start
        state = '已停止后续分析' if self.cancel.is_set() else '就绪'
        if errors:
            state += f'，本批有 {errors} 项错误'
        self.status_label.setText(f'本次会话共 {len(self.results)} 场战斗 · {state}')
        self.batchFinished.emit()

    def cancel_batch(self):
        self.cancel.set()
        self.pending.clear()
        self.status_label.setText('正在停止分析，等待当前步骤结束…')

    def toggle_watch(self):
        if self.watch_stop is not None:
            self._stop_watch()
            self.status_label.setText('已停止监听。')
            return
        stop = self.watch_stop = threading.Event()
        self.watch_generation += 1
        generation = self.watch_generation
        config = self.config
        self.watch_btn.setText('停止监听')
        self.status_label.setText('正在监听新战斗记录…')
        def listen():
            try:
                lookup = log_folder(config)
                suffix = '.jcl' if lookup.dataType == 'jcl' else '.fstt.jx3dat'
                watcher = StableLogs(lookup.basepath, suffix)
                while not stop.wait(1.5):
                    files = watcher.ready()
                    if files:
                        self.signals.readyFiles.emit(generation, files)
            except Exception as exc:
                if not stop.is_set():
                    self.signals.watchError.emit(generation, str(exc))
        threading.Thread(target=listen, name='log-monitor', daemon=True).start()

    def _watch_files(self, generation, paths):
        if generation == self.watch_generation and self.watch_stop and not self.closing:
            self.enqueue_files(paths)

    def _watch_error(self, generation, message):
        if generation == self.watch_generation:
            self._stop_watch()
            self._error('实时监听', message)

    def _stop_watch(self):
        if self.watch_stop is not None:
            self.watch_stop.set()
        self.watch_stop = None
        self.watch_generation += 1
        self.watch_btn.setText('开始监听')

    def open_selected(self):
        self.open_result(self.history.currentRow())

    def open_result(self, index):
        if not 0 <= index < len(self.results):
            return
        if index in self.dialogs:
            self.dialogs[index].raise_()
            self.dialogs[index].activateWindow()
            return self.dialogs[index]
        from window.QtResults import BattleView
        result = self.results[index]
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if self.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen):
            dialog.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        dialog.setWindowTitle(f'{result.bossAnalyseName} · {result.mapDetail}')
        dialog.resize(1080, 760)
        layout = QVBoxLayout(dialog)
        view = BattleView(result, dialog)
        layout.addWidget(view)
        dialog.finished.connect(lambda _: self._close_result(index, dialog))
        self.dialogs[index] = dialog
        dialog.show()
        return dialog

    def _close_result(self, index, dialog):
        if self.dialogs.get(index) is dialog:
            self.dialogs.pop(index)
        self.refresh_summary()

    def refresh_summary(self):
        people = {}
        for index, result in enumerate(self.results):
            for row in result.statDict:
                name = row['name'].strip('"')
                key = (result.server, name)
                person = people.setdefault(key, [[], 0, 0, [], False])
                person[0].append(index)
                person[4] |= bool(result.mask)
            for pot in result.potList:
                if len(pot) < 7:
                    continue
                key = (result.server, str(pot[0]).strip('"'))
                if key in people:
                    score = int(pot[6])
                    people[key][1] += max(0, score)
                    people[key][2] += min(0, score)
                    people[key][3].append(str(pot[4]))
        self.members = []
        self.summary.setRowCount(0)
        for i, ((_, name), (indices, plus, minus, notes, masked)) in enumerate(people.items()):
            label = f'队员{i + 1:02}' if masked and name else name
            self.members.append(indices)
            set_row(self.summary, i, (label, len(indices), plus, minus,
                    '、'.join(self.results[j].bossAnalyseName for j in indices)))
            if notes and not masked:
                self.summary.item(i, 0).setToolTip('\n'.join(notes))

    def summary_detail(self, row, col):
        if row < 0 or row >= len(self.members):
            return
        menu = QDialog(self)
        menu.setWindowTitle('参与的战斗')
        layout = QVBoxLayout(menu)
        choices = table(('首领', '开战时间', '地图'))
        indices = self.members[row]
        for i, idx in enumerate(indices):
            battle = self.results[idx]
            set_row(choices, i, (battle.bossAnalyseName,
                    time.strftime('%m-%d %H:%M', time.localtime(battle.timestamp)), battle.mapDetail))
        choices.selectRow(0)
        choices.cellDoubleClicked.connect(lambda *_: menu.accept())
        layout.addWidget(choices)
        layout.addWidget(self._button('打开战斗', menu.accept))
        menu.resize(520, 340)
        if menu.exec() == QDialog.DialogCode.Accepted and choices.currentRow() >= 0:
            self.open_result(indices[choices.currentRow()])

    def settings(self):
        from window.QtSettings import SettingsDialog
        if SettingsDialog(self.config, self).exec() == QDialog.DialogCode.Accepted:
            if self.watch_stop is not None:
                self._stop_watch()
                self.toggle_watch()
            self._upload_state()

    def _start_services(self):
        signals = self.signals
        def load():
            from tools.Preload import checkRateEdition, read_rate_cache
            try:
                _, cached = read_rate_cache()
                signals.service.emit({'rates': cached})
                with urllib.request.urlopen(get_api_url('/getAnnouncement', {'edition': EDITION}),
                                            timeout=6) as response:
                    announcement = json.load(response)
                signals.service.emit({'announcement': announcement, 'logs_url': get_logs_url('/')})
                rates = checkRateEdition(announcement['rateEdition'])
                signals.service.emit({'rates': rates})
            except (OSError, ValueError, KeyError, TypeError):
                return
        threading.Thread(target=load, name='replay-metadata', daemon=True).start()

    def _service(self, payload):
        if 'rates' in payload:
            self.rates = payload['rates']
        if 'announcement' in payload:
            from tools.Functions import parseEdition
            data = payload['announcement']
            self.announcement = data.get('announcement', ANNOUNCEMENT)
            if parseEdition(data.get('version','0')) > parseEdition(EDITION):
                self.update_url = data.get('url', '')
        if 'logs_url' in payload:
            self.logs_url = payload['logs_url']

    def announce(self):
        from window.QtSettings import AnnounceDialog, LicenseDialog
        dialog = AnnounceDialog(self.announcement, self)
        dialog.layout().addWidget(self._button('查看使用协议',
                                  lambda: LicenseDialog(dialog, read_only=True).exec()))
        if self.update_url and QUrl(self.update_url).scheme() in ('http','https'):
            dialog.layout().addWidget(self._button('打开更新下载页',
                                      lambda: QDesktopServices.openUrl(QUrl(self.update_url))))
        dialog.exec()

    def open_logs(self):
        from ServerAddress import FALLBACK_ADDRESS
        url = self.logs_url or 'https://' + FALLBACK_ADDRESS['logs']['host'] + '/'
        QDesktopServices.openUrl(QUrl(url))

    def closeEvent(self, event):
        if self.busy:
            if not self.closing and QMessageBox.question(self, '退出剑三警长',
                    '当前任务结束后退出？后续排队的战斗将停止分析。') == QMessageBox.StandardButton.Yes:
                self.closing = True
                self._stop_watch()
                self.cancel_batch()
            event.ignore()
            return
        self._stop_watch()
        event.accept()


def run():
    import sys
    from window.QtSettings import LicenseDialog, load_desktop_config
    app = QApplication.instance() or QApplication(sys.argv)
    configure_application(app)
    config_path = Path(get_writable_path('config.ini'))
    if not config_path.is_file():
        if LicenseDialog().exec() != QDialog.DialogCode.Accepted:
            return 0
    try:
        config = load_desktop_config(config_path)
    except (OSError, ValueError) as exc:
        QMessageBox.critical(None, '无法读取配置', str(exc))
        return 1
    window = DesktopWindow(config)
    window.show()
    return app.exec()

"""Qt dialogs for local analysis preferences, account operations and desktop help."""
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QUrl, Signal, Slot, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox,
    QStackedWidget, QTabWidget, QTextBrowser, QVBoxLayout, QWidget,
)

from ConfigTools import Config, ensure_user_uuid
from Constants import get_api_url
from window.LicenseText import LICENSE_TEXT


HEALERS = (("xiangzhi", "相知"), ("lingsu", "灵素"), ("lijing", "离经易道"),
           ("butian", "补天诀"), ("yunchang", "云裳心经"))
LINKS = (("复盘指南", "https://www.jx3box.com/bps/31349"),
         ("帮助文档", "https://wwe.lanzouy.com/iKY8Ayggt4j"),
         ("更新记录", "https://github.com/moeheart/jx3bla/blob/master/update.md"))


def load_desktop_config(path):
    """Load offline, creating defaults only after the caller obtained first-use consent."""
    path = Path(path)
    config = Config(path, offline=True)
    if not path.exists():
        config.printSettings()
    return config


def _account_request(endpoint, **fields):
    data = urlencode(fields).encode("utf-8")
    with urlopen(get_api_url(endpoint), data=data, timeout=10) as response:
        return json.load(response)


class _Signals(QObject):
    completed = Signal(str, object, str)


class _Job(QRunnable):
    def __init__(self, name, work):
        super().__init__()
        self.name = name
        self.work = work
        self.signals = _Signals()

    def run(self):
        try:
            value = self.work()
        except Exception as error:
            self.signals.completed.emit(self.name, None, str(error))
        else:
            self.signals.completed.emit(self.name, value, "")


def _button(text, callback):
    button = QPushButton(text)
    button.setAutoDefault(False)
    button.clicked.connect(callback)
    return button


def _row(*widgets):
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    for widget in widgets:
        layout.addWidget(widget)
    return row


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(640, 535)
        self.config = config
        self.fields = {}
        self.jobs = {}
        self._closed = False
        self._account_loaded = False
        self._invalid_uuid = None
        self._saving_account = False
        self._registered_name = None
        self.tabs = QTabWidget()
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(self.status)
        layout.addWidget(self.buttons)
        self._general()
        self._actor()
        self._healers()
        self._user()
        self.tabs.currentChanged.connect(self._tab_changed)
        self.finished.connect(self._finished)
        self._initial = {key: read() for key, read in self.fields.items()}

    def _page(self, title):
        body = QWidget()
        form = QFormLayout(body)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        self.tabs.addTab(scroll, title)
        return form

    def _text(self, section, key):
        entry = QLineEdit(str(self.config.item[section][key]))
        entry.setObjectName(section + "." + key)
        self.fields[section, key] = entry.text
        return entry

    def _check(self, form, section, key, text):
        box = QCheckBox(text)
        box.setObjectName(section + "." + key)
        box.setChecked(bool(self.config.item[section][key]))
        self.fields[section, key] = lambda: int(box.isChecked())
        form.addRow(box)

    def _number(self, form, section, key, label):
        box = QSpinBox()
        box.setRange(0, 2147483647)
        box.setValue(int(self.config.item[section][key]))
        box.setObjectName(section + "." + key)
        self.fields[section, key] = box.value
        form.addRow(label, box)

    def _choice(self, form, section, key, label, choices):
        combo = QComboBox()
        for name, value in choices:
            combo.addItem(name, value)
        combo.setCurrentIndex(max(0, combo.findData(self.config.item[section][key])))
        combo.setObjectName(section + "." + key)
        self.fields[section, key] = combo.currentData
        form.addRow(label, combo)
        return combo

    def _general(self):
        form = self._page("日志与上传")
        self.game_path = self._text("general", "jx3path")
        form.addRow("正式服目录", _row(self.game_path, _button("选择…", lambda: self._browse(self.game_path))))
        self.datatype = self._choice(form, "general", "datatype", "日志格式",
                                     [("JCL", "jcl"), ("JX3DAT（历史明文格式）", "jx3dat")])
        form.addRow("团队名", self._text("general", "team"))
        for key, label in (("autoupload", "分析后自动上传"), ("mask", "名称打码"),
                           ("color", "门派染色"), ("text", "保存文本结果"), ("trivia", "生成摘要统计")):
            self._check(form, "general", key, label)

    def _actor(self):
        form = self._page("团队复盘")
        self._check(form, "actor", "active", "启用团队复盘")
        self._number(form, "actor", "failthreshold", "拉脱末尾无效秒数")
        entry = self._text("actor", "filter")
        entry.setPlaceholderText("s6746,b17933,b6131")
        form.addRow("时间轴过滤列表", entry)

    def _healers(self):
        form = self._page("治疗复盘")
        selector = QComboBox()
        pages = QStackedWidget()
        for group, label in HEALERS:
            selector.addItem(label)
            page = QWidget()
            details = QFormLayout(page)
            self._check(details, group, "active", "启用此心法复盘")
            self._number(details, group, "speed", "手动加速等级")
            self._check(details, group, "speedforce", "始终使用手动加速")
            self._check(details, group, "public", "公开此心法的个人复盘")
            self._choice(details, group, "stack", "相同技能堆叠阈值",
                         [("连续 2 次", "2"), ("连续 3 次", "3"), ("不堆叠", "不堆叠")])
            if group == "xiangzhi":
                self._check(details, group, "caltank", "统计坦克心法覆盖率")
            pages.addWidget(page)
        selector.currentIndexChanged.connect(pages.setCurrentIndex)
        form.addRow("治疗心法", selector)
        form.addRow(pages)
        self.public_id = QLineEdit()
        self.public_id.setPlaceholderText("公开复盘编号或哈希")
        form.addRow("在线复盘", _row(self.public_id, _button("打开", self._open_replay)))

    def _user(self):
        form = self._page("用户")
        self.account_tab = self.tabs.count() - 1
        self.uuid_label = QLabel(self.config.userUuid or "尚未创建")
        self.uuid_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow("用户标识", self.uuid_label)
        self.username = QLineEdit(self.config.userId)
        self.username.setReadOnly(bool(self.config.userId))
        if not self.config.userId:
            self.username.setPlaceholderText("保存时向服务器绑定用户名")
        form.addRow("用户名", self.username)
        self.make_uuid = QCheckBox("保存时创建联网用户标识")
        self.make_uuid.setVisible(not bool(self.config.userUuid))
        form.addRow(self.make_uuid)
        self.refresh = _button("刷新用户信息", self._refresh_user)
        self.refresh.setEnabled(bool(self.config.userUuid))
        form.addRow(self.refresh)
        self.user_status = QLabel()
        self.user_status.setWordWrap(True)
        self.user_status.setTextFormat(Qt.TextFormat.PlainText)
        form.addRow(self.user_status)

    def _browse(self, entry):
        path = QFileDialog.getExistingDirectory(self, "选择目录", entry.text())
        if path:
            entry.setText(path)

    def _open_replay(self):
        replay = self.public_id.text().strip()
        if not replay or not replay.isascii() or not replay.isalnum():
            self.status.setText("请填写有效的复盘编号或哈希。")
            return
        self._start("url", lambda: get_api_url("/showReplayPro.html", {"id": replay}),
                    lambda url: QDesktopServices.openUrl(QUrl(url)))

    def _tab_changed(self, index):
        if index == self.account_tab and self.config.userUuid and not self._account_loaded:
            self._refresh_user()

    def _refresh_user(self):
        identifier = self.config.userUuid
        if not identifier:
            return
        self.user_status.setText("正在读取用户信息…")
        self._start("account", lambda: _account_request("/getUserInfo", uuid=identifier), self._display_user)

    def _display_user(self, data):
        if not data.get("exist"):
            self._invalid_uuid = self.config.userUuid
            self.make_uuid.setText("保存时换发用户标识，并清除旧的本机绑定")
            self.make_uuid.setVisible(True)
            self.user_status.setText("服务端未找到这个用户标识。可以换发，或保留配置并稍后重试。")
            return
        self._invalid_uuid = None
        self.make_uuid.setChecked(False)
        self.make_uuid.setVisible(False)
        self._account_loaded = True
        self.user_status.setText("用户标识有效。")

    def _start(self, name, work, callback):
        if name in self.jobs:
            return
        job = _Job(name, work)
        self.jobs[name] = (job, callback)
        job.signals.completed.connect(self._complete)
        QThreadPool.globalInstance().start(job)

    @Slot(str, object, str)
    def _complete(self, name, data, error):
        job, callback = self.jobs.pop(name)
        if self._closed:
            return
        if name == "save_user":
            self._saving_account = False
            self.buttons.setEnabled(True)
            self.tabs.setEnabled(True)
        try:
            if error:
                raise ValueError(error)
            callback(data)
        except (KeyError, ValueError, TypeError, OSError) as exc:
            (self.user_status if name == "account" else self.status).setText(f"操作未完成：{exc}")

    def _save(self, changes):
        if changes:
            self.config.saveSettings(changes)
        super().accept()

    def accept(self):
        if self._saving_account:
            return
        changes = {}
        for (group, key), read in self.fields.items():
            value = read()
            if value != self._initial[group, key]:
                changes.setdefault(group, {})[key] = value
        name = self.username.text().strip()
        binding = name and name != self.config.userId
        invalid = self._invalid_uuid if self.make_uuid.isChecked() else None
        needs_uuid = self.make_uuid.isChecked() and (not self.config.userUuid or invalid)
        if (binding and self._registered_name != name) or needs_uuid:
            self._saving_account = True
            self.buttons.setEnabled(False)
            self.tabs.setEnabled(False)
            self.status.setText("正在保存联网用户信息…")
            def work():
                identifier = ensure_user_uuid(self.config, invalid_uuid=invalid)
                if binding:
                    response = _account_request("/setUserId", uuid=identifier, id=name)
                    result = response.get("result")
                    if result != "success":
                        raise ValueError({"dupid": "用户名已被使用。", "hasuuid": "用户标识已绑定。",
                                          "nouuid": "用户标识无效。"}.get(result, "服务器未接受绑定。"))
                return identifier
            def saved(identifier):
                self.uuid_label.setText(identifier)
                if binding:
                    self._registered_name = name
                    changes["user"] = {"id": name}
                self._save(changes)
            self._start("save_user", work, saved)
            return
        if binding and name == self._registered_name:
            changes["user"] = {"id": name}
        try:
            self._save(changes)
        except (OSError, ValueError) as exc:
            self.status.setText(f"保存失败：{exc}")

    def reject(self):
        if not self._saving_account:
            super().reject()

    def closeEvent(self, event):
        if self._saving_account:
            event.ignore()
        else:
            super().closeEvent(event)

    def _finished(self):
        self._closed = True


class LicenseDialog(QDialog):
    def __init__(self, parent=None, *, read_only=False):
        super().__init__(parent)
        self.setWindowTitle("使用协议")
        self.resize(620, 480)
        layout = QVBoxLayout(self)
        terms = QTextBrowser()
        terms.setPlainText(LICENSE_TEXT)
        layout.addWidget(terms)
        if read_only:
            close = _button("关闭", self.accept)
            layout.addWidget(close)
        else:
            agree = QCheckBox("我已阅读并同意使用协议")
            layout.addWidget(agree)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            okay = buttons.button(QDialogButtonBox.StandardButton.Ok)
            okay.setText("同意并继续")
            okay.setEnabled(False)
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("退出")
            agree.toggled.connect(okay.setEnabled)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)


class AnnounceDialog(QDialog):
    def __init__(self, announcement, parent=None):
        super().__init__(parent)
        self.setWindowTitle("公告与帮助")
        self.resize(560, 350)
        layout = QVBoxLayout(self)
        text = QTextBrowser()
        text.setPlainText(announcement)
        layout.addWidget(text)
        layout.addWidget(QLabel("反馈 QQ 群　418483739"))
        links = [_button(title, lambda checked=False, url=url: QDesktopServices.openUrl(QUrl(url)))
                 for title, url in LINKS]
        layout.addWidget(_row(*links))
        layout.addWidget(_button("关闭", self.accept))

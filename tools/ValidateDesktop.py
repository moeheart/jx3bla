"""Exercise the production Qt shell, result views and ordered real-log analysis offline."""
import argparse
import contextlib
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QTabWidget

from data.ReplaySession import ReplaySession, display_result
from window.QtDesktop import DesktopWindow, configure_application

_application = None


def application():
    global _application
    _application = QApplication.instance() or QApplication([])
    configure_application(_application)
    return _application


@contextmanager
def checked_callbacks():
    """PySide delivers exceptions from slots to sys.excepthook outside unittest."""
    errors = []
    def capture(kind, value, trace):
        errors.append(value)
    with patch.object(sys, 'excepthook', capture):
        yield
    if errors:
        raise RuntimeError('Qt callback failed') from errors[0]


def check_shell():
    from window.QtSettings import AnnounceDialog, LicenseDialog, SettingsDialog, load_desktop_config
    app = application()
    with tempfile.TemporaryDirectory() as folder, checked_callbacks():
        config = load_desktop_config(Path(folder) / 'config.ini')
        shell = DesktopWindow(config, services=False)
        shell.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        shell.show()
        shell.nav[1].click()
        assert shell.pages.currentIndex() == 1
        shell.nav[0].click()
        for dialog in (LicenseDialog(shell), SettingsDialog(config, shell), AnnounceDialog('测试公告', shell)):
            dialog.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
            dialog.show()
            app.processEvents()
            assert not dialog.grab().isNull()
            dialog.reject()
        assert shell.history.rowCount() == 0 and not shell.busy
        shell.close()
        shell.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    return {'mainWindow': 'opened', 'settings': 'opened', 'license': 'opened', 'announcement': 'opened'}


def exercise_view(view, snapshot):
    app = QApplication.instance()
    assert view.team_table.model().rowCount() == len(snapshot.statDict)
    for i in range(view.tabs.count()):
        view.tabs.setCurrentIndex(i)
    pages = 0
    for name in snapshot.occResult:
        assert view.open_player(name)
        for i in range(view.personal_tabs.count()):
            view.personal_tabs.setCurrentIndex(i)
            pages += 1
        # Release the previous player's lazily-built tables and timeline.
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    assert not view.grab().isNull()
    return {'teamRows': len(snapshot.statDict), 'battleTabs': view.tabs.count(),
            'personalReports': len(snapshot.occResult), 'personalTabsVisited': pages}


def check_result_views(actor):
    from window.QtResults import BattleView
    application()
    snapshot = display_result(actor) if hasattr(actor, 'bld') else actor
    with checked_callbacks():
        view = BattleView(snapshot)
        view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        view.resize(1000, 660)
        view.show()
        try:
            return exercise_view(view, snapshot)
        finally:
            view.close()
            view.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def verify_group(baseline, group, log_dir):
    from tools.ValidateCleanupReplays import summarize
    from tools.ValidateLuoyang import make_config
    from window.QtResults import BattleView
    cases = json.loads(baseline.read_text('utf-8'))[group]
    expected = {item['file']: item for item in cases}
    results = []

    class VerifiedSession(ReplaySession):
        def analyse(self, path, config):
            case = expected[path.name]
            with path.open('rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == case['sha256']
            start = len(self.uploadData)
            actor = super().analyse(path, config)
            assert actor is not None
            local = [dict(row, id=i) for i, row in enumerate(self.uploadData[start:])]
            actual = summarize(actor, SimpleNamespace(uploadData=local))
            diff = [key for key in actual if actual[key] != case['result'][key]]
            if diff:
                raise AssertionError(f'{path.name}: 基线差异 {", ".join(diff)}')
            results.append({'file': path.name, 'sha256': case['sha256'], 'boss': actual['boss'],
                            'win': actual['win'], 'personalUploads': actual['personalUploads']})
            return actor

    app = application()
    shell = DesktopWindow(make_config(True), services=False, session=VerifiedSession())
    shell.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    shell.show()
    loop = QEventLoop()
    shell.batchFinished.connect(loop.quit)
    pulses = []
    pulse = QTimer()
    pulse.setInterval(250)
    pulse.timeout.connect(lambda: pulses.append(True))
    pulse.start()
    try:
        with checked_callbacks():
            shell.enqueue_files([log_dir/item['file'] for item in cases])
            loop.exec()
            pulse.stop()
            assert not shell.failures, shell.failures
            assert [r['file'] for r in results] == [r['file'] for r in cases]
            assert shell.history.rowCount() == len(cases) and pulses
            for i, snapshot in enumerate(shell.results):
                dialog = shell.open_result(i)
                view = dialog.findChild(BattleView)
                results[i]['ui'] = exercise_view(view, snapshot)
                dialog.close()
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            shell.nav[1].click()
            assert shell.summary.rowCount() > 0
            app.processEvents()
            return {'group': group, 'frozen': bool(getattr(sys, 'frozen', False)),
                    'cases': results, 'eventLoopTicks':len(pulses), 'matchesBaseline':True}
    finally:
        pulse.stop()
        shell.close()
        shell.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-desktop', action='store_true')
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--group', choices=['normal', 'heroic13', 'heroic14'], required=True)
    parser.add_argument('--log-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    with patch('socket.socket.connect', side_effect=AssertionError('Network disabled')), \
            patch('urllib.request.urlopen', side_effect=AssertionError('HTTP disabled')), \
            open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink):
        result = verify_group(args.baseline, args.group, args.log_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{args.group}: {len(result['cases'])} desktop replays passed")


if __name__ == '__main__':
    main()

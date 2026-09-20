"""Exercise the release executable in an empty directory without network access."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch
from release.ReleaseResources import CANGSHENG_FILES


RESOURCE_FILES = tuple(Path(path).name for path in CANGSHENG_FILES)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-smoke-test', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with patch('socket.socket.connect', side_effect=AssertionError('Release smoke test: network disabled')):
        import ServerAddress
        ServerAddress._address_cache = copy.deepcopy(ServerAddress.FALLBACK_ADDRESS)
        from Constants import EDITION
        from equip.AttributeDisplay import AttributeDisplay
        from equip.CangshengAttributeData import RESOURCE_ROOT, kungfu_data, npc_data
        from replayer import NameCangsheng
        from GenerateFiles import checkAndWriteFiles
        from MainWindow import MainWindow
        import tkinter as tk

        frozen = bool(getattr(sys, 'frozen', False))
        if frozen:
            assert RESOURCE_ROOT.resolve().is_relative_to(Path(sys._MEIPASS).resolve())
        resources = {}
        for name in RESOURCE_FILES:
            path = RESOURCE_ROOT / name
            data = path.read_bytes()
            resources[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        display = AttributeDisplay(gameEdition=160)
        assert display.status['status'] == 'supported', display.status
        assert len(kungfu_data()['occupations']) == 31
        assert npc_data()['profiles']
        for buff_id, value in ((29294, 7), (20938, 7), (23543, 7), (20854, 8)):
            assert NameCangsheng.BOOST_DICT['2,%s,1' % buff_id]['atStrainBase'] == value
        for level, value in zip(range(18, 23), range(15, 20)):
            assert NameCangsheng.BOOST_DICT['2,29608,%s' % level]['atStrainBase'] == value
        checkAndWriteFiles()
        application = MainWindow()
        assert application.uploadData == []
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
        result = {'version': EDITION, 'frozen': frozen, 'network': 'disabled',
                  'upload': 'disabled', 'resources': resources, 'attributeStatus': display.status,
                  'kungfus': 31, 'npcProfiles': len(npc_data()['profiles']),
                  'buffChecks': 'passed', 'tk': 'constructed',
                  'mainWindow': 'initialized', 'status': 'passed'}
        if args.manifest:
            from tools.ValidateLuoyangRdps import main as validate_rdps
            output = report_path.parent / 'rdps'
            argv = ['ValidateLuoyangRdps', '--manifest', str(args.manifest.resolve()),
                    '--output', str(output), '--healers', '--ui']
            with patch.object(sys, 'argv', argv):
                validate_rdps()
            result['replayReport'] = str(output / 'clear-rdps.json')
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Release smoke test passed: ' + str(report_path))


if __name__ == '__main__':
    main()

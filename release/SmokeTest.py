"""Exercise the release executable in an empty directory without network access."""
import argparse
import copy
import contextlib
import hashlib
import io
import json
import math
from io import BytesIO
from pathlib import Path
import sys
from unittest.mock import patch
from release.ReleaseResources import CANGSHENG_FILES


RESOURCE_FILES = tuple(Path(path).name for path in CANGSHENG_FILES)


def check_excel():
    """Exercise the existing spreadsheet support with standard Python values."""
    from openpyxl import Workbook, load_workbook
    from openpyxl.compat.numbers import NUMPY

    if getattr(sys, "frozen", False):
        assert not NUMPY, "The frozen client must use openpyxl's NumPy-free path"
    with BytesIO() as stream:
        workbook = Workbook()
        workbook.active.append(["装备", 160, 1.25, "=B1+C1"])
        workbook.save(stream)
        workbook.close()
        stream.seek(0)
        restored = load_workbook(stream)
        try:
            assert [cell.value for cell in restored.active[1]] == ["装备", 160, 1.25, "=B1+C1"]
        finally:
            restored.close()
    return {"roundTrip": "passed", "numpyAvailable": NUMPY}


def check_icons(root):
    """Decode generated PNG/ICO assets and exercise the Pillow/Tk bridge."""
    from PIL import Image, ImageTk
    from tools.ResourcePath import get_icon_path

    result = {}
    for icon_id, suffix in (("10442", "png"), ("jx3bla", "ico")):
        with Image.open(get_icon_path(icon_id, suffix)) as icon:
            icon.load()
            photo = ImageTk.PhotoImage(icon.resize((20, 20), Image.Resampling.LANCZOS), master=root)
            assert (photo.width(), photo.height()) == (20, 20)
            result[suffix] = {"format": icon.format, "tk": "passed"}
    return result



def check_damage_conservation(tracker):
    """Compare raw damage for the player casters handled by rDPS attribution."""
    # ndpsCast also contains NPC-to-NPC damage, which has no BoostCounter and
    # does not enter rDPS. Credited players can have different adjusted times,
    # so the sum of their displayed DPS rates is not a conserved quantity.
    eligible = tracker.boostCounter
    excluded = {caster: recorder.sum for caster, recorder in tracker.ndpsCast.items()
                if caster not in eligible and recorder.sum}
    assert all(caster in tracker.info.npc for caster in excluded), excluded
    result = {
        'directDamage': math.fsum(recorder.sum for caster, recorder in tracker.ndpsCast.items()
                                  if caster in eligible),
        'redistributedDamage': math.fsum(recorder.sum for recorder in tracker.rdpsCast.values()),
        'mainTargetDamage': math.fsum(recorder.sum for recorder in tracker.mndpsCast.values()),
        'redistributedMainTargetDamage': math.fsum(recorder.sum for recorder in tracker.mrdpsCast.values()),
        'excludedNpcDamage': math.fsum(excluded.values()),
    }
    assert all(math.isfinite(value) and value >= 0 for value in result.values()), result
    for direct, redistributed in (('directDamage', 'redistributedDamage'),
                                  ('mainTargetDamage', 'redistributedMainTargetDamage')):
        assert math.isclose(result[direct], result[redistributed], rel_tol=0, abs_tol=0.001), result
    result['conservationError'] = result['redistributedDamage'] - result['directDamage']
    result['mainTargetConservationError'] = result['redistributedMainTargetDamage'] - result['mainTargetDamage']
    return result


def check_replays(entries, report_path):
    """Exercise supplied current-season logs without enforcing a date boundary."""
    from tools.ValidateLuoyang import ValidationWindow, replay, check_windows
    from tools.Attribute import CURRENT_GAME_EDITION

    results = []
    for entry in entries:
        path = Path(entry['source'])
        print('Release replay: ' + path.name, flush=True)
        if entry.get('sha256'):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'].lower()
        with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), \
                patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'), \
                contextlib.redirect_stdout(io.StringIO()):
            actor = replay(path, ValidationWindow(), healers=True)
            assert actor.battleTime > 0 and actor.statDict
            tracker = actor.combatTracker
            assert tracker.rdpsStatus['gameEdition'] == CURRENT_GAME_EDITION
            totals = {name: getattr(tracker, name)['sum']
                      for name in ('ndps', 'mndps', 'rdps', 'mrdps', 'hps', 'ahps', 'rhps')}
            assert all(math.isfinite(value) and value >= 0 for value in totals.values())
            damage = check_damage_conservation(tracker)
            check_windows(actor)
        results.append({'file': path.name, 'boss': actor.bossAnalyseName,
                        'players': len(actor.statDict), 'specializationReplays': len(actor.occResult),
                        'seconds': actor.battleTime / 1000,
                        'attributeStatus': actor.detail.get('attributeStatus'),
                        'rdpsStatus': tracker.rdpsStatus, 'totals': totals,
                        'damage': damage, 'ui': 'constructed'})
        report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return str(report_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-smoke-test', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--wujie-log', type=Path)
    args = parser.parse_args()
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with patch('socket.socket.connect', side_effect=AssertionError('Release smoke test: network disabled')):
        import ServerAddress
        ServerAddress._address_cache = copy.deepcopy(ServerAddress.FALLBACK_ADDRESS)
        from Constants import EDITION
        from equip.AttributeDisplay import AttributeDisplay
        from equip.CangshengAttributeData import RESOURCE_ROOT, kungfu_data, npc_data
        from replayer import Name
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
        display = AttributeDisplay()
        assert display.status['status'] == 'supported', display.status
        profiles = kungfu_data()['occupations']
        assert len(profiles) == 64
        from tools.Functions import getOccDetailFromXinfaCode
        for occ in ('24w', '2hw', '10tw', '34w'):
            assert occ in profiles and profiles[occ]['raw_attributes']
            assert getOccDetailFromXinfaCode(str(profiles[occ]['skill_id'])) == occ
        assert npc_data()['profiles']
        for buff_id, value in ((29294, 7), (20938, 7), (23543, 7), (20854, 10), (24742, 26)):
            assert Name.BOOST_DICT['2,%s,1' % buff_id]['atStrainBase'] == value
        for level, value in zip(range(18, 23), (20, 22, 25, 27, 29)):
            assert Name.BOOST_DICT['2,29608,%s' % level]['atStrainBase'] == value
        checkAndWriteFiles()
        application = MainWindow()
        assert application.uploadData == []
        root = tk.Tk()
        root.withdraw()
        try:
            icon_checks = check_icons(root)
            root.update_idletasks()
        finally:
            root.destroy()
        excel_checks = check_excel()
        result = {'version': EDITION, 'frozen': frozen, 'network': 'disabled',
                  'upload': 'disabled', 'resources': resources, 'attributeStatus': display.status,
                  'kungfus': len(profiles), 'npcProfiles': len(npc_data()['profiles']),
                  'buffChecks': 'passed', 'tk': 'constructed',
                  'mainWindow': 'initialized', 'icons': icon_checks, 'excel': excel_checks,
                  'status': 'passed'}
        if args.manifest:
            entries = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
            result['replayReport'] = check_replays(entries, report_path.parent / 'replays.json')
        if args.wujie_log:
            result['wujieReport'] = check_replays([{'source': str(args.wujie_log.resolve())}],
                                                report_path.parent / 'wujie-report.json')
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Release smoke test passed: ' + str(report_path))


if __name__ == '__main__':
    main()

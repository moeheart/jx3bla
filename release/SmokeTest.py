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
from types import SimpleNamespace
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


def capture_uploads(window):
    """Use the real prepareUpload methods with a local-only queue sink."""
    def collect(data):
        data["id"] = len(window.uploadData)
        window.uploadData.append(data)
    window.addUploadData = collect
    return window


def check_upload_payloads(window, actor):
    """Check the actual combined-upload contract without sending any request."""
    rows = window.uploadData
    if not actor.win:
        assert rows == [], "An unconfirmed victory must not enqueue uploads"
        raw = json.dumps({"data": []}, sort_keys=True).encode("utf-8")
        return {"count": 0, "battle": 0, "replay": 0, "eligible": False,
                "reason": "victory_not_confirmed", "http": "disabled",
                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}, raw
    battles = [row for row in rows if row.get("type") == "battle"]
    replays = [row for row in rows if row.get("type") == "replay"]
    assert len(battles) == 1, "Expected exactly one battle upload"
    assert len(replays) == len(actor.occResult), "Missing personal replay uploads"
    assert len(rows) == len(replays) + 1
    status = actor.attributeStatus
    assert status.get("staticAttributes"), "Missing static attribute quality"
    battle = battles[0]["data"]
    assert battle["statistics"]["attributeStatus"] == status, "Missing battle quality"
    assert battle["statistics"]["act"]["rdpsStatus"] == actor.combatTracker.rdpsStatus
    for name in ("ndps", "mndps", "hps", "rhps"):
        value = battle["statistics"]["act"][name]["sum"]
        assert math.isfinite(value) and value >= 0, (name, value)
    for row in replays:
        data = row["data"]
        assert data["hash"] and data["battleID"] == battle["hash"]
        assert data["statistics"]["overall"]["attributeStatus"] == status, "Missing replay quality"
        for group, names in (("general", ("ndps", "mndps")), ("healer", ("hps", "rhps"))):
            for name in names:
                value = data["statistics"]["skill"][group][name]
                assert math.isfinite(value) and value >= 0, (group, name, value)
    assert [row["id"] for row in rows] == list(range(len(rows)))
    payload = {"data": [{key: row[key] for key in ("type", "data", "id")} for row in rows]}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
    return {"count": len(rows), "battle": len(battles), "replay": len(replays), "eligible": True,
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "quality": "retained", "observedMetrics": "retained", "http": "disabled"}, raw


def check_equipment_fallback(with_ui=False):
    """Run missing-gear fixtures through the actual actor, ranks and local upload queue."""
    from data.BattleLogData import BattleLogData
    from equip.CangshengAttributeData import kungfu_data
    from equip.EquipmentFallback import average_equipment_data, EQUIPMENT_FALLBACK_WARNING
    from replayer.ActorReplayPro import ActorProReplayer
    from replayer.ReplayerBase import ReplayerBase
    from tools.Attribute import CURRENT_GAME_EDITION
    from tools.ValidateLuoyang import ValidationWindow, make_config, check_windows

    profiles = kungfu_data()['occupations']
    averages = average_equipment_data()
    assert '6d' in averages['occupations']
    unavailable = next(occ for occ in averages['unavailableOccupations']
                       if not occ.endswith('w'))
    scenarios = (('estimated', {'estimate': '6d'}, 'estimated'),
                 ('unavailable', {'missing': unavailable}, 'incomplete'),
                 ('mixed', {'estimate': '6d', 'missing': unavailable}, 'incomplete'))
    results = {}
    for name, occupations, expected_status in scenarios:
        bld = BattleLogData()
        bld.dataType = 'jcl'
        bld.info.map, bld.info.boss = '25人普通洛阳之战', '田承嗣'
        bld.info.server, bld.info.battleTime, bld.info.sumTime = 'release-smoke', 1793620894, 10000
        bld.info.skill = {}
        for player, occ in occupations.items():
            bld.info.addPlayer(player, player, '0', str(profiles[occ]['skill_id']))
        bld.info.addNPC('boss', '田承嗣')
        bld.info.npc['boss'].templateID = '139329'
        bld.log = [SimpleNamespace(dataType='Skill', time=time, caster=player, target='boss',
                                  id='999999', level=1, scheme=1, full_id='1,999999,1',
                                  damage=1000, damageEff=1000, heal=0, healEff=0,
                                  effect=0, fullResult={'0': '1000'}, frame=time // 16)
                   for time in (0, 5000) for player in occupations]
        bld.log.append(SimpleNamespace(dataType='Death', time=10000, id='boss'))
        window = capture_uploads(ValidationWindow())
        actor = ActorProReplayer(make_config(True), [name, 0, 1], '', {name: bld}, window)
        with contextlib.redirect_stdout(io.StringIO()):
            actor.replay()
        queue_summary, _ = check_upload_payloads(window, actor)
        assert actor.win == 1
        assert actor.attributeStatus['status'] == expected_status, actor.attributeStatus
        assert actor.combatTracker.rdpsStatus['status'] == expected_status
        assert all(panel is None for panel in actor.panelAttribDict.values())
        assert window.playerEquipment == {}
        assert all(not player.equip for player in bld.info.player.values())
        if 'estimate' in occupations:
            assert actor.baseAttribDict['estimate']['_estimated']['occ'] == '6d'
            assert 'estimate' in actor.attributeStatus['estimatedPlayers']
            assert actor.attributeStatus['warning'] == EQUIPMENT_FALLBACK_WARNING
        if 'missing' in occupations:
            assert actor.baseAttribDict['missing'] is None
            assert 'missing' not in actor.attributeStatus.get('estimatedPlayers', {})
        for replay in actor.occResult.values():
            for key in ('rdps', 'mrdps'):
                assert replay['rank']['general'][key]['percent'] == -1

        # Use the real result propagation methods, with known percentile data
        # so a hidden rank cannot pass merely because its table is absent.
        percent_data = {'6d-835-田承嗣-%s-%s-%s' % (group, key, CURRENT_GAME_EDITION):
                        {'num': 100, 'value': json.dumps(list(range(102)))}
                        for group, key in (('general', 'rdps'), ('general', 'mrdps'),
                                           ('general', 'ndps'), ('stat', 'score'))}
        replay = ReplayerBase.__new__(ReplayerBase)
        replay.win, replay.actorData, replay.window = 1, actor.actorData, window
        replay.gameEdition = CURRENT_GAME_EDITION
        window.stat_percent = percent_data
        replay.config, replay.public, replay.occ = actor.config, 0, '6d'
        replay.battleID, replay.getHash = actor.hashGroup(), lambda: 'local-rank-fixture'
        replay.result = {'overall': {'map': bld.info.map, 'boss': bld.info.boss,
                                     'server': bld.info.server, 'playerID': 'local-rank-fixture',
                                     'battleTime': bld.info.battleTime, 'edition': 'local-smoke'},
                         'skill': {'general': {'rdps': 70, 'mrdps': 70, 'ndps': 70}},
                         'review': {'score': 70}}
        replay.getRankFromStat('6d')
        assert replay.rank['general']['rdps'] == {'num': 0, 'percent': -1}
        assert replay.rank['general']['mrdps'] == {'num': 0, 'percent': -1}
        assert replay.rank['general']['ndps'] == {'num': 100, 'percent': 70}
        assert replay.getScoreRankFromStat('6d')['score'] == {'num': 0, 'percent': -1}
        before_count = len(window.uploadData)
        replay.prepareUpload()
        assert len(window.uploadData) == before_count + 1
        assert window.uploadData[-1]['data']['statistics']['overall']['attributeStatus'] == actor.attributeStatus
        damage = check_damage_conservation(actor.combatTracker)
        if with_ui:
            check_windows(actor)
        results[name] = {'status': expected_status,
                         'estimatedPlayers': len(actor.attributeStatus.get('estimatedPlayers', {})),
                         'missingPanelRetained': True, 'realEquipmentCacheUnchanged': True,
                         'attributeRanks': 'blocked', 'directDamageRank': 'retained',
                         'uploads': 'captured', 'uploadQueue': queue_summary, 'damage': damage,
                         'ui': 'constructed' if with_ui else 'not requested'}
    return results


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
        window = capture_uploads(ValidationWindow())
        with patch('socket.socket.connect', side_effect=AssertionError('Replay network disabled')), \
                patch('urllib.request.urlopen', side_effect=AssertionError('Replay HTTP disabled')), \
                contextlib.redirect_stdout(io.StringIO()):
            actor = replay(path, window, healers=True)
            queue_summary, raw_payload = check_upload_payloads(window, actor)
            assert actor.battleTime > 0 and actor.statDict
            assert len(actor.occResult) == len(actor.statDict)
            tracker = actor.combatTracker
            assert tracker.rdpsStatus['gameEdition'] == CURRENT_GAME_EDITION
            totals = {name: getattr(tracker, name)['sum']
                      for name in ('ndps', 'mndps', 'rdps', 'mrdps', 'hps', 'ahps', 'rhps')}
            assert all(math.isfinite(value) and value >= 0 for value in totals.values())
            damage = check_damage_conservation(tracker)
            metric = ('ndps' if actor.attributeStatus.get('status') == 'incomplete'
                      and not actor.attributeStatus.get('estimatedPlayers') else 'rdps')
            values = [row.get(metric, 0) for row in actor.statDict]
            assert values == sorted(values, reverse=True), (actor.bossAnalyseName, metric)
            wujie = []
            for player, occ in actor.occDetailList.items():
                if occ.endswith('w'):
                    assert actor.bld.info.getName(player) in actor.occResult
                    wujie.append({'occ': occ, 'damage': tracker.ndpsCast[player].sum,
                                  'healing': tracker.hpsCast[player].sum})
            for expected in entry.get('expectedWujie', []):
                assert any(row['occ'] == expected['occ'] and row[expected['activity']] > 0
                           for row in wujie), (expected, wujie)
            check_windows(actor)
        if not results:
            # Local validation evidence only; release packaging excludes build outputs.
            payload_path = report_path.with_name(report_path.stem + '-first-upload-payload.json')
            payload_path.write_bytes(raw_payload)
            queue_summary['localPayload'] = payload_path.name
        results.append({'file': path.name, 'boss': actor.bossAnalyseName,
                        'players': len(actor.statDict), 'specializationReplays': len(actor.occResult),
                        'win': actor.win, 'uploadEnabled': bool(actor.upload),
                        'seconds': actor.battleTime / 1000,
                        'attributeStatus': actor.detail.get('attributeStatus'),
                        'rdpsStatus': tracker.rdpsStatus, 'totals': totals,
                        'damage': damage, 'displayOrderMetric': metric,
                        'wujie': wujie, 'uploadQueue': queue_summary, 'ui': 'constructed'})
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
        fallback_checks = check_equipment_fallback(with_ui=True)
        result = {'version': EDITION, 'frozen': frozen, 'network': 'disabled',
                  'upload': 'disabled', 'resources': resources, 'attributeStatus': display.status,
                  'kungfus': len(profiles), 'npcProfiles': len(npc_data()['profiles']),
                  'buffChecks': 'passed', 'tk': 'constructed',
                  'mainWindow': 'initialized', 'icons': icon_checks, 'excel': excel_checks,
                  'equipmentFallback': fallback_checks,
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

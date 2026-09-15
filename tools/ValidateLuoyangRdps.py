"""Calculate all five backed-up clears through Actor and export a local rDPS report."""
import argparse
import contextlib
import gc
import hashlib
import io
import json
import math
from pathlib import Path
from unittest.mock import patch

from FileLookUp import FileLookUp
from tools.Names import getJclEncounter
from data.BattleLogData import BattleLogData
from tools.Functions import getOccType
from tools.ValidateLuoyang import ValidationWindow, replay, check_windows
from equip.CangshengAttributeData import get_profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('backups/luoyang-20260915/manifest.json'))
    parser.add_argument('--output', type=Path, default=Path('backups/luoyang-20260915/rdps'))
    parser.add_argument('--boss', help='Replay only one named boss for a targeted regression')
    parser.add_argument('--healers', action='store_true')
    parser.add_argument('--ui', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    lookup = FileLookUp()
    lookup.dataType = 'jcl'
    lookup.specifyFiles([row['source'] for row in manifest])
    selected = {row[0] for row in lookup.getLocalFile()[0]}
    window, results = ValidationWindow(), []
    for entry in manifest:
        if entry['source'] not in selected:
            continue
        path = Path(entry['source'])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'].lower()
        if args.boss and getJclEncounter(path)[1] != args.boss:
            # Later JCLs can omit unchanged gear. Preserve the earlier logs'
            # raw equipment context without recalculating their encounters.
            with contextlib.redirect_stdout(io.StringIO()):
                earlier = BattleLogData()
                earlier.loadFromJcl(str(path))
            window.playerEquipment.update({key: player.equip for key, player in earlier.info.player.items() if player.equip})
            del earlier
            gc.collect()
            continue
        with patch('socket.socket.connect', side_effect=AssertionError('Network disabled')):
            with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'):
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, window, args.healers)
        tracker = actor.combatTracker
        assert actor.win == 1
        assert tracker.rdpsStatus['status'] == 'supported', tracker.rdpsStatus
        players = []
        for player_id, player in actor.bld.info.player.items():
            occ = actor.occDetailList[player_id]
            ndps = tracker.ndps['player'].get(player_id, {})
            rdps = tracker.rdps['player'].get(player_id, {})
            row = {
                'id': player_id, 'name': player.name.strip('"'), 'occ': occ, 'role': getOccType(occ),
                'kungfu': get_profile(occ)['name'],
                'ndps': ndps.get('dps', 0), 'rdps': rdps.get('dps', 0),
                'mrdps': tracker.mrdps['player'].get(player_id, {}).get('dps', 0),
                'panel': actor.panelAttribDict.get(player_id),
                'damage': ndps.get('sum', 0), 'redistributedDamage': rdps.get('sum', 0),
                'contributions': rdps.get('namedSource', {}),
                'creditedSkills': rdps.get('namedSkill', {}),
                'effectiveSeconds': rdps.get('adjustedTime', 0) / 1000,
                'hps': tracker.hps['player'].get(player_id, {}).get('hps', 0),
                'rhps': tracker.rhps['player'].get(player_id, {}).get('hps', 0),
            }
            assert all(math.isfinite(row[key]) and row[key] >= 0 for key in ('ndps', 'rdps', 'mrdps'))
            players.append(row)
        environment = {key: value for key, value in tracker.rdps['player'].items() if key not in actor.bld.info.player}
        direct_total = sum(row.get('sum', 0) for row in tracker.ndps['player'].values())
        redistributed_total = sum(row.get('sum', 0) for row in tracker.rdps['player'].values())
        assert math.isclose(direct_total, redistributed_total, abs_tol=0.001)
        result = {
            'boss': actor.bossAnalyseName, 'file': path.name, 'sha256': entry['sha256'],
            'seconds': actor.battleTime / 1000, 'status': tracker.rdpsStatus,
            'directDamage': direct_total, 'redistributedDamage': redistributed_total,
            'conservationError': redistributed_total - direct_total,
            'players': sorted(players, key=lambda row: -row['rdps']), 'environment': environment,
            'specializationReplays': len(actor.occResult),
            'healerReplays': sum(getOccType(row['occ']) == 'healer' for row in actor.occResult.values()),
        }
        if args.ui:
            result['ui'] = check_windows(actor)
        results.append(result)
        print(result['boss'], 'players=', len(players), 'conservationError=', result['conservationError'], flush=True)
        for row in players:
            if row['role'] != 'dps':
                print('  %s %s ndps=%.2f rdps=%.2f' % (row['name'], row['occ'], row['ndps'], row['rdps']), flush=True)
        del actor
        gc.collect()
        if args.boss:
            break
    write_reports(results, args.output)


def write_reports(results, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'clear-rdps.json').write_text(json.dumps({'network': 'disabled', 'upload': 'disabled', 'results': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 洛阳之战五场通关 rDPS', '', '依据 2026-09-15 25 人普通体服 JCL；网络及上传均禁用。', '']
    lines.extend(['## T 与治疗对照', '', '| 心法 | ' + ' | '.join(r['boss'] for r in results) + ' |',
                  '| --- | ' + ' | '.join('---:' for _ in results) + ' |'])
    roles = [row['occ'] for row in results[0]['players'] if row['role'] != 'dps']
    for occ in sorted(roles, key=lambda value: (getOccType(value), get_profile(value)['name'])):
        values = [next(row['rdps'] for row in result['players'] if row['occ'] == occ) for result in results]
        lines.append('| ' + get_profile(occ)['name'] + ' | ' + ' | '.join('%.0f' % value for value in values) + ' |')
    lines.extend(['', '数值按有效输出时间计算。不同职责的输出机会、增益覆盖与队伍构成不同；相近只作为合理性检查。',
                  'JCL 不含体型，裸属性采用当前客户端默认基线；尚未与游戏内实时面板逐项对照。', ''])
    for result in results:
        lines.extend(['## ' + result['boss'], '', '| 玩家 | 心法 | 职责 | nDPS | rDPS | 本体 rDPS |', '| --- | --- | --- | ---: | ---: | ---: |'])
        for row in result['players']:
            lines.append('| %s | %s | %s | %.2f | %.2f | %.2f |' % (row['name'].replace('|', '\\|'), row['kungfu'], row['role'], row['ndps'], row['rdps'], row['mrdps']))
        lines.extend(['', '总伤害分摊误差：%.6f。' % result['conservationError'], ''])
    (output / '通关rDPS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()

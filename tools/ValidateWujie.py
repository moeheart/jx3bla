"""Validate an explicitly selected current formal-server log containing Wujie players."""
import argparse
import contextlib
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch


from tools.Attribute import CURRENT_GAME_EDITION


def validate_wujie_log(path, ui=False):
    """Check an explicitly selected current formal log, without network/uploads."""
    path = Path(path).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with patch('socket.socket.connect', side_effect=AssertionError('Wujie validation: network disabled')):
        import ServerAddress
        with patch.object(ServerAddress, '_address_cache', copy.deepcopy(ServerAddress.FALLBACK_ADDRESS)):
            from tools.ValidateLuoyang import replay, check_windows
            from equip.CangshengAttributeData import get_profile
            with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'):
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, healers=True)
            tracker = actor.combatTracker
            wujie = {player: occ for player, occ in actor.occDetailList.items() if occ.endswith('w')}
            assert wujie, 'The selected log contains no Wujie players'
            assert tracker.rdpsStatus['gameEdition'] == CURRENT_GAME_EDITION
            assert tracker.rdpsStatus['status'] in ('supported', 'incomplete', 'estimated')
            if tracker.rdpsStatus['status'] == 'incomplete':
                assert tracker.rdpsStatus.get('reason')
            if tracker.rdpsStatus['status'] == 'estimated':
                assert tracker.rdpsStatus.get('estimatedPlayers') and tracker.rdpsStatus.get('warning')
            for player, occ in wujie.items():
                assert str(get_profile(occ)['skill_id']) == str(actor.bld.info.player[player].xinfaCode)
                assert player in tracker.boostCounter
            for metric in ('ndps', 'rdps', 'mrdps'):
                assert all(math.isfinite(row.get('dps', 0)) and row.get('dps', 0) >= 0
                           for row in getattr(tracker, metric)['player'].values())
            direct = sum(row.get('sum', 0) for row in tracker.ndps['player'].values())
            redistributed = sum(row.get('sum', 0) for row in tracker.rdps['player'].values())
            assert math.isclose(direct, redistributed, rel_tol=0, abs_tol=0.001)
            warnings = {player: base['_warnings'] for player, base in actor.baseAttribDict.items()
                        if base is not None and base.get('_warnings')}
            result = {
                'status': 'passed', 'frozen': bool(getattr(sys, 'frozen', False)),
                'network': 'disabled', 'upload': 'disabled', 'file': path.name, 'sha256': digest,
                'boss': actor.bossAnalyseName, 'win': actor.win, 'seconds': actor.battleTime / 1000,
                'players': len(actor.statDict), 'specializationReplays': len(actor.occResult),
                'wujiePlayers': wujie, 'rdpsStatus': tracker.rdpsStatus, 'equipmentWarnings': warnings,
                'directDamage': direct, 'redistributedDamage': redistributed,
                'conservationError': redistributed - direct,
            }
            if ui:
                result['ui'] = check_windows(actor)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
            return result


def write_report(result, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jcl', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ui', action='store_true')
    args = parser.parse_args()
    write_report(validate_wujie_log(args.jcl, ui=args.ui), args.output)
    print('Wujie replay validation passed: ' + str(args.output))


if __name__ == '__main__':
    main()

"""Replay the original Wujie regression log, retaining its known equipment warning."""
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


ORIGINAL_SHA256 = '05af99c7c388899dddaa829cf078efa4c4fafb5ed6167c348ecc7614cc0923fb'
KNOWN_WARNINGS = {'2836': ['装备8,23766词条17121: atSetEquipmentRecipe']}


def validate_wujie_log(path, ui=False):
    """Check the actual actor and optional hidden Tk windows without network/uploads."""
    path = Path(path).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == ORIGINAL_SHA256, 'Expected the unchanged original Wujie regression JCL'
    with patch('socket.socket.connect', side_effect=AssertionError('Wujie validation: network disabled')):
        import ServerAddress
        with patch.object(ServerAddress, '_address_cache', copy.deepcopy(ServerAddress.FALLBACK_ADDRESS)):
            from tools.ValidateLuoyang import replay, check_windows
            from equip.CangshengAttributeData import get_profile
            with patch('replayer.ActorReplayPro.ActorProReplayer.prepareUpload'), patch('replayer.ReplayerBase.ReplayerBase.prepareUpload'):
                with contextlib.redirect_stdout(io.StringIO()):
                    actor = replay(path, healers=True)

            tracker = actor.combatTracker
            assert actor.win == 1
            assert actor.bossAnalyseName == '史朝义'
            assert actor.occDetailList['2994'] == '24w'
            assert actor.bld.info.player['2994'].xinfaCode == '101090'
            assert get_profile('24w')['skill_id'] == 101090
            assert actor.baseAttribDict['2994'] is not None
            assert not actor.baseAttribDict['2994'].get('_warnings')
            assert not actor.panelAttribDict['2994'].get('_warnings')
            assert '2994' in tracker.boostCounter

            names = {player.name for player in actor.bld.info.player.values()}
            assert len(actor.bld.info.player) == len(names) == len(actor.statDict) == 25
            assert {row['name'] for row in actor.statDict} == names
            assert set(actor.occResult) == names
            assert all(base is not None for base in actor.baseAttribDict.values())
            assert not {target for counter in tracker.boostCounter.values()
                        for target in counter.unresolvedTargets}
            warnings = {player: base['_warnings'] for player, base in actor.baseAttribDict.items()
                        if base.get('_warnings')}
            # This separate ordinary Cangjian recipe remains unsupported. Freeze
            # the exact warning instead of accepting arbitrary incomplete results.
            assert warnings == KNOWN_WARNINGS, warnings
            assert actor.occDetailList['2836'] == '8'
            assert tracker.rdpsStatus['gameEdition'] == 160
            assert tracker.rdpsStatus['status'] == 'incomplete', tracker.rdpsStatus
            assert tracker.rdpsStatus['reason'] == '部分玩家装备或当前地图首领属性缺少验证数据。'

            damage, events = 0, 0
            for event in actor.bld.log:
                if event.dataType != 'Skill' or event.caster != '2994' or not actor.startTime <= event.time <= actor.finalTime:
                    continue
                if event.damageEff <= 0 or event.target not in actor.bld.info.npc or event.id in ('35990', '36026', '36735', '36734'):
                    continue
                excluded = next((state for time, state in reversed(actor.bh.badPeriodDpsLog) if event.time > time), 0)
                if not excluded:
                    damage += event.damageEff
                    events += 1
            assert damage == 17753129, damage
            assert tracker.ndpsCast['2994'].sum == damage
            assert tracker.getRdps('2994') > 0
            for metric in ('ndps', 'rdps', 'mrdps'):
                assert all(math.isfinite(row.get('dps', 0)) and row.get('dps', 0) >= 0
                           for row in getattr(tracker, metric)['player'].values())
            direct = sum(row.get('sum', 0) for row in tracker.ndps['player'].values())
            redistributed = sum(row.get('sum', 0) for row in tracker.rdps['player'].values())
            assert math.isclose(direct, redistributed, rel_tol=0, abs_tol=0.001)
            result = {
                'status': 'passed', 'frozen': bool(getattr(sys, 'frozen', False)),
                'network': 'disabled', 'upload': 'disabled', 'file': path.name, 'sha256': digest,
                'boss': actor.bossAnalyseName, 'seconds': actor.battleTime / 1000,
                'players': len(actor.statDict), 'specializationReplays': len(actor.occResult),
                'wujie': {'playerId': '2994', 'occ': '24w', 'xinfaCode': '101090',
                          'effectiveDamageEvents': events, 'effectiveDamage': damage,
                          'ndps': tracker.ndps['player']['2994']['dps'],
                          'rdps': tracker.rdps['player']['2994']['dps'], 'warnings': []},
                'rdpsStatus': tracker.rdpsStatus, 'equipmentWarnings': warnings,
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

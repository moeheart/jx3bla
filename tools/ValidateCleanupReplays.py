"""Compare offline Luoyang replays with a recorded baseline, one ordered raid at a time."""
import argparse
import contextlib
import gc
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch

from release.SmokeTest import capture_uploads, check_damage_conservation, check_upload_payloads
from tools.ValidateLuoyang import ValidationWindow, replay


def digest(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                         separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _accepted_display_changes(path):
    if not path.is_file():
        return {}
    cases = json.loads(path.read_text(encoding='utf-8'))['cases']
    return {case['source']: case for case in cases}


def _team_without_changed_fields(rows):
    normalized = []
    for original in rows:
        row = original.copy()
        if 'equip' in row:
            row['equip'] = {k: v for k, v in row['equip'].items() if k not in ('sketch', 'forge')}
        if str(row.get('occ', '')).rstrip('w').endswith('h'):
            for key in ('score', 'scoreRank', 'scoreRankNum'):
                row.pop(key, None)
        normalized.append(row)
    return normalized


def _skills(actor, *, skip_healer_score=False):
    skills = {}
    for name, player in actor.occResult.items():
        healer = str(player.get('occ', '')).rstrip('w').endswith('h')
        skills[name] = {
            group: {key: value for key, value in fields.items() if key != 'delaySamples'
                    and not (skip_healer_score and healer and group == 'general' and key == 'score')}
            for group, fields in player['result']['skill'].items()
        }
    return skills


def baseline_differences(actor, actual, expected, source_sha256, baseline):
    """Accept only the recorded pairs of pre/post-migration hashes on known inputs."""
    changes = [key for key in actual if actual[key] != expected.get(key)]
    receipt = Path(baseline).resolve().parents[1] / '9.0' / '装备摘要回归.json'
    evidence = _accepted_display_changes(receipt).get(source_sha256, {})
    for key, before, after in (('teamTableSha256', 'originalTeam', 'updatedTeam'),
                               ('skillMetricsSha256', 'originalSkills', 'updatedSkills')):
        if (key in changes and expected.get(key) == evidence.get(before)
                and actual[key] == evidence.get(after)):
            if key == 'teamTableSha256':
                unchanged = digest(_team_without_changed_fields(actor.statDict)) == evidence['excludingPresentation']
            else:
                unchanged = digest(_skills(actor, skip_healer_score=True)) == evidence['normalizedSkills']
            if unchanged:
                changes.remove(key)
    return changes


def summarize(actor, window):
    uploads, _ = check_upload_payloads(window, actor)
    # Compare the skill data emitted by both generations. The new observation
    # counts are checked by the delay ranking tests, separately from legacy metrics.
    return {
        'boss': actor.bossAnalyseName, 'win': actor.win, 'winReason': actor.detail.get('winReason'),
        'boundaryMs': [actor.startTime, actor.finalTime, actor.battleTime],
        'effectiveMs': [actor.bh.sumTime('dps'), actor.bh.sumTime('healer')],
        'players': len(actor.statDict), 'personalUploads': uploads['replay'],
        'quality': actor.attributeStatus['status'],
        'damage': check_damage_conservation(actor.combatTracker),
        'teamTableSha256': digest(actor.statDict),
        'skillMetricsSha256': digest(_skills(actor)),
        'timelineSha256': digest(actor.bh.log),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--group', required=True)
    parser.add_argument('--log-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads(args.baseline.read_text(encoding='utf-8'))[args.group]
    window = capture_uploads(ValidationWindow())
    results = []
    for case in cases:
        path = args.log_dir / case['file']
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != case['sha256']:
                raise ValueError(f'Unexpected log bytes: {path.name}')
        window.uploadData = []
        with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), patch(
                'socket.socket.connect', side_effect=AssertionError('Network disabled')):
            actor = replay(path, window, healers=True)
            result = summarize(actor, window)
            if 'result' in case:
                changed = baseline_differences(actor, result, case['result'], case['sha256'], args.baseline)
                if changed:
                    raise AssertionError(f"{case['file']}: changed {', '.join(changed)}")
        results.append(dict(file=path.name, sha256=case['sha256'], result=result))
        print(f"{args.group} {len(results)}/{len(cases)} {actor.bossAnalyseName} win={actor.win}", flush=True)
        del actor
        gc.collect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

"""Read heroic last-two logs into anonymous encounter evidence, offline only."""
import argparse
import contextlib
import csv
import io
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from data.BattleLogData import BattleLogData
from replayer.boss.luoyangzhizhan.AshinaChengqing import LuoyangAshinaChengqingReplayer as Ashina
from replayer.boss.luoyangzhizhan.ShiChaoyi import ShiChaoyiReplayer as Shi

NPC_NAMES = {'139378': '阿史那承庆', '139365': '史朝义', '139363': '煞将',
             '139394': '伏焰', '139398': '炽虎', '139404': '玄隼',
             '139408': '死侍', '139407': '玄隼弹', '139918': '飞行狼牙兵',
             '139388': '李复', '139971': '翅膀', '139140': '剑碎片', '139403': '高空的风'}
SUCCESS = ('2026-11-13-21-37-44-', '2026-11-13-22-49-04-')


def inspect(path, names):
    with contextlib.redirect_stdout(io.StringIO()):
        bld = BattleLogData()
        bld.loadFromJcl(str(path))
    cls = Ashina if '阿史那承庆' in path.name else Shi
    start, end = bld.log[0].time, bld.log[-1].time
    def npc(key):
        obj = bld.info.npc.get(key)
        template = str(obj.templateID) if obj else 'player'
        return (template, NPC_NAMES.get(template, ''))
    def encounter_npc(key):
        template = npc(key)[0]
        return template.isdigit() and 139000 <= int(template) < 142000
    timeline, counts, targets = [], Counter(), Counter()
    for event in bld.log:
        time = round((event.time-start)/1000, 3)
        kind = event.dataType
        if kind in ('Shout', 'Death', 'Scene', 'Battle') and encounter_npc(event.id):
            if kind == 'Shout' and npc(event.id)[0] not in NPC_NAMES:
                continue
            timeline.append([time, kind, *npc(event.id), getattr(event, 'content', ''),
                             getattr(event, 'enter', None), getattr(event, 'fight', None)])
        elif kind == 'Cast' and encounter_npc(event.caster):
            label = names.get(('s', event.id), '')
            timeline.append([time, kind, event.id, label, *npc(event.caster)])
            counts[(kind, event.id, label, *npc(event.caster))] += 1
        elif kind == 'Skill':
            if encounter_npc(event.target) and event.caster in bld.info.player and event.damageEff > 0:
                targets[npc(event.target)] += event.damageEff
            if encounter_npc(event.caster) and event.target in bld.info.player:
                counts[(kind, event.id, names.get(('s', event.id), ''), *npc(event.caster))] += 1
        elif kind == 'Buff' and event.target in bld.info.player and encounter_npc(event.caster):
            counts[(kind, event.id, names.get(('b', event.id), ''), *npc(event.caster))] += 1
    replay = cls(bld, {key: value.occ for key, value in bld.info.player.items()}, start, end,
                 end-start, cls.BOSS, SimpleNamespace(item={'actor': {'filter': ''}}))
    replay.initBattle()
    replay.recordEquipment({})
    for event in bld.log:
        replay.analyseSecondStage(event)
    replay.trimTime()
    replay.getResult()
    stats = Counter()
    for row in replay.statDict.values():
        stats.update({key: value for key, value in row['battle'].items() if isinstance(value, (int, float))})
    calls = [row for player in replay.bh.log['call'].values() for row in player]
    periods = replay.detail['phasePeriods']
    expected_win = int(path.name.startswith(SUCCESS))
    checks = {'expectedVictory': replay.win == expected_win,
              'phaseConservation': sum(replay.phaseTime) == replay.battleTime,
              'phaseCoverage': bool(periods) and periods[0]['start'] == start and periods[-1]['end'] == replay.finalTime,
              'phaseContinuity': all(a['end'] == b['start'] for a, b in zip(periods, periods[1:])),
              'environmentBounds': all(start <= row['start'] <= row['start']+row['duration'] <= replay.finalTime
                                       for row in replay.bh.log['environment']),
              'callBounds': all(start <= row['start'] <= row['start']+row['duration'] <= replay.finalTime for row in calls)}
    return {'file': path.name, 'start': start, 'duration': (end-start)/1000,
            'npcs': Counter(npc(key) for key in bld.info.npc if encounter_npc(key)).most_common(),
            'events': counts.most_common(), 'timeline': timeline, 'targets': targets.most_common(),
            'systemMessages': [vars(e) for e in bld.systemMessages if e.content.startswith('[全胜！25人英雄洛阳之战]')],
            'replay': {'win': replay.win, 'winReason': replay.detail['winReason'],
                       'checks': checks, 'expectedWin': expected_win, 'callCount': len(calls),
                       'effectiveMs': replay.battleTime, 'phases': replay.detail['phaseTimes'],
                       'stats': dict(stats), 'environment': replay.bh.log['environment'],
                       'phasePeriods': replay.detail['phasePeriods'],
                       'constructPeriods': replay.detail.get('constructPeriods', []),
                       'shaPeriods': replay.detail.get('shaPeriods', [])}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs', type=Path, required=True)
    parser.add_argument('--tables', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    names = {}
    for filename, prefix, key in [('skill.txt', 's', 'SkillID'), ('buff.txt', 'b', 'BuffID')]:
        with (args.tables/filename).open(encoding='utf-8-sig') as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                names.setdefault((prefix, row[key]), row.get('Name', ''))
    if args.all:
        templates = ('(139378).jcl', '(139365).jcl', '(139363).jcl', '(139388).jcl', '(139381).jcl')
        files = [path for path in sorted(args.logs.glob('2026-11-13-*英雄洛阳*.jcl'))
                 if path.name.endswith(templates)]
    else:
        files = []
        for boss in ('阿史那承庆', '史朝义'):
            files.extend(sorted(args.logs.glob('2026-11-13-*英雄洛阳*%s*.jcl' % boss))[-2:])
    results = []
    for path in files:
        result = inspect(path, names)
        results.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(path.name, result['replay']['win'], result['replay']['phases'], result['replay']['checks'], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    failures = [(r['file'], r['replay']['checks']) for r in results if not all(r['replay']['checks'].values())]
    if failures:
        raise AssertionError(failures)


if __name__ == '__main__':
    main()

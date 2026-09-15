"""Local evidence extraction; no edits to source JCL or unpacked files."""
import argparse, sys, csv, json
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.BattleLogData import BattleLogData
from tools.Names import getJclEncounter

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs', type=Path, required=True)
    parser.add_argument('--tables', type=Path, required=True)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('backups/luoyang-20260915/luoyang45-evidence.json'))
    args = parser.parse_args()
    BASE, DATA = args.logs, args.tables
    names = {}
    for fn, prefix, key in [('skill.txt','s','SkillID'), ('buff.txt','b','BuffID')]:
        with (DATA/fn).open(encoding='utf-8-sig') as f:
            for row in csv.DictReader(f, delimiter='\t'):
                names.setdefault(prefix+row[key], row)

    files = sorted(path for path in BASE.glob('*洛阳之战*.jcl') if getJclEncounter(path)[1] in ('阿史那承庆', '史朝义'))
    if not args.all:
        files = files[:1] + files[-1:]
    result = []
    for path in files:
        bld=BattleLogData(); bld.loadFromJcl(str(path))
        start=bld.log[0].time
        npc=lambda x: [bld.info.getName(x),bld.info.npc[x].templateID] if x in bld.info.npc else [x,'']
        timeline=[]; skills=Counter(); buffs=Counter(); dmg=Counter(); casts=Counter()
        for e in bld.log:
            t=round((e.time-start)/1000,2)
            if e.dataType=='Shout': timeline.append([t,'Shout',e.content])
            elif e.dataType=='Scene' and e.id in bld.info.npc:
                if npc(e.id)[0] or npc(e.id)[1] in ['139324']:
                    timeline.append([t,'Scene',*npc(e.id),e.enter])
            elif e.dataType=='Death' and e.id in bld.info.npc: timeline.append([t,'Death',*npc(e.id)])
            elif e.dataType=='Cast' and e.caster in bld.info.npc:
                label=names.get('s'+e.id,{}).get('Name',e.id)
                casts[(e.id,label,*npc(e.caster))]+=1
                timeline.append([t,'Cast',e.id,label,*npc(e.caster)])
            elif e.dataType=='Skill':
                if e.target in bld.info.npc and e.caster in bld.info.player and e.damageEff>0: dmg[tuple(npc(e.target))]+=e.damageEff
                if e.caster in bld.info.npc and e.target in bld.info.player and e.damage>0: skills[(e.id,names.get('s'+e.id,{}).get('Name',e.id),*npc(e.caster))]+=1
            elif e.dataType=='Buff' and e.target in bld.info.player and e.stack>0:
                if e.caster in bld.info.npc or int(e.id)>=34000:
                    buffs[(e.id,names.get('b'+e.id,{}).get('Name',e.id),*npc(e.caster))]+=1
        out={'file':path.name,'duration':round((bld.log[-1].time-start)/1000,2), 'timeline':timeline,
             'npc':Counter(tuple(npc(x)) for x in bld.info.npc).most_common(), 'damage':dmg.most_common(),
             'skills':skills.most_common(),'buffs':buffs.most_common(),'casts':casts.most_common()}
        result.append(out)
        print('SUMMARY',path.name,out['duration'],len(timeline),flush=True)
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()

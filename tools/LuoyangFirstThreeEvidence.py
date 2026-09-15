"""Read-only evidence inventory for the September 15 Luoyang test logs."""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.BattleLogData import BattleLogData


def display_table(root, filename, key):
    with (root / filename).open(encoding="utf-8-sig") as stream:
        return {row[key]: {k: row[k] for k in ("Name", "Desc", "IconID")}
                for row in csv.DictReader(stream, delimiter="\t")}


def inspect(path, skills, buffs):
    bld = BattleLogData()
    bld.loadFromJcl(str(path))
    start = bld.log[0].time
    damage = Counter()
    incoming = defaultdict(list)
    casts = defaultdict(list)
    debuffs = defaultdict(list)
    npc_buffs = defaultdict(list)
    shouts, scenes, deaths, battles, alerts = [], [], [], [], []
    npc = {key: [value.name, value.templateID] for key, value in bld.info.npc.items()}
    for event in bld.log:
        t = round((event.time - start) / 1000, 3)
        if event.dataType == "Skill":
            if event.caster in bld.info.player and event.target in npc:
                damage[event.target] += event.damageEff
            if event.caster in npc and event.target in bld.info.player and event.damage > 0:
                incoming[event.id].append([t, npc[event.caster], event.damageEff])
        elif event.dataType == "Cast" and event.caster in npc:
            casts[event.id].append([t, npc[event.caster]])
        elif event.dataType == "Buff" and event.target in bld.info.player and event.caster in npc:
            debuffs[event.id].append([t, event.stack, npc[event.caster]])
        elif event.dataType == "Buff" and event.target in npc and npc[event.target][1].startswith(("139", "140")):
            npc_buffs[event.id].append([t, event.stack, npc[event.target]])
        elif event.dataType == "Shout":
            shouts.append([t, event.name, event.content])
        elif event.dataType == "Scene" and event.id in npc:
            scenes.append([t, event.enter, npc[event.id]])
        elif event.dataType == "Death":
            deaths.append([t, npc.get(event.id, ["player", ""]), npc.get(event.killer)])
        elif event.dataType == "Battle" and event.id in npc:
            battles.append([t, npc[event.id], event.fight, event.hp, event.hpMax])
        elif event.dataType == "Alert":
            alerts.append([t, event.content])
    def summarized(groups, table):
        return {key: {"display": table.get(key), "count": len(rows), "events": rows}
                for key, rows in groups.items()}
    return {"file": path.name, "duration": (bld.log[-1].time-start)/1000,
            "sumTime": bld.info.sumTime, "start": start,
            "damage": [[npc[key], value] for key, value in damage.most_common()],
            "casts": summarized(casts, skills), "incoming": summarized(incoming, skills),
            "buffs": summarized(debuffs, buffs), "npcBuffs": summarized(npc_buffs, buffs), "shouts": shouts, "scenes": scenes,
            "deaths": deaths, "battles": battles, "alerts": alerts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", type=Path)
    parser.add_argument("tables", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    skills = display_table(args.tables, "skill.txt", "SkillID")
    buffs = display_table(args.tables, "buff.txt", "BuffID")
    paths = sorted(path for path in args.logs.glob("2026-09-15-*洛阳之战*.jcl")
                   if any(name in path.name for name in ("突利和顺", "田承嗣", "伊曼")))
    results = [inspect(path, skills, buffs) for path in paths]
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", len(results), "logs to", args.output)

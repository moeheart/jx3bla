"""Read-only, reproducible extraction of Shi Chaoyi circle evidence from JCL.

Only derived output is written. Millisecond time is the JCL local monotonic clock;
relative time uses the first raw record, not a reconstructed combat start.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.LoadData import LuaTableAnalyserToDict
from tools.Names import getJclEncounter

CIRCLE_IDS = {"139311": "red", "139314": "white"}
COLOR_BUFFS = {"34095": "red", "34096": "white"}
MECHANIC_SKILLS = {str(i) for i in range(45702, 45712)}


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_file(path, battle_id):
    raw = path.read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("gb18030")
    records = [line.split("\t", 5) for line in content.splitlines() if line.strip()]
    parser = LuaTableAnalyserToDict()
    npcs, players = {}, set()
    start = int(records[0][3])
    end = int(records[-1][3])
    npc_records = []
    for line, rec in enumerate(records, 1):
        if rec[4] in ("4", "8"):
            d = parser.analyse(rec[5], delta=1)
            if rec[4] == "4":
                players.add(d["1"])
            else:
                npcs.setdefault(d["1"], d)
                if d["3"] in CIRCLE_IDS:
                    npc_records.append((line, rec, d))
    circles = {}
    for line, rec, d in npc_records:
        circles.setdefault(d["1"], {
            "battle_id": battle_id, "file": path.name,
            "instance_id": d["1"], "npc_template_id": d["3"],
            "color": CIRCLE_IDS[d["3"]], "first_record_ms": int(rec[3]),
            "first_record_line": line, "spawn_ms": None, "spawn_line": None,
            "spawn_frame": None, "despawn_ms": None, "despawn_line": None,
            "x": int(d["5"]), "y": int(d["6"]), "z": int(d["7"]),
            "direction": int(d["8"]), "color_buff_ids": set(),
            "color_buff_lines": [], "skill_ids": set(), "first_resolve_ms": None,
        })
    casts, events, deaths, boss_exits, rewards = [], [], [], [], []
    for line, rec in enumerate(records, 1):
        typ = rec[4]
        # Skip unrelated high-volume events before Lua parsing.
        if typ not in {"6", "7", "13", "19", "21", "28", "14"}:
            continue
        if typ == "13" and not any("," + bid + "," in rec[5] for bid in (*COLOR_BUFFS, "34619", "34121", "34122")):
            continue
        if typ == "21" and not any("," + sid + "," in rec[5] for sid in MECHANIC_SKILLS):
            continue
        d = parser.analyse(rec[5], delta=1)
        time = int(rec[3])
        base = {"battle_id": battle_id, "line": line, "time_ms": time,
                "relative_s": round((time-start)/1000, 3), "frame": int(rec[1]), "type": int(typ)}
        if typ == "19" and d["2"] == "45711" and npcs.get(d["1"], {}).get("3") in ("139312", "139365", "138261"):
            casts.append({**base, "caster": d["1"], "skill_id": d["2"], "level": d["3"]})
        elif typ in ("6", "7"):
            if d["1"] in circles:
                c = circles[d["1"]]
                if typ == "6" and c["spawn_ms"] is None:
                    c.update(spawn_ms=time, spawn_line=line, spawn_frame=int(rec[1]))
                elif typ == "7" and c["despawn_ms"] is None:
                    c.update(despawn_ms=time, despawn_line=line)
                events.append({**base, "instance_id": d["1"]})
            if typ == "7" and npcs.get(d["1"], {}).get("3") == "139312":
                boss_exits.append(base)
        elif typ == "13" and d["5"] in (*COLOR_BUFFS, "34619", "34121", "34122"):
            source = d.get("10")
            if source in circles:
                c = circles[source]
                active = d["2"] != "true" and int(d["6"]) > 0 and d.get("11", "true") == "true"
                if d["5"] in COLOR_BUFFS and active:
                    c["color_buff_ids"].add(d["5"])
                    c["color_buff_lines"].append(line)
                events.append({**base, "instance_id": source, "target": d["1"], "buff_id": d["5"],
                               "stack": int(d["6"]), "delete": d["2"], "valid": d.get("11", "true")})
        elif typ == "21" and d["1"] in circles:
            c = circles[d["1"]]
            c["skill_ids"].add(d["5"])
            if c["first_resolve_ms"] is None:
                c["first_resolve_ms"] = time
            events.append({**base, "instance_id": d["1"], "target": d["2"], "skill_id": d["5"], "level": d["6"]})
        elif typ == "28" and d["1"] in players:
            deaths.append(base)
        elif typ == "14" and d.get("2") == "0" and "侠士完成【击杀25人普通秘境首领】" in d.get("1", ""):
            rewards.append(base)

    # Associate by explicit cast. Never split a truncated wave into a new cast.
    phases = []
    for idx, cast in enumerate(casts, 1):
        stop = casts[idx]["time_ms"] if idx < len(casts) else end+1
        cs = sorted((c for c in circles.values() if cast["time_ms"] <= (c["spawn_ms"] or c["first_record_ms"]) < stop),
                    key=lambda c: (c["spawn_ms"] or c["first_record_ms"], c["first_record_line"]))
        counts = Counter(c["color"] for c in cs)
        for order, c in enumerate(cs, 1):
            c["phase"] = idx
            c["order"] = order
            c["cast_ms"] = cast["time_ms"]
            c["spawn_relative_s"] = round(((c["spawn_ms"] or c["first_record_ms"])-start)/1000, 3)
            c["after_cast_s"] = round(((c["spawn_ms"] or c["first_record_ms"])-cast["time_ms"])/1000, 3)
            c["after_first_circle_s"] = round(((c["spawn_ms"] or c["first_record_ms"])-(cs[0]["spawn_ms"] or cs[0]["first_record_ms"]))/1000, 3)
            c["lifetime_s"] = round((c["despawn_ms"]-(c["spawn_ms"] or c["first_record_ms"]))/1000, 3) if c["despawn_ms"] else None
            c["resolve_after_spawn_s"] = round((c["first_resolve_ms"]-(c["spawn_ms"] or c["first_record_ms"]))/1000, 3) if c["first_resolve_ms"] else None
        phases.append({"battle_id": battle_id, "file": path.name, "phase": idx,
                       "cast_line": cast["line"], "cast_ms": cast["time_ms"], "cast_relative_s": cast["relative_s"],
                       "cast_frame": cast["frame"], "n_circles": len(cs), "red": counts["red"], "white": counts["white"],
                       "sequence": "".join("R" if c["color"] == "red" else "W" for c in cs),
                       "first_spawn_s": cs[0]["spawn_relative_s"] if cs else None,
                       "last_spawn_s": cs[-1]["spawn_relative_s"] if cs else None,
                       "first_delay_s": cs[0]["after_cast_s"] if cs else None,
                       "last_despawn_s": round((max(c["despawn_ms"] or end for c in cs)-start)/1000, 3) if cs else None,
                       "record_remaining_s": round((end-cast["time_ms"])/1000, 3),
                       "status": "full_40" if len(cs) == 40 else "incomplete",
                       "n_resolved_observed": sum(c["first_resolve_ms"] is not None for c in cs),
                       "n_unresolved_observed": sum(c["first_resolve_ms"] is None for c in cs),
                       "resolution_status": "all_observed" if cs and all(c["first_resolve_ms"] is not None for c in cs) else "missing_events",
                       "player_deaths_during_40s": sum(cast["time_ms"] <= d["time_ms"] < cast["time_ms"]+40000 for d in deaths),
                       "boss_exit_after_cast_s": next((round((e["time_ms"]-cast["time_ms"])/1000, 3) for e in boss_exits if e["time_ms"]>=cast["time_ms"]), None),
                       "kill_reward_after_cast_s": next((round((e["time_ms"]-cast["time_ms"])/1000, 3) for e in rewards if e["time_ms"]>=cast["time_ms"]), None)})
    for c in circles.values():
        assert c["color_buff_ids"] <= {bid for bid, color in COLOR_BUFFS.items() if color == c["color"]}, c
        c["color_buff_ids"] = ";".join(sorted(c["color_buff_ids"]))
        c["color_buff_lines"] = ";".join(map(str, c["color_buff_lines"]))
        c["skill_ids"] = ";".join(sorted(c["skill_ids"]))
        c.setdefault("phase", None)
    battle = {"battle_id": battle_id, "file": path.name,
              "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw),
              "start_ms": start, "end_ms": end, "duration_s": round((end-start)/1000, 3),
              "n_phases": len(phases), "n_circles": len(circles), "player_count": len(players),
              "kill_reward": bool(rewards), "unassigned_circles": sum(c["phase"] is None for c in circles.values())}
    return battle, phases, list(circles.values()), events


def verify_sample(paths, sample_path):
    """Replay exactly the published hashes, including fights without circles."""
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    expected = {row["sha256"]: row for row in sample["battles"]}
    sizes = {row["size_bytes"] for row in expected.values()}
    sources = {}
    for path in paths:
        if path.stat().st_size in sizes:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in expected:
                sources.setdefault(digest, path)
    missing = [row["battle_id"] for digest, row in expected.items() if digest not in sources]
    if missing:
        raise ValueError("Missing source logs for " + ", ".join(missing))
    actual = {"battles": [], "phases": [], "circles": []}
    for digest, reference in expected.items():
        battle, phases, circles, _ = parse_file(sources[digest], reference["battle_id"])
        actual["battles"].append(battle)
        actual["phases"].extend(phases)
        for circle in circles:
            dx, dy = circle["x"] - 7408, circle["y"] - 53794
            circle.update(x_chi=dx / 64, y_chi=dy / 64, radius_chi=(dx*dx + dy*dy)**0.5 / 64)
        actual["circles"].extend(circles)
    for group, rows in actual.items():
        if len(rows) != len(sample[group]):
            raise ValueError(f"{group} count differs from sample")
        for idx, (observed, recorded) in enumerate(zip(rows, sample[group]), 1):
            for key, value in recorded.items():
                # Discovery/validation assignment records the study design.
                if key != "discovery_set" and observed[key] != value:
                    raise ValueError(f"{group} row {idx}: {key} differs from sample")
    print(f"Verified {len(expected)} source logs, {len(actual['phases'])} waves, {len(actual['circles'])} circles")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    inputs = ap.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--logs", type=Path, help="Directory of experience-server map 835 JCL files")
    inputs.add_argument("--manifest", type=Path, help="JSON list of source paths and SHA256 digests")
    ap.add_argument("--output", type=Path, default=Path("build/research/shichaoyi-circles-20260915"))
    ap.add_argument("--check-sample", type=Path, help="Replay the source hashes and verify published observations")
    args = ap.parse_args()
    baseline = {}
    if args.logs:
        if not args.logs.is_dir():
            ap.error("--logs must point to a directory")
        files = list(args.logs.glob("*.jcl"))
    else:
        rows = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        files = [args.manifest.parent / row["source"] for row in rows]
        baseline = {p: row["sha256"].lower() for p, row in zip(files, rows)}
    if args.check_sample:
        verify_sample(files, args.check_sample)
        return
    files = sorted(p for p in files if getJclEncounter(p)[1] == "史朝义")
    if not files:
        ap.error("No Shi Chaoyi JCLs found for extraction")
    args.output.mkdir(parents=True, exist_ok=True)
    battles, phases, circles, events = [], [], [], []
    for idx, path in enumerate(files, 1):
        b, ps, cs, es = parse_file(path, f"B{idx:02d}")
        if path in baseline and b["sha256"] != baseline[path]:
            ap.error("Manifest SHA256 mismatch for " + path.name)
        battles.append(b); phases.extend(ps); circles.extend(cs); events.extend(es)
        print(b["battle_id"], path.name, f"phases={len(ps)} circles={len(cs)}", flush=True)
    result = {"battles": battles, "phases": phases, "circles": circles, "events": events}
    assert not any(b["unassigned_circles"] for b in battles), "Circles without a preceding cast need manual review"
    assert len({(c["battle_id"], c["instance_id"]) for c in circles}) == len(circles)
    assert sum(p["n_circles"] for p in phases) == len(circles)
    for key, rows in result.items():
        write_csv(args.output / (key + ".csv"), rows)
    (args.output / "evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {
        "scope": "2026-09-15 experience-server map 835, 25-player normal; other difficulties not established",
        "time_origin": "first raw JCL record in each file; not guaranteed exact combat engagement",
        "color_label": "white is the user's visual label; extracted internal name is black / Yousha",
        "phase_status": "full_40 means all 40 spawns observed, NOT all 40 resolutions completed",
        "npc_template_colors": CIRCLE_IDS, "player_color_buffs": COLOR_BUFFS,
        "precast_skill": "45711", "all_circle_instances_have_scene_enter": all(c["spawn_ms"] is not None for c in circles),
        "all_circle_instances_have_scene_exit": all(c["despawn_ms"] is not None for c in circles),
        "baseline_hash_matches": len(files) if args.manifest else 0,
        "baseline_hash_mismatches": [],
        "source_files": len(battles), "phases": len(phases), "circle_instances": len(circles),
        "color_contradictions": 0, "unassigned_circles": 0,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY", len(battles), len(phases), len(circles), Counter(p["status"] for p in phases))


if __name__ == "__main__":
    main()

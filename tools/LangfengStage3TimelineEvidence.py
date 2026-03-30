import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.BattleLogData import BattleLogData
from replayer.boss.langfengxuancheng.TimelineEvidence import (
    append_candidate,
    append_garbage_hit,
    build_common_filter_table,
    finalize_candidates,
    finalize_common_filters,
    finalize_garbage,
    format_time,
    get_garbage_reason,
    get_garbage_reason_by_id,
    get_parsed_key,
    is_unresolved_name,
    looks_suspicious,
    normalize_name,
)


BOSS_ORDER = ["笑妆娘", "唐醉", "柳公子", "阿史那承庆"]
BUFF_WHITELIST = {"32976", "32851", "32954"}
SEASON_OUTPUT_DIR = Path("docs/150")
VISIBLE_OUTPUT_DIR = Path("replayer/boss/langfengxuancheng")


def get_event_prefix(event_type):
    return {
        "Skill": "s",
        "Buff": "b",
        "Cast": "c",
        "Scene": "n",
    }.get(event_type, event_type[:1].lower())


def load_bld(path):
    bld = BattleLogData()
    bld.loadFromJcl(str(path))
    return bld


def get_clear_samples():
    groups = {boss: [] for boss in BOSS_ORDER}
    for path in sorted(Path(".").glob("*阆风悬城*.jcl")):
        bld = load_bld(path)
        if bld.info.boss in groups:
            groups[bld.info.boss].append(path)

    result = {}
    for boss in BOSS_ORDER:
        group = sorted(groups[boss])
        if group:
            result[boss] = group[-1]
    return result


def collect_raw_summary(path):
    bld = load_bld(path)
    boss_name = bld.info.boss
    other_boss_names = {name for name in BOSS_ORDER if name != boss_name}

    raw_candidates = {}
    garbage = {}
    suspicious = set()
    stats = defaultdict(int)

    for event in bld.log:
        if event.dataType == "Cast" and event.caster in bld.info.npc:
            skill_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(skill_name):
                continue
            garbage_reason = get_garbage_reason_by_id("Cast", event.id)
            if garbage_reason:
                append_garbage_hit(garbage, "Cast", skill_name, event.id, garbage_reason, event.time)
                continue
            garbage_reason = get_garbage_reason(skill_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Cast", skill_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(skill_name):
                suspicious.add(("Cast", skill_name, str(event.id)))
            append_candidate(raw_candidates, "c%s" % event.id, skill_name, event.time, "Cast", event.id)
            stats["cast"] += 1

        elif event.dataType == "Skill" and event.caster in bld.info.npc and event.target in bld.info.player:
            if event.damage <= 0 and event.heal <= 0:
                continue
            skill_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(skill_name):
                continue
            garbage_reason = get_garbage_reason_by_id("Skill", event.id)
            if garbage_reason:
                append_garbage_hit(garbage, "Skill", skill_name, event.id, garbage_reason, event.time)
                continue
            garbage_reason = get_garbage_reason(skill_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Skill", skill_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(skill_name):
                suspicious.add(("Skill", skill_name, str(event.id)))
            append_candidate(raw_candidates, "s%s" % event.id, skill_name, event.time, "Skill", event.id)
            stats["skill"] += 1

        elif event.dataType == "Buff" and event.caster in bld.info.npc and event.target in bld.info.player and event.stack > 0:
            buff_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(buff_name):
                continue
            if str(event.id) not in BUFF_WHITELIST:
                append_garbage_hit(garbage, "Buff", buff_name, event.id, "filtered_b", event.time)
                continue
            garbage_reason = get_garbage_reason(buff_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Buff", buff_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(buff_name):
                suspicious.add(("Buff", buff_name, str(event.id)))
            append_candidate(raw_candidates, "b%s" % event.id, buff_name, event.time, "Buff", event.id)
            stats["buff"] += 1

        elif event.dataType == "Scene" and event.id in bld.info.npc:
            name = normalize_name(bld.info.getName(event.id))
            if not name:
                continue
            template_id = bld.info.npc[event.id].templateID
            reason = "filtered_n"
            if name in other_boss_names:
                reason = "other_boss"
            append_garbage_hit(garbage, "Scene", name, template_id, reason, event.time)
            stats["scene"] += 1

    return {
        "file": path.name,
        "boss": boss_name,
        "map": bld.info.map,
        "candidateStats": dict(stats),
        "rawCandidates": finalize_candidates(raw_candidates),
        "garbageHits": finalize_garbage(garbage),
        "suspicious": sorted(
            [{"type": item[0], "name": item[1], "id": item[2]} for item in suspicious],
            key=lambda line: (line["type"], line["name"], line["id"]),
        ),
    }


def apply_common_filters(raw_info, common_filter_table):
    candidates = {}
    garbage = {}

    for item in raw_info["garbageHits"]:
        parsed_key = get_parsed_key(item["type"], item["id"])
        if parsed_key in common_filter_table:
            continue
        append_garbage_hit(garbage, item["type"], item["name"], item["id"], item["reason"], item["firstTime"])

    cast_name_set = {
        item["name"]
        for item in raw_info["rawCandidates"]
        if item["type"] == "Cast" and get_parsed_key(item["type"], item["id"]) not in common_filter_table
    }

    for item in raw_info["rawCandidates"]:
        parsed_key = get_parsed_key(item["type"], item["id"])
        if parsed_key in common_filter_table:
            continue

        if item["type"] == "Skill" and item["name"] in cast_name_set:
            append_garbage_hit(garbage, item["type"], item["name"], item["id"], "skill_has_cast", item["firstTime"])
            continue

        append_candidate(
            candidates,
            "%s%s" % (get_event_prefix(item["type"]), item["id"]),
            item["name"],
            item["firstTime"],
            item["type"],
            item["id"],
        )
        candidates["%s%s" % (get_event_prefix(item["type"]), item["id"])]["count"] = item["count"]
        candidates["%s%s" % (get_event_prefix(item["type"]), item["id"])]["lastTime"] = item["lastTime"]
        candidates["%s%s" % (get_event_prefix(item["type"]), item["id"])]["extra"] = set(item["extra"])

    return {
        "file": raw_info["file"],
        "boss": raw_info["boss"],
        "map": raw_info["map"],
        "candidateStats": raw_info["candidateStats"],
        "candidates": finalize_candidates(candidates),
        "garbageHits": finalize_garbage(garbage),
        "suspicious": raw_info["suspicious"],
    }


def render_markdown(summary, common_filter_lines):
    lines = []
    lines.append("# 阆风悬城时间轴候选名单")
    lines.append("")
    lines.append("说明：本名单只基于当前普通本 1-4 的 clear 参考样本生成，用于阶段 3 的人工筛选。")
    lines.append("")
    lines.append("过滤原则：")
    lines.append("")
    lines.append("- 已自动过滤未解析名（名字中仍带逗号的 `1,xxxx,x / 2,xxxx,x`）")
    lines.append("- `b` 只保留 `b32976 / b32851 / b32954`")
    lines.append("- 已显式过滤普通攻击：`s44021 / s43923 / s33125 / s44303 / s44171`")
    lines.append("- `s` 类技能重新纳入统计，但若同名 `c` 类技能已存在，则该 `s` 类技能会被过滤")
    lines.append("- 在不同 BOSS 中出现过 2 次以上的解析后 ID，会进入“公用内容”汇总")
    lines.append("- `n` 类主体/场景项继续视为本轮阶段 3 的过滤项")
    lines.append("")
    lines.append("## 公用内容")
    lines.append("")
    if common_filter_lines:
        for item in common_filter_lines:
            lines.append("- `%s` `%s` 类型=%s BOSS数=%d 包含=%s" % (
                item["key"],
                item["name"],
                item["type"],
                item["bossCount"],
                "/".join(item["bosses"]),
            ))
    else:
        lines.append("- 无")
    lines.append("")

    for boss in BOSS_ORDER:
        if boss not in summary:
            continue
        info = summary[boss]
        lines.append("## %s" % boss)
        lines.append("")
        lines.append("- 参考样本：`%s`" % info["file"])
        lines.append("- 地图：`%s`" % info["map"])
        lines.append("- 候选统计：`Cast=%d / Skill=%d / Buff=%d / Scene=%d`" % (
            info["candidateStats"].get("cast", 0),
            info["candidateStats"].get("skill", 0),
            info["candidateStats"].get("buff", 0),
            info["candidateStats"].get("scene", 0),
        ))
        lines.append("")
        lines.append("### 候选环境项")
        lines.append("")
        if info["candidates"]:
            for item in info["candidates"][:25]:
                lines.append("- `%s%s` `%s` 次数=%d 首次=%s 末次=%s" % (
                    get_event_prefix(item["type"]),
                    item["id"],
                    item["name"],
                    item["count"],
                    format_time(item["firstTime"]),
                    format_time(item["lastTime"]),
                ))
        else:
            lines.append("- 无")
        lines.append("")
        lines.append("### 已过滤垃圾项")
        lines.append("")
        if info["garbageHits"]:
            for item in info["garbageHits"][:25]:
                lines.append("- `%s%s` `%s` 原因=`%s` 次数=%d 首次=%s 末次=%s" % (
                    get_event_prefix(item["type"]),
                    item["id"],
                    item["name"],
                    item["reason"],
                    item["count"],
                    format_time(item["firstTime"]),
                    format_time(item["lastTime"]),
                ))
        else:
            lines.append("- 无")
        lines.append("")
        lines.append("### 需要赛季检查的可疑项")
        lines.append("")
        if info["suspicious"]:
            for item in info["suspicious"][:20]:
                lines.append("- `%s%s` `%s`" % (get_event_prefix(item["type"]), item["id"], item["name"]))
        else:
            lines.append("- 无")
        lines.append("")

    return "\n".join(lines)


def write_outputs(markdown_text, summary, common_filter_lines):
    payload = {
        "commonContents": common_filter_lines,
        "bosses": summary,
    }

    for directory in [SEASON_OUTPUT_DIR, VISIBLE_OUTPUT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "阆风悬城时间轴候选名单.md").write_text(markdown_text, encoding="utf-8")
        (directory / "langfeng_stage3_timeline_summary.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def main():
    raw_summary = {}
    for boss, path in get_clear_samples().items():
        raw_summary[boss] = collect_raw_summary(path)

    common_filter_table = build_common_filter_table(raw_summary)
    common_filter_lines = finalize_common_filters(common_filter_table)

    final_summary = {}
    for boss in BOSS_ORDER:
        if boss in raw_summary:
            final_summary[boss] = apply_common_filters(raw_summary[boss], common_filter_table)

    markdown_text = render_markdown(final_summary, common_filter_lines)
    write_outputs(markdown_text, final_summary, common_filter_lines)

    for boss in BOSS_ORDER:
        if boss in final_summary:
            info = final_summary[boss]
            print("%s | candidates=%d | garbage=%d | suspicious=%d" % (
                boss,
                len(info["candidates"]),
                len(info["garbageHits"]),
                len(info["suspicious"]),
            ))


if __name__ == "__main__":
    main()

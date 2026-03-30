import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.BattleLogData import BattleLogData
from replayer.boss.langfengxuancheng.TimelineEvidence import normalize_name, is_unresolved_name, get_garbage_reason, \
    looks_suspicious, append_garbage_hit, append_candidate, finalize_candidates, finalize_garbage, format_time


BOSS_ORDER = ["笑妆娘", "唐醉", "柳公子", "阿史那承庆"]


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


def summarize_boss(path):
    bld = load_bld(path)
    boss_name = bld.info.boss
    other_boss_names = {name for name in BOSS_ORDER if name != boss_name}

    candidates = {}
    boss_scenes = {}
    suspicious = set()
    garbage = {}
    stats = defaultdict(int)

    for event in bld.log:
        if event.dataType == "Cast" and event.caster in bld.info.npc:
            skill_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(skill_name):
                continue
            garbage_reason = get_garbage_reason(skill_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Cast", skill_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(skill_name):
                suspicious.add(("Cast", skill_name, event.id))
            append_candidate(candidates, "c%s" % event.id, skill_name, event.time, "Cast", event.id)
            stats["cast"] += 1

        elif event.dataType == "Skill" and event.caster in bld.info.npc and event.target in bld.info.player:
            if event.damage <= 0 and event.heal <= 0:
                continue
            skill_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(skill_name):
                continue
            garbage_reason = get_garbage_reason(skill_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Skill", skill_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(skill_name):
                suspicious.add(("Skill", skill_name, event.id))
            append_candidate(candidates, "s%s" % event.id, skill_name, event.time, "Skill", event.id)
            stats["skill"] += 1

        elif event.dataType == "Buff" and event.caster in bld.info.npc and event.target in bld.info.player and event.stack > 0:
            buff_name = normalize_name(bld.info.getSkillName(event.full_id))
            if is_unresolved_name(buff_name):
                continue
            garbage_reason = get_garbage_reason(buff_name)
            if garbage_reason:
                append_garbage_hit(garbage, "Buff", buff_name, event.id, garbage_reason, event.time)
                continue
            if looks_suspicious(buff_name):
                suspicious.add(("Buff", buff_name, event.id))
            append_candidate(candidates, "b%s" % event.id, buff_name, event.time, "Buff", event.id)
            stats["buff"] += 1

        elif event.dataType == "Scene" and event.id in bld.info.npc:
            name = normalize_name(bld.info.getName(event.id))
            if not name:
                continue
            template_id = bld.info.npc[event.id].templateID
            extra = "enter=%s" % event.enter
            if name == boss_name:
                append_candidate(boss_scenes, "n%s" % template_id, name, event.time, "Scene", template_id, extra)
            if not event.enter:
                continue
            if name in other_boss_names:
                append_garbage_hit(garbage, "Scene", name, template_id, "other_boss", event.time)
                continue
            garbage_reason = get_garbage_reason(name)
            if garbage_reason:
                append_garbage_hit(garbage, "Scene", name, template_id, garbage_reason, event.time)
                continue
            if looks_suspicious(name):
                suspicious.add(("Scene", name, template_id))
            append_candidate(candidates, "n%s" % template_id, name, event.time, "Scene", template_id, extra)
            stats["scene"] += 1

    return {
        "file": path.name,
        "boss": boss_name,
        "map": bld.info.map,
        "candidateStats": dict(stats),
        "bossScenes": finalize_candidates(boss_scenes),
        "candidates": finalize_candidates(candidates),
        "garbageHits": finalize_garbage(garbage),
        "suspicious": sorted(
            [{"type": x[0], "name": x[1], "id": x[2]} for x in suspicious],
            key=lambda line: (line["type"], line["name"], line["id"])
        ),
    }


def render_markdown(summary):
    lines = []
    lines.append("# 阆风悬城时间轴候选名单")
    lines.append("")
    lines.append("说明：本名单只基于当前普通本 1-4 的 clear 参考样本生成，用于阶段 3 的人工筛选。")
    lines.append("")
    lines.append("过滤原则：")
    lines.append("")
    lines.append("- 已自动过滤未解析名（名字中仍带逗号的 `1,xxxx,x / 2,xxxx,x`）")
    lines.append("- 已自动过滤当前赛季垃圾项，例如 `牧云`、玩家气场、骑宠/灵宠、内部接引人、标记等")
    lines.append("- `可疑项` 会单列出来，供后续赛季更新时检查是否需要加入垃圾列表")
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

        lines.append("### 主体场景")
        lines.append("")
        if info["bossScenes"]:
            for item in info["bossScenes"][:12]:
                extra = ", ".join(item["extra"])
                lines.append("- `%s%s` `%s` 次数=%d 首次=%s 末次=%s %s" % (
                    item["type"][0].lower(),
                    item["id"],
                    item["name"],
                    item["count"],
                    format_time(item["firstTime"]),
                    format_time(item["lastTime"]),
                    extra,
                ))
        else:
            lines.append("- 无")
        lines.append("")

        lines.append("### 候选环境项")
        lines.append("")
        if info["candidates"]:
            for item in info["candidates"][:25]:
                extra = ""
                if item["extra"]:
                    extra = " " + "/".join(item["extra"])
                lines.append("- `%s%s` `%s` 次数=%d 首次=%s 末次=%s%s" % (
                    item["type"][0].lower(),
                    item["id"],
                    item["name"],
                    item["count"],
                    format_time(item["firstTime"]),
                    format_time(item["lastTime"]),
                    extra,
                ))
        else:
            lines.append("- 无")
        lines.append("")

        lines.append("### 已过滤垃圾项")
        lines.append("")
        if info["garbageHits"]:
            for item in info["garbageHits"][:20]:
                lines.append("- `%s%s` `%s` 原因=`%s` 次数=%d 首次=%s 末次=%s" % (
                    item["type"][0].lower(),
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
                lines.append("- `%s%s` `%s`" % (item["type"][0].lower(), item["id"], item["name"]))
        else:
            lines.append("- 无")
        lines.append("")

    return "\n".join(lines)


def main():
    summary = {}
    for boss, path in get_clear_samples().items():
        summary[boss] = summarize_boss(path)

    Path("docs/阆风悬城时间轴候选名单.md").write_text(render_markdown(summary), encoding="utf-8")
    Path("tools/langfeng_stage3_timeline_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for boss in BOSS_ORDER:
        if boss in summary:
            info = summary[boss]
            print("%s | candidates=%d | garbage=%d | suspicious=%d" % (
                boss,
                len(info["candidates"]),
                len(info["garbageHits"]),
                len(info["suspicious"]),
            ))


if __name__ == "__main__":
    main()

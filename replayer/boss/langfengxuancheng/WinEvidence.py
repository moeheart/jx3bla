# Created by moeheart at 03/30/2026
# Thin helpers for Langfeng Xuancheng stage-2 win evidence collection.

from tools.Names import getGameEditionFromTime, getIDFromMap

TAIL_WINDOW = 30000
SYSTEM_SHOUT_MARKERS = ["获得了", "所有奖励已添加到包裹中", "已升至"]
REWARD_SHOUT_MARKERS = ["祈愿值", "所有奖励已添加到包裹中", "薪火点"]


def append_unique(items, item, keys=None):
    if keys is None:
        keys = ["time", "name", "templateID", "content", "enter", "npcID"]
    item_key = tuple(item.get(key, None) for key in keys)
    for line in items:
        line_key = tuple(line.get(key, None) for key in keys)
        if item_key == line_key:
            return
    items.append(item)


def boss_name_match(name, boss_name, extra_names=None):
    if not name:
        return False
    if name == boss_name or boss_name in name:
        return True
    if extra_names is not None:
        for line in extra_names:
            if line and line in name:
                return True
    return False


def is_meaningful_shout(content):
    if not content:
        return False
    for marker in SYSTEM_SHOUT_MARKERS:
        if marker in content:
            return False
    return True


def normalize_shout_content(content):
    if content is None:
        return ""
    text = str(content).strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text


def is_reward_shout(content):
    text = normalize_shout_content(content)
    for marker in REWARD_SHOUT_MARKERS:
        if marker in text:
            return True
    return False


def find_shout_win_reason(items, boss_win_shouts=None, damage_trim_time=0):
    boss_win_shouts = boss_win_shouts or []
    normalized_win_shouts = set([normalize_shout_content(line) for line in boss_win_shouts])
    reward_candidate = None
    boss_candidate = None

    for item in items:
        content = item.get("content", "")
        text = normalize_shout_content(content)
        if reward_candidate is None and is_reward_shout(text):
            reward_candidate = item
        if boss_candidate is None and text in normalized_win_shouts:
            boss_candidate = item

    chosen = None
    rule = ""
    if reward_candidate is not None:
        chosen = reward_candidate
        rule = "reward_shout"
    elif boss_candidate is not None:
        chosen = boss_candidate
        rule = "boss_win_shout"

    if chosen is None:
        return None

    event_time = chosen.get("time", 0)
    trim_time = 0
    if damage_trim_time and damage_trim_time <= event_time:
        event_time = damage_trim_time
        trim_time = damage_trim_time

    return {
        "rule": rule,
        "eventTime": event_time,
        "trimTime": trim_time,
        "backupRule": "damage" if trim_time else "",
        "needShoutHook": 0,
        "shoutTime": chosen.get("time", 0),
        "shout": normalize_shout_content(chosen.get("content", "")),
    }


def get_langfeng_game_edition(replayer):
    map_id = getIDFromMap(replayer.bld.info.map)
    return getGameEditionFromTime(map_id, replayer.bld.info.battleTime)


def allow_damage_win_fallback(replayer):
    return get_langfeng_game_edition(replayer) in ["0", "150"]


def template_id_match(template_id, template_ids):
    if isinstance(template_ids, str):
        template_ids = [template_ids]
    return template_id in template_ids


def is_reliable_shout_candidate(items):
    if not items:
        return False
    unique_contents = set()
    for item in items:
        unique_contents.add(item.get("content", ""))
    return len(items) <= 2 and len(unique_contents) <= 2


def filter_relevant_candidates(items, boss_name, boss_template_ids=None, extra_names=None):
    boss_template_ids = boss_template_ids or []
    extra_names = extra_names or []
    results = []
    for item in items:
        if boss_name_match(item.get("name", ""), boss_name, extra_names) or \
                item.get("templateID", "") in boss_template_ids:
            append_unique(results, item)
    results.sort(key=lambda x: (x.get("time", 0), x.get("name", ""), x.get("templateID", "")))
    return results


def filter_chest_candidates(items, chest_names=None, chest_template_ids=None):
    chest_names = chest_names or []
    chest_template_ids = chest_template_ids or []
    results = []
    for item in items:
        if item.get("name", "") in chest_names or item.get("templateID", "") in chest_template_ids:
            append_unique(results, item)
    results.sort(key=lambda x: (x.get("time", 0), x.get("name", ""), x.get("templateID", "")))
    return results


def filter_tail_scene_candidates(items, final_time, boss_name, scene_template_ids=None, extra_names=None,
                                 tail_window=TAIL_WINDOW):
    scene_template_ids = scene_template_ids or []
    extra_names = extra_names or []
    results = []
    for item in items:
        time = item.get("time", 0)
        name = item.get("name", "")
        template_id = item.get("templateID", "")
        if boss_name_match(name, boss_name, extra_names) or \
                template_id in scene_template_ids or \
                "宝箱" in name or "寶箱" in name or \
                (time >= final_time - tail_window and name):
            append_unique(results, item)
    results.sort(key=lambda x: (x.get("time", 0), x.get("name", ""), x.get("templateID", "")))
    return results


def build_damage_candidates(damage_by_npc, final_time, boss_name, boss_template_ids=None, extra_names=None,
                            tail_window=TAIL_WINDOW, limit=8):
    boss_template_ids = boss_template_ids or []
    extra_names = extra_names or []
    direct = []
    tail = []
    for npc_id in damage_by_npc:
        item = damage_by_npc[npc_id].copy()
        if boss_name_match(item.get("name", ""), boss_name, extra_names) or \
                item.get("templateID", "") in boss_template_ids:
            direct.append(item)
        elif item.get("lastTime", 0) >= final_time - tail_window and item.get("name", ""):
            tail.append(item)

    direct.sort(key=lambda x: (-x.get("damage", 0), -x.get("lastTime", 0), x.get("name", "")))
    tail.sort(key=lambda x: (-x.get("damage", 0), -x.get("lastTime", 0), x.get("name", "")))

    results = []
    for item in direct + tail:
        append_unique(results, item, ["npcID"])
        if len(results) >= limit:
            break
    return results


def build_recommendation(evidence):
    meaningful_shouts = [item for item in evidence.get("shouts", []) if is_meaningful_shout(item.get("content", ""))]
    reliable_shout = is_reliable_shout_candidate(meaningful_shouts)
    available = []
    if meaningful_shouts:
        available.append("shout")
    if evidence.get("deaths", []):
        available.append("death")
    if evidence.get("chests", []):
        available.append("chest")
    if evidence.get("scenes", []):
        available.append("scene")
    if evidence.get("damage", []):
        available.append("damage")

    if reliable_shout:
        recommended = "shout"
        risk = "Highest-confidence if later versions add an explicit kill shout; current samples may still be silent."
    elif evidence.get("deaths", []):
        recommended = "death"
        risk = "High-confidence after the exact NPC/templateID is confirmed."
    elif evidence.get("chests", []):
        recommended = "chest"
        risk = "Medium-confidence; chest events can be missing when the main view is on cooldown."
    elif evidence.get("scenes", []):
        recommended = "scene"
        risk = "Medium-risk; needs confirmation that the scene event is uniquely tied to battle end."
    elif evidence.get("damage", []):
        recommended = "damage"
        risk = "High-risk fallback only; must trim invalid tail time before formal use."
    else:
        recommended = "undetermined"
        risk = "No stable candidate has been confirmed from the current samples."

    return {
        "available": available,
        "recommended": recommended,
        "risk": risk,
        "needShoutHook": 0 if reliable_shout else 1,
    }


def format_evidence_report(boss_name, evidence, recommendation):
    lines = []
    lines.append("boss=%s" % boss_name)
    lines.append("available=%s" % ",".join(recommendation["available"]))
    lines.append("recommended=%s" % recommendation["recommended"])
    lines.append("risk=%s" % recommendation["risk"])
    lines.append("need_shout_hook=%s" % recommendation["needShoutHook"])
    for key in ["shouts", "deaths", "chests", "scenes", "damage"]:
        lines.append("[%s]" % key)
        for item in evidence.get(key, []):
            detail = []
            for field in ["time", "content", "name", "templateID", "enter", "damage", "lastTime", "npcID"]:
                if field in item and item[field] not in ["", None]:
                    detail.append("%s=%s" % (field, item[field]))
            lines.append("  " + ", ".join(detail))
    return "\n".join(lines)

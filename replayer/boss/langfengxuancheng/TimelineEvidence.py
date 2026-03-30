from collections import defaultdict


TIMELINE_GARBAGE_EXACT = {
    "铁骨",
    "洗髓",
    "铁牢",
    "明尊",
    "鏖战",
    "精神匮乏",
    "封足",
    "牧云",
    "牧雲",
    "耐力损耗",
    "微妙风",
    "松鼠",
    "蝶旋",
    "千蝶吐瑞",
}

TIMELINE_GARBAGE_CONTAINS = [
    "宿敌",
    "的气场",
    "@",
    "乘黄",
    "碧蝶",
    "灵蛇",
    "圣蝎",
    "逐云寒蕊",
    "青川濯莲",
    "切割的苍棘缚地",
    "内部接引人",
    "标记",
    "破苍穹",
    "吞日月",
    "碎星辰",
    "饼仙的",
]

TIMELINE_SUSPICIOUS_KEYWORDS = [
    "气场",
    "乘黄",
    "灵蛇",
    "碧蝶",
    "牧云",
    "牧雲",
    "标记",
    "内部接引人",
]


def normalize_name(name):
    if name is None:
        return ""
    return str(name).strip()


def is_unresolved_name(name):
    name = normalize_name(name)
    return "," in name or name == ""


def get_garbage_reason(name):
    name = normalize_name(name)
    if name in TIMELINE_GARBAGE_EXACT:
        return "exact"
    for keyword in TIMELINE_GARBAGE_CONTAINS:
        if keyword in name:
            return keyword
    return ""


def looks_suspicious(name):
    name = normalize_name(name)
    if not name:
        return False
    for keyword in TIMELINE_SUSPICIOUS_KEYWORDS:
        if keyword in name:
            return True
    return False


def append_garbage_hit(store, event_type, name, event_id, reason, time):
    key = (event_type, name, event_id, reason)
    if key not in store:
        store[key] = {"count": 0, "firstTime": time, "lastTime": time}
    store[key]["count"] += 1
    store[key]["lastTime"] = time


def append_candidate(store, key, name, time, event_type, event_id, extra=None):
    if key not in store:
        store[key] = {
            "type": event_type,
            "id": event_id,
            "name": name,
            "count": 0,
            "firstTime": time,
            "lastTime": time,
            "extra": set(),
        }
    store[key]["count"] += 1
    store[key]["lastTime"] = time
    if extra:
        store[key]["extra"].add(extra)


def finalize_candidates(store):
    results = []
    for item in store.values():
        line = item.copy()
        line["extra"] = sorted(item["extra"])
        results.append(line)
    results.sort(key=lambda x: (-x["count"], x["type"], x["id"], x["name"]))
    return results


def finalize_garbage(store):
    results = []
    for key, item in store.items():
        event_type, name, event_id, reason = key
        results.append({
            "type": event_type,
            "name": name,
            "id": event_id,
            "reason": reason,
            "count": item["count"],
            "firstTime": item["firstTime"],
            "lastTime": item["lastTime"],
        })
    results.sort(key=lambda x: (-x["count"], x["type"], x["name"], x["id"]))
    return results


def format_time(ms):
    total_seconds = int(ms / 1000)
    minute = total_seconds // 60
    second = total_seconds % 60
    return "%02d:%02d" % (minute, second)

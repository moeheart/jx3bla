"""Metric quality shared by uploads, replay displays and percentile collection.

The existing statistics JSON is authoritative. Cache only its small quality
summary, never the battle/replay payload, and validate file identity on every hit.
"""
import ast
from collections import OrderedDict
from copy import deepcopy
import json
import math
import os
from threading import RLock
from tools.ReplayRevision import get_analysis_revision


SENSITIVE_METRICS = frozenset(("score", "rdps", "mrdps"))
RANK_METRICS = ("score", "rdps", "mrdps", "hps", "rhps", "ndps", "mndps")
_CACHE_LIMIT = 8192
_quality_cache = OrderedDict()
_cache_lock = RLock()


def _quality_sources(data):
    if not isinstance(data, dict):
        return []
    sources = []
    if any(key in data for key in ("status", "staticAttributes", "estimatedPlayers", "missingEquipmentPlayers", "unmodeledEffects", "precise", "rankEligible")):
        sources.append(data)
    for key in ("statistics", "overall", "act", "attributeStatus", "rdpsStatus", "quality"):
        nested = data.get(key)
        if isinstance(nested, dict):
            sources.extend(_quality_sources(nested))
    return sources


def get_record_quality(data):
    """Normalize old/new replay, battle, upload or quality-status dictionaries."""
    sources = _quality_sources(data)
    estimated_players = {}
    missing_players = {}
    effects = []
    states = set()
    static = []
    warning = ""
    explicit_restriction = False
    estimated = False
    estimated_count = 0
    missing_count = 0
    unresolved_missing = False
    for source in sources:
        state = source.get("status")
        if isinstance(state, str):
            states.add(state)
        static_state = source.get("staticAttributes")
        if isinstance(static_state, str):
            static.append(static_state)
        for field, target in (("estimatedPlayers", estimated_players), ("missingEquipmentPlayers", missing_players)):
            values = source.get(field)
            if isinstance(values, dict):
                target.update(values)
                if field == "missingEquipmentPlayers":
                    unresolved_missing = unresolved_missing or any(not isinstance(item, dict) or item.get("hasReference") is not True for item in values.values())
            elif isinstance(values, (list, tuple)):
                target.update((str(value), None) for value in values)
        values = source.get("unmodeledEffects", [])
        if isinstance(values, (list, tuple)):
            for value in values:
                if value not in effects:
                    effects.append(value)
        if not warning and isinstance(source.get("warning"), str):
            warning = source["warning"]
        estimated = estimated or source.get("estimated") is True or state == "estimated" or static_state == "estimated"
        estimated_count = max(estimated_count, source.get("estimatedPlayerCount", 0) if isinstance(source.get("estimatedPlayerCount"), int) else 0)
        missing_count = max(missing_count, source.get("missingEquipmentPlayerCount", 0) if isinstance(source.get("missingEquipmentPlayerCount"), int) else 0)
        explicit_restriction = explicit_restriction or source.get("precise") is False
        eligibility = source.get("rankEligible", {})
        if isinstance(eligibility, dict):
            explicit_restriction = explicit_restriction or any(eligibility.get(metric) is False for metric in SENSITIVE_METRICS)
    estimated = estimated or bool(estimated_players)
    unavailable = "unavailable" in states
    incomplete = bool(states.intersection(("incomplete", "unsupported", "invalid"))) or unresolved_missing or any(value in ("missing", "partial") for value in static)
    restricted = unavailable or incomplete or estimated or bool(effects) or explicit_restriction
    status = "unavailable" if unavailable else "incomplete" if incomplete else "estimated" if estimated else "incomplete" if restricted else "supported" if sources else "legacy"
    if restricted and not warning:
        warning = "部分属性未完整建模，rDPS、mrDPS及表现分仅供参考，不参与精确排名。"
    result = {
        "status": status, "precise": not restricted, "estimated": estimated,
        "rankEligible": {metric: not restricted or metric not in SENSITIVE_METRICS for metric in RANK_METRICS},
        "warning": warning, "estimatedPlayerCount": max(len(estimated_players), estimated_count),
        "missingEquipmentPlayerCount": max(len(missing_players), missing_count),
    }
    if static:
        result["staticAttributes"] = next((value for value in ("missing", "partial", "estimated", "available") if value in static), static[0])
    if effects:
        result["unmodeledEffects"] = effects
    revision = get_analysis_revision(data)
    if revision is not None:
        result['analysisRevision'] = revision
    return result


def is_metric_rank_eligible(data, metric):
    return metric not in SENSITIVE_METRICS or get_record_quality(data)["precise"]


def quality_level(data):
    """Order source fidelity independently of eligibility for exact ranking."""
    quality = get_record_quality(data)
    if quality["precise"]:
        return 3
    if quality.get("staticAttributes") in ("missing", "partial") or quality["status"] == "unavailable":
        return 0
    if quality.get("staticAttributes") == "available" and not quality["estimated"]:
        return 2
    return 1 if quality["status"] == "estimated" or quality.get("staticAttributes") == "estimated" else 0


def is_valid_rank(value):
    try:
        return value is not None and not isinstance(value, bool) and math.isfinite(value) and value >= 0
    except TypeError:
        return False


def _signature(path):
    info = os.stat(path)
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _unavailable_quality():
    return get_record_quality({"status": "unavailable", "warning": "记录质量信息暂不可读取，属性相关排名暂不展示。"})


def parse_statistics(text):
    """Read JSON or historical Python literals without replacing apostrophes."""
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        value = ast.literal_eval(text)
    if not isinstance(value, dict):
        raise ValueError("Statistics must be an object")
    return value


def invalidate_quality_cache(path=None):
    with _cache_lock:
        if path is None:
            _quality_cache.clear()
        else:
            _quality_cache.pop(os.path.abspath(os.fspath(path)), None)


def load_record_quality(path):
    """Read only on a cache miss/change; unreadable JSON fails closed per metric.

    Historical valid files without quality metadata retain their former behavior.
    Missing/corrupt files cannot establish precision, but measured SQL metrics
    remain queryable. Transient read failures are not cached.
    """
    path = os.path.abspath(os.fspath(path))
    try:
        signature = _signature(path)
        with _cache_lock:
            cached = _quality_cache.get(path)
            if cached is not None and cached[0] == signature:
                _quality_cache.move_to_end(path)
                return deepcopy(cached[1])
        with open(path, "r", encoding="utf-8-sig") as stream:
            text = stream.read()
        value = parse_statistics(text)
        if _signature(path) != signature:
            return _unavailable_quality()
        quality = get_record_quality(value)
        with _cache_lock:
            _quality_cache[path] = (signature, quality)
            _quality_cache.move_to_end(path)
            while len(_quality_cache) > _CACHE_LIMIT:
                _quality_cache.popitem(last=False)
        return deepcopy(quality)
    except (OSError, ValueError, SyntaxError, TypeError, RecursionError):
        return _unavailable_quality()

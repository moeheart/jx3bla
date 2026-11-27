"""Qt timelines for boss mechanics and personal replays. Times in the view are milliseconds."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from html import escape
from functools import lru_cache
from itertools import accumulate, groupby
from math import ceil, isfinite
from typing import Optional
import re
import struct
import zlib

from PySide6.QtCore import QIODevice, QRect, QSaveFile, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractScrollArea, QApplication, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QHBoxLayout, QLabel, QMenu, QMessageBox, QPlainTextEdit,
    QToolButton, QToolTip, QVBoxLayout, QWidget, QWidgetAction,
)

from data.PersonalTimeline import ACTION_ICONS, Observation, build_personal_timelines
from data.ReplaySkillTiming import ATLAS_IDS, CAST_ICONS, healer_channel, is_healing_resource, skill_timing
from tools.ResourcePath import get_icon_path


MECHANICS = "首领机制"
PHASES = "阶段切换"
CALLS = "机制点名"
NORMAL = "占 GCD"
SPECIAL = "不占 GCD"
ROUTINE_BOSS_LABELS = {"常规技能", "常规", "常规阶段", "普通攻击", "攻击", "近战攻击", "远程攻击", "普攻"}
BANDS = {
    "badPeriodDps": ("输出无效", "#52647a"), "badPeriodHealer": ("治疗无效", "#657186"),
    "mxym": ("迷仙引梦", "#7953ac"), "xwgd": ("仙王蛊鼎", "#6c5ba0"),
    "ghzs": ("蛊惑众生", "#917847"), "zwjt": ("醉舞九天", "#8870ae"),
    "yaoxing": ("药性", "#2088ac"), "qianzhi": ("千枝", "#2b8170"),
    "qingchuan": ("青川", "#52864d"), "hxpy": ("回雪飘摇", "#a34482"),
    "moyi": ("墨意", "#384957"), "heizi": ("黑子", "#535c6b"), "baizi": ("白子", "#87796c"),
}


def number(value, default=0):
    try:
        value = float(value)
        return value if isfinite(value) else default
    except (ValueError, TypeError, OverflowError):
        return default


def clock(ms):
    seconds = max(0, ms) / 1000
    return f"{int(seconds // 60)}:{seconds % 60:04.1f}"


@dataclass(frozen=True)
class Mark:
    start: float
    end: float
    track: str
    name: str
    color: str
    detail: str = ""
    icon: str = ""
    focused: bool = True
    band: bool = False
    intensity: float = 1
    skill_name: str = ""
    lane: str = ""
    ticks: Optional[int] = None


def heat_series(replay, occ):
    """Read the different sample layouts emitted by old and current occupations."""
    heat = replay.get("heat") or {}
    if not isinstance(heat, dict):
        return
    for key, label in (("shangyang", "商阳指"), ("zhonglin", "钟林毓秀"),
                       ("lancui", "兰摧玉折"), ("kuaixue", "快雪时晴")):
        if key in heat:
            item = heat[key]
            yield label, item.get("timeline", []), item.get("interval", 500)
    values = heat.get("timeline", [])
    if not values:
        return
    if not isinstance(values[0], (list, tuple)):
        yield "梅花盾" if replay.get("heatType") == "meihua" else "覆盖热度", values, heat.get("interval", 500)
        return
    labels = ()
    if replay.get("heatType") == "combined":
        labels = ("梅花盾", "双持续治疗")
    elif occ == "5h" or "hxpy" in replay:
        labels = ("翔舞", "上元")
    for index, series in enumerate(values):
        label = labels[index] if index < len(labels) else f"小队 {index + 1} 覆盖"
        yield label, series, heat.get("interval", 500)


def bands(replay, start, duration, occ):
    for key, (label, color) in BANDS.items():
        if key in ("hxpy", "zwjt") and isinstance(replay.get(key + "Casts"), list):
            for cast in replay[key + "Casts"]:
                begin, end = number(cast["start"])-start, number(cast["end"])-start
                if end < 0 or begin > duration:
                    continue
                ticks = int(cast["ticks"])
                note = "开场时已在引导" if cast.get("partial") else label
                yield Mark(max(0, begin), min(duration, end), label, f"{ticks} 跳", color,
                           f"{note} · 引导 {ticks} 跳", band=True, lane="引导", ticks=ticks)
            continue
        points = [(number(row[0])-start, number(row[1])) for row in (replay.get(key) or [])
                  if isinstance(row, (tuple, list)) and len(row) >= 2]
        points.sort(key=lambda row: row[0])
        for index, (time, value) in enumerate(points):
            end = points[index + 1][0] if index + 1 < len(points) else duration
            begin, end = max(0, time), min(duration, end)
            if end <= begin or (not value and key not in ("moyi", "heizi", "baizi", "yaoxing")):
                continue
            shade = "#b16c49" if key == "yaoxing" and value < 0 else color
            intensity = {"yaoxing": 5, "moyi": 100, "heizi": 5, "baizi": 5}.get(key, 1)
            yield Mark(begin, end, label, f"{value:g}", shade, band=True,
                       intensity=min(1, abs(value)/intensity))
    for label, series, period in heat_series(replay, occ):
        period = number(period, 500)
        if period <= 0 or not isinstance(series, (tuple, list)):
            continue
        index = 0
        for sample, run in groupby(series):
            end_index = index + sum(1 for _ in run)
            begin, end = index*period, min(duration, end_index*period)
            if end > begin:
                value = number(sample)
                yield Mark(begin, end, label, f"{value:g}%", "#187e71", band=True,
                           intensity=max(0, min(1, value/100)))
            index = end_index


def _field(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def cooldown_intervals(uses, duration, icons=None):
    """Project serial recharge after observed uses; an early recast overrides the estimate."""
    for name, (seconds, maximum, times) in uses.items():
        period = seconds * 1000
        missing = 0
        next_ready = None
        last = 0

        def interval(end):
            available = maximum - missing
            status = "冷却" if maximum == 1 else f"{available}/{maximum}"
            detail = f"基础调息 {seconds:g} 秒 · {maximum} 层 · 按实录施放推算，减调息或重置可能提前恢复"
            return Mark(last, end, name, status, "#586d9d", detail, (icons or {}).get(name, ""), band=True,
                        intensity=missing / maximum, lane="调息")

        for time in sorted(set(times)):
            while missing and next_ready <= time:
                if next_ready > last:
                    yield interval(next_ready)
                last = next_ready
                missing -= 1
                next_ready += period
            if missing and time > last:
                yield interval(time)
            if not missing or missing == maximum:
                next_ready = time + period
            missing = min(maximum, missing + 1)
            last = time
        while missing and last < duration:
            end = min(next_ready, duration)
            yield interval(end)
            last = end
            missing -= 1
            next_ready += period


def _observations(records):
    """Accept native records and their array or named-object JSON encodings."""
    for raw in records or ():
        if isinstance(raw, Observation):
            yield raw
            continue
        if isinstance(raw, dict):
            if not all(key in raw for key in Observation._fields):
                continue
            raw = [raw[key] for key in Observation._fields]
        if not isinstance(raw, (tuple, list)) or len(raw) != len(Observation._fields):
            continue
        time, skill, name, kind, events, targets = raw
        if (not isinstance(time, (int, float)) or not isfinite(time)
                or not isinstance(skill, (int, str)) or not isinstance(name, str)
                or kind not in ("施放", "招式命中", "技能效果")
                or not isinstance(events, int) or not isinstance(targets, int)):
            continue
        yield Observation(time, str(skill), name, kind, events, targets)


def timeline_data(actor, player):
    """Copy only display fields. The analysed actor and the upload payload stay untouched."""
    history = _field(actor, "bh", None)
    people = _field(actor, "occResult", {}) or {}
    entry = people.get(player, {})
    result = entry.get("result", {})
    overall = result.get("overall") or {}
    config = _field(_field(actor, "config", None), "item", {}) or {}
    masked = any(str(flag).lower() in ("1", "true") for flag in
                 (_field(actor, "mask", None), config.get("general", {}).get("mask"), overall.get("mask")))
    roster = _field(_field(_field(actor, "bld", None), "info", None), "player", {}) or {}
    player_names = {key: _field(obj, "name") for key, obj in roster.items() if _field(obj, "name", None)}
    player_names.update(_field(actor, "playerNames", {}) or {})
    names = {str(name).strip('"') for name in player_names.values()}
    names.update(str(row["name"]).strip('"') for row in (_field(actor, "statDict", []) or [])
                 if isinstance(row, dict) and row.get("name"))
    names.update(str(name).strip('"') for name in people)
    if overall.get("playerID"):
        names.add(str(overall["playerID"]).strip('"'))
    personal_names = sorted((n for n in names if n), key=len, reverse=True)
    pattern = re.compile("|".join(map(re.escape, personal_names))) if masked and personal_names else None

    def display(value):
        value = str(value or "").strip('"')
        return pattern.sub("队员", value) if pattern else value

    observations = []
    if player is None:
        replay = dict(_field(history, "log", {}) or {})
        replay["badPeriodDps"] = _field(history, "badPeriodDpsLog", [])
        replay["badPeriodHealer"] = _field(history, "badPeriodHealerLog", [])
    else:
        replay = result.get("replay") or {}
        if not replay:
            if not hasattr(actor, "personalTimelines") and hasattr(actor, "bld"):
                actor.personalTimelines = build_personal_timelines(actor)
            saved = (_field(actor, "personalTimelines", {}) or {}).get(player, [])
            observations = list(_observations(saved))
            if observations and history is not None:
                log = _field(history, "log", {})
                key = next((key for key, name in player_names.items() if name == player), None)
                calls = log.get("call") or {}
                replay = {"environment": log.get("environment", []),
                          "call": calls.get(key, []) if isinstance(calls, dict) else [],
                          "badPeriodDps": _field(history, "badPeriodDpsLog", [])}
    # BattleHistory can extend through victory announcements after the analysed
    # encounter. Only a specialist replay owns an independent personal time range.
    specialist = (result.get("replay") or {}) if player is not None else {}
    actor_start = number(_field(actor, "startTime"), number(_field(history, "startTime")))
    actor_end = number(_field(actor, "finalTime"), number(_field(history, "finalTime"), None))
    start = number(specialist.get("startTime"), actor_start)
    personal_span = number(overall.get("sumTime"), None)
    fallback_end = start + personal_span if specialist and personal_span is not None else actor_end
    final = number(specialist.get("finalTime"), fallback_end)
    duration = max(0, final-start) if final is not None else 0
    observations = [row for row in observations if row.time >= start and (final is None or row.time <= final)]
    if final is None and observations:
        duration = max(row.time-start for row in observations)
    marks = []
    exports = []
    occ = str(entry.get("occ") or "")
    talents = {v for v in (result.get("qixue") or {}).values() if isinstance(v, str)}
    uses = {}
    resource_icons = {}
    channel_casts = []
    # Skill timings belong to the Cangsheng release. An older replay keeps its
    # own normal/special classification and recorded durations.
    stamp = number(overall.get("battleTime"), number(_field(actor, "timestamp")))
    current_rules = 1793228400 <= stamp < 1797807600

    def action_lane(name, time, fallback, is_use=True, native_id=None, channel=None, icon=""):
        if not (current_rules or channel):
            return fallback
        spec = skill_timing(occ, name, talents, native_id,
                            hxpy_triggers_gcd=replay.get("hxpyTriggersGcd"))
        if not spec:
            return fallback
        seconds, charges, gcd = spec
        if seconds and is_use and is_healing_resource(occ, name, talents):
            uses.setdefault(name, (seconds, charges, []))[2].append(time)
            if icon:
                resource_icons[name] = icon
        return NORMAL if gcd else SPECIAL

    def event(row, track, color, target=None):
        nonlocal duration
        if not isinstance(row, dict) or row.get("start") is None:
            return
        time = number(row["start"])-start
        end = time + max(0, number(row.get("duration")))
        raw_name = str(row.get("skillname") or "").strip('"')
        if track in (PHASES, MECHANICS) and raw_name.split("·", 1)[0] in ROUTINE_BOSS_LABELS:
            return
        name = display(raw_name) or "未命名事件"
        icon = str(row.get("iconid", ""))
        if (time < 0 and end <= 0) or (final is not None and time > duration):
            return
        if final is None:
            duration = max(duration, end)
        if time >= 0 and track in (MECHANICS, PHASES):
            exports.append((time, name, icon != "341"))
        count = int(number(row.get("num"), 1))
        label = name if count <= 1 or track in (NORMAL, SPECIAL) else f"{name} ×{count}"
        detail = []
        ticks = row.get("ticks")
        if ticks is not None:
            ticks = int(number(ticks))
            detail.append(f"引导 {ticks} 跳")
            if row.get("partial"):
                detail.append("开场时已在引导")
        elif count > 1 and track in (NORMAL, SPECIAL):
            detail.append(f"原记录计数 {count}")
        if row.get("description"):
            detail.append(display(row["description"]))
        target = target or row.get("targetName")
        if target:
            detail.append("目标 " + ("队员" if masked else display(target)))
        for field, caption in (("healeff", "有效治疗"), ("damageeff", "有效伤害")):
            if row.get(field):
                detail.append(f"{caption} {number(row[field]):,.0f}")
        resolved = track != MECHANICS or icon != "341"
        channel = None
        lane = track
        source = (track, row.get("skillid"))
        if track in (NORMAL, SPECIAL):
            channel = healer_channel(occ, raw_name, str(row.get("skillid") or ""))
            lane = action_lane(channel or raw_name, max(0, time), track, time >= 0, channel=channel, icon=icon)
            track = lane
        mark = Mark(max(0, time), min(duration, end), track, label, str(row.get("color") or color),
                    " · ".join(detail), icon, resolved, skill_name=name, lane=lane, ticks=ticks)
        if channel:
            channel_casts.append((mark, source, channel))
        else:
            marks.append(mark)

    casts = {row.skill for row in observations if row.kind == "施放"}
    fallback = set()
    if observations and not casts and not any(row.kind == "招式命中" for row in observations):
        counts = Counter(row.skill for row in observations)
        fallback = {skill for skill, _ in counts.most_common(3)}
    for row in observations:
        time = row.time-start
        channel = None
        lane = row.kind
        icon = ACTION_ICONS.get(row.skill) or CAST_ICONS.get(row.skill, "")
        if row.kind == "施放":
            detail, color, focus = "JCL 原生施放开始", "#247e78", True
            channel = healer_channel(occ, row.name, row.skill)
            lane = action_lane(row.name, time, row.kind, native_id=row.skill, channel=channel, icon=icon)
        else:
            detail = f"{row.targets} 个目标 · {row.events} 条同刻结算记录"
            color = "#4b758f" if row.kind == "招式命中" else "#797b8e"
            focus = (row.kind == "招式命中" and row.skill not in casts) or row.skill in fallback
        mark = Mark(time, time, row.kind, display(row.name), color,
                    f"{detail} · 技能 ID {row.skill}", icon, focus, lane=lane)
        if channel:
            channel_casts.append((mark, (row.kind, row.skill), channel))
        else:
            marks.append(mark)
    if player is not None:
        for row in replay.get("normal") or []:
            event(row, NORMAL, "#287d73")
        for row in replay.get("special") or []:
            event(row, SPECIAL, "#976a2f")
    # Old replays may contain both the shell and action for the same channel
    # start. Keep the earliest cast and the separately recorded channel band.
    previous_time = None
    previous_source = None
    for mark, source, channel in sorted(channel_casts, key=lambda item: item[0].start):
        if previous_time is not None and (mark.start == previous_time or
                (source != previous_source and mark.start - previous_time <= 100)):
            continue
        if mark.lane == SPECIAL:
            cast_key = "zwjtCasts" if channel == "醉舞九天" else "hxpyCasts"
            if isinstance(replay.get(cast_key), list):
                continue
            color = BANDS["zwjt" if channel == "醉舞九天" else "hxpy"][1]
            mark = replace(mark, track=channel, lane="引导起手", band=True, end=mark.start, color=color)
        marks.append(mark)
        previous_time, previous_source = mark.start, source
    calls = replay.get("call") or []
    if isinstance(calls, dict):
        for key, rows in calls.items():
            target = player_names.get(key)
            for row in rows:
                event(row, CALLS, "#b15e42", target)
    else:
        for row in calls:
            event(row, CALLS, "#b15e42")
    for row in replay.get("environment") or []:
        phase = isinstance(row, dict) and row.get("type") == "phase"
        event(row, PHASES if phase else MECHANICS, "#84649d" if phase else "#39769a")
    if player is None:
        phase_times = {mark.start for mark in marks if mark.track == PHASES}
        for row in (_field(actor, "detail", {}) or {}).get("phaseTransitions", []):
            if not isinstance(row, dict) or "time" not in row:
                continue
            time = number(row["time"])-start
            name = row.get("name") or "阶段切换"
            if 0 <= time <= duration and time not in phase_times and name not in ROUTINE_BOSS_LABELS:
                marks.append(Mark(time, time, PHASES, display(name), "#84649d"))
    marks.extend(cooldown_intervals(uses, duration, resource_icons))
    marks.extend(bands(replay, start, duration, occ))
    return duration, marks, exports


def export_text(events, offset, parallel=False):
    lines = [f"{start/1000-offset:.1f},{name};" for start, name, resolved in events
             if resolved and start >= offset*1000]
    if parallel:
        return "".join(lines[::2])+"\n"+"".join(lines[1::2])+"\n"
    return "".join(line+"\n" for line in lines)


@dataclass
class SkillGroup:
    """One label per skill and event source in a strip; records retain the original timeline."""
    name: str
    track: str
    records: list
    times: tuple
    color: QColor
    label: str
    rect: QRect
    points: tuple
    spans: tuple
    axis_y: int = 0


@dataclass
class Strip:
    start: int
    top: int
    bottom: int
    groups: list
    bands: list
    axis_y: int = 0


SKILL_PALETTE = ('#087e80', '#b65328', '#6556aa', '#2475ac', '#ac4175', '#507a2b',
                 '#846116', '#4b69ad', '#a55050', '#328367', '#764f88', '#526e83')
TEXT_FLAGS = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWrapAnywhere


class TimelineCanvas(QAbstractScrollArea):
    selected = Signal(object)
    PAD = 10

    def __init__(self, duration, *, parent=None):
        super().__init__(parent)
        self.duration = max(0, duration)
        self.marks = []
        self.rows = []
        self.ends = []
        self.hits = []
        self.choice = None
        self.seconds = 0
        self.layout_key = None
        self.setAccessibleName("分行战斗时间轴")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setSingleStep(42)
        self.viewport().setMouseTracking(True)

    def set_marks(self, marks):
        self.marks = marks
        self.choice = None
        self.verticalScrollBar().setValue(0)
        self.relayout()

    def set_seconds(self, seconds):
        self.seconds = seconds
        self.choice = None
        self.relayout()

    def relayout(self):
        width = self.viewport().width()
        seconds = self.seconds or (60 if width >= 660 else 30 if width >= 400 else 15)
        key = (width, seconds, id(self.marks), self.font().toString())
        if key != self.layout_key:
            self.layout_key = key
            self.build_rows(width, seconds * 1000)
        bar = self.verticalScrollBar()
        bar.setPageStep(max(1, self.viewport().height()))
        bar.setRange(0, max(0, self.content_height - self.viewport().height()))
        self.hits.clear()
        self.viewport().update()

    def build_rows(self, width, span):
        fm = self.fontMetrics()
        self.line = fm.height()
        self.span = span
        labels = sorted({m.track for m in self.marks if m.band})
        self.gutter = min(max(58, max((fm.horizontalAdvance(s) + 12 for s in labels), default=0)),
                          max(58, width // 4))
        self.plot = max(10, width - self.gutter - self.PAD)
        self.rows, self.ends = [], []
        self.content_height = 0
        if not self.marks:
            return
        count = max(1, ceil(self.duration / span))
        events = [{} for _ in range(count)]
        bands_by_row = [{} for _ in range(count)]
        palette = {}
        for mark in self.marks:
            first = min(count - 1, int(mark.start // span))
            # Use half-open intervals except for a point on the encounter's final instant.
            last = min(count - 1, max(first, ceil(mark.end / span) - 1))
            if mark.band:
                for index in range(first, last + 1):
                    bands_by_row[index].setdefault(mark.track, []).append(mark)
                continue
            # A boss cast, its phase annotation, and its target calls can describe
            # the same mechanic. A player's cast and a resulting hit remain distinct.
            track = '首领' if mark.track in (PHASES, MECHANICS, CALLS) else mark.track
            identity = (track, mark.skill_name or mark.name)
            if identity not in palette:
                palette[identity] = QColor(SKILL_PALETTE[len(palette) % len(SKILL_PALETTE)])
            for index in range(first, last + 1):
                events[index].setdefault(identity, []).append(mark)

        # A strip has exactly one time axis. Arrange labels on both sides,
        # then apply the largest required label/band area to every strip.
        layouts = []
        max_lanes = 2
        label_height = self.line + 4
        for index, items in enumerate(events):
            start = index * span
            groups = [self.group_records(identity, records, start, width, palette[identity])
                      for identity, records in items.items()]
            lanes = []
            for group in sorted(groups, key=lambda g: g.points[0]):
                label_height = max(label_height, group.rect.height())
                # Place near the event. Try a new lane before displacing a label
                # far from its tick. Multiple truly simultaneous labels can fan out.
                pos = group.rect.left()
                lane = next((i for i, right in enumerate(lanes)
                             if max(right + 5, pos) + group.rect.width() <= width - self.PAD
                             and right + 5 <= pos + min(38, self.plot // 7)), len(lanes))
                if lane == len(lanes):
                    lanes.append(self.gutter - 5)
                group.rect.moveLeft(max(lanes[lane] + 5, pos))
                lanes[lane] = group.rect.right()
                group.rect.moveTop(lane)
            max_lanes = max(max_lanes, len(lanes))
            layouts.append(groups)
        lane_pitch = label_height + 3
        band_pitch = max(16, self.line + 1)
        above = (max_lanes + 1) // 2
        axis_offset = self.line + 5 + above * lane_pitch + 6
        band_offset = axis_offset + 6 + (max_lanes // 2) * lane_pitch
        height = band_offset + len(labels) * band_pitch + 5
        for index, groups in enumerate(layouts):
            start = index * span
            top = index * height
            axis = top + axis_offset
            for group in groups:
                lane = group.rect.top()
                group.axis_y = axis
                if lane % 2:
                    group.rect.moveTop(axis + 6 + (lane // 2) * lane_pitch)
                else:
                    group.rect.moveBottom(axis - 6 - (lane // 2) * lane_pitch)
            band_layout = []
            for band_index, track in enumerate(labels):
                y = top + band_offset + band_index * band_pitch
                intervals = [(QRect(self.time_x(m.start, start), y + 2,
                                    max(1, self.time_x(m.end, start) - self.time_x(m.start, start)), band_pitch - 4), m)
                             for m in bands_by_row[index].get(track, ())]
                if intervals:
                    band_layout.append((y, track, intervals))
            self.rows.append(Strip(start, top, top + height, groups, band_layout, axis))
            self.ends.append(top + height)
        self.content_height = len(self.rows) * height

    def group_records(self, identity, records, start, width, color):
        track, name = identity
        fm = self.fontMetrics()
        records.sort(key=lambda m: m.start)
        # Prefer the boss's recorded event over near-simultaneous target
        # notifications for that same skill. Keep exact target times in details.
        primary = sorted({m.start for m in records if m.track != CALLS})
        times = set(primary)
        previous_call = None
        for m in records:
            if m.track != CALLS:
                continue
            i = bisect_right(primary, m.start)
            if track == '首领' and any(abs(t - m.start) <= 500 for t in primary[max(0, i - 1):i + 1]):
                continue
            if previous_call is None or m.start - previous_call > 250:
                times.add(m.start)
                previous_call = m.start
        times = sorted(times)
        points = tuple(self.time_x(t, start) for t in times)
        ranges = tuple((self.time_x(m.start, start), self.time_x(m.end, start))
                       for m in records if m.end > m.start)
        label = name if len(times) == 1 else f"{name} ×{len(times)}"
        if track in ("招式命中", "技能效果"):
            label += " · 命中" if track == "招式命中" else " · 效果"
        stamp = clock(max(start, times[0]))
        label_width = min(self.plot, max(fm.horizontalAdvance(label), fm.horizontalAdvance(stamp)) + 10)
        left = max(self.gutter, min(width - self.PAD - label_width, points[0] - label_width // 2))
        height = max(self.line, fm.boundingRect(QRect(0, 0, label_width - 4, 10000), TEXT_FLAGS, label).height())
        return SkillGroup(name, track, records, tuple(times), color, label,
                         QRect(left, 0, label_width, height + 3), points, ranges)

    def time_x(self, time, start):
        return self.gutter + round(min(1, max(0, (time - start) / self.span)) * self.plot)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout()

    def scrollContentsBy(self, dx, dy):
        self.hits.clear()
        self.viewport().update()

    def paintEvent(self, _event):
        p = QPainter(self.viewport())
        self.hits = []
        try:
            self.paint_rows(p, self.viewport().width(), self.viewport().height(),
                            self.verticalScrollBar().value(), self.hits)
        finally:
            p.end()

    def paint_rows(self, p, width, height, scroll, hits=None):
        p.fillRect(0, 0, width, height, QColor("#ffffff"))
        if not self.rows:
            p.setPen(QColor("#57717b"))
            p.drawText(QRect(5, 5, width - 10, 48), Qt.AlignCenter, "当前范围没有时间轴记录")
            return
        p.save()
        p.setFont(self.font())
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(0, -scroll)
        for index in range(bisect_right(self.ends, scroll), len(self.rows)):
            strip = self.rows[index]
            if strip.top >= scroll + height:
                break
            p.fillRect(0, strip.top, width, strip.bottom - strip.top,
                       QColor("#f2f6f6" if index % 2 == 0 else "#ffffff"))
            axis = strip.axis_y
            limit = self.time_x(self.duration, strip.start)
            p.setPen(QColor("#456569"))
            p.drawText(QRect(2, axis - self.line // 2, self.gutter - 10, self.line + 2),
                       Qt.AlignRight | Qt.AlignVCenter, clock(strip.start).split('.')[0])
            p.setPen(QPen(QColor("#9db7ba"), 1))
            p.drawLine(self.gutter, axis, limit, axis)
            for tick in range(1, 7):
                x = self.gutter + round(tick * self.plot / 6)
                if x <= limit:
                    p.drawLine(x, axis - 3, x, axis + 3)
                    seconds = clock(strip.start + self.span * tick / 6).split('.')[0]
                    tick_width = p.fontMetrics().horizontalAdvance(seconds) + 4
                    if self.plot / 6 >= tick_width + 3 or tick % 2 == 0:
                        p.setPen(QColor("#60777a"))
                        p.drawText(QRect(min(x-tick_width//2, width-self.PAD-tick_width),
                                         strip.top+1, tick_width, self.line), Qt.AlignCenter, seconds)
                        p.setPen(QPen(QColor("#9db7ba"), 1))
            for g in strip.groups:
                edge = g.rect.bottom() if g.rect.bottom() < axis else g.rect.top()
                p.setPen(QPen(g.color, 1))
                p.drawLine(g.points[0], axis, g.rect.center().x(), edge)
                p.setPen(QPen(g.color, 2))
                for a, b in g.spans:
                    p.drawLine(a, axis, b, axis)
                p.setBrush(QColor("#ffffff"))
                pixels = dict.fromkeys(g.points)
                for x in pixels:
                    p.drawEllipse(x - 2, axis - 2, 5, 5)
                color = QColor(g.color)
                color.setAlpha(52 if self.choice is g else 22)
                p.fillRect(g.rect, QColor("#ffffff"))
                p.fillRect(g.rect, color)
                p.setPen(g.color.darker(120))
                p.drawText(g.rect, TEXT_FLAGS, g.label)
                if hits is not None:
                    hits.append((g.rect.translated(0, -scroll), g))
                    hits.extend((QRect(x - 3, axis - scroll - 3, 7, 7), g) for x in pixels)
            for y, track, intervals in strip.bands:
                if y + self.line < scroll or y > scroll + height:
                    continue
                p.setPen(QColor("#64747a"))
                p.drawText(QRect(1, y, self.gutter - 8, self.line), Qt.AlignRight | Qt.AlignVCenter, track)
                for rect, mark in intervals:
                    color = QColor(mark.color)
                    color.setAlphaF(.12 + .80 * mark.intensity)
                    p.fillRect(rect, color)
                    if rect.width() > p.fontMetrics().horizontalAdvance(mark.name) + 5:
                        p.setPen(QColor("#ffffff" if color.alphaF() > .65 and color.lightnessF() < .53 else "#274246"))
                        p.drawText(rect, Qt.AlignCenter, mark.name)
                    if hits is not None:
                        hits.append((rect.translated(0, -scroll), mark))
        p.restore()

    @staticmethod
    def describe(mark):
        if isinstance(mark, SkillGroup):
            span = clock(mark.times[0])
            end = max(m.end for m in mark.records)
            if end > mark.times[0]:
                span += f" – {clock(end)}"
            kinds = " / ".join(dict.fromkeys(m.track for m in mark.records))
            return f"{span}  ·  {kinds}  ·  {mark.name}  ·  {len(mark.records)} 条记录"
        span = clock(mark.start)
        if mark.end > mark.start:
            span += f" – {clock(mark.end)}"
        return "  ·  ".join(filter(None, (span, mark.track, mark.name, mark.detail)))

    def mousePressEvent(self, event):
        selected = next((m for rect, m in self.hits if rect.contains(event.position().toPoint())), None)
        if selected is not None:
            self.choice = selected
            self.selected.emit(selected)
            self.viewport().update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        selected = next((m for rect, m in self.hits if rect.contains(event.position().toPoint())), None)
        if selected is None:
            QToolTip.hideText()
        else:
            detail = escape(self.describe(selected)).replace("\n", "<br>")
            QToolTip.showText(event.globalPosition().toPoint(), "<p>" + detail + "</p>", self)

    def export_height(self, width):
        return max(50, self.content_height)

    def paint_export(self, painter, width, height, top):
        self.paint_rows(painter, width, height, top)

    def save_png(self, filename, title=""):
        """Paint the complete sheet in strips, even when it is taller than Qt's raster limit."""
        width = self.viewport().width()
        header = self.line + 18 if title else 0
        height = header + self.export_height(width)
        file = QSaveFile(str(filename))
        if not file.open(QIODevice.OpenModeFlag.WriteOnly):
            raise OSError(file.errorString())

        def write(data):
            if file.write(data) != len(data):
                raise OSError(file.errorString())

        def chunk(tag, data):
            write(struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data)))

        try:
            write(b"\x89PNG\r\n\x1a\n")
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            compressor = zlib.compressobj()
            for top in range(0, height, 512):
                image = QImage(width, min(512, height - top), QImage.Format.Format_RGB888)
                if image.isNull():
                    raise OSError("无法创建时间轴图像。")
                p = QPainter(image)
                try:
                    self.paint_export(p, width, image.height(), top - header)
                    if top == 0 and title:
                        p.fillRect(0, 0, width, header, QColor("#e7eeee"))
                        p.setFont(self.font())
                        p.setPen(QColor("#234a50"))
                        p.drawText(QRect(8, 0, width - 16, header), Qt.AlignVCenter, title)
                finally:
                    p.end()
                pixels = image.constBits()
                stride = image.bytesPerLine()
                raw = b"".join(b"\x00" + pixels[i * stride:i * stride + width * 3].tobytes()
                             for i in range(image.height()))
                compressed = compressor.compress(raw)
                if compressed:
                    chunk(b"IDAT", compressed)
            chunk(b"IDAT", compressor.flush())
            chunk(b"IEND", b"")
            if not file.commit():
                raise OSError(file.errorString())
        except Exception:
            file.cancelWriting()
            raise


@dataclass
class IconCluster:
    start: float
    track: str
    records: list

    @property
    def name(self):
        return self.records[0].name


_ATLAS_INDEX = {str(icon): i for i, icon in enumerate(ATLAS_IDS)}


@lru_cache(maxsize=1)
def action_atlas():
    return QPixmap(get_icon_path("timeline-actions"))


@lru_cache(maxsize=640)
def action_icon(icon):
    if not str(icon).isdigit() or str(icon) in ("0", "341"):
        return QPixmap()
    index = _ATLAS_INDEX.get(str(icon))
    if index is None:
        return QPixmap(get_icon_path(icon))
    return action_atlas().copy((index % 16) * 32, (index // 16) * 32, 32, 32)


class PersonalCanvas(TimelineCanvas):
    """Continuous scrollable time with fixed track labels and viewport-only painting."""
    def __init__(self, duration, *, parent=None):
        super().__init__(duration, parent=parent)
        self.seconds = 40  # pixels/second; enough space for successive GCD icons
        self.setAccessibleName("个人技能时间轴，可左右拖动")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.horizontalScrollBar().setSingleStep(80)
        self.drag_origin = None
        self.dragged = False
        self.lanes = []
        self.starts = []
        self.ends_at = []
        self.content_height = 0

    def set_marks(self, marks):
        self.marks = marks
        self.choice = None
        self.verticalScrollBar().setValue(0)
        self.relayout()

    def set_seconds(self, scale):
        left_time = self.horizontalScrollBar().value() / self.seconds
        super().set_seconds(scale)
        self.horizontalScrollBar().setValue(round(left_time * scale))

    def relayout(self):
        if not hasattr(self, 'lanes'):
            return
        width = self.viewport().width()
        fm = self.fontMetrics()
        self.line = fm.height()
        self.tile = max(21, min(30, self.line + 6))
        self.pitch = self.tile + 6
        self.header = self.line + 8
        captions = {(m.track, m.lane == "调息") for m in self.marks if m.band}
        self.badge = min(20, self.tile)
        caption_width = max((fm.horizontalAdvance(label + " CD") + self.badge + 4 if cd
                             else fm.horizontalAdvance(label) for label, cd in captions), default=0)
        self.gutter = min(max(73, caption_width + 16), max(73, width // 3))
        self.plot = max(1, width - self.gutter - 6)
        scale = self.seconds / 1000
        key = (id(self.marks), self.seconds, self.tile)
        if self.layout_key != key:
            self.layout_key = key
            grouped = defaultdict(list)
            for m in self.marks:
                kind = m.lane or m.track
                if m.band:
                    key = ('cd' if kind == '调息' else 'band', m.track)
                else:
                    key = ('event', MECHANICS if kind == PHASES else kind)
                grouped[key].append(m)
            leading = {label: i for i, label in enumerate(
                (CALLS, MECHANICS, NORMAL, SPECIAL, '施放', '招式命中', '技能效果'))}
            coverage = {'上元': 0, '翔舞': 1, '回雪飘摇': 2, '醉舞九天': 0}

            def lane_order(key):
                kind, label = key
                if kind == 'event':
                    return (0, leading.get(label, len(leading)), label)
                if kind == 'band' and label not in ('输出无效', '治疗无效'):
                    return (1, coverage.get(label, len(coverage)), label)
                return (2 if kind == 'cd' else 3, 0, label)

            keys = sorted(grouped, key=lane_order)
            self.lanes = []
            self.starts = []
            self.ends_at = []
            self.spans = []
            for kind, label in keys:
                records = sorted(grouped[kind, label], key=lambda m:(m.start, -m.end))
                spans = []
                latest_end = []
                if kind == 'event':
                    clusters = []
                    for m in records:
                        if m.end > m.start:
                            spans.append(m)
                            latest_end.append(max(m.end, latest_end[-1] if latest_end else 0))
                        if (label not in (NORMAL, SPECIAL, '施放') and clusters and
                                (m.start - clusters[-1].start) * scale < self.tile + 1):
                            clusters[-1].records.append(m)
                        else:
                            clusters.append(IconCluster(m.start, label, [m]))
                    records = clusters
                self.lanes.append((kind, label, records))
                self.starts.append([r.start for r in records])
                self.spans.append((spans, latest_end))
                self.ends_at.append(list(accumulate((r.end for r in records), max)) if kind != 'event' else ())
            self.rows = self.lanes
        self.content_height = self.header + self.pitch * len(self.lanes) + 4 if self.lanes else 0
        h = self.horizontalScrollBar()
        h.setPageStep(self.plot)
        h.setRange(0, max(0, ceil(self.duration * scale) + self.tile - self.plot) if self.lanes else 0)
        v = self.verticalScrollBar()
        v.setPageStep(max(1,self.viewport().height()))
        v.setRange(0, max(0, self.content_height - self.viewport().height()))
        self.hits.clear()
        self.viewport().update()

    @staticmethod
    def describe(item):
        if isinstance(item, IconCluster):
            return "\n".join(TimelineCanvas.describe(m) for m in item.records[:5]) + (
                f"\n另有 {len(item.records) - 5} 条，可打开明细" if len(item.records) > 5 else "")
        return TimelineCanvas.describe(item)

    def paint_rows(self, p, width, height, scroll, hits=None):
        self.paint_window(p, width, height, scroll, self.horizontalScrollBar().value(), hits)

    def paint_window(self, p, width, height, scroll, offset, hits=None):
        p.fillRect(0, 0, width, height, QColor("#ffffff"))
        if not self.lanes:
            p.setPen(QColor("#57717b"))
            p.drawText(QRect(5, 5, width-10, 45), Qt.AlignCenter, "当前范围没有时间轴记录")
            return
        scale = self.seconds / 1000
        left = offset / scale
        right = (offset + self.plot) / scale
        p.save()
        p.setFont(self.font())
        p.translate(0, -scroll)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        def xpos(t):
            return self.gutter + round(t * scale - offset)
        step = next(t for t in (1000, 2000, 5000, 10000, 30000, 60000) if t * scale >= 60)
        ticks = [(t, xpos(t)) for t in range(ceil(left / step) * step, int(min(self.duration, right)) + 1, step)]
        p.setPen(QColor("#43626c"))
        for t, x in ticks:
            p.drawText(QRect(x+2, 1, 60, self.header), Qt.AlignVCenter, clock(t).split('.')[0])
        for i, (kind, label, records) in enumerate(self.lanes):
            y = self.header + i * self.pitch
            if y+self.pitch <= scroll or y >= scroll+height:
                continue
            tint = "#f0f5f4" if i % 2 == 0 else "#fafcfc"
            p.fillRect(0, y, width, self.pitch, QColor(tint))
            p.save()
            p.setClipRect(QRect(self.gutter, y, self.plot, self.pitch))
            p.setPen(QColor("#d9e5e4"))
            for _, x in ticks:
                p.drawLine(x, y, x, y+self.pitch)
            spans, latest_end = self.spans[i]
            for j in range(bisect_right(latest_end, left), len(spans)):
                m = spans[j]
                if m.start > right:
                    break
                p.fillRect(xpos(m.start), y+self.pitch-3,
                           max(1, xpos(m.end)-xpos(m.start)), 2, QColor(m.color))
            first = (bisect_left(self.starts[i], left - self.tile / scale) if kind == 'event'
                     else bisect_left(self.ends_at[i], left))
            last = bisect_right(self.starts[i], right)
            for j in range(first, last):
                entry = records[j]
                x = xpos(entry.start)
                if kind == 'event':
                    rect = QRect(x, y+2, self.tile, self.tile)
                    if label in (NORMAL, SPECIAL, '施放'):
                        # Each cast has its own hit target even when two actions share a timestamp.
                        start_index = bisect_left(self.starts[i], entry.start)
                        next_index = bisect_right(self.starts[i], entry.start)
                        if next_index < len(records):
                            rect.setWidth(max(1, min(self.tile, xpos(records[next_index].start) - x)))
                        count = next_index - start_index
                        if count > 1:
                            slot = j - start_index
                            rect.setTop(y + 2 + slot * self.tile // count)
                            rect.setBottom(y + 1 + (slot + 1) * self.tile // count)
                    m = entry.records[0]
                    icon = action_icon(m.icon)
                    if not icon.isNull():
                        p.drawPixmap(rect, icon)
                    else:
                        p.fillRect(rect, QColor(m.color))
                        p.setPen(Qt.white)
                        p.drawText(rect, Qt.AlignCenter, (m.skill_name or m.name)[:2])
                    badge = (str(m.ticks) if m.ticks is not None else
                             str(min(99, len(entry.records))) if len(entry.records) > 1 else None)
                    if badge and rect.width() >= 14:
                        b = QRect(rect.right()-13, rect.bottom()-11, 14, 12)
                        p.fillRect(b, QColor("#334555"))
                        p.setPen(Qt.white)
                        font = p.font()
                        font.setPixelSize(10)
                        p.setFont(font)
                        p.drawText(b, Qt.AlignCenter, badge)
                        p.setFont(self.font())
                elif entry.lane == "引导起手" or (entry.lane == "引导" and entry.start == entry.end):
                    rect = QRect(x, y+2, 3, self.pitch-4)
                    p.fillRect(rect, QColor(entry.color))
                else:
                    rect = QRect(x, y+5, max(1, xpos(entry.end) - x), self.pitch-10)
                    color = QColor(entry.color)
                    color.setAlphaF(.12 + .8 * entry.intensity)
                    p.fillRect(rect, color)
                    if entry.lane == "引导":
                        p.fillRect(x, y+2, 2, self.pitch-4, QColor(entry.color))
                    visible = rect.intersected(QRect(self.gutter,y,self.plot,self.pitch))
                    if visible.width() > p.fontMetrics().horizontalAdvance(entry.name) + 8:
                        p.setPen(QColor("#ffffff" if entry.intensity > .7 else "#274246"))
                        p.drawText(visible, Qt.AlignCenter, entry.name)
                if hits is not None:
                    clipped = rect.intersected(QRect(self.gutter,y,self.plot,self.pitch))
                    if not clipped.isEmpty():
                        hits.append((clipped.translated(0,-scroll), entry))
            p.restore()
            p.setPen(QColor("#284951"))
            text = label + " CD" if kind == 'cd' else label
            rect = QRect(3,y,self.gutter-8,self.pitch)
            if kind == 'cd':
                icon = action_icon(records[0].icon)
                if not icon.isNull():
                    p.drawPixmap(QRect(4, y+(self.pitch-self.badge)//2, self.badge, self.badge), icon)
                    rect.setLeft(8+self.badge)
            p.drawText(rect, Qt.AlignRight | Qt.AlignVCenter,
                       p.fontMetrics().elidedText(text, Qt.ElideRight, rect.width()))
        p.restore()

    def export_height(self, width):
        self.page_height = max(50,self.content_height)
        panels = max(1, ceil((self.duration * self.seconds / 1000 + self.tile) / self.plot))
        return self.page_height * panels

    def paint_export(self, p, width, height, top):
        # Wrap the long interactive timeline into consecutive printable panels.
        p.fillRect(0,0,width,height,Qt.white)
        first = max(0,top // self.page_height)
        for index in range(first, ceil((top + height) / self.page_height)):
            y = index * self.page_height - top
            p.save()
            p.translate(0,y)
            p.setClipRect(QRect(0,0,width,self.page_height))
            self.paint_window(p,width,self.page_height,0,index*self.plot)
            p.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_origin = event.position().toPoint()
            self.drag_value = self.horizontalScrollBar().value()
            self.dragged = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_origin is not None:
            dx = event.position().toPoint().x() - self.drag_origin.x()
            if self.dragged or abs(dx) >= QApplication.startDragDistance():
                self.dragged = True
                self.horizontalScrollBar().setValue(self.drag_value - dx)
                self.viewport().setCursor(Qt.ClosedHandCursor)
                QToolTip.hideText()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_origin is not None:
            self.drag_origin = None
            self.viewport().unsetCursor()
            if not self.dragged:
                super().mousePressEvent(event)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class TimelineView(QWidget):
    @classmethod
    def from_actor(cls, actor, player=None, parent=None, *, compact=False):
        view = cls(*timeline_data(actor, player), team=player is None, parent=parent, compact=compact)
        boss = _field(actor, "bossAnalyseName") or (_field(actor, "detail", {}) or {}).get("boss")
        if boss:
            view.title = f"{boss} · {view.title}"
        return view

    def __init__(self, duration, marks, exports, team=False, parent=None, *, compact=False):
        super().__init__(parent)
        self.marks, self.exports = marks, exports
        self.title = "整场时间轴" if team else "个人技能时间轴"
        kinds = {mark.track for mark in marks}
        if "施放" in kinds:
            self.hint = "施放为日志记录的开始时刻。命中和技能效果按同刻同技能合并。"
        elif "技能效果" in kinds and "招式命中" not in kinds:
            self.hint = "仅有可归属的技能效果。重点显示结算记录最多的三种。"
        elif "招式命中" in kinds:
            self.hint = "此记录缺少原生施放时刻。命中和技能效果按同刻同技能合并。"
        elif not marks and not team:
            self.hint = "该角色没有可归属的个人技能记录。"
        else:
            self.hint = "点击技能查看各次发生时间及目标"
        self.canvas = TimelineCanvas(duration, parent=self) if team else PersonalCanvas(duration, parent=self)
        if not team and marks:
            self.hint += " 左右拖动查看施放。CD 色条按基础调息推算，充能技能标记可用层数。"
        layout = QVBoxLayout(self)
        if compact:
            layout.setContentsMargins(2, 0, 2, 0)
        else:
            layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(3)
        bar = QHBoxLayout()
        self.scope = QComboBox()
        self.scope.addItems(["重点记录", "全部记录"])
        self.scope.setCurrentIndex(int(team))
        self.scope.setToolTip("重点显示已识别机制及个人主动技能。全部记录含其他命中、效果和未辨识的机制。")
        bar.addWidget(self.scope)
        self.zoom = QComboBox()
        zoom_options = (("自动分行", 0), ("每行 30 秒", 30), ("每行 1 分钟", 60), ("每行 2 分钟", 120)) if team else (
            ("标准间距", 40), ("紧凑间距", 24), ("放大间距", 72))
        for name, val in zoom_options:
            self.zoom.addItem(name, val)
        self.zoom.setToolTip("缩短每行时长可拉开临近技能。" if team else self.hint)
        bar.addWidget(self.zoom)
        self.summary = QLabel()
        bar.addWidget(self.summary)
        bar.addStretch()
        self.details_button = QToolButton()
        self.details_button.setText("明细")
        self.details_button.setEnabled(False)
        self.details_button.clicked.connect(self.show_details)
        bar.addWidget(self.details_button)
        export = QToolButton()
        export.setText("导出")
        export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(export)
        menu.addAction("保存整张时间轴图…", self.save_image)
        if exports:
            menu.addSeparator()
            row = QWidget(menu)
            options = QHBoxLayout(row)
            self.offset = QDoubleSpinBox()
            self.offset.setRange(-86400, max(86400, duration / 1000))
            self.offset.setSuffix(" 秒")
            self.offset.setAccessibleName("导出起始偏移")
            options.addWidget(QLabel("文本起点"))
            options.addWidget(self.offset)
            action = QWidgetAction(menu)
            action.setDefaultWidget(row)
            menu.addAction(action)
            menu.addAction("复制线性轴", self.copy_linear)
            menu.addAction("复制双排轴", self.copy_parallel)
        export.setMenu(menu)
        bar.addWidget(export)
        layout.addLayout(bar)
        layout.addWidget(self.canvas, 1)
        self.detail = QLabel(self.hint)
        self.detail.setTextFormat(Qt.PlainText)
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail)
        if compact:
            self.detail.hide()
        self.scope.currentIndexChanged.connect(self.change_scope)
        self.zoom.currentIndexChanged.connect(self.change_zoom)
        self.canvas.selected.connect(self.select_record)
        self.change_scope(self.scope.currentIndex())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.summary.setVisible(self.width() >= 505)

    def select_record(self, record):
        self.detail.setText(self.canvas.describe(record))
        self.details_button.setEnabled(True)
        self.details_button.setToolTip(self.canvas.describe(record))

    def show_details(self):
        record = self.canvas.choice
        if record is None:
            return
        rows = record.records if isinstance(record, (SkillGroup, IconCluster)) else [record]
        dialog = QDialog(self)
        dialog.setWindowTitle(record.name + " · 时间轴明细")
        dialog.resize(530, 360)
        layout = QVBoxLayout(dialog)
        data = QPlainTextEdit()
        data.setReadOnly(True)
        data.setPlainText("\n".join(self.canvas.describe(mark) for mark in rows))
        layout.addWidget(data)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(dialog.reject)
        layout.addWidget(close)
        dialog.exec()

    def change_scope(self, index):
        marks = self.marks if index else [m for m in self.marks if m.focused]
        self.canvas.set_marks(marks)
        records = sum(not m.band for m in marks)
        self.summary.setText(f"{clock(self.canvas.duration)}  ·  {records} 条")
        self.detail.setText(self.hint)
        self.details_button.setEnabled(False)

    def change_zoom(self, index):
        self.canvas.set_seconds(self.zoom.itemData(index))
        self.detail.setText(self.hint)
        self.details_button.setEnabled(False)

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存整张时间轴图", "时间轴.png", "PNG 图像 (*.png)")
        if filename:
            try:
                self.canvas.save_png(filename, f"{self.title}    {self.scope.currentText()}    {clock(self.canvas.duration)}")
                self.detail.setText("已保存整张时间轴图")
            except OSError as error:
                QMessageBox.warning(self, "保存失败", str(error))

    def copy_linear(self):
        self.copy_axis(False)

    def copy_parallel(self):
        self.copy_axis(True)

    def copy_axis(self, parallel):
        QApplication.clipboard().setText(export_text(self.exports, self.offset.value(), parallel))
        self.detail.setText("已复制双排时间轴" if parallel else "已复制线性时间轴")

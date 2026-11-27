"""Qt timelines for boss mechanics and personal replays. Times in the view are milliseconds."""
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from html import escape
from itertools import groupby
from math import ceil, isfinite
import re
import struct
import zlib

from PySide6.QtCore import QIODevice, QRect, QSaveFile, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractScrollArea, QApplication, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QHBoxLayout, QLabel, QMenu, QMessageBox, QPlainTextEdit,
    QToolButton, QToolTip, QVBoxLayout, QWidget, QWidgetAction,
)

from data.PersonalTimeline import ACTION_ICONS, Observation, build_personal_timelines


MECHANICS = "首领机制"
PHASES = "阶段切换"
CALLS = "机制点名"
NORMAL = "常规技能"
SPECIAL = "特殊技能"
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

    def event(row, track, color, target=None):
        nonlocal duration
        if not isinstance(row, dict) or row.get("start") is None:
            return
        time = number(row["start"])-start
        end = time + max(0, number(row.get("duration")))
        name = display(row.get("skillname")) or "未命名事件"
        icon = str(row.get("iconid", ""))
        if (time < 0 and end <= 0) or (final is not None and time > duration):
            return
        if final is None:
            duration = max(duration, end)
        if time >= 0 and track in (MECHANICS, PHASES):
            exports.append((time, name, icon != "341"))
        count = int(number(row.get("num"), 1))
        label = name if count <= 1 else f"{name} ×{count}"
        detail = []
        if row.get("description"):
            detail.append(display(row["description"]))
        target = target or row.get("targetName")
        if target:
            detail.append("目标 " + ("队员" if masked else display(target)))
        for field, caption in (("healeff", "有效治疗"), ("damageeff", "有效伤害")):
            if row.get(field):
                detail.append(f"{caption} {number(row[field]):,.0f}")
        resolved = track != MECHANICS or icon != "341"
        mark = Mark(max(0, time), min(duration, end), track, label, str(row.get("color") or color),
                    " · ".join(detail), icon, resolved, skill_name=name)
        marks.append(mark)

    casts = {row.skill for row in observations if row.kind == "施放"}
    fallback = set()
    if observations and not casts and not any(row.kind == "招式命中" for row in observations):
        counts = Counter(row.skill for row in observations)
        fallback = {skill for skill, _ in counts.most_common(3)}
    for row in observations:
        time = row.time-start
        if row.kind == "施放":
            detail, color, focus = "JCL 原生施放开始", "#247e78", True
        else:
            detail = f"{row.targets} 个目标 · {row.events} 条同刻结算记录"
            color = "#4b758f" if row.kind == "招式命中" else "#797b8e"
            focus = (row.kind == "招式命中" and row.skill not in casts) or row.skill in fallback
        marks.append(Mark(time, time, row.kind, display(row.name), color,
                          f"{detail} · 技能 ID {row.skill}", ACTION_ICONS.get(row.skill, ""), focus))
    for row in replay.get("normal") or []:
        event(row, NORMAL, "#287d73")
    for row in replay.get("special") or []:
        event(row, SPECIAL, "#976a2f")
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
            if 0 <= time <= duration and time not in phase_times:
                marks.append(Mark(time, time, PHASES, display(row.get("name") or "阶段切换"), "#84649d"))
    marks.extend(bands(replay, start, duration, entry.get("occ")))
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


SKILL_PALETTE = ('#087e80', '#b65328', '#6556aa', '#2475ac', '#ac4175', '#507a2b',
                 '#846116', '#4b69ad', '#a55050', '#328367', '#764f88', '#526e83')
TEXT_FLAGS = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWrapAnywhere


class TimelineCanvas(QAbstractScrollArea):
    selected = Signal(object)
    PAD = 10

    def __init__(self, duration, *, compact=False, parent=None):
        super().__init__(parent)
        self.duration = max(0, duration)
        self.marks = []
        self.rows = []
        self.ends = []
        self.hits = []
        self.choice = None
        self.seconds = -1 if compact else 0
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
            self.build_rows(width, max(1, self.duration) if seconds == -1 else seconds * 1000)
        bar = self.verticalScrollBar()
        bar.setPageStep(max(1, self.viewport().height()))
        bar.setRange(0, max(0, self.content_height - self.viewport().height()))
        self.hits.clear()
        self.viewport().update()

    def build_rows(self, width, span):
        fm = self.fontMetrics()
        self.line = fm.height()
        self.span = span
        labels = [m.track for m in self.marks if m.band]
        if self.seconds == -1:
            labels.extend((m.skill_name or m.name) + " ×99 · 命中" for m in self.marks if not m.band)
        self.gutter = min(max(61, max((fm.horizontalAdvance(s) + 13 for s in set(labels)), default=0)),
                          max(61, min(220, width // 3)))
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

        y = 0
        for index in range(count):
            start = index * span
            top = y
            groups = [self.group_records(identity, records, start, width, palette[identity])
                      for identity, records in events[index].items()]
            y = self.place_labels(groups, start, y)
            bands_layout = []
            for track, records in bands_by_row[index].items():
                height = max(15, self.line)
                intervals = [(QRect(self.time_x(m.start, start), y + 2,
                                    max(1, self.time_x(m.end, start) - self.time_x(m.start, start)), height - 4), m)
                             for m in sorted(records, key=lambda m:m.start)]
                bands_layout.append((y, track, intervals))
                y += height
            y += 6
            self.rows.append(Strip(start, top, y, groups, bands_layout))
            self.ends.append(y)
        self.content_height = y

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
        if times[0] < start:
            label = "续 · " + label
        stamp = clock(max(start, times[0]))
        label_width = min(self.plot, max(fm.horizontalAdvance(label), fm.horizontalAdvance(stamp)) + 10)
        left = max(self.gutter, min(width - self.PAD - label_width, points[0] - label_width // 2))
        height = max(self.line, fm.boundingRect(QRect(0, 0, label_width - 4, 10000), TEXT_FLAGS, label).height())
        return SkillGroup(name, track, records, tuple(times), color, label,
                         QRect(left, 0, label_width, height + 3), points, ranges)

    def place_labels(self, groups, start, y):
        fm = self.fontMetrics()
        # Reserve space for the full text and every tick belonging to a group's
        # time range. Two coincident labels go on separate aligned baselines.
        if self.seconds == -1:
            y += self.line + 6
            groups.sort(key=lambda g: (g.track in ('首领', MECHANICS, PHASES, CALLS), g.times[0], g.name))
            for group in groups:
                caption = QRect(4, y, self.gutter - 12, 0)
                height = fm.boundingRect(QRect(0, 0, caption.width(), 10000), TEXT_FLAGS, group.label).height()
                caption.setHeight(max(self.line, height) + 3)
                group.rect = caption
                group.axis_y = caption.center().y()
                y += caption.height()
        else:
            lanes = []
            groups.sort(key=lambda g: (min(g.rect.left(), g.points[0]), g.times[0], g.name))
            time_width = fm.horizontalAdvance(clock(start + self.span)) // 2 + 3
            for group in groups:
                left = min(group.rect.left(), group.points[0] - time_width)
                right = max(group.rect.right(), group.points[-1] + time_width,
                            max((b for _, b in group.spans), default=0))
                lane = next((lane for lane in lanes if lane[0] + 5 < left), None)
                if lane is None:
                    lane = [0, []]
                    lanes.append(lane)
                lane[0] = right
                lane[1].append(group)
            y += 4
            for _, lane in lanes or [(0, [])]:
                axis_y = y + self.line + 3
                for group in lane:
                    group.axis_y = axis_y
                    group.rect.moveTop(axis_y + 4)
                y = axis_y + 4 + max((g.rect.height() for g in lane), default=5) + 2
        return y

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
            first_y = strip.top + 4 + self.line + 3
            p.setPen(QColor("#426369"))
            if self.seconds == -1:
                step = next((s for s in (1, 5, 10, 15, 30, 60, 120, 300, 600, 1800)
                             if s * 1000 * self.plot / self.span >= 70), max(1800, ceil(self.span / 4000)))
                for sec in range(0, ceil(self.span / 1000), step):
                    x = self.time_x(sec * 1000, 0)
                    if x + 48 < width:
                        p.drawText(QRect(x, strip.top, 48, self.line + 4), Qt.AlignVCenter, clock(sec * 1000)[:-2])
            else:
                p.drawText(QRect(4, first_y - self.line // 2, self.gutter - 13, self.line + 2),
                           Qt.AlignRight | Qt.AlignVCenter, clock(strip.start).split('.')[0])
            groups = [g for g in strip.groups if g.rect.bottom() >= scroll
                      and g.axis_y - self.line - 3 < scroll + height]
            axes = {g.axis_y for g in groups}
            if self.seconds != -1:
                axes.add(first_y)
            for axis in sorted(axes):
                p.setPen(QPen(QColor("#c1d2d4"), 1))
                limit = self.time_x(self.duration, strip.start)
                p.drawLine(self.gutter, axis, limit, axis)
                for tick in range(6):
                    x = self.gutter + round(tick * self.plot / 5)
                    if x <= limit:
                        p.drawLine(x, axis - 3, x, axis + 3)
            for g in groups:
                p.setPen(QPen(g.color, 2))
                for a, b in g.spans:
                    p.drawLine(a, g.axis_y, b, g.axis_y)
                p.setBrush(QColor("#ffffff"))
                pixels = dict.fromkeys(g.points)
                for x in pixels:
                    p.drawEllipse(x - 3, g.axis_y - 3, 6, 6)
                if self.choice is g and hits is not None:
                    p.fillRect(g.rect, QColor("#d5e7e4"))
                p.setPen(QColor("#486168"))
                if self.seconds != -1:
                    end = -1
                    for t, x in zip(g.times, g.points):
                        stamp = clock(max(strip.start, t))
                        label_width = p.fontMetrics().horizontalAdvance(stamp) + 4
                        left = max(self.gutter, min(width - self.PAD - label_width, x - label_width // 2))
                        if left > end:
                            p.drawText(QRect(left, g.axis_y - self.line - 3, label_width, self.line), Qt.AlignCenter, stamp)
                            end = left + label_width + 3
                p.setPen(QColor("#183d42"))
                flags = Qt.AlignRight | Qt.AlignVCenter | Qt.TextWrapAnywhere if self.seconds == -1 else TEXT_FLAGS
                p.drawText(g.rect, flags, g.label)
                if hits is not None:
                    hits.append((g.rect.translated(0, -scroll), g))
                    hits.extend((QRect(x - 4, g.axis_y - scroll - 4, 9, 9), g) for x in pixels)
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
            QToolTip.showText(event.globalPosition().toPoint(), "<p>" + escape(self.describe(selected)) + "</p>", self)

    def save_png(self, filename, title=""):
        """Paint the complete sheet in strips, even when it is taller than Qt's raster limit."""
        width = self.viewport().width()
        header = self.line + 18 if title else 0
        height = header + max(50, self.content_height)
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
                    self.paint_rows(p, width, image.height(), top - header)
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
        self.canvas = TimelineCanvas(duration, compact=compact, parent=self)
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
        if compact:
            self.zoom.addItem("整场按技能", -1)
        for name, val in (("自动分行", 0), ("每行 30 秒", 30), ("每行 1 分钟", 60), ("每行 2 分钟", 120)):
            self.zoom.addItem(name, val)
        self.zoom.setToolTip("缩短每行时长可拉开临近技能。")
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
        rows = record.records if isinstance(record, SkillGroup) else [record]
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

"""Qt timelines for boss mechanics and personal replays. Times in the view are milliseconds."""
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from heapq import heappop, heappush
from html import escape
from itertools import groupby
from math import ceil, isfinite
import re

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractScrollArea, QApplication, QComboBox, QDoubleSpinBox,
    QHBoxLayout, QLabel, QPushButton, QToolTip, QVBoxLayout, QWidget,
)

from data.PersonalTimeline import ACTION_ICONS, Observation, build_personal_timelines
from tools.ResourcePath import get_icon_path


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
                    " · ".join(detail), icon, resolved)
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


def focused_marks(marks, team=False):
    """Condense consecutive casts for the overview; the full view retains each original."""
    result = [mark for mark in marks if mark.focused and mark.track != NORMAL
              and not (team and mark.track == CALLS)]
    if team:
        calls = sorted((m for m in marks if m.track == CALLS), key=lambda m: (m.name, m.icon, m.start))
        for _, same_skill in groupby(calls, key=lambda m: (m.name, m.icon)):
            cluster = []
            for mark in same_skill:
                if cluster and mark.start-cluster[0].start > 250:
                    result.append(_team_call(cluster))
                    cluster = []
                cluster.append(mark)
            result.append(_team_call(cluster))
    casts = sorted((mark for mark in marks if mark.track == NORMAL), key=lambda mark: mark.start)
    for _, group in groupby(casts, key=lambda mark: (mark.name, mark.icon)):
        run = []
        for mark in group:
            if run and mark.start-run[-1].end > 2500:
                result.extend(_cast_run(run))
                run = []
            run.append(mark)
        result.extend(_cast_run(run))
    return result


def _team_call(marks):
    first = marks[0]
    if len(marks) == 1:
        return first
    note = "、".join(dict.fromkeys(m.detail for m in marks if m.detail))
    return Mark(first.start, max(m.end for m in marks), CALLS, f"{first.name} · {len(marks)} 条",
                first.color, note, first.icon)


def _cast_run(marks):
    if len(marks) < 3:
        return marks
    first = marks[0]
    return [Mark(first.start, max(m.end for m in marks), NORMAL, f"{first.name} · {len(marks)} 条",
                 first.color, "连续施放，可在全部记录中查看每次施放。", first.icon)]


class TimelineCanvas(QAbstractScrollArea):
    selected = Signal(str)
    GUTTER = 106
    RULER = 32
    ROW = 31

    def __init__(self, duration, parent=None):
        super().__init__(parent)
        self.duration = duration
        self.marks = []
        self.rows = []
        self.scale = 24.0
        self.zoom = 24.0
        self.icons = {}
        self.hits = []
        self.choice = None
        self.layout_key = None
        self.setAccessibleName("可滚动时间轴")
        self.viewport().setMouseTracking(True)
        self.horizontalScrollBar().setSingleStep(64)
        self.verticalScrollBar().setSingleStep(self.ROW)

    def set_marks(self, marks):
        self.marks = marks
        self.choice = None
        self.verticalScrollBar().setValue(0)
        self.relayout()

    def set_zoom(self, zoom):
        center = (self.horizontalScrollBar().value() + self.plot_width()/2)/self.scale
        self.zoom = zoom
        self.relayout()
        self.horizontalScrollBar().setValue(round(center*self.scale-self.plot_width()/2))

    def plot_width(self):
        return max(80, self.viewport().width()-self.GUTTER-8)

    def relayout(self):
        width = self.plot_width()
        self.scale = self.zoom or width/max(1, self.duration/1000)
        key = (id(self.marks), self.scale, self.font().toString())
        if self.layout_key != key:
            self.rows = self.allocate_rows()
            self.layout_key = key
        last_x = max((ends[-1] for _, ends, _ in self.rows), default=0)
        total_width = max(last_x, ceil(self.duration*self.scale/1000)) + 2
        self.horizontalScrollBar().setRange(0, max(0, total_width-width))
        self.horizontalScrollBar().setPageStep(width)
        body = self.viewport().height()-self.RULER
        self.verticalScrollBar().setRange(0, max(0, len(self.rows)*self.ROW-body))
        self.verticalScrollBar().setPageStep(max(self.ROW, body))
        self.hits = []
        self.viewport().update()

    def allocate_rows(self):
        by_track = {key: [] for key in (NORMAL, SPECIAL, "施放", "招式命中", "技能效果", PHASES, MECHANICS, CALLS)}
        for mark in self.marks:
            by_track.setdefault(mark.track, []).append(mark)
        rows = []
        fm = self.fontMetrics()
        for track, entries in by_track.items():
            lanes = []
            occupied = []
            free = []
            for mark in sorted(entries, key=lambda m: m.start):
                x = round(mark.start*self.scale/1000)
                end = max(x+1, round(mark.end*self.scale/1000))
                if not mark.band:
                    # Reserve a bounded label footprint at close zoom. At overview
                    # scale, simultaneous records still receive independent lanes.
                    label_width = fm.horizontalAdvance(mark.name) + 25
                    end = max(end, x + min(label_width, max(5, round(self.scale*2.5))))
                while occupied and occupied[0][0] <= x:
                    _, index = heappop(occupied)
                    heappush(free, index)
                index = heappop(free) if free else len(lanes)
                if index == len(lanes):
                    lanes.append(([], []))
                ends, events = lanes[index]
                ends.append(end)
                events.append((x, end, mark))
                heappush(occupied, (end, index))
            for index, (ends, entries) in enumerate(lanes):
                caption = track if index == 0 else f"{track} {index + 1}"
                rows.append((caption, ends, entries))
        return rows

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout()

    def scrollContentsBy(self, dx, dy):
        self.hits = []
        self.viewport().update()

    def paintEvent(self, _event):
        vp = self.viewport()
        p = QPainter(vp)
        width, height = vp.width(), vp.height()
        p.fillRect(vp.rect(), QColor("#ffffff"))
        origin = self.GUTTER-self.horizontalScrollBar().value()
        scroll = self.verticalScrollBar().value()
        p.fillRect(0, 0, width, self.RULER, QColor("#eaf1f3"))
        p.setPen(QColor("#45606b"))
        p.drawText(QRect(9, 0, self.GUTTER-12, self.RULER), Qt.AlignVCenter, "战斗经过")
        seconds_step = next((s for s in (1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 1800)
                             if s*self.scale >= 60), max(3600, ceil(70/self.scale)))
        visible_start = self.horizontalScrollBar().value()/self.scale
        first_tick = int(visible_start//seconds_step)*seconds_step
        for sec in range(first_tick, min(ceil(self.duration/1000), ceil((width-origin)/self.scale))+1, seconds_step):
            x = round(origin+sec*self.scale)
            if x < self.GUTTER:
                continue
            p.setPen(QColor("#e5ecee"))
            p.drawLine(x, self.RULER-4, x, height)
            p.setPen(QColor("#405d66"))
            p.drawText(x+3, 20, f"{sec//60}:{sec%60:02}")
        self.hits = []
        fm = p.fontMetrics()
        first_row = scroll//self.ROW
        row_count = ceil(max(0,height-self.RULER)/self.ROW)+1
        p.setClipRect(0, self.RULER, width, max(0, height-self.RULER))
        for idx in range(first_row, min(len(self.rows), first_row+row_count)):
            label, ends, entries = self.rows[idx]
            y = self.RULER+idx*self.ROW-scroll
            p.fillRect(0, y, self.GUTTER, self.ROW, QColor("#f3f6f7"))
            p.setPen(QColor("#364e58"))
            p.drawText(QRect(9, y, self.GUTTER-15, self.ROW), Qt.AlignVCenter, label)
            p.setPen(QColor("#e2e9eb"))
            p.drawLine(0, y+self.ROW-1, width, y+self.ROW-1)
            p.save()
            p.setClipRect(self.GUTTER, self.RULER, self.plot_width()+8, height-self.RULER)
            for j in range(bisect_right(ends, self.horizontalScrollBar().value()), len(entries)):
                left, right, mark = entries[j]
                if origin+left >= width:
                    break
                rect = QRect(origin+left, y+4, right-left, self.ROW-9)
                color = QColor(mark.color)
                if not color.isValid() or color == QColor("#000000"):
                    color = QColor("#3b7586")
                if mark.band:
                    color.setAlphaF(.12+.80*mark.intensity)
                    p.fillRect(rect, color)
                else:
                    tint = QColor(color)
                    tint.setAlpha(33)
                    p.fillRect(rect, tint)
                    p.fillRect(rect.x(), rect.y(), min(3,rect.width()), rect.height(), color)
                if mark is self.choice:
                    p.setPen(QColor("#203f51"))
                    p.drawRect(rect.adjusted(0,0,-1,-1))
                content = rect.intersected(QRect(self.GUTTER, y, self.plot_width()+8, self.ROW))
                text_x = content.left()+4
                if not mark.band and content.width() >= 28 and mark.icon.isdecimal():
                    if mark.icon not in self.icons:
                        image = QPixmap(get_icon_path(mark.icon))
                        self.icons[mark.icon] = image.scaled(17,17,Qt.KeepAspectRatio,Qt.SmoothTransformation) if not image.isNull() else image
                    icon = self.icons[mark.icon]
                    if not icon.isNull():
                        p.drawPixmap(text_x, y+7, icon)
                        text_x += 19
                available = content.right()-text_x
                if available >= 12:
                    foreground = "#ffffff" if mark.band and color.alphaF() > .6 and color.lightnessF() < .5 else "#223b45"
                    p.setPen(QColor(foreground))
                    text = fm.elidedText(mark.name, Qt.ElideRight, available)
                    p.drawText(QRect(text_x, y, available, self.ROW), Qt.AlignVCenter, text)
                self.hits.append((content, mark))
            p.restore()
        if not self.rows:
            p.setPen(QColor("#57717b"))
            p.drawText(QRect(self.GUTTER+12, self.RULER+10, width-self.GUTTER-20, 36),
                       Qt.AlignVCenter, "当前范围没有时间轴记录")
        p.end()

    @staticmethod
    def describe(mark):
        span = clock(mark.start)
        if mark.end > mark.start:
            span += f" – {clock(mark.end)}"
        return "  ·  ".join(filter(None, [span, mark.track, mark.name, mark.detail]))

    def mousePressEvent(self, event):
        mark = next((mark for rect, mark in self.hits if rect.contains(event.position().toPoint())), None)
        if mark is not None:
            self.choice = mark
            self.selected.emit(self.describe(mark))
            self.viewport().update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        mark = next((mark for rect, mark in self.hits if rect.contains(event.position().toPoint())), None)
        if mark is None:
            QToolTip.hideText()
        else:
            # Plain text only; game labels and log descriptions can contain markup.
            QToolTip.showText(event.globalPosition().toPoint(), "<p>"+escape(self.describe(mark))+"</p>", self)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier:
            bar = self.horizontalScrollBar()
            bar.setValue(bar.value()-event.angleDelta().y())
            event.accept()
        else:
            super().wheelEvent(event)


class TimelineView(QWidget):
    @classmethod
    def from_actor(cls, actor, player=None, parent=None):
        return cls(*timeline_data(actor, player), team=player is None, parent=parent)

    def __init__(self, duration, marks, exports, team=False, parent=None):
        super().__init__(parent)
        self.marks = marks
        self.exports = exports
        self.team = team
        kinds = {mark.track for mark in marks}
        if "施放" in kinds:
            self.hint = "施放为日志记录的开始时刻。命中和技能效果按同刻同技能合并。"
        elif "技能效果" in kinds and "招式命中" not in kinds:
            self.hint = "仅有可归属的技能效果。重点显示结算记录最多的三种，完整明细见全部记录。"
        elif "招式命中" in kinds:
            self.hint = "此记录缺少原生施放时刻。命中和技能效果按同刻同技能合并。"
        elif not marks and not team:
            self.hint = "该角色没有可归属的个人技能记录。"
        else:
            self.hint = "点击记录查看详情"
        self.canvas = TimelineCanvas(duration, self)
        self.setMinimumSize(280, 215)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        toolbar = QHBoxLayout()
        self.scope = QComboBox()
        self.scope.addItems(["重点记录", "全部记录"])
        self.scope.setToolTip("重点显示已识别机制和原生施放，同时保留缺少原生施放记录的已知招式命中。临近的同名团队点名及连续的常规施放合并显示。")
        toolbar.addWidget(self.scope)
        self.zoom = QComboBox()
        for title, factor in (("适配整场", 0), ("10 px/s", 10), ("24 px/s", 24), ("48 px/s", 48), ("96 px/s", 96)):
            self.zoom.addItem(title, factor)
        self.zoom.setCurrentIndex(2)
        self.zoom.setToolTip("调整每秒的显示宽度。按住 Shift 滚轮可横向移动。")
        toolbar.addWidget(self.zoom)
        toolbar.addStretch()
        self.summary = QLabel()
        toolbar.addWidget(self.summary)
        layout.addLayout(toolbar)
        layout.addWidget(self.canvas, 1)
        self.detail = QLabel("点击记录查看详情")
        self.detail.setTextFormat(Qt.PlainText)
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail)
        if exports:
            footer = QHBoxLayout()
            self.offset = QDoubleSpinBox()
            self.offset.setRange(-86400, max(86400, duration/1000))
            self.offset.setSuffix(" 秒")
            self.offset.setAccessibleName("导出起始偏移")
            footer.addWidget(QLabel("导出起点"))
            footer.addWidget(self.offset)
            for label, handler in (("复制线性轴", self.copy_linear), ("复制双排轴", self.copy_parallel)):
                button = QPushButton(label)
                button.clicked.connect(handler)
                footer.addWidget(button)
            footer.addStretch()
            layout.addLayout(footer)
        self.scope.currentIndexChanged.connect(self.change_scope)
        self.zoom.currentIndexChanged.connect(self.change_zoom)
        self.canvas.selected.connect(self.detail.setText)
        self.change_scope(0)

    def change_scope(self, index):
        marks = self.marks if index else focused_marks(self.marks, self.team)
        self.canvas.set_marks(marks)
        records = sum(not m.band for m in marks)
        self.summary.setText(f"{clock(self.canvas.duration)}  ·  {records} 条")
        self.detail.setText(self.hint)

    def change_zoom(self, index):
        self.canvas.set_zoom(self.zoom.itemData(index))

    def copy_linear(self):
        self.copy_axis(False)

    def copy_parallel(self):
        self.copy_axis(True)

    def copy_axis(self, parallel):
        QApplication.clipboard().setText(export_text(self.exports, self.offset.value(), parallel))
        self.detail.setText("已复制双排时间轴" if parallel else "已复制线性时间轴")

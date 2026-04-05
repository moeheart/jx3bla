from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


TRIVIA_DIR = Path(__file__).resolve().parent / "trivia_result"
TRIVIA_OUTPUT_DIR = Path(__file__).resolve().parent / "trivia_output"
UTC8 = timezone(timedelta(hours=8))
DEAD_IGNORE_TAIL_MS = 20000
EVENT_ORDER = ["Dead", "TangZui33133", "Ashina44415"]
EVENT_LABELS = {
    "Dead": "\u91cd\u4f24",
    "TangZui33133": "33133",
    "Ashina44415": "44415",
}


def bool_flag(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = str(value).strip().lower()
    return text in ["1", "true", "yes"]


def format_start_time(start_ts: int) -> str:
    return datetime.fromtimestamp(start_ts, UTC8).strftime("%Y-%m-%d %H:%M:%S")


class LangfengTriviaRecorder:

    def __init__(self, config, boss_name: str, start_timestamp: int, start_time: int):
        self.enabled = bool(config.item["general"].get("trivia", 0))
        self.boss_name = boss_name
        self.start_timestamp = int(start_timestamp)
        self.start_time = start_time
        self.player_names = set()
        self.events = []

    def add_player_names(self, stat_dict):
        if not self.enabled:
            return
        for player in stat_dict:
            self.player_names.add(stat_dict[player]["name"])

    def record_event(self, event_type: str, player_name: str, event_time: int):
        if not self.enabled:
            return
        self.events.append((event_time, event_type, player_name))

    def _filter_events(self, final_time: int, battle_time: int):
        valid_events = []
        battle_end_time = self.start_time + battle_time
        death_cutoff = battle_end_time - DEAD_IGNORE_TAIL_MS
        for event_time, event_type, player_name in self.events:
            if event_time > final_time:
                continue
            if event_type == "Dead" and event_time > death_cutoff:
                continue
            valid_events.append((event_time, event_type, player_name))
        valid_events.sort(key=lambda x: (x[0], x[1], x[2]))
        return valid_events

    def flush(self, final_time: int, battle_time: int, win: int):
        if not self.enabled:
            return None

        TRIVIA_DIR.mkdir(parents=True, exist_ok=True)
        target = TRIVIA_DIR / ("%d.txt" % self.start_timestamp)
        valid_events = self._filter_events(final_time, battle_time)
        battle_seconds = battle_time / 1000

        lines = [
            "Totaltime 0 %.1f" % battle_seconds,
            "Boss %s %.1f" % (self.boss_name, battle_seconds),
            "Win %d %.1f" % (win, battle_seconds),
        ]
        for player_name in sorted(self.player_names):
            lines.append("Player %s %.1f" % (player_name, battle_seconds))
        for event_time, event_type, player_name in valid_events:
            event_seconds = (event_time - self.start_time) / 1000
            lines.append("%s %s %.1f" % (event_type, player_name, event_seconds))

        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target


def build_single_sheet_rows(fights):
    rows = []
    for index, fight in enumerate(fights, start=1):
        player_counts = defaultdict(Counter)
        for _, current_type, player_name in fight["events"]:
            player_counts[player_name][current_type] += 1

        player_cells = {}
        for player_name, counts in player_counts.items():
            parts = []
            for event_type in EVENT_ORDER:
                count = counts.get(event_type, 0)
                if count:
                    parts.append("%sx%d" % (EVENT_LABELS[event_type], count))
            if parts:
                player_cells[player_name] = "\n".join(parts)

        rows.append({
            "index": index,
            "start": format_start_time(fight["start_ts"]),
            "boss": fight["boss"],
            "win": fight["win"],
            "cells": player_cells,
        })
    return rows

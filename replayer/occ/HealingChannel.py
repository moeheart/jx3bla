"""Reconstruct healer channel time from cast starts and observed healing ticks."""
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass, field
from heapq import merge

from tools.Functions import IntervalCounter


def channel_efficiencies(history, channel_log):
    start, end = history.startTime, history.finalTime
    gcd, channel, excluded = (IntervalCounter(start, end) for _ in range(3))
    for action in history.log["normal"]:
        gcd.recordInterval(action["start"], action["start"] + action["duration"])
    channel.recordLog(channel_log)
    excluded.recordLog(history.badPeriodHealerLog)
    # All three tracks are clipped to the same personal fight. At each boundary
    # combine simultaneous starts and ends before measuring the next interval.
    changes = defaultdict(lambda: [0, 0, 0])
    changes[end] = [0, 0, 0]
    for index, track in enumerate((gcd, channel, excluded)):
        for a, b, _ in track.intervals:
            changes[a][index] += 1
            changes[b][index] -= 1
    gcd_active = channel_active = excluded_active = 0
    valid = gcd_busy = combat_busy = 0
    previous = start
    for time, (gcd_delta, channel_delta, excluded_delta) in sorted(changes.items()):
        if not excluded_active:
            duration = time - previous
            valid += duration
            if gcd_active:
                gcd_busy += duration
            if gcd_active or channel_active:
                combat_busy += duration
        gcd_active += gcd_delta
        channel_active += channel_delta
        excluded_active += excluded_delta
        previous = time
    return {"efficiency": gcd_busy / valid if valid > 0 else 0,
            "efficiencyNonGcd": combat_busy / valid if valid > 0 else 0}


@dataclass
class ChannelCast:
    start: int
    marked: bool
    partial: bool = False
    ticks: list = field(default_factory=list)
    heal: int = 0
    healeff: int = 0
    damage: int = 0
    damageeff: int = 0

    @property
    def end(self):
        return self.ticks[-1] if self.ticks else self.start

    def replay(self):
        row = {"start": self.start, "end": self.end, "ticks": len(self.ticks)}
        if self.partial:
            row["partial"] = True
        return row


class HealingChannel:
    def __init__(self):
        self._casts = set()
        self._shells = set()
        self._finishes = set()
        self._start_frames = {}
        self._hits = {}

    def cast(self, time, shell=False, frame=None):
        (self._shells if shell else self._casts).add(time)
        if frame is not None:
            self._start_frames[time] = frame

    def finish(self, time):
        self._finishes.add(time)

    @staticmethod
    def _elapsed(time, frame, previous_time, previous_frame):
        if 0 <= previous_frame <= frame:
            return (frame - previous_frame) * 62.5
        return time - previous_time

    @property
    def starts(self):
        # JCL can record a native Cast and a single-use shell Skill for one
        # action. Prefer the native time even when the shell was logged first.
        # Two distinct native Casts always describe two attempts.
        native = sorted(self._casts)
        starts = list(native)
        for shell in sorted(self._shells):
            i = bisect_left(native, shell - 100)
            if i == len(native) or native[i] > shell + 100:
                starts.append(shell)
        return sorted(starts)

    def tick(self, time, heal=0, healeff=0, damage=0, damageeff=0, frame=None):
        # Keep amounts for every target, even when several land in one frame.
        amounts = self._hits.setdefault((time, -1 if frame is None else frame), [0, 0, 0, 0])
        amounts[0] += heal
        amounts[1] += healeff
        amounts[2] += damage
        amounts[3] += damageeff

    def jiguang(self, talents):
        if '吉光' in talents.values():
            return True
        if talents.get('available') or {'霞绡', '妍姿'} & set(talents.values()):
            return False
        # A channel without 吉光 has no immediate tick. Older logs may omit talents.
        times = sorted(time for time, _ in self._hits)
        for start in self.starts:
            i = bisect_left(times, start)
            if i < len(times) and times[i] - start <= 100:
                return True
        return False

    def groups(self, start, end, tick_length, immediate=False, ticks_per_cast=0, marked_tick_limit=0):
        """Group pulses into casts, retaining interrupted casts with no hits.

        A start marker always opens a new cast. A known cast may miss individual
        healing pulses, so allow late effects within the full channel duration.
        In a section without markers only adjacent pulses can be joined.
        """
        casts = []
        current = None
        starts = self.starts
        finishes = sorted(self._finishes)
        markers = ((time, 0, self._start_frames.get(time, -1)) for time in starts)
        hits = ((time, 1, frame) for time, frame in sorted(self._hits))
        finish = None
        cast_frame = pulse_frame = -1
        for time, hit, frame in merge(markers, hits):
            if not start <= time <= end:
                continue
            if not hit:
                current = ChannelCast(time, marked=True)
                casts.append(current)
                cast_frame = pulse_frame = frame
                finish = None
                if finishes:
                    i = bisect_left(finishes, time)
                    next_cast = bisect_left(starts, time) + 1
                    if i < len(finishes) and (next_cast == len(starts) or finishes[i] < starts[next_cast]):
                        finish = finishes[i]
                continue
            # Multiple targets of one pulse can land a few frames apart. The
            # next start takes priority, even when it falls in the same frame.
            # Recorders may stall for seconds and then publish several true
            # pulses within milliseconds. JCL's 16 Hz logic frame follows the
            # battle during both the stall and the catch-up.
            gap = self._elapsed(time, frame, current.end, pulse_frame) if current else 0
            same_pulse = current and current.ticks and gap <= 150
            if not same_pulse:
                fits = current is not None and gap <= tick_length + 180
                limit = (marked_tick_limit or ticks_per_cast) if current and current.marked else ticks_per_cast
                if current and current.marked and limit:
                    age = self._elapsed(time, frame, current.start, cast_frame)
                    fits = age <= tick_length * limit + 350
                if current and current.marked and finish is not None:
                    # The channel buff spans logging stalls that can delay or
                    # compress the final pulses well beyond their nominal times.
                    fits = time <= finish + 150
                if not fits or (limit and len(current.ticks) >= limit):
                    inferred = time if immediate else time - tick_length
                    floor = current.end if current is not None else start
                    # A JCL that begins during an ongoing channel contains its
                    # remaining heals but no evidence of an in-fight GCD.
                    partial = not casts and bool(starts) and time - start <= tick_length + 180
                    current = ChannelCast(max(floor, inferred), marked=False, partial=partial)
                    casts.append(current)
                current.ticks.append(time)
                pulse_frame = frame
            heal, healeff, damage, damageeff = self._hits[time, frame]
            current.heal += heal
            current.healeff += healeff
            current.damage += damage
            current.damageeff += damageeff
        return casts

    @staticmethod
    def coverage(start, end, casts):
        coverage = IntervalCounter(start, end)
        for cast in casts:
            coverage.recordInterval(cast.start, cast.end)
        return coverage.export()

    def intervals(self, start, end, tick_length, immediate=False, ticks_per_cast=0):
        casts = self.groups(start, end, tick_length, immediate, ticks_per_cast)
        return self.coverage(start, end, casts), [cast.start for cast in casts if not cast.partial]

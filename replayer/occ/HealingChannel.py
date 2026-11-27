"""Reconstruct healer channel time from cast starts and observed healing ticks."""
from bisect import bisect_left, bisect_right
from collections import defaultdict

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


class HealingChannel:
    def __init__(self):
        self.starts = []
        self.ticks = []

    def cast(self, time):
        # JCL may report both a native Cast and a shell Skill for the same use.
        if not self.starts or time - self.starts[-1] > 100:
            self.starts.append(time)

    def tick(self, time):
        # One pulse can heal several targets a few frames apart.
        if (not self.ticks or time - self.ticks[-1] > 150 or
                (self.starts and self.ticks[-1] < self.starts[-1] <= time)):
            self.ticks.append(time)

    def jiguang(self, talents):
        if '吉光' in talents.values():
            return True
        if talents.get('available') or {'霞绡', '妍姿'} & set(talents.values()):
            return False
        # A channel without 吉光 has no immediate tick. Older logs may omit talents.
        for start in self.starts:
            index = bisect_left(self.ticks, start)
            if index < len(self.ticks) and self.ticks[index] - start <= 100:
                return True
        return False

    def intervals(self, start, end, tick_length, immediate=False, ticks_per_cast=0):
        """Return a union of observed channel intervals and individual cast starts.

        Native casts delimit each channel; the last landed tick is its last
        confirmed busy instant. Effect-only logs have no start markers, so use
        the nominal tick length for a first non-instant pulse.
        """
        coverage = IntervalCounter(start, end)
        starts = list(self.starts)
        previous = None
        count = 0
        for tick in self.ticks:
            index = bisect_right(self.starts, tick) - 1
            cast = self.starts[index] if index >= 0 else None
            # Allow for server tick and logging jitter around the nominal interval.
            near_previous = previous is not None and tick - previous <= tick_length + 180
            if cast is not None and (previous is None or cast > previous) and tick - cast <= tick_length + 180:
                left = cast
                count = 1
            elif near_previous and not (cast is None and ticks_per_cast and count >= ticks_per_cast):
                left = previous
                count += 1
            else:
                left = tick if immediate else tick - tick_length
                # With native markers the tick can also belong to a channel
                # begun before the fight. Never create an extra GCD from it.
                if not self.starts:
                    starts.append(max(start, left))
                count = 1
            coverage.recordInterval(left, tick)
            previous = tick
        return coverage.export(), sorted(set(starts))

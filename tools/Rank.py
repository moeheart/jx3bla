"""Values and percentile lookup shared by replay display and daily sampling."""
from bisect import bisect_right
import math


def rank_metric_value(metric, value, skill):
    if metric == "delaySamples" or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    if metric != "delay":
        return value
    count = skill.get("delaySamples")
    if "delaySamples" in skill and (type(count) is not int or count <= 0):
        return None
    # A positive historical average proves there was an observation. Historical
    # zero can also mean no casts, or only gaps that the counter discarded.
    if value < 0 or (count is None and value == 0):
        return None
    return -value


def percentile_rank(value, thresholds):
    """Keep the highest tied percentile and clamp values below the minimum."""
    return max(0, bisect_right(thresholds, value) - 1)

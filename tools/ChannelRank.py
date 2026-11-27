"""Use separate Logs percentile pools for cast-based healer channel metrics."""

CHANNEL_GROUPS = ("hxpy", "zwjt", "zhi", "dgsn", "longwu")
CAST_FIELDS = ("num", "numPerSec", "delay", "delaySamples")


def channel_rank_group(group, metric, fields):
    # The rebuilt skill cards always include observed ticks (even zero).
    # Historical records without that field use their original distribution.
    if group in CHANNEL_GROUPS and metric in CAST_FIELDS and "ticks" in fields:
        return group + "Cast"
    return group


def channel_upload_result(result):
    """Project only changed metrics into new groups for unmodified Logs servers."""
    skills = result.get("skill", {})
    channels = [group for group in CHANNEL_GROUPS if "ticks" in skills.get(group, {})]
    if not channels:
        return result
    projected = dict(result)
    for section in ("skill", "rank"):
        if section not in result:
            continue
        groups = dict(result[section])
        for group in channels:
            row = groups.get(group, {})
            cast_fields = {key: row[key] for key in CAST_FIELDS if key in row}
            if cast_fields:
                groups[group] = {key: value for key, value in row.items() if key not in cast_fields}
                groups[group + "Cast"] = cast_fields
        projected[section] = groups
    return projected


def display_channel_groups(groups):
    """Merge a stored cast group back into its skill for a downloaded report."""
    result = dict(groups)
    for group in CHANNEL_GROUPS:
        cast_row = result.pop(group + "Cast", None)
        if isinstance(cast_row, dict):
            result[group] = {**result.get(group, {}), **cast_row}
    return result


def display_channel_result(result):
    displayed = dict(result)
    for section in ("skill", "rank"):
        if section in result:
            displayed[section] = display_channel_groups(result[section])
    return displayed

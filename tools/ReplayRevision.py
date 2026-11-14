"""Allow a scoped 8.16.8 recalculation without changing the release version."""
from tools.Names import getIDFromMap, getNickToBoss


LUOYANG_EFFECTIVE_TIME = 'luoyang-effective-time-20261114'
RELEASE = 8016008  # parseEdition('8.16.8'); not a new client version.
MAPS = frozenset(('828', '835', '836'))
BOSSES = frozenset(('突利和顺', '田承嗣', '伊曼双子', '阿史那承庆', '史朝义'))


def in_scope(map_name, boss):
    map_id = str(map_name) if str(map_name) in MAPS else str(getIDFromMap(map_name))
    return map_id in MAPS and getNickToBoss(boss, mapName=map_name) in BOSSES


def mark_recalculation(statistics, map_name, boss):
    if in_scope(map_name, boss):
        statistics['analysisRevision'] = LUOYANG_EFFECTIVE_TIME


def get_analysis_revision(data):
    """Read the recognized marker from a payload or its cached quality summary."""
    if not isinstance(data, dict):
        return None
    if data.get('analysisRevision') == LUOYANG_EFFECTIVE_TIME:
        return LUOYANG_EFFECTIVE_TIME
    for key in ('statistics', 'overall', 'quality'):
        nested = data.get(key)
        if isinstance(nested, dict) and nested.get('analysisRevision') == LUOYANG_EFFECTIVE_TIME:
            return LUOYANG_EFFECTIVE_TIME
    return None


def revision_change(previous, incoming, map_name, boss, previous_edition, incoming_edition):
    """Return upgrade/downgrade only for this recognized fix and release scope.

    Source-quality checks remain mandatory at the caller. A later numbered
    release follows the usual version policy; arbitrary marker strings cannot
    opt into same-version replacement.
    """
    if not in_scope(map_name, boss):
        return None
    old = get_analysis_revision(previous) is not None
    new = get_analysis_revision(incoming) is not None
    if (old or new) and incoming_edition < previous_edition:
        return 'downgrade'
    if old and not new and incoming_edition <= previous_edition:
        return 'downgrade'
    if not old and new and incoming_edition == previous_edition == RELEASE:
        return 'upgrade'
    return None

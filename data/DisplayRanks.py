"""Read-only comparisons for the desktop. The server's sampling rules are independent."""
from collections import defaultdict
import json
import math

from Constants import OCC_PINYIN_DICT
from tools.Attribute import CURRENT_GAME_EDITION
from tools.Functions import getOccType
from tools.Names import getIDFromMap
from tools.Rank import percentile_rank
from tools.RecordQuality import get_record_quality, is_effect_warning_only


def _historical(sample, value):
    if not isinstance(sample, dict):
        return None
    try:
        n = int(sample['num'])
        thresholds = sample['value']
        if isinstance(thresholds, str):
            thresholds = json.loads(thresholds)
        if (n <= 0 or not isinstance(thresholds, list) or len(thresholds) != 101
                or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in thresholds)
                or thresholds != sorted(thresholds)):
            return None
        return percentile_rank(value, thresholds), n
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def desktop_percentiles(actor):
    """Use the same encounter/spec/edition sample, else describe local role peers."""
    rates = getattr(getattr(actor, 'window', None), 'stat_percent', {}) or {}
    map_id = getIDFromMap(actor.mapDetail)
    quality = get_record_quality(actor.attributeStatus)
    usable_rdps = (quality['precise'] or is_effect_warning_only(actor.attributeStatus)
                   or (quality['estimated'] and not quality.get('referenceUnavailable')
                       and not quality.get('unresolvedTargets') and not quality.get('targetProfileUnavailable')
                       and quality.get('staticAttributes') not in ('partial', 'missing')))
    role_names = {'dps': '输出', 'healer': '治疗', 'tank': '坦克'}
    peers = defaultdict(list)
    comparisons = {}
    tracker = actor.combatTracker
    for row in actor.statDict:
        occ, name = str(row['occ']), row['name']
        role = getOccType(occ)
        metric = 'rhps' if role == 'healer' else 'rdps'
        if metric == 'rdps' and not usable_rdps:
            continue
        table = getattr(tracker, metric, {}).get('player', {})
        stats = next((p for p in table.values() if p.get('name') == name), {})
        value = stats.get('hps' if metric == 'rhps' else 'dps', stats.get('sumPerSec'))
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            continue
        peers[role].append((name, value))
        group = 'healer' if metric == 'rhps' else 'general'
        key = f'{OCC_PINYIN_DICT.get(occ)}-{map_id}-{actor.bossAnalyseName}-{group}-{metric}-{CURRENT_GAME_EDITION}'
        historical = _historical(rates.get(key), value)
        if historical:
            percent, count = historical
            comparisons[name] = {'metric': metric, 'scope': 'historical', 'cohort': '同心法',
                                 'reference': metric == 'rdps' and not quality['precise'],
                                 'percent': percent, 'num': count}
    for role, members in peers.items():
        if len(members) < 2:
            continue
        for name, value in members:
            if name in comparisons:
                continue
            others = [v for who, v in members if who != name]
            if not others:
                continue
            # Percent of other participants below this value, with half credit for ties.
            percentile = round(100 * sum((v < value) + 0.5 * (v == value) for v in others) / len(others))
            comparisons[name] = {'metric': 'rhps' if role == 'healer' else 'rdps',
                                 'scope': 'team', 'cohort': role_names[role], 'reference': True,
                                 'percent': percentile, 'num': len(others)}
    return comparisons

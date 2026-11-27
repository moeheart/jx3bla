"""Compare a saved fight to the full-fight rDPS distribution published by JX3 Logs."""
import json
import math

from Constants import OCC_PINYIN_DICT
from tools.Names import getGameEditionFromTime, getIDFromMap
from tools.Rank import percentile_rank
from tools.RecordQuality import get_record_quality


def _distribution(sample):
    if not isinstance(sample, dict):
        return None
    try:
        count = int(sample['num'])
        thresholds = sample['value']
        if isinstance(thresholds, str):
            thresholds = json.loads(thresholds)
        if (count <= 0 or not isinstance(thresholds, list) or len(thresholds) != 101
                or not all(type(x) in (int, float) and math.isfinite(x) for x in thresholds)
                or thresholds != sorted(thresholds)):
            return None
        return thresholds, count
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def _rank_basis(quality, player_id, stats, direct, value, missing, official_luoyang):
    if (quality['status'] == 'unavailable' or quality.get('referenceUnavailable')
            or quality.get('targetProfileUnavailable')):
        return 'unavailable'
    if not official_luoyang:
        return 'verified' if quality['precise'] else 'unavailable'
    if value <= 0:
        return 'unavailable'
    own = missing.get(player_id, {})
    if (quality.get('unresolvedTargets') or quality.get('equipmentErrors')
            or quality.get('unparsedAttributes') or quality.get('staticAttributes') in ('missing', 'partial')
            or (isinstance(own, dict) and player_id in missing and own.get('hasReference') is not True)):
        # Match the Logs admission rule with the team contribution record already in memory.
        attributed = (type(direct) in (int, float) and math.isfinite(direct) and int(value) != int(direct))
        sources = stats.get('namedSource', {})
        if attributed or any(label != '自身伤害' and item.get('sum', 0) > 0
                             for label, item in sources.items() if isinstance(item, dict)):
            return 'partial_attribution'
        return 'unavailable'
    if quality['precise']:
        return 'verified'
    if quality['estimated'] or quality['missingEquipmentPlayerCount']:
        return 'estimated_equipment'
    return 'unmodeled_effects' if quality.get('unmodeledEffects') else 'reported'


def desktop_percentiles(result, rates):
    """Use the recorded map, encounter, specialization and season, for every role."""
    if not rates:
        return {}
    map_id = getIDFromMap(result.mapDetail)
    edition = getGameEditionFromTime(map_id, result.timestamp)
    if edition == '0':
        return {}
    tracker = result.combatTracker
    source = result.attributeStatus or {}
    quality = get_record_quality(source)
    missing = source.get('missingEquipmentPlayers', {})
    if not isinstance(missing, dict):
        missing = {str(key): {} for key in missing or ()}
    official = map_id in ('835', '836') and edition in ('161', '162')
    direct = tracker.get('ndps', {}).get('player', {})
    players = {stats.get('name'): (key, stats)
               for key, stats in tracker.get('rdps', {}).get('player', {}).items()}
    comparisons = {}
    for row in result.statDict:
        name = row['name']
        specialization = OCC_PINYIN_DICT.get(str(row['occ']))
        sample = rates.get(f'{specialization}-{map_id}-{result.bossAnalyseName}-stat-rdps-{edition}')
        distribution = _distribution(sample)
        if distribution is None:
            continue
        thresholds, count = distribution
        player_id, stats = players.get(name, (None, {}))
        value = stats.get('dps', stats.get('sumPerSec'))
        basis = 'unavailable'
        if type(value) in (int, float) and math.isfinite(value) and value >= 0:
            basis = _rank_basis(quality, player_id, stats, direct.get(player_id, {}).get('dps'),
                                value, missing, official)
        item = {'scope': 'logs', 'metric': 'rdps', 'edition': edition, 'basis': basis,
                'reference': basis != 'verified', 'num': count}
        if basis != 'unavailable':
            # Logs ranks the integer in the uploaded personal report.
            item['percent'] = percentile_rank(int(value), thresholds)
        comparisons[name] = item
    return comparisons

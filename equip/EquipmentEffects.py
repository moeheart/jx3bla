"""Resolve audited equipment effects without replaying their proc damage twice.

The catalogue identifies exact effect parameters, not broad at* categories.
Unlisted effects and unsupported platforms retain their existing quality guard.
"""
from functools import lru_cache
import json

from tools.ResourcePath import get_resource_path


def effect_key(effect):
    value = str(effect.get('value1') or '').replace('\\', '/')
    return (effect['type'], value, str(effect.get('value2') or '0'))


@lru_cache(maxsize=1)
def effect_catalogue():
    path = get_resource_path('equip/resources/cangshengtf/equipment_effects.json')
    with open(path, encoding='utf-8') as stream:
        data = json.load(stream)
    if data['schemaVersion'] != 1:
        raise ValueError('Unsupported equipment effect catalogue')
    result = {}
    for entry in data['effects']:
        key = effect_key(entry)
        if key in result:
            raise ValueError('Duplicate equipment effect identity: %r' % (key,))
        result[key] = entry
    return result


def resolve_equipment_effects(effects, occ):
    """Return resolved metadata, remaining warnings and verified static values.

    Ordinary and Wujie skills have different recipe/event paths. Wujie support
    requires its own reviewed handling and an explicit specialization scope.
    """
    if not effects:
        return [], set(), {}
    from equip.CangshengAttributeData import get_profile
    get_profile(occ)  # Do not silently certify an unknown specialization.
    catalogue = effect_catalogue()
    resolved, unresolved, raw = [], set(), {}
    applied = set()
    for effect in effects:
        key = effect_key(effect)
        model = catalogue.get(key)
        handling = model.get('ordinaryHandling') if model is not None else None
        if occ.endswith('w'):
            handling = (model.get('wujieHandling') if model is not None
                        and occ in model.get('wujieOccupations', []) else None)
        if handling not in ('logged_event', 'skill_coefficient', 'inactive_mobile',
                            'inactive_ordinary', 'static_attributes', 'non_combat'):
            unresolved.add(effect['warning'])
            continue
        entry = {'source': effect['source'], 'type': key[0], 'value1': key[1],
                 'value2': key[2], 'name': model['name'],
                 'handling': handling}
        resolved.append(entry)
        if handling == 'static_attributes' and key not in applied:
            for name, value in model.get('staticAttributes', {}).items():
                raw[name] = raw.get(name, 0) + value
            applied.add(key)
    return resolved, unresolved, raw

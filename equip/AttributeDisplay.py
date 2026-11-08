# Created by moeheart at 08/31/2021
# 维护属性展示类.

from equip.AttributeCal import AttributeCal
from equip.EquipmentInfo import is_unmodeled_effect_warning
from equip.EquipmentEffects import resolve_equipment_effects
from tools.Attribute import CURRENT_GAME_EDITION
from equip.CangshengAttributeData import make_base_attributes, calculate_attributes

class AttributeDisplay():

    def GetBaseAttrib(self, str, occ):
        """Combine the current 50-level equipment, role and kungfu attributes."""
        if not str.strip():
            return None
        equipment = self.ac.CalculateAll(str)
        if not equipment:
            return None
        effects = getattr(self.ac, 'lastEffects', [])
        modeled, unresolved, extra = resolve_equipment_effects(effects, occ)
        effect_warnings = {effect['warning'] for effect in effects}
        current_warnings = [warning for warning in self.ac.lastWarnings
                            if warning not in effect_warnings or warning in unresolved]
        for name, value in extra.items():
            equipment[name] = equipment.get(name, 0) + value
        base = make_base_attributes(equipment, occ)
        if modeled:
            base['_modeledEffects'] = modeled
        if current_warnings:
            base['_warnings'] = list(current_warnings)
            warnings = sorted(set(self.status.get('warnings', []) + current_warnings))
            unmodeled = [warning for warning in warnings if is_unmodeled_effect_warning(warning)]
            invalid = [warning for warning in warnings if not is_unmodeled_effect_warning(warning)]
            base['_unmodeledEffects'] = [warning for warning in current_warnings
                                         if is_unmodeled_effect_warning(warning)]
            self.status.update(status='incomplete', warnings=warnings,
                               unmodeledEffects=unmodeled,
                               staticAttributes='partial' if invalid else 'available',
                               reason='部分装备数值无法解析。' if invalid else '特殊效果未建模；已知静态属性仍可用。')
            if invalid:
                self.status['unparsedAttributes'] = invalid
        return base

    def GetPanelAttrib(self, str, occ):
        """Calculate a panel using the current formal-server kungfu profile."""
        baseAttrib = self.GetBaseAttrib(str, occ)
        if baseAttrib is None:
            return None
        panel = calculate_attributes(baseAttrib['_raw'], occ)
        panel['_baseSource'] = baseAttrib['_baseSource']
        if baseAttrib.get('_warnings'):
            panel['_warnings'] = baseAttrib['_warnings']
        if baseAttrib.get('_unmodeledEffects'):
            panel['_unmodeledEffects'] = baseAttrib['_unmodeledEffects']
        if baseAttrib.get('_modeledEffects'):
            panel['_modeledEffects'] = baseAttrib['_modeledEffects']
        return panel


    def Display(self, str, occ):
        """Retain the original public method name for current panel callers."""
        return self.GetPanelAttrib(str, occ)

    def __init__(self, gameEdition=CURRENT_GAME_EDITION):
        # The argument remains accepted by callers; it does not select old rules.
        self.gameEdition = CURRENT_GAME_EDITION
        self.status = {"status": "supported", "staticAttributes": "available",
                       "gameEdition": self.gameEdition,
                       "profile": "cangsheng50", "source": "formal client 1.6.0.10009 Lua and item tables",
                       "assumptions": ["JCL未提供体型，裸属性采用当前客户端默认基线"]}
        self.ac = AttributeCal()

    def GetRawEquipmentFeature(self, full_id):
        """Return verified item-table fields without pretending they are a panel."""
        return self.ac.equipmentInfo.getFeature(full_id)

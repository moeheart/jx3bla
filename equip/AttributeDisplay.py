# Created by moeheart at 08/31/2021
# 维护属性展示类.

from equip.AttributeCal import AttributeCal
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
        base = make_base_attributes(equipment, occ)
        if self.ac.lastWarnings:
            base['_warnings'] = list(self.ac.lastWarnings)
            warnings = sorted(set(self.status.get('warnings', []) + self.ac.lastWarnings))
            self.status.update(status='incomplete', reason='装备含尚未解析的脚本或技能效果。', warnings=warnings)
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
        return panel


    def Display(self, str, occ):
        """Retain the original public method name for current panel callers."""
        return self.GetPanelAttrib(str, occ)

    def __init__(self, gameEdition=CURRENT_GAME_EDITION):
        # The argument remains accepted by callers; it does not select old rules.
        self.gameEdition = CURRENT_GAME_EDITION
        self.status = {"status": "supported", "gameEdition": self.gameEdition,
                       "profile": "cangsheng50", "source": "formal client 1.6.0.10009 Lua and item tables",
                       "assumptions": ["JCL未提供体型，裸属性采用当前客户端默认基线"]}
        self.ac = AttributeCal()

    def GetRawEquipmentFeature(self, full_id):
        """Return verified item-table fields without pretending they are a panel."""
        return self.ac.equipmentInfo.getFeature(full_id)

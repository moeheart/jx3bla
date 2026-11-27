from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QIcon

from Constants import COLOR_DICT
from tools.ResourcePath import get_icon_path


# Formal skill and icon tables map each recorded occupation to its in-game passive icon.
ICON_IDS = {
    '1d': 425, '1t': 429, '2d': 406, '2h': 412, '3d': 633, '3t': 632,
    '4p': 619, '4m': 627, '5d': 888, '5h': 887, '6d': 2766, '6h': 2767,
    '7p': 3165, '7m': 3184, '8': 2376, '9': 4610, '10d': 3865, '10t': 3864,
    '21d': 6314, '21t': 6315, '22d': 7071, '22h': 7067, '23': 8424, '24': 10709,
    '25': 12128, '211': 13894, '212d': 15594, '212h': 15593, '213': 17633, '214': 19664,
    '215': 22823, '1dw': 100053, '1tw': 100069, '4pw': 100389, '4mw': 100398, '2dw': 100408,
    '2hw': 100411, '3dw': 100406, '3tw': 100407, '5dw': 100410, '5hw': 100409, '6dw': 100654,
    '6hw': 100655, '7pw': 101716, '7mw': 101734, '8w': 100725, '9w': 100651, '10dw': 100618,
    '10tw': 100631, '21tw': 101025, '21dw': 101024, '22dw': 101124, '22hw': 101125, '23w': 100994,
    '24w': 101090, '25w': 101173, '211w': 101450, '212hw': 101374, '212dw': 101355, '213w': 101375,
    '214w': 101740, '215w': 102278, '34w': 24908, '34': 24896,
}


@lru_cache(maxsize=100)
def occupation_color(occ):
    school = str(occ or '').rstrip('w').rstrip('dthpm')
    rgb = COLOR_DICT.get(school)
    if not rgb or school == '0':
        return None
    color = QColor(*rgb)
    # Keep the original hue while retaining readable text on the light table background.
    while True:
        channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055)**2.4
                    for v in (color.redF(), color.greenF(), color.blueF())]
        if sum(c * w for c, w in zip(channels, (.2126, .7152, .0722))) <= .17:
            return color
        color = color.darker(108)


@lru_cache(maxsize=100)
def occupation_icon(occ):
    icon_id = ICON_IDS.get(str(occ))
    return QIcon(get_icon_path(icon_id)) if icon_id else QIcon()


def style_player_item(item, occ):
    color = occupation_color(occ)
    if color:
        item.setForeground(QBrush(color))
    item.setIcon(occupation_icon(occ))


def add_player_choice(combo, label, name, occ):
    combo.addItem(occupation_icon(occ), label, name)
    color = occupation_color(occ)
    if color:
        combo.setItemData(combo.count() - 1, QBrush(color), Qt.ItemDataRole.ForegroundRole)

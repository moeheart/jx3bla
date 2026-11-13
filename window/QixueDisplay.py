"""Format the talent slots actually recorded by a replay, including old logs."""
import re

UNAVAILABLE_TEXT = "奇穴信息获取失败。\n在进入战斗后查看目标的奇穴即可获取。\n如果是第一视角也可以自动获取。"


def format_qixue(qixue):
    """Display recorded slots in numeric order without assuming twelve slots.

    A nonempty talent snapshot is marked available by the replay producers;
    that flag does not promise a particular slot count. An unavailable or
    empty snapshot keeps the existing hint instead of interrupting the window.
    """
    if not isinstance(qixue, dict) or qixue.get('available') not in (1, True):
        return UNAVAILABLE_TEXT
    slots = []
    for key, value in qixue.items():
        if (re.fullmatch(r'[1-9][0-9]*', str(key)) and isinstance(value, str)
                and value.strip()):
            slots.append((int(key), value.strip()))
    values = [value for _, value in sorted(slots)]
    if not values:
        return UNAVAILABLE_TEXT
    return '\n'.join(','.join(values[index:index + 6]) for index in range(0, len(values), 6))

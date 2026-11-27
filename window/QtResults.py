"""Qt battle and personal replay views backed by completed analysis results."""
import math
import re
from collections.abc import Mapping
from types import SimpleNamespace

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QDialogButtonBox,
    QCompleter, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea,
    QSpinBox, QSplitter, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTableView, QTabWidget, QVBoxLayout, QWidget,
)

from Constants import FALLBACK_ADDRESS, OCC_NAME_DICT, OCC_PINYIN_DICT
from equip.EquipmentExport import forge_tooltip
from tools.RecordQuality import get_record_quality, is_effect_warning_only, is_valid_rank
from window.QtOccupation import add_player_choice, occupation_color, occupation_icon
from tools.ResourcePath import get_icon_path
from window.QixueDisplay import format_qixue


METRICS = {
    'rdps': 'rDPS', 'ndps': 'nDPS', 'mrdps': '主目标 rDPS', 'mndps': '主目标 nDPS',
    'rhps': 'rHPS', 'hps': 'HPS', 'ahps': 'aHPS', 'ohps': 'oHPS', 'chps': 'cHPS',
}
SKILLS = {
    'general': '综合', 'healer': '治疗统计', 'mufeng': '沐风', 'bcqs': '冰蚕牵丝',
    'zwjt': '醉舞九天', 'sszt': '圣手织天', 'qdtr': '千蝶吐瑞', 'dc': '蝶池',
    'mxym': '迷仙引梦', 'ghzs': '蛊惑众生', 'nvwa': '女娲补天', 'qilong': '绮栊',
    'xwgd': '仙王蛊鼎', 'dx': '蝶旋', 'ymz': '阳明指', 'syz': '商阳指', 'zlyx': '钟林毓秀',
    'lcyz': '兰摧玉折', 'kxsq': '快雪时晴', 'kxsqdot': '快雪时晴持续伤害',
    'ysjf': '玉石俱焚', 'frbd': '芙蓉并蒂', 'wozhen': '握针', 'tizhen': '提针',
    'changzhen': '长针', 'bizhen': '彼针', 'lzwh': '落子无悔', 'suiyu': '碎玉',
    'qingshu': '清疏', 'qiusu': '秋肃', 'chunni': '春泥护花', 'longwu': '泷雾',
    'lszh': '灵素中和', 'bzhf': '白芷含芳', 'cshx': '赤芍寒香', 'dgsn': '当归四逆',
    'qczl': '青川濯莲', 'ygzx': '银光照雪', 'qqhh': '七情和合', 'piaohuang': '飘黄',
    'meihua': '梅花三弄', 'zhi': '徵', 'jue': '角', 'shang': '商', 'gong': '宫', 'yu': '羽',
    'zzm': '庄周梦', 'xiangyi': '相依', 'hxpy': '回雪飘摇', 'xlwl': '翔鸾舞柳',
    'sydh': '上元点鬟', 'wmhm': '王母挥袂', 'fxda': '风袖低昂', 'zxyz': '左旋右转',
    'jwfh': '九微飞花', 'tzhy': '跳珠撼玉',
}
LABELS = {
    **METRICS, 'name': '名称', 'occ': '心法', 'score': '评分', 'num': '次数', 'time': '时间',
    'sum': '总量', 'sumPerSec': '每秒', 'percent': '占比', 'HPS': 'HPS', 'numPerSec': '每秒次数',
    'delay': '平均延迟（毫秒）', 'delaySamples': '延迟样本数', 'effRate': '有效比例',
    'efficiency': '战斗效率', 'efficiencyNonGcd': '战斗效率', 'cover': '覆盖率',
    'coverAll': '存在比例', 'stack': '平均层数', 'heal': '治疗量', 'healEff': '有效治疗',
    'damage': '伤害', 'dps': 'DPS', 'rdpsRate': 'rDPS 占比', 'shCover': '述怀覆盖',
    'skillNum': '本体次数', 'skillHPS': '本体 HPS', 'allNum': '运功次数', 'tunhai': '吞海次数',
    'anxiangNum': '暗香次数', 'anxiangNumPerSec': '暗香每秒次数', 'shuangluanNum': '双鸾次数',
    'shengxiHPS': '生息 HPS', 'hzDirectHPS': '毫针直接 HPS', 'hzPercentHPS': '毫针比例 HPS',
    'gudaoHPS': '古道 HPS', 'pingyinHPS': '平吟 HPS', 'youxiangHPS': '犹香 HPS',
    'yuehuaHPS': '月华 HPS', 'zhenliuHPS': '枕流 HPS', 'shuangluanHPS': '首跳 HPS',
    'cizhiHPS': '辞致 HPS', 'wanqingHPS': '晚晴 HPS', 'chuimeiHPS': '垂眉 HPS',
    'shieldRate': '梅花三弄覆盖率', 'shieldBreak': '破盾次数', 'HanQingNum': '寒清次数',
    'xwgdNum': '吃鼎次数', 'qilongRate': '绮栊覆盖率', 'kumuHeal': '枯木治疗量',
    'PeiwuRate': '配伍比例', 'PeiwuDPS': '配伍 DPS', 'PiaohuangNum': '飘黄次数',
    'PiaohuangAllNum': '飘黄总次数', 'PiaohuangDPS': '飘黄 DPS', 'SangrouDPS': '桑柔 DPS',
    'YujianDPS': '玉简 DPS', 'ZhuangzhouDPS': '庄周梦 DPS',
    'sketch': '装备概况', 'forge': '强化', 'spirit': '根骨', 'spunk': '元气', 'strength': '力道',
    'agility': '身法', 'attack': '攻击', 'attackBase': '基础攻击', 'healBase': '基础治疗',
    'crit': '会心等级', 'critPercent': '会心', 'critpow': '会效等级', 'critpowPercent': '会效',
    'haste': '加速等级', 'hastePercent': '加速', 'overcome': '破防等级',
    'overcomePercent': '破防', 'strain': '无双等级', 'strainPercent': '无双', 'surplus': '破招',
    'phase': '阶段', 'start': '起点', 'end': '终点', 'duration': '时长', 'source': '来源',
    'player': '玩家', 'playerID': '角色', 'target': '目标', 'mechanic': '机制', 'skill': '技能',
    'kind': '类别', 'rule': '判定依据', 'reason': '原因', 'truncated': '截至记录结束',
    'content': '内容', 'evidence': '依据', 'responsibility': '判责', 'templateID': '模板编号',
    'phasePeriods': '阶段区间', 'phaseTimes': '阶段用时', 'phaseTransitions': '阶段切换',
    'phaseChanges': '阶段标记', 'mechanicEvents': '机制记录', 'mechanics': '点名记录',
    'mechanicHits': '机制受击', 'winEvidence': '通关依据', 'endEvidence': '结束依据',
    'downtimeEvidence': '无效时间依据', 'combatEndEvidence': '脱战依据', 'soulPeriods': '聚邪区间',
    'transitionPeriods': '转场区间', 'constructPeriods': '金刚出场', 'shaPeriods': '煞将区间',
    'swords': '巨剑记录', 'chains': '锁链记录', 'shouts': '喊话', 'phaseEvidence': '分段依据',
    'phaseSummary': '阶段概况', 'limitations': '统计口径', 'mechanicNote': '机制说明',
    'bossDamageDps': '本体 DPS', 'bossDamage': '本体伤害', 'mainDps': '本体 DPS',
    'mainDamage': '本体伤害', 'stingCalls': '潜渊点名', 'inkCalls': '倒悬点名',
    'surgeHits': '奔涌命中', 'fireHits': '业火命中', 'waveHits': '浊浪命中',
    'collapseHits': '崩天命中', 'fieldCalls': '力场次数', 'swordDamage': '巨剑伤害',
    'swordDamageDps': '巨剑 DPS', 'arrowCalls': '鸣镝点名', 'hammerCalls': '千钧点名',
    'swordCalls': '承剑次数', 'slashHits': '横斩命中', 'spearHits': '突刺命中',
    'nightDamageDps': '寂夜 DPS', 'fireDamageDps': '逐焰 DPS', 'lockCalls': '逐焰锁定',
    'chainHits': '横扫命中', 'ringHits': '火环命中', 'inertDamageDps': '机关 DPS',
    'chainDamageDps': '锁链 DPS', 'prisonCalls': '钉柱点名', 'constructDamage': '金刚伤害',
    'fuyanCalls': '伏焰锁定', 'remnantCalls': '残魂点名', 'bombCalls': '投弹点名',
    'soulCalls': '聚邪点名', 'bombHits': '弹爆受击', 'abyssMax': '失魂最高层',
    'shaDamage': '煞将伤害', 'flyingDamage': '飞兵伤害', 'swordActivations': '激活剑符',
    'fragmentPickups': '拾取碎片', 'wingCalls': '获得翅膀', 'shadowCalls': '幽影点名',
    'imbalanceHits': '消融受击', 'invasionMax': '分流最高层',
    'effectiveTime': '有效时间（毫秒）', 'effectiveTimeDps': '输出有效时间（毫秒）',
    'effectiveTimeHealer': '治疗有效时间（毫秒）', 'winReason': '通关判据', 'evidenceVersion': '证据版本',
    'judgement': '判责', 'fieldsObserved': '观察到的力场数', 'signalEnd': '技能结束',
    'fieldEnd': '力场结束', 'boundaryEnd': '边界', 'excludedMs': '扣除时长（毫秒）',
    'affectDps': '影响输出', 'affectHealer': '影响治疗', 'sourceTemplate': '来源模板',
    'P1Time': '一阶段用时（秒）', 'P2Time': '二阶段用时（秒）', 'P3Time': '三阶段用时（秒）',
    'nightDamage': '寂夜伤害', 'fireDamage': '逐焰伤害', 'chainDamage': '锁链伤害',
    'inertDamage': '机关伤害', 'value': '数值',
    'jingliDeal': '精力打击', 'nailiDeal': '耐力打击', 'jingliTaken': '精力损失', 'nailiTaken': '耐力损失',
    'jingliHeal': '精力回复', 'nailiHeal': '耐力回复', 'skill1': '百战技能一', 'skill2': '百战技能二',
    'skill3': '百战技能三', 'zhendang': '震荡层数', 'raoluan': '扰乱次数', 'daoyingDPS': '倒影伤害',
    'heiyingDPS1': '群攻黑影伤害', 'heiyingDPS2': '单体黑影伤害', 'daodunDamage': '刀盾兵伤害',
    'suolianDamage': '锁链手伤害', 'banyun1': '首次搬运用时', 'banyun2': '第二次搬运用时',
    'banyun3': '第三次搬运用时', 'shumuDPS': '树木伤害', 'btDPS': '本体 DPS', 'gzTime': '接罐次数',
    'fyTime': '扶摇次数', 'xgDPS': '小怪 DPS', 'ws2DPS': '双武士 DPS', 'ws4DPS': '四武士 DPS',
    'fx1DPS': '恐惧阶段打错', 'fx2DPS': '武士阶段打错', 'lhDPS1': '灵护一 DPS', 'lhDPS2': '灵护二 DPS',
    'mjDPS1': '魔剑一 DPS', 'mjDPS2': '魔剑二 DPS', 'wcDPS': '外场 DPS', 'fzDPS': '符咒 DPS',
    'qyDPS': '泉眼 DPS', 'numNayuan': '纳元次数', 'numPoye': '破野次数', 'mengdieDPS': '梦蝶伤害',
    'dieyuNum': '蝶雨次数', 'yztzDamage': '图腾伤害', 'binghuaDPS': '冰晶花伤害',
    'sfsDamage': '水分身伤害', 'nxzmRight': '逆心转脉正确', 'nxzmWrong': '逆心转脉失误',
    'lzDPS': '刘展 DPS', 'qwDPS': '枪卫 DPS', 'fwDPS': '斧卫 DPS', 'zjcDPS': '张景超 DPS',
    'jfDPS1': '第一轮劲风 DPS', 'jfDPS2': '第二轮劲风 DPS', 'zflDPS1': '第一轮张法雷 DPS',
    'zflDPS2': '第二轮张法雷 DPS', 'xiuxue': '金翅鸟修血伤害', 'damageTaken': '首领回蓝次数',
    'ybj': '月崩击 DPS', 'yj': '月茧 DPS', 'sdldNum': '三刀六洞次数', 'GarbageDamage': '无效目标伤害',
    'baizhan': '百战记录', 'pozhanList': '破绽记录', 'shejian': '射箭记录', 'info': '机制详情',
    'fenshenDPS': '分身 DPS', 'winRule': '通关规则', 'winEvidenceRecommendation': '判定建议',
    'winEvidenceReport': '通关证据报告', 'phps': '原始 HPS', 'chpsDescription': '关键治疗口径',
    'P2Time1': '二阶段首轮用时（秒）', 'P2Time2': '二阶段次轮用时（秒）',
    'P3Time1': '三阶段首轮用时（秒）', 'P3Time2': '三阶段次轮用时（秒）',
    'P3ybjTime': '月崩击用时（秒）', 'P3yjTime': '月茧用时（秒）',
    'btTime': '本体阶段用时（秒）', 'wcTime': '外场用时（秒）',
}
for _i in range(1, 4):
    LABELS.update({f'P{_i}DPS': f'P{_i} DPS', f'P{_i}Damage': f'P{_i} 伤害',
                   f'P{_i}BossDamage': f'P{_i} 本体伤害', f'P{_i}AddEffective': f'P{_i} 小怪有效伤害',
                   f'nc{_i}DPS': f'内场 {_i} DPS', f'nc{_i}Time': f'内场 {_i} 用时（秒）'})
for _i in (1, 2):
    LABELS.update({f'yr{_i}1': f'第 {_i} 次天引 · 第一轮掩日伤害', f'yr{_i}2': f'第 {_i} 次天引 · 第二轮掩日伤害',
                   f'yr{_i}group': f'第 {_i} 次天引分组', f'yr{_i}hit': f'第 {_i} 次天引命中',
                   f'yr{_i}delay': f'第 {_i} 次天引用时（毫秒）'})
for _i in range(1, 7):
    LABELS[f'Eye{_i}Damage'] = f'阿里曼之眼 {_i} 伤害'
PERCENT = {'effRate', 'efficiency', 'efficiencyNonGcd', 'cover', 'coverAll', 'shCover', 'rdpsRate',
           'shieldRate', 'qilongRate', 'PeiwuRate', 'percent'}
POT_LEVELS = {0: '观察／轻微', 1: '严重', 2: '提示', 3: '补贴'}
COMMON_ROSTER = {'name', 'occ', 'rdps', 'ndps', 'hps', 'score', 'rdpsRank', 'scoreRank',
                 'rdpsRankNum', 'scoreRankNum', 'equip', 'stunTime', 'battle', 'rdpsStatus',
                 'attributeEstimated', 'equipmentEstimated', 'rhpsRank', 'rhpsRankNum', 'exp', 'experience', 'healerScore'}


def _get(obj, name, default=None):
    return obj.get(name, default) if isinstance(obj, Mapping) else getattr(obj, name, default)


def _mapping(value):
    return value if isinstance(value, Mapping) else {}


def _text(value):
    if value is None or value == '':
        return '—'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, float):
        return str(int(value)) if math.isfinite(value) else '—'
    return str(value)


def _format(key, value):
    if key == 'occ':
        return OCC_NAME_DICT.get(str(value), str(value))
    if isinstance(value, (list, tuple)):
        return '、'.join(_format('', item) for item in value) or '—'
    if isinstance(value, Mapping):
        return '；'.join(f'{LABELS.get(k, k)} {_format(k, v)}' for k, v in value.items()) or '—'
    if key in PERCENT and isinstance(value, (int, float)):
        return f'{value:.0%}'
    if key.endswith('PerSec') and key != 'sumPerSec' and isinstance(value, (int, float)):
        # Cast frequencies below one per second would all round to zero.
        return f'{value:.2f}'.rstrip('0').rstrip('.')
    return _text(value)


def _clock(ms):
    sign = '−' if ms < 0 else ''
    secs = int(abs(ms)) // 1000
    return f'{sign}{secs // 60}:{secs % 60:02}'


def _label(value=''):
    label = QLabel(value)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return label


def _padded_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(8, 8, 8, 8)
    return page, layout


BAR_ROLE = Qt.ItemDataRole.UserRole + 1


def _rank_color(percent):
    # Logs thresholds, with shades readable against the desktop's light background.
    for ceiling, color in ((25, '#666666'), (50, '#137310'), (75, '#005ebe'),
                           (95, '#8b27bd'), (98, '#b15100'), (100, '#aa3377'), (101, '#886600')):
        if percent < ceiling:
            return QColor(color)


def _finite_positive(value):
    return value if isinstance(value, (float, int)) and math.isfinite(value) and value > 0 else 0


def _equipment_score(equip):
    try:
        score = int(equip.get('score') or 0)
    except (TypeError, ValueError, OverflowError):
        score = 0
    if score > 0:
        return str(score)
    return '未记录装分' if equip.get('sketch') or equip.get('raw') else '未读取'


def _team_equipment_sketch(sketch):
    fields = (field.strip() for field in (sketch or '').split('，'))
    return '，'.join(field for field in fields if field not in ('', '无套装', '0白字', '0黄字'))


class _BarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        fraction = index.data(BAR_ROLE)
        color = index.data(Qt.ItemDataRole.ForegroundRole)
        if fraction is None and color is None:
            return super().paint(painter, option, index)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        alternate = bool(opt.features & QStyleOptionViewItem.ViewItemFeature.Alternate)
        background = QPalette.ColorRole.AlternateBase if alternate else QPalette.ColorRole.Base
        if selected:
            background = QPalette.ColorRole.Highlight
        painter.save()
        painter.fillRect(opt.rect, opt.palette.brush(background))
        if fraction:
            bar = QColor(56, 143, 127, 55)
            if index.model().occupations:
                school = occupation_color(index.model().occupations[index.row()])
                if school:
                    bar = QColor(school)
                    bar.setAlpha(42)
            rect = opt.rect.adjusted(0, 2, 0, -2)
            rect.setWidth(round(rect.width() * fraction))
            painter.fillRect(rect, bar)
        # Let the native style draw icons, text elision and the focus indicator on top.
        opt.state &= ~QStyle.StateFlag.State_Selected
        opt.features &= ~QStyleOptionViewItem.ViewItemFeature.Alternate
        opt.backgroundBrush = QBrush(Qt.BrushStyle.NoBrush)
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)
        painter.restore()


class _Rows(QAbstractTableModel):
    """Show text on demand, even for long mechanic histories; selection follows source row order."""
    def __init__(self, headers, rows, parent, occupations=None, bars=None, tips=None, ranks=None, header_tips=None):
        super().__init__(parent)
        self.occupations = occupations or []
        self.headers = headers
        self.rows = rows
        self.tips = tips or {}
        self.ranks = ranks or {}
        self.header_tips = header_tips or {}
        self.bars = {}
        for column, values in (bars or {}).items():
            self.set_bars(column, values)

    def set_bars(self, column, values):
        weights = [_finite_positive(v) for v in values]
        maximum = max(weights, default=0)
        self.bars[column] = [v / maximum if maximum else 0 for v in weights]

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        cell = (index.row(), index.column())
        if role == BAR_ROLE and index.column() in self.bars:
            return self.bars[index.column()][index.row()]
        if role == Qt.ItemDataRole.ToolTipRole and cell in self.tips:
            return self.tips[cell]
        if role == Qt.ItemDataRole.ForegroundRole and cell in self.ranks:
            return QBrush(_rank_color(self.ranks[cell]))
        if index.column() == 0 and self.occupations:
            occ = self.occupations[index.row()]
            if role == Qt.ItemDataRole.DecorationRole:
                return occupation_icon(occ)
            if role == Qt.ItemDataRole.ForegroundRole:
                color = occupation_color(occ)
                return QBrush(color) if color else None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            return _text(self.rows[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.ToolTipRole:
            return self.header_tips.get(section)
        if role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section] if orientation == Qt.Orientation.Horizontal else str(section + 1)
        return None


def _table():
    table = QTableView()
    table.setItemDelegate(_BarDelegate(table))
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.setWordWrap(False)
    table.setShowGrid(False)
    table.verticalHeader().setDefaultSectionSize(23)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    return table


def _fill(table, headers, rows, occupations=None, **options):
    model = _Rows(headers, list(rows), table, occupations, **options)
    old = table.model()
    old_selection = table.selectionModel()
    table.setModel(model)
    if old is not None:
        old.deleteLater()
    if old_selection is not None:
        old_selection.deleteLater()
    table.horizontalHeader().setResizeContentsPrecision(30)
    table.resizeColumnsToContents()


# Skill icons used by the original specialization reports, in their display order.
SKILL_ICONS = {
    'wozhen':1519, 'tizhen':395, 'changzhen':396, 'bizhen':1518, 'lzwh':17705, 'suiyu':13441,
    'hxpy':894, 'xlwl':897, 'sydh':913, 'wmhm':900, 'fxda':1507, 'zxyz':904,
    'meihua':7059, 'zhi':7174, 'jue':7176, 'shang':7172, 'gong':7173, 'yu':7175,
    'lszh':16025, 'bzhf':15411, 'cshx':15414, 'dgsn':15412, 'qczl':15420, 'ygzx':15400,
    'bcqs':2745, 'zwjt':2746, 'sszt':3028, 'qdtr':2748, 'dc':9567, 'mxym':7255,
    'ymz':1527, 'syz':1514, 'zlyx':404, 'lcyz':390, 'kxsq':2999, 'ysjf':411, 'frbd':398,
}


class _CardModel(QAbstractTableModel):
    def __init__(self, cards, columns, parent):
        super().__init__(parent)
        self.cards = cards
        self.columns = columns

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else (len(self.cards) + self.columns - 1) // self.columns

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else self.columns

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        i = index.row() * self.columns + index.column()
        if i >= len(self.cards):
            return None
        text, icon, tooltip = self.cards[i]
        return {Qt.ItemDataRole.DisplayRole:text, Qt.ItemDataRole.ToolTipRole:tooltip,
                Qt.ItemDataRole.DecorationRole:icon}.get(role)


class _SkillCards(QTableView):
    """Keep all core skills together and wrap cards to the available window width."""
    def __init__(self, cards):
        super().__init__()
        self.setModel(_CardModel(cards, 3, self))
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setDefaultSectionSize(57)
        self.setIconSize(QSize(23,23))
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setStyleSheet('QTableView::item {border:1px solid #dfe8e6; padding:2px; background:#f8faf9;}')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        model = self.model()
        cols = max(1, min(len(model.cards), 4, self.viewport().width() // 155))
        if cols != model.columns:
            model.beginResetModel()
            model.columns = cols
            model.endResetModel()


class BattleView(QWidget):
    notesChanged = Signal()
    """Browse an actor or compact snapshot. Raw combat events are never required by this widget."""
    def __init__(self, actor, parent=None):
        super().__init__(parent)
        if isinstance(actor, Mapping):
            if isinstance(actor, dict):
                actor.setdefault('potList', [])
            actor = SimpleNamespace(**actor)
            if isinstance(getattr(actor, 'bh', None), Mapping):
                actor.bh = SimpleNamespace(**actor.bh)
        self.actor = actor
        self.detail = _mapping(_get(actor, 'detail'))
        self.occ_results = _mapping(_get(actor, 'occResult'))
        self.tracker = _get(actor, 'combatTracker', {})
        self.rdps_amounts = {}
        for player in _get(self.tracker, 'rdps', {}).get('player', {}).values():
            value = player.get('dps', player.get('sumPerSec'))
            if type(value) in (int, float) and math.isfinite(value):
                self.rdps_amounts[player.get('name')] = value
        self.roster = []
        for row in _get(actor, 'statDict', ()) or ():
            if isinstance(row, Mapping):
                self.roster.append(row)
            elif isinstance(row, (tuple, list)) and len(row) >= 3:
                # Early boss tables contain direct DPS in column 3.
                legacy = dict(name=row[0], occ=row[1], ndps=row[2])
                if len(row) > 5:
                    sketch, _, forge = str(row[5]).partition('|')
                    legacy['equip'] = {'score': row[4] if row[4] != -1 else '', 'sketch': sketch, 'forge': forge}
                if len(row) > 6:
                    legacy['stunTime'] = row[6]
                for i, value in enumerate(row[7:], 1):
                    legacy[f'旧版专项 {i}'] = value
                self.roster.append(legacy)
        self.names = list(dict.fromkeys([r['name'] for r in self.roster if r.get('name')] +
                                        list(self.occ_results)))
        self.occupations = {r["name"]: r.get("occ") for r in self.roster if r.get("name")}
        self.occupations.update({name: e.get("occ") for name, e in self.occ_results.items() if e.get("occ")})
        self.names_by_id = dict(_get(actor, 'playerNames', {}) or {})
        for name, entry in self.occ_results.items():
            overall = _get(_get(entry, 'result', {}), 'overall', {})
            if overall.get('mykey') is not None:
                self.names_by_id[str(overall['mykey'])] = name
        for metric in METRICS:
            for pid, stats in _get(self.tracker, metric, {}).get('player', {}).items():
                if stats.get('name') in self.names:
                    self.names_by_id[str(pid)] = stats['name']
        # Older results can include a healer or a marked player outside the visible roster.
        sensitive = list(self.names) + list(self.names_by_id.values())
        for pot in _get(actor, 'potList', ()) or ():
            if pot:
                sensitive.append(str(pot[0]).strip('"'))
        for entry in self.occ_results.values():
            data = _mapping(entry.get('result', entry))
            for section in ('healer', 'dps'):
                for row in _mapping(data.get(section)).get('table', ()):
                    if isinstance(row, Mapping):
                        sensitive.append(row.get('name'))
        sensitive = list(dict.fromkeys(name for name in sensitive if isinstance(name, str) and name))
        self.aliases = {name: f'队员{i:02}' for i, name in enumerate(sensitive, 1)}
        pattern = '|'.join(map(re.escape, sorted(sensitive, key=len, reverse=True)))
        self.name_pattern = re.compile(pattern) if pattern else None
        config = _get(_get(actor, 'config'), 'item', {})
        self.mask = _get(actor, 'mask', config.get('general', {}).get('mask', 0)) in (1, True, '1')
        tracker_status = _get(self.tracker, 'rdpsStatus') or _get(self.tracker, 'rdps', {}) or {}
        self.display_ranks = _mapping(_get(actor, "displayRanks"))
        self.equipment_source_notes = _mapping(_get(actor, 'equipmentSourceNotes'))
        self.status = (_get(actor, 'attributeStatus') or self.detail.get('attributeStatus')
                       or self.detail.get('rdpsStatus') or tracker_status)
        qualities = {'attributeStatus': self.status, 'rdpsStatus': tracker_status, 'statistics': self.detail}
        self.quality = get_record_quality(qualities)
        self.effects_only = is_effect_warning_only(qualities)
        self.boss = self.detail.get('boss') or _get(actor, 'bossAnalyseName', '战斗复盘')
        self.pots = _get(actor, 'potList')
        if self.pots is None:
            self.pots = []
            if isinstance(actor, dict):
                actor['potList'] = self.pots
            else:
                actor.potList = self.pots
        self.current_player = None
        self.pages = {}
        self.setWindowTitle(self.boss)
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = _label(self.boss)
        title.setStyleSheet('font-size: 22px; font-weight: 600')
        header.addWidget(title)
        result = self.detail.get('win', _get(actor, 'win'))
        status_text = {0: '未确认通关', 1: '通关'}.get(result, '通关状态未知')
        context = [self.detail.get('map') or _get(actor, 'mapDetail'), status_text, f'{len(self.roster)} 人']
        start, end = _get(actor, 'startTime'), _get(actor, 'finalTime')
        if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start:
            context.append('用时 ' + _clock(end - start))
        subtitle = _label('  ·  '.join(filter(None, context)))
        subtitle.setObjectName('muted')
        title.setWordWrap(False)
        header.addSpacing(8)
        header.addWidget(subtitle, 1)
        layout.addLayout(header)
        missing = _mapping(self.status.get('missingEquipmentPlayers'))
        estimated = _mapping(self.status.get('estimatedPlayers'))
        self.equipment_issues = {}
        for player_id, issue in missing.items():
            name = self.names_by_id.get(str(player_id))
            if name in self.occupations:
                self.equipment_issues[name] = (issue, player_id in estimated or str(player_id) in estimated)
        if self.equipment_issues:
            affected = len(self.equipment_issues)
            count = sum(int(is_estimated) for _, is_estimated in self.equipment_issues.values())
            summary = f'团队装备：{len(self.roster) - affected}/{len(self.roster)} 人资料齐全'
            if count:
                summary += f'，{count} 人使用估算'
            if affected > count:
                summary += f'，{affected-count} 人资料不足'
            layout.addWidget(_label(summary))
        elif not self.quality['precise']:
            warning = _label('团队装备已读取，部分装备特效尚未建模。' if self.effects_only else '本场属性或目标参数待校准。')
            layout.addWidget(warning)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        for name, factory in [('团队', self._team),
                              ('战斗记录', self._mistakes), ('数值统计', self._combat),
                              ('时间轴', self._timeline), ('个人复盘', self._personal)]:
            page, body = _padded_page()
            self.pages[self.tabs.addTab(page, name)] = (body, factory)
        self.tabs.currentChanged.connect(self._show_tab)
        self._show_tab(0)

    def _show_tab(self, index):
        page = self.pages.pop(index, None)
        if page:
            body, factory = page
            factory(body)
        if self.tabs.tabText(index) == '个人复盘':
            self.refresh_links()

    def _redact(self, value, mask=None):
        if (self.mask if mask is None else mask) and self.name_pattern and isinstance(value, str):
            return self.name_pattern.sub(lambda m: self.aliases[m[0]], value)
        return value

    def _render(self, key, value, mask=None):
        if key == 'name' and isinstance(value, str):
            value = LABELS.get(value, value)
        if key in ('player', 'playerID', 'target') and value is not None and not isinstance(value, (list, dict)):
            if key == 'playerID' and (self.mask if mask is None else mask) and str(value) not in self.names_by_id:
                return '未识别队员'
            value = self.names_by_id.get(str(value), value)
        return self._redact(_format(key, value), mask)

    def _team(self, body):
        extra = []
        for row in self.roster:
            for key in (*_mapping(row.get('battle')), *row):
                if key not in COMMON_ROSTER and key not in extra:
                    extra.append(key)
        rhps = {data.get('name'): data.get('hps', data.get('sumPerSec'))
                for data in _get(self.tracker, 'rhps', {}).get('player', {}).values()}
        self.team_roster = sorted(self.roster, key=lambda r: _finite_positive(self._source_rdps(r)), reverse=True)
        rows = []
        tips, ranks = {}, {}
        for i, row in enumerate(self.team_roster):
            equip = _mapping(row.get('equip'))
            rank, rank_display, tip = self._rdps_rank(row.get('name'))
            tips[i, 6] = tip
            if source := self.equipment_source_notes.get(row.get('name')):
                tips[i, 7] = tips[i, 8] = source
            tips[i, 9] = forge_tooltip(equip.get('forge') or '')
            if rank is not None:
                ranks[i, 6] = rank
            rows.append([
                self._redact(row.get('name', '')) + (' *' if row.get('equipmentEstimated') else ''),
                _format('occ', row.get('occ')), self._team_rdps(row),
                row.get('ndps'), rhps.get(row.get('name'), row.get('rhps')), row.get('hps'),
                rank_display, _equipment_score(equip), _team_equipment_sketch(equip.get('sketch')),
                equip.get('forge'), row.get('stunTime'),
                *(self._render(k, row.get(k, _mapping(row.get('battle')).get(k))) for k in extra)])
        self.team_table = _table()
        _fill(self.team_table, ['玩家', '心法', 'rDPS', 'nDPS', 'rHPS', 'HPS', 'rDPS 百分位', '装分', '装备', '强化', '被控（秒）',
                                *(LABELS.get(k, k) for k in extra)], rows, [row.get('occ') for row in self.team_roster],
              bars={0: [r[2] for r in rows]}, tips=tips, ranks=ranks,
              header_tips={0: '条形长度按本场玩家 rDPS 最高值折算', 6: '线上 Logs 同版本、同难度、同首领、同心法的全程 rDPS 百分位',
                           9: forge_tooltip()})
        self.team_table.setColumnWidth(0, max(145, self.team_table.columnWidth(0)))
        phases = self.detail.get('phaseTimes')
        if isinstance(phases, Mapping) and phases:
            times = '   ·   '.join(f'{phase} {_clock(seconds * 1000)}' for phase, seconds in phases.items()
                                 if isinstance(seconds, (float, int)) and seconds > 0)
            if times:
                body.addWidget(_label('阶段用时   ' + self._redact(times)))
        elif isinstance(self.detail.get('phaseSummary'), str) and self.detail['phaseSummary']:
            body.addWidget(_label(self._redact(self.detail['phaseSummary'])))
        body.addWidget(self.team_table)
        open_button = QPushButton('查看选中玩家的复盘')
        open_button.setEnabled(False)
        bar = QHBoxLayout()
        bar.addStretch()
        bar.addWidget(open_button)
        body.addLayout(bar)
        def selected():
            i = self.team_table.currentIndex().row()
            return self.team_roster[i].get('name') if i >= 0 else None
        self.team_table.selectionModel().currentRowChanged.connect(
            lambda *_: open_button.setEnabled(selected() in self.occ_results))
        open_button.clicked.connect(lambda: self.open_player(selected()))
        self.team_table.clicked.connect(
            lambda index: self.open_player(self.team_roster[index.row()].get('name')) if index.column() == 0 else None)
        self.team_table.doubleClicked.connect(lambda index: self.open_player(self.team_roster[index.row()].get('name')))
        if rows:
            self.team_table.selectRow(0)

    def _source_rdps(self, row):
        name = row.get('name')
        if name in self.rdps_amounts:
            return self.rdps_amounts[name]
        value = row.get('rdps')
        if value is None:
            entry = _mapping(self.occ_results.get(name))
            skills = _mapping(entry.get('result', entry)).get('skill')
            value = _mapping(_mapping(skills).get('general')).get('rdps')
        return value if type(value) in (int, float) and math.isfinite(value) else None

    def _team_rdps(self, row):
        supported = self.quality['precise'] and row.get('rdpsStatus') not in ('incomplete', 'estimated')
        reference = (self.quality['estimated'] or row.get('attributeEstimated')
                     or row.get('rdpsStatus') == 'estimated' or self.effects_only)
        if supported or reference or self._rdps_rank(row.get('name'))[0] is not None:
            return self._source_rdps(row)
        return None

    def _rdps_rank(self, name):
        display = _mapping(self.display_ranks.get(name))
        rank, count = display.get('percent'), display.get('num')
        if display.get('scope') == 'logs' and display.get('metric') == 'rdps':
            if display.get('basis') == 'unavailable':
                return None, '无法归因', '本场该玩家的 rDPS 缺少可核验的归因数据。'
            if is_valid_rank(rank) and rank <= 100 and isinstance(count, int) and count > 0:
                tip = f'线上 Logs · 同版本、同难度、同首领、同心法\n全程 rDPS 第 {rank:.0f} 百分位，样本 {count} 人'
                quality = {'estimated_equipment': '装备属性含估算', 'unmodeled_effects': '含未建模特效',
                           'partial_attribution': '部分归因', 'reported': '按记录值计算'}.get(display.get('basis'))
                if quality:
                    tip += '\n' + quality
                return rank, f'{rank:.0f}%', tip
        return None, '暂无线上样本', '当前没有可用的同版本、同难度、同首领、同心法的线上 rDPS 分布。'

    def refresh_display_ranks(self, mapping):
        """Apply a new Logs distribution in place without disturbing navigation."""
        self.display_ranks = _mapping(mapping)
        if hasattr(self, 'team_table'):
            model = self.team_table.model()
            for i, row in enumerate(self.team_roster):
                rank, label, tip = self._rdps_rank(row.get('name'))
                model.rows[i][6], model.tips[i, 6] = label, tip
                if rank is None:
                    model.ranks.pop((i, 6), None)
                else:
                    model.ranks[i, 6] = rank
                model.rows[i][2] = self._team_rdps(row)
            if model.rowCount():
                model.set_bars(0, (row[2] for row in model.rows))
                model.dataChanged.emit(model.index(0, 0), model.index(model.rowCount()-1, 6))
        if self.current_player and getattr(self, 'personal_rank', None):
            self._update_personal_rank()
            row = next((r for r in self.roster if r.get('name') == self.current_player), {'name': self.current_player})
            value = self._team_rdps(row)
            self.personal_rdps.setText(f'{int(value):,}' if value is not None else '—')

    def _mistakes(self, body):
        self.pot_table = _table()
        self.pot_details = QPlainTextEdit()
        self.pot_details.setReadOnly(True)
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(self.pot_table)
        split.addWidget(self.pot_details)
        split.setStretchFactor(0, 3)
        body.addWidget(split)
        bar = QHBoxLayout()
        add = QPushButton('添加手动记录')
        add.setEnabled(bool(self.names))
        add.clicked.connect(self._manual_dialog)
        bar.addWidget(add)
        bar.addStretch()
        self.pot_actions = []
        for title, fn in [('扣 1 分', lambda: self.adjust_pot(-1)), ('加 1 分', lambda: self.adjust_pot(1)),
                          ('复制记录', self.copy_pot)]:
            button = QPushButton(title)
            button.clicked.connect(fn)
            bar.addWidget(button)
            self.pot_actions.append(button)
        body.addLayout(bar)
        QShortcut(QKeySequence.StandardKey.Copy, self.pot_table, activated=self.copy_pot)
        self._refresh_pots(0)

    def _refresh_pots(self, selection):
        rows = []
        for pot in self.pots:
            rows.append([self._redact(str(pot[0]).strip('"')), _format('occ', pot[1]),
                         POT_LEVELS.get(pot[2], pot[2]), self._redact(pot[4]), pot[6] if len(pot) > 6 else 0])
        _fill(self.pot_table, ['玩家', '心法', '性质', '记录', '分数'], rows, [p[1] for p in self.pots])
        def select():
            index = self.pot_table.currentIndex().row()
            for button in self.pot_actions:
                button.setEnabled(index >= 0)
            if index < 0:
                self.pot_details.clear()
                return
            pot = self.pots[index]
            detail = pot[5] if len(pot) > 5 else []
            lines = detail if isinstance(detail, (list, tuple)) else [detail]
            self.pot_details.setPlainText(self._redact('\n'.join(str(v) for v in [pot[4], *lines] if v)))
        self.pot_table.selectionModel().currentRowChanged.connect(select)
        if rows:
            self.pot_table.selectRow(min(max(selection, 0), len(rows)-1))
        select()

    def adjust_pot(self, delta):
        index = self.pot_table.currentIndex().row()
        if index >= 0:
            pot = list(self.pots[index])
            while len(pot) < 7:
                pot.append(0)
            pot[6] = int(pot[6]) + delta
            self.pots[index] = pot
            self._refresh_pots(index)
            self.notesChanged.emit()

    def copy_pot(self):
        index = self.pot_table.currentIndex().row()
        if index >= 0:
            pot = self.pots[index]
            name = str(pot[0]).strip('"')
            QApplication.clipboard().setText(self._redact(f'[{name}] {pot[4]}'))

    def add_pot(self, name, description, severity=0, score=0):
        if name not in self.names or not description.strip():
            return False
        occ = next((r.get('occ', '0') for r in self.roster if r.get('name') == name), '0')
        self.pots.append([name, occ, severity, self.boss, '[手动] ' + description.strip(), [], score])
        self.notesChanged.emit()
        if hasattr(self, 'pot_table'):
            self._refresh_pots(len(self.pots)-1)
        return True

    def _manual_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('添加战斗记录')
        form = QFormLayout(dialog)
        player = QComboBox()
        for name in self.names:
            add_player_choice(player, self._redact(name), name, self.occupations.get(name))
        level = QComboBox()
        for severity in (0, 1, 3):
            level.addItem(POT_LEVELS[severity], severity)
        desc = QLineEdit()
        score = QSpinBox()
        score.setRange(-999, 999)
        for label, field in [('玩家', player), ('性质', level), ('说明', desc), ('分数', score)]:
            form.addRow(label, field)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        desc.textChanged.connect(lambda text: buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(text.strip())))
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.add_pot(player.currentData(), desc.text(), level.currentData(), score.value())

    def _combat(self, body):
        self.combat_selector = QComboBox()
        for key, name in METRICS.items():
            self.combat_selector.addItem(name, key)
        metric_bar = QHBoxLayout()
        metric_bar.addWidget(_label('统计口径'))
        metric_bar.addWidget(self.combat_selector)
        self.combat_detail_for = _label()
        metric_bar.addSpacing(12)
        metric_bar.addWidget(self.combat_detail_for, 1)
        body.addLayout(metric_bar)
        self.combat_table, self.combat_skill, self.combat_targets = _table(), _table(), _table()
        split = QSplitter(Qt.Orientation.Vertical)
        split.setChildrenCollapsible(False)
        details = QSplitter(Qt.Orientation.Horizontal)
        details.setChildrenCollapsible(False)
        for title, table in [('团队数值', self.combat_table), ('技能明细', self.combat_skill),
                             ('目标 / 增益来源', self.combat_targets)]:
            panel, content = _padded_page()
            content.setContentsMargins(0, 0, 0, 0)
            heading = _label(title)
            heading.setStyleSheet('font-weight: 600')
            content.addWidget(heading)
            content.addWidget(table, 1)
            (split if table is self.combat_table else details).addWidget(panel)
            table.horizontalHeader().setStretchLastSection(False)
            table.setMinimumHeight(84)
        split.addWidget(details)
        split.setSizes([360, 240])
        details.setSizes([465, 465])
        body.addWidget(split, 1)
        def change():
            key = self.combat_selector.currentData()
            data = _get(self.tracker, key, {}) or {}
            def amount_for(player):
                if key == 'rdps':
                    return self.rdps_amounts.get(player.get('name'))
                return player.get('sumPerSec', player.get('hps', player.get('dps')))
            players = sorted(_mapping(data.get('player')).values(),
                             key=lambda r: _finite_positive(amount_for(r)), reverse=True)
            blocked = key in ('rdps', 'mrdps') and not self.quality['precise'] and not (
                self.quality['estimated'] or self.effects_only)
            if blocked:
                players = [p for p in players if key == 'rdps' and self._rdps_rank(p.get('name'))[0] is not None]
            amount = [amount_for(p) for p in players]
            _fill(self.combat_table, ['玩家', '心法', METRICS[key], '总量', '有效时间'],
                  ([self._redact(p.get('name')), _format('occ', p.get('occ')),
                    value, p.get('sum'), _clock(p['adjustedTime']) if isinstance(p.get('adjustedTime'), (int, float)) else None]
                   for p, value in zip(players, amount)),
                  [p.get('occ') for p in players],
                  bars={0: amount})
            self.combat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            def select():
                i = self.combat_table.currentIndex().row()
                data = players[i] if i >= 0 else {}
                self.combat_detail_for.setText(self._redact(data.get('name', '')))
                color = occupation_color(data.get('occ'))
                self.combat_detail_for.setStyleSheet('font-weight:600; color:' + color.name() if color else '')
                for table, field in [(self.combat_skill, 'namedSkill'),
                                     (self.combat_targets, 'namedSource' if key in ('rdps', 'mrdps') else 'namedTarget')]:
                    items = sorted(_mapping(data.get(field)).items(), key=lambda item: item[1].get('sum', 0), reverse=True)
                    amounts = [v.get('sum') for _, v in items]
                    titles = [{'namedSource':'增益来源', 'namedSkill':'技能', 'namedTarget':'目标'}[field], '次数', '总量', '占比']
                    rows = [[self._redact(name), v.get('num'), v.get('sum') if v.get('sum') != -1 else None,
                             _format('percent', v.get('percent'))] for name, v in items]
                    tips = {}
                    if field == 'namedSource':
                        # CombatTracker exports the integral of buff stacks divided by effective time.
                        # Multi-stack buffs can have large values which cannot represent percent uptime.
                        titles.append('平均层数')
                        tips = {3: '相对自身伤害的比例', 4: '增益层数随时间的积分 ÷ 有效时间'}
                        for row, (_, item) in zip(rows, items):
                            cover = item.get('cover')
                            row.append(f'{cover:.2f}'.rstrip('0').rstrip('.') if isinstance(cover, (float,int)) and cover >= 0 else None)
                    _fill(table, titles, rows,
                          [self.occupations.get(name) for name, _ in items] if field != 'namedSkill' else None,
                          bars={0: amounts}, header_tips=tips)
                    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.combat_table.selectionModel().currentRowChanged.connect(select)
            if players:
                index = next((i for i, p in enumerate(players) if p.get('name') in self.occupations), 0)
                self.combat_table.selectRow(index)
            select()
        self.combat_selector.currentIndexChanged.connect(change)
        change()

    def _timeline(self, body):
        from window.QtTimeline import TimelineView
        body.addWidget(TimelineView.from_actor(self.actor, parent=self))
    def open_player(self, name):
        if name not in self.occ_results:
            return False
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        index = self.player_selector.findData(name)
        if index != self.player_selector.currentIndex():
            self.player_selector.setCurrentIndex(index)
        return True

    def _personal(self, body):
        self.player_selector = QComboBox()
        self.player_selector.setEditable(True)
        self.player_selector.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.player_selector.setMinimumContentsLength(12)
        for name, entry in self.occ_results.items():
            personal_mask = _get(_get(entry, 'result', {}), 'overall', {}).get('mask') in (1, True, '1')
            text = self._redact(name, self.mask or personal_mask) + ' · ' + _format('occ', entry.get('occ'))
            add_player_choice(self.player_selector, text, name, entry.get('occ'))
        completer = self.player_selector.completer()
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.player_selector.lineEdit().setPlaceholderText('输入角色名筛选')
        self.player_selector.setAccessibleName('搜索参战角色')
        actions = QHBoxLayout()
        actions.addWidget(self.player_selector)
        self.personal_summary = _label()
        actions.addWidget(self.personal_summary, 1)
        self.web_button = QPushButton('查看网页')
        self.web_button.clicked.connect(self._open_personal_web)
        actions.addWidget(self.web_button)
        self.copy_link = QPushButton('复制链接')
        self.copy_link.clicked.connect(self._copy_personal_link)
        actions.addWidget(self.copy_link)
        body.addLayout(actions)
        self.personal_scroll = QScrollArea()
        self.personal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.personal_scroll.setWidgetResizable(True)
        body.addWidget(self.personal_scroll, 1)
        self.player_selector.currentIndexChanged.connect(self._change_player)
        self._change_player()

    def _change_player(self):
        name = self.player_selector.currentData()
        self.current_player = name
        old = self.personal_scroll.takeWidget()
        if old:
            old.deleteLater()
        self.personal_dashboard, body = _padded_page()
        self.personal_dashboard.setObjectName('personalDashboard')
        body.setContentsMargins(2, 2, 2, 2)
        body.setSpacing(4)
        self.personal_scroll.setWidget(self.personal_dashboard)
        self.personal_timeline = self.skill_table = self.support_table = self.equipment_summary = self.personal_rank = None
        if not name:
            self.refresh_links()
            self.personal_summary.setText('这场战斗没有生成个人复盘。')
            return
        entry = self.occ_results[name]
        self.result = _mapping(entry.get('result', entry))
        self.refresh_links()
        self.rank = _mapping(entry.get('rank') or self.result.get('rank'))
        overall = _mapping(self.result.get('overall'))
        self.personal_mask = self.mask or overall.get('mask') in (1, True, '1')
        self.personal_quality = get_record_quality({'overall': overall, 'quality': self.quality})
        summary = [overall.get('battleTimePrint')]
        if overall.get('sumTimeEffPrint'):
            summary.append('有效 ' + str(overall['sumTimeEffPrint']))
        color = occupation_color(entry.get('occ'))
        self.player_selector.lineEdit().setStyleSheet('color:' + color.name() if color else '')
        self.personal_summary.setText(self._redact('  ·  '.join(str(s) for s in summary if s), self.personal_mask))

        skills = _mapping(self.result.get('skill'))
        general, healing = _mapping(skills.get('general')), _mapping(skills.get('healer'))
        healer = str(entry.get('occ', '')).rstrip('w').endswith('h')
        roster_row = next((r for r in self.roster if r.get('name') == name), {'name': name})
        rdps = self._team_rdps(roster_row)
        figures = (('rHPS', healing.get('rhps')), ('HPS', healing.get('hps')),
                   ('aHPS', healing.get('ahps')), ('关键 HPS', healing.get('chps')), ('rDPS', rdps)) if healer else (
                   ('rDPS', rdps), ('nDPS', general.get('ndps')),
                   ('主目标 rDPS', general.get('mrdps')), ('主目标 nDPS', general.get('mndps')))
        if 'efficiency' in general:
            label = '仅GCD效率' if 'efficiencyNonGcd' in general else '战斗效率'
            figures += ((label, _format('efficiency', general['efficiency'])),)
        if 'efficiencyNonGcd' in general:
            figures += (('战斗效率', _format('efficiencyNonGcd', general['efficiencyNonGcd'])),)
        figures += (('rDPS 百分位', None),)
        band = QFrame()
        band.setStyleSheet('QFrame {background:#edf3f2; border:0;}')
        metrics = QGridLayout(band)
        metrics.setContentsMargins(9, 4, 9, 5)
        metrics.setVerticalSpacing(0)
        for col, (label, value) in enumerate(figures):
            caption = _label(label)
            caption.setStyleSheet('color:#476562; font-size:11px')
            number = _label(f'{int(value):,}' if isinstance(value, (int, float)) and math.isfinite(value) else _text(value))
            number.setStyleSheet('color:#183e37; font-weight:600')
            if label == 'rDPS':
                self.personal_rdps = number
            if label == 'rDPS 百分位':
                self.personal_rank = number
                self._update_personal_rank()
            metrics.addWidget(caption, 0, col)
            metrics.addWidget(number, 1, col)
            metrics.setColumnStretch(col, 1)
        body.addWidget(band)

        equip = _mapping(self.result.get('equip'))
        equip_line = []
        score = _equipment_score(equip)
        if score != '未读取':
            equip_line.append('装分 ' + score if score.isdigit() else score)
        if equip.get('sketch'):
            equip_line.append(str(equip['sketch']))
        for key, caption in (('critPercent', '会心'), ('critpowPercent', '会效'),
                             ('hastePercent', '加速'), ('overcomePercent', '破防')):
            if key in equip:
                equip_line.append(caption + ' ' + _text(equip[key]))
        if name in self.equipment_issues:
            issue, estimated = self.equipment_issues[name]
            if not issue.get('hasEquipment') and score == '未读取':
                reason = '本次未记录该玩家装备'
            elif issue.get('reason') == 'unparseable':
                reason = '该玩家装备条目解析异常'
            elif issue.get('missingSlots'):
                reason = f'该玩家缺 {len(issue["missingSlots"])} 个装备部位'
            else:
                reason = '该玩家缺少可用装备属性'
            if estimated:
                reason += '，属性采用估算'
            equip_line.insert(0, reason)
        kit = QHBoxLayout()
        self.equipment_summary = _label(self._redact('   ·   '.join(equip_line) or '暂无装备面板', self.personal_mask))
        self.equipment_summary.setToolTip(self.equipment_source_notes.get(name, ''))
        kit.addWidget(self.equipment_summary, 1)
        details = QPushButton('装备详情')
        details.clicked.connect(lambda: self._open_detail('装备与奇穴', self._equipment))
        kit.addWidget(details)
        body.addLayout(kit)
        body.addWidget(_label('奇穴   ' + format_qixue(self.result.get('qixue'))))

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        left, skills_layout = _padded_page()
        right, support_layout = _padded_page()
        for content in (skills_layout, support_layout):
            content.setContentsMargins(0, 0, 0, 0)
            content.setSpacing(2)
        heading = QHBoxLayout()
        heading.addWidget(_label('技能表现'), 1)
        detail = QPushButton('全部指标')
        detail.clicked.connect(lambda: self._open_detail('技能指标', self._skills))
        heading.addWidget(detail)
        skills_layout.addLayout(heading)
        self.skill_table = self._compact_skills(skills, healer)
        skills_layout.addWidget(self.skill_table, 1)
        split.addWidget(left)
        self._support(support_layout)
        split.addWidget(right)
        split.setSizes([600, 365])
        split.setMinimumHeight(132)
        body.addWidget(split, 3)
        self._player_timeline(body)

    def _update_personal_rank(self):
        percent, text, tip = self._rdps_rank(self.current_player)
        self.personal_rank.setText(text)
        self.personal_rank.setToolTip(tip)
        color = _rank_color(percent).name() if percent is not None else '#526866'
        self.personal_rank.setStyleSheet(f'color:{color}; font-weight:600')

    def _open_detail(self, title, factory):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(740, 486)
        factory(QVBoxLayout(dialog))
        dialog.exec()

    def _tracker_player(self, metric):
        players = _get(self.tracker, metric, {}).get('player', {})
        return next((p for p in players.values() if p.get('name') == self.current_player), {})

    def _compact_skills(self, skills, healer):
        groups = [(key, _mapping(value)) for key, value in skills.items()
                  if key not in ('general', 'healer') and isinstance(value, Mapping) and value]
        if groups:
            selected = [(k, skills[k]) for k in SKILL_ICONS if k in skills]
            cards = []
            for key, fields in selected or groups:
                name = SKILLS.get(key, key)
                title = name + (f' ×{fields["num"]}' if 'num' in fields else '')
                metrics = [(caption, self._render(field, fields[field], self.personal_mask))
                           for field, caption in (('HPS', 'HPS'), ('dps', 'DPS'), ('cover', '覆盖'),
                               ('effRate', '有效'), ('delay', '延迟ms'), ('numPerSec', '每秒次数'))
                           if field in fields]
                if not metrics:
                    metrics = [(LABELS.get(k, k), self._render(k, v, self.personal_mask)) for k, v in fields.items()
                               if k not in ('num', 'score', 'delaySamples')]
                lines = [title] + [f'{caption} {value}' for caption, value in metrics[:2]]
                tooltip = '\n'.join([name] + [f'{LABELS.get(k,k)}  {self._render(k,v,self.personal_mask)}'
                                              for k,v in fields.items() if k != 'score'])
                icon = QIcon(get_icon_path(SKILL_ICONS[key])) if key in SKILL_ICONS else QIcon()
                cards.append(('\n'.join(lines), icon, tooltip))
            return _SkillCards(cards)
        data = self._tracker_player('hps' if healer else 'ndps')
        skills = sorted(_mapping(data.get('namedSkill')).items(), key=lambda row: row[1].get('sum', 0), reverse=True)
        table = _table()
        _fill(table, ['技能', '次数', '治疗量' if healer else '伤害量', '占比'],
              ([self._redact(key, self.personal_mask), row.get('num'), row.get('sum'),
                _format('percent', row.get('percent'))] for key, row in skills))
        return table

    def refresh_links(self):
        if hasattr(self, 'web_button'):
            has_link = self.personal_url() is not None
            self.web_button.setVisible(has_link)
            self.copy_link.setVisible(has_link)

    def personal_url(self):
        """Use the address already obtained by the desktop worker; opening a result never needs network I/O."""
        if not self.current_player:
            return None
        short_id = _get(self.result.get('overall', {}), 'shortID')
        code = self.occ_results[self.current_player].get('occ')
        route = OCC_PINYIN_DICT.get(str(code))
        if not route or route == 'unknown' or not re.fullmatch(r'[1-9][0-9]{0,17}', str(short_id)):
            return None
        widget = self
        base = None
        while widget and not base:
            base = getattr(widget, 'logs_url', None)
            widget = widget.parentWidget()
        if base:
            url = QUrl(str(base))
        else:
            data = FALLBACK_ADDRESS['logs']
            url = QUrl()
            url.setScheme(data['scheme'])
            url.setHost(data['host'])
            url.setPort(data['port'])
        url.setPath(f'/{route}/{short_id}')
        return url

    def _copy_personal_link(self):
        url = self.personal_url()
        if url:
            QApplication.clipboard().setText(url.toString())

    def _open_personal_web(self):
        url = self.personal_url()
        if url:
            QDesktopServices.openUrl(url)

    def _skills(self, body):
        table = _table()
        rows = []
        skills = _mapping(self.result.get('skill'))
        metric_order = ('rhps', 'hps', 'ahps', 'ohps', 'chps', 'rdps', 'ndps', 'mrdps', 'mndps',
                        'num', 'numPerSec', 'delay', 'HPS', 'cover', 'effRate', 'efficiency', 'efficiencyNonGcd')
        order = {key: i for i, key in enumerate(metric_order)}
        for group in sorted(skills, key=lambda k: (k not in ('general', 'healer'), k != 'general')):
            fields = _mapping(skills[group])
            for key in sorted(fields, key=lambda k: order.get(k, len(order))):
                if key in ('score', 'exp', 'experience'):
                    continue
                value = fields[key]
                rank = _mapping(_mapping(self.rank.get(group)).get(key))
                percentile = rank.get('percent')
                eligible = self.personal_quality['rankEligible'].get(key, True)
                valid = eligible and is_valid_rank(percentile) and (rank.get('num') or 0) > 0
                label = LABELS.get(key, key)
                if group == 'general' and key == 'efficiency' and 'efficiencyNonGcd' in fields:
                    label = '仅GCD效率'
                if group == 'healer' and key in ('heal', 'healEff'):
                    label = '原始 HPS（旧字段）' if key == 'heal' else '有效 HPS（旧字段）'
                if group == 'general' and key == 'rdps':
                    roster_row = next((r for r in self.roster if r.get('name') == self.current_player), {'name': self.current_player})
                    value = self._team_rdps(roster_row)
                    percentile, _, _ = self._rdps_rank(self.current_player)
                    samples = self.display_ranks.get(self.current_player, {}).get('num') if percentile is not None else None
                else:
                    percentile = percentile if valid and percentile <= 100 else None
                    samples = rank.get('num') if percentile is not None else None
                rows.append([SKILLS.get(group, group), label, self._render(key, value, self.personal_mask), percentile, samples])
        # Keep all historical metrics accessible; individual skill filters avoid
        # scrolling through every specialization measure to find one cast.
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(_label('技能'))
        selector = QComboBox()
        selector.addItem('全部技能', None)
        for group in dict.fromkeys(row[0] for row in rows):
            selector.addItem(group, group)
        filter_bar.addWidget(selector)
        filter_bar.addStretch()
        body.addLayout(filter_bar)
        def populate():
            group = selector.currentData()
            filtered = [r for r in rows if group is None or r[0] == group]
            _fill(table, ['技能', '指标', '数值', '指标百分位', '样本数'],
                  ([*r[:3], f'{r[3]:.0f}%' if r[3] is not None else None, r[4]] for r in filtered),
                  ranks={(i, 3): r[3] for i, r in enumerate(filtered) if r[3] is not None})
        selector.currentIndexChanged.connect(populate)
        populate()
        body.addWidget(table)
        if not rows:
            body.addWidget(_label('此版本没有记录技能统计。'))

    def _equipment(self, body):
        equip = _mapping(self.result.get('equip'))
        if source := self.equipment_source_notes.get(self.current_player):
            body.addWidget(_label(source))
        if equip.get('available') in (0, False) or not equip:
            body.addWidget(_label('未记录可展示的装备面板。'))
        else:
            table = _table()
            shown = [(k,v) for k,v in equip.items() if k not in ('raw', 'available')]
            _fill(table, ['装备属性', '数值'],
                  (['装备评分' if k == 'score' else LABELS.get(k, k), self._render(k, value, self.personal_mask)]
                   for k, value in shown),
                  tips={(i, col): forge_tooltip(value) for i, (k, value) in enumerate(shown) if k == 'forge' for col in (0, 1)})
            body.addWidget(table)
        if isinstance(equip.get('raw'), str) and equip['raw']:
            button = QPushButton('复制配装数据')
            button.clicked.connect(lambda: QApplication.clipboard().setText(equip['raw']))
            body.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
        body.addWidget(_label('奇穴'))
        body.addWidget(_label(format_qixue(self.result.get('qixue'))))
        body.addStretch()

    def _support(self, body):
        sections = {}
        for key, title in [('healer', '团队治疗'), ('dps', '团队专项')]:
            rows = _mapping(self.result.get(key)).get('table')
            if rows:
                sections[title] = rows
        for key, title in [('boost', '增益贡献'), ('fraction', '伤害构成')]:
            data = self.result.get(key)
            if key == 'fraction':
                data = _get(data, 'table')
            if isinstance(data, Mapping) and data:
                sections[title] = [dict(_mapping(v), name=k) for k, v in data.items()]
        if not sections:
            for metric, field, title in [('rdps', 'namedSource', '增益贡献'), ('ndps', 'namedTarget', '伤害目标')]:
                records = _mapping(self._tracker_player(metric).get(field))
                if records:
                    sections[title] = [dict(_mapping(v), name=k) for k, v in sorted(records.items(),
                                       key=lambda row: row[1].get('sum', 0), reverse=True)]
        selector = QComboBox()
        selector.addItems(list(sections))
        self.support_table = _table()
        if not sections:
            body.addWidget(_label('团队专项'))
            body.addWidget(_label('本场没有专项记录。'))
            body.addStretch()
            return
        body.addWidget(selector)
        body.addWidget(self.support_table, 1)
        def populate():
            rows = [r for r in sections[selector.currentText()] if isinstance(r, Mapping)]
            visible = list(dict.fromkeys(k for row in rows for k in row if k not in
                           ('score', 'scoreRank', 'exp', 'experience', 'heal', 'healEff', 'occ')))
            first = [k for k in ('name', 'rhps', 'hps', 'damage', 'sum', 'num', 'percent') if k in visible]
            keys = first + [k for k in visible if k not in first]
            if selector.currentText() == '团队治疗':
                keys = [k for k in ('name','rhps','hps','ahps','ohps','chps') if k in visible]
            _fill(self.support_table, [LABELS.get(k, k) for k in keys],
                  ([self._render(k, r.get(k), self.personal_mask) for k in keys] for r in rows),
                  [self.occupations.get(r.get('name')) or r.get('occ') for r in rows] if 'name' in keys else None)
            healer = _mapping(self.result.get('healer'))
            selector.setToolTip(str(healer.get('chpsDescription') or '') if selector.currentText() == '团队治疗' else '')
        selector.currentIndexChanged.connect(populate)
        populate()

    def _player_timeline(self, body):
        from window.QtTimeline import TimelineView
        if (not self.result.get('replay') and not _get(self.actor, 'personalTimelines', {}).get(self.current_player)
                and not hasattr(self.actor, 'bld')):
            body.addWidget(_label('这份复盘没有可归属的个人技能记录。'))
            return
        self.personal_timeline = TimelineView.from_actor(self.actor, player=self.current_player,
                                                         parent=self.personal_dashboard, compact=True)
        self.personal_timeline.setMinimumHeight(190)
        body.addWidget(self.personal_timeline, 4)

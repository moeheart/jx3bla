"""Qt battle and personal replay views backed by completed analysis results."""
import re
from collections.abc import Mapping
from types import SimpleNamespace

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSpinBox, QSplitter, QTableView, QTabWidget, QVBoxLayout, QWidget,
)

from Constants import FALLBACK_ADDRESS, OCC_NAME_DICT, OCC_PINYIN_DICT
from tools.RecordQuality import get_record_quality, is_effect_warning_only, is_valid_rank
from tools.StaticJson import REVIEW_JSON
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
    'efficiency': '战斗效率', 'efficiencyNonGcd': '含非公共调息技能效率', 'cover': '覆盖率',
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
REVIEWS = {str(item['code']): item for item in REVIEW_JSON['content']}
POT_LEVELS = {0: '观察／轻微', 1: '严重', 2: '提示', 3: '补贴'}
COMMON_ROSTER = {'name', 'occ', 'rdps', 'ndps', 'hps', 'score', 'rdpsRank', 'scoreRank',
                 'rdpsRankNum', 'scoreRankNum', 'equip', 'stunTime', 'battle', 'rdpsStatus',
                 'attributeEstimated', 'equipmentEstimated'}


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
        return f'{value:.2f}'.rstrip('0').rstrip('.')
    return str(value)


def _format(key, value):
    if key == 'occ':
        return OCC_NAME_DICT.get(str(value), str(value))
    if isinstance(value, (list, tuple)):
        return '、'.join(_format('', item) for item in value) or '—'
    if isinstance(value, Mapping):
        return '；'.join(f'{LABELS.get(k, k)} {_format(k, v)}' for k, v in value.items()) or '—'
    if key in PERCENT and isinstance(value, (int, float)):
        return f'{value:.1%}'
    return _text(value)


def _clock(ms):
    sign = '−' if ms < 0 else ''
    secs, millis = divmod(round(abs(ms)), 1000)
    return f'{sign}{secs // 60}:{secs % 60:02}.{millis:03}'


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


class _Rows(QAbstractTableModel):
    """Show text on demand, even for long mechanic histories; selection follows source row order."""
    def __init__(self, headers, rows, parent):
        super().__init__(parent)
        self.headers = headers
        self.rows = rows

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            return _text(self.rows[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section] if orientation == Qt.Orientation.Horizontal else str(section + 1)
        return None


def _table():
    table = QTableView()
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.setWordWrap(False)
    table.setShowGrid(False)
    table.verticalHeader().setDefaultSectionSize(28)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    return table


def _fill(table, headers, rows):
    model = _Rows(headers, list(rows), table)
    old = table.model()
    old_selection = table.selectionModel()
    table.setModel(model)
    if old is not None:
        old.deleteLater()
    if old_selection is not None:
        old_selection.deleteLater()
    table.horizontalHeader().setResizeContentsPrecision(30)
    table.resizeColumnsToContents()


def _records(table, entries, render):
    """Display every recorded column, including ones added by historic boss modules."""
    if isinstance(entries, Mapping):
        entries = [{'name': k, 'value': v} for k, v in entries.items()]
    if not isinstance(entries, (list, tuple)):
        entries = [entries] if entries is not None else []
    rows = [entry if isinstance(entry, Mapping) else {'value': entry} for entry in entries]
    keys = list(dict.fromkeys(key for row in rows for key in row))
    if 'player' in keys and 'playerID' in keys:
        keys.remove('playerID')
    _fill(table, [LABELS.get(k, '数值' if k == 'value' else k) for k in keys] or ['内容'],
          ([render(k, row.get(k)) for k in keys] for row in rows))


def _template(text, review, array=False):
    markers = re.findall(r'`([^`]+)`', text)
    lists = [review[k] for k in markers if isinstance(review.get(k), (list, tuple))]
    count = min(map(len, lists), default=1) if array else 1
    result = []
    for i in range(count):
        def replace(match):
            value = review.get(match[1])
            if array and isinstance(value, (tuple, list)):
                value = value[i]
            if isinstance(value, float) and 0 <= value < 1 and 'Per' not in match[1]:
                return f'{value:.1%}'
            return _format('', value)
        result.append(re.sub(r'`([^`]+)`', replace, text))
    return '\n'.join(result)


def _review_details(item):
    code = str(item.get('code', ''))
    spec = REVIEWS.get(code, {})
    status = item.get('status')
    messages = [_template(spec[key], item, key == 'addArray') for key in ('desc', 'add', 'addArray')
                if key in spec and status in spec.get(key + 'Condition', ())]
    return spec.get('title', '评分项目 ' + code), '\n'.join(filter(None, messages))
class BattleView(QWidget):
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
            context.append('用时 ' + _clock(end - start).split('.')[0])
        subtitle = _label('  ·  '.join(filter(None, context)))
        subtitle.setObjectName('muted')
        title.setWordWrap(False)
        header.addSpacing(8)
        header.addWidget(subtitle, 1)
        layout.addLayout(header)
        if not self.quality['precise']:
            layout.addWidget(_label(self.status.get('warning') or self.status.get('reason')
                                    or '属性资料不完整，rDPS 与评分仅供参考。'))
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        for name, factory in [('团队', self._team), ('阶段与机制', self._mechanics),
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
        if index == 5:
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
        rows = []
        for row in self.roster:
            equip = _mapping(row.get('equip'))
            supported = self.quality['precise'] and row.get('rdpsStatus') not in ('incomplete', 'estimated')
            reference = (self.quality['estimated'] or row.get('attributeEstimated')
                         or row.get('rdpsStatus') == 'estimated' or self.effects_only)
            healer = str(row.get('occ', '')).rstrip('w').endswith('h')
            rank_key = 'scoreRank' if healer else 'rdpsRank'
            rank = row.get(rank_key)
            if supported:
                rank_display = f'{rank}%' if is_valid_rank(rank) and row.get(rank_key+'Num', 1) else '暂无样本'
            else:
                rank_display = '仅供参考' if reference else '待校准'
            rows.append([
                self._redact(row.get('name', '')) + (' *' if row.get('equipmentEstimated') else ''),
                _format('occ', row.get('occ')), row.get('rdps') if supported or reference else None,
                row.get('ndps'), rhps.get(row.get('name'), row.get('rhps')), row.get('hps'), row.get('score') if healer and (supported or reference) else None,
                rank_display, equip.get('score'), equip.get('sketch'), equip.get('forge'), row.get('stunTime'),
                *(self._render(k, row.get(k, _mapping(row.get('battle')).get(k))) for k in extra)])
        self.team_table = _table()
        _fill(self.team_table, ['玩家', '心法', 'rDPS', 'nDPS', 'rHPS', 'HPS', '治疗评分', '百分位', '装分', '装备', '强化', '被控（秒）',
                                *(LABELS.get(k, k) for k in extra)], rows)
        body.addWidget(self.team_table)
        open_button = QPushButton('查看选中玩家的复盘')
        open_button.setEnabled(False)
        bar = QHBoxLayout()
        bar.addStretch()
        bar.addWidget(open_button)
        body.addLayout(bar)
        def selected():
            i = self.team_table.currentIndex().row()
            return self.roster[i].get('name') if i >= 0 else None
        self.team_table.selectionModel().currentRowChanged.connect(
            lambda *_: open_button.setEnabled(selected() in self.occ_results))
        open_button.clicked.connect(lambda: self.open_player(selected()))
        self.team_table.clicked.connect(
            lambda index: self.open_player(self.roster[index.row()].get('name')) if index.column() == 0 else None)
        self.team_table.doubleClicked.connect(lambda index: self.open_player(self.roster[index.row()].get('name')))
        if rows:
            self.team_table.selectRow(0)

    def _mechanics(self, body):
        for field in ('phaseSummary', 'mechanicNote', 'phaseEvidence', 'limitations'):
            if self.detail.get(field):
                body.addWidget(_label(self._redact(str(self.detail[field]))))
        omitted = {'boss', 'map', 'win', 'heroic', 'attributeStatus', 'rdpsStatus', 'phaseSummary',
                   'mechanicNote', 'phaseEvidence', 'limitations', 'analysisRevision'}
        sections = {k: v for k, v in self.detail.items() if k not in omitted and isinstance(v, (list, dict)) and v}
        facts = {k: v for k, v in self.detail.items() if k not in omitted and not isinstance(v, (list, dict))}
        if facts:
            sections['战斗信息'] = facts
        self.mechanic_selector = QComboBox()
        self.mechanic_table = _table()
        for key in sections:
            self.mechanic_selector.addItem(LABELS.get(key, key), key)
        body.addWidget(self.mechanic_selector)
        body.addWidget(self.mechanic_table)
        start = _get(self.actor, 'startTime')
        def render(key, value):
            if key in ('time', 'start', 'end', 'fieldEnd', 'boundaryEnd', 'signalEnd') and isinstance(start, (int, float)) and isinstance(value, (int, float)):
                return _clock(value - start)
            return self._render(key, value)
        def populate():
            _records(self.mechanic_table, sections.get(self.mechanic_selector.currentData(), []), render)
        self.mechanic_selector.currentIndexChanged.connect(populate)
        populate()
        if not sections:
            body.addWidget(_label('这份记录没有阶段或机制明细。'))

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
        _fill(self.pot_table, ['玩家', '心法', '性质', '记录', '分数'], rows)
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
        if hasattr(self, 'pot_table'):
            self._refresh_pots(len(self.pots)-1)
        return True

    def _manual_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('添加战斗记录')
        form = QFormLayout(dialog)
        player = QComboBox()
        for name in self.names:
            player.addItem(self._redact(name), name)
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
        body.addWidget(self.combat_selector)
        self.combat_table = _table()
        right = QTabWidget()
        self.combat_skill = _table()
        self.combat_targets = _table()
        right.addTab(self.combat_skill, '技能明细')
        right.addTab(self.combat_targets, '目标／增益来源')
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(self.combat_table)
        split.addWidget(right)
        body.addWidget(split)
        def change():
            key = self.combat_selector.currentData()
            data = _get(self.tracker, key, {}) or {}
            players = sorted(_mapping(data.get('player')).values(),
                             key=lambda r: r.get('sumPerSec', r.get('hps', r.get('dps', 0))) or 0, reverse=True)
            blocked = key in ('rdps', 'mrdps') and not self.quality['precise'] and not (
                self.quality['estimated'] or self.effects_only)
            if blocked:
                players = []
            _fill(self.combat_table, ['玩家', '心法', METRICS[key], '总量', '有效时间'],
                  ([self._redact(p.get('name')), _format('occ', p.get('occ')),
                    p.get('sumPerSec', p.get('hps', p.get('dps'))), p.get('sum'),
                    _clock(p['adjustedTime']) if isinstance(p.get('adjustedTime'), (int, float)) else None] for p in players))
            def select():
                i = self.combat_table.currentIndex().row()
                data = players[i] if i >= 0 else {}
                for table, field in [(self.combat_skill, 'namedSkill'),
                                     (self.combat_targets, 'namedSource' if key in ('rdps', 'mrdps') else 'namedTarget')]:
                    items = sorted(_mapping(data.get(field)).items(), key=lambda item: item[1].get('sum', 0), reverse=True)
                    _fill(table, ['增益来源' if field == 'namedSource' else ('技能' if field == 'namedSkill' else '目标'),
                                  '次数', '总量', '占比', '覆盖率'],
                          ([self._redact(name), v.get('num'), v.get('sum'), _format('percent', v.get('percent')),
                            _format('cover', v['cover']) if v.get('cover', -1) >= 0 else None] for name, v in items))
            self.combat_table.selectionModel().currentRowChanged.connect(select)
            if players:
                self.combat_table.selectRow(0)
            select()
        self.combat_selector.currentIndexChanged.connect(change)
        change()

    def _timeline(self, body):
        from window.QtTimeline import TimelineView
        body.addWidget(TimelineView.from_actor(self.actor, parent=self))
    def open_player(self, name):
        if name not in self.occ_results:
            return False
        self.tabs.setCurrentIndex(5)
        index = self.player_selector.findData(name)
        if index != self.player_selector.currentIndex():
            self.player_selector.setCurrentIndex(index)
        return True

    def _personal(self, body):
        self.player_selector = QComboBox()
        for name, entry in self.occ_results.items():
            personal_mask = _get(_get(entry, 'result', {}), 'overall', {}).get('mask') in (1, True, '1')
            self.player_selector.addItem(self._redact(name, self.mask or personal_mask) + ' · ' +
                                         _format('occ', entry.get('occ')), name)
        body.addWidget(self.player_selector)
        actions = QHBoxLayout()
        self.personal_summary = _label()
        actions.addWidget(self.personal_summary, 1)
        self.web_button = QPushButton('查看网页')
        self.web_button.clicked.connect(self._open_personal_web)
        actions.addWidget(self.web_button)
        self.copy_link = QPushButton('复制链接')
        self.copy_link.clicked.connect(self._copy_personal_link)
        actions.addWidget(self.copy_link)
        body.addLayout(actions)
        self.personal_tabs = QTabWidget()
        body.addWidget(self.personal_tabs)
        self._player_pages = {}
        self.personal_tabs.currentChanged.connect(self._show_player_tab)
        self.player_selector.currentIndexChanged.connect(self._change_player)
        self._change_player()

    def _change_player(self):
        name = self.player_selector.currentData()
        self.current_player = name
        previous_tab = max(self.personal_tabs.currentIndex(), 0)
        self.personal_tabs.blockSignals(True)
        while self.personal_tabs.count():
            page = self.personal_tabs.widget(0)
            self.personal_tabs.removeTab(0)
            page.deleteLater()
        self._player_pages = {}
        self.personal_tabs.blockSignals(False)
        if not name:
            self.web_button.hide()
            self.copy_link.hide()
            self.personal_summary.setText('这场战斗没有生成个人复盘。')
            return
        entry = self.occ_results[name]
        self.result = _mapping(entry.get('result', entry))
        self.refresh_links()
        self.rank = _mapping(entry.get('rank') or self.result.get('rank'))
        overall = _mapping(self.result.get('overall'))
        self.personal_mask = self.mask or overall.get('mask') in (1, True, '1')
        self.personal_quality = get_record_quality({'overall': overall, 'quality': self.quality})
        summary = [overall.get('battleTimePrint'), overall.get('edition'), overall.get('dataType')]
        if overall.get('sumTimeEffPrint'):
            summary.append('有效战斗时间 ' + str(overall['sumTimeEffPrint']))
        if not self.personal_quality['precise']:
            summary.append('rDPS 与评分仅供参考')
        self.personal_summary.setText(self._redact('  ·  '.join(str(s) for s in summary if s), self.personal_mask))
        self.personal_tabs.blockSignals(True)
        for tab_name, factory in [('技能统计', self._skills), ('装备与奇穴', self._equipment),
                                  ('团队专项', self._support), ('评分建议', self._reviews),
                                  ('个人时间轴', self._player_timeline)]:
            page, layout = _padded_page()
            self._player_pages[self.personal_tabs.addTab(page, tab_name)] = (layout, factory)
        self.personal_tabs.setCurrentIndex(previous_tab)
        self.personal_tabs.blockSignals(False)
        self._show_player_tab(previous_tab)

    def _show_player_tab(self, index):
        page = self._player_pages.pop(index, None)
        if page:
            body, factory = page
            factory(body)

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
        metric_order = ('rhps', 'hps', 'ahps', 'ohps', 'chps', 'rdps', 'ndps', 'mrdps', 'mndps', 'score',
                        'num', 'numPerSec', 'delay', 'HPS', 'cover', 'effRate', 'efficiency')
        order = {key: i for i, key in enumerate(metric_order)}
        for group in sorted(skills, key=lambda k: (k not in ('general', 'healer'), k != 'general')):
            fields = _mapping(skills[group])
            for key in sorted(fields, key=lambda k: order.get(k, len(order))):
                value = fields[key]
                rank = _mapping(_mapping(self.rank.get(group)).get(key))
                percentile = rank.get('percent')
                eligible = self.personal_quality['rankEligible'].get(key, True)
                valid = eligible and is_valid_rank(percentile) and (rank.get('num') or 0) > 0
                label = LABELS.get(key, key)
                if group == 'healer' and key in ('heal', 'healEff'):
                    label = '原始 HPS（旧字段）' if key == 'heal' else '有效 HPS（旧字段）'
                rows.append([SKILLS.get(group, group), label, self._render(key, value, self.personal_mask),
                             f'{percentile}%' if valid else None, rank.get('num') if valid else None])
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
            _fill(table, ['技能', '指标', '数值', '百分位', '样本数'],
                  (row for row in rows if group is None or row[0] == group))
        selector.currentIndexChanged.connect(populate)
        populate()
        body.addWidget(table)
        if not rows:
            body.addWidget(_label('此版本没有记录技能统计。'))

    def _equipment(self, body):
        equip = _mapping(self.result.get('equip'))
        if equip.get('available') in (0, False) or not equip:
            body.addWidget(_label('未记录可展示的装备面板。'))
        else:
            table = _table()
            _fill(table, ['装备属性', '数值'],
                  (['装备评分' if k == 'score' else LABELS.get(k, k), self._render(k, value, self.personal_mask)]
                   for k, value in equip.items() if k not in ('raw', 'available')))
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
        for section, title in [('healer', '团队治疗'), ('dps', '团队心法专项')]:
            data = _mapping(self.result.get(section)).get('table')
            if data:
                sections[title] = data
        for key, title in [('boost', '增益来源'), ('fraction', '伤害构成')]:
            data = self.result.get(key)
            if key == 'fraction':
                data = _get(data, 'table')
            if isinstance(data, Mapping) and data:
                sections[title] = [dict(_mapping(v), name=k) for k, v in data.items()]
        if not sections:
            body.addWidget(_label('此心法没有额外的团队专项数据。'))
            body.addStretch()
            return
        selector = QComboBox()
        selector.addItems(list(sections))
        table = _table()
        note = _label()
        body.addWidget(selector)
        body.addWidget(note)
        body.addWidget(table)
        def populate():
            healer = _mapping(self.result.get('healer'))
            desc = healer.get('chpsDescription') if selector.currentText() == '团队治疗' else None
            duration = healer.get('chpsDuration')
            if desc and isinstance(duration, (int, float)):
                desc = f'{desc}（{_clock(duration)}）'
            note.setText(self._redact(str(desc), self.personal_mask) if desc else '')
            note.setVisible(bool(desc))
            _records(table, sections[selector.currentText()],
                     lambda key, value: self._render(key, value, self.personal_mask))
        selector.currentIndexChanged.connect(populate)
        populate()

    def _reviews(self, body):
        review = _mapping(self.result.get('review'))
        if review.get('available') in (0, False) or not review:
            body.addWidget(_label('此心法没有评分建议。'))
            body.addStretch()
            return
        table = _table()
        detail = QPlainTextEdit()
        detail.setReadOnly(True)
        descriptions, rows = [], []
        for item in review.get('content', []):
            title, advice = _review_details(item)
            severity = {0: '良好', 1: '轻微', 2: '中等', 3: '严重'}.get(item.get('status'), '—')
            rows.append([title, severity, _format('percent', item.get('rate'))])
            descriptions.append(self._redact(advice, self.personal_mask))
        intro = _mapping(review.get('intro'))
        if intro:
            advice = REVIEWS.get(str(intro.get('code')), {}).get('desc')
            if advice:
                body.addWidget(_label(self._redact(_template(advice, intro), self.personal_mask)))
        if review.get('score') is not None:
            text = ('综合评分' if self.personal_quality['precise'] else '参考评分') + '  ' + _text(review['score'])
            ranking = _mapping(_mapping(self.rank.get('review')).get('score'))
            if self.personal_quality['precise'] and is_valid_rank(ranking.get('percent')) and ranking.get('num', 0) > 0:
                text += f"  ·  百分位 {ranking['percent']}%（{ranking['num']} 份样本）"
            body.addWidget(_label(text))
        _fill(table, ['项目', '程度', '达成率'], rows)
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(table)
        split.addWidget(detail)
        split.setStretchFactor(0, 2)
        body.addWidget(split)
        def select():
            i = table.currentIndex().row()
            detail.setPlainText(descriptions[i] if i >= 0 else '')
        table.selectionModel().currentRowChanged.connect(select)
        if rows:
            table.selectRow(0)

    def _player_timeline(self, body):
        from window.QtTimeline import TimelineView
        if (not self.result.get('replay') and not _get(self.actor, 'personalTimelines', {}).get(self.current_player)
                and not hasattr(self.actor, 'bld')):
            body.addWidget(_label('这份个人复盘没有记录个人技能时间轴。'))
            body.addStretch()
            return
        body.addWidget(TimelineView.from_actor(self.actor, player=self.current_player, parent=self))

"""Presentation rules for evidenced Luoyang mechanisms, independent of statistics."""

# Native skill display rows mostly have icon 0. Existing matching Buff icons
# are used where packaged; the remaining symbols are bundled visual substitutes:
# 2031 slash, 2033 thrust, 4564 sweep, 4516 shockwave, 14157 bomb, 1485 ascent.
STYLE_GROUPS = (
    ('2031', '#64748b', ('常规技能', '常规阶段', '双子交战', '巨剑击破后', '开战')),
    ('12452', '#b45309', ('潜渊之刺',)),
    ('12453', '#7e22ce', ('倒悬之墨', '逐焰追击')),
    ('12449', '#0369a1', ('玄溟奔涌', '浊浪登天', '死水微澜')),
    ('3399', '#6d28d9', ('黯穹崩天', '染魂', '邪魂散', '阴山旧血')),
    ('12452', '#c2410c', ('玄溟之火', '焚天炽焰', '圣火回应', '逐焰独战')),
    ('2031', '#b91c1c', ('断岳横斩', '裂剑·前式', '裂剑·回式', '裂峰斩', '裂峰斩·一式', '裂峰斩·二式', '凝渊刀', '黄泉斩')),
    ('16396', '#7e22ce', ('天陨一剑', '天陨一剑准备', '第二剑准备', '天陨巨剑', '苍天坠剑', '苍天坠剑·承剑', '苍天坠剑·气浪')),
    ('4516', '#a16207', ('雷霆震岳', '电扫千军', '千钧之压', '千钧锤落', '骨朵兵列阵', '军阵号令·砸碎')),
    ('2033', '#0369a1', ('鸣镝连珠', '三军围猎', '枪林突刺', '长枪兵列阵', '弓箭手放箭', '军阵号令·射穿', '军阵号令·捅穿')),
    ('2031', '#475569', ('全军准备', '狼牙军号令', '军阵号令·全军压上')),
    ('2123', '#7e22ce', ('锁链', '锁链横扫', '钉柱链狱', '钉柱炼狱准备', '链坠天崩')),
    ('12452', '#c2410c', ('链舞火环', '链舞火环准备')),
    ('14157', '#c2410c', ('逐猎爆弹', '散雷延爆', '爆裂轰退', '玄隼', '玄隼金刚', '召唤玄隼', '玄隼轰炸', '玄隼集中轰炸')),
    ('25109', '#b45309', ('伏焰', '伏焰金刚', '伏焰出击', '伏焰突破')),
    ('12453', '#b45309', ('炽虎', '炽虎金刚', '召唤炽虎', '铁颚扑咬')),
    ('4528', '#0f766e', ('爆裂残魂',)),
    ('4492', '#0f766e', ('聚邪凝渊', '聚邪阶段')),
    ('16396', '#0369a1', ('蓄能机枢受损', '玄天剑符', '重铸残刃', '利刃')),
    ('16371', '#b91c1c', ('煞将', '煞骸崩陨', '戾煞', '戾月崩斩', '本体红黑煞阶段')),
    ('4564', '#0f766e', ('刃轮',)),
    ('25109', '#b91c1c', ('杀机', '杀机结束')),
    ('16370', '#7e22ce', ('幽影斩', '戾芒天坠', '煞甲归身转场', '煞甲归身转场（喊话观测）')),
    ('2031', '#c2410c', ('连斩', '连斩·一式', '连斩·二式', '三阶段剑招')),
    ('4516', '#0369a1', ('啸天',)),
    ('16396', '#b91c1c', ('坠空斩',)),
)
STYLES = {name: (icon, color) for icon, color, names in STYLE_GROUPS for name in names}
FLAVOR_ONLY = frozenset(('开战', '机枢受损后宣言', '天命宣言', '帝煞威仪宣言', '圣恩已成'))
ALIASES = {'裂峰斩': '裂峰斩·一式', '连斩': '连斩·一式',
           '第二剑准备': '天陨一剑准备', '聚邪阶段': '聚邪凝渊',
           '苍天坠剑': '天陨巨剑',
           '煞甲归身转场': '煞甲归身转场（喊话观测）'}


def tag_source(replayer, source):
    replayer.bh.log['environment'][-1]['source'] = str(source)


def finalize_timeline(replayer):
    """Collapse alternative representations, preserving independent sources.

    Full dialogue remains in detail.shouts and phase records are unchanged.
    A shout can be late (潜渊 is ~6.8s after cast), hence its 8s fallback window.
    Casts of the same mechanism, even close together, are never merged here.
    """
    # Tail candidates must never suppress a valid in-bounds fallback.
    records = [record for record in replayer.bh.log['environment']
               if replayer.startTime <= record['start'] <= replayer.finalTime]
    result = []
    for record in records:
        label = record['skillname']
        if record['type'] == 'shout' and label in FLAVOR_ONLY:
            continue
        canonical = ALIASES.get(label, label)
        redundant = False
        for other in records:
            if other is record or ALIASES.get(other['skillname'], other['skillname']) != canonical:
                continue
            if record.get('source') and other.get('source') and record['source'] != other['source']:
                continue
            distance = abs(record['start'] - other['start'])
            if record['type'] == 'shout' and other['type'] != 'shout' and distance <= 8000:
                redundant = True
            elif (record['type'] == 'phase' and not record.get('duration', 0)
                  and other['type'] == 'cast' and distance <= 1000
                  and not (label == '链舞火环' and '英雄' in replayer.bld.info.map)):
                redundant = True
            elif (record['type'] == 'cast' and other['type'] == 'phase'
                  and other.get('duration', 0) > 0 and distance <= 1000):
                # A measured phase interval contains more information than
                # its near-simultaneous cast marker. Keep the interval intact.
                redundant = True
            elif record['type'] == 'skill' and other['type'] in ('cast', 'phase') and distance <= 1000:
                redundant = True
            elif (label == '链舞火环' and '英雄' in replayer.bld.info.map and record['type'] == 'cast'
                  and other['type'] == 'phase' and distance <= 3000):
                # Ring appearance is the wave boundary; the child starts
                # casting about2s later. Keep the cast only as missing-Scene fallback.
                redundant = True
        if redundant:
            continue
        if label in STYLES:
            record['iconid'], record['color'] = STYLES[label]
        result.append(record)
    replayer.bh.log['environment'] = result

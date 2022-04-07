# Created by moeheart at 10/17/2021
# 实现BOSS名称与地图名称的各种转化。
    
BOSS_RAW = {"铁黎": [1, 1, []], 
            "陈徽": [1, 2, []],
            "藤原武裔": [1, 3, []],
            "源思弦": [1, 4, ["咒飚狐", "咒凌狐", "咒狐"]],
            "驺吾": [1, 5, []],
            "方有崖": [1, 6, []],
            "周贽": [2, 1, ["狼牙精锐", "狼牙刀盾兵"]],
            "厌夜": [2, 2, []],
            "迟驻": [2, 3, []],
            "白某": [2, 4, ["少阴符灵", "少阳符灵"]],
            "安小逢": [2, 5, ["狼牙斧卫", "水鬼"]],
            "余晖": [3, 1, []],
            "宓桃": [3, 2, ["天欲宫弟子", "天欲宫男宠"]],
            "武雪散": [3, 3, []],
            "猿飞": [3, 4, []],
            "哑头陀": [3, 5, ["毗流驮迦", "毗留博叉", "充能核心", "提多罗吒", "毗沙门"]],
            "岳琳&岳琅": [3, 6, ["岳琳", "岳琅", "蜂群毛贼", "蜂群蟊贼", "蜂群凶贼", "蜂群胖墩"]],
            "胡汤&罗芬": [4, 1, ["胡汤", "罗芬"]],
            "赵八嫂": [4, 2, []],
            "海荼": [4, 3, ["天怒惊霆戟", "水鬼"]],
            "姜集苦": [4, 4, []],
            "宇文灭": [4, 5, []],
            "宫威": [4, 6, []],
            "宫傲": [4, 7, []],
            "修罗僧": [5, 7, []],
            "巨型尖吻凤": [6, 1, ["巨型尖吻鳳"]],
            "桑乔": [6, 2, ["桑喬"]],
            "悉达罗摩": [6, 3, ["蛊兽", "悉達羅摩"]],
            "尤珈罗摩": [6, 4, ["赐恩血瘤", "血蛊巢心", "賜恩血瘤"]],
            "月泉淮": [6, 5, []],
            "乌蒙贵": [6, 6, ["黑条巨蛾", "黑條巨蛾", "烏蒙貴"]],
            "勒齐那": [7, 1, ["勒齊那"]],
            "阿阁诺": [7, 2, ["阿閣諾"]],
            "周通忌": [7, 3, []],
            "周贽": [7, 4, ["周贄", "狼牙精锐", "狼牙精銳", "李秦授"]],
            "常宿": [7, 5, []],
            }
            
MAP_NAME_LIST = ["未知地图", "敖龙岛", "范阳夜变", "达摩洞", "白帝江关", "修罗挑战", "雷域大泽", "河阳之战"]
            
BOSS_DICT = {}
MAP_DICT = {}
NICK_TO_BOSS = {}

for line in BOSS_RAW:
    MAP_DICT[line] = BOSS_RAW[line][0]
    BOSS_DICT[line] = BOSS_RAW[line][1]
    NICK_TO_BOSS[line] = line
    for otherName in BOSS_RAW[line][2]:
        MAP_DICT[otherName] = BOSS_RAW[line][0]
        BOSS_DICT[otherName] = BOSS_RAW[line][1]
        NICK_TO_BOSS[otherName] = line
        
def getBossDictFromMap(map):
    if map == "敖龙岛":
        bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
        bossDictR = ["", "铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
    elif map == "范阳夜变":
        bossDict = {"周贽": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5}
        bossDictR = ["", "周贽", "厌夜", "迟驻", "白某", "安小逢"]
    elif map == "达摩洞":
        bossDict = {"余晖": 1, "宓桃": 2, "武雪散": 3, "猿飞": 4, "哑头陀": 5, "岳琳&岳琅": 6}
        bossDictR = ["", "余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅"]
    elif map == "白帝江关":
        bossDict = {"胡汤&罗芬": 1, "赵八嫂": 2, "海荼": 3, "姜集苦": 4, "宇文灭": 5, "宫威": 6, "宫傲": 7}
        bossDictR = ["", "胡汤&罗芬", "赵八嫂", "海荼", "姜集苦", "宇文灭", "宫威", "宫傲"]
    elif map == "修罗挑战":
        bossDict = {"修罗僧": 1}
        bossDictR = ["", "修罗僧"]
    elif map == "雷域大泽":
        bossDict = {"巨型尖吻凤": 1, "桑乔": 2, "悉达罗摩": 3, "尤珈罗摩": 4, "月泉淮": 5, "乌蒙贵": 6}
        bossDictR = ["", "巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]
    else:
        bossDict = {}
        bossDictR = [""]
    return bossDict, bossDictR
    
def getNickToBoss(nick):
    if nick in NICK_TO_BOSS:
        return NICK_TO_BOSS[nick]
    else:
        return nick

MAP_DICT = {"428": "25人英雄敖龙岛",
            "427": "25人普通敖龙岛",
            "426": "10人普通敖龙岛",
            "454": "25人英雄范阳夜变",
            "453": "25人普通范阳夜变",
            "452": "10人普通范阳夜变",
            "484": "25人英雄达摩洞",
            "483": "25人普通达摩洞",
            "482": "10人普通达摩洞",
            "520": "25人英雄白帝江关",
            "519": "25人普通白帝江关",
            "518": "10人普通白帝江关",
            "561": "25人英雄雷域大泽",
            "560": "25人普通雷域大泽",
            "559": "10人普通雷域大泽",
            "575": "25人英雄河阳之战",
            "574": "25人普通河阳之战",
            "573": "10人普通河阳之战",
}

def getMapFromID(map):
    '''
    从地图ID获取地图名字符串。
    params:
    - map: 地图ID
    returns:
    - res: 地图对应的中文字符串.
    '''
    if map in MAP_DICT:
        return MAP_DICT[map]
    else:
        return "未知"








# Created by moeheart at 10/17/2021
# 实现BOSS名称与地图名称的各种转化。
    
BOSS_RAW = {"未知": [0, 1, []],
            "铁黎": [1, 1, []],
            "陈徽": [1, 2, []],
            "藤原武裔": [1, 3, []],
            "源思弦": [1, 4, ["咒飚狐", "咒凌狐", "咒狐"]],
            "驺吾": [1, 5, []],
            "方有崖": [1, 6, []],
            "周贽_范阳夜变": [2, 1, ["狼牙精锐", "狼牙刀盾兵"]],
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
            "张景超": [8, 1, ["張景超", "张法雷", "張法雷"]],
            "刘展": [8, 2, ["劉展", "枪卫首领", "槍衛首領", "斧卫首领", "斧衛首領"]],
            "苏凤楼": [8, 3, ["蘇鳳樓", "凌雪阁杀手", "淩雪閣殺手", "剧毒孢子", "劇毒孢子"]],
            "韩敬青": [8, 4, ["韓敬青"]],
            "藤原佑野": [8, 5, []],
            "李重茂": [8, 6, ["永王叛军长枪兵", "一刀流精锐武士", "永王叛军剑卫", "永王叛軍長槍兵", "一刀流精銳武士", "永王叛軍劍衛"]],
            }

MAP_NAME_LIST = ["未知地图",  # 0
                 "敖龙岛",  # 1
                 "范阳夜变",  # 2
                 "达摩洞",  # 3
                 "白帝江关",  # 4
                 "修罗挑战",  # 5
                 "雷域大泽",  # 6
                 "河阳之战",  # 7
                 "西津渡"  # 8
                 ]

# 地图ID, logs得分系数, 别名
MAP_RAW = {"未知地图": [0, 0, []],
           "敖龙岛": [426, 0, []],
           "范阳夜变": [452, 0, []],
           "达摩洞": [482, 0, []],
           "白帝江关": [518, 0, []],
           "修罗挑战": [0, 0, []],
           "雷域大泽": [559, 0, ["雷域大澤"]],
           "河阳之战": [573, 1, ["河陽之戰"]],
           "西津渡": [586, 1, []]
           }

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
        
# def getBossDictFromMap(map):
#     if map == "敖龙岛":
#         bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
#         bossDictR = ["", "铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
#     elif map == "范阳夜变":
#         bossDict = {"周贽": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5}
#         bossDictR = ["", "周贽", "厌夜", "迟驻", "白某", "安小逢"]
#     elif map == "达摩洞":
#         bossDict = {"余晖": 1, "宓桃": 2, "武雪散": 3, "猿飞": 4, "哑头陀": 5, "岳琳&岳琅": 6}
#         bossDictR = ["", "余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅"]
#     elif map == "白帝江关":
#         bossDict = {"胡汤&罗芬": 1, "赵八嫂": 2, "海荼": 3, "姜集苦": 4, "宇文灭": 5, "宫威": 6, "宫傲": 7}
#         bossDictR = ["", "胡汤&罗芬", "赵八嫂", "海荼", "姜集苦", "宇文灭", "宫威", "宫傲"]
#     elif map == "修罗挑战":
#         bossDict = {"修罗僧": 1}
#         bossDictR = ["", "修罗僧"]
#     elif map == "雷域大泽":
#         bossDict = {"巨型尖吻凤": 1, "桑乔": 2, "悉达罗摩": 3, "尤珈罗摩": 4, "月泉淮": 5, "乌蒙贵": 6}
#         bossDictR = ["", "巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]
#     else:
#         bossDict = {}
#         bossDictR = [""]
#     return bossDict, bossDictR
    
def getNickToBoss(nick):
    if nick in NICK_TO_BOSS:
        return NICK_TO_BOSS[nick]
    else:
        return nick

MAP_DICT = {}
MAP_DICT_REVERSE = {}
MAP_TRADITIONAL = {}
MAP_DICT_RECORD_LOGS = {}

for map in MAP_RAW:
    if MAP_RAW[map][0] != 0:
        mapid = MAP_RAW[map][0]
        MAP_DICT[str(mapid)] = "10人普通%s" % map
        MAP_DICT[str(mapid + 1)] = "25人普通%s" % map
        MAP_DICT[str(mapid + 2)] = "25人英雄%s" % map
        if MAP_RAW[map][1]:
            MAP_DICT_RECORD_LOGS[str(mapid)] = int(MAP_RAW[map][1])
            MAP_DICT_RECORD_LOGS[str(mapid + 1)] = int(MAP_RAW[map][1] * 2)
            MAP_DICT_RECORD_LOGS[str(mapid + 2)] = int(MAP_RAW[map][1] * 4)
        MAP_DICT_REVERSE[map] = str(mapid)
        MAP_DICT_REVERSE["10人普通%s" % map] = str(mapid)
        MAP_DICT_REVERSE["25人普通%s" % map] = str(mapid+1)
        MAP_DICT_REVERSE["25人英雄%s" % map] = str(mapid+2)
        for map_othername in MAP_RAW[map][2]:
            MAP_TRADITIONAL[map_othername] = map
            MAP_TRADITIONAL["10人普通%s" % map_othername] = "10人普通%s" % map
            MAP_TRADITIONAL["25人普通%s" % map_othername] = "25人普通%s" % map
            MAP_TRADITIONAL["25人英雄%s" % map_othername] = "25人英雄%s" % map

# MAP_DICT = {"428": "25人英雄敖龙岛",
#             "427": "25人普通敖龙岛",
#             "426": "10人普通敖龙岛",
#             "454": "25人英雄范阳夜变",
#             "453": "25人普通范阳夜变",
#             "452": "10人普通范阳夜变",
#             "484": "25人英雄达摩洞",
#             "483": "25人普通达摩洞",
#             "482": "10人普通达摩洞",
#             "520": "25人英雄白帝江关",
#             "519": "25人普通白帝江关",
#             "518": "10人普通白帝江关",
#             "561": "25人英雄雷域大泽",
#             "560": "25人普通雷域大泽",
#             "559": "10人普通雷域大泽",
#             "575": "25人英雄河阳之战",
#             "574": "25人普通河阳之战",
#             "573": "10人普通河阳之战",
# }
#
# MAP_DICT_REVERSE = {}
# for key in MAP_DICT:
#     MAP_DICT_REVERSE[MAP_DICT[key]] = key
#     MAP_DICT_REVERSE["雷域大泽"] = "559"
#     MAP_DICT_REVERSE["河阳之战"] = "573"

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

def getIDFromMap(map):
    '''
    根据地图字符串获取地图ID。
    params:
    - map: 地图对应的中文字符串
    returns:
    - res: 地图ID.
    '''

    if map in MAP_DICT_REVERSE:
        return MAP_DICT_REVERSE[map]
    else:
        return "未知"







# Created by moeheart at 10/24/2020
# 由BOSS名称的各种变化形式到BOSS的对应方法，以及其它相关功能。
    
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
            "哑头陀": [3, 5, ["毗流驮迦", "毗留博叉", "充能核心"]],
            "岳琳&岳琅": [3, 6, ["岳琳", "岳琅", "蜂群毛贼", "蜂群蟊贼", "蜂群凶贼", "蜂群胖墩"]]}
            
MAP_NAME_LIST = ["未知地图", "敖龙岛", "范阳夜变", "达摩洞"]
            
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
    else:
        bossDict = {}
        bossDictR = [""]
    return bossDict, bossDictR
    
def getNickToBoss(nick):
    if nick in NICK_TO_BOSS:
        return NICK_TO_BOSS[nick]
    else:
        return nick




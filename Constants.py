# Created by moeheart at 10/11/2020
# 全局用到的部分常量。

EDITION = "8.3.9"
ANNOUNCEMENT = "8.3版本即将发布，支持120等级的副本与心法复盘，以及更全面的logs排名，请及时更新！"
IP = "120.48.95.56"
# IP = "139.199.102.41"
CHAPTER = 120

LVLTABLE = [0, 30, 100, 200, 300, 500, 700, 900, 1200, 1500, 1800, 2400, 3000, 999999]
LVLNAME = ["二级警员", "一级警员", "三级警司", "二级警司", "一级警司", "三级警督", "二级警督", "一级警督", "三级警监", "二级警监", "一级警监", "副总警监", "总警监", "最高等级"]

INTERRUPT_DICT = {
    "240": "抢珠式",
    "370": "八卦洞玄",
    "310": "剑飞惊天",
    "14975": "万剑归宗",  # 伤害技能
    "183": "厥阴指",
    "482": "崩",
    "547": "剑心通明",
    "2716": "剑破虚空",  # 仅主目标，2988是子目标，不附带打断
    "1577": "玉虹贯日",
    "1909": "平湖断月",  # ？
    "18584": "灵蛊",
    "2461": "蟾啸",  # 打断子技能，之前的蟾啸迷心
    "3092": "梅花针",
    "3961": "寒月耀",
    "5259": "棒打狗头",
    "13396": "盾飞",  # 打断子技能
    "14095": "清音长啸",
    #"16598": "雷走风切",
    "17364": "雷走风切",  # 非大刀雷走实际打断，推测
    "16632": "雷走风切",  # 大刀雷走实际打断
    "20065": "翔极碧落",
    "22640": "血覆黄泉",  # 打断子技能
    "25011": "神皆寂",
    "28377": "惊鸿掠水",  # 打断子技能
}

COLOR_DICT = {"0": (0, 0, 0),  # 未知
             "1": (210, 180, 0),  # 少林
             "2": (127, 31, 223),  # 万花
             "4": (56, 175, 255),  # 纯阳
             "5": (255, 127, 255),  # 七秀
             "3": (160, 0, 0),  # 天策
             "8": (220, 220, 0),  # 藏剑
             "9": (205, 133, 63),  # 丐帮
             "10": (253, 84, 0),  # 明教
             "6": (63, 31, 159),  # 五毒
             "7": (0, 133, 144),  # 唐门
             "21": (180, 60, 0),  # 苍云
             "22": (100, 250, 180),  # 长歌
             "23": (71, 73, 166),  # 霸刀
             "24": (195, 171, 227),  # 蓬莱
             "25": (161, 9, 34),  # 凌雪
             "211": (166, 83, 251),  # 衍天
             "212": (0, 172, 153),  # 药宗
             "213": (107, 183, 242),  # (64, 101, 169),  # 刀宗
             }

OCC_NAME_DICT = {"0": "未知",
                    "1": "少林",
                    "1d": "易筋",
                    "1t": "洗髓",
                    "2": "万花",
                    "2d": "花间",
                    "2h": "奶花",
                    "3": "天策",
                    "3d": "傲血",
                    "3t": "铁牢",
                    "4": "纯阳",
                    "4p": "剑纯",
                    "4m": "气纯",
                    "5": "七秀",
                    "5d": "冰心",
                    "5h": "奶秀",
                    "6": "五毒",
                    "6d": "毒经",
                    "6h": "奶毒",
                    "7": "唐门",
                    "7p": "惊羽",
                    "7m": "天罗",
                    "8": "藏剑",
                    "9": "丐帮",
                    "10": "明教",
                    "10d": "焚影",
                    "10t": "明尊",
                    "21": "苍云",
                    "21d": "分山",
                    "21t": "铁骨",
                    "22": "长歌",
                    "22d": "莫问",
                    "22h": "奶歌",
                    "23": "霸刀",
                    "24": "蓬莱",
                    "25": "凌雪",
                    "211": "衍天",
                    "212": "药宗",
                    "212d": "无方",
                    "212h": "灵素",
                    "213": "刀宗",
}

OCC_PINYIN_DICT = {"0": "unknown",
                    "1": "unknown",
                    "1d": "yijinjing",
                    "1t": "xisuijing",
                    "2": "unknown",
                    "2d": "huajianyou",
                    "2h": "lijingyidao",
                    "3": "unknown",
                    "3d": "aoxuezhanyi",
                    "3t": "tielaolv",
                    "4": "unknown",
                    "4p": "taixujianyi",
                    "4m": "zixiagong",
                    "5": "unknown",
                    "5d": "bingxinjue",
                    "5h": "yunchangxinjing",
                    "6": "unknown",
                    "6d": "dujing",
                    "6h": "butianjue",
                    "7": "unknown",
                    "7p": "jingyujue",
                    "7m": "tianluoguidao",
                    "8": "wenshuijue",
                    "9": "xiaochenjue",
                    "10": "unknown",
                    "10d": "fenyingshengjue",
                    "10t": "mingzunliuliti",
                    "21": "unknown",
                    "21d": "fenshanjin",
                    "21t": "tieguyi",
                    "22": "unknown",
                    "22d": "mowen",
                    "22h": "xiangzhi",
                    "23": "beiaojue",
                    "24": "linghaijue",
                    "25": "yinlongjue",
                    "211": "taixuanjing",
                    "212": "unknown",
                    "212d": "wufang",
                    "212h": "lingsu",
                    "213": "gufengjue",
}

CONTROL_DICT = {
    # 天策
    "431": "突",
    #### 青阳
    "481": "沧月",
    "432": "疾",
    "409": "断魂刺",
    "6231": "乘龙箭",
    "6232": "乘龙箭",
    "699": "破坚阵",
    "15163": "破重围",
    "24843": "力破万钧",
    "483": "崩",
    # 少林
    "236": "摩诃无量",
    "242": "捉影式",
    "262": "大狮子吼",
    "263": "大狮子吼",
    "264": "大狮子吼",
    "499": "千斤坠",
    # 明教
    "4035": "生死劫·日",
    "4476": "净世破魔击·月",
    "4910": "无明魂锁",
    "20380": "极乐引",
    "4968": "极乐引",
    ### 镇魔极道
    ### 知我罪我
    "24016": "朝圣言",
    # 唐门
    "3089": "雷震子",
    "3426": "迷神钉",
    ### 逐星箭
    "3116": "子母飞爪",
    "3357": "图穷匕见",  # 控怪主技能
    # 霸刀
    "17053": "踏宴扬旗",
    "16634": "踏宴扬旗",
    "16480": "割据秦宫",
    "16481": "割据秦宫",
    "16482": "割据秦宫",
    # "16870": "惊燕式",
    # "16933": "惊燕式",
    # "16934": "惊燕式",
    "16871": "逐鹰式",
    "16935": "逐鹰式",
    "16936": "逐鹰式",
    "16872": "控鹤式",
    "16937": "控鹤式",
    "16938": "控鹤式",
    "16873": "起风式",
    "16939": "起风式",
    "16940": "起风式",
    "16874": "腾蛟式",
    "16941": "腾蛟式",
    "16942": "腾蛟式",
    "16875": "擒龙式",
    "16943": "擒龙式",
    "16944": "擒龙式",
    # "23505": "擒龙六斩",
    "30645": "降麒式",
    # 藏剑
    "13470": "平湖断月",
    "1580": "玉泉鱼跃",
    "1782": "玉泉鱼跃",
    "1711": "醉月",
    "1712": "醉月",
    "1597": "鹤归孤山",
    "1598": "鹤归孤山",
    "1823": "峰插云景",
    # 纯阳
    "395": "大道无术",
    "396": "大道无术",
    "397": "大道无术",
    "398": "大道无术",
    "399": "大道无术",
    "421": "大道无术",
    "451": "大道无术",
    "452": "大道无术",
    "453": "大道无术",
    "454": "大道无术",
    "589": "人剑合一",
    "3050": "剑冲阴阳",
    "24973": "凌云剑",
    "327": "五方行尽",
    "328": "五方行尽",
    "329": "五方行尽",
    "330": "五方行尽",
    "331": "五方行尽",
    "461": "五方行尽",
    "462": "五方行尽",
    "463": "五方行尽",
    "464": "五方行尽",
    "465": "五方行尽",
    "3175": "三才化生",
    "303": "三才化生",
    "709": "七星拱瑞",
    "1776": "九转归一",
    ### 自化
    # 七秀
    "546": "剑影留痕",
    "15366": "帝骖龙翔",
    "15931": "水榭花盈",
    "558": "雷霆震怒",
    # 万花
    "497": "太阴指",
    "186": "芙蓉并蒂",
    "18406": "芙蓉并蒂",
    # 五毒
    "2209": "蝎心",
    "13472": "百足",
    "2218": "幻蛊",
    # 长歌
    ### 没有！
    # 苍云
    "13099": "盾猛",
    "13206": "撼地",
    "13068": "盾毅",
    "26232": "盾毅",
    "25215": "断马摧城",
    # 衍天
    "30026": "往者定",
    # 凌雪
    "22623": "骤雨寒江",
    "22610": "隐风雷",
    "22611": "隐风雷",
    "22787": "幽冥窥月",
    "22398": "铁马冰河",
    # 蓬莱
    ### 有奇穴基本都不带控
    # 丐帮
    ### 能进本再说
    # 药宗
    "29389": "沾衣未妨",
    "27539": "惊鸿掠水",
    "27636": "含锋破月",
    "27638": "飞叶满襟",
    # 刀宗
    "32766": "触石雨"
}

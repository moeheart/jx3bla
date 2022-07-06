# Created by moeheart at 10/11/2020
# 全局用到的部分常量。

EDITION = "7.10.0beta"
ANNOUNCEMENT = "剑三警长已经发布8.0.0，更新内容包括排名显示、专案组等重要功能，请务必更新！"
# IP = "120.48.95.56"
IP = "139.199.102.41"

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
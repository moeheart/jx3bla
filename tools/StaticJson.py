# [Auto-Generated File]
REVIEW_JSON = {
  "description1": "这份文档记录了所有在“专案组”模块中可能提及的问题。这既是技术文档也是用户文档。",
  "description2": "所有评判的细节都可以在这份文档中找到，同时文档也提供了json格式的所有接口及话术。",
  "description3": "json中必然会包含这三个字段：",
  "description4": "`code` 问题编号，唯一代表了所指定的问题。",
  "description5": "`status` 状态，指错误的严重程度，通常`0`代表正确，`1`代表轻微问题，`2`代表中等问题，`3`代表严重问题。",
  "description6": "每个问题不一定包含了所有的状态。",
  "description7": "`rate` 评分，100分为最好，0分为最差。这个评分会直接影响状态，也会作为结果显示。",
  "description8": "这份文档本身是json格式，是用于全流程中自动化生成话术的自动生成。",
  "description9": "review的结果也是json格式，用于作为展示界面的输入，请注意区分。",
  "content": [
    {
      "code": 1,
      "title": "不要死",
      "num": "重伤的次数",
      "duration": "重伤的总时间",
      "rate": "当`num`=0时为100%，否则为0%。",
      "threshold": [1, 1, 1, 0],
      "descCondition": [3],
      "desc": "所有的重伤都可以避免，请尝试躲避技能，正确处理机制。重伤会产生非常大的影响，不仅会极大程度降低你的团队贡献，而且增加了战斗失败的可能。",
      "addCondition": [3],
      "add": "你重伤了`num`次，期间浪费了`duration`s的时间。"
    },
    {
      "code": 10,
      "title": "不要放生队友",
      "num": "放生的次数",
      "time": "数组格式，放生的时间",
      "id": "数组格式，队友ID",
      "damage": "数组格式，队友受到的伤害名及伤害量",
      "rate": "当`num`=0时为100%，否则为0%。",
      "threshold": [1, 1, 1, 0],
      "descCondition": [3],
      "desc": "如果你的队友没有受到不可挽救的伤害，你就应当对其进行治疗以避免重伤。请记住，治疗职业的第一优先级永远是保证团队成员的存活，不要为了刷治疗量放弃队友。有时拯救队友需要快速的反应或者预判，这取决于你对副本的理解。",
      "addCondition": [3],
      "add": "你放生了`num`次队友：",
      "addArrayCondition": [3],
      "addArray": "`time`，`id`：`damage`"
    },
    {
      "code": 11,
      "title": "保持gcd不要空转",
      "cover": "战斗效率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "保持使用技能是战斗的基础。只要你持续处于读条或者转gcd的状态，就一定比站在原地发呆好。记得为可能产生的移动做好准备，在移动时也可以使用瞬发技能。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的战斗效率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 12,
      "title": "【已废弃】提高HPS或者虚条HPS",
      "hps": "HPS",
      "ohps": "虚条HPS",
      "hpsRank": "HPS的排名",
      "ohpsRank": "虚条HPS的排名",
      "rate": "为`hpsRank`与`ohpsRank`的较大者",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "HPS仍然是副本中评价治疗职业的公认标准，保证充足的HPS可以为团队提供更高的容错。在副本环境中，很多时候你需要用溢出治疗来保证血量健康，因此虚条HPS也可以是指标的一部分。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的HPS为`hps`，超过了`hpsRank`%的玩家；虚条HPS为`ohps`，超过了`ohpsRank`%的玩家。"
    },
    {
      "code": 13,
      "title": "使用有cd的技能",
      "cover": "技能使用率",
      "skill": "数组格式，技能名",
      "num": "数组格式，使用次数",
      "sum": "数组格式，总次数",
      "rate": "等于`cover`",
      "threshold": [50, 25, 0, 0],
      "descCondition": [1, 2],
      "desc": "有cd的技能大多都是十分强力的。虽然说有时这些技能应当用来救急，但是如果战斗中它们空转了过长的时间，你就应该去重新安排它们。",
      "addCondition": [0, 1, 2],
      "add": "技能使用情况：",
      "addArrayCondition": [0, 1, 2],
      "addArray": "`skill`：(`num`/`sum`)"
    },
    {
      "code": 14,
      "title": "提高rHPS",
      "rhps": "rHPS",
      "rhpsRank": "rHPS的排名",
      "rate": "为`rhpsRank",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "rHPS代表你对团队血量的综合贡献，是对治疗端的一个全局衡量方式。与游戏中HPS相比，化解、减伤等方式都可以提高rHPS，并且抢治疗量不会对rHPS有太多帮助。为了提高rHPS，最好的方式是熟悉基本循环；而当手法都合格的时候，调整团队治疗配置也可以进一步提高rHPS。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的rHPS为`rhps`，超过了`rhpsRank`%的玩家。"
    },
    {
      "code": 90,
      "title": "敬请期待",
      "rate": "固定为0%",
      "threshold": [100, 0, 0, 0],
      "descCondition": [1],
      "desc": "这个心法的功能还没有完全实现，敬请期待！"
    },
    {
      "code": 101,
      "title": "不要玩血歌",
      "num": "有没有玩血歌",
      "rate": "当`num`=0时为100%，否则为0%。",
      "threshold": [1, 1, 1, 0],
      "descCondition": [3],
      "desc": "只要不是全程持续伤害类型的副本，血歌的作用就永远比盾歌低。`梅花三弄`附带的化解和减伤同样可以减少团队血量的压力，并且还能带来输出增益，“团血崩了”绝不是你切血歌的理由。"
    },
    {
      "code": 102,
      "title": "保证`梅花三弄`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [50, 25, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`梅花三弄`的覆盖率是奶歌最重要的指标，保证覆盖率可以增加团队输出，同时也为团队血量提供保障。多数时候，即使面对血量不满的目标也应当贴盾，让其它治疗来奶满。",
      "addCondition": [0, 1, 2, 3],
      "add": "覆盖率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 103,
      "title": "中断`徵`的倒读条",
      "time": "次数",
      "perfectTime": "正确中断次数",
      "fullTime": "未中断次数",
      "rate": "等于`perfectTime`/`time`",
      "threshold": [50, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`徵`应当在读条过半时中断（带有`争簇`时为第3跳，无`争簇`时为第2跳），这样可以最大化利用`弄梅`；特别是当点出`谪仙`时，不中断会导致损失徵的跳数。",
      "addCondition": [0, 1, 2, 3],
      "add": "你总共运功了`time`次徵，其中正确中断了`perfectTime`次，有`fullTime`次完全没有进行中断。"
    },
    {
      "code": 104,
      "title": "选择合适的`徵`目标",
      "time": "次数",
      "coverTime": "覆盖人数正常的徵次数",
      "rate": "等于`coverTime`/`time`",
      "threshold": [75, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`徵`会以当前目标中心进行20尺扩散，因此选择正确的目标可以让更多队友受到治疗效果。使用茗伊团队面板的扩散辅助可以精准地找到最适合的目标。",
      "addCondition": [1, 2, 3],
      "add": "你总共施放了`time`次徵，但只有`coverTime`次覆盖了4个或更多的目标。"
    },
    {
      "code": 105,
      "title": "(废弃)使用`移形换影`",
      "time": "放影子的次数",
      "coverTime": "吃影子的次数",
      "wasteTime": "没有吃到影子的次数",
      "rate": "等于`covertime`/`time`",
      "threshold": [75, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "记得使用`移形换影`去回收影子以维持健康的内力，从而弥补贴盾的大量消耗。",
      "addCondition": [1, 2, 3],
      "add": "你浪费了`wasteTime`次影子提供的回蓝。"
    },
    {
      "code": 106,
      "title": "(废弃)使用`角`",
      "cover": "角的整体覆盖率",
      "rate": "吃影子的次数",
      "threshold": [50, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "记得保持`角`的覆盖以维持健康的内力，从而弥补贴盾的大量消耗。角的持续治疗效果对主T的血量也是可观的支持。"
    },
    {
      "code": 107,
      "title": "使用`暗香`提高刷盾的效率",
      "timeAnxiang": "暗香次数",
      "timeMhsn": "梅花三弄次数",
      "timeAll": "总次数",
      "rate": "等于(3)/(1+2)",
      "threshold": [50, 10, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "使用`暗香`进行刷盾可以节省一个gcd，是奶歌的进阶技巧；为了让`暗香`有效率地触发，你需要保证读条不中断，目标附近有玩家且远离NPC。尽量把影子放置在远离大团的位置可以很大程度提高暗香的效率。",
      "addCondition": [1, 2, 3],
      "add": "你共计有`timeAll`次补盾操作，其中`暗香`有`timeAnxiang`次。"
    },
    {
      "code": 201,
      "title": "保证`秋肃`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "`秋肃`会为团队带来可观的输出增益，是奶花在副本中最有价值的门票。尝试通过各种监控方式去适应秋肃的手感，绝对不要让增益中断。",
      "addCondition": [0, 1, 2, 3],
      "add": "覆盖率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 202,
      "title": "保证`握针`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "`握针`是奶花最重要的治疗量来源，尽可能使全团保持这个效果。`握针`的数量也是评判奶花手法最重要的依据。",
      "addCondition": [0, 1, 2, 3],
      "add": "覆盖率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 203,
      "title": "(废弃)不要浪费瞬发次数",
      "timeShuiyue": "水月次数",
      "timeXqx": "行气血次数",
      "timeCast": "用掉的瞬发次数",
      "rate": "等于(3)/(1+2)",
      "threshold": [75, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`行气血`与`水月无间`提供的瞬发效果可以让你无损瞬发技能，但是如果时间用尽或者被新的`行气血`顶掉就会失去这些机会。尽可能利用好这些瞬发次数。",
      "addCondition": [1, 2, 3],
      "add": "你获得了`timeShuiyue`层水月，`timeXqx`层行气血，但你只使用了其中的`timeCast`次。"
    },
    {
      "code": 204,
      "title": "(废弃)优先瞬发`长针`",
      "timeCast": "水月次数",
      "timeChangzhen": "长针次数",
      "rate": "等于2/1",
      "threshold": [75, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "尽可能使用瞬发效果去瞬发`长针`，这可以为你节省一个gcd的时间；瞬发`提针`与`彼针`不能为你节省gcd时间，除非这一个gcd可以用来救急，否则不应该这样瞬发。",
      "addCondition": [1, 2, 3],
      "add": "你使用了`timeCast`次瞬发，但只有`timeChangzhen`次用于长针。"
    },
    {
      "code": 205,
      "title": "选择合适的`长针`目标",
      "time": "长针次数",
      "coverTime": "覆盖人数正常的长针次数",
      "rate": "等于`coverTime`/`time`",
      "threshold": [75, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`微潮`会以当前目标中心进行15尺扩散，因此选择正确的目标可以让更多队友受到`握针`的效果。使用茗伊团队面板的扩散辅助可以精准地找到最适合的目标。",
      "addCondition": [1, 2, 3],
      "add": "你总共触发了`time`次微潮，但只有`coverTime`次覆盖了4个或更多的目标。"
    },
    {
      "code": 206,
      "title": "提高握针扩散效率",
      "cover": "握针平均扩散的数量",
      "rate": "等于`cover`/4",
      "threshold": [75, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`微潮`只能将`握针`扩散到身上没有`握针`的目标，所以使用时不仅要保证目标身上有`握针`，还要让对应小队的`握针`数量越少越好。如果小队中`握针`还没有跳完，就应当改用`束彼`去刷新，或是等待其时间结束。",
      "addCondition": [1, 2, 3],
      "add": "理想情况下每次微潮应该扩散4个目标，但你平均扩散了`cover`个目标。"
    },
    {
      "code": 207,
      "title": "优先使用`水月无间`瞬发`长针`",
      "timeCast": "水月无间提供的瞬发次数",
      "timeChangzhen": "用于瞬发长针的次数",
      "rate": "等于2/1",
      "threshold": [90, 70, 50, 0],
      "descCondition": [1, 2, 3],
      "desc": "在`水月无间`的瞬发效果期间应当瞬发`长针`，这可以为你节省一个gcd的时间；瞬发`提针`与`彼针`不能为你节省gcd时间，除非这一个gcd可以用来救急，否则不应该这样瞬发。",
      "addCondition": [1, 2, 3],
      "add": "你使用了`timeCast`次`水月无间`提供的瞬发，但只有`timeChangzhen`次用于长针。"
    },
    {
      "code": 208,
      "title": "充分利用墨意",
      "sumMoyi": "总计消耗的墨意值",
      "wastedMoyi": "浪费的墨意值",
      "usedMoyi": "有效使用的墨意值",
      "rate": "等于2/3",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "每20点墨意值可以用来瞬发一次`长针`，这可以节省一个gcd，是你最主要的治疗手段。如果墨意溢出，这部分墨意就会浪费掉，尽可能避免这种情况。",
      "addCondition": [1, 2, 3],
      "add": "你浪费了`wastedMoyi`点墨意值。"
    },
    {
      "code": 209,
      "title": "使用`落子无悔`的buff效果",
      "sumBlack": "触发黑子的次数",
      "sumWhite": "触发白子的次数",
      "sumNone": "没有触发的次数",
      "rate": "等于(1+2)/(1+2+3)",
      "threshold": [100, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`落子无悔`可以获得输出增益buff或者减伤buff，但是当黑白子数量相同时就无法获得这个buff，尽量避免这种情况。",
      "addCondition": [1, 2, 3],
      "add": "你浪费了`sumNone`次触发buff的机会。"
    },
    {
      "code": 301,
      "title": "保证`灵素中和`的触发次数",
      "numPerSec": "每秒次数",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "`灵素中和`是药奶的主要治疗来源，也是简单有效地衡量药奶手法的手段。由于其自动选取血量最低的队友的特点，只要保证中和的触发次数，就一定可以有稳定的治疗量。",
      "addCondition": [0, 1, 2, 3],
      "add": "每秒次数为`numPerSec`，超过了`rank`%的玩家。"
    },
    {
      "code": 302,
      "title": "避免药性溢出",
      "numOver": "溢出的药性数量",
      "numAll": "药性变化总量",
      "rate": "等于1 - `numOver` / `numAll`",
      "threshold": [95, 90, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "药奶的中和机制需要药性在温性与寒性之间互相抵消，而药性超过+5或-5的部分不会被累加，你需要调整技能的施放方式以尽量避免这种情况。有时药性溢出是不可避免的，但这个比例过高则意味着一定出现了问题。",
      "addCondition": [0, 1, 2, 3],
      "add": "由于药性溢出，你浪费了`numOver`点药性。"
    },
    {
      "code": 303,
      "title": "提高`飘黄`的覆盖人数",
      "numCover": "飘黄平均覆盖人数",
      "numAll": "总人数",
      "rate": "`numCover` / `numAll`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`飘黄`是药奶最有价值的增益技能，但是只对10尺内的玩家生效。你需要调整站位以使其覆盖更多的队友，有时还需要根据副本机制来决定合适的施放时机。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的`飘黄`平均覆盖人数为`numCover`，而总人数为`numAll`。"
    },
    {
      "code": 304,
      "title": "注意控制`七情`状态",
      "maxLayer": "最高的七情层数",
      "rate": "等于100-10*`maxlayer`",
      "threshold": [50, 30, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`七情和合`是优秀的爆发技能，但多次叠加`七情`会使自身叠加显著的治疗降低效果，因此需要尝试在合适的时机消除`七情`。",
      "addCondition": [1, 2, 3],
      "add": "你将`七情`debuff最高叠加到了`maxLayer`层。"
    },
    {
      "code": 305,
      "title": "充分使用`千枝绽蕊`",
      "time": "`千枝绽蕊`的总时间",
      "num": "千枝绽蕊期间触发的中和数量",
      "efficiency": "等于`num` / `time` * 1.75",
      "rate": "等于min(100, `efficiency`)",
      "threshold": [50, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`畅和`奇穴下，`千枝绽蕊`期间只有`灵素中和`能受到增益，但无论有没有触发中和都会消耗内力，所以尽量在此期间触发更多的中和数量。使用快速开关切换可以大幅度提高效率。",
      "addCondition": [1, 2, 3],
      "add": "在`千枝绽蕊`期间的`time`秒中，你触发了`num`次中和，效率为`efficiency`。"
    },
    {
      "code": 401,
      "title": "保证`冰蚕牵丝`或`醉舞九天`的触发次数",
      "bcNum": "`冰蚕牵丝`的每秒次数",
      "bcRank": "`冰蚕牵丝`的天网排名",
      "zwNum": "`醉舞九天`的每秒次数",
      "zwRank": "`醉舞九天`的天网排名",
      "rate": "等于max(`bcRank`, `zwRank`)",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "根据流派不同，`冰蚕牵丝`或`醉舞九天`之一是你的主要填充技能，你需要保证其触发次数从而提供稳定的治疗。",
      "addCondition": [0, 1, 2, 3],
      "add": "`冰蚕牵丝`的每秒次数为`bcNum`，超过了`bcRank`%的玩家；`醉舞九天`的每秒次数为`zwNum`，超过了`zwRank`%的玩家。"
    },
    {
      "code": 402,
      "title": "使用`蛊惑众生`",
      "cover": "`蛊惑众生`的整体覆盖率",
      "rate": "等于`cover`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`蛊惑众生`是非常强力的单体保人技能，不要因为游戏内插件不统计就忘记施放了。",
      "addCondition": [1, 2, 3],
      "add": "`蛊惑众生`的覆盖率为`cover`。"
    },
    {
      "code": 403,
      "title": "(废弃)保证回蓝技能的使用次数",
      "cover": "技能使用率",
      "skill": "数组格式，技能名",
      "num": "数组格式，使用次数",
      "sum": "数组格式，总次数",
      "rate": "等于`cover`",
      "threshold": [80, 60, 40, 0],
      "descCondition": [1, 2, 3],
      "desc": "`迷仙引梦`和`仙王蛊鼎`是相当强力的回蓝技能，并且在治疗层面也拥有超乎想象的性价比。作为奶毒，应当尽可能关注这两个技能的cd情况。",
      "addCondition": [0, 1, 2, 3],
      "add": "技能使用情况：",
      "addArrayCondition": [0, 1, 2, 3],
      "addArray": "`skill`：(`num`/`sum`)"
    },
    {
      "code": 404,
      "title": "不要回收`迷仙引梦`",
      "timeCast": "回收的次数",
      "timeAll": "总次数",
      "rate": "等于1 - `timeCast` / `timeAll`",
      "threshold": [90, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`迷仙引梦`的主要作用应当是回蓝，回收会导致损失回蓝的跳数，并且治疗量也得不偿失，不应当为了抢治疗进行回收。",
      "addCondition": [1, 2, 3],
      "add": "你回收了`timeCast`次`迷仙引梦`。"
    },
    {
      "code": 405,
      "title": "使用`蚕引`层数",
      "sumAll": "总层数",
      "timeCast": "用掉的瞬发次数",
      "rate": "等于`timeCast` / `sumall`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`蚕引`效果附赠了具有治疗增益的`冰蚕诀`，记得在30秒之内把它们全部用掉。",
      "addCondition": [1, 2, 3],
      "add": "你获得了`sumAll`层蚕引，但你只使用了其中的`timeCast`次。"
    },
    {
      "code": 406,
      "title": "保留`碧蝶献祭`的会心增益到`蝶池`",
      "sumAll": "施放献祭的次数",
      "rightTime": "正确保留的次数",
      "rate": "等于`rightTime` / `sumAll`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`碧蝶献祭`会获得一个必会心的buff，它会被治疗技能消耗掉，所以应当在1秒之内避免使用其它治疗技能从而让`蝶池`吃到这个增益。",
      "addCondition": [1, 2, 3],
      "add": "你使用了`sumAll`次`蛊虫献祭`，但是只有`rightTime`次正确处理了必会心的buff。"
    },
    {
      "code": 407,
      "title": "提高`仙王蛊鼎`的覆盖人数",
      "numCover": "仙王蛊鼎平均覆盖人数",
      "numAll": "总人数",
      "rate": "`numCover` / `numAll`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`仙王蛊鼎`的增益效果只在施放时判定。你需要在施放`仙王蛊鼎`之前调整站位，使其覆盖尽可能多的团队成员。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的`仙王蛊鼎`平均覆盖人数为`numCover`，而总人数为`numAll`。"
    },
    {
      "code": 408,
      "title": "保证`仙王蛊鼎`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [25, 0, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`仙王蛊鼎`是奶毒的增益技能，需要尽可能多地施放，从而最大程度提高团队输出。有时需要将锅对齐给爆发阶段，但你需要为这种情况设计技能轴，最大程度减少损失。",
      "addCondition": [0, 1, 2, 3],
      "add": "覆盖率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 409,
      "title": "保证`迷仙引梦`的使用次数",
      "cover": "技能使用率",
      "num": "使用次数",
      "sum": "总次数",
      "rate": "等于`cover`",
      "threshold": [80, 60, 40, 0],
      "descCondition": [1, 2, 3],
      "desc": "`迷仙引梦`是相当强力的回蓝技能，并且在治疗层面也拥有极高的性价比。作为奶毒，你需要尽可能不让其空转cd。",
      "addCondition": [0, 1, 2, 3],
      "add": "你使用了`num`次`迷仙引梦`，而战斗时间内总共可以使用`sum`次。"
    },
    {
      "code": 501,
      "title": "保证`回雪飘摇`的触发次数",
      "numPerSec": "每秒次数",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "`回雪飘摇`是奶秀的填充技能，也是最主要的治疗来源，保持回雪飘摇的不间断施放是奶秀最基本的手法，在充分练习之后可以得到非常稳定的治疗量。",
      "addCondition": [0, 1, 2, 3],
      "add": "每秒次数为`numPerSec`，超过了`rank`%的玩家。"
    },
    {
      "code": 502,
      "title": "保证`上元点鬟`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [50, 25, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`上元点鬟`是奶秀的进阶手法，但现在几乎也是必须掌握的操作了。在`翔舞`基本稳定覆盖大多数队友之后，`上元点鬟`就是拉开手法差距的最重要一环。",
      "addCondition": [0, 1, 2, 3],
      "add": "上元覆盖率为`cover`，超过了`rank`%的玩家。"
    },
    {
      "code": 503,
      "title": "中断`回雪飘摇`的倒读条",
      "time": "次数",
      "perfectTime": "正确中断次数",
      "earlyTime": "过早中断次数",
      "rate": "等于`perfectTime`/`time`",
      "threshold": [85, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "你需要在`回雪飘摇`第二跳之后直接使用gcd技能，而不是等倒读条结束，这样每6跳回雪飘摇中你就多了一个施展gcd技能的机会；另外，也不要过早中断，这样会直接导致回雪跳数损失。",
      "addCondition": [1, 2, 3],
      "add": "你总共运功了`time`次`回雪飘摇`，但其中只正确中断了`perfectTime`次，有`earlyTime`次因过早中断而损失了跳数。"
    },
    {
      "code": 504,
      "title": "不要重复施放`上元点鬟`",
      "time": "总次数",
      "perfectTime": "正确施放次数",
      "wrongTime": "错误施放次数",
      "rate": "等于`perfectTime`/`time`",
      "threshold": [95, 90, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "不要对已经有`上元点鬟`的目标再次施放`上元点鬟`，这样会使其末跳被覆盖。如果是极限的单加情况为了触发首跳，你也应当使用`翔鸾舞柳`来代替。",
      "addCondition": [1, 2, 3],
      "add": "你有`wrongTime`次`上元点鬟`重复施放，导致损失了末跳。"
    },
    {
      "code": 505,
      "title": "提高`左旋右转`的覆盖人数",
      "numCover": "左旋右转平均覆盖人数",
      "numAll": "总人数",
      "rate": "`numCover` / `numAll`",
      "threshold": [90, 50, 0, 0],
      "descCondition": [1, 2, 3],
      "desc": "`左旋右转`只对自己周围的目标有效。你需要在施放`左旋右转`之前调整站位，使其覆盖尽可能多的团队成员。",
      "addCondition": [0, 1, 2, 3],
      "add": "你的`左旋右转`平均覆盖人数为`numCover`，而总人数为`numAll`。"
    },
    {
      "code": 506,
      "title": "保证`左旋右转`的覆盖率",
      "cover": "覆盖率",
      "rank": "天网排名",
      "rate": "等于`rank`",
      "threshold": [75, 50, 25, 0],
      "descCondition": [1, 2, 3],
      "desc": "`左旋右转`有非常高的DPS增益，其持续时间比cd要长，是可以全程保持的。你需要保证最大的覆盖率，不能中断读条，在此基础上可以通过排轴来尽量使其治疗量发挥作用。",
      "addCondition": [0, 1, 2, 3],
      "add": "覆盖率为`cover`，超过了`rank`%的玩家。"
    }
  ]
}




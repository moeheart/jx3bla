# Created by moeheart at 11/20/2022
# 输出复盘的通用方法。尝试将共享的部分尽可能提取。

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from tools.Names import *
from tools.Functions import *
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *

import time

class DpsReplayer(ReplayerBase):

    # def calculateSkillInfoDirect(self, name, skillObj):
    #     '''
    #     根据技能名和对象统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - skillObj: skillInfo中定义的技能对象.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))
    #
    # def calculateSkillInfo(self, name, id):
    #     '''
    #     根据技能名和ID统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - id: 技能的ID，用于在skillInfo中查找.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     skillObj = self.skillInfo[self.gcdSkillIndex[id]][0]
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))

    def calculateSkillFinal(self):
        '''
        第二阶段结束时最后计算评分的部分.
        '''

        # 排序
        # self.result["review"]["content"].sort(key=lambda x: -x["status"] * 1000 + x["rate"])
        # num = 0
        # for line in self.result["review"]["content"]:
        #     if line["status"] > 0:
        #         num += 1
        #         self.reviewScore -= [0, 1, 3, 10][line["status"]] * 100
        # self.result["review"]["num"] = num

        self.calculateSkillOverall()
        self.result["review"]["score"] = self.reviewScore
        self.result["skill"]["general"]["score"] = self.reviewScore

    def calculateSkillOverall(self):
        '''
        第二阶段结束时共有的技能统计部分.
        '''

        # self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()
        self.result["skill"]["general"]["rdps"] = self.myHealStat.get("rdps", 0)
        self.result["skill"]["general"]["ndps"] = self.myHealStat.get("ndps", 0)
        self.result["skill"]["general"]["mrdps"] = self.myHealStat.get("mrdps", 0)
        self.result["skill"]["general"]["mndps"] = self.myHealStat.get("mndps", 0)

        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["ohps"] = self.myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = self.myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = self.myHealStat.get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = self.myHealStat.get("ahps", 0)

        self.getRankFromStat(self.occ)
        self.result["rank"] = self.rank
        # sumWeight = 0
        # sumScore = 0
        # for key1 in self.result["rank"]:
        #     for key2 in self.result["rank"][key1]:
        #         key = "%s-%s" % (key1, key2)
        #         weight = 1
        #         if key in self.specialKey:
        #             weight = self.specialKey[key]
        #         sumScore += self.result["rank"][key1][key2]["percent"] * weight
        #         sumWeight += weight

        self.reviewScore = 0

        # 计算专案组的公有部分.

        self.result["review"] = {"available": 0, "content": []}

    def completeSecondState(self):
        '''
        第二阶段扫描完成后的公共流程.
        '''
        bh = self.bh
        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]
            bh.badPeriodDpsLog = self.bossBh.badPeriodDpsLog
            bh.badPeriodHealerLog = self.bossBh.badPeriodHealerLog

        # 计算团队伤害区(Part 3)
        self.result["dps"] = {"stat": {}, "source": {}, "boostSource": {}}

        self.myHealStat = {}

        player = self.mykey
        res = {"rhps": int(self.act.getRhps(player)),
               "hps": int(self.act.getRhps(player, "hps")),
               "ahps": int(self.act.getRhps(player, "ahps")),
               "phps": int(self.act.getRhps(player, "ohps")),
               "rdps": int(self.act.getRdps(player)),
               "ndps": int(self.act.getRdps(player, "ndps")),
               "mrdps": int(self.act.getRdps(player, "mrdps")),
               "mndps": int(self.act.getRdps(player, "mndps"))}
        self.result["dps"]["stat"] = res
        self.myDpsStat = res


    def handleGcdSkill(self, event):
        '''
        处理gcd技能, 这是第二阶段主循环的子功能.
        params:
        - event: 处理的事件.
        '''
        pass

    def eventInSecondState(self, event):
        '''
        第二阶段处理事件的公共流程.
        params:
        - event: 处理的事件.
        '''

        # prevStatus = self.excludeStatusHealer
        #
        # while self.excludePosHealer < len(self.badPeriodHealerLog) and event.time > self.badPeriodHealerLog[self.excludePosHealer][0]:
        #     self.excludeStatusHealer = self.badPeriodHealerLog[self.excludePosHealer][1]
        #     self.excludePosHealer += 1
        #
        # if self.excludeStatusHealer != prevStatus:
        #     # 排除状态变化
        #     for obj in self.allSkillObjs:
        #         obj.setExclude(self.excludeStatusHealer)

        if event.dataType == "Skill":
            # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
            if event.effect == 7:
                return

            if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey:
                pass

            if event.caster == self.mykey and event.scheme == 1:
                # 根据技能表进行自动处理
                if event.id in self.gcdSkillIndex:
                    self.handleGcdSkill(event)
                # 处理特殊技能
                elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                    pass

        elif event.dataType == "Buff":
            pass


    def initSecondState(self):
        '''
        第二阶段初始化.
        '''
        self.battleTimeDict = {}  # 进战时间
        self.sumPlayer = 0  # 平均玩家数

        # 技能初始化
        # self.allSkillObjs = []
        self.gcdSkillIndex = {}
        self.nonGcdSkillIndex = {}
        # for i in range(len(self.skillInfo)):
        #     line = self.skillInfo[i]
        #     if line[0] is None:
        #         self.skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)
        #         # self.allSkillObjs.append(self.skillInfo[i][0])
        #     for id in line[2]:
        #         if line[4]:
        #             self.gcdSkillIndex[id] = i
        #         else:
        #             self.nonGcdSkillIndex[id] = i

        # 未解明技能
        self.unimportantSkill = ["4877",  # 水特效作用
                               "25682", "25683", "25684", "25685", "25686", "24787", "24788", "24789", "24790", # 破招
                               "22155", "22207", "22211", "22201", "22208",  # 大附魔
                               "3071", "18274", "14646", "604",  # 治疗套装，寒清，书离，春泥
                               "23951",  # 贯体通用
                               "14536", "14537",  # 盾填充, 盾移除
                               "3584", "2448",  # 蛊惑
                               "6800",  # 风特效
                               "25231",  # 桑柔判定
                               "21832",  # 绝唱触发
                               "9007", "9004", "9005", "9006",  # 后跳，小轻功
                               "29532", "29541",  # 飘黄
                               "4697", "13237",  # 明教阵眼
                               "13332",  # 锋凌横绝阵
                               "14427", "14426",  # 浮生清脉阵
                               "26128", "26116", "26129", "26087",  # 龙门飞剑
                               "28982",  # 药宗阵
                               "742",  # T阵
                               "14358",  # 删除羽减伤
                               "14250",  # 平吟删减伤
                               "2918",  # 可能和天策技能有关的驱散
                            ]

        # 战斗回放初始化
        self.bh = BattleHistory(self.startTime, self.finalTime)
        # self.ss = SingleSkill(self.startTime, self.haste)


    def getOverallInfo(self):
        '''
        获取全局信息.
        '''
        # 大部分全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "%s复盘pro v%s" % (self.occPrint, EDITION)
        self.result["overall"]["playerID"] = "未知"
        self.result["overall"]["server"] = self.bld.info.server
        self.result["overall"]["battleTime"] = self.bld.info.battleTime
        self.result["overall"]["battleTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        self.result["overall"]["generateTime"] = int(time.time())
        self.result["overall"]["generateTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["generateTime"]))
        self.result["overall"]["map"] = self.bld.info.map
        self.result["overall"]["boss"] = getNickToBoss(self.bld.info.boss)
        self.result["overall"]["sumTime"] = self.bld.info.sumTime
        self.result["overall"]["sumTimePrint"] = parseTime(self.bld.info.sumTime / 1000)
        self.result["overall"]["sumTimeEff"] = self.bossBh.sumTime("healer")
        self.result["overall"]["sumTimeEffPrint"] = parseTime(self.result["overall"]["sumTimeEff"] / 1000)
        self.result["overall"]["sumTimeDpsEff"] = self.bossBh.sumTime("dps")
        self.result["overall"]["dataType"] = self.bld.dataType
        self.result["overall"]["mask"] = self.config.item["general"]["mask"]
        self.result["overall"]["win"] = self.win

    def completeFirstState(self):
        '''
        第一阶段扫描完成后的公共流程.
        '''

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        self.result["overall"]["playerID"] = self.myname

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        self.result["equip"] = {"available": 0}

        if self.mykey in self.equip and self.equip[self.mykey] is not None:
            # TODO 验证
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            res = self.equip[self.mykey]
            self.result["equip"]["score"] = int(self.bld.info.player[self.mykey].equipScore)
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res["根骨"]
            # self.result["equip"]["heal"] = res["治疗"]
            # self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["attack"] = res["攻击"]
            self.result["equip"]["attackBase"] = res["基础攻击"]
            self.result["equip"]["critPercent"] = parseCent(res["会心"]) + "%"
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = parseCent(res["会效"]) + "%"
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["overcomePercent"] = parseCent(res["破防"]) + "%"
            self.result["equip"]["overcome"] = res["破防等级"]
            self.result["equip"]["strainPercent"] = parseCent(res["无双"]) + "%"
            self.result["equip"]["strain"] = res["无双等级"]
            self.result["equip"]["surplus"] = res["破招"]
            self.result["equip"]["hastePercent"] = parseCent(res["加速"]) + "%"
            self.result["equip"]["haste"] = res["加速等级"]
            self.haste = self.result["equip"]["haste"]
            self.result["equip"]["raw"] = strEquip

        self.result["qixue"] = {"available": 0}
        if self.bld.info.player[self.mykey].qx != {}:
            self.result["qixue"]["available"] = 1
            for key in self.bld.info.player[self.mykey].qx:
                qxKey = "1,%s,1" % self.bld.info.player[self.mykey].qx[key]["2"]
                qxKey0 = "1,%s,0" % self.bld.info.player[self.mykey].qx[key]["2"]
                if qxKey in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey]
                elif qxKey0 in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey0]
                elif self.bld.info.player[self.mykey].qx[key]["2"] == "0":
                    self.result["qixue"]["available"] = 0
                    break
                else:
                    self.result["qixue"][key] = self.bld.info.player[self.mykey].qx[key]["2"]

        # print(self.result["overall"])
        # print(self.result["equip"])
        # print(self.result["qixue"])

        # self.result["overall"]["hasteReal"] = self.haste

    def eventInFirstState(self, event):
        '''
        第一阶段处理事件的公共流程.
        params:
        - event: 处理的事件.
        '''

        if event.dataType == "Skill":
            # 记录治疗心法的出现情况.
            pass

        elif event.dataType == "Buff":
            pass

        elif event.dataType == "Shout":
            # 为未来需要统计喊话时备用.
            pass

    def initFirstState(self):
        '''
        第一阶段初始化.
        '''

        self.getOverallInfo()

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.  TODO 用无效时间修复这个逻辑
        self.interrupt = 0

        # 记录战斗开始时间与结束时间
        if self.startTime == 0:
            self.startTime = self.bld.log[0].time
        if self.finalTime == 0:
            self.finalTime = self.bld.log[-1].time

        # 如果时间被大幅度修剪过，则修正战斗时间  TODO 用无效时间修复这个逻辑
        if abs(self.finalTime - self.startTime - self.result["overall"]["sumTime"]) > 6000:
            actualTime = self.finalTime - self.startTime
            self.result["overall"]["sumTime"] = actualTime
            self.result["overall"]["sumTimePrint"] = parseTime(actualTime / 1000)

        # 记录具体心法的表.
        self.occDetailList = {}
        for key in self.bld.info.player:
            self.occDetailList[key] = self.bld.info.player[key].occ

        # 推导自身id
        for key in self.bld.info.player:
            if self.bld.info.player[key].name == self.myname:
                self.mykey = key

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        '''

        self.window.setNotice({"t2": "加载%s复盘..." % self.occ, "c2": self.occColor})

        self.initFirstState()

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue
            if self.interrupt != 0:
                continue

            self.eventInFirstState(event)

            if event.dataType == "Skill":
                pass

            elif event.dataType == "Buff":
                pass

        self.completeFirstState()
        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速, cd时间, 充能数量]
        self.skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True, 0, 1],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True, 30, 1],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True, 30, 1]
                    ]

        self.initSecondState()

        # for event in self.bld.log:
        #     if event.time < self.startTime:
        #         continue
        #     if event.time > self.finalTime:
        #         continue
        #
        #     self.eventInSecondState(event)
        #
        #     if event.dataType == "Skill":
        #         # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
        #         if event.effect == 7:
        #             # 所有治疗技能都不计算化解.
        #             continue
        #
        #     elif event.dataType == "Buff":
        #         pass
        #
        #     elif event.dataType == "Shout":
        #         pass
        #
        #     elif event.dataType == "Death":
        #         pass
        #
        #     elif event.dataType == "Battle":
        #         pass

        self.completeSecondState()

        # 计算DPS列表(Part 7)

        pass

        # 整体
        self.result["skill"] = {}
        self.result["skill"]["general"] = {}

        self.calculateSkillFinal()


    def replay(self):
        '''
        开始复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", actorData={}, myocc="0"):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - myname: 需要复盘的奶歌名.
        - actorData: 演员复盘得到的统计记录.
        '''
        super().__init__(config, fileNameInfo, path, bldDict, window, actorData)
        self.public = 1  # 暂时强制公开，反正没什么东西  TODO 更改设置中的选项，简化内容
        self.myname = myname
        self.occ = OCC_PINYIN_DICT[myocc]
        self.occCode = myocc
        self.occPrint = OCC_NAME_DICT[myocc]
        self.occColor = getColor(myocc)
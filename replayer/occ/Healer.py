# Created by moeheart at 08/08/2021
# 治疗复盘的通用方法。尝试将共享的部分尽可能提取。

from replayer.ReplayerBase import ReplayerBase
from replayer.occ.HealingChannel import HealingChannel, channel_efficiencies

from replayer.BattleHistory import BattleHistory, SingleSkill
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *

import time
from bisect import bisect_left

class HealerReplay(ReplayerBase):

    # (JCL Cast IDs, canonical pulse ID from skillInfo, pulses per channel)
    gcdChannel = None
    gcdChannelShells = ()
    gcdChannelImmediate = False

    def channelUseStats(self, casts):
        """Count starts and pulses independently, using the healer's valid periods."""
        exclusions = self.bh.badPeriodHealerLog
        boundaries = [time for time, _ in exclusions]

        def eligible(time):
            # SkillHealCounter applies each boundary strictly after its timestamp.
            pos = bisect_left(boundaries, time)
            return pos == 0 or not exclusions[pos - 1][1]

        actions = iter(self.bh.log["normal"])
        previous = next(actions, None)
        previous_end = self.startTime
        count = ticks = 0
        delays = []
        for cast in casts:
            while previous and previous["start"] < cast.start:
                previous_end = max(previous_end, previous["start"] + previous["duration"])
                previous = next(actions, None)
            if not cast.partial and eligible(cast.start):
                count += 1
                delay = max(0, cast.start - previous_end)
                if delay <= SkillCounter.MAX_DELAY_MS:
                    delays.append(delay)
            ticks += sum(eligible(time) for time in cast.ticks)
            previous_end = max(previous_end, cast.end)
        return {"num": count, "ticks": ticks, "delay": int(safe_divide(sum(delays), len(delays))),
                "delaySamples": len(delays)}

    def calculateSkillInfoDirect(self, name, skillObj, casts=None):
        """Summarize a skill's use count, delay and healing in valid combat time."""
        total_heal = skillObj.getHeal()
        effective_heal = skillObj.getHealEff()
        if casts is None:
            stats = {"num": skillObj.getNum(), **skillObj.getDelayStats()}
        else:
            stats = self.channelUseStats(casts)
            # One pulse may heal several targets. Keep those settlements and
            # their amounts separate from both cast starts and pulse counts.
            stats["healingEvents"] = sum(1 for row in skillObj.log if row[3] > 0 and not row[7])
            stats["heal"] = total_heal
            stats["healEff"] = effective_heal
        active_time = self.result["overall"]["sumTimeEff"]
        stats["numPerSec"] = roundCent(stats["num"] / active_time * 1000, 2) if active_time else 0
        stats["HPS"] = int(effective_heal / active_time * 1000) if active_time else 0
        stats["effRate"] = roundCent(safe_divide(effective_heal, total_heal))
        self.result["skill"][name] = stats

    def calculateSkillInfo(self, name, id):
        index = self.gcdSkillIndex[id]
        casts = self.channelCasts if self.gcdChannel and index == self.gcdSkillIndex[self.gcdChannel[1]] else None
        self.calculateSkillInfoDirect(name, self.skillInfo[index][0], casts)

    def calculateSkillOverall(self, channelLog=None):
        '''
        第二阶段结束时共有的技能统计部分.
        '''
        self.result["skill"]["mufeng"] = {}
        num = self.battleTimeDict[self.mykey]
        sum = self.mufengDict.buffTimeIntegral(exclude=self.bh.badPeriodHealerLog)
        self.result["skill"]["mufeng"]["cover"] = roundCent(safe_divide(sum, num))
        if channelLog is None:
            self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()
        else:
            self.result["skill"]["general"].update(channel_efficiencies(self.bh, channelLog))
        self.result["skill"]["general"]["rdps"] = self.myHealStat.get("rdps", 0)
        self.result["skill"]["general"]["ndps"] = self.myHealStat.get("ndps", 0)
        self.result["skill"]["general"]["mrdps"] = self.myHealStat.get("mrdps", 0)
        self.result["skill"]["general"]["mndps"] = self.myHealStat.get("mndps", 0)

        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = self.myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["healEff"] = self.myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["ohps"] = self.myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = self.myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = self.myHealStat.get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = self.myHealStat.get("ahps", 0)
        self.result["skill"]["healer"]["chps"] = self.myHealStat.get("chps", 0)

        self.getRankFromStat(self.occ)
        self.result["rank"] = self.rank

    def completeTeamDetect(self):
        '''
        小队聚类的结束流程.
        '''

        # 计算组队聚类信息
        self.teamCluster, self.numCluster = finalCluster(self.teamLog)

    def eventInTeamDetect(self, event):
        '''
        小队聚类在循环中的主体.
        params:
        - event: 处理的事件.
        '''

        if event.dataType == "Buff":
            if event.id in ["9459", "9460", "9461", "9462"] and event.caster == self.mykey:  # 商
                self.teamLog, self.teamLastTime = countCluster(self.teamLog, self.teamLastTime, event)
            if event.id in ["9463", "9464", "9465", "9466"] and event.caster == self.mykey:  # 角
                self.teamLog, self.teamLastTime = countCluster(self.teamLog, self.teamLastTime, event)
        elif event.dataType == "Skill":
            if event.id in ["14660", "14665"]:  # 微潮/零落
                self.teamLog, self.teamLastTime = countCluster(self.teamLog, self.teamLastTime, event)

    def initTeamDetect(self):
        '''
        小队聚类初始化.
        用于推测哪些队友处于一个小队，出现在奶花和奶歌的复盘中.
        '''
        self.teamLog = {}  # 小队聚类数量统计
        self.teamLastTime = {}  # 小队聚类时间
        for line in self.bld.info.player:
            self.teamLog[line] = {}
            self.teamLastTime[line] = 0

    def completeSecondState(self):
        '''
        第二阶段扫描完成后的公共流程.
        '''
        ss = self.ss
        bh = self.bh
        # 记录最后一个技能
        if ss.skill != "0":
            index = self.gcdSkillIndex[ss.skill]
            line = self.skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal, ss.damage, ss.damageEff,
                              roundCent(safe_divide(ss.healEff, ss.heal)),
                              int(safe_divide(ss.delay, ss.delayNum)), ss.busy, "")

        if self.gcdChannel:
            _, pulse, limit = self.gcdChannel
            line = self.skillInfo[self.gcdSkillIndex[pulse]]
            period = getLength(line[5], self.haste if line[7] else 0)
            self.channelCasts = self.gcdChannelLog.groups(
                self.startTime, self.finalTime, period,
                immediate=self.gcdChannelImmediate, ticks_per_cast=limit,
                marked_tick_limit=getattr(self, "gcdChannelMarkedTicks", 0))
            for cast in self.channelCasts:
                bh.setNormalSkill(pulse, line[1], line[3], cast.start, cast.end - cast.start,
                                  int(not cast.partial), cast.heal, cast.healeff, cast.damage, cast.damageeff)
                bh.log["normal"][-1]["ticks"] = len(cast.ticks)
                if cast.partial:
                    bh.log["normal"][-1]["partial"] = True
            bh.log["normal"].sort(key=lambda action: action["start"])

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]
            bh.badPeriodDpsLog = self.bossBh.badPeriodDpsLog
            bh.badPeriodHealerLog = self.bossBh.badPeriodHealerLog

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0, "chpsDescription": self.bossBh.critPeriodDesc, "chpsDuration": self.bossBh.critPeriodSum}

        self.myHealStat = {}
        for player in self.act.rhps["player"]:
            if player in self.healerDict:
                self.result["healer"]["numHealer"] += 1
                res = {"rhps": int(self.act.getRhps(player)),
                       "rdps": int(self.act.getRdps(player)),
                       "ndps": int(self.act.getRdps(player, "ndps")),
                       "mrdps": int(self.act.getRdps(player, "mrdps")),
                       "mndps": int(self.act.getRdps(player, "mndps")),
                       "name": self.act.rhps["player"][player]["name"],
                       "occ": self.bld.info.player[player].occ}
                if player in self.act.hps["player"]:
                    res["hps"] = int(self.act.hps["player"][player]["hps"])
                else:
                    res["hps"] = 0
                if player in self.act.ahps["player"]:
                    res["ahps"] = int(self.act.ahps["player"][player]["hps"])
                else:
                    res["ahps"] = 0
                if player in self.act.ohps["player"]:
                    res["ohps"] = int(self.act.ohps["player"][player]["hps"])
                else:
                    res["ohps"] = 0
                if player in self.act.chps["player"]:
                    res["chps"] = int(self.act.chps["player"][player]["hps"])
                else:
                    res["chps"] = 0
                res["heal"] = res.get("ohps", 0)
                res["healEff"] = res.get("hps", 0)
                if player == self.mykey:
                    self.myHealStat = res
                self.result["healer"]["table"].append(res)
        self.result["healer"]["table"].sort(key=lambda x: -x["rhps"])

    def handleGcdSkill(self, event):
        '''
        处理gcd技能, 这是第二阶段主循环的子功能.
        params:
        - event: 处理的事件.
        '''
        ss = self.ss
        bh = self.bh
        ss.initSkill(event)
        index = self.gcdSkillIndex[event.id]
        line = self.skillInfo[index]
        castTime = line[5]
        skip = 0
        target = ""

        if self.occ == "butianjue":
            # 奶毒特殊判定
            if event.id in ["2526", "27391", "6662"]:
                # 检查冰蚕诀
                sf = self.cyDict.checkState(event.time - 200)
                if sf:
                    castTime = 0
                    if self.bh.log["normal"] == [] or self.bh.log["normal"][-1]["skillname"] != "冰蚕牵丝" or event.time - \
                            self.bh.log["normal"][-1]["start"] - self.bh.log["normal"][-1]["duration"] > -100:
                        self.instantNum += 1
                        # print("[CanyinTrigger] success", self.instantNum)
                    else:
                        pass
                        # print("[CanyinTrigger] fail", self.instantNum)
                        # print(self.bh.log["normal"][-1]["skillname"], self.bh.log["normal"][-1]["start"], self.bh.log["normal"][-1]["duration"], event.time)

                else:
                    pass
                    # print("[CanyinTrigger] not detected", self.instantNum)
            if event.id in ["2965"]:
                # 检查碧蝶引
                skip = self.xjDict.checkState(event.time - 200)
                if skip:
                    self.bh.setSpecialSkill(event.id, 0, 0, event.time, 0, "瞬发碧蝶引")
        elif self.occ == "lijingyidao":
            # 奶花特殊判定
            sfFlag = 0
            sf = 0
            if event.id in ["22792", "22886", "3038", "26666", "26667", "26668"]:
                # 检查水月
                sf = self.shuiyueDict.checkState(event.time - 200)
                if sf:
                    sfFlag = 1
            if not sfFlag and event.id in ["3038"]:
                # 检查行气血
                sf2 = self.xqxDict.checkState(event.time - 200)
                if sf2:
                    sfFlag = 1
            if not sfFlag and event.id in ["3038", "26666", "26667", "26668"]:
                # 检查cw
                sf3 = self.cwDict.checkState(event.time - 200)
                if sf3:
                    sfFlag = 1
            if sf and sfFlag:  # 使用水月瞬发
                if event.time - self.lastInstant > 100:
                    self.instantNum += 1
                self.lastInstant = event.time
                if event.id in ["3038"]:
                    self.instantChangzhenNum += 1
            if event.id == "3038" and not sfFlag:  # 用推测的墨意来调整长针的瞬发状态
                lastMoyi = self.moyiInfer[-1][1]
                if lastMoyi > 20:
                    sfFlag = 1
            if sfFlag:  # 瞬发修改技能
                castTime = 0
                # 消耗墨意推测
                lastMoyi = self.moyiInfer[-1][1]
                nowMoyi = lastMoyi - 20
                if nowMoyi < 0:
                    nowMoyi = 0
                if lastMoyi > nowMoyi:
                    self.usedMoyi += lastMoyi - nowMoyi
                self.moyiInfer.append([event.time, nowMoyi])
            if event.id in ["101", "3038", "26666", "26667", "26668"]:
                target = event.target
            if event.id in ["22792", "22886"]:  # 提针
                # print("[Tizhen]", event.time, event.id, event.heal, event.healEff, self.moyiInfer[-1])
                # 获得墨意推测
                lastMoyi = self.moyiInfer[-1][1]
                maxMoyi = 60
                nowMoyi = lastMoyi + 10
                if sf:
                    maxMoyi = 100
                    nowMoyi += 7
                if nowMoyi > maxMoyi:
                    self.wastedMoyi += nowMoyi - maxMoyi
                    nowMoyi = maxMoyi
                self.moyiInfer.append([event.time, nowMoyi])
        elif self.occ == "xiangzhi":
            # 暗香的特殊判断
            if event.id == "14231" and event.target in self.anxiangTimeDict:
                # 滚动
                while self.anxiangTimeIndex[event.target] < len(self.anxiangTimeDict[event.target]) and \
                        self.anxiangTimeDict[event.target][self.anxiangTimeIndex[event.target]] + 50 < event.time:
                    self.anxiangTimeIndex[event.target] += 1
                # 判断是否在暗香刷盾的时间点附近，如果是就跳过
                if self.anxiangTimeIndex[event.target] < len(self.anxiangTimeDict[event.target]) and \
                        abs(event.time - self.anxiangTimeDict[event.target][self.anxiangTimeIndex[event.target]]) < 100:
                    skip = 1
        if not skip:
            ss.analyseSkill(event, castTime, line[0], tunnel=line[6], hasteAffected=line[7])
            if self.gcdChannel and index == self.gcdSkillIndex[self.gcdChannel[1]]:
                self.gcdChannelLog.tick(event.time, event.heal, event.healEff, event.damage,
                                        event.damageEff, frame=getattr(event, "frame", None))
                self.lastNormalImpact = None
                ss.reset()
                return
            targetName = "Unknown"
            if event.target in self.bld.info.player:
                targetName = self.bld.info.player[event.target].name
            elif event.target in self.bld.info.npc:
                targetName = self.bld.info.getName(event.target)
            lastSkillID, _ = bh.getLastNormalSkill()
            frame = getattr(event, "frame", None)
            sameImpact = self.lastNormalImpact is not None and (
                0 <= event.time - self.lastNormalImpact < 100 or
                (frame is not None and frame == self.lastNormalFrame))
            if (sameImpact and self.gcdSkillIndex.get(lastSkillID) == index
                    and event.target not in self.normalTargets):
                # 一次群疗命中多个目标，只累加治疗量。
                bh.updateNormalSkill(ss.skill, line[1], line[3],
                                     ss.timeStart, ss.timeEnd - ss.timeStart, 0, ss.heal,
                                     ss.healEff, ss.damage, ss.damageEff, 0, ss.busy, "", target, targetName)
            else:
                self.lastNormalImpact = event.time
                self.lastNormalFrame = frame
                self.normalTargets = set()
                bh.setNormalSkill(ss.skill, line[1], line[3],
                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                  ss.healEff, ss.damage, ss.damageEff, 0, ss.busy, "", target, targetName)
            self.normalTargets.add(event.target)
            ss.reset()

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
                # 打印所有有治疗量的技能，以进行整理
                # print("[Heal]", event.id, event.heal)
                pass

            if event.caster == self.mykey and event.scheme == 1:
                if event.id in self.gcdChannelShells:
                    self.gcdChannelLog.cast(event.time, shell=True, frame=getattr(event, "frame", None))
                # 根据技能表进行自动处理
                if event.id in self.gcdSkillIndex:
                    self.handleGcdSkill(event)
                # 处理特殊技能
                elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                    pass
                # 无法分析的技能，或者统计被隐藏的治疗量
                # elif event.id not in self.unimportantSkill and event.heal != 0:
                #     print("[NonRec]", event.id, event.time, self.bld.info.getSkillName(event.full_id), event.healEff,
                #           self.bld.info.getName(event.caster), self.bld.info.getName(event.target))

        elif event.dataType == "Cast" and event.caster == self.mykey:
            self.lastNormalImpact = None
            if self.gcdChannel and event.id in self.gcdChannel[0]:
                self.gcdChannelLog.cast(event.time, frame=getattr(event, "frame", None))
        elif event.dataType == "Buff":
            if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1 and event.target == self.mykey:  # 特效腰坠:
                self.bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                   event.time, 0, "开启特效腰坠")
                self.yzSkill.recordSkill(event.time, 0, 0, self.ss.timeEnd, delta=-1)
            if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                self.mufengDict.setState(event.time, event.stack)


    def initSecondState(self):
        '''
        第二阶段初始化.
        '''
        self.numPurge = 0  # 驱散次数
        self.battleTimeDict = {}  # 进战时间
        self.sumPlayer = 0  # 平均玩家数

        # 技能初始化
        # self.allSkillObjs = []
        self.gcdSkillIndex = {}
        self.nonGcdSkillIndex = {}
        for i in range(len(self.skillInfo)):
            line = self.skillInfo[i]
            if line[0] is None:
                self.skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste, exclude=self.bossBh.badPeriodHealerLog)
                # self.allSkillObjs.append(self.skillInfo[i][0])
            for id in line[2]:
                if line[4]:
                    self.gcdSkillIndex[id] = i
                else:
                    self.nonGcdSkillIndex[id] = i

        self.yzSkill = self.skillInfo[self.nonGcdSkillIndex["yaozhui"]][0]
        self.mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风
        # self.allSkillObjs.append(self.yzSkill)

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
                               "33613",  # 治疗腰带附魔
                            ]

        # 战斗回放初始化
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.ss = SingleSkill(self.startTime, self.haste)
        self.lastNormalImpact = None
        self.lastNormalFrame = None
        self.normalTargets = set()
        if self.gcdChannel:
            self.gcdChannelLog = HealingChannel()

        # self.excludePosHealer = 0
        # self.badPeriodHealerLog = self.bossBh.badPeriodHealerLog
        # self.excludeStatusHealer = 0

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
        self.result["overall"]["calTank"] = self.config.item["xiangzhi"]["caltank"]
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
        # if self.bld.info.player[self.mykey].equip != {} and "beta" not in EDITION:
            # TODO 验证
            self.result["equip"]["available"] = 1
            # ea = EquipmentAnalyser()
            # jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            # eee = ExcelExportEquipment()
            # strEquip = eee.export(jsonEquip)
            jsonEquip = self.jsonEquip[self.mykey]
            strEquip = self.strEquip[self.mykey]
            # res = adr.Display(strEquip, self.occCode)
            # self.result["equip"]["score"] = int(self.bld.info.player[self.mykey].equipScore)
            # self.result["equip"]["sketch"] = jsonEquip["sketch"]
            # self.result["equip"]["forge"] = jsonEquip["forge"]
            # self.result["equip"]["spirit"] = res["根骨"]
            # self.result["equip"]["heal"] = res["治疗"]
            # self.result["equip"]["healBase"] = res["基础治疗"]
            # self.result["equip"]["critPercent"] = res["会心"]
            # self.result["equip"]["crit"] = res["会心等级"]
            # self.result["equip"]["critpowPercent"] = res["会效"]
            # self.result["equip"]["critpow"] = res["会效等级"]
            # self.result["equip"]["hastePercent"] = res["加速"]
            # self.result["equip"]["haste"] = res["加速等级"]
            # if not self.config.item["xiangzhi"]["speedforce"]:
            #     self.haste = self.result["equip"]["haste"]
            # self.result["equip"]["raw"] = strEquip
            res = self.equip[self.mykey]
            self.result["equip"]["score"] = str(jsonEquip.get("score", 0))  # int(self.bld.info.player[self.mykey].equipScore)
            if jsonEquip.get("cached", 0) == 1:
                self.result["equip"]["score"] += "*"
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res.get("根骨", 0)
            self.result["equip"]["heal"] = res.get("治疗", 0)
            self.result["equip"]["healBase"] = res.get("基础治疗", 0)
            self.result["equip"]["critPercent"] = parseCent(res.get("会心", 0)) + "%"
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = parseCent(res.get("会效", 0)) + "%"
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["hastePercent"] = parseCent(res.get("加速", 0)) + "%"
            self.result["equip"]["haste"] = res["加速等级"]
            if not self.config.item["xiangzhi"]["speedforce"]:
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

        self.result["overall"]["hasteReal"] = self.haste


    def eventInFirstState(self, event):
        '''
        第一阶段处理事件的公共流程.
        params:
        - event: 处理的事件.
        '''

        if event.dataType == "Skill":
            # 记录治疗心法的出现情况.
            if event.caster not in self.healerDict and event.id in ["14231", "14140", "14301", "565", "554", "555", "2232",
                                                                    "6662", "2233", "6675",
                                                                    "2231", "101", "142", "138", "16852", "18864", "27621",
                                                                    "27623", "28083"]:  # 治疗的特征技能
                self.healerDict[event.caster] = 0

            if event.caster in self.occDetailList and self.occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                                 '21', '22', '212']:
                self.occDetailList[event.caster] = checkOccDetailBySkill(self.occDetailList[event.caster], event.id, event.damageEff)

        elif event.dataType == "Buff":
            if event.id in ["15774", "17200"]:  # buff精神匮乏
                if event.target not in self.jianLiaoLog:
                    self.jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                self.jianLiaoLog[event.target].setState(event.time, event.stack)
            if event.caster in self.occDetailList and self.occDetailList[event.caster] in ['21']:
                self.occDetailList[event.caster] = checkOccDetailByBuff(self.occDetailList[event.caster], event.id)

        elif event.dataType == "Shout":
            # 为未来需要统计喊话时备用.
            pass

    def initFirstState(self):
        '''
        第一阶段初始化.
        '''

        self.getOverallInfo()

        # 记录盾的存在情况与减疗
        self.jianLiaoLog = {}

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.
        self.interrupt = 0

        # 记录战斗开始时间与结束时间
        if self.startTime == 0:
            self.startTime = self.bld.log[0].time
        if self.finalTime == 0:
            self.finalTime = self.bld.log[-1].time

        # 如果时间被大幅度修剪过，则修正战斗时间
        if abs(self.finalTime - self.startTime - self.result["overall"]["sumTime"]) > 6000:
            actualTime = self.finalTime - self.startTime
            self.result["overall"]["sumTime"] = actualTime
            self.result["overall"]["sumTimePrint"] = parseTime(actualTime / 1000)

        # 记录所有治疗的key，首先尝试直接使用心法列表获取.
        self.healerDict = {}

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
        第一阶段复盘. 需要子类实现.
        '''
        pass

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘. 需要子类实现.
        '''
        pass

    def replay(self):
        '''
        开始复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", actorData={}):
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
        self.myname = myname

# Created by moeheart at 08/08/2021
# 治疗复盘的通用方法。尝试将共享的部分尽可能提取。

from replayer.ReplayerBase import ReplayerBase

from replayer.BattleHistory import BattleHistory, SingleSkill
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *

import time

class HealerReplay(ReplayerBase):

    def calculateSkillInfoDirect(self, name, skillObj):
        '''
        根据技能名和对象统计对应技能的基本信息.
        注意更复杂的信息依然需要在派生类中手动统计.
        params:
        - name: 技能的简称. 会存储在result中.
        - skillObj: skillInfo中定义的技能对象.
        returns:
        - skillObj: 查找到的技能对象，用于进一步的手动统计.
        '''
        self.result["skill"][name] = {}
        self.result["skill"][name]["num"] = skillObj.getNum()
        self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
        effHeal = skillObj.getHealEff()
        self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"][name]["effRate"] = roundCent(effHeal / (skillObj.getHeal() + 1e-10))

    def calculateSkillInfo(self, name, id):
        '''
        根据技能名和ID统计对应技能的基本信息.
        注意更复杂的信息依然需要在派生类中手动统计.
        params:
        - name: 技能的简称. 会存储在result中.
        - id: 技能的ID，用于在skillInfo中查找.
        returns:
        - skillObj: 查找到的技能对象，用于进一步的手动统计.
        '''
        skillObj = self.skillInfo[self.gcdSkillIndex[id]][0]
        self.result["skill"][name] = {}
        self.result["skill"][name]["num"] = skillObj.getNum()
        self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
        effHeal = skillObj.getHealEff()
        self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"][name]["effRate"] = roundCent(effHeal / (skillObj.getHeal() + 1e-10))

    def calculateSkillFinal(self):
        '''
        第二阶段结束时最后计算评分的部分.
        '''

        # 排序
        self.result["review"]["content"].sort(key=lambda x: -x["status"] * 1000 + x["rate"])
        num = 0
        for line in self.result["review"]["content"]:
            if line["status"] > 0:
                num += 1
                self.reviewScore -= [0, 1, 3, 10][line["status"]]
        self.result["review"]["num"] = num
        if self.reviewScore < 0:
            self.reviewScore = 0
        self.result["review"]["score"] = self.reviewScore
        self.result["skill"]["general"]["score"] = self.reviewScore


    def calculateSkillOverall(self):
        '''
        第二阶段结束时共有的技能统计部分.
        '''
        self.result["skill"]["mufeng"] = {}
        num = self.battleTimeDict[self.mykey]
        sum = self.mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["general"]["efficiency"] = self.bh.getNormalEfficiency()

        # 统计治疗相关
        self.result["skill"]["healer"] = {}
        self.result["skill"]["healer"]["heal"] = self.myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["healEff"] = self.myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["ohps"] = self.myHealStat.get("ohps", 0)
        self.result["skill"]["healer"]["hps"] = self.myHealStat.get("hps", 0)
        self.result["skill"]["healer"]["rhps"] = self.myHealStat.get("rhps", 0)
        self.result["skill"]["healer"]["ahps"] = self.myHealStat.get("ahps", 0)

        self.getRankFromStat(self.occ)
        self.result["rank"] = self.rank
        sumWeight = 0
        sumScore = 0
        for key1 in self.result["rank"]:
            for key2 in self.result["rank"][key1]:
                key = "%s-%s" % (key1, key2)
                weight = 1
                if key in self.specialKey:
                    weight = self.specialKey[key]
                sumScore += self.result["rank"][key1][key2]["percent"] * weight
                sumWeight += weight

        self.reviewScore = roundCent((sumScore / sumWeight) ** 0.5 * 10, 2)


        # 计算专案组的公有部分.

        self.result["review"] = {"available": 1, "content": []}

        # code 1 不要死
        num = self.deathDict[self.mykey]["num"]
        if num > 0:
            time = roundCent(((self.finalTime - self.startTime) - self.battleDict[self.mykey].buffTimeIntegral()) / 1000, 2)
            self.result["review"]["content"].append({"code": 1, "num": num, "duration": time, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 1, "num": num, "duration": 0, "rate": 1, "status": 0})

        # code 10 不要放生队友
        num = 0
        log = []
        time = []
        id = []
        damage = []
        for key in self.unusualDeathDict:
            if self.unusualDeathDict[key]["num"] > 0:
                for line in self.unusualDeathDict[key]["log"]:
                    num += 1
                    log.append([(int(line[0]) - self.startTime) / 1000, self.bld.info.player[key].name, "%s:%d/%d" % (line[1], line[2], line[6])])
        log.sort(key=lambda x: x[0])
        for line in log:
            time.append(parseTime(line[0]))
            id.append(line[1])
            damage.append(line[2])
        if num > 0:
            self.result["review"]["content"].append({"code": 10, "num": num, "time": time, "id": id, "damage": damage, "rate": 0, "status": 3})
        else:
            self.result["review"]["content"].append({"code": 10, "num": num, "time": time, "id": id, "damage": damage, "rate": 1, "status": 0})

        # code 11 保持gcd不要空转
        gcd = self.result["skill"]["general"]["efficiency"]
        gcdRank = self.result["rank"]["general"]["efficiency"]["percent"]
        res = {"code": 11, "cover": gcd, "rank": gcdRank, "rate": roundCent(gcdRank / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 12 提高HPS或者虚条HPS
        hps = 0
        ohps = 0
        for record in self.result["healer"]["table"]:
            if record["name"] == self.result["overall"]["playerID"]:
                # 当前玩家
                hps = record["healEff"]
                ohps = record["heal"]
        hpsRank = self.result["rank"]["healer"]["healEff"]["percent"]
        ohpsRank = self.result["rank"]["healer"]["heal"]["percent"]
        rate = max(hpsRank, ohpsRank)
        res = {"code": 12, "hps": hps, "ohps": ohps, "hpsRank": hpsRank, "ohpsRank": ohpsRank, "rate": roundCent(rate / 100)}
        res["status"] = getRateStatus(res["rate"], 75, 50, 25)
        self.result["review"]["content"].append(res)

        # code 13 使用有cd的技能

        scCandidate = []
        for id in self.markedSkill:
            if id in self.nonGcdSkillIndex:
                scCandidate.append(self.skillInfo[self.nonGcdSkillIndex[id]][0])
            else:
                scCandidate.append(self.skillInfo[self.gcdSkillIndex[id]][0])
        scCandidate.append(self.yzSkill)
        for line in self.outstandingSkill:
            scCandidate.append(line)

        rateSum = 0
        rateNum = 0
        numAll = []
        sumAll = []
        skillAll = []
        for skillObj in scCandidate:
            num = skillObj.getNum()
            sum = skillObj.getMaxPossible()
            # if sum < num:
            #     sum = num
            skill = skillObj.name
            if skill in ["特效腰坠", "百药宣时", "青圃着尘", "余寒映日", "九微飞花", "折叶笼花", "大针"] and num == 0:
                continue
            rateNum += 1
            rateSum += min(num / (sum + 1e-10), 1)
            numAll.append(num)
            sumAll.append(sum)
            skillAll.append(skill)
        rate = roundCent(rateSum / (rateNum + 1e-10), 4)
        res = {"code": 13, "skill": skillAll, "num": numAll, "sum": sumAll, "rate": rate}
        res["status"] = getRateStatus(res["rate"], 50, 25, 0)
        self.result["review"]["content"].append(res)

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
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]
            bh.badPeriodDpsLog = self.bossBh.badPeriodDpsLog
            bh.badPeriodHealerLog = self.bossBh.badPeriodHealerLog

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0}

        self.myHealStat = {}
        for player in self.act.rhps["player"]:
            if player in self.healerDict:
                self.result["healer"]["numHealer"] += 1
                res = {"rhps": int(self.act.rhps["player"][player]["hps"]),
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

        # 奶毒特殊判定
        if self.occ == "butianjue":
            if event.id in ["2526", "27391", "6662"]:
                # 检查冰蚕诀
                sf = self.cyDict.checkState(event.time - 200)
                if sf:
                    castTime = 0
                    if self.bh.log["normal"] == [] or self.bh.log["normal"][-1]["skillname"] != "冰蚕牵丝" or event.time - \
                            self.bh.log["normal"][-1]["start"] - self.bh.log["normal"][-1]["duration"] > 100:
                        self.instantNum += 1
            if event.id in ["2965"]:
                # 检查碧蝶引
                skip = self.xjDict.checkState(event.time - 200)
                if skip:
                    self.bh.setSpecialSkill(event.id, 0, 0, event.time, 0, "瞬发碧蝶引")
        elif self.occ == "lijingyidao":
            sfFlag = 0
            if event.id in ["22792", "22886", "3038", "26666", "26667", "26668"]:
                # 检查水月
                sf = self.shuiyueDict.checkState(event.time - 200)
                if sf:
                    sfFlag = 1
            if not sfFlag and event.id in ["3038", "26666", "26667", "26668"]:
                # 检查行气血、cw
                sf2 = self.xqxDict.checkState(event.time - 200)
                sf3 = self.cwDict.checkState(event.time - 200)
                if sf2 or sf3:
                    sfFlag = 1
            if sfFlag:
                castTime = 0
                if event.time - self.lastInstant > 100:
                    self.instantNum += 1
                self.lastInstant = event.time
                if event.id in ["3038"]:
                    self.instantChangzhenNum += 1
            if event.id in ["101", "3038", "26666", "26667", "26668"]:
                target = event.target


        if not skip:
            ss.analyseSkill(event, castTime, line[0], tunnel=line[6], hasteAffected=line[7])
            targetName = "Unknown"
            if event.target in self.bld.info.player:
                targetName = self.bld.info.player[event.target].name
            elif event.target in self.bld.info.npc:
                targetName = self.bld.info.npc[event.target].name
            lastSkillID, lastTime = bh.getLastNormalSkill()
            if self.gcdSkillIndex[lastSkillID] == self.gcdSkillIndex[ss.skill] and ss.timeStart - lastTime < 100:
                # 相同技能，原地更新
                bh.updateNormalSkill(ss.skill, line[1], line[3],
                                     ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                     ss.healEff, 0, ss.busy, "", target, targetName)
            else:
                # 不同技能，新建条目
                bh.setNormalSkill(ss.skill, line[1], line[3],
                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                  ss.healEff, 0, ss.busy, "", target, targetName)
            ss.reset()

    def eventInSecondState(self, event):
        '''
        第二阶段处理事件的公共流程.
        params:
        - event: 处理的事件.
        '''

        if event.dataType == "Skill":
            # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
            if event.effect == 7:
                return
            # 统计自身技能使用情况.
            # if event.caster == self.mykey and event.scheme == 1 and event.id in self.unimportantSkill and event.heal != 0:
            #     print(event.id, event.time)

            if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey:
                # 打印所有有治疗量的技能，以进行整理
                # print("[Heal]", event.id, event.heal)
                pass

            if event.caster == self.mykey and event.scheme == 1:
                # 根据技能表进行自动处理
                if event.id in self.gcdSkillIndex:
                    self.handleGcdSkill(event)
                # 处理特殊技能
                elif event.id in self.nonGcdSkillIndex:  # 特殊技能
                    pass
                # 无法分析的技能
                elif event.id not in self.unimportantSkill:
                    pass
                    # print("[XiangzhiNonRec]", event.time, event.id, event.heal, event.healEff)

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
        self.gcdSkillIndex = {}
        self.nonGcdSkillIndex = {}
        for i in range(len(self.skillInfo)):
            line = self.skillInfo[i]
            if line[0] is None:
                self.skillInfo[i][0] = SkillCounterAdvance(line, self.startTime, self.finalTime, self.haste)
            for id in line[2]:
                if line[4]:
                    self.gcdSkillIndex[id] = i
                else:
                    self.nonGcdSkillIndex[id] = i

        self.yzSkill = self.skillInfo[self.nonGcdSkillIndex["yaozhui"]][0]
        self.mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风

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
                            ]

        # 战斗回放初始化
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.ss = SingleSkill(self.startTime, self.haste)


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
        if self.bld.info.player[self.mykey].equip != {} and "beta" not in EDITION:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, self.occCode)
            self.result["equip"]["score"] = int(self.bld.info.player[self.mykey].equipScore)
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res["根骨"]
            self.result["equip"]["heal"] = res["治疗"]
            self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["critPercent"] = res["会心"]
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = res["会效"]
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["hastePercent"] = res["加速"]
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
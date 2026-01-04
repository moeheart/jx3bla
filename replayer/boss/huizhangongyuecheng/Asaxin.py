# Created by moeheart at 09/25/2025
# 阿萨辛的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
import os

def parseBigNum(number):
    if int(number) == 0:
        return 0
    else:
        return str(int(int(number) / 10000)) + "w"

def getPercentColor(value, maxValue):
    num = 128 - int(safe_divide(value, maxValue) * 128)
    return getColorHex((num, num, num))

class AsaxinWindow(SpecificBossWindow):
    '''
    阿萨辛的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("阿萨辛", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()

        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("P1本体", "在P1对[阿萨辛]本体的伤害总量。\n阶段持续时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2本体", "在P2对[阿萨辛]本体的伤害总量。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("P2小怪", "在P2对[塔洛马蒂幻象]和[姬无双幻象]的伤害。注意无效伤害不会计入，对锁链的伤害也不计入。")
        tb.AppendHeader("P3本体", "在P3对[阿萨辛]本体的伤害总量。\n阶段持续时间：%s" % parseTime(self.detail["P3Time"]))
        tb.AppendHeader("P3小怪", "在P3对[戮之血影]、[灭之血影]、[伽巴尔锁链]的伤害。")
        tb.AppendHeader("眼睛1", "在P3对第1次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("眼睛2", "在P3对第2次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("眼睛3", "在P3对第3次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("眼睛4", "在P3对第4次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("眼睛5", "在P3对第5次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("眼睛6", "在P3对第6次激活的[阿里曼之眼]的伤害。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(parseBigNum(line["battle"]["P1BossDamage"]), color=getPercentColor(line["battle"]["P1BossDamage"], self.detail["maxP1BossDamage"]))
            tb.AppendContext(parseBigNum(line["battle"]["P2BossDamage"]), color=getPercentColor(line["battle"]["P2BossDamage"], self.detail["maxP2BossDamage"]))
            tb.AppendContext(parseBigNum(line["battle"]["P2AddEffective"]), color=getPercentColor(line["battle"]["P2AddEffective"], self.detail["maxP2AddEffective"]))
            tb.AppendContext(parseBigNum(line["battle"]["P3BossDamage"]), color=getPercentColor(line["battle"]["P3BossDamage"], self.detail["maxP3BossDamage"]))
            tb.AppendContext(parseBigNum(line["battle"]["P3AddEffective"]), color=getPercentColor(line["battle"]["P3AddEffective"], self.detail["maxP3AddEffective"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye1Damage"]), color=getPercentColor(line["battle"]["Eye1Damage"], self.detail["maxEye1Damage"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye2Damage"]), color=getPercentColor(line["battle"]["Eye2Damage"], self.detail["maxEye2Damage"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye3Damage"]), color=getPercentColor(line["battle"]["Eye3Damage"], self.detail["maxEye3Damage"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye4Damage"]), color=getPercentColor(line["battle"]["Eye4Damage"], self.detail["maxEye4Damage"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye5Damage"]), color=getPercentColor(line["battle"]["Eye5Damage"], self.detail["maxEye5Damage"]))
            tb.AppendContext(parseBigNum(line["battle"]["Eye6Damage"]), color=getPercentColor(line["battle"]["Eye6Damage"], self.detail["maxEye6Damage"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])

            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)


class AsaxinReplayer(SpecificReplayerPro):

    def triviaWrite(self, type, id, time, content):
        '''
        向文件中写内容
        '''
        if self.config.item["general"]["trivia"]:
            eventTime = (time - self.startTime + self.timeDelay) / 1000
            self.triviaFile.write("%s %s %.1f %s\n" % (type, self.bld.info.getName(id), eventTime, content))

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()
        # print(self.bh.log)

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)
        self.detail["P3Time"] = int(self.phaseTime[3] / 1000)

        # 结算所有玩家对P2NPC的伤害
        for player in self.p2info:
            for npc in self.p2info[player]["damage"]:
                self.statDict[player]["battle"]["P2AddEffective"] += self.p2info[player]["damage"][npc]

        # 第一部分：战斗时间和死亡事件
        # totalTime = (self.finalTime - self.startTime + self.timeDelay) / 1000
        # self.triviaFile.write("Totaltime %.1f\n" % totalTime)
        self.triviaWrite("Totaltime", "0", self.finalTime, "")

        for player in self.statDict:
            damageStr = str(self.statDict[player]["battle"])
            self.triviaWrite("Statistics", player, self.finalTime, damageStr)

        if self.config.item["general"]["trivia"]:
            self.triviaFile.close()

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                res = self.getBaseList(id)
                for key in res["battle"]:
                    fullkey = "max" + key
                    if fullkey not in self.detail:
                        self.detail[fullkey] = res["battle"][key]
                    else:
                        self.detail[fullkey] = max(self.detail[fullkey], res["battle"][key])
                bossResult.append(res)
        self.statList = bossResult


        return self.statList, self.potList, self.detail, self.stunCounter

    def recordDeath(self, item, deathSource):
        '''
        在有玩家重伤时的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        - deathSource 重伤来源。
        '''
        pass

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

        self.checkTimer(event.time)

        # 检查血泉渡
        toRemove = []
        for player in self.drujRecord:
            if event.time - self.drujRecord[player] > 10000:
                self.triviaWrite("DrujFail", player, event.time, "")
                toRemove.append(player)
        for line in toRemove:
            del self.drujRecord[line]

        # 检查巴赫曼誓约
        if (self.p2Bahman != 0 and event.time - self.p2Bahman > 1500) or (self.phase == 3 and self.p3check == 0):
            if self.phase == 3:
                self.p3check = 1
            # 如果有仍在激活的小怪，将其数值设置为0
            for npc in self.p2npc:
                if self.p2npc[npc]["status"] != 0:
                    self.p2npc[npc]["status"] = 1
                    self.p2npc[npc]["startCast"] = 0
                    for player in self.p2info:
                        self.statDict[player]["battle"]["GarbageDamage"] += self.p2info[player]["damage"].get(npc, 0)
                        self.p2info[player]["damage"][npc] = 0
                        self.p2info[player]["history"][npc] = []
            self.p2Bahman = 0

        # 检查有没有未结算的NPC
        for npc in self.p2npc:
            if self.p2npc[npc]["status"] == 1 and self.p2npc[npc]["startCast"] != 0 and event.time - self.p2npc[npc]["startCast"] > 3000:
                # print("error:")
                # print(time)
                # print(npc)
                # print(self.p2npc)
                timeStr = parseTime((event.time - self.startTime) / 1000)
                npcStr = "蛇"
                if self.p2npc[npc]["templateID"] == "134734":
                    npcStr = "人"
                colorStr = "红"
                if self.p2npc[npc]["sex"] < 0:
                    colorStr = "蓝"
                # 判定这个NPC打快
                for player in self.p2info:
                    if npc in self.p2info[player]["damage"]:
                        history = []
                        for i in range(len(self.p2info[player]["history"][npc])-1, max(len(self.p2info[player]["history"][npc])-21, -1), -1):
                            history.append(self.p2info[player]["history"][npc][i][0])
                        # totalDamage = 0
                        # for line in self.p2info[player]["history"][npc]:
                        #     if event.time - line[1] < 5000:
                        #         totalDamage += line[2]
                        totalDamage = self.p2info[player]["damage"][npc]
                        # print("player:" + player)
                        # print(totalDamage)
                        # print(history)
                        if totalDamage > 0:
                            self.addPot([self.bld.info.getName(player),
                                         self.bld.info.getOcc(player),
                                         0,
                                         self.bossNamePrint,
                                         "%s%s%s打慢，总伤害：%d" % (timeStr, colorStr, npcStr, totalDamage),
                                         history,
                                         0])

                # 找到同场地的NPC
                dualNPC = ""
                for npc2 in self.p2npc:
                    if self.p2npc[npc2]["status"] == 1 and self.p2npc[npc2]["sex"] * self.p2npc[npc]["sex"] > 0 and npc2 != npc:
                        dualNPC = npc2
                        break

                # print("findDual", npc, dualNPC)

                if dualNPC != "":
                    npcStr = "蛇"
                    if self.p2npc[dualNPC]["templateID"] == "134734":
                        npcStr = "人"
                    # 判定这个NPC打慢
                    for player in self.p2info:
                        if dualNPC in self.p2info[player]["damage"]:
                            history = []
                            for i in range(len(self.p2info[player]["history"][dualNPC])-1, max(len(self.p2info[player]["history"][dualNPC])-21, -1), -1):
                                history.append(self.p2info[player]["history"][dualNPC][i][0])
                            totalDamage = 0
                            for line in self.p2info[player]["history"][dualNPC]:
                                if event.time - line[1] < 6000:
                                    totalDamage += line[2]
                            if totalDamage > 0:
                                self.addPot([self.bld.info.getName(player),
                                             self.bld.info.getOcc(player),
                                             0,
                                             self.bossNamePrint,
                                             "%s%s%s打快，最后3秒伤害：%d" % (timeStr, colorStr, npcStr, totalDamage),
                                             history,
                                             0])
                    self.p2npc[dualNPC]["status"] = 2

                self.p2npc[npc]["status"] = 2
                self.p2npc[npc]["startCast"] = 0

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                if event.caster in self.bld.info.npc and event.heal == 0 and event.scheme == 1:
                    # 尝试记录技能事件
                    name = "s%s" % event.id
                    if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                        self.bhTime[name] = event.time
                        skillName = self.bld.info.getSkillName(event.full_id)
                        if "," not in skillName:
                            key = "s%s" % event.id
                            if key in self.bhInfo or self.debug:
                                self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家",
                                                       "skill")

                if event.id == "42626":  # 阴阳二元阵
                    if self.bld.info.getName(event.caster) in ["阳阵", "陽陣"]:
                        self.sexCal[event.target] += 1
                    elif self.bld.info.getName(event.caster) in ["阴阵", "陰陣"]:
                        self.sexCal[event.target] -= 1

                if event.id == "42602":  # 真理圣炎斩
                    # eventTime = (event.time - self.startTime + self.timeDelay) / 1000
                    # self.triviaFile.write("Semicircle %s %.1f\n" % (self.bld.info.getName(event.target), eventTime))
                    self.triviaWrite("Semicircle", event.target, event.time, "")

                if event.id == "42633":  # 原罪缚穴术
                    # eventTime = (event.time - self.startTime + self.timeDelay) / 1000
                    # self.triviaFile.write("Jump %s %.1f\n" % (self.bld.info.getName(event.target), eventTime))
                    self.triviaWrite("Jump", event.target, event.time, "")

                if event.id == "42961":  # 血泉渡单体击飞
                    self.triviaWrite("Druj", event.target, event.time, "")
                    self.drujRecord[event.target] = event.time

                if event.id == "42963":  # 倾泻之欲
                    if self.aesmaPlayer != "":
                        self.triviaWrite("AesmaFail", self.aesmaPlayer, event.time, "")
                        self.aesmaPlayer = ""

                if event.id == "42964":  # 狂放之气
                    if self.tarumatPlayer != "":
                        self.triviaWrite("TarumatFail", self.tarumatPlayer, event.time, "")
                        self.tarumatPlayer = ""

                if event.id == "42975":  # 狂妄之击
                    self.tarumatHit = 1

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["阿萨辛"]:
                            self.bh.setMainTarget(event.target)
                            if self.phase == 1:
                                self.statDict[event.caster]["battle"]["P1BossDamage"] += event.damageEff
                            elif self.phase == 2:
                                self.statDict[event.caster]["battle"]["P2BossDamage"] += event.damageEff
                            elif self.phase == 3:
                                self.statDict[event.caster]["battle"]["P3BossDamage"] += event.damageEff
                        elif self.bld.info.getName(event.target) in ["阿里曼之眼"] and self.eyeActiveNum in [1,2,3,4,5,6]:
                            self.statDict[event.caster]["battle"]["Eye%dDamage" % self.eyeActiveNum] += event.damageEff
                        else:
                            # if self.phase == 2:
                            #     self.statDict[event.caster]["battle"]["P2AddEffective"] += event.damageEff
                            if self.phase == 3:
                                self.statDict[event.caster]["battle"]["P3AddEffective"] += event.damageEff

                        # 计算伤害
                        if self.bld.info.npc[event.target].templateID in ["134733", "134734"]:
                            if event.target not in self.p2npc:
                                self.p2npc[event.target] = {"status": 1, "sex": 0, "templateID": self.bld.info.npc[event.target].templateID, "startCast": 0}
                            self.p2npc[event.target]["sex"] += self.sexCal[event.caster]

                            # 累计伤害数值
                            if event.target not in self.p2info[event.caster]["damage"]:
                                self.p2info[event.caster]["damage"][event.target] = 0
                                self.p2info[event.caster]["history"][event.target] = []
                            self.p2info[event.caster]["damage"][event.target] += event.damageEff

                            # 记录伤害事件
                            if event.damageEff > 0:
                                timeStr = parseTime((event.time - self.startTime) / 1000)
                                skillNameStr = self.bld.info.getSkillName(event.full_id)
                                effectStr = ""
                                if event.effect > 0 and event.effect <= 7:
                                    effectStr = ["", "(招架)", "(免疫)", "(偏离)", "(闪避)", "(会心)", "(识破)", "(化解)"][
                                        event.effect]
                                self.p2info[event.caster]["history"][event.target].append(["%s,%s%s:%d" % (timeStr, skillNameStr, effectStr, event.damageEff), event.time, event.damageEff])
                            while len(self.p2info[event.caster]["history"][event.target]) >= 20 and event.time - self.p2info[event.caster]["history"][event.target][0][1] > 6000:
                                del self.p2info[event.caster]["history"][event.target][0]

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 5000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

            if event.id == "32181" and event.stack == 1:  # 达埃瓦献祭
                # eventTime = (event.time - self.startTime + self.timeDelay) / 1000
                # self.triviaFile.write("Semicircle %s %.1f\n" % (self.bld.info.getName(event.target), eventTime))
                self.triviaWrite("Daeva", event.target, event.time, "")

            if event.id == "32636" and event.stack == 1 and self.killAppear == 0:  # 戮影注视
                self.killAppear = 1
                self.triviaWrite("AkaManah", event.target, event.time, "")

            if event.id == "32103" and event.stack == 0:  # 血凝
                if event.target in self.drujRecord:
                    del self.drujRecord[event.target]

            if event.id == "32104" and event.stack == 10 and self.aesmaAppear == 0:  # 倾泻之欲
                self.aesmaAppear = 1
                self.aesmaPlayer = event.target
                self.triviaWrite("Aesma", event.target, event.time, "")

            if event.id == "32263" and event.stack == 1 and self.tarumatAppear == 0:  # 傲气
                self.tarumatAppear = 1
                self.tarumatPlayer = event.target
                self.triviaWrite("Tarumat", event.target, event.time, "")

            # if event.id == "28050":  # 红宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28050", "红宝石", "2654", event.time, 5000, event.target, "红宝石点名")
            #
            # if event.id == "28052":  # 蓝宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28052", "蓝宝石", "2653", event.time, 5000, event.target, "蓝宝石点名")
            #
            # if event.id == "28054":  # 绿宝石
            #     if event.stack == 1:
            #         self.bh.setCall("28054", "绿宝石", "2652", event.time, 5000, event.target, "绿宝石点名")

        elif event.dataType == "Shout":
            if event.content in ['"迷途的羔羊……摆脱伪神的蛊惑吧！"', '"迷途的羔羊……擺脫偽神的蠱惑吧！"']:
                self.bh.setBadPeriod(self.startTime, event.time - 1000, True, True)
                self.timeDelay = 0 - (event.time - self.startTime)
            elif event.content in ['"不……不想死……叫……叫太医……"', '"不……不想死……叫……叫太醫……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setCritPeriod(self.cszzStart, event.time, False, True)
            elif event.content in ['"驱逐虚伪的迷雾，指引羔羊的明途！"', '"驅逐虛偽的迷霧，指引羔羊的明途！"']:
                pass
            elif event.content in ['"天理之刃！斩断这旧世的枷锁！"', '"天理之刃！斬斷這舊世的枷鎖！"']:
                pass
            elif event.content in ['"超越阴阳的裂痕，重铸永恒的灵魂！"', '"超越陰陽的裂痕，重鑄永恆的靈魂！"']:
                pass
            elif event.content in ['"圣火焚尽皮囊，真理自现光芒！"', '"聖火焚儘皮囊，真理自現光芒！"']:
                pass
            elif event.content in ['"吾之圣谕，尔之涤罪！"', '"吾之聖諭，爾之滌罪！"']:
                self.changePhase(event.time,0)
                self.changePhase(event.time + 19000, 2)
                self.bh.setBadPeriod(event.time, event.time + 19000, True, False)
                self.timeDelay = 190000 - (event.time - self.startTime)
            elif event.content in ['"尔等可知，灵魂本无阴阳！"', '"爾等可知，靈魂本無陰陽！"']:
                pass
            elif event.content in ['"吾神最忠实的信徒啊，在此浮现尔等的身影吧！"', '"吾神最忠實的信徒啊，在此浮現爾等的身影吧！"']:
                pass
            elif event.content in ['"燚日！燃尽狂徒的罪业！"', '"燚日！燃儘狂徒的罪業！"']:
                pass
            elif event.content in ['"棺月！倾泻愚者的悔恨！"', '"棺月！傾瀉愚者的悔恨！"']:
                pass
            elif event.content in ['"尔等的梦……已锈迹斑斑。"', '"爾等的夢……已鏽跡斑斑。"']:
                pass
            elif event.content in ['"啊……堕落的羔羊，可曾听见深渊中的悲鸣！"', '"啊……墮落的羔羊，可曾聽見深淵中的悲鳴！"']:
                self.changePhase(event.time,0)
                self.changePhase(event.time + 17000, 3)
                self.bh.setBadPeriod(event.time, event.time + 17000, True, False)
                self.timeDelay = 452000 - (event.time - self.startTime)
            elif event.content in ['"黑暗之神安哥拉……借汝神力供我驱策。"', '"黑暗之神安哥拉……藉汝神力供我驅策。"']:
                if event.time - self.eyeActiveTime > 10000:
                    self.eyeActiveTime = event.time
                    self.eyeActiveNum += 1
            elif event.content in ['"为黑暗献上生命吧！"', '"爲黑暗獻上生命吧！"']:
                pass
            elif event.content in ['"以黑暗主宰之名！显其兽血狂沸！阿卡玛纳！"', '"以黑暗主宰之名！顯其獸血狂沸！阿卡瑪納！"']:
                pass
            elif event.content in ['"以黑暗主宰之名！昭其异心孤寒！德鲁杰！"', '"以黑暗主宰之名！昭其異心孤寒！德魯傑！"']:
                pass
            elif event.content in ['"赐予尔等这黑暗之血！"', '"賜予爾等這黑暗之血！"']:
                pass
            elif event.content in ['"终焉将至……"', '"終焉將至……"']:
                pass
            elif event.content in ['"以黑暗主宰之名！灭其欲火升腾！阿埃什马！"', '"以黑暗主宰之名！滅其欲火昇騰！阿埃什馬！"']:
                pass
            elif event.content in ['"以黑暗主宰之名！逐其傲气纵横！塔鲁马特！"', '"以黑暗主宰之名！逐其傲氣縱橫！塔魯馬特！"']:
                pass
            elif event.content in ['"这令人憎恶的光芒！"', '"這令人憎噁的光芒！"']:
                if self.tarumatHit == 0:
                    self.triviaWrite("TarumatPerfect", self.tarumatPlayer, event.time, "")
                self.aesmaAppear = 0
                self.tarumatAppear = 0
                self.aesmaPlayer = ""
                self.tarumatPlayer = ""
                self.tarumatHit = 0

            elif event.content in ['"黑暗君临……"', '"黑暗君臨……"']:
                pass
            elif event.content in ['"以黑暗主宰之名！浊其阴阳两极！图里兹！"', '"以黑暗主宰之名！濁其陰陽兩極！圖裡茲！"']:
                pass
            elif event.content in ['"以黑暗主宰之名！终其命运无常！阿斯托维扎图！"', '"以黑暗主宰之名！終其命運無常！阿斯托維紥圖！"']:
                pass
            elif event.content in ['"吾之神力，吾之教义，才是这世间的真理！"', '"吾之神力，吾之教義，才是這世間的真理！"']:
                pass
            elif event.content in ['""', '""']:
                pass
            elif event.content in ['""', '""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["阿萨辛的宝物", "阿薩辛的寶物", "陆危楼", "陸危樓"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        # if key in self.bhInfo or self.debug:
                        #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                        #                        1, "NPC出现", "npc")
                        # npc = self.bld.info.npc[event.id]
                        # print("[NPCappear]", npc.templateID, npc.x, npc.y ,npc.z)
            if event.id in self.p2npc and self.p2npc[event.id]["status"] == 1 and event.enter == 0:
                # print("npcSuccess", event.id)
                # NPC成功处理
                # for player in self.p2info:
                #     if event.id in self.p2info[player]["damage"]:
                #         # 结算这名玩家的伤害
                #         self.statDict[player]["battle"]["P2AddEffective"] += self.p2info[player]["damage"][event.id]
                self.p2npc[event.id]["status"] = 0
                # 找到另一个NPC
                dualNPC = ""
                for npc in self.p2npc:
                    if self.p2npc[npc]["status"] == 1 and self.p2npc[npc]["sex"] * self.p2npc[event.id]["sex"] > 0 and npc != event.id:
                        dualNPC = npc
                        break
                if dualNPC != "":
                    # 同样结算这个NPC
                    # for player in self.p2info:
                    #     if dualNPC in self.p2info[player]["damage"]:
                    #         # 结算这名玩家的伤害
                    #         self.statDict[player]["battle"]["P2AddEffective"] += self.p2info[player]["damage"][dualNPC]
                    self.p2npc[dualNPC]["status"] = 0

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.getName(event.id) in ["阿萨辛"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.player:
                # deathTime = (event.time - self.startTime + self.timeDelay) / 1000
                # self.triviaFile.write("Dead %s %.1f\n" % (self.bld.info.getName(event.id), deathTime))
                self.triviaWrite("Dead", event.id, event.time, "")
            # if event.id in self.p2npc and self.p2npc[event.id]["status"] == 1:
            #     print("npcSuccess", event.id)
            #     # NPC成功处理
            #     for player in self.p2info:
            #         if event.id in self.p2info[player]["damage"]:
            #             # 结算这名玩家的伤害
            #             self.statDict[player]["battle"]["P2AddEffective"] += self.p2info[player]["damage"][event.id]
            #     self.p2npc[event.id]["status"] = 0
            #     # 找到另一个NPC
            #     dualNPC = ""
            #     for npc in self.p2npc:
            #         if self.p2npc[npc]["status"] == 1 and self.p2npc[npc]["sex"] * self.p2npc[event.id]["sex"] > 0:
            #             dualNPC = npc
            #             break
            #     if dualNPC != "":
            #         # 同样结算这个NPC
            #         for player in self.p2info:
            #             if dualNPC in self.p2info[player]["damage"]:
            #                 # 结算这名玩家的伤害
            #                 self.statDict[player]["battle"]["P2AddEffective"] += self.p2info[player]["damage"][dualNPC]
            #         self.p2npc[dualNPC]["status"] = 0

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 2000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        key = "c%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")
                if event.id == "42946":
                    if event.time - self.eyeActiveTime > 10000:
                        self.eyeActiveTime = event.time
                        self.eyeActiveNum += 1
                if event.id == "42836":
                    if event.caster in self.p2npc:
                        self.p2npc[event.caster]["startCast"] = event.time
                if event.id == "42770":
                    self.p2Bahman = event.time

    def analyseFirstStage(self, item):
        '''
        处理单条复盘数据时的流程，在第一阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        '''
        self.initBattleBase()
        self.activeBoss = "阿萨辛"
        self.debug = 1

        self.initPhase(3, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.cszzStart = 0

        self.bhBlackList.extend(["s42596",  # 攻击
                                 "b31974",  # 圣痕
                                 "b31909",  # 注视（通用点名）
                                 "s42599", "b31908",  # 圣炎
                                 "s42615", "s42616",  # 亚兹丹启示
                                 "s42627", "s42628", "s42629", "b32395",  # 阴差阳错/非阴非阳
                                 "s42955", "s42604", "s42605",  # 真理圣炎舞
                                 "s42623",  # 驱魔斩
                                 "s42624",  # 驱魔炎
                                 "s42633",  # 原罪缚穴术
                                 "s42602",  # 真理圣炎斩
                                 "s42791", "s42792", "s42793",  # 天罚刖刑
                                 "s42760",  # 二元旋涡
                                 "s42766",  # 圣炎灼
                                 "s43586",  # 攻击（小怪）
                                 "b31973",  # 剧毒
                                 "s42788", "s42794",  # 圣炎化身斩
                                 "s42778",  # 蛇尾剪
                                 "s42786",  # 毒风
                                 "s42777",  # 毒咆
                                 "s42779",  # 锯牙毒雾
                                 "s42784",  # 毒手功
                                 "c42833",  # 二元转化
                                 "b31980",  # 誓约印记
                                 "b32008",  # 禁锢
                                 "s43613", "s43612",  # 阴浊（P2反弹）
                                 "c42836",  # 同生共死
                                 "s43417", "b32379", "s43707",  # 灰烬
                                 "b32380", "s43708",  # 灭烬
                                 "s42973", "s43725", "c42946",  # 阿里曼之视
                                 "b32240",  # 视之痕
                                 "b32181", "s42945",  # 达埃瓦献祭
                                 "s42961",  # 血泉渡
                                 "b32122",  # 血寒入体
                                 "s42954",  # 血誓寒凝
                                 "s42953",  # 赤血之约
                                 "b32101",  # 血毒
                                 "s42962",  # 血泉渡
                                 "s42957",  # 终焉吞噬
                                 "b5197",  # 濒死窒息
                                 "s42958", "b32466",  # 血影击, 破裂
                                 "s42956",  # 真理圣炎舞(P3)
                                 "b32117", "b32116",  # 阳浊之疾/阴浊之疾
                                 "s43028", "s42967",  # 终焉残片
                                 "b31961",  # 眩晕
                                 "s42975",  # 狂妄之击
                                 "s42774",  # 伽巴尔审判
                                 "s42773",  # 圣月浊
                                 "s42974",  # 暴虐之击
                                 "s42963", "s42964",  # 倾泻之欲, 狂放之气
                                 "s42969",  # 凝视之殇
                                 "s42966",  # 终焉残章
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c42597": ["4497", "#0000ff", 2000],  # 圣炎
                       "c42613": ["4532", "#0077ff", 3000],  # 亚兹丹启示
                       "c42621": ["4567", "#0077ff", 1000],  # 天罚
                       "c42622": ["4567", "#0077ff", 0],  # 驱魔斩
                       "c42600": ["4519", "#0000ff", 3000],  # 库尔达祷言
                       "c42625": ["3429", "#ff0000", 3000],  # 阴阳二元论
                       "c42603": ["2024", "#ff0077", 3000],  # 真理圣炎舞
                       "c42632": ["2144", "#ff7700", 4000],  # 原罪缚穴术
                       "c42601": ["2911", "#7700ff", 3000],  # 真理圣炎斩
                       "c42789": ["3435", "#777777", 2000],  # 绯烬神谕
                       "c42758": ["3446", "#777777", 4000],  # 亚泽特恩泽
                       "c42770": ["3417", "#0000ff", 1500],  # 巴赫曼誓约
                       "c42781": ["4546", "#0077ff", 3000],  # 锯牙毒雾
                       "c42783": ["4564", "#ff0077", 1500],  # 毒手功
                       "c42787": ["3426", "#ff0000", 4000],  # 圣炎化身斩
                       "c42798": ["327", "#777777", 3000],  # 圣火临
                       "c42852": ["10783", "#777777", 3000],  # 二元化月
                       "c42780": ["4492", "#7700ff", 2000],  # 蛇尾剪
                       "c42785": ["4501", "#ff7700", 3000],  # 潜蛇手
                       "c42782": ["2134", "#00ff77", 2500],  # 毒印
                       "c42776": ["2142", "#77ff00", 2000],  # 毒咆
                       "c42775": ["733", "#77ff77", 4000],  # 伽巴尔审判
                       "c43416": ["18459", "#00ff00", 3000],  # 安哥拉启示
                       "c42943": ["2133", "#777777", 5000],  # 达埃瓦献祭
                       "c42960": ["345", "#ff0000", 2000],  # 血泉渡
                       "c42951": ["2039", "#ff0077", 3000],  # 赤血之约
                       "c43782": ["2039", "#ff0077", 3000],  # 血祭圣典
                       "b32104": ["3398", "#ff7700", 0],  # 倾泻之欲
                       "b32263": ["2035", "#00ff77", 0],  # 傲气
                       "c43048": ["4531", "#77ff00", 5000],  # 图里兹之疫
                       "c42965": ["16844", "#0000ff", 3000],  # 终焉残章
                       "c43634": ["2028", "#000000", 7000],  # 永夜降临
                       }

        # 阿萨辛数据格式：
        # ？


        # if self.bld.info.map == "会战弓月城":
        #     self.bh.critPeriodDesc = "暂无."
        # if self.bld.info.map == "25人普通会战弓月城":
        #     self.bh.critPeriodDesc = "[镇魂梵音劫]期间."
        # if self.bld.info.map == "25人英雄会战弓月城":
        #     self.bh.critPeriodDesc = "[镇魂梵音劫]期间."
        self.bh.critPeriodDesc = "暂无."

        self.eyeActiveNum = 0
        self.eyeActiveTime = 0

        self.sexCal = {}  # 判断玩家性别

        self.p2info = {}  # 对NPC的战斗事件
        self.p2npc = {}  # P2NPC的记录
        self.p2Bahman = 0  # P2召唤读条时间

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"P1BossDamage": 0,
                                             "P2BossDamage": 0,
                                             "P2AddEffective": 0,
                                             "P3BossDamage": 0,
                                             "P3AddEffective": 0,
                                             "Eye1Damage": 0,
                                             "Eye2Damage": 0,
                                             "Eye3Damage": 0,
                                             "Eye4Damage": 0,
                                             "Eye5Damage": 0,
                                             "Eye6Damage": 0,
                                             "GarbageDamage": 0,}
            self.sexCal[line] = 0
            self.p2info[line] = {"history": {}, "damage": {}}

        self.startTimeStamp = self.bld.info.battleTime

        if self.config.item["general"]["trivia"]:
            if not os.path.exists("triviaResult"):
                os.makedirs("triviaResult")
            self.triviaFileName = "triviaResult/%s.txt" % self.startTimeStamp
            self.triviaFile = open(self.triviaFileName, "w", encoding="utf-8")

        self.timeDelay = 0
        self.killAppear = 0
        self.drujRecord = {}
        self.aesmaAppear = 0
        self.tarumatAppear = 0
        self.tarumatHit = 0
        self.aesmaPlayer = ""
        self.tarumatPlayer = ""
        self.p3check = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

    # 技能
    # 真理圣炎斩
    # 原罪缚穴术
    # 达埃瓦献祭
    # 戮之血影点名
    # 血泉渡点名（重叠、失败）
    # 黑狗点名
    # 黑狗失败
    # 白狗点名
    # 白狗失败
    # P2毛伤害
    # 所有伤害
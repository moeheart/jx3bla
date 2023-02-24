# Created by moeheart at 11/03/2022
# 李重茂的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class LiChongmaoWindow(SpecificBossWindow):
    '''
    李重茂的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("李重茂", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("本体DPS", "对BOSS的原始DPS。\n战斗时间：%s\n由于这个BOSS有高额易伤，rDPS的结果会与实际很不一样，因此将本体DPS列出作为参考。" % parseTime(self.detail["btTime"]))
        tb.AppendHeader("小怪", "战斗开始时三只小怪的伤害总量。\n这个BOSS小怪的战斗时间不好设置统一标准，因此不展示DPS而是展示伤害总量，其余几个也一样。")
        tb.AppendHeader("2武士", "对第一次怒阶段和第二次恨阶段的2个[一刀流武士]的伤害总量，通常共4次。\n这两个武士因为没有易伤且需要转火，常被忽略。")
        tb.AppendHeader("4武士", "在皇天真气阶段的4个[一刀流武士]的伤害总量，通常共2次。\n一般来说这是战斗的主要难点。")
        tb.AppendHeader("恐阶段打错", "对恐阶段对本体/镜影的错误输出对战斗有负面影响，这里以1:1的比例记录这些反向DPS。\n这里使用DPS，是除以战斗总时间的。")
        tb.AppendHeader("武士打错", "对错误属性武士的输出导致的回血，这里以1:1的比例记录这些反向DPS。\n这里使用DPS，是除以战斗总时间的。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["btDPS"]))
            tb.AppendContext(int(line["battle"]["xgDPS"]))
            tb.AppendContext(int(line["battle"]["ws2DPS"]))
            tb.AppendContext(int(line["battle"]["ws4DPS"]))
            tb.AppendContext(int(line["battle"]["fx1DPS"]))
            tb.AppendContext(int(line["battle"]["fx2DPS"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class LiChongmaoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        if self.phase == 3:
            # 结算怒阶段犯错
            self.phase3Finalize(self.finalTime)

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        self.detail["btTime"] = int(sum(self.phaseTime[1:]) / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.wushiControl(-1, "initial", 0, "")
        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                # line = self.stat[id]
                res = self.getBaseList(id)
                res["battle"]["btDPS"] = int(safe_divide(res["battle"]["btDPS"], self.detail["btTime"]))
                res["battle"]["fx1DPS"] = int(safe_divide(res["battle"]["fx1DPS"], self.detail["btTime"]))
                res["battle"]["fx2DPS"] = int(safe_divide(res["battle"]["fx2DPS"], self.detail["btTime"]))
                bossResult.append(res)
        # bossResult.sort(key=lambda x: -x[2])
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

    def wushiControl(self, time, caster, id, skillName):
        '''
        记录一次控制武士的事件。用于合并对多个武士的控制.
        params:
        - time: 控制事件的时间. 如果为-1, 则代表强制结算最后一次事件.
        - caster: 控制事件的发起者.
        - id: 被控制武士的编号.
        - skillName: 用来控制的技能的名称.
        '''

        if time != -1 and time - self.wushiStack["time"] < 100 and caster == self.wushiStack["caster"] and skillName == self.wushiStack["skillName"]:
            if id not in self.wushiStack["id"]:
                self.wushiStack["id"].append(id)
        else:
            # 记录原本的结果
            if self.wushiStack["caster"] != "initial":
                self.wushiStack["id"].sort()
                self.wushiStack["id"] = [str(id) for id in self.wushiStack["id"]]
                castTime = parseTime((self.wushiStack["time"] - self.startTime) / 1000)
                ids = ",".join(self.wushiStack["id"])
                self.addPot([self.bld.info.getName(self.wushiStack["caster"]),
                             self.bld.info.getOcc(self.wushiStack["caster"]),
                             0,
                             self.bossNamePrint,
                             "%s控制武士%s，来源：%s" % (castTime, ids, self.wushiStack["skillName"]),
                             [],
                             0])
            # 替换暂存区
            self.wushiStack = {"time": time, "caster": caster, "id": [id], "skillName": skillName}

    def phase3Finalize(self, time):
        '''
        结算怒阶段的犯错记录.
        params:
        - time: 怒阶段结束的时间. 也有可能是脱战时间(如果在怒阶段结束战斗的话)
        '''

        endTime = parseTime((time - self.startTime) / 1000)
        maxTianzhu = max(self.tianzhuTime.values())
        maxZongheng = max(self.zonghengTime.values())
        for line in self.bld.info.player:
            if line not in self.p3alive or not self.p3alive[line]:
                continue
            # if (self.sanriTime[line] == 0 and self.henTime == 1) or (self.sanriTime[line] > 0 and self.henTime == 2):
            #     self.addPot([self.bld.info.player[line].name,
            #                  self.occDetailList[line],
            #                  1,
            #                  self.bossNamePrint,
            #                  "%s三日处理错误，次数%d" % (endTime, self.sanriTime[line]),
            #                  [],
            #                  0])
            if (self.xuefengTime[line] == 0 and self.henTime == 1) or (self.xuefengTime[line] > 0 and self.henTime == 2):
                self.addPot([self.bld.info.player[line].name,
                             self.occDetailList[line],
                             1,
                             self.bossNamePrint,
                             "%s雪风处理错误，次数%d" % (endTime, self.xuefengTime[line]),
                             [],
                             0])
            if (self.tianzhuTime[line] < min(2, maxTianzhu) and self.henTime == 1) or (self.tianzhuTime[line] > 0 and self.henTime == 2):
                self.addPot([self.bld.info.player[line].name,
                             self.occDetailList[line],
                             1,
                             self.bossNamePrint,
                             "%s天诛处理错误，次数%d" % (endTime, self.tianzhuTime[line]),
                             [],
                             0])
            if (self.zonghengTime[line] < min(2, maxZongheng) and self.zonghengTime[line] >= 0 and self.henTime == 1) or (self.zonghengTime[line] > 0 and self.henTime == 2):
                self.addPot([self.bld.info.player[line].name,
                             self.occDetailList[line],
                             1,
                             self.bossNamePrint,
                             "%s刀气纵横处理错误，次数%d" % (endTime, self.zonghengTime[line]),
                             [],
                             0])
            self.zonghengTime[line] = 0
            # self.sanriTime[line] = 0
            self.xuefengTime[line] = 0
            self.tianzhuTime[line] = 0

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

        self.checkTimer(event.time)

        # 结算武士的控制组
        if event.time - self.wushiStack["time"] > 100 and self.wushiStack["time"] != -1:
            self.wushiControl(-1, "initial", 0, "")

        # 判断驱散与打断
        if self.purgeEventInfo["time"] != -1:
            if abs(self.purgeEventInfo["time"] - self.purgeInfo["time"]) < 100 and self.henTime == 1:
                # 记录驱散
                castTime = parseTime((self.purgeInfo["time"] - self.startTime) / 1000)
                self.addPot([self.bld.info.player[self.purgeInfo["caster"]].name,
                             self.occDetailList[self.purgeInfo["caster"]],
                             1,
                             self.bossNamePrint,
                             "%s意外驱散印痕，来源：%s" % (castTime, self.purgeInfo["skillName"]),
                             ["这一记录只能说明施放了技能，但秘籍和奇穴可能使这个技能没有驱散效果，请进一步确认"],
                             0])
                self.purgeEventInfo["time"] = -1
            if event.time - self.purgeEventInfo["time"] > 1000:
                self.purgeEventInfo["time"] = -1

        if self.interruptEventInfo["time"] != -1:
            if abs(self.interruptEventInfo["time"] - self.interruptInfo["time"]) < 3000 and self.henTime == 1:
                # 记录打断
                castTime = parseTime((self.interruptInfo["time"] - self.startTime) / 1000)
                self.addPot([self.bld.info.player[self.interruptInfo["caster"]].name,
                             self.occDetailList[self.interruptInfo["caster"]],
                             1,
                             self.bossNamePrint,
                             "%s意外打断秋水，来源：%s" % (castTime, self.interruptInfo["skillName"]),
                             ["这一记录只能说明施放了技能，但秘籍和奇穴可能使这个技能没有打断效果，请进一步确认"],
                             0])
                self.interruptEventInfo["time"] = -1
            if event.time - self.interruptEventInfo["time"] > 3000:
                self.interruptEventInfo["time"] = -1

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
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

                if event.id == "33376":  # 武士必中普攻
                    self.wushiControl(-1, "initial", 0, "")
                    deathTime = parseTime((event.time - self.startTime) / 1000)
                    source = event.caster
                    id = 0
                    if source in self.wushiDict:
                        id = self.wushiDict[source]
                    self.addPot([self.bld.info.player[event.target].name,
                                  self.occDetailList[event.target],
                                  1,
                                  self.bossNamePrint,
                                  "%s武士惩罚击杀，来源：武士%d" % (deathTime, id),
                                  [],
                                  0])

                if event.id in PURGE_DICT and event.target == self.yinhenTarget:
                    if self.purgeEventInfo["time"] == -1 or event.time - self.purgeEventInfo["time"] < self.purgeEventInfo["time"] - self.purgeInfo["time"]:
                        self.purgeInfo = {"time": event.time, "caster": event.caster, "skillName": PURGE_DICT[event.id]}

                if event.id == "33311":  # 刀气纵横
                    self.zonghengTime[event.target] += 1

                if event.id in ["33085", "33086"]:  # 天诛/天谴
                    self.tianzhuTime[event.target] += 1

                if event.id in ["33483"] and event.damageEff > 0:    # P3dot
                    self.p3alive[event.target] = 1

            else:

                # if event.id in ["262", "263", "264"]:
                #     print("[Shizihou]", self.bld.info.getName(event.target), self.bld.info.getSkillName(event.full_id), parseTime((event.time - self.startTime) / 1000))
                #
                # if self.phase == 5 and self.bld.info.getName(event.target) in ["一刀流武士"] and event.target in self.wushiDict: # and self.wushiDict[event.target] == 2:
                #     print("[Wushi%dTest]" % self.wushiDict[event.target], parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), self.bld.info.getSkillName(event.full_id),
                #           event.id, event.level, event.damageEff)

                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if self.bld.info.getName(event.target) in ["李重茂", "镜影·李重茂"]:
                        self.bh.setMainTarget(event.target)
                        if self.jzly != 0 and event.time - self.jzly > 2000 and \
                                ((self.henTime == 1 and self.bld.info.getName(event.target) in ["李重茂"]) or \
                                 (self.henTime == 2 and self.bld.info.getName(event.target) in ["镜影·李重茂"])):
                            self.statDict[event.caster]["battle"]["fx1DPS"] += event.damageEff
                        else:
                            self.statDict[event.caster]["battle"]["btDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["一刀流精锐武士", "一刀流精銳武士", "永王叛军长枪兵", "永王叛军剑卫", "永王叛軍長槍兵", "永王叛軍劍衛"]:
                        self.statDict[event.caster]["battle"]["xgDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["一刀流武士"]:
                        if self.phase == 5:
                            self.statDict[event.caster]["battle"]["ws4DPS"] += event.damageEff
                        else:
                            self.statDict[event.caster]["battle"]["ws2DPS"] += event.damageEff

                # if event.id in CONTROL_DICT:
                #     print("[Control_test]", parseTime((event.time - self.startTime) / 1000), event.id, self.bld.info.getSkillName(event.full_id),
                #           CONTROL_DICT[event.id], self.bld.info.getName(event.target), event.damageEff)

                if self.phase == 5 and self.bld.info.getName(event.target) in ["一刀流武士"] and event.id in CONTROL_DICT:  # and event.caster in self.bld.info.player:
                    # castTime = parseTime((event.time - self.startTime) / 1000)
                    id = 0
                    if event.target in self.wushiDict:
                        id = self.wushiDict[event.target]

                    skillName = CONTROL_DICT[event.id]
                    if skillName == "":
                        skillName = self.bld.info.getSkillName(event.full_id)

                    self.wushiControl(event.time, event.caster, id, skillName)

                if self.bld.info.getName(event.target) in ["一刀流武士"]:
                    # 判断是否是回血
                    if "7" in event.fullResult and event.caster in self.statDict:
                        damage = int(event.fullResult["7"])
                        self.statDict[event.caster]["battle"]["fx2DPS"] += damage

                if event.id in INTERRUPT_DICT and not (event.id == "18584" and self.fenlanDict[event.caster]):
                    # print("[Interrupt]", parseTime((event.time - self.startTime) / 1000), self.bld.info.getSkillName(event.full_id), self.bld.info.getName(event.caster), event.damageEff)
                    if self.interruptEventInfo["time"] == -1 or self.interruptEventInfo["time"] > self.interruptInfo["time"]:
                        self.interruptInfo = {"time": event.time, "caster": event.caster, "skillName": INTERRUPT_DICT[event.id]}

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

            if event.id == "24289":  # 枪兵目标
                if event.stack == 1:
                    self.qiangbingStart[event.target] = event.time
                    # self.stunCounter[event.target].setState(event.time, 1)
                else:
                    self.bh.setCall("24289", "枪兵目标", "3426", self.qiangbingStart[event.target], event.time - self.qiangbingStart[event.target], event.target, "被枪兵点名")
                    # self.stunCounter[event.target].setState(event.time, 0)

            if event.id == "24078":  # 潜龙真气
                if event.stack == 1:
                    self.bh.setCall("24078", "潜龙真气", "3431", event.time, 12000, event.target, "潜龙真气点名")

            if event.id == "24593":  # 雪风
                if event.stack == 1:
                    self.bh.setCall("24593", "雪风", "3414", event.time, 2500, event.target, "雪风点名")

            if event.id == "24932":  # 铁索牢狱
                self.stunCounter[event.target].setState(event.time, event.stack)
                if event.stack == 1:
                    self.bh.setCall("24932", "铁索牢狱", "3408", event.time, 0, event.target, "铁索牢狱点名")

            if event.id == "24085":  # 印痕
                if event.stack == 1:
                    self.yinhenTarget = event.target
                    self.yinhenTime = event.time
                else:
                    if event.time - self.yinhenTime < 14900:  # 因为被驱散而消失
                        self.purgeEventInfo["time"] = event.time
                    self.yinhenTarget = ""

            if event.id == "12658":  # 分澜
                self.fenlanDict[event.target] = 1

            if event.id == "24808" and event.stack == 1:  # 刀气纵横
                self.zonghengTime[event.target] -= 10

            # if event.id == "24591" and event.stack == 1:  # 三日
            #     self.sanriTime[event.target] += 1

            if event.id == "24589" and event.stack == 1:  # 雪风
                self.xuefengTime[event.target] += 1

            if event.id == "24593" and event.stack == 1:  # 雪风点名
                self.xuefengTime[event.target] -= 10

        elif event.dataType == "Shout":
            if event.content in ['"这就是乱臣贼子的下场！"']:
                pass
            elif event.content in ['"有刺客，快来人护驾！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"御林军何在！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"太平公主、临淄王……你们休想夺走朕的皇位！"']:
                self.changePhase(event.time, 2)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                self.henTime += 1
            elif event.content in ['"我忍辱负重至今，只为重夺皇位，我才是真命天子！"']:
                self.changePhase(event.time, 3)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"救驾！人呢？救驾！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"护驾二字岂是你这贼子能喊的？"']:
                pass
            elif event.content in ['"把这些逆贼打入天牢！"']:
                pass
            elif event.content in ['"朕没有错！是天下人负了朕！"']:
                if self.phase == 3:
                    # 结算怒阶段犯错
                    self.phase3Finalize(event.time)
                self.changePhase(event.time, 5)
                self.jzly = 0
                self.yshp = 0
            elif event.content in ['"师兄.....师兄你在哪？有人要害我！"']:
                self.changePhase(event.time, 4)
            elif event.content in ['"啧……"']:
                pass
            elif event.content in ['"啊……"']:
                pass
            elif event.content in ['"啊！"']:
                pass
            elif event.content in ['"凤棠……是你……"']:
                pass
            elif event.content in ['"哥……你醒了。"']:
                pass
            elif event.content in ['"我清醒的时间有限……好多事……李重茂……我要告诉你们……"']:
                pass
            elif event.content in ['"哥，不要怕。我们先回万花谷去治你的伤，我们还有很多的时间。"']:
                pass
            elif event.content in ['"不，还不能走……现在必须立即前去阻止那个姓韩的怪人和那个东瀛人！不能让他们的蛊毒污染水源！"']:
                pass
            elif event.content in ['"那个怪人熔炼出的蛊毒虽然与江河相比如沧海一粟，但若以阴阳术催化毒性，就能在水源中快速扩散，污染大片的土地。"']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["李重茂宝箱", "李重茂寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")
            if self.bld.info.getName(event.id) in ["一刀流武士"] and event.enter and self.phase == 5:
                self.wushiNum += 1
                self.wushiDict[event.id] = self.wushiNum

        elif event.dataType == "Death":  # 重伤记录

            if event.id not in self.bld.info.player:
                return

            # deathTime = parseTime((event.time - self.startTime) / 1000)
            # source = event.killer
            # sourceName = self.bld.info.getName(source)
            # id = 0
            # if source in self.wushiDict:
            #     id = self.wushiDict[source]
            # if sourceName in ["一刀流武士"]:
            #
            #     self.addPot([self.bld.info.player[event.id].name,
            #                   self.occDetailList[event.id],
            #                   1,
            #                   self.bossNamePrint,
            #                   "%s被武士击杀，来源：一刀流武士%d" % (deathTime, id),
            #                   [],
            #                   0])


        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")
            if event.id == "32333":  # 一刀流·秋水
                self.interruptEventInfo["time"] = event.time
            if event.id == "33337":  # 移神换魄
                self.yshp = 1
                # print("[yshp]", parseTime((event.time - self.startTime) / 1000))
            if event.id == "33356":  # 镜中胧月
                self.jzly = event.time
                # print("[jzly]", parseTime((event.time - self.startTime) / 1000))
                    
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
        self.activeBoss = "李重茂"

        self.initPhase(5, 1)

        self.bhBlackList.extend(["n112037", "n112576", "s32339", "b24289", "c32634", "c33075", "s33076", "c32596",
                                 "b24079", "n112030", "c32075", "b24338", "s32634", "s32596",
                                 "n112523", "n112520", "n112521", "n112493", "n113449", "n112506",  # P1
                                 "b24085", "b24270", "s32331", "b24078", "s32340", "s32632", "b20485", "s32631",    # P2
                                 "b24589", "s33085", "s33086", "s33079", "s33080", "n112044", "s33078", "c33087",
                                 "b24593", "b24591", "b24853",  # P3
                                 "n112856", "n112917", "n112829", "n112091", "n112578",  # 剧情
                                 "b24854", "s33445", "n113447", "s33438", "s33437", "b24858", "s33342", "s33340", "b24947",  # P4
                                 "b24931", "b24932", "b24938", "b24940", "s33440", "s33439", "n112536", "s33375",
                                 "n113450",  # 间段机制
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c33076": ["2028", "#0000ff", 4000],  # 剑锋纵横
                       "c32331": ["332", "#ff00ff", 3000],  # 一刀流·龙锤
                       "c32332": ["3431", "#7777ff", 4000],  # 潜龙真气
                       "c32333": ["3429", "#ff77cc", 0],  # 一刀流·秋水
                       "c33085": ["3430", "#ff7777", 4500],  # 一刀流·天诛
                       "c33078": ["2021", "#ff7700", 2500],  # 一刀流·雪风
                       "c33079": ["327", "#ff0000", 2000],  # 一刀流·X日
                       "c33433": ["2022", "#ff7700", 2000],  # 真气化龙
                       "c33435": ["3408", "#77ff00", 2000],  # 铁索牢狱
                       "c33356": ["337", "#0077ff", 2000],  # 镜中胧月
                       "c33437": ["3398", "#0000ff", 2000],  # 怒焚九州
                       "c33346": ["2023", "#7700ff", 2000],  # 镜中影月
                       "c33347": ["2023", "#7700ff", 2000],  # 镜中影月
                       "c33342": ["348", "#7777ff", 2000],  # 临影剑法·乱风
                       "c33340": ["348", "#7777ff", 2000],  # 临影剑法
                       "c33337": ["2120", "#cc77ff", 2000],  # 移神换魄
                       "c33441": ["3398", "#00ff77", 2000],  # 魔障缠身
                       }

        # 李重茂数据格式：
        # 7 ？

        # 武士控制复盘
        self.qiangbingStart = {}
        self.wushiDict = {}
        self.wushiNum = 0
        self.wushiStack = {"time": -1, "caster": "initial", "id": [], "skillName": ""}

        # 驱散打断复盘
        self.yinhenTarget = ""
        self.yinhenTime = 0
        self.purgeInfo = {"time": -1, "caster": "", "skillName": ""}
        self.purgeEventInfo = {"time": -1}
        self.interruptInfo = {"time": -1, "caster": "", "skillName": ""}
        self.interruptEventInfo = {"time": -1}
        self.fenlanDict = {}

        # 阶段与目标复盘
        self.yshp = 0  # 移神换魄
        self.jzly = 0  # 镜中胧月
        self.henTime = 0  # 恨阶段次数
        self.zonghengTime = {}  # 刀气纵横次数
        # self.sanriTime = {}  # 三日次数
        self.xuefengTime = {}  # 雪风次数
        self.tianzhuTime = {}  # 天诛次数
        self.p3alive = {}  # P3存活记录

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"btDPS": 0,
                                             "xgDPS": 0,
                                             "ws2DPS": 0,
                                             "ws4DPS": 0,
                                             "fx1DPS": 0,
                                             "fx2DPS": 0}
            self.qiangbingStart[line] = 0
            self.fenlanDict[line] = 0
            self.zonghengTime[line] = 0
            # self.sanriTime[line] = 0
            self.xuefengTime[line] = 0
            self.tianzhuTime[line] = 0
            self.p3alive[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


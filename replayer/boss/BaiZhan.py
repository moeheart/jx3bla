# Created by moeheart at 11/03/2022
# 张景超&张法雷的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class BaiZhanWindow(SpecificBossWindow):
    '''
    张景超&张法雷的定制复盘窗口类。
    '''

    def getColor(self, color):
        '''
        根据百战的简写颜色来获取显示颜色.
        '''
        return {"red": "#ff0000",
                "blue": "#0077ff",
                "yellow": "#ff7700",
                "green": "#007700",
                "purple": "#7700ff",
                "black": "#000000",
                "passive": "#777777",
                "normal": "#000000",
                "white": "#777777",
                }[color]

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("百战：%s" % self.detail["boss"], "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        # self.constructCommonHeader(tb, "")
        # tb.AppendHeader("本体DPS", "对张景超的DPS。\n常规阶段时间：%s" % parseTime(self.detail["P1Time"]))
        # tb.AppendHeader("双体1DPS", "第一次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time1"]))
        # tb.AppendHeader("双体2DPS", "第二次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time2"]))

        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("nDPS/分数", "在百战复盘中，显示nDPS。")
        # tb.AppendHeader("排名", "前一项的排名，表示超过了百分之多少的玩家。\n有时这个排名会与详细复盘中不一致，这是因为这里是“全时刻排名”，而详细复盘中是“即时排名”。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。\n被星号标记的装分表示对应的装备已经获取失败，但服务器可以从最近的战斗记录中读取到缓存。")
        # tb.AppendHeader("详情", "装备详细描述。")
        # tb.AppendHeader("强化", "装备强化列表，表示[精炼满级装备数量]/[插8]-[插7]-[插6]/[五彩石等级]/[紫色附魔]-[蓝色附魔]/[大附魔：手腰脚头衣裤]\n注意精炼与镶嵌目前无法准确获取，但附魔情况是准确的。")
        # tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。%s" % stunDescription)

        tb.AppendHeader("技能1", "百战技能，注意不一定会按照顺序。")
        tb.AppendHeader("技能2", "百战技能，注意不一定会按照顺序。")
        tb.AppendHeader("技能3", "百战技能，注意不一定会按照顺序。")

        tb.AppendHeader("打精", "玩家对所有类型目标的精力打击总和。")
        tb.AppendHeader("打耐", "玩家对所有类型目标的耐力打击总和。")
        tb.AppendHeader("掉精", "玩家受到的精力打击总和（不包括施放技能的消耗）。")
        tb.AppendHeader("掉耐", "玩家受到的耐力打击总和（不包括施放技能的消耗）。")
        tb.AppendHeader("回精", "玩家对友方目标的精力回复总和。")
        tb.AppendHeader("回耐", "玩家对友方目标的耐力回复总和。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            # self.constructCommonLine(tb, line)

            name = self.getMaskName(line["name"])
            color = getColor(line["occ"])
            tb.AppendContext(name, color=color, width=13)

            tb.AppendContext(str(line.get("ndps", 0)), color="#000000")

            if line["equip"]["score"] == "":
                text4 = "-"
            else:
                text4 = str(line["equip"]["score"])
            color4 = "#000000"
            if "大橙武" in line["equip"]["sketch"]:
                color4 = "#ffcc00"
            tb.AppendContext(text4, color=color4)

            if "name" in line["battle"]["skill1"]:
                text1 = "%d%s" % (int(line["battle"]["skill1"]["level"]), line["battle"]["skill1"]["name"])
                color = self.getColor(line["battle"]["skill1"]["color"])
                tb.AppendContext(text1, color=color)
            else:
                tb.AppendContext("")

            if "name" in line["battle"]["skill2"]:
                text2 = "%d%s" % (int(line["battle"]["skill2"]["level"]), line["battle"]["skill2"]["name"])
                color = self.getColor(line["battle"]["skill2"]["color"])
                tb.AppendContext(text2, color=color)
            else:
                tb.AppendContext("")

            if "name" in line["battle"]["skill3"]:
                text3 = "%d%s" % (int(line["battle"]["skill3"]["level"]), line["battle"]["skill3"]["name"])
                color = self.getColor(line["battle"]["skill3"]["color"])
                tb.AppendContext(text3, color=color)
            else:
                tb.AppendContext("")

            tb.AppendContext(int(line["battle"]["jingliDeal"]), color="#7700ff")
            tb.AppendContext(int(line["battle"]["nailiDeal"]), color="#ff7700")
            tb.AppendContext(int(line["battle"]["jingliTaken"]), color="#330077")
            tb.AppendContext(int(line["battle"]["nailiTaken"]), color="#773300")
            tb.AppendContext(int(line["battle"]["jingliHeal"]), color="#cc77ff")
            tb.AppendContext(int(line["battle"]["nailiHeal"]), color="#ffcc77")

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

        frame2 = tk.Frame(window)
        frame2.pack()

        # 显示所有的破绽记录

        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("破绽复盘", "")
        tb.EndOfLine()

        for line in self.detail["pozhanList"]:
            tb.AppendContext(line["time"])
            tb.AppendContext(line["name"])
            name = "%s: %s" % (line["skill"], line["level"])
            color = self.getColor(line["color"])
            tb.AppendContext(name, color=color)
            tb.AppendContext("|")
            for single in line["log"]:
                player = single["player"]
                color = getColor(single["occ"])
                tb.AppendContext(single["player"], color=color)
                skill = "%d%s" % (single["level"], single["skill"])
                color = self.getColor(single["color"])
                tb.AppendContext(skill, color=color)
                tb.AppendContext("|")
            tb.EndOfLine()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class BaiZhanReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        # self.bh.printEnvironmentInfo()
        self.baiZhanSummary()

        # self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        # self.detail["P2Time1"] = int(self.phaseTime[2] / 1000)
        # self.detail["P2Time2"] = int(self.phaseTime[3] / 1000)

    def baiZhanSummary(self):
        '''
        战斗结束时整理百战技能.
        '''
        for player in self.statDict:
            num = 0
            for skill in self.baiZhanSkill[player]:
                if num >= 3:
                    break
                num += 1
                self.statDict[player]["battle"]["skill%d" % num] = {"name": skill,
                                                                    "level": self.baiZhanSkill[player][skill]["level"],
                                                                    "color": self.baiZhanSkill[player][skill]["color"]}

        for line in self.poZhanStatus:
            self.summaryPoZhan(line)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                # line = self.stat[id]
                res = self.getBaseList(id)
                # res["battle"]["zjcDPS"] = int(safe_divide(res["battle"]["zjcDPS"], self.detail["P1Time"]))
                # res["battle"]["zflDPS1"] = int(safe_divide(res["battle"]["zflDPS1"], self.detail["P2Time1"]))
                # res["battle"]["zflDPS2"] = int(safe_divide(res["battle"]["zflDPS2"], self.detail["P2Time2"]))
                # res["battle"]["jfDPS1"] = int(safe_divide(res["battle"]["jfDPS1"], self.detail["P2Time1"]))
                # res["battle"]["jfDPS2"] = int(safe_divide(res["battle"]["jfDPS2"], self.detail["P2Time2"]))
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

    def summaryPoZhan(self, id):
        '''
        结算某个破绽并且计入记录。
        '''
        if self.poZhanStatus[id] == 1:
            poZhanInfo = self.poZhanRaw[self.poZhanSkillRecord[id]]
            skill = poZhanInfo[0]
            color = poZhanInfo[3]
            level = poZhanInfo[4]
            self.detail["pozhanList"].append({"name": self.bld.info.getName(id),
                                              "time": parseTime((self.poZhanStart[id] - self.startTime) / 1000),
                                              "skill": skill,
                                              "color": color,
                                              "level": level,
                                              "log": self.poZhanResult[id],
                                              })
        self.poZhanStatus[id] = 0
        self.poZhanNum[id] = 0
        self.poZhanLast[id] = 0
        self.poZhanResult[id] = []
        self.poZhanSkillRecord[id] = 0

    def triggerPoZhan(self, caster, target, time):
        '''
        触发破绽时的记录流程.
        params:
        - caster: 破绽的施放者
        - target: 破绽的目标
        - time: 触发时的时间
        '''
        if target not in self.poZhanStatus:
            return
        if self.poZhanStatus[target] == 1 and (self.poZhanNum[target] >= 6 or time - self.poZhanLast[target] > 4000):  # 距离上一次破绽经过太久
            self.summaryPoZhan(target)  # 结算破绽

        if target not in self.baiZhanLastSkill[caster]:
            return
        if self.poZhanStatus[target] == 0:
            self.poZhanStatus[target] = 1  # 开始记录
            self.poZhanSkillRecord[target] = self.poZhanSkill[target]
            self.poZhanSkill[target] = 0
            self.poZhanStart[target] = time
        self.poZhanNum[target] += 1
        self.poZhanLast[target] = time
        self.poZhanResult[target].append(self.baiZhanLastSkill[caster][target])
        if self.poZhanSkillRecord[target] == 0 and target == self.yuanmingyaActive and self.baiZhanLastSkill[caster][target]["color"] == "blue":
            self.poZhanSkillRecord[target] = self.skillNameLine["火圈"]

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

        self.checkTimer(event.time)

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

                if event.caster in self.statDict:  # 精耐回复
                    self.statDict[event.caster]["battle"]["jingliHeal"] += int(event.fullResult.get("17", 0))
                    self.statDict[event.caster]["battle"]["nailiHeal"] += int(event.fullResult.get("18", 0))
                if event.target in self.statDict:  # 精耐被击
                    self.statDict[event.target]["battle"]["jingliTaken"] -= min(int(event.fullResult.get("17", 0)), 0)
                    self.statDict[event.target]["battle"]["nailiTaken"] -= min(int(event.fullResult.get("18", 0)), 0)

                if event.caster in self.poZhanSkill:  # 记录一个破绽的名字
                    name = self.bld.info.getSkillName(event.full_id)
                    # if name not in ["攻击", "普通攻击", '1,33878,1', '1,33537,1', "流血", "爪击", "血雾侵蚀", '1,33540,1', '1,29786,1', '黑蜂蛊迷雾（穿刺）']:
                    #     self.poZhanSkill[event.caster] = name
                    print("[BossSkill]", event.time, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), event.full_id,
                          self.bld.info.getSkillName(event.full_id), event.damage, self.bld.info.getName(event.target))
                    if name in self.skillNameLine:
                        if self.poZhanStatus[event.caster] == 1 and self.poZhanSkillRecord[event.caster] != self.skillNameLine[name]:
                            self.summaryPoZhan(event.caster)
                        self.poZhanSkill[event.caster] = self.skillNameLine[name]
                        print("[RecordSkill]", self.skillNameLine[name])
                    if event.id in self.skillIdLine:
                        if self.poZhanStatus[event.caster] == 1 and self.poZhanSkillRecord[event.caster] != self.skillIdLine[event.id]:
                            self.summaryPoZhan(event.caster)
                        self.poZhanSkill[event.caster] = self.skillIdLine[event.id]
                        print("[RecordSkill]", self.skillIdLine[event.id])

                    if self.bld.info.getName(event.caster) == "源明雅":
                        self.yuanmingyaActive = event.caster

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        pass
                        # if self.bld.info.getName(event.target) in ["张景超", "張景超"]:
                        #     self.bh.setMainTarget(event.target)
                        #     self.statDict[event.caster]["battle"]["zjcDPS"] += event.damageEff
                        # elif self.bld.info.getName(event.target) in ["张法雷", "張法雷"]:
                        #     if self.phase == 2:
                        #         self.statDict[event.caster]["battle"]["zflDPS1"] += event.damageEff
                        #     else:
                        #         self.statDict[event.caster]["battle"]["zflDPS2"] += event.damageEff
                        # elif self.bld.info.getName(event.target) in ["劲风", "勁風"]:
                        #     if self.phase == 2:
                        #         self.statDict[event.caster]["battle"]["jfDPS1"] += event.damageEff
                        #     else:
                        #         self.statDict[event.caster]["battle"]["jfDPS2"] += event.damageEff

                if event.caster in self.statDict:  # 精耐打击
                    self.statDict[event.caster]["battle"]["jingliDeal"] -= int(event.fullResult.get("17", 0))
                    self.statDict[event.caster]["battle"]["nailiDeal"] -= int(event.fullResult.get("18", 0))

            if event.caster in self.statDict:
                if event.id in self.baiZhanLine:
                    line = self.baiZhanLine[event.id]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    level = event.level
                    if level > 5:
                        level -= 5
                    if name not in self.baiZhanSkill[event.caster]:
                        self.baiZhanSkill[event.caster][name] = {"level": level, "color": skill[1]}
                    else:
                        if level > self.baiZhanSkill[event.caster][name]["level"]:
                            self.baiZhanSkill[event.caster][name]["level"] = level

                    if event.damageEff > 0:
                        # print("[BaizhanSkill]", event.time, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), event.id, event.level,
                        #       self.bld.info.getSkillName(event.full_id), event.damage, self.bld.info.getName(event.target))
                        pass

                    if event.target in self.bld.info.npc:
                        recordPoZhan = 0
                        # 如果有还在暂存的破绽
                        if self.poZhanAppear[event.caster] != 0:
                            if event.time - self.poZhanAppear[event.caster] > 100:
                                # print("[PoZhanRecord2]", event.time, self.bld.info.getName(event.caster))
                                self.triggerPoZhan(event.caster, self.poZhanSaveTarget[event.caster], event.time)
                            else:
                                # 在这个技能后记录
                                recordPoZhan = 1
                        self.baiZhanLastSkill[event.caster][event.target] = {"time": event.time, "skill": name, "level": level, "color": skill[1],
                                                                             "player": self.bld.info.getName(event.caster),
                                                                             "occ": self.occDetailList[event.caster]}
                        if recordPoZhan:
                            # print("[BaizhanSkill3]", event.time, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), event.id, event.level,
                            #       self.bld.info.getSkillName(event.full_id), event.damage, self.bld.info.getName(event.target))
                            # print("[PoZhanRecord3]", event.time, self.bld.info.getName(event.caster))
                            self.triggerPoZhan(event.caster, self.poZhanSaveTarget[event.caster], event.time)

                        self.poZhanAppear[event.caster] = 0

            if event.id == "29906":
                targetName = self.bld.info.getName(event.target)
                if targetName not in ["凌太虚·霄风", "生太极", "碎星辰·返", "无影无相", "韬光养晦", "吞日月·虚空"]:
                    if event.target in self.baiZhanLastSkill[event.caster] and event.time - self.baiZhanLastSkill[event.caster][event.target]["time"] < 100:  # 有最近施放过的技能
                        # print("[PoZhanRecord1]", event.time, self.bld.info.getName(event.caster))
                        self.triggerPoZhan(event.caster, event.target, event.time)
                    else:  # 没有最近施放过的技能，先记录下这个时刻
                        self.poZhanAppear[event.caster] = event.time
                        self.poZhanSaveTarget[event.caster] = event.target

                print("[PoZhan!!]", event.time, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), event.id, event.level,
                      self.bld.info.getSkillName(event.full_id), event.damage, self.bld.info.getName(event.target))

            # if event.caster in self.statDict:
            #     print("[BaizhanLog]", parseTime((event.time - self.startTime) / 1000), event.id, event.level, self.bld.info.getSkillName(event.full_id), event.damage, self.bld.info.getName(event.target))

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

            if event.target in self.statDict:
                if event.id in ["20613", "22726"]:
                    line = self.baiZhanLine["28337"]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    self.baiZhanSkill[event.caster][name] = {"level": event.level, "color": skill[1]}
                if event.id in ["20598"]:
                    line = self.baiZhanLine["33194"]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    self.baiZhanSkill[event.caster][name] = {"level": event.level, "color": skill[1]}
                if event.id in ["20768"]:  # TODO 归潮长生法等级可能判断不准确
                    line = self.baiZhanLine["28554"]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    self.baiZhanSkill[event.caster][name] = {"level": event.level, "color": skill[1]}
                if event.id in ["21265"]:
                    line = self.baiZhanLine["29111"]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    self.baiZhanSkill[event.caster][name] = {"level": event.level, "color": skill[1]}
                if event.id in ["20604"]:
                    line = self.baiZhanLine["28330"]
                    skill = self.baiZhanRaw[line]
                    name = skill[0]
                    self.baiZhanSkill[event.caster][name] = {"level": event.level, "color": skill[1]}

        elif event.dataType == "Shout":
            if event.content in ['']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")
            name = event.content
            if name in self.shoutLine:
                for id in self.poZhanStatus:
                    if self.poZhanStatus[id] == 1 and self.poZhanSkillRecord[id] != self.shoutLine[name]:
                        self.summaryPoZhan(id)
                    self.poZhanSkill[id] = self.shoutLine[name]
                print("[RecordCast]", self.shoutLine[name])

            print("[BossShout]", event.time, parseTime((event.time - self.startTime) / 1000), event.content)

        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["张景超宝箱", "張景超寶箱"]:
            #     self.win = 1
            #     self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            pass

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

            if event.caster in self.poZhanSkill:  # 记录一个破绽的名字
                name = self.bld.info.getSkillName(event.full_id)
                # if name not in ["攻击", "普通攻击"]:
                #     self.poZhanSkill[event.caster] = name
                print("[BossCast]", event.time, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.caster), event.full_id,
                      self.bld.info.getSkillName(event.full_id))

                if name in self.castNameLine:
                    if self.poZhanStatus[event.caster] == 1 and self.poZhanSkillRecord[event.caster] != self.castNameLine[name]:
                        self.summaryPoZhan(event.caster)
                    self.poZhanSkill[event.caster] = self.castNameLine[name]
                    print("[RecordCast]", self.castNameLine[name])
                if event.id in self.castIdLine:
                    if self.poZhanStatus[event.caster] == 1 and self.poZhanSkillRecord[event.caster] != self.castIdLine[event.id]:
                        self.summaryPoZhan(event.caster)
                    self.poZhanSkill[event.caster] = self.castIdLine[event.id]
                    print("[RecordCast]", self.castIdLine[event.id])

                    
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
        self.activeBoss = "百战异闻录"
        self.detail["baizhan"] = 1

        self.initPhase(1, 1)
        # self.firstPhase2 = 1

        # self.bhBlackList.extend(["s31089", "s32392", "s31146", "b23271", "s31253", "s31259", "s31152", "b23274",
        #                          "b23360", "n112005", "b23361", "c31935", "s31294", "s31327", "s32943", "n111977",
        #                          "s31324", "s31297", "c31296", "n112915", "b23235", "s31267", "s31150",
        #                          "c31293", "c31326", "n112022", "n112029", "c31803", "s31803", "s31296", "n112061",
        #                          "s31325", "s31851", "n112875", "n112464", "n112491", "n112501", "n112461", "c31936",
        #                          "n112524", "s33455"
        #                          ])
        # self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        # key: 技能标志ID
        # array: 技能名，技能颜色，技能ID
        self.baiZhanRaw = [["一刀柄锤", "yellow", ["28030", "30599", "28216"]],  # 2
                           ["枪法炎罗", "yellow", ["28105", "30665", "28107", "28941"]],  # 2
                           ["一闪天诛", "yellow", ["28126", "30592", "28266"]],  # 2
                           ["一闪无痕", "yellow", ["28127", "30593", "33579"]],  # 2
                           ["黑煞落贪狼", "yellow", ["28193", "30787", "28194", "28201"]],  # 2
                           ["枪法散阵", "yellow", ["28300", "28320", "30142"]],  # 2
                           ["居合贯诚", "yellow", ["28769", "28770", "30611", "30612"]],  # 2
                           ["飞云回转刀", "yellow", ["28781", "30793", "28791"]],  # 2
                           ["奔狼踏月式", "yellow", ["28911", "28913", "30673", "28111"]],  # 2
                           ["五行术雷震", "yellow", ["28940", "30618"]],  # 2
                           ["散阵枪", "yellow", ["28960", "28964", "30543"]],  # 2
                           ["枪断晴川", "yellow", ["29096", "31641", "29198", "27581"]],  # 2
                           ["陀罗曲破镜", "yellow", ["32014", "32050", "32015"]],  # 2
                           ["巨猿劈山", "yellow", ["28303", "30604"]],  # 1
                           ["剑心通明", "blue", ["28321", "30676", "28390", "28391"]],  # 2
                           ["帝骖龙翔", "blue", ["28324", "30687", "28358"]],  # 2
                           ["九阴封脉指", "blue", ["28527", "28528", "30583"]],  # 2
                           ["幽冥指", "blue", ["28801", "30643"]],  # 2
                           ["血涂风暴", "blue", ["28803", "30655"]],  # 2
                           ["阴阳术退散", "blue", ["28942", "30620"]],  # 2
                           ["踏月式掠途", "blue", ["28956", "30679", "32960", "28957"]],  # 2
                           ["冥府滑行", "blue", ["29097", "31652", "33193", "29152"]],  # 2
                           ["尸鬼封烬", "blue", ["29121", "30580"]],  # 2
                           ["兔死狐悲", "blue", ["29347", "30696", "29348", "30697", "29662"]],  # 1
                           ["破裂", "green", ["28174", "30131"]],  # 2
                           ["一刀浮尘", "green", ["28178", "30136"]],  # 2
                           ["七荒黑牙", "green", ["28487"]],  # 2
                           ["百步缠丝手", "green", ["28772", "30614"]],  # 2
                           ["伤寒刺骨针", "green", ["29639", "30702"]],  # 2
                           ["枪法蝮蛇", "green", ["33595", "33602"]],  # 2
                           ["毒指功", "green", ["33599", "33601"]],  # 2
                           ["暗狼袭爪", "red", ["28146", "30785"]],  # 2
                           ["凶刃乱舞", "red", ["28306", "30569", "28313"]],  # 2
                           ["花钱消灾", "red", ["28493", "30741", "28702"]],  # 2
                           ["土崩炸弹", "red", ["28778", "30822"]],  # 2
                           ["气血蚕食法", "red", ["28779", "30804"]],  # 2
                           ["火魅指", "red", ["28802", "30644"]],  # 2
                           ["仇恨咆哮", "red", ["29111", "30550"]],  # 1
                           ["三阳穿心掌", "red", ["29343", "30692"]],  # 2
                           ["血龙甩尾", "red", ["29344", "30693"]],  # 2
                           ["龙象般若功", "red", ["29952", "31801", "32241", "32242"]],  # 2
                           ["暗龙火冲", "red", ["32023", "32052"]],  # 2
                           ["空穴来风", "purple", ["28029", "28041", "28044", "30535", "30590"]],  # 2
                           ["初景白雨", "purple", ["28128", "30594"]],  # 2
                           ["通世金诀", "purple", ["28492", "29917", "29918", "30747"]],  # 2
                           ["斗转金移", "purple", ["28497", "30606"]],  # 2
                           ["漾剑式", "purple", ["28525", "30582"]],  # 2
                           ["定波式", "purple", ["28570", "28571", "30137"]],  # 2
                           ["陀罗曲波纹", "purple", ["29012", "30810", "29033", "29034", "29035"]],  # 2
                           ["五灵加护", "black", ["29123", "30642", "29127"]],  # 1
                           ["华散曲黑洞", "black", ["32011", "32049"]],  # 2
                           ["破竹返", "passive", ["28129", "30595", "28179"]],  # 2
                           ["枪法铁林", "passive", ["33194"]],  # 2
                           ["杀红眼", "passive", ["28823", "28337"]],  # 2
                           ["归潮长生法", "passive", ["28554", "30587", "28557"]],  # 2
                           ["凌云步", "passive", ["29014", "30807"]],  # 2
                           ["气刃法", "passive", ["29054", "30627"]],  # 2
                           ["画影飞赴", "passive", ["29098", "30809"]],  # 1
                           ["天养生息法", "passive", ["29643", "30100", "30705", "30709", "30711", "29909"]],  # 2
                           ["顽抗", "passive", ["28330", "30765", "29905"]],  # 1
                           ["蝮蛇召唤", "normal", ["28495", "30631", "28500", "33042"]],  # 2
                           ["炼蛇花召唤", "normal", ["28496", "28763", "30635", "28686", "29099"]],  # 2
                           ["梁上君子", "normal", ["28767", "30609"]],  # 2
                           ["渐影凝视", "normal", ["28768", "30610", "28777"]],  # 2
                           ["傲然刀势", "normal", ["28780", "30792"]],  # 2
                           ["内力潮汐", "normal", ["28945", "30626"]],  # 2
                           ["五行术土遁", "normal", ["28959", "30542"]],  # 2
                           ["逆心转脉", "normal", ["29460", "30698", "29461", "30699"]],  # 2
                           ["特制止血钳", "normal", ["29633", "30700"]],  # 2
                           ["麻沸散", "normal", ["29648", "30701"]],  # 2
                           ["玄珠花蜜", "normal", ["29954", "30714", "30110"]],  # 2
                           ["红蝠掠影", "normal", ["32016", "32018", "32051"]],  # 2
                           ["特制金疮药", "normal", ["28176", "30536"]],  # 2
                           ["麝鹿续命丸", "normal", ["28302", "30603"]],  # 2
                           ["武傀召来", "normal", ["29052", "30755"]],  # 2
                           ["毓秀灵药", "normal", ["28304", "30670"]],  # 2
                           ["万蛇骨", "normal", ["28491", "30947", "28586"]],  # 2
                           ["万花金创药", "normal", ["28607", "30608"]],  # 2
                           ["土灵道符", "normal", ["28943", "28944", "30621"]],  # 2
                           ["皓莲望月", "normal", ["28967", "30766"]],  # 2
                           ["陀罗曲静壁", "normal", ["29011", "30815", "29015"]],  # 2
                           ["积气法门", "normal", ["28133", "28132", "30781"]],  # 2
                           ["霞月长针", "normal", ["28135", "28136", "28137", "30782"]],  # 2
                           ["兵犬丸", "normal", ["28152", "30566"]],  # 2
                           ]

        self.baiZhanLine = {}
        for i in range(len(self.baiZhanRaw)):
            line = self.baiZhanRaw[i]
            for id in line[2]:
                self.baiZhanLine[id] = i


        # 破绽名，破绽类型(伤害/读条/喊话)，触发名，破绽颜色，破绽等级，是否会重复触发（用于强制刷新）
        self.poZhanRaw = [["未知技能", "", "", "white", "?"],
                          ["五行术·震雷", "castname", "五行术·震雷", "yellow", "2"],  # 华鹤炎
                          ["五行术·土盾", "skillid", "33537", "white", "3"],
                          ["逃跑", "shout", '"失算了，来人！给我拦住他们……"', "white", "3"],
                          ["阴阳术·咒印", "skillid", '29239', "white", "1"],  # 源明雅
                          ["火圈", "skillname", '火圈', "blue", "2"],
                          ["尸鬼封烬", "castname", '尸鬼封烬', "red", "3"],
                          ["剑流痕", "skillname", '剑流痕', "yellow", "1"],  # 方宇谦
                          ["召唤流云剑", "castname", '召唤流云剑', "purple", "3"],
                          ["九音陀罗曲·破浪", "castid", '33637', "white", "1/3"],  # 提多罗吒
                          ["九音陀罗曲·破镜", "castid", '31480', "white", "1"],
                          ["九音陀罗曲·刚震", "castname", '九音陀罗曲·刚震', "yellow", "2"],
                          ["黑煞落贪狼", "skillname", '暗狼蚀日', "white", "2/3"],  # 秦雷
                          ["心眼泯灭", "castname", '心眼泯灭', "red", "2"],
                          ["枪断晴川", "castname", '枪断晴川', "yellow", "1"],  # 陆寻
                          ["冥府滑行", "skillname", '冥府滑行', "white", "1/2"],
                          ["横戈平潮", "skillname", '横戈平潮', "blue", "2/3"],
                          ["九渊寒刺", "castname", '九渊寒刺', "yellow", "1"],
                          ["一刀·破竹割", "skillname", '一刀·破竹割', "yellow", "1"],  # 上衫勇刀
                          ["枪法·散阵", "skillname", '枪法·散阵', "white", "1"],
                          ["枪法·铁林", "castname", '枪法·铁林', "white", "2"],
                          ["万蛇骨", "castname", '万蛇骨', "white", "1"],  # 肖童
                          ["软蝮鞭", "skillname", '软蝮鞭', "yellow", "1"],
                          ["欠债", "skillname", '欠债', "white", "2"],  # 冯度
                          ["还钱", "skillname", '还钱', "yellow", "1"],
                          ["骰子", "shout", '"我们来玩一些更好玩的。"', "white", "3"],
                          ["钱袋", "shout", '"没意思，换个玩法，你我且来试一试，这运气呐，是谁的更好。"', "white", "2"],
                          ["华佗天灵切", "castname", '华佗天灵切', "green", "3"],  # 程沐华
                          ["特制止血钳", "castname", '特制止血钳', "red", "2"],
                          ["天养生息法", "castname", '天养生息法', "black", "2"],
                          ["豪气剑空", "skillname", '豪气剑空', "purple", "2/3"],  # 谢云流
                          ["纵断千浪", "castname", '纵断千浪', "purple", "2"],
                          ["纵断千浪", "skillname", '纵断千浪', "yellow", "1"],
                          ["居合·贯诚", "castname", '居合·贯诚', "yellow", "1"],
                          ["百刃斩魔（空精）", "shout", '"现下精神不振，且饶你们一次。"', "yellow", "2"],
                          ["外层扩张", "skillname", '外层扩张', "white", "3"],  # 武逸青
                          ["土崩炸弹", "castname", '土崩炸弹', "white", "3"],
                          ["地鼠土甲盾", "skillname", '浮光暗爪风', "green", "3"],
                          ["黑血甲壳", "skillname", '吸血之法', "green", "3"],
                          ["葬魂钉", "castname", '葬魂钉', "blue", "3"],  # 韦柔丝
                          ["逆心转脉", "castname", '逆心转脉', "black", "3"],
                          ["赤龙瞪目", "castname", '赤龙瞪目', "blue", "2"],
                          ["傲然刀势", "castname", '傲然刀势', "red", "2"],  # 卫栖梧
                          ["百步缠丝手", "skillname", '百步缠丝手', "yellow", "3"],
                          ["巧蛛八手", "skillname", '巧蛛八手', "blue", "3"],
                          ["一闪·破竹", "skillname", '一闪·破竹', "white", "1"],  # 鬼影小次郎
                          ["一闪·天诛", "castname", '一闪·天诛', "purple", "2/3"],
                          ]

        self.castNameLine = {}
        self.skillNameLine = {}
        self.shoutLine = {}
        self.skillIdLine = {}
        self.castIdLine = {}

        for i in range(len(self.poZhanRaw)):
            line = self.poZhanRaw[i]
            if line[1] == "castname":
                self.castNameLine[line[2]] = i
            elif line[1] == "skillname":
                self.skillNameLine[line[2]] = i
            elif line[1] == "shout":
                self.shoutLine[line[2]] = i
            elif line[1] == "skillid":
                self.skillIdLine[line[2]] = i
            elif line[1] == "castid":
                self.castIdLine[line[2]] = i

        self.bhInfo = {}

        self.baiZhanSkill = {}  # 记录玩家放过的百战技能
        self.detail["pozhanList"] = []
        self.baiZhanLastSkill = {}  # 记录玩家上一次对每个目标放过的百战技能
        self.poZhanSaveTarget = {}  # 记录上次出现破绽的目标
        self.poZhanAppear = {}  # 上次出现破绽，并且没有记录的时间

        self.poZhanStatus = {}  # 是否处于破绽期间
        self.poZhanStart = {}  # 第一次触发破绽的时间
        self.poZhanLast = {}  # 上一次触发破绽的时间
        self.poZhanNum = {}  # 触发破绽的次数
        self.poZhanSkill = {}  # 上一次施放的可能触发破绽的技能
        self.poZhanSkillRecord = {}  # 上一次施放的可能触发破绽的技能
        self.poZhanResult = {}  # 累计受到的触发破绽的百战技能

        self.yuanmingyaActive = 0

        for line in self.bld.info.player:
            # self.stat[line].extend([0, 0, 0])
            self.statDict[line]["battle"] = {"skill1": {},
                                             "skill2": {},
                                             "skill3": {},
                                             "jingliDeal": 0,
                                             "nailiDeal": 0,
                                             "jingliTaken": 0,
                                             "nailiTaken": 0,
                                             "jingliHeal": 0,
                                             "nailiHeal": 0}
            self.baiZhanSkill[line] = {}
            self.baiZhanLastSkill[line] = {}
            self.poZhanSaveTarget[line] = "0"
            self.poZhanAppear[line] = 0

        for line in self.bld.info.npc:
            self.poZhanStatus[line] = 0
            self.poZhanStart[line] = 0
            self.poZhanLast[line] = 0
            self.poZhanNum[line] = 0
            self.poZhanSkill[line] = 0
            self.poZhanSkillRecord[line] = 0
            self.poZhanResult[line] = []

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


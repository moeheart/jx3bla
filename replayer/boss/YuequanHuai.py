# Created by moeheart at 09/16/2023
# 月泉淮的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class YuequanHuaiWindow(SpecificBossWindow):
    '''
    翁幼之的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("月泉淮", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        # tb.AppendHeader("本体DPS", "对张景超的DPS。\n常规阶段时间：%s" % parseTime(self.detail["P1Time"]))
        # tb.AppendHeader("双体1DPS", "第一次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time1"]))
        # tb.AppendHeader("双体2DPS", "第二次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time2"]))
        tb.AppendHeader("分身伤害", "对P1[暗梦仙体的幻影]的伤害，注意这个伤害没有除以时间。")
        tb.AppendHeader("P1DPS", "对P1[暗梦仙体]的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "对P2[月泉淮]在100%%-60%%蓝量期间的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("被命中", "被P1的技能命中导致BOSS回蓝的次数")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["fenshenDPS"]))
            tb.AppendContext(int(line["battle"]["P1DPS"]))
            tb.AppendContext(int(line["battle"]["P2DPS"]))
            tb.AppendContext(int(line["battle"]["damageTaken"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class YuequanHuaiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                res = self.getBaseList(id)
                res["battle"]["P1DPS"] = int(safe_divide(res["battle"]["P1DPS"], self.detail["P1Time"]))
                res["battle"]["P2DPS"] = int(safe_divide(res["battle"]["P2DPS"], self.detail["P2Time"]))
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

        idRemoveList = []
        for id in self.fenshen:
            if self.fenshen[id]["alive"] == 0 and event.time - self.fenshen[id]["lastDamage"] > 500:
                time = parseTime((event.time - 500 - self.startTime) / 1000)
                self.addPot([self.bld.info.getName(self.fenshen[id]["lastID"]),
                             self.occDetailList[self.fenshen[id]["lastID"]],
                             0,
                             self.bossNamePrint,
                             "%s分身被击破" % time,
                             self.fenshen[id]["damageList"],
                             0])
                idRemoveList.append(id)
        for id in idRemoveList:
            del self.fenshen[id]

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
                                self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

                # if event.id in ["35485", "35490", "35486", "35493"]:
                #     print("[Skill]", parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.target), event.damage, event.damageEff, 
                #         self.bld.info.getSkillName(event.full_id), event.id)


                if event.id in ["32514", "32520", "32547", "36249", "36250", "36248"]:
                    self.statDict[event.target]["battle"]["damageTaken"] += 1

                if event.id in ["32529", "32535", "32540"]:
                    # print("[Damage]", event.id, parseTime((event.time - self.startTime) / 1000), self.bld.info.getName(event.target), event.damage, event.damageEff)
                    if self.lostBuff[event.target]:
                        self.addPot([self.bld.info.player[event.target].name,
                                    self.occDetailList[event.target],
                                    1,
                                    self.bossNamePrint,
                                    "丢失buff导致承伤失败",
                                    [],
                                    0])
                    else:
                        self.addPot([self.bld.info.player[event.target].name,
                                    self.occDetailList[event.target],
                                    1,
                                    self.bossNamePrint,
                                    "未获得buff，不应该承伤",
                                    [],
                                    0])

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["月泉淮", "暗梦仙体"]:
                            self.bh.setMainTarget(event.target)
                        if self.bld.info.getName(event.target) in ["暗梦仙体"]:
                            self.statDict[event.caster]["battle"]["P1DPS"] += event.damageEff
                        if self.bld.info.getName(event.target) in ["月泉淮"]:
                            self.statDict[event.caster]["battle"]["P2DPS"] += event.damageEff
                        if self.bld.info.getName(event.target) in ["暗梦仙体的幻影"]:
                            self.statDict[event.caster]["battle"]["fenshenDPS"] += event.damageEff
                            if event.target not in self.fenshen:
                                self.fenshen[event.target] = {"lastDamage": event.time, "alive": 1, "damageList": [], "lastName": "未知"}
                            if event.damage > 0:
                                skillName = self.bld.info.getSkillName(event.full_id)
                                name = self.bld.info.getName(event.caster)
                                resultStr = ""
                                value = event.damage
                                self.fenshen[event.target]["damageList"] = ["-%s, %s:%s%s(%d)" % (
                                        parseTime((int(event.time) - self.startTime) / 1000), name, skillName, resultStr, value)] + self.fenshen[event.target]["damageList"]
                                if len(self.fenshen[event.target]["damageList"]) > 20:
                                    del self.fenshen[event.target]["damageList"][20]
                                self.fenshen[event.target]["lastDamage"] = event.time
                                self.fenshen[event.target]["lastID"] = event.caster

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
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")
                
            if event.id in ["26606", "26694"]:
                num = event.stack
                if num > 1:
                    num = 1
                self.stunCounter[event.target].setState(event.time, num)

            if event.id == "26597":
                if event.stack < self.buffLayers[event.target]:
                    self.lostBuff[event.target] = 1
                self.buffLayers[event.target] = event.stack

        elif event.dataType == "Shout":
            if event.content in ['"谁？！别过来！别逼我出手！"']:
                pass
            elif event.content in ['"……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"看招！"']:
                pass
            elif event.content in ['"再接我这招！"']:
                pass
            elif event.content in ['"哈啊！！！"']:
                pass
            elif event.content in ['"哦？能和老夫的暗梦仙体周旋这么久，看来你长进不小。"']:
                self.changePhase(event.time, 0)
            elif event.content in ['"......"']:
                self.win = 1
                self.changePhase(event.time, 0)
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"哼，这点内力实在微不足道"']:
                pass
            elif event.content in ['"嗯？何等侥幸？！这些伎俩似曾相识，但为何让老夫心生厌恶！"']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["翁幼之宝箱", "??寶箱"]:
            #     self.win = 1
            #     self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")

            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name == "暗梦仙体的幻影":
                pass
                #print("[Huanying]", parseTime((event.time - self.startTime) / 1000), event.id, self.bld.info.npc[event.id].templateID)

        elif event.dataType == "Death":  # 重伤记录
            pass
            if event.id in self.fenshen:
                self.fenshen[event.id]["alive"] = 0
                self.fenshen[event.id]["lastDamage"] = event.time

        elif event.dataType == "Battle":  # 战斗状态变化
            pass
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name == "暗梦仙体的幻影":
                pass
                #print("[Huanying2]", parseTime((event.time - self.startTime) / 1000), event.id, event.fight, event.hpMax)

        elif event.dataType == "Alert":  # 系统警告框
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 2000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")
            # if self.bld.info.getSkillName(event.full_id) in ["血影坠击", "怨·黄泉鬼步"]:
            #     print("[Xueyingzhuiji]", event.id, parseTime((event.time - self.startTime) / 1000))
                if event.id == "35491":
                    if self.phase == 0:
                        self.bh.setBadPeriod(self.phaseStart, event.time, True, False)
                        self.changePhase(event.time, 2)

                    
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
        self.activeBoss = "月泉淮"
        self.debug = 1

        self.initPhase(2, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["s32514", "b26823", "s32392", "s32549", "s32540", "s32544", "s32516", "s36249", "s32567",
                                 "s32519", "s32520", "s36250", "n124637", "s36248", "s32547", "s36162", "s35511", "s32535",
                                 "s32570", "s32548", "s32529", "n125069", "n125071", "s35489", "b26688", "s35491", "s35549",
                                 "s35851", "s35852", "n124991", "b26606", "s35850", "s35488", "b26605",
                                 "b26691", "b26719", "s35493", "s35493", "s35486", "s35490", "s35485", "b26604", "s35482",
                                 "s35484", "b26694", "s35849", "s35481", "c35494", "s32563", "s35487", "s35854", "s35856",
                                 "s35847"

                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       "c32547": ["3428", "#ff0000", 3000],  # 月铳
                       # b26662 凝视
                       "c32519": ["3312", "#ff7777", 750],  # 迦楼罗连闪·挑飞
                       "c32518": ["4528", "#7700ff", 0],  # 月盈
                       "c32568": ["4529", "#ff00ff", 0],  # 月落
                       "c32557": ["2031", "#ff77ff", 9375],  # 月蚀
                       "c32545": ["2144", "#00ff00", 6000],  # 月华天相
                       "c32548": ["3407", "#00ffff", 2000],  # 振翅
                       "c35491": ["3407", "#00ff77", 2000],  # 内力汲取
                       "c35548": ["3407", "#77ff77", 2000],  # 夺命碧波剑
                       "c32564": ["3407", "#0000ff", 4000],  # 月引
                       "c32559": ["3407", "#0000ff", 4000],  # 月引
                       "c36389": ["3407", "#777700", 0],  # 五行技·水
                       "c36388": ["3407", "#77ff77", 0],  # 五行技·木
                       "c36390": ["3407", "#77ff77", 0],  # 五行技·火
                       "c36391": ["3407", "#77ff77", 0],  # 五行技·土
                       "s35847": ["3407", "#77ff77", 0],  # 五行技·金
                       "c35527": ["3407", "#77ff77", 0],  # 五行技·终结技
                       }

        # 数据格式：
        # 7

        self.lostBuff = {}
        self.buffLayers = {}
        self.fenshen = {}

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"fenshenDPS": 0,
                                             "P1DPS": 0,
                                             "P2DPS": 0,
                                             "damageTaken": 0,}
            self.buffLayers[line] = 0
            self.lostBuff[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


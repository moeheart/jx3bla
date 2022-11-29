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
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

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

        self.countFinalOverall()
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

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

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

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

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if self.bld.info.getName(event.target) in ["李重茂"]:
                        self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["btDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["一刀流精锐武士", "一刀流精銳武士", "永王叛军长枪兵", "永王叛军剑卫", "永王叛軍長槍兵", "永王叛軍劍衛"]:
                        self.statDict[event.caster]["battle"]["xgDPS"] += event.damageEff

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
                pass
            elif event.content in ['"师兄.....师兄你在哪？有人要害我！"']:
                pass
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

        self.initPhase(4, 1)

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

        self.qiangbingStart = {}

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"btDPS": 0,
                                             "xgDPS": 0}
            self.qiangbingStart[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


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
        self.constructWindow("月泉淮", "1400x900")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("P1DPS", "对P1[暗梦仙体]的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("修血", "在[月华天相·满月]结束后，对前两只P1[金翅鸟化身]造成的伤害。\n这个伤害越快，治疗的容错就越高，是通过这个治疗检测的关键。\n注意这个伤害没有除以时间。")
        tb.AppendHeader("回蓝", "被P1的技能命中导致BOSS回蓝的次数。")
        tb.AppendHeader("P2DPS", "对P2[月泉淮]在100%%-60%%蓝量期间的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("P3月崩击", "P3[月崩击]期间对[暗梦仙体]的DPS。将所有流程相加计算。\n阶段持续时间：%s" % parseTime(self.detail["P3ybjTime"]))
        tb.AppendHeader("月茧", "P3[月茧]期间对[暗梦仙体]的DPS。将所有流程相加计算。\n阶段持续时间：%s" % parseTime(self.detail["P3yjTime"]))
        tb.AppendHeader("1-1", "P3的第一次[月泉天引]期间，对第一轮[掩日]的总伤害。")
        tb.AppendHeader("1-2", "P3的第一次[月泉天引]期间，对第二轮[掩日]的总伤害。\n这是这个阶段的关键所在。")
        tb.AppendHeader("1分组", "P3的第一次[月泉天引]期间，根据五行buff推测的分组顺位。\n如果吃到了错误的buff，可能导致这个分组不正确，但这正好可以指出错误。\n灰色表示无分组，红色表示没有被落剑推过。")
        # tb.AppendHeader("1用时", "P3的第一次[月泉天引]期间，从获得buff到上点花费的时间。\n这是这个阶段的关键所在。")
        tb.AppendHeader("2-1", "P3的第二次[月泉天引]期间，对第一轮[掩日]的总伤害。")
        tb.AppendHeader("2-2", "P3的第二次[月泉天引]期间，对第二轮[掩日]的总伤害。\n这是这个阶段的关键所在。")
        tb.AppendHeader("2分组", "P3的第二次[月泉天引]期间，根据五行buff推测的分组顺位。\n如果吃到了错误的buff，可能导致这个分组不正确，但这正好可以指出错误。\n灰色表示无分组，红色表示没有被落剑推过。")
        # tb.AppendHeader("2用时", "P3的第二次[月泉天引]期间，从获得buff到上点花费的时间。\n这是这个阶段的关键所在。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["P1DPS"]))
            tb.AppendContext(int(line["battle"]["xiuxue"]))
            tb.AppendContext(int(line["battle"]["damageTaken"]))
            tb.AppendContext(int(line["battle"]["P2DPS"]))
            tb.AppendContext(int(line["battle"]["ybj"]))
            tb.AppendContext(int(line["battle"]["yj"]))
            tb.AppendContext(int(line["battle"]["yr11"]))
            tb.AppendContext(int(line["battle"]["yr12"]))
            if int(line["battle"]["yr1group"]) == 0:
                tb.AppendContext(int(line["battle"]["yr1group"]), color="#777777")
            elif int(line["battle"]["yr1hit"]) == 1:
                tb.AppendContext(int(line["battle"]["yr1group"]), color="#000000")
            else:
                tb.AppendContext(int(line["battle"]["yr1group"]), color="#ff0000")
            # tb.AppendContext(int(line["battle"]["yr1delay"] / 10) / 100)
            tb.AppendContext(int(line["battle"]["yr21"]))
            tb.AppendContext(int(line["battle"]["yr22"]))
            if int(line["battle"]["yr2group"]) == 0:
                tb.AppendContext(int(line["battle"]["yr2group"]), color="#777777")
            elif int(line["battle"]["yr2hit"]) == 1:
                tb.AppendContext(int(line["battle"]["yr2group"]), color="#000000")
            else:
                tb.AppendContext(int(line["battle"]["yr2group"]), color="#ff0000")
            # tb.AppendContext(int(line["battle"]["yr2delay"] / 10) / 100)

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
        self.detail["P3ybjTime"] = int(self.phaseTime[3] / 1000)
        self.detail["P3yjTime"] = int(self.phaseTime[4] / 1000)

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
                res["battle"]["ybj"] = int(safe_divide(res["battle"]["ybj"], self.detail["P3ybjTime"]))
                res["battle"]["yj"] = int(safe_divide(res["battle"]["yj"], self.detail["P3yjTime"]))
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

                if event.id in ["35489"]:  # 月衍万化·初式
                    if self.phase == 0:
                        self.bh.setBadPeriod(self.phaseStart, event.time, True, False)
                        self.bh.setBadPeriod(self.p1healerEndTime, event.time, False, True)
                        self.changePhase(event.time, 2)

                if event.id in ["32527", "32529"]:  # 月华天相·满月
                    self.countP1last = 2
                    # print("[Manyue]", parseTime((event.time - self.startTime) / 1000))

                if event.id in ["35528"] and self.p33Group[event.target] != 0:  # 落剑
                    self.p33YanriHit[event.target] = 1
                    self.statDict[event.target]["battle"]["yr%dhit" % self.p3yqtyTime] = 1

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["月泉淮", "暗梦仙体"] and self.phase in [1,2]:
                            self.bh.setMainTarget(event.target)
                        if self.bld.info.getName(event.target) in ["暗梦仙体"] and self.phase == 1:
                            self.statDict[event.caster]["battle"]["P1DPS"] += event.damageEff
                        if self.bld.info.getName(event.target) in ["月泉淮"] and self.phase == 2:
                            self.statDict[event.caster]["battle"]["P2DPS"] += event.damageEff
                        if self.bld.info.getName(event.target) in ["金翅鸟化身"] and self.phase == 1:
                            # self.statDict[event.caster]["battle"]["fenshenDPS"] += event.damageEff
                            if event.target not in self.fenshen:
                                self.fenshen[event.target] = {"lastDamage": event.time, "alive": 1, "damageList": [], "lastName": "未知", "damageSum": {}}
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
                                if self.countP1last:
                                    if event.caster not in self.fenshen[event.target]["damageSum"]:
                                        self.fenshen[event.target]["damageSum"][event.caster] = 0
                                    self.fenshen[event.target]["damageSum"][event.caster] += event.damageEff

                        if self.bld.info.getName(event.target) in ["暗梦仙体"] and self.bld.info.npc[event.target].templateID in ["123830"]:
                            self.statDict[event.caster]["battle"]["ybj"] += event.damageEff
                            if self.p31Ready:
                                self.bh.setBadPeriod(self.phaseStart, event.time, True, False)
                                self.changePhase(event.time, 3)
                                self.p31Ready = 0
                                self.p3amxtCount = 2
                        if self.bld.info.getName(event.target) in ["暗梦仙体", "被束缚的暗梦仙体"] and self.bld.info.npc[event.target].templateID in ["123809", "123808"]:
                            self.statDict[event.caster]["battle"]["yj"] += event.damageEff
                            if self.p32Ready:
                                self.bh.setBadPeriod(self.phaseStart, event.time, True, False)
                                self.changePhase(event.time, 4)
                                self.p32Ready = 0
                                self.p3amxtCount = 4
                        if self.bld.info.getName(event.target) in ["掩日"]:
                            if self.p3yrTime in [1,2] and self.p3yqtyTime in [1,2]:
                                self.statDict[event.caster]["battle"]["yr%d%d" % (self.p3yqtyTime, self.p3yrTime)] += event.damageEff

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

            if event.id == "26957" and event.stack > 0:  # 内力聚集
                if self.phase == 4:
                    # 强制结束阶段
                    self.changePhase(event.time, 0)

            if event.id == "26599" and event.stack == 1:  # 金之形
                if self.startWuxing == -1 or event.time - self.startWuxingProtect < 500:
                    self.startWuxing = 0
                    self.startWuxingProtect = event.time
                    self.p33Group[event.target] = 1
                if self.p33Ready:
                    self.p33Group[event.target] = (self.startWuxing * 2) % 5 + 1
                    self.p33Active[event.target] = event.time

            if event.id == "26601" and event.stack == 1:  # 水之形
                if self.startWuxing == -1 or event.time - self.startWuxingProtect < 500:
                    self.startWuxing = 1
                    self.startWuxingProtect = event.time
                    self.p33Group[event.target] = 1
                if self.p33Ready:
                    self.p33Group[event.target] = (self.startWuxing * 2 + 3) % 5 + 1
                    self.p33Active[event.target] = event.time

            if event.id == "26600" and event.stack == 1:  # 木之形
                if self.startWuxing == -1 or event.time - self.startWuxingProtect < 500:
                    self.startWuxing = 2
                    self.startWuxingProtect = event.time
                    self.p33Group[event.target] = 1
                if self.p33Ready:
                    self.p33Group[event.target] = (self.startWuxing * 2 + 1) % 5 + 1
                    self.p33Active[event.target] = event.time

            if event.id == "26602" and event.stack == 1:  # 火之形
                if self.startWuxing == -1 or event.time - self.startWuxingProtect < 500:
                    self.startWuxing = 3
                    self.startWuxingProtect = event.time
                    self.p33Group[event.target] = 1
                if self.p33Ready:
                    self.p33Group[event.target] = (self.startWuxing * 2 + 4) % 5 + 1
                    self.p33Active[event.target] = event.time

            if event.id == "26603" and event.stack == 1:  # 土之形
                if self.startWuxing == -1 or event.time - self.startWuxingProtect < 500:
                    self.startWuxing = 4
                    self.startWuxingProtect = event.time
                    self.p33Group[event.target] = 1
                if self.p33Ready:
                    self.p33Group[event.target] = (self.startWuxing * 2 + 2) % 5 + 1
                    self.p33Active[event.target] = event.time

            # if event.id == "26715" and event.stack == 1:  # 激活
            #     if self.p33Group[event.target] != 0 and self.p3yqtyTime in [1,2] and self.statDict[event.target]["battle"]["yr%ddelay" % self.p3yqtyTime] == 0:
            #         self.statDict[event.target]["battle"]["yr%ddelay" % self.p3yqtyTime] = event.time - self.p33Active[event.target]
            #         self.statDict[event.target]["battle"]["yr%dgroup" % self.p3yqtyTime] = self.p33Group[event.target]

            if event.id == "26715" and event.stack == 0:  # 激活
                if event.time - self.p33Start < 35500 and self.p33YanriHit[event.target] == 0:
                    time = parseTime((event.time - self.startTime) / 1000)
                    self.addPot([self.bld.info.getName(event.target),
                                 self.occDetailList[event.target],
                                 0,
                                 self.bossNamePrint,
                                 "%s提前离开卦点" % time,
                                 [],
                                 0])

        elif event.dataType == "Shout":
            if event.content in ['"谁？！别过来！别逼我出手！"']:
                pass
            elif event.content in ['"……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"哼！可怜的东西！"']:
                pass
            elif event.content in ['"烦人的苍蝇解决了……吕洞宾，老夫倒要看看，你在这龙脉下面，究竟藏了什么！"']:
                pass
            elif event.content in ['"幻惑化生，破！"']:
                pass
            elif event.content in ['"哦？能和老夫的暗梦仙体周旋这么久，看来你长进不小。"']:
                self.changePhase(event.time, 0)
                self.p1healerEndTime = event.time
            elif event.content in ['"......"']:
                self.win = 1
                self.changePhase(event.time, 0)
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"哼，这点内力实在微不足道"']:
                pass
            elif event.content in ['"嗯？何等侥幸？！这些伎俩似曾相识，但为何让老夫心生厌恶！"']:
                pass
            elif event.content in ['"哦？竟能扛住老夫的暗梦仙体，看来着实轻看了你们这些蝼蚁……"']:
                self.changePhase(event.time, 0)
            elif event.content in ['"......."']:
                pass
            elif event.content in ['"哼！无聊透顶！"']:
                pass
            elif event.content in ['"各位施主，请至小僧身后！"']:
                self.p1healerEndTime = event.time
            elif event.content in ['"轮到这群蝼蚁了，老夫瞬间就能让你们……消失~"']:
                pass
            elif event.content in ['"吕洞宾的徒儿们？来得正好！"']:
                self.changePhase(event.time, 0)
            elif event.content in ['"诸位侠士请退下！之后便交给我等，结阵！"']:
                pass
            elif event.content in ['"侠士，请你收集月泉淮击碎的石碑，上面或许有师父留下的信息。"']:
                pass
            elif event.content in ['"这股浊气……不好！"']:
                pass
            elif event.content in ['"这是……有余以奉天下……"']:
                pass
            elif event.content in ['"……唯有道者，原来这便是天道剑阵的关键。"']:
                pass
            elif event.content in ['"纯阳门下，结天道剑阵！"']:
                self.p2healerEndTime = event.time
            elif event.content in ['"哦？这就是吕洞宾所留下的招式，让老夫看看谁更甚一筹。"']:
                self.bh.setBadPeriod(self.p2healerEndTime, event.time, False, True)
            elif event.content in ['"让老夫看看你们负隅顽抗的丑态！"']:
                if self.p3yqtyTime in [1,2]:
                    for player in self.bld.info.player:
                        self.statDict[player]["battle"]["yr%dgroup" % self.p3yqtyTime] = self.p33Group[player]
                self.p31Ready = 1
                self.p33Ready = 0
                self.p3yqtyTime += 1
                self.p3yrTime = 0
                self.startWuxing = -1
                for line in self.bld.info.player:
                    self.p33Group[line] = 0
                    self.p33YanriHit[line] = 0
            elif event.content in ['"呵呵，天地不仁以万物为刍狗，就让尔等体会一下吧！"']:
                self.p32Ready = 1
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
            elif event.content in ['"咳！"']:
                self.p33Ready = 1
            elif event.content in ['"与其流散无用，不如皆归我仙人所有……"']:
                for line in self.bld.info.player:
                    self.p33Active[line] = event.time
                self.p33Start = event.time
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
            elif event.content in ['"这些内力……吕洞宾，那么这招又如何！？"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
            elif event.content in ['"竟能破去老夫的功法，哈哈哈……有趣，有趣！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
                if self.p3yqtyTime in [1,2] and self.p33Ready:
                    for player in self.bld.info.player:
                        self.statDict[player]["battle"]["yr%dgroup" % self.p3yqtyTime] = self.p33Group[player]
            elif event.content in ['"退下！"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")

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

            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name == "掩日":
                if event.time - self.p3yrAppear > 5000:
                    self.p3yrAppear = event.time
                    self.p3yrTime += 1

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.fenshen:
                self.fenshen[event.id]["alive"] = 0
                self.fenshen[event.id]["lastDamage"] = event.time
                if self.countP1last:
                    # print("[Death]", parseTime((event.time - self.startTime) / 1000), self.countP1last)
                    # print(self.fenshen[event.id]["damageSum"])
                    for key in self.fenshen[event.id]["damageSum"]:
                        self.statDict[key]["battle"]["xiuxue"] += self.fenshen[event.id]["damageSum"][key]
                    self.countP1last -= 1
            if self.bld.info.getName(event.id) in ["暗梦仙体"] and self.bld.info.npc[event.id].templateID in ["123830"]:
                self.p3amxtCount -= 1
                if self.p3amxtCount == 0:
                    self.changePhase(event.time, 0)
            if self.bld.info.getName(event.id) in ["暗梦仙体"] and self.bld.info.npc[event.id].templateID in ["123809"]:
                self.p3amxtCount -= 1
                if self.p3amxtCount == 0:
                    self.changePhase(event.time, 0)

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
            #     if event.id == "35491":
            #         if self.phase == 0:
            #             self.bh.setBadPeriod(self.phaseStart, event.time, True, False)
            #             self.changePhase(event.time, 2)

                    
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

        self.initPhase(4, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["s32514", "b26823", "s32392", "s32549", "s32540", "s32544", "s32516", "s36249", "s32567",
                                 "s32519", "s32520", "s36250", "n124637", "s36248", "s32547", "s36162", "s35511", "s32535",
                                 "s32570", "s32548", "s32529", "n125069", "n125071", "s35489", "b26688", "s35491", "s35549",
                                 "s35851", "s35852", "n124991", "b26606", "s35850", "s35488", "b26605", "b26601",
                                 "b26691", "b26719", "s35493", "s35493", "s35486", "s35490", "s35485", "b26604", "s35482",
                                 "s35484", "b26694", "s35849", "s35481", "c35494", "s32563", "s35487", "s35854", "s35856",
                                 "s35847", "n125986", "n122939", "n123795", "n126013", "n125024", "n125278", "n123792",
                                 "n123796", "s35512", "b26649", "n123797", "b26619", "n123891", "n123892", "n123893", "n123894", "n123895",
                                 "n123896", "n123897", "n123898", "n123899", "n123900", "s35848",
                                 "n123784", "n123783", "n123785", "n123786", "n123787", "n123788", "s35524", "s35513", "n123807",
                                 "n123793", "n125095", "n125302", "n126043", "n126044", "n123832", "s35543", "s35526", "s35528", "b26617",
                                 "b26614", "n123794", "c32537", "b26718", "s32556", "c32537", "n125191", "n125093", "c32534", "s32556",
                                 "n123813", "n123878", "s35510", "b26609", "s35880", "s35883", "s35519", "s35517", "n123809", "s35525",
                                 "b26616", "n123810", "n124464", "s36000", "b26700", "s35536", "n123830", "b26650", "s35516",
                                 "n122406", "b24862", "b26600", "s35538", "s35537", "n125301", "n123782", "s35520"

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
                       "c32548": ["4522", "#0000ff", 2000],  # 振翅
                       "s32555": ["335", "#77ff00", 2000],  # 能量散逸
                       "s32536": ["4498", "#ffff77", 0],  # 天极月荡
                       "c35491": ["3404", "#ff7700", 2000],  # 内力汲取
                       "c35548": ["3408", "#ff7700", 2000],  # 夺命碧波剑
                       "c32564": ["2022", "#0000ff", 4000],  # 月引
                       "c32559": ["2022", "#0000ff", 4000],  # 月引
                       "c36389": ["4548", "#0000ff", 4000],  # 五行技·水
                       "c36388": ["4546", "#00ff00", 4000],  # 五行技·木
                       "c36390": ["4549", "#ff0000", 4000],  # 五行技·火
                       "c36391": ["4551", "#ff00ff", 8000],  # 五行技·土
                       "s35847": ["4550", "#ffff00", 4000],  # 五行技·金
                       "s35848": ["4550", "#ffff00", 4000],  # 五行技·金
                       "c35527": ["3440", "#77ff77", 4000],  # 五行技·终结技
                       "s35833": ["4498", "#ffff77", 2000],  # 天极月荡
                       "c32530": ["2023", "#0077ff", 5000],  # 内力汲取
                       "c32531": ["327", "#00ff77", 18000],  # 月崩击
                       }

        # 数据格式：
        # 7

        self.lostBuff = {}
        self.buffLayers = {}
        self.fenshen = {}

        self.countP1last = 0
        self.p1healerEndTime = 0
        self.p2healerEndTime = 0
        self.p31Ready = 0
        self.p32Ready = 0
        self.p33Ready = 0
        self.p3amxtCount = 0
        self.p3yqtyTime = 0
        self.startWuxing = 0
        self.startWuxingProtect = 0  # 第一个buff的保护判断时间
        self.p3yrTime = 0
        self.p3yrAppear = 0
        self.p33Group = {}
        self.p33Active = {}  # 计算P3-3激活的时间，也即获取五行buff的时间
        self.p33YanriHit = {}  # 有没有被掩日击中过
        self.p33Start = 0

        # P2驱散记录
        # P2打断记录
        # 技能展示 1
        # 无效时间 1
        # 阶段DPS统计 1
        # P3月泉天引 1
        # MVP去除蓄力一击，单独记录蓄力一击伤害

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"P1DPS": 0,
                                             "xiuxue": 0,
                                             "damageTaken": 0,
                                             "P2DPS": 0,
                                             "ybj": 0,
                                             "yj": 0,
                                             "yr11": 0,
                                             "yr12": 0,
                                             "yr1hit": 0,
                                             "yr1group": 0,
                                             # "yr1delay": 0,
                                             "yr21": 0,
                                             "yr22": 0,
                                             "yr2hit": 0,
                                             "yr2group": 0,
                                             # "yr2delay": 0,
                                             }
            self.buffLayers[line] = 0
            self.lostBuff[line] = 0
            self.p33Group[line] = 0
            self.p33Active[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


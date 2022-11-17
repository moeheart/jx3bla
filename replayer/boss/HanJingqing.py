# Created by moeheart at 11/03/2022
# 韩敬青的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class HanJingqingWindow(SpecificBossWindow):
    '''
    韩敬青的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("韩敬青", "1200x800")
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
            if line[0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line[0]], line[0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class HanJingqingReplayer(SpecificReplayerPro):

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
            if id in self.stat:
                line = self.stat[id]
                res = self.getBaseList(id)
                bossResult.append(res)
        bossResult.sort(key=lambda x: -x[2])
        self.effectiveDPSList = bossResult

        return self.effectiveDPSList, self.potList, self.detail, self.stunCounter

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
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if self.bld.info.getName(event.target) in ["韩敬青", "韓敬青"]:
                        self.bh.setMainTarget(event.target)
                        self.stat[event.caster][7] += event.damageEff

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

            if event.id == "24760":  # 毒液缠身
                if event.stack == 1:
                    self.bh.setCall("24760", "毒液缠身", "16540", event.time, 5000, event.target, "毒液缠身接罐子")
                    self.stunCounter[event.target].setState(event.time, 1)
                    self.stunCounter[event.target].setState(event.time + 5000, 0)

            if event.id == "23890":  # 毒技能点名标记
                if event.stack == 1:
                    self.bh.setCall("23890", "点名标记", "2027", event.time, 0, event.target, "点名去BOSS的另一侧排buff")
                    # self.stunCounter[event.target].setState(event.time, 1)
                    # self.stunCounter[event.target].setState(event.time + 3000, 0)

        elif event.dataType == "Shout":
            if event.content in ['"好，好！就用你们来试试我的蛊毒..."']:
                pass
            elif event.content in ['"奔涌吧！"']:
                pass
            elif event.content in ['"号哭吧！"']:
                pass
            elif event.content in ['"嘿嘿嘿...蛊毒早已渗入泉眼，你们都要葬身于此！桑乔，我给你报仇了…….."']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"感受我的痛苦！"']:
                pass
            elif event.content in ['"为你们的罪行付出代价！"']:
                self.bh.setBadPeriod(event.time, event.time + 18000, True, True)
            elif event.content in ['"谢谢各位。"']:
                pass
            elif event.content in ['"如此……依计行事。"']:
                pass
            elif event.content in ['"是。"']:
                pass
            elif event.content in ['"什么人？"']:
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
        self.activeBoss = "韩敬青"

        self.initPhase(1, 1)

        self.bhBlackList.extend(["n112021", "s32128", "b23868", "n113050", "n113050", "s32127", "b24758", "b23869",
                                 "n112016", "s32827", "b24760", "s33241", "b24759", "s32828", "s33251", "b24770",
                                 "s33139", "n112497", "n112487", "n112506", "s32129", "n112686"])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c32173": ["4519", "#007777", 0],  # 毒浪翻涌
                       "c32183": ["16540", "#ff7700", 0],  # 雨倾蛊纵
                       "c32172": ["4501", "#00ff33", 0],  # 毒风怒号
                       "c32182": ["3434", "#ff7777", 0],  # 刀锋毒影
                       "c33154": ["4547", "#ff0000", 0],  # 黯蛊尘锋
                       }

        # 韩敬青数据格式：
        # 7 ？

        for line in self.bld.info.player:
            self.stat[line].extend([0, 0, 0])

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config


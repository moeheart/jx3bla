# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.ReplayerBase import ReplayerBase
from BossNameUtils import *
from Constants import *
from tools.Functions import *

import time

class ShieldCounter():
    '''
    盾的统计类.
    TODO: 之后可能会用一个更通用的buff统计类替换掉.
    '''
    shieldLog = []
    breakCount = 0
    shieldCount = 0
    shieldDuration = [0, 0]
    startTime = 0
    finalTime = 0
    nowi = 0
    timeCount = 0

    def checkTime(self, time):
        while self.nowi + 1 < len(self.shieldLog) and self.shieldLog[self.nowi + 1][0] < time:
            self.nowi += 1
        return self.shieldLog[self.nowi][1]

    def analysisShieldData(self):

        s = self.shieldLog

        newList = []
        for i in range(len(s)):
            if i > 0 and i + 1 < len(s) and s[i][1] == 0 and s[i + 1][1] == 1 and s[i + 1][0] - s[i][0] < 500:
                s[i][1] = 2
                s[i + 1][1] = 2
            if i < len(s) and len(newList) > 0 and s[i][1] == newList[-1][1]:
                s[i][1] = 2
            if s[i][1] != 2:
                newList.append(s[i])

        if newList == []:
            newList = [[self.startTime, 0]]
        else:
            if newList[0][1] == 0:
                newList = [[self.startTime, 1]] + newList
            else:
                newList = [[self.startTime, 0]] + newList

        self.shieldLog = newList

        n = len(newList)
        self.shieldDuration = [0, 0]
        self.breakCount = 0
        self.shieldCount = 0
        for i in range(1, n):
            assert newList[i][1] != newList[i - 1][1]
            self.shieldDuration[newList[i - 1][1]] += newList[i][0] - newList[i - 1][0]
            if newList[i][1] == 0:
                self.breakCount += 1
            if newList[i - 1][1] == 1:
                self.shieldCount += 1

        if newList[-1][1] == 1:
            self.shieldCount += 1

        self.shieldDuration[newList[n - 1][1]] += self.finalTime - newList[n - 1][0]

    def __init__(self, shieldLog, startTime, finalTime):
        self.shieldLog = shieldLog
        self.startTime = startTime
        self.finalTime = finalTime

class SkillCounter():
    '''
    技能统计类.
    TODO: 扩展这个类的功能，支持更多统计.
    '''
    skillLog = []
    actLog = []
    startTime = 0
    finalTime = 0
    speed = 3770
    sumBusyTime = 0
    sumSpareTime = 0

    def getLength(self, length):
        flames = calculSpeed(self.speed, length)
        return flames * 0.0625 * 1000

    def analysisSkillData(self):
        for line in self.skillLog:
            if line[1] in [15181, 15082, 25232]:  #奶歌常见的自动施放技能：影子宫，影子宫，桑柔
                continue
            elif line[1] in [14137, 14300]:  # 宫，变宫
                self.actLog.append([line[0] - self.getLength(24), self.getLength(24)])
            elif line[1] in [14140, 14301]:  # 徵，变徵
                self.actLog.append([line[0] - self.getLength(16), self.getLength(16)])
            else:
                self.actLog.append([line[0], self.getLength(24)])

        self.actLog.sort(key=lambda x: x[0])

        nowTime = self.startTime
        self.sumBusyTime = 0
        self.sumSpareTime = 0
        for line in self.actLog:
            if line[0] > nowTime:
                self.sumSpareTime += line[0] - nowTime
                self.sumBusyTime += line[1]
                nowTime = line[0] + line[1]
            elif line[0] + line[1] > nowTime:
                self.sumBusyTime += line[0] + line[1] - nowTime
                nowTime = line[0] + line[1]

    def __init__(self, skillLog, startTime, finalTime, speed=3770):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed

class XiangZhiProReplayer(ReplayerBase):
    '''
    奶歌复盘pro类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶歌复盘pro v%s"%EDITION
        self.result["overall"]["playerID"] = "未知"
        self.result["overall"]["server"] = self.bld.info.server
        self.result["overall"]["battleTime"] = self.bld.info.battleTime
        self.result["overall"]["battleTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        self.result["overall"]["generateTime"] = time.time()
        self.result["overall"]["generateTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["generateTime"]))
        self.result["overall"]["map"] = self.bld.info.map
        self.result["overall"]["boss"] = getNickToBoss(self.bld.info.boss)
        self.result["overall"]["sumTime"] = self.bld.info.sumTime
        self.result["overall"]["sumTimePrint"] = parseTime(self.bld.info.sumTime / 1000)

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"', '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
                self.npcKey = key
                break

        # 记录盾的存在情况与减疗
        shieldLogDict = {}
        jianLiaoLog = {}

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.
        self.interrupt = 0

        # 不知道有什么用
        self.activeBoss = ""

        # 记录战斗开始时间与结束时间
        self.startTime = 0
        self.finalTime = 0

        # 记录所有治疗的key，首先尝试直接使用心法列表获取.
        self.healerDict = {}
        XiangZhiList = []

        # 记录具体心法的表.
        occDetailList = {}
        for key in self.bld.info.player:
            occDetailList[key] = self.bld.info.player[key].occ

        # for line in sk:
        for event in self.bld.log:
            #item = line[""]
            if self.startTime == 0:
                self.startTime = event.time
            self.finalTime = event.time

            if self.interrupt != 0:
                continue

            if event.dataType == "Skill":
                # 记录奶歌和治疗心法的出现情况.
                if event.caster not in XiangZhiList and event.id in ["14231", "14140", "14301"]:  # 奶歌的特征技能
                    XiangZhiList.append(event.caster)
                    self.healerDict[event.caster] = 0
                if event.caster not in self.healerDict and event.id in ["565", "554", "555", "2232", "6662", "2233", "6675",
                                                                  "2231", "101", "142", "138", "16852", "18864"]:  # 其它治疗的特征技能
                    self.healerDict[event.caster] = 0

                # 记录主动贴盾
                if event.id == "14231":
                    jianLiaoStack = 0
                    if event.target in jianLiaoLog:
                        jianLiaoStack = jianLiaoLog[event.target].checkState(event.time)
                    if jianLiaoStack < 20:
                        if event.target not in shieldLogDict:
                            shieldLogDict[event.target] = []
                        shieldLogDict[event.target].append([event.time, 1])

                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"宓桃"':
                    self.activeBoss = "宓桃"
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif event.dataType == "Buff":
                if event.id in ["9334", "16911"]:  # buff梅花三弄
                    if event.target not in shieldLogDict:
                        shieldLogDict[event.target] = []
                    shieldLogDict[event.target].append([event.time, event.stack])
                if event.id in ["15774", "17200"]:  # buff精神匮乏
                    if event.target not in jianLiaoLog:
                        jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                    jianLiaoLog[event.target].setState(event.time, event.stack)
                if event.caster in occDetailList and occDetailList[event.caster] in ['21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                # 为未来需要统计喊话时备用.
                pass

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        # 自动推导奶歌角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            if len(XiangZhiList) >= 2:
                nameList = []
                for line in XiangZhiList:
                    nameList.append(namedict[line][0])
                s = str(nameList)
                raise Exception('奶歌的数量不止一个，请手动指示ID。可能的ID为：%s' % s)
            elif len(XiangZhiList) == 0:
                raise Exception('没有找到奶歌，请确认数据是否正确')
            else:
                self.mykey = XiangZhiList[0]
                self.myname = self.bld.info.player[self.mykey].name
                print("自动推断奶歌角色名为：%s"%self.myname)
        else:
            for key in self.bld.info.player:
                if self.bld.info.player[key].name == self.myname:
                    self.mykey = key

        self.shieldCounters = {}
        for key in shieldLogDict:
            self.shieldCounters[key] = ShieldCounter(shieldLogDict[key], self.startTime, self.finalTime)
            self.shieldCounters[key].analysisShieldData()

        # 为0覆盖率的玩家记录数据
        for key in self.bld.info.player:
            if  key not in self.shieldCounters:
                self.shieldCounters[key] = ShieldCounter([], self.startTime, self.finalTime)
                self.shieldCounters[key].analysisShieldData()

        self.occDetailList = occDetailList

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        # TODO

        print(self.result["overall"])

        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        occDetailList = self.occDetailList

        #data = XiangZhiData()

        num = 0
        skillLog = []

        # 以承疗者记录的关键治疗
        self.criticalHealCounter = {}
        hpsActive = 0

        # 以治疗者记录的关键治疗
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            numSmall = 0

        numHeal = 0
        numEffHeal = 0
        numAbsorb = 0
        npcHealStat = {}
        numPurge = 0 # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害]
        damageDict = {}  # 伤害统计
        myDamageRank = 0  # 个人伤害排名
        myDamage = 0  # 个人伤害
        healStat = {}  # 治疗统计
        healList = {}  # list形式的治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        healRate = 0  # 治疗占比
        rateDict = {}  # 盾覆盖率
        durationDict = {}  # 盾持续时间
        breakDict = {}  # 破盾次数
        sumShield = 0  # 盾数量
        equalDPS = 0  # 强度，相当于几个DPS
        overallRate = 0  # 盾的整体覆盖率

        for event in self.bld.log:
            if event.time > self.finalTime:
                break

            if event.dataType == "Skill":
                # 统计自身治疗
                if event.caster == self.mykey and event.heal != 0:
                    if event.effect != 7:  # 非化解
                        numHeal += event.heal
                        numEffHeal += event.healEff
                    else:
                        numAbsorb += event.healEff

                # 统计团队治疗
                if event.healEff > 0 and event.effect != 7 and event.caster in self.healerDict:
                    if event.caster not in healStat:
                        healStat[event.caster] = 0
                    healStat[event.caster] += event.healEff

                # 统计自身技能使用情况. TODO: 扩展为每个技能分别处理
                if event.caster == self.mykey and event.scheme == 1:
                    skillLog.append([event.time, event.id])

                # 统计对NPC的治疗情况.
                if event.healEff > 0 and event.target == self.npcKey:
                    if event.caster not in npcHealStat:
                        npcHealStat[event.caster] = 0
                    npcHealStat[event.caster] += event.healEff

                # 统计以承疗者计算的关键治疗
                if event.healEff > 0 and self.npcKey != 0:
                    if event.target in self.criticalHealCounter and self.criticalHealCounter[event.target].checkState(event.time):
                        if event.caster not in npcHealStat:
                            npcHealStat[event.caster] = event.healEff
                        else:
                            npcHealStat[event.caster] += event.healEff

                # 统计以治疗者计算的关键治疗
                if self.activeBoss in ["宓桃", "哑头陀"]:
                    if event.healEff > 0 and self.npcKey != 0 and hpsActive:
                        if event.caster not in npcHealStat:
                            npcHealStat[event.caster] = 0
                        npcHealStat[event.caster] += event.healEff

                if event.id == "14169":  # 一指回鸾
                    numPurge += 1

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.shieldCounters:
                        if event.caster not in battleStat:
                            battleStat[event.caster] = [0, 0, 0]  # 无盾伤害，有盾伤害，桑柔伤害
                        if int(event.id) >= 21827 and int(event.id) <= 21831:  # 桑柔
                            battleStat[event.caster][2] += event.damageEff
                        elif event.id == "25232" and event.caster == self.mykey:  # 桑柔伤害
                            battleStat[event.caster][2] += event.damageEff
                        else:
                            hasShield = self.shieldCounters[event.caster].checkTime(event.time)
                            battleStat[event.caster][hasShield] += event.damageEff

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            num += 1

        # 计算战斗效率等统计数据，TODO 扩写
        skillCounter = SkillCounter(skillLog, self.startTime, self.finalTime, self.result["attribute"]["haste"])
        skillCounter.analysisSkillData()
        sumBusyTime = skillCounter.sumBusyTime
        sumSpareTime = skillCounter.sumSpareTime
        spareRate = sumSpareTime / (sumBusyTime + sumSpareTime + 1e-10)

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

        # 计算等效伤害
        numdam1 = 0
        for key in battleStat:
            # if int(occdict[key][0]) == 0:
            #     continue
            line = battleStat[key]
            # damageDict[key] = line[0] + line[1] / 1.117 # 100赛季数值
            # numdam1 += line[1] / 1.117 * 0.117# + line[2]
            damageDict[key] = line[0] + line[1] / 1.0554  # 110赛季数值
            numdam1 += line[1] / 1.0554 * 0.0554
        if self.mykey in battleStat:
            numdam2 = battleStat[self.mykey][2]
        else:
            numdam2 = 0
        numdam = numdam1 + numdam2

        # 计算DPS列表
        if self.mykey not in damageDict:
            damageDict[self.mykey] = 0
        damageDict[self.mykey] += numdam

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        for i in range(len(damageList)):
            damageList[i].append(self.bld.info.player[damageList[i][0]].name)
            damageList[i].append(occDetailList[damageList[i][0]])

        sumDamage = 0
        numid = 0
        for line in damageList:
            line[1] /= self.result["overall"]["sumTime"] * 1000
            sumDamage += line[1]
            numid += 1
            if line[0] == self.mykey and myDamageRank == 0:
                myDamageRank = numid
                myDamage = line[1]
                sumDamage -= line[1]

        # 计算HPS列表
        healList = dictToPairs(healStat)
        healList.sort(key=lambda x: -x[1])

        sumHeal = 0
        numid = 0
        topHeal = 0
        for line in healList:
            if numid == 0:
                topHeal = line[1]
            sumHeal += line[1]
            numid += 1
            if line[0] == self.mykey and myHealRank == 0:
                myHealRank = numid
            if line[1] > topHeal * 0.2:
                numHealer += 1

        if myHealRank > numHealer:
            numHealer = myHealRank

        healRate = numEffHeal / (sumHeal + 1e-10)

        # 计算DPS的盾指标
        for key in self.shieldCounters:
            sumShield += self.shieldCounters[key].shieldCount
            if key not in damageDict or damageDict[key] / self.result["overall"]["sumTime"] * 1000 < 10000:
                continue
            if occDetailList[key] in ["1t", "2h", "3t", "5h", "10t", "6h", "21t", "22h"]:
                continue
            if key == self.mykey:
                continue

            rate = self.shieldCounters[key].shieldDuration[1] / \
                   (self.shieldCounters[key].shieldDuration[0] + self.shieldCounters[key].shieldDuration[1] + 1e-10)
            rateDict[key] = rate
            durationDict[key] = self.shieldCounters[key].shieldDuration[1]
            breakDict[key] = self.shieldCounters[key].breakCount

        equalDPS = myDamage / (sumDamage + 1e-10) * (len(durationDict) - 1)

        # 关键治疗量统计
        if self.activeBoss in ["宓桃", "哑头陀"]:
            for line in npcHealStat:
                npcHealStat[line] /= (hpsSumTime + 1e-10)

        # 计算覆盖率
        numRate = 0
        sumRate = 0
        for key in rateDict:
            numRate += 1
            sumRate += rateDict[key]

        overallRate = sumRate / (numRate + 1e-10)

        print("[测试]盾覆盖率为：", overallRate)
        print("[测试]治疗量：", numHeal)
        print("[测试]有效治疗量：", numEffHeal)
        print("[测试]化解：", numAbsorb)


    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        pass


    def replay(self):
        '''
        开始奶歌复盘pro分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", battleDate=""):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        '''
        #self.battleDate = battleDate
        #self.win = 0
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.myname = myname
        self.failThreshold = config.failThreshold
        self.mask = config.mask
        self.filePath = path + '\\' + fileNameInfo[0]
        self.bld = bldDict[fileNameInfo[0]]

        self.result = {}
        self.result["attribute"] = {"haste": 8780}  # TODO: 在属性计算完成后修改

        #if self.numTry == 0:
        #    self.bossNamePrint = self.bossname
        #else:
        #    self.bossNamePrint = "%s.%d" % (self.bossname, self.numTry)

        print("奶歌复盘pro类创建成功...")


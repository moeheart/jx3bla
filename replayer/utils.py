# Created by moeheart at 1/24/2021
# 复盘的常用函数库。

class DpsShiftWindow():
    '''
    DPS滑动窗口类，用于在战斗记录中识别出停手的时间点，并统计对应的DPS。
    使用两个连在一起的窗口，长度为a与b，不断向右滑动。当a中的DPS总量与b中的DPS总量比例小于一个值时，判定中间的位置出现了停手。
    '''
    
    def calSetADps(self):
        '''
        计算集合A中的所有DPS。
        '''
        return self.damage
    
    def checkItem(self, item):
        '''
        处理一条战斗记录。
        '''
        # 处理战斗记录本身
        if item[4] in self.damage:
            self.damage[item[4]] += int(item[14])
            self.logA.append([int(item[2]), item[4], int(item[14])])
            self.damageA += int(item[14])
        
        #将A中的超时记录转移给B
        self.middleTime = int(item[2]) - self.a
        while len(self.logA) > 0 and self.middleTime > self.logA[0][0]:
            player = self.logA[0][1]
            dam = self.logA[0][2]
            self.damageA -= dam
            self.damage[player] -= dam
            
            self.logB.append([int(item[2]), player, dam])
            self.damageB += dam
            
            del self.logA[0]
            
        #将B中的超时记录移除
        self.expireTime = int(item[2]) - self.a - self.b
        while len(self.logB) > 0 and self.expireTime > self.logB[0][0]:
            player = self.logB[0][1]
            dam = self.logB[0][2]
            self.damageB -= dam
            
            del self.logB[0]
            
        if self.expireTime > self.startTime:
            self.initialized = 1
            
        #判断是否出现停手
        self.stopped = 0
        if self.initialized and self.damageA / self.damageB < self.rate:
            self.stopped = 1
        
        return self.stopped
    
    def __init__(self, playerIDs, a, b, rate, startTime): 
        self.damage = {}
        for line in playerIDs:
            self.damage[line] = 0
        self.a = a * 1000
        self.b = b * 1000
        self.rate = rate
        self.startTime = startTime
        
        self.middleTime = self.startTime - self.a
        self.initialized = 0
        self.logA = [] #队列A中的记录
        self.logB = [] #队列B中的记录
        self.damageA = 0
        self.damageB = 0

class PurgeCounter():
    '''
    检测特定角色对于特定buff的驱散类。
    '''
    
    def recordPurge(self, item):
        '''
        记录对应的item中的驱散技能。
        这里的item必须经过检验，确定是技能类别。
        '''
        if item[7] in self.purgeSkill:
            self.player = item[4]
            self.time = int(item[2])
            
    def recordDeduct(self, item):
        '''
        检测对应的item是否是监控buff消失事件，若是则记录消失状态，准备之后结算。
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if item[6] in self.targetBuff and int(item[10]) == 0:
            self.purgeTime = int(item[2])
            self.purgeBuff = item[6]
    
    def checkPurge(self, item):
        '''
        检测对应的item是否是监控buff消失事件，若是则结算，并返回
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if self.purgeTime == 0 or int(item[2]) - self.purgeTime < 100: #结算延迟100毫秒
            return "0"
        self.purgeTime = 0
        return self.player
    
    def __init__(self, buffList):
        self.targetBuff = buffList
        self.purgeSkill = ["133", #清风垂露
                           "2654", #利针
                           "138", #提针
                           "566", #跳珠憾玉
                           "3052", #蝶鸾子技能
                           "14169", #一指回鸾
                          ]
        self.player = "0"
        self.time = 0
        self.purgeTime = 0
        
class CriticalHealCounter():
    '''
    检测特定角色的关键治疗量类。
    除了传统的治疗量，还会同时记录减伤所等效的治疗量。
    '''
    
    def setCriticalTime(self, time):
        '''
        设定关键治疗的过期时间。
        '''
        if time > self.expireTime:
            self.expireTime = time
    
    def recordHeal(self, item):
        '''
        记录对应的item中的治疗量。
        这里的item必须经过检验，确定是技能类别。
        '''
        if int(item[2]) > self.expireTime:
            self.unactive()
        
        if not self.activeNum:
            return {}
            
        result = {}
        heal = int(item[12])
        damage = int(item[14])
        if heal > 0:
            result[item[4]] = heal
        
        if damage > 0:
            deductRate = 0
            for line in self.deductStatus:
                if self.deductStatus[line] != "0":
                    deductRate += self.deductDict[line]
            #若减伤系数总和大于1，则跳过处理
            if deductRate < 1:
                originDamage = damage / (1 - deductRate)
                for line in self.deductStatus:
                    if self.deductStatus[line] != "0":
                        if self.deductStatus[line] not in result:
                            result[self.deductStatus[line]] = 0
                        result[self.deductStatus[line]] += originDamage * self.deductDict[line]
                        
        return result
        
    def checkDeduct(self, item):
        '''
        记录对应的item中，减伤的获得或消失。
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if item[6] in self.deductDict:
            if int(item[10]) > 0:
                #添加减伤
                self.deductStatus[item[6]] = item[4]
            else:
                #移除减伤
                self.deductStatus[item[6]] = "0"
        
    def unactive(self):
        '''
        关闭计数。
        '''
        self.activeNum = 0
        
    def active(self):
        '''
        开启计数。
        '''
        self.activeNum = 1
    
    def __init__(self):
        #仅列举大部分治疗心法给队友的减伤。
        self.deductDict = {"9336": 0.3, #寒梅
                           "9337": 0.3, #寒梅
                           "6636": 0.45, #圣手织天
                           "122": 0.45, #春泥护花
                           "6264": 0.6, #南柯
                           "9933": 0.3, #折叶
                           "684": 0.4, #风袖（天地）
                          }
                          
        self.deductStatus = {}
        
        self.activeNum = 0
        self.expireTime = 0
        
        
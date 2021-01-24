# Created by moeheart at 1/24/2021
# 复盘的常用函数库。

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
    
    def checkPurge(self, item):
        '''
        检测对应的item是否是监控buff消失事件，若是则结算，并返回
        这里的item必须经过检验，确定是气劲类别，并且是玩家。
        '''
        if item[6] in self.targetBuff and int(item[10]) == 0:
            #以500毫秒为界限，避免数据丢失导致错乱
            if int(item[2]) - self.time < 500:
                return self.player
        return "0" 
    
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
        
        
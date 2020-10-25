# Created by moeheart at 10/10/2020
# 通过选项自动查找剑三战斗记录文件的功能类，包括寻找文件夹，与自动识别有效的战斗记录。

import os
import winreg
import functools
from BossNameUtils import *

class FileLookUp():
    jx3path = ""
    basepath = "."
    mode = ""
    specifiedFiles = []

    # Add by KEQX
    def specifyFiles(self, files):
        def compare(a, b):
            if a < b:
                return -1
            elif a > b:
                return 1
            else:
                return 0
        self.specifiedFiles = sorted(files, key=functools.cmp_to_key(compare))

    def getPathFromWinreg(self):
        '''
        从注册表获取剑三的目录。这种方式有可能失败。
        '''
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\JX3Installer', )
            pathres = winreg.QueryValueEx(key, "InstPath")[0]
        except:
            print("自动获取目录失败，请手动指定目录")
            pathres = ""
        self.jx3path = pathres

    def getBasePath(self, playerName):
        '''
        通过剑三目录与玩家角色名，获取对应的战斗复盘路径。
        params
        - playerName 玩家名。
        '''
        datapath = "%s\\Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA" % self.jx3path
        resDir = ""
        l = os.listdir(datapath)
        for name in l:
            path2 = "%s\\%s" % (datapath, name)
            if os.path.isdir(path2):
                l2 = os.listdir(path2)
                if playerName in l2:
                    resDir = "%s\\userdata\\fight_stat" % path2
                    break

        self.basepath = resDir
        if resDir == "":
            print("剑三目录有误，请检查记录者角色名是否正确")

    def getLocalFile(self):
        '''
        在已确定战斗复盘路径时，获取其中的部分战斗记录。
        return
        - finalList 最近一次副本中，每个BOSS各取最后一次战斗记录组成的列表。
        - finalListAll 最近一次副本中，所有战斗记录组成的列表。
        - finalMap 从文件名推断的副本。
        '''
        selectFileList = []

        # Add by KEQX
        if len(self.specifiedFiles) > 0:
            selectFileList = self.specifiedFiles
        else:
            filelist = os.listdir(self.basepath)
            for line in filelist:
                if line[-6:] == "jx3dat":
                    selectFileList.append(line)
        
        '''
        bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6,
                    "周贽": 1, "狼牙精锐": 1, "狼牙刀盾兵": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5,
                    "余晖": 1, "宓桃": 2, "武雪散": 3, "猿飞": 4, "哑头陀": 5, "岳琳": 6,
                    "毗流驮迦": 5, "毗留博叉": 5, "充能核心": 5}
        mapDict = {"铁黎": 1, "陈徽": 1, "藤原武裔": 1, "源思弦": 1, "驺吾": 1, "方有崖": 1,
                   "周贽": 2, "狼牙精锐": 2, "狼牙刀盾兵": 2, "厌夜": 2, "迟驻": 2, "白某": 2, "安小逢": 2,
                   "余晖": 3, "宓桃": 3, "武雪散": 3, "猿飞": 3, "哑头陀": 3, "岳琳": 3,
                   "毗流驮迦": 3, "毗留博叉": 3, "充能核心": 3}
        mapNameList = ["未知地图", "敖龙岛", "范阳夜变", "达摩洞"]
        '''
        
        bossDict = BOSS_DICT
        mapDict = MAP_DICT
        mapNameList = MAP_NAME_LIST

        nowBoss = 6
        bossPos = [-1] * 8
        bossPos[7] = 999
        bossList = [0] * len(selectFileList)
        for i in range(len(selectFileList) - 1, -1, -1):
            if selectFileList[i][-13:] == "config.jx3dat":
                continue
            bossname = selectFileList[i].split('_')[-2]
            if bossname in bossDict:
                if bossDict[bossname] <= nowBoss:
                    bossPos[bossDict[bossname]] = i
                    bossList[i] = bossDict[bossname]
                    nowBoss = bossDict[bossname] - 1
                elif bossDict[bossname] == nowBoss + 1:
                    bossList[i] = bossDict[bossname]
            # battletime = int(selectFileList[i].split('_')[2].split('.')[0])

        # for i in range(1, 7):
        #    if bossPos[i] == -1:
        #        for j in range(len(selectFileList)):
        #            if j > bossPos[i-1] and j < bossPos[i+1] and bossList[j] == 999:
        #                bossList[j] = i
        #                bossPos[i] = j

        finalList = []
        finalListAll = []
        lastName = ""
        lastNum = 0
        for i in range(1, 7):
            if bossPos[i] != -1:
                finalList.append([selectFileList[bossPos[i]], 0, 1])

        for i in range(len(selectFileList)):
            if bossList[i] != 0:
                bossname = selectFileList[i].split('_')[-2]
                if bossname != lastName:
                    lastName = bossname
                    lastNum = 0
                    if finalListAll != []:
                        finalListAll[-1][2] = 1
                else:
                    lastNum += 1
                finalListAll.append([selectFileList[i], lastNum, 0])

        finalListAll[-1][2] = 1
        if finalList == []:
            print("没有合适的战斗记录，请确认目录设置或角色是否正确。")

        finalFileName = finalList[-1][0]
        finalBossName = finalFileName.split('_')[-2]
        finalMap = mapNameList[mapDict[finalBossName]]

        return finalList, finalListAll, finalMap
        
    def initFromConfig(self, config):
        '''
        从config.ini的设置，按照一定优先级，获取正确的战斗记录位置。
        params
        - config 设置类
        '''
        if config.basepath != "":
            print("指定基准目录，使用：%s" % config.basepath)
            self.basepath = config.basepath
        elif config.playername == "":
            self.basepath = '.'  # 这一句有点废话的意思，但为了让别人看得清晰还是写上吧
            print("没有指定记录者角色名，将查找当前目录下的文件……")
        else:
            if config.jx3path != "":
                print("指定剑三目录，使用：%s" % config.jx3path)
                self.jx3path = config.jx3path
            else:
                print("无指定目录，自动查找目录……")
                self.getPathFromWinreg()
            self.getBasePath(config.playername)
            
    def __init__(self):
        pass 
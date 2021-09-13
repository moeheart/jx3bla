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
            print("自动获取目录失败，请手动指定剑三目录")
            self.basepath = "自动获取目录失败，请手动指定剑三目录"
            pathres = ""
        self.jx3path = pathres

    def getBasePath(self, playerName):
        '''
        通过剑三目录与玩家角色名，获取对应的战斗复盘路径。
        params
        - playerName 玩家名。
        '''
        l1 = os.listdir(self.jx3path)
        datapath = "%s\\Game\\JX3\\bin\\zhcn_hd\\interface\\MY#DATA" % self.jx3path
        resDir = ""
        l = os.listdir(datapath)
        
        resTime = 0
        
        for name in l:
            path2 = "%s\\%s" % (datapath, name)
            if os.path.isdir(path2):
                l2 = os.listdir(path2)
                if playerName in l2:
                    newresTime = os.path.getmtime(path2)
                    if newresTime > resTime:
                        resTime = newresTime
                        if self.dataType == "jcl":
                            resDir = "%s\\userdata\\combat_logs" % path2
                        else:
                            resDir = "%s\\userdata\\fight_stat" % path2
        self.basepath = resDir
        print(self.basepath)
        if resDir == "":
            print("查找角色失败，请检查记录者角色名或剑三目录是否正确")
            self.basepath = "查找角色失败，请检查记录者角色名或剑三目录是否正确"

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
                if line[-6:] == self.dataType or line[-3:] == self.dataType:
                    selectFileList.append(line)

        bossDict = BOSS_DICT
        mapDict = MAP_DICT
        mapNameList = MAP_NAME_LIST

        nowBoss = 7
        bossPos = [-1] * 9
        bossPos[8] = 999
        bossList = [0] * len(selectFileList)
        for i in range(len(selectFileList) - 1, -1, -1):
            if selectFileList[i][-13:] == "config.jx3dat":
                continue
            if self.dataType == "jx3dat":
                bossname = getNickToBoss(selectFileList[i].split('_')[1])
            else:
                bossname = getNickToBoss(selectFileList[i].split('-')[-1].split('.')[0])
            if bossname in bossDict:
                if bossDict[bossname] <= nowBoss:
                    bossPos[bossDict[bossname]] = i
                    bossList[i] = bossDict[bossname]
                    nowBoss = bossDict[bossname] - 1
                elif bossDict[bossname] == nowBoss + 1:
                    bossList[i] = bossDict[bossname]
            else:
                bossPos[0] = i

        finalList = []
        finalListAll = []
        lastName = ""
        lastNum = 0
        for i in range(1, 8):
            if bossPos[i] != -1:
                finalList.append([selectFileList[bossPos[i]], 0, 1])

        for i in range(len(selectFileList)):
            if bossList[i] != 0:
                if self.dataType == "jx3dat":
                    bossname = selectFileList[i].split('_')[1]
                else:
                    bossname = selectFileList[i].split('-')[-1].split('.')[0]
                if bossname != lastName:
                    lastName = bossname
                    lastNum = 0
                    if finalListAll != []:
                        finalListAll[-1][2] = 1
                else:
                    lastNum += 1
                finalListAll.append([selectFileList[i], lastNum, 0])

        if finalList == []:
            if bossPos[0] == -1:
                raise Exception("没有合适的战斗记录，请确认路径是否正确.")
            finalList.append([selectFileList[bossPos[0]], 0, 1])
            finalListAll.append([selectFileList[bossPos[0]], 0, 1])

        finalListAll[-1][2] = 1

        finalFileName = finalList[-1][0]
        if self.dataType == "jx3dat":
            finalBossName = finalFileName.split('_')[1]
        else:
            finalBossName = finalFileName.split('-')[-1].split('.')[0]

        if finalBossName in mapDict:
            finalMap = mapNameList[mapDict[finalBossName]]
        else:
            finalMap = "未知"

        return finalList, finalListAll, finalMap
        
    def initFromConfig(self, config):
        '''
        从config.ini的设置，按照一定优先级，获取正确的战斗记录位置。
        params
        - config 设置类
        '''
        self.dataType = config.datatype
        if config.basepath != "":
            print("指定基准目录，使用：%s" % config.basepath)
            self.basepath = config.basepath
            return ""
        elif config.playername == "":
            self.basepath = '.'  # 这一句有点废话的意思，但为了让别人看得清晰还是写上吧
            print("没有指定记录者角色名，将查找当前目录下的文件……")
        else:
            if config.jx3path != "":
                self.jx3path = config.jx3path
            else:
                self.getPathFromWinreg()
            self.getBasePath(config.playername)
        return self.basepath
            
    def __init__(self):
        self.dataType = "jx3dat"

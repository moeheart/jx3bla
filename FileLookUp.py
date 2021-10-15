# Created by moeheart at 10/10/2020
# 通过选项自动查找剑三战斗记录文件的功能类，包括寻找文件夹，与自动识别有效的战斗记录。

import os
import winreg
import functools
from BossNameUtils import *

import threading
import tkinter as tk

class FileLookUp():
    jx3path = ""
    basepath = "."
    # mode = ""
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

class FileSelector():
    '''
    文件选取类，由用户手动选取文件.
    维护一个选取文件的窗口，以及选取文件本身的逻辑。
    '''


    def GetOptions(self):
        '''
        获取选择清单.
        '''
        filelist = os.listdir(self.basepath)
        optionList = []
        for line in filelist:
            if (line[-6:] == self.dataType or line[-3:] == self.dataType) and line != "config.jx3dat":
                optionList.append(line)

        print(optionList)
        return optionList

    def final(self):
        '''
        选择完成时执行的命令.
        '''
        self.selectionList = []
        for i in range(len(self.vars)):
            var = self.vars[i]
            if var.get() == 1:
                self.selectionList.append([self.optionList[i], 0, 1])
        self.window.destroy()
        if self.selectionList != []:
            self.replayThread = threading.Thread(target=self.mainWindow.replay, args=(self.selectionList,))
            self.replayThread.start()


    def loadWindow(self):
        '''
        展示选择界面.
        '''

        self.optionList = self.GetOptions()
        numFile = len(self.optionList)
        self.vars = []
        self.buttons = []

        window = tk.Toplevel()
        window.title('选择复盘记录')
        window.geometry('500x700')

        canvas = tk.Canvas(window, width=600, height=500, scrollregion=(0, 0, 580, numFile * 30))  # 创建canvas
        canvas.place(x=25, y=25)  # 放置canvas的位置
        frame = tk.Frame(canvas)  # 把frame放在canvas里
        frame.place(width=580, height=500)  # frame的长宽，和canvas差不多的
        vbar = tk.Scrollbar(canvas, orient=tk.VERTICAL)  # 竖直滚动条
        vbar.place(x=580, width=20, height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置
        canvas.create_window((265, numFile * 15), window=frame)  # create_window

        for i in range(numFile):
            fileName = self.optionList[i]
            var = tk.IntVar(window)
            button = tk.Checkbutton(frame, text=fileName, variable=var, onvalue=1, offvalue=0)
            self.vars.append(var)
            self.buttons.append(button)
            button.grid(row=i, column=0)

        buttonFinal = tk.Button(window, text='选择完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=220, y=570)

        self.window = window
        # window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def __init__(self, config, mainWindow):
        '''
        初始化. 需要根据config来确定基础路径及文件格式.
        '''
        self.fileLookUp = FileLookUp()
        self.basepath = self.fileLookUp.initFromConfig(config)
        self.dataType = self.fileLookUp.dataType
        self.mainWindow = mainWindow


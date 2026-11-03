# Created by moeheart at 10/10/2020
# 通过选项自动查找剑三战斗记录文件的功能类，包括寻找文件夹，与自动识别有效的战斗记录。

import os
import winreg
import functools
from tools.Names import *

import threading
import tkinter as tk

class FileLookUp():
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
        '''读取正式服安装记录，优先使用西山居启动器的独立游戏目录。'''
        self.jx3path = ""
        self.datapath = ""
        # SeasunGame's own InstPath is the launcher, not the installed game.
        # Only JX3 is the formal client; EXP, CLASSIC and WJ are other products.
        locations = (
            (r'SOFTWARE\Kingsoft\SeasunGame\JX3', 'InstallPath'),
            (r'SOFTWARE\Kingsoft\JX3', 'InstallPath'),
            (r'SOFTWARE\JX3Installer', 'InstPath'),
        )
        seen = set()
        for location, value_name in locations:
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
                    try:
                        with winreg.OpenKey(hive, location, 0, winreg.KEY_READ | view) as key:
                            value, value_type = winreg.QueryValueEx(key, value_name)
                    except OSError:
                        continue
                    if value_type not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) or not isinstance(value, str):
                        continue
                    path = self.normalizePath(value)
                    if not path or os.path.normcase(path) in seen:
                        continue
                    seen.add(os.path.normcase(path))
                    datapath = self.findDataFolder(path)
                    if datapath:
                        self.jx3path, self.datapath = path, datapath
                        return path
        self.basepath = "自动获取目录失败，请手动指定剑三目录"
        print(self.basepath)
        return ""

    @staticmethod
    def normalizePath(path):
        path = os.path.expandvars(path.strip().strip('"').strip())
        return os.path.normpath(path) if path else ""

    @staticmethod
    def findDataFolder(path):
        '''接受正式服安装根目录、MY#DATA 的任意上层目录或它本身。'''
        if not path:
            return ""
        if os.path.basename(path).casefold() == 'my#data' and os.path.isdir(path):
            return path
        parts = ('Game', 'JX3', 'bin', 'zhcn_hd', 'interface', 'MY#DATA')
        for index in range(len(parts)):
            candidate = os.path.join(path, *parts[index:])
            if os.path.isdir(candidate):
                return candidate
        return ""

    def getDataFolder(self):
        '''
        由剑三路径获取MY_DATA数据文件夹路径.
        '''
        self.datapath = ""
        self.jx3path = self.normalizePath(self.jx3path)
        if not self.jx3path and not self.getPathFromWinreg():
            return ""
        self.datapath = self.findDataFolder(self.jx3path)
        if not self.datapath:
            print("自动读取剑三路径失败，请尝试手动输入剑三路径。")
            self.basepath = "自动读取剑三路径失败，请尝试手动输入剑三路径。"
        return self.datapath

    def getBasePath(self, playerName):
        '''
        通过剑三目录与玩家角色名，获取对应的战斗复盘路径。
        params
        - playerName 玩家名。
        '''
        if not self.getDataFolder():
            return
        datapath = self.datapath
        try:
            l = os.listdir(datapath)
        except OSError:
            self.basepath = "无法读取剑三日志目录，请检查目录访问权限。"
            return

        resTime = 0

        resDir = ""
        for name in l:
            path2 = os.path.join(datapath, name)
            logFolder = 'combat_logs' if self.dataType == 'jcl' else 'fight_stat'
            candidate = os.path.join(path2, 'userdata', logFolder)
            if os.path.isdir(os.path.join(path2, playerName)) and os.path.isdir(candidate):
                try:
                    newresTime = os.path.getmtime(path2)
                except OSError:
                    continue
                if newresTime > resTime:
                    resTime = newresTime
                    resDir = candidate
        self.basepath = resDir
        print("自动推导的基准路径：", self.basepath)
        if resDir == "":
            print("查找角色失败，请检查记录者角色名是否正确。")
            self.basepath = "查找角色失败，请检查记录者角色名是否正确。"

    def getAllPlayers(self):
        '''
        尝试通过当前的剑三路径查找所有可能的角色名.
        '''
        if not self.getDataFolder():
            return []
        datapath = self.datapath
        try:
            l = os.listdir(datapath)
        except OSError:
            return []

        res = []

        for name in l:
            path2 = "%s\\%s" % (datapath, name)
            if os.path.isdir(path2):
                try:
                    l2 = os.listdir(path2)
                except OSError:
                    continue
                resTime = 0
                bestPlayer = ""
                bestTime = 0
                for playerName in l2:
                    if playerName not in ['audio', 'cache', 'config', 'export', 'font', 'info.jx3dat', 'manifest.jx3dat', 'temporary', 'userdata', 'logs', 'decode', 'curl']:
                        playerPath = os.path.join(path2, playerName)
                        if not os.path.isdir(playerPath):
                            continue
                        try:
                            newresTime = os.path.getmtime(playerPath)
                        except OSError:
                            continue
                        if newresTime > resTime:
                            resTime = newresTime
                            bestPlayer = playerName
                try:
                    bestTime = os.path.getmtime(os.path.join(path2, 'manifest.jx3dat'))
                except OSError:
                    pass
                if bestPlayer != "":
                    res.append([bestPlayer, bestTime])
        res.sort(key=lambda x: -x[1])
        result = []
        for line in res:
            result.append(line[0])
        return result

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

        selectFileList = sorted(selectFileList)
        if self.dataType == "jcl" and selectFileList:
            if self.specifiedFiles:
                # Explicit selection may intentionally span days or raids.
                # Preserve every selected attempt instead of applying the
                # automatic "latest session" filter to the user's choices.
                finalList, finalListAll = [], []
                lastKey, lastNum = None, 0
                for name in selectFileList:
                    mapName, bossName = getJclEncounter(name)
                    key = (self.getJclSessionKey(name), bossName)
                    if key != lastKey:
                        if finalListAll:
                            finalListAll[-1][2] = 1
                            finalList.append([finalListAll[-1][0], 0, 1])
                        lastKey, lastNum = key, 0
                    else:
                        lastNum += 1
                    finalListAll.append([name, lastNum, 0])
                finalListAll[-1][2] = 1
                finalList.append([finalListAll[-1][0], 0, 1])
                return finalList, finalListAll, MAP_ORIGINAL.get(getIDFromMap(mapName), mapName)
            latestSession = self.getJclSessionKey(selectFileList[-1])
            if latestSession is not None:
                selectFileList = [name for name in selectFileList
                                  if self.getJclSessionKey(name) == latestSession]
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
                _, bossname = getJclEncounter(selectFileList[i])
            if bossname in bossDict:
                if self.dataType == "jcl" and nowBoss != 7 and bossDict[bossname] > nowBoss + 1:
                    # Reverse progression has crossed into an earlier run of
                    # this raid on the same day (e.g. ...5, then a new 1...5).
                    break
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
                    _, bossname = getJclEncounter(selectFileList[i])
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
            finalMapName, finalBossName = getJclEncounter(finalFileName)

        if self.dataType == "jcl":
            mapID = getIDFromMap(finalMapName)
            finalMap = MAP_ORIGINAL.get(mapID, finalMapName)
        elif finalBossName in mapDict:
            finalMap = mapNameList[mapDict[finalBossName]]
        else:
            finalMap = "未知"

        return finalList, finalListAll, finalMap

    @staticmethod
    def getJclSessionKey(filename):
        """The automatic latest batch is scoped to the filename's raid/date."""
        basename = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
        parts = basename.split("-", 7)
        if len(parts) < 8:
            return None
        mapName, _ = getJclEncounter(basename)
        return mapName, "-".join(parts[:3])
        
    def initFromConfig(self, config):
        '''
        从config.ini的设置，按照一定优先级，获取正确的战斗记录位置。
        params
        - config 设置类
        '''
        self.dataType = config.item["general"]["datatype"]
        # Settings also use this object to list characters, even when the log
        # directory is explicit or no character has been selected yet.
        self.jx3path = self.normalizePath(config.item["general"]["jx3path"])
        self.datapath = ""
        if config.item["general"]["basepath"] != "":
            self.basepath = config.item["general"]["basepath"]
            # print("指定基准目录，使用：%s" % self.basepath)
            return self.basepath
        elif config.item["general"]["playername"] == "":
            self.basepath = '.'
            print("没有指定记录者角色名，将查找当前目录下的文件……")
        else:
            self.getBasePath(config.item["general"]["playername"])
        return self.basepath
            
    def __init__(self):
        self.specifiedFiles = []
        self.dataType = "jx3dat"
        self.jx3path = ""
        self.datapath = ""
        self.basepath = "."

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

        optionList.sort()
        if len(optionList) > 50:
            # A progression session can exceed 50 attempts. Keep its early
            # bosses selectable, while retaining the usual recent-file list.
            lookup = FileLookUp()
            lookup.basepath = self.basepath
            lookup.dataType = self.dataType
            _, attempts, _ = lookup.getLocalFile()
            retained = set(optionList[-50:])
            retained.update(row[0] for row in attempts)
            optionList = [name for name in optionList if name in retained]
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

    def open_folder(self):
        '''
        打开对应的目录.
        '''
        dir = self.basepath.replace('/', '\\')
        os.startfile(dir)

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

        canvas = tk.Canvas(window, width=450, height=500, scrollregion=(0, 0, 430, numFile * 50))  # 创建canvas
        canvas.place(x=25, y=25)  # 放置canvas的位置
        frame = tk.Frame(canvas)  # 把frame放在canvas里
        frame.place(width=430, height=500)  # frame的长宽，和canvas差不多的
        vbar = tk.Scrollbar(canvas, orient=tk.VERTICAL)  # 竖直滚动条
        vbar.place(x=430, width=20, height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置
        canvas.create_window((190, numFile * 15), window=frame)  # create_window

        for i in range(numFile):
            fileName = self.optionList[i]
            var = tk.IntVar(window)
            showName = fileName
            if len(showName) > 40:
                showName = showName[:40]
            button = tk.Checkbutton(frame, text=showName, variable=var, onvalue=1, offvalue=0)
            self.vars.append(var)
            self.buttons.append(button)
            button.grid(row=numFile-i, column=0, sticky='w')

        buttonOpen = tk.Button(window, text='打开目录', width=10, height=1, command=self.open_folder)
        buttonOpen.place(x=180, y=570)

        buttonFinal = tk.Button(window, text='选择完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=260, y=570)

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


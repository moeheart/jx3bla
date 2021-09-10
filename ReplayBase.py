# Created by moeheart at 10/11/2020
# 复盘相关方法的基类库。

from tools.Functions import *
from tools.LoadData import *
from BossNameUtils import *

class StatGeneratorBase():
    filename = ""
    rawdata = {}
    bossname = ""
    battleTime = 0

    def parseFile(self, path):
        if path == "":
            name = self.filename
        else:
            name = "%s\\%s" % (path, self.filename)
        print("读取文件：%s" % name)
        f = open(name, "r")
        s = f.read()
        
        if self.window is not None:
            bossname = getNickToBoss(self.filename.split('_')[1])
            self.window.setNotice({"t1": "正在读取[%s]..."%bossname, "c1": "#000000"})
        
        luatableAnalyser = LuaTableAnalyser(self.window)
        res = luatableAnalyser.analyse(s)
        self.rawdata = res


        luatableAnalyser2 = LuaTableAnalyserToDict(self.window)
        res2 = luatableAnalyser2.analyse(s)
        self.formatData = res2

        if '9' not in self.rawdata:
            if len(self.rawdata['']) == 17:
                for i in range(1, 17):
                    self.rawdata[str(i)] = [self.rawdata[''][i - 1]]
            else:
                raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")

        self.bossname = getNickToBoss(self.filename.split('_')[1])
        self.battleTime = int(self.filename.split('_')[2].split('.')[0])

    def __init__(self, filename, path="", rawdata={}, window = None):
        self.window = window
        if rawdata == {}:
            self.filename = filename
            self.parseFile(path)
        else:
            self.filename = filename
            self.rawdata = rawdata
            self.bossname = getNickToBoss(self.filename.split('_')[1])
            self.battleTime = int(self.filename.split('_')[2].split('.')[0])
            
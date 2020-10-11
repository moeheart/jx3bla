# Created by moeheart at 10/11/2020
# 复盘相关方法的基类库。

from Functions import *

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
        res, _ = parseLuatable(s, 8, len(s))
        self.rawdata = res

        if '9' not in self.rawdata:
            if len(self.rawdata['']) == 17:
                for i in range(1, 17):
                    self.rawdata[str(i)] = [self.rawdata[''][i - 1]]
            else:
                raise Exception("数据不完整，无法生成，请确认是否生成了正确的茗伊战斗复盘记录。")

        self.bossname = self.filename.split('_')[1]
        self.battleTime = int(self.filename.split('_')[2].split('.')[0])

    def __init__(self, filename, path="", rawdata={}):
        if rawdata == {}:
            self.filename = filename
            self.parseFile(path)
        else:
            self.filename = filename
            self.rawdata = rawdata
            self.bossname = self.filename.split('_')[1]
            self.battleTime = int(self.filename.split('_')[2].split('.')[0])
            
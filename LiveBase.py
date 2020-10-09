# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time

def listenPath(basepath):
    filelist = os.listdir(basepath)
    dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
    if dataList != []:
        newestFile = dataList[-1]
    else:
        newestFile = ""
    while(True):
        time.sleep(3)
        filelist = os.listdir(basepath)
        dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
        if dataList != []:
            lastFile = dataList[-1]
        else:
            lastFile = ""
        if lastFile != newestFile:
            newestFile = lastFile
            print("Newest File: %s"%lastFile)

class LiveListener():

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenThread = threading.Thread(target = listenPath, args = (self.basepath,))    
        self.listenThread.start()
    
    def __init__(self, basepath):
        '''
        构造方法。
        params
        - basepath: 战斗记录生成的路径。
        '''
        self.basepath = basepath
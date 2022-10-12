# Created by moeheart at 10/07/2022
# 预加载流程，用于处理一些预加载方法.
# 并非所有的预加载流程都放在了这个文件里，但是之后会逐步迁移过来.

import os
import json
import urllib
from Constants import *
from tools.Functions import *

def checkRateEdition(serverEdition):
    '''
    检查排名的版本是否和服务器一致.
    params:
    - serverEdition: 服务器返回的版本.
    '''
    global STAT_PERCENT
    requireUpdate = False
    if os.path.exists('icons/rate.dat'):
        try:
            with open('icons/rate.dat', 'r') as f:
                s = f.read()
                j = json.loads(s)
                edition = j["edition"]
                STAT_PERCENT = j["data"]
                if edition < serverEdition:
                    requireUpdate = True
        except:
            requireUpdate = True
    else:
        requireUpdate = True

    # requireUpdate = False

    if requireUpdate:
        # 从服务器重新读取排名
        if parseEdition(EDITION) == 0:  # 非联机版本跳过加载步骤
            res = {"announcement": "", "version": "0.0.0", "url": ""}
        else:
            resp = urllib.request.urlopen('http://%s:8009/getPercentInfo' % IP)
            res = json.load(resp)
            STAT_PERCENT = res["data"]
            j = {"edition": serverEdition, "data": STAT_PERCENT}
            s = json.dumps(j)
            with open('icons/rate.dat', 'w') as f:
                f.write(s)

    # 待测试





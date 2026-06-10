# Created by moeheart at 10/07/2022
# 预加载流程，用于处理一些预加载方法.
# 并非所有的预加载流程都放在了这个文件里，但是之后会逐步迁移过来.

import os
import json
import urllib
from Constants import *
from tools.Functions import *
from tools.ResourcePath import ensure_parent_dir, get_resource_path, get_writable_path

def checkRateEdition(serverEdition):
    '''
    检查排名的版本是否和服务器一致.
    params:
    - serverEdition: 服务器返回的版本.
    '''
    global STAT_PERCENT
    requireUpdate = False
    STAT_PERCENT = {}

    rate_path = get_writable_path(os.path.join("icons", "rate.dat"))
    read_rate_path = get_resource_path(os.path.join("icons", "rate.dat"))

    if os.path.exists(rate_path):
        read_rate_path = rate_path

    if os.path.exists(read_rate_path):
        try:
            with open(read_rate_path, 'r') as f:
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
            # STAT_PERCENT = {}
            pass
        else:
            print("正在更新排名数据，所需时间可能较长，请等待...")
            print("注意不要选择此窗口的任何区域，否则会使程序暂停运行！")
            resp = urllib.request.urlopen(get_api_url('/getPercentInfo'))
            res = json.load(resp)
            STAT_PERCENT = res["data"]
            j = {"edition": serverEdition, "data": STAT_PERCENT}
            s = json.dumps(j)
            ensure_parent_dir(rate_path)
            with open(rate_path, 'w') as f:
                f.write(s)

    return STAT_PERCENT

    # 待测试





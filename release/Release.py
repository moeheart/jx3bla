# Created by moeheart at 11/13/2020
# 发布流程。只能在Windows下运行。

import json
import urllib.request
from Constants import *
import subprocess

if __name__ == "__main__":
    #第一步：运行Release.ps1
    #第二步：将生成的exe文件上传到网盘
    #第三步：运行此脚本
    
    url = input("请记录下载链接：")
    result = {"version": EDITION, "announcement": ANNOUNCEMENT, "updateurl": url}
    Jdata = json.dumps(result)
    jpost = {'jdata': Jdata}
    jparse = urllib.parse.urlencode(jpost).encode('utf-8')
    urllib.request.urlopen('http://%s:8009/setAnnouncement' % IP, data=jparse)


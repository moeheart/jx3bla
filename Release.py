# Created by moeheart at 11/13/2020
# 发布流程。只能在Windows下运行。

import json
import urllib.request
from Constants import *
import subprocess

if __name__ == "__main__":
    
    args = [r"powershell", r"Release.ps1", EDITION]
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    dt = p.stdout.read()
    
    url = input("exe文件生成完毕，在上传至网盘后，记录其下载链接：")
    result = {"version": EDITION, "announcement": ANNOUNCEMENT, "url": url}
    Jdata = json.dumps(result)
    jpost = {'jdata': Jdata}
    jparse = urllib.parse.urlencode(jpost).encode('utf-8')
    urllib.request.urlopen('http://139.199.102.41:8009/setAnnouncement', data=jparse)
    

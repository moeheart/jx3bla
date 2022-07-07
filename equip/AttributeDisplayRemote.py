# Created by moeheart at 08/31/2021
# 维护属性远程展示类，通过与服务器通信获取装备属性，避免反复读取数据。

from equip.AttributeCal import AttributeCal
import json
import urllib.request
from Constants import *

class AttributeDisplayRemote():

    def Display(self, str, occ):
        '''
        根据装备信息与心法，与服务器通信生成结果. 具体定义在AttributeDisplay中。
        不同心法关注的结果也不同.
        params:
        - str 字符串形式的装备信息.
        - occ 心法.
        returns:
        属性结果
        '''

        query = {"equipStr": str, "occ": occ}
        Jdata = json.dumps(query)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')

        for i in range(0, 5):
            resp = urllib.request.urlopen('http://%s:8009/getAttribute' % IP, data=jparse)
            if resp is None:
                print("连接失败，重试中...")
            else:
                break
        result = json.load(resp)

        return result

    def __init__(self):
        pass

if __name__ == "__main__":
    str = """27106	0	0	0	4			
51011	0	0	0	4	4		
54043	0	0	0	4	4		
30907	0	0	0	4			
29330	0	0	0				
29330	0	0	0				
54025	0	0	0	4	4		
29396	0	0	0	4			
53509	0	0	0	4	4		
51029	0	0	0	4	4		
50981	0	0	0	4	4		
26782	0	0	0	4	4	4	25692"""
    ad = AttributeDisplayRemote()
    res = ad.Display(str, '22h')
    for line in res:
        print(line, res[line])
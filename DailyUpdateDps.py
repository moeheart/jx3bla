# Created by moeheart at 02/05/201
# 每日的数据库更新，用于刷新DPS统计等占用资源的操作。

import numpy as np
import pymysql
import configparser
import json
import time


def RefreshDps():
    ip = "127.0.0.1"
    config = configparser.RawConfigParser()
    config.readfp(open('settings.cfg'))

    dbname = config.get('jx3bla', 'username')
    dbpwd = config.get('jx3bla', 'password')
    db = pymysql.connect(ip,dbname,dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    edition = "5.1.0"
    mapdetail = "25人英雄达摩洞"
    
    sql = """DROUP TABLE IF EXISTS HighestDps"""%edition
    cursor.execute(sql)

    sql = """SELECT * FROM ActorStat WHERE edition>='%s' AND win=1"""%edition
    cursor.execute(sql)
    result = cursor.fetchall()

    dpsAll = {"483": {}, "484": {}}

    for rec in result:
        server = rec[0]
        boss = rec[1]
        map = rec[3]
        if map not in dpsAll:
            continue
        dpsMap = dpsAll[map]
        if boss not in dpsMap:
            dpsMap[boss] = {}
        dpsBoss = dpsMap[boss]
        if server not in dpsBoss:
            dpsBoss[server] = {}
        dpsServer = dpsBoss[server]
        
        stat = rec[7].replace("'",'"')
        Jstat = json.loads(stat)
        
        for line in Jstat["effectiveDPSList"]:
            player = line[0]
            occ = line[1]
            dps = int(line[2])
            if player not in dpsServer:
                dpsServer[player] = [dps, occ]
            else:
                if dps > dpsServer[player][0]:
                    dpsServer[player] = [dps, occ]
                    
                    
    for map in dpsAll:
        mapName = {"483":"25人普通达摩洞", "484":"25人英雄达摩洞"}[map]
        for boss in dpsAll[map]:
            for server in dpsAll[map][boss]:
                for player in dpsAll[map][boss][server]:
                    dps = dpsAll[map][boss][server][player][0]
                    occ = dpsAll[map][boss][server][player][1]
                    sql = """INSERT INTO HighestDps VALUES ("%s", "%s", "%s", "%s", "%s", %d)"""%(server, player, occ, mapName, boss, dps)
                    cursor.execute(sql)
                    
    db.commit()
    
if __name__ == "__main__":
    RefreshDps()
                    
                    
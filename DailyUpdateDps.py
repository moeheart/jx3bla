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

    sql = """DROP TABLE IF EXISTS HighestDps"""
    cursor.execute(sql)

    sql = """CREATE TABLE HighestDps(
             server VARCHAR(32),
             player VARCHAR(32),
             occ VARCHAR(32),
             map VARCHAR(32),
             boss VARCHAR(32),
             num INT, 
             dps INT
             ) DEFAULT CHARSET utf8mb4"""
    cursor.execute(sql)

    sql = """DROP TABLE IF EXISTS PotHistory"""
    cursor.execute(sql)

    sql = """CREATE TABLE PotHistory(
             server VARCHAR(32),
             player VARCHAR(32),
             occ VARCHAR(32),
             battleDate VARCHAR(32),
             map VARCHAR(32),
             boss VARCHAR(32),
             severe INT, 
             pot VARCHAR(64)
             ) DEFAULT CHARSET utf8mb4"""
    cursor.execute(sql)

    sql = """SELECT * FROM ActorStat WHERE edition>='%s' AND win=1"""%edition
    cursor.execute(sql)
    result = cursor.fetchall()

    dpsAll = {"483": {}, "484": {}, "519": {}, "520": {}}
    potAll = {"483": {}, "484": {}, "519": {}, "520": {}}

    for rec in result:
        server = rec[0]
        boss = rec[1]
        battleDate = rec[2]
        map = rec[3]
        if map not in dpsAll:
            continue
        dpsMap = dpsAll[map]
        potMap = potAll[map]
        if boss not in dpsMap:
            dpsMap[boss] = {}
            potMap[boss] = {}
        dpsBoss = dpsMap[boss]
        potBoss = potMap[boss]
        if server not in dpsBoss:
            dpsBoss[server] = {}
            potBoss[server] = []
        dpsServer = dpsBoss[server]
        potServer = potBoss[server]

        stat = rec[7].replace("'",'"')
        Jstat = json.loads(stat)

        for line in Jstat["effectiveDPSList"]:
            player = line[0]
            occ = line[1]
            dps = int(line[2])
            if player not in dpsServer:
                dpsServer[player] = [dps, occ, 1]
            else:
                dpsServer[player][2] += 1
                if dps > dpsServer[player][0]:
                    dpsServer[player][0] = dps
                    dpsServer[player][1] = occ
                    
        for line in Jstat["potList"]:
            player = line[0]
            occ = line[1]
            severe = line[2]
            pot = line[4]
            if "小药" not in pot and "DPS" not in pot:
                potServer.append([player, occ, severe, pot, battleDate])

    for map in dpsAll:
        mapName = {"483":"25人普通达摩洞", "484":"25人英雄达摩洞", "519": "25人普通白帝江关", "520": "25人英雄白帝江关"}[map]
        for boss in dpsAll[map]:
            for server in dpsAll[map][boss]:
                for player in dpsAll[map][boss][server]:
                    dps = dpsAll[map][boss][server][player][0]
                    occ = dpsAll[map][boss][server][player][1]
                    num = dpsAll[map][boss][server][player][2]
                    #print(server, player, occ, mapName, boss, dps, num)
                    sql = """INSERT INTO HighestDps VALUES ("%s", "%s", "%s", "%s", "%s", %d, %d)"""%(server, player, occ, mapName, boss, num, dps)
                    cursor.execute(sql)

    for map in potAll:
        mapName = {"483":"25人普通达摩洞", "484":"25人英雄达摩洞", "519": "25人普通白帝江关", "520": "25人英雄白帝江关"}[map]
        for boss in potAll[map]:
            for server in potAll[map][boss]:
                for line in potAll[map][boss][server]:
                    player = line[0]
                    occ = line[1]
                    severe = line[2]
                    pot = line[3]
                    battleDate = line[4]
                    sql = """INSERT INTO PotHistory VALUES ("%s", "%s", "%s", "%s", "%s", "%s", %d, "%s")"""%(server, player, occ, battleDate, mapName, boss, severe, pot)
                    cursor.execute(sql)
                
    db.commit()
    
if __name__ == "__main__":
    RefreshDps()


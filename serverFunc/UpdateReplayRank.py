# Created by moeheart at 06/07/2022
# 更新复盘的数据排行，用于刷新复盘中各项数据的百分位数并存在数据库中。

import numpy as np
import pymysql
import configparser
import json
import time
import urllib.request
from tools.Names import *
from tools.Functions import parseEdition

# 数据库的屎山
STAT_ID = {"score": 3, "rhps": 18, "hps": 20, "rdps": 22, "ndps": 24, "mrdps": 26, "mndps": 28}
RANK_ID = {"score": 17, "rhps": 19, "hps": 21, "rdps": 23, "ndps": 25, "mrdps": 27, "mndps": 29}

def getDirection(key):
    if "delay" in key:
        return -1
    else:
        return 1

def getSingleStat(record):
    res = {}
    key1 = record[2]
    key2 = getIDFromMap(record[5])
    key3 = record[6]
    edition = record[11]
    if key2 not in MAP_DICT_RECORD_LOGS:
        return {}
    if key3 not in BOSS_RAW:
        return {}

    with open("database/ReplayProStat/%d" % record[8], "r") as f:
        s = f.read().replace('\n', '\\n').replace('\t', '\\t').replace("'", '"')

    d = json.loads(s)
    skillStat = d["skill"]
    for skillName in skillStat:
        for item in skillStat[skillName]:
            key4 = skillName
            key5 = item
            if key4 == "qczl" and key5 in ["num", "numPerSec"] and record[11] < parseEdition("8.1.0"):
                continue
            key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
            value = skillStat[skillName][item] * getDirection(key)
            if "delay" in key and value == 0:
                value = -9999
            res[key] = value
    if "healer" in d:
        for line in d["healer"]["table"]:
            if line["name"] == record[1]:
                key4 = "healer"
                for key5 in ["heal", "healEff", "rhps", "hps", "ahps", "ohps"]:
                    if key5 not in line:
                        continue
                    key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
                    value = line[key5] * getDirection(key)
                    res[key] = value

    for id in STAT_ID:
        if parseEdition(edition) >= parseEdition("8.3.5") or id != "score":
            key4 = "stat"
            key5 = id
            value = record[STAT_ID[id]]
            if value is None:
                continue
            key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
            res[key] = value
    return res

def getAllStat(records):
    allResults = {}
    for record in records:
        res = getSingleStat(record)
        uid = "%s-%s" % (record[0], record[1])
        for key in res:
            if key not in allResults:
                allResults[key] = {}
            if uid not in allResults[key]:
                allResults[key][uid] = res[key]
            else:
                allResults[key][uid] = max(res[key], allResults[key][uid])
    allFilteredResults = {}
    for key in allResults:
        allFilteredResults[key] = []
        for uid in allResults[key]:
            allFilteredResults[key].append(allResults[key][uid])
    return allResults

def getPercent(records):
    allResults = getAllStat(records)
    percentResults = {}
    for key in allResults:
        res_percent = []
        for i in range(101):
            num = np.percentile(allResults[key], i)
            num = int(num * 100000) / 100000
            if num > 1000000000:
                num = 1000000000
            res_percent.append(num)
        percentResults[key] = {"num": len(allResults[key]), "value": str(res_percent)}
    return percentResults
    
def getRank(value, table):
    '''
    获取单个数值的百分位排名.
    '''
    if value is None:
        return None
    l = 0
    r = 101
    while r > l + 1:
        m = (l + r + 1) // 2
        if value >= table[m]:
            l = m
        else:
            r = m
    percent = l
    return percent
    
def updatePercent(raw_rank, cursor, db):
    '''
    直接使用计算的结果更新数据库大项的百分位排名.
    '''
    
    edition = "8.0.2"
    
    sql = """SELECT * FROM ReplayProStat WHERE editionFull>=%d AND hold=1""" % parseEdition(edition)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    for record in result:
        key1 = record[2]
        key2 = getIDFromMap(record[5])
        key3 = record[6]
        shortID = record[8]
        hash = record[7]

        # 新赛季更新时删除，后续再进行改动
        try:
            if int(key2) < 573:
                continue
        except:
            sql = """UPDATE ReplayProStat SET hold=0 WHERE hash = '%s'""" % hash
            cursor.execute(sql)
            continue

        for id in STAT_ID:
            key4 = "stat"
            key5 = id
            key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
            if key not in raw_rank:
                continue
            order = json.loads(raw_rank[key]["value"])
            value = record[STAT_ID[id]]
            rank = getRank(value, order)
            # print("updating database")
            if rank is not None:
                sql = """UPDATE ReplayProStat SET %sRank = %d WHERE hash = '%s'""" % (id, rank, hash)
                cursor.execute(sql)
            # print("updated!")

        # TODO 在一周后恢复
        # sql = """UPDATE ReplayProStat SET hold=0 WHERE hash = '%s'""" % hash
        # cursor.execute(sql)

        # print("Complete: ", shortID)
        db.commit()

def RefreshStat():
    ip = "127.0.0.1"
    config = configparser.RawConfigParser()
    config.readfp(open('settings.cfg'))

    dbname = config.get('jx3bla', 'username')
    dbpwd = config.get('jx3bla', 'password')
    db = pymysql.connect(host=ip, user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    edition = "8.0.2"

    sql = """SELECT * FROM ReplayProStat WHERE editionFull>=%d""" % parseEdition(edition)
    cursor.execute(sql)
    result = cursor.fetchall()

    res = getPercent(result)

    sql = """DROP TABLE IF EXISTS ReplayProStatRank"""
    cursor.execute(sql)

    sql = """CREATE TABLE ReplayProStatRank(
             name VARCHAR(128),
             number INT,
             records VARCHAR(1280)) DEFAULT CHARSET utf8mb4"""
    cursor.execute(sql)

    try:
        for key in res:
            sql = """INSERT INTO ReplayProStatRank VALUES ("%s", %d, "%s")""" % (key, res[key]["num"], res[key]["value"])
            cursor.execute(sql)
    except:
        print(res[key])

    dataDict = {"rateEdition": str(int(time.time()))}
    
    updatePercent(res, cursor, db)

    try:
        for key in dataDict:
            sql = '''DELETE FROM PreloadInfo WHERE datakey = "%s";''' % key
            cursor.execute(sql)
            sql = '''INSERT INTO PreloadInfo VALUES ("%s", "%s");''' % (key, dataDict[key])
            cursor.execute(sql)
    except:
        print("fail!")
        
    # 通知主线程更新完毕
    
    resp = urllib.request.urlopen('http://%s:8009/refreshRateData' % "localhost")

    db.commit()
    db.close()
    
if __name__ == "__main__":
    RefreshStat()


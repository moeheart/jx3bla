# Created by moeheart at 06/07/2022
# 更新复盘的数据排行，用于刷新复盘中各项数据的百分位数并存在数据库中。

import numpy as np
import pymysql
import configparser
import json
import time
from tools.Names import *

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
    if key2 == "未知":
        return {}
    if key3 not in BOSS_RAW:
        return {}
    s = record[9].decode().replace("'", '"').replace('\n', '\\n').replace('\t', '\\t')
    d = json.loads(s)
    skillStat = d["skill"]
    for skillName in skillStat:
        for item in skillStat[skillName]:
            key4 = skillName
            key5 = item
            key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
            value = skillStat[skillName][item] * getDirection(key)
            if "delay" in key and value == 0:
                value = -9999
            res[key] = value
    for line in d["healer"]["table"]:
        if line["name"] == record[1]:
            key4 = "healer"
            for key5 in ["heal", "healEff"]:
                key = "%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5)
                value = line[key5] * getDirection(key)
                res[key] = value
    return res

def getAllStat(records):
    allResults = {}
    for record in records:
        res = getSingleStat(record)
        for key in res:
            if key not in allResults:
                allResults[key] = []
            allResults[key].append(res[key])
    return allResults

def getPercent(records):
    allResults = getAllStat(records)
    percentResults = {}
    for key in allResults:
        for i in range(100):
            num = np.percentile(allResults[key], i)
            key_percent = "%s-%d" % (key, i)
            percentResults[key_percent] = num
        key_percent = "%s-num" % key
        percentResults[key_percent] = len(allResults[key])
    return percentResults

def RefreshStat():
    ip = "127.0.0.1"
    config = configparser.RawConfigParser()
    config.readfp(open('settings.cfg'))

    dbname = config.get('jx3bla', 'username')
    dbpwd = config.get('jx3bla', 'password')
    db = pymysql.connect(host=ip, user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    edition = "7.8.0"

    sql = """SELECT * FROM ReplayProStat WHERE editionFull>=%d""" % parseEdition(edition)
    cursor.execute(sql)
    result = cursor.fetchall()

    res = getPercent(result)

    sql = """DROP TABLE IF EXISTS ReplayProStatRank"""
    cursor.execute(sql)

    sql = """CREATE TABLE ReplayProStatRank(
             name VARCHAR(128),
             number DOUBLE) DEFAULT CHARSET utf8mb4"""
    cursor.execute(sql)

    for key in res:
        sql = """INSERT INTO ReplayProStatRank VALUES ("%s", %.5f)""" % (key, res[key])
        cursor.execute(sql)

    db.commit()
    db.close()
    
if __name__ == "__main__":
    RefreshStat()


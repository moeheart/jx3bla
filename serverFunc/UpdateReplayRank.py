# Created by moeheart at 06/07/2022
# 更新复盘的数据排行，用于刷新复盘中各项数据的百分位数并存在数据库中。

import numpy as np
import pymysql
import configparser
import json
import time
import urllib
from tools.Names import *
from tools.Functions import parseEdition

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
    if key2 not in ["559", "560", "561", "573", "574", "575"]:
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
    for line in d["healer"]["table"]:
        if line["name"] == record[1]:
            key4 = "healer"
            for key5 in ["heal", "healEff", "rhps", "hps", "ahps", "ohps"]:
                if key5 not in line:
                    continue
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
        res_percent = []
        for i in range(101):
            num = np.percentile(allResults[key], i)
            num = int(num * 100000) / 100000
            if num > 1000000000:
                num = 1000000000
            res_percent.append(num)
        percentResults[key] = {"num": len(allResults[key]), "value": str(res_percent)}
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


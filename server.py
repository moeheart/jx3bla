# coding:utf-8
from flask import Flask, render_template, url_for, request, redirect, session, make_response, jsonify, abort
from flask import request    
from flask import make_response,Response
import urllib
import json
import re
import pymysql
import random
import time
import urllib.request
import hashlib
import configparser
import os
from Constants import *
from Functions import *

from painter import XiangZhiPainter

version = EDITION
ip = "139.199.102.41"
announcement = "全新的DPS统计已出炉，大家可以关注一下，看一下各门派的表现~"
app = Flask(__name__) 
app.config['JSON_AS_ASCII'] = False

def Response_headers(content):    
    resp = Response(content)    
    resp.headers['Access-Control-Allow-Origin'] = '*'    
    return resp
    
@app.route('/getAnnouncement', methods=['GET'])
def getAnnouncement():
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    sql = '''SELECT * FROM PreloadInfo;'''
    cursor.execute(sql)
    result = cursor.fetchall()
    version = result[0][0]
    announcement = result[0][1]
    updateurl = result[0][2]
    
    db.close()
    return jsonify({'version': version, 'announcement': announcement, 'url': updateurl})

@app.route('/setAnnouncement', methods=['POST'])
def setAnnouncement():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    version = jdata["version"]
    announcement = jdata["announcement"]
    updateurl = jdata["updateurl"]
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''DELETE FROM PreloadInfo;'''
    cursor.execute(sql)
    sql = '''INSERT INTO PreloadInfo VALUES ("%s", "%s", "%s");'''%(version, announcement, updateurl)
    cursor.execute(sql)
    
    db.commit()
    db.close()
    
    return jsonify({'result': 'success'})
    
@app.route('/getUuid', methods=['POST'])
def getUuid():
    mac = request.form.get('mac')
    userip = request.remote_addr
    intTime = int(time.time())
    
    hashStr = mac + ip + str(intTime)
    uuid = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''INSERT INTO UserInfo VALUES ("%s", "%s", "%s", "%s", %d, %d, %d);'''%(uuid, "", mac, userip, intTime, 0, 0)
    cursor.execute(sql)
    
    db.commit()
    db.close()
    
    return jsonify({'uuid': uuid})
    
@app.route('/setUserId', methods=['POST'])
def setUserId():
    uuid = request.form.get('uuid')
    id = request.form.get('id')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT * from UserInfo WHERE uuid = "%s"'''%(uuid)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    sql = '''SELECT * from UserInfo WHERE id = "%s"'''%(id)
    cursor.execute(sql)
    result2 = cursor.fetchall()
    
    if result:
    
        if result[0][1] != "":
            db.close()
            return jsonify({'result': 'hasuuid'})
        elif result2:
            db.close()
            return jsonify({'result': 'dupid'})
        else:
            sql = """UPDATE UserInfo SET id="%s" WHERE uuid="%s";"""%(id, uuid)
            cursor.execute(sql)
            db.commit()
            db.close()
            return jsonify({'result': 'success'})
    else:
        db.close()
        return jsonify({'result': 'nouuid'})
    
@app.route('/getDpsStat', methods=['POST'])
def getDpsStat():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    mapDetail = jdata["mapdetail"]
    boss = jdata["boss"]
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT statistics from DpsStat WHERE mapdetail = "%s" and boss = "%s"'''%(mapDetail, boss)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        J = result[0][0]
        db.close()
        return jsonify({'result': 'success', 'statistics': J})
    else:
        db.close()
        return jsonify({'result': 'norecord'})
        
@app.route('/Tianwang.html', methods=['GET'])
def Tianwang():
 
    server = request.args.get('server')
    ids = request.args.get('ids')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()

    playerDps = {}
    playerPot = {}

    ids_split = ids.split(' ')
    for id in ids_split:
        sql = '''SELECT occ, map, boss, dps, num from HighestDps WHERE server = "%s" and player = "%s"'''%(server, id)
        cursor.execute(sql)
        result = cursor.fetchall()
        playerDps[id] = {}
        for line in result:
            playerDps[id]["occ"] = line[0]
            if line[1] not in playerDps[id]:
                playerDps[id][line[1]] = [0, 0, 0, 0, 0, 0, 0]
            if line[2] in ["余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅"]:
                bossNum = {"余晖": 0, "宓桃": 1, "武雪散": 2, "猿飞": 3, "哑头陀": 4, "岳琳&岳琅": 5}[line[2]]
                playerDps[id][line[1]][bossNum] = line[3]
                playerDps[id][line[1]][6] += line[4]
                
        sql = '''SELECT occ, map, boss, battledate, severe, pot from PotHistory WHERE server = "%s" and player = "%s"'''%(server, id)
        cursor.execute(sql)
        result = cursor.fetchall()   
        playerPot[id] = {}
        for line in result:
            if line[1] not in playerPot[id]:
                playerPot[id][line[1]] = []
            if line[2] in ["余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅"]:
                playerPot[id][line[1]].append([line[2], line[3], line[4], line[5]])

    db.close()

    return render_template("Tianwang.html", playerDps=playerDps, playerPot=playerPot, edition=EDITION)
    
@app.route('/TianwangSearch.html', methods=['GET'])
def TianwangSearch():

    return render_template("TianwangSearch.html", edition=EDITION)
        
@app.route('/XiangZhiTable.html', methods=['GET'])
def XiangZhiTable():
    map = request.args.get('map')
    page = request.args.get('page')
    order = request.args.get('order')
    
    if map is None:
        map = '25人普通达摩洞'
    if page is None:
        page = 1
    if order is None:
        order = "score"
        
    page = int(page)
    
    if map not in ['25人普通达摩洞', '25人英雄达摩洞']:
        return jsonify({'result': '地图不正确'})
    if order not in ['score', 'battledate']:
        return jsonify({'result': '排序方式不正确'})
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    edition = "5.1.0"
    mapdetail = map

    sql = """SELECT server, id, score, battledate, mapdetail, edition, hash FROM XiangZhiStat WHERE edition>='%s' AND mapdetail='%s' AND public=1"""%(edition, mapdetail)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    db.close()
    
    result = list(result)
    
    pageNum = int((len(result) + 29) / 30)
    
    if order == "score":
        result.sort(key=lambda x:-x[2])
    elif order == "battledate":
        result.sort(key=lambda x:x[3])
        result = result[::-1]
        
        
    start = (page-1)*30
    end = page*30
    if start >= len(result):
        start = len(result)-1
    if end >= len(result):
        end = len(result)
    result = result[start:end]


    return render_template("XiangZhiTable.html", result=result, edition=EDITION, 
                           order=order, map=map, page=page, pagenum=pageNum)
    
@app.route('/XiangZhiData/png', methods=['GET'])
def XiangZhiDataPng():
    key = request.args.get('key')
    
    if key != None:
        db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
        cursor = db.cursor()
        
        sql = '''SELECT * FROM XiangZhiStat WHERE hash = "%s"'''%key
        cursor.execute(sql)
        result = cursor.fetchall()
        
        db.close()
        
        if result:
            line = result[0]
            stat = json.loads(line[7].replace("'", '"'))
            info = {"server": line[0],
                    "id": line[1],
                    "score": line[2],
                    "battledate": line[3],
                    "mapdetail": line[4],
                    "edition": line[5],
                    "hash": line[6],
                    "statistics": stat}
            fileList = os.listdir("static/png")
            print(stat)
            if "%s.png"%key not in fileList:
                printint = 1
                if len(key) < 16:
                    printint = 0
                painter = XiangZhiPainter(printint = printint)
                painter.paint(info, "static/png/%s.png"%key)
            return render_template("XiangZhiPng.html", key = key)
        
    return jsonify({'result': '记录不存在'})

@app.route('/uploadActorData', methods=['POST'])
def uploadActorData():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    server = jdata["server"]
    boss = jdata["boss"]
    battleDate = jdata["battledate"]
    mapDetail = jdata["mapdetail"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    
    if "win" not in jdata:
        jdata["win"] = 1
        
    win = int(jdata["win"])
    
    if "time" not in jdata:
        jdata["time"] = 0
    if "begintime" not in jdata:
        jdata["begintime"] = 0
    if "userid" not in jdata:
        jdata["userid"] = "unknown"
        
    submitTime = jdata["time"]
    battleTime = jdata["begintime"]
    userID = jdata["userid"]
    editionFull = parseEdition(edition)
    
    #增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT * from ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result and result[0][6] == 1:
        if parseEdition(result[0][4]) >= parseEdition(edition):
            print("Find Duplicated")
            db.close()
            return jsonify({'result': 'dupid'})
        else:
            print("Update edition")
        
    sql = '''DELETE FROM ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
        
    sql = """INSERT INTO ActorStat VALUES ("%s", "%s", "%s", "%s", "%s", "%s", %d, "%s")"""%(
        server, boss, battleDate, mapDetail, edition, hash, win, statistics)
    cursor.execute(sql)
    db.commit()
    db.close()
    
    return jsonify({'result': 'success'})
    
@app.route('/uploadXiangZhiData', methods=['POST'])
def uploadXiangZhiData():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    server = jdata["server"]
    id = jdata["id"]
    score = jdata["score"]
    battleDate = jdata["battledate"]
    mapDetail = jdata["mapdetail"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    
    if "public" not in jdata:
        jdata["public"] = 0
        
    public = jdata["public"]
    
    if "time" not in jdata:
        jdata["time"] = 0
    if "begintime" not in jdata:
        jdata["begintime"] = 0
    if "userid" not in jdata:
        jdata["userid"] = "unknown"
        
    submitTime = jdata["time"]
    battleTime = jdata["begintime"]
    userID = jdata["userid"]
    editionFull = parseEdition(edition)
    
    #增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT score from XiangZhiStat WHERE mapdetail = "%s"'''%mapDetail
    cursor.execute(sql)
    result = cursor.fetchall()
    
    num = 0
    numOver = 0
    for line in result:
        if line[0] == 0:
            continue
        num += 1
        if score > line[0]:
            numOver += 1
            
    print(num, numOver)
    
    sql = '''SELECT * from XiangZhiStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        if parseEdition(result[0][5]) >= parseEdition(edition):
            print("Find Duplicated")
            db.close()
            return jsonify({'result': 'dupid', 'num': num, 'numOver': numOver})
        else:
            print("Update edition")
    
    sql = '''DELETE FROM ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
        
    sql = """INSERT INTO XiangZhiStat VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s", %d)"""%(
        server, id, score, battleDate, mapDetail, edition, hash, statistics, public)
    cursor.execute(sql)
    db.commit()
    db.close()
    
    return jsonify({'result': 'success', 'num': num, 'numOver': numOver})
    
if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.readfp(open('./settings.cfg'))
    
    app.dbname = config.get('jx3bla', 'username')
    app.dbpwd = config.get('jx3bla', 'password')
    app.debug = config.getboolean('jx3bla', 'debug')
    
    app.run(host='0.0.0.0', port=8009, debug=app.debug, threaded=True)

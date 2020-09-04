# coding:utf-8
from flask import Flask, render_template, url_for, request, redirect, session, make_response, jsonify, abort
from flask import request    
from flask import make_response,Response
import urllib
import json
import read
import re
import pymysql
import random
import time
import urllib.request
import hashlib
import configparser

version = "3.5.0"
ip = "127.0.0.1"
app = Flask(__name__) 
app.config['JSON_AS_ASCII'] = False

def Response_headers(content):    
    resp = Response(content)    
    resp.headers['Access-Control-Allow-Origin'] = '*'    
    return resp

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
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT * from ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        db.close()
        return jsonify({'result': 'dupid'})
        
    sql = """INSERT INTO ActorStat VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")"""%(
        server, boss, battleDate, mapDetail, edition, hash, statistics)
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
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT score from XiangZhiStat WHERE mapdetail = "%s"'''%mapDetail
    cursor.execute(sql)
    result = cursor.fetchall()
    
    num = 0
    numOver = 0
    for line in result:
        num += 1
        if score > line[0]:
            numOver += 1
            
    print(num, numOver)
    
    sql = '''SELECT * from XiangZhiStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        db.close()
        return jsonify({'result': 'dupid', 'num': num, 'numOver': numOver})
        
    sql = """INSERT INTO XiangZhiStat VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s")"""%(
        server, id, score, battleDate, mapDetail, edition, hash, statistics)
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

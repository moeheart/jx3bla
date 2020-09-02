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

version = "3.4.0"
app = Flask(__name__) 
app.config['JSON_AS_ASCII'] = False

def Response_headers(content):    
    resp = Response(content)    
    resp.headers['Access-Control-Allow-Origin'] = '*'    
    return resp

@app.route('/uploadActorData', methods=['POST'])
def postregister():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    server = jdata["server"]
    boss = jdata["boss"]
    battleDate = jdata["battledate"]
    mapDetail = jdata["mapdetail"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    
    db = pymysql.connect("127.0.0.1",app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = """SELECT * from ActorStat WHERE hash = '%s'"""%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        db.close()
        return jsonify({'result': 'dupid'})
        
    sql = """INSERT INTO ActorStat VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"""%(
        server, boss, battleDate, mapDetail, edition, hash, statistics)
    cursor.execute(sql)
    db.commit()
    db.close()
    
    return jsonify({'result': 'success'})
    
@app.route('/uploadXiangZhiData', methods=['POST'])
def postregister():
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
    
    db = pymysql.connect("127.0.0.1",app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = """SELECT * from XiangZhiStat WHERE hash = '%s'"""%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        db.close()
        return jsonify({'result': 'dupid'})
        
    sql = """INSERT INTO XiangZhiStat VALUES ('%s', '%s', %d, '%s', '%s', '%s', '%s', '%s')"""%(
        server, id, score, battleDate, mapDetail, edition, hash, statistics)
    cursor.execute(sql)
    db.commit()
    db.close()
    
    return jsonify({'result': 'success'})
    
if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.readfp(open('./settings.cfg'))
    
    app.dbname = config.get('healerhelper', 'username')
    app.dbpwd = config.get('healerhelper', 'password')
    app.debug = config.getboolean('healerhelper', 'debug')
    
    app.run(host='0.0.0.0', port=8009, debug=app.debug, threaded=True)

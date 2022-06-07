# Created by moeheart at 06/07/2022
# 百分位生成器，用于从服务器数据获取各种统计数据的百分位数。

import numpy as np
import pymysql
import configparser
import time

if __name__ == "__main__":
    # 数据准备
    print("连接数据库...")
    ip = "139.199.102.41"
    config = configparser.RawConfigParser()
    config.readfp(open('settings.cfg'))

    dbname = config.get('jx3bla', 'username')
    dbpwd = config.get('jx3bla', 'password')
    db = pymysql.connect(host=ip, user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    sql = """SELECT * FROM ReplayProStatRank"""
    cursor.execute(sql)
    result = cursor.fetchall()

    db.close()

    print("数据读取完成！")

    resultDict = {}
    for line in result:
        resultDict[line[0]] = {"num": line[1], "value": line[2]}

    # 输出python文件
    g = open("replayer/Percent.py", "w", encoding='utf-8')
    text = """# [Auto-Generated File]
STAT_PERCENT = %s"""%(str(resultDict))
    g.write(text)
    g.close()


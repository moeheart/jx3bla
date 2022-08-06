# Created by moeheart at 08/06/2022
# 这个脚本把数据库的字段提取成文件，用来解决长字段存入数据库后效率爆炸的问题
# 往mysql里放100kB的字段纯属脑子进水，以后不许这样了

import pymysql
import configparser

START = 1
END = 1000

config = configparser.RawConfigParser()
config.readfp(open('./settings.cfg'))

name = config.get('jx3bla', 'username')
pwd = config.get('jx3bla', 'password')
db = pymysql.connect(host="127.0.0.1", user=name, password=pwd, database="jx3bla", port=3306, charset='utf8')

cursor = db.cursor()

for start in range(START, END + 1, 100):
    end = start + 100
    print("Running from %d to %d" % (start, end))

    sql = """SELECT statistics, shortID FROM ReplayProStat WHERE shortID >= %d AND shortID <= %d;"""%(start, end)
    cursor.execute(sql)
    result = cursor.fetchall()

    for line in result:
        f = open("database/ReplayProStat/%d" % line[1], "w")
        f.write(line[0])
        f.close()

db.close()
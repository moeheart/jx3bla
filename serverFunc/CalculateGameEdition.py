# created by moeheart on 02/28/2024
# 这是为服务器中的数据更新游戏版本字段的代码，用于计算数据所对应的版本。如果游戏版本更新后上传了新的数据，但是服务器还没有更新，则需要运行这个脚本。
# 注意：第二次以后的运行需要移除ALTER TABLE的部分，其存在仅用于显示逻辑。

import pymysql
import configparser

from tools.Names import *

config = configparser.RawConfigParser()
config.readfp(open('./settings.cfg'))

name = config.get('jx3bla', 'username')
pwd = config.get('jx3bla', 'password')
db = pymysql.connect(host="127.0.0.1", user=name, password=pwd, database="jx3bla", port=3306, charset='utf8')

cursor = db.cursor()

sql = "ALTER TABLE ReplayProStat ADD COLUMN gameEdition VARCHAR(32)"
cursor.execute(sql)

sql = "SELECT hash, shortID, battletime, mapdetail from ReplayProStat"
cursor.execute(sql)
result = cursor.fetchall()
for line in result:
    mapid = getIDFromMap(line[3])
    gameedition = getGameEditionFromTime(mapid, line[2])
    sql = 'UPDATE ReplayProStat SET gameEdition="%s" WHERE hash="%s"' % (gameedition, line[0])

sql = "ALTER TABLE ActorStat ADD COLUMN gameEdition VARCHAR(32)"
cursor.execute(sql)

sql = "SELECT hash, battletime, mapdetail from ActorStat"
cursor.execute(sql)
result = cursor.fetchall()
for line in result:
    mapid = getIDFromMap(line[2])
    gameedition = getGameEditionFromTime(mapid, line[1])
    sql = 'UPDATE ActorStat SET gameEdition="%s" WHERE hash="%s"' % (gameedition, line[0])

db.commit()
db.close()
import configparser
import pymysql
import os

config = configparser.RawConfigParser()
config.read_file(open('./settings.cfg'))

dbname = config.get('jx3bla', 'username')
dbpwd = config.get('jx3bla', 'password')

db = pymysql.connect(host="127.0.0.1", user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
cursor = db.cursor()

sql = '''SELECT shortID FROM ReplayProStat WHERE editionfull<8008000 limit 100;'''
cursor.execute(sql)
result = cursor.fetchall()

for line in result:
    id = line[0]
    f = "database/ReplayProStat/%s" % id
    os.system("rm %s" % f)
    sql = '''DELETE FROM ReplayProStat WHERE shortID=%s;''' % id
    cursor.execute(sql)

db.commit()
db.close()

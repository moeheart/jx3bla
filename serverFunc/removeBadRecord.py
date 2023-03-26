import configparser
import pymysql

l = []
with open("serverFunc/remove.txt") as f:
    s = f.read()
    l = s.split('\n')

print(l)

config = configparser.RawConfigParser()
config.readfp(open('./settings.cfg'))

dbname = config.get('jx3bla', 'username')
dbpwd = config.get('jx3bla', 'password')

db = pymysql.connect(host="127.0.0.1", user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
cursor = db.cursor()

for line in l:
    sql = '''DELETE FROM ReplayProStat WHERE shortID=%s;''' % line
    cursor.execute(sql)
    sql = '''DELETE FROM ReplayProStat WHERE battleID="%s";''' % line
    cursor.execute(sql)

db.commit()
db.close()
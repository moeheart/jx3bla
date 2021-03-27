import pymysql
import configparser

print("This operation is DANGEROUS!")
print("To continue, type 'yes':")
res = input()
if (res != "yes"):
    exit
    
config = configparser.RawConfigParser()
config.readfp(open('./settings.cfg'))

name = config.get('jx3bla', 'username')
pwd = config.get('jx3bla', 'password')
db = pymysql.connect("127.0.0.1", name, pwd,"jx3bla",port=3306,charset='utf8mb4')

cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS XiangZhiStat")
cursor.execute("DROP TABLE IF EXISTS ActorStat")
cursor.execute("DROP TABLE IF EXISTS PreloadInfo")
cursor.execute("DROP TABLE IF EXISTS HighestDps")

sql = """CREATE TABLE XiangZhiStat (
         server VARCHAR(32),
         id VARCHAR(32),
         score INT,
         battledate VARCHAR(32),
         mapdetail VARCHAR(32),
         edition VARCHAR(32),
         hash VARCHAR(32) primary key,
         statistics VARCHAR(16000), 
         public INT,
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)


sql = """CREATE TABLE ActorStat (
         server VARCHAR(32),
         boss VARCHAR(32), 
         battledate VARCHAR(32),
         mapdetail VARCHAR(32),
         edition VARCHAR(32),
         hash VARCHAR(32) primary key,
         statistics VARCHAR(16000)
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

sql = """CREATE TABLE PreloadInfo(
         edition VARCHAR(32),
         announcement VARCHAR(1024), 
         updateurl VARCHAR(1024),
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

sql = """CREATE TABLE HighestDps(
         server VARCHAR(32),
         player VARCHAR(32),
         occ VARCHAR(32),
         map VARCHAR(32),
         boss VARCHAR(32),
         dps INT
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

sql = """CREATE TABLE UserInfo(
         uuid VARCHAR(32) primary key,
         id VARCHAR(32),
         mac VARCHAR(32),
         ip VARCHAR(32),
         regtime INT,
         score INT,
         exp INT,
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

db.commit()
db.close()
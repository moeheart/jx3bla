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

#在XiangZhiStat最后增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)

sql = """CREATE TABLE ReplayProStat (
         server VARCHAR(32),
         id VARCHAR(32),
         occ VARCHAR(32),
         score INT,
         battledate VARCHAR(32),
         mapdetail VARCHAR(32),
         boss VARCHAR(32),
         hash VARCHAR(32) primary key,
         shortID INT,
         public INT,
         edition VARCHAR(32),
         editionfull INT,
         replayedition VARCHAR(32),
         userid VARCHAR(32),
         battletime INT, 
         submittime INT
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

# ReplayProStat表，支持更广泛形式的复盘数据
# 加一个数据battleID VARCHAR(32), 链接到ActorStat中.
# 扩展ReplayProStat, 加13个数据 scoreRank INT, rhps DOUBLE, rhpsRank INT, hps DOUBLE, hpsRank INT, 
# rdps DOUBLE, rdpsRank INT, ndps DOUBLE, ndpsRank INT, mrdps DOUBLE, mrdpsRank INT, mndps DOUBLE, mndpsRank INT, hold INT
# 02/28/2024 再次扩展ReplayProStat，加1个字段 gameEdition VARCHAR(32)

sql = """CREATE TABLE ReplayProInfo(
         dataname VARCHAR(32),
         datavalue VARCHAR(32),
         datavalueint INT
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)
sql = """INSERT INTO ReplayProInfo VALUES ("num", "", 0)"""
cursor.execute(sql)

# ReplayProInfo整体信息

sql = """CREATE TABLE ActorStat (
         server VARCHAR(32),
         boss VARCHAR(32), 
         battledate VARCHAR(32),
         mapdetail VARCHAR(32),
         edition VARCHAR(32),
         hash VARCHAR(32) primary key,
         win INT,
         statistics VARCHAR(16000)
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

#在ActorStat最后增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)
# 02/28/2024 再次扩展ActorStat，加1个字段 gameEdition VARCHAR(32)

# sql = """CREATE TABLE PreloadInfo(
#          edition VARCHAR(32),
#          announcement VARCHAR(1024),
#          updateurl VARCHAR(1024),
#          ) DEFAULT CHARSET utf8mb4"""
# cursor.execute(sql)

# 修改为更通用的格式

sql = """CREATE TABLE PreloadInfo(
         datakey VARCHAR(32),
         datavalue VARCHAR(1024), 
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
         exp INT
         ) DEFAULT CHARSET utf8mb4"""
cursor.execute(sql)

#在UserInfo最后增加11个字段：item(1-10) INT, lvl INT

sql = """CREATE TABLE ScoreInfo(
         id VARCHAR(32),
         userid VARCHAR(32),
         time INT,
         reason VARCHAR(128), 
         val INT) DEFAULT CHARSET utf8mb4"""

#新建一个表ScoreInfo，表示积分变动，记录scoreid，userid，时间，原因，变化量。

sql = """CREATE TABLE CommentInfo(
         id VARCHAR(32),
         server VARCHAR(32),
         player VARCHAR(32),
         userid VARCHAR(32),
         mapdetail VARCHAR(32),
         instanceid VARCHAR(32),
         time INT,
         type INT,
         power INT,
         content VARCHAR(1280),
         pot VARCHAR(1280)) DEFAULT CHARSET utf8mb4"""

#新建一个表CommentInfo，用于收集评价，记录commentid，区服，玩家名，userid，时间，分类，等级，评论内容

sql = """CREATE TABLE InstanceInfo(
         id VARCHAR(32),
         server VARCHAR(32),
         date VARCHAR(32),
         cd VARCHAR(32)) DEFAULT CHARSET utf8mb4"""

#新建一个表InstanceInfo，表示副本信息，记录instanceid，区服，日期，副本ID。

sql = """CREATE TABLE ReplayProStatRank(
         name VARCHAR(128),
         number DOUBLE) DEFAULT CHARSET utf8mb4"""
#ReplayProStatRank，记录统计的数据种类和值。

sql = """CREATE TABLE EquipmentInfo(
         id VARCHAR(32),
         server VARCHAR(32),
         uid VARCHAR(32),
         occ VARCHAR(32),
         equip VARCHAR(512),
         score VARCHAR(8),
         time INT
         ) DEFAULT CHARSET utf8mb4"""
#EquipmentInfo，用于缓存玩家的装备表，这样在装备表读取失败时可以尝试补救
# 注意id是玩家中文名（游戏ID），uid才是数字id

db.commit()
db.close()
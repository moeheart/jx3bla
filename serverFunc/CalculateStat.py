# Created by moeheart at 10/13/2022
# 从数据库的result计算其rhps、hps，只在8.2版本更新时使用一次，但其中的逻辑可以复用.

def getSingleStat(record, cursor):
    '''
    处理单条数据.
    '''
    
    shortID = record[8]

    with open("database/ReplayProStat/%d" % shortID, "r") as f:
        s = f.read().replace('\n', '\\n').replace('\t', '\\t').replace("'", '"')
    d = json.loads(s)
    
    rhps = d["skill"]["healer"].get("rhps", None)
    hps = d["skill"]["healer"].get("hps", None)
    
    rhpsData = "NULL"
    if rhps is not None:
        rhpsData = "%.2f" % rhps
    
    hpsData = "NULL"
    if hps is not None:
        hpsData = "%.2f" % hps
    
    sql = """UPDATE ReplayProStat SET rhps = %s WHERE shortID = %d""" % (rhpsData, shortID)
    cursor.execute(sql)
    sql = """UPDATE ReplayProStat SET hps = %s WHERE shortID = %d""" % (hpsData, shortID)
    cursor.execute(sql)
    

def calculate():
    '''
    开始计算.
    '''
    ip = "127.0.0.1"
    config = configparser.RawConfigParser()
    config.readfp(open('settings.cfg'))

    dbname = config.get('jx3bla', 'username')
    dbpwd = config.get('jx3bla', 'password')
    db = pymysql.connect(host=ip, user=dbname, password=dbpwd, database="jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    edition = "7.8.0"

    sql = """SELECT * FROM ReplayProStat WHERE editionFull>=%d""" % parseEdition(edition)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    for record in result:
        getSingleStat(record, cursor)
        
    db.commit()
    db.close()
    
if __name__ == "__main__":
    calculate()
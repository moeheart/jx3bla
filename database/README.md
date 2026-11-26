# 数据库与复盘文件

`ActorStat/` 和 `ReplayProStat/` 存放服务端保存的复盘正文。迁移已有部署时，使用经授权取得的同一停写时间点的 MySQL 备份与这两个目录；完整恢复需要索引、业务数据和文件正文。

## 核对回放表结构

从有备份授权的真实部署取得可信的 schema 导出，在一个全新、与业务隔离的 MySQL 数据库中导入。下面的 shell 命令使用预先配置的 MySQL 登录方式。先确认用于恢复的连接和库名指向空的隔离库。

```sh
mysqldump --no-data --skip-triggers --no-tablespaces --set-gtid-purged=OFF --default-character-set=utf8mb4 --result-file=replay-schema.sql jx3bla ReplayProStat ActorStat ReplayProStatRank PreloadInfo ReplayProInfo
mysql --database=jx3bla_restore < replay-schema.sql
mysql --database=jx3bla_restore --default-character-set=utf8mb4 --batch --skip-column-names < database/replay-columns.sql > replay-columns.tsv
python -m tools.CheckReplaySchema replay-columns.tsv
```

MySQL 负责解释 DDL。[查询](replay-columns.sql)只读已导入表的元数据，导出无表头的 UTF-8 TSV，每行依次为库名、表名、列序号、列名、存储引擎。接收端按位置写入，排名程序按位置取数。本地检查器只核对上述五张表的列名、顺序及 InnoDB 引擎。完整迁移另需核对数据类型、索引、其他业务表（包括 `UserInfo`、`ScoreInfo`、`EquipmentInfo`）、应用配置和复盘文件，再在隔离库验证接收、重复上传、读回和排名。历史初始化脚本可从 8.16.8 源码基线 `531aa11` 查阅。

## 核对回放编号

`--no-data` 导出没有初始行。首次接收新回放前，服务端依赖 `ReplayProInfo` 中唯一的 `dataname='num'` 行来分配下一个公开编号。隔离恢复后，用下列只读查询检查计数与已占用的最大编号。

```sql
SELECT COUNT(*) AS counter_rows,
       MIN(datavalueint) AS counter_value,
       (SELECT COALESCE(MAX(shortID), 0) FROM ReplayProStat) AS largest_replay_id
FROM ReplayProInfo
WHERE dataname = 'num';
```

已有部署须保留原计数器。验收要求 `counter_rows = 1`、`counter_value` 非空且大于等于 `largest_replay_id`。计数器可以高于现存记录的最大编号，恢复时保留该值可避免重用已删除记录的编号。仅在刚创建、尚未接收写入的空库中，确认 `ReplayProStat` 为空且 `num` 行缺失后初始化一次。

```sql
INSERT INTO ReplayProInfo (dataname, datavalue, datavalueint)
SELECT 'num', '', 0
WHERE NOT EXISTS (SELECT 1 FROM ReplayProInfo WHERE dataname = 'num')
  AND NOT EXISTS (SELECT 1 FROM ReplayProStat);
```

隔离验证期间仅启动一个初始化进程；再次执行上面的只读查询确认初值为 0。复盘数据库与文件系统的一致性还需通过一次隔离上传、回读和重复上传验证。

# jx3bla 服务器迁移 TODO

本文记录从旧服务器 `116.211.150.188` 迁移到 `moeheart.cn` 的准备项、执行项和校验项。

当前阶段只做评估和准备，不迁移、不切流量。迁移窗口可接受约 12 小时服务中断，因此正式切换时可以采用“停写后一次性收尾”的保守方案，不需要引入 MySQL 主从或双写。

## 现状快照

快照时间：2026-06-10。

旧服务器：

- SSH：`root@116.211.150.188 -p 31662`
- 主项目目录：`/root/jx3bla`
- API 进程：`python3 server.py`，监听 `0.0.0.0:8009`
- nginx：宝塔路径 `/www/server/nginx`
- MySQL：`8.0.42`，`bind-address = 127.0.0.1`
- 根分区：约 `87G`，已用约 `79G`，剩余约 `4.9G`
- inode：约 `5.6M` 总量，已用约 `1.8M`
- 业务 systemd：无 jx3bla 服务，API 是手工/tmux 形态

目标服务器：

- SSH：`ubuntu@124.222.132.122`
- 现有域名：`moeheart.cn`
- 已有跳板服务：`jx3blaaddress.moeheart.cn -> 127.0.0.1:8033`
- Python：`3.12.3`
- MySQL：`8.0.45`
- 根分区：约 `178G`，剩余约 `162G`
- inode：约 `12M` 可用
- `8009` 当前可作为 jx3bla API 端口候选
- MySQL 当前没有 `jx3bla` 库，也没有 `jx3bla` 用户

## 必迁内容

- [ ] `/root/jx3bla` 项目运行目录。
- [ ] `/root/jx3bla/settings.cfg`。
- [ ] MySQL 库 `jx3bla`。
- [ ] `/root/jx3bla/database/ActorStat`。
- [ ] `/root/jx3bla/database/ReplayProStat`。
- [ ] `/root/jx3bla/equip/resources`。
- [ ] `/www/wwwroot/default` 的 JX3 Logs 静态前端，或用重新构建后的前端替代。
- [ ] 旧机 root crontab 中的每日排名更新任务。
- [ ] nginx 站点配置：`jx3bla.moeheart.cn` 和必要的 SPA fallback。
- [ ] 跳板服务返回值：最终从旧 IP 改到新域名。

## 数据规模基线

MySQL 关键表精确行数：

| 表 | 行数 |
| --- | ---: |
| `ReplayProStat` | `1,749,325` |
| `ActorStat` | `119,379` |
| `EquipmentInfo` | `500,760` |
| `ReplayProStatRank` | `37,543` |
| `UserInfo` | `22,336` |
| `CommentInfo` | `37` |
| `PreloadInfo` | `4` |

MySQL 体量：

- `/var/lib/mysql` 约 `3.9G`
- `jx3bla` 逻辑库约 `1.15G`
- 最大表为 `ReplayProStat` 和 `EquipmentInfo`

文件型统计数据：

| 路径 | 文件数 | payload 体量 | `du` 体量 | 最新写入 |
| --- | ---: | ---: | ---: | --- |
| `database/ReplayProStat` | `1,621,418` | `37.65 GiB` | 约 `41G` | `2026-06-10 22:33:21` |
| `database/ActorStat` | `73,118` | `21.97 GiB` | 约 `23G` | `2026-06-10 22:33:21` |
| `equip/resources` | `257` | `1.90 GiB` | 约 `1.9G` | `2026-04-05 15:54:25` |

这些统计文件仍在写入。正式迁移前如果服务未停写，不能把一次静态 rsync 当成最终结果。

## 已知特殊点

- [ ] 旧机 root crontab 有业务任务：

```cron
0 4 * * * /root/jx3bla/serverFunc/updateReplayRank.sh
```

脚本内容：

```bash
cd /root/jx3bla
python3 -m serverFunc.UpdateReplayRank
```

该任务会重建 `ReplayProStatRank`、更新 `PreloadInfo.rateEdition`，并访问 `http://localhost:8009/refreshRateData` 刷新 API 进程内缓存。迁移后必须恢复，否则排名百分位会停更。

- [ ] 旧机 `/root/jx3bla/requirements.txt` 是 UTF-16 LE 编码。目标机安装依赖时建议使用本地仓库 UTF-8 版本，或先转换编码。
- [ ] 旧机仓库不是干净状态，不能只依赖 `git clone`：
  - `database/ActorStat/README.md` 被删除。
  - `database/ReplayProStat/README.md` 被删除。
  - `serverFunc/UpdateReplayRank.py` 有修改。
  - `serverFunc/updateReplayRank.sh` 有修改。
- [ ] JX3 Logs 静态资源中硬编码了 `http://116.211.150.188:8009/...`。迁移时需要重建前端或替换 API 基址。
- [ ] 旧机 `:888` 当前对 `/`、`/getMultiRank.html`、`/<occ>/<id>` 等路径返回 `404`，不应盲目照搬为 logs 入口。
- [ ] `jx3logs.com` 根页可返回 JX3 Logs 静态前端，但深链当前也会 `404`。目标 nginx 应配置 SPA fallback 到 `index.html`。

## 推荐目标形态

- [ ] API 服务在目标机监听 `127.0.0.1:8009` 或 `0.0.0.0:8009`。优先只绑定本机，再由 nginx 反代。
- [ ] `jx3bla.moeheart.cn` 作为统一入口。
- [ ] API 路径反代到 `127.0.0.1:8009`。
- [ ] Logs 前端静态资源由 nginx 直接服务。
- [ ] 前端深链 fallback 到 `index.html`。
- [ ] 跳板 JSON 最终改为：

```json
{
  "api": {"host": "jx3bla.moeheart.cn", "port": 80},
  "logs": {"host": "jx3bla.moeheart.cn", "port": 80}
}
```

## 迁移前准备

- [ ] 确认当前客户端版本已稳定发布，可以进入迁移窗口。
- [ ] 确认 `jx3blaaddress.moeheart.cn` 的跳板机制已经被客户端使用。
- [ ] 在目标机创建 `/home/ubuntu/jx3bla`。
- [ ] 在目标机准备 Python venv。
- [ ] 验证 Python 3.12 是否能运行 `server.py` 和 `serverFunc.UpdateReplayRank`。
- [ ] 如果 Python 3.12 不兼容，准备 Python 3.8/3.10 环境。
- [ ] 在目标机创建 MySQL 库 `jx3bla`。
- [ ] 在目标机创建 MySQL 用户 `jx3bla`，并只授予该库权限。
- [ ] 生成目标机到旧机的 SSH key 或配置可用凭据。
- [ ] 确认目标机可以访问旧机 `116.211.150.188:31662`。
- [ ] 预同步 `/root/jx3bla/database`。
- [ ] 预同步 `/root/jx3bla/equip`。
- [ ] 预同步项目代码和其它运行资源。
- [ ] 准备 JX3 Logs 前端的新构建或 API 地址替换方案。
- [ ] 准备目标机 nginx 配置草稿。
- [ ] 准备回滚方案：跳板 JSON 保持或恢复为旧服务器。

## 正式迁移窗口

允许服务中断约 12 小时。建议按以下顺序执行。

- [ ] 在旧机停止 API 进程 `python3 server.py`。
- [ ] 在旧机临时停用 root crontab 的 jx3bla 排名任务。
- [ ] 确认旧机 `:8009` 不再接受写入。
- [ ] 从目标机拉取旧机最终增量：
  - `/root/jx3bla/database`
  - `/root/jx3bla/equip`
  - `/root/jx3bla/static`
  - `/root/jx3bla/templates`
  - `/root/jx3bla/icons`
  - `/root/jx3bla/release`
  - `/root/jx3bla/serverFunc`
  - 其它运行所需源码文件
- [ ] 流式导出旧机 MySQL `jx3bla`。
- [ ] 在目标机导入 MySQL `jx3bla`。
- [ ] 将目标机 `settings.cfg` 指向目标机本地 MySQL。
- [ ] 在目标机启动 API。
- [ ] 在目标机执行一次 `python3 -m serverFunc.UpdateReplayRank` 或至少调用 `/refreshRateData`。
- [ ] 配置并 reload 目标机 nginx。
- [ ] 恢复目标机每日 04:00 排名 cron。
- [ ] 完成 smoke test。
- [ ] 修改跳板服务 JSON，把目标从旧 IP 切到 `jx3bla.moeheart.cn:80`。
- [ ] 再跑一次客户端 smoke test。

## 验证清单

API 验证：

- [ ] `GET /getAnnouncement?edition=8.15.5`
- [ ] `POST /getUuid`
- [ ] `POST /getUserInfo`
- [ ] `POST /uploadActorData`
- [ ] `POST /uploadReplayPro`
- [ ] `POST /uploadCombinedData`
- [ ] `GET /getReplayPro?id=<shortID>`
- [ ] `GET /getBattle?hash=<hash>`
- [ ] `GET /getRank?...`
- [ ] `GET /getXinfaRank?...`
- [ ] `GET /refreshRateData`

Logs 前端验证：

- [ ] `http://jx3bla.moeheart.cn/`
- [ ] `http://jx3bla.moeheart.cn/getMultiRank.html?...`
- [ ] `http://jx3bla.moeheart.cn/<occ>/<shortID>`
- [ ] 前端实际请求的 API 不再包含 `116.211.150.188`。
- [ ] 页面刷新深链不返回 nginx 404。

数据库校验：

- [ ] `ReplayProStat` 行数与迁移前基线一致或只差迁移窗口内预期变化。
- [ ] `ActorStat` 行数与迁移前基线一致或只差迁移窗口内预期变化。
- [ ] `EquipmentInfo` 行数与迁移前基线一致或只差迁移窗口内预期变化。
- [ ] `PreloadInfo` 包含 `version`、`announcement`、`updateurl`、`rateEdition`。
- [ ] `ReplayProInfo` 中短 ID 计数逻辑正常。

文件校验：

- [ ] `database/ReplayProStat` 文件数量与迁移前基线一致或只差迁移窗口内预期变化。
- [ ] `database/ActorStat` 文件数量与迁移前基线一致或只差迁移窗口内预期变化。
- [ ] 抽样读取若干 `shortID` 对应文件。
- [ ] 抽样读取若干 `hash` 对应文件。

客户端验证：

- [ ] 启动时能从 `jx3blaaddress.moeheart.cn` 解析地址。
- [ ] 公告读取正常。
- [ ] 上传复盘正常。
- [ ] 设置页远程读取正常。
- [ ] 评论上传正常。
- [ ] logs 按钮正常打开新域名页面。
- [ ] 跳板失败时仍可按回退逻辑访问旧地址。

## 回滚方案

如果目标机验证失败：

- [ ] 不修改跳板 JSON，客户端继续访问旧机。
- [ ] 如果已经修改跳板 JSON，立即改回：

```json
{
  "api": {"host": "116.211.150.188", "port": 8009},
  "logs": {"host": "116.211.150.188", "port": 888}
}
```

- [ ] 重新启动旧机 `python3 server.py`。
- [ ] 恢复旧机 root crontab 排名任务。
- [ ] 保留目标机数据副本，用于排查问题，不立即删除。

## 待确认问题

- [ ] `logs` 的最终入口是否统一到 `jx3bla.moeheart.cn`，还是另设 `jx3logs.moeheart.cn`。
- [ ] JX3 Logs 前端源码在哪里，优先重建而不是直接替换打包产物。
- [ ] 目标机是否继续沿用 tmux 运行 API，还是迁移后改成 systemd。
- [ ] API 是否只绑定 `127.0.0.1:8009`。
- [ ] 旧机上的宝塔/phpMyAdmin 是否需要保留访问，或迁移后完全废弃。
- [ ] 迁移完成后旧机保留多久作为只读回滚点。

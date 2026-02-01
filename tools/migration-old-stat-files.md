# 旧统计文件迁移（先备份，后清理）

服务端会把大体积统计写成文件：

- `database/ActorStat/<hash>`
- `database/ReplayProStat/<shortID>`

当服务器磁盘空间紧张时，可以按文件修改时间（mtime）把旧文件迁移到本地保存。

重要：为避免“传输/解压失败但远端已删除”导致数据丢失，本方案现在默认只做备份；删除必须显式执行。

## 脚本

- `tools/migrate_old_stat_files.ps1`（推荐：Windows / PowerShell）
- `tools/migrate_old_stat_files.sh`（备用：bash / Linux / Git Bash）

## PowerShell（推荐）

### 前置要求

- 本机可用 `ssh` 与 `tar`（Windows 10/11 通常自带 OpenSSH 与 bsdtar）。
- 远端是 Linux，且有 `find`/`tar`（可选：`gzip`）。

下面示例按你的环境填写：

- Remote：`root@116.211.150.188`
- 端口：`31662`
- RemoteDir：`/root/jx3bla`

### 0)（强烈建议）先停掉写入

停 `server.py` 或至少暂停上传，避免迁移期间又产生新文件。

### 1) 预估（只统计，不拷贝）

```powershell
powershell -ExecutionPolicy Bypass -File tools\migrate_old_stat_files.ps1 `
  -Remote root@116.211.150.188 `
  -Port 31662 `
  -RemoteDir /root/jx3bla `
  -LocalDir E:\jx3bla-backup-2025-01-01 `
  -Cutoff 2025-01-01 `
  -DryRun
```

`-DryRun` 会输出：

- 满足 cutoff 的文件数量
- 满足 cutoff 的文件总大小（字节 + GiB）
- 目录总大小（不做过滤，仅参考）
- 比 cutoff 新的文件数量（用于确认过滤在生效）

### 2) 复制（备份 + 解压；默认不删远端）

脚本会先把远端数据落到本地一个归档文件（`.tar`/`.tar.gz`），通过 `tar -t` 校验可读后再解压。

不压缩（更吃带宽）：

```powershell
powershell -ExecutionPolicy Bypass -File tools\migrate_old_stat_files.ps1 `
  -Remote root@116.211.150.188 `
  -Port 31662 `
  -RemoteDir /root/jx3bla `
  -LocalDir E:\jx3bla-backup-2025-01-01 `
  -Cutoff 2025-01-01
```

带宽小推荐开启 gzip（更省带宽，通常更快）：

```powershell
powershell -ExecutionPolicy Bypass -File tools\migrate_old_stat_files.ps1 `
  -Remote root@116.211.150.188 `
  -Port 31662 `
  -RemoteDir /root/jx3bla `
  -LocalDir E:\jx3bla-backup-2025-01-01 `
  -Cutoff 2025-01-01 `
  -Compress gzip
```

### 3) 删除（确认备份无误后再执行）

确认本地归档可读、解压目录里确实有文件后，再显式删除远端匹配文件：

```powershell
powershell -ExecutionPolicy Bypass -File tools\migrate_old_stat_files.ps1 `
  -Remote root@116.211.150.188 `
  -Port 31662 `
  -RemoteDir /root/jx3bla `
  -LocalDir E:\jx3bla-backup-2025-01-01 `
  -Cutoff 2025-01-01 `
  -DeleteRemote
```

### 分批迁移建议（目标：先迁 ~2GiB）

如果一次要迁几十 GiB，在 10Mbps 带宽下会非常久。建议先把 `-Cutoff` 改成更早的日期，找到一个匹配大小约 2GiB 的 cutoff，先迁一批腾出空间，再继续推进。

试探示例：

```powershell
powershell -ExecutionPolicy Bypass -File tools\migrate_old_stat_files.ps1 `
  -Remote root@116.211.150.188 `
  -Port 31662 `
  -RemoteDir /root/jx3bla `
  -LocalDir E:\jx3bla-backup-tmp `
  -Cutoff 2024-01-01 `
  -DryRun
```

## 排查：`tar.exe: Error opening archive: Unrecognized archive format`

这通常意味着“本地收到的不是 tar 流”（例如远端输出了错误信息/登录 banner）。建议先验证远端命令是否正常：

```bash
ssh -p 31662 root@116.211.150.188 "cd /root/jx3bla && find database/ActorStat database/ReplayProStat -type f ! -newermt '2025-01-01' | head"
ssh -p 31662 root@116.211.150.188 "cd /root/jx3bla && tar --version || tar -h"
```

## 如果已经误删远端但本地没备份

- 立刻停掉 `server.py` / 停止写入，避免覆盖已删除文件的磁盘块。
- 检查是否有云盘快照/备份。
- ext4 场景可尝试 `extundelete` / `testdisk`（SSD/TRIM 场景成功率更低）。

## bash（备用）

### 预估

```bash
bash tools/migrate_old_stat_files.sh \
  --remote root@116.211.150.188 \
  --remote-dir /root/jx3bla \
  --local-dir /data/jx3bla-backup-2025-01-01 \
  --cutoff 2025-01-01 \
  --dry-run
```

### 复制（默认不删远端）

```bash
bash tools/migrate_old_stat_files.sh \
  --remote root@116.211.150.188 \
  --remote-dir /root/jx3bla \
  --local-dir /data/jx3bla-backup-2025-01-01 \
  --cutoff 2025-01-01
```

带宽小可启用 gzip：

```bash
bash tools/migrate_old_stat_files.sh \
  --remote root@116.211.150.188 \
  --remote-dir /root/jx3bla \
  --local-dir /data/jx3bla-backup-2025-01-01 \
  --cutoff 2025-01-01 \
  --compress gzip
```

### 删除（确认备份无误后再执行）

```bash
bash tools/migrate_old_stat_files.sh \
  --remote root@116.211.150.188 \
  --remote-dir /root/jx3bla \
  --local-dir /data/jx3bla-backup-2025-01-01 \
  --cutoff 2025-01-01 \
  --delete-remote
```

### rsync 模式（需要两端都有 rsync）

```bash
bash tools/migrate_old_stat_files.sh \
  --remote root@116.211.150.188 \
  --remote-dir /root/jx3bla \
  --local-dir /data/jx3bla-backup-2025-01-01 \
  --cutoff 2025-01-01 \
  --mode rsync
```

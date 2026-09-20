# 发布构建说明

## 8.16.0 正式版

苍生铸世（游戏版本 160 起）的 Actor 在正式版和 beta 版中都会使用本地属性计算。正式 EXE 必须带入对应装备表、50 级心法和首领防御数据。版本名不含 `beta` 并不代表新赛季可以省略这些数据。

正式构建使用 `MainWindow.spec`；该文件必须随代码版本管理。构建前完成版本号、公告、数据与测试更新，再执行：

```powershell
./release/Release.ps1
# 指定同一套 Python 环境：
./release/Release.ps1 -Python C:/Python314/python.exe
```

脚本自动切到仓库根目录，所有 Python 步骤使用同一个解释器，失败即停止。流水线为：

1. 检查 PyInstaller、正式版本号和 11 份运行资源。
2. 依次运行 `GeneratorGenerator`（图标）、`EquipmentTypeGenerator`（已有装备分类）、`JsonGenerator`（复盘说明）。
3. 以 `equip/resources/cangshengtf` 为输入生成 `replayer/NameCangsheng.py`。旧赛季 `replayer/Name.py` 保留。
4. 通过 `python -m PyInstaller` 在独立的 `build/release-*` 目录构建。
5. 读取 EXE 内部归档，逐份核对 11 个资源的 SHA256，检查没有额外混入旧装备表、原始 buff 表或开发取证文件。
6. 从新建的空工作目录执行 EXE 内置冒烟检查：资源、心法、关键增益及隐藏 Tk 窗口。测试阻断网络和上传。
7. 全部通过后替换 `dist/j3jz.exe`，打印 EXE SHA256 和冒烟报告位置。之前任一步失败，都保留原有 `dist/j3jz.exe`。

脚本只负责生成、构建和验证，不执行 Git 操作、不上传网盘、不更新服务器公告。失败目录保留在忽略的 `build/` 下，便于检查日志。重新运行会使用新的临时产物目录。

### 正式包内数据

唯一清单为 `release/ReleaseResources.py` 的 `CANGSHENG_FILES`，正式 spec、验包和冒烟检查共用该清单。均位于 `equip/resources/cangshengtf/`：

- `Custom_Trinket.tab`、`Custom_Armor.tab`、`Custom_Weapon.tab`
- `attrib.tab`、`enchant.tab`、`item.txt`、`other.tab`、`Set.tab`
- `StrengthableAttrib.tab`、`xinfa50.json`、`luoyang_npc_defense.json`

增益和技能名称使用编译入包的 `NameCangsheng.py`；原始 `buff*.tab`、`buff*.txt`、`skill*.txt` 仅供生成时使用。旧赛季的大型静态表不进入正式包。图标由 `GenerateFiles.py` 写到运行目录；`icons/rate.dat` 是可写缓存。

可以单独检查现有 EXE 内的资源，无需启动它：

```powershell
python -m release.ValidateRelease --exe dist/j3jz.exe
```

该检查要求源码快照与目标 EXE 对应；换过底表后，旧 EXE 应当校验失败。

### 打包后真实日志验证

有本地备份清单时，可让构建流程在发布产物前追加五场通关、各心法/治疗复盘和隐藏窗口验证：

```powershell
./release/Release.ps1 -Python C:/Python314/python.exe `
  -ReplayManifest backups/luoyang-20260915/manifest.json
```

也可把最终 EXE 复制到一个新的空目录，从该目录执行以下命令（清单使用绝对路径）：

```powershell
./j3jz.exe --release-smoke-test --report ./release-smoke.json `
  --manifest C:/Develop/21/jx3bla/backups/luoyang-20260915/manifest.json
```

省略 `--manifest` 只做基础冒烟。报告必须同时包含 `status: passed` 和 `frozen: true`；失败时命令返回非零。日志和身份明细保留在本地验证目录。EXE 冒烟不等于游戏内手工验收。

## 提交、上传与公告

构建和验证通过后，单独进行发布操作：

1. 审核源码、版本公告和生成文件的变更；用准确文件路径暂存本次修改，检查 `git diff --cached --name-only` 和 `git diff --cached --check`，确保没有带入其他分析任务的文件。
2. 提交，并确认当前分支与远端目标后推送。发布脚本没有自动提交或推送步骤。
3. 将已验证的 `dist/j3jz.exe` 人工上传到发布网盘，确认用户可下载，再记录真实下载链接。
4. 运行 `python -m release.Release`，输入该链接。此步骤会将 `Constants.py` 的版本号、公告和下载地址写入 `/setAnnouncement`，属于实际发布动作；只有文件上传成功后才执行。

构建成功本身不代表下载链接、网盘文件或服务器公告已经更新。

## Beta 离线包边界

`MainWindow.beta.spec` 还会打包旧赛季八份大型装备表和图标，适用于需要旧赛季离线计算的 beta 包；正式 8.16.0 使用 `MainWindow.spec`。历史 `ReleaseBeta.ps1` 仍含自动 Git 步骤，本次标准发布不调用它。

新赛季增益表的独立生成命令是：

```powershell
python -m release.NameGenerator --resources equip/resources/cangshengtf --output replayer/NameCangsheng.py
```

心法原始字节码、原生机器码与审计工具用于开发复核，无需随运行包发布。数据启用范围与验证边界见 `docs/160/苍生铸世接入手册.md`。

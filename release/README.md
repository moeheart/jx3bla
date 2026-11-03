# 发布构建说明

## 支持范围

新版仅适配 50 级苍生铸世正式服，使用 2026-10-29 的 `1.6.0.10009` 数据。输入约定为 10 月 29 日以后正式服日志；客户端不检查或拦截日志日期，不再按日期、地图或版本号切换体服/旧等级公式。排名与服务端统计的时间分区保留原有定义。

## 构建

正式入口仍为 `MainWindow.spec` 和 `release/Release.ps1`：

```powershell
./release/Release.ps1 -Python C:/Python314/python.exe
```

所有 Python 步骤使用同一个解释器，失败即停止。脚本依次生成图标、当前装备分类、复盘说明和 `replayer/Name.py`，在独立的 `build/release-*` 中构建，核对资源 SHA256 与依赖清单，并在空目录执行冻结 EXE 的心法、增益、PNG/ICO + Tk 和 Excel 读写检查。全部通过后才替换 `dist/j3jz.exe`。

`MainWindow.beta.spec` 保留为旧命令入口，使用完全相同的当前资源；`ReleaseBeta.ps1` 转调上述构建脚本，输出同一个 `dist/j3jz.exe`。两个入口均不执行 Git 提交、推送、网盘上传或服务器公告更新。

## 包内资源

唯一清单为 `release/ReleaseResources.py` 的 `CANGSHENG_FILES`。资源仍位于 `equip/resources/cangshengtf/`，保留既有赛季目录名称：

- `Custom_Trinket.tab`、`Custom_Armor.tab`、`Custom_Weapon.tab`
- `attrib.tab`、`enchant.tab`、`item.txt`、`other.tab`、`Set.tab`
- `StrengthableAttrib.tab`、`xinfa50.json`、`global_parameters.json`
- `luoyang_npc_defense.json`

名称和增益统一由原有 `replayer/Name.py` 提供。正式服 JSON 使用单一名称，不再同时保留 `_hd` 与体服运行副本。旧赛季原表、体服装备 zip、旧名称表和开发证据不进入安装包。图标由 `GenerateFiles.py` 写入运行目录，`icons/rate.dat` 为运行时缓存。

原始 `buff*.tab`、`buff*.txt`、`skill*.txt` 用于生成名称表。来源清单和 `docs/160/evidence/` 中的原件用于开发复核；历史取证资料不承担客户端兼容功能。

```powershell
python -m release.NameGenerator
python -m release.ValidateRelease --exe dist/j3jz.exe
```

验包要求源码与目标 EXE 对应，并拒绝混入旧运行模块、旧资源、文档及 NumPy/AVIF 可选依赖。

## 本地回放验证

可通过 `-ReplayManifest` 传入当前正式服日志清单。清单是 JSON 数组，每项含 `source` 绝对路径及可选 `sha256`；构建脚本会追加实际复盘、治疗模块、伤害守恒和隐藏窗口检查。`-WujieLog` 可追加单个当前日志，原有参数入口保留。

也可从空目录运行已经构建的 EXE：

```powershell
./MainWindow.exe --release-smoke-test --report ./report.json --manifest C:/验证资料/formal-manifest.json
```

报告要求 `status: passed` 和 `frozen: true`。回放检查阻断网络与上传，记录未标定装备/目标的已有提示；它不等同于游戏内手工验收，也不为旧日志提供兼容承诺。

## 提交、上传与公告

构建和验证通过后，单独进行发布操作：

1. 审核源码、版本公告和生成文件的变更；用准确文件路径暂存本次修改，检查 `git diff --cached --name-only` 和 `git diff --cached --check`，确保没有带入其他分析任务的文件。
2. 提交，并确认当前分支与远端目标后推送。发布脚本没有自动提交或推送步骤。
3. 将已验证的 `dist/j3jz.exe` 人工上传到发布网盘，确认用户可下载，再记录真实下载链接。
4. 运行 `python -m release.Release`，输入该链接。此步骤会将 `Constants.py` 的版本号、公告和下载地址写入 `/setAnnouncement`，属于实际发布动作；只有文件上传成功后才执行。

构建成功本身不代表下载链接、网盘文件或服务器公告已经更新。

## 数据生成与体积

生成器保留在 `release/`，采用原有 `*Generator.py` 命名：

| 入口 | 用途 |
| --- | --- |
| `NameGenerator` | 正式表生成 `replayer/Name.py` |
| `FormalXinfa50Generator` | 10009 原件生成或校验心法、全局参数和首领防御 |
| `SyncCangshengTables` | 核对提取凭据后更新正式源表及名称表 |
| `Xinfa50Generator`、`WujieXinfa50Generator` | 仅复核 `docs/160/evidence/legacy9506/` 历史证据，不作为当前构建步骤 |


心法重生成或校验需要与所用 Python 版本匹配、包含 `lupa.lua51` 的 Lupa。可先在该解释器环境安装 `lupa`；已有独立依赖目录时，通过 `--deps <目录>` 提供。客户端运行与普通构建不需要 Lupa。

```powershell
python -m release.FormalXinfa50Generator --check
# 若依赖位于独立目录，改用：
python -m release.FormalXinfa50Generator --deps C:/开发依赖/python-deps --check
python -m unittest discover -s tests
```

rDPS 报告工具需要显式传入 `--manifest`，例如 `python -m tools.ValidateLuoyangRdps --manifest C:/验证资料/formal-manifest.json`，默认输出到 `build/validation/luoyang-rdps/`。

两个 spec 都排除 Excel 库的可选 NumPy 适配和未使用的 AVIF 解码器；专项绘图脚本仍可在源码环境使用 NumPy。新版进一步去掉体服兼容 zip 和重复名称/公式模块。旧版 8.16.3 的依赖瘦身对照保存在 `build/structure-size-20261103/`；当前仅正式服的构建验证记录在 `build/formal50-only-20261103/`。

2026-11-03 在上游 8.16.3 基础上整合并验收，保留其公告与首领修复。验证包为 35,855,099 字节（34.19 MiB），比原 8.16.3 的 63.12 MiB 减少约 45.8%；对比包含支持范围缩减与依赖精简。196 项自动测试通过，1 项因缺少可选本地日志跳过；12 项运行资源、内嵌源码、PNG/ICO + Tk、Excel 和五场正式服日志的冻结 EXE 回放全部通过。原有装备脚本未解析提示保留。

本次提交不含工作区原有、尚未提交的平均装备估算或独立来源目标增益功能；这些改动及其分析资料仍保留在原工作区。验证包位于 `build/submission-20261103/artifact/MainWindow.exe`，整合回执为 `build/submission-20261103/summary.json`；未替换原发布包或更新线上公告。

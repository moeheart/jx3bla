# 发布构建说明

8.16.8修复战斗主表居中与25人默认展示、可变奇穴槽位导致的个人窗口中断，并整理五首领技能轴的去重、颜色、图标及并发分轨。实现范围、验证和发布状态见[8.16.8复盘界面修复](../docs/160/8.16.8复盘界面修复.md)。

## 支持范围

新版仅适配 50 级苍生铸世正式服，基础表使用 2026-10-29 的 `1.6.0.10009` 数据。8.16.6 的装备特效补充使用 `1.6.0.10072` 正式客户端脚本，并逐行核对相关归档表关联；来源版本和边界记录在装备特效证据中。输入约定为 10 月 29 日以后正式服日志；客户端不检查或拦截日志日期，不再按日期、地图或版本号切换体服/旧等级公式。排名与服务端统计的时间分区保留原有定义。

8.16.7补充英雄洛阳五首领复盘和英雄NPC档案，并核查35个装备来源的66个精确效果参数。英雄NPC原表和关联装备、技能、Buff对照使用`1.6.0.10082`，新鲜提取的配方表和脚本使用`1.6.0.10086`；两者版本边界见[装备核查说明](../docs/160/8.16.7装备特效核查.md)。悟心法只扩展已取证的`4pw`精确条目，缺装备、估算或未核验效果仍阻止精确排名。

本轮解析和统计还补入JCL原生反射返回值，按反射玩家和原NPC目标计入伤害；五首领专属伤害表使用同一字段约束和结束边界。日志反射总量不等于单件套装贡献，必须重新分析旧记录才能补齐漏算。

8.16.7服务端已于2026-11-13 18:58:47 UTC上线并通过生产验收，部署源码为`e37bb5d455f45a88a0266e3c315bc169053d5ca3`，已推送`origin/codex/dev-8.16`，详见[8.16.7发布记录](../docs/160/8.16.7发布记录.md)。最终五场完整回放、125/125份个人复盘精确资格及隔离接收回归已通过，装备告警为零，最大实际合并表单2,147,260字节。全套390项运行先通过389项；唯一旧版本断言更新后，所属模块11项重跑通过，运行代码和资源未再变动，故390个不同测试均已通过。详细口径及普通实录回归见[最终验证回执](../docs/160/heroic-20261113-validation.json)。125份真实个人复盘仅作隔离验收，未补传生产。本轮没有制作或分发8.16.7客户端安装包，公开下载及下载公告仍对应8.16.6。

125份全部精确依赖按时间顺序包含20:01:33前一失败记录的实际装备上下文；只选五个成功文件时，一号仍有1人缺装备，保留估算与精确排名限制。

## 构建

正式入口仍为 `MainWindow.spec` 和 `release/Release.ps1`：

```powershell
C:/Python314/python.exe -m release.EquipmentEffectGenerator --check
./release/Release.ps1 -Python C:/Python314/python.exe
```

装备特效目录的生成与审核独立于 `Release.ps1`。修改已审核效果条目后，先运行 `python -m release.EquipmentEffectGenerator` 同步 `equipment_effects.json` 及来源清单，再运行上述 `--check`，确认精确效果参数和证据 SHA256 一致；构建不自动放行新效果。

生成器合并`docs/160/evidence/equipment_effects/`与`docs/160/evidence/heroic_equipment10082/`的精确模型。补充条目必须保留既有普通心法的处理方式和静态属性；悟心法需要独立处理方式和明确心法名单。当前合并目录193项已通过生成校验，其中63项为普通心法不适用的无界配方。

所有 Python 步骤使用同一个解释器，失败即停止。脚本依次生成图标、当前装备分类、复盘说明和 `replayer/Name.py`，在独立的 `build/release-*` 中构建，核对资源 SHA256 与依赖清单，并在空目录执行冻结 EXE 的心法、增益、PNG/ICO + Tk 和 Excel 读写检查。装备估算另走真实 Actor 流程，检查有样本、无样本和混合状态，确认属性排名与上传受到保护、实测伤害百分位仍可使用。全部通过后才替换 `dist/j3jz.exe`。

`MainWindow.beta.spec` 保留为旧命令入口，使用完全相同的当前资源；`ReleaseBeta.ps1` 转调上述构建脚本，输出同一个 `dist/j3jz.exe`。两个入口均不执行 Git 提交、推送、网盘上传或服务器公告更新。

## 包内资源

唯一清单为 `release/ReleaseResources.py` 的 `CANGSHENG_FILES`。资源仍位于 `equip/resources/cangshengtf/`，保留既有赛季目录名称：

- `Custom_Trinket.tab`、`Custom_Armor.tab`、`Custom_Weapon.tab`
- `attrib.tab`、`enchant.tab`、`item.txt`、`other.tab`、`Set.tab`
- `StrengthableAttrib.tab`、`xinfa50.json`、`global_parameters.json`
- `luoyang_npc_defense.json`、`luoyang_heroic_npc_defense.json`、`average_equipment.json`、`equipment_effects.json`

英雄洛阳适配后为 15 项运行资源；新增英雄 NPC 表来自正式服 `1.6.0.10082`，以 54 级本体和各小怪独立防御档案计算。复核命令：`python -m tools.ValidateLuoyangNpcDefense --heroic --source docs/160/evidence/heroic10082/sNpcTemplate.tab`。

名称和增益统一由原有 `replayer/Name.py` 提供。正式服 JSON 使用单一名称，不再同时保留 `_hd` 与体服运行副本。旧赛季原表、体服装备 zip、旧名称表和开发证据不进入安装包。图标由 `GenerateFiles.py` 写入运行目录，`icons/rate.dat` 为运行时缓存。

8.16.6 共包含 14 项上述运行资源。`equipment_effects.json` 是按精确类型、ID／脚本路径、参数生成的运行目录；对应 `docs/160/evidence/equipment_effects/` 和本轮 `docs/160/evidence/heroic_equipment10082/` 原件与反汇编只用于开发复核，不进入安装包。证据目录由 Git 保留原始字节，避免换行转换使清单 SHA256 失效。

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
| `EquipmentEffectGenerator` | 已审核装备特效证据生成或校验 `equipment_effects.json` 与来源 SHA256 |
| `FormalXinfa50Generator` | 10009 原件生成或校验心法、全局参数和首领防御 |
| `SyncCangshengTables` | 核对提取凭据后更新正式源表及名称表 |
| `AverageEquipmentGenerator` | 从 10 月 29 日起的正式服日志生成可用心法的平均装备参考；原始日志不入包 |
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

上述 8.16.3 整合验收未包含平均装备估算和独立来源目标增益修复，验证包位于 `build/submission-20261103/artifact/MainWindow.exe`。8.16.4 在此基础上纳入这两项修复，运行资源共 13 项；最终构建、校验和发布状态见 [8.16.4 发布记录](../docs/160/8.16.4发布记录.md)。
